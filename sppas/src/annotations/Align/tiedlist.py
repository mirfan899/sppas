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
# File: tiedlist.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------


import sys
import codecs


class Tiedlist:
    """ This class is used to manage the tiedlist of a triphone acoustic model.
    """

    def __init__(self, filename):
        """ Create a new Tiedlist instance.
            Parameters:
                - filename is the tiedlist file name.
            Exceptions;  IOError, ValueError
        """
        self.observed = []
        self.tied = {}
        encoding='utf-8'
        with codecs.open(filename, 'r', encoding) as fp:
            for line in fp:
                tab = line.split(' ')
                if len(tab) == 1:
                    self.observed.append( line.strip() )
                elif len(tab) == 2:
                    self.tied[tab[0].strip()] = tab[1].strip()
                else:
                    raise ValueError('Tiedlist: Unexpected entry: %r' % tab)

    # End __init__
    # ------------------------------------------------------------------


    def is_observed(self,entry):
        """ Return True if entry is really observed (not tied!).
            Parameters:
                - entry is a triphone/biphone/monophone String
            Return:      Boolean
            Exception:   None
        """
        for triphone in self.observed:
            if triphone == entry:
                return True
        return False

    # End is_observed
    # ------------------------------------------------------------------


    def is_tied(self,entry):
        """ Return True if entry is a tied triphone.
            Parameters:
                - entry is a triphone/biphone/monophone String
            Return:      Boolean
            Exception:   None
        """
        return self.tied.has_key( entry )

    # End is_tied
    # ------------------------------------------------------------------


    def save(self, filename):
        """ Write the tiedlist in a file.
            Parameters:
                - filename is the tiedlist file name to save
            Return:      Boolean
            Exception:   IOError
        """
        encoding='utf-8'
        with codecs.open(filename, 'w', encoding) as fp:
            for triphone in self.observed:
                fp.write( triphone + "\n" )
            for k,v in sorted(self.tied.items()):
                fp.write( k + " " + v + "\n")

    # End save
    # ------------------------------------------------------------------


    def __find(self,phones):
        tied = ""
        frqtied = {}
        for k,v in self.tied.items():
            if v.find( phones )>-1:
                # Caution: a biphone can only be tied with a biphone
                if phones.find("-")==-1 and v.find("-")>-1:
                    pass
                else:
                    if frqtied.has_key( v ):
                        f = frqtied[ v ]
                        frqtied[ v ] = f+1
                    else:
                        frqtied[ v ] = 1
        frqmax = 0
        for p,f in frqtied.items():
            if f > frqmax:
                frqmax = f
                tied = p
        return tied


    def __addtriphone( self, entry ):
        # Get the biphon to tie
        biphone = entry[ entry.find('-')+1: ]
        tied = self.__find( biphone )

        if len(tied)==0:
            # Get the monophone to tie
            monophone = entry[ entry.find('-'):entry.find('+')+1 ]
            tied = self.__find( monophone )
            if len(tied)==0:
                return False
        self.tied[ entry ] = tied
        return True


    def __addbiphone( self, entry ):
        # Get the monophone to tie
        monophone = entry[ :entry.find('+')+1 ]
        tied = self.__find( monophone )
        if len(tied)==0:
            return False
        self.tied[ entry ] = tied
        return True

    # End __add private methods
    # ------------------------------------------------------------------


    def add(self, entry):
        """ Add an entry into the tiedlist.
            Parameters:
                - entry is the triphone/biphone String to add
            Return:      Boolean (added or not)
            Exception:   None
        """
        # Which type of entry?
        if entry.find("+")==-1:
            # NOT either a biphone or triphone
            return False
        if entry.find("-")==-1:
            return self.__addbiphone( entry )
        return self.__addtriphone( entry )

    # End add
    # ------------------------------------------------------------------
