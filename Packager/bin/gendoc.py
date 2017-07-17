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
    :summary:      Documentation generator for SPPAS.

"""
import os
import sys
import glob
from subprocess import Popen, PIPE, STDOUT

PROGRAM = os.path.abspath(__file__)
SPPAS = os.path.dirname(os.path.dirname(os.path.dirname(PROGRAM)))
sys.path.append(SPPAS)

import sppas

# File extensions
MARKDOWN_EXT = ".md"
INDEX_EXT = ".idx"

# ---------------------------------------------------------------------------


def test_file(filename):
    """ Test if a file exists.

    :param filename: (str) Name of the file to test.

    """
    if os.path.exists(filename) is False:
        raise IOError("The file {:s} is missing of the documentation.".format(filename))

# ---------------------------------------------------------------------------


def exec_external_command(command, result_filename):
    """ Execute a command.

    :param command: (str) The external command to be executed, with its parameters.
    :param result_filename: (str) Name of the expected output file of the command

    """
    p = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
    p.wait()
    line = p.communicate()

    # Check output file
    if os.path.isfile(result_filename) is False:
        raise Exception("Error: {:s}.".format(line[0]))


# ---------------------------------------------------------------------------
# Explore the documentation directory and folders
# ---------------------------------------------------------------------------


def get_idx_markdown_files(doc_dir, folder):
    """ Return the list of files for a folder of the documentation.

    :param doc_dir: (str) Root directory of the documentation
    :param folder: (str) Folder to search for markdown files
    :returns: list of filenames

    """
    if folder is None:
        # search for an index file
        index_files = glob.glob(os.path.join(doc_dir, "*" + INDEX_EXT))
        if len(index_files) > 0:
            index_filename = index_files[0]
    else:
        index_filename = os.path.join(doc_dir, folder, folder + INDEX_EXT)
        test_file(index_filename)

    files = list()
    fp = open(index_filename, "r")
    # Get all files mentioned in the idx
    for line in fp.readlines():
        filename = line.strip()
        # Add its path to each file name
        if folder is not None:
            new_file = os.path.join(doc_dir, folder, filename)
        else:
            new_file = os.path.join(doc_dir, filename)

        if os.path.exists(new_file) is False:
            raise IOError("File {:s} is missing.".format(new_file))
        files.append(new_file)

    return files

# ---------------------------------------------------------------------------


def get_doc_folders(doc_dir):
    """ Return the list of folders of the documentation.
    This list is extracted from the file markdown.idx which should be included
    into the documentation directory. Instead, all 1st level folders will be explored.

    :param doc_dir: (str) Root directory of the documentation
    :returns: list of dirnames

    """
    folders = list()
    index_filename = os.path.join(doc_dir, "markdown" + INDEX_EXT)
    if os.path.exists(index_filename) is False:
        # Explore folders
        for folder in os.listdir(doc_dir):
            try:
                get_idx_markdown_files(doc_dir, folder)
                folders.append(folder)
            except IOError:
                pass
            folders = sorted(folders)
    else:
        fp = open(index_filename, "r")
        # Get all folders mentioned in the idx
        for line in fp.readlines():
            dirname = line.strip()
            # Add its path to each folder name
            new_folder = os.path.join(doc_dir, dirname)
            if os.path.exists(new_folder) is False:
                raise IOError("Folder {:s} is missing.".format(new_folder))
            folders.append(dirname)

    return folders

# ---------------------------------------------------------------------------


def get_header(doc_temp):
    """ Return the header file of the doc or None.

    :param doc_temp: (str) Root directory to find the header file
    :returns: filename

    """
    header_filename = os.path.join(doc_temp, "header" + MARKDOWN_EXT)
    if os.path.exists(header_filename):
        return header_filename

    raise IOError("Header file {:s} does not exist.".format(header_filename))

# ---------------------------------------------------------------------------


def get_footer(doc_temp):
    """ Return the footer file of the doc or None.

    :param doc_temp: (str) Root directory to find the header file
    :returns: filename

    """
    footer_filename = os.path.join(doc_temp, "footer" + MARKDOWN_EXT)
    if os.path.exists(footer_filename):
        return footer_filename

    raise IOError("Footer file {:s} does not exist.".format(footer_filename))

# ---------------------------------------------------------------------------


def get_all_md(doc_dir, doc_temp, header=True, footer=False):
    """ Return the list of markdown files for a documentation directory.
    Explore 1st level folders (if any) OR the doc dir.

    :param doc_dir: (str) Root directory of the documentation
    :param doc_temp: (str) Root directory to find the header file
    :param header: (bool) Add an header markdown file into the list
    :param footer: (bool) Add a footer markdown file into the list

    :returns: list of filenames

    """
    files = list()

    # add the header file into the list
    if header is True:
        files.append(get_header(doc_temp))

    # get the list of all indexed folders in the documentation directory
    folders = get_doc_folders(doc_dir)

    # get all indexed files of each folder
    if len(folders) > 0:
        for folder in folders:
            files.extend(get_idx_markdown_files(doc_dir, folder))
    else:
        files.extend(get_idx_markdown_files(doc_dir, None))

    # add the footer file into the list
    if footer is True:
        files.append(get_footer(doc_temp))

    return files


# ---------------------------------------------------------------------------
# Generate a documentation file from some markdown sources
# ---------------------------------------------------------------------------


def gen_pdf_file(doc_temp, files, result_filename):
    """ Execute pandoc to generate a documentation in PDF.

    :param doc_temp: (str) Root directory of template files for the documentation
    :param files: (list) List of filenames (markdown files)
    :param result_filename: (str) Name of the newly created PDF documentation file

    """
    if len(files) == 0:
        raise IOError("No markdown files to generate the documentation!")

    # The expected files to generate the PDF:
    latex_template = os.path.join(doc_temp, "mytemplate.tex")
    test_file(latex_template)

    front_page = os.path.join(doc_temp, "frontpage.pdf")
    test_file(front_page)

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
    if front_page is not None:
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


def gen_html_file(doc_temp, css_filename, files, result_filename):
    """ Execute pandoc to generate a documentation in HTML 5.

    :param doc_temp: (str) Root directory of template files for the documentation
    :param css_filename: (str) Name of a CSS file
    :param files: (list) List of filenames (markdown files)
    :param result_filename: (str) Name of the newly created HTML documentation file

    """
    if len(files) == 0:
        raise IOError("No markdown files to generate the documentation!")

    test_file(css_filename)
    head_html_file = os.path.join(doc_temp, "include-scripts.txt")
    test_file(head_html_file)
    body_header_html_file = os.path.join(doc_temp, "header.txt")
    test_file(body_header_html_file)
    body_footer_html_file = os.path.join(doc_temp, "footer.txt")
    test_file(body_footer_html_file)

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
# Generate the SPPAS documentation file from all markdown sources
# ---------------------------------------------------------------------------


def generate_pdf():
    """ Generate the SPPAS documentation in PDF format. """

    # test if documentation directory is ok.
    doc_dir = os.path.join(SPPAS, "sppas", "doc")
    if os.path.exists(doc_dir) is False:
        print("Directory {:s} of the documentation is missing. Program halted.".format(doc_dir))
        sys.exit(1)

    # doc template files
    doc_temp = os.path.join(SPPAS, "Packager", "doc")

    # name of the resulting file
    result_filename = os.path.join(SPPAS, "documentation", "Documentation.pdf")

    # A unique PDF documentation file is generated from all markdown files
    md_files = get_all_md(doc_dir, doc_temp, header=False, footer=False)
    gen_pdf_file(doc_temp, md_files, result_filename)

# ---------------------------------------------------------------------------


def generate_html():
    """ Generate the SPPAS documentation in a directory with HTML files. """

    # test if documentation directory is ok.
    doc_dir = os.path.join(SPPAS, "sppas", "doc")
    if os.path.exists(doc_dir) is False:
        print("Directory {:s} of the documentation is missing. Program halted.".format(doc_dir))
        sys.exit(1)

    # doc template files
    css_file = os.path.join(".", "etc", "styles", "sppas.css")
    doc_temp = os.path.join(SPPAS, "Packager", "doc")

    # web directory to store resulting HTML files
    result_dirname = os.path.join(SPPAS, "Packager", "web")

    # get the list of all indexed folders in the documentation directory
    folders = get_doc_folders(doc_dir)

    for folder in folders:
        print(folder)
        folder_dirname = os.path.join(doc_dir, folder)
        files = get_all_md(folder_dirname, doc_temp, header=True, footer=False)
        print(files)
        result_filename = os.path.join(result_dirname, "documentation_" + folder + ".html")
        gen_html_file(doc_temp, css_file, files, result_filename)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    generate_pdf()
    generate_html()
