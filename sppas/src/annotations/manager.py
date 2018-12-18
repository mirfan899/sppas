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

    src.annotations.manager.py
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

"""
import logging
import os
from threading import Thread

from sppas.src.utils.fileutils import sppasFileUtils
from sppas.src.utils.fileutils import sppasDirUtils
from sppas.src.anndata import sppasTranscription, sppasRW

import sppas.src.audiodata.aio
import sppas.src.anndata.aio
from sppas.src.annotations.infotier import sppasMetaInfoTier
from sppas.src.annotations.log import sppasLog

from sppas.src.annotations.Momel.sppasmomel import sppasMomel
from sppas.src.annotations.Intsint.sppasintsint import sppasIntsint
from sppas.src.annotations.SearchIPUs.sppassearchipus import sppasSearchIPUs
from sppas.src.annotations.FillIPUs.sppasfillipus import sppasFillIPUs
from sppas.src.annotations.TextNorm.sppastextnorm import sppasTextNorm
from sppas.src.annotations.Phon.sppasphon import sppasPhon
from sppas.src.annotations.Chunks.sppaschunks import sppasChunks
from sppas.src.annotations.Align.sppasalign import sppasAlign
from sppas.src.annotations.Syll.sppassyll import sppasSyll
from sppas.src.annotations.TGA.sppastga import sppasTGA
from sppas.src.annotations.SelfRepet.sppasrepet import sppasSelfRepet

from .annotationsexc import AnnotationOptionError

# ----------------------------------------------------------------------------


class sppasAnnotationsManager(Thread):
    """Parent class for running annotation processes.

    :author:       Brigitte Bigi
    :organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    :contact:      develop@sppas.org
    :license:      GPL, v3
    :copyright:    Copyright (C) 2011-2018  Brigitte Bigi

    Process a directory full of files or a single file, and report on a
    progress.

    """
    def __init__(self, parameters):
        """Create a new sppasAnnotationsManager instance.

        Initialize a Thread.

        :param parameters: (sppasParam) SPPAS parameters, i.e. config of annotations

        """
        Thread.__init__(self)

        # fix input variables
        self.parameters = parameters
        self._progress = None
        self._logfile = None
        self.__do_merge = True

        self._annotations = dict()
        self._annotations['intsint'] = sppasIntsint
        self._annotations['momel'] = sppasMomel
        self._annotations['searchipus'] = sppasSearchIPUs
        self._annotations['fillipus'] = sppasFillIPUs
        self._annotations['textnorm'] = sppasTextNorm
        self._annotations['phon'] = sppasPhon

        self.start()

    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """Fix all options.

        Available options are:

            - domerge (bool) create a merged TextGrid file.

        :param options: (option)

        """
        for opt in options:

            key = opt.get_key()
            if key == "domerge":
                self.set_do_merge(opt.get_value())
            else:
                raise AnnotationOptionError(key)

    # -----------------------------------------------------------------------

    def set_do_merge(self, do_merge):
        """Fix the domerge option.

        If do merge is set to True, a merged TextGrid file is created.

        :param do_merge: (bool)

        """
        self.__do_merge = do_merge

    # ----------------------------------------------------------------------

    def set_progress(self, p=None):
        """Fix the progress system.

        :param p:

        """
        self._progress = p

    # -----------------------------------------------------------------------

    def set_filelist(self, extension, not_ext=[], not_start=[]):
        """Create a list of file names from the parameter inputs.

        :param extension: (str) expected file extension
        :param not_ext: (str) list of extensions of files that must not be treated
        :param not_start: (str) list of start of filenames that must not be treated
        :returns: a list of strings

        """
        filelist = []
        try:
            for sinput in self.parameters.get_sppasinput():

                inputfilename, inputfileextension = os.path.splitext(sinput)

                # Input is a file (and not a directory)
                if extension.lower() in sppas.src.audiodata.aio.extensions and \
                        os.path.isfile(sinput) is True:
                    if sinput not in filelist:
                        filelist.append(sinput)

                elif inputfileextension.lower() in sppas.src.audiodata.aio.extensions:
                    sinput = inputfilename + extension
                    if os.path.isfile(sinput) is True:
                        if sinput not in filelist:
                            filelist.append(sinput)
                    else:
                        if self._logfile is not None:
                            self._logfile.print_message(
                                "Can't find file %s\n" % sinput,
                                indent=1, status=1)

                # Input is a directory:
                else:
                    # Get the list of files with 'extension' from the input directory
                    files = sppasDirUtils(sinput).get_files(extension)
                    filelist.extend(files)
        except:
            pass

        # Removing files with not_ext as extension or containing not_start
        fl2 = []
        for x in filelist:
            is_valid = True
            for ne in not_ext:
                if x.lower().endswith(ne.lower()) is True:
                    is_valid = False

            for ns in not_start:
                basex = os.path.basename(x.lower())
                if basex.startswith(ns.lower()) is True:
                    is_valid = False

            if is_valid is True:
                fl2.append(x)

        return fl2

    # ------------------------------------------------------------------------

    def get_annot_files(self, pattern=None, extensions=None):
        """Search for annotated files with pattern.

        :param pattern: (str) The pattern to search in the filenames
        :param extensions: (str) The extension to search
        :returns: List of filenames matching pattern and extensions

        """
        files = list()

        # get from audio files
        audio_files = self.set_filelist(".wav")

        if extensions is None:
            extensions = sppas.src.anndata.aio.extensions_out

        if pattern is not None:
            ext = [pattern + self.parameters.get_output_format()]
            for e in extensions:
                ext.append(pattern + e)
        else:
            ext = extensions

        for f in audio_files:
            new_file = self._get_filename(f, ext)
            if new_file is not None and new_file not in files:
                files.append(new_file)

        # get from annotated files
        if pattern is not None:
            for f in self.parameters.get_sppasinput():
                if pattern in f and f not in files:
                    files.append(f)

        return files

    # ------------------------------------------------------------------------

    def _get_filename(self, filename, extensions):
        """Return a filename corresponding to one of extensions.

        :param filename: input file name
        :param extensions: the list of expected extension
        :returns: a file name of the first existing file with an expected extension or None

        """
        base_name = os.path.splitext(filename)[0]
        for ext in extensions:

            ext_filename = base_name + ext
            new_filename = sppasFileUtils(ext_filename).exists()
            if new_filename is not None and os.path.isfile(new_filename):
                return new_filename

        return None

    # ------------------------------------------------------------------------
    # Run annotations.
    # ------------------------------------------------------------------------

    def create_ann(self, annotation_key):
        """Create and configure an instance of an automatic annotation.

        :param annotation_key: (str) Key of an annotation
        :returns: sppasBaseAnnotation

        """
        # Find the index of this annotation
        step_idx = self.parameters.get_step_idx(annotation_key)
        if self._logfile is not None:
            self._logfile.print_step(step_idx)

        # Create the instance and fix options
        options = self.parameters.get_options(step_idx)
        auto_annot = self._annotations[annotation_key](self._logfile)
        if len(options) > 0:
            auto_annot.fix_options(options)

        return auto_annot

    # ------------------------------------------------------------------------

    def run_momel(self):
        """Execute the SPPAS implementation of Momel.

        :returns: number of files processed successfully

        """
        a = self.create_ann("momel")
        return a.batch_processing(
            self.get_annot_files(extensions=[".hz", ".PitchTier"]),
            self._progress,
            self.parameters.get_output_format())

    # ------------------------------------------------------------------------

    def run_intsint(self):
        """Execute the SPPAS implementation of Intsint.

        :returns: number of files processed successfully

        """
        a = self.create_ann("intsint")
        return a.batch_processing(
            self.get_annot_files(pattern="-momel"),
            self._progress,
            self.parameters.get_output_format())

    # -----------------------------------------------------------------------

    def run_searchipus(self):
        """Execute the SearchIPUs automatic annotation.

        :returns: number of files processed successfully

        """
        a = self.create_ann("searchipus")
        return a.batch_processing(
            self.set_filelist(".wav"),
            self._progress,
            self.parameters.get_output_format())

    # -----------------------------------------------------------------------

    def run_fillipus(self):
        """Execute the FillIPUs automatic annotation.

        :returns: number of files processed successfully

        """
        a = self.create_ann("fillipus")
        return a.batch_processing(
            self.set_filelist(".wav"),
            self._progress,
            self.parameters.get_output_format())

    # -----------------------------------------------------------------------

    def run_tokenization(self):
        """Execute the Text normalization automatic annotation.

        :returns: number of files processed successfully

        """
        a = self.create_ann("textnorm")

        self._progress.set_text("Loading resources...")
        step_idx = self.parameters.get_step_idx("textnorm")
        step = self.parameters.get_step(step_idx)
        a.set_vocab(step.get_langresource(), step.get_lang())

        return a.batch_processing(
            self.get_annot_files(),
            self._progress,
            self.parameters.get_output_format())

    # ------------------------------------------------------------------------

    def run_phonetization(self):
        """Execute the Phonetization automatic annotation.

        :returns: number of files processed successfully

        """
        a = self.create_ann("phon")

        self._progress.set_text("Loading resources...")
        step_idx = self.parameters.get_step_idx("phon")
        step = self.parameters.get_step(step_idx)
        a.set_dict(step.get_langresource())
        a.set_map(None)

        return a.batch_processing(
            self.get_annot_files(pattern="-token"),
            self._progress,
            self.parameters.get_output_format())

    # ------------------------------------------------------------------------

    def run_chunks_alignment(self):
        """Execute the SPPAS Chunks alignment program.

        """
        step_idx = self.parameters.get_step_idx("chunks")
        if self._logfile is not None:
            self._logfile.print_step(step_idx)

        # Initializations
        step = self.parameters.get_step(step_idx)
        stepname = self.parameters.get_step_name(step_idx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0, "")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            a = sppasChunks(step.get_langresource(), logfile=self._logfile)
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message("%s\n" % str(e), indent=1, status=4)
            return 0

        # Execute the annotation for each file in the list
        for i, f in enumerate(filelist):

            # fix the default values
            a.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            # Get the input file: only txt and xra supports non-time-aligned data
            extt = ['-token.txt', '-token.xra']
            extp = ['-phon.txt', '-phon.xra']

            inname = self._get_filename(f, extp)
            intok  = self._get_filename(f, extt)
            if inname is not None and intok is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-chunks' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    a.run(inname, intok, f, outname)
                except Exception as e:
                    if self._logfile is not None:
                        stre = unicode(e.message).encode("utf-8")
                        self._logfile.print_message("%s for file %s\n" % (stre, outname), indent=2, status=-1)
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2, status=0)

            else:
                self._logfile.print_message("File " + f, indent=1)
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a raw file with phonetization/tokenization."
                                                "Read the documentation for details.", indent=2, status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1, "Completed (%d files successfully over %d files).\n" % (files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # ------------------------------------------------------------------------

    def run_alignment(self):
        """Execute the SPPAS-Alignment program.

        """
        step_idx = self.parameters.get_step_idx("align")
        if self._logfile is not None:
            self._logfile.print_step(step_idx)

        # Initializations
        step = self.parameters.get_step(step_idx)
        stepname = self.parameters.get_step_name(step_idx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0, "")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")  #,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            a = sppasAlign(step.get_langresource(), logfile=self._logfile)
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message("%s\n" % str(e), indent=1, status=4)
            return 0

        # Execute the annotation for each file in the list
        for i, f in enumerate(filelist):

            # fix the default values
            a.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            # Get the input file
            extt = ['-token'+self.parameters.get_output_format()]
            extp = ['-phon'+self.parameters.get_output_format()]
            for e in sppas.src.anndata.aio.extensions_out:
                extt.append('-token'+e)
                extp.append('-phon'+e)
            extt.append('-chunks'+self.parameters.get_output_format())
            extp.append('-chunks'+self.parameters.get_output_format())

            inname = self._get_filename(f, extp)
            intok = self._get_filename(f, extt)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-palign' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    a.run(inname, intok, f, outname)
                    files_processed_success += 1
                except Exception as e:
                    if self._logfile is not None:
                        stre = unicode(e.message).encode("utf-8")
                        self._logfile.print_message("%s for file %s\n" % (stre, outname), indent=2, status=-1)

            else:
                self._logfile.print_message("File " + f, indent=1)
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with phonetization. "
                                                "Read the documentation for details.",
                                                indent=2, status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1, "Completed (%d files successfully over %d files).\n" % (files_processed_success, total))
        self._progress.set_header("")

        return files_processed_success

    # ------------------------------------------------------------------------

    def run_syllabification(self):
        """Execute the SPPAS syllabification.

        """
        step_idx = self.parameters.get_step_idx("syll")
        if self._logfile is not None:
            self._logfile.print_step(step_idx)

        # Initializations
        step = self.parameters.get_step(step_idx)
        stepname = self.parameters.get_step_name(step_idx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav",not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            s = sppasSyll(step.get_langresource(), self._logfile)
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message("%s\n" % str(e), indent=1, status=4)
            return 0

        for i, f in enumerate(filelist):

            # fix the default values
            s.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            # Get the input file
            ext = ['-palign'+self.parameters.get_output_format()]
            for e in sppas.src.anndata.aio.extensions_out_multitiers:
                ext.append('-palign'+e)

            inname = self._get_filename(f,ext)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-salign' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    s.run(inname, outname)
                    files_processed_success += 1
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message("%s for file %s\n" % (str(e), outname), indent=2, status=-1)

            else:
                self._logfile.print_message("File " + f, indent=1)
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with time-aligned phonemes. "
                                                "Read the documentation for details.", indent=2, status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1, "Completed (%d files successfully over %d files)."
                                 "\n" % (files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # ------------------------------------------------------------------------

    def run_tga(self):
        """Execute the SPPAS TGA.

        """
        step_idx = self.parameters.get_step_idx("tga")
        if self._logfile is not None:
            self._logfile.print_step(step_idx)

        # Initializations
        step = self.parameters.get_step(step_idx)
        step_name = self.parameters.get_step_name(step_idx)
        files_processed_success = 0
        self._progress.set_header(step_name)
        self._progress.update(0, "")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav", not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        s = sppasTGA(self._logfile)

        for i, f in enumerate(filelist):

            # fix the default values
            s.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            # Get the input file
            ext = ['-salign'+self.parameters.get_output_format()]
            for e in sppas.src.anndata.aio.extensions_out_multitiers:
                ext.append('-salign'+e)

            inname = self._get_filename(f, ext)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-tga' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    s.run(inname, outname)
                    files_processed_success += 1
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message("%s for file %s\n" % (str(e), outname), indent=2, status=-1)

            else:
                self._logfile.print_message("File " + f, indent=1)
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with time-aligned syllables. "
                                                "Read the documentation for details.", indent=2, status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1, "Completed (%d files successfully over %d files)."
                                 "\n" % (files_processed_success, total))
        self._progress.set_header("")

        return files_processed_success

    # ------------------------------------------------------------------------

    def run_self_repetition(self):
        """Execute the automatic repetitions detection.

        """
        step_idx = self.parameters.get_step_idx("selfrepet")
        if self._logfile is not None:
            self._logfile.print_step(step_idx)

        # Initializations
        step = self.parameters.get_step(step_idx)
        stepname = self.parameters.get_step_name(step_idx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0, "")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav", not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            self._progress.set_text("Loading resources...")
            r = sppasSelfRepet(step.get_langresource(), self._logfile)
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message("%s\n" % str(e), indent=1, status=4)
            return 0

        for i, f in enumerate(filelist):

            # fix the default values
            r.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text(os.path.basename(f)+
                                    " ("+str(i+1)+"/"+str(total)+")")

            # Get the input file
            ext = ['-palign'+self.parameters.get_output_format()]
            for e in sppas.src.anndata.aio.extensions_out_multitiers:
                ext.append('-palign'+e)

            inname = self._get_filename(f, ext)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-sralign' + \
                          self.parameters.get_output_format()

                # Execute annotation
                try:
                    r.run(inname, outname)
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname,
                                                    indent=2, status=0)
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message(
                            "%s for file %s\n" % (str(e), outname),
                            indent=2, status=-1)

            else:
                self._logfile.print_message("File " + f, indent=1)
                if self._logfile is not None:
                    self._logfile.print_message(
                        "Failed to find a file with time-aligned tokens/lemmas. "
                        "Read the documentation for details.",
                        indent=2, status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(
            1, "Completed ({:d} files successfully over {:d} files)."
               "\n".format(files_processed_success, total))
        self._progress.set_header("")

        return files_processed_success

    # ------------------------------------------------------------------------

    def __add_trs(self, trs, trs_inputfile):

        try:
            parser = sppasRW(trs_inputfile)
            trs_input = parser.read(trs_inputfile)
        except IOError:
            return 0

        for tier in trs_input:
            already_in = False
            if trs.is_empty() is False:
                tier_name = tier.get_name()
                for t in trs:
                    if t.get_name() == tier_name:
                        already_in = True
            if already_in is False:
                trs.append(tier)
        return 1

    # ------------------------------------------------------------------------

    def merge(self):
        """Merge all annotated files.

        Force output format to TextGrid.

        """
        self._progress.set_header("Create a merged TextGrid file...")
        self._progress.update(0, "")

        # Get the list of files with the ".wav" extension
        filelist = self.set_filelist(".wav", ["track_"])
        total = len(filelist)

        output_format = self.parameters.get_output_format()

        for i, f in enumerate(filelist):

            nbfiles = 0

            # Change f, to allow "replace" to work properly
            basef = os.path.splitext(f)[0]

            if self._logfile is not None:
                self._logfile.print_message("Merge outputs " + f, indent=1)
            self._progress.set_text(os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")")

            trs = sppasTranscription()
            nbfiles += self.__add_trs(trs, basef + output_format)               # OrthoTranscription
            nbfiles += self.__add_trs(trs, basef + "-token" + output_format)    # Tokenization
            nbfiles += self.__add_trs(trs, basef + "-phon" + output_format)     # Phonetization
            nbfiles += self.__add_trs(trs, basef + "-chunks" + output_format)   # ChunckAlign
            nbfiles += self.__add_trs(trs, basef + "-palign" + output_format)   # PhonAlign, TokensAlign
            nbfiles += self.__add_trs(trs, basef + "-salign" + output_format)   # SyllAlign
            nbfiles += self.__add_trs(trs, basef + "-sralign" + output_format)  # SelfRepetitions
            nbfiles += self.__add_trs(trs, basef + "-momel" + output_format)    # Momel
            nbfiles += self.__add_trs(trs, basef + "-intsint" + output_format)  # INTSINT
            nbfiles += self.__add_trs(trs, basef + "-tga" + output_format)      # TGA

            try:
                if nbfiles > 1:
                    info_tier = sppasMetaInfoTier(trs)
                    tier = info_tier.create_time_tier(trs.get_min_loc().get_midpoint(), 
                                                      trs.get_max_loc().get_midpoint())
                    trs.append(tier)
                    parser = sppasRW(basef + "-merge.TextGrid")
                    parser.write(trs)
                    if self._logfile is not None:
                        self._logfile.print_message(basef + "-merge.TextGrid", indent=2, status=0)
                elif self._logfile is not None:
                    self._logfile.print_message("", indent=2, status=2)
            except Exception as e:
                if self._logfile is not None:
                    self._logfile.print_message(str(e), indent=2, status=-1)

            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        self._progress.update(1, "Completed.")
        self._progress.set_header("")

    # ------------------------------------------------------------------------

    def run_annotations(self, progress):
        """Execute activated SPPAS steps.

        Get execution information from the 'parameters' object.

        """
        self._progress = progress

        # ##################################################################### #
        # Print header message in the log file
        # ##################################################################### #
        try:
            self._logfile = sppasLog(self.parameters)
            self._logfile.create(self.parameters.get_report_filename())
            self._logfile.print_header()
            self._logfile.print_annotations_header()
        except:
            self._logfile = None
            pass

        # ##################################################################### #
        # Run!
        # ##################################################################### #
        nbruns = []
        steps = False

        for i in range(self.parameters.get_step_numbers()):

            nbruns.append(-1)
            if self.parameters.get_step_status(i) is True:

                if steps is False:
                    steps = True
                else:
                    self._progress.set_new()

                try:
                    if self.parameters.get_step_key(i) == "momel":
                        nbruns[i] = self.run_momel()

                    elif self.parameters.get_step_key(i) == "intsint":
                        nbruns[i] = self.run_intsint()

                    elif self.parameters.get_step_key(i) == "searchipus":
                        nbruns[i] = self.run_searchipus()

                    elif self.parameters.get_step_key(i) == "fillipus":
                        nbruns[i] = self.run_fillipus()

                    elif self.parameters.get_step_key(i) == "textnorm":
                        nbruns[i] = self.run_tokenization()

                    elif self.parameters.get_step_key(i) == "phon":
                        nbruns[i] = self.run_phonetization()

                    elif self.parameters.get_step_key(i) == "chunks":
                        nbruns[i] = self.run_chunks_alignment()

                    elif self.parameters.get_step_key(i) == "align":
                        nbruns[i] = self.run_alignment()

                    elif self.parameters.get_step_key(i) == "syll":
                        nbruns[i] = self.run_syllabification()

                    elif self.parameters.get_step_key(i) == "tga":
                        nbruns[i] = self.run_tga()

                    elif self.parameters.get_step_key(i) == "selfrepet":
                        nbruns[i] = self.run_self_repetition()

                    else:
                        raise KeyError(
                            'Unrecognized annotation step: {:s}'
                            ''.format(self.parameters.get_step_name(i)))

                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message(
                            "{:s}\n".format(str(e)), indent=1, status=4)
                    nbruns[i] = 0

        if self._logfile is not None:
            self._logfile.print_separator()
            self._logfile.print_newline()
            self._logfile.print_separator()

        if self.__do_merge:
            self.merge()

        # ##################################################################### #
        # Log file: Final information
        # ##################################################################### #
        if self._logfile is not None:
            self._logfile.print_separator()
            self._logfile.print_message('Result statistics:')
            self._logfile.print_separator()
            for i in range(self.parameters.get_step_numbers()):
                self._logfile.print_stat(i, str(nbruns[i]))
            self._logfile.print_separator()
            self._logfile.close()
