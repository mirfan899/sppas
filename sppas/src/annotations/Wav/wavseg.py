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
from audiodata.channelsilence import ChannelSilence

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
        self.silence       = []
        self.restaure_default()

    # ------------------------------------------------------------------

    def restaure_default(self):
        """
        Set default values.
        """
        self.pause_seconds = 0.250
        self.min_length    = 0.300
        self.volume_cap    = 0
        self.shift_start   = 0.010
        self.shift_end     = 0.020
        self.winlenght     = 0.020

        self.bornestart = 0
        self.borneend   = 0

        self.trsunits      = []
        self.trsnames      = []
        self.chansil       = None
        self.dirtracks     = False

        self.save_as_trs   = False
        self.addipuidx     = True  # Add IPU index in transcription tier (if any)

    # ------------------------------------------------------------------
    # Getters and Setters
    # ------------------------------------------------------------------

    def set_min_volume(self,volume_cap):
        """
        Fix the default minimum volume value (rms).

        """
        self.volume_cap = int(volume_cap)

    def set_min_silence(self,pause_seconds):
        """
        Fix the default minimum speech duration (in seconds).

        """
        self.pause_seconds = float(pause_seconds)

    def set_min_speech(self,min_length):
        """
        Fix the default minimum silence duration (in seconds).

        """
        self.min_length = float(min_length)

    def set_vol_win_lenght(self, winlength):
        """
        Fix the default windows length for RMS estimations.

        """
        self.winlenght = max(winlength, 0.005)

    def set_shift(self,s):
        """
        Fix the default minimum boundary shift value (in seconds).

        """
        self.shift_start = float(s)
        self.shift_end   = float(s)

    def set_shift_start(self,s):
        """
        Fix the default minimum boundary shift value (in seconds).

        """
        self.shift_start = float(s)

    def set_shift_end(self,s):
        """
        Fix the default minimum boundary shift value (in seconds).

        """
        self.shift_end = float(s)

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
                self.set_shift( opt.get_value() )

            elif "shift_start" == opt.get_key():
                self.set_shift_start( opt.get_value() )

            elif "shift_end" == opt.get_key():
                self.set_shift_end( opt.get_value() )

            elif "min_speech" == opt.get_key():
                self.set_min_speech( opt.get_value() )

            elif "min_sil" == opt.get_key():
                self.set_min_silence( opt.get_value() )

            elif "min_vol" == opt.get_key():
                v = opt.get_value()
                if v > 0:
                    self.set_min_volume( v )

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
        # 0 means that I doN'T know if there is a silence:
        # It does not mean that there IS NOT a silence.
        self.bornestart = 0
        self.borneend   = 0

        self.trsunits = []
        trs = annotationdata.io.read( filename )
        if trs.GetSize() != 1:
            raise IOError('Error while reading %s (not the expected number of tiers. Got %d)'%(filename,trs.GetSize()))
        tier = trs[0]
        if tier.GetSize() == 0:
            raise IOError('Error while reading %s (Got no utterances!)'%filename)

        # Fix bornes
        if tier[0].GetLabel().IsSilence() is True:
            self.bornestart = 1
        if tier[-1].GetLabel().IsSilence() is True and tier.GetSize()>1:
            self.borneend = 1

        for ann in tier:
            if ann.GetLabel().IsSilence() is False:
                self.trsunits.append( ann.GetLabel().GetValue() )

    # ------------------------------------------------------------------

    def check_boundaries(self, tracks):
        """
        Check if silences at start and end are as expected.

        @return bool

        """
        if self.bornestart == 0 and self.borneend == 0:
            # we do not know anything about silences at start and end
            # then, everything is ALWAYS OK!
            return True

        first_from_pos = tracks[0][0]
        last_to_pos = tracks[len(tracks)-1][1]

        # If I expected a silence at start... and I found a track
        if self.bornestart != 0 and first_from_pos==0:
            return False

        # If I expected a silence at end... and I found a track
        if self.borneend != 0 and last_to_pos==self.chansil.get_channel().get_nframes():
            return False

        return True

    # ------------------------------------------------------------------

    def search_tracks(self, volume):
        """
        Return the number of tracks if volume is used as threshold.
        """
        self.chansil.search_silences(volume, mintrackdur=0.08)
        self.chansil.filter_silences(self.pause_seconds)
        return self.chansil.extract_tracks(self.min_length, self.shift_start, self.shift_end)

    # ------------------------------------------------------------------

    def split_into_vol(self, nbtracks):
        """
        Try various volume values to estimate silences then get the expected number of tracks.

        @param nbtracks is the expected number of IPUs

        """
        volstats = self.chansil.get_volstats()
        # Min volume in the speech
        vmin = volstats.min()
        # Max is set to the mean
        vmax = volstats.mean()
        # Step is necessary to not exaggerate a detailed search!
        # step is set to 5% of the volume between min and mean.
        step = int( (vmax - vmin) / 20.0 )
        # Min and max are adjusted
        vmin += step
        vmax -= step

        # Save initial value (to restore it later)
        init_vol_cap = self.volume_cap

        # First Test !!!
        self.volume_cap = vmin
        tracks = self.search_tracks(vmin)
        n = len(tracks)
        b = self.check_boundaries(tracks)

        while (n != nbtracks or b is False):
            # We would never be done anyway.
            if (vmax==vmin) or (vmax-vmin) < step:
                self.volume_cap = init_vol_cap
                return n

            # Try with the middle volume value
            vmid = int(vmin + (vmax - vmin) / 2.0)
            if n > nbtracks:
                # We split too often. Need to consider less as silence.
                vmax = vmid
            elif n < nbtracks:
                # We split too seldom. Need to consider more as silence.
                vmin = vmid
            else:
                # We did not find start/end silence.
                vmin += step

            # Find silences with these parameters
            self.volume_cap = int(vmid)
            tracks = self.search_tracks(vmid)
            n = len(tracks)
            b = self.check_boundaries(tracks)

        self.volume_cap = init_vol_cap
        return 0

    # ------------------------------------------------------------------

    def split_into(self, nbtracks):
        """
        Try various volume values, pause durations and silence duration to get silences.

        @param nbtracks is the expected number of silences

        """
        # Try with default parameters:
        tracks = self.search_tracks(self.volume_cap)
        n = len(tracks)
        b = self.check_boundaries(tracks)

        if n == nbtracks and b is True:
            return True

        # Try with default lengths (change only volume):
        n = self.split_into_vol( nbtracks )
        if n == 0:
            return True

        if n > nbtracks:
            # We split too often. Try with larger' values.
            while n > nbtracks:
                self.pause_seconds += 0.010
                self.min_length    += 0.010
                try:
                    n = self.split_into_vol( nbtracks )
                except Exception:
                    return False
                if n == 0:
                    return True
        else:
            # We split too seldom. Try with shorter' values.
            p = self.pause_seconds
            m = self.min_length
            while n < nbtracks and self.pause_seconds>0.040:
                self.pause_seconds -= 0.010
                try:
                    n = self.split_into_vol( nbtracks )
                except Exception:
                    return False
                if n == 0:
                    return True
            # we failed...
            self.pause_seconds = p
            while n < nbtracks and self.min_length>0.040:
                self.min_length -= 0.010
                try:
                    n = self.split_into_vol( nbtracks )
                except Exception:
                    return False
                if n == 0:
                    return True
            # we failed...
            self.min_length = m
            while n < nbtracks and self.pause_seconds>0.040 and self.min_length>0.040:
                self.min_length    -= 0.010
                self.pause_seconds -= 0.010
                try:
                    n = self.split_into_vol( nbtracks )
                except Exception:
                    return False
                if n == 0:
                    return True

        return False

    # ------------------------------------------------------------------

    def split(self, nbtracks=None):
        """
        Main split function: blind or controlled silence detection.

        """
        if nbtracks is not None:
            _nbtracks = nbtracks
        else:
            _nbtracks = len( self.trsunits )

        if self.channel.get_duration() <= max(self.min_length,self.pause_seconds):
            if self.logfile:
                self.logfile.print_message("Speech file is too short!",indent=3,status=1)
            else:
                logging.info('Speech file is too short: %f'%self.channel.get_duration())
            self.chansil.reset_silences()
            return

        # Blind or controlled silence detection
        if _nbtracks > 0:
            res = self.split_into( _nbtracks )
            if not res:
                raise Exception("Silence detection failed.\nUnable to find "+str(_nbtracks)+" inter-pausal units.\n")

        else:
            self.search_tracks( self.volume_cap )

        if self.logfile:
            self.logfile.print_message("Threshold volume value:     "+str(self.volume_cap),    indent=3)
            self.logfile.print_message("Threshold silence duration: "+str(self.pause_seconds), indent=3)
            self.logfile.print_message("Threshold speech duration:  "+str(self.min_length),    indent=3)
        else:
            logging.info("Threshold volume value:     "+str(self.volume_cap))
            logging.info("Threshold silence duration: "+str(self.pause_seconds))
            logging.info("Threshold speech duration:  "+str(self.min_length))

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
        self.silence = []
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
                self.silence.append([__start,__end])
            else:
                __start = int(__ann.GetLocation().GetBeginMidpoint() * self.channel.get_framerate())
                __end   = int(__ann.GetLocation().GetEndMidpoint()   * self.channel.get_framerate())
                trstracks.append([__start,__end])
                self.trsunits.append( __label )

                if nametier is not None:
                    time = (__ann.GetLocation().GetBeginMidpoint() + __ann.GetLocation().GetEndMidpoint()) / 2.0
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

        return trstracks

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

            # Finally, print wav duration
            fp.write( "%.4f\n" %(float(self.channel.get_nframes())/float(self.channel.get_framerate())) )

    # ------------------------------------------------------------------

    def write_transcription(self, filename, trstracks, inputaudioname=None):
        if trstracks is None:
            raise Exception('No tracks found to be written.\n')

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
            logging.info('Error while assigning hierarchy between IPU tier and Transcription tier: %s'%(str(e)))
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

        # Set input

        fileName, fileExtension = os.path.splitext( audiofile )
        if fileExtension.lower() in audiodata.io.extensions:

            audiospeech = audiodata.io.open( audiofile )
            idx = audiospeech.extract_channel()
            self.channel = audiospeech.get_channel(idx)
            self.chansil = ChannelSilence( self.channel, self.winlenght )

        else:
            raise Exception('Input error: unrecognized file format %s\n'%fileExtension)

        self.bornestart = 0
        self.borneend   = 0

        # Fix transcription units if a transcription is given

        trstracks = None
        sil = True

        self.trsinput = None
        if trsinputfile:
            if trsinputfile.lower().endswith("txt"):
                self.set_trs( trsinputfile )
            else:
                # Get tracks and silences from an annotated file
                trstracks = self.get_from_transcription( trsinputfile, trstieridx )
                self.chansil.set_silences( self.silence )
                # Do not find silences automatically!
                sil = False

        if sil is True:
            # Find automatically silences
            self.split( ntracks )
            trstracks = self.chansil.extract_tracks( self.min_length, self.shift_start, self.shift_end)

        if trstracks is None:
            trstracks = self.chansil.extract_tracks( self.min_length, 0., 0.)


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
                self.logfile.print_message(str(len(self.silence))+" silences.", indent=3)
            # Automatically Activate the list output file
            if listoutput is None:
                listoutput = os.path.join(diroutput, "index.txt")
                if self.logfile is not None:
                    self.logfile.print_message(listoutput, indent=3)

            # Fix output files format (txt or TextGrid)
            if tracksext is None:
                tracksext = "TextGrid" if self.save_as_trs is True else "txt"

            if "."+tracksext.strip().lower() in annotationdata.io.extensions and tracksext != "txt":
                trs = self.create_trsunits(trstracks)
                audiosilpres = AudioSilencePresenter(self.chansil)
                audiosilpres.write_tracks(trstracks, diroutput, ext=tracksext, trsunits=trs, trsnames=self.trsnames)
            else:
                audiosilpres = AudioSilencePresenter(self.chansil)
                audiosilpres.write_tracks(trstracks, diroutput, ext=tracksext, trsunits=self.trsunits, trsnames=self.trsnames)

        # Write silences boundaries (in seconds) into a file
        if (listoutput):
            self.write_list(listoutput,trstracks)


        # finish properly

        self.restaure_default()
        if trstracks is None:
            nbtracks = 0
        else:
            try:
                nbtracks = len(trstracks)
            except Exception:
                nbtracks = 0
        return (self.silence,nbtracks)

    # ------------------------------------------------------------------
