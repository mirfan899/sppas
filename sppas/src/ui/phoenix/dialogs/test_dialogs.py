import wx
import sys
from os import path
PROGRAM = path.abspath(__file__)
SPPAS = path.dirname(path.dirname(path.dirname(path.dirname(path.dirname(path.dirname(PROGRAM))))))
sys.path.append(SPPAS)

from sppas.src.ui.phoenix.dialogs.basedialog import sppasDialog, YesNoQuestion
from sppas.src.ui.phoenix import WxAppConfig, WxAppSettings

# ---------------------------------------------------------------------------


class testApp(wx.App):
    """Create a test SPPAS Phoenix application.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self):
        """Wx Application initialization."""
        # Initialize the wx application
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)
        self.cfg = WxAppConfig()
        self.settings = WxAppSettings()

# ---------------------------------------------------------------------------


app = testApp()

# demo = sppasDialog(None, title="sppasDialog")
# demo.CreateHeader("This is a BaseDialog...")
# demo.CreateButtons([wx.CANCEL], [wx.OK])
# demo.LayoutComponents()
# demo.ShowModal()
# demo.Destroy()

demo = YesNoQuestion("This is a question?")
r = demo.ShowModal()
if r == wx.ID_YES:
    print("Click on Yes")
elif r == wx.ID_NO:
    print("Click on No")
else:
    print('Nothing clicked on. {:d}'.format(r))
demo.Destroy()
app.SetTopWindow(demo)
app.MainLoop()
