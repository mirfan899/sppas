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

    src.anndata.aio.rw.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Readers and writers of annotated data.

"""
import os.path

from sppas.src.utils.makeunicode import u

from ..anndataexc import AioEncodingError

from .xra import sppasXRA
# from .text import RawText, CSV
# from .praat import TextGrid, PitchTier, IntensityTier
# from .signaix import HzPitch
# from .transcriber import Transcriber
# from .phonedit import Phonedit
# from .htk import HTKLabel, MasterLabel
# from .subtitle import SubRip, SubViewer
# from .sclite import TimeMarkedConversation, SegmentTimeMark
# from .elan import Elan
# from .anvil import Anvil
# from .annotationpro import Antx
# from .xtrans import Xtrans
# from .audacity import Audacity

# ----------------------------------------------------------------------------


class sppasRW(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Main parser of annotated data.

    """
    TRANSCRIPTION_TYPES = {
        "xra": sppasXRA,
        # "textgrid": TextGrid,
        # "eaf": Elan,
        # "trs": Transcriber,
        # "mrk": Phonedit,
        # "lab": HTKLabel,
        # "mlf": MasterLabel,
        # "srt": SubRip,
        # "sub": SubViewer,
        # "ctm": TimeMarkedConversation,
        # "stm": SegmentTimeMark,
        # "anvil": Anvil,
        # "antx": Antx,
        # "tdf": Xtrans,
        # "aup": Audacity,
        # "csv": CSV,
        # "intensitytier": IntensityTier,
        # "pitchtier": PitchTier,
        # "hz": HzPitch,
        # "txt": RawText
    }

    # -----------------------------------------------------------------------

    def __init__(self, filename):
        """ Create a Transcription reader-writer.

        :param filename: (str)

        """
        self.__filename = u(filename)

    # -----------------------------------------------------------------------

    def get_filename(self):
        """ Return the filename. """

        return self.__filename

    # -----------------------------------------------------------------------

    def set_filename(self, filename):
        """ Set a new filename. 

        :param filename: (str)

        """
        self.__filename = u(filename)
        
    # -----------------------------------------------------------------------

    def read(self):
        """ Read a transcription from a file.

        :param filename: (str) the file name (including path)
        :raises: IOError, UnicodeError, Exception
        :returns: Transcription

        """
        try:
            trs = sppasRW.create_trs_from_extension(self.__filename)
        except KeyError:
            trs = sppasRW.create_trs_from_heuristic(self.__filename)

        try:
            trs.read(self.__filename)
        except IOError:
            raise
        except UnicodeError as e:
            raise AioEncodingError(self.__filename, e)

        return trs

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_extension(filename):
        """ Return a transcription according to a given filename.
        Only the extension of the filename is used.

        :param filename: (str)
        :returns: Transcription()

        """
        extension = os.path.splitext(filename)[1][1:]
        try:
            return sppasRW.TRANSCRIPTION_TYPES[extension.lower()]()
        except KeyError:
            raise KeyError("Unrecognized file extension: %s" % extension)

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_heuristic(filename):
        """ Return a transcription according to a given filename.
        The given file is opened and an heuristic allows to fix the format.

        :param filename: (str)
        :returns: Transcription()

        """
        for file_reader in sppasRW.TRANSCRIPTION_TYPES.values():
            try:
                if file_reader.detect(filename) is True:
                    return file_reader()
            except Exception:
                continue
        return RawText()

    # -----------------------------------------------------------------------

    def write(self, transcription):
        """ Write a transcription into a file.

        :param transcription: (str)

        """
        trs_rw = sppasRW.create_trs_from_extension(self.__filename)
        trs_rw.set(transcription)
        trs_rw.write(self.__filename)
