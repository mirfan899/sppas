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

import utils.fileutils

from resources.dictpron import DictPron
from hmm        import HMM
from htkscripts import HtkScripts

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_PROTO_FILENAME="proto"
DEFAULT_MONOPHONES_FILENAME="monophones"

DEFAULT_PROTO_DIR="protos"
DEFAULT_SCRIPTS_DIR="scripts"
DEFAULT_LOG_DIR="log"
DEFAULT_DICT_DIR="dict"

# ---------------------------------------------------------------------------

class DataTrainer(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model trainer: data manager.

    """
    def __init__(self):
        """
        Constructor.

        """
        # The directory with all HMM prototypes, and the default proto file.
        self.protodir  = None
        self.protofile = None

        # The working directory. Commonly temporary, used to stash everything
        self.workdir    = None
        self.scriptsdir = None
        self.logdir     = None
        self.dictdir    = None

    # -----------------------------------------------------------------------

    def default_init(self):
        """
        Create all directories and their content (if possible) with their
        default names.

        """
        self.init_working_dir()
        self.init_proto_dir()
        self.check()

    # -----------------------------------------------------------------------

    def init_working_dir(self, workdir=None, scriptsdir=DEFAULT_SCRIPTS_DIR, logdir=DEFAULT_LOG_DIR):
        """
        Initialize the working directory and its folders if necessary.
        Notice that the working directory is normally deleted at the end
        of the training procedure.

        """
        if self.workdir is None:
            self.workdir = utils.fileutils.gen_name()
            os.mkdir( self.workdir )

        if os.path.exists( scriptsdir ) is False:
            scriptsdir = os.path.join(self.workdir,scriptsdir)
            h = HtkScripts()
            h.write_all( scriptsdir )
        else:
            # TODO: check scriptsdir file by file...
            pass

        if os.path.exists( logdir ) is False:
            logdir = os.path.join(self.workdir,logdir)
            os.mkdir( logdir )

        self.scriptsdir = scriptsdir
        self.logdir     = logdir

    # -----------------------------------------------------------------------

    def init_proto_dir(self):
        """
        Create a proto directory and add the default proto file.

        """
        self.protodir = os.path.join(self.workdir, DEFAULT_PROTO_DIR)
        os.mkdir( self.protodir )

        self.write_htk_proto( 25 )

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

        if self.logdir is None:
            raise IOError("No log directory defined.")
        if os.path.isdir( self.logdir ) is False:
            raise IOError("Bad log directory.")

    # -----------------------------------------------------------------------

    def write_htk_proto(self, protosize, protofilename=DEFAULT_PROTO_FILENAME):
        """
        Write the `proto` file into the proto directory.
        The proto is based on a 5-states HMM.

        @param protosize (int) Number of mean and variance values. It's commonly
        either 25 or 39, it depends on the MFCC parameters.
        @param protofilename (str) Name of the prototype to write (without the path).

        """
        if self.protodir is None:
            raise IOError("A proto directory must be defined.")
        if os.path.exists( self.protodir) is False:
            raise IOError("Bad proto directory.")

        h = HMM()
        h.create_proto( protosize )
        h.save( os.path.join( self.protodir, protofilename ) )

        self.protofile = protofilename

    # -----------------------------------------------------------------------

# ---------------------------------------------------------------------------

class HTKModelTrainer(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model trainer.

    This class allows to train an acoustic model from audio data and their
    transcriptions (either phonetic or orthographic or both).

    It is based on the HTK toolbox.

    """

    def __init__(self, datatrainer=None):
        """
        Constructor.

        """
        # Prepare or set a data directory.
        self.data = datatrainer
        if self.data is None:
            self.data = DataTrainer()
        try:
            self.data.check()
        except IOError:
            self.data.default_init()

        # Epoch directories (the content of one round of train)
        self.epochs = 0
        self.curdir = None

    # -----------------------------------------------------------------------

    def write_monophones(self, dictfilename, monophonesfilename=DEFAULT_MONOPHONES_FILENAME):
        """
        Write the monophones file, created from a pronunciation dictionary.
        Add events to this list (laughter, dummy, noise, silence).

        """
        d = DictPron( dictfilename ).get_dict()
        phoneset = ["@@", "dummy", "gb", "sil"]
        for value in d.values():
            variants = value.split("|")
            for phone in variants.split("."):
                if not phone in phoneset:
                    phoneset.append( phone )

        self.monophones = os.path.join(self.hmmdir, monophonesfilename)
        with open(self.monophones, "w") as fp:
            for phone in sorted(phoneset):
                fp.write('%s\n'%phone)

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

        self.curdir = nextdir

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

# ---------------------------------------------------------------------------
