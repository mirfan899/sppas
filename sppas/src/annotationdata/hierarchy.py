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
# File: hierarchy.py
# ----------------------------------------------------------------------------


class Hierarchy(object):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    @summary:      Generic representation of a hierarchy between tiers.

    Two types of hierarchy are considered:
      - TimeAssociation:
        the points of a child tier are all equals to the points of
        a reference tier, as for example:

            parent:  Tokens     | l' |  âne  | est |  là   |
            child:   Lemmas     | le |  âne  | être |  là  |

      - TimeAlignment:
        the points of a child tier are all included in the set of
        points of a reference tier, as for example:

            parent: Phonemes    | l  | a | n |  e  | l | a |
            child:  Tokens      | l' |  âne  | est |  là   |

            parent: Phonemes    | l  | a | n |  e  | l | a |
            child:  Syllables   |   l.a  |  n.e    |   l.a |

    (Notice that there's no hierarchy link between Tokens and Syllables!)
    (Notice that "Phonemes" is the grand-parent of lemmas!)

    A child can have ONLY ONE parent!
    A parent can have as many children as wanted.
    A hierarchy is obviously a tree, not a graph.

    """
    types = {"TimeAssociation", "TimeAlignment"}

    def __init__(self, ):
        """
        Creates a new Hierarchy instance.

        """
        self.__hierarchy = {}  # key = child tier ; value = (parent, link)

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_parent(self, child_tier):
        """
        Return the reference tier for a given child tier.

        :param child_tier: (Tier) The child tier to found

        """
        if child_tier not in self.__hierarchy.keys():
            return None
        parent, link = self.__hierarchy[child_tier]
        return parent

    # -----------------------------------------------------------------------

    def get_hierarchy_type(self, child_tier):
        """
        Return the hierarchy type between a child tier and its parent.

        :return (str) one of the hierarchy type

        """
        if child_tier not in self.__hierarchy.keys():
            return ""
        parent, link = self.__hierarchy[child_tier]
        return link

    # -----------------------------------------------------------------------

    def get_children(self, parent_tier, link_type=None):
        """
        Return the list of children of a tier, for a given type.

        :param parent_tier: (Tier) The child tier to found
        :param link_type: (str) The type of hierarchy
        :return: List of tiers

        """
        if link_type is not None:
            if link_type not in Hierarchy.types:
                raise TypeError("Unsupported hierarchy type: %s" % link_type)

        children = []
        for child_tier in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child_tier]
            if parent is parent_tier:
                if link_type is None or link_type == link:
                    children.append(child_tier)

        return children

    # -----------------------------------------------------------------------

    def get_ancestors(self, child_tier):
        """
        Return all the direct ancestors of a tier (parent, grand-parent, grand-grand-parent...).

        :param child_tier:
        :return: List of tiers

        """
        if child_tier not in self.__hierarchy.keys():
            return []

        ancestors = []
        parent = self.get_parent(child_tier)
        while parent is not None:
            ancestors.append(parent)
            parent = self.get_parent(parent)

        return ancestors

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def add_link(self, link_type, parent_tier, child_tier):
        """
        Add a hierarchy link between 2 tiers.

        :param link_type: (constant) is one of the hierarchy types
        :param parent_tier: (Tier) The reference tier
        :param child_tier: (Tier) The child tier to be linked to reftier

        """
        if link_type not in Hierarchy.types:
            raise TypeError("Unsupported link type: %s" % link_type)

        # A child has only one parent
        if child_tier in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child_tier]
            raise Exception("%s has already a parent in the hierarchy."
                            "Its parent is %s, with link of type %s." %
                            (child_tier.GetName(), parent.Get_Name(), link))

        # A tier can't be its own child/parent
        if parent_tier == child_tier:
            raise Exception("A tier can't be whether the parent and its own child.")

        # Check for TimeAlignment
        if link_type == "TimeAlignment":
            if parent_tier.IsSuperset(child_tier) is False:
                raise Exception(
                    "Can't align values, %s is not a superset of %s" % (
                        parent_tier.GetName(),
                        child_tier.GetName()))

        # Check for TimeAssociation
        if link_type == "TimeAssociation":
            if parent_tier.IsSuperset(child_tier) is False and child_tier.IsSuperset(parent_tier) is False:
                raise Exception(
                    "Can't associate values, "
                    "%s and %s are not supersets of each other" % (
                        parent_tier.GetName(),
                        child_tier.GetName()))

        # No circular hierarchy allowed.
        ancestors = self.get_ancestors(parent_tier)
        family = []
        for ancestor in ancestors:
            uncles = self.get_children(ancestor)
            family.extend(uncles)
        family.extend(ancestors)
        if child_tier in family:
            raise Exception("%s is an ancestor of %s in the hierarchy." %
                            (child_tier.GetName(), parent_tier.Get_Name()))

        # OK!
        self.__hierarchy[child_tier] = (parent_tier, link_type)

    # -----------------------------------------------------------------------

    def remove_child(self, child_tier):
        """
        Remove a hierarchy link between a parent and a child.

        :param child_tier: (Tier) The tier linked to a reference

        """
        if child_tier in self.__hierarchy.keys():
            del self.__hierarchies[child_tier]

    # -----------------------------------------------------------------------

    def remove_parent(self, parent_tier):
        """
        Remove all hierarchy links between a parent and its children.

        :param parent_tier: (Tier) The reference tier

        """
        to_remove = []
        for child_tier in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child_tier]
            if parent is parent_tier:
                to_remove.append(child_tier)

        for child_tier in to_remove:
            del self.__hierarchy[child_tier]

    # ------------------------------------------------------------------------------------

    def remove_tier(self, tier):
        """
        Remove all occurrences of a tier inside the hierarchy.

        :param tier: (Tier) The tier to remove as parent or child.

        """
        to_remove = []
        for child in self.__hierarchy.keys():
            parent, link = self.__hierarchy[child]
            if parent is tier or child is tier:
                to_remove.append(child)

        for child_tier in to_remove:
            del self.__hierarchy[child_tier]

    # -----------------------------------------------------------------------
    # Automatic hierarchy
    # -----------------------------------------------------------------------

    @staticmethod
    def infer_hierarchy_type(tier1, tier2):
        """
        Test if tier1 can be a reference tier for tier2.

        :return type (constant): One of hierarchy types or an empty string

        """
        if tier1.IsSuperset(tier2) is False:
            return ""

        if tier2.IsSuperset(tier1) is True:
            return "TimeAssociation"

        return "TimeAlignment"

    # -----------------------------------------------------------------------
