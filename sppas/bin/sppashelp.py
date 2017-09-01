#!/usr/bin/env python2
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

    bin.sppashelp.py
    ~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Run the Help Browser tool

"""
import sys
import os.path
import traceback

from butils import exit_error, check_python
check_python()

try:
    import wx
except ImportError:
    exit_error("WxPython is not installed on your system\n. "
               "The Graphical User Interface of SPPAS can't work. "
               "Refer to the installation instructions of the SPPAS web site.")

# import SPPAS Application Programming Interface
# ----------------------------------------------

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

try:
    from sppas import SETTINGS_FILE
    from sppas.src.wxgui.frames.helpbrowser import HelpBrowser
    from sppas.src.utils.fileutils import setup_logging
    from sppas.src.wxgui.dialogs.msgdialogs import ShowInformation
    from sppas.src.wxgui.structs.prefs import Preferences_IO
    from sppas.src.wxgui.structs.theme import sppasTheme
    from sppas.src.utils.fileutils import setup_logging
except ImportError:
    exit_error("An error occurred.\n"
               "Verify the SPPAS installation and try again. "
               "Full error message is: %s" % traceback.format_exc())

# ----------------------------------------------------------------------------
# SPPAS GUI is here:
# ----------------------------------------------------------------------------

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

app = wx.App(redirect=True)

# Fix preferences
prefsIO = Preferences_IO(SETTINGS_FILE)
if prefsIO.Read() is False:
    prefsIO.SetTheme(sppasTheme())

frame = HelpBrowser(None, prefsIO)
frame.Show()

app.SetTopWindow(frame)
app.MainLoop()
