#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2014  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: wavsplit.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2014  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

from sppas.src.annotations.IPUs.sppasipusseg import sppasIPUseg
from sppas.src.utils.fileutils import setup_logging


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -w file [options]" % os.path.basename(PROGRAM),
                        description="IPUs segmentation command line interface.")

parser.add_argument("-w", metavar="file", required=True,  help='Input wav file name')

# Silence/Speech segmentation options:
parser.add_argument("-r", "--winrms", type=float, help='Window size to estimate rms, in seconds (default: 0.010)')
parser.add_argument("-m", "--minipu", type=float, help='Drop speech shorter than m seconds long (default: 0.300)')
parser.add_argument("-s", "--minsil", type=float, help='Drop silences shorter than s seconds long (default: 0.200)')
parser.add_argument("-v", "--minrms", type=int, default=0, help='Assume everything with a rms lower than v is a silence. (default: auto-adjust)')

# Controlled search, choose one of -t or -n options:
parser.add_argument("-t", metavar="file", help='Input transcription (default: None)')
parser.add_argument("-n", type=int, default=-1, help='Input transcription tier number (if any, default = 0 = first tier).')
parser.add_argument("-N", type=int, help='Adjust the volume cap until it splits into N tracks. (default = 0 = do not do that).')

# Other options:
parser.add_argument("-d", "--shiftstart", type=float, help='Shift-left the start boundary of IPUs (default: 0.010)')
parser.add_argument("-D", "--shiftend",   type=float, help='Shift-right the end boundary of IPUs (default: 0.020)')

# Output options:
parser.add_argument("-o", metavar="dir",  help='Output directory name (default: None)')
parser.add_argument("-e", metavar="ext",  help='Output tracks extension, available only if -t (default: txt)')
parser.add_argument("-p", metavar="file", help='Annotated file with silences/units segmentation (default: None)')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


if args.t and args.N:
    print "You can NOT use both -t and -N options!\nUse option -h for any help."
    sys.exit(1)

log_level = 1
log_file  = None
try:
    setup_logging(log_level, log_file)
except Exception:
    pass

# ----------------------------------------------------------------------------
# Automatic IPUs segmentation is here:
# ----------------------------------------------------------------------------


if args.o and not os.path.exists(args.o):
    os.mkdir(args.o)

w = sppasIPUseg()

if args.shiftstart: w.ipusaudio.set_shift_start(args.shiftstart)
if args.shiftend:   w.ipusaudio.set_shift_start(args.shiftend)
if args.minipu:     w.ipusaudio.set_min_speech(args.minipu)
if args.minsil:     w.ipusaudio.set_min_silence(args.minsil)
if args.minrms:     w.ipusaudio.set_min_vol_threshold(args.minrms)
if args.winrms:     w.ipusaudio.set_vol_win_lenght(args.winrms)

if args.o: w.set_dirtracks(True)
if args.p: w.set_save_as_trs(True)
if args.e: w.set_save_as_trs(True)
if args.n == -1:
    tieridx = None
else:
    tieridx = 0

w.run(args.w, args.t, tieridx, args.N, args.o, args.e, args.p)

#     - wavfile is the wav input file name
#     - trsinputfile is a transcription (or 'None')
#     - trstieridx is the tier index with the transcription
#     - ntracks
#     - diroutput is a directory name to save output tracks (one per unit)
#     - tracksext is the track extension (used with the diroutput option)
#     - textgridoutput is a file name to save the IPU segmentation result.

# ----------------------------------------------------------------------------
