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

    ui.phoenix.main_config.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""
import wx

from sppas.src.config import sg
from sppas.src.config import sppasBaseSettings

# ---------------------------------------------------------------------------


class WxAppConfig(sppasBaseSettings):
    """Manage the application global settings.

    Config is represented in a dictionary.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self):
        """Create the dictionary of wx settings."""
        super(WxAppConfig, self).__init__()

        self.__dict__ = dict(
            name=sg.__name__ + " " + sg.__version__,
            log_level=15,
            log_file=None,
        )

    def set(self, key, value):
        """Set a new value to a key."""
        self.__dict__[key] = value

# ---------------------------------------------------------------------------


class WxAppSettings(sppasBaseSettings):
    """Manage the application global settings for look&feel.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """
    def __init__(self):
        """Create the dictionary of settings."""
        super(WxAppSettings, self).__init__()

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of settings from a json file."""
        self.reset()

    # -----------------------------------------------------------------------

    def reset(self):
        """Fill the dictionary with the default values."""
        font_height = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPixelSize()[1]

        self.__dict__ = dict(
            splash_delay=3,
            frame_style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX,
            frame_size=self.__frame_size(),

            icons_theme="Refine",

            fg_color=wx.Colour(230, 230, 230, alpha=wx.ALPHA_OPAQUE),
            title_fg_color=wx.Colour(128, 128, 128, alpha=wx.ALPHA_OPAQUE),
            button_fg_color=wx.Colour(128, 128, 128),

            bg_color=wx.Colour(20, 20, 20, alpha=wx.ALPHA_OPAQUE),
            title_bg_color=wx.Colour(40, 40, 40, alpha=wx.ALPHA_OPAQUE),
            button_bg_color=wx.Colour(30, 30, 30, alpha=wx.ALPHA_OPAQUE),

            title_text_font=self.__title_font(),
            button_text_font=self.__button_font(),
            text_font=self.__text_font(),
            mono_text_font=self.__mono_font(),

            title_height=font_height*5,
            action_height=font_height*3,
        )

    # -----------------------------------------------------------------------

    def __text_font(self):
        text_font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        return text_font

    # -----------------------------------------------------------------------

    def __title_font(self):
        title_font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font = title_font.Bold()
        title_font = title_font.Scale(2.)
        return title_font

    # -----------------------------------------------------------------------

    def __button_font(self):
        system_font_size = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT).GetPointSize()
        button_font = wx.Font(system_font_size,       # point size
                              wx.FONTFAMILY_DEFAULT,  # family,
                              wx.FONTSTYLE_NORMAL,    # style,
                              wx.FONTWEIGHT_NORMAL,   # weight,
                              underline=False,
                              faceName="Calibri",
                              encoding=wx.FONTENCODING_SYSTEM)
        button_font.Scale(1.2)
        return button_font

    # -----------------------------------------------------------------------

    def __mono_font(self):
        mono_font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        mono_font.SetFamily(wx.FONTFAMILY_MODERN)
        mono_font.Scale(0.9)
        return mono_font

    # -----------------------------------------------------------------------

    def __frame_size(self):
        (w, h) = wx.GetDisplaySize()
        w *= 0.6
        h = min(0.9*h, w*9/16)
        return wx.Size(max(int(w), 640), max(int(h), 480))

    # -----------------------------------------------------------------------

    def set(self, key, value):
        """Set a new value to a key."""
        setattr(self, key, value)
