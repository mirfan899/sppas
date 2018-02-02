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

    src.anndata.aio.transcriber.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # list of noise events with descriptions
    noise        {
        {"r"        "[r] respiration"}
        {"i"        "[i] inspiration"}
        {"e"        "[e] expiration"}
        {"n"        "[n] reniflement"}
        {"pf"        "[pf] soufle"}
        {""        ""}
        {"bb"        "[bb] bruit de bouche"}
        {"bg"        "[bg] bruit de gorge"}
        {"tx"        "[tx] toux, raclement, eternuement"}
        {"rire"        "[rire] rires du locuteur"}
        {"sif"        "[sif] sifflement du locuteur"}
        {""        ""}
        {"b"        "[b] bruit indetermine"}
        {"conv"        "[conv] conversations de fond"}
        {"pap"        "[pap] froissement de papiers"}
        {"shh"        "[shh] souffle electrique"}
        {"mic"        "[mic] bruits micro"}
        {"rire en fond" ""}
        {"toux en fond" ""}
        {"indicatif" ""}
        {"jingle" ""}
        {"top"    ""}
         {"musique" ""}
         {"applaude" "applaudissements"}
         {"nontrans" "[nontrans] segment"}
    }

    # list of pronounciation events with descriptions
    pronounce {
        {"*"        "mal prononce"}
        {"lapsus"        ""}
        {"pi"        "[pi] inintelligible"}
        {"pif"        "[pif] inintelligible/faible"}
        {"ch"        "[ch] voix chuchotee"}
        {"lu"                "sigle lu"}
        {"epele"        "sigle epele"}
        {"19 cent..." ""}
    }

    # list of lexical events with descriptions
    lexical {
        {"?"        "orthographe incertaine"}
        {"^^"        "mot inconnu"}
        {"n�ologisme" ""}
        {"()"        "rupture de syntaxe"}
    }


