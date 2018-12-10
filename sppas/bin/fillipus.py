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

    bin.fillipus.py
    ~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Search IPUs and fill in with a transcription

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.FillIPUs.sppasfillipus import sppasFillIPUs
from sppas.src.anndata.aio import extensions_out
from sppas.src.config import annots
from sppas.src.annotations.param import sppasParam

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam("fillipus")
    ann_step_idx = parameters.activate_annotation("fillipus")
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

    parser.add_argument(
        "-i",
        metavar="file",
        help='Input wav file name.')

    parser.add_argument(
        "-t",
        metavar="file",
        help='Input transcription file name.')

    parser.add_argument(
        "-o",
        metavar="file",
        help='Annotated file with filled IPUs ')

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

    # get options from arguments
    # --------------------------
    arguments = vars(args)
    for a in arguments:
        if a not in ('i', 'o', 't', 'e', 'quiet'):
            parameters.set_option_value(ann_step_idx, a, arguments[a])

    # Perform the annotation on a single file
    # ---------------------------------------
    if args.i:
        if not args.t:
            print("argparse.py: error: option -t is required with option -i")
            sys.exit(1)
        ann = sppasFillIPUs(logfile=None)
        ann.fix_options(parameters.get_options(ann_step_idx))
        if args.o:
            ann.run(args.i, args.t, args.o)
        else:
            trs = ann.run(args.i, args.t, None)
            for ann in trs[0]:
                print("{:f} {:f} {:s}".format(
                    ann.get_location().get_best().get_begin().get_midpoint(),
                    ann.get_location().get_best().get_end().get_midpoint(),
                    ann.get_best_tag().get_typed_content()))
        sys.exit(0)
