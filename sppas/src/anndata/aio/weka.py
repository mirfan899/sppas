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

    src.anndata.aio.weka.py
    ~~~~~~~~~~~~~~~~~~~~~~~

    Writers for file formats of WEKA software:
    Weka is a collection of machine learning algorithms for data mining tasks.

    https://www.cs.waikato.ac.nz/ml/weka/

    A file for weka has the following structure:

        1. Several lines starting by '%' with any kind of comment,
        2. The name of the relation,
        3. The set of attributes,
        4. The set of instances.

    WEKA is supporting 2 file formats:
        - ARFF: a simple ASCII file,
        - XRFF: an XML file which can be compressed with gzip.

    ARFF format description is at the following URL:
    http://weka.wikispaces.com/ARFF+(book+version)
    It's currently the only file format supported by SPPAS.

    :TODO: Support of XRFF file format.

"""
import codecs
from datetime import datetime

import sppas
from .basetrs import sppasBaseIO
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag
from ..annlocation import sppasPoint

from sppas.src.utils.makeunicode import sppasUnicode

# ----------------------------------------------------------------------------

# Maximum number of class to predict
MAX_CLASS_TAGS = 10

# Maximum of attributes to explicitly list. Others are mentioned with "STRING".
MAX_ATTRIBUTES_TAGS = 20

# ----------------------------------------------------------------------------


class sppasWEKA(sppasBaseIO):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS Base writer for ARFF and XRFF formats.

    """
    def __init__(self, name=None):
        """ Initialize a new sppasARFF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasBaseIO.__init__(self, name)

        self._max_class_tags = MAX_CLASS_TAGS
        self._max_attributes_tags = MAX_ATTRIBUTES_TAGS
        self._empty_annotation_tag = "none"
        self._uncertain_annotation_tag = "?"
        self._epsilon_proba = 0.001

        self._accept_multi_tiers = True
        self._accept_no_tiers = False
        self._accept_metadata = True
        self._accept_ctrl_vocab = True
        self._accept_media = False
        self._accept_hierarchy = False
        self._accept_point = True
        self._accept_interval = True
        self._accept_disjoint = True
        self._accept_alt_localization = False
        self._accept_alt_tag = True
        self._accept_radius = False
        self._accept_gaps = False
        self._accept_overlaps = True

    # -----------------------------------------------------------------
    # Getters and setters
    # -----------------------------------------------------------------

    def get_max_class_tags(self):
        """ Return the maximum number of tags for the class. """

        return self._max_class_tags

    # -----------------------------------------------------------------

    def set_max_class_tags(self, nb_tags):
        """ Set the maximum number of tags for a class.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        class tier

        """
        old = self._max_class_tags
        self._max_class_tags = nb_tags
        try:
            self.check_max_class_tags(nb_tags)
        except ValueError:
            self._max_class_tags = old
            raise

    # -----------------------------------------------------------------

    def check_max_class_tags(self, nb_tags):
        """ Check the maximum number of tags for the class.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        class tier

        """
        nb_tags = int(nb_tags)
        if nb_tags < 2:
            raise ValueError("The class must have at least 2 different tags.")
        if nb_tags > self._max_class_tags:
            raise ValueError("The class must have at max {:d} different tags."
                             "".format(self._max_class_tags))

    # -----------------------------------------------------------------

    def set_max_attributes_tags(self, nb_tags):
        """ Set the maximum number of tags for an attribute.
        Instead, the program won't list the attribute and will use 'STRING'.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        class tier

        """
        old = self._max_attributes_tags
        self._max_attributes_tags = nb_tags
        try:
            self.check_max_attributes_tags(nb_tags)
        except ValueError:
            self._max_attributes_tags = old
            raise

    # -----------------------------------------------------------------

    def check_max_attributes_tags(self, nb_tags):
        """ Check the maximum number of tags for an attribute.

        :param nb_tags: (int) Size of the controlled vocabulary of the
        attribute tier

        """
        nb_tags = int(nb_tags)
        if nb_tags < 1:
            raise ValueError("The attributes must have at least one tag.")
        if nb_tags > self._max_attributes_tags:
            raise ValueError("The attributes must have at max {:d} "
                             "different tags.".format(self._max_attributes_tags))

    # -----------------------------------------------------------------

    def set_empty_annotation_tag(self, tag_str):
        """ Fix the annotation tag that will be used to replace
        empty annotations.

        :param tag_str: (str)

        """
        tag_str = sppasUnicode(tag_str).clear_whitespace()
        if len(tag_str) > 0:
            self._empty_annotation_tag = tag_str
        else:
            raise ValueError('{:s} is not a valid tag.'.format(tag_str))

    # -----------------------------------------------------------------

    def set_uncertain_annotation_tag(self, tag_str):
        """ Fix the annotation tag that is used in the annotations to
        mention an uncertain label.

        :param tag_str: (str)

        """
        tag_str = sppasUnicode(tag_str).clear_whitespace()
        if len(tag_str) > 0:
            self._uncertain_annotation_tag = tag_str
        else:
            raise ValueError('{:s} is not a valid tag.'.format(tag_str))

    # -----------------------------------------------------------------
    # Validation methods
    # -----------------------------------------------------------------

    def check_metadata(self):
        """ Check the metadata and fix the variable members. """

        if self.is_meta_key("weka_max_class_tags") is True:
            self.set_max_class_tags(self.get_meta("weka_max_class_tags"))

        if self.is_meta_key("weka_max_attributes_tags") is True:
            self.set_max_attributes_tags(self.get_meta("weka_max_attributes_tags"))

        if self.is_meta_key("weka_empty_annotation_tag") is True:
            self.set_empty_annotation_tag(self.get_meta("weka_empty_annotation_tag"))

        if self.is_meta_key("weka_uncertain_annotation_tag") is True:
            self.set_uncertain_annotation_tag(self.get_meta("weka_uncertain_annotation_tag"))

    # -----------------------------------------------------------------

    def validate_annotations(self):
        """ Prepare data to be compatible.

        Convert tier names.
        Delete the existing controlled vocabularies and convert tags.

        """
        for tier in self:

            # Name of the tier.
            name = tier.get_name()
            tier.set_name(sppasUnicode(name).clear_whitespace())

            # Delete current controlled vocabulary.
            if tier.is_meta_key("weka_attribute") or tier.is_meta_key("weka_class"):
                if tier.get_ctrl_vocab() is not None:
                    tier.set_ctrl_vocab(None)

            # Convert annotation tags.
            for ann in tier:
                if ann.get_label() is not None:
                    label = ann.get_label()
                    if len(label) > 0:
                        for tag, score in label:
                            if tag.get_type() == "str":
                                # Replace whitespace by underscore and check for an empty tag.
                                tag_text = sppasUnicode(tag.get_content()).clear_whitespace()
                                if len(tag_text) == 0:
                                    if tier.is_meta_key("weka_class") is False:
                                        # The tag is empty. We have to fill it.
                                        tag_text = self._empty_annotation_tag
                                new_tag = sppasTag(tag_text)
                                # Set the new version of the tag to the label
                                if new_tag != tag:
                                    ann.remove_tag(tag)
                                    label.append(new_tag, score)
                    else:
                        # The annotation was not labelled. We have to do it.
                        label.append(sppasTag(self._empty_annotation_tag))

        # Set the controlled vocabularies
        self._create_ctrl_vocab()

    # -----------------------------------------------------------------

    def validate(self):
        """ Check the tiers to verify if everything is ok:

            1. A class is defined: "weka_class" in the metadata of a tier
            2. Attributes are fixed: "weka_attribute" in the metadata of at least one tier

        Raises ValueError if something is wrong.

        """
        if self.is_empty() is True:
            raise ValueError("Empty transcription. Nothing to do!")
        if len(self) == 1:
            raise ValueError("The transcription must contain at least 2 tiers.")

        class_tier = self._get_class_tier()
        if class_tier is None:
            raise ValueError("The transcription must contain a class.")
        if class_tier.is_empty():
            raise ValueError("The class tier must contain annotations.")
        self.check_max_class_tags(len(class_tier.get_ctrl_vocab()))

        has_attribute = list()
        for tier in self:
            if tier.is_meta_key("weka_attribute"):
                has_attribute.append(tier)
                if tier is class_tier:
                    raise ValueError("A tier can be either an attribute or "
                                     "the class. It can't be both.")
        if len(has_attribute) == 0:
            raise ValueError("The transcription must contain attributes.")
        for tier in has_attribute:
            if tier.is_empty():
                raise ValueError("The attributes tier {:s} must contain annotations.".format(tier.get_name()))

        has_time_slice = False
        if self.is_meta_key("weka_instance_step") is False:
            for tier in self:
                if tier.is_meta_key("weka_instance_anchor"):
                    has_time_slice = True
        else:
            try:
                time = float(self.get_meta("weka_instance_step"))
            except ValueError:
                raise ValueError("The instance step must be a numerical value. "
                                 "Not {:s}".format(self.get_meta("weka_instance_step")))
            has_time_slice = True
        if has_time_slice is False:
            raise ValueError("No instance time step nor anchor tier defined.")

    # -----------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------

    def _create_ctrl_vocab(self):
        """ Fix the controlled vocabularies of attribute tiers. """

        for tier in self:
            if tier.is_meta_key("weka_attribute") or tier.is_meta_key("weka_class"):
                tier.create_ctrl_vocab()

    # -----------------------------------------------------------------

    @staticmethod
    def _tier_is_attribute(tier):
        """ Check if a tier is an attribute for the classification.

        :param tier: (sppasTier)
        :returns: (is attribute, is numeric)

        """
        is_att = False
        is_numeric = False
        if tier.is_meta_key("weka_attribute"):
            is_att = True
            is_numeric = "numeric" in tier.get_meta("weka_attribute").lower()

        return is_att, is_numeric

    # -----------------------------------------------------------------

    def _get_class_tier(self):
        """ Return the tier which is the class. """

        for tier in self:
            if tier.is_meta_key("weka_class"):
                return tier

        return None

    # -----------------------------------------------------------------

    def _get_anchor_tier(self):
        """ Return the tier which will be used to create the instances. """

        for tier in self:
            if tier.is_meta_key("weka_instance_anchor"):
                return tier

        return None

    # -----------------------------------------------------------------

    def _get_label(self, localization, tier):
        """ Return the sppasLabel() at the given time in the given tier.

        TODO: return a sppasLabel() with all sppasTag and their scores
        depending on the observed tags during the localization (i.e.
        during the period including the vagueness) and not only at the
        midpoint of the localization.

        :param localization: (sppasPoint)
        :param tier: (sppasTier)

        :returns: sppasLabel()

        """
        mindex = tier.mindex(localization)
        if mindex != -1:
            return tier[mindex].get_label()

        return sppasLabel(sppasTag(self._empty_annotation_tag))

    # -----------------------------------------------------------------

    def _get_tag(self, localization, tier):
        """ Return the best sppasTag() of at the given time in the given tier.

        :param localization: (sppasPoint)
        :param tier: (sppasTier)

        :returns: sppasTag()

        """
        label = self._get_label(localization, tier)
        if label is None:
            return sppasTag(self._empty_annotation_tag)
        return label.get_best()

    # -----------------------------------------------------------------

    def _fix_instance_steps(self):
        """ Fix the time-points to create the instances and the
        tag of the class to predict by the classification system.

        :returns: List of (sppasPoint, tag content)

        """
        # The instances are created only if the class is labelled.
        class_tier = self._get_class_tier()

        # The localization point to start the instances
        time_value = class_tier.get_first_point().get_midpoint()

        # The localization point to finish the instances
        max_time = class_tier.get_last_point()

        # Create the list of all possible points for the instances
        all_points = list()

        # A timer is used to fix the steps
        if self.is_meta_key("weka_instance_step") is True:
            time_step = float(self.get_meta("weka_instance_step"))

            while time_value < max_time:
                # Fix the anchor point of the instance
                midpoint = time_value + (time_step/2.)
                radius = time_step/2.
                all_points.append(sppasPoint(midpoint, radius))
                # next...
                time_value += time_step

        # An anchor class is used to fix the steps
        else:
            anchor_tier = self._get_anchor_tier()

            for ann in anchor_tier:
                localization = ann.get_highest_localization()
                if localization.is_point():
                    all_points.append(localization)
                else:
                    # Fix the anchor point of the instance
                    duration = localization.get_duration()
                    midpoint = \
                        localization.get_begin().get_midpoint() + \
                        (duration.get_value()/2.)
                    radius = (duration.get_value() + duration.get_margin()) / 2.
                    all_points.append(sppasPoint(midpoint, radius))

        # Create the list of points for the instances
        instance_points = list()
        for point in all_points:
            # Fix the tag to predict by the classification system
            class_tag = self._get_tag(point, class_tier)
            # Append only if the class was labelled
            if class_tag != sppasTag(self._empty_annotation_tag):
                instance_points.append((point, class_tag.get_content()))

        return instance_points

    # -----------------------------------------------------------------

    @staticmethod
    def _scores_to_probas(label):
        """ Convert scores to probas. """

        function_score = label.get_function_score()
        if function_score is min:
            for tag in label:
                score = label.get_score(tag)
                label.set_score(tag, -score)
            label.set_function_score(max)

        total = float(sum(label.get_score(tag) for tag in label))
        for tag in label:
            score = label.get_score(tag)
            label.set_score(tag, float(score) / total)

# ----------------------------------------------------------------------------


class sppasARFF(sppasWEKA):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      SPPAS ARFF writer.

    The following metadata of the Transcription object can be defined:
        - weka_instance_step: time step for the data instances. Do not
        define if "weka_instance_anchor" is set to a tier.

    The following metadata can be defined in the tiers:
        - weka_attribute: is fixed if the tier will be used as attribute
        (i.e. its data will be part of the instances). The value can
        be "numeric" to use distributions of probabilities or
        "label" to use the annotation labels in the vector of parameters.
        - weka_class: is fixed to the tier with the annotation labels to
         be inferred by the classification system. No matter of the value.
        - weka_instance_anchor: is fixed if the tier has to be used to
        define the time intervals of the instances.

    """
    @staticmethod
    def detect(filename):
        try:
            with codecs.open(filename, 'r', 'utf-8') as fp:
                for i in range(200):
                    line = fp.readline()
                    if "@relation" in line.lower():
                        return True
        except Exception:
            return False

        return False

    # -----------------------------------------------------------------

    def __init__(self, name=None):
        """ Initialize a new sppasARFF instance.

        :param name: (str) This transcription name.

        """
        if name is None:
            name = self.__class__.__name__
        sppasWEKA.__init__(self, name)

    # -----------------------------------------------------------------
    # Write data
    # -----------------------------------------------------------------

    def write(self, filename):
        """ Write a RawText file.

        :param filename: (str)

        """
        with codecs.open(filename, 'w', sppas.encoding, buffering=8096) as fp:

            # Check metadata
            self.check_metadata()

            # Check the annotation tags.
            self.validate_annotations()

            # Check if the metadata are properly fixed.
            self.validate()

            # OK, we are ready to write
            sppasARFF._write_header(fp)
            self._write_metadata(fp)
            self._write_relation(fp)
            self._write_attributes(fp)
            self._write_data(fp)

            fp.close()

    # -----------------------------------------------------------------
    # Private
    # -----------------------------------------------------------------

    @staticmethod
    def _write_header(fp):
        """ Write a standard header in comments. """

        fp.write("% creator: {:s}\n".format(sppas.__name__))
        fp.write("% version: {:s}\n".format(sppas.__version__))
        fp.write("% date: {:s}\n".format(datetime.now().strftime("%Y-%m-%d")))
        fp.write("% author: {:s}\n".format(sppas.__author__))
        fp.write("% license: {:s}\n".format(sppas.__copyright__))
        fp.write("% \n")

    # -----------------------------------------------------------------

    def _write_metadata(self, fp):
        """ Write metadata in comments. """

        for key in self.get_meta_keys():
            value = self.get_meta(key)
            fp.write("% {:s}: {:s}\n".format(key, value))
        fp.write("\n\n")

    # -----------------------------------------------------------------

    def _write_relation(self, fp):
        """ Write the relation of the ARFF file. """

        fp.write("@RELATION {:s}\n".format(self.get_name()))
        fp.write("\n")

    # -----------------------------------------------------------------

    def _write_attributes(self, fp):
        """ Write the attributes of the ARFF file.
        Attributes are corresponding to the controlled vocabulary.
        They are the list of possible tags of the annotations, except
        for the numerical ones.

        It is supposed that the transcription has been already validated.

        """
        for tier in self:

            is_att, is_numeric = sppasWEKA._tier_is_attribute(tier)
            if is_att is False:
                continue

            if is_numeric is True:
                # Tags will be converted to probabilities
                for tag in tier.get_ctrl_vocab():
                    # Do not write an uncertain label in that situation.
                    if tag.get_content() != self._uncertain_annotation_tag:
                        attribute_name = tier.get_name() + "-" + tag.get_content()
                        fp.write("@ATTRIBUTES {:s} NUMERIC\n".format(attribute_name))
            else:
                # Either a generic "string" or we can explicitly fix the list
                if len(tier.get_ctrl_vocab()) > self._max_attributes_tags:
                    fp.write("@ATTRIBUTES {:s} STRING\n".format(tier.get_name()))
                else:
                    # The controlled vocabulary
                    fp.write("@ATTRIBUTES {:s} {{".format(tier.get_name()))
                    for tag in tier.get_ctrl_vocab():
                        fp.write("{:s} ".format(tag.get_content()))
                    fp.write("}\n")

        for tier in self:

            if tier.is_meta_key("weka_class"):
                # The controlled vocabulary
                fp.write("@ATTRIBUTES class {")
                for tag in tier.get_ctrl_vocab():
                    fp.write("{:s} ".format(tag.get_content()))
                fp.write("}\n")

        fp.write("\n")

    # -----------------------------------------------------------------

    def _write_data(self, fp):
        """ Write the data content of the ARFF file.
        Data are the tags of the annotations or distributions of
        probabilities.

        """
        steps = self._fix_instance_steps()

        fp.write("@DATA\n")
        for point, class_str in steps:
            self._write_data_instance(point, class_str, fp)

    # -----------------------------------------------------------------

    def _write_data_instance(self, point, class_str, fp):
        """ Write an instance of the data content of the ARFF file.

        * Each instance is represented on a single line, with carriage
        returns denoting the end of the instance.
        * Attribute values for each instance are delimited by commas.
        They must appear in the order that they were declared in the header.
        * Missing values are represented by a single question mark
        * Values of string and nominal attributes are case sensitive,
        and any that contain space must be quoted

        - tiers with points
        - tiers with boolean tags
        - tiers with int/float tags: should be converted to labels

        """
        fp.write(str(point))
        fp.write(";")

        # Create the instance of the interval with annotations of all
        # attribute tiers, followed by the class.
        for tier in self:

            is_att, is_numeric = sppasWEKA._tier_is_attribute(tier)
            if is_att is False:
                continue

            if is_numeric is True:

                label = self._get_label(point, tier)

                # Scores of observed tags are converted to probabilities
                self._scores_to_probas(label)

                # Score of un-observed tags are all set to an epsilon probability
                nb_eps_tags = len(tier.get_ctrl_vocab()) - len(label)
                epsilon = self._epsilon_proba
                if tier.is_meta_key('weka_epsilon'):
                    epsilon = float(tier.get_meta('weka_epsilon'))
                # ... if an uncertain tag is observed
                if label.contains(sppasTag(self._uncertain_annotation_tag)) is True:
                    score = label.get_score(sppasTag(self._uncertain_annotation_tag))
                    nb_eps_tags += 1
                    epsilon = score / float(nb_eps_tags)
                    label.remove(sppasTag(self._uncertain_annotation_tag))

                # All possible tags are written
                for tag in tier.get_ctrl_vocab():
                    proba = epsilon
                    if label.contains(tag) is True:
                        proba = label.get_score(tag) - (nb_eps_tags*epsilon)
                    fp.write(proba)
            else:
                tag = self._get_tag(point, tier)
                fp.write(tag.get_content()+",")

        fp.write(class_str + "\n")
