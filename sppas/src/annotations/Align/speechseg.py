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
# File: speechseg.py
# ----------------------------------------------------------------------------

import os.path
import codecs
import re

from sp_glob import encoding

import audiodata
from audiodata.channel    import Channel
from audiodata.channelsilence import ChannelSilence

from resources.mapping  import Mapping

from presenters.audiosilencepresenter import AudioSilencePresenter

from juliusalign    import JuliusAligner
from hvitealign     import HviteAligner
from basicalign     import BasicAligner

from resources.rutils   import ToStrip

# ----------------------------------------------------------------------------

class SpeechSegmenter:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Automatic speech segmentation.

    Speech segmentation of a unit of speech (an IPU/utterance/sentence/segment).

    """
    # List of supported aligners (with lowered names)
    # Notice that the basic aligner can be used to align without audio file!
    ALIGNERS = ['julius', 'hvite', 'basic']

    # ------------------------------------------------------------------------

    def __init__(self, model, alignername="julius"):
        """
        Constructor.

        @param model is the acoustic model directory name. It is expected
        to contain at least a file with name "hmmdefs". It can also contain:
            - tiedlist file;
            - monophones.repl file;
            - config file.
        Any other file will be ignored.

        """
        # Options, must be fixed before to instantiate the aligner
        self._infersp = False

        # The acoustic model directory
        self._modeldir = model

        # Map phoneme names from model-specific to SAMPA and vice-versa
        mappingfilename = os.path.join( self._modeldir, "monophones.repl")
        if os.path.isfile( mappingfilename ):
            try:
                self._mapping = Mapping( mappingfilename )
            except Exception:
                self._mapping = Mapping()
        else:
            self._mapping = Mapping()

        # The automatic alignment system:
        # The basic aligner is used:
        #   - when the IPU contains only one phoneme;
        #   - when the automatic alignment system failed to perform segmn.
        self.set_aligner(alignername)
        self._basicaligner = BasicAligner(model, self._mapping)
        self._instantiate_aligner()

    # ------------------------------------------------------------------------

    def set_model(self, model):
        """
        Fix an acoustic model to perform time-alignment.

        @param model (string) Directory that contains the Acoustic Model.

        """
        self._modeldir = model
        self._instantiate_aligner()

    # ----------------------------------------------------------------------

    def set_aligner(self, alignername):
        """
        Fix the name of the aligner, one of ALIGNERS.

        @param alignername (string) Case-insensitive name of an aligner system.

        """
        alignername = alignername.lower()
        if not alignername in SpeechSegmenter.ALIGNERS:
            raise ValueError('Unknown aligner name.')

        self._alignerid = alignername
        self._instantiate_aligner()

    # ----------------------------------------------------------------------

    def set_infersp(self, infersp):
        """
        Fix the automatic inference of short pauses.

        @param infersp (bool) If infersp is set to True, a short pause is
        added at the end of each token, and the automatic aligner will infer
        if it is relevant or not.

        """
        self._infersp = infersp
        self._aligner.set_infersp( infersp )

    # ----------------------------------------------------------------------

    def get_aligner(self):
        """
        Return the aligner name.

        """
        return self._alignerid

    # ----------------------------------------------------------------------

    def get_model(self):
        """
        Return the model directory name.

        """
        return self._modeldir

    # ----------------------------------------------------------------------

    def split(self, inputaudio, trstier, diralign, extension, listfile=None):
        """
        Split all the data into tracks.

        @param trstier is the tier to split
        @param diralign is the directory to put units.
        @param extension is the file extension of units.

        @return tuple with number of silences and number of tracks

        """
        audiospeech = audiodata.io.open( inputaudio )
        idx         = audiospeech.extract_channel()
        channel     = audiospeech.get_channel(idx)
        chansil     = ChannelSilence( channel )
        framerate   = channel.get_framerate()
        duration    = float(channel.get_nframes())/float(framerate)

        trstracks = []
        silence   = []
        trsunits  = []
        i = 0
        last = trstier.GetSize()
        while i < last:
            # Set the current annotation values
            __ann   = trstier[i]
            __label = __ann.GetLabel().GetValue()
            # Save information
            if __ann.GetLabel().IsSilence():
                __start = int(__ann.GetLocation().GetBegin().GetMidpoint() * framerate)
                __end   = int(__ann.GetLocation().GetEnd().GetMidpoint()   * framerate)
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    __nextann = trstier[i + 1]
                    while (i + 1) < last and __nextann.GetLabel().IsSilence():
                        __end = int(__nextann.GetLocation().GetEnd().GetMidpoint() * framerate)
                        i = i + 1
                        if (i + 1) < last:
                            __nextann = trstier[i+1]
                silence.append((__start,__end))
            else:
                __start = int(__ann.GetLocation().GetBeginMidpoint() * framerate)
                __end   = int(__ann.GetLocation().GetEndMidpoint()   * framerate)
                trstracks.append((__start,__end))
                trsunits.append( __label )

            i = i+1
        # end while

        chansil.set_silences( silence )
        audiosilpres = AudioSilencePresenter(chansil)
        audiosilpres.write_tracks(trstracks, diralign, ext=extension, trsunits=trsunits, trsnames=[])

        if listfile is not None:
            # write the list file
            with codecs.open(listfile ,'w', encoding) as fp:
                idx = 0
                for from_pos, to_pos in trstracks:
                    fp.write( "%.4f %.4f " %( float(from_pos)/float(framerate) , float(to_pos)/float(framerate) ))
                    fp.write( "\n" )
                    idx = idx+1
                # Finally, print audio file duration
                fp.write( "%.4f\n" % duration )

        return (len(silence), len(trstracks))

    # ------------------------------------------------------------------------

    def _readline(self, filename):
        """
        Return the first line of filename, formatted.

        """
        line = ""
        with codecs.open(filename, 'r', encoding) as fp:
            # Get the phoneme sequence
            line = fp.readline()

        return ToStrip(line)

    # ------------------------------------------------------------------------

    def segmenter(self, audiofilename, phonname, tokenname, alignname):
        """
        Call an aligner to perform speech segmentation and manage errors.

        @param audiofilename (str - IN) the audio file name of an IPU
        @param phonname (str - IN) the file name with the phonetization
        @param tokenname (str - IN) the file name with the tokenization
        @param alignname (str - OUT) the file name to save the result

        @return A message of the aligner in case of any problem, or
        an empty string if success.

        """
        # Get the phonetization and tokenization strings to time-align.
        phones = ""
        tokens = ""

        if phonname is not None:
            phones = self._readline(phonname)
        self._aligner.set_phones( phones )

        if tokenname is not None:
            tokens = self._readline(tokenname)
        self._aligner.set_tokens( tokens )

        # Do not align nothing!
        if len(phones) == 0:
            self._basicaligner.run_alignment(audiofilename, alignname)
            return "Empty annotation: nothing to align."

        # Do not align only one phoneme!
        if len(phones.split()) <= 1 and "-" not in phones:
            self._basicaligner.run_alignment(audiofilename, alignname)
            return ""

        # Execute Alignment
        ret = self._aligner.run_alignment(audiofilename, alignname)

        return ret

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _instantiate_aligner(self):
        """
        Instantiate self._aligner to the appropriate Aligner system.

        """
        if self._alignerid == "julius":
            self._aligner = JuliusAligner( self._modeldir, self._mapping )

        elif self._alignerid == "hvite":
            self._aligner = HviteAligner( self._modeldir, self._mapping )

        else:
            self._aligner = BasicAligner( self._modeldir, self._mapping )

        self._aligner.set_infersp( self._infersp )

    # ------------------------------------------------------------------------
