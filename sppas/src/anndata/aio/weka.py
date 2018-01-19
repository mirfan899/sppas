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

    Writer for the ARFF file format of WEKA software:
    Weka is a collection of machine learning algorithms for data mining tasks.

    https://www.cs.waikato.ac.nz/ml/weka/

"""
import codecs
from datetime import datetime

import sppas
from .basetrs import sppasBaseIO

# ----------------------------------------------------------------------------


class sppasARFF(sppasBaseIO):
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
        sppasBaseIO.__init__(self, name)

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

    def write(self, filename):
        """ Write a RawText file.

        :param filename: (str)

        """
        with codecs.open(filename, 'w', sppas.encoding, buffering=8096) as fp:

            if self.is_empty() is True:
                return

            sppasARFF._write_header(fp)
            self._write_metadata(fp)
            self._write_relation(fp)
            self._write_attributes(fp)
            self._write_data(fp)

            fp.close()

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

        fp.write("@RELATION {:s}".format(self.get_name()))
        fp.write("\n")

    # -----------------------------------------------------------------

    def _write_attributes(self, fp):
        """ Write the attributes of the ARFF file.
        Attributes are corresponding to the controlled vocabulary.
        They are the list of possible tags of the annotations, except
        for the numerical ones.
        """
        has_attributes = False
        for tier in self:
            is_att = False
            is_numeric = False
            if tier.is_meta_key("weka_attribute"):
                has_attributes = True
                is_att = True
                is_numeric = tier.get_meta("weka_attribute")

            if is_att is False:
                continue

            if is_numeric is True:
                # Tags will be converted to probabilities
                fp.write("@ATTRIBUTES {:s} NUMERIC".format(tier.get_name()))
                fp.write("\n")
            else:
                # The controlled vocabulary
                fp.write("@ATTRIBUTES {:s} {".format(tier.get_name()))
                for tag in tier.get_ctrl_vocab():
                    fp.write("{:s} ".format(tag.get_content()))
                fp.write("}\n")

        if has_attributes is False:
            raise ValueError("No attribute tier was defined.")

        has_class = False
        for tier in self:
            if tier.is_meta_key("weka_class"):
                has_class = True
                # The controlled vocabulary
                fp.write("@ATTRIBUTES class {")
                for tag in tier.get_ctrl_vocab():
                    fp.write("{:s} ".format(tag.get_content()))
                fp.write("}\n\n")

        if has_class is False:
            raise ValueError("No class tier was defined.")

    # -----------------------------------------------------------------

    def _write_data(self, fp):
        """ Write the data content of the ARFF file.
        Data are the tags of the annotations or distributions of
        probabilities.
        """
        intervals = list()
        if self.is_meta_key("weka_instance_step") is True:
            time_step = float(self.get_meta("weka_instance_step"))
            # From... To... depends on the class.
            time_value = 0
            max_time = 0
            for tier in self:
                if tier.is_meta_key("weka_class"):
                    time_value = tier.get_first_point()
                    max_time = tier.get_last_point()

            while time_value < max_time:
                intervals.append(time_value)
                time_value += time_step

        else:
            # Create the list of intervals for the instances
            for tier in self:
                if tier.is_meta_key("weka_instance_anchor"):
                    for ann in tier:
                        localization = ann.get_highest_localization()
                        if localization.is_point():
                            intervals.append(
                                (localization.get_midpoint() - localization.get_radius(),
                                 localization.get_midpoint() + localization.get_radius()))
                        else:
                            intervals.append(
                                (localization.get_begin().get_midpoint(),
                                 localization.get_end().get_midpoint()))
                    break
        if len(intervals) == 0:
            raise ValueError("No instance time step nor anchor tier defined.")

        for (b, e) in intervals:
            self._write_data_instance(b, e, fp)

    # -----------------------------------------------------------------

    def _write_data_instance(self, begin, end, fp):
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
        # Check if the class has a tag. No class tag = no instance.

        for tier in self:
            pass
