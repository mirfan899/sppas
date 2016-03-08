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

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import logging
import os
import subprocess

from resources.dictpron import DictPron

DEFAULT_PROTO_FILENAME="proto"
DEFAULT_MONOPHONES_FILENAME="monophones"

# ---------------------------------------------------------------------------

class AcModelTrainer(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Acoustic model trainer.

    """

    def __init__(self):
        """
        Constructor.

        """
        self.protodir = None

        # make temporary directories to stash everything
        hmmdir = os.environ["TMPDIR"] if "TMPDIR" in os.environ else None
        self.hmmdir = mkdtemp(dir=hmmdir)

        # initialize directories
        self.epochs = 0
        self.curdir = os.path.join(self.hmmdir, str(self.epochs).zfill(3))
        os.makedirs(self.curdir, exist_ok=True)


    def write_htk_proto(self, protosize, protofilename=DEFAULT_PROTO_FILENAME):
        """
        Write the `proto` file into the proto directory.
        The proto is based on a 5-states HMM.

        @param protosize (int) Number of mean and variance values. It's commonly
        either 25 or 39, it depends on the MFCC parameters.
        @param protofilename (str) Name of the prototype to write (without the path).

        """
        # TODO: Define an HMM instance, then use HMM.create_proto(), then HMM.save(fn)
        if self.protodir is None:
            raise IOError("A proto directory must be fixed.")

        with open(os.path.join( self.protodir, protofilename ), "w") as fp:
            means     = "0.0 "*protosize
            variances = "1.0 "*protosize

            fp.write("~h \"proto\"\n")
            fp.write("<BeginHMM>\n")
            fp.write("<NumStates> 5\n")
            for i in range(2, 5):
                fp.write("<State> {}\n".format(i))
                fp.write("<Mean> %d\n"%protosize)
                fp.write("%s\n"%means)
                fp.write("<Variance> %d\n"%protosize)
                fp.write("%s\n"%variances)
            fp.write("<Transp> 5\n")
            fp.write(" 0.0 1.0 0.0 0.0 0.0\n")
            fp.write(" 0.0 0.6 0.4 0.0 0.0\n")
            fp.write(" 0.0 0.0 0.6 0.4 0.0\n")
            fp.write(" 0.0 0.0 0.0 0.7 0.3\n")
            fp.write(" 0.0 0.0 0.0 0.0 0.0\n")
            fp.write("<EndHMM>\n")

        self.protofile = protofilename



    def write_monophones(self, dictfilename, monophonesfilename=DEFAULT_MONOPHONES_FILENAME):
        """
        Write the monophones file, created from a pronunciation dictionary.
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


    def write_mlf(self, corpusdir, tiername, mlffilename):
        """
        Write a mlf file from a corpus.
        All annotated files are loaded and examined to get the given tier
        and to append it into the mlf file.

        """
        pass


    def check_init(self, directory):
        """
        """
        if self.prododir is None:
            raise IOError("No proto directory.")
        if os.path.isdir( self.prododir ) is False:
            raise IOError("Bad proto directory.")


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
