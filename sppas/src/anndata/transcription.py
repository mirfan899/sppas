# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.transcription.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A transcription is a set of tiers.

"""
from sppas.src.utils.fileutils import sppasGUID
from sppas.src.utils.makeunicode import sppasUnicode

from .anndataexc import AnnDataTypeError
from .anndataexc import TrsAddError
from .anndataexc import TrsRemoveError
from .anndataexc import AnnDataIndexError

from .metadata import sppasMetaData
from .ctrlvocab import sppasCtrlVocab
from .media import sppasMedia
from .tier import sppasTier
from .hierarchy import sppasHierarchy


# ----------------------------------------------------------------------------


class sppasTranscription(sppasMetaData):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Representation of a transcription.

    Transcriptions in SPPAS are represented with:
        - metadata: a list of tuple key/value;
        - a name (used to identify the transcription);
        - a list of tiers;
        - a hierarchy between tiers.

    Inter-tier relations are managed by establishing alignment or association
    links between 2 tiers:
        - alignment: annotations of a tier A (child) have only localization
          instances included in those of annotations of tier B (parent);
        - association: annotations of a tier A have exactly localization
         instances included in those of annotations of tier B.

    >>> # Create an instance
    >>> trs = sppasTranscription()

    >>> # Get a tier of a transcription from its index:
    >>> tier = trs[0]

    """
    def __init__(self, name=None, min_point=None, max_point=None):
        """ Creates a new sppasTranscription instance.

        :param name: (str) Name of the transcription. It is used as identifier.
        :param min_point: (sppasPoint)
        :param max_point: (sppasPoint)

        """
        super(sppasTranscription, self).__init__()

        self.__name = None
        self.__min_point = min_point
        self.__max_point = max_point
        self.__media = list()      # a list of sppasMedia() instances
        self.__ctrlvocab = list()  # a list of sppasCtrlVocab() instances
        self.__tiers = list()      # a list of sppasTier() instances
        self.hierarchy = sppasHierarchy()

        self.set_name(name)

    # -----------------------------------------------------------------------
    # Name
    # -----------------------------------------------------------------------

    def get_name(self):
        """ Return the identifier name of the transcription. """

        return self.__name

    # -----------------------------------------------------------------------

    def set_name(self, name=None):
        """ Set the name of the tier.

        :param name: (str or None) The identifier name or None.
        :returns: the name

        """
        if name is None:
            name = sppasGUID().get()
        su = sppasUnicode(name)
        self.__name = su.to_strip()

        return self.__name

    # ------------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------------

    def get_media_list(self):
        """ Return the list of sppasMedia. """

        return self.__media

    # ------------------------------------------------------------------------

    def get_media_from_name(self, media_name):
        """ Return a sppasMedia from its name or None.

        :param media_name: (str) Identifier name of a media

        """
        idt = media_name.strip()
        for m in self.__media:
            if m.get_name() == idt:
                return m
        return None

    # ------------------------------------------------------------------------

    def add_media(self, new_media):
        """ Add a new media in the list of media.

        :param new_media: (sppasMedia)
        :raises: AnnDataTypeError, TrsAddError

        """
        if isinstance(new_media, sppasMedia) is False:
            raise AnnDataTypeError(new_media, "sppasMedia")

        ids = [m.get_name() for m in self.__media]
        if new_media.get_name() in ids:
            raise TrsAddError(new_media.get_name())

        self.__media.append(new_media)

    # ------------------------------------------------------------------------

    def remove_media(self, old_media):
        """ Remove a media of the list of media.

        :param old_media: (sppasMedia)
        :raises: AnnDataTypeError, TrsRemoveError

        """
        if not isinstance(old_media, sppasMedia):
            raise AnnDataTypeError(old_media, "sppasMedia")

        if old_media not in self.__media:
            raise TrsRemoveError(old_media.get_name())

        self.__media.remove(old_media)
        for tier in self.__tiers:
            if tier.get_media() == old_media:
                tier.set_media(None)

    # ------------------------------------------------------------------------

    def set_media_list(self, media_list):
        """ Set the list of media.

        :param media_list: (list)
        :returns: list of rejected media

        """
        self.__media = list()
        rejected = list()
        for m in media_list:
            try:
                self.add_media(m)
            except Exception:
                rejected.append(m)

        return rejected

    # ------------------------------------------------------------------------
    # Controlled vocabularies
    # ------------------------------------------------------------------------

    def get_ctrl_vocab_list(self):
        """ Return the list of controlled vocabularies. """

        return self.__ctrlvocab

    # ------------------------------------------------------------------------

    def get_ctrl_vocab_from_name(self, ctrl_vocab_name):
        """ Return a sppasCtrlVocab from its name or None.

        :param ctrl_vocab_name: (str) Identifier name of a controlled vocabulary

        """
        idt = ctrl_vocab_name.strip()
        for c in self.__ctrlvocab:
            if c.get_name() == idt:
                return c

        return None

    # ------------------------------------------------------------------------

    def add_ctrl_vocab(self, new_ctrl_vocab):
        """ Add a new controlled vocabulary in the list of ctrl vocab.

        :param new_ctrl_vocab: (sppasCtrlVocab)
        :raises: AnnDataTypeError, TrsAddError

        """
        if not isinstance(new_ctrl_vocab, sppasCtrlVocab):
            raise AnnDataTypeError(new_ctrl_vocab, "sppasCtrlVocab")

        ids = [c.get_name() for c in self.__ctrlvocab]
        if new_ctrl_vocab.get_name() in ids:
            raise TrsAddError(new_ctrl_vocab.get_name())

        self.__ctrlvocab.append(new_ctrl_vocab)

    # ------------------------------------------------------------------------

    def remove_ctrl_vocab(self, old_ctrl_vocab):
        """ Remove a controlled vocabulary of the list of ctrl vocab.

        :param old_ctrl_vocab: (sppasCtrlVocab)
        :raises: AnnDataTypeError, TrsRemoveError

        """
        if not isinstance(old_ctrl_vocab, sppasCtrlVocab):
            raise AnnDataTypeError(old_ctrl_vocab, "sppasCtrlVocab")

        if old_ctrl_vocab not in self.__ctrlvocab:
            raise TrsRemoveError(old_ctrl_vocab.get_name())

        self.__ctrlvocab.remove(old_ctrl_vocab)
        for tier in self.__tiers:
            if tier.get_ctrl_vocab() == old_ctrl_vocab:
                tier.set_ctrl_vocab(None)

    # ------------------------------------------------------------------------

    def set_ctrl_vocab_list(self, ctrl_vocab_list):
        """ Set the list of controlled vocabularies.

        :param ctrl_vocab_list: (list)
        :returns: list of rejected ctrl_vocab

        """
        self.__ctrlvocab = list()
        rejected = list()
        for c in ctrl_vocab_list:
            try:
                self.add_ctrl_vocab(c)
            except Exception:
                rejected.append(c)

        return rejected

    # -----------------------------------------------------------------------
    # Tiers
    # ------------------------------------------------------------------------

    def is_empty(self):
        """ Return True if the transcription does not contains tiers. """

        return len(self.__tiers) == 0

    # ------------------------------------------------------------------------

    def find(self, name, case_sensitive=True):
        """ Find a tier from its name.

        :param name: (str) EXACT name of the tier
        :param case_sensitive: (bool)
        :returns: sppasTier or None

        """
        for tier in self.__tiers:
            if case_sensitive:
                if tier.get_name() == name.strip():
                    return tier
            else:
                if tier.get_name().lower() == name.strip().lower():
                    return tier

        return None

    # ------------------------------------------------------------------------

    def get_tier_index(self, name, case_sensitive=True):
        """ Get the index of a tier from its name.

        :param name: (str) EXACT name of the tier
        :param case_sensitive: (bool)
        :returns: index or -1 if not found

        """
        t = self.find(name, case_sensitive)
        if t is None:
            return -1
        return self.__tiers.index(t)

    # ------------------------------------------------------------------------

    def rename_tier(self, tier):
        """ Rename a tier by appending a digit.

        :param tier: (sppasTier) The tier to rename.

        """
        if not isinstance(tier, sppasTier):
            raise AnnDataTypeError(tier, "sppasTier")

        name = tier.get_name()
        i = 2
        while self.find(name) is not None:
            name = u"%s(%d)" % (tier.get_name(), i)
            i += 1
        tier.set_name(name)

    # ------------------------------------------------------------------------

    def create_tier(self, name=None, ctrl_vocab=None, media=None):
        """ Append a new empty tier.

        :param name: (str) the name of the tier to create
        :param ctrl_vocab: (sppasCtrlVocab)
        :param media: (sppasMedia)
        :returns: newly created empty tier

        """
        tier = sppasTier(name, ctrl_vocab, media, parent=self)
        self.append(tier)

        return tier

    # ------------------------------------------------------------------------

    def append(self, tier):
        """ Append a new tier.

        :param tier: (sppasTier) the tier to append

        """
        if tier in self.__tiers:
            raise TrsAddError(tier.get_name())

        self.rename_tier(tier)
        if tier.get_ctrl_vocab() is not None:
            try:
                self.add_ctrl_vocab(tier.get_ctrl_vocab())
            except TrsAddError:
                pass
        if tier.get_media() is not None:
            try:
                self.add_media(tier.get_media())
            except TrsAddError:
                pass

        self.__tiers.append(tier)
        tier.set_parent(self)

    # ------------------------------------------------------------------------

    def pop(self, index=-1):
        """ Remove the tier at the given position in the transcription,
        and return it. If no index is specified, pop() removes
        and returns the last tier in the transcription.

        :param index: (int) Index of the transcription to remove.

        """
        try:
            tier = self.__tiers[index]
            self.hierarchy.remove_tier(tier)
            self.__tiers.pop(index)
            tier.set_parent(None)
            return tier
        except IndexError:
            raise AnnDataIndexError(index)

    # ------------------------------------------------------------------------
    # Input/Output
    # ------------------------------------------------------------------------

    def read(self):
        raise NotImplementedError

    # ------------------------------------------------------------------------

    def write(self):
        raise NotImplementedError

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
