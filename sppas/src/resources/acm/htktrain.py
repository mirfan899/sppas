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
# File: htktrain.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import logging
import os
import subprocess
import shutil
import copy
import collections

import utils.fileutils
from utils.type import test_command

from annotations.Phon.phon import sppasPhon
from annotations.Token.tok import sppasTok
from annotations.Align.align import sppasAlign

import annotationdata.io
import annotationdata.utils.tierutils
import audiodata

from annotationdata.transcription import Transcription
from audiodata.audio                import AudioPCM
from audiodata.channelformatter     import ChannelFormatter
from audiodata.channelmfcc          import ChannelMFCC

from resources.dictpron import DictPron
from resources.wordslst import WordsList

from hmm          import HMM
from htkscripts   import HtkScripts
from acmodel      import AcModel
from acmodelhtkio import HtkIO
from ..mapping      import Mapping
from features     import Features
from phoneset     import PhoneSet

from sp_glob import UNKSTAMP

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HMMDEFS_FILENAME    = "hmmdefs"
DEFAULT_MACROS_FILENAME     = "macros"
DEFAULT_PROTO_FILENAME      = "proto"
DEFAULT_MONOPHONES_FILENAME = "monophones"
DEFAULT_MAPPINGMONOPHONES_FILENAME = "monophones.repl"

DEFAULT_PROTO_DIR="protos"
DEFAULT_SCRIPTS_DIR="scripts"
DEFAULT_FEATURES_DIR="features"
DEFAULT_LOG_DIR="log"



# ---------------------------------------------------------------------------

