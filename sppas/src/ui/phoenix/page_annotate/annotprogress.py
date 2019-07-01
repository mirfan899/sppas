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

    ui.phoenix.page_annotate.annotprogress.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

import wx
import time
import logging

from sppas.src.ui.progress import sppasBaseProgress
from sppas.src.ui.cfg import sppasAppConfig

from sppas.src.ui.phoenix.main_settings import WxAppSettings
from sppas.src.ui.phoenix.windows import sppasTopFrame
from sppas.src.ui.phoenix.windows import sppasPanel
from sppas.src.ui.phoenix.windows import sppasStaticText

# ---------------------------------------------------------------------------


class sppasProgressPanel(sppasPanel, sppasBaseProgress):

    def __init__(self, parent):
        super(sppasProgressPanel, self).__init__(parent)

        self.SetName("annot_progress_panel")
        self._create_content()
        self.Layout()

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the progress dialog."""
        # an header text used to print the annotation step
        self.header = sppasStaticText(self, label="HEADER IS HERE", style=wx.ALIGN_CENTRE)
        # the gauge
        self.gauge = wx.Gauge(self, range=100, size=(400, 24))
        # a bottom text used to print the current file name
        self.text = sppasStaticText(self, label="BOTTOM IS HERE", style=wx.ALIGN_CENTRE)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.header, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer.Add(self.gauge, 0, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 4)
        sizer.Add(self.text, 1, wx.ALL | wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, 4)

        self.SetSizer(sizer)

    # -----------------------------------------------------------------------

    def set_header(self, header):
        """Overridden. Set a new progress header text.

        :param header: (str) new progress header text.

        """
        self.header.SetLabel(header)
        self.Refresh()
        self.Update()

    # -----------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Overridden. Update the progress box.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text  (default: None)

        """
        if percent is not None:
            fraction = float(percent)
            # convert fraction to a percentage (if necessary)
            if fraction < 1:
                fraction = int(fraction * 100.)
            if fraction > 100:
                fraction = 100
            self.gauge.SetValue(fraction)

        if message is not None:
            self.text.SetLabel(message)
            self.text.Refresh()

        self.Refresh()
        self.Update()
        time.sleep(0.2)

# ---------------------------------------------------------------------------


class sppasProgressDialog(wx.GenericProgressDialog, sppasBaseProgress):
    """Progress dialog for the annotations.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    """

    def __init__(self):
        """Create a dialog with a progress for the annotations."""
        super(sppasProgressDialog, self).__init__(
            title="Automatic annotations",
            message="",
            style=wx.PD_SMOOTH)

        self.SetTitle("Automatic annotations")
        self.SetWindowStyle(wx.CAPTION | wx.RESIZE_BORDER)
        self.SetName("annot_progress_dialog")
        self.SetRange(101)

        # Fix frame properties
        self.SetMinSize(wx.Size(self.fix_size(400),
                                self.fix_size(128)))
        self.Layout()

    # -----------------------------------------------------------------------

    @staticmethod
    def fix_size(value):
        """Return a proportional size value.

        :param value: (int)
        :returns: (int)

        """
        try:
            obj_size = int(float(value) * wx.GetApp().settings.size_coeff)
        except AttributeError:
            obj_size = int(value)
        return obj_size

    # -----------------------------------------------------------------------

    def set_header(self, header):
        """Overridden. Set a new progress header text.

        :param header: (str) new progress header text.

        """
        self.SetTitle(header)
        self.Refresh()

    # -----------------------------------------------------------------------

    def update(self, percent=None, message=None):
        """Overridden. Update the progress box.

        :param message: (str) progress bar value (default: 0)
        :param percent: (float) progress bar text  (default: None)

        """
        if percent is not None:
            fraction = float(percent)
            # convert fraction to a percentage (if necessary)
            if fraction < 1:
                fraction = int(fraction * 100.)
            if fraction > 100:
                fraction = 100
        else:
            fraction = self.GetValue()

        if message is not None:
            self.SetLabel(message)
            self.Refresh()
        else:
            message = self.GetMessage()

        self.Update(fraction, message)
        time.sleep(0.2)

    # -----------------------------------------------------------------------

    def close(self):
        """Close the progress box."""
        self.Destroy()

# ----------------------------------------------------------------------------
# App to test
# ----------------------------------------------------------------------------


class TestApp(wx.App):

    def __init__(self):
        """Create a customized application."""
        # ensure the parent's __init__ is called with the args we want
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()

        # create the frame
        self.frm = wx.Frame(None, title='Progress test', size=(256, 128), name="main")
        self.SetTopWindow(self.frm)

        # create a panel in the frame
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.Button(self.frm, label="start"), 1, wx.EXPAND, 0)
        self.frm.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self._on_start)

        # show result
        self.frm.Show(True)


    def _on_start(self, event):

        self.progress = sppasProgressDialog()

        self.progress.set_new()
        self.progress.set_header("Annotation number 1")
        self.progress.set_fraction(0)
        self.progress.set_text("file one")
        time.sleep(1)
        self.progress.set_fraction(34)
        self.progress.set_text("file two")
        time.sleep(1)
        self.progress.set_fraction(70)
        self.progress.set_text("file three")
        time.sleep(1)
        self.progress.set_fraction(100)

        self.progress.set_new()
        self.progress.set_header("Another annotation")
        self.progress.set_fraction(0)
        self.progress.set_text("one file")
        time.sleep(1)
        self.progress.set_fraction(50)
        self.progress.set_text("two files")
        time.sleep(1)
        self.progress.set_fraction(100)

        self.progress.close()

# ----------------------------------------------------------------------------


if __name__ == "__main__":
    app = TestApp()
    app.MainLoop()
