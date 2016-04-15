#!/usr/bin/env python2
# vim: set fileencoding=UTF-8 ts=4 sw=4 expandtab:
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: delay_relations.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Tatsuya Watanabe, Brigitte Bigi (brigitte.bigi@gmail.com), Grégoire Montcheuil"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# import TimePoint for intervals
from ..ptime.point import TimePoint
# import Decimal
from decimal import *

#---------------------------------------------------------------
# Utils
#---------------------------------------------------------------


def joinWithQuote(sep, *args, **kwargs):
    if len(args)<=0: return "";
    if 'lastsep' in kwargs:
        return ( "'%s'" % args[0] if (len(args)<2)
               else ( sep.join(map(lambda k: "'%s'" % k, args[:-2]))
                    + kwargs['lastsep'] + ("'%s'" % args[:-1])
                    )
               )
    else:
        return sep.join(map(lambda k: "'%s'" % k, args))



#---------------------------------------------------------------
class JoinList(list):
    """
    A list with customizable str() method
    @param args:    the list of predicates
    @param kwargs:    options
        - sep (str): set the join separator (default: ',')
        - left (str): string before the list, p.e. '[' (default: '')
        - right (str): string after the list, p.e. ']' (default: '')
    """
    def __init__(self, *args, **kwargs):
        list.__init__(self, args)
        self.__str__opts = {'sep':',', 'left':'', 'right':''}
        for k,v in kwargs.items():
            self.__str__opts[k]=v;

    def __str__(self):
        return "{left}{join}{right}".format(
                left = self.__str__opts['left'] if (self.__str__opts['left'] is not None) else '',
                right = self.__str__opts['right'] if (self.__str__opts['right'] is not None) else '',
                join = (self.__str__opts['sep'] if (self.__str__opts['sep'] is not None) else '').join(map(str, self))
                )

#---------------------------------------------------------------
class OrPredicates(JoinList):
    """
    A Predicates disjunction
    @param args:    the list of predicates
    @param kwargs:    options
        - name : set a name for string conversion
        if falsy, string conversion join the predicates' names with " OR "
    """

    def __init__(self, *args, **kwargs):
        JoinList.__init__(self, *args, sep=" OR ", **kwargs)
        self.name = kwargs.get('name', None)

    def __call__(self, *args, **kwargs):
        """
        Call the sequence of predicate, returning the first truthy result (not None, False, 0, '', []).
        @return: the first truthy result or None if any.
        """
        # return the 1st not None result
        for p in self:
            res = p(*args, **kwargs)
            if res:
                return res
        return None # any not None result
    
    def __str__(self):
        return self.name if (self.name is not None) else JoinList.__str__(self)
    
    #---------------------------------------------
    #-- '&' and '|' operators
    #---------------------------------------------

    #---------------------------------------------
    def __or__(self, other):
        """
        Allow to combine 2 predicates with the '|' operator
        """
        return OrPredicates(self, other)

    #---------------------------------------------
    def __and__(self, other):
        """
        Allow to combine 2 predicates with the '&' operator
        """
        return AndPredicates(self, other)


#---------------------------------------------------------------
class AndPredicates(JoinList):
    """
    A Predicates conjunction
    @param args:    the list of predicates
    @param kwargs:    options
        - name : set a name for string conversion
        if falsy, string conversion join the predicates' names with " AND "
    """

    def __init__(self, *args, **kwargs):
        JoinList.__init__(self, *args, sep=" AND ", **kwargs)
        self.name = kwargs.get('name', None)

    def __call__(self, *args, **kwargs):
        """
        Call the sequence of predicate, returning the list of results or None if any result is falsy (None, False, 0, '', []).
        @return: the list of all results if all are verified
            or None if any result is falsy
        """
        results = JoinList(sep=" and ")
        # return None if one is None
        for p in self:
            res = p(*args, **kwargs)
            if res:
                results.append(res)
            else:
                return None;
        # join the result
        return results #" AND ".join(map(str, results))

    def __str__(self):
        return self.name if (self.name is not None) else JoinList.__str__(self)

    #---------------------------------------------
    #-- '&' and '|' operators
    #---------------------------------------------

    #---------------------------------------------
    def __or__(self, other):
        """
        Allow to combine 2 predicates with the '|' operator
        """
        return OrPredicates(self, other)

    #---------------------------------------------
    def __and__(self, other):
        """
        Allow to combine 2 predicates with the '&' operator
        """
        return AndPredicates(self, other)

    #TODO?  def __invert__(self):

#---------------------------------------------------------------
# Delay : a value with a margin/vagueness/radius
# (similar to ..ptime.Duration but allowing negative values)
#---------------------------------------------------------------

