#!/usr/bin python
"""

:author:       Fix Me
:date:         Now
:contact:      me@me.org
:license:      GPL, v3
:copyright:    Copyright (C) 2017  Fixme

:summary:      This is the skeleton of a python script.

"""
import os
import sys
SPPAS_IS_HERE = os.getcwd()
sys.path.append(SPPAS_IS_HERE)

# Get SPPAS API for reading/writing/modifying annotated files
import sppas.src.annotationdata.aio as trsio
from sppas.src.annotationdata import Transcription
from sppas.src.annotationdata import Tier
from sppas.src.annotationdata import Annotation
from sppas.src.annotationdata import Label
from sppas.src.annotationdata import TimePoint
from sppas.src.annotationdata import TimeInterval
from sppas.src.annotationdata import Sel
from sppas.src.annotationdata import Rel
from sppas.src.annotationdata import Filter, SingleFilter, RelationFilter

# ----------------------------------------------------------------------------
# Global variables
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Functions
# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# This is the python entry point:
if __name__ == '__main__':
    pass
