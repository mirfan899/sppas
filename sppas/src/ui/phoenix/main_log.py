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
import os
import platform
import wx
import wx.lib.newevent
import logging
from datetime import date

from sppas.src.config import sg
from sppas.src.config import paths
from sppas.src.utils.datatype import sppasTime

from .controls.buttons import sppasBitmapTextButton
from .controls.texts import sppasTitleText

# ---------------------------------------------------------------------------

# event used to send a logging record to a wx object
wxLogEvent, EVT_WX_LOG_EVENT = wx.lib.newevent.NewEvent()

# match between wx log levels and python log level names
match_levels = {
    wx.LOG_FatalError: 'CRITICAL',
    wx.LOG_Error: 'ERROR',
    wx.LOG_Warning: 'WARNING',
    wx.LOG_Info: 'INFO',
    wx.LOG_Message: 'INFO',
    wx.LOG_Debug: 'DEBUG'
}

# ---------------------------------------------------------------------------


def log_level_to_wx(log_level):
    """Convert a python logging log level to a wx one.

    From python logging log levels:

        50 - CRITICAL
        40 - ERROR
        30 - WARNING
        20 - INFO
        10 - DEBUG
        0 - NOTSET

    To wx log levels:

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

    :param log_level: (int) python logging log level
    :return: (int) wx log level

    """
    if log_level == logging.CRITICAL:
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


