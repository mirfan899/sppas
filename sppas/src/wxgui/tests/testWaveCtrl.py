# coding=UTF8
# Copyright (C) 2014  Brigitte Bigi
#
# This file is part of DataEditor.
#
# DataEditor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DataEditor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with DataEditor.  If not, see <http://www.gnu.org/licenses/>.
#

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path
sys.path.append(os.path.dirname( os.path.dirname( os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname( os.path.dirname( os.path.abspath(__file__) )))

import wx
from test_utils import *
from demo.WaveCtrlDemo import WaveCtrlFrame

# ----------------------------------------------------------------------------


class MyApp(wx.App):
    def OnInit(self):
        frame = WaveCtrlFrame(None, -1, 'Wave Demo')
        frame.Show(True)
        return True

# ----------------------------------------------------------------------------

if __name__ == '__main__':
    # Log
    log_level = 1
    log_file  = None
    setup_logging(log_level, log_file)

# ----------------------------------------------------------------------------

    app = MyApp(0)
    app.MainLoop()

# ---------------------------------------------------------------------------
