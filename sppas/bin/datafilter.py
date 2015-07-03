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
# ----------------------------------------------------------------------------
# File: datafilter.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2014  Brigitte Bigi"""


# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys
import os
import os.path
from argparse import ArgumentParser
import tkMessageBox


# VERIFY PYTHON
# -------------
if sys.version_info < (2, 7):
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is too old. SPPAS requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)

if sys.version_info >= (3, 0):
    tkMessageBox.showwarning(
        "Python Error...",
        "Your python version is not appropriate. SPPAS requires 2.7\n. Verify your python installation and try again."
        )
    sys.exit(1)


# VERIFY WXPYTHON
# ----------------
try:
    import wx
except ImportError:
    tkMessageBox.showwarning(
        "WxPython Error...",
        "WxPython is not installed on your system\n. Verify your installation and try again."
        )
    sys.exit(1)


# THEN, VERIFY SPPAS
# ------------------

# Make sure that we can import libraries
PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.insert(0,SPPAS)

try:
    from wxgui.frames.datafilterframe import DataFilterFrame
    from wxgui.sp_icons import DATAFILTER_APP_ICON
    from utils.commons import setup_logging
except ImportError as e:
    tkMessageBox.showwarning(
        "Error...",
        "A problem occurred.\nVerify your installation and try again.\n\nThe system error message is: %s" % str(e)
        )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

# Log
log_level = 0
log_file  = None
setup_logging(log_level, log_file)


# Arguments
# ------------------------------------------------------------------------

parser = ArgumentParser(usage="%s files" % os.path.basename(PROGRAM), description="DataRoamer graphical user interface.")
parser.add_argument("files", nargs="*", help='Input file name(s)')
args = parser.parse_args()

# force to add path
filenames = []
for f in args.files:
    p,b = os.path.split( f )
    if not p:
        p = os.getcwd()
    filenames.append( os.path.abspath(os.path.join(p,b) ))

# App
arguments = {}
arguments['files'] = []
arguments['title'] = "DataFilter"
arguments['type']  = "DATAFILES"
arguments['icon']  = DATAFILTER_APP_ICON

app = wx.App()
frame = DataFilterFrame(None, -1, arguments)
app.SetTopWindow(frame)

frame.AddFiles( filenames )

app.MainLoop()

# ---------------------------------------------------------------------------
