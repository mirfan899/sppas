#!/usr/bin/env python2
# encoding: utf-8

from os.path import abspath, dirname, join
import sys

SPPAS = dirname(dirname(dirname(dirname(abspath(__file__)))))
sys.path.append(join(SPPAS, 'sppas', 'src'))
samples = join(dirname(dirname(dirname(abspath(__file__)))), 'samples')
