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
import subprocess
from subprocess import Popen, PIPE, STDOUT

PROGRAM = os.path.abspath(__file__)
SPPAS = os.getenv('SPPAS')
if SPPAS is None:
    SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))

if os.path.exists(SPPAS) is False:
    print("ERROR: SPPAS not found in directory: {:s}.".format(SPPAS))
    sys.exit(1)
sys.path.append(SPPAS)

import sppas.src.annotationdata.aio as aio
from sppas.src.annotationdata.transcription import Transcription

# ---------------------------------------------------------------------------


def test_command(command):
    """ Test if a command is available.

    :param command: (str) The command to execute as a sub-process.

    """
    try:
        NULL = open(os.devnull, "w")
        subprocess.call([command], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        return False

    return True

# ----------------------------------------------------------------------------
# Verify and extract args:
# ----------------------------------------------------------------------------

parser = ArgumentParser(usage="%s -i file -p path" %
                        os.path.basename(PROGRAM),
                        description="... a program to apply MarsaTag on a file annotated by SPPAS.")

parser.add_argument("-i",
                    metavar="file",
                    required=True,
                    help='Input annotated file name')

parser.add_argument("-p",
                    metavar="path",
                    required=True,
                    help='MarsaTag main directory')

if len(sys.argv) <= 1:
    sys.argv.append('-h')

args = parser.parse_args()


# ----------------------------------------------------------------------------
# test java

java_ok = test_command("java")
if java_ok is False:
    print("ERROR: Java must be installed for MarsaTag to operate.")
    sys.exit(1)

# ----------------------------------------------------------------------------
# Convert input file if not TextGrid

filename = args.i
fname, fext = os.path.splitext(filename)

if fname.endswith("-palign") is False:
    print("ERROR: MarsaTag plugin requires SPPAS alignment files "
          "(i.e. with -palign in its name).")
    sys.exit(1)

if fext.lower() != "textgrid":

    # read content
    trs_input = aio.read(filename)
    tier = trs_input.Find("TokensAlign", case_sensitive=False)
    if tier is None:
        print("ERROR: A tier with name TokensAlign is required.")
        sys.exit(1)

    # write as textgrid
    trs = Transcription(name="TokensAlign")
    trs.Append(tier)
    filename = fname + ".TextGrid"
    aio.write(filename, trs)

# ----------------------------------------------------------------------------
# Get MarsaTag path 

if len(args.p) == 0:
    print("ERROR: No given directory for MarsaTag software tool.")
    sys.exit(1)

if os.path.isdir(args.p) is False:
    print("ERROR: {:s} is not a valid directory.".format(args.p))
    sys.exit(1)

MARSATAG = os.path.join(args.p, "lib", "MarsaTag-UI.jar")
if os.path.exists(MARSATAG) is False:
    print("ERROR: MarsaTag is not properly installed: {:s} is not existing.".format(MARSATAG))
    sys.exit(1)

# ----------------------------------------------------------------------------
# Check the given filename

if os.path.exists(filename) is False:
    print("ERROR: The given file can't be found: {s}.".format(filename))
    sys.exit(1)

# ----------------------------------------------------------------------------
# Call MarsaTag

command = "java -Xms300M -Xmx600M -Dortolang.home=" + args.p
command += ' -jar "' + MARSATAG + '" '
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
print("".join(message[0]))

# ----------------------------------------------------------------------------
# Clean

if os.path.exists('marsatag-ui.log'):
    os.remove('marsatag-ui.log')
if filename != args.i:
    os.remove(filename)
