#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
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
# File: param.py
# ----------------------------------------------------------------------------

import os.path

from sppas import SPPAS_CONFIG_DIR
from sppas.src.annotations.cfgparser import AnnotationConfigParser
from . import DEFAULT_OUTPUT_EXTENSION

# ----------------------------------------------------------------------------


class annotationParam( object ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      One SPPAS annotation parameters (Private class).

    """
    def __init__(self, filename=None):
        """
        Creates a new annotationParam instance.

        """
        # An identifier to represent this annotation step
        self.key  = None
        # The name of the annotation
        self.name = ""
        # The description of the annotation
        self.desc = ""
        # The annotation status
        self.activated = False
        self.invalid = False
        # The language resource
        self.langres = []
        # The list of options
        self.options = []

        # OK... now fix all values from the given file
        if filename:
            self.parse( filename )

    # ------------------------------------------------------------------------

    def parse(self, filename):
        p = AnnotationConfigParser()
        p.parse( filename )
        self.options = p.get_options()
        self.langres = p.get_resources()
        conf = p.get_config()
        self.key   = conf['id']
        self.name  = conf.get('name', "")
        self.descr = conf.get('descr', "")

    # ------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------

    def set_activate(self, activate):
        self.activated = activate
        if activate is True and self.invalid is True:
            self.activated = False

    def set_lang(self, lang):
        if len(self.langres)>0:
            try:
                self.langres[0].set_lang( lang )
            except Exception:
                self.invalid = True
                self.activated = False

    # ------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------

    def get_key(self):
        return self.key

    def get_name(self):
        return self.name

    def get_descr(self):
        return self.descr

    def get_activate(self):
        return self.activated


    def get_lang(self):
        if len(self.langres)>0:
            return self.langres[0].get_lang()
        return ""

    def get_langlist(self):
        if len(self.langres)>0:
            return self.langres[0].get_langlist()
        return []

    def get_langresource(self):
        if len(self.langres)>0:
            return self.langres[0].get_langresource()
        return []


    def get_options(self):
        return self.options

    def get_option(self, step):
        return self.options[step]

    def get_option_by_key(self, key):
        for opt in self.options:
            if key == opt.get_key():
                return opt

# ----------------------------------------------------------------------------

class sppasParam:
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      SPPAS annotations parameters manager.

    """
    def __init__(self):
        """
        Creates a new sppasParam instance with default values.

        """
        # Internal variables
        self.continuer = False

        # User
        self.logfilename = ""
        self.output_format = DEFAULT_OUTPUT_EXTENSION

        # SPPAS parameters
        self.sppasinput  = []

        # Annotation steps
        self.annotations = []
        with open( os.path.join(SPPAS_CONFIG_DIR,"sppas.conf") , "r" ) as fp:
            # Read the whole file and load annotation options
            for line in fp:
                line = line.strip()
                if line.startswith("annotation:") is True:
                    line = line.replace( "annotation:", "" )
                    annotationdir  = os.path.join( os.path.dirname( os.path.abspath(__file__)), line.strip() )

                    cfgfile = os.path.basename( annotationdir )+".ini"
                    self.annotations.append( annotationParam( os.path.join(SPPAS_CONFIG_DIR,cfgfile) ))

    # ------------------------------------------------------------------------

    # ################################## #
    # INFORMATIONS ABOUT SPPAS PARAMETERS:
    # ################################## #

    # sppas input (file name or directory) getter and setter
    def set_sppasinput(self,inputlist):
        self.sppasinput  = inputlist
        self.logfilename = self.sppasinput[0]+".log"

    def get_sppasinput(self):
        return self.sppasinput

    def add_sppasinput(self,inputfilename):
        self.sppasinput.append(inputfilename)
        self.logfilename = self.sppasinput[0]+".log"

    def clear_sppasinput(self):
        del self.sppasinput
        self.sppasinput = []

    # sppas log file name
    def set_logfilename(self,logfilename):
        self.logfilename = logfilename

    def get_logfilename(self):
        return self.logfilename

    # sppas selected language
    def set_lang(self, language, step=None):
        if step is not None:
            self.annotations[step].set_lang(language)
        else:
            for i in range(len(self.annotations)):
                self.annotations[i].set_lang(language)

    def get_lang(self, step=2):
        return self.annotations[step].get_lang()

    def get_langresource(self,step):
        return self.annotations[step].get_langresource()


    # ######################################## #
    # INFORMATION ABOUT SPPAS ANNOTATION STEPS #
    # ######################################## #

    def activate_annotation(self, stepname):
        for a in self.annotations:
            if a.get_key() == stepname:
                a.set_activate(True)

    def activate_step(self, step):
        self.annotations[step].set_activate(True)

    def disable_step(self, step):
        self.annotations[step].set_activate(False)

    def get_step_status(self, step):
        return self.annotations[step].get_activate()

    def get_step_name(self, step):
        return self.annotations[step].get_name()

    def get_step_descr(self, step):
        return self.annotations[step].get_descr()

    def get_step_key(self, step):
        return self.annotations[step].get_key()

    def get_step_numbers(self):
        return len(self.annotations)

    def get_steplist(self):
        steps = []
        for i in range(len(self.annotations)):
            steps.append(self.annotations[i].get_name())
        return steps

    def get_langlist(self, step=2):
        return self.annotations[step].get_langlist()

    def get_step(self, step):
        return self.annotations[step]

    def get_options(self, step):
        return self.annotations[step].get_options()

    def get_output_format(self):
        return self.output_format

    def set_output_format(self, output_format):
        self.output_format = output_format


    # ########################### #
    # Continue: everything is ok?
    # ########################### #

    def set_continue(self,status):
        self.continuer = status

    def get_continue(self):
        """
        Ask to continue SPPAS or not!
        @return Boolean
        """
        return self.continuer

    # ------------------------------------------------------------------------
