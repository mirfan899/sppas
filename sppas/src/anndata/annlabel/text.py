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

    src.anndata.annlabel.text.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
from sppas.src.utils.makeunicode import sppasUnicode, b

# ---------------------------------------------------------------------------


class sppasText(object):

    def __init__(self, text_content, data_type="str"):
        """ Initialize a new sppasText instance.

        :param text_content: (str)
        :param data_type: (str): The type of this value (str, int, float, bool)

        >>> t = sppasText("2")                      # "2"
        >>> t = sppasText(2, data_type="int")        # 2
        >>> t = sppasText("2", data_type="int")      # 2
        >>> t = sppasText("2", data_type="float")    # 2.
        >>> t = sppasText("true", data_type="bool")  # True
        >>> t = sppasText(0, data_type="bool")       # False
        >>> t = sppasText(1, data_type="bool")       # True

        """
        self.__value = ""
        self.__data_type = "str"
        
        self.set_value(text_content, data_type)

    # ------------------------------------------------------------------------

    def get_value(self):
        """ Return the string corresponding to the value of this sppasText. """

        return self.__value

    # ------------------------------------------------------------------------

    def set_value(self, text_content, data_type="str"):
        """ Change value of this sppasText.

        :param text_content: New text content for this sppasText
        :param data_type: The type of this value (str, int, float, bool)

        """
        if data_type in ["float", "int", "bool"]:
            if data_type == "float":
                text_content = float(text_content)
            elif data_type == "int":
                text_content = int(text_content)
            else:
                text_content = bool(text_content)

        if isinstance(text_content, (float, int, bool)):
            text_content = str(text_content)

        su = sppasUnicode(text_content)
        self.__value = su.to_strip()
        self.__data_type = data_type

    # ------------------------------------------------------------------------

    def get_typed_value(self):
        """ Return the value of this sppasText, in its appropriate type. """

        if self.__data_type == "int":
            return int(self.__value)

        if self.__data_type == "float":
            return float(self.__value)

        if self.__data_type == "bool":
            if self.__value.lower() == "true":
                return True
            else:
                return False

        return self.__value

    # ------------------------------------------------------------------------

    def is_empty(self):
        """ Return True if the text value is an empty string. """
        
        return self.__value == ""

    # -----------------------------------------------------------------------

    def is_speech(self):
        """ Return True if the text value is not a silence. """
        
        return not (self.is_silence() or self.is_pause() or self.is_laugh() or self.is_noise() or self.is_dummy())

    # -----------------------------------------------------------------------

    def is_silence(self):
        """ Return True if the text value is a silence. """

        # SPPAS representation of silences
        if self.__value in ("#", "sil"):
            return True

        # The French CID corpus:
        if self.__value.startswith("gpf_"):
            return True

        return False

    # -----------------------------------------------------------------------

    def is_pause(self):
        """ Return True if the text value is a short pause. """

        return self.__value == "+"

    # -----------------------------------------------------------------------

    def is_laugh(self):
        """ Return True if the text value is a laughing. """

        return self.__value == "@@"

    # -----------------------------------------------------------------------

    def is_noise(self):
        """ Return True if the text value is a noise. """

        return self.__value == "*"

    # -----------------------------------------------------------------------

    def is_dummy(self):
        """ Return True if the text value is a dummy label. """

        return self.__value == "dummy"

    # ------------------------------------------------------------------------
    # Overloads
    # ------------------------------------------------------------------------

    def __repr__(self):
        return "Text: {:s}".format(b(self.get_value()))

    def __str__(self):
        return b(self.get_value())

    def __eq__(self, other):
        return self.get_typed_value() == other.get_typed_value()
