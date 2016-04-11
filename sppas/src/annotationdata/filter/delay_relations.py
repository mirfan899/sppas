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
    
    def __init__(self, mindelay=0, maxdelay=0, xpercent=DEFAULT_PERCENT, ypercent=DEFAULT_PERCENT, name=''):
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
        @param name:    custom name for the relation
        @type name: str
        """
        IntervalsDelay.validMinMaxDelay(mindelay, maxdelay) # raise ValueError
        self.mindelay = mindelay
        self.maxdelay = maxdelay
        self.xpercent = xpercent
        self.ypercent = ypercent
        self.name = name

    def delay(self, x1, x2, y1, y2):
        """
        Compute the actual delay between the two intervals
        @param x1:  first interval start point
        @param x2:  first interval end point
        @param y1:  second interval start point
        @param y2:  second interval end point
        """
        return ( ( (1-self.ypercent) * y1.GetMidpoint() + self.ypercent * y2.GetMidpoint() )
               - ( (1-self.xpercent) * x1.GetMidpoint() + self.xpercent * x2.GetMidpoint() )
               )

    def check(self, x1, x2, y1, y2):
        """
        Check if the delay between the two intervals respect max/mindelay
        @param x1:  first interval start point
        @param x2:  first interval end point
        @param y1:  second interval start point
        @param y2:  second interval end point
        """
        delay = self.delay(x1, x2, y1, y2)
        #print "[{self.xpercent},{self.ypercent}] delay({x1}, {x2}, {y1}, {y2}) = {delay}".format(**locals())
        if IntervalsDelay.checkDelay(delay, self.mindelay, self.maxdelay):
            return CheckedIntervalsDelay(delay, **{a:getattr(self,a) for a in ['mindelay', 'maxdelay', 'xpercent', 'ypercent']})
        else:
            return None;

    def __call__(self, *args, **kwargs):
        """
        IntervalsDelay's predicate
        Accecpt either:
            - 2 Annotation arguments (x,y)
            - 4 Point arguments (x1, x2, y1, y2)
        """
        if (len(args)==2): # 2 arguments => x,y (Annotation) => split into x1, x2, y1, y2
            return self.check(*IntervalsDelay.splitAnnotations(*args))
        elif (len(args)==4): # 4 arguments => yet x1, x2, y1, y2
            return self.check(*args)
        else:
            raise ValueError("IntervalsDelay's function require 2 Annotation parameters or 4 Point parameters")

    def __str__(self):
        if self.name:
            return self.name
        else:
            return '_'.join([IntervalsDelay.pointStr(self.xpercent), IntervalsDelay.pointStr(self.ypercent), IntervalsDelay.delayStr(self.mindelay, self.maxdelay)])

    def __cmp__(self, other):
        """
        Compare IntervalsDelay based on 
            - (1) the first interval point (i.e. xpercent)
            - (2) the second interval point (i.e. ypercent)
            - (3) the minimal delay (None ~ -infinity)
            - (3) the maximal delay (None ~ +infinity)
        """
        def sign(x):
            if x<0: return -1;
            if x>0: return +1;
            return 0;

        res = self.xpercent - other.xpercent # start < mid < end
        if res: return sign(res);
        res = self.ypercent - other.ypercent # start < mid < end
        if res: return sign(res);
        # compare mindelay (None is -infinity)
        if self.mindelay is None:
            res = ( 0 if other.mindelay is None # both None => 'equals'
                    else -1 ) # self(-infinity) < other
        else:
            res = ( +1 if other.mindelay is None # self > other(-infinity)
                    else self.mindelay - other.mindelay ) # self - other
        if res: return sign(res);
        # compare maxdelay (None is +infinity)
        if self.maxdelay is None:
            res = ( 0 if other.maxdelay is None # both None => 'equals'
                    else +1 ) # self(+infinity) > other
        else:
            res = ( -1 if other.maxdelay is None # self < other(+infinity)
                    else self.maxdelay - other.maxdelay ) # self - other
        return sign(res);

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
        @type delay:    float
        @param mindelay:    the minimum delay (if defined, default 0)
        @type mindelay: float or None
        @param maxdelay:    the maximum delay (if defined, default 0)
        @type maxdelay: float or None
        @rtype: Boolean
        """
        return (  (mindelay is None or delay >= mindelay)
                and (maxdelay is None or delay <= maxdelay)
                )
    
    # copy of annotationdata/filter/_relations.py#split()
    @staticmethod
    def splitAnnotations(x, y):
        """ x,y (Annotation) """
        if x.GetLocation().IsPoint():
            x1 = x.GetLocation().GetPoint()
            x2 = x.GetLocation().GetPoint()
        else:
            x1 = x.GetLocation().GetBegin()
            x2 = x.GetLocation().GetEnd()
        if y.GetLocation().IsPoint():
            y1 = y.GetLocation().GetPoint()
            y2 = y.GetLocation().GetPoint()
        else:
            y1 = y.GetLocation().GetBegin()
            y2 = y.GetLocation().GetEnd()
        return x1, x2, y1, y2

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
            elif rel.startswith('min'):
                res['mindelay'] = vmin if vmin is not None else v; # vmin or v
                res['maxdelay'] = 0 if (res['mindelay'] is None or res['mindelay']<0) else None; # max is +∞ (or 0 if min is negative)
            elif rel.startswith('max'): # max or empty str
                res['maxdelay'] = vmax if vmax is not None else v; # vmax or v
                res['mindelay'] = 0 if (res['maxdelay'] is None or res['maxdelay'] >= 0) else None; # min is 0 (or -∞ if max is negative)
            elif rel.startswith('eq'):
                res['maxdelay'] = v if v is not None else vmax; # v or vmax
                res['mindelay'] = res['maxdelay'];
            else: raise ValueError("relation '%s' isn't a valid relation, correct values are 'max', 'min' or 'eq'" % rel);
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
        @param kwargs: more key-value, same as args
        """
        # the default options
        DEFAULT_OPTS={'maxdelay':0, 'mindelay':0, 'xpercent':0.5, 'ypercent':0.5}
        JOIN_VALUES=('and', 'or');
        atts = {'join':'and'}; # relation attributes
        
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
    
            # build the final options
            opts = v.copy() if isinstance(v, dict) else {};
    
            # (a) split key into <point>_<point>(_<rel>)?
            xpoint, ypoint, rel = 3 * [None]
            ksplit = k.lower().split('_', 2);
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
    
        # look for the first argument
        iArg=0;
        if len(args)>0 and (args[iArg].lower() in JOIN_VALUES):
            atts['join'] = args[iArg].lower(); iArg+=1  # the join type
        
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
        lIntDelays = map(lambda opts: IntervalsDelay(**opts), lOpts)
    
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
class CheckedIntervalsDelay(IntervalsDelay):
    def __init__(self, delay, mindelay=0, maxdelay=0, xpercent=IntervalsDelay.DEFAULT_PERCENT, ypercent=IntervalsDelay.DEFAULT_PERCENT, name=''):
        IntervalsDelay.__init__(self, mindelay=mindelay, maxdelay=maxdelay, xpercent=xpercent, ypercent=ypercent, name=name)
        self.delay=delay;

    def delay(self):
        """
        Get the actual delay.
        """
        return  self.delay


#---------------------------------------------------------------

def start_start(x1, x2, y1, y2, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between 2 intervals starts
      |----x----|
          |---y---|
      |~d~|          mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=0, ypercent=0).check(x1, x2, y1, y2)

def start_end(x1, x2, y1, y2, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between first interval start and second interval end
      |----x----|
          |---y---|
      |~~~~~d~~~~~|  mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=0, ypercent=1).check(x1, x2, y1, y2)

def end_start(x1, x2, y1, y2, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between first interval end and second interval start
      |-x-|
            |-y-|
          |d|        mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=1, ypercent=0).check(x1, x2, y1, y2)

def end_end(x1, x2, y1, y2, mindelay=0, maxdelay=0):
    """
    Maximal/minimal delay between 2 intervals ends
      |----x----|
          |---y---|
                |d|  mindelay <= d <= maxdelay
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent=1, ypercent=1).check(x1, x2, y1, y2)