class sppasLogFile(object):
    """Utility file name manager for wx logs.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self):
        """Create a sppasLogFile instance.

        Create the log directory if not already existing then fix the
        log filename with increment=0.

        """
        log_dir = paths.logs
        if os.path.exists(log_dir) is False:
            os.mkdir(log_dir)

        self.__filename = "{:s}_log_".format(sg.__name__)
        self.__filename += str(date.today()) + "_"
        self.__filename += str(os.getpid()) + "_"
        self.__current = 0

    # -----------------------------------------------------------------------

    def get_filename(self):
        """Return the current log filename."""
        fn = os.path.join(paths.logs, self.__filename)
        fn += "{0:04d}".format(self.__current)
        return fn + ".txt"

    # -----------------------------------------------------------------------

    def increment(self):
        """Increment the current log filename."""
        self.__current += 1

    # -----------------------------------------------------------------------

    def get_header(self):
        """Return a string with an header for log files."""
        header = "-"*78
        header += "\n\n"
        header += " {:s} {:s}".format(sg.__name__, sg.__version__)
        header += "\n"
        header += " {:s}".format(sppasTime().now)
        header += "\n"
        header += " {:s}".format(platform.platform())
        header += "\n"
        header += " python {:s}".format(platform.python_version())
        header += "\n"
        header += " wxpython {:s}".format(wx.version())
        header += "\n\n"
        header += "-"*78
        header += "\n\n"
        return header

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


class sppasLogWindow(wx.TopLevelWindow):
    """Create a log window for SPPAS.

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
        super(sppasLogWindow, self).__init__(
            parent=parent,
            title='{:s} Log'.format(sg.__name__),
            style=wx.DEFAULT_FRAME_STYLE | wx.FRAME_TOOL_WINDOW)

        # Members
        self.handler = sppasHandlerToWx(self)
        self.txt = None
        self.log_file = sppasLogFile()

        # Fix frame properties
        self.SetMinSize((320, 200))
        self.SetSize(wx.Size(640, 480))
        self.SetName('{:s}-log'.format(sg.__name__))

        # Fix frame content and actions
        self._create_content()
        self._setup_wx_logging(log_level)
        self.setup_events()
        self.Show(True)

    # -----------------------------------------------------------------------

    def _create_content(self):
        """Create the content of the frame.

        Content is made of a title, the log textctrl and action buttons.

        """
        self.SetBackgroundColour(wx.GetApp().settings.bg_color)

        # create a sizer to add and organize objects
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized title and separate title and the rest with a line
        title = sppasLogTitlePanel(self)
        top_sizer.Add(title, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)
        line_top = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a panel for the messages
        msg_panel = sppasLogMessagePanel(
            parent=self,
            header=self.log_file.get_header())
        top_sizer.Add(msg_panel, 3, wx.ALL | wx.EXPAND, 0)
        self.txt = msg_panel.txt

        # separate top and the rest with a line
        line = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = sppasLogActionPanel(self)
        top_sizer.Add(actions, 0,
                      wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Layout the content
        self.SetAutoLayout(True)
        self.SetSizer(top_sizer)
        self.Layout()

    # -----------------------------------------------------------------------

    def _setup_wx_logging(self, log_level):
        """Setup the logging.

        Fix the level of messages and where to redirect them.

        :param log_level: (int) Python logging log level.

        """
        # python log level
        self.handler.setLevel(log_level)

        # fix wx log messages
        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(log_level_to_wx(log_level))
        wx.Log.SetActiveTarget(sppasLogTextCtrl(self.txt))

        # redirect python logging messages to wx.Log
        self.redirect_logging()

        # test if everything is ok
        logging.debug('This is how a debug message looks like. ')
        logging.info('This is how an information message looks like.')
        logging.warning('This is how a warning message looks like.')
        logging.error('This is how an error message looks like.')

    # -----------------------------------------------------------------------
    # Events
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

        # Bind all events from our buttons
        self.Bind(wx.EVT_BUTTON, self.process_event)

    # -----------------------------------------------------------------------

    def process_event(self, event):
        """Process any kind of events.

        :param event: (wx.Event)

        """
        event_obj = event.GetEventObject()
        event_name = event_obj.GetName()
        event_id = event_obj.GetId()

        wx.LogMessage("Log frame received event id {:d} of {:s}"
                      "".format(event_id, event_name))

        if event_name == "save_log":
            self.save()
        elif event_name == "broom":
            self.clear()
        else:
            event.Skip()

    # -----------------------------------------------------------------------
    # Override existing methods in wx.Frame
    # -----------------------------------------------------------------------

    def Show(self, show=True):
        """Override. Disable the availability to Hide()."""
        wx.Frame.Show(self, True)

    # -----------------------------------------------------------------------
    # Callbacks to events
    # -----------------------------------------------------------------------

    def on_close(self, event):
        """Cancel the availability to close the frame, iconize instead.

        :param event: (wxEvent) unused

        """
        wx.LogMessage("Attempt to close {:s}.".format(self.GetName()))
        self.Iconize(True)

    # -----------------------------------------------------------------------

    def on_log_event(self, event):
        """Add event.message to the textctrl.

        :param event: (wxLogEvent)

        """
        levels = {
            'DEBUG': wx.LogDebug,
            'INFO': wx.LogMessage,
            'WARNING': wx.LogWarning,
            'ERROR': wx.LogError,
            'CRITICAL': wx.LogFatalError
        }
        levels[event.record.levelname](event.record.message)
        event.Skip()

    # -----------------------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------------------

    def redirect_logging(self, redirect=True):
        """Stop/Start the python logging redirection to this frame.

        :param redirect: (bool) redirect python logging to wx, or not

        """
        if redirect is False:
            logging.getLogger().removeHandler(self.handler)
            logging.info('Python logging messages are directed to stderr.')
        else:
            logging.getLogger().addHandler(self.handler)
            logging.info('Python logging messages are redirected to wxLog.')

    # -----------------------------------------------------------------------

    def focus(self):
        """Assign the focus to the log frame."""
        if self.IsIconized():
            self.Iconize(False)
        self.SetFocus()

    # -----------------------------------------------------------------------

    def save(self):
        """Save the messages in the current log file."""
        self.txt.SaveFile(self.log_file.get_filename())
        self.clear()
        self.txt.AppendText('Previous messages were saved in : {:s}\n'
                            ''.format(self.log_file.get_filename()))
        self.log_file.increment()

    # -----------------------------------------------------------------------

    def clear(self):
        """Clear all messages (irreversible, the messages are deleted)."""
        self.txt.Clear()
        self.txt.AppendText(self.log_file.get_header())

# ---------------------------------------------------------------------------


class sppasLogTextCtrl(wx.LogTextCtrl):
    """Create a textctrl to display log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, textctrl):
        """Initialize a sppasLogTextCtrl."""
        super(sppasLogTextCtrl, self).__init__(textctrl)
        self.textctrl = textctrl
        # here we could create various styles (one for debug messages, one
        # for information, one for errors, etc).

    # -----------------------------------------------------------------------

    def DoLogRecord(self, level, msg, info=None):
        """Override. Called to log a new record.

        :param level: (wx.LogLevel)
        :param msg: (string)
        :param info: (wx.LogRecordInfo)

        Display the message with colors.

        """
        # Display time with the default color
        self.textctrl.SetDefaultStyle(
            wx.TextAttr(wx.GetApp().settings.fg_color))
        self.textctrl.write("{:s} ".format(sppasTime().now[:-6]))

        # Display the log level name and message with colors
        if level == wx.LOG_Error or level == wx.LOG_FatalError:
            self.textctrl.SetDefaultStyle(wx.TextAttr(wx.RED))
        elif level == wx.LOG_Warning:
            self.textctrl.SetDefaultStyle(wx.TextAttr(wx.YELLOW))
        elif level in (wx.LOG_Info, wx.LOG_Message, wx.LOG_Status):
            self.textctrl.SetDefaultStyle(wx.TextAttr(wx.WHITE))
        else:
            self.textctrl.SetDefaultStyle(wx.TextAttr(wx.LIGHT_GREY))

        level_name = "[{:s}]".format(match_levels[level])
        self.textctrl.write("{0: <10}".format(level_name))
        self.textctrl.write("{:s}\n".format(msg))

# ---------------------------------------------------------------------------
# Panels
# ---------------------------------------------------------------------------


class sppasLogTitlePanel(wx.Panel):
    """Create a panel to include the frame title.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasLogTitlePanel, self).__init__(
            parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | wx.CLIP_CHILDREN)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.title_bg_color)
        self.SetMinSize((-1, settings.title_height))

        # Create the title
        title = '{:s} Log Window'.format(sg.__name__)
        st = sppasTitleText(self, title)

        # Put the title in a sizer
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        title_sizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, border=10)
        self.SetSizer(title_sizer)
        self.SetAutoLayout(True)

