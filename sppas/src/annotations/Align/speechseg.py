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
import re
import random
import codecs
import shutil
from datetime import date

from sp_glob import encoding


import signals
from signals.channel    import Channel
from signals.channelsil import ChannelSil

from resources.acm.tiedlist import TiedList
from resources.mapping  import Mapping

from presenters.audiosilencepresenter import AudioSilencePresenter

from juliusalign    import juliusAligner
from hvitealign     import hviteAligner
from basicalign     import basicAligner

# ----------------------------------------------------------------------------

class SpeechSegmenter:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Automatic speech segmentation.

    Speech segmentation of a unit of speech (an IPU).

    """

    # List of supported aligners (with lowered names)
    # Notice that the basic aligner can be used to align without audio file!
    ALIGNERS = ['julius', 'hvite', 'basic']

    # ------------------------------------------------------------------------

    def __init__(self, model):
        """
        Constructor.

        @param model is the acoustic model directory name. It is expected
        to contain at least a file with name "hmmdefs". It can also contain:
            - tiedlist file;
            - monophones.repl file;
            - config file.
        Any other file will be ignored.

        """
        # The automatic alignment system:
        self._alignerid = SpeechSegmenter.ALIGNERS[0]
        self._model   = model
        self._infersp = False

        # Map phoneme names from model-specific to SAMPA and vice-versa
        mappingfilename = os.path.join( self._model, "monophones.repl")
        if os.path.isfile( mappingfilename ):
            self._mapping = Mapping( mappingfilename )
        else:
            self._mapping = Mapping()

        # The basic aligner is used:
        #   - when the IPU contains only one phoneme;
        #   - when the automatic alignment system failed to perform segmn.
        self._basicaligner = basicAligner(model, self._mapping, None)
        self._instantiate_aligner()

    # ------------------------------------------------------------------------

    def set_model(self, model):
        """
        Fix an acoustic model to perform time-alignment.

        @param model (string) Directory that contains the Acoustic Model.

        """
        self._model = model
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

    def split(self, inputaudio, trstier, diralign, extension, listfile=None):
        """
        Split the phonetization and the audio speech into inter-pausal units.

        @param trstier is the tier to split
        @param diralign is the directory to put units.
        @param extension is the file extension of units.
        @return tuple with number of silences and number of tracks

        """
        audiospeech = signals.open( inputaudio )
        idx = audiospeech.extract_channel(0)
        channel = audiospeech.get_channel(idx)
        framerate = channel.get_framerate()
        duration  = float(channel.get_nframes())/float(framerate)

        trstracks = []
        silence   = []
        trsunits  = []
        i = 0
        last = trstier.GetSize()
        while i < last:
            # Set the current annotation values
            __ann = trstier[i]
            __label = __ann.GetLabel().GetValue()
            # Save information
            if __ann.GetLabel().IsSilence():
                __start = int(__ann.GetLocation().GetBeginMidpoint() * framerate)
                __end   = int(__ann.GetLocation().GetEndMidpoint()   * framerate)
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    __nextann = trstier[i + 1]
                    while (i + 1) < last and __nextann.GetLabel().IsSilence():
                        __end   = int(__nextann.GetLocation().GetEndMidpoint() * framerate)
                        i = i + 1
                        if (i + 1) < last:
                            __nextann = trstier[i + 1]
                silence.append([__start,__end])
            else:
                __start = int(__ann.GetLocation().GetBeginMidpoint() * framerate)
                __end   = int(__ann.GetLocation().GetEndMidpoint()   * framerate)
                trstracks.append([__start,__end])
                trsunits.append( __label )

            # Continue
            i = i + 1
        # end while

        chansil = ChannelSil( channel , 0.3 )
        chansil.set_silence( silence )
        audiosilpres = AudioSilencePresenter(chansil, None)
        audiosilpres.write_tracks(trstracks, diralign, ext=extension, trsunits=trsunits, trsnames=[]) #, logfile=None)

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

    def add_tiedlist(self, inputaudio, outputalign):
        """
        Add missing triphones/biphones in the tiedlist.
        IMPORTANT: efficient only if the aligner is Julius.

        @param inputaudio is the audio input file name.
        @param outputalign is a file name with the failed julius alignment.

        """
        fileName, fileExtension = os.path.splitext(inputaudio)
        tiedfile = os.path.join(self._model, "tiedlist")
        dictfile = inputaudio[:-len(fileExtension)] + ".dict"

        # Create a new Tiedlist instance and backup the current tiedlist file
        tie = TiedList( )
        tie.load( tiedfile )
        dirty = False

        with codecs.open(outputalign, 'r', encoding) as f:
            for line in f:
                if line.find("Error: voca_load_htkdict")>-1 and line.find("not found")>-1:
                    line = re.sub("[ ]+", " ", line)
                    line = line.strip()
                    line = line[line.find('"')+1:]
                    line = line[:line.find('"')]
                    if len(line)>0:
                        entries = line.split(" ")
                        for entry in entries:
                            if tie.is_observed( entry ) is False and tie.is_tied( entry ) is False:
                                ret = tie.add_tied( entry )
                                if ret is True:
                                    dirty = True
                                    #if self._logfile:
                                    #    self._logfile.print_message(entry+" successfully added in the tiedlist.",indent=4,status=3)
                                #else:
                                #    if self._logfile:
                                #        self._logfile.print_message("I do not know how to add "+entry+" in the tiedlist.",indent=4,status=3)

        if dirty is True:
            today          = str(date.today())
            randval        = str(int(random.random()*10000))
            backuptiedfile = os.path.join(self._model, "tiedlist."+today+"."+randval)
            shutil.copy( tiedfile,backuptiedfile )
            tie.save( tiedfile )

    # ------------------------------------------------------------------------

    def exec_basic_alignment_track(self, unitduration, phonname, alignname):
        self._basicaligner.run_basic(unitduration, phonname, alignname)

    def exec_basic_alignment(self, audiofilename, phonname, alignname):
        self._basicaligner.run_alignment(audiofilename, phonname, alignname)


    def exec_alignment(self, audiofilename, phonname, alignname):
        """
        Call Aligner to align.

        @param audiofilename is the audio file name of the unit
        @param phonname is the file name with the phonetization
        @param alignname is the output file name to save alignment

        """
        with codecs.open(phonname, 'r', encoding) as fp:
            # Get the phoneme sequence
            phones = fp.readline()
            # Remove multiple spaces
            phones = re.sub("[ ]+", " ", phones)

        # Do not align nothing!
        if len(phones)==0:
            #if self._logfile:
            #    self._logfile.print_message('Nothing to do: empty unit!!!', indent=3,status=1)
            return -1

        # Do not ask Aligner to align only one phoneme!
        if len(phones.split()) <= 1 and '.' not in phones:
            #if self._logfile:
            #    self._logfile.print_message('Execute Basic Align', indent=3)
            self._basicaligner.run_alignment(audiofilename, phonname, alignname)
            return 0

        fileName, fileExtension = os.path.splitext(audiofilename)
        ret = 0

        # Create the dictionary and the grammar
        dictname = audiofilename[:-len(fileExtension)] + ".dict"
        if self._alignerid == "julius":
            grammarname = audiofilename[:-len(fileExtension)] + ".dfa"
            basename = audiofilename[:-len(fileExtension)]
        elif self._alignerid == "hvite":
            grammarname = audiofilename[:-len(fileExtension)] + ".lab"
            basename = dictname
        else:
            grammarname = ''

        # Map phonemes to the appropriate phoneset

        # Generate dependencies (grammar, dict...)
        self._aligner.gen_dependencies(phones,grammarname,dictname)

        # Execute Alignment
        #if self._logfile: self._logfile.print_message('Execute '+self._alignerid+' Align',indent=3)
        ret = self._aligner.run_alignment(audiofilename, basename, alignname)

        # Map-back the phoneset

        return ret

    # ------------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------------

    def _instantiate_aligner(self):
        """
        Instantiate self._aligner to the appropriate Aligner system.

        """
        if self._alignerid == "julius":
            self._aligner = juliusAligner( self._model, self._mapping) #, self._logfile )

        elif self._alignerid == "hvite":
            self._aligner = hviteAligner( self._model, self._mapping) #, self._logfile )

        else:
            self._aligner = basicAligner( self._model, self._mapping) #, self._logfile )

        self._aligner.set_infersp( self._infersp )

    # ------------------------------------------------------------------------
