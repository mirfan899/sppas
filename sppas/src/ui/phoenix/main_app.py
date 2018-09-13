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

    ui.phoenix.main.py
    ~~~~~~~~~~~~~~~~~~

This is the main application for SPPAS, based on the Phoenix API.
Create and run the application:

>>> app = sppasApp()
>>> app.run()

"""
import wx
import logging
from os import path
from argparse import ArgumentParser

from sppas.src.config import sg
from .main_config import WxAppConfig, WxAppSettings
from .main_frame import sppasFrame

# ---------------------------------------------------------------------------


class sppasApp(wx.App):
    """Create the SPPAS Phoenix application.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self):
        """Wx Application initialization."""
        # Initialize the wx application
        self.cfg = WxAppConfig()
        wx.App.__init__(self,
                        redirect=False,
                        filename=self.cfg.log_file,
                        useBestVisual=True,
                        clearSigInt=True)

        self.SetAppName(self.cfg.name)
        self.SetAppDisplayName(self.cfg.name)

        # Fix language and translation
        lang = wx.LANGUAGE_DEFAULT
        self.locale = wx.Locale(lang)

        # Fix wx settings and logging
        self.settings = WxAppSettings()
        self.process_command_line_args()
        self.setup_python_logging()

    # -----------------------------------------------------------------------

    def process_command_line_args(self):
        """Process the command line...

        This is an opportunity for users to fix some args.

        """
        # create a parser for the command-line arguments
        parser = ArgumentParser(
            usage="{:s}".format(path.basename(__file__)),
            description="... " + sg.__longname__)

        # add arguments here
        parser.add_argument("-l", "--log_level",
                            required=False,
                            type=int,
                            default=self.cfg.log_level,
                            help='Log level (default={:d}).'
                                 ''.format(self.cfg.log_level))

        # then parse
        args = parser.parse_args()

        # and do things with arguments
        if args.log_level:
            self.cfg.set('log_level', args.log_level)

    # -----------------------------------------------------------------------

    def setup_python_logging(self):
        """Setup python logging to stderr."""
        # Fix the format of the messages
        format_msg = "%(asctime)s [%(levelname)s] %(message)s"

        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(format_msg))
        handler.setLevel(self.cfg.log_level)
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(self.cfg.log_level)

        # Show a welcome message on the console!
        logging.info("{:s} logging set up level={:d}"
                     "".format(self.GetAppDisplayName(), self.cfg.log_level))

    # -----------------------------------------------------------------------

    def run(self):
        # here we could fix things like:
        #  - is first launch? No? so create config! and/or display a welcome msg!
        #  - fix config dir,
        #  - etc

        # Create the main frame of the application and show it.
        frame = sppasFrame()
        self.SetTopWindow(frame)
        self.MainLoop()

    # -----------------------------------------------------------------------

    def OnExit(self):
        """Optional. Override the already existing method to kill the app.

        This method is invoked when the user:

            - clicks on the [X] button of the frame manager
            - does "ALT-F4" (Windows) or CTRL+X (Unix)

        """
        logging.info('OnExit the wx.App.')
        # then it will exit. Nothing special to do. Return the exit status.
        return 0
