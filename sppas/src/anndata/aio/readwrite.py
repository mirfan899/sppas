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

    src.anndata.aio.readwrite.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Readers and writers of annotated data.

"""
import os.path
from collections import OrderedDict

from sppas.src.utils.makeunicode import u

from ..anndataexc import AioEncodingError
from ..anndataexc import AioFileExtensionError

from .xra import sppasXRA
from .text import sppasRawText
# from .text import CSV
from .praat import sppasTextGrid  #, PitchTier, IntensityTier
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
    TRANSCRIPTION_TYPES = OrderedDict()
    TRANSCRIPTION_TYPES["xra"] = sppasXRA
    TRANSCRIPTION_TYPES["textgrid"] = sppasTextGrid
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
    TRANSCRIPTION_TYPES["txt"] = sppasRawText

    # -----------------------------------------------------------------------

    @staticmethod
    def extensions():
        """ Return the list of supported extensions in lower case. """

        return sppasRW.TRANSCRIPTION_TYPES.keys()

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

    def read(self, heuristic=True):
        """ Read a transcription from a file.

        :param heuristic: (bool) if the extension of the file is unknown,
        use an heuristic to detect the format, then to choose the reader-writer.
        :returns: sppasTranscription reader-writer

        """
        try:
            trs = sppasRW.create_trs_from_extension(self.__filename)
        except AioFileExtensionError:
            if heuristic is True:
                trs = sppasRW.create_trs_from_heuristic(self.__filename)
            else:
                raise

        try:
            trs.read(self.__filename)
        except UnicodeError as e:
            raise AioEncodingError(self.__filename, e)
        except Exception:
            raise

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
        extension = extension.lower()
        if extension in sppasRW.extensions():
            return sppasRW.TRANSCRIPTION_TYPES[extension]()

        raise AioFileExtensionError(filename)

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
        return sppasRawText()

    # -----------------------------------------------------------------------

    def write(self, transcription):
        """ Write a transcription into a file.

        :param transcription: (str)

        """
        trs_rw = sppasRW.create_trs_from_extension(self.__filename)
        trs_rw.set(transcription)

        try:
            trs_rw.write(self.__filename)
        except UnicodeError as e:
            raise AioEncodingError(self.__filename, e)
        except Exception:
            raise
