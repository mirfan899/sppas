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
from _snack import size
from sppas.src.utils import fileutils

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import logging
import os
import subprocess
import shutil

import utils.fileutils
from utils.type import test_command

import annotationdata.io
import signals

from annotationdata.transcription import Transcription
from signals.audio                import Audio
from signals.channelformatter     import ChannelFormatter
from signals.channelmfcc          import ChannelMFCC

from resources.dictpron import DictPron
from resources.wordslst import WordsList

from hmm          import HMM
from htkscripts   import HtkScripts
from acmodel      import AcModel
from acmodelhtkio import HtkIO

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HMMDEFS_FILENAME    = "hmmdefs"
DEFAULT_MACROS_FILENAME     = "macros"
DEFAULT_PROTO_FILENAME      = "proto"
DEFAULT_MONOPHONES_FILENAME = "monophones"

DEFAULT_PROTO_DIR="protos"
DEFAULT_SCRIPTS_DIR="scripts"
DEFAULT_FEATURES_DIR="features"
DEFAULT_LOG_DIR="log"


# ---------------------------------------------------------------------------

class Features( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model features.

    """
    def __init__(self):
        """
        Constructor.

        """
        self.win_length_ms = 25   # The window length of the cepstral analysis in milliseconds
        self.win_shift_ms  = 10   # The window shift of the cepstral analysis in milliseconds
        self.num_chans     = 26   # Number of filterbank channels
        self.num_lift_ceps = 22   # Length of cepstral liftering
        self.num_ceps      = 12   # The number of cepstral coefficients
        self.pre_em_coef   = 0.97 # The coefficient used for the pre-emphasis
        self.targetkind    = "MFCC_0_D_N_Z"
        self.nbmv= 25   # The number of means and variances. It's commonly either 25 or 39.

        self.wavconfigfile = ""
        self.configfile = ""

        self.framerate     = 16000 # Hz
        self.sampwidth     = 2     # 16 bits

    # -----------------------------------------------------------------------

    def write_all(self, dirname):
        """
        Write all files at once, with their default name, in the given
        directory.

        @param dirname (str) a directory name (existing or to be created).

        """
        if os.path.exists( dirname ) is False:
            os.mkdir( dirname )

        self.write_wav_config( os.path.join( dirname, "wav_config") )
        self.write_config( os.path.join( dirname, "config") )

    # -----------------------------------------------------------------------

    def write_wav_config(self, filename):
        """
        Write the wav config into a file.

        """
        logging.info('Write wav config file: %s'%filename)
        with open( filename, "w") as fp:
            fp.write("SOURCEFORMAT = WAV\n")
            fp.write("SOURCEKIND = WAVEFORM\n")
            fp.write("TARGETFORMAT = HTK\n")
            fp.write("TARGETKIND = MFCC_0_D\n")
            fp.write("TARGETRATE = %.1f\n"%(self.win_shift_ms*100000))
            fp.write("SAVECOMPRESSED = T\n")
            fp.write("SAVEWITHCRC = T\n")
            fp.write("WINDOWSIZE = %.1f\n"%(self.win_length_ms*100000))
            fp.write("USEHAMMING = T\n")
            fp.write("PREEMCOEF = %f\n"%self.pre_em_coef)
            fp.write("NUMCHANS = %d\n"%self.num_chans)
            fp.write("CEPLIFTER = %d\n"%self.num_lift_ceps)
            fp.write("NUMCEPS = %d\n"%self.num_ceps)
            fp.write("ENORMALISE = F\n")
        self.wavconfigfile = filename

    # -----------------------------------------------------------------------

    def write_config(self, filename):
        """
        Write the config into a file.

        """
        logging.info('Write config file: %s'%filename)
        with open( filename, "w") as fp:
            fp.write("TARGETKIND = %s\n"%self.targetkind)
            fp.write("TARGETRATE = %.1f\n"%(self.win_shift_ms*100000))
            fp.write("SAVECOMPRESSED = T\n")
            fp.write("SAVEWITHCRC = T\n")
            fp.write("WINDOWSIZE = %.1f\n"%(self.win_length_ms*100000))
            fp.write("USEHAMMING = T\n")
            fp.write("PREEMCOEF = %f\n"%self.pre_em_coef)
            fp.write("NUMCHANS = %d\n"%self.num_chans)
            fp.write("CEPLIFTER = %d\n"%self.num_lift_ceps)
            fp.write("NUMCEPS = %d\n"%self.num_ceps)
            fp.write("ENORMALISE = F\n")
        self.configfile = filename

    # -----------------------------------------------------------------------

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
        self.storetrs = None
        self.storewav = None
        self.storemfc = None

        # The directory with all HMM prototypes, and the default proto file.
        self.protodir  = None
        self.protofile = None
        self.proto     = HMM()
        self.proto.create_proto( self.features.nbmv )

    # -----------------------------------------------------------------------

    def create(self, **kwargs):
        """
        Create all directories and their content (if possible) with their
        default names.

        Expected args are:
            - workdir=None,
            - scriptsdir=DEFAULT_SCRIPTS_DIR,
            - featsdir=DEFAULT_FEATURES_DIR,
            - logdir=DEFAULT_LOG_DIR,
            - protodir=DEFAULT_PROTO_DIR,
            - protofilename=DEFAULT_PROTO_FILENAME
            - dictfile=None,

        @raise IOError

        """
        protodir=None
        protofilename=DEFAULT_PROTO_FILENAME
        if "protodir" in kwargs.keys():
            protodir=kwargs["protodir"]
            del kwargs["protodir"]
        if "protofilename" in kwargs.keys():
            protofilename=kwargs["protofilename"]
            del kwargs["protofilename"]

        self.fix_working_dir( **kwargs )
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
        if self.workdir is None:
            self.workdir = utils.fileutils.gen_name()
            os.mkdir( self.workdir )

        if os.path.exists( scriptsdir ) is False:
            scriptsdir = os.path.join(self.workdir,scriptsdir)
            self.htkscripts.write_all( scriptsdir )

        if os.path.exists( featsdir ) is False:
            featsdir = os.path.join(self.workdir,featsdir)
            self.features.write_all( featsdir )

        if os.path.exists( logdir ) is False:
            logdir = os.path.join(self.workdir,logdir)
            os.mkdir( logdir )

        self.scriptsdir = scriptsdir
        self.featsdir   = featsdir
        self.logdir     = logdir

    # -----------------------------------------------------------------------

    def fix_storage_dirs(self, basename):
        """
        Fix the directories to store annotated speech and audio files.

        @param basename (str) indicates a name to identify storage dirs (like: algn, phon, trans, ...)

        """
        if basename is None:
            self.storetrs = None
            self.storeaudio = None
            return

        if self.workdir is None:
            raise IOError("A working directory must be fixed.")

        self.storetrs = os.path.join(self.workdir,"trs-"+basename)
        self.storewav = os.path.join(self.workdir,"wav-"+basename)
        self.storemfc = os.path.join(self.workdir,"mfc-"+basename)

        if os.path.exists( self.storetrs ) is False:
            os.mkdir( self.storetrs )
            os.mkdir( self.storewav )
            os.mkdir( self.storemfc )

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
            raise IOError("Bad proto directory.")

        if self.protofile is None:
            raise IOError("No proto file defined.")
        if os.path.isfile( os.path.join( self.protodir, self.protofile) ) is False:
            raise IOError("Bad proto file name.")

        if self.workdir is None:
            raise IOError("No working directory defined.")
        if os.path.isdir( self.workdir ) is False:
            raise IOError("Bad working directory.")

        if self.scriptsdir is None:
            raise IOError("No scripts directory defined.")
        if os.path.isdir( self.scriptsdir ) is False:
            raise IOError("Bad scripts directory.")

        if self.featsdir is None:
            raise IOError("No features directory defined.")
        if os.path.isdir( self.featsdir ) is False:
            raise IOError("Bad features directory.")

        if self.logdir is None:
            raise IOError("No log directory defined.")
        if os.path.isdir( self.logdir ) is False:
            raise IOError("Bad log directory.")

    # -----------------------------------------------------------------------

    def __del__(self):
        return
        if self.workdir is not None:
            shutil.rmtree( self.workdir )

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class PhoneSet( WordsList ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Manager of the list of phonemes.

    This class allows to manage the list of phonemes:

    - get it from a pronunciation dictionary,
    - read it from a file,
    - write it into a file,
    - check if a phone string is valid to be used with HTK toolkit.

    """
    def __init__(self, filename=None):
        """
        Constructor.
        Add events to the list: laughter, dummy, noise, silence.

        @param filename (str) is the phoneset file name, i.e. a file with 1 column.

        """
        WordsList.__init__(self, filename, nodump=True, casesensitive=True)
        self.add("@@")
        self.add("dummy")
        self.add("gb")
        self.add("sil")

    # -----------------------------------------------------------------------

    def add_from_dict(self, dictfilename):
        """
        Add the list of phones from a pronunciation dictionary.

        @param dictfilename (str) is the name of an HTK-ASCII pronunciation dictionary

        """
        d = DictPron( dictfilename ).get_dict()
        for value in d.values():
            variants = value.split("|")
            for variant in variants:
                phones = variant.split(".")
                for phone in phones:
                    self.add( phone )

    # -----------------------------------------------------------------------

    def check(self, phone):
        """
        Check if a phone is correct to be used with HTK toolkit.
        A phone can't start by a digit nor '-' nor '+', and must be ASCII.

        @param phone (str) the phone to be checked

        """
        # Must contain characters!
        if len(phone) == 0:
            return False

        if phone[0] in ['-', '+']:
            return False
        try:
            int(phone[0])
            str(phone)
        except Exception:
            return False

        return True

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
        - audio files: one of signals.extensions

    """
    def __init__(self, datatrainer=None):
        """
        Constructor.

        @param datatrainer (DataTrainer)

        """
        self.datatrainer = datatrainer
        if datatrainer is None:
            self.datatrainer = DataTrainer()

        # Selection of the input data files.
        self.transfiles = {}  # Time-aligned at the utterance level, orthography
        self.phonfiles  = {}  # Time-aligned at the utterance level, phonetization
        self.alignfiles = {}  # Time-aligned at the phone level
        self.audiofiles = {}  # Key=annotated file, value=audio file

        # HTK-specific files
        self.scpfile = None

        self.phonmlffile  = None
        self.transmlffile = None
        self.alignmlffile = None

        # The lexicon, the pronunciation dictionary and the phoneset
        self.vocabfile  = None
        self.dictfile   = None
        self.phonesfile = None
        self.monophones = PhoneSet()

        # TODO: Add a mapping table --> training data are not consistent with the dictionary
        # Ex: /@/ in data and /eu/ in dict.

    # -----------------------------------------------------------------------

    def fix_resources(self, vocabfile=None, dictfile=None):
        """
        Fix resources using default values.

        @param vocabfile (str) The lexicon, used during tokenization of the corpus.
        @param dictfile (str) The pronunciation dictionary, used both to
        generate the list of phones and to perform phonetization of the corpus.

        """
        if dictfile is not None and os.path.exists( dictfile ) is True:
            self.dictfile = dictfile
            self.monophones.add_from_dict( self.dictfile )

        if vocabfile is not None:
            self.vocabfile = vocabfile

        if self.datatrainer.workdir is not None:
            self.phonesfile = os.path.join(self.datatrainer.workdir, "monophones")
            self.monophones.save( self.phonesfile )

    # -----------------------------------------------------------------------

    def create(self):
        """
        Create MLF files and SCP file.

        """
        if self.datatrainer.workdir is None:
            logging.info('Create a temporary working directory: ')
            self.datatrainer.create()

        self.alignmlffile = os.path.join( self.datatrainer.workdir, "PhonAlign.mlf")
        self.phonmlffile  = os.path.join( self.datatrainer.workdir, "Phonetized.mlf")
        self.transmlffile = os.path.join( self.datatrainer.workdir, "Transcribed.mlf")

        with open( self.alignmlffile, "w") as fp:
            fp.write('#!MLF!#\n')
        with open( self.phonmlffile, "w") as fp:
            fp.write('#!MLF!#\n')
        with open( self.transmlffile, "w") as fp:
            fp.write('#!MLF!#\n')

        self.scpfile = os.path.join( self.datatrainer.workdir, "train.scp")

    # -----------------------------------------------------------------------

    def add_corpus(self, directory):
        """
        Add a new corpus to deal with.

        """
        raise NotImplementedError

        # For each audio file of the directory:
        # Get transcription file
        # If annotated file / audio file couple is checked:
        # Create lab files
        # Append into mlf file
        # Append into scp file
        # Convert audio into 16bits-16000hz
        # Generates mfcc

    # -----------------------------------------------------------------------

    def add_file(self, trsfilename, audiofilename):
        """
        Add a new couple of files to deal with.

        @param trsfilename (str) The annotated file.
        @param audiofilename (str) The audio file.
        @param Bool

        TODO: Add phonetized data, Add transcribed data.

        """
        if self.datatrainer.workdir is None:
            self.create()

        try:
            trs = annotationdata.io.read( trsfilename )
            tier = trs.Find('PhonAlign', case_sensitive=False)
        except Exception:
            logging.info('No tier PhonAlign was found in %s'%trsfilename)
            return False

        if tier is not None:
            if self.datatrainer.storetrs is None:
                logging.info('Fix storage directory name to "align"')
                self.datatrainer.fix_storage_dirs("align")
            outfile = os.path.basename(utils.fileutils.gen_name(root="track_aligned", addtoday=False, addpid=False))

            ret = self._add_tier( tier, outfile )
            if ret is True:

                ret = self._add_audio( audiofilename, outfile )
                if ret is True:

                    ret = self._append_mlf( self.alignmlffile, outfile )
                    if ret is True:

                        self._append_scp( outfile )
                        logging.info('Files %s / %s appended as %s.'%(trsfilename,audiofilename,outfile))
                        self.audiofiles[ trsfilename ] = audiofilename
                        return True
                    else:
                        self._pop_tier( outfile )
                        self._pop_audio( outfile )
                else:
                    self._pop_tier( outfile )

        logging.info('Files %s / %s rejected.'%(trsfilename,audiofilename))
        return False

    # -----------------------------------------------------------------------

    def _add_tier( self, tier, outfile ):
        try:
            trs = Transcription()
            trs.Append( tier )
            annotationdata.io.write( os.path.join(self.datatrainer.storetrs, outfile+".lab"), trs )
        except Exception as e:
            print str(e)
            return False
        return True

    # -----------------------------------------------------------------------

    def _pop_tier( self, outfile ):
        try:
            os.remove( os.path.join(self.datatrainer.storetrs, outfile + ".lab" ))
        except IOError:
            pass

    # -----------------------------------------------------------------------

    def _add_audio( self, audiofilename, outfile ):
        # Get the first channel
        try:
            audio = signals.open( audiofilename )
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
        audio_out = Audio()
        audio_out.append_channel( formatter.channel )
        signals.save( os.path.join(self.datatrainer.storewav, outfile + ".wav" ), audio_out )

        # Generate MFCC
        wav = os.path.join(self.datatrainer.storewav, outfile + ".wav" )
        mfc = os.path.join(self.datatrainer.storemfc, outfile + ".mfc" )
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
            os.remove( os.path.join(self.datatrainer.storewav, outfile + ".wav" ))
        except IOError:
            pass

    # -----------------------------------------------------------------------

    def _append_mlf(self, filename, outfile):
        """
        Append a transcription in a mlf file from a prepared corpus.

        """
        lab = ""
        with open( os.path.join(self.datatrainer.storetrs,outfile+".lab"), "r") as fp:
            lab = "".join(fp.readlines()).strip()
        if len(lab) == 0:
            return False

        with open( filename, "a+") as fp:
            fp.write('"*/%s/%s.lab"\n'%(os.path.basename(self.datatrainer.storetrs),os.path.basename(outfile)))
            fp.write('%s\n'%lab)

        return True

    # -----------------------------------------------------------------------

    def _append_scp(self, outfile):
        """
        Append a MFC file into the SCP file.

        """
        with open( self.scpfile, "w+") as fp:
            #fp.write('./%s/%s.mfc\n'%(os.path.basename(self.datatrainer.storemfc),outfile))
            fp.write('%s.mfc\n'%os.path.join(self.datatrainer.storemfc,outfile))

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

    def create_model(self, hack=True):
        """
        Main method to create the initial acoutic model.

        @param hack (bool) Force to use the given prototype (if any) for the fillers.

        """
        if self.trainingcorpus.monophones is None:
            raise IOError('A list of monophones must be defined in order to initialize the model.')

        self.create_models(hack)
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

        try:
            subprocess.check_call(["HCompV", "-T", "0", "-m",
                                  "-f", str(0.01),
                                  "-C", self.trainingcorpus.datatrainer.features.configfile,
                                  "-S", self.trainingcorpus.scpfile,
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

        try:
            subprocess.check_call(["HInit", "-T", "0", "-i", "20",
                                   "-m", "1",
                                   "-v", "0.0001",
                                   "-l", phone,
                                   "-o", outfile,
                                   "-C", self.trainingcorpus.datatrainer.features.configfile,
                                   "-L", self.trainingcorpus.datatrainer.storetrs,
                                   "-S", self.trainingcorpus.scpfile,
                                   "-M", self.directory,
                                   self.trainingcorpus.datatrainer.protofile],
                                  stdout=open(os.devnull, 'wb'),
                                  stderr=open(os.devnull, 'wb'))
        except subprocess.CalledProcessError:
            pass

    # -----------------------------------------------------------------------

    def create_models(self, hack=True):
        """
        Create an initial model for each phoneme.

        Create a start model for each phoneme from time-aligned data,
        or use the prototype trained by HCompV (i.e. a flat-start-model),
        or use the existing saved prototype,
        or use the default prototype.

        """
        # Adapt the proto file from the corpus (if any)
        if self.trainingcorpus.scpfile is not None:
            if self.trainingcorpus.datatrainer.protofile is not None:
                logging.info(' ... Train proto model:')
                self._create_flat_start_model()
                if os.path.exists( os.path.join( self.directory, "proto") ):
                    logging.info(' [  OK  ] ')
                    self.trainingcorpus.datatrainer.protofile = os.path.join( self.directory, "proto")
                else:
                    logging.info(' [ FAIL ] ')

        # Create a start model for each phoneme
        for phone in self.trainingcorpus.monophones.get_list():

            logging.info(' ... Train initial model of %s: '%phone)
            outfile = os.path.join( self.directory, phone + ".hmm" )

            if self.trainingcorpus.scpfile is not None:
                self._create_start_model( phone, outfile )

            # the start model was not created.
            if os.path.exists( outfile ) is False:
                infile = self.trainingcorpus.datatrainer.protofile
                h = HMM()
                if self.trainingcorpus.datatrainer.protodir is not None:
                    protophone = os.path.join( self.trainingcorpus.datatrainer.protodir, phone + ".hmm" )
                    if os.path.exists(protophone):
                        infile = os.path.join( protophone )

                if infile is not None:
                    logging.info(' ... ... [ PROTO ]')
                    h.load( infile )
                else:
                    logging.info(' ... ... ... [ CREATE ]')
                    h = self.trainingcorpus.datatrainer.proto

                h.set_name( phone )
                h.save( outfile )
                h.set_name( "proto" )
            else:
                # HInit gives a bad name (it's the filename, including path!!)!
                h = HMM()
                h.load( outfile )
                h.set_name( phone )
                h.save( outfile )
                logging.info(' ... ... [ DATA ]')

        # Hack for the fillers...
        if hack is True and self.trainingcorpus.datatrainer.protodir is not None:
            for phone in PhoneSet().get_list():
                infile  = os.path.join( self.trainingcorpus.datatrainer.protodir, phone + ".hmm" )
                if os.path.exists( infile ) is True:
                    outfile = os.path.join( self.directory, phone + ".hmm" )
                    shutil.copy( infile, outfile )
                    logging.info(' ... Hack initial model of %s:'%phone)

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
        os.mkdir(nextdir)

        if self.curdir is not None:
            # TODO: copy macros ??
            pass

        self.prevdir = self.curdir
        self.curdir  = nextdir
        self.epochs  = self.epochs + 1

    # -----------------------------------------------------------------------

    def small_pause(self):
        """
        TODO
        Fixing the Silence Models
             * get sil HMM model
             * create a "silst" macro, using state 3 of the "sil" HMM.
             * Adapt "sil" HMM definition, of course!
             * Create a "sp" HMM with 3 states, state 2 is the macro "silst"
             * Set a 3x3 transition matrix as follow:
               0.0 1.0 0.0
               0.0 0.9 0.1
               0.0 0.0 0.0

        Add sp into monophones list.

        """
        self.init_epoch_dir()
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def realign(self):
        """
        TODO
        """
        self.init_epoch_dir()
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def train_step(self, rounds=3):
        """
        Perform one or more rounds of HERest estimation.

        @param rounds (int) Number of times HERest is called.

        """
        for _ in range(rounds):
            logging.info("Training iteration {}.".format(self.epochs))
            self.init_epoch_dir()

            try:
                subprocess.check_call(["HERest", "-T", "0",
                            "-C", self.corpus.datatrainer.features.configfile,
                            "-S", self.corpus.scpfile,
                            "-L", self.corpus.datatrainer.storetrs,
                            "-M", self.curdir,
                            "-H", os.path.join(self.prevdir, DEFAULT_MACROS_FILENAME),
                            "-H", os.path.join(self.prevdir, DEFAULT_HMMDEFS_FILENAME),
                            "-t", "250.0", "150.0", "1000.0",
                            self.corpus.phonesfile],
                            stdout=open(os.devnull, 'wb'),
                            stderr=open(os.devnull, 'wb'))
            except subprocess.CalledProcessError as e:
                logging.info('HERest failed: %s'%str(e))
                return False
        return True

    # -----------------------------------------------------------------------

    def training_recipe(self):
        """
        Create an acoustic model and return it.
        A corpus (TrainingCorpus) must be previously defined.

        """
        model = AcModel()

        # Step 1: Data preparation
        # --------------------------

        if self.corpus is None: return model
        if self.corpus.datatrainer.workdir is None:
            self.corpus.datatrainer.workdir = fileutils.gen_name()
            os.mkdir( self.corpus.datatrainer.workdir )
        if self.corpus.phonesfile is None:
            self.corpus.fix_resources()

        # Step 2: Monophones initialization
        # --------------------------

        logging.info("Monophones initialization.")
        self.init_epoch_dir()
        initial = HTKModelInitializer( self.corpus, self.curdir )
        initial.create_model()

        if os.path.exists(os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME)) is False:
            raise IOError('Monophones initialization failed.')

        if len(self.corpus.audiofiles) == 0:
            logging.info('No audio file: Monophone training performed only from prototypes.')
            model.load_htk( os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME) )
            self.corpus.datatrainer.delete()
            return model

        # Step 3: Monophone training
        # --------------------------

        logging.info("Initial training.")
        ret = self.train_step()
        if ret is False:
            logging.info(' * * * * * * * * * * *  INITIAL TRAINING: FAILED * * * * ')
            return model

        logging.info(' * * * * * * * * * * *  INITIAL TRAINING: SUCCESS * * * * ')
        return model

        logging.info("Modeling silence.")
        self.small_pause()

        logging.info("Additional training.")
        self.train_step()

        logging.info("Re-aligning.")
        self.realign()

        logging.info("Final training.")
        self.train_step()

        # --------------------------

        model.load_htk( os.path.join( self.curdir,DEFAULT_HMMDEFS_FILENAME) )
        return model

    # -----------------------------------------------------------------------

    def __del__(self):
        return
        if self.corpus is not None:
            self.corpus.datatrainer.delete()

# ---------------------------------------------------------------------------
