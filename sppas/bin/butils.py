#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
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
# File: butils.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import os
import sys
import time
import subprocess

EXIT_DELAY=20
EXIT_STATUS=1

# ----------------------------------------------------------------------------

def exit_error( msg="Unknown." ):
    """
    Exit the program with status 1 and an error message.

    @param msg (str) Message to print on stdout.

    """
    print "[ ERROR ] ",msg
    time.sleep( EXIT_DELAY )
    sys.exit( EXIT_STATUS )

# ----------------------------------------------------------------------------

def check_python():
    """
    Check if the current python in use is the right one: 2.7.something.
    Exit if it's not the case.

    """
    if sys.version_info < (2, 7):
        exit_error(" The version of Python is too old: SPPAS requires exactly the version 2.7.something.")

    if sys.version_info >= (3, 0):
        exit_error( "The version of Python is not the right one: SPPAS requires exactly the version 2.7.something.")

# ----------------------------------------------------------------------------

def check_aligner():
    """
    Test if one of julius/HVite is available.
    Return False if none of them are available.

    """
    julius = True
    hvite  = True
    try:
        NULL = open(os.devnull, "r")
        subprocess.call(['julius'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        julius = False

    try:
        NULL = open(os.devnull, "r")
        subprocess.call(['HVite'], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        hvite = False

    return (julius or hvite)

# ----------------------------------------------------------------------------

def install_gettext():
    def _(message):
        return message
    import __builtin__
    if not "_" in __builtin__.__dict__:
        __builtin__.__dict__["_"] = _

# ----------------------------------------------------------------------------