class Delay(object):

    def __init__(self, value, margin=None):
        """
        Constructor
        @param value:   the delay value or any object 'unpackable' into (value, margin)
        @param margin:  (optional) a (new) margin
        @see Dealy.unpack()
        """
        self.value, self.margin = Delay.unpack(value)   # this accept many values and init the margin
        if self.value is None:
            raise ValueError("Incorrect Delay value {value} ({value.__class__.__name__})".format(**locals()))
        if margin is not None:  # (re)define margin
            self.margin = Delay.numeric(margin)
       

    # -----------------------------------------------------------------------
    # --- core tools method
    # -----------------------------------------------------------------------
    _NUMERIC = None    # type of numeric (float, Decimal, ..., accept either keys of _NUMERIC_FROMSTRING)
    _NUMERIC_FROMSTRING = {'float':float, 'Decimal':Decimal}
    _VALUE_ATTRIBUTES = ['value', 'GetValue', 'GetMidpoint']
    _MARGIN_ATTRIBUTES = ['margin', 'GetMargin', 'GetRadius']
    
    # -----------------------------------------------------------------------
    @classmethod
    def numeric(cls, value):
        """
        Class method to convert a value into a numeric, based on _NUMERIC (default float)
        @param value:   the value to convert
        @return:    the converted value or None if error
        @raise  ValueError  if the class _NUMERIC parameter isn't correct
        """
        #TODO? add a 'numeric' parameter
        numeric = cls._NUMERIC
        if numeric is None: # default to float
            numeric = float
        if not callable(numeric) and numeric in cls._NUMERIC_FROMSTRING:
            numeric = cls._NUMERIC_FROMSTRING[numeric]
        if not callable(numeric):
            raise ValueError("_NUMERIC parameter '{cls._NUMERIC}' of class '{cls}' isn't a valid method ({numeric})".format(**locals()))
        elif isinstance(value, numeric):
            return value;
        else:
            try:
                return numeric(value)
            except:
                return None;

    # -----------------------------------------------------------------------
    @classmethod
    def unpack(cls, other, noValue=None, noMargin=0.):
        """
        Split a object into (value, margin)
        @param other:   the object to split
        @type other:    a Delay, float, int, or many other things
        @param noValue:   (optional) value to return if any value is found.  Default is None.
        @param noMargin:   (optional) margin to return if any margin is found. Default 0.
            nota: noMargin=None allow to know tets if a margin was found.
        @return:    a tuple of 2 'numerics' (value, margin)
            default value is None   (=> other's value isn't a valid number)
            default margin is 0.    (=> other hasn't a margin)
        """
        hasValue = hasMargin = False
        value = None; margin = None #cls.numeric(0.)
        # easy cases
        if isinstance(other, Delay):
            value, margin = other.value, other.margin
            hasValue = hasMargin = True
        elif isinstance(other, (int, float)):
            value = other; hasValue = True
        elif (  isinstance(other, (list, tuple))    # list/tuple
            and not isinstance(other, basestring)   # avoid string
            and len(other)>0    # or empty list/tuple
            ):
            value = other[0]; hasValue = True
            if len(other)>1:
                margin = other[1]; hasMargin = True
        
        # other cases
        # (a) look for 'value' or other cls._VALUE_ATTRIBUTES
        if not hasValue:
            for att in cls._VALUE_ATTRIBUTES:
                oatt = getattr(other, att, None)
                if callable(oatt):
                    try:
                        value = oatt();
                        hasValue=True
                        break
                    except:
                        pass
                elif oatt is not None:
                    value = oatt
                    hasValue=True
                    break;
        # (b) look for 'margin' or other cls._MARGIN_ATTRIBUTES
        if not hasMargin:
            for att in cls._MARGIN_ATTRIBUTES:
                oatt = getattr(other, att, None)
                if callable(oatt):
                    try:
                        margin = oatt();
                        hasMargin=True
                        break
                    except:
                        pass
                elif oatt is not None:
                    margin = oatt
                    hasMargin=True
                    break;
        # convert value into classes' numeric (float, Decimal, ...)
        try:
            value = cls.numeric(value if hasValue else other) # use other as default value
        except: # value stay None => next try with noValue
            pass
        if (value is None and noValue is not None):
            try:
                value = cls.numeric(noValue) # convert noValue
            except:
                value = None    # final default
        # convert margin into classes' numeric (float, Decimal, ...)
        if hasMargin:
            try:
                margin = cls.numeric(margin)
            except:
                margin = cls.numeric(0.)
        if (margin is None and noMargin is not None):
            try:
                margin = cls.numeric(noMargin) # convert noMargin
            except:
                margin = cls.numeric(0.)    # final default

        # result
        return value, margin

    # -----------------------------------------------------------------------
    # --- formating methods
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    def __repr__(self):
        return "%s(%r~%r)" % (self.__class__.__name__, self.value, self.margin)

    # -----------------------------------------------------------------------
    def __str__(self):
        return "(%f~%.1f)" % (self.value, self.margin)

    # -----------------------------------------------------------------------
    def __format__(self, f):
        # easy case
        if f=='r':
            return repr(self)
        if f=='s':
            return str(self)
        vformat = 'f'; mformat = '.2f' # default value/margin format
        if f:
            iTilde = f.find('~') # split with '~'
            if iTilde>=0:
                vformat = f[:iTilde]; mformat = f[(iTilde+1):]
            else:
                vformat = f
        res = format(self.value, vformat)
        if mformat and (self.margin>0.): # append margin except with empty format or null margin
            res += '~'+format(self.margin, mformat)
        return res

    def __hash__(self):
        return hash((self.value, self.margin))

    # -----------------------------------------------------------------------
    # --- comparition methods
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    # inspired by Duration
    def __eq__(self, other):
        """
        Equal is required to use '==' between 2 Delay instances
         or between a Delay and another object a time/number

        @param other:   the other duration to compare with.
        @type other:    Delay, float, int (or any thing convertible into float)
        """
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        # bad values => not equals
        if svalue is None or ovalue is None:
            return self is other    # False except if same reference
        delta = abs(svalue - ovalue)
        radius = smargin + omargin
        return delta <= radius

    # -----------------------------------------------------------------------
    # inspired by Duration
    def __lt__(self, other):
        """
        LowerThan is required to use '<' between 2 Delay instances
         or between a Delay and an other time/number.

        @param other:   the other duration to compare with.
        @type other:    Delay, float, int (or any thing convertible into float)
        """
        # start by check if self == other (this use the margins)
        if self == other:
            return False
        # compare value
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        return (svalue < ovalue)
    
    # -----------------------------------------------------------------------
    # inspired by Duration
    def __gt__(self, other):
        """
        GreaterThan is required to use '>' between 2 Delay instances
         or between a Delay and an other time/number.

        @param other:   the other duration to compare with.
        @type other:    Delay, float, int (or any thing convertible into float)
        """
        # start by if self == other (this use the margins)
        if self == other:
            return False
        # compare value
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        return (svalue > ovalue)

    # ------------------------------------------------------------------------
    # copied from Duration
    def __ne__(self, other):
        """
        Not equals.
        """
        return not (self == other)

    # ------------------------------------------------------------------------
    # inspired by __lt__
    def __le__(self, other):
        """
        Lesser or equal.
        """
        # start by self == other (this use the margin)
        if self == other:
            return True
        # compare value
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        return (svalue <= ovalue)

    # ------------------------------------------------------------------------
    # inspired by Duration
    # inspired by __lt__
    def __ge__(self, other):
        """
        Greater or equal.
        """
        # start by self == other (this use the margin)
        if self == other:
            return True
        # compare value
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        return (svalue >= ovalue)

    
    # -----------------------------------------------------------------------
    # --- mathematic methods
    # -----------------------------------------------------------------------
    def _newSelf(self, value, margin=None):
        """
        Method that try to build a new instance of 
        """
        #TODO: try a 'copy' of self
        try:
            return type(self)(value, margin)    # new object of the same class that self
        #TODO: try all the inheritance path between self and Delay
        except:
            return Delay(value, margin)

    def __add__(self, other):
        """
        Delay addition
        (!) the new margin is the max of the initial margins
        @type other:    Delay or float/int
        @return:    a Delay with the sum of value and the maximum margin
        """
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        # error case
        if svalue is None or ovalue is None:
            raise ValueError("Can't add undefined values ({} + {})".format(self, other))
        # idempotent cases
        if ovalue == 0.:
            if omargin <= smargin:  #TODO: a option self._DELAY_MARGIN_OP = 'sum' or 'max' (default) , etc.
                return self
            else:
                return self._newSelf(svalue, omargin)
        margin = omargin if omargin > smargin else smargin  #TODO: a option self._DELAY_MARGIN_OP = 'sum' or 'max' (default), etc.
        return self._newSelf(svalue+ovalue, margin)

    def __sub__(self, other):
        """
        Delay substraction
        (!) the new margin is the max of the initial margins
        @type other:    Delay or float/int
        @return:    a Delay with the difference of values and the maximum margin
        """
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        # error case
        if svalue is None or ovalue is None:
            raise ValueError("Can't substract undefined values ({} - {})".format(self, other))
        # idempotent cases
        if ovalue == 0.:
            if omargin <= smargin:
                return self
            else:
                return self._newSelf(svalue, omargin)
        margin = omargin if omargin > smargin else smargin
        return self._newSelf(svalue-ovalue, margin)

    def __mul__(self, other):
        """
        Delay multiplication
        (!) the new margin is the max of the initial margins
        @type other:    Delay or float/int
        @return:    a Delay with the product of values and the maximum margin
        """
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        # error case
        if svalue is None or ovalue is None:
            raise ValueError("Can't multiply undefined values ({} * {})".format(self, other))
        # idempotent cases
        if ovalue == 1.:
            if omargin <= smargin:
                return self
            else:
                return self._newSelf(svalue, omargin)
        margin = omargin if omargin > smargin else smargin
        return self._newSelf(svalue*ovalue, margin)

    def __div__(self, other):
        """
        Delay "classic" division
        (!) the new margin is the max of the initial margins
        @type other:    Delay or float/int
        @return:    a Delay with the "classic" division of values and the maximum margin
        """
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        # error case
        if svalue is None or ovalue is None:
            raise ValueError("Can't divided undefined values ({} / {})".format(self, other))
        if ovalue == 0.:
            raise ValueError("Can't divided by 0 ({} / {})".format(self, other))
        # idempotent cases
        if ovalue == 1.:
            if omargin <= smargin:
                return self
            else:
                return self._newSelf(svalue, omargin)
        margin = omargin if omargin > smargin else smargin
        return self._newSelf(svalue/ovalue, margin)


    def __truediv__(self, other):
        """
        Delay "true" division
        @type other:    Delay or float/int
        @return:    a Delay with the "true" division of values and the maximum margin
        """
        svalue, smargin = Delay.unpack(self)
        ovalue, omargin = Delay.unpack(other)
        # error case
        if svalue is None or ovalue is None:
            raise ValueError("Can't divided undefined values ({} / {})".format(self, other))
        if ovalue == 0.:
            raise ValueError("Can't divided by 0 ({} / {})".format(self, other))
        # idempotent cases
        if ovalue == 1.:
            if omargin <= smargin:
                return self
            else:
                return self._newSelf(svalue, omargin)
        margin = omargin if omargin > smargin else smargin
        return self._newSelf(svalue/ovalue, margin)

    def __neg__(self):
        return self._newSelf(-self.value, self.margin);

    def __pos__(self):
        return self;
    
    def __abs__(self):
        return self if self.value >= 0 else -self;

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __round__(self, n=0):
        return round(self.value, n)

