#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: type.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import os
import subprocess

# ---------------------------------------------------------------------------


def test_command( command ):
    """
    Test if a command is available.

    """
    try:
        NULL = open(os.devnull, "w")
        subprocess.call([command], stdout=NULL, stderr=subprocess.STDOUT)
    except OSError:
        return False
    return True

# ---------------------------------------------------------------------------


def type_dict(d):
    """
    Return True if d is of type dictionary.

    """
    if type(d) is dict:
        return True
    if "collections." in str(type(d)):
        return True
    return False

# ---------------------------------------------------------------------------


def compare(data1, data2, case_sensitive=False, verbose=False):
    """
    Compare two data of any type.

    """
    if data1 is None or data2 is None:
        if verbose:
            print("FALSE: None instead of data.")
        return False

    if type(data1) is list:
        return compare_lists(data1, data2, case_sensitive, verbose)

    if type_dict(data1) is True:
        return compare_dictionaries(data1, data2, case_sensitive, verbose)

    return compare_others(data1, data2, case_sensitive, verbose)

# ---------------------------------------------------------------------------


def compare_others(data1,data2,case_sensitive=False,verbose=False):
    """
    Compare 2 data of type string or numeric.

    @param data1
    @param data2
    @param case_sensitive (bool) Case sensitive comparison for strings.
    @param verbose (bool) Indicates the comparisons which is False.

    """
    if case_sensitive is True and type(data1) is str:
        return data1.lower() == data2.lower()

    if type(data1) is float:
        if round(data1, 4) != round(data2, 4):
            if verbose is True:
                print("Float values rounded to 4 digits are not equals: {:f} {:f}".format(data1, data2))
            return False

    if data1 != data2 is False:
        if verbose is True:
            print("Not equals: " + str(data1) + " vs " + str(data2))
        return False

    return True

# ---------------------------------------------------------------------------


def compare_lists(list1,list2,case_sensitive=False,verbose=False):
    """
    Compare two lists.

    @param list1 (list) The list to compare.
    @param list2 (list) The list to be compared with.
    @param case_sensitive (bool) Case sensitive comparison for strings.
    @param verbose (bool) Indicates the comparisons which is False.

    """
    if list1 is None or list2 is None:
        if verbose:
            print("FALSE: None instead of lists.")
        return False

    if type(list1) != type(list2) or type(list1) is not list or type(list2) is not list:
        if verbose:
            print("FALSE: Not same types as input (expected two lists).")
        return False

    if not len(list1) == len(list2):
        if verbose:
            print("FALSE: Not the same number of items: {:d} vs {:d}".format(len(list1),len(list2)))
        return False

    lists_are_equal = True
    for item1, item2 in zip(list1, list2):
        if type_dict(item1) is True:
            lists_are_equal = lists_are_equal and compare_dictionaries(item1, item2)
        elif type(item1) is list:
            lists_are_equal = lists_are_equal and compare_lists(item1, item2)
        else:
            lists_are_equal = lists_are_equal and compare_others(item1, item2, case_sensitive, verbose)

    return lists_are_equal

# ---------------------------------------------------------------------------


def compare_dictionaries(dict1,dict2,case_sensitive=False,verbose=False):
    """
    Compare two dictionaries.

    @param dict1 (dict or collection) The dict to compare.
    @param dict2 (dict or collection) The dict to be compared with.
    @param case_sensitive (bool) Case sensitive comparison for strings.
    @param verbose (bool) Indicates the comparisons which is False.

    """
    if dict1 == None or dict2 == None:
        if verbose:
            print("FALSE: None instead of data.")
        return False

    if type_dict(dict1) is not True or type_dict(dict2) is not True:
        if verbose:
            print("FALSE: Not same type as input (expected two dictionaries).")
        return False

    shared_keys = set(dict2.keys()) & set(dict2.keys())

    if not len(shared_keys) == len(dict1.keys()) or not len(shared_keys) == len(dict2.keys()):
        if verbose:
            print("FALSE: not shared keys: " + dict1.keys() + " vs " + dict2.keys())
        return False

    dicts_are_equal = True
    for key in dict1.keys():
        if type_dict(dict1[key]) is True:
            dicts_are_equal = dicts_are_equal and compare_dictionaries(dict1[key],dict2[key])
        elif type(dict1[key]) is list:
            dicts_are_equal = dicts_are_equal and compare_lists(dict1[key],dict2[key])
        else:
            dicts_are_equal = dicts_are_equal and compare_others(dict1[key], dict2[key], case_sensitive, verbose)

    return dicts_are_equal

# ---------------------------------------------------------------------------
