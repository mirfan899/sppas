"""
    ..
        ---------------------------------------------------------------------
         ___   __    __    __    ___
        /     |  \  |  \  |  \  /              the automatic
        \__   |__/  |__/  |___| \__             annotation and
           \  |     |     |   |    \             analysis
        ___/  |     |     |   | ___/              of speech

        http://www.sppas.org/

        Use of this software is governed by the GNU Public License, version 3.

        SPPAS is free software: you can redistribute it and/or modify
        it under the terms of the GNU General Public License as published by
        the Free Software Foundation, either version 3 of the License, or
        (at your option) any later version.

        SPPAS is distributed in the hope that it will be useful,
        but WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        GNU General Public License for more details.

        You should have received a copy of the GNU General Public License
        along with SPPAS. If not, see <http://www.gnu.org/licenses/>.

        This banner notice must not be removed.

        ---------------------------------------------------------------------

    src.annotations.param.py
    ~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import os

from sppas.src.config import paths
from sppas.src.config import annots
from sppas.src.anndata.aio import extensions_out

from .cfgparser import sppasAnnotationConfigParser

# ----------------------------------------------------------------------------


class annotationParam(object):
    """Annotation parameters data manager.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Class to store data of an automatic annotation like its name, description, 
    supported languages, etc.
    
    """

    def __init__(self, filename=None):
        """Create a new annotationParam instance.

        :param filename: (str) Annotation configuration file
        
        """
        # An identifier to represent this annotation step
        self.__key = None
        # The name of the annotation
        self.__name = ""
        # The description of the annotation
        self.__descr = ""
        # The annotation status
        self.__enabled = False
        self.__invalid = False
        # The language resource
        self.__langres = list()
        # The list of options
        self.__options = list()
        # Status
        self.__invalid = False

        # OK... now fix all member values from the given file
        if filename:
            self.parse(filename)

    # ------------------------------------------------------------------------

    def parse(self, filename):
        """Parse a configuration file to fill members.
        
        :param filename: (str) Annotation configuration file (.ini)

        """
        p = sppasAnnotationConfigParser()
        p.parse(filename)

        self.__options = p.get_options()
        self.__langres = p.get_resources()
        conf = p.get_config()
        self.__key = conf['id']
        self.__name = conf.get('name', "")
        self.__descr = conf.get('descr', "")

    # -----------------------------------------------------------------------
    # Setters
    # -----------------------------------------------------------------------

    def set_activate(self, activate):
        """Enable the annotation but only if this annotation is valid.
        
        :param activate: (bool) Enable or disable the annotation
        :returns: (bool) enabled or disabled
        
        """
        self.__enabled = activate
        if activate is True and self.__invalid is True:
            self.__enabled = False
        return self.__enabled

    # -----------------------------------------------------------------------

    def set_lang(self, lang):
        """Set the language of the annotation only if this latter is accepted.

        :param lang: (str) Language to fix for the annotation
        :returns: (bool) Language is set or not

        """
        if len(self.__langres) > 0:
            try:
                self.__langres[0].set_lang(lang)
                return True
            except:
                self.__invalid = True
                self.__enabled = False
        return False

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_key(self):
        """Return the identifier of the annotation (str)."""
        return self.__key

    # -----------------------------------------------------------------------

    def get_name(self):
        """Return the name of the annotation (str)."""
        return self.__name

    # -----------------------------------------------------------------------

    def get_descr(self):
        """Return the description of the annotation (str)."""
        return self.__descr

    # -----------------------------------------------------------------------

    def get_activate(self):
        """Return the activation status of the annotation (bool)."""
        return self.__enabled

    # -----------------------------------------------------------------------

    def get_lang(self):
        """Return the language or an empty string."""
        if len(self.__langres) > 0:
            return self.__langres[0].get_lang()
        return ""

    # -----------------------------------------------------------------------

    def get_langlist(self):
        """Return the list of available languages (list of str)."""
        if len(self.__langres) > 0:
            return self.__langres[0].get_langlist()
        return []

    # -----------------------------------------------------------------------

    def get_langresource(self):
        """Return the list of language resources (list of sppasLang)."""
        if len(self.__langres) > 0:
            return self.__langres[0].get_langresource()
        return []

    # -----------------------------------------------------------------------

    def get_options(self):
        """Return the list of options of the annotation."""
        return self.__options

    # -----------------------------------------------------------------------

    def get_option(self, step):
        """Return the step-th option."""
        return self.__options[step]

    # -----------------------------------------------------------------------

    def get_option_by_key(self, key):
        """Return an option from its key."""
        for opt in self.__options:
            if key == opt.get_key():
                return opt

    # -----------------------------------------------------------------------

    def set_option_value(self, key, value):
        """Change value of an option."""
        # the option is already in the list, change its value
        for opt in self.__options:
            if key == opt.get_key():
                opt.set_value(value)
                return
        raise KeyError("Unknown option {:s} in annotation parameters."
                       "".format(key))

# ---------------------------------------------------------------------------


class sppasParam(object):
    """Annotations parameters manager.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    """

    def __init__(self, annotation_keys=None):
        """Create a new sppasParam instance with default values.

        :param annotation_keys: (list) List of annotations to load. None=ALL.

        """
        # Internal variables
        self.continuer = False

        # User
        self.logfilename = ""
        self.output_format = annots.extension

        # SPPAS parameters
        self.sppasinput = []

        # Annotation steps
        self.annotations = []
        self.parse_config_file(annotation_keys)

    # ------------------------------------------------------------------------

    def parse_config_file(self, annotation_keys=None):
        """Parse the sppas.conf file to get the list of annotations.

        :param annotation_keys: (list) List of annotations to load. None=ALL.

        """
        with open(os.path.join(paths.etc, "sppas.conf"), "r") as fp:
            lines = fp.readlines()

        # Read the whole file and load annotation options
        for line in lines:
            line = line.strip()
            if line.lower().startswith("annotation:") is True:
                data = line.split(":")
                if annotation_keys is None or\
                   (annotation_keys and data[1].strip() in annotation_keys):
                    cfg_file = data[2].strip()
                    a = annotationParam(os.path.join(paths.etc, cfg_file))
                    self.annotations.append(a)

    # -----------------------------------------------------------------------
    # input file name or directory, i.e. entry to annotate
    # -----------------------------------------------------------------------

    def set_sppasinput(self, inputlist):
        self.sppasinput = inputlist
        self.logfilename = self.sppasinput[0] + ".log"

    def get_sppasinput(self):
        return self.sppasinput

    def add_sppasinput(self, inputfilename):
        self.sppasinput.append(inputfilename)
        self.logfilename = self.sppasinput[0] + ".log"

    def clear_sppasinput(self):
        del self.sppasinput
        self.sppasinput = []

    # -----------------------------------------------------------------------
    # log file name for the procedure outcome report
    # -----------------------------------------------------------------------

    def set_logfilename(self, logfilename):
        self.logfilename = logfilename

    def get_logfilename(self):
        return self.logfilename

    # -----------------------------------------------------------------------
    # selected language
    # -----------------------------------------------------------------------

    def set_lang(self, language, step=None):
        if step is not None:
            self.annotations[step].set_lang(language)
        else:
            for i in range(len(self.annotations)):
                self.annotations[i].set_lang(language)

    def get_lang(self, step=2):
        return self.annotations[step].get_lang()

    def get_langresource(self, step):
        return self.annotations[step].get_langresource()

    # ------------------------------------------------------------------------
    # annotations
    # ------------------------------------------------------------------------

    def activate_annotation(self, stepname):
        for i, a in enumerate(self.annotations):
            if a.get_key() == stepname:
                a.set_activate(True)
                return i
        return -1

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

    def set_option_value(self, step, key, value):
        self.annotations[step].set_option_value(key, value)

    # -----------------------------------------------------------------------
    # Annotation file output format
    # -----------------------------------------------------------------------

    def get_output_format(self):
        return self.output_format

    def set_output_format(self, output_format):
        """Fix the output format of the annotations.

        :param output_format: (str) File extension (with or without a dot)

        """
        # Force to contain the dot
        if not output_format.startswith("."):
            output_format = "." + output_format

        # Check if this extension is know. If not, set to the default.
        # Instead we could raise an exception... is it appropriate to do that?
        extensions = [e.lower() for e in extensions_out]
        if not output_format.lower() in extensions:
            logging.warning("Unknown extension: {:s}. "
                            "Extension is set to default."
                            "".format(output_format))
            output_format = annots.extension

        self.output_format = output_format

    # -----------------------------------------------------------------------
    # Continue: everything is ok?
    # -----------------------------------------------------------------------

    def set_continue(self, status):
        self.continuer = status

    # ------------------------------------------------------------------------

    def get_continue(self):
        """Ask to continue SPPAS or not!

        :returns: (bool)

        """
        return self.continuer
