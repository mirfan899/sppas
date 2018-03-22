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

    src.anndata.metadata.py
    ~~~~~~~~~~~~~~~~~~~~~~~

"""
from collections import OrderedDict

import sppas
from sppas.src.utils.makeunicode import sppasUnicode
from sppas.src.utils.fileutils import sppasGUID

# ---------------------------------------------------------------------------


class sppasMetaData(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Dictionary of meta data.

    Meta data keys and values are unicode strings.

    """
    def __init__(self):
        """ Create a sppasMetaData instance.
        Add a GUID in the dictionary of metadata, with key "id".

        """
        # Dictionary with key and value
        self.__metadata = OrderedDict()
        self.__metadata["id"] = sppasGUID().get()

        # Dictionary with key and description
        self.__metadescr = dict()

    # -----------------------------------------------------------------------

    def is_meta_key(self, entry):
        """ Check if an entry is a key in the list of metadata.

        :param entry: (str) Entry to check
        :returns: (Boolean)

        """
        return entry in self.__metadata

    # -----------------------------------------------------------------------

    def get_meta(self, entry):
        """ Return the value of the given key.
        Return an empty string if the given entry if not a key of metadata.

        :param entry: (str) Entry to be checked as a key.
        :returns: (str)

        """
        return self.__metadata.get(entry, "")

    # -----------------------------------------------------------------------

    def get_meta_keys(self):
        """ Return the list of metadata keys. """

        return self.__metadata.keys()

    # -----------------------------------------------------------------------

    def set_meta(self, key, value, description=None):
        """ Set or update a metadata.

        :param key: (str) The key of the metadata.
        :param value: (str) The value assigned to the key.
        :param description: (str) An optional description of this metadata.

        key, value and description are formatted and stored in unicode.

        """
        su = sppasUnicode(key)
        key = su.to_strip()

        su = sppasUnicode(value)
        value = su.to_strip()

        self.__metadata[key] = value

        # Add the optional description
        if description is not None:
            su = sppasUnicode(description)
            descr = su.to_strip()
            self.__metadescr[key] = descr

    # -----------------------------------------------------------------------

    def pop_meta(self, key):
        """ Remove a metadata from its key.

        :param key: (str)

        """
        if key in self.__metadata:
            del self.__metadata[key]
        if key in self.__metadescr:
            del self.__metadescr[key]

# ---------------------------------------------------------------------------


class sppasDefaultMeta(sppasMetaData):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Dictionary of default meta data in SPPAS.

    Many annotation tools are using metadata... Moreover, each annotation
    tool is encoding data with its own formalism. SPPAS aio API enables
    metadata to store information related to the read data in order to
    give them back when writing the data, either in the same file format
    or to export in another format. Such option is possible only if some
    kind of "generic" metadata names are fixed.

    """
    def __init__(self):
        """ Instantiate a default set of meta data. """
        super(sppasDefaultMeta, self).__init__()

    # -----------------------------------------------------------------------

    def software_tool(self):
        """ Add metadata related to the annotation software tool.
        These metadata are assigned by sppasRW() when writing a file.

        """
        self.set_meta("software_name", "")
        self.set_meta("software_version", "")
        self.set_meta("software_url", "")
        self.set_meta("software_author", "")
        self.set_meta("software_contact", "")
        self.set_meta("software_copyright", "")

    # -----------------------------------------------------------------------

    def rw_file(self):
        """ Add metadata related to a file to read/write.
        These metadata are assigned by sppasRW() when reading and/or writing
        a file.

        """
        self.set_meta("file_name", "")
        self.set_meta("file_path", "")
        self.set_meta("file_ext", "")

        self.set_meta("file_reader", "")
        self.set_meta("file_read_date", "")

        self.set_meta("file_writer", "")
        self.set_meta("file_write_date", "")

        # annotation pro
        self.set_meta("file_version", "")
        self.set_meta("file_created_date", "")

    # -----------------------------------------------------------------------

    def project(self):
        """ Add metadata related to the annotation project. """

        # annotation pro
        self.set_meta("project_description", "")
        self.set_meta("project_corpus_owner", "")
        self.set_meta("project_corpus_type", "")
        self.set_meta("project_license", "")
        self.set_meta("project_environment", "")
        self.set_meta("project_collection", "")
        self.set_meta("project_title", "")
        self.set_meta("project_noises", "")

    # -----------------------------------------------------------------------

    def annotator(self):
        """ Add metadata related to an annotator. """

        # subtitle, transcriber
        self.set_meta("annotator_name", "")

        # transcriber
        self.set_meta("annotator_version", "")

        # transcriber
        self.set_meta("annotator_version_date", "")

    # -----------------------------------------------------------------------

    def speaker(self):
        """ Add metadata related to a speaker. """

        # sclite, transcriber
        self.set_meta("speaker_id", "", "Identifier of the speaker")

        # sclite, xtrans, transcriber
        self.set_meta("speaker_name", "", "Name of the speaker.")

        # xtrans, transcriber
        self.set_meta("speaker_type", "", "Speaker can be male, female, child or unknown.")

        # xtrans, transcriber
        self.set_meta("speaker_dialect", "", "Native or non-native speaker.")

        # transcriber
        self.set_meta("speaker_accent", "", "Accent of the speaker.")

        # transcriber
        self.set_meta("speaker_scope", "")  # (local|global)

        # other
        self.set_meta("speaker_current_occupation", "")
        self.set_meta("speaker_current_city", "")
        self.set_meta("speaker_current_country", "")

        self.set_meta("speaker_past_occupation", "")
        self.set_meta("speaker_education", "")

        self.set_meta("speaker_birth_date", "")
        self.set_meta("speaker_birth_city", "")
        self.set_meta("speaker_birth_country", "")

        self.set_meta("speaker_language", "")

    # -----------------------------------------------------------------------

    def tier(self):
        """ Add metadata related to a tier. """

        # transcriber
        self.set_meta("language", "")

        # audacity, annotation pro (IsClosed)
        self.set_meta("tier_is_minimized", "")

        # audacity, annotation pro
        self.set_meta("tier_height", "")

        # audacity, annotation pro
        self.set_meta("tier_is_selected", "")

    # -----------------------------------------------------------------------

    def media(self):
        """ Add metadata related to a media. """

        # sclite, xtrans
        self.set_meta("media_channel", "")

        # subtitle
        self.set_meta("media_shift_delay", "")

        # elan, annotation pro
        self.set_meta("media_file", "")
        self.set_meta("media_path", "")

        # annotation pro
        self.set_meta("media_sample_rate", "")

    # -----------------------------------------------------------------------

    def generic(self):
        """ Add metadata related to any level (document, tier, annotation...). """

        # transcriber, annotation pro
        self.set_meta("language", "")
