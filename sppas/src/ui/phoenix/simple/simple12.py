import wx
import logging
import os
import json
import traceback
from argparse import ArgumentParser

try:
    import wx.adv
    adv_import = True
except ImportError:
    adv_import = False


"""

An extended solution to use global settings, saved in a json file.

"""

# ---------------------------------------------------------------------------
# Base classes to manage global settings.
# ---------------------------------------------------------------------------


class sppasBaseSettings(object):
    """A dictionary of settings stored in a JSON file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Base class to manage any kind of settings, represented in a dictionary.
    A configuration file can be loaded when init and saved when exit.

    """

    def __init__(self):
        """Create the dictionary and load config file if any."""
        self.__dict__ = dict()
        self.load()

    # -----------------------------------------------------------------------

    def __enter__(self):
        return self

    # -----------------------------------------------------------------------

    def __exit__(self, exc_type, exc_value, traceback):
        self.save()

    # -----------------------------------------------------------------------

    def load(self):
        """Load the dictionary of settings from a file."""
        pass

    # -----------------------------------------------------------------------

    def save(self):
        """Save the dictionary of settings in a file."""
        pass

# ---------------------------------------------------------------------------
# Wx global settings
# ---------------------------------------------------------------------------


class WxAppConfig(sppasBaseSettings):
    """Manage the application global settings.

    Config is represented in a non-iterable dictionary.

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
            __name__="Simple wx app",
            splash_delay=10,
            save_on_exit=True,
        )

# ---------------------------------------------------------------------------


class WxAppSettings(sppasBaseSettings):
    """Manage the application modifiable global settings.

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
        try:
            config = json.load(open("settings.json"))
        except FileNotFoundError:
            logging.warning('File with settings not found.')
            return
        except:
            print(traceback.format_exc())
            logging.error('File with settings not loaded.')
            return
        else:
            for key in config:
                value = config[key]

                if value[0] == 'wx.Colour':
                    self.__dict__[key] = self.__parse_color(config, key)

                elif value[0] == 'wx.Font':
                    self.__dict__[key] = self.__parse_font(config, key)

                else:
                    self.__dict__[key] = value[1]
            logging.debug("Application settings loaded successfully.")

    # -----------------------------------------------------------------------

    def __parse_color(self, cfg, key):
        """Return a wx.Colour() from the config dict."""
        if len(cfg[key]) < 4:
            return wx.Colour(0, 0, 0)
        r = cfg[key][1]
        g = cfg[key][2]
        b = cfg[key][3]
        a = cfg[key][4]
        return wx.Colour(r, g, b, a)

    # -----------------------------------------------------------------------

    def __parse_font(self, cfg, key):
        """Return a wx.Font() from the config dict."""
        if len(cfg[key]) < 7:
            return wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        size = cfg[key][1]
        family = cfg[key][2]
        style = cfg[key][3]
        weight = cfg[key][4]
        u = cfg[key][5]
        face = cfg[key][6]
        enc = cfg[key][7]
        return wx.Font(size, family, style, weight, u, face, enc)

    # -----------------------------------------------------------------------

    def __serialize_color(self, color):
        """Return a tuple of values from a wx.Colour()."""
        r = color.Red()
        g = color.Green()
        b = color.Blue()
        a = color.Alpha()
        return 'wx.Colour', r, g, b, a

    # -----------------------------------------------------------------------

    def __serialize_font(self, font):
        """Return a tuple of values from a wx.Font()."""
        size = font.GetPointSize()
        family = font.GetFamily()
        style = font.GetStyle()
        weight = font.GetWeight()
        underline = font.GetUnderlined()
        face = font.GetFaceName()
        enc = font.GetEncoding()
        return 'wx.Font', size, family, style, weight, underline, face, enc

    # -----------------------------------------------------------------------

    def save(self):
        """Save the dictionary of settings in a json file.

        Because wx objects are not serializable by the json library, we have
        to do it before saving.

        """
        config = dict()
        for key in self.__dict__:
            value = self.__dict__[key]

            if isinstance(value, wx.Colour):
               config[key] = self.__serialize_color(value)

            elif isinstance(value, wx.Font):
               config[key] = self.__serialize_font(value)

            else:
                config[key] = str(type(value)), value

        try:
            json.dump(config, open("settings.json", 'w'))
        except:
            print(traceback.format_exc())
            logging.error('Settings not saved in a file.')
            return
        else:
            logging.debug("Application settings saved successfully.")

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
            title_fg_color=wx.Colour(65, 65, 60, alpha=wx.ALPHA_OPAQUE),
            title_bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
            title_text_font=title_font,
            button_text_font=button_font,
            button_fg_color=wx.Colour(250, 250, 240, alpha=wx.ALPHA_OPAQUE),
            button_bg_color=wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE),
        )

