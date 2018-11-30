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

    scripts.tieradjustbounds.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

:author:       Brigitte Bigi
:organization: Laboratoire Parole et Langage, Aix-en-Provence, France
:contact:      develop@sppas.org
:license:      GPL, v3
:copyright:    Copyright (C) 2011-2018  Brigitte Bigi
:summary:      a script to get information about a tier of an annotated file.

"""
import sys
import os
import math
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas import sppasRW

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} -i file [options]"
                              "".format(os.path.basename(PROGRAM)),
                        description="... a script to get information about "
                                    "a tier of an annotated file.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-t",
                    required=True,
                    metavar="adjust",
                    help='Name of the tier to be adjusted')

parser.add_argument("-T",
                    required=True,
                    metavar="bounds",
                    help='Name of the tier to adjust bounds on')

parser.add_argument("-d",
                    metavar="value",
                    default=0.04,
                    type=float,
                    help='Maximum time diff to adjust a bound (default: 0.04)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()

# ----------------------------------------------------------------------------

parser = sppasRW(args.i)
trs_input = parser.read()

tier = trs_input.find(args.t)
ref = trs_input.find(args.T)

for ann in tier:
    location = ann.get_location()
    for l, s in location:
        time = l.get_midpoint()
        a = ref.near(l, direction=0)
        # the nearest point is either begin or end of a
        a_begin = a.get_lowest_localization()
        a_end = a.get_highest_localization()
        delta_begin = math.fabs(a_begin.get_midpoint() - time)
        delta_end = math.fabs(a_end.get_midpoint() - time)
        if delta_begin < delta_end:
            l.set_midpoint(a_begin)
            l.set_radius(delta_begin)
        else:
            l.set_midpoint(a_end)
            l.set_radius(delta_end)

    print("New ann: {:s}".format(ann))

