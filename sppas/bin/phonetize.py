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
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Phonetization automatic annotation.

"""
import sys
import os
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.Phon.sppasphon import sppasPhon
from sppas.src.annotations.Phon.phonetize import sppasDictPhonetizer
from sppas.src.resources.dictpron import sppasDictPron
from sppas.src.resources.mapping import sppasMapping
from sppas.src.anndata.aio import extensions_out
from sppas.src.config import annots
from sppas.src.annotations.param import sppasParam


if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Fix initial annotation parameters
    # -----------------------------------------------------------------------

    parameters = sppasParam("phon")
    ann_step_idx = parameters.activate_annotation("phon")
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
        help='Input tokenization file name.')

    parser.add_argument(
        "-o",
        metavar="file",
        help='Annotated file with filled IPUs ')

    parser.add_argument(
        "-r", "--dict",
        required=True,
        help='Pronunciation dictionary (HTK-ASCII format).')

    parser.add_argument(
        "-m", "--map",
        required=False,
        help='Pronunciation mapping table. '
             'It is used to generate new pronunciations by '
             'mapping phonemes of the dictionary.')

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
        if a not in ('i', 'o', 'dict', 'map', 'e', 'quiet'):
            parameters.set_option_value(ann_step_idx, a, str(arguments[a]))
            o = parameters.get_step(ann_step_idx).get_option_by_key(a)

    if args.i:

        # Perform the annotation on a single file
        # ---------------------------------------

        ann = sppasPhon(args.dict, map_filename=args.map, logfile=None)
        ann.fix_options(parameters.get_options(ann_step_idx))
        if args.o:
            ann.run(args.i, args.o)
        else:
            trs = ann.run(args.i, None)
            for tier in trs:
                print(tier.get_name())
                for a in tier:
                    print("{:f} {:f} {:s}".format(
                        a.get_location().get_best().get_begin().get_midpoint(),
                        a.get_location().get_best().get_end().get_midpoint(),
                        a.serialize_labels(" ")))

    else:

        # Perform the annotation on stdin
        # an argument 'unk' must exists.
        # -------------------------------

        pdict = sppasDictPron(args.dict, nodump=False)
        mapping = sppasMapping()
        if args.map:
            map_table = sppasMapping(args.map)
        phonetizer = sppasDictPhonetizer(pdict, mapping)
        for line in sys.stdin:
            print("{:s}".format(phonetizer.phonetize(line, args.unk)))
