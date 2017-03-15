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

DX_VALID = ":INFO 1000: "
DX_ADMIT = ":INFO 1002: "
DX_INVALID = ":INFO 1004: "
DX_FAILED = ":INFO 1006: "
DX_AUDIO_CHANNELS_ERROR = ":INFO 1010: "
DX_AUDIO_SAMPWIDTH_ERROR = ":INFO 1012: "
DX_AUDIO_FRAMERATE_ERROR = ":INFO 1014: "
DX_AUDIO_SAMPWIDTH_WARN = ":INFO 1016: "
DX_AUDIO_FRAMERATE_WARN = ":INFO 1018: "
DX_UNKNOWN_FILE = ":INFO 1020: "
DX_FILE_NON_ASCII = ":INFO 1022: "
DX_FILE_WHITESPACE = ":INFO 1024: "
DX_FILE_ENCODING = ":INFO 1026: "

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

    def __init__(self, logfile=None):
        """ SPPAS files diagnosis.
        
        :param logfile: (sppasLog)

        """
        self._logfile = logfile

        # for transcriptions
        self._encoding = encoding

    # ------------------------------------------------------------------------
    # Workers
    # ------------------------------------------------------------------------

    def check_file(self, filename):
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

        message = t.gettext(DX_FAILED) + (t.gettext(DX_UNKNOWN_FILE)).format(extension=ext)
        return (ERROR_ID, message)

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
            message = t.gettext(DX_INVALID) + (t.gettext(DX_FILE_ENCODING)).format(encoding=encoding)
            return (ERROR_ID, message)
        except Exception as e:
            message = t.gettext(DX_INVALID) + str(e)
            return (ERROR_ID, message)

        if nc > sppasDiagnosis.EXPECTED_CHANNELS:
            status = ERROR_ID
            message += (t.gettext(DX_AUDIO_CHANNELS_ERROR)).format(number=audio.get_nchannels())

        if sp < sppasDiagnosis.EXPECTED_SAMPLE_WIDTH*8:
            status = ERROR_ID
            message += (t.gettext(DX_AUDIO_SAMPWIDTH_ERROR)).format(sampwidth=sp)

        if fm < sppasDiagnosis.EXPECTED_FRAME_RATE:
            status = ERROR_ID
            message += (t.gettext(DX_AUDIO_FRAMERATE_ERROR)).format(framerate=fm)

        if status != ERROR_ID:
            if sp > sppasDiagnosis.EXPECTED_SAMPLE_WIDTH*8:
                status = WARNING_ID
                message += (t.gettext(DX_AUDIO_SAMPWIDTH_WARN)).format(sampwidth=sp)

            if fm > sppasDiagnosis.EXPECTED_FRAME_RATE:
                status = WARNING_ID
                message += (t.gettext(DX_AUDIO_FRAMERATE_WARN)).format(framerate=fm)

        # test whitespace and US-ASCII chars
        try:
            str(filename)
        except Exception:
            status = WARNING_ID
            message += t.gettext(DX_FILE_NON_ASCII)

        if " " in filename:
            status = WARNING_ID
            message += t.gettext(DX_FILE_WHITESPACE)

        if status == ERROR_ID:
            message = t.gettext(DX_INVALID) + message
        elif status == WARNING_ID:
            message = t.gettext(DX_ADMIT) + message
        else:
            message = t.gettext(DX_VALID)

        return (status, message)

    # ------------------------------------------------------------------------

    @staticmethod
    def check_trs_file(filename):
        """ Return a status and a message depending on the fact that the file 
        is matching the requirements.

        :param filename: (string) name of the input file
        :returns: tuple with (status identifier, message)

        """
        status = OK_ID
        message = t.gettext(DX_VALID)

        # test encoding
        try:
            codecs.open(filename, "r", encoding)
        except UnicodeDecodeError:
            message = t.gettext(DX_INVALID) + (t.gettext(DX_FILE_ENCODING)).format(encoding=encoding)
            return (ERROR_ID, message)
        except Exception as e:
            message = t.gettext(DX_INVALID) + str(e)
            return (ERROR_ID, message)

        # test US_ASCII in filename
        try:
            str(filename)
        except Exception:
            message = t.gettext(DX_ADMIT) + t.gettext(DX_FILE_NON_ASCII)
            return (WARNING_ID, message)

        # test whitespace and accents in filename
        if " " in filename:
            message = t.gettext(DX_ADMIT) + t.gettext(DX_FILE_WHITESPACE)
            return (WARNING_ID, message)

        return (status, message)
