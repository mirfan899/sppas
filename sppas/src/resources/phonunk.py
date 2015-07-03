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
# File: phonunk.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------

import sys
import os
from os.path import *

import re


# ----------------------------------------------------------------------------

class DAG:
    """
    Direct Acyclic Graph.

    Implementation from: http://www.python.org/doc/essays/graphs/

    """

    def __init__(self):
        """
        Create a new DAG instance.

        dictgraph (Dictionary) represents the graph as for example:
            - A -> B
            - A -> C
            - B -> C
            - B -> D
            - C -> D
        is represented as:
        dictgraph = {'A': ['B', 'C'], 'B': ['C', 'D'], 'C': ['D'],}

        """
        self.__graph = {}

    # End __init__
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------

    def __Get(self):
        return self.__graph

    def __Set(self, dag):
        self.__graph = dag

    Graph = property(__Get, __Set)

    # -----------------------------------------------------------------------


    def add_node(self, node):
        """ Add a new node (not added if already in the DAG). """
        if node not in self.__graph.keys():
            self.__graph[node] = list()

    def add_edge(self, src, dst):
        """ Add a new edge to a node. """
        # TODO. Must check if no cycle...
        self.__graph[src].append(dst)

    def remove_node(self, node):
        """ Remove a node. """
        if node in self.__graph.keys():
            del self.__graph[node]

    def remove_edge(self, src, dst):
        self.__graph[src].pop(dst)

    # -----------------------------------------------------------------------


    def find_path(self, start, end, path=[]):
        """
        Determine a path between two nodes.

        It takes a graph and the start and end nodes as arguments. It
        will return a list of nodes (including the start and end nodes)
        comprising the path. When no path can be found, it returns None.
        Note: The same node will not occur more than once on the path
        returned (i.e. it won't contain cycles).

            >>> find_path(graph, 'A', 'C')
            >>> ['A', 'B', 'C'']
        """
        path = path + [start]
        if start == end:
            return [path]
        if not self.__graph.has_key(start):
            return []

        for node in self.__graph[start]:
            if node not in path:
                newpath = self.find_path(node, end, path)
                if len(newpath)>0:
                    return newpath
        return []

    # End find_path
    # -----------------------------------------------------------------------


    def find_all_paths(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        if not self.__graph.has_key(start):
            return []

        paths = []
        for node in self.__graph[start]:
            if node not in path:
                newpaths = self.find_all_paths(node, end, path)
                for newpath in newpaths:
                    paths.append(newpath)

        return paths

    # End find_all_path
    # -----------------------------------------------------------------------


    def find_shortest_path(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not self.__graph.has_key(start):
            return None

        shortest = None
        for node in self.__graph[start]:
            if node not in path:
                newpath = self.find_shortest_path(node, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath

        return shortest

    # End find_shortest_path
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __repr__(self):
        print "Number of nodes:", len(self.__graph.keys())
        for i in self.__graph.keys():
            if  self.__graph[i]:
                print "  Node ",i," has edge to --> ", self.__graph[i]
            else:
                print "  Node ",i," has no edge "

    def __len__(self):
        return len(self.__graph)

    # -----------------------------------------------------------------------

# End DAG
# ----------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Class PhonUnk
# ---------------------------------------------------------------------------

class PhonUnk:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi((AATT))lpl-aix.fr
    @license: GPL
    @summary: Perform a G2P conversion for unknown entries.

    Phonetization, also called grapheme-phoneme conversion, is the process of
    representing sounds with phonetic signs. This class implements a
    language-independent algorithm to phonetize unknown words.
    Our system is based on the idea that given enough examples it should be
    possible to predict the pronunciation of unseen words purely by analogy.

    At this stage, it consists in exploring the unknown word from left to
    right and to find the longest strings in the dictionary.
    Since this algorithm uses the dictionary, the quality of
    such a phonetization will depend on this resource.

    For details, see the following reference:

        Brigitte Bigi (2013).
        A phonetization approach for the forced-alignment task,
        3rd Less-Resourced Languages workshop, 6th Language & Technology
        Conference, Poznan (Poland).

    """

    def __init__(self, prondict):
        """
        Create a new PhonUnk instance.

        @param prondict is a python dictionary with a set of couples:
            token=key, phonetization=value.
        """

        self.prondict = prondict
        self.__variants = 4

    # End __init__
    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------


    def set_variants(self, v):
        """
        Fix the variants option value.

        @param v (int) fix the maximum number of variants. If v is set to 0,
            all variants will be returned.

        """
        self.__variants = v


    # End set_variants
    # -----------------------------------------------------------------------


    def get_variants(self):
        """
        Get the variants option value.

        """
        return self.__variants

    # End get_variants
    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # DAG
    # -----------------------------------------------------------------------


    def pron2DAG(self, pron):
        """
        Convert a phonetization into a DaG.

        @param pron

        """
        tabpron = pron.split()

        graph     = DAG()       # the Graph, used to store segments and to get all paths
        prongraph = list()      # the pronunciation of each segment
        variants  = None

        # A Start node (required if the 1st segment has variants)
        graph.add_node( 0 )
        prongraph.append( "start" )

        # Init values
        prec  = 1
        precv = 1

        # Get all longest-segments of a token
        for i in range(len(tabpron)):

            variants = tabpron[i].split('|')
            # Get all variants of this part-of-token
            for v in range(len(variants)):

                # store variants
                prongraph.append( variants[v] )
                if i < len(tabpron):
                    graph.add_node( prec+v )
                # add these variants to the precedings segments
                for k in range(prec-precv, prec):
                    graph.add_edge(k,prec+v)

            prec  = prec + len(variants)
            precv = len(variants)

        # add a "End" node
        prongraph.append( "end" )
        graph.add_node( prec )
        for k in range(prec-precv, prec):
            graph.add_edge(k,prec)

        return (graph,prongraph)

    # -----------------------------------------------------------------------

    def DAG2phon(self, graph, prongraph):
        """
        Convert a DAG into a dictionary including all pronunciation variants.

        """
        pathslist = graph.find_all_paths( 0, len(graph)-1 )
        pron = {}
        for variant in pathslist:
            p = ""
            for i in variant[1:len(variant)-1]: # do not include Start and End nodes
                p = p + "." + prongraph[i]
            p = re.sub('^.', "", p)
            pron[p] = len(p.split('.'))

        return pron


    def decompose(self, pron1, pron2):
        """
        Create a phonetization from a string as follow:

            - input example: p1 p2|x2 p3|x3
            - output example: p1.p2.p3|p1.p2.x3|p1.x2.p3|p1.x2.x3

        The input string is converted into a DAG, then output corresponds
        to all paths.

        """
        if len(pron1) == 0 and len(pron2) == 0:
            return ""
        tabpron1 = pron1.split()
        tabpron2 = pron2.split()

        # Only one phoneme in the phonetization: nothing to do!
        if len(tabpron1) < 2:
            return pron1
        if len(tabpron2) < 2:
            return pron2

        # Complex phonetization: converted into a DAG
        (graph1,prongraph1) = self.pron2DAG( pron1 )
        (graph2,prongraph2) = self.pron2DAG( pron2 )

        # Create all pronunciations from the DAG
        pron1 = self.DAG2phon(graph1,prongraph1)
        pron2 = self.DAG2phon(graph2,prongraph2)

        # Merge =======>  TODO: MERGE DAGs instead of merging prons
        pron = dict(pron1.items() + pron2.items())

        # Output selection

        # Return all variants
        if self.__variants == 0:
            return "|".join(pron.keys())

        # Choose the shorter variants
        if self.__variants == 1:
            return min(pron.items(), key=lambda x: x[1])[0]

        # Other number of variants: choose shorters
        l = sorted(pron.items(), key=lambda x: x[1])[:self.__variants]
        return "|".join(zip(*l)[0])

    # -----------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------


    def get_phon(self,entry):
        """
        Return the phonetization of an unknown entry.

        @param entry is the string to phonetize
        @return a string with the proposed phonetization
        @raise Exception if the word can NOT be phonetized

        """
        __str = re.sub("[\s]+", " ", entry)
        __str = re.sub("-$", "", __str)  # rustine
        __str = re.sub("'$", "", __str)  # rustine

        # Find all pronunciations of segments with a longest matching algo.
        # if entry contains separators:
        #  1. phonetize each part independently and
        #  2. separate segments with a space.
        __tabstr = re.split(u"[-'_\s]",__str)
        pronlr = ""
        for s in __tabstr:
            pronlr = pronlr + " " + self.__recurslr(s)
        pronrl = ""
        for s in __tabstr:
            pronrl = pronrl + " " + self.__recursrl(s)

        # Create the output
        pron = self.decompose( pronlr.strip(), pronrl.strip() )

        if len(pron.strip())>0:
            return pron

        raise Exception('Unable to phonetize the unknown token: '+entry)

    # End get_phon
    # ------------------------------------------------------------------


    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __longestlr(self,entry):
        """
        Select the longest phonetization of an entry, from the end.
        """
        i = len(entry)
        while (i>0):
            # Find in the dictionary a substring from 0 to i
            if self.prondict.has_key( entry[:i] ):
                # Return index for the longest string
                return i
            i = i-1

        # Did not find any pronunciation for this entry!
        return 0


    def __recurslr(self,str):
        """
        Recursive method to find a phonetization of a supposed unknown entry.
        Return a string with the proposed phonetization.
        Spaces separate segments.
        """
        if len(str) == 0:
            return ""

        # LEFT:
        # ###########
        # Find the index of the longest left string that can be phonetized
        leftindex = self.__longestlr(str)
        # Nothing can be phonetized at the left part!
        if leftindex == 0:
            _phonleft = ""
            leftindex = 1
            left = ""
        else:
            # left is from the first to the leftindex character in str
            left = str[:leftindex]
            # Phonetize
            if not self.prondict.has_key( left ):
                _phonleft = ""
            else:
                _phonleft = self.prondict.get( left )
            # The entire entry can be phonetized (nothing to do at right)
            ##if left == len(str):
            if leftindex == len(str):
                return _phonleft

        # RIGHT:
        # ###########
        right = str[leftindex:len(str)]
        if len(right) == 0:
            return _phonleft
        if self.prondict.has_key( right ):
            _phonright = self.prondict.get( right )
        else:
            # If right part of the entry is unknown...
            # Use recursivity to phonetize
            _phonright = self.__recurslr(right)

        if len(_phonleft)>0 and len(_phonright)>0:
            return _phonleft+" "+_phonright

        return _phonright


    def __longestrl(self,entry):
        """
        Select the longest phonetization of an entry, from the start.
        """
        i = 0
        while (i<len(entry)):
            # Find in the dictionary a substring from i to the entry-length
            if self.prondict.has_key( entry[i:] ):
                # Return index for the longest string
                return i
            i = i+1

        # Did not find any pronunciation for this entry!
        return len(entry)


    def __recursrl(self,str):
        """
        Recursive method to find a phonetization of a supposed unknown entry.
        Return a string with the proposed phonetization.
        Spaces separate segments.
        """
        if len(str) == 0:
            return ""

        # RIGHT:
        # ###########
        # Find the index of the longest right string that can be phonetized
        rightindex = self.__longestrl(str)
        # Nothing can be phonetized at the right part!
        if rightindex == len(str):
            _phonright = ""
            rightindex = len(str)-1
            right = ""
        else:
            # right is from the end to the rightindex character in str
            right = str[rightindex:]
            # Phonetize
            if not self.prondict.has_key( right ):
                _phonright = ""
            else:
                _phonright = self.prondict.get( right )
            # The entire entry can be phonetized (nothing to do at left)
            if rightindex == 0:
                return _phonright

        # LEFT:
        # ###########
        left = str[0:rightindex]
        if len(left) == 0:
            return _phonright
        if self.prondict.has_key( left ):
            _phonleft = self.prondict.get( left )
        else:
            # If left part of the entry is unknown...
            # Use recursivity to phonetize
            _phonleft = self.__recursrl( left )

        if len(_phonleft)>0 and len(_phonright)>0:
            return _phonleft+" "+_phonright

        return _phonleft

# End PhonUnk
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Used to debug:

if __name__ == '__main__':

    d = { 'a':'a|aa', 'b':'b', 'c':'c|cc', 'abb':'abb', 'bac':'bac' }
    p = PhonUnk(d)

    print p.get_phon('abbac')

# ----------------------------------------------------------------------

