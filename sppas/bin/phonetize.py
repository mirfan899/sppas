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

    bin.phonetize.py
    ~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      contact@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2019  Brigitte Bigi
:summary:      Phonetization automatic annotation.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg, annots
from sppas.src.anndata.aio import extensions_out
from sppas import sppasPhon
from sppas.src.annotations.Phon.phonetize import sppasDictPhonetizer
from sppas import sppasDictPron
from sppas import sppasMapping
from sppas import sppasParam
from sppas import sppasAnnotationsManager
from sppas import sppasLogSetup
from sppas import sppasAppConfig


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam(["phonetize.json"])
    ann_step_idx = parameters.activate_annotation("phonetize")
    ann_options = parameters.get_options(ann_step_idx)

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description=
        parameters.get_step_name(ann_step_idx) + ": " +
        parameters.get_step_descr(ann_step_idx),
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__)
    )

    parser.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    parser.add_argument(
        "--log",
        metavar="file",
        help="File name for a Procedure Outcome Report (default: None)")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-i",
        metavar="file",
        help='Input tokenization file name.')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Annotated file with phonetization')

    group_io.add_argument(
        "-I",
        metavar="file",
        action='append',
        help='Input transcription file name (append).')

    group_io.add_argument(
        "-r",
        metavar="dict",
        help='Pronunciation dictionary (HTK-ASCII format).')

    group_io.add_argument(
        "-l",
        metavar="lang",
        choices=parameters.get_langlist(ann_step_idx),
        help='Language code (iso8859-3). One of: {:s}.'
             ''.format(" ".join(parameters.get_langlist(ann_step_idx))))

    group_io.add_argument(
        "-e",
        metavar=".ext",
        default=annots.extension,
        choices=extensions_out,
        help='Output file extension. One of: {:s}'
             ''.format(" ".join(extensions_out)))

    group_io.add_argument(
        "-m",
        metavar="map_file",
        required=False,
        help='Pronunciation mapping table. '
             'It is used to generate new pronunciations by '
             'mapping phonemes of the dictionary.')

    # Add arguments for the options
    # -----------------------------

    group_opt = parser.add_argument_group('Options')

    for opt in ann_options:
        group_opt.add_argument(
            "--" + opt.get_key(),
            type=opt.type_mappings[opt.get_type()],
            default=opt.get_value(),
            help=opt.get_text() + " (default: {:s})"
                                  "".format(opt.get_untypedvalue()))

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Mutual exclusion of inputs
    # --------------------------

    if args.i and args.I:
        parser.print_usage()
        print("{:s}: error: argument -I: not allowed with argument -i"
              "".format(os.path.basename(PROGRAM)))
        sys.exit(1)

    # -----------------------------------------------------------------------
    # The automatic annotation is here:
    # -----------------------------------------------------------------------

    # Redirect all messages to logging
    # --------------------------------

    with sppasAppConfig() as cg:
        if not args.quiet:
            log_level = cg.log_level
        else:
            log_level = cg.quiet_log_level
        lgs = sppasLogSetup(log_level)
        lgs.stream_handler()

    # Get options from arguments
    # --------------------------

    arguments = vars(args)
    for a in arguments:
        if a not in ('i', 'o', 'r', 'l', 'm', 'I', 'e', 'quiet', 'log'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        if not args.r:
            print("argparse.py: error: option -r is required with option -i")
            sys.exit(1)

        ann = sppasPhon(log=None)
        ann.load_resources(args.r, args.m)
        ann.fix_options(parameters.get_options(ann_step_idx))
        if args.o:
            ann.run([args.i], output_file=args.o)
        else:
            trs = ann.run([args.i])
            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    if a.location_is_point():
                        print("{}, {:s}".format(
                            a.get_location().get_best().get_midpoint(),
                            a.serialize_labels(" ")))
                    else:
                        print("{}, {}, {:s}".format(
                            a.get_location().get_best().get_begin().get_midpoint(),
                            a.get_location().get_best().get_end().get_midpoint(),
                            a.serialize_labels(" ")))

    elif args.I:

        # Perform the annotation on a set of files
        # ----------------------------------------

        if not args.l:
            print("argparse.py: error: option -l is required with option -I")
            sys.exit(1)

        # Fix input files
        for f in args.I:
            parameters.add_to_workspace(os.path.abspath(f))

        # Fix the output file extension and others
        parameters.set_lang(args.l)
        parameters.set_output_format(args.e)
        parameters.set_report_filename(args.log)

        # Perform the annotation
        process = sppasAnnotationsManager()
        process.annotate(parameters)

    else:

        # Perform the annotation on stdin
        # an argument 'unk' must exists (which is in the options).
        # -------------------------------

        if not args.phonunk:
            print("argparse.py: error: option -unk is required")
            sys.exit(1)

        if not args.r:
            print("argparse.py: error: option -r is required")
            sys.exit(1)

        pdict = sppasDictPron(args.r, nodump=False)
        mapping = sppasMapping()
        if args.m:
            map_table = sppasMapping(args.m)
        phonetizer = sppasDictPhonetizer(pdict, mapping)
        for line in sys.stdin:
            print("{:s}".format(phonetizer.phonetize(line, args.phonunk)))
