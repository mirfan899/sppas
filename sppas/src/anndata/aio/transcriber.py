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
        {"lapsus"   ""}
        {"pi"       "[pi] inintelligible"}
        {"pif"      "[pif] inintelligible/faible"}
        {"ch"       "[ch] voix chuchotee"}
        {"lu"       "sigle lu"}
        {"epele"    "sigle epele"}
        {"19 cent..." ""}
    }

    # list of lexical events with descriptions
    lexical {
        {"?"        "orthographe incertaine"}
        {"^^"        "mot inconnu"}
        {"neologisme" ""}
        {"()"        "rupture de syntaxe"}
    }


"""
import codecs
import xml.etree.cElementTree as ET

from .basetrs import sppasBaseIO
from ..anndataexc import AnnDataTypeError
from ..media import sppasMedia
from ..ctrlvocab import sppasCtrlVocab
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

# ----------------------------------------------------------------------------

NO_SPK_TIER = "Trans-NoSpeaker"

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
            it.close()

        return '<!DOCTYPE Trans SYSTEM "trans' in doctype_line

    # -----------------------------------------------------------------

    @staticmethod
    def make_point(midpoint):
        """ In TRS, the localization is a time value, so a float. """

        try:
            midpoint = float(midpoint)
        except ValueError:
            raise AnnDataTypeError(midpoint, "float")
        return sppasPoint(midpoint, radius=0.005)

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
        self._accept_media = True
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
        try:
            tree = ET.parse(filename)
        except ET.ParseError:
            xmlp = ET.XMLParser(encoding="ISO-8859-1")
            tree = ET.parse(filename, parser=xmlp)
        root = tree.getroot()

        # Get metadata for self
        self._parse_metadata(root)

        # Speakers. One tier by speaker is created.
        self._parse_speakers(root.find('Speakers'))
        self.create_tier(NO_SPK_TIER)

        # Topics. Set the controlled vocabulary.
        topics = self.create_tier("Topics")
        sppasTRS._parse_topics(root.find('Topics'), topics)

        # Episodes. Fill the tier.
        episodes_tier = self.create_tier("Episodes")
        for episode_root in root.iter('Episode'):
            sppasTRS._parse_episode_attributes(episode_root, episodes_tier)

        # Episodes. Examine sections.
        section_tier = self.create_tier("Sections")
        for section_root in root.iter('Section'):
            self._parse_section_attributes(section_root, section_tier)

        # Episodes. Examine each "Turn" (content of tiers)
        self.create_tier("Turns")
        for turn_root in root.iter('Turn'):
            self._parse_turn(turn_root)

        # Create the hierarchy
        self.add_hierarchy_link("TimeAlignment", self.find('Turns'), self.find('Sections'))
        self.add_hierarchy_link("TimeAlignment", self.find('Sections'), self.find('Episodes'))
        self.add_hierarchy_link("TimeAlignment", self.find('Sections'), self.find('Topics'))
        # TurnRecordingQuality, TurnElocutionMode and TurnChannel should be
        # "TimeAssociation" of Turns but... sparse data (?) !

        # All turns/events were assigned to a speaker.
        if len(self.find(NO_SPK_TIER)) == 0:
            self.pop(self.get_tier_index(NO_SPK_TIER))

    # -----------------------------------------------------------------

    def _parse_metadata(self, root):
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
        # The media linked to this file.
        try:
            media_name = root.attrib['audio_filename']
            media = sppasMedia(media_name)
            self.set_media_list([media])
        except KeyError:
            pass

        # Name of the annotator.
        try:
            scribe = root.attrib['scribe']
            self.set_meta("annotator_name", scribe)
        except KeyError:
            pass

        # Version of the annotation.
        try:
            version = root.attrib['version']
            self.set_meta("annotator_version", version)
        except KeyError:
            pass

        # Date of the annotation.
        try:
            version_date = root.attrib['version_date']
            self.set_meta("annotator_version_date", version_date)
        except KeyError:
            pass

        # Language of the annotation.
        try:
            lang = root.attrib['xml:lang']
            self.set_meta("language", lang)
        except KeyError:
            pass

    # -----------------------------------------------------------------

    def _parse_speakers(self, spk_root):
        """ Read the <Speakers> element and create tiers.

        <!ELEMENT Speakers (Speaker*)>
        <!ATTLIST Speakers>

        <!ELEMENT Speaker EMPTY>
        <!ATTLIST Speaker
            id		    ID		#REQUIRED
            name		CDATA		#REQUIRED
            check		(yes|no)	#IMPLIED
            type 		(male|female|child|unknown)	#IMPLIED
            dialect		(native|nonnative)		#IMPLIED
            accent		CDATA		#IMPLIED
            scope		(local|global)	#IMPLIED
        >
        :param spk_root: (ET) XML Element tree root.

        """
        if spk_root is not None:
            for spk_node in spk_root.findall('Speaker'):
                # Speaker identifier -> new tier
                try:
                    value = spk_node.attrib['id']
                    tier = self.create_tier("Trans-" + value)
                    tier.set_meta("speaker_id", value)
                except KeyError:
                    continue
                # Speaker name: CDATA
                try:
                    tier.set_meta("speaker_name", spk_node.attrib['name'])
                except KeyError:
                    pass
                # Speaker type: male/female/child/unknown
                try:
                    tier.set_meta("speaker_type", spk_node.attrib['type'])
                except KeyError:
                    pass
                # "spelling checked" for speakers whose name has been checked: yes/no
                try:
                    tier.set_meta("speaker_check", spk_node.attrib['check'])
                except KeyError:
                    pass
                # Speaker dialect: native/nonnative
                try:
                    tier.set_meta("speaker_dialect", spk_node.attrib['dialect'])
                except KeyError:
                    pass
                # Speaker accent: CDATA
                try:
                    tier.set_meta("speaker_accent", spk_node.attrib['accent'])
                except KeyError:
                    pass
                # Speaker scope: local/global
                try:
                    tier.set_meta("speaker_scope", spk_node.attrib['scope'])
                except KeyError:
                    pass

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_topics(topic_root, topic_tier):
        """ Read the <Topics> element and create a tier.
        The topics and their description are stored in a controlled
        vocabulary.

        <!ELEMENT Topics (Topic*)>
        <!ATTLIST Topics>

        <!ELEMENT Topic EMPTY>
        <!ATTLIST Topic
            id		ID		#REQUIRED
            desc	CDATA	#REQUIRED
        >

        :param topic_root: (ET) XML Element tree root.
        :param topic_tier: (sppasTier) Tier to store topic segmentation

        """
        if topic_root is None:
            return

        # assign the vocabulary.
        ctrl_vocab = sppasCtrlVocab('topics')
        for topic_node in topic_root.findall('Topic'):
            # Topic identifier
            try:
                topic_id = topic_node.attrib['id']
            except KeyError:
                continue
            # Topic description: CDATA
            try:
                topic_desc = topic_node.attrib['desc']
            except KeyError:
                topic_desc = ""
            # Add an entry in the controlled vocabulary
            ctrl_vocab.add(sppasTag(topic_id), topic_desc)

        topic_tier.set_ctrl_vocab(ctrl_vocab)

    # -----------------------------------------------------------------

    @staticmethod
    def _parse_episode_attributes(episode_root, episodes_tier):
        """ Read the episode attributes.

        <!ELEMENT Episode (Section*)>
        <!ATTLIST Episode
        program		CDATA		#IMPLIED
        air_date	CDATA		#IMPLIED
        >

        :param episode_root: (ET) XML Element tree root.

        """
        if episode_root is None:
            return
        if len(episode_root) == 0:
            # no sections in this episode.
            return

        # Get this episode information
        begin = episode_root[0].attrib['startTime']
        end = episode_root[-1].attrib['endTime']
        try:
            program = episode_root.attrib['program']
        except KeyError:
            program = "episode"

        # Add the episode in the tier
        episodes_tier.create_annotation(
            sppasLocation(
                sppasInterval(
                    sppasTRS.make_point(begin),
                    sppasTRS.make_point(end))),
            sppasLabel(sppasTag(program)))

    # -----------------------------------------------------------------

    def _parse_section_attributes(self, section_root, section_tier):
        """ Read the section attributes.
        Sections are mainly used to segment the topics and to mention
        un-transcribed segments.

        <!ELEMENT Section (Turn*)>
        <!ATTLIST Section
        type		(report | nontrans | filler)	#REQUIRED
        topic		IDREF		#IMPLIED
        startTime	CDATA		#REQUIRED
        endTime		CDATA		#REQUIRED
        >

        :param section_root: (ET) XML Element tree root.

        """
        if section_root is None:
            return

        # Get the location of the section
        begin = section_root.attrib['startTime']
        end = section_root.attrib['endTime']
        location = sppasLocation(sppasInterval(sppasTRS.make_point(begin),
                                               sppasTRS.make_point(end)))

        # Check if it's a non-transcribed section
        section_type = self.__parse_type_in_section(section_root, location)

        # Check the topic
        self.__parse_topic_in_section(section_root, location)

        # Add the section in the tier
        section_tier.create_annotation(location, sppasLabel(sppasTag(section_type)))

    # -----------------------------------------------------------------

    def _parse_turn_attributes(self, turn_root):
        """ Read the turn attributes and fill the tiers.

        <!ATTLIST Turn
        speaker		IDREFS		#IMPLIED
        startTime	CDATA		#REQUIRED
        endTime		CDATA		#REQUIRED
        mode		(spontaneous|planned)	#IMPLIED
        fidelity	(high|medium|low)		#IMPLIED
        channel		(telephone|studio)		#IMPLIED
        >

        :param turn_root: (ET) XML Element tree root.
        :returns: (list) the tiers of the turn (i.e. speakers...)

        """
        if turn_root is None:
            return

        # Get the location of the turn
        begin = sppasTRS.make_point(turn_root.attrib['startTime'])
        end = sppasTRS.make_point(turn_root.attrib['endTime'])
        location = sppasLocation(sppasInterval(begin, end))

        self.__parse_mode_in_turn(turn_root, location)
        self.__parse_fidelity_in_turn(turn_root, location)
        self.__parse_channel_in_turn(turn_root, location)

        try:
            tiers = []
            speakers = turn_root.attrib['speaker']
            for speaker in speakers.split():
                tier = self.find("Trans-" + speaker)
                tiers.append(tier)
        except KeyError:
            pass

        return tiers, begin, end

    # -----------------------------------------------------------------

    def _parse_turn(self, turn_root):
        """ Fill a tier with the content of a turn.

        <!ELEMENT Turn (#PCDATA|Sync|Background|Comment|Who|Vocal|Event)*>

        :param turn_root: (ET) XML Element tree root.

        """
        # the turn attributes
        # -------------------

        tiers, turn_begin, turn_end = self._parse_turn_attributes(turn_root)
        tier = None
        if len(tiers) == 0:
            tier = self.find(NO_SPK_TIER)
            tiers.append(tier)
        elif len(tiers) == 1:
            tier = tiers[0]
        turn_tier = self.find("Turns")
        turn_tier.create_annotation(
            sppasLocation(sppasInterval(turn_begin, turn_end)),
            sppasLabel(sppasTag('turn')))

        # the content of the turn
        # -----------------------

        # PCDATA: handle text directly inside the Turn
        if turn_root.text.strip() != '':
            # create new annotation covering the whole turn.
            # will eventually be reduced by the rest of the turn content.
            prev_ann = sppasTRS.__create_annotation(turn_begin, turn_end, turn_root.text)
            turn_tier.add(prev_ann)
        else:
            prev_ann = None

        begin = turn_begin
        for node in turn_root.iter():

            if node.tag == 'Sync':
                begin = sppasTRS.make_point(node.attrib['time'])
                # Update the end of the previous annotation to the current value
                if prev_ann is not None:
                    prev_ann.get_location().get_best().set_end(begin)

            elif node.tag == 'Background':
                pass

            elif node.tag == 'Comment':
                pass

            elif node.tag == 'Who':
                # Update the tier to be annotated
                tier_index = int(node.attrib['nb']) - 1
                tier = tiers[tier_index]

            elif node.tag == 'Vocal':
                pass

            elif node.tag == 'Event':
                if prev_ann is None:
                    prev_ann = sppasTRS.__create_annotation(begin, turn_end, node.tail)
                    tier.add(prev_ann)
                sppasTRS.__append_event_in_label(node, prev_ann)

            # ----------
            # PCDATA: handle text directly inside the Turn
            if node.tail.strip() != "":
                # create new annotation covering the rest of the turn.
                # will eventually be reduced by the rest of the turn content.
                new_ann = sppasTRS.__create_annotation(begin, turn_end, node.tail)
                tier.add(new_ann)
                # end the previous annotation
                prev_ann = new_ann

        return

    # -----------------------------------------------------------------
    # Private - parse attributes
    # -----------------------------------------------------------------

    @staticmethod
    def __append_event_in_label(node_event, annotation):
        """
        <!ATTLIST Event
        type		(noise|lexical|pronounce|language)	"noise"
        extent		(begin|end|previous|next|instantaneous)	"instantaneous"
        desc		CDATA		#REQUIRED
        >

        :param node_event:
        :param annotation:

        """
        description = node_event.attrib['desc']
        extent = (node_event.attrib['extent']
                  if 'extent' in node_event.attrib
                  else '')

        if description == 'rire':
            if extent == 'begin' or extent == 'end':
                sppasTRS.__append_text_in_label(annotation, ' @@ ')
            else:
                sppasTRS.__append_text_in_label(annotation, ' @ ')
        elif description == 'i':
            sppasTRS.__append_text_in_label(annotation, ' * ')
        else:
            sppasTRS.__append_text_in_label(annotation, '(%s) ' % description)

    # -----------------------------------------------------------------

    @staticmethod
    def __append_text_in_label(annotation, text):
        old_tag = annotation.get_label().get_best()
        old_text = old_tag.get_content()
        old_tag.set_content(old_text + text)

    # -----------------------------------------------------------------

    @staticmethod
    def __create_annotation(begin, end, text):
        return sppasAnnotation(
            sppasLocation(sppasInterval(begin, end)),
            sppasLabel(sppasTag(text)))

    # -----------------------------------------------------------------

    def __parse_type_in_section(self, section_root, location):
        """ Extract the type of a section. """

        try:
            section_type = section_root.attrib['type']
        except KeyError:
            return "undefined"

        if section_type == "nontrans":
            # Add this section into a "Non-Transcribed tier"
            dummies = self.find('Dummies')
            if dummies is None:
                dummies = self.create_tier("Dummies")
                dummies.create_annotation(location, sppasLabel(sppasTag("dummy")))

        return section_type

    # -----------------------------------------------------------------

    def __parse_topic_in_section(self, section_root, location):
        """ Extract the topic of a section. """

        try:
            section_topic = section_root.attrib['topic']
        except KeyError:
            return

        # Append this section in the Topics tier
        topics = self.find('Topics')
        topics.create_annotation(location, sppasLabel(sppasTag(section_topic)))

    # -----------------------------------------------------------------

    def __parse_mode_in_turn(self, turn_root, location):
        """ Extract the mode of a turn. """

        try:
            mode = turn_root.attrib['mode']
        except KeyError:
            return

        mode_tier = self.find('TurnElocutionMode')
        if mode_tier is None:
            mode_tier = self.create_tier('TurnElocutionMode')
            ctrl = sppasCtrlVocab('mode', description="Elocution mode")
            ctrl.add(sppasTag('spontaneous'))
            ctrl.add(sppasTag('planned'))
            mode_tier.set_ctrl_vocab(ctrl)

        mode_tier.create_annotation(location, sppasLabel(sppasTag(mode)))

    # -----------------------------------------------------------------

    def __parse_fidelity_in_turn(self, turn_root, location):
        """ Extract the fidelity of a turn. """

        try:
            fidelity = turn_root.attrib['fidelity']
        except KeyError:
            return

        fidelity_tier = self.find('TurnRecordingQuality')
        if fidelity_tier is None:
            fidelity_tier = self.create_tier('TurnRecordingQuality')
            ctrl = sppasCtrlVocab('fidelity', description="Recording quality")
            ctrl.add(sppasTag('high'))
            ctrl.add(sppasTag('medium'))
            ctrl.add(sppasTag('low'))
            fidelity_tier.set_ctrl_vocab(ctrl)

        fidelity_tier.create_annotation(location, sppasLabel(sppasTag(fidelity)))

    # -----------------------------------------------------------------

    def __parse_channel_in_turn(self, turn_root, location):
        """ Extract the channel of a turn. """

        try:
            channel = turn_root.attrib['channel']
        except KeyError:
            return

        channel_tier = self.find('TurnChannel')
        if channel_tier is None:
            channel_tier = self.create_tier('TurnChannel')
            ctrl = sppasCtrlVocab('channel', description="Recording quality")
            ctrl.add(sppasTag('studio'))
            ctrl.add(sppasTag('telephone'))
            channel_tier.set_ctrl_vocab(ctrl)

        channel_tier.create_annotation(location, sppasLabel(sppasTag(channel)))
