from os.path import abspath, dirname, join
import sys

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(join(SPPAS, 'sppas', 'src'))

import wx
from wxgui.dialogs.trsinfodialog import TrsInfoDialog

TEST = "oriana2-merge.TextGrid"

if __name__ == '__main__':

    # App
    app = wx.App()
    frame = TrsInfoDialog(None, trsname=TEST, trs=None)
    app.SetTopWindow(frame)
    app.MainLoop()

