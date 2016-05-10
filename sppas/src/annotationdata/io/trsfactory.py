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
# File: trsfactory.py
# ---------------------------------------------------------------------------

from text          import RawText, CSV
from praat         import TextGrid, PitchTier, IntensityTier
from signaix       import HzPitch
from transcriber   import Transcriber
from xra           import XRA
from phonedit      import Phonedit
from htk           import HTKLabel, MasterLabel
from subtitle      import SubRip, SubViewer
from sclite        import TimeMarkedConversation, SegmentTimeMark
from elan          import Elan
from anvil         import Anvil
from annotationpro import Antx
from xtrans        import Xtrans

# ----------------------------------------------------------------------------

class TrsFactory(object):
    """
    @authors:      Tatsuya Watanabe, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Factory for Transcription.

    """

    TRANSCRIPTION_TYPES = {
        "txt": RawText,
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
        "tdf": Xtrans
    }

    @staticmethod
    def NewTrs(trs_type):
        """
        Return a new Transcription() according to the format.

        @param trs_type (str) a file extension.
        @return Transcription()

        """
        try:
            return TrsFactory.TRANSCRIPTION_TYPES[trs_type.lower()]()
        except KeyError:
            raise KeyError("Unrecognized Transcription type: %s" % trs_type)

# ----------------------------------------------------------------------------