# ---------------------------------------------------------------------------


def setup_logging(log_level=15, filename=None):
    """Setup default logger to log to stderr or and possible also to a file.

    :param log_level: Sets the threshold for this logger. Logging messages
    which are less severe than this value will be ignored. When NOTSET is
    assigned, all messages are printed.
    :param filename: Specifies that a FileHandler be created, using the
    specified filename, rather than a StreamHandler.

    The numeric values of logging levels are given in the following:

        - CRITICAL 	50
        - ERROR 	40
        - WARNING 	30
        - INFO 	    20
        - DEBUG 	10
        - NOTSET 	 0

    """
    formatmsg = "%(asctime)s [%(levelname)s] %(message)s"
    if log_level is None:
        log_level = 15

    # Setup logging to file if filename is specified
    if filename is not None:
        file_handler = logging.FileHandler(filename, "a+")
        file_handler.setFormatter(logging.Formatter(formatmsg))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
        logging.getLogger().setLevel(log_level)
        logging.info("Logging set up level={:d}, filename={:s}".format(log_level, filename))

    else:
        # Setup logging to stderr
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(formatmsg))
        console_handler.setLevel(log_level)
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().setLevel(log_level)
        logging.info("Logging set up level={:d}".format(log_level))

# ---------------------------------------------------------------------------


class myTitleText(wx.StaticText):
    """A class to write a title."""

    def __init__(self, parent, title_text):

        wx.StaticText.__init__(self, parent, label=title_text, style=wx.ALIGN_CENTER)

        # Fix Look&Feel
        settings = wx.GetApp().settings

        self.SetFont(settings.title_text_font)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetForegroundColour(settings.title_fg_color)

# ---------------------------------------------------------------------------


class myButton(wx.Button):
    """Create my own button. Inherited from the wx.Button.

    """
    def __init__(self, parent, label, name):

        wx.Button.__init__(self,
                           parent,
                           wx.ID_ANY,
                           label,
                           style=wx.NO_BORDER,
                           name=name)
        # Fix Look&Feel
        settings = wx.GetApp().settings

        self.SetForegroundColour(settings.button_fg_color)
        self.SetBackgroundColour(settings.button_bg_color)
        self.SetFont(settings.button_text_font)

# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        settings = wx.GetApp().settings

        title = wx.GetApp().GetAppDisplayName()
        wx.Frame.__init__(self,
                          None,
                          title=title,
                          style=settings.frame_style)
        self.SetMinSize((300, 200))
        self.SetSize(wx.Size(settings.frame_width, settings.frame_height))

        # Store all panels in a dictionary with key=name, value=object
        self.panels = dict()

        # create a sizer to add and organize objects
        top_sizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = myMenuPanel(self)
        top_sizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # separate menu and the rest with a line
        line_top = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a 1st panel for files
        self.panels["files"] = myFilePanel(self)
        top_sizer.Add(self.panels["files"], 3, wx.ALL | wx.EXPAND, 0)

        # add a 2nd panel for annotations
        self.panels["annotate"] = myAnnotatePanel(self)
        top_sizer.Add(self.panels["annotate"], 3, wx.ALL | wx.EXPAND, 0)

        # add a 3rd panel for analysis
        self.panels["analyze"] = myAnalyzePanel(self)
        top_sizer.Add(self.panels["analyze"], 3, wx.ALL | wx.EXPAND, 0)

        # separate the rest and the action buttons with a line
        line_bottom = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        top_sizer.Add(line_bottom, 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = myActionPanel(self)
        top_sizer.Add(actions, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Associate a handler function with the EVT_BUTTON event.
        # That means that when a button is clicked then the process
        # handler function will be called.
        self.Bind(wx.EVT_BUTTON, self.process_event)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetAutoLayout(True)
        self.SetSizer(top_sizer)
        self.Layout()

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def process_event(self, event):
        """Process any kind of events."""

        event_name = event.GetEventObject().GetName()
        event_id = event.GetEventObject().GetId()
        logging.debug("Received event id {:d} of {:s}"
                      "".format(event_id, event_name))

        if event_name == "exit":
            self.exit()
        elif event_name == "save":
            pass
        elif event_name == "open":
            pass
        elif event_name in ["files", "annotate", "analyze"]:
            self.switch_to_panel(event_name)
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def exit(self):
        """Close the frame, terminating the application."""

        self.Close(True)

    # -----------------------------------------------------------------------

    def switch_to_panel(self, panel_name):
        """Switch to the expected panel. Hide the current."""

        if panel_name not in self.panels:
            logging.warning("Unknown panel name '{:s}' to switch on."
                            "".format(panel_name))
            return

        logging.debug("Switch to panel '{:s}'.".format(panel_name))
        if self.panels[panel_name].IsShown() is False:
            # hide the current
            for p in self.panels:
                if self.panels[p].IsShown() is True:
                    self.panels[p].HideWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                                                  timeout=400)
            # show the expected
            self.panels[panel_name].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM,
                                                   timeout=400)

        self.Layout()
        self.Refresh()

