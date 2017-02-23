# -*- coding: UTF-8 -*-
"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.anndata.ctrlvocab.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    A controlled Vocabulary is a set of tags. It is used to restrict the use
    of tags in a label: only the accepted tags can be set to a label.

"""
from sppas.src.utils.makeunicode import sppasUnicode
from .anndataexc import AnnDataTypeError
from .annlabel.tag import sppasTag

# ----------------------------------------------------------------------------


class sppasCtrlVocab(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Generic representation of a controlled vocabulary.

    A controlled vocabulary is made of an identifier name, a description and
    a list of pairs tag/description.

    """
    def __init__(self, name, description=""):
        """ Creates a new sppasCtrlVocab instance.

        :param name: (str) Identifier name of the controlled vocabulary
        :param description: (str)

        """
        # The name:
        # make unicode, strip and replace whitespace by underscore.
        su = sppasUnicode(str(name))
        self.__name = su.clear_whitespace()

        # The description:
        self.__desc = ""
        if len(description) > 0:
            self.set_description(description)

        # The set of tags:
        self.__entries = dict()

    # -----------------------------------------------------------------------

    def get_name(self):
        """ Return the name of the controlled vocabulary. """

        return self.__name

    # -----------------------------------------------------------------------

    def get_description(self):
        """ Return the unicode string of the description of the controlled vocabulary. """

        return self.__desc

    # ------------------------------------------------------------------------

    def set_description(self, description=""):
        """ Set the description of the controlled vocabulary.

        :param description: (str)

        """
        su = sppasUnicode(description)
        self.__desc = su.to_strip()

    # -----------------------------------------------------------------------

    def contains(self, tag):
        """ Test if a tag is already in the controlled vocabulary.

        :param tag: (sppasTag) the tag to check.
        :returns: Boolean

        """
        if isinstance(tag, sppasTag) is False:
            raise AnnDataTypeError(tag, "sppasTag")

        return tag in self.__entries

    # -----------------------------------------------------------------------

    def add(self, tag, description=""):
        """ Add a tag in the controlled vocab.

        :param tag: (sppasTag): the tag to add.
        :param description: (str)
        :returns: Boolean

        """
        if isinstance(tag, sppasTag) is False:
            raise AnnDataTypeError(tag, "sppasTag")

        if self.contains(tag) is True:
            return False

        su = sppasUnicode(description)
        self.__entries[tag] = su.to_strip()
        return True

    # -----------------------------------------------------------------------

    def remove(self, tag):
        """ Remove a tag of the controlled vocab.

        :param tag: (sppasTag) the tag to remove.
        :returns: Boolean

        """
        if isinstance(tag, sppasTag) is False:
            raise AnnDataTypeError(tag, "sppasTag")

        if self.contains(tag) is False:
            return False

        del self.__entries[tag]
        return True

    # -----------------------------------------------------------------------
    # Overloads
    # -----------------------------------------------------------------------

    def __iter__(self):
        for a in self.__entries:
            yield a

    def __len__(self):
        return len(self.__entries)
