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

from .text import RawText, CSV
from .praat import TextGrid, PitchTier, IntensityTier
from .signaix import HzPitch
from .transcriber import Transcriber
from .xra import XRA
from .phonedit import Phonedit
from .htk import HTKLabel, MasterLabel
from .subtitle import SubRip, SubViewer
from .sclite import TimeMarkedConversation, SegmentTimeMark
from .elan import Elan
from .anvil import Anvil
from .annotationpro import Antx
from .xtrans import Xtrans
from .audacity import Audacity

# ----------------------------------------------------------------------------


class sppasRW(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Readers and writers of annotated data.

    """
    TRANSCRIPTION_TYPES = {
        "csv": CSV,
        "intensitytier": IntensityTier,
        "pitchtier": PitchTier,
        "hz": HzPitch,
        "textgrid": TextGrid,
        "trs": Transcriber,
        "xra": XRA,
        "mrk": Phonedit,
        "lab": HTKLabel,
        "mlf": MasterLabel,
        "srt": SubRip,
        "sub": SubViewer,
        "ctm": TimeMarkedConversation,
        "stm": SegmentTimeMark,
        "eaf": Elan,
        "anvil": Anvil,
        "antx": Antx,
        "tdf": Xtrans,
        "aup": Audacity,
        "txt": RawText
    }

    # -----------------------------------------------------------------------

    def __init__(self):
        pass

    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a transcription from a file.

        :param filename: (str) the file name (including path)
        :raises: IOError, UnicodeError, Exception
        :returns: Transcription

        """
        try:
            trs = sppasRW.create_trs_from_extension(filename)
        except KeyError:
            trs = sppasRW.create_trs_from_heuristic(filename)

        try:
            #transcription.read(unicode(filename))
            trs.read(filename)
        except IOError:
            raise
        except UnicodeError as e:
            raise UnicodeError('Encoding error: the file %r contains non-UTF-8 characters: %s' % (filename, e))

        # Each reader has its own solution to assign min and max.
        # Anyway, here we take care, if one missed to assign the values!
        # if transcription.GetMinTime() is None:
        #    transcription.SetMinTime(transcription.GetBegin())
        # if transcription.GetMaxTime() is None:
        #    transcription.SetMaxTime(transcription.GetEnd())

        return trs

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_extension(filename):
        """ Return a new Transcription() according to a given filename.
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
        """ Return a new Transcription() according to a given filename.
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