class DataTrainer( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model trainer: temporary data manager.

    This class manage the data created at each step of the acoustic training
    model procedure, including:

        - HTK scripts
        - phoneme prototypes
        - log files
        - features

    """
    def __init__(self):
        """
        Constructor: initialize all members to None.

        """
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """
        Fix all members to None.

        """
        # The working directory.
        self.workdir    = None
        self.featsdir   = None
        self.scriptsdir = None
        self.logdir     = None
        self.htkscripts = HtkScripts()
        self.features   = Features()

        # The data storage directories, for transcribed speech and audio files.
        self.storetrs = []
        self.storewav = []
        self.storemfc = []
        self.storeidx = -1

        # The directory with all HMM prototypes, and the default proto file.
        self.protodir  = None
        self.protofile = None
        self.proto     = HMM()
        self.proto.create_proto( self.features.nbmv )

    # -----------------------------------------------------------------------

    def create(self, workdir=None, scriptsdir=DEFAULT_SCRIPTS_DIR, featsdir=DEFAULT_FEATURES_DIR, logdir=DEFAULT_LOG_DIR, protodir=None, protofilename=DEFAULT_PROTO_FILENAME ):
        """
        Create all directories and their content (if possible) with their
        default names.

        @raise IOError

        """
        self.fix_working_dir( workdir, scriptsdir, featsdir, logdir )
        self.fix_proto( protodir,protofilename  )
        self.check()

    # -----------------------------------------------------------------------

    def delete(self):
        """
        Delete all directories and their content, then reset members.

        """
        if self.workdir is not None:
            shutil.rmtree( self.workdir )
        self.reset()

    # -----------------------------------------------------------------------

    def fix_working_dir(self, workdir=None, scriptsdir=DEFAULT_SCRIPTS_DIR, featsdir=DEFAULT_FEATURES_DIR, logdir=DEFAULT_LOG_DIR):
        """
        Set the working directory and its folders. Create all of them if necessary.

        @param workdir (str) The working main directory
        @param scriptsdir (str) The folder for HTK scripts
        @param featsdir (str) The folder for features
        @param logdir (str) The folder to write output logs

        """
        # The working directory will be located in the system temporary directory
        if workdir is None:
            workdir = utils.fileutils.gen_name()
        if os.path.exists( workdir ) is False:
            os.mkdir( workdir )
        self.workdir = workdir

        if os.path.exists( scriptsdir ) is False:
            scriptsdir = os.path.join(self.workdir,scriptsdir)
        self.htkscripts.write_all( scriptsdir )

        if os.path.exists( featsdir ) is False:
            featsdir = os.path.join(self.workdir,featsdir)
        self.features.write_all( featsdir )

        if os.path.exists( logdir ) is False:
            logdir = os.path.join(self.workdir,logdir)
            if os.path.exists( logdir ) is False:
                os.mkdir( logdir )

        self.scriptsdir = scriptsdir
        self.featsdir   = featsdir
        self.logdir     = logdir
        logging.info('Working directory is fixed to: %s'%self.workdir)

    # -----------------------------------------------------------------------

    def fix_storage_dirs(self, basename):
        """
        Fix the directories to store annotated speech and audio files.

        @param basename (str) indicates a name to identify storage dirs (like: align, phon, trans, ...)

        """
        if basename is None:
            self.storeidx = -1
            return

        if self.workdir is None:
            raise IOError("A working directory must be fixed.")

        storetrs = os.path.join(self.workdir,"trs-"+basename)
        storewav = os.path.join(self.workdir,"wav-"+basename)
        storemfc = os.path.join(self.workdir,"mfc-"+basename)

        if os.path.exists( storetrs ) is False:
            os.mkdir( storetrs )
            os.mkdir( storewav )
            os.mkdir( storemfc )

        if not storetrs in self.storetrs:
            self.storetrs.append( storetrs )
            self.storewav.append( storewav )
            self.storemfc.append( storemfc )

        self.storeidx = self.storetrs.index( storetrs )

    # -----------------------------------------------------------------------

    def get_storetrs(self):
        """
        Return the current directory to store transcribed data files, or None.

        """
        if self.storeidx == -1: return None
        return self.storetrs[self.storeidx]

    # -----------------------------------------------------------------------

    def get_storewav(self):
        """
        Return the current directory to store audio data files, or None.

        """
        if self.storeidx == -1: return None
        return self.storewav[self.storeidx]

    # -----------------------------------------------------------------------

    def get_storemfc(self):
        """
        Return the current directory to store MFCC data files, or None.

        """
        if self.storeidx == -1: return None
        return self.storemfc[self.storeidx]

    # -----------------------------------------------------------------------

    def fix_proto(self, protodir=DEFAULT_PROTO_DIR, protofilename=DEFAULT_PROTO_FILENAME):
        """
        (Re-)Create the proto, then if relevant only, create a `protos` directory
        and add the proto file.

        @param protodir (str) Directory in which prototypes will be stored
        @param protofilename (str) File name of the default prototype

        """
        self.proto.create_proto( self.features.nbmv )
        if protodir is not None and os.path.exists( protodir ) is True:
            self.protodir = protodir

        if self.workdir is not None:
            if protodir is None or os.path.exists( protodir ) is False:
                protodir = os.path.join(self.workdir, DEFAULT_PROTO_DIR)
                if os.path.exists( protodir ) is False:
                    os.mkdir( protodir )

        if protodir is not None and os.path.exists( protodir ):
            self.protodir = protodir

        if self.protodir is not None:
            self.protofile = os.path.join( self.protodir, protofilename)
            logging.info('Write proto file: %s'%self.protofile)

            protomodel = AcModel()

            vectorsize = self.features.nbmv
            targetkind = self.features.targetkind
            paramkind  = protomodel.create_parameter_kind("mfcc", targetkind[4:])

            protomodel.macros = [ protomodel.create_options( vector_size=vectorsize, parameter_kind=paramkind,stream_info=[vectorsize]) ]
            protomodel.append_hmm( self.proto )
            protomodel.save_htk( self.protofile )

    # -----------------------------------------------------------------------

    def check(self):
        """
        Check if all members are initialized with appropriate values.
        Return None if success.

        @raise IOError

        """
        if self.protodir is None:
            raise IOError("No proto directory defined.")
        if os.path.isdir( self.protodir ) is False:
            raise IOError("Bad proto directory: %s."%self.protodir)

        if self.protofile is None:
            raise IOError("No proto file defined.")
        if os.path.isfile( self.protofile ) is False:
            raise IOError("Bad proto file name: %s."%self.protofile)

        if self.workdir is None:
            raise IOError("No working directory defined.")
        if os.path.isdir( self.workdir ) is False:
            raise IOError("Bad working directory: %s."%self.workdir)

        if self.scriptsdir is None:
            raise IOError("No scripts directory defined.")
        if os.path.isdir( self.scriptsdir ) is False:
            raise IOError("Bad scripts directory: %s."%self.scriptsdir)

        if self.featsdir is None:
            raise IOError("No features directory defined.")
        if os.path.isdir( self.featsdir ) is False:
            raise IOError("Bad features directory: %s."%self.featsdir)

        if self.logdir is None:
            raise IOError("No log directory defined.")
        if os.path.isdir( self.logdir ) is False:
            raise IOError("Bad log directory: %s."%self.logdir)

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class TrainingCorpus( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Manager of a training corpus, to prepare such a set of data.

    Data preparation is the step 1 of the acoustic model training procedure.

    It establishes the list of phonemes.
    It converts the input data into the HTK-specific data format.
    It codes the audio data, also called "parameterizing the raw speech
    waveforms into sequences of feature vectors" (i.e. convert from wav
    to MFCC format).

    Accepted input:

        - annotated files: one of annotationdata.io.extensions_in
        - audio files: one of audiodata.extensions

    """
    def __init__(self, datatrainer=None, lang="und"):
        """
        Constructor.

        @param datatrainer (DataTrainer)

        """
        self.datatrainer = None
        self.lang = lang
        self.reset()

        self.datatrainer = datatrainer
        if datatrainer is None:
            self.datatrainer = DataTrainer()

        self.create()

    # -----------------------------------------------------------------------

    def reset(self):
        """
        Fix all members to None or to their default values.

        """
        if self.datatrainer is not None:
            self.datatrainer.reset()

        # Selection of the input data files.
        #   - Key   = original file
        #   - Value = working file
        self.transfiles = {}  # Time-aligned at the utterance level, orthography
        self.phonfiles  = {}  # Time-aligned at the utterance level, phonetization
        self.alignfiles = {}  # Time-aligned at the phone level
        self.audiofiles = {}  #
        self.mfcfiles   = {}  #

        # The lexicon, the pronunciation dictionary and the phoneset
        self.vocabfile  = None
        self.dictfile   = None
        self.phonesfile = None
        self.monophones = PhoneSet()
        self.phonemap   = Mapping()

    # -----------------------------------------------------------------------

    def create(self):
        """
        Create files and directories.

        """
        if self.datatrainer.workdir is None:
            logging.info('Create a temporary working directory: ')
            self.datatrainer.create()

    # -----------------------------------------------------------------------

    def fix_resources(self, vocabfile=None, dictfile=None, mappingfile=None):
        """
        Fix resources using default values.
        Ideally, resources are fixed *after* the datatrainer.

        @param vocabfile (str) The lexicon, used during tokenization of the corpus.
        @param dictfile (str) The pronunciation dictionary, used both to
        generate the list of phones and to perform phonetization of the corpus.
        @param mappingfile (str) file that contains the mapping table for the phone set.

        """
        logging.info('Fix resources: ')

        # The mapping table (required to convert the dictionary)
        if self.datatrainer.workdir is not None and mappingfile is not None:
            self._create_phonemap( mappingfile )

        # The pronunciation dictionary (also used to construct the vocab if required)
        if dictfile is not None and os.path.exists( dictfile ) is True:
            # Map the phoneme strings of the dictionary. Save the mapped version.
            pdict = DictPron( dictfile )
            if self.datatrainer.workdir is not None:
                mapdict = pdict.map_phones( self.phonemap )
                dictfile = os.path.join(self.datatrainer.workdir, self.lang+".dict")
                mapdict.save_as_ascii( dictfile )
            if vocabfile is None:
                tokenslist = pdict.get_keys()
                vocabfile = os.path.join(self.datatrainer.workdir, self.lang+".vocab")
                w = WordsList()
                for token in tokenslist:
                    if not '(' in token and not ')' in token:
                        w.add( token )
                w.save( vocabfile )
            logging.info(' - pronunciation dictionary: %s'%dictfile)
            self.dictfile = dictfile
            self.monophones.add_from_dict( self.dictfile )
        else:
            logging.info(' - no pronunciation dictionary is defined.')

        # Either the given vocab or the constructed one
        if vocabfile is not None:
            logging.info('- vocabulary: %s'%vocabfile)
            self.vocabfile = vocabfile
        else:
            logging.info(' - no vocabulary is defined.')

        # The list of monophones included in the dict
        if self.datatrainer.workdir is not None:
            self.phonesfile = os.path.join(self.datatrainer.workdir, "monophones")
            self.monophones.save( self.phonesfile )

    # -----------------------------------------------------------------------

    def add_corpus(self, directory):
        """
        Add a new corpus to deal with.
        Find matching pairs of files (audio / transcription) of the
        given directory and its folders.

        @param directory (str) The directory to find data files of a corpus.
        @return the number of pairs appended.

        """
        # Get the list of audio files from the input directory
        audiofilelist = []
        for extension in audiodata.extensions:
            files = utils.fileutils.get_files( directory, extension )
            audiofilelist.extend( files )

        # Get the list of transciption files from the input directory
        trsfilelist = []
        for extension in annotationdata.io.extensions_in:
            if extension.lower() in [ ".hz", ".pitchtier", ".txt" ]: continue
            files = utils.fileutils.get_files( directory, extension )
            trsfilelist.extend( files )

        count = 0
        # Find matching files (audio / transcription files).
        for trsfilename in trsfilelist:
            trsbasename = os.path.splitext(trsfilename)[0]
            if trsbasename.endswith("-palign"):
                trsbasename = trsbasename[:-7]
            if trsbasename.endswith("-phon"):
                trsbasename = trsbasename[:-5]

            for audiofilename in audiofilelist:
                audiobasename = os.path.splitext(audiofilename)[0]

                if audiobasename == trsbasename:
                    ret = self.add_file(trsfilename, audiofilename)
                    if ret is True:
                        count = count + 1

        return count

    # -----------------------------------------------------------------------

    def add_file(self, trsfilename, audiofilename):
        """
        Add a new couple of files to deal with.
        If such files are already in the data, they will be added again.

        @param trsfilename (str) The annotated file.
        @param audiofilename (str) The audio file.
        @param Bool

        """
        if self.datatrainer.workdir is None: self.create()

        try:
            trs = annotationdata.io.read( trsfilename )
        except Exception:
            logging.info('Error reading file: %s'%trsfilename)
            return False

        tier = trs.Find('PhonAlign', case_sensitive=False)
        if tier is not None:
            return self._append_phonalign(tier, trsfilename, audiofilename)
        else:
            tier = trs.Find('Phonetization', case_sensitive=False)
            if tier is not None:
                return self._append_phonetization(tier, trsfilename, audiofilename)
            else:
                for tier in trs:
                    if "trans" in tier.GetName().lower():
                        return self._append_transcription(tier, trsfilename, audiofilename)
        logging.info('None of the expected tier was found in %s'%trsfilename)
        return False

    # -----------------------------------------------------------------------
    # -----------------------------------------------------------------------

    def get_scp(self, aligned=True, phonetized=False, transcribed=False ):
        """
        Fix the scp file by choosing the files to add.

        @param aligned (bool) Add time-aligned data in the scp file
        @param phonetized (bool) Add phonetized data in the scp file
        @param transcribed (bool) Add transcribed data in the scp file

        @return filename or None if no data is available.

        """
        files = False
        scpfile = os.path.join( self.datatrainer.workdir, "train.scp")

        with open( scpfile, "w") as fp:

            if transcribed is True:
                for trsfile,workfile in self.transfiles.items():
                    if workfile.endswith(".lab"):
                        mfcfile = self.mfcfiles[ trsfile ]
                        fp.write('%s\n'%mfcfile)
                        files = True

            if phonetized is True:
                for trsfile in self.phonfiles.keys():
                    mfcfile = self.mfcfiles[ trsfile ]
                    fp.write('%s\n'%mfcfile)
                    files = True

            if aligned is True:
                for trsfile in self.alignfiles.keys():
                    mfcfile = self.mfcfiles[ trsfile ]
                    fp.write('%s\n'%mfcfile)
                    files = True

        if files is True: return scpfile
        return None

    # -----------------------------------------------------------------------

    def get_mlf(self):
        """
        Fix the mlf file by defining the directories to add.

        Example of a line of the MLF file is:
        "*/mfc-align/*" => "workdir/trs-align"

        """
        files = False
        mlffile = os.path.join( self.datatrainer.workdir, "train.mlf")

        with open( mlffile, "w") as fp:
            fp.write('#!MLF!#\n')
            for i,trsdir in enumerate(self.datatrainer.storetrs):
                mfcdir = self.datatrainer.storemfc[i]
                mfc = os.path.basename( mfcdir )
                fp.write('"*/%s/*" => "%s"\n' % (mfc, trsdir))
                files = True

        if files is True: return mlffile
        return None

    # -----------------------------------------------------------------------

    def map_phonemes(self, tier, unkstamp="UNK"):
        """
        Map phonemes of a tier.

        """
        # Map phonemes.
        for ann in tier:
            label = ann.GetLabel().GetValue()
            if label == "sp":
                newlabel = "sil"
            elif label == unkstamp:
                newlabel = "dummy"
            else:
                newlabel = self.phonemap.map_entry( label )
            if label != newlabel:
                ann.GetLabel().SetValue( newlabel )
        return tier

    def _append_phonalign(self, tier, trsfilename, audiofilename):
        """
        Append a PhonAlign tier in the set of known data.

        """
        tier = self.map_phonemes(tier)

        # Fix current storage dir.
        self.datatrainer.fix_storage_dirs("align")
        outfile = os.path.basename(utils.fileutils.gen_name(root="track_aligned", addtoday=False, addpid=False))

        # Add the tier
        res = self._append_tier( tier, outfile, trsfilename, audiofilename )
        if res is True:
            self.alignfiles[ trsfilename ] = os.path.join(self.datatrainer.get_storetrs(), outfile+".lab")
        return res


    def _append_phonetization(self, tier, trsfilename, audiofilename):
        """
        Append a Phonetization tier in the set of known data.

        """
        # Map phonemes.
        for ann in tier:
            label = ann.GetLabel().GetValue()
            newlabel = label.replace('sp',"sil")
            newlabel = self.phonemap.map( newlabel, delimiters=[" ","-","|"] )
            newlabel = self._format_phonetization( newlabel )
            if label != newlabel:
                ann.GetLabel().SetValue( newlabel )

        # Fix current storage dir.
        self.datatrainer.fix_storage_dirs("phon")
        outfile = os.path.basename(utils.fileutils.gen_name(root="track_phonetized", addtoday=False, addpid=False))

        # Add the tier
        res =  self._append_tier( tier, outfile, trsfilename, audiofilename )
        if res is True:
            self.phonfiles[ trsfilename ] = os.path.join(self.datatrainer.get_storetrs(), outfile+".lab")
        return res


    def _append_transcription(self, tier, trsfilename, audiofilename):
        """
        Append a Transcription tier in the set of known data.

        """
        # Fix current storage dir.
        self.datatrainer.fix_storage_dirs("trans")
        outfile = os.path.basename(utils.fileutils.gen_name(root="track_transcribed", addtoday=False, addpid=False))

        # Add the tier
        res =  self._append_tier( tier, outfile, trsfilename, audiofilename, ext=".xra" )
        if res is True:
            # no lab file created (it needs sppas... a vocab, a dict and an acoustic model).
            self.transfiles[ trsfilename ] = os.path.join(self.datatrainer.get_storetrs(), outfile+".xra")
        return res


    def _append_tier( self, tier, outfile, trsfilename, audiofilename, ext=".lab" ):
        """
        Append a Transcription (orthography) tier in the set of known data.

        """
        ret = self._add_tier( tier, outfile, ext )
        if ret is True:

            ret = self._add_audio( audiofilename, outfile )
            if ret is True:

                logging.info('Files %s / %s appended as %s.'%(trsfilename,audiofilename,outfile))
                self.audiofiles[ trsfilename ] = os.path.join(self.datatrainer.get_storewav(), outfile + ".wav" )
                self.mfcfiles[ trsfilename ]   = os.path.join(self.datatrainer.get_storemfc(), outfile + ".mfc" )
                return True

            else:
                self._pop_tier( outfile )

        logging.info('Files %s / %s rejected.'%(trsfilename,audiofilename))
        return False

    # -----------------------------------------------------------------------

    def _add_tier( self, tier, outfile, ext ):
        try:
            trs = Transcription()
            trs.Append( tier )
            annotationdata.io.write( os.path.join(self.datatrainer.get_storetrs(), outfile+ext), trs )
        except Exception as e:
            print str(e)
            return False
        return True

    # -----------------------------------------------------------------------

    def _pop_tier( self, outfile ):
        try:
            os.remove( os.path.join(self.datatrainer.get_storetrs(), outfile + ".lab" ))
        except IOError:
            pass

    # -----------------------------------------------------------------------

    def _add_audio( self, audiofilename, outfile ):
        # Get the first channel
        try:
            audio = audiodata.open( audiofilename )
            audio.extract_channel(0)
            formatter = ChannelFormatter( audio.get_channel(0) )
        except Exception as e:
            print str(e)
            return False

        # Check/Convert
        formatter.set_framerate( self.datatrainer.features.framerate )
        formatter.set_sampwidth( self.datatrainer.features.sampwidth )
        formatter.convert()
        audio.close()

        # Save the converted channel
        audio_out = AudioPCM()
        audio_out.append_channel( formatter.channel )
        audiodata.save( os.path.join(self.datatrainer.get_storewav(), outfile + ".wav" ), audio_out )

        # Generate MFCC
        wav = os.path.join(self.datatrainer.get_storewav(), outfile + ".wav" )
        mfc = os.path.join(self.datatrainer.get_storemfc(), outfile + ".mfc" )
        tmpfile = utils.fileutils.gen_name(root="scp", addtoday=False, addpid=False)
        with open( tmpfile, "w") as fp:
            fp.write('%s %s\n'%(wav,mfc))

        cmfc = ChannelMFCC( formatter.channel )
        cmfc.hcopy( self.datatrainer.features.wavconfigfile, tmpfile)
        os.remove(tmpfile)

        return True

    # -----------------------------------------------------------------------

    def _pop_audio( self, outfile ):
        try:
            os.remove( os.path.join(self.datatrainer.get_storewav(), outfile + ".wav" ))
        except IOError:
            pass

    # -----------------------------------------------------------------------

    def _append_mlf(self, filename, outfile):
        """
        Append a transcription in a mlf file from a prepared corpus.

        """
        lab = ""
        with open( os.path.join(self.datatrainer.get_storetrs(),outfile+".lab"), "r") as fp:
            lab = "".join(fp.readlines()).strip()
        if len(lab) == 0:
            return False

        with open( filename, "a+") as fp:
            fp.write('"*/%s/%s.lab"\n'%(os.path.basename(self.datatrainer.get_storetrs()),os.path.basename(outfile)))
            fp.write('%s\n'%lab)

        return True

    # -----------------------------------------------------------------------

    def _create_phonemap(self, mapfile):
        """
        Create the default mapping table, and/or get from a file.

        """
        self.phonemap = Mapping( mapfile )

        if self.phonemap.is_key("sil") is False:
            self.phonemap.add('sil','#')

        if self.phonemap.is_key("sp") is False:
            self.phonemap.add('sp','+')

        if self.phonemap.is_key("gb") is False:
            self.phonemap.add('gb','*')

        self.phonemap.set_reverse( True )

    # -----------------------------------------------------------------------

    def _format_phonetization(self, ipu):
        """
        Remove variants of a phonetized ipu, replace dots by whitespaces.

        @return the ipu without pronunciation variants.

        """
        selectlist = []
        for pron in ipu.split(" "):
            tab = pron.split("|")
            i=0
            m=len(tab[0])
            for n,p in enumerate(tab):
                if len(p)<m:
                    i = n
                    m = len(p)
            selectlist.append( tab[i].replace("-"," ") )
        return " ".join( selectlist )

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class HTKModelInitializer( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model initializer.

    Monophones initialization is the step 2 of the acoustic model training
    procedure.

    In order to create a HMM definition, it is first necessary to produce a
    prototype definition. The function of a prototype definition is to describe
    the form and topology of the HMM, the actual numbers used in the definition
    are not important.
    Having set up an appropriate prototype, an HMM can be initialized by both
    methods:
    1. create a flat start monophones model, a prototype trained from
       phonetized data, and copied for each phoneme (using `HCompV` command).
       It reads in a prototype HMM definition and some training data and outputs
       a new definition in which every mean and covariance is equal to the
       global speech mean and covariance.
    2. create a prototype for each phoneme using time-aligned data (using
       `Hinit` command). Firstly, the Viterbi algorithm is used to find the most
       likely state sequence corresponding to each training example, then the
       HMM parameters are estimated. As a side-effect of finding the Viterbi
       state alignment, the log likelihood of the training data can be computed.
        Hence, the whole estimation process can be repeated until no further
       increase in likelihood is obtained.
    This program trains the flat start model and fall back on this model
    for each phoneme that fails to be trained with `Hinit` (if there are not
    enough occurrences).

    """
    def __init__(self, trainingcorpus, directory):
        """
        Constructor.

        @param trainingcorpus (TrainingCorpus) The data prepared during strep 1.
        @param directory (str) The current directory to write the result of this step.

        """
        self.trainingcorpus = trainingcorpus
        self.directory = directory
        if os.path.exists( directory ) is False:
            raise IOError('A valid directory must be defined in order to initialize the model.')

    # -----------------------------------------------------------------------

    def create_model(self):
        """
        Main method to create the initial acoutic model.

        """
        if self.trainingcorpus.monophones is None:
            raise IOError('A list of monophones must be defined in order to initialize the model.')

        self.create_models()
        self.create_hmmdefs()
        self.create_macros()

    # -----------------------------------------------------------------------

    def _create_flat_start_model(self):
        """
        Create a new version of proto in the directory with `HCompV`.
        This creates two new files in the directory:
            - proto
            - vFloors

        """
        if test_command("HCompV") is False: return
        scpfile = self.trainingcorpus.get_scp( aligned=True, phonetized=True, transcribed=False )
        if scpfile is None: return

        try:
            subprocess.check_call(["HCompV", "-T", "0", "-m",
                                  "-I", self.trainingcorpus.get_mlf(),
                                  "-f", str(0.01),
                                  "-C", self.trainingcorpus.datatrainer.features.configfile,
                                  "-S", scpfile,
                                  "-M", self.directory,
                                  self.trainingcorpus.datatrainer.protofile],
                                  stdout=open(os.devnull, 'wb'),
                                  stderr=open(os.devnull, 'wb'))
        except subprocess.CalledProcessError as e:
            logging.info('HCompV failed: %s'%str(e))
            pass

    # -----------------------------------------------------------------------

    def _create_start_model(self, phone, outfile):
        """
        Create a proto for a specific phone, using `HInit`.

        """
        if test_command("HInit") is False: return
        scpfile = self.trainingcorpus.get_scp( aligned=True, phonetized=False, transcribed=False )
        if scpfile is None: return

        try:
            subprocess.check_call(["HInit", "-T", "0", "-i", "20",
                                   "-m", "1",
                                   "-v", "0.0001",
                                   "-I", self.trainingcorpus.get_mlf(),
                                   "-l", phone,
                                   "-o", outfile,
                                   "-C", self.trainingcorpus.datatrainer.features.configfile,
                                   "-S", scpfile,
                                   "-M", self.directory,
                                   self.trainingcorpus.datatrainer.protofile],
                                stdout=open(os.devnull, 'wb'),
                                stderr=open(os.devnull, 'wb'))
        except subprocess.CalledProcessError:
            pass

    # -----------------------------------------------------------------------

    def create_models(self):
        """
        Create an initial model for each phoneme.

        Create a start model for each phoneme from time-aligned data,
        or use the prototype trained by HCompV (i.e. a flat-start-model),
        or use the existing saved prototype,
        or use the default prototype.

        """
        scpfile = self.trainingcorpus.get_scp( aligned=True, phonetized=False, transcribed=False )

        # Adapt the proto file from the corpus (if any)
        if scpfile is not None:
            if self.trainingcorpus.datatrainer.protofile is not None:
                logging.info(' ... Train proto model:')
                self._create_flat_start_model()
                if os.path.exists( os.path.join( self.directory, "proto") ):
                    logging.info(' [  OK  ] ')
                    self.trainingcorpus.datatrainer.protofile = os.path.join( self.directory, "proto")
                    self.trainingcorpus.datatrainer.proto = HMM()
                    self.trainingcorpus.datatrainer.proto.load( self.trainingcorpus.datatrainer.protofile )
                else:
                    logging.info(' [ FAIL ] ')

        # Create a start model for each phoneme
        logging.info(' ... Train initial model for phones: %s '%" ".join(self.trainingcorpus.monophones.get_list()))

        for phone in self.trainingcorpus.monophones.get_list():

            logging.info(' ... Train initial model of %s: '%phone)
            outfile = os.path.join( self.directory, phone + ".hmm" )

            # If a proto is existing, just keep it.
            if self.trainingcorpus.datatrainer.protodir is not None:
                protophone = os.path.join( self.trainingcorpus.datatrainer.protodir, phone + ".hmm" )
                if os.path.exists(protophone):
                    infile = os.path.join( protophone )
                    h = HMM()
                    h.load( infile )
                    h.set_name( phone )
                    h.save( outfile )
                    logging.info(' ... ... [ PROTO ]: %s'%infile)
                    continue

            # Train an initial model
            if scpfile is not None:
                if os.path.exists( scpfile ):
                    self._create_start_model( phone, outfile )

            # the start model was not created.
            if os.path.exists( outfile ) is False:
                h = self.trainingcorpus.datatrainer.proto
                h.set_name( phone )
                h.save( outfile )
                logging.info(' ... ... ... [ FLAT ]')
                h.set_name( "proto" )
            else:
                # HInit gives a bad name (it's the filename, including path!!)!
                h = HMM()
                h.load( outfile )
                h.set_name( phone )
                h.save( outfile )
                logging.info(' ... ... [ TRAIN ]')

    # -----------------------------------------------------------------------

    def create_hmmdefs(self):
        """
        Create an hmmdefs file from a set of separated hmm files.

        """
        acmodel = AcModel()

        vectorsize = self.trainingcorpus.datatrainer.features.nbmv
        targetkind = self.trainingcorpus.datatrainer.features.targetkind
        paramkind = acmodel.create_parameter_kind("mfcc", targetkind[4:])

        acmodel.macros = [ acmodel.create_options(vector_size=vectorsize, parameter_kind=paramkind,stream_info=[vectorsize]) ]

        for phone in self.trainingcorpus.monophones.get_list():
            filename = os.path.join( self.directory, phone + ".hmm" )
            h = HMM()
            h.load( filename )
            acmodel.append_hmm( h )

        acmodel.save_htk( os.path.join(self.directory, DEFAULT_HMMDEFS_FILENAME))

    # -----------------------------------------------------------------------

    def create_macros(self):
        """
        Create macros file.

        """
        vfloors = os.path.join( self.directory, "vFloors")
        if os.path.exists( vfloors ):

            acmodel = AcModel()

            vectorsize = self.trainingcorpus.datatrainer.features.nbmv
            targetkind = self.trainingcorpus.datatrainer.features.targetkind
            paramkind = acmodel.create_parameter_kind("mfcc", targetkind[4:])

            acmodel.macros = [ acmodel.create_options(vector_size=vectorsize, parameter_kind=paramkind,stream_info=[vectorsize]) ]
            h = HtkIO( vfloors  )
            acmodel.macros.append( h.macros[0] )

            acmodel.save_htk( os.path.join(self.directory, DEFAULT_MACROS_FILENAME))

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class HTKModelTrainer( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model trainer.

    This class allows to train an acoustic model from audio data and their
    transcriptions (either phonetic or orthographic or both).

    Acoustic models are trained with HTK toolbox using a training corpus of
    speech, previously segmented in utterances and transcribed.
    The trained models are Hidden Markov models (HMMs).
    Typically, the HMM states are modeled by Gaussian mixture densities
    whose parameters are estimated using an expectation maximization procedure.
    The outcome of this training procedure is dependent on the availability
    of accurately annotated data and on good initialization.

    Acoustic models are trained from 16 bits, 16000 hz wav files.
    The Mel-frequency cepstrum coefficients (MFCC) along with their first
    and second derivatives are extracted from the speech.

    Step 1 is the data preparation.

    Step 2 is the monophones initialization.

    Step 3 is the monophones generation.
    This first model is re-estimated using the MFCC files
    to create a new model, using ``HERest''. Then, it fixes the ``sp''
    model from the ``sil'' model by extracting only 3 states of the initial
    5-states model. Finally, this monophone model is re-estimated using the
    MFCC files and the training data.

    Step 4 creates tied-state triphones from monophones and from some language
    specificities defined by means of a configuration file.

    """
    def __init__(self, corpus=None):
        """
        Constructor.

        @param corpus (TrainingCorpus)

        """
        self.corpus = corpus

        # Epoch directories (the content of one round of train)
        self.epochs  = 0    # Number of the current epoch
        self.prevdir = None # Directory of the previous epoch
        self.curdir  = None # Directory we're currently working in

    # -----------------------------------------------------------------------

    def init_epoch_dir(self):
        """
        Create an epoch directory to work with.

        """
        nextdir = os.path.join(self.corpus.datatrainer.workdir, "hmm" + str(self.epochs).zfill(2))
        if os.path.exists( nextdir ) is False:
            os.mkdir(nextdir)

        if self.curdir is not None:
            if os.path.exists(os.path.join(self.curdir,DEFAULT_MACROS_FILENAME)):
                shutil.copy( os.path.join(self.curdir,DEFAULT_MACROS_FILENAME), nextdir)

        self.prevdir = self.curdir
        self.curdir  = nextdir
        self.epochs  = self.epochs + 1

    # -----------------------------------------------------------------------

    def small_pause(self):
        """
        Fixing the Silence Models:

             * create a "silst" macro, using state 3 of the "sil" HMM.
             * adapt state 3 of the "sil" HMM definition, to use "silst".
             * create a "sp" HMM.

        Add sp into monophones list.

        """
        # Load current acoustic model and prepare the new working directory
        model = AcModel()
        model.load_htk( os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME) )
        self.init_epoch_dir()

        # Manage sil
        sil = model.get_hmm("sil")
        silst = copy.deepcopy( sil.get_state(3) )
        states = sil.definition['states']
        for item in states:
            if int(item['index']) == 3:
                item['state'] = "silst"

        macro = collections.defaultdict(lambda: None)
        option = collections.defaultdict(lambda: None)
        option['name'] = "silst"
        option['definition'] = silst
        macro['state'] = option
        model.macros.append( macro )

        # Manage sp
        sp = HMM()
        sp.create_sp()
        model.append_hmm(sp)

        # Finally, save the model with the new sp HMM.
        model.save_htk( os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME) )
        self.corpus.monophones.add("sp")
        self.corpus.monophones.save( self.corpus.phonesfile )

    # -----------------------------------------------------------------------

    def align_trs(self, infersp=False ):
        """
        Alignment of the transcribed speech using the current model.

        @param infersp (bool) If infersp is set to True, sppasAlign() will add
        a short pause at the end of each token, and the automatic aligner will
        infer if it is appropriate or not.

        """
        # Nothing to do!
        if len(self.corpus.transfiles) == 0:
            logging.info('No transcribed files. Nothing to do!')
            return True

        # Create Tokenizer, Phonetizer, Aligner
        try:
            tokenizer = sppasTok( self.corpus.vocabfile, self.corpus.lang, logfile=None)
            tokenizer.set_std( False )

            phonetizer = sppasPhon( self.corpus.dictfile )
            phonetizer.set_unk( True )
            phonetizer.set_usestdtokens( False )

            aligner = sppasAlign( self.curdir )
            aligner.set_extend( False )
            aligner.set_expend( False )
            aligner.set_infersp( infersp )

            #aligner.set_aligner( "hvite" )
            #aligner.set_clean( False )

        except Exception as e:
            logging.info('Error while creating automatic annotations: %s'%e)
            return False

        for trsfilename,trsworkfile in self.corpus.transfiles.items():
            # we are re-aligning...
            if trsworkfile.endswith(".lab"):
                trsworkfile = trsworkfile.replace('.lab','.xra')

            # Read input file, get tier with orthography
            trsinput  = annotationdata.io.read( trsworkfile )
            tierinput = None
            for tier in trsinput:
                tiername = tier.GetName().lower()
                if "trans" in tiername:
                    tierinput = tier
                    break
            if tierinput is None:
                logging.info(' ... [ ERROR ] No data for file: %s'%trsworkfile)
                continue

            audioworkfile = self.corpus.audiofiles[trsfilename]

            # Annotate the tier: tokenization, phonetization, time-alignment
            try:
                tiertokens, tierStokens = tokenizer.convert( tierinput )
                tierphones = phonetizer.convert( tiertokens )
                trsalign = aligner.convert( tierphones,None,audioworkfile )
            except Exception as e:
                logging.info(' ... [ ERROR ] Annotation error for file: %s. %s'%(trsworkfile,str(e)))
                return False

            # Get only the phonetization from the time-alignment
            tiera = trsalign.Find('PhonAlign')
            tiera = self.corpus.map_phonemes( tiera, unkstamp=UNKSTAMP )
            tier = annotationdata.utils.tierutils.align2phon( tiera )
            trs = Transcription()
            trs.Add( tier )

            # Save file.
            outfile = trsworkfile.replace('.xra','.lab')
            annotationdata.io.write( outfile,trs )
            self.corpus.transfiles[trsfilename] = outfile
            logging.info(' ... [ SUCCESS ] Created file: %s'%outfile)

        return True

    # -----------------------------------------------------------------------

    def train_step(self, scpfile, rounds=3, dopruning=True):
        """
        Perform one or more rounds of HERest estimation.

        @param scpfile (str)
        @param rounds (int) Number of times HERest is called.
        @return bool

        """
        if test_command("HERest") is False: return False

        # Is there files?
        if scpfile is None: return True

        macro = []
        if self.prevdir is not None and os.path.exists(os.path.join(self.prevdir, DEFAULT_MACROS_FILENAME)) is True:
            macro.append('-H')
            macro.append(os.path.join(self.prevdir, DEFAULT_MACROS_FILENAME))

        statfile  = os.path.join( self.corpus.datatrainer.logdir, "stats-step"+str(self.epochs).zfill(2)+".txt" )
        logfile   = os.path.join( self.corpus.datatrainer.logdir, "log-step"+str(self.epochs).zfill(2)+".txt" )
        errorfile = os.path.join( self.corpus.datatrainer.logdir, "err-step"+str(self.epochs).zfill(2)+".txt" )

        pruning = []
        if dopruning is True:
            pruning.append("-t")
            pruning.append( "250.0" )
            pruning.append( "150.0" )
            pruning.append( "1000.0" )

        for _ in range(rounds):
            logging.info("Training iteration {}.".format(self.epochs))
            self.init_epoch_dir()

            try:
                subprocess.check_call(["HERest", "-T", "2",
                            "-I", self.corpus.get_mlf(),
                            "-C", self.corpus.datatrainer.features.configfile,
                            "-S", scpfile,
                            "-s", statfile,
                            "-M", self.curdir,
                            "-H", os.path.join(self.prevdir, DEFAULT_HMMDEFS_FILENAME)]
                            +macro+pruning+
                            [self.corpus.phonesfile],
                            stdout=open(logfile, 'wb'),
                            stderr=open(errorfile, 'wb'))
            except subprocess.CalledProcessError as e:
                logging.info('HERest failed: %s'%str(e))
                return False
        return True

    # -----------------------------------------------------------------------

    def training_step1(self):
        """
        Step 1 of the training procedure: Data preparation.

        """
        logging.info("Step 1. Data preparation.")

        if self.corpus.datatrainer.workdir is None:
            self.corpus.datatrainer.workdir = utils.fileutils.gen_name()
            os.mkdir( self.corpus.datatrainer.workdir )
        if self.corpus.phonesfile is None:
            self.corpus.fix_resources()

    # -----------------------------------------------------------------------

    def training_step2(self):
        """
        Step 2 of the training procedure: Monophones initialization.

        """
        logging.info("Step 2. Monophones initialization.")
        self.init_epoch_dir()
        initial = HTKModelInitializer( self.corpus, self.curdir )
        initial.create_model()

        if os.path.exists(os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME)) is False:
            raise IOError('Monophones initialization failed.')

        if len(self.corpus.audiofiles) == 0:
            logging.info('No audio file: the model was created only from prototypes.')
            return False

        return True

    # -----------------------------------------------------------------------

    def training_step3(self):
        """
        Step 3 of the training procedure: Monophones training.

            1. Train phonemes from time-aligned data.
            2. Create sp model
            3. Train from phonetized data.
            4. Align transcribed data.
            5. Train from all data.

        """
        logging.info("Step 3. Monophones training.")

        # Step 3.1 Train from time-aligned data.
        # ---------------------------------------

        logging.info("Initial training.")
        scpfile = self.corpus.get_scp( aligned=True, phonetized=False, transcribed=False )
        ret = self.train_step( scpfile, dopruning=True )
        if ret is False:
            logging.info('Initial training failed.')
            return False

        # Step 3.2 Modeling silence.
        # --------------------------

        logging.info("Modeling silence.")
        self.small_pause()

        # Step 3.3 Train from utterrance-aligned data with phonetization.
        # ---------------------------------------------------------------

        logging.info("Additional training.")
        scpfile = self.corpus.get_scp( aligned=True, phonetized=True, transcribed=False )
        ret = self.train_step( scpfile, dopruning=True )
        if ret is False:
            logging.info('Additional training failed.')
            return False

        # Step 3.4 Train from utterrance-aligned data with orthography.
        # -------------------------------------------------------------

        logging.info("Aligning transcribed files.")
        self.align_trs( infersp=False )

        logging.info("Intermediate training.")
        ret = self.train_step( self.corpus.get_scp( aligned=True, phonetized=True, transcribed=True ) )
        if ret is False:
            logging.info('Intermediate training failed.')
            return False

        logging.info("Re-Aligning transcribed files.")
        self.align_trs( infersp=True )

        logging.info("Final training.")
        ret = self.train_step( self.corpus.get_scp( aligned=True, phonetized=True, transcribed=True ) )
        if ret is False:
            logging.info('Final training failed.')
            return False

        return True

    # -----------------------------------------------------------------------

    def training_step4(self):
        """
        Step 4 of the training procedure: Triphones training.

        """
        return True

    # -----------------------------------------------------------------------

    def get_current_model(self):
        """
        Return the model of the current epoch, or None.

        """
        model = AcModel()
        try:
            model.load_htk( os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME) )
        except Exception:
            return None
        return model

    # -----------------------------------------------------------------------

    def get_current_macro(self):
        """
        Return the macros of the current epoch, or None.

        """
        model = AcModel()
        try:
            model.load_htk( os.path.join( self.curdir,DEFAULT_MACROS_FILENAME) )
        except Exception:
            return None
        return model

    # -----------------------------------------------------------------------

    def training_recipe(self, outdir=None, delete=False):
        """
        Create an acoustic model and return it.
        A corpus (TrainingCorpus) must be previously defined.

        @param outdir (str) Directory to save the final model and related files
        @param delete (bool) Delete the working directory.
        @return AcModel

        """
        if self.corpus is None: return AcModel()

        # Step 1: Data preparation
        self.training_step1()

        # Step 2: Monophones initialization
        if self.training_step2() is True:

            # Step 3: Monophones training
            if self.training_step3() is True:

                # Step 4: Triphones training
                self.training_step4()

        model = self.get_current_model()
        macro = self.get_current_macro()

        if outdir is not None and model is not None:
            continuee = True
            if os.path.exists(outdir) is False:
                try:
                    os.mkdir( outdir )
                except Exception:
                    logging.info('Error while creating %s'%outdir)
                    continuee = False
            if continuee:
                model.save_htk( os.path.join(outdir, DEFAULT_HMMDEFS_FILENAME ))
                if macro is not None:
                    macro.save_htk( os.path.join(outdir, DEFAULT_MACROS_FILENAME ))
                self.corpus.monophones.save( os.path.join(outdir, DEFAULT_MONOPHONES_FILENAME) )
                self.corpus.phonemap.save_as_ascii( os.path.join(outdir, DEFAULT_MAPPINGMONOPHONES_FILENAME) )
                self.corpus.datatrainer.features.write_wav_config( os.path.join(outdir, "config") )

        if delete is True:
            self.corpus.datatrainer.delete()

        return model

# ---------------------------------------------------------------------------
