# -*- coding:utf-8 -*-

import unittest

from ..resourcesexc import FileIOError, FileFormatError
from ..resourcesexc import NgramRangeError, GapRangeError, ScoreRangeError
from ..resourcesexc import DumpExtensionError
from ..resourcesexc import FILE_IO_ERROR, FILE_FORMAT_ERROR
from ..resourcesexc import NGRAM_RANGE_ERROR, GAP_RANGE_ERROR, SCORE_RANGE_ERROR
from ..resourcesexc import DUMP_EXTENSION_ERROR

# ---------------------------------------------------------------------------


class TestExceptions(unittest.TestCase):

    def test_file_exceptions(self):
        try:
            raise FileIOError("path/filename")
        except Exception as e:
            self.assertTrue(isinstance(e, FileIOError))
            self.assertTrue(FILE_IO_ERROR in str(e))

        try:
            raise FileFormatError(10, "wrong line content or filename")
        except Exception as e:
            self.assertTrue(isinstance(e, FileFormatError))
            self.assertTrue(FILE_FORMAT_ERROR in str(e))

        try:
            raise DumpExtensionError(".doc")
        except Exception as e:
            self.assertTrue(isinstance(e, DumpExtensionError))
            self.assertTrue(DUMP_EXTENSION_ERROR in str(e))

    def test_range_exceptions(self):
        try:
            raise NgramRangeError(100, 300)  # maximum, observed
        except Exception as e:
            self.assertTrue(isinstance(e, NgramRangeError))
            self.assertTrue(NGRAM_RANGE_ERROR in str(e))

        try:
            raise GapRangeError(100, 300)  # maximum, observed
        except Exception as e:
            self.assertTrue(isinstance(e, GapRangeError))
            self.assertTrue(GAP_RANGE_ERROR in str(e))

        try:
            raise ScoreRangeError(3.)  # observed
        except Exception as e:
            self.assertTrue(isinstance(e, ScoreRangeError))
            self.assertTrue(SCORE_RANGE_ERROR in str(e))


