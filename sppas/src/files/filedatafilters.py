# -*- coding: UTF-8 -*-
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

    src.files.filedatafilters.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

from sppas.src.structs.basefilters import sppasBaseFilters
from sppas.src.structs.basefset import sppasBaseSet

from .filedatacompare import sppasPathCompare

# ---------------------------------------------------------------------------


class sppasFileDataFilters(sppasBaseFilters):
    """This class implements the 'SPPAS file data filter system'.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Search in file data.

    Methods to be implemented (and tested):
    =======================================

        - root()       for FileRoot().id, FileRoot().check, FileRoot().expand
        - name()       for FileName().name
        - extension()  for FileName().extension
        - file()       for FileName().check, FileName().lock, ...

    :Example:

        >>> # Search for all checked TextGrid files in a path containing 'corpus'
        >>> f = sppasFileDataFilters(data)
        >>> f.path(contains='corpus') & f.file(check=True) & f.extension(iexact='textgrid')

    """

    def __init__(self, obj):
        """Create a sppasFileDataFilters instance.

        :param obj: (FileData) The object to be filtered.

        """
        super(sppasFileDataFilters, self).__init__(obj)

    # -----------------------------------------------------------------------

    def path(self, **kwargs):
        """Apply functions on all paths of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.path(startswith="c:\\users\myname", not_endswith='a', logic_bool="and")
            >>> f.path(startswith="c:\\users\myname") & f.path(not_endswith='a')
            >>> f.path(startswith="c:\\users\myname") | f.path(startswith="ta")

        :param kwargs: logic_bool/any sppasPathCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasPathCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:

            is_matching = path.match(path_functions, logic_bool)
            if is_matching is True:
                data.append(path, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def root(self, **kwargs):
        """Apply functions on all roots of the object.

        Not Implemented.

        """
        return sppasBaseSet()

    # -----------------------------------------------------------------------

    def name(self, **kwargs):
        """Apply functions on all names of the files of the object.

        Not Implemented.

        """
        return sppasBaseSet()

    # -----------------------------------------------------------------------

    def extension(self, **kwargs):
        """Apply functions on all extensions of the files of the object.

        Not Implemented.

        """
        return sppasBaseSet()

    # -----------------------------------------------------------------------

    def file(self, **kwargs):
        """Apply functions on all file properties of the object.

        Not Implemented.

        """
        return sppasBaseSet()

