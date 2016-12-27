#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re


def text_preprocess(f):
    def deco(v):
        if not isinstance(v, (basestring)):
            msg = "value type must be basestring for %s: %s"
            raise TypeError(msg % (f.__name__, v))
        v = " ".join(v.split())
        def inner(a):
            a = a.TextValue
            return f(a, v)
        inner.__name__ = f.__name__
        return inner
    return deco


def regexp_preprocess(f):
    def deco(v):
        try:
            re.compile(v)
        except:
            msg = "invalid regular expression: %s"
            raise TypeError(msg % v)
        def inner(a):
            a = a.TextValue
            return f(a, v)
        inner.__name__ = f.__name__
        return inner
    return deco


def begintime_preprocess(f):
    def deco(v):
        if not isinstance(v, (int, float)):
            msg = "value type must be int or float for %s: %s"
            raise TypeError(msg % (f.__name__, v))
        def inner(a):
            if a.IsInterval():
                a = a.Begin
            else:
                a = a.Point
            return f(a, v)
        inner.__name__ = f.__name__
        return inner
    return deco


def endtime_preprocess(f):
    def deco(v):
        if not isinstance(v, (int, float)):
            msg = "value type must be int or float for %s: %s"
            raise TypeError(msg % (f.__name__, v))
        def inner(a):
            if a.IsInterval():
                a = a.End
            else:
                a = a.Point
            return f(a, v)
        inner.__name__ = f.__name__
        return inner
    return deco


def duration_preprocess(f):
    def deco(v):
        if not isinstance(v, (int, float)):
            msg = "value type must be int or float for %s: %s"
            raise TypeError(msg % (f.__name__, v))
        def inner(a):
            a = a.Time.Duration()
            return f(a, v)
        inner.__name__ = f.__name__
        return inner
    return deco


@text_preprocess
def exact(s1, s2):
    return s1 == s2

@text_preprocess
def iexact(s1, s2):
    return s1.lower() == s2.lower()

@text_preprocess
def startswith(s1, s2):
    return s1.startswith(s2)

@text_preprocess
def istartswith(s1, s2):
    return s1.lower().startswith(s2.lower())

@text_preprocess
def endswith(s1, s2):
    return s1.endswith(s2)

@text_preprocess
def iendswith(s1, s2):
    return s1.lower().endswith(s2.lower())

@text_preprocess
def contains(s1, s2):
    return s2 in s1

@text_preprocess
def icontains(s1, s2):
    return s2.lower() in s1.lower()

@regexp_preprocess
def regexp(text, pattern):
    return True  if re.search(pattern, text) else False

@begintime_preprocess
def begin_lt(x, y):
    return x < y

@begintime_preprocess
def begin_le(x, y):
    return x <= y

@begintime_preprocess
def begin_gt(x, y):
    return x > y

@begintime_preprocess
def begin_ge(x, y):
    return x >= y

@begintime_preprocess
def begin_eq(x, y):
    return x == y

@endtime_preprocess
def end_lt(x, y):
    return x < y

@endtime_preprocess
def end_le(x, y):
    return x <= y

@endtime_preprocess
def end_gt(x, y):
    return x > y

@endtime_preprocess
def end_ge(x, y):
    return x >= y

@endtime_preprocess
def end_eq(x, y):
    return x == y

@duration_preprocess
def duration_lt(x, y):
    return x < y

@duration_preprocess
def duration_le(x, y):
    return x <= y

@duration_preprocess
def duration_gt(x, y):
    return x > y

@duration_preprocess
def duration_ge(x, y):
    return x >= y

@duration_preprocess
def duration_eq(x, y):
    return x == y