"""
import codecs
import xml.etree.cElementTree as ET

from .basetrs import sppasBaseIO
from ..annlabel.tag import sppasTag

# ----------------------------------------------------------------------------


class sppasTRS(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi
    :summary:      SPPAS reader for TRS format.

    """
    @staticmethod
    def detect(filename):
        """ Detect if filename if of TRS type.

        :param filename:
        :return:
        """
        with codecs.open(filename, 'r', "ISO-8859-1") as it:
            it.next()
            doctype_line = it.next().strip()

        return '<!DOCTYPE Trans SYSTEM "trans' in doctype_line

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasTRS instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
        self._accept_metadata = True
        self._accept_ctrl_vocab = False
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = False
        self._accept_interval = True
        self._accept_disjoint = False
        self._accept_alt_localization = False
        self._accept_alt_tag = False
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = False

    # -----------------------------------------------------------------

    def read(self, filename):
        """ Read a TRS file and fill the Transcription.

        <!ELEMENT Trans ((Speakers|Topics)*,Episode)>

        :param filename: (str)

        """
        tree = ET.parse(filename)
        root = tree.getroot()

        # Get metadata for self
        self.__parse_metadata(root)

        # One tier by speaker is created.
        self.__parse_speakers(root.find('Speakers'))
        if self.is_empty() is True:
            self.create_tier("Transcription")

        # Topics
        self.__parse_topics(root.find('Topics'))

        # Examine each "Turn" (content of tiers)
        for turn_root in root.iter('Turn'):
            tier = self.__parse_turn_metadata(turn_root)
            sppasTRS.__parse_turn(tier, turn_root)

    # -----------------------------------------------------------------

    def __parse_metadata(self, root):
        """ Get metadata from attributes of the main root.

        <!ATTLIST Trans
        audio_filename  CDATA           #IMPLIED
        scribe          CDATA           #IMPLIED
        xml:lang        NMTOKEN         #IMPLIED
        version         NMTOKEN         #IMPLIED
        version_date    CDATA           #IMPLIED
        elapsed_time    CDATA           "0"
        >

        :param root: (ET) Main XML Element tree root of a TRS file.

        """
        try:
            self.set_meta("scribe", root.attrib['scribe'])
        except Exception:
            pass

    # -----------------------------------------------------------------

    def __parse_speakers(self, spk_root):
        """ Read the <Speakers> element and create tiers.

        :param spk_root: (ET) XML Element tree root.

        """
        if spk_root is not None:
            for spk_node in spk_root.findall('Speaker'):
                # Speaker identifier -> new tier
                try:
                    value = spk_node.attrib['id']
                    tier = self.create_tier("Trans-" + value)
                    tier.set_meta("speaker_id", value)
                except Exception:
                    continue
                # Speaker name: CDATA
                try:
                    tier.set_meta("speaker_name", spk_node.attrib['name'])
                except Exception:
                    pass
                # Speaker type: male/female/child/unknown
                try:
                    tier.set_meta("speaker_type", spk_node.attrib['type'])
                except Exception:
                    pass
                # "spelling checked" for speakers whose name has been checked: yes/no
                try:
                    tier.set_meta("speaker_check", spk_node.attrib['check'])
                except Exception:
                    pass
                # Speaker dialect: native/nonnative
                try:
                    tier.set_meta("speaker_dialect", spk_node.attrib['dialect'])
                except Exception:
                    pass
                # Speaker accent: CDATA
                try:
                    tier.set_meta("speaker_accent", spk_node.attrib['accent'])
                except Exception:
                    pass
                # Speaker scope: local/global
                try:
                    tier.set_meta("speaker_scope", spk_node.attrib['scope'])
                except Exception:
                    pass

    # -----------------------------------------------------------------

    def __parse_topics(self, topic_root):
        """ Read the <Topics> element and create a tier.
        The topics and their description are stored in a controlled
        vocabulary.

        :param topic_root: (ET) XML Element tree root.

        """
        if topic_root is not None:
            # topics are stored into a tier
            tier = self.create_tier("Topics")
            tier.create_ctrl_vocab("topics")
            for topic_node in topic_root.findall('Topic'):
                # Topic identifier
                try:
                    topic_id = topic_node.attrib['id']
                except Exception:
                    continue
                # Topic description: CDATA
                try:
                    topic_desc = topic_node.attrib['desc']
                except Exception:
                    topic_desc = ""
                # Add an entry in the controlled vocabulary
                tier.get_ctrl_vocab().add(sppasTag(topic_id),
                                          topic_desc)

    # -----------------------------------------------------------------

    def __parse_sections(self, section_root):
        """ Read the section elements.

        <!ELEMENT Section (Turn*)>
        <!ATTLIST Section
        type		(report | nontrans | filler)	#REQUIRED
        topic		IDREF		#IMPLIED
        startTime	CDATA		#REQUIRED
        endTime		CDATA		#REQUIRED
        >

        :param section_root: (ET) XML Element tree root.

        """
        if section_root is not None:
            pass

    # -----------------------------------------------------------------

    def __parse_turn_metadata(self, turn_root):
        """ Read the turn attributes and fill metadata of the tier.

        <!ATTLIST Turn
        	speaker		IDREFS		#IMPLIED
        	startTime	CDATA		#REQUIRED
        	endTime		CDATA		#REQUIRED
            mode		(spontaneous|planned)	#IMPLIED
            fidelity	(high|medium|low)		#IMPLIED
            channel		(telephone|studio)		#IMPLIED
        >

        :param turn_root: (ET) XML Element tree root.
        :returns: the tier of the turn

        """
        # Turn speaker = the tier
        tier = self.find("Trans-" + turn_root.attrib['speaker'])
        return tier

    # -----------------------------------------------------------------

    @staticmethod
    def __parse_turn(tier, turn_root):
        """ Fill a tier with the content of a turn.

        <Turn startTime="0" endTime="184.64575" speaker="spk1"
              mode="spontaneous" fidelity="medium" channel="studio">
            ...
        </Turn>

        :param turn_root: (ET) XML Element tree root.

        """
        pass