def percent_start(x1, x2, y1, y2, mindelay=0, maxdelay=0, xpercent=0.5):
    """
    Maximal/minimal delay between a fraction of the first interval and the start of the second interval
       |-+--x----|    where the '+' mark xpercent of the interval x
           |---y---|
         |d|          mindelay <= d  <= maxdelay
     nota: startStartDelay <=> percentStartDelay(xpercent=0), endStartDelay <=> percentStartDelay(xpercent=1)
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent, ypercent=0).check(x1, x2, y1, y2)


def percent_end(x1, x2, y1, y2, mindelay=0, maxdelay=0, xpercent=0.5):
    """
    Maximal/minimal delay between a fraction of the first interval and the end of the second interval
       |-+--x----|    where the '+' mark xpercent of the interval x
           |---y---|
         |~~~~d~~~~|  mindelay <= d
     nota: startEndDelay <=> percentEndDelay(xpercent=0), endEndDelay <=> percentEndDelay(xpercent=1), 
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent, ypercent=1).check(x1, x2, y1, y2)


def percent_percent(x1, x2, y1, y2, mindelay=0, maxdelay=0, xpercent=0.5, ypercent=0.5):
    """
    Maximal/minimal delay between a fraction of the first interval and a fraction of the second interval
       |-+--x----|    where the '+' mark xpercent of the interval x
           |---y+--|  where the '+' mark ypercent of the interval y
         |~~~d~~|     mindelay <= d
     nota: startStartDelay <=> percentPercentDelay(xpercent=0, ypercent=0), endStartDelay <=> percentPercentDelay(xpercent=1, ypercent=0), 
     nota: startEndDelay <=> percentPercentDelay(xpercent=0, ypercent=1), endEndDelay <=> percentPercentDelay(xpercent=1, ypercent=1), 
    """
    return IntervalsDelay(mindelay, maxdelay, xpercent, ypercent).check(x1, x2, y1, y2)

