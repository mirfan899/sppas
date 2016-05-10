#!/usr/bin/env python2
# encoding: utf-8

from os.path import abspath, dirname, join

SPPAS   = dirname(dirname(dirname(dirname(abspath(__file__)))))
SAMPLES = join(dirname(abspath(__file__)), 'samples')
TEMP    = join(dirname(abspath(__file__)), 'temp')

SPPASSAMPLES = join(SPPAS, "samples")
