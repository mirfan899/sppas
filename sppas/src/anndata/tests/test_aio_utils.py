# -*- coding:utf-8 -*-

import unittest

from ..tier import sppasTier
from ..annotation import sppasAnnotation
from ..annlocation.location import sppasLocation
from ..annlocation.point import sppasPoint
from ..annlocation.interval import sppasInterval
from ..annlabel.label import sppasLabel
from ..annlabel.tag import sppasTag

from ..aio.aioutils import fill_gaps
from ..aio.aioutils import unfill_gaps
from ..aio.aioutils import merge_overlapping_annotations

# ---------------------------------------------------------------------------


class TestUtils(unittest.TestCase):

    def test_fill_gaps(self):
        # integers
        tier = sppasTier()
        anns = [sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))),
                        sppasLabel(sppasTag("bar"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                        sppasLabel(sppasTag("foo"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(6))),
                        sppasLabel(sppasTag("fiz"))),
                ]
        for a in anns:
            tier.append(a)
        self.assertEqual(len(tier), 3)
        self.assertEqual(tier.get_first_point().get_midpoint(), 1)
        self.assertEqual(tier.get_last_point().get_midpoint(), 6)
        filled_tier = fill_gaps(tier, sppasPoint(0), sppasPoint(10))
        self.assertEqual(len(filled_tier), 7)
        self.assertEqual(filled_tier.get_first_point().get_midpoint(), 0)
        self.assertEqual(filled_tier.get_last_point().get_midpoint(), 10)

        # float
        tier = sppasTier()
        anns = [sppasAnnotation(
            sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(2.))),
            sppasLabel(sppasTag("bar"))),
            sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.))),
                sppasLabel(sppasTag("foo"))),
            sppasAnnotation(
                sppasLocation(sppasInterval(sppasPoint(5.), sppasPoint(6.))),
                sppasLabel(sppasTag("fiz"))),
        ]
        for a in anns:
            tier.append(a)
        self.assertEqual(len(tier), 3)
        self.assertEqual(tier.get_first_point().get_midpoint(), 1.)
        self.assertEqual(tier.get_last_point().get_midpoint(), 6.)
        filled_tier = fill_gaps(tier, sppasPoint(0.), sppasPoint(10.))
        self.assertEqual(len(filled_tier), 7)
        self.assertEqual(filled_tier.get_first_point().get_midpoint(), 0.)
        self.assertEqual(filled_tier.get_last_point().get_midpoint(), 10.)

    def test_unfill_gaps(self):
        # integers
        tier = sppasTier()
        anns = [sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(1), sppasPoint(2))),
                        sppasLabel(sppasTag("bar"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(2), sppasPoint(3))),
                        sppasLabel(sppasTag(""))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(3), sppasPoint(4))),
                        sppasLabel(sppasTag("foo"))),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(4), sppasPoint(5)))
                ),
                sppasAnnotation(
                        sppasLocation(sppasInterval(sppasPoint(5), sppasPoint(6))),
                        sppasLabel(sppasTag("fiz"))),
                ]
        for a in anns:
            tier.append(a)
        self.assertEqual(len(tier), 5)
        self.assertEqual(tier.get_first_point().get_midpoint(), 1)
        self.assertEqual(tier.get_last_point().get_midpoint(), 6)
        new_tier = unfill_gaps(tier)
        self.assertEqual(len(new_tier), 3)

    # -----------------------------------------------------------------------

    def test_merge_overlapping_annotations(self):
        tier = sppasTier()
        localizations = [sppasInterval(sppasPoint(1.), sppasPoint(2.)),    # 0
                         sppasInterval(sppasPoint(1.5), sppasPoint(2.)),   # 1
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.)),   # 2
                         sppasInterval(sppasPoint(1.8), sppasPoint(2.5)),  # 3
                         sppasInterval(sppasPoint(2.), sppasPoint(2.3)),   # 4
                         sppasInterval(sppasPoint(2.), sppasPoint(2.5)),   # 5
                         sppasInterval(sppasPoint(2.), sppasPoint(3.)),    # 6
                         sppasInterval(sppasPoint(2.4), sppasPoint(4.)),   # 7
                         sppasInterval(sppasPoint(2.5), sppasPoint(3.))    # 8
                         ]
        annotations = [sppasAnnotation(sppasLocation(t), sppasLabel(sppasTag(i))) for i, t in enumerate(localizations)]
        for i, a in enumerate(annotations):
            tier.add(a)
            self.assertEqual(len(tier), i + 1)

        copy_tier = tier.copy()
        new_tier = merge_overlapping_annotations(tier)

        # we expect the original tier was not modified
        for ann, copy_ann in zip(tier, copy_tier):
            self.assertEqual(ann, copy_ann)

        expected_tier = sppasTier()
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.), sppasPoint(1.5))),
                                        sppasLabel(sppasTag("0")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.5), sppasPoint(1.8))),
                                        sppasLabel(sppasTag("0 1")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(1.8), sppasPoint(2.0))),
                                        sppasLabel(sppasTag("0 1 2 3")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.0), sppasPoint(2.3))),
                                        sppasLabel(sppasTag("3 4 5 6")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.3), sppasPoint(2.4))),
                                        sppasLabel(sppasTag("3 5 6")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.4), sppasPoint(2.5))),
                                        sppasLabel(sppasTag("3 5 6 7")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(2.5), sppasPoint(3.))),
                                        sppasLabel(sppasTag("6 7 8")))
        expected_tier.create_annotation(sppasLocation(sppasInterval(sppasPoint(3.), sppasPoint(4.))),
                                        sppasLabel(sppasTag("7")))
        self.assertEqual(len(expected_tier), len(new_tier))
        for new_ann, expected_ann in zip(new_tier, expected_tier):
            self.assertEqual(new_ann, expected_ann)
