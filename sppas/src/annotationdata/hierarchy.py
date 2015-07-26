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
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2015-2015  Brigitte Bigi
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
# File: hierarchy.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


class Hierarchy(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Generic representation of a hierarchy between tiers.

    Three types of hierarchy:
    - TimeAssociation:
        the points of a child tier are all equals
        to the points of a reference tier.
    - TimeAlignment:
        the points of a child tier are all included
        in the points of a reference tier.

    Examples:
    Lemmas are child of Tokens,      with TimeAssociation.
    Tokens are child of Phonemes,    with TimeAlignment.
    But no hierarchy between Tokens and Phonemes!

    A child tier can have only one reference tier.
    Of course, a reference tier can have children...
    like Phonemes in the previous example.

    """
    hierarchy_types = {"TimeAssociation", "TimeAlignment"}

    def __init__(self):
        """
        Creates a new Hierarchy instance.

        """
        self.__hierarchies = {}
        for type in Hierarchy.hierarchy_types:
            self.__hierarchies[type] = set()

    # End __init__
    # ------------------------------------------------------------------------------------

    def addLink(self, type, formerArg, latterArg):
        if type not in Hierarchy.hierarchy_types:
            raise Exception("unsupported Link type: %s" % type)

        # Check for TimeAlignment
        if type is 'TimeAlignment' and not formerArg.IsSuperset(latterArg):
            raise Exception(
                "Can't align values, %s is not a superset of %s" % (
                    formerArg.GetName(),
                    latterArg.GetName()))

        # Check for TimeAssociation
        if type is 'TimeAssociation' and not (
            formerArg.IsSuperset(latterArg) and
            latterArg.IsSuperset(formerArg)
        ):
            raise Exception(
                "Can't associate values, "
                "%s and %s are not supersets of each other" % (
                    formerArg.GetName(),
                    latterArg.GetName()))

        link = (formerArg, latterArg)

        self.__hierarchies[type].add(link)

    # End addLink
    # ------------------------------------------------------------------------------------

    def removeLink(self, type, formerArg, latterArg):
        if type not in Hierarchy.hierarchy_types:
            raise Exception("unsupported Link type: %s" % type)

        link = (formerArg, latterArg)

        self.__hierarchies[type].remove(link)

    # End removeLink
    # ------------------------------------------------------------------------------------

    def removeTier(self, tier):
        """
        Remove all references to a tier inside all hierarchies
        """
        for hierarchy in self.__hierarchies.values():
            for link in hierarchy:
                if tier in link:
                    hierarchy.remove(link)

    # End removeTier
    # ------------------------------------------------------------------------------------

    def getHierarchy(self, type):
        return self.__hierarchies[type]

    # End getHierarchy
    # ------------------------------------------------------------------------------------

    def getParent(self, tier):
        for key in self.__hierarchies:
            for (former, latter) in self.__hierarchies[key]:
                if latter is tier:
                    return former
        return None

    # End getParent
    # ------------------------------------------------------------------------------------
