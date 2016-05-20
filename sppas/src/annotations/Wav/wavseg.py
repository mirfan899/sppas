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
# File: wavseg.py
# ----------------------------------------------------------------------------

import os
import codecs
import logging

import audiodata.io
from audiodata.audiovolume    import AudioVolume
from audiodata.channel        import Channel

from presenters.audiosilencepresenter import AudioSilencePresenter

import annotationdata.io
from annotationdata.io.utils import gen_id
import annotationdata.utils.trsutils as trsutils
from annotationdata.utils.tierutils import TierUtils
from annotationdata.transcription   import Transcription
from annotationdata.media           import Media
from annotationdata.ptime.point     import TimePoint
from annotationdata.ptime.interval  import TimeInterval
from annotationdata.label.label     import Label
from annotationdata.annotation      import Annotation

from utils.fileutils import format_filename

from ipusaudio import IPUsAudio

# ----------------------------------------------------------------------------

class sppasSeg:
    """
    This class implements the IPUs segmentation.

    """
    def __init__(self, logfile=None):
        """
        Create a sppasSeg instance.

        @param logfile (sppasLog): a log file mainly used to print messages
                to the user.

        """
        self.logfile       = logfile
        self.ipusaudio     = IPUsAudio(None)
        self.restaure_default()

    # ------------------------------------------------------------------

    def restaure_default(self):
        """
        Set default values.

        """
        self.ipusaudio.set_channel(None)

        self.trsunits      = []
        self.trsnames      = []
        self.dirtracks     = False

        self.save_as_trs   = False
        self.addipuidx     = True  # Add IPU index in transcription tier (if any)

    # ------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------

    def set_dirtracks(self, dirtracks):
        """
        Fix the "dirtracks" option (boolean).

        """
        self.dirtracks = dirtracks

    def get_dirtracks(self):
        """
        Get the "dirtracks" option (boolean).

        """
        return self.dirtracks

    def set_save_as_trs(self, output):
        """
        Fix the "save as transcription" option (boolean).

        """
        self.save_as_trs = output

    def get_save_as_trs(self):
        """
        Get the "save as textgrid" option (boolean).

        """
        return self.save_as_trs

    def set_add_ipu_idx_in_trs(self, value):
        """
        Fix the "add IPU index in the transcription output" option (boolean).

        """
        self.addipuidx = value

    def get_add_ipu_idx_in_trs(self):
        """
        Get the "add IPU index in the transcription output" option (boolean).

        """
        return self.addipuidx

    # End OPTIONS
    # ------------------------------------------------------------------

    def fix_options(self, options):

        for opt in options:

            if "shift" == opt.get_key():
                self.ipusaudio.set_shift( opt.get_value() )

            elif "shift_start" == opt.get_key():
                self.ipusaudio.set_shift_start( opt.get_value() )

            elif "shift_end" == opt.get_key():
                self.ipusaudio.set_shift_end( opt.get_value() )

            elif "min_speech" == opt.get_key():
                self.ipusaudio.set_min_speech( opt.get_value() )

            elif "min_sil" == opt.get_key():
                self.ipusaudio.set_min_silence( opt.get_value() )

            elif "min_vol" == opt.get_key():
                self.ipusaudio.set_vol_threshold( opt.get_value() )

            elif "tracks" == opt.get_key():
                self.set_dirtracks( opt.get_value() )

            elif "save_as_trs" == opt.get_key():
                self.set_save_as_trs(opt.get_value())

            elif "add_ipu_idx" == opt.get_key():
                self.set_add_ipu_idx_in_trs(opt.get_value())

    # ------------------------------------------------------------------

    def get_trs(self):
        return self.trsunits


    def set_trs(self, filename):
        """
        Extract inter pausal units of the transcription.
        Input is a text file as:
                - Each line is supposed to be at least one unit.
                - Each '#' symbol is considered as a unit boundary.

        @param filename (string): contains the transcription

        """
        # False means that I DON'T know if there is a silence:
        # It does not mean that there IS NOT a silence.
        self.ipusaudio.set_bound_start(False)
        self.ipusaudio.set_bound_end(False)

        self.trsunits = []
        trs = annotationdata.io.read( filename )
        if trs.GetSize() != 1:
            raise IOError('Error while reading %s (not the expected number of tiers. Got %d)'%(filename,trs.GetSize()))
        tier = trs[0]
        if tier.GetSize() == 0:
            raise IOError('Error while reading %s (Got no utterances!)'%filename)

        # Fix bornes
        if tier[0].GetLabel().IsSilence() is True:
            self.ipusaudio.set_bound_start(True)
        if tier[-1].GetLabel().IsSilence() is True and tier.GetSize()>1:
            self.ipusaudio.set_bound_end(True)

        for ann in tier:
            if ann.GetLabel().IsSilence() is False:
                self.trsunits.append( ann.GetLabel().GetValue() )

    # ------------------------------------------------------------------

    def split(self, nbtracks=0):
        """
        Blind or controlled speech/silence segmentation.

        """
        if self.channel is None:
            raise Exception("No speech data to split.\n")

        if self.channel.get_duration() <= self.ipusaudio.min_channel_duration():
            raise Exception("Speech file is too short.\n")

        n = self.ipusaudio.split_into( nbtracks )
        if n != nbtracks:
            raise Exception("Silence detection failed: unable to find "+str(nbtracks)+" Inter-Pausal Units. Got: %d."%n)

        if self.logfile:
            self.logfile.print_message("Threshold volume value:     "+str(self.ipusaudio.vol_threshold), indent=3)
            self.logfile.print_message("Threshold silence duration: "+str(self.ipusaudio.min_sil_dur),   indent=3)
            self.logfile.print_message("Threshold speech duration:  "+str(self.ipusaudio.min_ipu_dur),   indent=3)
        else:
            logging.info("Threshold volume value:     "+str(self.ipusaudio.vol_threshold))
            logging.info("Threshold silence duration: "+str(self.ipusaudio.min_sil_dur))
            logging.info("Threshold speech duration:  "+str(self.ipusaudio.min_ipu_dur))

    # ------------------------------------------------------------------

    def get_from_transcription(self, inputfilename, tieridx=None):
        """
        Extract silences and transcription units from a transcription.
        Also extract track names if any.

        @param inputfilename is the input transcription file name

        """
        try:
            trsinput  = annotationdata.io.read(inputfilename)
        except IOError as e:
            raise IOError('WavSeg. No input transcription.\n'+str(e))

        self.trsinput = trsinput

        # Input tier
        if tieridx is None:
            trstier = None
            # priority: try to find a transcription.
            for tier in trsinput:
                tiername = tier.GetName().lower()
                if "trans" in tiername:
                    trstier = tier
                    break
            if trstier is None:
                # try other tier names
                for tier in trsinput:
                    tiername = tier.GetName().lower()
                    if "trs" in tiername or "ortho" in tiername or "toe" in tiername or "ipu" in tiername:
                        trstier = tier
                        break
            if trstier is None:
                trstier = trsinput[0]
        else:
            trstier = trsinput[tieridx]

        # Expected file names
        nametier = None
        for tier in trsinput:
            tiername = tier.GetName().lower()
            if "name" in tiername or "file" in tiername:
                nametier = tier

        trstracks = []
        silences  = []
        self.trsunits = []
        self.trsnames = []
        i = 0
        last = trstier.GetSize()
        while i < last:
            # Set the current annotation values
            __ann = trstier[i]
            __label = __ann.GetLabel().GetValue()

            # Save information
            if __ann.GetLabel().IsSilence():
                __start = int(__ann.GetLocation().GetBeginMidpoint() * self.channel.get_framerate())
                __end   = int(__ann.GetLocation().GetEndMidpoint()   * self.channel.get_framerate())
                # Verify next annotations (concatenate all silences between 2 tracks)
                if (i + 1) < last:
                    __nextann = trstier[i + 1]
                    while (i + 1) < last and __nextann.GetLabel().IsSilence():
                        __end   = int(__nextann.GetLocation().GetEndMidpoint() * self.channel.get_framerate())
                        i = i + 1
                        if (i + 1) < last:
                            __nextann = trstier[i + 1]
                silences.append([__start,__end])
            else:
                __start = int(__ann.GetLocation().GetBeginMidpoint() * self.channel.get_framerate())
                __end   = int(__ann.GetLocation().GetEndMidpoint()   * self.channel.get_framerate())
                trstracks.append([__start,__end])
                self.trsunits.append( __label )

                if nametier is not None:
                    #time = (__ann.GetLocation().GetBeginMidpoint() + __ann.GetLocation().GetEndMidpoint()) / 2.0
                    ##????????iname = TierUtils.Select(nametier, lambda a: time in a.Time)
                    # iname = TierUtils.Select(nametier, lambda a: time in a.GetLocation().GetValue().GetMidpoint())
                    aname = nametier.Find(__ann.GetLocation().GetBeginMidpoint(), __ann.GetLocation().GetEndMidpoint(), True)
                    if not len(aname):
                        trstracks.pop()
                        self.trsunits.pop()
                    else:
                        self.trsnames.append( format_filename(aname[0].GetLabel().GetValue()) )

            # Continue
            i = i + 1

        return (trstracks,silences)

    # ------------------------------------------------------------------


    # ------------------------------------------------------------------
    # Outputs
    # ------------------------------------------------------------------

    def write_list(self, filename, trstracks):
        encoding='utf-8'
        with codecs.open(filename ,'w', encoding) as fp:
            idx = 0
            for from_pos, to_pos in trstracks:
                # Print informations on stdout
                fp.write( "%.4f %.4f " %( float(from_pos)/float(self.channel.get_framerate()) , float(to_pos)/float(self.channel.get_framerate()) ))
                if len(self.trsnames)>0 and idx < len(self.trsnames):
                    ustr = self.trsnames[idx].encode('utf8')
                    fp.write( ustr.decode(encoding)+"\n" )
                else:
                    fp.write( "\n" )
                idx = idx+1

            # Finally, print audio duration
            fp.write( "%.4f\n" %self.channel.get_duration() )

    # ------------------------------------------------------------------

    def write_transcription(self, filename, trstracks, inputaudioname=None):
        if trstracks is None:
            raise Exception('No tracks to write.\n')

        # Create a transcription from tracks
        trs = Transcription("IPU-Segmentation")
        tieripu = trs.NewTier("IPU")
        tier    = trs.NewTier("Transcription")
        radius  = 1.0 / self.channel.get_framerate()

        try:
            i = 0
            to_pos_prec = 0
            for from_pos, to_pos in trstracks:
                if self.trsunits:
                    if (i > len(self.trsunits)):
                        raise Exception('Bad number of tracks to write\n')
                # From the previous track to the current track: silence
                if to_pos_prec < from_pos:
                    begin = float(to_pos_prec)/float(self.channel.get_framerate())
                    end   = float(from_pos)/float(self.channel.get_framerate())
                    a     = Annotation(TimeInterval(TimePoint(begin,radius), TimePoint(end,radius)), Label("#"))
                    tieripu.Append(a)
                    tier.Append(a.Copy())

                # New track with speech
                begin = float(from_pos)/float(self.channel.get_framerate())
                end   = float(to_pos)/float(self.channel.get_framerate())
                # ... IPU tier
                label = "ipu_%d"%(i+1)
                a  = Annotation(TimeInterval(TimePoint(begin,radius), TimePoint(end,radius)), Label(label))
                tieripu.Append(a)
                # ... Transcription tier
                if self.addipuidx is False:
                    label = ""
                if self.trsunits:
                    label = label + " " + self.trsunits[i]
                a  = Annotation(TimeInterval(TimePoint(begin,radius), TimePoint(end,radius)), Label(label))
                tier.Append(a)

                # Go to the next
                i += 1
                to_pos_prec = to_pos

            # The end is a silence?
            end_pos = float( self.channel.get_nframes() )
            if to_pos_prec < end_pos:
                begin = TimePoint(float(to_pos_prec)/float(self.channel.get_framerate()),radius)
                end   = TimePoint(float(end_pos)/float(self.channel.get_framerate()),radius)
                if begin < end:
                    a  = Annotation(TimeInterval(begin, end), Label("#"))
                    tieripu.Append(a)
                    tier.Append(a.Copy())
        except Exception as e:
            raise Exception('Error while converting tracks to the tier output.\n'+str(e)+'\n')

        # Link both tiers: IPU and Transcription
        try:
            trs.GetHierarchy().addLink('TimeAssociation', tieripu, tier)
        except Exception as e:
            logging.info('Error while assigning TimeAssociation hierarchy between IPU tier and Transcription tier: %s'%(str(e)))
            pass

        # Set media
        if inputaudioname is not None:
            extm = os.path.splitext(inputaudioname)[1].lower()[1:]
            media = Media( gen_id(), inputaudioname, "audio/"+extm )
            trs.AddMedia( media )
            for tier in trs:
                tier.SetMedia( media )

        # Write the transcription
        try:
            annotationdata.io.write(filename, trs)
        except Exception as e:
            raise Exception('Error while saving the transcription output.\n'+str(e)+'\n')

    # ------------------------------------------------------------------

    def create_trsunits(self, trstracks):
        """
        Create a list of transcription units from tracks.

        @param trstracks
        @return list of Transcription objects

        """
        if trstracks is None:
            raise Exception("No tracks found.\n")

        if self.trsinput is None:
            raise Exception("No trsinput found.\n")

        trs_list = []
        trsunits_size = len(self.trsunits)
        for i, track in enumerate(trstracks):
            from_pos = track[0]
            to_pos   = track[1]
            if self.trsunits and i > trsunits_size:
                raise Exception("Bad number of tracks.\n")

            # Create a new Transcription with speech
            start = float(from_pos) / float(self.channel.get_framerate())
            end   = float(to_pos) / float(self.channel.get_framerate())
            a = Annotation(TimeInterval(TimePoint(start,0.001), TimePoint(end,0.001)))
            new_trs = Transcription(self.trsinput.GetName())

            new_trs.SetMinTime( start )
            new_trs.SetMaxTime( end )

            for tier in self.trsinput:
                new_tier = TierUtils.Select(tier, lambda x: trsutils.overlaps(a, x))
                if new_tier is not None:
                    if new_tier[0].GetLocation().IsInterval():
                        new_tier[0].GetLocation().SetBeginMidpoint( start )
                        new_tier[-1].GetLocation().SetEndMidpoint( end )
                    new_trs.Append(new_tier)

            trsutils.TrsUtils.Shift(new_trs, new_trs.GetBegin())
            trs_list.append(new_trs)

        return trs_list

    # ------------------------------------------------------------------

    def run(self, audiofile, trsinputfile=None, trstieridx=None, ntracks=None, diroutput=None, tracksext=None, listoutput=None, textgridoutput=None):
        """
        Perform an IPU segmentation from an audio file.

            - audiofile is the sound input file name
            - trsinputfile is a transcription (or 'None')
            - ntracks expected number of tracks
            - diroutput is a directory name to save output tracks (one per unit)
            - tracksext is the track extension (used with the diroutput option)
            - listoutput is a file name  to save the IPU segmentation result (this file contains the begin time and end time of each unit, and the wav duration)
            - textgridoutput is a file name to save the IPU segmentation result.

        """

        # Fix audio
        fileName, fileExtension = os.path.splitext( audiofile )
        if not fileExtension.lower() in audiodata.io.extensions:
            raise Exception('Un-recognized audio file format: %s\n'%fileExtension)

        audiospeech = audiodata.io.open( audiofile )
        idx = audiospeech.extract_channel()
        self.channel = audiospeech.get_channel(idx)
        self.ipusaudio.set_channel( self.channel )
        self.ipusaudio.set_bound_start(False)
        self.ipusaudio.set_bound_end(False)

        # Fix transcription units if a transcription is given
        trstracks = None
        sil = True

        self.trsinput = None
        if trsinputfile:
            if trsinputfile.lower().endswith("txt"):
                self.set_trs( trsinputfile )
            else:
                # Get tracks and silences from an annotated file
                (trstracks,silences) = self.get_from_transcription( trsinputfile, trstieridx )
                self.ipusaudio.set_silences( silences )
                # Do not find silences automatically!
                sil = False

        if sil is True:
            # Fix nb tracks to split into
            if ntracks is not None:
                ntracks = ntracks
            else:
                ntracks = len( self.trsunits )

            # Find automatically silences
            self.split( ntracks )
            trstracks = self.ipusaudio.extract_tracks()

        if trstracks is None:
            trstracks = self.ipusaudio.extract_tracks(shift_start=0., shift_end=0.)


        # save output

        # Write silences/units into a transcription file
        if textgridoutput is not None:
            self.write_transcription(textgridoutput,trstracks,audiofile)

        # Write speech into track files with a given file extension
        if diroutput is not None or self.dirtracks is True:
            if diroutput is None:
                diroutput = fileName+"-tracks"
            if self.logfile is not None:
                self.logfile.print_message(str(len(self.trsunits))+" units to write.", indent=3)
                #self.logfile.print_message(str(len(self.silence))+" silences.", indent=3)
            # Automatically activate the list output file
            if listoutput is None:
                listoutput = os.path.join(diroutput, "index.txt")
                if self.logfile is not None:
                    self.logfile.print_message(listoutput, indent=3)

            # Fix output files format (txt or TextGrid)
            if tracksext is None:
                tracksext = "TextGrid" if self.save_as_trs is True else "txt"

            if "."+tracksext.strip().lower() in annotationdata.io.extensions and tracksext != "txt":
                trs = self.create_trsunits(trstracks)
                audiosilpres = AudioSilencePresenter(self.ipusaudio.chansil)
                audiosilpres.write_tracks(trstracks, diroutput, ext=tracksext, trsunits=trs, trsnames=self.trsnames)
            else:
                audiosilpres = AudioSilencePresenter(self.ipusaudio.chansil)
                audiosilpres.write_tracks(trstracks, diroutput, ext=tracksext, trsunits=self.trsunits, trsnames=self.trsnames)

        # Write silences boundaries (in seconds) into a file
        if (listoutput):
            self.write_list(listoutput,trstracks)

    # ------------------------------------------------------------------
