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
# ----------------------------------------------------------------------------
# File: dataroamer.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys
import os
import os.path
import traceback
import time
from argparse import ArgumentParser

def exit_error( msg ):
    print "[ ERROR ] ",msg
    time.sleep( 5 )
    sys.exit(1)

# VERIFY PYTHON
# -------------
if sys.version_info < (2, 7):
    exit_error(" The version of Python is too old: SPPAS requires exactly the version 2.7.something.")

if sys.version_info >= (3, 0):
    exit_error( "The version of Python is not the right one: SPPAS requires exactly the version 2.7.something.")

# VERIFY WXPYTHON
# ----------------
try:
    import wx
except ImportError:
    exit_error( "WxPython is not installed on your system\n. The Graphical User Interface of SPPAS can't work. Refer to the installation instructions of the SPPAS web site.")

try:
    wxv = wx.version().split()[0]
except Exception:
    wxv = '2'

if int(wxv[0]) < 3:
    print "[ WARNING ] The version of WxPython is too old.\n\tThe Graphical User Interface will not display properly.\n\tUpdate at http://wxpython.org/ and restart SPPAS.\n\tFor any help, see SPPAS installation page.\n"
    time.sleep( 20 )

# THEN, VERIFY SPPAS
# ------------------

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.insert(0,SPPAS)

try:
    from wxgui.frames.dataroamerframe import DataRoamerFrame
    from wxgui.sp_icons import DATAROAMER_APP_ICON
    from utils.fileutils import setup_logging
except ImportError as e:
    print traceback.format_exc()
    exit_error( "A problem occurred when launching DataRoamer.\nThe error is: %s.\nVerify the SPPAS installation directory and try again."%(str(e)))


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

# Log
log_level = 0
log_file  = None

try:
    setup_logging(log_level, log_file)
except Exception:
    # stdin is not available if pythonw is used on Windows!
    log_file = os.path.join( os.path.dirname( os.path.dirname( os.path.dirname( PROGRAM ) )), "sppas.log")
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
arguments['title'] = "DataRoamer"
arguments['type']  = "DATAFILES"
arguments['icon']  = DATAROAMER_APP_ICON

app = wx.App()
try:
    frame = DataRoamerFrame(None, -1, arguments)
    app.SetTopWindow(frame)
    frame.AddFiles( filenames )
except Exception as e:
    print traceback.format_exc()
    exit_error("A problem occurred when creating the Graphical User Interface.\nThe error is: %s"%(str(e)) )

app.MainLoop()

# ---------------------------------------------------------------------------
