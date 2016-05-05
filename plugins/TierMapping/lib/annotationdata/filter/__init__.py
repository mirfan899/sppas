#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import operator
import bool_helper
import relation_helper
from annotationdata.tier import Tier
from annotationdata.ptime.interval import TimeInterval
import itertools


class Bool(object):
    """
    Predicate Factory.
    """
    def __new__(cls, **kwargs):
        """
        Create a Predicate.

        Kwargs:
            exact (str): exact match
            iexact (str): Case-insensitive exact match
            startswith (str):
            istartswith (str): Case-insensitive startswith
            endswith (str):
            iendswith: Case-insensitive endswith
            contains (str):
            icontains: Case-insensitive contains
            regexp (str): regular expression
            begin_lt (float):
            begin_le (float):
            begin_gt (float):
            begin_ge (float):
            begin_eq (float):
            end_lt (float):
            end_le (float):
            end_gt (float):
            end_ge (float):
            end_eq (float):
            duration_lt (float):
            duration_le (float):
            duration_gt (float):
            duration_ge (float):
            duration_eq (float):

        Returns:
            predicate (Predicate):

        """
        functions = []
        if not kwargs:
            functions.append(lambda a: True)

        for func_name, param in kwargs.items():
            function = getattr(bool_helper, func_name, None)
            if function is None:
                raise Exception("Bool error. Unknown keyword: %s" % func_name)
            try:
                function = function(param)
            except Exception as e:
                raise Exception("Invalid parameter: %s" % e)
            else:
                functions.append(function)
        return reduce(operator.and_, (Predicate(f) for f in functions))


class R(object):
    """
    RelationPredicate Factory.
    """
    def __new__(cls, *args, **kwargs):
        """
        Create a RelationPredicate.

        Args:
            meets (str):
            meets_eq (str):
            meets_ge (str):
            meets_gt (str):
            meets_le (str):
            meets_lt (str):
            metby (str):
            metby_eq (str):
            metby_ge (str):
            metby_gt (str):
            metby_le (str):
            metby_lt (str):
            overlaps (str):
            overlaps_eq (str):
            overlaps_ge (str):
            overlaps_gt (str):
            overlaps_le (str):
            overlaps_lt (str):
            overlappedby (str):
            overlappedby_eq (str):
            overlappedby_ge (str):
            overlappedby_gt (str):
            overlappedby_le (str):
            overlappedby_lt (str):
            starts (str):
            startedby (str):
            contains (str):
            during (str):
            finishes (str):
            finishedby (str):
            disjoint (str):
            convergent (str):
            equals (str):

        Kwargs:
            after (float):
            after_eq (float):
            after_ge (float):
            after_gt (float):
            after_le (float):
            after_lt (float):
            before (float):
            before_eq (float):
            before_ge (float):
            before_gt (float):
            before_le (float):
            before_lt (float):

        Returns:
            predicate (RelationPredicate):

        """
        functions = []
        for r in args:
            func = relation_helper.create(r)
            functions.append(func)
        for k, v in kwargs.items():
            func = relation_helper.create(k, v)
            functions.append(func)
        return reduce(operator.or_, (RelationPredicate(f) for f in functions))


class FilterFactory(object):
    """
    Filter Factory.
    """
    def __new__(cls, tier, *predicate, **kwargs):
        """
        Create a Filter.
        Args:
            tier (Tier):
            predicate :
            kwargs :
        Returns:
            filter (Filter):
        """
        if not predicate and not kwargs:
            predicate = Bool(**kwargs)
        elif kwargs:
            predicate = Bool(**kwargs)
        elif not isinstance(predicate[0], Predicate):
            raise Exception("Invalid argument %s" % predicate[0])
        else:
            predicate = predicate[0]
        return Filter(predicate, tier)


class Filter(object):
    def __init__(self, predicate, tier):
        """
        Args:
            predicate (Predicate):
            tier (Tier):
        """
        self.predicate = predicate
        self.tier = tier

    def __iter__(self):
        for x in self.tier:
            if self.predicate(x):
                yield x

    def Link(self, other, relation):
        """
        Args:
            other (Filter):
            relation (RelationPredicate):
        Returns:
            filter (RelationFilter):
        """
        return RelationFilter(relation, self, other)

    def Filter(self):
        """
        Returns:
            tier (Tier):
        """
        tier = Tier()
        for x in self:
            try:
                tier.Add(x.Copy())
            except:
                pass
        return tier


class RelationFilter(Filter):
    def __init__(self, relation, filter1, filter2):
        """
        Args:
            relation (RelationPredicate):
            filter1 (Filter):
            filter2 (Filter):
        """
        self.pred = relation
        self.filter1 = filter1
        self.filter2 = filter2

    def __iter__(self):
        f1 = [x for x in self.filter1 if not x.Text.IsEmpty()]
        f2 = [x for x in self.filter2 if not x.Text.IsEmpty()]
        for x in f1:
            for y in f2:
                ret = self.pred(x, y)
                if ret:
                    yield x, ret

    def Filter(self, replace=False):
        """
        Returns:
            tier (Tier):
        """
        tier = Tier()
        if replace:
            for x, label in self:
                a = x.Copy()
                a.TextValue = label
                try:
                    tier.Append(a)
                except:
                    e = tier[-1]
                    e.TextValue += " | %s" % label
        else:
            for x, label in self:
                x = x.Copy()
                try:
                    tier.Append(x)
                except:
                    pass
        return tier

class Predicate(object):
    def __init__(self, pred):
        self.pred = pred

    def __call__(self, *args, **kwargs):
        return self.pred(*args, **kwargs)

    def __or__(self, other):
        def func(*args, **kwargs):
            return self(*args, **kwargs) or other(*args, **kwargs)
        func.__name__ = "%s OR %s" % (str(self), str(other))
        return Predicate(func)

    def __and__(self, other):
        def func(*args, **kwargs):
            return self(*args, **kwargs) and other(*args, **kwargs)
        func.__name__ = "%s AND %s" % (str(self), str(other))
        return Predicate(func)

    def __invert__(self):
        def func(*args, **kwargs):
            return not self(*args, **kwargs)
        func.__name__ = "NOT (%s)" % (str(self),)
        return Predicate(func)

    def __str__(self):
        return self.pred.__name__


class RelationPredicate(Predicate):
    def __init__(self, pred):
        Predicate.__init__(self, pred)

    def __and__(self, other):
        raise Exception("& operator exception.")