# ---------------------------------------------------------------------------


class myMenuPanel(wx.Panel):
    """Create my own menu panel with several action buttons.
    It aims to replace the old-style menus.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        # Fix Look&Feel
        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.title_bg_color)
        self.SetMinSize((-1, settings.title_height))

        menu_sizer = wx.BoxSizer(wx.HORIZONTAL)
        st = myTitleText(self, "My App!")
        menu_sizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        menu_sizer.AddStretchSpacer(prop=1)

        # Will switch to the "Files" main panel
        file_btn = myButton(self, "Files", name="files")
        menu_sizer.Add(file_btn, 1, wx.EXPAND, 0)

        # Will switch to the "Annotate" main panel
        annot_btn = myButton(self, "Annotate", name="annotate")
        menu_sizer.Add(annot_btn, 1, wx.EXPAND, 0)

        # Will switch to the "Analyze" main panel
        analyse_btn = myButton(self, "Analyze", name="analyze")
        menu_sizer.Add(analyse_btn, 1, wx.EXPAND, 0)

        menu_sizer.AddStretchSpacer(prop=5)

        # Will open an about message dialog
        about_btn = myButton(self, "About", name="about")
        menu_sizer.Add(about_btn, 0, wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Bind all buttons of this menu
        self.Bind(wx.EVT_BUTTON, self.OnAction, file_btn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, annot_btn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, analyse_btn)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, about_btn)

        self.SetSizer(menu_sizer)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """A button was clicked.
        
        Here we just send the event to the parent.

        """
        logging.debug("A button in the menu was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)

    # -----------------------------------------------------------------------

    def OnAbout(self, event):
        """Display an About Dialog."""

        # Default dialog which will have the default style... so, it won't
        # have our own colors...
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World",
                      wx.OK | wx.ICON_INFORMATION)

# ---------------------------------------------------------------------------


class myActionPanel(wx.Panel):
    """Create my own panel with 3 action buttons: exit, open, save.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetMinSize((-1, 32))

        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.title_bg_color)

        exit_btn = myButton(self, "Exit", name="exit")
        open_btn = myButton(self, "Open", name="open")
        save_btn = myButton(self, "Save", name="save")

        action_sizer = wx.BoxSizer(wx.HORIZONTAL)
        action_sizer.Add(exit_btn, 1, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(open_btn, 1, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        action_sizer.Add(save_btn, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(action_sizer)

        self.Bind(wx.EVT_BUTTON, self.OnAction, exit_btn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, open_btn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, save_btn)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """A button was clicked.

        Here we just send the event to the parent.

        """
        logging.debug("A button in the action panel was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)

# ---------------------------------------------------------------------------


class myContentPanel(wx.Panel):
    """Create my own panel for the content of the frame.

    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        settings = wx.GetApp().settings
        self.SetBackgroundColour(settings.bg_color)

# ---------------------------------------------------------------------------


class myFilePanel(myContentPanel):
    """Create my own panel to work with files.

    """
    def __init__(self, parent):
        myContentPanel.__init__(self, parent)

        settings = wx.GetApp().settings

        st = wx.StaticText(self, wx.ID_ANY, label="Files panel", pos=(25, 25))
        st.SetForegroundColour(settings.fg_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(True)

# ---------------------------------------------------------------------------


class myAnnotatePanel(myContentPanel):
    """Create my own panel to annotate files.

    """
    def __init__(self, parent):

        myContentPanel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(10, 10, 5))
        settings = wx.GetApp().settings

        st = wx.StaticText(self, wx.ID_ANY, label="Annotate panel", pos=(25, 25))
        st.SetForegroundColour(settings.fg_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(False)

# ---------------------------------------------------------------------------


class myAnalyzePanel(myContentPanel):
    """Create my own panel to analyze files.

    """
    def __init__(self, parent):

        myContentPanel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(80, 80, 75))
        settings = wx.GetApp().settings

        st = wx.StaticText(self, wx.ID_ANY, label="Analyze panel", pos=(25, 25))
        st.SetForegroundColour(settings.fg_color)
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(False)

# ---------------------------------------------------------------------------


class myApp(wx.App):
    """Create my own wx application."""

    def __init__(self):

        # Create members
        self.app_dir = os.path.dirname(os.path.realpath(__file__))
        self.splash = None
        self.cfg = WxAppConfig()
        self.settings = None
        self.log_file = None  # os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple.log")
        self.log_level = 10
        self.init_members()

        # Initialize the wx application
        wx.App.__init__(self,
                        redirect=False,
                        filename=self.log_file,
                        useBestVisual=True,
                        clearSigInt=True)

        self.SetAppName(self.cfg.__name__)
        # self.SetAppDisplayName("Displayed application name")

        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(20)
        
        lang = wx.LANGUAGE_DEFAULT
        self.locale = wx.Locale(lang)

    # -----------------------------------------------------------------------

    def init_members(self):

        self.process_command_line_args()

        # Fix the level of messages and where to redirect them (file or std)
        try:
            setup_logging(self.log_level, self.log_file)
        except:
            setup_logging(self.log_level, None)

    # -----------------------------------------------------------------------

    def run(self):
        
        # here we could fix things like:
        #  - is first launch? No? so create config! and/or display a welcome msg!
        #  - fix config dir,
        #  - etc

        if adv_import:
            self.show_splash_screen(self.cfg.splash_delay)
        self.background_initialization()
        self.create_application()   
        self.MainLoop()

    # -----------------------------------------------------------------------

    def process_command_line_args(self):
        """This is an opportunity for users to fix some args."""
        parser = ArgumentParser(
            usage="{:s}".format(os.path.basename(__file__)),
            description="... a program to do something.")
        # add arguments here
        # then parse
        args = parser.parse_args()

        # and do things with arguments

    # -----------------------------------------------------------------------

    def background_initialization(self):
        """Initialize the application. """
        #   here we could read some config file, load some resources, etc
        #   while we show the Splash window
        # for this example, we simply create a dictionary with the config
        # (and sleep some time to simulate we're doing something).
        a = 1.5
        for i in range(1000000):
            a *= float(i)

        self.settings = WxAppSettings()

    # -----------------------------------------------------------------------

    def create_application(self):
        """Create the main frame of the application and show it."""
        frm = myFrame()
        self.SetTopWindow(frm)
        if self.splash:
            self.splash.Close()
        frm.Show()

    # -----------------------------------------------------------------------

    def show_splash_screen(self, delay=10):
        """Create and show the splash image during a delay.

        :param delay: (int) Seconds

        """
        if delay <= 0:
            return

        bitmap = wx.Bitmap('splash.png', wx.BITMAP_TYPE_PNG)
        self.splash = wx.adv.SplashScreen(
          bitmap,
          wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
          delay*100,
          None,
          -1,
          wx.DefaultPosition,
          wx.DefaultSize,
          wx.BORDER_SIMPLE | wx.STAY_ON_TOP)
        self.Yield()

    # -----------------------------------------------------------------------

    def OnExit(self):
        """Optional. Override the already existing method to kill the app.

        This method is invoked when the user:

            - clicks on the [X] button of the frame manager
            - does "ALT-F4" (Windows) or CTRL+X (Unix)

        """
        # do whatever you want here (save session, ...)
        logging.debug("OnExit method invoked.")

        if self.cfg.save_on_exit is True:
            self.settings.save()
    
        # then it will exit. Nothing special to do. Return the exit status.
        return 0

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    # Create and run the application
    app = myApp()
    app.run()

    # do some job after the application is stopped.
    logging.info("Application terminated.")
