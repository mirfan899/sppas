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

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import sys
import os.path

from sp_glob import RESOURCES_PATH
from sp_glob import SPPAS_CONFIG
from sp_glob import DEFAULT_OUTPUT_EXTENSION

import utils.fileutils

from structs.baseoption import BaseOption

# ----------------------------------------------------------------------------

class option( BaseOption ):
    """
    Class to deal with one option of one annotation step (Private class).

    """
    def __init__(self, optionkey):
        BaseOption.__init__(self, "unknown")
        self.key = optionkey

    def get_key(self):
        return self.key

# ----------------------------------------------------------------------------

class annotationParam():
    """
    One SPPAS annotation step parameters (Private class).
    Used to parse the sppas.conf file.

    """
    def __init__(self, anndir):
        """
        Creates a new annotationParam instance.
        """
        # The annotation directory:
        self.annotationdir = anndir
        # An identifier to represent this annotation step (not used)
        self.key  = None
        # The name of the annotation
        self.name = "None"
        # The list of languages this annotation can provide
        self.langlist  = []
        # The selected language
        self.lang      = None
        # The annotation status
        self.activated = False
        # The list of options available for the annotation
        self.options   = []
        # All available language resources (type, path, filename, extension)
        self.resource  = {}
        # The language resource after the language is fixed
        self.langresource = ""
        # Initialize variables from the configuration file
        self.__set_annotations( os.path.join(anndir, "sppas.conf") )


    def __set_annotations(self,annfile):
        with open(annfile, "r") as fp:
            lines = fp.readlines()

        for line in lines:
            line = line.strip()

            if line.startswith("identifier:"):
                line = line.replace( "identifier:", "" )
                self.key = line.strip()

            elif line.startswith("name:"):
                line = line.replace( "name:", "" )
                self.name = line.strip()

            elif line.startswith("resources_path:"):
                line = line.replace( "resources_path:", "" )
                self.resource["path"] = line.strip()

            elif line.startswith("resources_type:"):
                line = line.replace( "resources_type:", "" )
                self.resource["type"] = line.strip()

            elif line.startswith("resources_name:"):
                line = line.replace( "resources_name:", "" )
                self.resource["name"] = line.strip()

            elif line.startswith("resources_ext:"):
                line = line.replace( "resources_ext:", "" )
                self.resource["ext"] = line.strip()

            elif line.startswith("optionid:"):
                line = line.replace( "optionid:", "" )
                self.options.append( option(line.strip()) )

            elif line.startswith("optiontype:"):
                line = line.replace( "optiontype:", "" )
                self.options[-1].set_type(line.strip())

            elif line.startswith("optionvalue:"):
                line = line.replace( "optionvalue:", "" )
                self.options[-1].set_value(line.strip())

            elif line.startswith("optiontext:"):
                line = line.replace( "optiontext:", "" )
                self.options[-1].set_text(line.strip())

            elif line.startswith("optiondescr:"):
                line = line.replace( "optiondescr:", "" )
                self.options[-1].set_description(line.strip())

        # Fix the language list
        if len(self.resource) > 0:
            directory = os.path.join(RESOURCES_PATH, self.resource["path"])
            filename = ""
            ext = ""
            langlistext = ""
            if self.resource["type"] == "file":
                if "name" in self.resource.keys():
                    filename = self.resource["name"]
                if "ext" in self.resource.keys():
                    ext = self.resource["ext"]
                    langlistext = utils.fileutils.get_files( directory, ext )

                # Remove file name, extension and directory
                self.langlist = [x[len(directory)+len(filename)+1:-len(ext)] for x in langlistext]

            elif self.resource["type"] == "directory":
                if "name" in self.resource.keys():
                    self.langresource = directory
                for dirname in os.listdir(directory):
                    if dirname.startswith(self.resource["name"]) is True:
                        self.langlist.append(dirname.replace(self.resource["name"], ""))


    # Getters and setters

    def get_langlist(self):
        return self.langlist

    def get_name(self):
        return self.name

    def set_activate(self, activate):
        self.activated = activate

    def get_activate(self):
        return self.activated

    def set_lang(self, l):
        self.lang = l
        # Is there a resource available for this annotation?
        if l in self.langlist:
            directory = os.path.join(RESOURCES_PATH, self.resource["path"])
            if self.resource["type"] == "file":
                filestart = ""
                if "name" in self.resource.keys():
                    filestart = self.resource["name"]
                self.langresource = os.path.join(directory, filestart)
                self.langresource += l
                if "ext" in self.resource.keys():
                    self.langresource += self.resource["ext"]

            elif self.resource["type"] == "directory":
                if "name" in self.resource.keys():
                    self.langresource = os.path.join(directory, self.resource["name"]+l)
                else:
                    self.langresource = directory

    def get_key(self):
        return self.key

    def get_lang(self):
        return self.lang

    def get_langresource(self):
        return self.langresource

    def get_langresourcetype(self):
        return self.resource["type"]

    def get_options(self):
        return self.options

    def get_option(self, step):
        return self.options[step]

    def get_option_by_key(self, key):
        for opt in self.options:
            if key == opt.get_key():
                return opt


