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

    src.anndata.filter.filters.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Search in tiers.

"""
from ..anndataexc import AnnDataValueError
from ..anndataexc import AnnDataKeyError
from ..anndataexc import AnnDataTypeError
from ..annlabel.tagcompare import sppasTagCompare
from ..annlocation.durationcompare import sppasDurationCompare

# ---------------------------------------------------------------------------


class sppasSetFilter(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      The data that are the result of the filter system.

    """
    def __init__(self):
        self._data_set = dict()

    # -----------------------------------------------------------------------

    def get_value(self, ann):
        return self._data_set.get(ann, None)

    # -----------------------------------------------------------------------

    def append(self, ann, value):
        """ Append an annotation in the data set, with the given value.

        :param ann: (sppasAnnotation)
        :param value: (list)

        """
        if value is None:
            raise AnnDataTypeError(value, "list")
        if isinstance(value, list) is False:
            raise AnnDataTypeError(value, "list")

        if ann not in self._data_set:
            self._data_set[ann] = value
        else:
            old_value_list = self._data_set[ann]
            self._data_set[ann] = list(set(old_value_list + value))

    # -----------------------------------------------------------------------

    def copy(self):
        """ return a deep copy of self. """

        d = sppasSetFilter()
        for ann, value in self._data_set.items():
            d.append(ann, value)
        return d

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for ann in list(self._data_set.keys()):
            yield ann

    def __len__(self):
        return len(self._data_set)

    # -----------------------------------------------------------------------
    # Logical connectors
    # -----------------------------------------------------------------------

    def __or__(self, other):

        d = self.copy()
        for ann in other:
            d.append(ann, other.get_value(ann))

        return d

    # -----------------------------------------------------------------------

    def __and__(self, other):

        d = sppasSetFilter()
        for ann in self:
            if ann in other:
                d.append(ann, self.get_value(ann))
                d.append(ann, other.get_value(ann))

        return d

# ---------------------------------------------------------------------------


class sppasFilters(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS annotated data filter system.

    To create a filter:

        >>> f = sppasFilters(tier)

    To apply a filter...

    Example1 in the requests: extract silences more than 200ms

        >>> f.tag(exact=u("#")) and f.duration(gt=0.2)

    """
    def __init__(self, tier):
        """ Create a sppasFilters instance. """

        self.tier = tier

    # -----------------------------------------------------------------------

    def tag(self, **kwargs):
        """ Apply functions on all tags of all labels of annotations of a tier.

        Each argument is made of a function name and its expected value.

        The following returns the annotations with at least a label with a tag
        starting by "pa" and ending by "a" like "pa", "papa", "pasta", etc:

            >>> f.tag(startswith="pa", endswith='a')

        It's equivalent to write:

            >>> f.tag(startswith="pa", endswith='a', logic_gate="and")

        The classical "and" and "or" logic gates are accepted; "and" is the
        default one. It defines whether all the functions must be True ("and")
        or any of them ("or").

        The result is the same, but two times faster, compared to use this:

            >>> f.tag(startswith="pa") and f.tag(endswith='a')

        Return the list of sppasAnnotation instances for which at least one
        label is True for all the given functions. Each function can be
        prefixed with "not_", like:

            >>> f.tag(startswith="pa", not_endswith='a', logic_gate="and")
            >>> f.tag(startswith="pa") and f.tag(not_endswith='a')

        :param kwargs: logic_gate/any sppasTagCompare() method.
        :returns: (sppasSetFilter)

        """
        comparator = sppasTagCompare()

        # extract the information from the arguments
        sppasFilters.__test_args(comparator, **kwargs)
        logic_gate = sppasFilters.__fix_logic_gate(**kwargs)
        tag_fct_values = sppasFilters.__fix_function_values(comparator, **kwargs)
        tag_functions = sppasFilters.__fix_functions(comparator, **kwargs)

        data = sppasSetFilter()

        # search the annotations to be returned:
        for annotation in self.tier:

            # any label can match
            for label in annotation.get_labels():

                is_matching = label.match(tag_functions, logic_gate)
                # no need to test the next labels if the current one is matching.
                if is_matching is True:
                    data.append(annotation, tag_fct_values)
                    break

        return data

    # -----------------------------------------------------------------------

    def duration(self, **kwargs):
        """ Apply functions on durations of all locations of annotations of a tier.

        :param kwargs: logic_gate/any sppasTagCompare() method.
        :returns: (sppasSetFilter)

        """
        comparator = sppasDurationCompare()

        # extract the information from the arguments
        sppasFilters.__test_args(comparator, **kwargs)
        logic_gate = sppasFilters.__fix_logic_gate(**kwargs)
        dur_fct_values = sppasFilters.__fix_function_values(comparator, **kwargs)
        dur_functions = sppasFilters.__fix_functions(comparator, **kwargs)

        data = sppasSetFilter()

        # search the annotations to be returned:
        for annotation in self.tier:

            location = annotation.get_location()
            is_matching = False  # location.match(dur_functions, logic_gate)
            if is_matching is True:
                data.append(annotation, dur_fct_values)

        return data

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    @staticmethod
    def __test_args(comparator, **kwargs):
        """ Raise an exception if any of the args is not correct. """

        names = ["logic_gate"] + comparator.get_function_names()
        for func_name, value in kwargs.items():
            if func_name not in names:
                raise AnnDataKeyError("kwargs function name", func_name)

    # -----------------------------------------------------------------------

    @staticmethod
    def __fix_logic_gate(**kwargs):
        """ Return the value of a logic gate. """

        for func_name, value in kwargs.items():
            if func_name == "logic_gate":
                if value not in ['and', 'or']:
                    raise AnnDataValueError(value, "logic gate")
                return value
        return "and"

    # -----------------------------------------------------------------------

    @staticmethod
    def __fix_function_values(comparator, **kwargs):
        """ Return the list of function names and the expected value. """

        tag_fct_values = list()
        for func_name, value in kwargs.items():
            if func_name in comparator.get_function_names():
                tag_fct_values.append("{:s} = {!s:s}".format(func_name, value))

        return tag_fct_values

    # -----------------------------------------------------------------------

    @staticmethod
    def __fix_functions(comparator, **kwargs):
        """ Parse the arguments to get the list of function/value/complement. """

        tag_functions = list()
        for func_name, value in kwargs.items():
            if func_name in comparator.get_function_names():
                logical_not = False
                if func_name.startswith("not_"):
                    logical_not = True
                    func_name = func_name[4:]

                tag_functions.append((comparator.get(func_name),
                                      value,
                                      logical_not))

        return tag_functions
