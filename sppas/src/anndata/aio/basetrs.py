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

    src.anndata.aio.basetrs.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Base object for readers and writers of annotated data.

"""
from ..transcription import sppasTranscription
from ..anndataexc import AnnDataTypeError

# ---------------------------------------------------------------------------


class sppasBaseIO(sppasTranscription):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Base object for readers and writers of annotated data.

    """
    @staticmethod
    def detect(filename):
        return False

    # -----------------------------------------------------------------------

    @staticmethod
    def is_number(s):
        """ Check whether a string is a number or not.

        :param s: (str or unicode)
        :returns: (bool)

        """
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new Transcription reader-writer instance.

        :param name: (str) A transcription name.
        :param multi_tiers: (bool) The IO supports (or not) to read and write
        several tiers.
        :param no_tiers: (bool) The IO supports (or not) to write no tiers.

        """
        sppasTranscription.__init__(self, name)

        self._accept_multi_tiers = False
        self._accept_no_tiers = False
        self._accept_metadata = False
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = False
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = True
        self._accept_gaps = False
        self._accept_overlaps = False
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def multi_tiers_support(self):
        """ Return True if this reader-writer supports to read and write
        several tiers.

        :returns: boolean

        """
        return self._accept_multi_tiers

    # -----------------------------------------------------------------------

    def no_tiers_support(self):
        """ Return True if this reader-writer supports to write no tier.

        :returns: boolean

        """
        return self._accept_no_tiers

    # -----------------------------------------------------------------------

    def metadata_support(self):
        """ Return True if this reader-writer supports to read and write
        metadata.

        :returns: boolean

        """
        return self._accept_metadata

    # -----------------------------------------------------------------------

    def ctrl_vocab_support(self):
        """ Return True if this reader-writer supports to read and write
        a controlled vocabulary.

        :returns: boolean

        """
        return self._accept_ctrl_vocab

    # -----------------------------------------------------------------------

    def media_support(self):
        """ Return True if this reader-writer supports to read and write
        a link to a media.

        :returns: boolean

        """
        return self._accept_media

    # -----------------------------------------------------------------------

    def hierarchy_support(self):
        """ Return True if this reader-writer supports to read and write
        a hierarchy between tiers.

        :returns: boolean

        """
        return self._accept_hierarchy

    # -----------------------------------------------------------------------

    def point_support(self):
        """ Return True if this reader-writer supports to read and write
        tiers with localizations as points.

        :returns: boolean

        """
        return self._accept_point

    # -----------------------------------------------------------------------

    def interval_support(self):
        """ Return True if this reader-writer supports to read and write
        tiers with localizations as intervals.

        :returns: boolean

        """
        return self._accept_interval

    # -----------------------------------------------------------------------

    def disjoint_support(self):
        """ Return True if this reader-writer supports to read and write
        tiers with localizations as disjoint intervals.

        :returns: boolean

        """
        return self._accept_disjoint

    # -----------------------------------------------------------------------

    def alternative_localization_support(self):
        """ Return True if this reader-writer supports to read and write
        alternative localizations (with a score or not).

        :returns: boolean

        """
        return self._accept_alt_localization

    # -----------------------------------------------------------------------

    def alternative_tag_support(self):
        """ Return True if this reader-writer supports to read and write
        alternative tags (with a score or not).

        :returns: boolean

        """
        return self._accept_alt_tag

    # -----------------------------------------------------------------------

    def radius_support(self):
        """ Return True if this reader-writer supports to read and write
        the radius value (the vagueness or a point).

        :returns: boolean

        """
        return self._accept_radius

    # -----------------------------------------------------------------------

    def gaps_support(self):
        """ Return True if this reader-writer supports gaps between
        annotations of a tier (i.e. gaps = holes).

        :returns: boolean

        """
        return self._accept_gaps

    # -----------------------------------------------------------------------

    def overlaps_support(self):
        """ Return True if this reader-writer supports overlaps between
        annotations of a tier.

        :returns: boolean

        """
        return self._accept_overlaps

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self with other content.

        :param other: (sppasTranscription)

        """
        if isinstance(other, sppasTranscription) is False:
            raise AnnDataTypeError(other, "sppasTranscription")

        for key in other.get_meta_keys():
            self.set_meta(key, other.get_meta(key))
        self._name = other.get_name()
        self._media = other.get_media_list()
        self._ctrlvocab = other.get_ctrl_vocab_list()
        self._tiers = other.get_tier_list()
        self._hierarchy = other.get_hierarchy()

    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a file and fill the Transcription.

        :param filename: (str)

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def write(self, filename):
        """ Write the transcription into a file.

        :param filename: (str)

        """
        raise NotImplementedError
