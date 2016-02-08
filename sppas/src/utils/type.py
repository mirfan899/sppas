#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr00800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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

def compare_lists(list1,list2,case_sensitive=False,verbose=False):
    """
    Compare two lists.

    @param list1 (list) The list to compare.
    @param list2 (list) The list to be compared with.
    @param case_sensitive (bool) Case sensitive comparison for strings.
    @param verbose (bool) Indicates the comparisons which is False.

    """
    if list1 == None or list2 == None:
        if verbose: print "FALSE: None instead of lists."
        return False

    if type(list1) != type(list2) or type(list1) is not list or type(list2) is not list:
        if verbose: print "FALSE: Not same types as input (expected two lists)."
        return False

    if not len(list1) == len(list2):
        if verbose: print "FALSE: Not the same number of items.",len(list1),len(list2)
        return False

    lists_are_equal = True
    for item1,item2 in zip(list1,list2):
        if type_dict(item1) is True:
            lists_are_equal = lists_are_equal and compare_dictionaries(item1,item2)
        elif type(item1) is list:
            lists_are_equal = lists_are_equal and compare_lists(item1,item2)
        elif type(item1) is str:
            lists_are_equal = lists_are_equal and (item1.lower() == item2.lower())
            if verbose and lists_are_equal is False:
                print " ... FALSE: ",item1.lower(),item2.lower()
        else:
            lists_are_equal = lists_are_equal and (item1 == item2)
            if verbose and lists_are_equal is False:
                print " ... FALSE: ",item1,item2

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
        if verbose: print "FALSE: None instead of data."
        return False

    if type(dict1) != type(dict2) or type_dict(dict1) is not True or type_dict(dict2) is not True:
        if verbose: print "FALSE: Not same type as input."
        return False

    shared_keys = set(dict2.keys()) & set(dict2.keys())

    if not len(shared_keys) == len(dict1.keys()) or not len(shared_keys) == len(dict2.keys()):
        print "FALSE: not shared keys."
        return False

    dicts_are_equal = True
    for key in dict1.keys():
        if type_dict(dict1[key]) is True:
            dicts_are_equal = dicts_are_equal and compare_dictionaries(dict1[key],dict2[key])
        elif type(dict1[key]) is list:
            dicts_are_equal = dicts_are_equal and compare_lists(dict1[key],dict2[key])
        elif type(dict1[key]) is str:
            dicts_are_equal = dicts_are_equal and (dict1[key].lower() == dict2[key].lower())
            if verbose and dicts_are_equal is False:
                print " ... FALSE: ",dict1[key].lower(),dict2[key].lower()
        else:
            dicts_are_equal = dicts_are_equal and (dict1[key] == dict2[key])
            if verbose and dicts_are_equal is False:
                print " ... FALSE: ",dict1[key],dict2[key]

    return dicts_are_equal

# ---------------------------------------------------------------------------
