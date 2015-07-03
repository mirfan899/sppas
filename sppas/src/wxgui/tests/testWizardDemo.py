# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import wx
import sys
import os.path
sys.path.append(os.path.dirname( os.path.dirname( os.path.abspath(__file__) )))
sys.path.append(os.path.dirname( os.path.dirname( os.path.dirname( os.path.abspath(__file__)))))

from demo.wizardDemo import WizardDemo

# ----------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.App(False)
    WizardDemo()
    app.MainLoop()

#----------------------------------------------------------------------
