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

    src.anndata.anndataexc.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Exceptions for anndata package.

"""
from sppas.src.config import sg
from . import t

ANN_DATA_ERROR = ":ERROR 1000: "
ANN_DATA_EQ_ERROR = ":ERROR 1010: "

ANN_UNK_TYPE_ERROR = ":ERROR 1050: "
ANN_DATA_TYPE_ERROR = ":ERROR 1100: "
ANN_DATA_EQ_TYPE_ERROR = ":ERROR 1105: "

ANN_DATA_INDEX_ERROR = ":ERROR 1200: "
ANN_DATA_KEY_ERROR = ":ERROR 1250: "

ANN_DATA_VALUE_ERROR = ":ERROR 1300: "
ANN_DATA_NEG_VALUE_ERROR = ":ERROR 1310: "

INTERVAL_BOUNDS_ERROR = ":ERROR 1120: "
CTRL_VOCAB_CONTAINS_ERROR = ":ERROR 1130: "
CTRL_VOCAB_SET_TIER_ERROR = ":ERROR 1132: "
TIER_APPEND_ERROR = ":ERROR 1140: "
TIER_ADD_ERROR = ":ERROR 1142: "
TIER_HIERARCHY_ERROR = ":ERROR 1144: "

TRS_ADD_ERROR = ":ERROR 1150: "
TRS_REMOVE_ERROR = ":ERROR 1152: "
TRS_INVALID_TIER_ERROR = ":ERROR 1160: "

HIERARCHY_ALIGNMENT_ERROR = ":ERROR 1170: "
HIERARCHY_ASSOCIATION_ERROR = ":ERROR 1172: "
HIERARCHY_PARENT_TIER_ERROR = ":ERROR 1174: "
HIERARCHY_CHILD_TIER_ERROR = ":ERROR 1176: "
HIERARCHY_ANCESTOR_TIER_ERROR = ":ERROR 1178: "

TAG_VALUE_ERROR = ":ERROR 1190: "

AIO_ERROR = ":ERROR 1400: "
AIO_ENCODING_ERROR = ":ERROR 1500: "
AIO_FILE_EXTENSION_ERROR = ":ERROR 1505: "
AIO_MULTI_TIERS_ERROR = ":ERROR 1510: "
AIO_NO_TIERS_ERROR = ":ERROR 1515: "
AIO_LINE_FORMAT_ERROR = ":ERROR 1520: "
AIO_FORMAT_ERROR = ":ERROR 1521: "
AIO_EMPTY_TIER_ERROR = ":ERROR 1525: "
AIO_LOCATION_TYPE_ERROR = ":ERROR 1530: "

# -----------------------------------------------------------------------


class AnnDataError(Exception):
    """ :ERROR 1000: ANN_DATA_ERROR.
    No annotated data file is defined.

    """
    def __init__(self):
        self.parameter = ANN_DATA_ERROR + (t.gettext(ANN_DATA_ERROR))

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataEqError(Exception):
    """ :ERROR 1010: ANN_DATA_EQ_ERROR.
    Values are expected to be equals but are {:s!s} and {:s!s}.

    """
    def __init__(self, v1, v2):
        self.parameter = ANN_DATA_EQ_ERROR + \
                         (t.gettext(ANN_DATA_EQ_ERROR)).format(v1, v2)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataTypeError(TypeError):
    """ :ERROR 1100: ANN_DATA_TYPE_ERROR.
    {!s:s} is not of the expected type '{:s}'.

    """
    def __init__(self, rtype, expected):
        self.parameter = ANN_DATA_TYPE_ERROR + \
                      (t.gettext(ANN_DATA_TYPE_ERROR)).format(rtype, expected)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnUnkTypeError(TypeError):
    """ :ERROR 1050: ANN_UNK_TYPE_ERROR.
    {!s:s} is not a valid type.

    """
    def __init__(self, rtype):
        self.parameter = ANN_UNK_TYPE_ERROR + \
                         (t.gettext(ANN_UNK_TYPE_ERROR)).format(rtype)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataIndexError(IndexError):
    """ :ERROR 1200: ANN_DATA_INDEX_ERROR.
    Invalid index value {:d}.

    """
    def __init__(self, index):
        self.parameter = ANN_DATA_INDEX_ERROR + \
                         (t.gettext(ANN_DATA_INDEX_ERROR)).format(index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataEqTypeError(TypeError):
    """ :ERROR 1105: ANN_DATA_EQ_TYPE_ERROR.
    {!s:s} is not of the same type as {!s:s}.

    """
    def __init__(self, obj, obj_ref):
        self.parameter = ANN_DATA_EQ_TYPE_ERROR + \
                      (t.gettext(ANN_DATA_EQ_TYPE_ERROR)).format(obj, obj_ref)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataValueError(ValueError):
    """ :ERROR 1300: ANN_DATA_VALUE_ERROR.
    Invalid value '{!s:s}' for '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = ANN_DATA_VALUE_ERROR + \
                    (t.gettext(ANN_DATA_VALUE_ERROR)).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataNegValueError(ValueError):
    """ :ERROR 1310: ANN_DATA_NEG_VALUE_ERROR.
    Expected a positive value. Got '{:f}'.

    """
    def __init__(self, value):
        self.parameter = ANN_DATA_NEG_VALUE_ERROR + \
                         (t.gettext(ANN_DATA_NEG_VALUE_ERROR)).format(value)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AnnDataKeyError(KeyError):
    """ :ERROR 1250: ANN_DATA_KEY_ERROR.
    Invalid key '{!s:s}' for data '{!s:s}'.

    """

    def __init__(self, data_name, value):
        self.parameter = ANN_DATA_KEY_ERROR + \
                      (t.gettext(ANN_DATA_KEY_ERROR)).format(value, data_name)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class IntervalBoundsError(ValueError):
    """ :ERROR 1120: INTERVAL_BOUNDS_ERROR.
    The begin must be strictly lesser than the end in an interval.
    Got: [{:s};{:s}].

    """
    def __init__(self, begin, end):
        self.parameter = INTERVAL_BOUNDS_ERROR + \
                         (t.gettext(INTERVAL_BOUNDS_ERROR)).format(begin, end)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CtrlVocabContainsError(ValueError):
    """ :ERROR 1130: CTRL_VOCAB_CONTAINS_ERROR.
    {:s} is not part of the controlled vocabulary.

    """
    def __init__(self, tag):
        self.parameter = CTRL_VOCAB_CONTAINS_ERROR + \
                         (t.gettext(CTRL_VOCAB_CONTAINS_ERROR)).format(tag)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class CtrlVocabSetTierError(ValueError):
    """ :ERROR 1132: CTRL_VOCAB_SET_TIER_ERROR.
    The controlled vocabulary {:s} can't be associated to the tier {:s}.

    """
    def __init__(self, vocab_name, tier_name):
        self.parameter = CTRL_VOCAB_SET_TIER_ERROR + \
          (t.gettext(CTRL_VOCAB_SET_TIER_ERROR)).format(vocab_name, tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TierAppendError(ValueError):
    """ :ERROR 1140: TIER_APPEND_ERROR.
    Can't append annotation. Current end {!s:s} is highest than the given
    one {!s:s}.

    """
    def __init__(self, cur_end, ann_end):
        self.parameter = TIER_APPEND_ERROR + \
                      (t.gettext(TIER_APPEND_ERROR)).format(cur_end, ann_end)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TierAddError(ValueError):
    """ :ERROR 1142: TIER_ADD_ERROR.
    Can't add annotation. An annotation with the same location is already
    in the tier at index {:d}.

    """
    def __init__(self, index):
        self.parameter = TIER_ADD_ERROR + \
                         (t.gettext(TIER_ADD_ERROR)).format(index)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TierHierarchyError(ValueError):
    """ :ERROR 1144: TIER_HIERARCHY_ERROR.
    Attempt a modification in tier '{:s}' that invalidates its hierarchy.

    """
    def __init__(self, name):
        self.parameter = TIER_HIERARCHY_ERROR + \
                         (t.gettext(TIER_HIERARCHY_ERROR)).format(name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TrsAddError(ValueError):
    """ :ERROR 1150: TRS_ADD_ERROR.
    Can't add: '{:s}' is already in '{:s}'.

    """
    def __init__(self, tier_name, transcription_name):
        self.parameter = TRS_ADD_ERROR + \
                    (t.gettext(TRS_ADD_ERROR)).format(tier_name,
                                                      transcription_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TrsRemoveError(ValueError):
    """ :ERROR 1152: TRS_REMOVE_ERROR.
    Can't remove: '{:s}' is not in '{:s}'.

    """
    def __init__(self, tier_name, transcription_name):
        self.parameter = TRS_REMOVE_ERROR + \
                      (t.gettext(TRS_REMOVE_ERROR)).format(tier_name,
                                                           transcription_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TrsInvalidTierError(ValueError):
    """ :ERROR 1160: TRS_INVALID_TIER_ERROR.
    {:s} is not a tier of {:s}. It can't be included in its hierarchy.

    """
    def __init__(self, tier_name, transcription_name):
        self.parameter = TRS_INVALID_TIER_ERROR + \
                (t.gettext(TRS_INVALID_TIER_ERROR)).format(tier_name,
                                                           transcription_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyAlignmentError(ValueError):
    """ :ERROR 1170: HIERARCHY_ALIGNMENT_ERROR.
    Can't create a time alignment between tiers: '{:s}' is not a superset
    of '{:s}'."

    """
    def __init__(self, parent_tier_name, child_tier_name):
        self.parameter = HIERARCHY_ALIGNMENT_ERROR + \
               (t.gettext(HIERARCHY_ALIGNMENT_ERROR)).format(parent_tier_name,
                                                             child_tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyAssociationError(ValueError):
    """ :ERROR 1172: HIERARCHY_ASSOCIATION_ERROR.
    Can't create a time association between tiers: '{:s}' and '{:s}' are not
    supersets of each other.

    """
    def __init__(self, parent_tier_name, child_tier_name):
        self.parameter = HIERARCHY_ASSOCIATION_ERROR + \
             (t.gettext(HIERARCHY_ASSOCIATION_ERROR)).format(parent_tier_name,
                                                             child_tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyParentTierError(ValueError):
    """ :ERROR 1174: HIERARCHY_PARENT_TIER_ERROR.
    The tier can't be added into the hierarchy: '{:s}' has already a link of
    type {:s} with its parent tier '{:s}'.

    """
    def __init__(self, child_tier_name, parent_tier_name, link_type):
        self.parameter = HIERARCHY_PARENT_TIER_ERROR + \
              (t.gettext(HIERARCHY_PARENT_TIER_ERROR)).format(child_tier_name,
                                                              parent_tier_name,
                                                              link_type)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class HierarchyChildTierError(ValueError):
    """ :ERROR 1176: HIERARCHY_CHILD_TIER_ERROR.
    The tier '{:s}' can't be added into the hierarchy: a tier can't be its
    own child.

    """

    def __init__(self, tier_name):
        self.parameter = HIERARCHY_CHILD_TIER_ERROR + \
                     (t.gettext(HIERARCHY_CHILD_TIER_ERROR)).format(tier_name)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class HierarchyAncestorTierError(ValueError):
    """ :ERROR 1178: HIERARCHY_ANCESTOR_TIER_ERROR.
    The tier can't be added into the hierarchy: '{:s}' is an ancestor
    of '{:s}'.

    """

    def __init__(self, child_tier_name, parent_tier_name):
        self.parameter = HIERARCHY_ANCESTOR_TIER_ERROR + \
           (t.gettext(HIERARCHY_ANCESTOR_TIER_ERROR)).format(child_tier_name,
                                                             parent_tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------
# AIO
# -----------------------------------------------------------------------


class AioError(IOError):
    """ :ERROR 1400: AIO_ERROR.
    No such file: '{!s:s}'.

    """
    def __init__(self, filename):
        self.parameter = AIO_ERROR + \
                         (t.gettext(AIO_ERROR)).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioEncodingError(UnicodeDecodeError):
    """ :ERROR 1500: AIO_ENCODING_ERROR.
    The file {filename} contains non {encoding} characters: {error}.

    """
    def __init__(self, filename, error, encoding=sg.__encoding__):
        self.parameter = AIO_ENCODING_ERROR + \
                     (t.gettext(AIO_ENCODING_ERROR)).format(filename=filename,
                                                            error=error,
                                                            encoding=encoding)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioFileExtensionError(IOError):
    """ :ERROR 1505: AIO_FILE_EXTENSION_ERROR.
    Fail formats: unrecognized extension for file {:s}.

    """
    def __init__(self, filename):
        self.parameter = AIO_FILE_EXTENSION_ERROR + \
                        (t.gettext(AIO_FILE_EXTENSION_ERROR)).format(filename)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioMultiTiersError(IOError):
    """ :ERROR 1510: AIO_MULTI_TIERS_ERROR.
    The file format {!s:s} does not support multi-tiers.

    """
    def __init__(self, file_format):
        self.parameter = AIO_MULTI_TIERS_ERROR + \
                        (t.gettext(AIO_MULTI_TIERS_ERROR)).format(file_format)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioNoTiersError(IOError):
    """ :ERROR 1515: AIO_NO_TIERS_ERROR.
    The file format {!s:s} does not support to save no tiers.

    """
    def __init__(self, file_format):
        self.parameter = AIO_NO_TIERS_ERROR + \
                         (t.gettext(AIO_NO_TIERS_ERROR)).format(file_format)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioLineFormatError(IOError):
    """ :ERROR 1520: AIO_LINE_FORMAT_ERROR.
    Unexpected format string at line {:d}: '{!s:s}'.

    """
    def __init__(self, number, line):
        self.parameter = AIO_LINE_FORMAT_ERROR + \
                       (t.gettext(AIO_LINE_FORMAT_ERROR)).format(number, line)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioFormatError(IOError):
    """ :ERROR 1521: AIO_FORMAT_ERROR.
    Unexpected format about '{!s:s}'.

    """

    def __init__(self, line):
        self.parameter = AIO_FORMAT_ERROR + \
                         (t.gettext(AIO_FORMAT_ERROR)).format(line)

    def __str__(self):
        return repr(self.parameter)


# -----------------------------------------------------------------------


class AioEmptyTierError(IOError):
    """ :ERROR 1525: AIO_EMPTY_TIER_ERROR.
    The file format {!s:s} does not support to save empty tiers: {:s}.

    """
    def __init__(self, file_format, tier_name):
        self.parameter = AIO_EMPTY_TIER_ERROR + \
                         (t.gettext(AIO_EMPTY_TIER_ERROR)).format(file_format,
                                                                  tier_name)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class AioLocationTypeError(TypeError):
    """ :ERROR 1530: AIO_LOCATION_TYPE_ERROR.
    The file format {!s:s} does not support tiers with {:s}.

    """
    def __init__(self, file_format, location_type):
        self.parameter = AIO_LOCATION_TYPE_ERROR + \
                     (t.gettext(AIO_LOCATION_TYPE_ERROR)).format(file_format,
                                                                 location_type)

    def __str__(self):
        return repr(self.parameter)

# -----------------------------------------------------------------------


class TagValueError(ValueError):
    """ :ERROR 1190: TAG_VALUE_ERROR.
    {!s:s} is not a valid tag.

    """
    def __init__(self, tag_str):
        self.parameter = TAG_VALUE_ERROR + \
                         (t.gettext(TAG_VALUE_ERROR)).format(tag_str)

    def __str__(self):
        return repr(self.parameter)
