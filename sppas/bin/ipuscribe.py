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
# File: ipuscribe.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import sys
import os.path
import traceback
from argparse import ArgumentParser

from butils import exit_error, check_python, install_gettext
from checkwx import get_wx_version

check_python()

try:
    import wx
except ImportError:
    exit_error( "WxPython is not installed on your system\n. The Graphical User Interface of SPPAS can't work. Refer to the installation instructions of the SPPAS web site.")

# import SPPAS Application Programming Interface
# ----------------------------------------------

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.join(os.path.dirname( os.path.dirname( PROGRAM ) ), "src")
sys.path.insert(0,SPPAS)

try:
    from wxgui.frames.ipuscribeframe import IPUscribeFrame
    from wxgui.sp_icons import IPUSCRIBE_APP_ICON
    from utils.fileutils import setup_logging
    from wxgui.dialogs.msgdialogs  import ShowInformation
    from wxgui.structs.prefs       import Preferences_IO
    from wxgui.structs.theme      import sppasTheme
    from utils.fileutils           import setup_logging
    from sp_glob                   import SETTINGS_FILE
except ImportError:
    exit_error( "An error occurred.\nVerify the SPPAS installation and try again. Full error message is: %s"%traceback.format_exc() )

# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

# Arguments
# ------------------------------------------------------------------------

parser = ArgumentParser(usage="%s files" % os.path.basename(PROGRAM), description="IPUscribe graphical user interface.")
parser.add_argument("files", nargs="*", help='Input file name(s)')
args = parser.parse_args()

# force to add path
filenames = []
for f in args.files:
    p,b = os.path.split( f )
    if not p:
        p = os.getcwd()
    filenames.append( os.path.abspath(os.path.join(p,b) ))

# Logging and Gettext
# ----------------------------------------------------------------------------

log_level = 1
log_file  = None
try:
    setup_logging(log_level, log_file)
except Exception:
    # stdin is not available if pythonw is used instead of python, on Windows!
    log_file = os.path.join( os.path.dirname( os.path.dirname( os.path.dirname( PROGRAM ) )), "sppas.log")
    setup_logging(log_level, log_file)

install_gettext()

# GUI is here:
# ----------------------------------------------------------------------------

app = wx.App( redirect=True )

# Fix preferences
prefsIO = Preferences_IO( SETTINGS_FILE )
if prefsIO.Read() is False:
    prefsIO.SetTheme( sppasTheme() )

# Tests
v = get_wx_version()
if v < 3:
    message = "The version of WxPython is too old.\n\tThe Graphical User Interface will not display properly.\n\tUpdate at http://wxpython.org/ and restart SPPAS.\n\tFor any help, see SPPAS installation page.\n"
    ShowInformation( None, prefsIO, message, style=wx.ICON_WARNING)

# App
frame = IPUscribeFrame(None, -1, prefsIO)
frame.AddFiles( filenames )

app.SetTopWindow(frame)
app.MainLoop()

# ---------------------------------------------------------------------------
