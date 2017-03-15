# -*- coding:utf-8 -*-

import unittest

from ..structsexc import MetaKeyError, LangTypeError, LangNameError, LangPathError
from ..structsexc import META_KEY_ERROR, LANG_TYPE_ERROR, LANG_PATH_ERROR, LANG_NAME_ERROR

# ---------------------------------------------------------------------------

class TestExceptions(unittest.TestCase):

    def test_glob_exceptions(self):
        try:
            raise MetaKeyError("clé")
        except Exception as e:
            self.assertTrue(isinstance(e, MetaKeyError))
            self.assertTrue(META_KEY_ERROR in str(e))

    def test_lang_exceptions(self):
        try:
            raise LangTypeError("français")
        except Exception as e:
            self.assertTrue(isinstance(e, LangTypeError))
            self.assertTrue(LANG_TYPE_ERROR in str(e))

        try:
            raise LangPathError("directory/folder")
        except Exception as e:
            self.assertTrue(isinstance(e, LangPathError))
            self.assertTrue(LANG_PATH_ERROR in str(e))

        try:
            raise LangNameError("iso639-3")
        except Exception as e:
            self.assertTrue(isinstance(e, LangNameError))
            self.assertTrue(LANG_NAME_ERROR in str(e))
