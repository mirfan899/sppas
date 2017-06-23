# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
from os.path import abspath, dirname, join
import sys

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(join(SPPAS, 'sppas', 'src'))

import wx
from wxgui.demo.wizardDemo import WizardDemo

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(False)
    WizardDemo()
    app.MainLoop()

#----------------------------------------------------------------------
