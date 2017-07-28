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

    src.anndata.media.py
    ~~~~~~~~~~~~~~~~~~~~~

"""
import mimetypes

from sppas.src.utils.fileutils import sppasGUID
from sppas.src.utils.makeunicode import u

from .metadata import sppasMetaData

# ----------------------------------------------------------------------------


class sppasMedia(sppasMetaData):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Generic representation of a media file.
    
    """
    def __init__(self, filename, media_name=None, mime_type=None):
        """ Creates a new sppasMedia instance.

        :param filename: (str) File name of the media
        :param media_name: (str) Identifier of the media
        :param mime_type: (str) Mime type of the media

        """
        super(sppasMedia, self).__init__()

        self.__url = filename
        self.__name = None
        self.__mime = ""
        self.__content = ""

        if media_name is None:
            self.__name = sppasGUID().get()
        else:
            self.__name = media_name

        if mime_type is None:
            m = mimetypes.guess_type(self.__url)
            if m[0] is None:
                mime_type = "audio/basic"
            else:
                mime_type = m[0]
        self.__mime = mime_type

    # -----------------------------------------------------------------------

    def get_filename(self):
        """ Return the URL of the media. """

        return self.__url

    # -----------------------------------------------------------------------

    def get_name(self):
        """ Return the identifier name of the media. """
        
        return self.__name

    # -----------------------------------------------------------------------

    def get_mime_type(self):
        """ Return the mime type of the media. """

        return self.__mime

    # -----------------------------------------------------------------------

    def get_content(self):
        """ Return the content of the media. """

        return self.__content

    # -----------------------------------------------------------------------

    def set_content(self, content):
        """ Set the content of the media.

        :param content: (str)
        """

        self.__content = u(content)

    # -----------------------------------------------------------------------
