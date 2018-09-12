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

    ui.phoenix.main_log.py
    ~~~~~~~~~~~~~~~~~~~~~

"""
import wx
import wx.lib.newevent
import logging

from sppas.src.config import sg

# ---------------------------------------------------------------------------

# event used to send a logging record to a wx object
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()

# style of the frame (disable 'Close')
frame_style = wx.DEFAULT_FRAME_STYLE & ~wx.CLOSE_BOX

# ---------------------------------------------------------------------------


def log_level_to_wx(log_level):
    """Convert a python logging log level to a wx one.

    From:
        50 - CRITICAL
        40 - ERROR
        30 - WARNING
        20 - INFO
        10 - DEBUG
        0 - NOTSET

    To:
        0 - LOG_FatalError 	program can’t continue, abort immediately
        1 - LOG_Error 	a serious error, user must be informed about it
        2 - LOG_Warning user is normally informed about it but may be ignored
        3 - LOG_Message normal message (i.e. normal output of a non GUI app)
        4 - LOG_Status 	informational: might go to the status line of GUI app
        5 - LOG_Info 	informational message (a.k.a. ‘Verbose’)
        6 - LOG_Debug 	never shown to the user, disabled in release mode
        7 - LOG_Trace 	trace messages are also only enabled in debug mode
        8 - LOG_Progress 	used for progress indicator (not yet)
        100 - LOG_User 	user defined levels start here
        10000 LOG_Max

    :param log_level: (int)
    :return: (int)

    """
    if log_level == 0:
        return wx.LOG_Message
    if log_level <= 10:
        return wx.LOG_Debug
    if log_level <= 20:
        return wx.LOG_Info
    if log_level <= 30:
        return wx.LOG_Warning
    if log_level <= 40:
        return wx.LOG_Error
    return wx.LOG_FatalError

# ---------------------------------------------------------------------------


class sppasHandlerToWx(logging.Handler):
    """Logging handler class which sends log strings to a wx object.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, wx_dest=None):
        """Initialize the handler.

        :param wx_dest: (wx.Window) destination object to post the event to

        """
        super(sppasHandlerToWx, self).__init__()

        if isinstance(wx_dest, wx.Window) is False:
            raise TypeError('Expected a wx.Window but got {} instead.'
                            ''.format(type(wx_dest)))
        self.wx_dest = wx_dest

    # -----------------------------------------------------------------------

    def flush(self):
        """Override. Do nothing for this handler."""
        pass

    # -----------------------------------------------------------------------

    def emit(self, record):
        """Override. Emit a record.

        :param record: (logging.LogRecord)

        """
        try:
            # the log event sends the record to the destination wx object
            event = wxLogEvent(record=record)
            wx.PostEvent(self.wx_dest, event)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

# ---------------------------------------------------------------------------


class sppasLogFrame(wx.Frame):
    """Create a log frame for SPPAS.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    A background log window: it collects all log messages in the log
    frame which it manages but also collect them from the log target
    which was active at the moment of its creation.

    """

    def __init__(self, parent, log_level=0):
        """Create the frame to display log messages.

        :param parent: (wx.Window)
        :param log_level: (int)

        Log levels:

            - CRITICAL 	50
            - ERROR 	40
            - WARNING 	30
            - INFO 	    20
            - DEBUG 	10
            - NOTSET 	0

        """
        super(sppasLogFrame, self).__init__(
            parent=parent,
            title='{:s} Log Window'.format(sg.__name__),
            style=frame_style)

        # Members
        self.handler = sppasHandlerToWx(self)
        self.txt = None

        # Fix frame properties
        self.SetMinSize((300, 200))
        self.SetSize(wx.Size(640, 480))
        self.SetName('{:s} Log Window'.format(sg.__name__))

        # Fix frame content and actions
        self.create_content()
        self.setup_wx_logging(log_level)
        self.setup_events()

    # -----------------------------------------------------------------------

    def create_content(self):
        """Create the content of the frame."""
        settings = wx.GetApp().settings
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER
        self.txt = wx.TextCtrl(self, wx.ID_ANY,
                               value="",
                               style=text_style)
        font = settings.text_font
        self.txt.SetFont(font)
        self.txt.SetForegroundColour(settings.fg_color)
        self.txt.SetBackgroundColour(settings.bg_color)

    # -----------------------------------------------------------------------

    def setup_events(self):
        """Associate a handler function with the events.

        It means that when an event occurs then the process handler function
        will be called.

        """
        # Bind close event from the close dialog 'x' on the frame
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Bind the log event
        self.Bind(EVT_WX_LOG_EVENT, self.on_log_event)

    # -----------------------------------------------------------------------

    def setup_wx_logging(self, log_level):
        """Setup the logging.

        Fix the level of messages and where to redirect them.

        :param log_level: (int) Python logging log level.

        """
        # Fix the format and level of python logging messages
        format_msg = "[%(levelname)s] %(message)s"
        self.handler.setFormatter(logging.Formatter(format_msg))
        self.handler.setLevel(log_level)

        # Fix wx log messages
        wx_log_level = log_level_to_wx(log_level)
        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(wx_log_level)
        wx.Log.SetTimestamp('%Y-%m-%d %H:%M:%S')
        wx.Log.SetActiveTarget(sppasLogTextCtrl(self.txt))
        # todo: Set a wx.LogFormatter to wx.Log (to see the level name!)

        # Redirect python logging messages to wx.Log
        self.redirect_logging()

        # test if everything is ok
        logging.info('++ info. Appears to both sppasLogFrame and stderr.')
        logging.debug('-- debug. Appears to stderr but not in sppasLogFrame.')
        wx.LogMessage('++ wxinfo. Appears to sppasLogFrame.')
        wx.LogDebug('-- wxdebug. Do not appear anywhere.')

    # -----------------------------------------------------------------------

    def on_close(self, event):
        """Cancel the availability to close the frame."""
        wx.LogMessage("Attempt to close {:s}.".format(self.GetName()))

    # -----------------------------------------------------------------------

    def on_log_event(self, event):
        """Add event.message to text window.

        :param event: (wxLogEvent)
        """
        levels = {
            'DEBUG': wx.LogDebug,
            'INFO': wx.LogMessage,
            'WARNING': wx.LogWarning,
            'ERROR': wx.LogError,
            'CRITICAL': wx.LogFatalError
        }
        msg = self.handler.format(event.record)
        levels[event.record.levelname](msg)
        event.Skip()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def redirect_logging(self, value=True):
        """Stop/Start the python logging redirection to this frame.

        :param value: (bool) redirect python logging to wx, or not

        """
        if value is False:
            logging.getLogger().removeHandler(self.handler)
        else:
            logging.getLogger().addHandler(self.handler)

# ---------------------------------------------------------------------------


class sppasLogTextCtrl(wx.LogTextCtrl):

    def __init__(self, textctrl):
        super(sppasLogTextCtrl, self).__init__(textctrl)
        self.textctrl = textctrl

    def DoLogRecord(self, level, msg, info=None):
        """Override. Called to log a new record.

        :param level: (wx.LogLevel)
        :param msg: (string)
        :param info: (wx.LogRecordInfo)

        """
        #if level == wx.LOG_Info:
        self.textctrl.SetDefaultStyle(wx.TextAttr(wx.RED))
        # Show the message into the wx.TextCtrl
        wx.LogTextCtrl.DoLogRecord(self, level, msg, info)
