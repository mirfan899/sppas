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

    src.annotations.diagnosis.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import codecs
import os

from sppas import encoding
import sppas.src.annotationdata.aio
import sppas.src.audiodata.aio
from . import ERROR_ID, WARNING_ID, OK_ID
from .import t

# ----------------------------------------------------------------------------

MSG_VALID = t.gettext(":INFO 1000: ")
MSG_ADMIT = t.gettext(":INFO 1002: ")
MSG_INVALID = t.gettext(":INFO 1004: ")
MSG_FAILED = t.gettext(":INFO 1006: ")
MSG_AUDIO_CHANNELS_ERROR = (t.gettext(":INFO 1010: "))
MSG_AUDIO_SAMPWIDTH_ERROR = (t.gettext(":INFO 1012: "))
MSG_AUDIO_FRAMERATE_ERROR = (t.gettext(":INFO 1014: "))
MSG_AUDIO_SAMPWIDTH_WARN = (t.gettext(":INFO 1016: "))
MSG_AUDIO_FRAMERATE_WARN = (t.gettext(":INFO 1018: "))
MSG_UNKNOWN_FILE = (t.gettext(":INFO 1020: "))
MSG_FILE_NON_ASCII = (t.gettext(":INFO 1022: "))
MSG_FILE_WHITESPACE = (t.gettext(":INFO 1024: "))
MSG_FILE_ENCODING = (t.gettext(":INFO 1026: "))

# ----------------------------------------------------------------------------


class sppasDiagnosis(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      A class to diagnose if files are appropriate.
    
    Check if files are valid for SPPAS automatic annotations.

    """
    EXPECTED_CHANNELS = 1
    EXPECTED_FRAME_RATE = 16000
    EXPECTED_SAMPLE_WIDTH = 2

    # ------------------------------------------------------------------------

    def __init__(self):
        """ SPPAS files diagnosis. """

        pass

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    @staticmethod
    def check_file(filename):
        """ Return a status and a message depending on the fact that the file
        is matching the requirements.

        :param filename: (str) name of the input file to diagnose.
        :returns: tuple with (status identifier, message)

        """
        ext = os.path.splitext(filename)[1]

        if ext.lower() in sppas.src.audiodata.aio.extensions:
            return sppasDiagnosis.check_audio_file(filename)

        if ext.lower() in sppas.src.annotationdata.aio.extensions:
            return sppasDiagnosis.check_trs_file(filename)

        message = MSG_FAILED + MSG_UNKNOWN_FILE.format(extension=ext)
        return ERROR_ID, message

    # ------------------------------------------------------------------------

    @staticmethod
    def check_audio_file(filename):
        """ Return a status and a message depending on the fact that the 
        file is matching the requirements.

        :param filename: (str) name of the input file
        :returns: tuple with (status identifier, message)

        """
        status = OK_ID
        message = ""

        # test file format: can we support it?
        try:
            audio = sppas.src.audiodata.aio.open(filename)
            fm = audio.get_framerate()
            sp = audio.get_sampwidth()*8
            nc = audio.get_nchannels()
            audio.close()
        except UnicodeDecodeError:
            message = MSG_INVALID + MSG_FILE_ENCODING.format(encoding=encoding)
            return ERROR_ID, message
        except Exception as e:
            message = MSG_INVALID + str(e)
            return ERROR_ID, message

        if nc > sppasDiagnosis.EXPECTED_CHANNELS:
            status = ERROR_ID
            message += MSG_AUDIO_CHANNELS_ERROR.format(number=audio.get_nchannels())

        if sp < sppasDiagnosis.EXPECTED_SAMPLE_WIDTH*8:
            status = ERROR_ID
            message += MSG_AUDIO_SAMPWIDTH_ERROR.format(sampwidth=sp)

        if fm < sppasDiagnosis.EXPECTED_FRAME_RATE:
            status = ERROR_ID
            message += MSG_AUDIO_FRAMERATE_ERROR.format(framerate=fm)

        if status != ERROR_ID:
            if sp > sppasDiagnosis.EXPECTED_SAMPLE_WIDTH*8:
                status = WARNING_ID
                message += MSG_AUDIO_SAMPWIDTH_WARN.format(sampwidth=sp)

            if fm > sppasDiagnosis.EXPECTED_FRAME_RATE:
                status = WARNING_ID
                message += MSG_AUDIO_FRAMERATE_WARN.format(framerate=fm)

        # test US-ASCII chars
        if all(ord(x) < 128 for x in filename) is False:
            status = WARNING_ID
            message += MSG_FILE_NON_ASCII

        if " " in filename:
            status = WARNING_ID
            message += MSG_FILE_WHITESPACE

        # test whitespace
        if status == ERROR_ID:
            message = MSG_INVALID + message
        elif status == WARNING_ID:
            message = MSG_ADMIT + message
        else:
            message = MSG_VALID

        return status, message

    # ------------------------------------------------------------------------

    @staticmethod
    def check_trs_file(filename):
        """ Return a status and a message depending on the fact that the file 
        is matching the requirements.

        :param filename: (string) name of the input file
        :returns: tuple with (status identifier, message)

        """
        status = OK_ID
        message = MSG_VALID

        # test encoding
        try:
            codecs.open(filename, "r", encoding)
        except UnicodeDecodeError:
            message = MSG_INVALID + MSG_FILE_ENCODING.format(encoding=encoding)
            return ERROR_ID, message
        except Exception as e:
            message = MSG_INVALID + str(e)
            return ERROR_ID, message

        # test US_ASCII in filename
        if all(ord(x) < 128 for x in filename) is False:
            message = MSG_ADMIT + MSG_FILE_NON_ASCII
            return WARNING_ID, message

        # test whitespace in filename
        if " " in filename:
            message = MSG_ADMIT + MSG_FILE_WHITESPACE
            return WARNING_ID, message

        return status, message
