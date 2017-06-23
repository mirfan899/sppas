#!/usr/bin/env python2
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

    scripts.acmtrain.py
    ~~~~~~~~~~~~~~~~~~~

    ... a script to train an acoustic model.

"""
import sys
import os.path
import logging
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.models.acm.htktrain import HTKModelTrainer, TrainingCorpus, DataTrainer
from sppas.src.utils.fileutils import setup_logging


# ----------------------------------------------------------------------------
# The main function:

def train(pron_dict,
          mapping_table,
          protos_dir,
          corpus_dir_list,
          lang,
          working_dir,
          output_dir):

    # ---------------------------------
    # 1. Create a Data Manager
    # it manages the data created at each step of the acm training procedure
    # create parameters:
    #  - workdir=None (in)
    #  - scriptsdir=DEFAULT_SCRIPTS_DIR (in)
    #  - featsdir=DEFAULT_FEATURES_DIR (in)
    #  - logdir=DEFAULT_LOG_DIR (in)
    #  - protodir=None (in)
    #  - protofilename=DEFAULT_PROTO_FILENAME (out)

    datatrainer = DataTrainer()
    # we could either use:
    #  datatrainer.create( workdir=args.t, protodir=args.p )
    # or:
    datatrainer.fix_working_dir(workdir=working_dir)
    datatrainer.fix_proto(proto_dir=protos_dir)
    datatrainer.check()

    # ---------------------------------
    # 2. Create a Corpus Manager
    # it manages the set of training data:
    #   - establishes the list of phonemes (from the dict);
    #   - converts the input annotated data into the HTK-specific data format;
    #   - codes the audio data.

    corpus = TrainingCorpus(datatrainer, lang=lang)
    corpus.fix_resources(dictfile=pron_dict, mappingfile=mapping_table)

    if corpus_dir_list:
        for entry in corpus_dir_list:
            if os.path.isdir(entry):
                corpus.add_corpus(entry)
            else:
                logging.info('[ WARNING ] Ignore the given entry: %s' % entry)

    # ---------------------------------
    # 3. Acoustic Model Training

    trainer = HTKModelTrainer(corpus)
    DELETE = False
    if args.t is None:
        DELETE = True
    trainer.training_recipe(outdir=output_dir, delete=DELETE)

    # ---------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -r dict " % os.path.basename(PROGRAM),
                        description="... a script to train an acoustic model.")

parser.add_argument("-r",
                    metavar="dict",
                    required=True,
                    help='Pronunciation dictionary (HTK-ASCII format).')

parser.add_argument("-m",
                    metavar="map",
                    required=False,
                    default=None,
                    help='Phoneset mapping table SAMPA <-> Model, '
                         'if dict is based on SAMPA phoneme encoding.')

parser.add_argument("-p",
                    metavar="protos",
                    required=False,
                    default=None,
                    help='Directory with HMM prototypes.')

parser.add_argument("-i",
                    metavar="input",
                    required=False,
                    action='append',
                    help='Input directory name(s) of the training corpus.')

parser.add_argument("-l",
                    metavar="lang",
                    required=False,
                    default="und",
                    help='Language code in ISO639-3 format. Default: und')

parser.add_argument("-t",
                    metavar="temp",
                    required=False,
                    default=None,
                    help='Working directory name.')

parser.add_argument("-o",
                    metavar="output",
                    required=False,
                    default=None,
                    help='Output directory name.')

parser.add_argument("--quiet", action='store_true', help="Disable the verbosity." )

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------
# Main program
# ----------------------------------------------------------------------------

if not args.quiet:
    setup_logging(1, None)
else:
    setup_logging(None, None)

train(pron_dict=args.r,
      mapping_table=args.m,
      protos_dir=args.p,
      corpus_dir_list=args.i,
      lang=args.l,
      working_dir=args.t,
      output_dir=args.o)
