import sys
from os.path import abspath, dirname
SRC = dirname(dirname(dirname(abspath(__file__))))
if not SRC in sys.path:
    sys.path.append(SRC)