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

    config.settings.py
    ~~~~~~~~~~~~~~~~~~

    Base classes to manage any kind of settings, represented in a dictionary.

    :Example:

        >>>with sppasBaseSettings() as settings:
        >>>    settings.newKey = 'myNewValue'
        >>>    print(settings.newKey)

"""
import json

# ---------------------------------------------------------------------------


class sppasBaseSettings(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Representation of a dictionary of settings.

    """
    def __init__(self):
        self.__dict__ = dict()  # load(open(self._config_location))

    def __enter__(self):
        return self

    # def __iter__(self):
    #     return self.__dict__.__iter__()
    #
    # def __getitem__(self, key):
    #     return self.__dict__[key]
    #
    # def __len__(self):
    #     return len(self)

    def __exit__(self, exc_type, exc_value, traceback):
        pass
        # here we could write things on the console, or anything else!
        # json.dump(self.__dict__, open(self._config_location, 'w'))

# ---------------------------------------------------------------------------


class sppasBaseModifiableSettings(sppasBaseSettings):
    """ A dictionary of settings stored in a file.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    The configuration file is loaded when init and saved when exit.

    """
    def __init__(self, _config_location):
        sppasBaseSettings.__init__(self)
        self.__dict__ = json.load(open(_config_location))
        self._config_location = _config_location

    def __exit__(self, exc_type, exc_value, traceback):
        json.dump(self.__dict__, open(self._config_location, 'w'))
