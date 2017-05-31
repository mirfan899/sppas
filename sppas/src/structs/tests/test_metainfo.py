# -*- coding:utf-8 -*-

import unittest

from ..metainfo import sppasMetaInfo
from ..structsexc import MetaKeyError

# ---------------------------------------------------------------------------


class TestMetaInfo(unittest.TestCase):

    def test_add_get_metainfo(self):

        self.meta = sppasMetaInfo()
        self.assertEqual(len(self.meta), 0)

        # add a meta info
        self.meta.add_metainfo('author', 'moi')
        self.assertEqual(len(self.meta), 1)
        self.assertEqual(self.meta.get_metainfo('author'), 'moi')
        self.assertTrue(self.meta.is_enable_metainfo('author'))
        self.assertEqual(len(self.meta.keys_enabled()), 1)

        # disable
        self.meta.enable_metainfo('author', False)
        self.assertFalse(self.meta.is_enable_metainfo('author'))
        self.assertEqual(len(self.meta.keys_enabled()), 0)
        # enable
        self.meta.enable_metainfo('author', True)
        self.assertEqual(len(self.meta.keys_enabled()), 1)
        self.assertTrue(self.meta.is_enable_metainfo('author'))

        # tests raises:
        with self.assertRaises(MetaKeyError):
            self.meta.add_metainfo('author', 'toto')
        with self.assertRaises(MetaKeyError):
            self.meta.pop_metainfo('toto')
        with self.assertRaises(MetaKeyError):
            self.meta.enable_metainfo('toto')
        with self.assertRaises(MetaKeyError):
            self.meta.get_metainfo('toto')
        with self.assertRaises(MetaKeyError):
            self.meta.is_enable_metainfo('toto')

        # pop
        self.meta.pop_metainfo('author')
        self.assertEqual(len(self.meta), 0)

        # add a "complex" meta info
        self.meta.add_metainfo('author', ('moi', 'toi'))
        self.assertEqual(self.meta.get_metainfo('author'), ('moi', 'toi'))
