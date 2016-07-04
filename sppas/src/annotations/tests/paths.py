#!/usr/bin/env python2
# encoding: utf-8

import sys
from os.path import abspath, dirname, join
SPPAS = dirname(dirname(dirname(dirname(dirname(abspath(__file__))))))
sys.path.append( join(SPPAS, "sppas", "src") )

TEMP = join(dirname(abspath(__file__)), "temp")
