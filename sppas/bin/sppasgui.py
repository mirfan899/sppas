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

    bin.sppasgui.py
    ~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi

    This is the main program to execute the Graphical User Interface of SPPAS.
    
"""
import sys
import os.path
import traceback
from argparse import ArgumentParser
from butils import exit_error, check_python, check_aligner
check_python()

try:
    import wx
except ImportError:
    exit_error("WxPython is not installed on your system\n."
               "The Graphical User Interface of SPPAS can't work.")
from checkwx import get_wx_version

# import SPPAS Application Programming Interface
# ----------------------------------------------

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

try:
    from sppas import encoding
    from sppas import SETTINGS_FILE
    from sppas.src.wxgui.frames.mainframe import FrameSPPAS
    from sppas.src.wxgui.dialogs.msgdialogs import ShowInformation
    from sppas.src.wxgui.structs.prefs import Preferences_IO
    from sppas.src.wxgui.structs.theme import sppasTheme
    from sppas.src.utils.fileutils import setup_logging
except ImportError:
    exit_error("An unexpected error occurred.\n"
               "Verify the SPPAS installation and try again. "
               "The error message is: %s" % traceback.format_exc())

# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

# Arguments
# ------------------------------------------------------------------------

parser = ArgumentParser(usage="%s files" % os.path.basename(PROGRAM),
                        description="SPPAS Graphical User Interface.")
parser.add_argument("files", nargs="*", help='Input audio file name(s)')
args = parser.parse_args()

# force to add path
filenames = []
for f in args.files:
    p,b = os.path.split(f)
    if not p:
        p = os.getcwd()
    filenames.append(os.path.abspath(os.path.join(p,b)))

# Logging
# ----------------------------------------------------------------------------

log_level = 1
log_file = None
try:
    setup_logging(log_level, log_file)
except Exception:
    # stdin is not available if pythonw is used instead of python, on Windows!
    log_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM))), "sppas.log")
    setup_logging(log_level, log_file)

# GUI is here:
# ----------------------------------------------------------------------------

sppas = wx.App(redirect=True)

# Fix preferences
prefsIO = Preferences_IO(SETTINGS_FILE)
if prefsIO.Read() is False:
    prefsIO.SetTheme(sppasTheme())

# Tests
v = get_wx_version()
if v < 3:
    message = "The version of WxPython is too old.\nThe Graphical User Interface will not display properly.\n"
    ShowInformation(None, prefsIO, message, style=wx.ICON_WARNING)

if check_aligner() is False:
    ShowInformation(None, prefsIO, 'None of julius or HVite command is installed on your system.\n'
                                   'The Alignment automatic annotation will NOT WORK normally.',
                    style=wx.ICON_ERROR)

# Main frame
frame = FrameSPPAS(prefsIO)
if len(filenames) > 0:
    frame.flp.RefreshTree(filenames)

frame.Show()
sppas.SetTopWindow(frame)
sppas.MainLoop()