#---------------------------------------------------------------
# IntervalsDelay
#---------------------------------------------------------------

#---------------------------------------------------------------
class BinaryPredicate(object):
    """
    A BinaryPredicate is an abstract Predicate with 2 Annotation parameters
    So you should callesd instance with 2 Annotation parameters
        bp = BinaryPredicate(...)
        bp(x,y, **kwargs)
    """
    pass

#---------------------------------------------------------------
class IntervalsDelay(BinaryPredicate):
    """
    Predicate on the Maximal/minimal delay between two intervals.
    The reference point of each interval is express in percent,
     i.e. start point <=> 0%, end point <=> 100%, middle point 50% (default), etc.
    """

    # some points percent values
    POINTS_PERCENT={'start':0, 'end':1, 'mid':0.5, 'middle':0.5}
    # the default points percent values (middle)
    DEFAULT_PERCENT=0.5
    # 'percent' name
    PERCENT_ALIASES=('percent', '%')
    # dictionnary of directions
    DIRECTIONS={'after':'after', 'before':'before'}
    __DEFAULT_DIRECTION='before'
    
    def __init__(self, mindelay=0, maxdelay=0, xpercent=DEFAULT_PERCENT, ypercent=DEFAULT_PERCENT, direction=__DEFAULT_DIRECTION, name=''):
        """
        Build a new IntervalsDelay
        @param mindelay:    minimum delay between the 2 intervals (in second, default:0)
        @type mindelay: float
        @param maxdelay:    maximum delay between the 2 intervals (in second, default:0)
        @type maxdelay: float
        @param xpercent:    first interval reference point ([0,1], default:0.5)
        @type xpercent: float
        @param ypercent:    second interval reference point ([0,1], default:0.5)
        @type ypercent: float
        @param direction:    the X-Y direction
            if (direction=='after'), the delay is positif when X is after Y (usefull if we search X that are 'consequence' of Y)
            else, i.e. (direction=='before'), the delay is positif when X is before Y (usefull if we search X that 'imply' Y)
        @type name: 'before' or 'after'
        @param name:    custom name for the relation
        @type name: str
        """
        IntervalsDelay.validMinMaxDelay(mindelay, maxdelay) # raise ValueError
        self.mindelay = mindelay
        self.maxdelay = maxdelay
        self.xpercent = xpercent
        self.ypercent = ypercent
        if direction not in self.DIRECTIONS:
            raise ValueError("Incorrect IntervalsDelay direction '{}', correct values are {}".format(direction, joinWithQuote(',', self.DIRECTIONS.keys())))
        else:
            self.direction = self.DIRECTIONS[direction]
        self.name = name

    def delay(self, xstart, xend, ystart, yend):
        """
        Compute the actual delay between the two intervals
        @param xstart:  first interval start point
        @param xend:  first interval end point
        @param ystart:  second interval start point
        @param yend:  second interval end point
        @return:    the delay between the two intervals
        @rtype: a Delay if any of the (usefull) points is a TimePoint
            else a float
            nota: 'usefull points' if xpercent=0., point(xstart,xend) is xstart, so xend is useless
        """
        xpoint = IntervalsDelay.point(xstart, xend, self.xpercent)
        ypoint = IntervalsDelay.point(ystart, yend, self.ypercent)

        # evaluate the delay/vagueness (~ sum of radius)
        # use Delay.unpack to be more generic than TimePoint
        xvalue, xmargin = Delay.unpack(xpoint, noMargin=None)
        yvalue, ymargin = Delay.unpack(ypoint, noMargin=None)
        #hasMargin = isinstance(xpoint, TimePoint) or isinstance(ypoint, TimePoint) #TODO: Delay.unpack 3rd return value or Delay.hasMargin() method
        hasMargin=False
        if xmargin is None:    xmargin = Delay.numeric(0.);# remplace None by Delay.numeric(0.)
        else: hasMargin=True
        if ymargin is None:    ymargin = Delay.numeric(0.)# remplace None by Delay.numeric(0.)
        else: hasMargin=True
        # calculate the delay based on the direction
        delay = Delay.numeric(0.)
        if self.direction == 'after': # delay of X after Y, i.e. X-Y
            delay = (xvalue - yvalue)
        elif self.direction == 'before': # delay of X after Y, i.e. X-Y
            delay = (yvalue - xvalue)
        else: # __DEFAULT_DIRECTION
            delay = (xvalue - yvalue) if self.__DEFAULT_DIRECTION=='after' else (yvalue - xvalue)
        #print "delay({xstart}, {xend}, {ystart}, {yend})\n\t=> {xpoint}, {ypoint}\n\t=> ({xvalue}, {xmargin}) , ({yvalue}, {ymargin}) hasMargin:{hasMargin}\n\t{delay} (direction={self.direction})".format(**locals())
        return Delay(delay, xmargin+ymargin) if hasMargin else delay;   #TODO: a option self._DELAY_MARGIN_OP = 'sum' (default) or 'max', etc.

    def check(self, xstart, xend, ystart, yend):
        """
        Check if the delay between the two intervals respect max/mindelay
        @param xstart:  first interval start point
        @param xend:  first interval end point
        @param ystart:  second interval start point
        @param yend:  second interval end point
        """
        delay = self.delay(xstart, xend, ystart, yend)
        #print "[{self.xpercent},{self.ypercent}] delay({xstart}, {xend}, {ystart}, {yend}) = {delay}".format(**locals())
        if IntervalsDelay.checkDelay(delay, self.mindelay, self.maxdelay):
            return CheckedIntervalsDelay(delay, **{a:getattr(self,a) for a in ['mindelay', 'maxdelay', 'xpercent', 'ypercent']})
        else:
            return None;

    def __call__(self, *args, **kwargs):
        """
        IntervalsDelay's predicate
        Accecpt either:
            - 2 Annotation arguments (x,y)
            - 4 Point arguments (xstart, xend, ystart, yend)
        """
        if (len(args)==2): # 2 arguments => x,y (Annotation) => split into xstart, xend, ystart, yend
            return self.check(*IntervalsDelay.splitAnnotations(*args))
        elif (len(args)==4): # 4 arguments => yet xstart, xend, ystart, yend
            return self.check(*args)
        else:
            raise ValueError("IntervalsDelay's function require 2 Annotation parameters or 4 Point parameters")

    def __str__(self):
        if self.name:
            return self.name
        else:
            elems = [IntervalsDelay.pointStr(self.xpercent), IntervalsDelay.pointStr(self.ypercent)]
            if (self.direction and self.direction != self.__DEFAULT_DIRECTION): # insert the direction if it isn't the default
                elems.append(self.direction)
            elems.append(IntervalsDelay.delayStr(self.mindelay, self.maxdelay))
            return '_'.join(elems)

    def __cmp__(self, other):
        """
        Compare IntervalsDelay based on 
            - (1) the first interval point (i.e. xpercent)
            - (2) the second interval point (i.e. ypercent)
            - (3) the direction (before < after)
            - (4) the minimal delay (None ~ -infinity)
            - (5) the maximal delay (None ~ +infinity)
        """
        def sign(x):
            if x<0: return -1;
            if x>0: return +1;
            return 0;

        # a secure way to get the real direction of an IntervalDelay/object
        def dir_(x):
            if hasattr(x, 'direction'):
                return x.direction or self.__DEFAULT_DIRECTION  # if x.direction isn't true, return __DEFAULT_DIRECTION
            else:
                return self.__DEFAULT_DIRECTION

        # (1) the first interval point (i.e. xpercent)
        res = self.xpercent - other.xpercent # start < mid < end
        if res: return sign(res);

        # (2) the second interval point (i.e. ypercent)
        res = self.ypercent - other.ypercent # start < mid < end
        if res: return sign(res);
        
        # (3) the direction (before < after)
        sdir, odir = dir_(self), dir_(other)
        if (sdir != odir):            
            return -1 if sdir=='before' else +1 # (sdir!=odir and sdir==before) => odir == after => self < other 

        # (4) the minimal delay (None ~ -infinity)
        if self.mindelay is None:
            res = ( 0 if other.mindelay is None # both None => 'equals'
                    else -1 ) # self(-infinity) < other
        else:
            res = ( +1 if other.mindelay is None # self > other(-infinity)
                    else self.mindelay - other.mindelay ) # self - other
        if res: return sign(res);
        
        # (5) the maximal delay (None ~ +infinity)
        if self.maxdelay is None:
            res = ( 0 if other.maxdelay is None # both None => 'equals'
                    else +1 ) # self(+infinity) > other
        else:
            res = ( -1 if other.maxdelay is None # self < other(+infinity)
                    else self.maxdelay - other.maxdelay ) # self - other
        return sign(res);

    
    #---------------------------------------------
    #-- '&' and '|' operators
    #---------------------------------------------

    #---------------------------------------------
    def __or__(self, other):
        """
        Allow to combine 2 predicates with the '|' operator
        """
        return OrPredicates(self, other)

    #---------------------------------------------
    def __and__(self, other):
        """
        Allow to combine 2 predicates with the '&' operator
        """
        return AndPredicates(self, other)

    #---------------------------------------------
    @staticmethod
    def validMinMaxDelay(mindelay, maxdelay):
        """
        Check if the min/max delays are a valid combination,
         i.e. min <= max, considering None as -/+infinity
        """
        if mindelay is None: # -infinity
            if maxdelay is None:
                raise ValueError("min/maxdelay can't be both None")
            return True;
        if maxdelay is None: # +infinity
            return True; # mindelay != None
        if mindelay > maxdelay: # min < max
            raise ValueError("mindelay({}) should be less or equals to maxdelay({})".format(mindelay, maxdelay))
        return True;

    @staticmethod
    def pointStr(percent):
        """
        Convert a percent to the point name (start/end/middle/<p>%)
        """
        if percent is None: return 'percent'; # default/undefined
        try:
            fpercent = float(percent)
            if fpercent==0.: return 'start'
            if fpercent==1.: return 'end'
            if fpercent==0.5: return 'middle'
            return "{:02.0%}".format(fpercent)
        except:
            raise ValueError("Percent value '{}' isn't a real number".format(percent))

    @staticmethod
    def point(start, end, percent=0):
        """
        Compute the point corresponding to a percent of an interval
        @param start: start of the interval
        @type start: TimePoint (better) or float/int
        @param end: end of the interval
        @type end: TimePoint (better) or float/int
        @param percent: percent value
        @type percent: float
        @return: the point corresponding to the percent of the interval
        @rtype: TimePoint (better) if start/end are a TimePoint, else a float
        """
        if start is end:  return start; # point
        if percent==0.:  return start;
        if percent==1.:  return end;
        # compute the percent point
        ppoint = ( (1.-percent) * ( start.GetMidpoint() if isinstance(start, TimePoint) else start )
                  + percent * ( end.GetMidpoint() if isinstance(end, TimePoint) else end )
                 )
        # compute the TimePoint radius : Max(start.radius, end.radius)
        radius = None;
        if isinstance(start, TimePoint): # get the start radius
            radius = start.GetRadius();
        if isinstance(end, TimePoint): # get Max(start.radius, end.radius)
            endRadius = end.GetRadius();
            if radius is None or endRadius>radius:
                radius = endRadius
        return TimePoint(ppoint, radius) if radius is not None else ppoint # return a TimePoint if at least one TimePoint

    @staticmethod
    def delayStr(mindelay=0, maxdelay=0, unit='', delayformat='.3f'):
        """
        Convert the minimal/maximal delays into string
        """
        if maxdelay is None: # max is None => +infinity
            if mindelay is None:
                raise ValueError("[delayStr] at least one not None delay required")
            elif mindelay < 0: # negative min => explicit [min, +infinity[
                return ("between[{:"+delayformat+"}{unit},+infinity[").format(mindelay, unit=unit)
            #?elif mindelay ==0: return "after"  
            else: # positive min => implicit +infinity
                return ("min({:"+delayformat+"}{unit})").format(mindelay, unit=unit)
        elif mindelay is None: # min is None => -infinity
            if maxdelay < 0: # negative max => implicit ]-infinity,max]
                return ("max({:"+delayformat+"}{unit})").format(maxdelay, unit=unit)
            #?elif maxdelay==0: return "before"
            else:   # positive min => explicit ]-infinity,max]
                return ("between]-infinity,{:"+delayformat+"}{unit}]").format(maxdelay, unit=unit)
        else: # both defined
            if (maxdelay<mindelay):
                raise ValueError("[delayStr] maxdelay({:f}) should be greater or equal to mindelay({:f})".format(maxdelay,mindelay))
            if (mindelay==maxdelay):
                return ("equals({:"+delayformat+"}{unit})").format(maxdelay, unit=unit)
            elif (mindelay==0): # [0,max] => implicit 0
                return ("max({:"+delayformat+"}{unit})").format(maxdelay, unit=unit)
            else:
                return ("between[{:"+delayformat+"},{:"+delayformat+"}{unit}]").format(mindelay, maxdelay, unit=unit)

    @staticmethod
    def checkDelay(delay, mindelay=0, maxdelay=0):
        """
        Check a delay value between (optionals) maxdelay/mindelay
        @param delay:   the delay
        @type delay:    Delay or float
        @param mindelay:    the minimum delay (if defined, default 0)
        @type mindelay: float or Delay or None
        @param maxdelay:    the maximum delay (if defined, default 0)
        @type maxdelay: float or Delay or None
        @rtype: Boolean
        """
        if isinstance(delay, Delay): # delay is a Delay, so we use the Delay comparision
            return (  (mindelay is None or delay >= mindelay)
                  and (maxdelay is None or delay <= maxdelay)
                   )
        else: # we use mindelay/maxdelay comparision (float or Delay)
            return (  (mindelay is None or mindelay <= delay)
                  and (maxdelay is None or maxdelay >= delay)
                   )
    
    # copy of annotationdata/filter/_relations.py#split()
    @staticmethod
    def splitAnnotations(x, y):
        """ x,y (Annotation) """
        if x.GetLocation().IsPoint():
            xstart = x.GetLocation().GetPoint()
            xend = x.GetLocation().GetPoint()
        else:
            xstart = x.GetLocation().GetBegin()
            xend = x.GetLocation().GetEnd()
        if y.GetLocation().IsPoint():
            ystart = y.GetLocation().GetPoint()
            yend = y.GetLocation().GetPoint()
        else:
            ystart = y.GetLocation().GetBegin()
            yend = y.GetLocation().GetEnd()
        return xstart, xend, ystart, yend

    @staticmethod
    def parsePoint(ptStr, default=DEFAULT_PERCENT, prefix=None):
        """
        Parse a point string into it's percent value
        @type ptStr:    str
        @param ptStr:    the point string (start, end, mid, 20%, ...)
        @param type:  float, None
        @param default:  (optional) the default value
        @param type:  str
        @param prefix:  (optional) a prefix for a return of type {xpercent=<value>}
        @rtype: float or dict
        @return:    the percent value, or a {<prefix>percent=<value>} object if prefix is defined
        @raise ValueError:  uncorrect ptStr
        """
        percent=default
        if ptStr in IntervalsDelay.POINTS_PERCENT: percent = IntervalsDelay.POINTS_PERCENT[ptStr];
        elif ptStr in IntervalsDelay.PERCENT_ALIASES: pass;# percent => return DEFAULT_PERCENT
        elif ptStr.endswith('%'):
            try:
                percent = float(ptStr[:-1]) / 100
            except:
                raise ValueError("Invalid percent value '%s'" % ptStr)
        else: raise ValueError("Invalid point '%s', correct values are %s or %s or <p>%%" % (xpoint, joinWithQuote(", ", IntervalsDelay.POINTS_PERCENT.keys()), joinWithQuote("/", IntervalsDelay.PERCENT_ALIASES)));
        return percent if not prefix else {prefix+"percent" : percent}

    @staticmethod
    def relationValues(rel, value, res=None):
        """
        Parse a point string into it's percent value
        @type rel:    str
        @param rel:    the 'relation' part : min, max, eq, ...
            Nota: could be prefixed by a direction part 'before' or 'after' with an optional '_', b.e. 'aftermax', 'before_min'
        @type value:  float, (min, max), {delay=<float>}
        @param value:  the 'numeric' value(s)
        @type res:  a dict
        @param res:  (optional) the result object
        @return:    an dict with mindelay/maxdelay key:value set
        @raise ValueError:  uncorrect relation/value(s)
        """

        def floatOrNone(v):
            return None if v is None else float(v);

        # init res
        if res is None: res={};
        
        # Get the value(s)
        v, vmin, vmax = None, None, None
        # (a) using attributes delay or mindelay/maxdelay
        if ( hasattr(value, 'mindelay') or hasattr(value, 'maxdelay') ):
            vmin = floatOrNone(value.mindelay) if hasattr(value, 'mindelay') else None;
            vmax = floatOrNone(value.maxdelay) if hasattr(value, 'maxdelay') else None;
        elif hasattr(value, 'delay'):
            v = floatOrNone(value.delay); # raise ValueError for invalid number
        # (b) 'dict' using key delay or mindelay/maxdelay
        elif isinstance(value, dict) and ( 'mindelay' in value or 'maxdelay' in value ):
            vmin = floatOrNone(value.get('mindelay', None));
            vmax = floatOrNone(value.get('maxdelay', None));
        elif isinstance(value, dict) and 'delay' in value:
            v = floatOrNone(value['delay']); # raise ValueError for invalid number
        # (c) list/tuple of one (delay), two(min/max) (or more value)
        elif isinstance(value, (list, tuple)) and not isinstance(value, basestring):
            if len(value)>1:  vmin = floatOrNone(value[0]); vmax = floatOrNone(value[1]);
            elif len(value)>0: v = floatOrNone(value[0]);
            else: raise ValueError("Empty value(s) tuple")
        # (d) one (float) value
        else: v = floatOrNone(value);
        #HERE: we have v or (vmin,vmax) set and others are None

        # Check the relation
        if isinstance(rel, str):
            if len(rel)==0: # empty str
                if v is not None: # only one value => equivalent to 'eq'
                    res['maxdelay'] = v; # v
                    res['mindelay'] = v; # v
                else:   # min and max values
                    res['maxdelay'] = vmax; # vmax
                    res['mindelay'] = vmin; # vmin
            else:
                # look for a direction prefix
                relcopy = rel
                for dstr in IntervalsDelay.DIRECTIONS.keys():
                    if rel.startswith(dstr):
                        res['direction'] = dstr # add the direction option
                        rel = rel[len(dstr):] # remove dstr
                        if rel.startswith('_'): rel = rel[1:] # remove '_' if any
                        break;
                if rel.startswith('min'):
                    res['mindelay'] = vmin if vmin is not None else v; # vmin or v
                    res['maxdelay'] = 0 if (res['mindelay'] is None or res['mindelay']<0) else None; # max is +∞ (or 0 if min is negative)
                elif rel.startswith('max'): # max or empty str
                    res['maxdelay'] = vmax if vmax is not None else v; # vmax or v
                    res['mindelay'] = 0 if (res['maxdelay'] is None or res['maxdelay'] >= 0) else None; # min is 0 (or -∞ if max is negative)
                elif rel.startswith('eq'):
                    res['maxdelay'] = v if v is not None else vmax; # v or vmax
                    res['mindelay'] = res['maxdelay'];
                else: raise ValueError("relation '%s' isn't a valid relation, correct values are 'max', 'min' or 'eq'" % relcopy);
        else:
            raise ValueError("relation '%s' isn't a valid relation, correct values are 'max', 'min' or 'eq'" % rel);
        return res;
    
    
    #---------------------------------------------------------------
    # Predicate factory function
    #---------------------------------------------------------------
    @staticmethod
    def create(*args, **kwargs):
        """
        Create a IntervalsDelay predicate.
        For complex predicate, the default is a conjunction ('and').
        Can be specified by a first parameter or the special key 'join'
        @param args: a key-value sequence
            keys have generally the form <point>_<point>(_<rel>)?
                where <point> are in 'start', 'end', 'mid'/'middle' or 'percent' (default)
                  and <rel> are 'max' (default), 'min' or 'eq'
            values are either a single numeric value (for maxdelay and/or mindelay),
                          or a dict of parameters (p.e. {maxdelay=1, xpercent=0.3} after 'percent_start')
            Special keys :
            - name(str): the relation name
            - join(str): 'and' or 'or' 
            - direction(str): the X-Y direction ('before' or 'after')
              . before : positive delay <=> X before Y (~ X is a 'cause' of Y)
              . after : positive delay <=> X after Y (~ X is a 'consequence' of Y)
        @param kwargs: more key-value, same as args
        """
        # the default options
        DEFAULT_OPTS={'maxdelay':0, 'mindelay':0, 'xpercent':0.5, 'ypercent':0.5}
        JOIN_VALUES=('and', 'or');
        atts = {'join':'and'}; # relation attributes
        idOpts = {}; # IntervalDelay constructor options
        
        #----- convert (key, value) into options
        def keyValueOptions(k,v):
            # (0) special keys
            # (0.1) the 'join' attribute
            if k.lower() == 'join':
                if v.lower() in JOIN_VALUES:
                    atts['join'] = v.lower()
                    #print("[keyValueOptions({k},{v})]Set 'join' attribute to {join}".format(join=atts['join'], **locals()))
                else:
                    raise ValueError("Bad join value '%s', correct values are %s" % (v, joinWithQuote(", ", *JOIN_VALUES, lastsep=" or ")));
                return None;
            # (0.2) the 'name' attribute
            if k.lower() == 'name':
                atts['name'] = v
                return None;
            # (0.3) the 'direction' attribute
            if k.lower() == 'direction':
                idOpts['direction'] = v
                return None;
    
            # build the final options
            opts = v.copy() if isinstance(v, dict) else {};
    
            # (a) split key into <point>_<point>(_<rel>)?
            xpoint, ypoint, rel = 3 * [None]
            ksplit = k.lower().split('_', 2); # nota: rel could contain a '_' (p.e. after_max)
            if len(ksplit)<2:
                raise ValueError("Bad point_point value '%s'" % k);
            else:
                xpoint=ksplit[0]; ypoint=ksplit[1];
            if len(ksplit)>2: rel=ksplit[2];
            
            # (b) set xpercent/ypercent
            # xpoint => update xpercent
            xpercent = IntervalsDelay.parsePoint(xpoint, opts.get('xpercent')) # raise ValueError
            if xpercent is not None: opts['xpercent'] = xpercent;
            #?  else:   opts['xpercent'] = DEFAULT_OPTS['xpercent'];
            # ypoint => update xpercent
            ypercent = IntervalsDelay.parsePoint(ypoint, opts.get('ypercent')) # raise ValueError
            if ypercent is not None: opts['ypercent'] = ypercent;
            #?  else:   opts['ypercent'] = DEFAULT_OPTS['ypercent'];
            
            # (c) set mindelay/maxdelay
            # rel (and numeric value or v.delay) => update min/maxdelay
            if not rel: rel=''; # remplace falsy value of rel by the empty string
            IntervalsDelay.relationValues(rel, v, opts); # set mindelay/maxdelay in opts, raise ValueError
            if 'delay' in opts: del opts['delay']; # remove 'delay', now convert into mindelay/maxdelay
            return opts;
            
        #-----
        def buildID(idOpts, opts):  # build IntervalsDelay with 2 dict of options
            bOpts = idOpts.copy(); # make a copy of idOpts
            bOpts.update(opts); # update with opts value
            return IntervalsDelay(**bOpts); # build IntervalsDelay with all options
    
        #-----

        # look for the first argument (JOIN_VALUES/IntervalsDelay.DIRECTIONS)
        iArg=0;
        while (iArg<len(args)):
            if (args[iArg].lower() in JOIN_VALUES):
                atts['join'] = args[iArg].lower();  # the join type
                iArg+=1
            elif (args[iArg].lower() in IntervalsDelay.DIRECTIONS):
                idOpts['direction'] = args[iArg].lower();  # the direction type
                iArg+=1
            else:
                break
        
        lOpts = []
        # other arguments
        while iArg < len(args):
            k = args[iArg]; iArg+=1
            v = DEFAULT_OPTS;
            if iArg<len(args):
                v = args[iArg]; iArg+=1
            opts = keyValueOptions(k,v)
            if opts: lOpts.append(opts);
        # and the kwargs
        for k, v in kwargs.items():
            opts = keyValueOptions(k,v)
            if opts: lOpts.append(opts);
    
        # create IntervalsDelay for each lOpts and join them
        lIntDelays = [buildID(idOpts,opts) for opts in lOpts]
    
        #TODO: reduce AND predicates with the same (xpercent,ypercent)
        # b.e. (start_start_max=2, start_start_min=1)
        #   => {xpercent=0,ypercent=0, maxdelay=2, mindelay=0} AND {xpercent=0,ypercent=0, maxdelay=None, mindelay=1}
        #  --> {xpercent=0,ypercent=0, maxdelay=2, mindelay=1}

        if len(lIntDelays)==1:
            if atts.get('name') is not None:
                lIntDelays[0].name = atts['name']
            return lIntDelays[0]
        elif atts['join']=='or':
            #print "[create({args}, {kwargs})] => OrPredicates({lIntDelaysStr},{atts})".format(lIntDelaysStr=[str(item) for item in lIntDelays] ,**locals())
            return OrPredicates(*lIntDelays, **atts)
        else:
            return AndPredicates(*lIntDelays, **atts)
    
    
