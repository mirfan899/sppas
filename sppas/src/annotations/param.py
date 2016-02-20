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
from sp_glob import ANNOTATIONS_LIST_FILE
from sp_glob import DEFAULT_OUTPUT_EXTENSION

import utils.fileutils

# ----------------------------------------------------------------------------


class option():
    """
    Class to deal with one option of one annotation step (Private class).

    For example:
    optionid:    unk
    optiontype:  boolean
    optionvalue: True
    optiontext:  This is the text in the GUI
    """

    def __init__(self, optionkey):
        """
        Creates a new option instance.
        """
        self.key   = optionkey
        self.name  = "None"
        self.value = None
        self.text  = ""

    # ############## #
    # Getters        #
    # ############## #

    def get_name(self):
        return self.name

    def get_type(self):
        return type(self.get_value())

    def get_value(self):
        return self.value

    def get_text(self):
        return self.text

    def get_key(self):
        return self.key


    # ############## #
    # Setters        #
    # ############## #

    def set_name(self, name):
        self.name = name


    def parse_value(self, type, value):
        """
        Parse a new entry.
        Parameters:
            - type (String)
            - value (String)
        The possible values for type are: boolean, int, float, string
        Exceptions:
            -ValueError (if value is not of the appropriate type)
            -TypeError (if type is unknown)
        """
        if type.lower() == 'boolean' or type.lower() == 'bool':
            self.value = (value.lower() == "true")
        elif type.lower() == 'int' or type.lower() == 'integer' or type.lower() == 'long' or type.lower() == 'short':
            self.value = int(value)
        elif type.lower() == 'float' or type.lower() == 'double':
            self.value = float(value)
        elif type.lower() == 'string':
            self.value = value.decode('utf-8')
        else:
            raise TypeError


    def set_value(self, value):
        """ Set a new value.
            Exception: TypeError if the new value is not of the same type as the old value
        """
        if type(value) == type(self.value):
            self.value = value
        else:
            raise TypeError


    def set_text(self, text):
        self.text = text


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
        # The HTML file with the annotation description
        self.helpfile  = None
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
            type = None
            # Read the whole file
            for line in fp:
                if( line.find("identifier:")>-1 ):
                    line = line.replace( "identifier:", "" )
                    self.key = line.strip()
                elif( line.startswith("name:")==True ):
                    line = line.replace( "name:", "" )
                    self.name = line.strip()
                elif( line.find("resources_path:")>-1 ):
                    line = line.replace( "resources_path:", "" )
                    self.resource["path"] = line.strip()
                elif( line.find("resources_type:")>-1 ):
                    line = line.replace( "resources_type:", "" )
                    self.resource["type"] = line.strip()
                elif( line.find("resources_name:")>-1 ):
                    line = line.replace( "resources_name:", "" )
                    self.resource["name"] = line.strip()
                elif( line.find("resources_ext:")>-1 ):
                    line = line.replace( "resources_ext:", "" )
                    self.resource["ext"] = line.strip()
                elif( line.find("param:")>-1 ):
                    line = line.replace( "param:", "" )
                    self.helpfile = line.strip()
                elif( line.find("optionid:")>-1 ):
                    line = line.replace( "optionid:", "" )
                    self.options.append( option(line.strip()) )
                elif( line.find("optiontype:")>-1 ):
                    line = line.replace( "optiontype:", "" )
                    type = line.strip()
                elif( line.find("optionvalue:")>-1 ):
                    line = line.replace( "optionvalue:", "" )
                    self.options[-1].parse_value( type, line.strip())
                elif( line.find("optiontext:")>-1 ):
                    line = line.replace( "optiontext:", "" )
                    self.options[-1].set_text( line.strip() )

        # Fix the language list
        if len(self.resource) > 0 and self.resource["path"]!="None":
            directory = os.path.join(RESOURCES_PATH, self.resource["path"])
            filename = ""
            ext = ""
            langlistext = ""
            if self.resource["type"]=="file":
                if self.resource["name"] != "None":
                    filename = self.resource["name"]
                if self.resource["ext"]!="None":
                    ext = self.resource["ext"]
                    langlistext = utils.fileutils.get_files( directory, ext )

                # Remove file name, extension and directory
                self.langlist = [x[len(directory)+len(filename)+1:-len(ext)] for x in langlistext]
            elif self.resource["type"]=="directory":
                if self.resource["name"] == "None":
                    self.langresource = directory
                for dirname in os.listdir(directory):
                    if dirname.startswith(self.resource["name"])==True:
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
            if self.resource["type"]=="file":
                filestart = ""
                if self.resource["name"]!="None":
                    filestart = self.resource["name"]
                self.langresource = os.path.join(directory, filestart)
                self.langresource += l
                if self.resource["ext"]!="None":
                    self.langresource += self.resource["ext"]
            elif self.resource["type"]=="directory":
                filestart = self.resource["name"]
                if filestart != "None":
                    self.langresource = os.path.join(directory, filestart+l)
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
        with open( ANNOTATIONS_LIST_FILE, "r" ) as fp:
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

    def get_helpfile(self,stepnumber):
        return self.annotations[stepnumber].get_helpfile()

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
