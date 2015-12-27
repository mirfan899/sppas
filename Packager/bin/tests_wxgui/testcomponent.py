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

from wxgui.frames.baseframe   import ComponentFrame
from wxgui.clients.baseclient import BaseClient


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

class TestClient( BaseClient ):
    def __init__( self, parent, prefsIO ):
        BaseClient.__init__( self, parent, prefsIO )
    def CreateComponent(self, parent, prefsIO ):
        panel = wx.Panel(parent, -1)
        panel.SetBackgroundColour( prefsIO.GetValue( "M_BG_COLOUR" ))
        box = wx.BoxSizer(wx.VERTICAL)
        m_text = wx.StaticText(panel, -1, "Hello World!")
        m_text.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
        m_text.SetSize(m_text.GetBestSize())
        box.Add(m_text, 0, wx.ALL, 10)
        panel.SetSizer(box)
        panel.Layout()
        return panel


class TestComponent( ComponentFrame ):
    def __init__(self, parent, id, args={}):
        ComponentFrame.__init__(self, parent, id, args)
    def CreateClient(self, parent, prefsIO):
        #return wx.Panel(parent, -1)
        return TestClient(parent,prefsIO)

# ---------------------------------------------------------------------------


def test_component( argv ):

    # Log
    log_level = 1
    log_file  = None
    setup_logging(log_level, log_file)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:t:", ["help"])
    except getopt.GetoptError, err:
        # Print help information and exit:
        quit("Error: "+str(err)+".\nUse option --help for any help.\n", 1)

    # Args
    arguments = {}

    # Extract options
    for o, a in opts:
        if o == "-i":
            p,b = os.path.split(a)
            if not p:
                p = os.getcwd()
            arguments['files'].append( os.path.abspath(os.path.join(p,b)) )
        elif o == "-t":
            arguments['title'] = a
        elif o == "--help": # need help
            print 'No Help!'
            sys.exit(0)

    # App
    app = wx.App()
    frame = TestComponent(None, -1, arguments)

    app.SetTopWindow(frame)
    if "files" in arguments:
        frame.AddFiles( arguments["files"] )

    app.MainLoop()

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    if len(sys.argv) < 1:
        # stop the program and print an error message
        sys.exit(1)

    test_component( sys.argv )

# ---------------------------------------------------------------------------

