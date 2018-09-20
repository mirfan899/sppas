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

    src.ui.phoenix.dialogs.settings.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import logging

from ..controls.windows import sppasPanel
from ..controls.windows import sppasNotebook
from ..controls.buttons import sppasBitmapTextButton
from ..tools import sppasSwissKnife

from .basedialog import sppasDialog

# ---------------------------------------------------------------------------


def GetColour(parent):
    """Return the color choose by the user.

    :param parent: (wx.Window)

    """
    # open the dialog
    dlg = wx.ColourDialog(parent)

    # Ensure the full colour dialog is displayed,
    # not the abbreviated version.
    dlg.GetColourData().SetChooseFull(True)

    c = None
    if dlg.ShowModal() == wx.ID_OK:
        color = dlg.GetColourData().GetColour()
        r = color.Red()
        g = color.Green()
        b = color.Blue()
        c = wx.Colour(r, g, b)
    dlg.Destroy()
    return c

# ----------------------------------------------------------------------------


class sppasSettingsDialog(sppasDialog):
    """Settings dialogs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Returns either wx.ID_CANCEL or wx.ID_OK if ShowModal().

    """
    def __init__(self, parent):
        """Create a dialog to fix settings.

        :param parent: (wx.Window)

        """
        super(sppasSettingsDialog, self).__init__(
            parent=parent,
            title="Settings",
            style=wx.DEFAULT_FRAME_STYLE | wx.DIALOG_NO_PARENT)

        self._back_up = dict()
        self._backup_settings()

        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_CLOSE, self.on_cancel)

        self.CreateHeader("Settings...", "settings")
        self._create_content()
        self._create_buttons()
        self.LayoutComponents()
        self.CenterOnParent()

    # -----------------------------------------------------------------------

    def _backup_settings(self):
        """Store settings that can be modified."""
        settings = wx.GetApp().settings

        self._back_up['bg_color'] = settings.bg_color
        self._back_up['fg_color'] = settings.fg_color
        self._back_up['text_font'] = settings.text_font

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the message dialog."""
        notebook = sppasNotebook(self, name="content")
        page1 = WxSettingsPanel(notebook)
        # page2 = PrefsThemePanel(self.notebook, self.preferences)
        # page3 = PrefsAnnotationPanel(self.notebook, self.preferences)
        # add the pages to the notebook with the label to show on the tab
        notebook.AddPage(page1, "General")
        # self.notebook.AddPage(page2, "Icons Theme")
        # self.notebook.AddPage(page3, "Annotation")

    # -----------------------------------------------------------------------

    def _create_buttons(self):
        """Create the buttons and bind events."""
        settings = wx.GetApp().settings
        panel = wx.Panel(self, name="actions")
        panel.SetMinSize(wx.Size(-1, settings.action_height))
        panel.SetBackgroundColour(settings.button_bg_color)

        close_btn = sppasBitmapTextButton(panel, "Okay", name="okay")
        cancel_btn = sppasBitmapTextButton(panel, "Cancel", name="cancel")
        apply_btn = sppasBitmapTextButton(panel, "Test", name="apply")
        line_1 = wx.StaticLine(panel, style=wx.LI_VERTICAL)
        line_2 = wx.StaticLine(panel, style=wx.LI_VERTICAL)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(apply_btn, 2, wx.EXPAND, border=0)
        sizer.Add(line_1, 0, wx.EXPAND, 0)
        sizer.Add(cancel_btn, 2, wx.EXPAND, border=0)
        sizer.Add(line_2, 0, wx.EXPAND, 0)
        sizer.Add(close_btn, 2, wx.EXPAND, border=0)
        self.Bind(wx.EVT_BUTTON, self._process_event)

        self.SetAffirmativeId(close_btn.GetId())
        self.SetEscapeId(cancel_btn.GetId())

        panel.SetSizer(sizer)

    # ------------------------------------------------------------------------
    # Callback to events
    # ------------------------------------------------------------------------

    def _process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()

        if event_name == "cancel":
            self.on_cancel(event)

        elif event_name == "apply":
            self._apply()

        else:
            event.Skip()

    # ------------------------------------------------------------------------

    def on_cancel(self, event):
        """Restore initial settings and close dialog."""
        # Get initial settings from our backup: set to settings
        settings = wx.GetApp().settings
        for k in self._back_up:
            settings.set(k, self._back_up[k])
        # close the dialog with a wx.ID_CANCEL response
        self.SetReturnCode(wx.ID_CANCEL)
        event.Skip()

    # ------------------------------------------------------------------------

    def _apply(self):
        """Apply new settings to the dialog."""
        p = self.FindWindow("content")
        p.SetBackgroundColour(wx.GetApp().settings.bg_color)
        p.SetForegroundColour(wx.GetApp().settings.fg_color)
        p.SetFont(wx.GetApp().settings.text_font)
        self.Refresh()

# ----------------------------------------------------------------------------


class WxSettingsPanel(sppasPanel):
    """Settings for wx objects: background, foreground, font, etc.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self, parent):
        super(WxSettingsPanel, self).__init__(
            parent=parent,
            style=wx.BORDER_NONE
        )
        self._create_content()
        self.SetAutoLayout(True)

        self.SetBackgroundColour(wx.GetApp().settings.bg_color)
        self.SetForegroundColour(wx.GetApp().settings.fg_color)
        self.SetFont(wx.GetApp().settings.text_font)

    # ------------------------------------------------------------------------

    def _create_content(self):
        """"""
        flag = wx.ALL | wx.ALIGN_CENTER_VERTICAL
        gbs = wx.GridBagSizer(hgap=10, vgap=10)

        # ---------- Background color

        txt_bg = wx.StaticText(self, -1, "Background color: ")
        gbs.Add(txt_bg, (0, 0), flag=flag, border=5)

        bmp = sppasSwissKnife.get_bmp_icon("bg_color", height=24)
        self.btn_color_bg = wx.BitmapButton(self, -1, bmp, name="bg_color")
        self.btn_color_bg.Bind(wx.EVT_BUTTON, self.on_color_dialog, self.btn_color_bg)
        gbs.Add(self.btn_color_bg, (0, 1), flag=flag, border=5)

        # ---------- Foreground color

        bmp = sppasSwissKnife.get_bmp_icon("fg_color", height=24)
        txt_fg = wx.StaticText(self, -1, "Foreground color: ")
        gbs.Add(txt_fg, (1, 0), flag=flag, border=5)

        self.btn_color_fg = wx.BitmapButton(self, -1, bmp, name="fg_color")
        self.btn_color_fg.Bind(wx.EVT_BUTTON, self.on_color_dialog, self.btn_color_fg)
        gbs.Add(self.btn_color_fg, (1, 1), flag=flag, border=5)

        # ---------- Font

        txt_font = wx.StaticText(self, -1, "Font: ")
        gbs.Add(txt_font, (2, 0), flag=flag, border=5)

        bmp = sppasSwissKnife.get_bmp_icon("font", height=24)
        btn_font = wx.BitmapButton(self, -1, bmp)
        self.Bind(wx.EVT_BUTTON, self.on_select_font, btn_font)
        gbs.Add(btn_font, (2, 1), flag=flag, border=5)

        # ---------- tips
        #
        # txt_tips = wx.StaticText(self, -1, "Show tips at start-up: ")
        # gbs.Add(txt_tips, (4,0), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        #
        # btn_tips = wx.CheckBox(self, -1, "")
        # btn_tips.SetValue( self.preferences.GetValue('M_TIPS'))
        # self.Bind(wx.EVT_CHECKBOX, self.onTipsChecked, btn_tips)
        # gbs.Add(btn_tips, (4,1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        # ----------

        gbs.AddGrowableCol(1)
        self.SetSizer(gbs)

    # -----------------------------------------------------------------------
    # Callbacks to event
    # -----------------------------------------------------------------------

    def on_color_dialog(self, event):
        """Open a dialog to choose a color, then fix it.

        :param event: (wx.Event)

        """
        color = GetColour(self)
        if color is not None:

            # get the button that was clicked on
            button = event.GetEventObject()
            name = button.GetName()

            # fix new value in the settings
            wx.GetApp().settings.set(name, color)
            if name == "bg_color":
                logging.debug('New {:s}: ({:d}, {:d}, {:d})'.format(
                    name,
                    wx.GetApp().settings.bg_color.Red(),
                    wx.GetApp().settings.bg_color.Green(),
                    wx.GetApp().settings.bg_color.Blue()))
            if name == "fg_color":
                logging.debug('New fg color: ({:d}, {:d}, {:d})'.format(
                    wx.GetApp().settings.fg_color.Red(),
                    wx.GetApp().settings.fg_color.Green(),
                    wx.GetApp().settings.fg_color.Blue()))

    # -----------------------------------------------------------------------

    def on_select_font(self, event):
        """Open a dialog to choose a font, then fix it.

        :param event: (wx.Event)

        """
        data = wx.FontData()
        data.EnableEffects(True)
        data.SetColour(wx.GetApp().settings.fg_color)
        data.SetInitialFont(wx.GetApp().settings.text_font)

        dlg = wx.FontDialog(self, data)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            wx.GetApp().settings.set('text_font', font)
            logging.debug('New text font: {:s}'.format(wx.GetApp().settings.text_font.GetFaceName()))

        dlg.Destroy()

# ---------------------------------------------------------------------------


def Settings(parent):
    """Display a dialog to fix new settings.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    :param parent: (wx.Window)
    :returns: the response

    Returns wx.ID_CANCEL if the dialog is destroyed or wx.ID_OK if some
    settings changed.

    """
    dialog = sppasSettingsDialog(parent)
    response = dialog.ShowModal()
    dialog.Destroy()
    return response