#---------------------------------------------------------------
class CheckedIntervalsDelay(Delay, IntervalsDelay):
    def __init__(self, delay, mindelay=0, maxdelay=0, xpercent=IntervalsDelay.DEFAULT_PERCENT, ypercent=IntervalsDelay.DEFAULT_PERCENT, name=''):
        Delay.__init__(self, delay)
        IntervalsDelay.__init__(self, mindelay=mindelay, maxdelay=maxdelay, xpercent=xpercent, ypercent=ypercent, name=name)

    @property
    def delay(self):
        """
        Get the actual delay.
        """
        return  self

    # -----------------------------------------------------------------------
    # --- formating methods
    # -----------------------------------------------------------------------

    # -----------------------------------------------------------------------
    def __repr__(self):
        return "%s(%s=%r~%r)" % (self.__class__.__name__, IntervalsDelay.__format__(self, 's'), self.value, self.margin)

    # -----------------------------------------------------------------------
    def __str__(self):
        return IntervalsDelay.__str__(self) # default to only the IntervalsDelay predicate
        #return "(%s=%f~%.2f)" % (IntervalsDelay.__format__(self, 's'), self.value, self.margin)

    # -----------------------------------------------------------------------
    def __format__(self, f):
        """
        Format a CheckedIntervalsDelay
        @param f: the format
            if f is 's', format like a IntervalsDelay, i.e. the predicate name
            else, the format as the form '[<fid>=]<fd>', where :
              <fid> is an optional format for the IntervalsDelay (predicate) part
              <fd> is the format for the Delay (value) part
            Some example with a 'start_start_max(2)' predicate and a delay of +1.5 (margin 0.2)
              - 'f' => only the Delay part => "1.50000~0.2"
              - '.2f' => only the Delay part => "1.5~0.2"
              - 's=.2f' => <fid> is 's' and <fd> is '.2f' => "start_start_max(2)=1.5~0.2"
              - 's= =+3.2f' => <fid> is 's' and <fd> is '0=+3.2f' => "start_start_max(2)=+ 1.5~0.2"
              - 's=.2f~' => <fid> is 's' and <fd> is '.2f~' => "start_start_max(2)=1.5" (no margin)
              - 's=' => <fid> is 's' and <fd> is '' (default) => "start_start_max(2)=1.50000~0.2" (same as 's=f')
              - 's' => "start_start_max(2)"
        """
        # easy cases
        if f=='r':
            return repr(self)
        if f=='s':
            return str(self)
        # other case
        delayFormat = 'f'; idFormat = '' # default delay/interval delay format
        if f:
            iEqual = f.find('=') # split with 1st '='
            if iEqual>=0:
                idFormat = f[:iEqual]; delayFormat = f[(iEqual+1):]
            else:   # any equals => only delayFormat
                delayFormat = f
        res = ''
        if idFormat: # prepend Interval delay
            res += IntervalsDelay.__format__(self, idFormat) + '='
        res += Delay.__format__(self, delayFormat)
        return res


