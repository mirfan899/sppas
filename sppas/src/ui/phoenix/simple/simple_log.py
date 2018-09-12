import logging
import wx


# -----------------------------------------------------------------------

def setup_logging(log_level):
    """Setup the logging.

    Fix the level of messages and where to redirect them.

    """
    # Fix the format of the messages
    formatmsg = "%(asctime)s [%(levelname)s] %(message)s"

    # Setup logging to stderr
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(formatmsg))
    handler.setLevel(log_level)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(log_level)

    # Show a welcome!
    logging.info("Logging set up level={:d}".format(log_level))

# -----------------------------------------------------------------------


class MyLogTarget(wx.Log):
    WXLOG_TO_PYLOG = {
        wx.LOG_FatalError: logging.critical,
        wx.LOG_Error: logging.error,
        wx.LOG_Warning: logging.warning,
        wx.LOG_Message: logging.info,
        wx.LOG_Status: logging.info,
        wx.LOG_Info: logging.info,
        wx.LOG_Debug: logging.debug,
    }

    def DoLogRecord(self, level, msg, info=None):
        msg = '[wxPython] ' + msg
        MyLogTarget.WXLOG_TO_PYLOG[level](msg)

# -----------------------------------------------------------------------


class MyLogTextCtrl(wx.LogTextCtrl):
    WXLOG_TO_PYLOG = {
        wx.LOG_FatalError: logging.critical,
        wx.LOG_Error: logging.error,
        wx.LOG_Warning: logging.warning,
        wx.LOG_Message: logging.info,
        wx.LOG_Status: logging.info,
        wx.LOG_Info: logging.info,
        wx.LOG_Debug: logging.debug,
    }

    def __init__(self, textctrl):
        super(MyLogTextCtrl, self).__init__(textctrl)

    def DoLogRecord(self, level, msg, info=None):
        """Override."""
        # Send the message to the python logging
        msg = '[wxPython] ' + msg
        MyLogTextCtrl.WXLOG_TO_PYLOG[level](msg)
        # Show the message into the wx.TextCtrl
        wx.LogTextCtrl.DoLogRecord(self, level, msg, info)


class MyLogFrame(wx.Frame):
    def __init__(self, *a, **k):
        wx.Frame.__init__(self, *a, **k)
        text_style = wx.TAB_TRAVERSAL | \
                     wx.TE_MULTILINE | \
                     wx.TE_READONLY | \
                     wx.TE_BESTWRAP | \
                     wx.TE_AUTO_URL | \
                     wx.NO_BORDER
        self.txt = wx.TextCtrl(self, wx.ID_ANY,
                               value="",
                               style=text_style)
        self.Show(True)

# -----------------------------------------------------------------------


class MyFrame(wx.Frame):
    def __init__(self, *a, **k):
        wx.Frame.__init__(self, *a, **k)
        b = wx.Button(self, -1, 'clic')
        b.Bind(wx.EVT_BUTTON, self.on_clic)

    def on_clic(self, evt):
        wx.LogMessage('clic from wx.LogMessage')
        logging.info('info from logging.info')

# -----------------------------------------------------------------------


class MyApp(wx.App):
    def __init__(self):
        # Initialize the wx application
        wx.App.__init__(self,
                        redirect=False,
                        filename=None,
                        useBestVisual=True,
                        clearSigInt=True)

        # Setup the logging of Python
        setup_logging(10)

        # Setup the logging of wx
        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(10)

        # This is a first solution using a wx.LogWindow
        #wx.Log.SetActiveTarget(MyLogTarget())
        #self.log_window = wx.LogWindow(None, 'Log Window', show=True, passToOld=True)

        # This is a second solution using a customized frame
        self.log_window = MyLogFrame(None)
        wx.Log.SetActiveTarget(MyLogTextCtrl(self.log_window.txt))

# -----------------------------------------------------------------------


if __name__ == '__main__':
    app = MyApp()
    MyFrame(None).Show()
    app.MainLoop()
