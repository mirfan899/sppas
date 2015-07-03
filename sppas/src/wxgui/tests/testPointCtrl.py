# coding=UTF8
# Copyright (C) 2014  Brigitte Bigi

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path
sys.path.append(os.path.dirname( os.path.dirname(os.path.abspath(__file__) )))

import wx
from test_utils import setup_logging
from demo.PointCtrlDemo import PointCtrlFrame

# ----------------------------------------------------------------------------


class MyApp(wx.App):
    def OnInit(self):
        frame = PointCtrlFrame(None, -1, 'Time Point Demo')
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
