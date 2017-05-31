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

    src.annotations.sppasipusseg.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import os
import logging

import sppas.src.annotationdata.aio
import sppas.src.audiodata.aio
from sppas.src.annotationdata.aio.utils import gen_id
from sppas.src.annotationdata.transcription import Transcription
from sppas.src.annotationdata.media import Media
from sppas.src.audiodata.autils import times2frames

from .. import INFO_ID
from ..baseannot import sppasBaseAnnotation
from ..annotationsexc import AnnotationOptionError

from .ipusaudio import IPUsAudio  # find silences/tracks from audio
from .ipustrs import IPUsTrs      # find IPUs from transcription
from .ipusout import IPUsOut      # IPUs writer

# ------------------------------------------------------------------


class sppasIPUseg(sppasBaseAnnotation):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS integration of the IPUs segmentation.

    """
    def __init__(self, logfile=None):
        """ Create a sppasIPUseg instance.

        :param logfile: (sppasLog) a log system used to communicate
        messages to the user.

        """
        sppasBaseAnnotation.__init__(self, logfile)

        self.ipusaudio = IPUsAudio(None)  # Find IPUs from an audio file
        self.ipustrs = IPUsTrs(None)      # Get IPUs from a transcription file

        # List of options to configure this automatic annotation
        self._options['dirtracks'] = False
        self._options['save_as_trs'] = False
        self._options['addipuidx'] = False

    # ------------------------------------------------------------------

    def reset(self):
        """ Set default values. """

        self.ipusaudio.set_channel(None)
        self.ipustrs.set_transcription(None)

    # ------------------------------------------------------------------------
    # Methods to fix options
    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """ Fix all options. Available options are:

            - shift
            - shift_start
            - shift_end
            - min_speech
            - min_sil
            - tracks
            - save_as_trs
            - add_ipu_idx

        :param options: (sppasOption)

        """
        for opt in options:

            if "shift" == opt.get_key():
                self.ipusaudio.set_shift(opt.get_value())

            elif "shift_start" == opt.get_key():
                self.ipusaudio.set_shift_start(opt.get_value())

            elif "shift_end" == opt.get_key():
                self.ipusaudio.set_shift_end(opt.get_value())

            elif "min_speech" == opt.get_key():
                self.ipusaudio.set_min_speech(opt.get_value())

            elif "min_sil" == opt.get_key():
                self.ipusaudio.set_min_silence(opt.get_value())

            elif "min_vol" == opt.get_key():
                self.ipusaudio.set_vol_threshold(opt.get_value())

            elif "tracks" == opt.get_key():
                self.set_dirtracks(opt.get_value())

            elif "save_as_trs" == opt.get_key():
                self.set_save_as_trs(opt.get_value())

            elif "add_ipu_idx" == opt.get_key():
                self.set_addipuidx(opt.get_value())

            else:
                raise AnnotationOptionError(key)

    # ------------------------------------------------------------------------

    def set_dirtracks(self, value):
        """ Fix the "dirtracks" option.

        :param value: (bool)

        """
        self._options['dirtracks'] = value

    # ------------------------------------------------------------------------

    def set_save_as_trs(self, value):
        """ Fix the "save as transcription" option.

        :param value: (bool)

        """
        self._options['save_as_trs'] = value

    # ------------------------------------------------------------------------

    def set_addipuidx(self, value):
        """ Fix the "add IPU index in the transcription output" option.

        :param value: (bool)

        """
        self._options['addipuidx'] = bool(value)

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def get_transcription(self, input_filename, tier_idx=None):
        """ Extract transcription from a file, either time-aligned or not.

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

        :param input_filename: (str) Name of the input file
        :param tier_idx: (int) Force the tier index for the transcription
        :returns: Transcription

        """
        if input_filename is None:
            return Transcription()

        trs_input = sppas.src.annotationdata.aio.read(input_filename)
        # input is a simple text file
        if input_filename.lower().endswith("txt"):
            if trs_input.GetSize() != 1:
                raise IOError('Error while reading file (expected one tier. Got %d)' % trs_input.GetSize())
            return trs_input

        # input is a time-aligned file
        if tier_idx is None:
            trs_tier = None
            # priority: try to find a tier with "trans" in its name
            for tier in trs_input:
                tier_name = tier.GetName().lower()
                if "trans" in tier_name:
                    trs_tier = tier
                    break
            if trs_tier is None:
                # try other tier names
                for tier in trs_input:
                    tier_name = tier.GetName().lower()
                    if "trs" in tier_name or "ortho" in tier_name or "toe" in tier_name or "ipu" in tier_name:
                        trs_tier = tier
                        break
            if trs_tier is None:
                raise IOError('No tier with transcription found.')
        else:
            trs_tier = trs_input[tier_idx]

        trs_output = Transcription("Output")
        if self.logfile:
            self.logfile.print_message("IPUs+Transcription tier found: %s" % trs_tier.GetName(), indent=3, status=INFO_ID)

        trs_tier.SetName('Transcription')
        trs_output.Append(trs_tier)

        # Expected IPUs file names
        for tier in trs_input:
            tier_name = tier.GetName().lower()
            if "name" in tier_name or "file" in tier_name:
                if self.logfile:
                    self.logfile.print_message("IPUs file names found: %s" % tier.GetName(), indent=3, status=INFO_ID)
                tier.SetName('Name')
                trs_output.Append(tier)
                break

        return trs_output

    # ------------------------------------------------------------------

    def split(self, nbipus=0):
        """ Blind or controlled speech/silence segmentation.

        :param nbtracks: (int) Expected number of IPUs. 0=automatic.

        """
        if self.ipusaudio.get_channel() is None:
            raise Exception("No speech data.\n")

        if self.ipusaudio.get_channel().get_duration() <= self.ipusaudio.min_channel_duration():
            raise Exception("Audio file is too short.\n")

        n = self.ipusaudio.split_into(nbipus)
        if n != nbipus:
            raise Exception("Silence detection failed: unable to find "+str(nbipus)+" Inter-Pausal Units. Got: %d." % n)

        if self.logfile:
            self.logfile.print_message("Threshold volume value:     "+str(self.ipusaudio.get_vol_threshold()), indent=3)
            self.logfile.print_message("Threshold silence duration: "+str(self.ipusaudio.get_min_sil_dur()),   indent=3)
            self.logfile.print_message("Threshold speech duration:  "+str(self.ipusaudio.get_min_ipu_dur()),   indent=3)
        else:
            logging.info("Threshold volume value:     "+str(self.ipusaudio.get_vol_threshold()))
            logging.info("Threshold silence duration: "+str(self.ipusaudio.get_min_sil_dur()))
            logging.info("Threshold speech duration:  "+str(self.ipusaudio.get_min_ipu_dur()))

    # ------------------------------------------------------------------
    # Outputs
    # ------------------------------------------------------------------

    def run(self, audiofile, trsinputfile=None, trstieridx=None, ntracks=None, diroutput=None, tracksext=None, trsoutput=None):
        """ Perform an IPU segmentation from an audio file.

        :param audiofile: (str) the speech audio input file name
        :param trsinputfile: (str) the transcription file name (or 'None')
        :param trstieridx: (int)
        :param ntracks: (int) an expected number of IPUs (or 'None')
        :param diroutput: (str) a directory name to save output IPUs (one per unit)
        :param tracksext: (str) the file extension for IPUs (used with the diroutput option)
        :param trsoutput: (str) a file name to save the IPUs segmentation result.

        """
        self.print_options()
        self.print_diagnosis(audiofile)

        # Get the inputs.
        # ---------------

        # Get audio and the channel we'll work on
        audiospeech = sppas.src.audiodata.aio.open(audiofile)
        idx = audiospeech.extract_channel()
        channel = audiospeech.get_channel(idx)
        self.ipusaudio.set_channel(channel)

        # Fix transcription (if a transcription is given)
        trs = self.get_transcription(trsinputfile, trstieridx)

        # Assign the audio file as Media to the extracted transcription instance.
        extm = os.path.splitext(audiofile)[1].lower()[1:]
        media = Media(gen_id(), os.path.abspath(audiofile), "audio/"+extm)
        trs.AddMedia(media)
        for tier in trs:
            tier.SetMedia(media)

        # Set the Transcription
        self.ipustrs.set_transcription(trs)
        (trackslist, silences) = self.ipustrs.extract()

        # Process the data.
        # -----------------

        # We got tracks from the transcription
        if len(trackslist) > 0:
            # but we have time in seconds. we expect frames...
            fm = channel.get_framerate()
            trackslist = times2frames(trackslist, fm)

        # We got silences from the transcription
        if len(silences) > 0:
            # but we have time in seconds. we expect frames...
            fm = channel.get_framerate()
            silences = times2frames(silences, fm)
            # inject silences in the IPUsAudio
            # (so it won't have to find them automatically)
            self.ipusaudio.set_silences(silences)

        else:

            # Fix if we have to find silences at start and end of the speech
            (bs, be) = self.ipustrs.extract_bounds()
            self.ipusaudio.set_bound_start(bs)
            self.ipusaudio.set_bound_end(be)

            # Fix the number of tracks to split into
            if ntracks is None:
                ntracks = len(self.ipustrs.get_units())  # 0 = automatic!

            # Find automatically silences and tracks
            self.split(ntracks)
            trackslist = self.ipusaudio.extract_tracks()

        # No tracks? Find them from the audio.
        if len(trackslist) == 0:
            trackslist = self.ipusaudio.extract_tracks(shift_start=0., shift_end=0.)

        # Save output(s).
        # ---------------
        ipusout = IPUsOut(None)   # IPUs writer
        ipusout.set_tracks(trackslist)

        # Create a Transcription from tracks and units
        trs = ipusout.tracks2transcription(self.ipustrs, self.ipusaudio, self._options['addipuidx'])

        # Assign unit contents if it was not already done.
        if len(self.ipustrs.get_units()) == 0:
            self.ipustrs.set_transcription(trs)
            self.ipustrs.extract_units()

        # Write the tracks into a transcription file.
        if trsoutput is not None:
            try:
                sppas.src.annotationdata.aio.write(trsoutput, trs)
            except Exception as e:
                raise Exception('Error while saving the transcription output.\n'+str(e)+'\n')

        # Write audio/units into separated track files
        if diroutput is not None or self._options['dirtracks'] is True:
            if diroutput is None:
                fileName = os.path.splitext(audiofile)[0]
                diroutput = fileName+"-ipus"

            if os.path.exists(diroutput) is False:
                os.mkdir(diroutput)

            if self.logfile is not None:
                self.logfile.print_message(str(len(self.ipustrs.get_units()))+" units to write.", indent=3)

            # Write the list output files and the tracks
            listoutput = os.path.join(diroutput, "index.txt")
            ipusout.write_list(listoutput, self.ipustrs, self.ipusaudio)
            if self._options['save_as_trs'] is True and tracksext is None:
                tracksext = "TextGrid"
            ipusout.write_tracks(self.ipustrs, self.ipusaudio, diroutput, tracksext, "wav")
