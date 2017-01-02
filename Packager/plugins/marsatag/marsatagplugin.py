#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2017  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
#
# this program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# this program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# marsatagplugin.py
# ---------------------------------------------------------------------------

import sys
import os
import shlex
from argparse import ArgumentParser
from subprocess import Popen, PIPE, STDOUT

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print "ERROR: SPPAS not found."
    sys.exit(1)

SPPASSRC = os.path.join(SPPAS, "sppas", "src")
sys.path.append(SPPASSRC)

import annotationdata.io


# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -p path" %
                        os.path.basename(PROGRAM),
                        description="... a program to apply MarsaTag on a file annotated by SPPAS.")
parser.add_argument("-i", metavar="file", required=True,  help='Input annotated file name')
parser.add_argument("-p", metavar="path", required=True,  help='MarsaTag main directory')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# Convert input file if not TextGrid

filename = args.i
fname, fext = os.path.splitext(filename)

if fname.endswith("-palign") is False:
    print "ERROR: MarsaTag plugin requires SPPAS alignment files (i.e. with -palign in its name)."
    sys.exit(1)

if fext.lower() != "textgrid":

    # read content
    trs_input = annotationdata.io.read(filename)
    
    # write as textgrid
    filename = fname + ".TextGrid"
    annotationdata.io.write(filename, trs_input)

# ----------------------------------------------------------------------------
# Get MarsaTag path 

MARSATAG = args.p

if len(MARSATAG) == 0:
    print "ERROR: No given directory for MarsaTag software tool."
    sys.exit(1)

if os.path.exists(MARSATAG) is False:
    print "ERROR: MarsaTag directory not found."
    sys.exit(1)

# ----------------------------------------------------------------------------
# Call MarsaTag

command  = "java -Xms300M -Xmx600M -Dortolang.home=" + MARSATAG
command += ' -jar "' + os.path.join(MARSATAG, "lib", "MarsaTag-UI.jar") + '" '
command += ' --cli '
command += ' -tier TokensAlign '
command += ' -reader praat-textgrid '
command += ' -encoding UTF8 '
command += ' -in-ext -palign.TextGrid '
command += ' -w praat-textgrid '
command += ' -out-encoding UTF8 '
command += ' -rm-ext '
command += ' --writer-option keep-input-tiers=false '
command += ' -out-ext -pos.TextGrid '
command += ' --oral '
command += ' -M -P -Q '
command += ' ' + filename

command_args = shlex.split(command)
p = Popen(command_args, shell=False, stdout=PIPE, stderr=STDOUT)
message = p.communicate()
if message is None:
    message = ["Done."]
print "".join(message[0])

# ----------------------------------------------------------------------------
# Clean

if os.path.exists('marsatag-ui.log'):
    os.remove('marsatag-ui.log')
if filename != args.i:
    os.remove(filename)
