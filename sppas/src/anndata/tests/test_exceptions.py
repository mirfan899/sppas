# -*- coding:utf-8 -*-

import unittest
from ..anndataexc import *

# -----------------------------------------------------------------------


class TestExceptions(unittest.TestCase):

    def test_exc_global(self):
        try:
            raise AnnDataError()
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataError))
            self.assertTrue(ANN_DATA_ERROR in str(e))

        try:
            raise AnnDataTypeError("observed_type", "expected_type")
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataTypeError))
            self.assertTrue(ANN_DATA_TYPE_ERROR in str(e))

        try:
            raise AnnDataIndexError(4)
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataIndexError))
            self.assertTrue(ANN_DATA_INDEX_ERROR in str(e))

        try:
            raise AnnDataEqTypeError("object", "object_ref")
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataEqTypeError))
            self.assertTrue(ANN_DATA_EQ_TYPE_ERROR in str(e))

        try:
            raise AnnDataNegValueError(-5)
        except Exception as e:
            self.assertTrue(isinstance(e, AnnDataNegValueError))
            self.assertTrue(ANN_DATA_NEG_VALUE_ERROR in str(e))

    def test_exc_Tier(self):
        try:
            raise TierAppendError(3, 5)
        except Exception as e:
            self.assertTrue(isinstance(e, TierAppendError))
            self.assertTrue(TIER_APPEND_ERROR in str(e))

        try:
            raise TierAddError(3)
        except Exception as e:
            self.assertTrue(isinstance(e, TierAddError))
            self.assertTrue(TIER_ADD_ERROR in str(e))

        try:
            raise TierHierarchyError("name")
        except Exception as e:
            self.assertTrue(isinstance(e, TierHierarchyError))
            self.assertTrue(TIER_HIERARCHY_ERROR in str(e))

        try:
            raise CtrlVocabContainsError("tag")
        except Exception as e:
            self.assertTrue(isinstance(e, CtrlVocabContainsError))
            self.assertTrue(CTRL_VOCAB_CONTAINS_ERROR in str(e))

        try:
            raise IntervalBoundsError("begin", "end")
        except Exception as e:
            self.assertTrue(isinstance(e, IntervalBoundsError))
            self.assertTrue(INTERVAL_BOUNDS_ERROR in str(e))

    def test_exc_Trs(self):
        try:
            raise TrsAddError("tier_name", "transcription_name")
        except Exception as e:
            self.assertTrue(isinstance(e, TrsAddError))
            self.assertTrue(TRS_ADD_ERROR in str(e))

        try:
            raise TrsRemoveError("tier_name", "transcription_name")
        except Exception as e:
            self.assertTrue(isinstance(e, TrsRemoveError))
            self.assertTrue(TRS_REMOVE_ERROR in str(e))

    def test_exc_AIO(self):
        try:
            raise AioEncodingError("filename", "error éèàçù")
        except Exception as e:
            self.assertTrue(isinstance(e, AioEncodingError))
            self.assertTrue(AIO_ENCODING_ERROR in str(e))

        try:
            raise AioFileExtensionError("filename")
        except Exception as e:
            self.assertTrue(isinstance(e, AioFileExtensionError))
            self.assertTrue(AIO_FILE_EXTENSION_ERROR in str(e))

        try:
            raise AioMultiTiersError("file_format")
        except Exception as e:
            self.assertTrue(isinstance(e, AioMultiTiersError))
            self.assertTrue(AIO_MULTI_TIERS_ERROR in str(e))

        try:
            raise AioNoTiersError("file_format")
        except Exception as e:
            self.assertTrue(isinstance(e, AioNoTiersError))
            self.assertTrue(AIO_NO_TIERS_ERROR in str(e))

        try:
            raise AioLineFormatError(3, "line")
        except Exception as e:
            self.assertTrue(isinstance(e, AioLineFormatError))
            self.assertTrue(AIO_LINE_FORMAT_ERROR in str(e))

        try:
            raise AioEmptyTierError("file_format", "tier_name")
        except Exception as e:
            self.assertTrue(isinstance(e, AioEmptyTierError))
            self.assertTrue(AIO_EMPTY_TIER_ERROR in str(e))
