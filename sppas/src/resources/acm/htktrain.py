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

from resources.dictpron import DictPron
from resources.wordslst import WordsList

from hmm        import HMM
from htkscripts import HtkScripts
from acmodel    import AcModel
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

def test_command( command ):
    """
    Test if a command is available.

    """
    try:
        NULL = open(os.devnull, "w")
        subprocess.call([command], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        return False
    return True

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
    @summary: Acoustic model trainer: data manager.

    """
    def __init__(self):
        """
        Constructor: init all members to None.

        """
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """
        Fix all members to None.

        """
        # The working directory. Commonly temporary, used to stash everything
        self.workdir    = None
        self.featsdir   = None
        self.scriptsdir = None
        self.logdir     = None
        self.htkscripts = HtkScripts()
        self.features   = Features()

        # The directory with all HMM prototypes, and the default proto file.
        self.protodir  = None
        self.protofile = None
        self.proto     = HMM()
        self.proto.create_proto( self.features.nbmv )

        # The lexicon, the pronunciation dictionary and the phoneset
        self.vocabfile  = None
        self.dictfile   = None
        self.monophones = PhoneSet()

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
            - dictfile=None,
            - protodir=DEFAULT_PROTO_DIR,
            - protofilename=DEFAULT_PROTO_FILENAME

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
        Delete all directories and their content.

        """
        if self.workdir is not None:
            shutil.rmtree( self.workdir )
        self.reset()

    # -----------------------------------------------------------------------

    def fix_working_dir(self, workdir=None, scriptsdir=DEFAULT_SCRIPTS_DIR, featsdir=DEFAULT_FEATURES_DIR, logdir=DEFAULT_LOG_DIR, dictfile=None):
        """
        Set the working directory and its folders.
        Create ell of them if necessary.

        """
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

        if dictfile is not None and os.path.exists( dictfile ) is True:
            self.dictfile = dictfile
            self.monophones.add_from_dict( self.dictfile )

    # -----------------------------------------------------------------------

    def fix_proto(self, protodir=DEFAULT_PROTO_DIR, protofilename=DEFAULT_PROTO_FILENAME):
        """
        (Re-)Create the proto, then if relevant only, create a `protos` directory
        and add the proto file.

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
            self.proto.save( self.protofile )

    # -----------------------------------------------------------------------

    def check(self):
        """
        Check is all members are initialized with appropriate values.

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

        """
        # TODO: Verify if the following rules are really the good ones!

        # Must contain characters!
        if len(phone) == 0:
            return False

        # Must not start with a number
        # Include only ASCII characters
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
    @summary: Manager of a corpus during acoustic model training procedure.

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
        self.scp0file = None
        self.scp1file = None

        self.phonmlffile  = None
        self.transmlffile = None
        self.alignmlffile = None

    # -----------------------------------------------------------------------

    def add_corpus(self, directory):
        """
        Add a new corpus to deal with.

        """
        raise NotImplementedError

        # If annotated file / audio file couple is checked:
        # Create lab files
        # Append into mlf file
        # Append into scp file
        # Convert audio into 16bits-16000hz
        # Generates mfcc

    # -----------------------------------------------------------------------

    def write_mlf(self, corpusdir, tiername, mlffilename):
        """
        Write a mlf file from a corpus.
        All annotated files are loaded and examined to get the given tier
        and to append it into the mlf file.

        """
        pass

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

        """
        self.trainingcorpus = trainingcorpus
        self.directory = directory

    # -----------------------------------------------------------------------

    def create_model(self, hack=True):
        """
        Main method to create the initial acoutic model.

        """
        if self.trainingcorpus.datatrainer.monophones is None:
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

        subprocess.check_call(["HCompV", "-A -D -T 1 -m",
                              "-f", str(0.01),
                              "-C", self.trainingcorpus.datatrainer.features.configfile,
                              "-S", self.trainingcorpus.scp0file,
                              "-M", self.directory, self.trainingcorpus.datatrainer.protofile])

    # -----------------------------------------------------------------------

    def _create_start_model(self, phone, outfile):
        """
        Create a proto for a specific phone, using `HInit`.

        """
        if test_command("HInit") is False: return

        subprocess.check_call(["HInit", "-T 1 -A -i 20",
                               "-D -m 1",
                               "-v 0.0001",
                               "-I", self.trainingcorpus.alignmlffile,
                               "-l", phone,
                               "-o", outfile,
                               "-C", self.trainingcorpus.datatrainer.features.configfile,
                               "-S", self.trainingcorpus.scp0file,
                               "-M", self.directory, self.trainingcorpus.datatrainer.protofile])

    # -----------------------------------------------------------------------

    def create_models(self, hack=True):
        """
        Create an initial model for each phoneme,
        either by using a prototype or a start model.

        """
        # Adapt the proto file from the corpus (if any)
        if self.trainingcorpus.scp0file is not None:
            if self.trainingcorpus.datatrainer.protofile is not None:
                logging.info(' ... Train proto model:')
                self._create_flat_start_model()
                if os.path.exists( os.path.join( self.directory, "proto") ):
                    logging.info(' [  OK  ] ')
                    self.trainingcorpus.datatrainer.protofile = os.path.join( self.directory, "proto")
                else:
                    logging.info(' [ FAIL ] ')

        # Create a start model for each phoneme
        # ... or use the prototype trained by HCompV (flat-start-model)
        # ... ... or use the existing saved prototype
        # ... ... ... or use the default prototype.
        for phone in self.trainingcorpus.datatrainer.monophones.get_list():

            logging.info(' ... Train initial model of %s: '%phone)
            outfile = os.path.join( self.directory, phone + ".hmm" )

            if self.trainingcorpus.scp0file is not None:
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
                logging.info(' ... ... [ DATA ]')

        # Some hack...
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
        Create hmmdefs file from a set of separated monophones.

        """
        acmodel = AcModel()

        vectorsize = self.trainingcorpus.datatrainer.features.nbmv
        targetkind = self.trainingcorpus.datatrainer.features.targetkind
        paramkind = acmodel.create_parameter_kind("mfcc", targetkind[4:])

        acmodel.macros = [ acmodel.create_options(vector_size=vectorsize, parameter_kind=paramkind,stream_info=[vectorsize]) ]

        for phone in self.trainingcorpus.datatrainer.monophones.get_list():
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

    Step 1 is the data preparation. It establishes the list of phonemes.
    It converts the input data into the HTK-specific data format (MLF files).
    It codes the audio data, also called "parameterizing the raw speech
    waveforms into sequences of feature vectors" (i.e. convert from wav
    to MFCC format).

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

        """
        # Prepare or set all directories to work with.
        self.corpus = corpus
        if self.corpus is None:
            self.corpus = TrainingCorpus()

        # Epoch directories (the content of one round of train)
        self.epochs  = 0    # Number of the current epoch
        self.prevdir = None # Directory of the previous epoch
        self.curdir  = None # Directory we're currently working in

    # -----------------------------------------------------------------------

    def init_epoch_dir(self):
        """
        Create an epoch directory to work with.

        """
        nextdir = os.path.join(self.corpus.datatrainer.workdir, "hmm", str(self.epochs).zfill(3))
        os.mkdir(nextdir)

        if self.curdir is not None:
            # copy macros ??
            pass

        self.prevdir = self.curdir
        self.curdir  = nextdir

    # -----------------------------------------------------------------------

    def train(self, rounds=2):
        """
        Perform one or more rounds of HERest estimation.

        @param rounds (int) Number of times HERest is called.

        """
        for _ in range(rounds):
            logging.debug("Training iteration {}.".format(self.epochs))
            self.init_epoch_dir()

            subprocess.check_call(["HERest", "-C", self.HERest_cfg,
                        "-S", self.corpus.scp0file,
                        "-I", self.corpus.alignmlffile,
                        "-M", self.curdir,
                        "-H", os.path.join(self.prevdir, DEFAULT_MACROS_FILENAME),
                        "-H", os.path.join(self.prevdir, DEFAULT_HMMDEFS_FILENAME),
                        "-t"] + self.pruning + [self.corpus.monophones.get_list()],
                       stdout=subprocess.PIPE)

            # Check if we got the expected files.

            # OK, we can go to the next round
            self.epochs = self.epochs + 1

    # -----------------------------------------------------------------------

    def training_recipe(self, corpus):
        #if flatstart:
        #    logging.info("Flat start training.")
        #    self.flatstart(corpus)

        initial = HTKModelInitializer( self.corpus )
        initial.create_model()

        logging.info("Initial training.")
        self.train(corpus)

        logging.info("Modeling silence.")
        self.small_pause(corpus)

        logging.info("Additional training.")
        self.train(corpus)

        logging.info("Realigning.")
        self.realign(corpus)

        logging.info("Final training.")
        self.train(corpus)

    # -----------------------------------------------------------------------

    def __del__(self):
        self.corpus.datatrainer.delete()


# ---------------------------------------------------------------------------
