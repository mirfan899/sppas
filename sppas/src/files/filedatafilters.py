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
from operator import contains

from sppas.src.files.filedata import FileRoot
from sppas.src.structs.basefilters import sppasBaseFilters
from sppas.src.structs.basefset import sppasBaseSet

from .filedatacompare import sppasPathCompare, sppasRootCompare, sppasFileNameCompare, sppasFileNameExtensionCompare, \
    sppasFileNamePropertiesCompare, sppasReferenceCompare, sppasAttValueCompare


# ---------------------------------------------------------------------------


class sppasFileDataFilters(sppasBaseFilters):
    """This class implements the 'SPPAS file data filter system'.

    :author:       Brigitte Bigi
    :author:       Barthélémy Drabczuk
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2019  Brigitte Bigi

    Search in file data.

    :Example:

        >>> # Search for all checked TextGrid files in a path containing 'corpus'
        >>> f = sppasFileDataFilters(data)
        >>> f.path(contains='corpus') & f.file(state=True) & f.extension(iexact='textgrid')

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
                # append all files of the path
                for fr in path:
                    for fn in fr:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def root(self, **kwargs):
        """Apply functions on all roots of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.root(startswith="myfile", not_endswith='a', logic_bool="and")
            >>> f.root(startswith="myfile") & f.root(not_endswith='a')
            >>> f.root(startswith="myfile") | f.root(startswith="ta")

        :param kwargs: logic_bool/any sppasRootCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasRootCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            for root in path:
                is_matching = root.match(path_functions, logic_bool)
                if is_matching is True:
                    # append all files of the path
                    for fn in root:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def name(self, **kwargs):
        """Apply functions on all names of the files of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.name(iexact="myfile-phon", not_startswith='a', logic_bool="and")
            >>> f.name(iexact="myfile-phon") & f.name(not_startswith='a')
            >>> f.name(iexact="myfile-phon") | f.name(startswith="ta")

        :param kwargs: logic_bool/any sppasFileNameCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasFileNameCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            # append all files of the path
            for fr in path:
                for fn in fr:
                    is_matching = fn.match(path_functions, logic_bool)
                    if is_matching is True:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def extension(self, **kwargs):
        """Apply functions on all extensions of the files of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.extension(startswith=".TEXT", not_endswith='a', logic_bool="and")
            >>> f.extension(startswith=".TEXT") & f.extension(not_endswith='a')
            >>> f.extension(startswith=".TEXT") | f.extension(startswith="ta")

        :param kwargs: logic_bool/any sppasFileNameExtensionCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasFileNameExtensionCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:

                # append all files of the path
                for fr in path:
                    for fn in fr:
                        is_matching = fn.match(path_functions, logic_bool)
                        if is_matching is True:
                            data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def fprop(self, **kwargs):
        """Apply functions on all file properties of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.file(lock='true')

        :param kwargs: logic_bool/any sppasFileNamePropertiesCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasFileNamePropertiesCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            # append all files of the path
            for fr in path:
                for fn in fr:
                    is_matching = fn.match(path_functions, logic_bool)
                    if is_matching is True:
                        data.append(fn, path_fct_values)

        return data

    # -----------------------------------------------------------------------

    def ref(self, **kwargs):
        """Apply functions on all file properties of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

            >>> f.ref(startswith="toto", not_endswith="tutu", logic_bool="and")
            >>> f.ref(startswith="toto") & f.ref(not_endswith="tutu")
            >>> f.ref(startswith="toto") | f.ref(startswith="tutu")

        :param kwargs: logic_bool/any sppasFileNamePropertiesCompare() method.
        :returns: (sppasDataSet)

        """
        comparator = sppasReferenceCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        path_fct_values = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        path_functions = sppasBaseFilters.fix_functions(comparator, **kwargs)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            # append all files of the path
            for fr in path:
                for ref in fr.categories:
                    is_matching = ref.match(path_functions, logic_bool)
                    if is_matching is True:
                        data.append(ref, path_fct_values)

        return data


    # -----------------------------------------------------------------------

    def att(self, **kwargs):
        """Apply functions on all file properties of the object.

        Each argument is made of a function name and its expected value.
        Each function can be prefixed with 'not_', like in the next example.

        :Example:

        >>> f.ref(startswith="toto", not_endswith="tutu", logic_bool="and")
        >>> f.ref(startswith="toto") & f.ref(not_endswith="tutu")
        >>> f.ref(startswith="toto") | f.ref(startswith="tutu")

        :param kwargs: logic_bool/any sppasFileNamePropertiesCompare() method.
        :returns: (sppasDataSet)
        """
        def exctract_function_info(functions):
            functions_att = list()
            functions_name = list()
            functions_value = list()
            for function in functions:
                function_value = function[function.rindex('='):]
                function = function[:function.rindex('=')]
                function_name = function[function.rindex('_') + 1:]
                function_att = function[:function.rindex('_')]
                functions_att.append(function_att)
                functions_name.append(function_name)
                functions_value.append(function_value)
            return functions_att, functions_name, functions_value

        # -----------------------------------------------------------------------

        comparator = sppasAttValueCompare()

        # extract the information from the arguments
        sppasBaseFilters.test_args(comparator, **kwargs)
        logic_bool = sppasBaseFilters.fix_logic_bool(**kwargs)
        ref_function_value = sppasBaseFilters.fix_function_values(comparator, **kwargs)
        ref_function = sppasBaseFilters.fix_functions(comparator, **kwargs)
        function_atts, function_names, function_values = exctract_function_info(ref_function_value)

        # the set of results
        data = sppasBaseSet()

        # search for the data to be returned:
        for path in self.obj:
            # append all files of the path
            for fr in path:
                for ref in fr.categories:
                    for key in function_atts:
                        is_matching = ref[key].match(function_names, logic_bool)
                        print(is_matching)
                        if is_matching is True:
                            data.append(ref, function_values)

        return data

# ---------------------------------------------------------------------------
