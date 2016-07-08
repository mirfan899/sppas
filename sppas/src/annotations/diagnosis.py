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
# File: diagnosis.py
# ----------------------------------------------------------------------------

import audiodata
from audiodata.audio import AudioPCM
from audiodata.channel import Channel

from sp_glob import encoding
from sp_glob import ERROR_ID, WARNING_ID, INFO_ID, OK_ID

import annotationdata.io
import codecs

# ----------------------------------------------------------------------------

class SppasDiagnosis:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      A class to diagnose if files are appropriate for SPPAS.

    """
    def __init__(self, logfile=None):
        """
        SppasDiagnosis.

        """
        self._logfile = logfile

        # for audio
        self._reqSamplewidth = 2
        self._reqFramerate   = 16000
        self._reqChannels    = 1

        # for transcriptions
        self._encoding = encoding

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def audiofile(self, inputname):
        """
        Return a status and a message depending on the fact that the file corresponds to the requirements.

        @param inputname (string) name of the inputfile

        """
        status  = OK_ID
        message = "Valid."

        # test file format: can we support it?
        try:
            audio = audiodata.io.open(inputname)
            fm = audio.get_framerate()
            sp = audio.get_sampwidth()*8
            nc = audio.get_nchannels()
            audio.close()
        except Exception as e:
            return (ERROR_ID,str(e))

        if nc > 1:
            status = ERROR_ID
            message = "Invalid. Audio file must contain only 1 channel. Got %d."%(audio.get_nchannels())

        elif sp < 16:
            status = ERROR_ID
            message = "Invalid. Sample width must be at least 16 bits. Got %d."%(sp)

        elif fm < 16000:
            status = ERROR_ID
            message = "Invalid. The frame rate of audio file must be at least 16000 Hz. Got %d."%(fm)

        elif sp > 16:
            status = WARNING_ID
            message = "Admit. Sample width is preferably 16 bits. Got %d. SPPAS will work on a converted file."%(sp)

        elif fm > 16000:
            status = WARNING_ID
            message = "Admit. The frame rate of audio file is preferably 16000 Hz. Got %d. SPPAS will work on a converted file."%(fm)

        # append in message: test whitespace and accents in filename

        return (status,message)

    # ------------------------------------------------------------------------

    def trsfile(self, inputname):
        """
        Return a status and a message depending on the fact that the file corresponds to the requirements.

        @param inputname (string) name of the inputfile

        """
        status  = OK_ID
        message = "Valid or Admit."

        # test encoding
        try:
            codecs.open(inputname,"r",encoding)
        except Exception as e:
            return (ERROR_ID,"Invalid. "+str(e))

        # test whitespace and accents in filename

        # test extension
        # exists or heuristic...

        return (status,message)

    # ------------------------------------------------------------------------
