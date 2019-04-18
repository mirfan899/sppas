#!/usr/bin/env python

import sys
import os

sppasDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, sppasDir)
from sppas.src.ui.phoenix.main_app import sppasApp
from sppas.src.config import sg

# Create and run the wx application
app = sppasApp()
status = app.run()
if status != 0:
    print("{:s} exits with error status: {:d}"
          "".format(sg.__name__, status))
sys.exit(status)
