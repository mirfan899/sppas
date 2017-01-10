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

import codecs
import os

import annotationdata.io
import audiodata.aio
from audiodata.audio import AudioPCM
from audiodata.channel import Channel

from sp_glob import encoding
from sp_glob import ERROR_ID, WARNING_ID, INFO_ID, OK_ID

# ----------------------------------------------------------------------------

class sppasDiagnosis:
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
        SPPAS files diagnosis.

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

    def checkfile(self, filename):
        """
        Return a status and a message depending on the fact that the file corresponds to the requirements.

        @param filename (string) name of the input file to diagnose.

        """
        ext = os.path.splitext( filename )[1]

        if ext.lower() in audiodata.aio.extensions:
            return self.audiofile( filename )

        if ext.lower() in annotationdata.io.extensions:
            return self.trsfile( filename )

        return (ERROR_ID,"Invalid. Unknown file extension %s."%ext)

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
            audio = audiodata.aio.open(inputname)
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
        # test encoding
        try:
            codecs.open(inputname,"r",encoding)
        except UnicodeDecodeError:
            return (ERROR_ID,"Invalid. Bad file encoding: only %s is accepted."%encoding)
        except Exception as e:
            return (ERROR_ID,"Invalid. %s."%str(e))

        # test US_ASCII  in filename
        try:
            str( inputname )
        except Exception:
            return (WARNING_ID,"Admit. File name should contain only US-ASCII characters.")

        # test whitespace and accents in filename
        if " " in inputname:
            return (WARNING_ID,"Admit. File name should not contain whitespace.")

        return (OK_ID,"Valid.")

    # ------------------------------------------------------------------------
