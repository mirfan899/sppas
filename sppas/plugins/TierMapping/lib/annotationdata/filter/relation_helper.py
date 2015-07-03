#!/usr/bin/env python2
# -*- coding: utf-8 -*-


#---------------------------------------------------------------
# Allens
#---------------------------------------------------------------

def before(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X precedes Y.
        X  |-------|
        Y            |-------|
    """
    return x2 < y1


def after(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X follows Y.
        X              |--------|
        Y |-------|
    """
    return y2 < x1


def meets(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X meets Y.
        X  |-------|
        Y         |-------|
    """
    return not equals(x1, x2, y1, y2) and x2 == y1


def metby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X is met by Y.
        X          |-------|
        Y |-------|
    """
    return not equals(x1, x2, y1, y2) and x1 == y2


def overlaps(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X overlaps with Y.
        X |-------|
        Y    |------|
    """
    return x1 < y1 and y1 < x2 and x2 < y2


def overlappedby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X overlapped by Y.
        X      |-------|
        Y |------|
    """
    return y1 < x1 and x1 < y2 and y2 < x2


def starts(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X starts at the start of Y and finishes within it.
        X  |-----|
        Y |---------|
    """
    return x1 == y1 and x2 < y2


def startedby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X is started at the start of Y interval.
        X  |--------|
        Y |-----|
    """
    return x1 == y1 and y2 < x2


def finishes(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X finishes at the y2 and within of Y.
        X     |-----|
        Y |--------|
    """
    return y1 < x1 and x2 == y2


def finishedby(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X finished at the y2 of Y.
        X  |--------|
        Y     |----|
    """
    return x1 < y1 and x2 == y2


def during(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X is located during Y.
        X     |-----|
        Y |-----------|
    """
    return y1 < x1 and x2 < y2


def contains(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X contains Y.
        X  |------------|
        Y    |-----|
    """
    return x1 < y1 and y2 < x2


def equals(x1, x2, y1, y2):
    """ Allen's interval algebra.
        Return True if X equals Y.
        X  |-------|
        Y |-------|
    """
    return x1 == y1 and x2 == y2


#---------------------------------------------------------------
# Meta
#---------------------------------------------------------------


def disjoint(x1, x2, y1, y2):
    """
        X  |-------|
        Y            |-------|

        X              |--------|
        Y |-------|

        X  |-------|
        Y         |-------|

        X          |-------|
        Y |-------|
    """
    return before(x1, x2, y1, y2) or\
           after(x1, x2, y1, y2) or\
           meets(x1, x2, y1, y2) or\
           metby(x1, x2, y1, y2)


def convergent(x1, x2, y1, y2):
    """
        X  |--------|
        Y |-----|

        X  |--------|
        Y     |----|

        X  |------------|
        Y    |-----|

        X  |-----|
        Y |---------|

        X     |-----|
        Y |--------|

        X |-------|
        Y    |------|

        X |-------|
        Y    |------|

        X     |-----|
        Y |-----------|

    """
    return startedby(x1, x2, y1, y2) or\
           finishedby(x1, x2, y1, y2) or\
           contains(x1, x2, y1, y2) or\
           overlaps(x1, x2, y1, y2) or\
           overlappedby(x1, x2, y1, y2) or\
           starts(x1, x2, y1, y2) or\
           finishes(x1, x2, y1, y2) or \
           during(x1, x2, y1, y2)


#---------------------------------------------------------------
# Indu
#---------------------------------------------------------------


def lt(x1, x2, y1, y2):
    return (x2.Value - x1.Value) < (y2.Value - y1.Value)


def le(x1, x2, y1, y2):
    return (x2.Value - x1.Value) <= (y2.Value - y1.Value)


def gt(x1, x2, y1, y2):
    return (y2.Value - y1.Value) < (x2.Value - x1.Value)


def ge(x1, x2, y1, y2):
    return (y2.Value - y1.Value) <= (x2.Value - x1.Value)


def eq(x1, x2, y1, y2):
    return (x2.Value - x1.Value) == (y2.Value - y1.Value)


#---------------------------------------------------------------
# Utils
#---------------------------------------------------------------


def split(x, y):
    if x.IsPoint():
        x1 = x.Point
        x2 = x.Point
    else:
        x1 = x.Begin
        x2 = x.End
    if y.IsPoint():
        y1 = y.Point
        y2 = y.Point
    else:
        y1 = y.Begin
        y2 = y.End
    return x1, x2, y1, y2


def min_overlap(x1, x2, y1, y2, minoverlap):
    if x1 > y1:
        x1, x2, y1, y2 = y1, y2, x1, x2
    if x2 <= y1:
        return False
    return x2.Value - y1.Value >= minoverlap


def max_delay(x1, x2, y1, y2, maxdelay):
    if x1 > y1:
        x1, x2, y1, y2 = y1, y2, x1, x2
    if x2 >= y1:
        return False
    return y1.Value - x2.Value <= maxdelay


#---------------------------------------------------------------
# Predicate factory function
#---------------------------------------------------------------


def create(name, *args):
    """
       name (str):
            'before'
            'before_eq'
            'before_ge'
            'before_gt'
            'before_le'
            'before_lt'
            'after'
            'after_eq'
            'after_ge'
            'after_gt'
            'after_le'
            'after_lt'
            'meets'
            'meets_eq'
            'meets_ge'
            'meets_gt'
            'meets_le'
            'meets_lt'
            'metby'
            'metby_eq'
            'metby_ge'
            'metby_gt'
            'metby_le'
            'metby_lt'
            'overlaps'
            'overlaps_eq'
            'overlaps_ge'
            'overlaps_gt'
            'overlaps_le'
            'overlaps_lt'
            'overlappedby'
            'overlappedby_eq'
            'overlappedby_ge'
            'overlappedby_gt'
            'overlappedby_le'
            'overlappedby_lt'
            'starts'
            'startedby'
            'contains'
            'during'
            'finishes'
            'finishedby'
            'disjoint'
            'convergent'
            'equals'
        *args
    """
    module = globals()
    functions = name.split('_')
    q = []
    extra = None
    if len(functions) == 2:
        func = functions[0]
        indu = functions[1]
    else:
        func = functions[0]
        indu = None

    allen = module.get(func, None)
    if not allen:
        raise Exception("Unknown relation: %s" % name)
    else:
        q.append(allen)

    if indu:
        indu = module.get(indu, None)
        if not indu:
            raise Exception("Unknown relation: %s" % name)
        q.append(indu)

    if args:
        if allen.__name__ in ("before", "after"):
            extra = max_delay
        elif allen.__name__ in ("overlaps", "overlappedby"):
            extra = min_overlap

    def wrap(X, Y, *opt, **kwopt):
        x1, x2, y1, y2 = split(X, Y)
        ret = all(f(x1, x2, y1, y2) for f in q)
        if extra:
            ret = ret and extra(x1, x2, y1, y2, *args)

        # Return relation name if ret
        return allen.__name__ if ret else ret

    wrap.__name__ = allen.__name__
    wrap.__doc__ = allen.__doc__
    return wrap
