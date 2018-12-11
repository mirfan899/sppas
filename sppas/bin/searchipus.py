#!/usr/bin/env python
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

    bin.searchipus.py
    ~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      IPUs automatic detection.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.SearchIPUs.sppassearchipus import sppasSearchIPUs
from sppas.src.anndata.aio import extensions_out
from sppas.src.config import annots
from sppas.src.annotations.param import sppasParam
from sppas.src.config.ui import sppasAppConfig
from sppas.src.annotations.manager import sppasAnnotationsManager
from sppas.src.utils.fileutils import setup_logging

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["SearchIPUs.ini"])
    ann_step_idx = parameters.activate_annotation("searchipus")
    ann_options = parameters.get_options(ann_step_idx)

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="{:s} ...".format(os.path.basename(PROGRAM)),
        description=
        parameters.get_step_name(ann_step_idx) + " automatic annotation: " +
        parameters.get_step_descr(ann_step_idx))

    # Add arguments for input/output of the annotations
    # -------------------------------------------------

    input_group = parser.add_mutually_exclusive_group()

    input_group.add_argument(
        "-i",
        metavar="file",
        help='Input wav file name.')

    parser.add_argument(
        "-o",
        metavar="file",
        help='Annotated file with silences/units segmentation '
             '(default: None)')

    parser.add_argument(
        "-I",
        action='append',
        metavar="file",
        help='Input wav file name (append).')

    parser.add_argument(
        "-e",
        default=annots.extension,
        metavar="extension",
        choices=extensions_out,
        help='Output file extension. One of: {:s}'
             ''.format(" ".join(extensions_out)))

    # Add arguments from the options of the annotation
    # ------------------------------------------------

    for opt in ann_options:
        parser.add_argument(
            "--" + opt.get_key(),
            type=opt.type_mappings[opt.get_type()],
            default=opt.get_value(),
            help=opt.get_text() + " (default: {:s})"
                                  "".format(opt.get_untypedvalue()))

    # Add quiet and help arguments
    # ----------------------------

    parser.add_argument("--quiet",
                        action='store_true',
                        help="Print only warnings and errors.")

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # The automatic annotation is here:
    # -----------------------------------------------------------------------

    # Redirect all messages to logging
    # --------------------------------

    with sppasAppConfig() as cg:
        parameters.set_logfilename(cg.log_file)
        if not args.quiet:
            setup_logging(cg.log_level, None)
        else:
            setup_logging(cg.quiet_log_level, None)

    # Get options from arguments
    # --------------------------

    arguments = vars(args)
    for a in arguments:
        if a not in ('i', 'o', 'I', 'e', 'quiet'):
            parameters.set_option_value(ann_step_idx, a, arguments[a])

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        ann = sppasSearchIPUs(logfile=None)
        ann.fix_options(parameters.get_options(ann_step_idx))
        if args.o:
            ann.run(args.i, args.o)
        else:
            trs = ann.run(args.i, None)
            for ann in trs[0]:
                print("{:f} {:f} {:s}".format(
                    ann.get_location().get_best().get_begin().get_midpoint(),
                    ann.get_location().get_best().get_end().get_midpoint(),
                    ann.get_best_tag().get_typed_content()))

    elif args.I:

        # Perform the annotation on a set of files
        # ----------------------------------------

        # Fix the output file extension
        parameters.set_output_format(args.e)

        # Fix input files
        files = list()
        for f in args.I:
            parameters.add_sppasinput(os.path.abspath(f))

        # Redirect all messages to logging.
        with sppasAppConfig() as cg:
            parameters.set_logfilename(cg.log_file)
            if not args.quiet:
                setup_logging(cg.log_level, None)
            else:
                setup_logging(cg.quiet_log_level, None)

        # Perform the annotation
        process = sppasAnnotationsManager(parameters)
        process.run_searchipus()

    else:

        if not args.quiet:
            print("No file was given to be annotated. Nothing to do!")
