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

# ----------------------------------------------------------------------------


class sppasBaseIO(sppasTranscription):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Base object for readers and writers of annotated data.

    """
    @staticmethod
    def detect(filename):
        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new Transcription reader-writer instance.

        :param name: (str) A transcription name.

        """
        sppasTranscription.__init__(self, name)

    # -----------------------------------------------------------------------

    def set(self, other):
        """ Set self with other content.

        :param other: (sppasTranscription)

        """
        if isinstance(other, sppasTranscription) is False:
            raise AnnDataTypeError(other, "sppasTranscription")

        for key in other.get_meta_keys():
            self.set_meta(key, other.get_meta(key))
        self.__name = other.get_name()
        self.__media = other.get_media_list()
        self.__ctrlvocab = other.get_ctrl_vocab_list()
        self.__tiers = [tier for tier in other]
        self.hierarchy = other.hierarchy

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
