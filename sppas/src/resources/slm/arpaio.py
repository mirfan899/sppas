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
# File: acmodelhtkio.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors___  = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------

class ArpaIO:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: ARPA statistical language models reader/writer.

    This class is able to load and save statistical language models from
    ARPA-ASCII files.

    """
    def __init__(self, filename=None):
        """
        Create an ArpaIO instance, and optionaly load a model from a file.

        @param filename (str)

        """
        self.slm = None
        if filename:
            self.load(filename)

    # -----------------------------------------------------------------------

    def load(self, filename):
        """
        Load an ARPA model from a file.

        @param filename (str) Filename of the model.

        """
        raise NotImplementedError

    # -----------------------------------------------------------------------

    def save(self, filename):
        """
        Save the model into a file, in ARPA-ASCII format.
        The ARPA format:

             \data\
             ngram 1=nb1
             ngram 2=nb2
             ...
             ngram N=nbN

             \1-grams:
             p(a_z)  a_z  bow(a_z)
             ...

             \2-grams:
             p(a_z)  a_z  bow(a_z)
             ...

             \N-grams:
             p(a_z)  a_z
             ...

             \end\

        @param filename (str) File where to save the model.

        """
        with open(filename, 'w') as f:
            if self.slm:
                f.write( self._serialize_slm() )

    # -----------------------------------------------------------------------

    def set(self, slm):
        """
        Set the model of the SLM.

        @param slm (list) List of SLM instances 1-gram, 2-grams, ...).

        """
        if not (isinstance(slm, list) and all([isinstance(m,slm.SLM) for m in slm])):
            raise TypeError('Expected a list of HMMs instances.')

        self.slm = slm

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _serialize_slm(self):
        """
        Serialize a model into a string, in ARPA-ASCII format.

        @return The ARPA-ASCII model as a string.

        """
        result = self._serialize_header()
        for m in self.slm:
            result += self._serialize_ngram( m )

        return result

    # -----------------------------------------------------------------------

    def _serialize_header(self):
        """

             \data\
             ngram 1=nb1
             ngram 2=nb2
             ...
             ngram N=nbN

        """
        r = "\\data\\ \n"
        for i,m in enumerate(self.slm):
            r += "ngram " + str(i) + "=" +m.get_order()+"\n"
        r += "\n"
        return r

    # -----------------------------------------------------------------------

    def _serialize_ngram(self, model):
        """

             \2-grams:
             p(a_z)  a_z  bow(a_z)
             ...

        """
        r = "\\"+str(model.get_order())+"-grams: \n"
        for (wseq,lp,bo) in model:
            r += lp+" "+wseq
            if bo is not None:
                r+=" "+bo
            r+="\n"
        r+="\n"
        return r

    # -----------------------------------------------------------------------
