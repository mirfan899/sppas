# -*- coding:utf-8 -*-

import unittest

from ..annotation import Annotation
from ..label.label import Label
from ..ptime.interval import TimeInterval
from ..ptime.point import TimePoint
from ..tier import Tier
from ..filter.predicate import Rel, RelationPredicate
from ..filter.filters import Filter, RelationFilter

# ---------------------------------------------------------------------------


class TestRelationFilter(unittest.TestCase):

    def test_before_after(self):
        x = Annotation(TimeInterval(TimePoint(1), TimePoint(2)))
        y = Annotation(TimeInterval(TimePoint(3), TimePoint(4)))

        r = Rel('before')
        self.assertTrue(r(x, y))

        r = Rel(before=1.5)
        self.assertTrue(r(x, y))

        r = Rel(before=0.5)
        self.assertFalse(r(x, y))

        x = Annotation(TimeInterval(TimePoint(3), TimePoint(4)))
        y = Annotation(TimeInterval(TimePoint(1), TimePoint(2)))

        r = Rel('after')
        self.assertTrue(r(x, y))

        r = Rel('after')
        self.assertTrue(r(x, y))

        r = Rel(after=1.5)
        self.assertTrue(r(x, y))

        r = Rel(after=0.5)
        self.assertFalse(r(x, y))

    def test_overlaps_overlappedby(self):
        x = Annotation(TimeInterval(TimePoint(1), TimePoint(3)))
        y = Annotation(TimeInterval(TimePoint(2), TimePoint(4)))

        r = Rel('overlaps')
        self.assertTrue(r(x, y))

        r = Rel(overlaps=1)
        self.assertTrue(r(x, y))

        r = Rel(overlaps=2)
        self.assertFalse(r(x, y))

        r = Rel('overlappedby')
        self.assertFalse(r(x, y))

        r = Rel(overlappedby=0.5)
        self.assertFalse(r(x, y))

    def test_equals(self):
        x = Annotation(TimeInterval(TimePoint(3), TimePoint(4)))
        y = Annotation(TimeInterval(TimePoint(1), TimePoint(2)))

        r = Rel('equals')
        self.assertFalse(r(x, y))

        x = Annotation(TimeInterval(TimePoint(1), TimePoint(4)))
        y = Annotation(TimeInterval(TimePoint(1), TimePoint(4)))

        r = Rel('equals')
        self.assertTrue(r(x, y))

    def test_(self):
        relations = ('equals',
                     'before',
                     'after',
                     'meets',
                     'metby',
                     'overlaps',
                     'overlappedby',
                     'starts',
                     'startedby',
                     'finishes',
                     'finishedby',
                     'during',
                     'contains',
                     )
        preds = map(Rel, relations)
        for p in preds:
            self.assertIsInstance(p, RelationPredicate)

    def test_filter(self):
        tierx = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label("label-%s" % i))
            tierx.Append(a)

        tiery = Tier()
        for i in range(10):
            a = Annotation(TimeInterval(TimePoint(i), TimePoint(i+1)), Label("label-%s" % i))
            tiery.Append(a)

        fX = Filter(tierx)
        fY = Filter(tiery)
        relation = Rel('equals')
        new_tier = RelationFilter( relation, fX, fY ).Filter()
