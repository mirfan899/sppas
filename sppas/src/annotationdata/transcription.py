#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: transcription.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (develop@sppas.org)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import copy

import sppas.src.anndata as anndata

from .ptime.interval import TimeInterval
from .ptime.point import TimePoint
from .label.label import Label
from .annotation import Annotation

from .meta import MetaObject
from .tier import Tier
from .hierarchy import Hierarchy
from .media import Media
from .ctrlvocab import CtrlVocab

from .utils.deprecated import deprecated

# ----------------------------------------------------------------------------


class Transcription(MetaObject):
    """
    @authors: Brigitte Bigi
    @contact: develop@sppas.org
    @license: GPL, v3
    @summary: Generic representation of an annotated file.

    Transcriptions in SPPAS are represented with:
        - meta data: a serie of tuple key/value
        - a name (used as Id)
        - tiers
        - a hierarchy
        - controlled vocabularies (yet not used)

    Inter-tier relations are managed by establishing alignment or association
    links between 2 tiers:
        - alignment: annotations of a tier A (child) have only Time instances
          included in those of annotations of tier B (parent);
        - association: annotations of a tier A have exactly Time instances
          included in those of annotations of tier B.

    >>> transcription = Transcription()
    >>> formertier = transcription.NewTier("parent")
    >>> lattertier = transcription.NewTier("child")
    >>> transcription.GetHierarchy().add_link("TimeAlignment", formertier, lattertier)

    """
    def __init__(self, name="NoName", mintime=0., maxtime=0.):
        """
        Creates a new Transcription instance.

        @param name: (str) the name of the transcription
        @param mintime in seconds
        @param maxtime in seconds

        """
        super(Transcription, self).__init__()
        self.__name      = u'NoName'
        self.__mintime   = mintime
        self.__maxtime   = maxtime
        self.__tiers     = [] # a list of Tier() instances
        self.__media     = [] # a list of Media() instances
        self.__ctrlvocab = [] # a list of CtrlVocab() instances
        self._hierarchy = Hierarchy()

        self.SetName(name)

    # ------------------------------------------------------------------------

    def SetFromAnnData(self, trs):
        """Set the transcription from anndata.sppasTranscription() object.

        @param trs: sppasTranscription.

        """
        self.SetName(trs.get_name())

        for meta_key in trs.get_meta_keys():
            self.metadata[meta_key] = trs.get_meta(meta_key)

        for ctrl_vocab in trs.get_ctrl_vocab_list():
            new_cv = CtrlVocab(ctrl_vocab.get_name())
            new_cv.SetDescription(ctrl_vocab.get_description())
            for tag in ctrl_vocab:
                new_cv.Append(tag.get_content(), ctrl_vocab.get_tag_description(tag))

        for media in trs.get_media_list():
            new_m = Media(media.get_meta('id'), media.get_filename(), media.get_mime_type())
            self.AddMedia(new_m)

        for tier in trs:
            new_tier = Tier(tier.get_name())
            is_point = tier.is_point()
            for ann in tier:
                # here we go to the essential...
                begin = ann.get_lowest_localization()
                r = begin.get_radius()
                if r is None:
                    r = 0.
                new_begin = TimePoint(begin.get_midpoint(), r)
                if is_point is False:
                    end = ann.get_highest_localization()
                    new_end = TimePoint(end.get_midpoint(), end.get_radius())
                    localization = TimeInterval(new_begin, new_end)
                else:
                    localization = new_begin
                label_text = ann.serialize_labels(separator="\n", empty="", alt=True)
                new_tier.Add(Annotation(localization, Label(label_text)))
            for meta_key in tier.get_meta_keys():
                new_tier.metadata[meta_key] = tier.get_meta(meta_key)
            ctrl_vocab = tier.get_ctrl_vocab()
            if ctrl_vocab is not None:
                new_tier.SetCtrlVocab(self.GetCtrlVocabFromId(ctrl_vocab.get_name()))
            media = tier.get_media()
            if media is not None:
                new_tier.SetMedia(self.GetMediaFromId(media.get_meta('id')))

            self.Add(new_tier)

        self.__mintime = trs.get_min_loc().get_midpoint()
        self.__maxtime = trs.get_max_loc().get_midpoint()

        hierarchy = trs.get_hierarchy()
        for tier in trs:
            parent_tier = hierarchy.get_parent(tier)
            if parent_tier is not None:
                link_type = hierarchy.get_hierarchy_type(tier)
                new_tier = self.Find(tier.get_name())
                new_parent_tier = self.Find(parent_tier.get_name())
                self._hierarchy.add_link(link_type, new_parent_tier, new_tier)

    # ------------------------------------------------------------------------

    def ExportToAnnData(self):
        """Export this transcription to anndata.sppasTranscription()."""

        trs = anndata.sppasTranscription(self.__name)

        for meta_key in self.metadata:
            if self.metadata[meta_key] is not None:
                trs.set_meta(meta_key, self.metadata[meta_key])

        for ctrl_vocab in self.GetCtrlVocab():
            other_cv = anndata.sppasCtrlVocab(ctrl_vocab.id, ctrl_vocab.GetDescription())
            for entry in ctrl_vocab:
                entry_text = entry.Text
                entry_desc = entry.GetDescription()
                other_cv.add(anndata.sppasTag(entry_text), entry_desc)
            trs.add_ctrl_vocab(other_cv)

        for media in self.GetMedia():
            other_m = anndata.sppasMedia(media.url, media.id, media.mime)
            trs.add_media(other_m)

        for tier in self:
            c = tier.GetCtrlVocab()
            if c is not None:
                ctrl_vocab = trs.get_ctrl_vocab_from_name(c.GetName())
            else:
                ctrl_vocab = None
            m = tier.GetMedia()
            if m is not None:
                media = trs.get_media_from_id(m.id)
            else:
                media = None
            other_t = trs.create_tier(tier.GetName(), ctrl_vocab, media)
            is_point = tier.IsPoint()
            for ann in tier:
                text = ann.GetLabel().GetLabel()
                if is_point is True:
                    p = ann.GetLocation().GetPoint().GetValue()
                    r = ann.GetLocation().GetPoint().GetRadius()
                    if r == 0.:
                        r = None
                    other_t.create_annotation(
                        anndata.sppasLocation(anndata.sppasPoint(p, r)),
                        anndata.sppasLabel(anndata.sppasTag(text)))
                else:
                    b = ann.GetLocation().GetBegin().GetValue()
                    rb = ann.GetLocation().GetBegin().GetRadius()
                    if rb == 0.:
                        rb = None
                    e = ann.GetLocation().GetEnd().GetValue()
                    re = ann.GetLocation().GetEnd().GetRadius()
                    if rb == 0.:
                        rb = None
                    other_t.create_annotation(
                        anndata.sppasLocation(anndata.sppasInterval(
                            anndata.sppasPoint(b, rb),
                            anndata.sppasPoint(e, re))),
                        anndata.sppasLabel(anndata.sppasTag(text)))

        for tier in self:
            parent_tier = self._hierarchy.get_parent(tier)
            if parent_tier is not None:
                link_type = self._hierarchy.get_hierarchy_type(tier)
                new_tier = trs.find(tier.GetName())
                new_parent_tier = trs.find(parent_tier.GetName())
                trs.add_hierarchy_link(link_type, new_parent_tier, new_tier)

        return trs

    # ------------------------------------------------------------------------

    def Set(self, other, name='NoName'):
        """
        Set a transcription.

        @param other: Transcription or list of Tier instances.
        :param name: (str)
        @raise TypeError:

        """
        if isinstance(other, Transcription):
            self.metadata    = other.metadata
            self._hierarchy  = other._hierarchy
            self.__media     = other.__media
            self.__ctrlvocab = other.__ctrlvocab
            self.__name      = other.__name
            self.__mintime   = other.__mintime
            self.__maxtime   = other.__maxtime
            self.__tiers     = other.__tiers

        if all(isinstance(tier, Tier) for tier in other) is False:
            raise TypeError("Transcription or List of Tier instances argument required, not %r" % other)

        self.__tiers = [tier for tier in other]
        self.__media     = set([tier.GetMedia() for tier in other])
        self.__ctrlvocab = set([tier.GetCtrlVocab() for tier in other])

        self.__name  = name

    # ------------------------------------------------------------------------

    def GetHierarchy(self):
        """
        Return the Hierarchy instance.

        """
        return self._hierarchy

    # ------------------------------------------------------------------------

    def GetName(self):
        """
        Return the string of the name of the transcription.

        """
        return self.__name

    # ------------------------------------------------------------------------

    def SetName(self, name):
        """
        Set a new name (the name is also used as Id, to identify a Transcription)

        @param name (str)
        @raise UnicodeDecodeError

        """
        name = ' '.join(name.split())

        if isinstance(name, unicode):
            self.__name = name
        else:
            try:
                self.__name = name.decode("utf-8")
            except UnicodeDecodeError as e:
                raise e

    # ------------------------------------------------------------------------

    def Copy(self):
        """
        Return a copy of the transcription.

        """
        return copy.deepcopy(self)

    # ------------------------------------------------------------------------

    def SetSherableProperties(self, other):
        """
        Set some of the properties of other to self: media, ctrlvocab.

        """
        if not isinstance(other, Transcription):
            raise TypeError("Can not set properties. Expected Transcription instance, got %s."%type(other))

        self.SetMedia(other.GetMedia())
        self.SetCtrlVocab(other.GetCtrlVocab())

    # ------------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------------

    def GetMedia(self):
        return self.__media

    def GetMediaFromId(self, idm):
        idt = idm.strip()
        for m in self.__media:
            if m.id == idt:
                return m
        return None

    def AddMedia(self, newmedia):
        if not isinstance(newmedia, Media):
            raise TypeError("Can not add media in Transcription. Expected Media instance, got %s."%type(newmedia))
        ids = [ m.id for m in self.__media ]
        if newmedia.id in ids:
            raise ValueError('A media is already defined with the same identifier %s'%newmedia.id)
        self.__media.append(newmedia)

    def RemoveMedia(self, oldmedia):
        if not isinstance(oldmedia, Media) or not oldmedia in self.__media:
            raise TypeError("Can not remove media of Transcription.")
        self.__media.remove(oldmedia)
        for tier in self.__tiers:
            if tier.GetMedia() == oldmedia:
                tier.SetMedia(None)

    def SetMedia(self, media):
        self.__media = []
        for m in media:
            self.AddMedia(m)

    # ------------------------------------------------------------------------
    # Controlled vocabularies
    # ------------------------------------------------------------------------

    def GetCtrlVocab(self):
        return self.__ctrlvocab

    def GetCtrlVocabFromId(self, idt):
        idt = idt.strip()
        for c in self.__ctrlvocab:
            if c.id == idt:
                return c
        return None

    def AddCtrlVocab(self, ctrlvocab):
        if not isinstance(ctrlvocab, CtrlVocab):
            raise TypeError("Unknown controlled vocabulary error in transcription.py.")
        self.__ctrlvocab.append(ctrlvocab)

    def RemoveCtrlVocab(self, ctrlvocab):
        if not isinstance(ctrlvocab, CtrlVocab):
            raise TypeError("Unknown controlled vocabulary error in transcription.py.")
        self.__ctrlvocab.remove(ctrlvocab)
        for tier in self.__tiers:
            if tier.GetCtrlVocab() == ctrlvocab:
                tier.SetCtrlVocab(None)

    def SetCtrlVocab(self, ctrlvocab):
        self.__ctrlvocab = list()
        for c in ctrlvocab:
            self.AddCtrlVocab(c)

    # -----------------------------------------------------------------------
    # Tiers
    # ------------------------------------------------------------------------

    def GetMinTime(self):
        """
        Return the minimum time value.

        """

        return self.__mintime

    # ------------------------------------------------------------------------

    def SetMinTime(self, mintime):
        """
        Set the minimum time value.

        """
        self.__mintime = mintime

    # ------------------------------------------------------------------------

    def GetMaxTime(self):
        """
        Return the maximum time value.

        """
        # In theory, maxtime represents the duration of the annotated media.
        # Then, it can not be lesser than the end of the last annotation...
        # But... none of the annotation formats indicate such duration!
        # So, we do what we can with what we have.
        if self.GetEnd() > self.__maxtime:
            self.__maxtime = self.GetEnd()

        return self.__maxtime

    # ------------------------------------------------------------------------

    def SetMaxTime(self, maxtime):
        """
        Set the maximum time value.

        """
        self.__maxtime = maxtime

        if self.__maxtime < self.GetEnd():
            raise Exception(
                'Impossible to fix a max time value '
                'lesser than the end of annotations.')

    # ------------------------------------------------------------------------

    def GetSize(self):
        """
        Return the number of tiers in the transcription.

        """
        return len(self.__tiers)

    # ------------------------------------------------------------------------

    def NewTier(self, name="Empty"):
        """
        Add a new empty tier at the end of the transcription.

        @param name: (str) the name of the tier to create
        @return: newly created empty tier

        """
        tier = Tier(name)
        tier.SetTranscription(self)
        self.__rename(tier)
        self.__tiers.append(tier)

        return tier

    # ------------------------------------------------------------------------

    def Add(self, tier, index=None):
        """
        Add a new tier at a given index.

        Index must be lower than the transcription size.
        By default, the tier is appended at the end of the list.

        @param tier (Tier) the tier to add to the transcription
        @param index (int) the position in the list of tiers
        @raise IndexError
        @return: Tier index

        """
        tier.SetTranscription(self)
        self.__rename(tier)

        if tier.GetEnd() > self.__maxtime:
            self.__maxtime = tier.GetEndValue()
        if tier.GetBegin() < self.__mintime:
            self.__mintime = tier.GetBeginValue()

        if index is not None:
            if index >= len(self.__tiers) or index < 0:
                raise IndexError
            self.__tiers.insert(index, tier)
        else:
            self.__tiers.append(tier)
            index = len(self.__tiers)-1

        # TODO: GET ITS MEDIA AND SET TO THE TRANSCRIPTION???
        # TODO: IDEM WITH CTRLVOCAB....????

        return index

    # ------------------------------------------------------------------------

    def Append(self, tier):
        """
        Append a tier in the transcription.

        @param tier (Tier) the tier to add to the transcription
        @return Tier index (int)

        """
        tier.SetTranscription(self)
        self.__rename(tier)
        self.__tiers.append(tier)

        if tier.GetEnd() > self.__maxtime:
            self.__maxtime = tier.GetEndValue()
        if tier.GetBegin() < self.__mintime:
            self.__mintime = tier.GetBeginValue()

        # TODO: GET ITS MEDIA AND SET TO THE TRANSCRIPTION???
        # TODO: IDEM WITH CTRLVOCAB....???

        return len(self.__tiers)-1

    # ------------------------------------------------------------------------

    def Pop(self, index=-1):
        """
        Pop a tier of the transcription.

        @param index: the index of the tier to pop. Default is the last one.
        @raise IndexError
        @return: Return the removed tier

        """
        if self.IsEmpty():
            raise IndexError("Pop from empty transcription.")

        try:
            self._hierarchy.remove_tier(self.__tiers[index])
            return self.__tiers.pop(index)
        except IndexError as e:
            raise e

    # ------------------------------------------------------------------------

    def Remove(self, index):
        """
        Remove a tier of the transcription.

        @param index: the index of the tier to remove.
        @raise IndexError:

        """
        if index >= len(self.__tiers) or index < 0:
            raise IndexError

        self._hierarchy.remove_tier(self.__tiers[index])
        del self.__tiers[index]

    # ------------------------------------------------------------------------

    def GetIndex(self, name, case_sensitive=True):
        """
        Get the index of a tier from its name.

        @param name: (str) EXACT name of the tier
        @param case_sensitive: (bool)
        @return: Return the tier index or -1

        """
        t = self.Find(name, case_sensitive)
        for i, tier in enumerate(self.__tiers):
            if t is tier:
                return i

        return -1

    # ------------------------------------------------------------------------

    def Find(self, name, case_sensitive=True):
        """
        Find a tier from its name.

        @param name: (str) EXACT name of the tier
        @param case_sensitive: (bool)
        @return: Return the tier or None

        """
        for tier in self:
            if case_sensitive:
                if tier.GetName() == name.strip():
                    return tier
            else:
                if tier.GetName().lower() == name.strip().lower():
                    return tier

        return None

    # ------------------------------------------------------------------------

    def GetBeginValue(self):
        """
        Return the smaller begin time value of all tiers.
        Return 0 if the transcription contains no tiers.

        @return: Float value, or 0 if the transcription contains no tiers.

        """
        if self.IsEmpty():
            return 0.

        return min(tier.GetBeginValue() for tier in self.__tiers)

    @deprecated
    def GetBegin(self):
        return self.GetBeginValue()

    # ------------------------------------------------------------------------

    def GetEndValue(self):
        """
        Return the higher end time value of all tiers.
        Return 0 if the transcription contains no tiers.

        @return: Float value, or 0 if the transcription contains no tiers.

        """
        if self.IsEmpty():
            return 0.

        return max(tier.GetEndValue() for tier in self.__tiers)

    @deprecated
    def GetEnd(self):
        return self.GetEndValue()

    # ------------------------------------------------------------------------

    def IsEmpty(self):
        """
        Ask the transcription to be empty or not.
        A transcription is empty if it does not contain tiers.

        @return: bool

        """
        return len(self.__tiers) == 0

    # ------------------------------------------------------------------------
    # Input/Output
    # ------------------------------------------------------------------------

    def read(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support read()." % name)

    # ------------------------------------------------------------------------

    def write(self):
        name = self.__class__.__name__
        raise NotImplementedError("%s does not support write()." % name)

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def __rename(self, tier):
        name = tier.GetName()
        i = 2
        while self.Find(name) is not None:
            name = u"%s-%d" % (tier.GetName(), i)
            i += 1
        tier.SetName(name)

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __len__(self):
        return len(self.__tiers)

    # ------------------------------------------------------------------------

    def __iter__(self):
        for x in self.__tiers:
            yield x

    # ------------------------------------------------------------------------

    def __getitem__(self, i):
        return self.__tiers[i]
