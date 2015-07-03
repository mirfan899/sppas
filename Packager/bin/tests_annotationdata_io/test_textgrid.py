#!/usr/bin/env python2
# -*- coding: utf8 -*-

import unittest
import os
import sys
from os.path import dirname, abspath
from annotationdata.label.label import Label
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.annotation import Annotation
from annotationdata.io.praat import TextGrid

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(os.path.join(SPPAS, 'sppas', 'src'))

SAMPLES = os.path.join(dirname(dirname(dirname(abspath(__file__)))), "samples")


class TestTextGrid(unittest.TestCase):
    """ Represents a TextGrid file
        TextGrid in SPPAS are represented as:
            - a name
            - an array of tiers
            - a time coefficient (1=seconds).
    """

    def test_ReadIntervalsLong(self):
        tg1 = TextGrid()
        tg2 = TextGrid()
        tg1.read(os.path.join(SAMPLES, "sample.TextGrid"))
        tg1.write(os.path.join(SAMPLES, "sample2.TextGrid"))
        tg2.read(os.path.join(SAMPLES, "sample2.TextGrid"))
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
        tg1.read(os.path.join(SAMPLES, "sample_points.TextGrid"))
        tg1.write(os.path.join(SAMPLES, "sample_points2.TextGrid"))
        tg2.read(os.path.join(SAMPLES, "sample_points2.TextGrid"))
        for t1, t2 in zip(tg1, tg2):
            self.assertEqual(t1.GetSize(), t2.GetSize())
            for a1, a2 in zip(t1, t2):
                self.assertEqual(a1.GetLabel().GetValue(),
                                 a2.GetLabel().GetValue())
                self.assertEqual(a1.GetLocation().GetValue(),
                                 a2.GetLocation().GetValue())

    # def test_read(self):
    #     tg = TextGrid()
    #     tg.read("samples/sample_freq.TextGrid")
    #     tier = tg[0]

    #     self.assertTrue(tier.GetSize() == 9)
    #     for a in tier:
    #         self.assertFalse(a.Text.IsEmpty())

    # def test_overlaps(self):
    #     tg = TextGrid()
    #     tg2 = TextGrid()
    #     tier = tg.NewTier()

    #     anns = [Annotation(TimeInterval(TimePoint(1), TimePoint(2)), Label("bar")),
    #             Annotation(TimeInterval(TimePoint(1), TimePoint(2.5)), Label("buz")),
    #             Annotation(TimeInterval(TimePoint(1), TimePoint(3)), Label("foo")),
    #             Annotation(TimeInterval(TimePoint(1), TimePoint(4)), Label("fiz")),
    #             Annotation(TimeInterval(TimePoint(1), TimePoint(5)), Label("biz")),
    #             Annotation(TimeInterval(TimePoint(6), TimePoint(7)), Label("biz")),
    #             Annotation(TimeInterval(TimePoint(6.5), TimePoint(7)), Label("biz")),
    #             Annotation(TimeInterval(TimePoint(7), TimePoint(8)), Label("biz")),
    #             Annotation(TimeInterval(TimePoint(8), TimePoint(9)), Label("biz")),
    #             Annotation(TimeInterval(TimePoint(7), TimePoint(10)), Label("fin"))
    #             ]
    #     for a in anns:
    #         tier.Add(a)

    #     tg.write("samples/testIO.TextGrid")

    #     tg2.read("samples/testIO.TextGrid")
    #     annotation = tg2[0][0]

    #     self.assertEqual(annotation.GetLabel().GetValue(), 'bar buz foo fiz biz')
    #     self.assertEqual(annotation.BeginValue, 1)
    #     self.assertEqual(annotation.EndValue, 5)

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

        tg.write(os.path.join(SAMPLES, "gaps.TextGrid"))

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

    def test_Add(self):
        """
            Add a new tier at a given index.
            Index must be lower than the transcription size.
            By default, the tier is added at the end of the list.
            Parameters:
                - tier (Tier): the tier to add to the transcription
                - index (int): the position in the list of tiers
            Exception:   IndexError
            Return:      Tier index
        """
        pass

    def test_Append(self):
        """
            Append a tier in the transcription.
            Parameters:
                - tier (Tier): the tier to add to the transcription
            Exception:   None
            Return:      Tier index
        """
        pass

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

    def test_MinTime(self):
        tg = TextGrid(mintime=None, maxtime=None)
        self.assertTrue(tg.GetMinTime() is None)
        tg.SetMinTime(3000)
        self.assertEqual(tg.GetMinTime(), 3000)

    def test_MaxTime(self):
        tg = TextGrid()
        self.assertEqual(tg.GetMaxTime(), tg.GetEnd())
        tg.SetMaxTime(3000)
        self.assertEqual(tg.GetMaxTime(), 3000)


# End TestTextGrid
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTextGrid)
    unittest.TextTestRunner(verbosity=2).run(suite)
