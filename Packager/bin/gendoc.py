#!/usr/bin/env python
# -*- coding: UTF-8 -*-
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

    gendoc.py
    ~~~~~~~~~~

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Documentation generator.


"""
import os
import sys
import glob
from subprocess import Popen, PIPE, STDOUT
from argparse import ArgumentParser

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas

# ---------------------------------------------------------------------------

MARKDOWN_EXT = ".md"
INDEX_EXT = ".idx"

# ---------------------------------------------------------------------------


class sppasDocFiles(object):
    """
    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      brigitte.bigi@gmail.com
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2017  Brigitte Bigi
    :summary:      Documentation explorer.

    Fix all files required to generate the documentation, and explore the
    documentation directory and folders.

    The file markdown.idx contains the list of folders of the documentation.
    It can be a 1 column file, or a two-columns file with ';' to separate
    the two columns.
    Each folder must also contain an index file with the list of markdown
    files.

    """
    # Documentation file explore
    BASE_INDEX = "markdown.idx"
    MARKDOWN_HEADER = "header.md"
    MARKDOWN_FOOTER = "footer.md"

    # Documentation generation
    LATEX_TEMPLATE = "sppasdoctemplate.tex"
    LATEX_FRONTPAGE = "frontpage.pdf"
    HTML_HEADER = "header.html"
    HTML_FOOTER = "footer.html"
    HTML_JS_HEAD = "head_js.html"

    # -----------------------------------------------------------------------

    def __init__(self, doc_dir, doc_temp):
        """ Create a sppasDocFiles instance.

        :param doc_dir: (str) Name of the directory of the markdown and index files
        :param doc_temp: (str) Name of the directory of the external template files.

        """
        self._doc_dir = doc_dir
        self._doc_temp = doc_temp

    # -----------------------------------------------------------------------

    @staticmethod
    def test_file(filename):
        """ Test if a file exists.

        :param filename: (str) Name of the file to test.
        :raises: IOError

        """
        if os.path.exists(filename) is False:
            raise IOError("The file {:s} is missing of the documentation.".format(filename))

    # -----------------------------------------------------------------------
    # Getters
    # -----------------------------------------------------------------------

    def get_file(self, filename):
        """ Return a file of the documentation. """

        new_filename = os.path.join(self._doc_temp, filename)
        sppasDocFiles.test_file(new_filename)
        return new_filename

    # -----------------------------------------------------------------------

    def get_base_index(self):
        """ Return the file indicating the list of documentation folders. """

        filename = os.path.join(self._doc_dir, sppasDocFiles.BASE_INDEX)
        sppasDocFiles.test_file(filename)
        return filename

    # -----------------------------------------------------------------------

    def get_markdown_header(self):
        """ Return the header markdown file. """

        return self.get_file(sppasDocFiles.MARKDOWN_HEADER)

    # -----------------------------------------------------------------------

    def get_markdown_footer(self):
        """ Return the footer markdown file. """

        return self.get_file(sppasDocFiles.MARKDOWN_FOOTER)

    # -----------------------------------------------------------------------

    def get_latex_template(self):
        """ Return the LaTeX template file. """

        return self.get_file(sppasDocFiles.LATEX_TEMPLATE)

    # -----------------------------------------------------------------------

    def get_latex_front_page(self):
        """ Return the LaTeX front page file. """

        return self.get_file(sppasDocFiles.LATEX_FRONTPAGE)

    # -----------------------------------------------------------------------

    def get_html_header(self):
        """ Return the header html file. """

        return self.get_file(sppasDocFiles.HTML_HEADER)

    # -----------------------------------------------------------------------

    def get_html_footer(self):
        """ Return the footer html file. """

        return self.get_file(sppasDocFiles.HTML_FOOTER)

    # -----------------------------------------------------------------------

    def get_js_head_scripts(self):
        """ Return the scripts for the <head> of an html file. """

        return self.get_file(sppasDocFiles.HTML_FOOTER)

    # -----------------------------------------------------------------------
    # Explore the documentation folders and files
    # -----------------------------------------------------------------------

    @staticmethod
    def get_index(dirname):
        """ Return the filename of the index of a directory. """

        try:
            index_filename = os.path.join(dirname, sppasDocFiles.BASE_INDEX)
            sppasDocFiles.test_file(index_filename)
        except IOError:
            index_files = glob.glob(os.path.join(dirname, "*" + INDEX_EXT))
            if len(index_files) > 0:
                index_filename = index_files[0]
            else:
                raise IOError("No index found in {:s}.".format(dirname))

        return index_filename

    # -----------------------------------------------------------------------

    def get_idx_markdown_files(self, folder):
        """ Return a list of markdown files.
        Search for an index file either in doc_dir/folder or in doc_dir.

        :param folder: (str) Folder to search for markdown files. If folder is
        None, search is performed directly in doc_dir.
        :returns: list of filenames

        """
        # Search the index file

        if folder is None:
            index_filename = self.get_index(self._doc_dir)
        else:
            index_filename = self.get_index(os.path.join(self._doc_dir, folder))

        # Get all files mentioned in the idx

        files = list()
        fp = open(index_filename, "r")
        for line in fp.readlines():
            line = line.strip()
            if ";" in line:
                tabline = line.split(';')
                filename = tabline[0]
            else:
                filename = line.strip()
            # Add its path to each file name
            if folder is not None:
                new_file = os.path.join(self._doc_dir, folder, filename)
            else:
                new_file = os.path.join(self._doc_dir, filename)

            if os.path.exists(new_file) is False:
                raise IOError("File {:s} is missing.".format(new_file))
            files.append(new_file)

        return files

    # -----------------------------------------------------------------------

    def get_doc_folders(self):
        """ Return the list of folders of the documentation.

        This list is extracted from the BASE_INDEX file which should be included
        into the documentation directory.
        Instead, all 1st level folders will be explored.

        :returns: list of dirnames

        """
        folders = list()
        try:
            index_filename = self.get_base_index()
            fp = open(index_filename, "r")
            # Get all folders mentioned in the index file
            for line in fp.readlines():
                dirname = line.strip()
                # Add its path to each folder name
                new_folder = os.path.join(self._doc_dir, dirname)
                if os.path.exists(new_folder) is False:
                    raise IOError("Folder {:s} is indexed but is missing.".format(new_folder))
                folders.append(dirname)

        except IOError:
            # No base index. Explore folders
            for folder in os.listdir(self._doc_dir):
                try:
                    self.get_idx_markdown_files(folder)
                    folders.append(folder)
                except IOError:
                    pass
            folders = sorted(folders)

        return folders

    # -----------------------------------------------------------------------

    def get_all_md(self, header=True, footer=False):
        """ Return the list of markdown files for a documentation directory.
        Explore 1st level folders (if any) OR the doc dir.

        :param header: (bool) Add an header markdown file into the list
        :param footer: (bool) Add a footer markdown file into the list

        :returns: list of filenames

        """
        files = list()

        # add the header file into the list
        if header is True:
            files.append(self.get_markdown_header())

        # get the list of all indexed folders in the documentation directory
        folders = self.get_doc_folders()

        # get all indexed files of each folder
        if len(folders) > 0:
            for folder in folders:
                new_files = self.get_idx_markdown_files(folder)
                files.extend(new_files)
        else:
            files.extend(self.get_idx_markdown_files(folder=None))

        # add the footer file into the list
        if footer is True:
            files.append(self.get_markdown_footer())

        return files


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def exec_external_command(command, result_filename):
    """ Execute a command and check the output file.

    :param command: (str) The external command to be executed, with its parameters.
    :param result_filename: (str) Name of the expected output file of the command
    :raises: Exception

    """
    p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    p.wait()
    line = p.communicate()

    # Check output file
    if os.path.exists(result_filename) is False:
        raise Exception("Error: {}.".format(line[0]))

# ---------------------------------------------------------------------------
# Generate a documentation file from some markdown sources
# ---------------------------------------------------------------------------


def gen_pdf_file(doc, files, result_filename):
    """ Execute pandoc to generate a documentation in PDF.

    :param doc: (sppasDocFiles) Documentation, used to get filenames.
    :param files: (list) List of filenames (markdown files)
    :param result_filename: (str) Name of the newly created PDF documentation file

    """
    if len(files) == 0:
        raise IOError("No markdown files to generate the documentation!")

    # The expected files to generate the PDF:
    latex_template = doc.get_latex_template()
    front_page = doc.get_latex_front_page()

    # Remove the existing file
    if os.path.exists(result_filename):
        os.remove(result_filename)

    # the command
    command = "pandoc"

    # the parameters
    command += " -N --template=" + latex_template
    command += ' --variable toc-depth=2'
    command += ' -V geometry:a4paper'
    command += ' -V geometry:"top=3cm, bottom=3cm, left=3cm, right=2.5cm"'
    command += ' --variable documentclass="report"'
    command += ' --variable classoption="twoside, openright"'
    command += ' --variable mainfont="FreeSerif"'
    command += ' --variable sansfont="FreeSans"'
    command += ' --variable monofont="FreeMono"'
    command += ' --variable fontsize=11pt'
    command += ' --variable version="' + sppas.__version__ + '"'
    command += ' --variable frontpage="' + front_page + '"'

    # the files and LaTeX options
    command += " "
    command += " ".join(files)
    command += ' --latex-engine=xelatex'
    command += ' --toc'
    command += ' -o ' + result_filename

    print("Command to be executed: {:s}".format(command))

    # Execute the command
    # -------------------
    exec_external_command(command, result_filename)

# ---------------------------------------------------------------------------


def gen_html_file(doc, css_filename, files, result_filename):
    """ Execute pandoc to generate a documentation in HTML 5.

    :param doc: (sppasDocFiles) Documentation, used to get filenames.
    :param css_filename: (str) Name of a CSS file
    :param files: (list) List of filenames (markdown files)
    :param result_filename: (str) Name of the newly created HTML documentation file

    """
    if len(files) == 0:
        raise IOError("No markdown files to generate the documentation!")

    sppasDocFiles.test_file(css_filename)

    head_html_file = doc.get_js_head_scripts()
    body_header_html_file = doc.get_html_header()
    body_footer_html_file = doc.get_html_footer()

    # Remove the existing file
    if os.path.exists(result_filename):
        os.remove(result_filename)

    # the command
    command = "pandoc"

    # the parameters
    command += " -s"
    command += " --toc"
    command += " --mathjax"
    command += " --html5"
    command += " --css " + css_filename
    command += " -H " + head_html_file
    command += " -B " + body_header_html_file
    command += " -A " + body_footer_html_file

    # the files and HTML options
    command += " "
    command += " ".join(files)
    command += " --highlight-style haddock"
    command += ' -o ' + result_filename

    # print("Command to be executed: {:s}".format(command))

    # Execute the command
    # -------------------
    exec_external_command(command, result_filename)

# ---------------------------------------------------------------------------


def gen_html_slides_file(tuto, css_filename, files, result_filename):
    """ Execute pandoc to generate slides in HTML 5.

    :param tuto: (sppasDocFiles) Documentation, used to get filenames.
    :param css_filename: (str) Name of a CSS file.
    :param files: (list) Names of the markdown files.
    :param result_filename: (str) Name of the newly created HTML documentation file

    """
    if len(files) == 0:
        raise IOError("No markdown files to generate the tutorial!")

    sppasDocFiles.test_file(css_filename)
    head_html_file = tuto.get_js_head_scripts()

    # Remove the existing file
    if os.path.exists(result_filename):
        os.remove(result_filename)

    # the command
    command = "pandoc"

    # the parameters
    command += " -s"
    command += " --mathjax"
    command += " -t dzslides"
    command += " --html5"
    command += " --css " + css_filename
    command += "--slide-level=2"
    command += " -H " + head_html_file

    # the files and HTML options
    command += " "
    command += " ".join(files)
    command += ' -o ' + result_filename

    print("Command to be executed: {:s}".format(command))

    # Execute the command
    # -------------------
    exec_external_command(command, result_filename)


# ---------------------------------------------------------------------------
# Generate the SPPAS documentation file from all markdown sources
# ---------------------------------------------------------------------------


def generate_pdf(doc_dir, doc_temp):
    """ Generate the SPPAS documentation in PDF format. """

    doc = sppasDocFiles(doc_dir, doc_temp)

    # name of the resulting file
    result_filename = os.path.join(SPPAS, "documentation", "Documentation.pdf")

    # A unique PDF documentation file is generated from all markdown files
    md_files = doc.get_all_md(header=False, footer=False)
    gen_pdf_file(doc, md_files, result_filename)

# ---------------------------------------------------------------------------


def generate_web(doc_dir, doc_temp):
    """ Generate the SPPAS documentation in a directory with HTML files. """

    # doc template files
    css_file = os.path.join(".", "etc", "styles", "sppas.css")

    # web directory to store resulting HTML files
    result_dirname = os.path.join(SPPAS, "Packager", "web")

    # get the list of all indexed folders in the documentation directory
    base_doc = sppasDocFiles(doc_dir, doc_temp)
    folders = base_doc.get_doc_folders()

    for folder in folders:
        print(folder)
        folder_dirname = os.path.join(doc_dir, folder)
        folder_doc = sppasDocFiles(folder_dirname, doc_temp)
        files = folder_doc.get_all_md(header=True, footer=False)
        print(files)
        result_filename = os.path.join(result_dirname, "documentation_" + folder + ".html")
        gen_html_file(base_doc, css_file, files, result_filename)

# ---------------------------------------------------------------------------


def generate_tuto(tuto_dir, doc_temp):

    # tuto template files
    css_file = os.path.join(".", "etc", "styles", "tuto.css")

    # web directory to store resulting TUTORIAL files
    result_dirname = os.path.join(SPPAS, "Packager", "web")

    base_doc = sppasDocFiles(tuto_dir, doc_temp)
    folders = base_doc.get_doc_folders()

    for folder in folders:
        print(folder)
        folder_dirname = os.path.join(tuto_dir, folder)
        folder_tuto = sppasDocFiles(folder_dirname, doc_temp)
        files = folder_tuto.get_all_md(header=False, footer=False)
        for md_file in files:
            result_filename = os.path.join(result_dirname, "tutorial_" + os.path.basename(md_file))
            result_filename, ext = os.path.splitext(result_filename)
            result_filename += ".html"
            # gen_html_slides_file(folder_tuto, css_file, [file], result_filename)
            print(result_filename)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    # -----------------------------------------------------------------------
    # Verify and extract args:
    # -----------------------------------------------------------------------

    parser = ArgumentParser(usage="%s [options]" % os.path.basename(PROGRAM),
                            description="... a script to generate the documentation of SPPAS.")

    parser.add_argument("--web",
                        action='store_true',
                        help="Enable the generation of web pages")

    parser.add_argument("--doc",
                        action='store_true',
                        help="Enable the generation of the PDF")

    parser.add_argument("--tuto",
                        action='store_true',
                        help="Enable the generation of the tutorials")

    if len(sys.argv) <= 1:
        sys.argv.append('-h')

    args = parser.parse_args()

    # -----------------------------------------------------------------------

    # fix directory for external files is ok.
    doc_temp = os.path.join(SPPAS, "Packager", "doc")
    if os.path.exists(doc_temp) is False:
        raise IOError("Directory {:s} of the documentation is missing. Program halted.".format(doc_temp))

    if args.doc or args.web:
        # test if documentation directory for markdown files is ok.
        doc_dir = os.path.join(SPPAS, "sppas", "doc")
        if os.path.exists(doc_dir) is False:
            raise IOError("Directory {:s} of the documentation is missing. Program halted.".format(doc_dir))

        if args.doc:
            generate_pdf(doc_dir, doc_temp)
        else:
            generate_web(doc_dir, doc_temp)

    if args.tuto:
        # test if tutorial directory for markdown files is ok.
        tuto_dir = os.path.join(SPPAS, "Packager", "tuto")
        if os.path.exists(tuto_dir) is False:
            raise IOError("Directory {:s} of the tutorials is missing. Program halted.".format(tuto_dir))

        # generate_tuto(tuto_dir, doc_temp)
        print("NOT IMPLEMENTED")