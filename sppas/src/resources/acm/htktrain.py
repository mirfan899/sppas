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
        with open( filename, "w") as fp:
            fp.write("TARGETKIND = MFCC_0_D_N_Z\n")
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

    # -----------------------------------------------------------------------

    def create(self):
        """
        Create all directories and their content (if possible) with their
        default names.

        """
        self.fix_working_dir()
        self.fix_proto()
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

    def fix_working_dir(self, workdir=None, scriptsdir=DEFAULT_SCRIPTS_DIR, featsdir=DEFAULT_FEATURES_DIR, logdir=DEFAULT_LOG_DIR):
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

    # -----------------------------------------------------------------------

    def fix_proto(self, protodir=DEFAULT_PROTO_DIR):
        """
        Create a `protos` directory and add the default proto file.

        """
        if os.path.exists( protodir ) is False:
            protodir = os.path.join(self.workdir, DEFAULT_PROTO_DIR)
            os.mkdir( protodir )
        self.protodir = protodir

        self.write_htk_proto()

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

    def write_htk_proto(self, protofilename=DEFAULT_PROTO_FILENAME):
        """
        Write the `proto` file into the proto directory.
        The proto is based on a 5-states HMM.

        @param protofilename (str) Name of the prototype to write (without the path).

        """
        if self.protodir is None:
            raise IOError("A proto directory must be defined.")
        if os.path.exists( self.protodir) is False:
            raise IOError("Bad proto directory.")

        h = HMM()
        h.create_proto( self.features.nbmv )
        h.save( os.path.join( self.protodir, protofilename ) )

        self.protofile = protofilename

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

class HTKModelInitializer( object ):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model initializer.

    Monophones initialization is the step 2 of the acoustic model training
    procedure.

    """
    def __init__(self, datatrainer, directory):
        """
        Constructor.

        """
        self.datatrainer = datatrainer
        self.directory = directory

    # -----------------------------------------------------------------------

    def create_vFloors(self):
        """
        Create a new version of proto in the directory with `HCompV`.
        This creates two files in the directory:
            * proto
            * vFloors

        """
        scpfile = "./mfcc-phon/train0.scp"
        subprocess.check_call(["HCompV", "-A -D -T 1 -m",
                              "-f", str(0.01),
                              "-C", self.datatrainer.features.configfile,
                              "-S", scpfile,
                              "-M", self.directory, self.datatrainer.protofile])

    # -----------------------------------------------------------------------

    def create_model(self):
        """
        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def create_macros(self):
        """
        Create macros File
            * create a new file called macros in directory;
            * copy the first 3 lines of proto, add them to the top of the macros file;
            * copy vFloors to macros.
        """
        raise NotImplementedError

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

    Step 3 is the monophones generation.
    This first model is re-estimated using the MFCC files
    to create a new model, using ``HERest''. Then, it fixes the ``sp''
    model from the ``sil'' model by extracting only 3 states of the initial
    5-states model. Finally, this monophone model is re-estimated using the
    MFCC files and the training data.

    Step 4 creates tied-state triphones from monophones and from some language
    specificities defined by means of a configuration file.

    """
    def __init__(self, datatrainer=None):
        """
        Constructor.

        """
        # Prepare or set all directories to work with.
        self.data = datatrainer
        if self.data is None:
            self.data = DataTrainer()
        try:
            self.data.check()
        except IOError:
            self.data.create()

        self.monophones = PhoneSet()

        # Epoch directories (the content of one round of train)
        self.epochs = 0
        self.curdir = None

    # -----------------------------------------------------------------------

    def write_mlf(self, corpusdir, tiername, mlffilename):
        """
        Write a mlf file from a corpus.
        All annotated files are loaded and examined to get the given tier
        and to append it into the mlf file.

        """
        pass

    # -----------------------------------------------------------------------

    def init_epoch_dir(self):
        """
        Create an epoch directory to work with.

        """
        nextdir = os.path.join(self.data.workdir, "hmm", str(self.epochs).zfill(3))
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
        corpus = None ########################
        for _ in range(rounds):
            logging.debug("Training iteration {}.".format(self.epochs))
            self.init_epoch_dir()

            subprocess.check_call(["HERest", "-C", self.HERest_cfg,
                        "-S", corpus.feature_scp,
                        "-I", corpus.phon_mlf,
                        "-M", self.curdir,
                        "-H", os.path.join(self.prevdir, DEFAULT_MACROS_FILENAME),
                        "-H", os.path.join(self.prevdir, DEFAULT_HMMDEFS_FILENAME),
                        "-t"] + self.pruning + [corpus.phons],
                       stdout=subprocess.PIPE)

            # Check if we got the expected files.

            # OK, we can go to the next round
            self.epochs = self.epochs + 1

    # -----------------------------------------------------------------------

    def training_recipe(self, corpus):
        #if flatstart:
        #    logging.info("Flat start training.")
        #    self.flatstart(corpus)

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
        self.data.delete()


# ---------------------------------------------------------------------------
