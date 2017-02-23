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

    src.anndata.annlabel.tag.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.utils.makeunicode import sppasUnicode, b
from ..anndataexc import AnnDataTypeError

# ---------------------------------------------------------------------------


class sppasTag(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Represents one of the possible tags of a label.

    """
    def __init__(self, tag_content, tag_type="str"):
        """ Initialize a new sppasTag instance.

        :param tag_content: (str)
        :param tag_type: (str): The type of this content (str, int, float, bool)

        >>> t = sppasTag("2")                      # "2"
        >>> t = sppasTag(2, tag_type="int")        # 2
        >>> t = sppasTag("2", tag_type="int")      # 2
        >>> t = sppasTag("2", tag_type="float")    # 2.
        >>> t = sppasTag("true", tag_type="bool")  # True
        >>> t = sppasTag(0, tag_type="bool")       # False
        >>> t = sppasTag(1, tag_type="bool")       # True

        """
        self.__tag_content = ""
        self.__tag_type = "str"
        
        self.set_content(tag_content, tag_type)

    # ------------------------------------------------------------------------

    def set(self, other):
        """ Set self members from another sppasTag instance.

        :param other: (sppasTag)

        """
        if isinstance(other, sppasTag) is False:
            raise AnnDataTypeError(other, "sppasTag")

        self.set_content(other.get_content())
        self.__tag_type = other.get_type()

    # -----------------------------------------------------------------------

    def get_content(self):
        """ Return the unicode string corresponding to the content of this sppasTag. """

        return self.__tag_content

    # ------------------------------------------------------------------------

    def get_typed_content(self):
        """ Return the content value of this sppasTag, in its appropriate type. """

        if self.__tag_type == "int":
            return int(self.__tag_content)

        if self.__tag_type == "float":
            return float(self.__tag_content)

        if self.__tag_type == "bool":
            if self.__tag_content.lower() == "true":
                return True
            else:
                return False

        return self.__tag_content

    # ------------------------------------------------------------------------

    def set_content(self, tag_content, tag_type="str"):
        """ Change content of this sppasTag.

        :param tag_content: New text content for this sppasTag
        :param tag_type: The type of this value (str, int, float, bool)

        """
        if tag_type in ["float", "int", "bool"]:
            if tag_type == "float":
                tag_content = float(tag_content)
            elif tag_type == "int":
                tag_content = int(tag_content)
            else:
                tag_content = bool(tag_content)

        if isinstance(tag_content, (float, int, bool)):
            tag_content = str(tag_content)

        su = sppasUnicode(tag_content)
        self.__tag_content = su.to_strip()
        self.__tag_type = tag_type

    # ------------------------------------------------------------------------

    def get_type(self):
        """ Return the type of the tag content. """
        
        return self.__tag_type

    # ------------------------------------------------------------------------

    def is_empty(self):
        """ Return True if the tag is an empty string. """
        
        return self.__tag_content == ""

    # -----------------------------------------------------------------------

    def is_speech(self):
        """ Return True if the tag is not a silence. """
        
        return not (self.is_silence() or self.is_pause() or self.is_laugh() or self.is_noise() or self.is_dummy())

    # -----------------------------------------------------------------------

    def is_silence(self):
        """ Return True if the tag is a silence. """

        # SPPAS representation of silences
        if self.__tag_content in ("#", "sil"):
            return True

        # The French CID corpus:
        if self.__tag_content.startswith("gpf_"):
            return True

        return False

    # -----------------------------------------------------------------------

    def is_pause(self):
        """ Return True if the tag is a short pause. """

        return self.__tag_content == "+"

    # -----------------------------------------------------------------------

    def is_laugh(self):
        """ Return True if the tag is a laughing. """

        return self.__tag_content == "@@"

    # -----------------------------------------------------------------------

    def is_noise(self):
        """ Return True if the tag is a noise. """

        return self.__tag_content == "*"

    # -----------------------------------------------------------------------

    def is_dummy(self):
        """ Return True if the tag is a dummy label. """

        return self.__tag_content == "dummy"

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __repr__(self):
        return "Tag: {:s},{:s}".format(b(self.get_content()), self.get_type())

    def __str__(self):
        return "{:s} ({:s})".format(b(self.get_content()), self.get_type())

    def __eq__(self, other):
        return self.get_typed_content() == other.get_typed_content()

    def __hash__(self):
        return hash((self.__tag_content, self.__tag_type))