#---------------------------------------------------------------
# Old <point>_<point> methods rewrite with IntervalsDelay
#---------------------------------------------------------------

def start_start(xstart, xend, ystart, yend, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between 2 intervals starts
      |----x----|
          |---y---|
      |~d~|          mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=0, ypercent=0).check(xstart, xend, ystart, yend)

def start_end(xstart, xend, ystart, yend, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between first interval start and second interval end
      |----x----|
          |---y---|
      |~~~~~d~~~~~|  mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=0, ypercent=1).check(xstart, xend, ystart, yend)

def end_start(xstart, xend, ystart, yend, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between first interval end and second interval start
      |-x-|
            |-y-|
          |d|        mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=1, ypercent=0).check(xstart, xend, ystart, yend)

def end_end(xstart, xend, ystart, yend, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between 2 intervals ends
      |----x----|
          |---y---|
                |d|  mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=1, ypercent=1).check(xstart, xend, ystart, yend)

def percent_start(xstart, xend, ystart, yend, mindelay=0, maxdelay=0, xpercent=0.5):
    """
    Maximal/minimal delay between a fraction of the first interval and the start of the second interval
       |-+--x----|    where the '+' mark xpercent of the interval x
           |---y---|
         |d|          mindelay <= d  <= maxdelay
     nota: startStartDelay <=> percentStartDelay(xpercent=0), endStartDelay <=> percentStartDelay(xpercent=1)
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent, ypercent=0).check(xstart, xend, ystart, yend)


def percent_end(xstart, xend, ystart, yend, mindelay=0, maxdelay=0, xpercent=0.5):
    """
    Maximal/minimal delay between a fraction of the first interval and the end of the second interval
       |-+--x----|    where the '+' mark xpercent of the interval x
           |---y---|
         |~~~~d~~~~|  mindelay <= d
     nota: startEndDelay <=> percentEndDelay(xpercent=0), endEndDelay <=> percentEndDelay(xpercent=1), 
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent, ypercent=1).check(xstart, xend, ystart, yend)


def percent_percent(xstart, xend, ystart, yend, mindelay=0, maxdelay=0, xpercent=0.5, ypercent=0.5):
    """
    Maximal/minimal delay between a fraction of the first interval and a fraction of the second interval
       |-+--x----|    where the '+' mark xpercent of the interval x
           |---y+--|  where the '+' mark ypercent of the interval y
         |~~~d~~|     mindelay <= d
     nota: startStartDelay <=> percentPercentDelay(xpercent=0, ypercent=0), endStartDelay <=> percentPercentDelay(xpercent=1, ypercent=0), 
     nota: startEndDelay <=> percentPercentDelay(xpercent=0, ypercent=1), endEndDelay <=> percentPercentDelay(xpercent=1, ypercent=1), 
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent, ypercent).check(xstart, xend, ystart, yend)

