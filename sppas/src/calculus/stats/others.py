def percentile(xs, p=(25, 50, 75), sort=True):
493      """Returns the pth percentile of an unsorted or sorted numeric vector.
494
495      This is equivalent to calling quantile(xs, p/100.0); see L{quantile}
496      for more details on the calculation.
497
498      Example:
499
500          >>> round(percentile([15, 20, 40, 35, 50], 40), 2)
501          26.0
502          >>> for perc in percentile([15, 20, 40, 35, 50], (0, 25, 50, 75, 100)):
503          ...     print "%.2f" % perc
504          ...
505          15.00
506          17.50
507          35.00
508          45.00
509          50.00
510
511      @param xs: the vector itself.
512      @param p: the percentile we are looking for. It may also be a list if you
513        want to calculate multiple quantiles with a single call. The default
514        value calculates the 25th, 50th and 75th percentile.
515      @param sort: whether to sort the vector. If you know that the vector is
516        sorted already, pass C{False} here.
517      @return: the pth percentile, which will always be a float, even if the vector
518        contained integers originally. If p is a list, the result will also be a
519        list containing the percentiles for each item in the list.
520      """
521      if hasattr(p, "__iter__"):
522          return quantile(xs, (x/100.0 for x in p), sort)
523      return quantile(xs, p/100.0, sort)

def quantile(xs, q=(0.25, 0.5, 0.75), sort=True):
583      """Returns the qth quantile of an unsorted or sorted numeric vector.
584
585      There are a number of different ways to calculate the sample quantile. The
586      method implemented by igraph is the one recommended by NIST. First we
587      calculate a rank n as q(N+1), where N is the number of items in xs, then we
588      split n into its integer component k and decimal component d. If k <= 1,
589      we return the first element; if k >= N, we return the last element,
590      otherwise we return the linear interpolation between xs[k-1] and xs[k]
591      using a factor d.
592
593      Example:
594
595          >>> round(quantile([15, 20, 40, 35, 50], 0.4), 2)
596          26.0
597
598      @param xs: the vector itself.
599      @param q: the quantile we are looking for. It may also be a list if you
600        want to calculate multiple quantiles with a single call. The default
601        value calculates the 25th, 50th and 75th percentile.
602      @param sort: whether to sort the vector. If you know that the vector is
603        sorted already, pass C{False} here.
604      @return: the qth quantile, which will always be a float, even if the vector
605        contained integers originally. If q is a list, the result will also be a
606        list containing the quantiles for each item in the list.
607      """
608      if not xs:
609          raise ValueError("xs must not be empty")
610
611      if sort:
612          xs = sorted(xs)
613
614      if hasattr(q, "__iter__"):
615          qs = q
616          return_single = False
617      else:
618          qs = [q]
619          return_single = True
620
621      result = []
622      for q in qs:
623          if q < 0 or q > 1:
624              raise ValueError("q must be between 0 and 1")
625          n = float(q) * (len(xs)+1)
626          k, d = int(n), n-int(n)
627          if k >= len(xs):
628              result.append(xs[-1])
629          elif k < 1:
630              result.append(xs[0])
631          else:
632              result.append((1-d) * xs[k-1] + d * xs[k])
633      if return_single:
634          result = result[0]
635      return result
636