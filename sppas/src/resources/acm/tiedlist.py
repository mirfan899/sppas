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
# File: tiedlist.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import codecs

import resources.rutils as rutils

# ---------------------------------------------------------------------------

class TiedList:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Tiedlist of an acoustic model.

    This class is used to manage the tiedlist of a triphone acoustic model, i.e:
        - the list of observed phones, biphones, triphones,
        - a list of biphones or triphones to tie.

    """
    def __init__(self):
        """
        Constructor.

        """
        self.observed = []
        self.tied     = {}

    # -----------------------------------------------------------------------

    def load(self, filename):
        """
        Load a tiedlist from a file.

        @param filename (str)

        """
        with codecs.open(filename, 'r', rutils.ENCODING) as fd:
            for nbl, line in enumerate(fd, 1):
                line=line.strip()
                try:
                    tab = line.split(' ')
                    if len(tab) == 1:
                        self.add_observed(line)
                    elif len(tab) == 2:
                        self.add_tied(tab[0].strip(), tab[1].strip())
                    else:
                        raise ValueError('Unexpected entry at line %d: %r' %(nbl,tab))
                except Exception as e:
                    raise Exception("Read file failed due to the following error at line %d: %s" % (nbl,str(e)))

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the tiedlist into a file.

        @param filename is the tiedlist file name

        """
        with codecs.open(filename, 'w', rutils.ENCODING) as fp:
            for triphone in self.observed:
                fp.write( triphone + "\n" )
            for k,v in sorted(self.tied.items()):
                fp.write( k + " " + v + "\n")

    # -----------------------------------------------------------------------

    def is_empty(self):
        """
        Return True if the TiedList() is empty.

        """
        return len(self.observed)==0 and len(self.tied)==0

    # -----------------------------------------------------------------------

    def is_observed(self, entry):
        """
        Return True if entry is really observed (not tied!).

        @param entry is a triphone/biphone/monophone

        """
        return entry in self.observed

    # -----------------------------------------------------------------------

    def is_tied(self, entry):
        """
        Return True if entry is tied.

        @param entry is a triphone/biphone/monophone

        """
        return self.tied.has_key( entry )

    # -----------------------------------------------------------------------

    def add_tied(self, tied, observed=None):
        """
        Add an entry into the tiedlist.
        If observed is None, an heuristic will assign one.

        @param tied is the biphone/triphone to add,
        @param observed is the biphone/triphone to tie with.
        @return bool

        """
        if self.tied.has_key( tied ) or tied in self.observed:
            return False

        if observed is None:
            # Which type of entry?
            if tied.find("+") == -1:
                # NOT either a biphone or triphone
                return False
            if tied.find("-") == -1:
                return self.__add_biphone( tied )
            return self.__add_triphone( tied )

        self.tied[ tied ] = observed
        return True

    # -----------------------------------------------------------------------

    def add_observed(self, entry):
        """
        Add an entry.

        @param entry (str)
        @return bool

        """
        if not entry in self.observed:
            self.observed.append( entry )
            return True
        return False

    # -----------------------------------------------------------------------

    def merge(self, other):
        """
        Merge self with another tiedlist.

        @param other (TiedList)

        """
        if isinstance(other,TiedList) is False:
            raise TypeError('A TiedList can only be merged with another TiedList. Got %s.'%type(other))

        for obs in other.observed:
            self.add_observed( obs )

        for tie,obs in other.tied.items():
            self.add_tied(tie, obs)

    # -----------------------------------------------------------------------

    def remove(self, entry, propagate=False):
        """
        Remove an entry of the list of observed or tied entries.

        @param entry (str) the entry to be removed
        @param propagate (bool) if entry is an observed item, remove all tied
        that are using this observed item.

        """
        if entry in self.observed:
            self.observed.remove( entry )
            if propagate is True:
                for k,v in self.tied.items():
                    if v == entry:
                        self.tied.pop( k )

        if entry in self.tied.keys():
            self.tied.pop( entry )

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def __find(self, tied):
        """
        Find which observed model will match to tie the given entry.

        @param tied (str) the model to be tied
        @return the observed model to tie with.

        """
        observed = ""
        frqtied = {}
        for v in self.tied.values():
            if v.find( tied )>-1:
                # Caution: a biphone can only be tied with a biphone
                if tied.find("-")==-1 and v.find("-")>-1:
                    pass
                else:
                    if frqtied.has_key( v ):
                        frqtied[ v ] = frqtied[ v ]+1
                    else:
                        frqtied[ v ] = 1
        frqmax = 0
        for p,f in frqtied.items():
            if f > frqmax:
                frqmax = f
                observed = p

        return observed

    # -----------------------------------------------------------------------

    def __add_triphone( self, entry ):
        """
        Add an observed model to tie with the given entry.

        @param entry (str) the model to be tied
        @return bool

        """
        # Get the biphone to tie
        biphone = entry[ entry.find('-')+1: ]
        observed = self.__find( biphone )

        if len(observed) == 0:
            # Get the monophone to tie
            monophone = entry[ entry.find('-'):entry.find('+')+1 ]
            observed = self.__find( monophone )
            if len(observed) == 0:
                return False

        self.tied[ entry ] = observed

        return True

    # -----------------------------------------------------------------------

    def __add_biphone( self, entry ):
        """
        Add an observed model to tie with the given entry.

        @param entry (str) the model to be tied
        @return bool

        """
        # Get the monophone to tie
        monophone = entry[ :entry.find('+')+1 ]
        observed = self.__find( monophone )
        if len(observed) == 0:
            return False

        self.tied[ entry ] = observed

        return True

    # -----------------------------------------------------------------------
