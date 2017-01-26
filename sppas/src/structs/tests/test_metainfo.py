# -*- coding:utf-8 -*-

import unittest

from ..metainfo import sppasMetaInfo

# ---------------------------------------------------------------------------


class TestMetaInfo(unittest.TestCase):

    def test_add_get_metainfo(self):

        self.meta = sppasMetaInfo()
        self.assertEqual(len(self.meta), 0)

        # add a meta info
        self.meta.add_metainfo('author', 'moi')
        self.assertEqual(len(self.meta), 1)
        self.assertEqual(self.meta.get_metainfo('author'), 'moi')
        self.assertTrue(self.meta.is_active_metainfo('author'))
        self.assertEqual(len(self.meta.keys_activated()), 1)

        # disable
        self.meta.activate_metainfo('author', False)
        self.assertFalse(self.meta.is_active_metainfo('author'))
        self.assertEqual(len(self.meta.keys_activated()), 0)
        # enable
        self.meta.activate_metainfo('author', True)
        self.assertEqual(len(self.meta.keys_activated()), 1)
        self.assertTrue(self.meta.is_active_metainfo('author'))

        # tests raises:
        with self.assertRaises(KeyError):
            self.meta.add_metainfo('author', 'toto')
        with self.assertRaises(KeyError):
            self.meta.pop_metainfo('toto')
        with self.assertRaises(KeyError):
            self.meta.activate_metainfo('toto')
        with self.assertRaises(KeyError):
            self.meta.get_metainfo('toto')
        with self.assertRaises(KeyError):
            self.meta.is_active_metainfo('toto')

        # pop
        self.meta.pop_metainfo('author')
        self.assertEqual(len(self.meta), 0)

        # add a "complex" meta info
        self.meta.add_metainfo('author', ('moi', 'toi'))
        self.assertEqual(self.meta.get_metainfo('author'), ('moi', 'toi'))
