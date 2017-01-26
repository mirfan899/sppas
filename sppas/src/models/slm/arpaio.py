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
__authors___ = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ---------------------------------------------------------------------------

import codecs
from sppas.src.sp_glob import encoding

# ---------------------------------------------------------------------------

class ArpaIO(object):
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: ARPA statistical language models reader/writer.

    This class is able to load and save statistical language models from
    ARPA-ASCII files.

    """
    def __init__(self):
        """
        Create an ArpaIO instance.

        """
        self.slm = None

    # -----------------------------------------------------------------------

    def set(self, slm):
        """
        Set the model of the SLM.

        @param slm (list) List of tuples for 1-gram, 2-grams, ...

        """
        if not (isinstance(slm, list) and all([isinstance(m, list) for m in slm])):
            raise TypeError('Expected a list of lists of tuples.')

        self.slm = slm

    # -----------------------------------------------------------------------

    def load(self, filename):
        """
        Load an ARPA model from a file.

        @param filename (str - IN) Filename of the model.

        """
        # we expect small models, so we can read the whole file in one
        with codecs.open(filename, 'r', encoding) as f:
            lines = f.readlines()

        self.slm = []
        n = 0
        lm = []
        for line in lines:
            line = line.strip()
            if len(line) == 0:
                pass
            elif line.startswith('\\end'):
                break
            elif line.startswith('\\') and not "data" in line:
                if n > 0:
                    self.slm.append(lm)
                n += 1
                lm = []
            elif n > 0:
                # split line into columns
                cols = line.split()
                if len(cols) < n+1:
                    raise ValueError('Unexpected line: %s' % line)
                # probability is the first column
                proba = float(cols[0])
                # the n- following columns are the ngram
                tokenseq = " ".join(cols[1:n+1])
                # the last (optional) value is the bow
                bow = None
                if len(cols) > n+1:
                    bow = float(cols[-1])
                lm.append((tokenseq, proba, bow))

        if n > 0:
            self.slm.append(lm)
        return self.slm

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

        @param filename (str - IN) File where to save the model.

        """
        with codecs.open(filename, 'w', encoding) as f:
            if self.slm is not None:
                f.write(self._serialize_slm())

    # -----------------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------------

    def _serialize_slm(self):
        """
        Serialize a model into a string, in ARPA-ASCII format.

        @return The ARPA-ASCII model as a string.

        """
        result = self._serialize_header()
        for n, m in enumerate(self.slm):
            newngram = self._serialize_ngram(m, n+1)
            result = result + newngram
        result += self._serialize_footer()

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
        for i, m in enumerate(self.slm):
            r += "ngram " + str(i+1) + "=" + str(len(m)) + "\n"
        r += "\n"
        return r

    # -----------------------------------------------------------------------

    def _serialize_ngram(self, model, order):
        """

             \2-grams:
             p(a_z)  a_z  bow(a_z)
             ...

        """
        r = "\\"+str(order)+"-grams: \n"
        for (wseq, lp, bo) in model:
            r += str(round(lp, 6)) + "\t" + wseq
            if bo is not None:
                r += "\t"+str(round(bo, 6))
            r += "\n"
        r += "\n"
        return r

    # -----------------------------------------------------------------------

    def _serialize_footer(self):
        """
             \end
        """
        return "\\end\n"

    # -----------------------------------------------------------------------
