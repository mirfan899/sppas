#!/bin/bash
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://www.lpl-aix.fr/~bigi/sppas
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2014  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# Summary: SPPAS GUI run script
# ---------------------------------------------------------------------------


# ===========================================================================
# Fix global variables
# ===========================================================================

# Fix the locale with a generic value!
LANG='C'

# Program infos
PROGRAM_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)
PROGRAM_NAME=$(grep -i program: $PROGRAM_DIR/README.txt | awk -F":" '{print $2}')
PROGRAM_AUTHOR=$(grep -i author: $PROGRAM_DIR/README.txt | awk -F":" '{print $2}')
PROGRAM_VERSION=$(grep -i version: $PROGRAM_DIR/README.txt | awk -F":" '{print $2}')
PROGRAM_COPYRIGHT=$(grep -i copyright: $PROGRAM_DIR/README.txt | awk -F":" '{print $2}')

# Expected files and directories
BIN_DIR="sppas/bin"
ETC_DIR="sppas/etc"
DOC_DIR="doc"
SAMPLES_DIR="samples"

# User-Interface
MSG_HEADER="${PROGRAM_NAME} ${PROGRAM_VERSION}, a program written by ${PROGRAM_AUTHOR}."
MSG_FOOTER="${PROGRAM_NAME} ${PROGRAM_VERSION} finished."
TODAY=$(date "+%Y-%m-%d")

BLACK='\e[0;30m'
WHITE='\e[1;37m'
LIGHT_GRAY='\e[0;37m'
DARK_GRAY='\e[1;30m'
BLUE='\e[0;34m'
DARK_BLUE='\e[1;34m'
GREEN='\e[0;32m'
LIGHT_GREEN='\e[1;32m'
CYAN='\e[0;36m'
LIGHT_CYAN='\e[1;36m'
RED='\e[0;31m'
LIGHT_RED='\e[1;31m'
PURPLE='\e[0;35m'
LIGHT_PURPLE='\e[1;35m'
BROWN='\e[0;33m'
YELLOW='\e[1;33m'
NC='\e[0m' # No Color



# ===========================================================================
# Functions generic
# ===========================================================================


# Print a title message on stdout
# Parameters:
#   $1: message
function fct_echo_title {
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------"
    echo -e "${BROWN}$@"
    echo -e "${LIGHT_GREEN}-----------------------------------------------------------------------${NC}"
    echo
}


# Print a warning message.
# Parameters:
#   $1: message
function fct_echo_warning {
    echo -e "${RED}[WARNING] $@${NC}"
    echo
}

# Print an error message, then exit
# Parameters:
#   $1: error message
function fct_exit_error {
    fct_echo_title $MSG_HEADER
    echo -e "${RED}[ ERROR ] $1${NC}"
    echo
    fct_echo_title $MSG_FOOTER
    exit 1
}


# ===========================================================================
# Functions
# ===========================================================================


# Clean the current directory: remove temporary files
function fct_clean_temp {
    rm "$PROGRAM_DIR"/tmp*     2>> /dev/null;
    rm "$PROGRAM_DIR"/*.log    2>> /dev/null;
}



# ===========================================================================
# MAIN
# ===========================================================================


fct_echo_title $MSG_HEADER  # Print the header message on stdout
fct_clean_temp              # Remove temporary files (if any)

# Test python
PYTHON="python2"
$PYTHON --version >> /dev/null &> /dev/null
if [ $? != "0" ]; then
    PYTHON="python"
    $PYTHON --version >> /dev/null &> /dev/null
    if [ $? != "0" ]; then
        fct_exit_error "Python is not an internal command of your operating system. For any help, have a look on the SPPAS installation page on http://www.sppas.org."
    fi
fi

# get the name of the SE
unamestr="`uname`"

echo "Command: "$PYTHON
echo "System:  "$unamestr

# Linux
if [[ "$unamestr" == 'Linux' ]]; then
    $PYTHON "$PROGRAM_DIR"/$BIN_DIR/checkwx.py
    wxstatus="$?"
    if [[ $wxstatus == "1" ]]; then
        fct_echo_warning "It seems you are using SPPAS with an old version of wxPython.\nUpdate it at: <http://www.wxpython.org/>."
    elif [[ $wxstatus == "2" ]]; then
        fct_exit_error "Wxpython is not installed. Get it at: <http://www.wxpython.org/> "
    fi
    $PYTHON "$PROGRAM_DIR"/$BIN_DIR/sppasgui.py

# Cygwin
elif [[ "$unamestr" == 'CYGWIN_*' ]]; then
   fct_echo_warning "It seems you are using SPPAS under Cygwin... Some troubles can occur!"
   $PYTHON "$PROGRAM_DIR"/$BIN_DIR/sppasgui.py

# MacOS
elif [[ "$unamestr" == 'Darwin' ]]; then
    $PYTHON "$PROGRAM_DIR"/$BIN_DIR/checkwx.py
    wxstatus="$?"
    if [[ $wxstatus == "1" ]]; then
        fct_echo_warning "It seems you are using SPPAS with an old version of wxPython.\nUpdate it at: <http://www.wxpython.org/>."
        export VERSIONER_PYTHON_PREFER_32_BIT=yes
        arch -i386 $PYTHON "$PROGRAM_DIR"/$BIN_DIR/sppasgui.py
    elif [[ $wxstatus == "2" ]]; then
        fct_exit_error "Wxpython is not installed. Get it at: <http://www.wxpython.org/> "
    else
        $PYTHON "$PROGRAM_DIR"/$BIN_DIR/sppasgui.py
    fi

else
    fct_exit_error "Your operating system is not supported, or the "uname" command\nreturns an unexpected entry.\nPlease, send an e-mail to <brigitte.bigi@gmail.com>. "
fi


fct_echo_title $MSG_FOOTER  # Print the footer message on stdout

# ----------------------------------------------------------------------------
