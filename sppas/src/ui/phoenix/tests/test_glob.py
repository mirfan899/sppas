# -*- coding: UTF-8 -*-
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

    src.ui.phoenix.tests.test_glob.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import logging

from sppas.src.config.ui import sppasAppConfig
from sppas.src.ui.phoenix.main_settings import WxAppSettings

# Tested files are the ones with a TestPanel class:
import sppas.src.ui.phoenix.windows.line
import sppas.src.ui.phoenix.windows.button
import sppas.src.ui.phoenix.pages.filespck.filesmanager
import sppas.src.ui.phoenix.pages.filespck.catsmanager
import sppas.src.ui.phoenix.pages.filespck.wksmanager

# ----------------------------------------------------------------------------
# Panel to test
# ----------------------------------------------------------------------------


class TestPanel(wx.Choicebook):
    def __init__(self, parent):
        wx.Choicebook.__init__(self, parent, wx.ID_ANY)

        # Make the bunch of test panels for the choice book
        self.AddPage(sppas.src.ui.phoenix.pages.filespck.wksmanager.TestPanel(self), "Workspaces manager")
        self.AddPage(sppas.src.ui.phoenix.pages.filespck.catsmanager.TestPanel(self), "Catalogues manager")
        self.AddPage(sppas.src.ui.phoenix.pages.filespck.filesmanager.TestPanel(self), "Files manager")
        self.AddPage(sppas.src.ui.phoenix.windows.button.TestPanel(self), "Buttons")
        self.AddPage(sppas.src.ui.phoenix.windows.line.TestPanel(self), "Lines")

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def OnPageChanged(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        logging.debug('OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()

    def OnPageChanging(self, event):
        old = event.GetOldSelection()
        new = event.GetSelection()
        sel = self.GetSelection()
        logging.debug('OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel))
        event.Skip()


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

        # create the frame
        frm = wx.Frame(None, title='Test frame', size=(640, 540))
        self.SetTopWindow(frm)

        # Fix language and translation
        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.__cfg = sppasAppConfig()
        self.settings = WxAppSettings()
        self.setup_debug_logging()

        # create a panel in the frame
        sizer = wx.BoxSizer()
        sizer.Add(TestPanel(frm), 1, wx.EXPAND, 0)
        frm.SetSizer(sizer)

        # show result
        frm.Show()

    @staticmethod
    def setup_debug_logging():
        logger = logging.getLogger()
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logging.debug('Logging set to DEBUG level')

# ---------------------------------------------------------------------------


if __name__ == '__main__':
    app = TestApp()
    app.MainLoop()
