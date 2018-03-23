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

    src.anndata.aio.readwrite.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Readers and writers of annotated data.

"""
import os.path
import datetime
from collections import OrderedDict

import sppas
from sppas.src.utils.makeunicode import u

from ..anndataexc import AioEncodingError
from ..anndataexc import AioFileExtensionError

from .text import sppasRawText
from .text import sppasCSV
from .sclite import sppasCTM
from .sclite import sppasSTM
from .xtrans import sppasTDF
from .praat import sppasTextGrid
from .praat import sppasPitchTier
from .praat import sppasIntensityTier
from .phonedit import sppasMRK
from .phonedit import sppasSignaix
from .htk import sppasLab
from .subtitle import sppasSubRip
from .subtitle import sppasSubViewer
from .weka import sppasARFF
from .weka import sppasXRFF
from .transcriber import sppasTRS
from .audacity import sppasAudacity
# from .elan import Elan
# from .anvil import Anvil
# from .annotationpro import Antx
from .xra import sppasXRA

# ---------------------------------------------------------------------------


class sppasRW(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Main parser of annotated data.

    """
    TRANSCRIPTION_TYPES = OrderedDict()
    TRANSCRIPTION_TYPES[sppasXRA().default_extension.lower()] = sppasXRA
    TRANSCRIPTION_TYPES[sppasTextGrid().default_extension.lower()] = sppasTextGrid
    TRANSCRIPTION_TYPES[sppasARFF().default_extension.lower()] = sppasARFF
    TRANSCRIPTION_TYPES[sppasXRFF().default_extension.lower()] = sppasXRFF
    # TRANSCRIPTION_TYPES["eaf"] = Elan,
    # TRANSCRIPTION_TYPES["anvil"] = Anvil
    # TRANSCRIPTION_TYPES["antx"] = Antx
    TRANSCRIPTION_TYPES[sppasTRS().default_extension.lower()] = sppasTRS
    TRANSCRIPTION_TYPES[sppasMRK().default_extension.lower()] = sppasMRK
    TRANSCRIPTION_TYPES[sppasSignaix().default_extension.lower()] = sppasSignaix
    TRANSCRIPTION_TYPES[sppasLab().default_extension.lower()] = sppasLab
    TRANSCRIPTION_TYPES[sppasSubRip().default_extension.lower()] = sppasSubRip
    TRANSCRIPTION_TYPES[sppasSubViewer().default_extension.lower()] = sppasSubViewer
    TRANSCRIPTION_TYPES[sppasCTM().default_extension.lower()] = sppasCTM
    TRANSCRIPTION_TYPES[sppasSTM().default_extension.lower()] = sppasSTM
    TRANSCRIPTION_TYPES[sppasIntensityTier().default_extension.lower()] = sppasIntensityTier
    TRANSCRIPTION_TYPES[sppasPitchTier().default_extension.lower()] = sppasPitchTier
    TRANSCRIPTION_TYPES[sppasAudacity().default_extension.lower()] = sppasAudacity
    TRANSCRIPTION_TYPES[sppasTDF().default_extension.lower()] = sppasTDF
    TRANSCRIPTION_TYPES[sppasCSV().default_extension.lower()] = sppasCSV
    TRANSCRIPTION_TYPES[sppasRawText().default_extension.lower()] = sppasRawText

    # -----------------------------------------------------------------------

    @staticmethod
    def extensions():
        """ Return the list of supported extensions in lower case. """

        return sppasRW.TRANSCRIPTION_TYPES.keys()

    # -----------------------------------------------------------------------

    def __init__(self, filename):
        """ Create a Transcription reader-writer.

        :param filename: (str)

        """
        self.__filename = u(filename)

    # -----------------------------------------------------------------------

    def get_filename(self):
        """ Return the filename. """

        return self.__filename

    # -----------------------------------------------------------------------

    def set_filename(self, filename):
        """ Set a new filename. 

        :param filename: (str)

        """
        self.__filename = u(filename)
        
    # -----------------------------------------------------------------------

    def read(self, heuristic=True):
        """ Read a transcription from a file.

        :param heuristic: (bool) if the extension of the file is unknown,
        use an heuristic to detect the format, then to choose the reader-writer.
        :returns: sppasTranscription reader-writer

        """
        try:
            trs = sppasRW.create_trs_from_extension(self.__filename)
        except AioFileExtensionError:
            if heuristic is True:
                trs = sppasRW.create_trs_from_heuristic(self.__filename)
            else:
                raise

        try:
            # Add metadata about SPPAS
            sppasRW.add_sppas_metadata(trs)

            # Add metadata about the file
            trs.set_meta('file_reader', trs.__class__.__name__)
            trs.set_meta('file_name', os.path.basename(self.__filename))
            trs.set_meta('file_path', os.path.dirname(self.__filename))
            trs.set_meta('file_ext', os.path.splitext(self.__filename)[1])
            now = datetime.datetime.now()
            trs.set_meta('file_read_date', "{:d}-{:d}-{:d}".format(now.year, now.month, now.day))

            # Read the file content dans store into a Trancription()
            trs.read(self.__filename)
        except UnicodeError as e:
            raise AioEncodingError(filename=self.__filename, error=str(e))
        except Exception:
            raise

        return trs

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_extension(filename):
        """ Return a transcription according to a given filename.
        Only the extension of the filename is used.

        :param filename: (str)
        :returns: Transcription()

        """
        extension = os.path.splitext(filename)[1][1:]
        extension = extension.lower()
        if extension in sppasRW.extensions():
            return sppasRW.TRANSCRIPTION_TYPES[extension]()

        raise AioFileExtensionError(filename)

    # -----------------------------------------------------------------------

    @staticmethod
    def create_trs_from_heuristic(filename):
        """ Return a transcription according to a given filename.
        The given file is opened and an heuristic allows to fix the format.

        :param filename: (str)
        :returns: Transcription()

        """
        for file_reader in sppasRW.TRANSCRIPTION_TYPES.values():
            try:
                if file_reader.detect(filename) is True:
                    return file_reader()
            except:
                continue
        return sppasRawText()

    # -----------------------------------------------------------------------

    def write(self, transcription):
        """ Write a transcription into a file.

        :param transcription: (sppasTranscription)

        """
        trs_rw = sppasRW.create_trs_from_extension(self.__filename)
        trs_rw.set(transcription)

        # Add metadata about SPPAS
        sppasRW.add_sppas_metadata(trs_rw)

        # Add metadata about the file
        trs_rw.set_meta('file_writer', trs_rw.__class__.__name__)
        trs_rw.set_meta('file_name', os.path.basename(self.__filename))
        trs_rw.set_meta('file_path', os.path.dirname(self.__filename))
        trs_rw.set_meta('file_ext', os.path.splitext(self.__filename)[1])
        now = datetime.datetime.now()
        trs_rw.set_meta('file_write_date', "{:d}-{:d}-{:d}".format(now.year, now.month, now.day))

        try:
            trs_rw.write(self.__filename)
        except UnicodeError as e:
            raise AioEncodingError(self.__filename, str(e))
        except Exception:
            raise

    # -----------------------------------------------------------------------

    @staticmethod
    def add_sppas_metadata(trs):
        """ Add metadata about SPPAS. """

        trs.set_meta('software_name', sppas.__name__)
        trs.set_meta('software_version', sppas.__version__)
        trs.set_meta('software_url', sppas.__url__)
        trs.set_meta('software_author', sppas.__author__)
        trs.set_meta('software_contact', sppas.__contact__)
        trs.set_meta('software_copyright', sppas.__copyright__)
