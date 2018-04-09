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

    src.anndata.aio.elan.py
    ~~~~~~~~~~~~~~~~~~~~~~~


"""
import time
import xml.etree.cElementTree as ET

import sppas
from sppas.src.resources.mapping import sppasMapping
from sppas.src.utils.datatype import sppasTime

from ..anndataexc import AnnDataTypeError
from ..anndataexc import AioNoTiersError
from ..anndataexc import AioEmptyTierError
from ..anndataexc import AioLocationTypeError
from ..anndataexc import AioError
from ..anndataexc import AioLocationTypeError
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..media import sppasMedia

from ..ctrlvocab import sppasCtrlVocab

from .basetrs import sppasBaseIO
from .aioutils import serialize_labels
from .aioutils import format_labels

# ---------------------------------------------------------------------------

ETYPES = {'iso12620',
          'ecv',
          'cve_id',
          'lexen_id',
          'resource_url'}

CONSTRAINTS = {
    'Time_Subdivision': "Time subdivision of parent annotation's time inte"
    'rval, no time gaps allowed within this interval',
    'Symbolic_Subdivision': 'Symbolic subdivision of a parent annotation. '
    'Annotations refering to the same parent are ordered',
    'Symbolic_Association': '1-1 association with a parent annotation',
    'Included_In': 'Time alignable annotations within the parent annotatio'
    "n's time interval, gaps are allowed"}

MIMES = {'wav': 'audio/x-wav',
         'mpg': 'video/mpeg',
         'mpeg': 'video/mpg',
         'xml': 'text/xml'}

# ---------------------------------------------------------------------------


class sppasEAF(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS ELAN EAF files reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of XRA format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with open(filename, 'r') as fp:
                for i in range(10):
                    line = fp.readline()
                    if "<ANNOTATION_DOCUMENT" in line:
                        return True
                fp.close()
        except IOError:
            return False

        return False

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasMLF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__

        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = True
        self._accept_media = True
        self._accept_hierarchy = True
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False  # to be verified

        self.default_extension = "eaf"

        # Information that are both used by ELAN and another software tool
        self._map_meta = sppasMapping()
        self._map_meta.add('PARTICIPANT', 'speaker_name')
        self._map_meta.add('ANNOTATOR', 'annotator_name')

        # ELAN only supports (and assumes) milliseconds.
        self.unit = 0.001
        self.time_slots = dict()

    # -----------------------------------------------------------------------

    def make_point(self, midpoint):
        """ Convert data into the appropriate sppasPoint().

        :param midpoint: (str) a time in ELAN format
        :returns: (sppasPoint) Representation of time in seconds with a (very)
        large vagueness!

        """
        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")

        return sppasPoint(midpoint * self.unit, radius=0.02)

    # -----------------------------------------------------------------------

    def format_point(self, second_count):
        """ Convert a time in seconds into ELAN format.

        :param second_count: (float) Time value (in seconds)
        :returns: (int) a time in ELAN format

        """
        try:
            second_count = float(second_count)
        except ValueError:
            raise AnnDataTypeError(second_count, "float")

        return int((1./self.unit) * float(second_count))

    # -----------------------------------------------------------------------
    # reader
    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read a ELAN EAF file.

        :param filename: (str) intput filename.

        """
        tree = ET.parse(filename)
        root = tree.getroot()
        self._parse_document(root)

        # License (0..*)
        for license_root in root.findall('LICENSE'):
            self._parse_license(license_root)

        # Header (1..1)
        self._parse_header(root.find('HEADER'))

        # Time order (1..1)
        self._parse_time_order(root.find('TIME_ORDER'))

        # Controlled vocabularies (0..*)
        for vocabulary_root in root.findall('CONTROLLED_VOCABULARY'):
            self._parse_ctrl_vocab(vocabulary_root)

        # Linguistic type

        # Locale

        # Language

        # Constraint

        # Lexicon ref

        # External ref

        # Tiers (0..*)
        for tier_root in root.findall('TIER'):
            self._parse_tier(tier_root)

    # -----------------------------------------------------------------------

    def _parse_document(self, document_root):
        """ Get the main element root.

        :param document_root: (ET) Main root.

        """
        if "DATE" in document_root.attrib:
            self.set_meta('file_created_date', document_root.attrib['DATE'])

        if "VERSION" in document_root.attrib:
            self.set_meta('file_format_version', document_root.attrib['VERSION'])

        if "AUTHOR" in document_root.attrib:
            self.set_meta('file_author', document_root.attrib['AUTHOR'])

    # -----------------------------------------------------------------------

    def _parse_license(self, license_root):
        """ Get an element 'LICENSE'.
        The current version of ELAN does not yet provide a means to edit
        or view the contents of the license.

        :param license_root: (ET) License root.

        """
        self.set_meta('file_license', license_root.text)

        if "LICENSE_URL" in license_root.attrib:
            self.set_meta('file_license_url', license_root.attrib['LICENSE_URL'])

    # -----------------------------------------------------------------------

    def _parse_header(self, header_root):
        """ Get the element 'HEADER'.
        There should be exactly one HEADER element. It can contain sequences
        of three elements and has two attributes.

        :param header_root: (ET) Header root.

        """
        # Fix the time unit
        unit_string = header_root.attrib['TIME_UNITS']
        if unit_string == 'seconds':
            # it should never happen if the EAF file was generated with Elan software
            self.unit = 1.0

        for media_root in header_root.findall('MEDIA_DESCRIPTOR'):
            self._parse_media_descriptor(media_root, header_root)

        for linked_root in header_root.findall('LINKED_FILE_DESCRIPTOR'):
            self._parse_media_descriptor(linked_root)

        for property_root in header_root.findall('PROPERTY'):
            self._parse_property(property_root)

    # -----------------------------------------------------------------------

    def _parse_media_descriptor(self, media_root, header_root):
        """ Get the elements 'MEDIA_DESCRIPTOR'.
        This element describes one primary media source.
        Create a sppasMedia instance and add it.

        :param media_root: (ET) Media root element.

        """
        media_url = media_root.attrib['MEDIA_URL']
        media_mime = media_root.attrib['MIME_TYPE']

        # Create the new Media and put all information in metadata
        media = sppasMedia(media_url, mime_type=media_mime)
        media.set_meta('media_source', 'primary')
        if 'RELATIVE_MEDIA_URL' in media_root.attrib:
            media.set_meta('RELATIVE_MEDIA_URL', media_root.attrib['RELATIVE_MEDIA_URL'])
        if 'TIME_ORIGIN' in media_root.attrib:
            media.set_meta('TIME_ORIGIN', media_root.attrib['TIME_ORIGIN'])
        if 'EXTRACTED_FROM' in media_root.attrib:
            media.set_meta('EXTRACTED_FROM', media_root.attrib['EXTRACTED_FROM'])

        # media identifier
        for property_root in header_root.findall('PROPERTY'):
            if 'NAME' in property_root.attrib:
                name = property_root.attrib['NAME']
                if name == 'media_id_'+media.get_filename():
                    media.set_meta('id', property_root.text)

        # Add media into sppasEAF();
        # but the media is not linked to tiers... Elan doesn't support it.
        self.add_media(media)

    # -----------------------------------------------------------------------

    def _parse_linked_file_descriptor(self, linked_root):
        """ Get the elements 'LINKED_FILE_DESCRIPTOR'.
        This element describes a “secondary”, additional source.
        Create a sppasMedia instance and add it.

        :param linked_root: (ET) Linked file descriptor root element.

        """
        media_url = linked_root.attrib['LINK_URL']
        media_mime = linked_root.attrib['MIME_TYPE']

        # Create the new Media and put all information in metadata
        media = sppasMedia(media_url, mime_type=media_mime)
        media.set_meta('media_source', 'secondary')
        if 'RELATIVE_LINK_URL' in linked_root.attrib:
            media.set_meta('RELATIVE_LINK_URL', linked_root.attrib['RELATIVE_LINK_URL'])
        if 'TIME_ORIGIN' in linked_root.attrib:
            media.set_meta('TIME_ORIGIN', linked_root.attrib['TIME_ORIGIN'])
        if 'ASSOCIATED_WITH' in linked_root.attrib:
            media.set_meta('ASSOCIATED_WITH', linked_root.attrib['ASSOCIATED_WITH'])

        # Add media into sppasEAF();
        # but the media is not linked to tiers... Elan doesn't support it.
        self.add_media(media)

    # -----------------------------------------------------------------------

    @staticmethod
    def _parse_property(self, property_root):
        """ Get the elements 'PROPERTY'.
        This is a general purpose element for storing key-value pairs.

        :param property_root: (ET) Property root element.

        """
        if 'NAME' in property_root.attrib:
            name = property_root.attrib['NAME']
            if name.startswith('media_id_') is False:
                self.set_meta(name, property_root.text)

    # -----------------------------------------------------------------------

    def _parse_time_order(self, time_order_root):
        """ Get the elements 'TIME_ORDER'.
        The TIME_ORDER element is a container for ordered TIME_SLOT elements.

        :param time_order_root: (ET) Time order root element.

        """
        time_slot_tuples = list()

        # parse each of the <TIME_SLOT> elements
        for time_slot_node in time_order_root.findall('TIME_SLOT'):
            time_id = time_slot_node.attrib['TIME_SLOT_ID']

            if 'TIME_VALUE' in time_order_root.attrib:
                value = self.make_point(time_slot_node.attrib['TIME_VALUE'])
                time_slot_tuples.append((time_id, value))

        #
        # # create a midpoint value for undefined TIME_VALUE
        # for i in range(1, len(time_slot_tuples) - 1):
        #     (id, val) = time_slot_tuples[i]
        #     if val is None:
        #         (prevId, prevVal) = time_slot_tuples[i - 1]
        #         (nextId, nextVal) = time_slot_tuples[i + 1]
        #         midPoint = (prevVal.GetMidpoint() +
        #                     nextVal.GetMidpoint()) / 2  # /!\ failed if nextVal is None
        #         newVal = TimePoint(midPoint, midPoint -
        #                            prevVal.GetMidpoint())
        #         time_slot_tuples[i] = (id, newVal)
        #
        self.time_slots = dict(time_slot_tuples)

    # -----------------------------------------------------------------------

    def _parse_ctrl_vocab(self, ctrl_vocab_root):
        """ Get the elements 'CONTROLLED_VOCABULARY'.

        :param ctrl_vocab_root: (ET) Controlled vocabulary root element.

        """
        # Create a sppasCtrlVocab instance
        vocab_id = ctrl_vocab_root.attrib['CV_ID']
        ctrl_vocab = sppasCtrlVocab(vocab_id)

        # Description
        if "DESCRIPTION" in ctrl_vocab_root.attrib:
            ctrl_vocab.set_description(ctrl_vocab_root.attrib['DESCRIPTION'])

        # Add the list of entries
        # if Elan eaf format < 2.8
        for entry_node in ctrl_vocab_root.findall('CV_ENTRY'):
            entry_text = entry_node.text
            entry_desc = ""
            if "DESCRIPTION" in entry_node.attrib:
                entry_desc = entry_node.attrib['DESCRIPTION']
            ctrl_vocab.add(sppasTag(entry_text), entry_desc)

        # if Elan eaf format = 2.8
        for entry_node in ctrl_vocab_root.findall('CV_ENTRY_ML'):
            entry_value_node = entry_node.find('CVE_VALUE')
            entry_text = entry_value_node.text
            entry_desc = ""
            if "DESCRIPTION" in entry_value_node.attrib:
                entry_desc = entry_value_node.attrib['DESCRIPTION']
            ctrl_vocab.add(sppasTag(entry_text), entry_desc)
        # mutually exclusive with a sequence of CV_ENTRY_ML elements:
        if 'EXT_REF' in ctrl_vocab_root.attrib:
            ctrl_vocab_url = ctrl_vocab_root.attrib['EXT_REF']
            # todo: open and parse the ctrl vocab external file.

        if len(ctrl_vocab) > 0:
            self.add_ctrl_vocab(ctrl_vocab)

    # -----------------------------------------------------------------------

    def _parse_tier(self, tier_root):
        """ Get the elements 'TIER'.

        :param tier_root: (ET) Tier root.

        """
        # The name is used as identifier.
        tier = self.create_tier(tier_root.attrib['TIER_ID'])

        # a reference to a type object that defines constraints for this tier
        linguistic_type = tier_root.attrib['LINGUISTIC_TYPE_REF']
        tier.set_meta('LINGUISTIC_TYPE_REF', linguistic_type)

        # other meta information
        for key in ['DEFAULT_LOCALE', 'PARTICIPANT', 'ANNOTATOR', 'LANG_REF']:
            if key in tier_root.attrib:
                tier.set_meta(key, tier_root.attrib[key])

        # get annotations
        if 'PARENT_REF' in tier_root.attrib:
            parent_ref = tier_root.attrib['PARENT_REF']
            self._parse_ref_tier(tier_root, tier, parent_ref)
        else:
            for annotation_root in tier_root.findall('ANNOTATION'):
                self._parse_alignable_annotation(annotation_root.find('ALIGNABLE_ANNOTATION'), tier)

    # -----------------------------------------------------------------

    def _parse_alignable_annotation(self, annotation_root, tier):
        """ Get the elements 'ANNOTATION'.

        :param annotation_root: (ET) Annotation root element.
        :param tier: (sppasTier) The tier to add the annotation

        """
        # Location
        begin_key = annotation_root.attrib['TIME_SLOT_REF1']
        begin_time = self.time_slots[begin_key]
        end_key = annotation_root.attrib['TIME_SLOT_REF2']
        end_time = self.time_slots[end_key]
        localization = sppasInterval(self.make_point(begin_time),
                                     self.make_point(end_time))

        # Labels
        text = list()
        for value_node in annotation_root.findall('ANNOTATION_VALUE'):
            if value_node.text is not None:
                text.append(value_node.text)
        labels = format_labels("\n".join(text), separator="\n")

        ann = tier.create_annotation(sppasLocation(localization), labels)

        # metadata
        if 'SVG_REF' in annotation_root.attrib:
            ann.set_meta('SVG_REF', annotation_root.attrib['SVG_REF'])

    # -----------------------------------------------------------------

    def _parse_ref_tier(self, tier_root, tier, parent_ref):
        """ Get the elements 'ANNOTATION'.

        :param tier_root: (ET) Tier root element.
        :param tier: (sppasTier) The tier to add the annotations
        :param parent_ref:

        """
        pass

    # -----------------------------------------------------------------------
    # writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """ Write an ELAN EAF file.

        :param filename: output filename.

        """
        root = sppasEAF._format_document()

        self._format_license(root)

        header_root = ET.SubElement(root, 'HEADER')

        for media in self.get_media_list():
            self._format_media(root, media)

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_document():
        """ Create a root element tree for EAF format. """

        root = ET.Element('ANNOTATION_DOCUMENT')
        author = sppas.__name__ + " " + sppas.__version__ + " (C) " + sppas.__author__

        root.set('AUTHOR', author)
        root.set('DATE', sppasTime().now)
        root.set('FORMAT', '2.8')
        root.set('VERSION', '2.8')
        root.set('xmlns:xsi',
                 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xsi:noNamespaceSchemaLocation',
                 'http://www.mpi.nl.tools/elan/EAFv2.8.xsd')

        return root

    # -----------------------------------------------------------------------

    def _format_license(self, root):
        """ Add an element 'LICENSE' into the ElementTree (if any).

        :param root: (ElementTree)
        :returns: (ET) License root.

        """
        if self.is_meta_key('file_license') or self.is_meta_key('file_license_url'):

            license_root = ET.SubElement(root, "LICENSE")

            if self.is_meta_key('file_license'):
                license_root.text = self.get_meta('file_license')
            if self.is_meta_key('file_license_url'):
                license_root.set('LICENSE_URL', self.get_meta('file_license_url'))

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_media(root, media):
        """ Add 'MEDIA' into the ElementTree (if any).

        :param root: (ElementTree)
        :param media: (sppasMedia)

        """
        # do not add the media if it's not a primary one
        if media.is_meta_key('media_source'):
            if media.get_meta('media_source') != 'primary':
                return

        media_root = ET.SubElement(root, 'MEDIA')

        # Write all the elements SPPAS has interpreted (required by EAF)
        media_root.set('MEDIA_URL', media.get_filename())
        media_root.set('MIME_TYPE', media.get_mime_type())

        # other EAF optional elements
        for key in ['RELATIVE_MEDIA_URL', 'TIME_ORIGIN', 'EXTRACTED_FROM']:
            if media.is_meta_key(key):
                media_root.set(key, media.get_meta(key))

        # In EAF, a media doesn't have an identifier.
        header_root = root.find('HEADER')
        property_root = ET.SubElement(header_root, 'PROPERTY')
        property_root.text = media.get_meta('id')
        property_root.set('NAME', "media_id_"+media.get_filename())