# ----------------------------------------------------------------------------


class sppasParam():
    """
    Getters and Setters for all sppas parameters.
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

        # Annotation steps
        self.annotations = []
        with open( SPPAS_CONFIG, "r" ) as fp:
            # Read the whole file and load annotation options
            for line in fp:
                line = line.strip()
                if line.startswith("annotation:") is True:
                    line = line.replace( "annotation:", "" )
                    annotationdir  = os.path.join( os.path.dirname( os.path.abspath(__file__)), line.strip() )
                    self.annotations.append( annotationParam( annotationdir ) )

        # SPPAS parameters
        self.sppasinput  = []

    # End __init__
    # --------------------------


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
    # then ... dictionary/model/descr are fixed.
    def set_lang(self,language,stepnumber=None):
        if stepnumber is not None:
            self.annotations[stepnumber].set_lang(language)
        else:
            for i in range(len(self.annotations)):
                self.annotations[i].set_lang(language)

    def get_lang(self,stepnumber=2):
        return self.annotations[stepnumber].get_lang()

    def get_langresource(self,stepnumber):
        return self.annotations[stepnumber].get_langresource()

    def get_langresourcetype(self,stepnumber):
        return self.annotations[stepnumber].get_langresourcetype()


    # ######################################## #
    # INFORMATION ABOUT SPPAS ANNOTATION STEPS #
    # ######################################## #

    def activate_annotation(self,stepname):
        for a in self.annotations:
            if a.get_key() == stepname:
                a.set_activate(True)

    def activate_step(self,stepnumber):
        self.annotations[stepnumber].set_activate(True)

    def disable_step(self,stepnumber):
        self.annotations[stepnumber].set_activate(False)

    def get_step_status(self,stepnumber):
        return self.annotations[stepnumber].get_activate()

    def get_step_name(self,stepnumber):
        return self.annotations[stepnumber].get_name()

    def get_step_key(self,stepnumber):
        return self.annotations[stepnumber].get_key()

    def get_step_numbers(self):
        return len(self.annotations)

    def get_steplist(self):
        steps = []
        for i in range(len(self.annotations)):
            steps.append(self.annotations[i].get_name())
        return steps

    def get_langlist(self,stepnumber=2):
        """ Get the list of available languages of an annotation.
           Return:      List
           Exceptions:  none
        """
        return self.annotations[stepnumber].get_langlist()

    def get_step(self,stepnumber):
        return self.annotations[stepnumber]

    def get_options(self,stepnumber):
        return self.annotations[stepnumber].get_options()

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

    # ########################### #

# ----------------------------------------------------------------------------

#  Used to debug:
if __name__ == "__main__":
    p = sppasParam()
    p.set_lang('eng')

# ----------------------------------------------------------------------------
