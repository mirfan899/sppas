# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import platform
import logging
from logging import info as loginfo
import getopt
import wx

from os.path import abspath, dirname, join
import sys

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(join(SPPAS, 'sppas', 'src'))

from wxgui.panels.sndplayer import SndPlayer
from wxgui.sp_consts import *


# ---------------------------------------------------------------------------
# Fix locale, install Gettext
# ---------------------------------------------------------------------------

if platform.system() == "Windows":
    # The appropriate environment variables are set on other systems
    import locale
    language, encoding = locale.getdefaultlocale()
    os.environ['LANG'] = language

# ---------------------------------------------------------------------------
# Setup a logger to communicate on the terminal, or a file.
# ---------------------------------------------------------------------------

def setup_logging(log_level, filename):
    """
    Setup default logger to log to stderr or and possible also to a file.

    The default logger is used like this:
        >>> import logging
        >>> logging.error(text message)
    """
    format= "%(asctime)s [%(levelname)s] %(message)s"
    # Setup logging to stderr
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format))
    console_handler.setLevel(log_level)
    logging.getLogger().addHandler(console_handler)

    # Setup logging to file if filename is specified
    if filename:
        file_handler = logging.FileHandler(filename, "w")
        file_handler.setFormatter(logging.Formatter(format))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
    logging.getLogger().setLevel(log_level)
    loginfo("Logging set up with log level=%s, filename=%s", log_level,
            filename)


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------


def test_factory( argv ):

    # Log
    log_level = 1
    log_file  = None
    setup_logging(log_level, log_file)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "t:", ["help"])
    except getopt.GetoptError, err:
        # Print help information and exit:
        quit("Error: "+str(err)+".\nUse option --help for any help.\n", 1)

    # Args
    arguments = {}
    arguments['files'] = []
    arguments['title'] = "SndRoamer"
    arguments['FILESTYPE']  = "SOUND_FILES"

    # Extract options
    for o, a in opts:
        if o == "-t":
            arguments['title'] = a
        elif o == "--help": # need help
            print 'Help'
            sys.exit(0)


    # App
    app = wx.App()
    frame = wx.Frame(None, -1, 'player test')
    player = SndPlayer(frame)
    frame.Show(True)

    app.SetTopWindow(frame)

    app.MainLoop()

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    if len(sys.argv) < 1:
        # stop the program and print an error message
        usage(sys.stderr)
        sys.exit(1)

    test_factory( sys.argv )

# ---------------------------------------------------------------------------

