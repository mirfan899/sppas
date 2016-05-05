#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# Copyright (C) 2013  Brigitte Bigi
#
# This file is part of SPPAS.
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
# along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.

from os.path import splitext

from trsfactory import TrsFactory
from annotationdata.annotation import Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.ptime.interval import TimeInterval
from annotationdata.label.label import Label


def read(filename):
    """ Read a transcription file.
        Parameters:
            - filename (string): the file name (including path)
        Exception:   IOError
        Return:      a Transcription
    """
    ext = getExtension(filename).lower()
    transcription = TrsFactory.NewTrs(ext)
    try:
        transcription.read(filename)
    except IOError:
        raise
    except UnicodeError:
        raise UnicodeError('Encoding error: %r contains non-UTF-8 characters.' % filename)
    except Exception as e:
        raise Exception('Invalid transcription file: %s' % e)
    transcription.MinTime = transcription.GetBegin()
    transcription.MaxTime = transcription.GetEnd()
    return transcription


def write(filename, transcription):
    """ Write a transcription file.
        Parameters:
            - filename (string): the file name (including path)
            - transcription (Transcription): the Transcription to write.
        Exception:   IOError
        Return:      none
    """
    if transcription.IsEmpty():
        raise Exception('Cannot save a Transcription file without tiers.')
    elif all(tier.IsEmpty() for tier in transcription):
        raise Exception('Cannot save a Tier without annotations.')

    begin = TimePoint(transcription.GetBegin())
    end = TimePoint(transcription.GetEnd())
    for tier in transcription:
        if tier.IsEmpty():
            tier.Append(Annotation(TimeInterval(begin, end)))

    ext = getExtension(filename).lower()
    output = TrsFactory.NewTrs(ext)
    mintime = transcription.MinTime
    maxtime = transcription.MaxTime

    for tier in transcription:
        if tier.IsPoint():
            continue
        begin = TimePoint(tier.GetBegin())
        end = TimePoint(tier.GetEnd())
        if mintime is not None and TimePoint(mintime) < begin:
            gap = Annotation(TimeInterval(TimePoint(mintime), begin))
            tier.Add(gap)
        if maxtime is not None and end < TimePoint(maxtime):
            gap = Annotation(TimeInterval(end, TimePoint(maxtime)))
            tier.Add(gap)

    output.Set(transcription, transcription.Name)
    output.write(filename)

def getExtension(filename):
    return splitext(filename)[1][1:]
