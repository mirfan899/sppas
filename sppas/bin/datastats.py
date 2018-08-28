#!/usr/bin/env python
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

    bin.datastats.py
    ~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      contact@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Run the DataStats analysis tool

"""
import sys
import traceback
from argparse import ArgumentParser

from os import path, getcwd
PROGRAM = path.abspath(__file__)
SPPAS = path.dirname(path.dirname(path.dirname(PROGRAM)))
sys.path.append(SPPAS)
from sppas.bin import exit_error, check_python
check_python()

try:
    import wx
except ImportError:
    exit_error("WxPython is not installed on your system\n. "
               "The Graphical User Interface of SPPAS can't work. "
               "Refer to the installation instructions of the web site.")

try:
    from sppas.src.ui import SETTINGS_FILE
    from sppas.src.ui.wxgui.frames.datastatsframe import DataStatsFrame
    from sppas.src.ui.wxgui.sp_icons import STATISTICS_APP_ICON
    from sppas.src.utils.fileutils import setup_logging
    from sppas.src.ui.wxgui.dialogs.msgdialogs import ShowInformation
    from sppas.src.ui.wxgui.structs.prefs import Preferences_IO
    from sppas.src.ui.wxgui.structs.theme import sppasTheme
    from sppas.src.utils.fileutils import setup_logging
except ImportError:
    exit_error("An error occurred.\n"
               "Verify the SPPAS installation and try again. "
               "Full error message is: %s" % traceback.format_exc())


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

# Arguments
# ---------------------------------------------------------------------------

parser = ArgumentParser(usage="{:s} files".format(path.basename(PROGRAM)),
                        description="Statistics graphical user interface.")
parser.add_argument("files", nargs="*", help='Input file name(s)')
args = parser.parse_args()

# force to add path
filenames = []
for f in args.files:
    p, b = path.split(f)
    if not p:
        p = getcwd()
    filenames.append(path.abspath(path.join(p, b)))

# Logging
# ----------------------------------------------------------------------------

log_level = 1
log_file = None
try:
    setup_logging(log_level, log_file)
except Exception:
    # stdin is not available if pythonw is used instead of python, on Windows!
    log_file = path.join(path.dirname(
        path.dirname(path.dirname(PROGRAM))), "sppas.log")
    setup_logging(log_level, log_file)


# GUI is here:
# ----------------------------------------------------------------------------

app = wx.App(redirect=True)

# Fix preferences
prefsIO = Preferences_IO(SETTINGS_FILE)
if prefsIO.Read() is False:
    prefsIO.SetTheme(sppasTheme())

# App

frame = DataStatsFrame(None, -1, prefsIO)
frame.AddFiles(filenames)

app.SetTopWindow(frame)
app.MainLoop()
