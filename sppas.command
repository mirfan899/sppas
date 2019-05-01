#!/bin/bash
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              the automatic
#           \__   |__/  |__/  |___| \__             annotation and
#              \  |     |     |   |    \             analysis
#           ___/  |     |     |   | ___/              of speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2018  Brigitte Bigi
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
# File:    sppas.command
# Author:  Brigitte Bigi
# Summary: SPPAS GUI run script for unix-based systems.
# ---------------------------------------------------------------------------


# ===========================================================================
# Fix global variables
# ===========================================================================

# Fix the locale with a generic value!
LANG='C'

# Program infos
PROGRAM_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)


# ===========================================================================
# MAIN
# ===========================================================================
export PYTHONIOENCODING=UTF-8

PYTHON=""

# Search for pythonw, v2
for cmd in `which -a pythonw`;
do
    v=`$cmd -c "import sys; print(sys.version_info[0])"`;
    if [ $v == "2" ]; then
        PYTHON=$cmd;
    fi;
done

# Search for pythonw, v3
if [ $PYTHON == "" ]; then
    for cmd in `which -a pythonw`;
    do
        v=`$cmd -c "import sys; print(sys.version_info[0])"`;
        if [ $v == "3" ]; then
            PYTHON=$cmd;
        fi;
    done
fi

# Search for python, v2
if [ $PYTHON == "" ]; then
    for cmd in `which -a python`;
    do
        v=`$cmd -c "import sys; print(sys.version_info[0])"`;
        if [ $v == "2" ]; then
            PYTHON=$cmd;
        fi;
    done
fi

# Search for python, v3
if [ $PYTHON == "" ]; then
    for cmd in `which -a python`;
    do
        v=`$cmd -c "import sys; print(sys.version_info[0])"`;
        if [ $v == "3" ]; then
            PYTHON=$cmd;
        fi;
    done
fi

if [ $PYTHON == "" ]; then
    echo "Python is not an internal command of your operating system."
    echo "For any help, take a look at the SPPAS installation page: http://www.sppas.org."
    exit -1
fi

# Get the name of the system
unamestr="`uname | cut -f1 -d'_'`"

echo "Command: "$PYTHON
echo "System:  "$unamestr

# Cygwin
if [[ "$unamestr" == 'CYGWIN' ]]; then
   if [ -z $DISPLAY ]; then
       echo "Unable to access the X Display. Did you enabled XWin server?"
       exit -1
   fi
fi

$PYTHON $PROGRAM_DIR/sppas/bin/sppasgui.py
