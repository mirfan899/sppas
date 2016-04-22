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
# File: audiosspaspresenter.py
# ----------------------------------------------------------------------------


__docformat__ = """epytext"""
__authors__   = """Nicolas Chazeau (n.chazeau94@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import signals
from signals.audio import Audio
from signals.channel import Channel
from signals.channelformatter import ChannelFormatter

# ----------------------------------------------------------------------------

class AudioSppasPresenter:
    """
    @authors: Nicolas Chazeau, Brigitte Bigi
    @contact: n.chazeau94@gmail.com, brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: An audio presenter class to have the specifications needed by automatic alignment in SPPAS.

    """

    def __init__(self, logfile=None):
        """
        Create a AudioSppasPresenter.

        """
        self._logfile = logfile
        self._reqSamplewidth = 2
        self._reqFramerate   = 16000
        self._reqChannels    = 1

    # End __init__
    # ------------------------------------------------------------------------

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_sampwidth(self):
        """
        Return the sample width required by automatic alignment in SPPAS.

        @return the sample width required by SPPAS

        """
        return self._reqSamplewidth

    def get_framerate(self):
        """
        Return the framerate required by automatic alignment in SPPAS.

        @return the frame rate required by SPPAS

        """
        return self._reqFramerate

    def get_nchannels(self):
        """
        Return the number of channels required by automatic alignment in SPPAS.

        @return the number of channels authorized by SPPAS

        """
        return self._reqChannels

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def diagnosis(self, inputname):
        """
        Return True if the file corresponds to the requirements.

        @param inputname (string) name of the inputfile

        """
        toconvert = False
        audio = signals.open(inputname)

        if (self._reqSamplewidth != audio.get_sampwidth()):
            toconvert = True
        if (self._reqChannels != audio.get_nchannels()):
            toconvert = True
        if (self._reqFramerate != audio.get_framerate()):
            toconvert = True

        audio.close()
        return toconvert

    # ------------------------------------------------------------------------

    def export(self, inputname, outputname):
        """
        Create a new wav file with requested parameters.

        @param inputname (string) name of the inputfile
        @param reqSamplewidth (string) name of the outputfile

        """
        toconvert = False

        audio = signals.open(inputname)

        if (audio.get_sampwidth() < self._reqSamplewidth):
            raise NameError("The sample width of ("+str(audio.get_sampwidth())+") of the given file is not appropriate. " + str(self._reqSamplewidth) + " bytes required")

        if (audio.get_framerate() < self._reqFramerate):
            raise NameError("The framerate of "+str(audio.get_framerate())+" Hz of the given file is not appropriate: " + str(self._reqFramerate) + " Hz required")

        if (self._reqSamplewidth != audio.get_sampwidth()):
            toconvert = True
            if self._logfile:
                self._logfile.print_message("The sample width of ("+str(audio.get_sampwidth())+") of the given file is not appropriate. Sample width is changed to " + str(self._reqSamplewidth) + " bytes", indent=3, status=1)

        if (self._reqChannels != audio.get_nchannels()):
            toconvert = True
            if self._logfile:
                self._logfile.print_message("The number of channels of ("+str(audio.get_nchannels())+") of the given file is not appropriate. Number of channels is changed to " + str(self._reqChannels) + " channels", indent=3, status=1)

        if (self._reqFramerate != audio.get_framerate()):
            toconvert = True
            if self._logfile:
                self._logfile.print_message("The framerate of "+str(audio.get_framerate())+" Hz is not appropriate: " + str(self._reqFramerate) + " Hz required.", indent=3, status=1)

        if toconvert is True:
            # Get the expected channel
            idx = audio.extract_channel(0)
            # no more need of input data, can close
            audio.close()

            # Do the job (do not modify the initial channel).
            formatter = ChannelFormatter( audio.get_channel(idx) )
            formatter.set_framerate(self._reqFramerate)
            formatter.set_sampwidth(self._reqSamplewidth)
            formatter.convert()

            # Save the converted channel
            audio_out = Audio()
            audio_out.append_channel( formatter.channel )
            signals.save( outputname, audio_out )

        return toconvert

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------
