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
# File: manager.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""


# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

import os

from utils.fileutils import sppasFileUtils
from utils.fileutils import sppasDirUtils

from annotationdata.transcription import Transcription

import audiodata.aio
import annotationdata.aio
from annotations.infotier import sppasMetaInfoTier
from annotations.log import sppasLog

from annotations.Momel.sppasmomel import sppasMomel
from annotations.Intsint.sppasintsint import sppasIntsint
from annotations.IPUs.ipusseg import sppasIPUs
from annotations.Token.sppastok import sppasTok
from annotations.Phon.sppasphon import sppasPhon
from annotations.Chunks.sppaschunks import sppasChunks
from annotations.Align.sppasalign import sppasAlign
from annotations.Syll.sppassyll import sppasSyll
from annotations.Repet.sppasrepet import sppasRepet

from threading import Thread

# ----------------------------------------------------------------------------


class sppasAnnotationsManager( Thread ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      Parent class for running annotation processes.

    Process a directory full of files or a single file, and report on a
    progress.

    """
    def __init__(self, parameters):
        """
        Create a new sppasAnnotationsManager instance.
        Initialize a Thread.

        @param parameters (sppasParam) SPPAS parameters, i.e. config of annotations

        """
        Thread.__init__(self)

        # fix input variables
        self.parameters = parameters
        self._progress = None
        self._logfile  = None
        self._domerge  = True

        self.start()

    # ------------------------------------------------------------------------

    def fix_options(self, options):
        """
        Fix all options.

        Available options are:
            - domerge (bool) create a merged TextGrid file.

        @param options (option)

        """

        for opt in options:

            key = opt.get_key()

            if key == "domerge":
                self.set_domerge(opt.get_value())

            else:
                raise Exception('Unknown key option: %s'%key)

    # -----------------------------------------------------------------------

    def set_domerge(self, domerge):
        """
        Fix the domerge option.
        If domerge is set to True, a merged TextGrid file is created.

        @param domerge (Boolean)

        """
        self._domerge = domerge

    # ----------------------------------------------------------------------

    # -----------------------------------------------------------------------

    def set_filelist(self, extension, not_ext=[], not_start=[]):
        """
        Create a list of file names from the parameter inputs.

        @param extension: expected file extension
        @param not_ext: list of extension of files that must not be treated
        @param not_start: list of start of filenames that must not be treated
        @return a list of strings

        """
        filelist = []
        try:
            for sinput in self.parameters.get_sppasinput():

                inputfilename, inputfileextension = os.path.splitext(sinput)

                # Input is a file (and not a directory)
                if extension.lower() in audiodata.aio.extensions and os.path.isfile(sinput) is True:
                    filelist.append( sinput )

                elif inputfileextension.lower() in audiodata.aio.extensions:
                    sinput = inputfilename + extension
                    if os.path.isfile(sinput) is True:
                        filelist.append( sinput )
                    else:
                        if self._logfile is not None:
                            self._logfile.print_message("Can't find file %s\n" % sinput, indent=1, status=1)

                # Input is a directory:
                else:
                    # Get the list of files with 'extension' from the input directory
                    files = sppasDirUtils(sinput).get_files( extension )
                    filelist.extend( files )
        except:
            pass

        # Removing files with not_ext as extension or containing not_start
        # TODO: DEBUG!!!
        fl2 = []
        for x in filelist:
            is_valid = True
            for ne in not_ext:
                if x.lower().endswith(ne.lower()) == True:
                    #filelist.remove(x)
#                    print "remove %s"%x
                    is_valid = False
#                else:
#                    print "end with %s:%s? added %s"%(ne,x,x)
            for ns in not_start:
                basex = os.path.basename(x.lower())
                if basex.startswith(ns.lower()) == True:
                    #filelist.remove(x)
#                    print "remove %s"%x
                    is_valid = False
#                else:
#                    print "start with %s:%s? added %s"%(ns,x,x)
            if is_valid == True:
                fl2.append(x)

        return fl2

    # ------------------------------------------------------------------------

    def _get_filename(self, filename, extensions):
        """
        Return a filename corresponding to one of extensions.

        @param filename input file name
        @param extensions is the list of expected extension
        @return a file name of the first existing file with an expected extension or None

        """

        for ext in extensions:

            extfilename = os.path.splitext( filename )[0] + ext
            newfilename = sppasFileUtils(extfilename).exists()
            if newfilename is not None and os.path.isfile(newfilename):
                return newfilename

        return None

    # ------------------------------------------------------------------------
    # Run annotations.
    # ------------------------------------------------------------------------

    def run_momel(self, stepidx):
        """
        Execute the SPPAS implementation of momel.

        @param stepidx index of this annotations in the parameters
        @return number of files processed successfully

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            m = sppasMomel( self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=1 )
            return 0

        # Execute annotation for each file in the list
        for i,f in enumerate(filelist):

            # fix the default values
            m.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

            # Get the input file
            inname = self._get_filename(f, [".hz", ".PitchTier"])
            if inname is not None:

                # Fix output file names
                outname = os.path.splitext(f)[0]+"-momel.PitchTier"
                textgridoutname = os.path.splitext(f)[0] + '-momel' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    m.run(inname, trsoutput=textgridoutname, outputfile=outname)
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(textgridoutname,indent=2,status=0)
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message(textgridoutname+": %s"%str(e),indent=2,status=-1)
            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with pitch values. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_momel
    # ------------------------------------------------------------------------

    def run_intsint(self, stepidx):
        """
        Execute the SPPAS implementation of Intsint.

        @param stepidx index of this annotations in the parameters
        @return number of files processed successfully

        """
        # Initializations
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            intsint = sppasIntsint( self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=1 )
            return 0

        # Execute annotation for each file in the list
        for i,f in enumerate(filelist):

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

            # Get the input file
            ext = ['-momel'+self.parameters.get_output_format()]
            for e in annotationdata.aio.extensions_out:
                ext.append( '-momel'+e )

            inname = self._get_filename(f, ext)
            if inname is not None:

                # Fix output file names
                outname = os.path.splitext(f)[0] + '-intsint' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    intsint.run(inname, outname)
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname,indent=2,status=0)
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message(outname+": %s"%str(e),indent=2,status=-1)
            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with momel targets. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_intsint
    # ------------------------------------------------------------------------

    def run_ipusegmentation(self, stepidx):
        """
        Execute the SPPAS-IPUSegmentation program.

        @return number of files processed successfully

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" extension
        filelist = self.set_filelist(".wav")
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance, and fix options
        try:
            seg = sppasIPUs(self._logfile)
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=4 )
            return 0

        # Execute the annotation for each file in the list
        for i,f in enumerate(filelist):

            # fix the default values
            seg.reset()
            seg.fix_options(step.get_options())

            # Indicate the file to be processed
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file "+f, indent=1 )
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )

            # Fix input/output file name
            outname = os.path.splitext(f)[0] + self.parameters.get_output_format()

            # Is there already an existing IPU-seg (in any format)!
            ext = []
            for e in annotationdata.aio.extensions_in:
                if not e in ['.txt','.hz', '.PitchTier']:
                    ext.append(e)
            existoutname = self._get_filename(f, ext)

            # it's existing... but not in the expected format: convert!
            if existoutname is not None and existoutname != outname:
                # just copy the file!
                if self._logfile is not None:
                    self._logfile.print_message('Export '+existoutname, indent=2)
                    self._logfile.print_message('into '+outname, indent=2)
                try:
                    t = annotationdata.aio.read(existoutname)
                    annotationdata.aio.write(outname,t)
                    # OK, now outname is as expected! (or not...)
                except Exception:
                    pass

            # Execute annotation
            tgfname = sppasFileUtils(outname).exists()
            if tgfname is None:
                # No already existing IPU seg., but perhaps a txt.
                txtfile = self._get_filename(f, [".txt"])
                if self._logfile is not None:
                    if txtfile:
                        self._logfile.print_message("A transcription was found, perform Silence/Speech segmentation time-aligned with a transcription %s"%txtfile, indent=2,status=3)
                    else:
                        self._logfile.print_message("No transcription was found, perform Silence/Speech segmentation only.", indent=2,status=3)
                try:
                    seg.run(f, trsinputfile=txtfile, ntracks=None, diroutput=None, tracksext=None, trsoutput=outname)
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0)
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message( "%s for file %s\n" % (str(e),outname), indent=2,status=-1 )
            else:
                if seg.get_option('dirtracks') is True:
                    self._logfile.print_message("A time-aligned transcription was found, split into multiple files", indent=2,status=3)
                    try:
                        seg.run(f, trsinputfile=tgfname, ntracks=None, diroutput=None, tracksext=None, trsoutput=None)
                        files_processed_success += 1
                        if self._logfile is not None:
                            self._logfile.print_message(tgfname, indent=2,status=0 )
                    except Exception as e:
                        if self._logfile is not None:
                            self._logfile.print_message( "%s for file %s\n"%(str(e),tgfname), indent=2,status=-1 )
                else:
                    if self._logfile is not None:
                        self._logfile.print_message( "because a previous segmentation is existing.", indent=2,status=2 )

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_ipusegmentation
    # ------------------------------------------------------------------------

    def run_tokenization(self, stepidx):
        """
        Execute the SPPAS-Tokenization program.

        @return number of files processed successfully

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            self._progress.set_text("Loading resources...")
            t = sppasTok( step.get_langresource(), logfile=self._logfile, lang=step.get_lang() )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=4 )
            return 0

        # Execute the annotation for each file in the list
        for i,f in enumerate(filelist):

            # fix the default values
            t.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

            # Get the input file
            inname = self._get_filename(f, [self.parameters.get_output_format()] + annotationdata.aio.extensions_out)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-token' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    t.run( inname, outname )
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message( "%s for file %s\n"%(str(e),outname), indent=2,status=-1 )
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0 )

            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with transcription. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_tokenization
    # ------------------------------------------------------------------------

    def run_phonetization(self, stepidx):
        """
        Execute the SPPAS-Phonetization program.

        @return number of files processed successfully

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            self._progress.set_text("Loading resources...")
            p = sppasPhon( step.get_langresource(), logfile=self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%e, indent=1,status=4 )
            return 0

        # Execute the annotation for each file in the list
        for i,f in enumerate(filelist):

            # fix the default values
            p.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1)

            # Get the input file
            ext = ['-token'+self.parameters.get_output_format()]
            for e in annotationdata.aio.extensions_out_multitiers:
                ext.append( '-token'+e )

            inname = self._get_filename(f, ext)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-phon' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    p.run( inname, outname )
                except Exception as e:
                    import traceback
                    print traceback.format_exc()
                    if self._logfile is not None:
                        self._logfile.print_message( "%s for file %s\n"%(str(e),outname), indent=2,status=-1 )
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0 )

            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with toketization. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_phonetization
    # ------------------------------------------------------------------------

    def run_chunks_alignment(self, stepidx):
        """
        Execute the SPPAS Chunks alignment program.

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            a = sppasChunks( step.get_langresource(), logfile=self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=4 )
            return 0

        # Execute the annotation for each file in the list
        for i,f in enumerate(filelist):

            # fix the default values
            a.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

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
                    a.run( inname, intok, f, outname )
                except Exception as e:
                    if self._logfile is not None:
                        stre = unicode(e.message).encode("utf-8")
                        self._logfile.print_message( "%s for file %s\n"%(stre,outname), indent=2,status=-1 )
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0 )

            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a raw file with phonetization/tokenization. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_alignment
    # ------------------------------------------------------------------------

    def run_alignment(self, stepidx):
        """
        Execute the SPPAS-Alignment program.

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
        files_processed_success = 0
        self._progress.set_header(stepname)
        self._progress.update(0,"")

        # Get the list of input file names, with the ".wav" (or ".wave") extension
        filelist = self.set_filelist(".wav")#,not_start=["track_"])
        if len(filelist) == 0:
            return 0
        total = len(filelist)

        # Create annotation instance
        try:
            a = sppasAlign( step.get_langresource(), logfile=self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=4 )
            return 0

        # Execute the annotation for each file in the list
        for i,f in enumerate(filelist):

            # fix the default values
            a.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

            # Get the input file
            extt = ['-token'+self.parameters.get_output_format()]
            extp = ['-phon'+self.parameters.get_output_format()]
            for e in annotationdata.aio.extensions_out:
                extt.append( '-token'+e )
                extp.append( '-phon'+e )
            extt.append('-chunks'+self.parameters.get_output_format())
            extp.append('-chunks'+self.parameters.get_output_format())

            inname = self._get_filename(f, extp)
            intok  = self._get_filename(f, extt)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-palign' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    a.run( inname, intok, f, outname )
                except Exception as e:
                    if self._logfile is not None:
                        stre = unicode(e.message).encode("utf-8")
                        self._logfile.print_message( "%s for file %s\n"%(stre,outname), indent=2,status=-1 )
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0 )

            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with phonetization. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_alignment
    # ------------------------------------------------------------------------

    def run_syllabification(self, stepidx):
        """
        Execute the SPPAS syllabification.

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
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
            s = sppasSyll( step.get_langresource(), self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=4 )
            return 0

        for i,f in enumerate(filelist):

            # fix the default values
            s.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

            # Get the input file
            ext = ['-palign'+self.parameters.get_output_format()]
            for e in annotationdata.aio.extensions_out_multitiers:
                ext.append( '-palign'+e )

            inname = self._get_filename(f,ext)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-salign' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    s.run( inname, outname )
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message( "%s for file %s\n"%(str(e),outname), indent=2,status=-1 )
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0 )
            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with time-aligned phonemes. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_syllabification
    # ------------------------------------------------------------------------

    def run_repetition(self, stepidx):
        """
        Execute the automatic repetitions detection.

        """
        # Initializations
        step = self.parameters.get_step(stepidx)
        stepname = self.parameters.get_step_name(stepidx)
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
            self._progress.set_text("Loading resources...")
            r = sppasRepet( step.get_langresource(), self._logfile )
        except Exception as e:
            if self._logfile is not None:
                self._logfile.print_message( "%s\n"%str(e), indent=1,status=4 )
            return 0

        for i,f in enumerate(filelist):

            # fix the default values
            r.fix_options(step.get_options())

            # Indicate the file to be processed
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )
            if self._logfile is not None:
                self._logfile.print_message(stepname+" of file " + f, indent=1 )

            # Get the input file
            ext = ['-palign'+self.parameters.get_output_format()]
            for e in annotationdata.aio.extensions_out_multitiers:
                ext.append( '-palign'+e )

            inname = self._get_filename(f, ext)
            if inname is not None:

                # Fix output file name
                outname = os.path.splitext(f)[0] + '-ralign' + self.parameters.get_output_format()

                # Execute annotation
                try:
                    r.run( inname, None, outname )
                except Exception as e:
                    if self._logfile is not None:
                        self._logfile.print_message( "%s for file %s\n"%(str(e),outname), indent=2,status=-1 )
                else:
                    files_processed_success += 1
                    if self._logfile is not None:
                        self._logfile.print_message(outname, indent=2,status=0 )
            else:
                if self._logfile is not None:
                    self._logfile.print_message("Failed to find a file with time-aligned tokens. Read the documentation for details.",indent=2,status=2)

            # Indicate progress
            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        # Indicate completed!
        self._progress.update(1,"Completed (%d files successfully over %d files).\n"%(files_processed_success,total))
        self._progress.set_header("")

        return files_processed_success

    # End run_repetition
    # ------------------------------------------------------------------------

    def __add_trs(self, trs, trsinputfile):
        trsinput = annotationdata.aio.read( trsinputfile )
        for tier in trsinput:
            alreadin = False
            if trs.IsEmpty() is False:
                tiername = tier.GetName()
                for t in trs:
                    if t.GetName() == tiername:
                        alreadin = True
            if alreadin is False:
                trs.Add(tier)

    # ------------------------------------------------------------------------

    def merge(self):
        """
        Merge all annotated files.
        Force output format to TextGrid.
        It will be changed to XRA as soon as SppasEdit will allow to view:
            - annotation overlaps
            - alternative labels
            - hierarchy

        """
        self._progress.set_header("Create a merged TextGrid file...")
        self._progress.update(0,"")

        # Get the list of files with the ".wav" extension
        filelist = self.set_filelist(".wav", ["track_"])
        total = len(filelist)

        output_format = self.parameters.get_output_format()

        for i,f in enumerate(filelist):

            nbfiles = 0

            # Change f, to allow "replace" to work properly
            basef = os.path.splitext(f)[0]

            if self._logfile is not None:
                self._logfile.print_message("Merge outputs " + f, indent=1 )
            self._progress.set_text( os.path.basename(f)+" ("+str(i+1)+"/"+str(total)+")" )

            trs = Transcription()
            try:
                self.__add_trs(trs, basef + output_format) # Transcription
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-token" + output_format) # Tokenization
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-phon" + output_format) # Phonetization
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-chunks" + output_format) # PhonAlign, TokensAlign
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-palign" + output_format) # PhonAlign, TokensAlign
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-salign" + output_format) # Syllables
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-ralign" + output_format) # Repetitions
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-momel" + output_format) # Momel
                nbfiles = nbfiles + 1
            except Exception:
                pass
            try:
                self.__add_trs(trs, basef + "-intsint" + output_format) # INTSINT
                nbfiles = nbfiles + 1
            except Exception:
                pass

            try:
                if nbfiles > 1:
                    infotier = sppasMetaInfoTier()
                    tier = infotier.create_time_tier(trs.GetBegin(),trs.GetEnd())
                    trs.Add(tier)
                    annotationdata.aio.write( basef + "-merge.TextGrid", trs)
                    if self._logfile is not None:
                        self._logfile.print_message( basef + "-merge.TextGrid", indent=2,status=0)
                elif self._logfile is not None:
                    self._logfile.print_message( "", indent=2,status=2 )
            except Exception as e:
                if self._logfile is not None:
                    self._logfile.print_message( str(e), indent=2,status=-1)

            self._progress.set_fraction(float((i+1))/float(total))
            if self._logfile is not None:
                self._logfile.print_newline()

        self._progress.update(1,"Completed.")
        self._progress.set_header("")

    # End merge
    # ------------------------------------------------------------------------

    def run_annotations(self, progress):
        """
        Execute activated SPPAS steps.
        Get execution information from the 'parameters' object.

        """
        self._progress = progress

        # ##################################################################### #
        # Print header message in the log file
        # ##################################################################### #
        try:
            self._logfile = sppasLog( self.parameters )
            self._logfile.open_new( self.parameters.get_logfilename() )
            self._logfile.print_header()
        except Exception:
            self._logfile=None
            pass

        # ##################################################################### #
        # Run!
        # ##################################################################### #
        nbruns = []
        steps = False

        for i in range( self.parameters.get_step_numbers() ):

            nbruns.append(-1)
            if self.parameters.get_step_status(i) is True:

                if self._logfile is not None:
                    self._logfile.print_step(i)

                if steps is False:
                    steps=True
                else:
                    self._progress.set_new()

                if self.parameters.get_step_key(i) == "momel":
                    nbruns[i] = self.run_momel(i)
                elif self.parameters.get_step_key(i) == "intsint":
                    nbruns[i] = self.run_intsint(i)
                elif self.parameters.get_step_key(i) == "ipus":
                    nbruns[i] = self.run_ipusegmentation(i)
                elif self.parameters.get_step_key(i) == "tok":
                    nbruns[i] = self.run_tokenization(i)
                elif self.parameters.get_step_key(i) == "phon":
                    nbruns[i] = self.run_phonetization(i)
                elif self.parameters.get_step_key(i) == "chunks":
                    nbruns[i] = self.run_chunks_alignment(i)
                elif self.parameters.get_step_key(i) == "align":
                    nbruns[i] = self.run_alignment(i)
                elif self.parameters.get_step_key(i) == "syll":
                    nbruns[i] = self.run_syllabification(i)
                elif self.parameters.get_step_key(i) == "repet":
                    nbruns[i] = self.run_repetition(i)
                elif self._logfile is not None:
                    self._logfile.print_message('Unrecognized annotation step:%s'%self.parameters.get_step_name(i))

        if self._logfile is not None:
            self._logfile.print_separator()
            self._logfile.print_newline()
            self._logfile.print_separator()

        if self._domerge: self.merge()

        # ##################################################################### #
        # Log file: Final information
        # ##################################################################### #
        if self._logfile is not None:
            self._logfile.print_separator()
            self._logfile.print_message('Result statistics:')
            self._logfile.print_separator()
            for i in range( self.parameters.get_step_numbers() ):
                self._logfile.print_stat( i,nbruns[i] )
            self._logfile.print_separator()
            self._logfile.close()

    # End run
    # ------------------------------------------------------------------------
