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
    ~~~~~~~~~~~~~~~~

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
from sppas.src.utils.fileutils import setup_logging

# ---------------------------------------------------------------------------
# Verify and extract args:
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    w = sppasSearchIPUs()

    parser = ArgumentParser(usage="{:s} -w file [options]"
                                  "".format(os.path.basename(PROGRAM)),
                            description="Search for IPUs automatic annotation.")

    parser.add_argument("-w",
                        metavar="file",
                        required=True,
                        help='Input wav file name')

    # Silence/Speech segmentation options:
    parser.add_argument("-r", "--winrms",
                        type=float,
                        default=w.get_win_length(),
                        help='Window size to estimate rms, in seconds '
                             '(default: {:f})'.format(w.get_win_length()))

    parser.add_argument("-m",
                        "--minipu",
                        type=float,
                        default=w.get_min_ipu(),
                        help='Drop speech shorter than m seconds long '
                             '(default: {:f})'.format(w.get_min_ipu()))

    parser.add_argument("-s",
                        "--minsil",
                        type=float,
                        default=w.get_min_sil(),
                        help='Drop silences shorter than s seconds long '
                             '(default: {:f})'.format(w.get_min_sil()))

    parser.add_argument("-v",
                        "--minrms",
                        type=int,
                        default=w.get_threshold(),
                        help='Assume everything with a rms lower than v is a silence. 0=automatic adjust.'
                             '(default: {:d})'.format(w.get_threshold()))

    # Other options:
    parser.add_argument("-d",
                        "--shiftstart",
                        type=float,
                        default=w.get_shift_start(),
                        help='Shift-left the start boundary of IPUs '
                             '(default: {:f})'.format(w.get_shift_start()))

    parser.add_argument("-D",
                        "--shiftend",
                        type=float,
                        default=w.get_shift_end(),
                        help='Shift-right the end boundary of IPUs '
                             '(default: {:f})'.format(w.get_shift_end()))

    # Output options:
    parser.add_argument("-o",
                        metavar="file",
                        help='Annotated file with silences/units segmentation '
                             '(default: None)')

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    log_level = 1
    log_file = None
    setup_logging(log_level, log_file)

    # ----------------------------------------------------------------------------
    # Automatic IPUs segmentation is here:
    # ----------------------------------------------------------------------------

    w.set_shift_start(args.shiftstart)
    w.set_shift_end(args.shiftend)
    w.set_min_ipu(args.minipu)
    w.set_min_sil(args.minsil)
    w.set_threshold(args.minrms)
    w.set_win_length(args.winrms)

    trs_out = w.run(args.w, args.o)
