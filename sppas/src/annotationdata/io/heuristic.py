#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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


from text import RawText, CSV
from praat import TextGrid, PitchTier, IntensityTier
from signaix import HzPitch
from transcriber import Transcriber
from xra import XRA
from phonedit import Phonedit
from htk import Label, MasterLabel
from subtitle import SubRip, SubViewer
from sclite import TimeMarkedConversation, SegmentTimeMark
from elan import Elan


class HeuristicFactory(object):
    __OPTS = [
        TextGrid,
        IntensityTier,
        PitchTier,
        Transcriber,
        XRA,
        # Phonedit,
        # Label,
        # MasterLabel,
        # SubRip,
        # SubViewer,
        # TimeMarkedConversation,
        # SegmentTimeMark,
        # Elan,
        CSV,
        HzPitch,
        RawText  # must be last
    ]

    @staticmethod
    def NewTrs(filename):
        """
        Return a new Transcription.

        @param trs_type:

        @return Transcription

        """
        for type in HeuristicFactory.__OPTS:
            try:
                if type.detect(filename):
                    return type()
            except Exception:
                continue

    # End NewTrs
    # -----------------------------------------------------------------
