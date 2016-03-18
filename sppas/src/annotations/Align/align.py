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
# File: align.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import sys
import os
import shutil
import re
import random
import glob
import string
import codecs
import logging
import os.path
from datetime import date

import utils.fileutils as fileutils

import annotationdata.io
from annotationdata.transcription import Transcription
from annotationdata.media         import Media
from annotationdata.io.utils      import gen_id

import signals
from signals.channel    import Channel
from signals.channelsil import ChannelSil

from resources.acm.mapping  import Mapping
from resources.acm.tiedlist import TiedList

from presenters.audiosilencepresenter import AudioSilencePresenter
from presenters.audiosppaspresenter   import AudioSppasPresenter

from juliusalign    import juliusAligner
from hvitealign     import hviteAligner
from basicalign     import basicAligner
from alignerio      import AlignerIO

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------

# List of supported aligners
# Notice that the basic aligner can be used to align without wav!
ALIGNERS = ['julius', 'hvite', 'basic']

# File encoding
ENCODING = 'utf-8'

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------

class sppasAlign:
    """
    SPPAS automatic Alignment (also called phonetic segmentation).

    SPPAS alignment is performed in 3 sub-steps:

        1. Split the audio/trs into units;
        2. Align each unit using an external aligner;
        3. Create a transcription with results.

    If step 1 fails, a basic alignment is applied on all units.
    At step 2, if the aligner fails, a basic alignment is applied on the unit.

    This alignment produces 3 tiers:

        - Phonemes,
        - PhonTokens (if tokens are given in the input),
        - Tokens (if tokens are given in the input).

    How to use sppasAlign?

    >>> a = sppasAlign( modeldirname )
    >>> a.run(inputphonesname, inputtokensname, inputaudioname, outputfilename)

    """

    def __init__(self, model, logfile=None):
        """
        Create a new sppasAlign instance.

        @param model is the acoustic model directory name,
        @param logfile is a file descriptor of a log file (see log.py).

        """
        # Members
        self._model   = model
        self._logfile = logfile

        mappingfilename = os.path.join( self._model, "monophones.repl")
        if os.path.isfile( mappingfilename ):
            self._mapping = Mapping( mappingfilename )
        else:
            self._mapping = Mapping()

        # List of options to configure this automatic annotation
        self._options = {}
        self._options['expend']  = True
        self._options['extend']  = False
        self._options['merge']   = False # Add the output inside the input
        self._options['clean']   = True  # Remove temporary files
        self._options['infersp'] = False # Add 'sp' at the end of each token

        # The automatic alignment system:
        self._alignerid = 'julius'
        self.__instanciate_aligner()

        # The basic aligner is used:
        #   - when the IPU contains only one phoneme;
        #   - when the automatic alignment system failed to perform segmn.
        self._basicaligner = basicAligner(model, self._mapping, logfile)

    # End __init__
    # ------------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Options
    # ------------------------------------------------------------------------


    def fix_options(self, options):
        """
        Fix all options.

        @param options (dict) Dictionary with key=optionname (string).

        """
        for opt in options:
            if "expend" == opt.get_key():
                self.set_expend( opt.get_value() )
            elif "extend" == opt.get_key():
                self.set_extend( opt.get_value() )
            elif "merge" == opt.get_key():
                self.set_merge( opt.get_value() )
            elif "clean" == opt.get_key():
                self.set_clean( opt.get_value() )
            elif "aligner" == opt.get_key():
                self.set_aligner( opt.get_value() )
            elif "infersp" == opt.get_key():
                self.set_infersp( opt.get_value() )

    # End fix_options
    # ------------------------------------------------------------------------


    def set_extend(self,extend):
        """
        Fix the extend option.
        If extend is set to True, sppasAlign() will extend the last
        phoneme/token to the audio file duration.
        Otherwise, a silence is inserted.

        @param extend is a Boolean

        """
        self._options['extend'] = extend

    # End set_extend
    # ----------------------------------------------------------------------


    def set_expend(self,expend):
        """
        Fix the expend option.
        If expend is set to True, sppasAlign() will expend the last
        phoneme/token of each unit to the unit duration.

        @param expend is a Boolean

        """
        self._options['expend'] = expend

    # End set_expend
    # ----------------------------------------------------------------------


    def set_merge(self,merge):
        """
        Fix the merge option.
        If merge is set to True, sppasAlign() will save the input tiers
        in the output file.

        @param merge is a Boolean

        """
        self._options['merge'] = merge

    # End set_merge
    # ----------------------------------------------------------------------


    def set_clean(self,clean):
        """
        Fix the clean option.
        If clean is set to True, sppasAlign() will remove temporary files.

        @param clean is a Boolean

        """
        self._options['clean'] = clean

    # End set_merge
    # ----------------------------------------------------------------------


    def set_infersp(self, infersp):
        """
        Fix the infersp option.
        If infersp is set to True, sppasAlign() will add a short pause at
        the end of each token, and the automatic aligner will infer if it is
        appropriate or not.

        @param infersp is a Boolean

        """
        self._options['infersp'] = infersp
        self._aligner.set_infersp( infersp )

    # End set_infersp
    # ----------------------------------------------------------------------


    # ----------------------------------------------------------------------
    # Fix members
    # ----------------------------------------------------------------------


    def set_model(self, model):
        """
        Fix a new model to perform alignment.

        @param model (string) name of the directory that contains the Acoustic Model

        """
        self._model = model
        self.__instanciate_aligner()

    # End set_model
    # ----------------------------------------------------------------------


    def set_aligner(self, alignername):
        """
        Fix the name of the aligner: julius, hvite or basic.

        @param alignername is a string (upper/lower accepted)

        """
        if not alignername.lower() in ALIGNERS:
            raise ValueError('Error: Bad aligner name.')

        self._alignerid = string.lower(alignername)
        self.__instanciate_aligner()

    # End set_aligner
    # ----------------------------------------------------------------------


    # ------------------------------------------------------------------------
    # Segmentation steps
    # ------------------------------------------------------------------------


    def audioinput(self):
        """
        Fix the self.inputaudio value.
        Verify if a audio file corresponds to the expected
        input format and convert_tracks if it is needed.

        @return Boolean value (the input audio file was converted or not).

        """
        isconverted = False
        tmpname = fileutils.gen_name() + ".wav"
        try:
            converter = AudioSppasPresenter(self._logfile)
            isconverted = converter.export(self.inputaudio, tmpname)
        except Exception:
            pass # hum... TODO something better...

        if isconverted is False:
            testname = fileutils.string_to_ascii(fileutils.format_filename(self.inputaudio))
            if testname != self.inputaudio:
                shutil.copy(self.inputaudio, tmpname)
                isconverted = True

        if isconverted is True:
            self.inputaudio = tmpname

        return isconverted

    # End audioinput
    # ------------------------------------------------------------------------


    def split(self, trstier, diralign, extension, listfile=None):
        """
        Split the phonetization and the audio speech into inter-pausal units.

        @param trstier is the tier to split
        @param diralign is the directory to put units.
        @param extension is the file extension of units.
        @return tuple with number of silences and number of tracks
        """
        channel = None
        try:
            audiospeech = signals.open( self.inputaudio )
            idx = audiospeech.extract_channel(0)
            channel = audiospeech.get_channel(idx)
            framerate = channel.get_framerate()
            duration  = float(channel.get_nframes())/float(framerate)
        except Exception as e:
            self.set_aligner( 'basic' )
            audiospeech = None
            framerate = 16000
            duration  = trstier.GetEndValue()
            if self._logfile is not None:
                self._logfile.print_message("The audio input file is corrupted: "+str(e), indent=2, status=-1)
                self._logfile.print_message("Automatic Speech Segmentation CAN'T work properly.", indent=2, status=3)
                self._logfile.print_message("It will be rescued with a basic segmentation: same duration for each phoneme!",indent=2, status=3)
            #else:# outside SPPAS
            #    raise Exception('Alignment error: '+str(e)+'\n The audio input file is corrupted. Automatic Speech Segmentation CANT work. Rescued with a basic segmentation: same duration for each phoneme!')

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
        audiosilpres = AudioSilencePresenter(chansil, self._logfile)
        ret = audiosilpres.write_tracks(trstracks, diralign, ext=extension, trsunits=trsunits, trsnames=[], logfile=self._logfile)

        if listfile is not None:
            # write the list file
            with codecs.open(listfile ,'w', ENCODING) as fp:
                idx = 0
                for from_pos, to_pos in trstracks:
                    fp.write( "%.4f %.4f " %( float(from_pos)/float(framerate) , float(to_pos)/float(framerate) ))
                    fp.write( "\n" )
                    idx = idx+1
                # Finally, print audio file duration
                fp.write( "%.4f\n" % duration )

        return (len(silence), len(trstracks))

    # End split
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

        with codecs.open(outputalign, 'r', ENCODING) as f:
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
                                    if self._logfile:
                                        self._logfile.print_message(entry+" successfully added in the tiedlist.",indent=4,status=3)
                                else:
                                    if self._logfile:
                                        self._logfile.print_message("I do not know how to add "+entry+" in the tiedlist.",indent=4,status=3)

        if dirty is True:
            today          = str(date.today())
            randval        = str(int(random.random()*10000))
            backuptiedfile = os.path.join(self._model, "tiedlist."+today+"."+randval)
            shutil.copy( tiedfile,backuptiedfile )
            tie.save( tiedfile )

    # End add_tiedlist
    # ------------------------------------------------------------------------


    def exec_alignment(self, audiofilename, phonname, alignname):
        """
        Call Aligner to align.

        @param audiofilename is the audio file name of the unit
        @param phonname is the file name with the phonetization
        @param alignname is the output file name to save alignment

        """
        with codecs.open(phonname, 'r', ENCODING) as fp:
            # Get the phoneme sequence
            phones = fp.readline()
            # Remove multiple spaces
            phones = re.sub("[ ]+", " ", phones)

        # Do not align nothing!
        if len(phones)==0:
            if self._logfile:
                self._logfile.print_message('Nothing to do: empty unit!!!', indent=3,status=1)
            return -1

        # Do not ask Aligner to align only one phoneme!
        if len(phones.split()) <= 1 and '.' not in phones:
            if self._logfile:
                self._logfile.print_message('Execute Basic Align', indent=3)
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
        if self._logfile: self._logfile.print_message('Execute '+self._alignerid+' Align',indent=3)
        ret = self._aligner.run_alignment(audiofilename, basename, alignname)

        # Map-back the phoneset

        return ret

    # End exec_alignment
    # ------------------------------------------------------------------------


    def __convert_basic(self, diralign, trstier=None):
        """ Perform segmentation without an audio file. """

        if self._logfile: self._logfile.print_message('Basic Align', indent=2)

        i = 0
        track = 1
        last = trstier.GetSize()

        if self._logfile: self._logfile.print_message('NB TRACKS: %d'%last, indent=2)

        while i < last:

            if self._logfile: self._logfile.print_message('Basic Align, unit number '+str(track), indent=3)

            # Set the current annotation values
            __ann   = trstier[i]
            __label = __ann.GetLabel().GetValue()

            # Save information
            if __ann.GetLabel().IsSilence():
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    __nextann = trstier[i + 1]
                    while (i + 1) < last and __nextann.GetLabel().IsSilence():
                        i = i + 1
                        if (i + 1) < last:
                            __nextann = trstier[i+1]

            else:
                try:
                    unitduration = __ann.GetLocation().GetEnd().GetMidpoint() - __ann.GetLocation().GetBegin().GetMidpoint()
                    phonname  = os.path.join(diralign, "track_%06d.phon"%track)
                    alignname = os.path.join(diralign, "track_%06d.palign"%track)
                    self._basicaligner.run_basic(unitduration, phonname, alignname)
                    if self._logfile:
                        self._logfile.print_message(" ", indent=3,status=0)
                except Exception as e:
                    if self._logfile:
                        self._logfile.print_message(str(e), indent=3,status=-1)
                track = track + 1

            i = i + 1


    def convert_tracks(self, diralign, trstier):
        """
        Call the Aligner to align each unit of a directory.

        @param diralign is the directory to get units and put alignments.
        @param trstier (Tier) required only if basic alignment.

        """
        # Verify if the directory exists
        if not os.path.exists( diralign ):
            raise IOError('The directory '+diralign+' does not exist.')

        if self._alignerid == 'basic':
            self.__convert_basic(diralign, trstier)
            return

        # Get all audio tracks
        dirlist = glob.glob(os.path.join(diralign, "track_*.wav"))
        ntracks = len(dirlist)
        if ntracks==0:
            raise IOError('The directory '+diralign+' does not contain tracks.')

        ret = 2
        track = 1
        while track <= ntracks:

            if self._logfile:
                self._logfile.print_message('Align unit number '+str(track), indent=3)
            else:
                logging.info( ' ... Align unit number %d'%track)

            audiofilename = os.path.join(diralign, "track_%06d.wav"%track)
            phonname = os.path.join(diralign, "track_%06d.phon"%track)
            if self._alignerid == 'julius' or self._alignerid == 'basic':
                alignname = os.path.join(diralign, "track_%06d.palign"%track)
            elif self._alignerid == 'hvite':
                alignname = os.path.join(diralign, "track_%06d.mlf"%track)

            try:
                ret = self.exec_alignment(audiofilename, phonname, alignname)
            except Exception as e:
                ret = 1
                if self._logfile:
                    self._logfile.print_message(self._alignerid+' failed to perform segmentation: '+str(e), indent=3,status=3)
            try:
                if ret>2:
                    if self._logfile:
                        self._logfile.print_message('Try to add missing triphones into the tiedlist',indent=3,status=3)
                        self.add_tiedlist(audiofilename, alignname)
                        self._logfile.print_message('Perform alignment again:', indent=3)
                    ret = self.exec_alignment(audiofilename, phonname, alignname)
                elif ret>0:
                    if self._logfile:
                        self._logfile.print_message(self._alignerid+' failed to perform segmentation.',indent=3,status=1)
                    else:
                        logging.info( ' ... ... [ ERROR ] %s failed to perform segmentation.'%self._alignerid)
            except Exception as e:
                ret = 1
                if self._logfile:
                        self._logfile.print_message(self._alignerid+' failed to perform segmentation: %s'%str(e),indent=3,status=-1)

            # Execute BasicAlign
            if ret != 0:
                if os.path.exists(alignname):
                    os.rename(alignname, alignname+'.backup')
                if self._logfile:
                    self._logfile.print_message('Execute a Basic Alignment - same duration for each phoneme:',indent=3)
                alignname = os.path.join(diralign, "track_%06d.palign"%track)
                self._basicaligner.run_alignment(audiofilename, phonname, alignname)

            if self._logfile:
                self._logfile.print_message(" ",indent=3,status=0)

            track = track + 1

    # End convert_tracks
    # ------------------------------------------------------------------------


    def save(self, trsinput, inputfilename, trsoutput, outputfilename):
        """
        Merge all unit alignments into a transcription and save.

        @param diralign is the directory to get alignments.
        @param listfilename is the list of start/end time values of each IPU
        @param outputfilename is the file name to save results.

        """
        if self._options['merge'] is True:
            for i in range(trsinput.GetSize()):
                trsoutput.Append(trsinput[i])

        # An alignment file name is given
        if outputfilename:
            annotationdata.io.write( outputfilename, trsoutput )
        # No output file name
        # the output tiers are added to the input
        else:
            for i in range(trsoutput.GetSize()):
                trsinput.Append( trsoutput[i] )
                # To be verified: it appends SubDivisions too ?????

            annotationdata.io.write( inputfilename, trsinput )

    # End save
    # ------------------------------------------------------------------------

    def convert( self, phontier, toktier, inputaudioname ):
        """
        """
        # Set local file names
        self.inputaudio = inputaudioname

        # Verify the input audio file (and optionally convert it...)
        # --------------------------------------------------------------
        try:
            if self._logfile:
                self._logfile.print_message("Check audio file: ",indent=2)
            converted = self.audioinput( )
            if self._logfile:
                if converted is False:
                    self._logfile.print_message("",indent=3,status=0)
                else:
                    self._logfile.print_message("The file was converted to the required format.",indent=3,status=3)
        except IOError as e:
            raise IOError('Not a valid audio file: '+str(e))

        # Fix the working directory name
        # ------------------------------
        # we use inputaudio instead of inputphonesname because it contains
        # only ascii characters in filename (required under windows).
        diralign, fileExt = os.path.splitext( self.inputaudio )
        if not os.path.exists( diralign ):
            os.mkdir( diralign )
        listfilename = os.path.join(diralign, "tracks.list")

        # Split input into inter-pausal units
        # --------------------------------------------------------------
        if self._logfile:
            self._logfile.print_message("Split into inter-pausal units: ",indent=2)

        try:
            s1 = s2 = 0
            t1 = t2 = 0
            if self._logfile:
                self._logfile.print_message("Phonemes",indent=3)
            (s1,t1) = self.split( phontier, diralign, "phon", listfilename )
            if toktier is not None:
                if self._logfile:
                    self._logfile.print_message("Tokens",indent=3)
                dirtmp = diralign+"tmp"
                if not os.path.exists( dirtmp ):
                    os.mkdir( dirtmp )
                (s2,t2) = self.split( toktier, dirtmp, "trans" )
                if s1 != s2  or  t1 != t2:
                    if self._logfile is not None:
                        self._logfile.print_message("Inconsistency between phonetization and tokenization: ",indent=3,status=1)
                        self._logfile.print_message("Got %d silences and %d ipus in phonetization."%(s1,t1), indent=4)
                        self._logfile.print_message("Got %d silences and %d ipus in tokenization"%(s2,t2), indent=4)
                        self._logfile.print_message("Tokens wont be time-aligned.", indent=4)
                    else:#out of SPPAS
                        raise Exception('align.py. Split error: inconsistency between phonemes and tokens (not the same number of IPUs)',indent=3)
                else:
                    self.split( toktier, diralign, "trans" )
                shutil.rmtree( dirtmp )
        except Exception as e:
            if self._options['clean'] is True:
                shutil.rmtree( diralign )
            raise Exception('Split error: '+str(e))

        if self._logfile:
            self._logfile.print_message("",indent=2,status=0)

        # Align each unit
        # --------------------------------------------------------------
        if self._logfile:
            self._logfile.print_message("Align each inter-pausal unit: ",indent=2)
        try:
            self.convert_tracks( diralign , phontier)
        except Exception as e:
            if self._options['clean'] is True:
                shutil.rmtree( diralign )
            raise
        else:
            if self._logfile:
                self._logfile.print_message("",indent=2,status=0)

        # Merge unit alignments
        # --------------------------------------------------------------
        if self._logfile:
            self._logfile.print_message("Merge unit's alignment and save into a file ",indent=2)

        # Create a Transcription() object with alignments
        if self._logfile:
            self._logfile.print_message("Read each alignment unit: ",indent=3)

        try:
            trsoutput = AlignerIO(self._alignerid)
            if toktier is not None:
                trsoutput.read( diralign, listfilename, self._mapping, expend=self._options['expend'], extend=self._options['extend'], tokens=True)
            else:
                trsoutput.read( diralign, listfilename, self._mapping, expend=self._options['expend'], extend=self._options['extend'], tokens=False)

            if self._alignerid != 'basic':
                trsoutput = self.rustine_liaisons(trsoutput)
                trsoutput = self.rustine_others(trsoutput)

            if self._logfile:
                self._logfile.print_message("",indent=4,status=0)

        except Exception as e:
            if self._options['clean'] is True:
                shutil.rmtree( diralign )
            raise IOError("align.py. AlignerIO. Error while reading aligned tracks: " + str(e))

        # Set media
        extm = os.path.splitext(inputaudioname)[1].lower()[1:]
        media = Media( gen_id(), inputaudioname, "audio/"+extm )
        trsoutput.AddMedia( media )
        for tier in trsoutput:
            tier.SetMedia( media )

        return trsoutput

    # ------------------------------------------------------------------------

    def run(self, inputphonesname, inputtokensname, inputaudioname, outputfilename=None):
        """
        Execute SPPAS Alignment.

        @param inputphonesname is the file containing the phonetization
        @param inputtokensname is the file containing the tokenization
        @param outputfilename is the file name with the result (3 tiers)

        """
        # Get input data and merge tokenization/phonetization in a Transcription()
        trsinput = Transcription()

        try:
            phontier = self.__get_phonestier( inputphonesname )
            trsinput.Add( phontier )
        except Exception as e:
            raise IOError(' Not a valid input file: '+str(e))

        toktier = self.__get_tokenstier( inputtokensname )
        if toktier is not None:
            trsinput.Add( toktier )
        else:
            if self._logfile:
                self._logfile.print_message("Tokens alignment disabled: no tokenization available",indent=2,status=3)

        # Processing...
        trsoutput = self.convert( phontier,toktier,inputaudioname )

        # Save results
        try:
            if self._logfile:
                self._logfile.print_message("Save each alignment unit: ",indent=3)
            self.save( trsinput, inputphonesname, trsoutput, outputfilename )

            if self._logfile:
                self._logfile.print_message("",indent=4,status=0)

        except Exception as e:
            if self._options['clean'] is True:
                diralign, fileExt = os.path.splitext( self.inputaudio )
                shutil.rmtree( diralign )
            raise IOError("align.py. Save. Error while saving file: " + str(e))

        # Clean!
        # if the audio file was converted.... remove the tmpaudio
        if self.inputaudio != inputaudioname:
            os.remove(self.inputaudio)
        if self._options['clean'] is True:
            diralign, fileExt = os.path.splitext( self.inputaudio )
            shutil.rmtree( diralign )

    # End run
    # ------------------------------------------------------------------------


    # ###################################################################### #
    # Private!                                                               #
    # ###################################################################### #


    def __instanciate_aligner(self):
        """ Instanciate self._aligner to the appropriate Aligner system. """

        if self._alignerid == "julius":
            self._aligner = juliusAligner( self._model, self._mapping, self._logfile )

        elif self._alignerid == "hvite":
            self._aligner = hviteAligner( self._model, self._mapping, self._logfile )

        else:
            self._aligner = basicAligner( self._model, self._mapping, self._logfile )

        self._aligner.set_infersp( self._options['infersp'] )

    # ------------------------------------------------------------------------

    def __get_phonestier(self, inputname):
        """ Return the tier with phonemes. """

        phontier = 0 # First tier by default
        trsp = annotationdata.io.read( inputname )

        for i in range( trsp.GetSize() ):
            if "phon" in trsp[i].GetName().lower():
                phontier = i
                break

        return trsp[phontier]

    # ------------------------------------------------------------------------

    def __get_tokenstier(self, inputname):
        """ Return the tier with tokens, or None. """

        toktier = None # None tier with tokens
        std     = None # index of stdtoken tier
        faked   = None # index of fakedtoken tier

        try:
            trst = annotationdata.io.read( inputname )
        except Exception:
            return None

        # Attention: seulement une tier de tokens est utilisee...
        # mais en cas de TOE, on peut en avoir 2... va falloir choisir!
        for i in range(trst.GetSize()):
            tiername = trst[i].GetName().lower()
            if "std" in tiername and "token" in tiername:
                std = i
            elif "faked" in tiername and "token" in tiername:
                faked = i
            elif "token" in tiername:
                toktier = trst[i]

        if std is not None:
            toktier = trst[std]
        elif faked is not None:
            toktier = trst[faked]

        return toktier

    # ------------------------------------------------------------------------

    def rustine_others(self, trs):
        """ veritable rustine pour decaler la fin des non-phonemes. """
        tierphon   = trs.Find("PhonAlign")
        if tierphon is None:
            return trs

        imax = tierphon.GetSize() - 1
        for i, a in reversed(list(enumerate(tierphon))):
            if i < imax:
                nexta = tierphon[i+1]
                durnexta = nexta.GetLocation().GetDuration()

                if a.GetLabel().GetValue() == "sil" and durnexta > 0.04:
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.03 )

                if a.GetLabel().GetValue() in [ "gb", "@@", "fp", "dummy" ]:
                    a.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() + 0.02 )

                nexta.GetLocation().SetBeginMidpoint( a.GetLocation().GetEndMidpoint() )

        return trs

    def rustine_liaisons(self, trs):
        """ veritable rustine pour supprimer qqs liaisons en trop. """
        # Only for French!
        if "fra" not in self._model: return trs

        tierphon   = trs.Find("PhonAlign")
        tiertokens = trs.Find("TokensAlign")
        if tiertokens is None or tierphon is None:
            return trs

        # supprime les /z/ et /t/ de fin de mot si leur duree est < 65ms.
        for i, a in reversed(list(enumerate(tierphon))):
            if a.GetLocation().GetDuration() < 0.045 and a.GetLabel().GetValue() in [ "z", "n", "t" ]:
                # get the corresponding token
                for t in tiertokens:
                    # this is not the only phoneme in this token!
                    # and the token is not finishing by a vowel...
                    lastchar = t.GetLabel().GetValue()
                    if len(lastchar)>0:
                        lastchar = lastchar[-1]
                    if a.GetLocation().GetEnd() == t.GetLocation().GetEnd() and a.GetLocation().GetBegin() != t.GetLocation().GetBegin() and not lastchar in ["a", "e", "i", "o", "u", u"é", u"à", u"è"] :
                        # Remove a and extend previous annotation
                        prev = tierphon[i-1]
                        a = tierphon.Pop(i)
                        prev.GetLocation().SetEndMidpoint( a.GetLocation().GetEndMidpoint() )
                        #self._logfile.print_message( "Liaison removed: %s " % a)
                        # Enlever le phoneme de tierphntok!

        return trs

    # ------------------------------------------------------------------------
