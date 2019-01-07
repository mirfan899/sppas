import os
import platform
from datetime import date

try:
    import wx
    IMPORT_WX = True
except:
    IMPORT_WX = False

from sppas.src.utils.datatype import sppasTime
from sppas.src.config import paths
from sppas.src.config import sg

# ---------------------------------------------------------------------------


class sppasLogFile(object):
    """Utility file name manager for logs.

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

        self.__current = 1
        while os.path.exists(self.get_filename()) is True:
            self.__current += 1

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

    @staticmethod
    def get_header():
        """Return a string with an header for logs."""
        header = "-"*78
        header += "\n\n"
        header += " {:s} {:s}".format(sg.__name__, sg.__version__)
        header += "\n"
        header += " {:s}".format(sppasTime().now)
        header += "\n"
        header += " {:s}".format(platform.platform())
        header += "\n"
        header += " python {:s}".format(platform.python_version())
        if IMPORT_WX:
            header += "\n"
            header += " wxpython {:s}".format(wx.version())
        header += "\n\n"
        header += "-"*78
        header += "\n\n"
        return header
