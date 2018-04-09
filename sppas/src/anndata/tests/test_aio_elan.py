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

    src.anndata.tests.test_aio_elan.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      Test the reader/writer of ELAN files.

"""
import unittest
import os.path
import xml.etree.cElementTree as ET

import sppas
from sppas.src.utils.datatype import sppasTime
from ..aio.elan import sppasEAF
from ..annlocation.point import sppasPoint
from ..tier import sppasTier
from ..media import sppasMedia


DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestEAF(unittest.TestCase):
    """
    Test reader/writer of EAF files.

    """
    def test_detect(self):
        """ Test the file format detection method. """

        for filename in os.listdir(DATA):
            f = os.path.join(DATA, filename)
            if filename.endswith(sppasEAF().default_extension):
                self.assertTrue(sppasEAF.detect(f))
            else:
                self.assertFalse(sppasEAF.detect(f))

    # -----------------------------------------------------------------------

    def test_members(self):
        txt = sppasEAF()
        self.assertTrue(txt.multi_tiers_support())
        self.assertTrue(txt.no_tiers_support())
        self.assertTrue(txt.metadata_support())
        self.assertTrue(txt.ctrl_vocab_support())
        self.assertTrue(txt.media_support())
        self.assertTrue(txt.hierarchy_support())
        self.assertFalse(txt.point_support())
        self.assertTrue(txt.interval_support())
        self.assertFalse(txt.disjoint_support())
        self.assertFalse(txt.alternative_localization_support())
        self.assertFalse(txt.alternative_tag_support())
        self.assertFalse(txt.radius_support())
        self.assertTrue(txt.gaps_support())
        self.assertFalse(txt.overlaps_support())

    # -----------------------------------------------------------------------

    def test_make_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(sppasPoint(132.3), sppasEAF().make_point("132300"))
        self.assertEqual(sppasPoint(4.2), sppasEAF().make_point("4200."))

        with self.assertRaises(TypeError):
            sppasEAF().make_point("3a")

    # -----------------------------------------------------------------------

    def test_format_point(self):
        """ Convert data into the appropriate digit type, or not. """

        self.assertEqual(132300, sppasEAF().format_point(132.3))
        self.assertEqual(4200, sppasEAF().format_point(4.2))

        with self.assertRaises(TypeError):
            sppasEAF().format_point("3a")

    # -----------------------------------------------------------------------

    def test_document_root(self):
        """ document <-> root. """

        # create an element tree for EAF format
        root = sppasEAF._format_document()

        # then, create a Transcription from the element tree
        eaf = sppasEAF()
        eaf._parse_document(root)

        # so, test the result!
        author = sppas.__name__ + " " + sppas.__version__ + " (C) " + sppas.__author__
        self.assertEqual(sppasTime().now, eaf.get_meta("file_created_date"))
        self.assertEqual("2.8", eaf.get_meta("file_format_version"))
        self.assertEqual(author, eaf.get_meta("file_author"))

    # -----------------------------------------------------------------------

    def test_license(self):
        """ LICENSE <-> root element. """

        # create an element tree for EAF format
        root = sppasEAF._format_document()
        eaf = sppasEAF()

        # no license
        eaf._format_license(root)
        self.assertFalse(eaf.is_meta_key('file_license'))
        self.assertFalse(eaf.is_meta_key('file_license_url'))

        # a license (content only)
        eaf.set_meta('file_license', 'This is the license content of the document.')
        eaf._format_license(root)
        for license_root in root.findall('LICENSE'):
            eaf._parse_license(license_root)
        self.assertTrue(eaf.is_meta_key('file_license'))
        self.assertFalse(eaf.is_meta_key('file_license_url'))
        self.assertEqual('This is the license content of the document.', eaf.get_meta('file_license'))

        # a license (content + url)
        eaf.set_meta('file_license_url', 'filename.txt')
        eaf._format_license(root)
        for license_root in root.findall('LICENSE'):
            eaf._parse_license(license_root)
        self.assertTrue(eaf.is_meta_key('file_license'))
        self.assertTrue(eaf.is_meta_key('file_license_url'))
        self.assertEqual('This is the license content of the document.', eaf.get_meta('file_license'))
        self.assertEqual('filename.txt', eaf.get_meta('file_license_url'))

    # -----------------------------------------------------------------------

    def test_media(self):
        """ MEDIA_DESCRIPTOR <-> sppasMedia(). """

        root = sppasEAF._format_document()
        header_root = ET.SubElement(root, "HEADER")
        eaf = sppasEAF()
        media = sppasMedia("filename.wav")

        # Format eaf: from sppasMedia() to 'MEDIA'
        sppasEAF._format_media(root, media)

        # Parse the tree: from 'MEDTA' to eaf.MEDIA
        for child in root.iter('MEDIA'):
            eaf._parse_media_descriptor(child, header_root)

        self.assertEqual(len(eaf.get_media_list()), 1)
        eaf_media = eaf.get_media_list()[0]
        self.assertEqual(eaf_media, media)
        # self.assertEqual('', eaf_media.get_meta('RELATIVE_MEDIA_URL'))
        # self.assertEqual('', eaf_media.get_meta('TIME_ORIGIN'))
        # self.assertEqual('', eaf_media.get_meta('EXTRACTED_FROM'))

    # -----------------------------------------------------------------------

    def test_linked_file(self):
        """ LINKED_FILE_DESCRIPTOR <-> sppasMedia(). """
        pass

    # -----------------------------------------------------------------------

    def test_property(self):
        """ PROPERTY <-> sppasMetadata(). """
        pass

    # -----------------------------------------------------------------------


