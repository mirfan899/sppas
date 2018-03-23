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

    src.anndata.aio.annotationpro.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    http://annotationpro.org/

"""
from datetime import datetime
import xml.etree.cElementTree as ET

import sppas

from ..media import sppasMedia
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..anndataexc import AioLineFormatError
from ..anndataexc import AnnDataTypeError

from .basetrs import sppasBaseIO
from .aioutils import merge_overlapping_annotations

# ---------------------------------------------------------------------------


class sppasANTX(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      AnnotationPro ANTX reader and writer.

    """
    @staticmethod
    def detect(filename):
        """ Check whether a file is of ANTX format or not.

        :param filename: (str) Name of the file to check.
        :returns: (bool)

        """
        try:
            with open(filename, 'r') as it:
                it.next()
                doctype_line = it.next().strip()
                it.close()
        except IOError:
            return False

        return 'AnnotationSystemDataSet' in doctype_line

    # -----------------------------------------------------------------------

    @staticmethod
    def make_point(midpoint, sample_rate=44100):
        """ The localization is a frame value, so an int. """

        try:
            midpoint = int(midpoint)
            midpoint = float(midpoint) / float(sample_rate)
        except ValueError:
            raise AnnDataTypeError(midpoint, "int")

        return sppasPoint(midpoint, radius=0.005)

    # -----------------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasANTX instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = True
        self._accept_metadata = True
        self._accept_ctrl_vocab = False
        self._accept_media = True
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = True
        self._accept_overlaps = False

        self.default_extension = "antx"
        self.__id_tier_map = dict()

    # -----------------------------------------------------------------------

    def read(self, filename):
        """ Read an ANTX file and fill the Transcription.

        :param filename: (str)

        """
        self.__id_tier_map = dict()
        tree = ET.parse(filename)
        root = tree.getroot()
        uri = root.tag[:root.tag.index('}')+1]

        for child in tree.iter(tag=uri+'Configuration'):
            self._read_configuration(child, uri)

        for child in tree.iter(tag=uri+"AudioFile"):
            self._read_audiofile(child, uri)

        for child in tree.iter(tag=uri+"Layer"):
            self._read_layer(child, uri)

        for child in tree.iter(tag=uri+"Segment"):
            self._read_segment(child, uri)

    # -----------------------------------------------------------------------

    def _read_configuration(self, configuration_root, uri):
        """ Get the elements 'Configuration' """

        key_tag = configuration_root.find(uri+'Key').text
        if key_tag is not None:
            new_key = key_tag.replace(uri, '')
            new_value = configuration_root.find(uri+'Value').text
            if new_key is not None:
                self.set_meta(new_key, new_value)

    # -----------------------------------------------------------------------

    def _read_audiofile(self, audio_root, uri):
        """ Get the elements 'AudioFile'. """

        media_id = audio_root.find(uri + 'Id').text.replace(uri, '')
        media_url = audio_root.find(uri + 'FileName').text
        media = sppasMedia(media_url)

        # Put all information in metadata of Media
        media.set_meta("id", media_id)
        for node in audio_root:
            if node.text is not None:
                media.set_meta(node.tag.replace(uri, ''), node.text)

        self.add_media(media)

    # -----------------------------------------------------------------------

    def _read_layer(self, tier_root, uri):
        """ Get the elements 'Layer'. """

        tier_name = tier_root.find(uri + 'Name').text
        tier = self.create_tier(tier_name)

        # Put all other information in metadata
        for node in tier_root:
            if node.text is not None:
                if "Id" in node.tag:
                    self.__id_tier_map[node.text] = tier
                    tier.set_meta('id', node.text)
                elif 'Name' not in node.tag:
                    tier.set_meta(node.tag.replace(uri, ''), node.text)
                # IsSelected -> is_selected

    # -----------------------------------------------------------------------

    def _read_segment(self, annotation_root, uri):
        """ Get the elements 'Segment'. """

        # fix tier
        tier_id = annotation_root.find(uri + 'IdLayer').text
        tier = None
        for t in self:
            if t.get_meta(tier_id) != "":
                tier = t
                break
        if tier is None:
            raise AioLineFormatError(0, tier_id)

        # fix localization
        begin = float(annotation_root.find(uri + 'Start').text)
        duration = float(annotation_root.find(uri + 'Duration').text)
        end = begin + duration
        sample_rate = self.get_meta('samplerate', 44100)

        if end > begin:
            localization = sppasInterval(
                sppasANTX.make_point(begin, sample_rate),
                sppasANTX.make_point(end, sample_rate))
        else:
            localization = sppasANTX.make_point(begin)

        # fix tag and create annotation
        tag = sppasTag(annotation_root.find(uri + 'Label').text)
        ann = tier.create_annotation(sppasLocation(localization),
                                     sppasLabel(tag))

        # fix other information in metadata
        for node in annotation_root:
            if node.text is not None:
                key = node.tag.replace(uri, '')
                if key not in ['Id', 'IdLayer', 'Start', 'Duration', 'Label']:
                    ann.set_meta(key, node.text)
                elif key == 'Id':
                    ann.set_meta('id', node.text)

    # ----------------------------------------------------------------------
    # Writer
    # -----------------------------------------------------------------------

    def write(self, filename):
        """ Write an Antx file.

        :param filename:

        """
        try:
            root = ET.Element('AnnotationSystemDataSet')
            root.set('xmlns', 'http://tempuri.org/AnnotationSystemDataSet.xsd')

            # Write layers
            for tier in self:
                sppasANTX._format_tier(root, tier)

            # Write segments
            for tier in self:
                #if tier.is_point():
                #    tier = point2interval(tier, ANTX_RADIUS)
                tier = merge_overlapping_annotations(tier)
                for ann in tier:
                    self._format_segment(root, tier, ann)

            # Write media
            for media in self.get_media_list():
                if media:
                    sppasANTX._format_media(root, media)

            # Write configurations
            self._format_configuration(root)

            sppasANTX.indent(root)
            tree = ET.ElementTree(root)
            tree.write(filename, encoding=sppas.encoding, xml_declaration=True, method="xml")
            # TODO: add standalone="yes" in the declaration
            # (but not available with ElementTree)

        except Exception:
            # import traceback
            # print(traceback.format_exc())
            raise

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_media(root, media):
        """ Write the sppasMedia element. """

        media_root = ET.SubElement(root, 'AudioFile')

        # Write all the elements SPPAS has interpreted
        child_id = ET.SubElement(media_root, 'Id')
        child_id.text = media.get_meta('id')
        child_id = ET.SubElement(media_root, 'FileName')
        child_id.text = media.get_filename()

        # other ANTX required elements
        child = ET.SubElement(media_root, "Name")
        child.text = media.get_meta("Name", "NoName")

        child = ET.SubElement(media_root, "External")
        child.text = media.get_meta("External", "false")

        child = ET.SubElement(media_root, "Current")
        child.text = media.get_meta("Current", "false")

    # -----------------------------------------------------------------------

    def _format_configuration(self, root):
        """ Write the Configuration element. """

        now = datetime.now().strftime("%Y-%M-%d %H:%M")

        # File format version
        sppasANTX.__add_configuration(root, "Version", "5")

        # Author
        author = sppas.__name__ + " " + sppas.__version__ + " (C) " + sppas.__author__
        sppasANTX.__add_configuration(root, "Author", author)

        # FileVersion
        sppasANTX.__add_configuration(root, "FileVersion",
                                      self.get_meta("file_version", "1"))

        # SampleRate
        sppasANTX.__add_configuration(root, "SampleRate",
                                      self.get_meta("sample_rate", "44100"))

        # Created
        sppasANTX.__add_configuration(root, "Created",
                                      self.get_meta("file_created_date", now))

        # Modified
        sppasANTX.__add_configuration(root, "Modified",
                                      self.get_meta("file_write_date", now))

    # -----------------------------------------------------------------------

    @staticmethod
    def __add_configuration(root, key, value):
        """ Add a new 'Configuration' element in root. """

        conf_root = ET.SubElement(root, 'Configuration')
        child_key = ET.SubElement(conf_root, 'Key')
        child_key.text = key
        child_value = ET.SubElement(conf_root, 'Value')
        child_value.text = value

    # -----------------------------------------------------------------------

    @staticmethod
    def _format_tier(root, tier):
        """ Write a 'Layer' element and its content. """

        tier_root = ET.SubElement(root, 'Layer')

        # Write all the elements SPPAS has interpreted
        child_id = ET.SubElement(tier_root, 'Id')
        tier_id = tier.get_meta('id')
        child_id.text = tier_id

        child_name = ET.SubElement(tier_root, 'Name')
        child_name.text = tier.getN_name()

        # Layer required elements:
        # 'is_selected' and 'height' are shared with Audacity.
        child = ET.SubElement(tier_root, 'ForeColor')
        child.text = tier.get_meta("ForeColor", "-16777216")

        child = ET.SubElement(tier_root, 'BackColor')
        child.text = tier.get_meta("BackColor", "-3281999")

        child = ET.SubElement(tier_root, 'IsSelected')
        child.text = tier.get_meta("is_selected", "false")

        child = ET.SubElement(tier_root, 'Height')
        child.text = tier.get_meta("height", "70")

        # Layer optional elements:
        # is_closed is shared with Audacity
        child = ET.SubElement(tier_root, 'IsClosed')
        child.text = tier.get_meta("is_closed", "false")

        elt_opt_layer = {'CoordinateControlStyle': "0", 'IsLocked': "false",
                         'ShowOnSpectrogram': "false", 'ShowAsChart': "false",
                         'ChartMinimum': "-50", 'ChartMaximum': "50",
                         'ShowBoundaries': "true", 'IncludeInFrequency': "true",
                         'Parameter1Name': "Parameter 1", 'Parameter2Name': "Parameter 2",
                         'Parameter3Name': "Parameter 3",
                         'IsVisible': "true", 'FontSize': "10"}

        for key in elt_opt_layer:
            # here, we have to restore original upper/lower case for the key
            child = ET.SubElement(tier_root, key)
            child.text = tier.get_meta(key, elt_opt_layer[key])

    # -----------------------------------------------------------------------

    def _format_segment(self, root, tier, ann):
        segment_root = ET.SubElement(root, 'Segment')

        # Write all the elements SPPAS has interpreted
        child_id = ET.SubElement(segment_root, 'Id')            # Id
        child_id.text = ann.get_meta('id')

        child_id_layer = ET.SubElement(segment_root, 'IdLayer')  # IdLayer
        child_id_layer.text = tier.get_meta('id')

        child_id_label = ET.SubElement(segment_root, 'Label')    # Label
        child_id_label.text = sppasANTX._serialize_label(ann.get_label())

        child_id_start = ET.SubElement(segment_root, 'Start')    # Start
        child_id_dur = ET.SubElement(segment_root, 'Duration')   # Duration
        if ann.is_point():
            start = ann.get_location().get_lowest_localization()
        else:
            start = ann.get_location().get_best().get_begin().get_midpoint()
        duration = ann.get_location().get_best().get_duration().get_value()

        start *= float(self.get_meta('sample_rate', 44100))
        duration *= float(self.get_meta('sample_rate', 44100))
        child_id_start.text = str(start)
        child_id_dur.text = str(duration)

        # Segment required elements
        elt_segment = {'ForeColor': '-16777216', 'BackColor': '-1',
                       'BorderColor': '-16777216', 'IsSelected': 'false'}

        for key in elt_segment:
            child = ET.SubElement(segment_root, key)
            child.text = ann.get_meta(key, elt_segment[key])

        # Segment optional elements

        elt_opt_segment = {'Feature': None, 'Language': None, 'Group': None, 'Name': None,
                           'Parameter1': None, 'Parameter2': None, 'Parameter3': None,
                           'IsMarker': "false", 'Marker': None, 'RScript': None}

        for key, value in elt_opt_segment:
            child = ET.SubElement(segment_root, key)
            child.text = ann.get_meta(key, elt_opt_segment[key])

    # -----------------------------------------------------------------------

    @staticmethod
    def _serialize_label(label):
        """ Convert a label into a string. """

        if label is None:
            return ""

        if label.get_best() is None:
            return ""

        if label.get_best().is_empty():
            return ""

        return label.get_best().get_content()

    # -----------------------------------------------------------------------

    @staticmethod
    def indent(elem, level=0):
        """ Pretty indent.
        http://effbot.org/zone/element-lib.htm#prettyprint

        """
        i = "\n" + level * "\t"
        if len(elem) > 0:
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                if level < 2:
                    elem.tail = "\n" + i
                else:
                    elem.tail = i
            for elem in elem:
                sppasANTX.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
