#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import shutil

from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.aio.praat import TextGrid
from utils.fileutils import sppasFileUtils

# ---------------------------------------------------------------------------

TEMP = sppasFileUtils().set_random()
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# ---------------------------------------------------------------------------


class TestTextGrid(unittest.TestCase):
    """
    Test reader/writers of TextGrid files from Praat.
    
    """
    def setUp(self):
        if os.path.exists(TEMP) is False:
            os.mkdir(TEMP)

    def tearDown(self):
        shutil.rmtree(TEMP)

    def test_ReadIntervalsLong(self):
        tg1 = TextGrid()
        tg2 = TextGrid()
        tg1.read(os.path.join(DATA, "sample.TextGrid"))
        tg1.write(os.path.join(TEMP, "sample.TextGrid"))
        tg2.read(os.path.join(TEMP, "sample.TextGrid"))
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),
                                 a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(),
                                 a2.GetLocation().GetValue())

    def test_ReadPointsLong(self):
        tg1 = TextGrid()
        tg2 = TextGrid()
        tg1.read(os.path.join(DATA, "sample_points.TextGrid"))
        tg1.write(os.path.join(TEMP, "sample_points.TextGrid"))
        tg2.read(os.path.join(TEMP, "sample_points.TextGrid"))
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),
                                 a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(),
                                 a2.GetLocation().GetValue())

    def test_fill_gaps(self):
        tg = TextGrid(mintime=0.5, maxtime=10.1)
        tier = tg.NewTier()

        anns = [Annotation(TimeInterval(TimePoint(1), TimePoint(2)),
                           Label("bar")),
                Annotation(TimeInterval(TimePoint(3), TimePoint(4)),
                           Label("foo")),
                Annotation(TimeInterval(TimePoint(5), TimePoint(6)),
                           Label("fiz")),
                ]
        for a in anns:
            tier.Add(a)
        #tg.write(os.path.join(DATA, "gaps.TextGrid"))

    def test_GetName(self):
        """
            Get the transcription name string.
            Parameters:  None
            Exception:   None
            Return:      A string label
        """
        tg = TextGrid(name="日本語")
        self.assertIsInstance(tg.GetName(), unicode)

    def test_SetName(self):
        """
            Set a new transcription name.
            Parameters:
                - name (string): represents the transcription name
            Exception:   None
            Return:      None
        """
        tg = TextGrid(name="日本語")
        tg.SetName("日本語ファイル")
        self.assertIsInstance(tg.GetName(), unicode)

    def test_NewTier(self):
        """
            Add a new empty tier at the end of the transcription.
            Parameters:
                - name (string): the name of the tier to create
            Exception:   None
            Return:      Tier index
        """
        tg = TextGrid()
        tier = tg.NewTier("ファイル")
        self.assertIsInstance(tier.GetName(), unicode)

    def test_Pop(self):
        """
            Pop a tier of the transcription.
            Parameters:
                - index (int): the index of the tier to pop.
                               Default is the last one.
            Exception:   IndexError
            Return:      Tier
        """
        tg = TextGrid()
        tg.NewTier("tier1")
        tg.NewTier("tier2")

        self.assertFalse(tg.IsEmpty())
        self.assertEqual(tg.Pop().GetName(), "tier2")
        self.assertEqual(tg.Pop().GetName(), "tier1")
        self.assertTrue(tg.IsEmpty())

        with self.assertRaises(IndexError):
            tg.Pop()

    def test_Remove(self):
        """
            Remove a tier of the transcription.
            Parameters:
                - index (int): the index of the tier to remove.
            Exception:   IndexError
            Return:      None
        """
        tg = TextGrid()
        tg.NewTier("foo")
        tg.NewTier("bar")

        self.assertFalse(tg.IsEmpty())
        tg.Remove(0)
        tg.Remove(0)
        self.assertTrue(tg.IsEmpty())

        with self.assertRaises(IndexError):
            tg.Remove(0)

    def test_Find(self):
        """
            Find a tier from its name
            Parameters:
                - name (string) EXACT name of the tier
            Exception:  None
            Return:     Tier
        """
        tg = TextGrid()
        self.assertIsNone(tg.Find("new tier"))

        tier = tg.NewTier("new tier")
        self.assertIs(tg.Find("new tier"), tier)

    def test_GetBegin(self):
        """
            Return the smaller begin time value of all tiers
            or 0 if the transcription contains no tiers.
            Parameters: None
            Exception:  None
            Return:     time value
        """
        tg = TextGrid()
        self.assertEqual(tg.GetBegin(), 0)

    def test_GetEnd(self):
        """
            Return the higher end time value of all tiers.
            Parameters: None
            Exception:  None
            Return:     time value
        """
        tg = TextGrid()
        self.assertEqual(tg.GetEnd(), 0)

    def test_IsEmpty(self):
        """
            Ask the transcription to be empty or not. A transcription is
            empty if it does not contain tiers.
            Parameters:  none
            Exception:   none
            Return:      boolean
        """
        tg = TextGrid()
        self.assertTrue(tg.IsEmpty())

    def test_MinMaxTime(self):
        tg = TextGrid(mintime=0., maxtime=0.)
        self.assertEqual(tg.GetMinTime(), 0.)
        tg.SetMaxTime(3000)
        self.assertEqual(tg.GetMaxTime(), 3000)
        tg.SetMinTime(3000)
        self.assertEqual(tg.GetMinTime(), 3000)

# ---------------------------------------------------------------------------

if __name__ == '__main__':
    testsuite = unittest.TestSuite()
    testsuite.addTest(unittest.makeSuite(TestTextGrid))
    unittest.TextTestRunner(verbosity=2).run(testsuite)
