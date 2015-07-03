#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.

from ascii import Ascii
from ctm import ScliteCTM
from eaf import Elan
from intensity import Intensity
from julius import JuliusIO
from pitch import Pitch
from tag import TranscriberAG
from textgrid import TextGrid
from trs import Transcriber


class TrsFactory(object):
    """
    Factory for Transcription.
    """

    __TRS = {"txt": Ascii,
             "liatxt": Ascii,
             "info": Ascii,
             "csv": Ascii,
             "lab": Ascii,
             "ipulab": Ascii,
             "ctm": ScliteCTM,
             "eaf": Elan,
             "intensity": Intensity,
             "julius": JuliusIO,
             "pitchtier": Pitch,
             "hz": Pitch,
             "tag": TranscriberAG,
             "textgrid": TextGrid,
             "trs": Transcriber
            }

    @staticmethod
    def NewTrs(trs_type):
        """ Return a new Transcription.
            Parameters:
                - trs_type
            Exception:   Exception
            Return:      Transcription
        """
        try:
           return TrsFactory.__TRS[trs_type]()
        except KeyError:
            raise Exception("Unrecognized Transcription type: %s" % trs_type)
