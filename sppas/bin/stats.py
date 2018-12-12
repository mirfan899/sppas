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

    scripts.stats.py
    ~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to estimate stats of annotated files.

"""

import logging
import sys
import os.path
from argparse import ArgumentParser
import codecs
import pickle
import time

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sg
from sppas.src.anndata import sppasRW
from sppas.src.presenters.tierstats import TierStats
from sppas.src.utils.fileutils import setup_logging
from sppas.src.config.ui import sppasAppConfig

# ----------------------------------------------------------------------------

modes_help = "Stat to estimate, in:\n"
modes_help += "  0 = ALL,\n"
modes_help += "  1 = Occurrences,\n"
modes_help += '  2 = Total duration,\n'
modes_help += '  3 = Average duration,\n'
modes_help += '  4 = Median duration,\n'
modes_help += '  5 = Standard deviation duration.'

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(
        usage="%(prog)s [files] [options]",
        description="... a program to estimate distributions of annotations.",
        add_help=True,
        epilog="This program is part of {:s} version {:s}. {:s}. Contact the "
               "author at: {:s}".format(sg.__name__, sg.__version__,
                                        sg.__copyright__, sg.__contact__))

    group_verbose = parser.add_mutually_exclusive_group()

    group_verbose.add_argument(
        "--quiet",
        action='store_true',
        help="Disable the verbosity")

    group_verbose.add_argument(
        "--debug",
        action='store_true',
        help="Highest level of verbosity")

    # Add arguments for input/output files
    # ------------------------------------

    group_io = parser.add_argument_group('Files')

    group_io.add_argument(
        "-i",
        metavar="file",
        action='append',
        required=True,
        help='Input annotated file name (as many as wanted)')

    group_io.add_argument(
        "-o",
        metavar="file",
        help='Output annotated file name')

    # Add arguments for the options
    # -----------------------------

    group_opt = parser.add_argument_group('Options')

    group_opt.add_argument(
        "-t",
        metavar="tiername",
        required=True,
        type=str,
        help='Name of the tier to estimate distributions.')

    group_opt.add_argument(
        "-s",
        metavar="stat",
        type=int,
        action="append",
        help=modes_help)

    group_opt.add_argument(
        "-n",
        metavar="ngram",
        default=1,
        type=int,
        help='Value of N of the Ngram sequences (default: 1; Max: 5)')

    # Force to print help if no argument is given then parse
    # ------------------------------------------------------

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # Redirect all messages to logging
    # --------------------------------

    with sppasAppConfig() as cg:
        if not args.quiet:
            if args.debug:
                setup_logging(0, None)
            else:
                setup_logging(cg.log_level, None)
        else:
            setup_logging(cg.quiet_log_level, None)

    # -----------------------------------------------------------------------
    # Check args. Set variables: modes, ngram, tier_name
    # -----------------------------------------------------------------------

    if args.s:
        modes = args.s
        for mode in args.s:
            if mode not in range(6):
                logging.error("Unknown stat: {}".format(mode))
                sys.exit(1)
    else:
        modes = [0]

    ngram = 1
    if args.n:
        if args.n < 6:
            ngram = args.n
        else:
            logging.warning("Invalid ngram value {:d}. Max is 5."
                            "".format(args.n))

    tier_name = args.t
    tier_name = tier_name.replace(' ', '_')

    # -----------------------------------------------------------------------
    # Read data
    # -----------------------------------------------------------------------

    tiers = list()
    files = list()
    for file_input in args.i:

        logging.info("Read {:s}".format(args.i))
        start_time = time.time()
        parser = sppasRW(file_input)
        trs_input = parser.read()
        end_time = time.time()

        # General information
        # -------------------
        logging.debug(
            "Elapsed time for reading: {:f} seconds"
            "".format(end_time - start_time))
        pickle_string = pickle.dumps(trs_input)
        logging.debug(
            "Memory usage of the transcription: {:d} bytes"
            "".format(sys.getsizeof(pickle_string)))

        # Get expected tier
        # -----------------
        tier = trs_input.find(args.t, case_sensitive=False)
        if tier is not None:
            tiers.append(tier)
            files.append(file_input)
            logging.info("  - Tier {:s}. Selected."
                         "".format(tier.get_name()))
        else:
            logging.error("  - Tier {:s}: Not found."
                          "".format(args.t))

    # ----------------------------------------------------------------------------
    # Estimates statistical distributions
    # ----------------------------------------------------------------------------

    t = TierStats(tiers)
    t.set_ngram(ngram)

    ds = t.ds()
    occurrences = dict()
    total = dict()
    mean = dict()
    median = dict()
    stdev = dict()

    title = ["filename", "tier", "annotation tag"]
    stats = dict()  # used only to get the list of keys
    if 0 in modes or 1 in modes:
        occurrences = ds.len()
        title.append('occurrences')
        stats = occurrences
    if 0 in modes or 2 in modes:
        total = ds.total()
        title.append('total duration')
        if not stats:
            stats = total
    if 0 in modes or 3 in modes:
        mean = ds.mean()
        title.append('mean duration')
        if not stats:
            stats = mean
    if 0 in modes or 4 in modes:
        median = ds.median()
        title.append('median duration')
        if not stats:
            stats = median
    if 0 in modes or 5 in modes:
        stdev = ds.stdev()
        title.append('Std dev duration')
        if not stats:
            stats = stdev

    # -----------------------------------------------------------------------
    # Format statistical distributions
    # -----------------------------------------------------------------------

    row_data = list()
    row_data.append(title)

    for i, key in enumerate(stats.keys()):
        if len(key) == 0:  # ignore empty label
            continue
        row = ["file", tier_name, key]
        if 0 in modes or 1 in modes:
            row.append(str(occurrences[key]))
        if 0 in modes or 2 in modes:
            row.append(str(round(total[key], 3)))
        if 0 in modes or 3 in modes:
            row.append(str(round(mean[key], 3)))
        if 0 in modes or 4 in modes:
            row.append(str(round(median[key], 3)))
        if 0 in modes or 5 in modes:
            row.append(str(round(stdev[key], 3)))
        row_data.append(row)

    # -----------------------------------------------------------------------
    # Save stats
    # -----------------------------------------------------------------------

    if args.o:
        file_output = args.o
        with codecs.open(file_output, 'w', sg.__encoding__) as fp:
            for row in row_data:
                s = ','.join(row)
                fp.write(s)
                fp.write('\n')

    else:
        for row in row_data:
            print(','.join(row))
