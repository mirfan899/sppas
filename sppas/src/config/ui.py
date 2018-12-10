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

from sppas.src.config import sg
from sppas.src.config import sppasBaseSettings

# ---------------------------------------------------------------------------


class sppasAppConfig(sppasBaseSettings):
    """User Interface global configuration.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Config is represented in the dictionary of the class.
    Inherited of sppasBaseSettings which allows to load and save settings.

    """

    def __init__(self):
        """Create the dictionary of key/value configuration."""
        super(sppasAppConfig, self).__init__()

        self.__dict__ = dict(
            name=sg.__name__ + " " + sg.__version__,
            log_level=15,
            quiet_log_level=30,
            log_file=None,
            splash_delay=3,
        )

    # -----------------------------------------------------------------------

    def set(self, key, value):
        """Set a new value to a key."""
        setattr(self, key, value)
