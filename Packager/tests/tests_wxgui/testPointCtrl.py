# coding=UTF8
# Copyright (C) 2014  Brigitte Bigi

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
from os.path import abspath, dirname, join
import sys

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(join(SPPAS, 'sppas', 'src'))

import wx
from test_utils import setup_logging
from wxgui.demo.PointCtrlDemo import PointCtrlFrame

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
