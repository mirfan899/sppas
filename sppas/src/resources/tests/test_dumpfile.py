#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest

from ..dumpfile import DumpFile
from ..resourcesexc import DumpExtensionError

# ---------------------------------------------------------------------------


class TestDumpFile(unittest.TestCase):

    def test_extension(self):
        dp = DumpFile("E://data/toto.txt")
        self.assertEqual(dp.get_dump_extension(), DumpFile.DUMP_FILENAME_EXT)
        dp.set_dump_extension(".DUMP")
        self.assertEqual(dp.get_dump_extension(), ".DUMP")
        dp.set_dump_extension("DUMP")
        self.assertEqual(dp.get_dump_extension(), ".DUMP")
        dp.set_dump_extension()
        self.assertEqual(dp.get_dump_extension(), DumpFile.DUMP_FILENAME_EXT)
        with self.assertRaises(DumpExtensionError):
            dp.set_dump_extension(".txt")
        with self.assertRaises(DumpExtensionError):
            dp.set_dump_extension(".TXT")
        with self.assertRaises(DumpExtensionError):
            dp.set_dump_extension("TXT")

    def test_filename(self):
        dp = DumpFile("E://data/toto.txt")
        self.assertEqual(dp.get_dump_filename(), "E://data/toto.dump")
        self.assertFalse(dp.has_dump())

