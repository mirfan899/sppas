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
# File: ipusseg.py
# ----------------------------------------------------------------------------

import os
import logging

from sp_glob import ERROR_ID, WARNING_ID, OK_ID, INFO_ID

import annotationdata.io
from annotationdata.io.utils import gen_id
import audiodata.io
from audiodata.audiovolume        import AudioVolume
from audiodata.channel            import Channel
from annotationdata.transcription import Transcription
from annotationdata.media         import Media

from annotations.IPUs.ipusaudio import IPUsAudio # find IPUs/tracks from audio
from annotations.IPUs.ipustrs   import IPUsTrs   # find IPUs/tracks/utterances from transcription
from annotations.IPUs.ipusout   import IPUsOut   # IPUs Output (writer)
from audiodata.autils import frames2times, times2frames

from annotations.sppasbase import sppasBase

# ------------------------------------------------------------------
# Main class
# ------------------------------------------------------------------

class sppasIPUs( sppasBase ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS integration of the IPUs segmentation.

    """
    def __init__(self, logfile=None):
        """
        Create a sppasIPUs instance.

        @param logfile (sppasLog) a log file mainly used to print messages
                to the user.

        """
        sppasBase.__init__(self, logfile)

        self.ipusaudio = IPUsAudio(None) # Find IPUs from an audio file
        self.ipustrs   = IPUsTrs(None)   # Get IPUs from a transcription file
        self.reset()

    # ------------------------------------------------------------------

    def reset(self):
        """
        Set default values.

        """
        # List of options to configure this automatic annotation
        self._options = {}
        self._options['dirtracks']   = False
        self._options['save_as_trs'] = False
        self._options['addipuidx']   = False

        # The workers
        self.ipusaudio.set_channel(None)
        self.ipustrs.set_transcription(None)

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        @param options (option)

        """
        for opt in options:

            if "shift" == opt.get_key():
                self.ipusaudio.set_shift( opt.get_value() )

            elif "shift_start" == opt.get_key():
                self.ipusaudio.set_shift_start( opt.get_value() )

            elif "shift_end" == opt.get_key():
                self.ipusaudio.set_shift_end( opt.get_value() )

            elif "min_speech" == opt.get_key():
                self.ipusaudio.set_min_speech( opt.get_value() )

            elif "min_sil" == opt.get_key():
                self.ipusaudio.set_min_silence( opt.get_value() )

            elif "min_vol" == opt.get_key():
                self.ipusaudio.set_vol_threshold( opt.get_value() )

            elif "tracks" == opt.get_key():
                self.set_dirtracks( opt.get_value() )

            elif "save_as_trs" == opt.get_key():
                self.set_save_as_trs(opt.get_value())

            elif "add_ipu_idx" == opt.get_key():
                self.set_addipuidx(opt.get_value())

    # ------------------------------------------------------------------------

    def set_dirtracks(self, value):
        """
        Fix the "dirtracks" option (boolean).

        @param value (bool)

        """
        self._options['dirtracks'] = value

    # ------------------------------------------------------------------------

    def set_save_as_trs(self, value):
        """
        Fix the "save as transcription" option (boolean).

        @param value (bool)

        """
        self._options['save_as_trs'] = value

    # ------------------------------------------------------------------------

    def set_addipuidx(self, value):
        """
        Fix the "add IPU index in the transcription output" option (boolean).

        @param value (bool)

        """
        self._options['addipuidx'] = bool(value)


    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def get_transcription(self, inputfilename, tieridx=None):
        """
        Extract transcription from a file, either time-aligned or not.

        If input is a simple text file, it must be formatted like:
            - each line is supposed to be at least one unit;
            - each '#' symbol is considered as a unit boundary.
            - both can be combined.

        If input is a time-aligned file, the expected tier name for the
        transcription are:
            - priority: trans in the tier name;
            - secondary: trs, ortho, toe or ipu in the tier name.
        It also extracts IPUs file names if any, i.e. a tier with name
        "Name" or "File".

        @param inputfilename (str) the input file name
        @param tieridx (int) Force the tier index for the transcription
        @return Transcription

        """
        if inputfilename is None:
            return Transcription()

        trsinput = annotationdata.io.read( inputfilename )
        # input is a simple text file
        if inputfilename.lower().endswith("txt"):
            if trsinput.GetSize() != 1:
                raise IOError('Error while reading file (expected one tier. Got %d)'%trsinput.GetSize())
            return trsinput

        # input is a time-aligned file
        if tieridx is None:
            # priority: try to find a tier with "trans" in its name
            for tier in trsinput:
                tiername = tier.GetName().lower()
                if "trans" in tiername:
                    trstier = tier
                    break
            if trstier is None:
                # try other tier names
                for tier in trsinput:
                    tiername = tier.GetName().lower()
                    if "trs" in tiername or "ortho" in tiername or "toe" in tiername or "ipu" in tiername:
                        trstier = tier
                        break
            if trstier is None:
                raise IOError('No tier with transcription found.')
        else:
            trstier = trsinput[tieridx]

        trsoutput = Transcription("Output")
        if self.logfile:
            self.logfile.print_message("IPUs+Transcription tier found: %s"%trstier.GetName(), indent=3, status=INFO_ID)

        trstier.SetName('Transcription')
        trsoutput.Append(trstier)

        # Expected IPUs file names
        for tier in trsinput:
            tiername = tier.GetName().lower()
            if "name" in tiername or "file" in tiername:
                if self.logfile:
                    self.logfile.print_message("IPUs file names found: %s"%tier.GetName(), indent=3, status=INFO_ID)
                tier.SetName('Name')
                trsoutput.Append(tier)
                break

        return trsoutput

    # ------------------------------------------------------------------

    def split(self, nbipus=0):
        """
        Blind or controlled speech/silence segmentation.

        @param nbtracks (int) Expected number of IPUs. 0=automatic.

        """
        if self.ipusaudio.get_channel() is None:
            raise Exception("No speech data.\n")

        if self.ipusaudio.get_channel().get_duration() <= self.ipusaudio.min_channel_duration():
            raise Exception("Audio file is too short.\n")

        n = self.ipusaudio.split_into( nbipus )
        if n != nbipus:
            raise Exception("Silence detection failed: unable to find "+str(nbipus)+" Inter-Pausal Units. Got: %d."%n)

        if self.logfile:
            self.logfile.print_message("Threshold volume value:     "+str(self.ipusaudio.vol_threshold), indent=3)
            self.logfile.print_message("Threshold silence duration: "+str(self.ipusaudio.min_sil_dur),   indent=3)
            self.logfile.print_message("Threshold speech duration:  "+str(self.ipusaudio.min_ipu_dur),   indent=3)
        else:
            logging.info("Threshold volume value:     "+str(self.ipusaudio.vol_threshold))
            logging.info("Threshold silence duration: "+str(self.ipusaudio.min_sil_dur))
            logging.info("Threshold speech duration:  "+str(self.ipusaudio.min_ipu_dur))

    # ------------------------------------------------------------------
    # Outputs
    # ------------------------------------------------------------------

    def run(self, audiofile, trsinputfile=None, trstieridx=None, ntracks=None, diroutput=None, tracksext=None, trsoutput=None):
        """
        Perform an IPU segmentation from an audio file.

        @param audiofile (str) the speech audio input file name
        @param trsinputfile (str) the transcription file name (or 'None')
        @param ntracks (int) an expected number of IPUs (or 'None')
        @param diroutput (str) a directory name to save output IPUs (one per unit)
        @param tracksext (str) the file extension for IPUs (used with the diroutput option)
        @param trsoutput (str) a file name to save the IPUs segmentation result.

        """
        self.print_options()
        self.print_diagnosis(audiofile)

        # Get the inputs.
        # ---------------

        # Get audio and the channel we'll work on
        audiospeech = audiodata.io.open( audiofile )
        idx         = audiospeech.extract_channel()
        channel     = audiospeech.get_channel(idx)
        self.ipusaudio.set_channel( channel )

        # Fix transcription (if a transcription is given)
        trs = self.get_transcription(trsinputfile, trstieridx)

        # Assign the audio file as Media to the extracted transcription instance.
        extm = os.path.splitext(audiofile)[1].lower()[1:]
        media = Media( gen_id(), os.path.abspath(audiofile), "audio/"+extm )
        trs.AddMedia( media )
        for tier in trs:
            tier.SetMedia( media )

        # Set the Transcription
        self.ipustrs.set_transcription( trs )
        (trackslist,silences) = self.ipustrs.extract()

        # Process the data.
        # -----------------

        # We got tracks from the transcription
        if len(trackslist) > 0:
            # but we have time in seconds. we expect frames...
            fm = channel.get_framerate()
            trackslist = times2frames( trackslist, fm )

        # We got silences from the transcription
        if len(silences) > 0:
            # but we have time in seconds. we expect frames...
            fm = channel.get_framerate()
            silences = times2frames( silences, fm )
            # inject silences in the IPUsAudio
            # (so it won't have to find them automatically)
            self.ipusaudio.set_silences( silences )

        else:

            # Fix if we have to find silences at start and end of the speech
            (bs,be) = self.ipustrs.extract_bounds()
            self.ipusaudio.set_bound_start(bs)
            self.ipusaudio.set_bound_end(be)

            # Fix the number of tracks to split into
            if ntracks is None:
                ntracks = len( self.ipustrs.get_units() ) # 0 = automatic!

            # Find automatically silences and tracks
            self.split( ntracks )
            trackslist = self.ipusaudio.extract_tracks()

        # No tracks? Find them from the audio.
        if len(trackslist) == 0:
            trackslist = self.ipusaudio.extract_tracks(shift_start=0., shift_end=0.)

        # Save output(s).
        # ---------------
        ipusout = IPUsOut(None)   # IPUs writer
        ipusout.set_tracks( trackslist )

        # Create a Transcription from tracks and units
        trs = ipusout.tracks2transcription(self.ipustrs, self.ipusaudio, self._options['addipuidx'])

        # Assign unit contents if it was not already done.
        if len(self.ipustrs.get_units()) == 0:
            self.ipustrs.set_transcription( trs )
            self.ipustrs.extract_units()

        # Write the tracks into a transcription file.
        if trsoutput is not None:
            try:
                annotationdata.io.write(trsoutput, trs)
            except Exception as e:
                raise Exception('Error while saving the transcription output.\n'+str(e)+'\n')

        # Write audio/units into separated track files
        if diroutput is not None or self._options['dirtracks'] is True:
            if diroutput is None:
                fileName = os.path.splitext( audiofile )[0]
                diroutput = fileName+"-ipus"

            if os.path.exists(diroutput) is False:
                os.mkdir( diroutput )

            if self.logfile is not None:
                self.logfile.print_message(str(len(self.ipustrs.get_units()))+" units to write.", indent=3)

            # Write the list output files and the tracks
            listoutput = os.path.join(diroutput, "index.txt")
            ipusout.write_list(listoutput, self.ipustrs, self.ipusaudio)
            if self._options['save_as_trs'] is True and tracksext is None:
                tracksext="TextGrid"
            ipusout.write_tracks(self.ipustrs, self.ipusaudio, diroutput, tracksext, "wav" )

    # ------------------------------------------------------------------
