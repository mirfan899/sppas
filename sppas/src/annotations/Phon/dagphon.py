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
# File: dagphon.py
# ----------------------------------------------------------------------------

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

# ----------------------------------------------------------------------------

class DAGPhon:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Utility class to manage phonetizations with a DAG.

    """
    def __init__(self, variants=4):
        """
        Constructor.

        @param variants (int) Maximum number of variants for phonetizations.

        """
        self.variants = variants

    # -----------------------------------------------------------------------

    def phon2DAG(self, pron):
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
                p = p + "-" + prongraph[i]
            p = re.sub('^.', "", p)
            pron[p] = len(p.split("-"))

        return pron

    # -----------------------------------------------------------------------

    def decompose(self, pron1, pron2=""):
        """
        Create a decomposed-phonetization from a string as follow:

            >>> self.decompose("p1 p2|x2 p3|x3")
            p1.p2.p3|p1.p2.x3|p1.x2.p3|p1.x2.x3

        The input string is converted into a DAG, then output corresponds
        to all paths.

        """
        if len(pron1) == 0 and len(pron2) == 0:
            return ""

        # Complex phonetization: converted into a DAG
        (graph1,prongraph1) = self.phon2DAG( pron1 )
        if len(pron2) > 0:
            (graph2,prongraph2) = self.phon2DAG( pron2 )

        # Create all pronunciations from the DAG
        pron1 = self.DAG2phon(graph1,prongraph1)
        if len(pron2) > 0:
            pron2 = self.DAG2phon(graph2,prongraph2)
        else:
            pron2 = {}

        # Merge =======>
        # TODO: MERGE DAGs instead of merging prons
        pron = dict(pron1.items() + pron2.items())

        # Output selection

        # Return all variants
        if self.variants == 0:
            return "|".join(pron.keys())

        # Choose the shorter variants
        if self.variants == 1:
            return min(pron.items(), key=lambda x: x[1])[0]

        # Other number of variants: choose shorters
        l = sorted(pron.items(), key=lambda x: x[1])[:self.variants]
        return "|".join(zip(*l)[0])

    # -----------------------------------------------------------------------