# ---------------------------------------------------------------------------


class sppasLogMessagePanel(wx.Panel):
    """Create the panel to display log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent, header=""):
        super(sppasLogMessagePanel, self).__init__(
            parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | wx.CLIP_CHILDREN)

        # fix this panel look&feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.bg_color)
        self.SetMinSize((-1, 128))

        # create a log message, i.e. a wx textctrl
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER | wx.TE_RICH
        self.txt = wx.TextCtrl(self, wx.ID_ANY,
                               value=header,
                               style=text_style)
        self.txt.SetFont(settings.mono_text_font)
        self.txt.SetForegroundColour(settings.fg_color)
        self.txt.SetBackgroundColour(settings.bg_color)

        # put the text in a sizer to expand it
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.txt, 1, wx.ALL | wx.EXPAND, border=10)
        self.SetSizer(sizer)
        self.SetAutoLayout(True)

# ---------------------------------------------------------------------------


class sppasLogActionPanel(wx.Panel):
    """Create a panel with some action buttons to manage log messages.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, parent):
        super(sppasLogActionPanel, self).__init__(
            parent,
            style=wx.TAB_TRAVERSAL | wx.BORDER_NONE | \
                  wx.WANTS_CHARS | wx.CLIP_CHILDREN)

        # fix this panel look&feel
        settings = wx.GetApp().settings
        self.SetMinSize((-1, settings.action_height))
        self.SetBackgroundColour(settings.bg_color)

        # create action buttons
        clear_btn = sppasBitmapTextButton(self, "Clear", name="broom")
        save_btn = sppasBitmapTextButton(self, "Save", name="save_log")

        # organize buttons in a sizer
        line = wx.StaticLine(self, style=wx.LI_VERTICAL)
        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(clear_btn, 2, wx.ALL | wx.EXPAND, 1)
        action_sizer.Add(line, 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(save_btn, 2, wx.ALL | wx.EXPAND, 1)
        self.SetSizer(action_sizer)
        self.SetAutoLayout(True)
