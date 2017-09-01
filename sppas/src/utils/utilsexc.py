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

    src.utils.utilsexc.py
    ~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for utils package.

"""
from .maketext import translate
t = translate("utils")

# -----------------------------------------------------------------------

NO_DIR_ERROR = ":ERROR 1210: "

# -----------------------------------------------------------------------


class NoDirectoryError(IOError):
    """ :ERROR 1210: The directory {dirname} does not exist. """

    def __init__(self, dirname):
        self.parameter = NO_DIR_ERROR + (t.gettext(NO_DIR_ERROR)).format(dirname=dirname)

    def __str__(self):
        return repr(self.parameter)
