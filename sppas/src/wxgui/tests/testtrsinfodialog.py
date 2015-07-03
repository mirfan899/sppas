import sys
import os.path
sys.path.append( os.path.dirname(os.path.dirname(os.path.abspath(__file__) )))
sys.path.append( os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__) ))))

import wx
from dialogs.trsinfodialog import TrsInfoDialog

TEST = "oriana2-merge.TextGrid"

if __name__ == '__main__':

    # App
    app = wx.App()
    frame = TrsInfoDialog(None, trsname=TEST, trs=None)
    app.SetTopWindow(frame)
    app.MainLoop()

