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
            log_file=None
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
        title_font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font = title_font.Bold()
        title_font = title_font.Scale(2.)

        button_font = wx.Font(12,  # point size
                              wx.FONTFAMILY_DEFAULT,  # family,
                              wx.FONTSTYLE_NORMAL,    # style,
                              wx.FONTWEIGHT_NORMAL,   # weight,
                              underline=False,
                              faceName="Calibri",
                              encoding=wx.FONTENCODING_SYSTEM)

        self.__dict__ = dict(
            frame_style=wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX,
            frame_width=640,
            frame_height=480,
            fg_color=wx.Colour(250, 250, 240, alpha=wx.ALPHA_OPAQUE),
            bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            title_height=64,
            title_fg_color=wx.Colour(95, 95, 90, alpha=wx.ALPHA_OPAQUE),
            title_bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            title_text_font=title_font,
            button_text_font=button_font,
            button_fg_color=wx.Colour(250, 250, 240, alpha=wx.ALPHA_OPAQUE),
            button_bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            text_font=wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        )
