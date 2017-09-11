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

    src.models.modelsexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for models package.

"""
from . import t

# -----------------------------------------------------------------------

DATATYPE_ERROR = ":ERROR 7010: "

MIO_ENCODING_ERROR = ":ERROR 7500: "
MIO_FILE_FORMAT_ERROR = ":ERROR 7505: "
MIO_FOLDER_ERROR = ":ERROR 7510: "

# -----------------------------------------------------------------------


class ModelsDataTypeError(TypeError):
    """ :ERROR 7010: Expected a {data_name} of type {expected_type}. Got {data_type} instead. """

    def __init__(self, data_name, expected_type, data_type):
        self.parameter = DATATYPE_ERROR + \
                         (t.gettext(DATATYPE_ERROR)).format(data_name=data_name,
                                                            expected_type=expected_type,
                                                            data_type=data_type)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class MioEncodingError(UnicodeDecodeError):
    """ :ERROR 7500: MIO_ENCODING_ERROR
    The file {!s:s} contains non UTF-8 characters: {:s}.

    """
    def __init__(self, filename, error):
        self.parameter = MIO_ENCODING_ERROR + \
                         (t.gettext(MIO_ENCODING_ERROR)).format(filename, error)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class MioFileFormatError(IOError):
    """ :ERROR 7505: MIO_FILE_EXTENSION_ERROR
    Fail formats: unrecognized file format {!s:s}.

    """
    def __init__(self, name):
        self.parameter = MIO_FILE_FORMAT_ERROR + \
                         (t.gettext(MIO_FILE_FORMAT_ERROR)).format(name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class MioFolderError(IOError):
    """ :ERROR 7510: MIO_FOLDER_ERROR
    Fail formats: the folder {!s:s} does not contain a known model.

    """
    def __init__(self, folder):
        self.parameter = MIO_FOLDER_ERROR + \
                         (t.gettext(MIO_FOLDER_ERROR)).format(folder)

    def __str__(self):
        return repr(self.parameter)
