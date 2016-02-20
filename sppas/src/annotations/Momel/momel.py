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
# File: momel.py
# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2015  Brigitte Bigi"""

# ----------------------------------------------------------------------------

import os
import sys
import math

from annotationdata.transcription import Transcription
from annotationdata.annotation import Annotation
from annotationdata.ptime.point import TimePoint
from annotationdata.label.label import Label
import annotationdata.io

from annotations.Wav.wavpitch import WavePitch
from annotationdata.pitch import Pitch

from st_cib import Targets
from intsint import Intsint
import momelutil


# ##################################################################### #
# Momel class implementation
# ##################################################################### #
class Momel:
    """ A class to filter f0 and to modelize the melodie.
    """

    # ##################################################################### #
    # Constructor
    # ##################################################################### #
    def __init__(self):
        """ Create a new sppasMomel instance.
        """

        # Constants
        self.SEUILV = 50.
        self.FSIGMA = 1.
        self.HALO_BORNE_TRAME = 4
        self.RAPP_GLITCH = 0.05
        self.ELIM_GLITCH = True

        # Create data structures with default values
        self.initialize()

        # Default Option values

        # cible window length (lfen1 est en pointes echantillon, pas milliseconds)
        self.lfen1 = 30
        # f0 threshold
        self.hzinf = 50
        # f0 ceiling (Hirst, Di Cristo et Espesser : hzsup est calcule automatiquement)
        self.hzsup = 600
        # maximum error (Maxec est 1+Delta en Hirst, Di Cristo et Espesser)
        self.maxec = 1.04
        # reduc window length (lfen2 est en pointes echantillon, pas milliseconds)
        self.lfen2 = 20
        # minimal distance (seuildiff_x est en pointes echantillon, pas milliseconds)
        self.seuildiff_x = 5
        # minimal frequency ratio
        self.seuilrapp_y = 0.05

    # End __init__
    # -------------------------------------------------------------------


    def initialize(self):
        """ Set some variables to their default values.
            Parameters: None
            Return:     None
        """
        # Array of pitch values
        self.hzptr = []
        self.nval  = 0
        self.delta = 0.01

        # Output of cible:
        self.cib = []
        # Output of reduc:
        self.cibred = []
        # Output of reduc2:
        self.cibred2 = []

    # End initialize
    # -------------------------------------------------------------------


    # ##################################################################### #
    # Setters for optional values
    # ##################################################################### #

    def set_pitch_array(self,arrayvals):
        self.hzptr = arrayvals
        self.nval = len(self.hzptr)

    def set_option_elim_glitch(self,activate=True):
        self.ELIM_GLITCH=activate

    def set_option_win1(self,val):
        self.lfen1 = val
        assert(self.lfen1 > 0)

    def set_option_lo(self,val):
        self.hzinf = val

    def set_option_hi(self,val):
        self.hzsup = val

    def set_option_maxerr(self,val):
        self.maxec = val

    def set_option_win2(self,val):
        self.lfen2 = val

    def set_option_mind(self,val):
        self.seuildiff_x = val

    def set_option_minr(self,val):
        self.seuilrapp_y = val


    # ################################################################# #
    # Elim glitch
    # ################################################################# #

    def elim_glitch(self):
        """ Eliminate Glitch of the pitch values array.
            Set a current pith value to 0 if left and right values
            are greater than 5% more than the current value.
            Parameters: None
            Return:     None
        """
        _delta = 1.0 + self.RAPP_GLITCH
        for i in range(1,self.nval-1):
            cur  = self.hzptr[i]
            gprec = self.hzptr[i-1] * _delta
            gnext = self.hzptr[i+1] * _delta
            if (cur > gprec and cur > gnext):
                self.hzptr[i] = 0.

    # End elim_glitch
    # ------------------------------------------------------------------


    # ################################################################## #
    # Cible
    # ################################################################## #

    def calcrgp(self,pond,dpx,fpx):
        """ From inputs, estimates: a0, a1, a2.
            Exception:   raise if an error occurs
        """
        pn = 0.
        sx = sx2 = sx3 = sx4 = sy = sxy = sx2y = 0.
        for ix in range(dpx,fpx+1):
            p = pond[ix]
            if (p != 0.):
                val_ix = float(ix)
                y   = self.hzptr[ix]
                x2  = val_ix * val_ix
                x3  = x2 * val_ix
                x4  = x2 * x2
                xy  = val_ix * y
                x2y = x2 * y

                pn   = pn  + p
                sx   = sx  + (p * val_ix)
                sx2  = sx2 + (p * x2)
                sx3  = sx3 + (p * x3)
                sx4  = sx4 + (p * x4)
                sy   = sy  + (p * y)
                sxy  = sxy + (p * xy)
                sx2y = sx2y + (p * x2y)

        if (pn < 3.):
            raise ValueError('pn < 3')

        spdxy  = sxy  - (sx * sy) / pn
        spdx2  = sx2  - (sx * sx) / pn
        spdx3  = sx3  - (sx * sx2) / pn
        spdx4  = sx4  - (sx2 * sx2) / pn
        spdx2y = sx2y - (sx2 * sy) / pn

        muet = (spdx2 * spdx4) - (spdx3 * spdx3)
        if (spdx2 == 0. or muet == 0.):
            raise ValueError('spdx2 == 0. or muet == 0.')

        self.a2 = (spdx2y * spdx2 - spdxy * spdx3) / muet
        self.a1 = (spdxy - self.a2 * spdx3) / spdx2
        self.a0 = (sy - self.a1 * sx - self.a2 * sx2) / pn

    # End calcrgp
    # ------------------------------------------------------------------


    def cible(self):
        """ cible.
        """
        if len(self.hzptr)==0:
            raise IOError('Momel::momel.py. IOError: empty pitch array')
        if (self.hzsup < self.hzinf):
            raise ValueError('Momel::momel.py. Options error: F0 ceiling > F0 threshold')

        pond = []
        pondloc = [] # local copy of pond
        hzes = []
        for ix in range(self.nval):
            hzes.append(0.)
            if (self.hzptr[ix] > self.SEUILV):
                pond.append(1.0)
                pondloc.append(1.0)
            else:
                pond.append(0.0)
                pondloc.append(0.0)

        # Examinate each pitch value
        for ix in range(self.nval):
            # Current interval to analyze: from dpx to fpx
            dpx = ix - int(self.lfen1 / 2)
            fpx = dpx + self.lfen1 + 1


            # BB: do not go out of the range!
            if dpx < 0:
                dpx = 0
            if fpx > self.nval:
                fpx = self.nval

            # copy original pond values for the current interval
            for i in range(dpx,fpx):
                pondloc[i] = pond[i]

            nsup  = 0
            nsupr = -1
            xc = yc = 0.0
            ret_rgp = True
            while nsup > nsupr:
                nsupr = nsup
                nsup  = 0
                try:
                    # Estimate values of: a0, a1, a2
                    self.calcrgp(pondloc, dpx, fpx-1)
                except Exception:
                    # if calcrgp failed.
                    #print "calcrgp failed: ",e
                    ret_rgp=False
                    break
                else:
                    # Estimate hzes
                    for ix2 in range(dpx,fpx):
                        hzes[ix2] = self.a0 + (self.a1 + self.a2 * float(ix2)) * float(ix2)
                    for x in range(dpx,fpx):
                        if (self.hzptr[x] == 0. or (hzes[x] / self.hzptr[x]) > self.maxec):
                            nsup = nsup + 1
                            pondloc[x] = 0.0

            # Now estimate xc and yc for the new 'cible'
            if (ret_rgp==True and self.a2 != 0.0):
                vxc = (0.0 - self.a1) / (self.a2 + self.a2)
                if ((vxc > ix - self.lfen1) and (vxc < ix + self.lfen1)):
                    vyc = self.a0 + (self.a1 + self.a2 * vxc) * vxc
                    if (vyc > self.hzinf and vyc < self.hzsup):
                        xc = vxc
                        yc = vyc

            c = Targets()
            c.set(xc,yc)
            self.cib.append(c)

    # End cible
    # ------------------------------------------------------------------



    # ##################################################################### #
    # Reduc
    # ##################################################################### #

    def reduc(self):
        """ reduc.
        """

        # initialisations
        # ---------------
        xdist = []
        ydist = []
        dist  = []
        for i in range(self.nval):
            xdist.append(-1.)
            ydist.append(-1.)
            dist.append(-1.)

        lf  = int(self.lfen2 / 2)
        xds = yds = 0.
        np  = 0

        # xdist and ydist estimations
        for i in range(self.nval-1):
            # j1 and j2 estimations (interval min and max values)
            j1 = 0
            if (i > lf):
                j1 = i - lf
            j2 = self.nval - 1
            if (i+lf < self.nval-1):
                j2 = i + lf

            # left (g means left)
            sxg = syg = 0.
            ng = 0
            for j in range(j1,i+1):
                if (self.cib[j].get_y() > self.SEUILV):
                    sxg = sxg + self.cib[j].get_x()
                    syg = syg + self.cib[j].get_y()
                    ng = ng + 1

            # right (d means right)
            sxd = syd = 0.
            nd = 0
            for j in range(i+1,j2):
                if (self.cib[j].get_y() > self.SEUILV):
                    sxd = sxd + self.cib[j].get_x()
                    syd = syd + self.cib[j].get_y()
                    nd = nd + 1

            # xdist[i] and ydist[i] evaluations
            if (nd * ng > 0):
                xdist[i] = math.fabs (sxg / ng - sxd / nd)
                ydist[i] = math.fabs (syg / ng - syd / nd)
                xds = xds + xdist[i]
                yds = yds + ydist[i]
                np = np + 1
        # end for

        if np==0 or xds==0. or yds==0.:
            raise ValueError('Not enough targets with a value more than '+str(self.SEUILV)+' hz \n')


        # dist estimation (on pondere par la distance moyenne)
        # ----------------------------------------------------
        px = float(np) / xds
        py = float(np) / yds
        for i in range(self.nval):
            if (xdist[i] > 0.):
                dist[i] = (xdist[i] * px + ydist[i] * py) / (px + py)

        # Cherche les maxs des pics de dist > seuil
        # -----------------------------------------
        # Seuil = moy des dist ponderees
        seuil = 2. / (px + py)

        susseuil = False
        # Add the start value (=0)
        xd = []
        xd.append(0)
        xmax = 0

        for i in range(self.nval):
            if (len(xd) > int(self.nval/2)):
                raise Exception('Too many partitions (',len(xd),')\n')
            if (susseuil == False):
                if (dist[i] > seuil):
                    susseuil = True
                    xmax = i
            else:
                if (dist[i] > dist[xmax]):
                    xmax = i
                if (dist[i] < seuil and xmax > 0):
                    xd.append(xmax)
                    susseuil = False
        # end for
        # do not forget the last analyzed value!
        if (susseuil == True):
            xd.append(xmax)
        # Add the final value (=nval)
        xd.append(self.nval)

        # Partition sur les x
        # -------------------
        for ip in range(len(xd)-1):
            # bornes partition courante
            parinf = xd[ip]
            parsup = xd[ip + 1]

            sx = sx2 = sy = sy2 = 0.
            n = 0

            # moyenne sigma
            for j in range(parinf,parsup):
                # sur la pop d'une partition
                if (self.cib[j].get_y() > 0.):
                    sx  = sx  + self.cib[j].get_x()
                    sx2 = sx2 + self.cib[j].get_x() * self.cib[j].get_x()
                    sy  = sy  + self.cib[j].get_y()
                    sy2 = sy2 + self.cib[j].get_y() * self.cib[j].get_y()
                    n = n + 1

            # pour la variance
            if (n > 1):
                xm = float(sx) / float(n)
                ym = float(sy) / float(n)
                varx = float(sx2) / float(n) - xm * xm
                vary = float(sy2) / float(n) - ym * ym

                if (varx <= 0.):
                # cas ou variance devrait etre == +epsilon
                    varx = 0.1
                if (vary <= 0.):
                    vary = 0.1

                et2x = self.FSIGMA * math.sqrt (varx)
                et2y = self.FSIGMA * math.sqrt (vary)
                seuilbx = xm - et2x
                seuilhx = xm + et2x
                seuilby = ym - et2y
                seuilhy = ym + et2y

                #  Elimination (set cib to 0)
                for j in range(parinf,parsup):
                    if (self.cib[j].get_y() > 0. and (self.cib[j].get_x() < seuilbx or self.cib[j].get_x() > seuilhx or self.cib[j].get_y() < seuilby or self.cib[j].get_y() > seuilhy)):
                        self.cib[j].set_x(0.)
                        self.cib[j].set_y(0.)

            # Recalcule moyennes
            # ------------------
            sx = sy = 0.
            n = 0
            for j in range(parinf,parsup):
                if (self.cib[j].get_y() > 0.):
                    sx = sx + self.cib[j].get_x()
                    sy = sy + self.cib[j].get_y()
                    n = n + 1

            # Reduit la liste des cibles
            if (n > 0):
                cibred_cour = Targets()
                cibred_cour.set(sx/n, sy/n, n)
                ncibr = len(self.cibred) - 1

                if (ncibr < 0 ):
                    ncibr = 0
                    self.cibred.append(cibred_cour)
                else:
                    # si les cibred[].x ne sont pas strictement croissants
                    # on ecrase  la cible ayant le poids le moins fort
                    if (cibred_cour.get_x() > self.cibred[ncibr].get_x()):
                        # 1 cibred en +  car t croissant
                        ncibr = ncibr + 1
                        self.cibred.append(cibred_cour)
                    else:
                        # t <= precedent
                        if (cibred_cour.get_p() > self.cibred[ncibr].get_p()):
                            # si p courant >, ecrase la precedente
                            self.cibred[ncibr].set(cibred_cour.get_x(),cibred_cour.get_y(),cibred_cour.get_p())
        # end For ip

    # End reduc
    # ------------------------------------------------------------------


    def reduc2(self):
        """ reduc2.
            2eme filtrage des cibles trop proches en t [et Hz]
        """
        # classe ordre temporel croissant les cibred
        c = momelutil.quicksortcib(self.cibred)
        self.cibred = c

        self.cibred2.append(self.cibred[0])
        pnred2 = 0
        assert(self.seuilrapp_y > 0.)
        ncibr_brut = len(self.cibred)
        for i in range(1,ncibr_brut):
            delta_x = self.cibred[i].get_x() - self.cibred2[pnred2].get_x()
            if(float(delta_x) < float(self.seuildiff_x)):
                if ( math.fabs( float((self.cibred[i].get_y() - self.cibred2[pnred2].get_y()) ) / self.cibred2[pnred2].get_y())  < self.seuilrapp_y ):
                    self.cibred2[pnred2].set_x( (self.cibred2[pnred2].get_x() + self.cibred[i].get_x())/2. )
                    self.cibred2[pnred2].set_y( (self.cibred2[pnred2].get_y() + self.cibred[i].get_y())/2. )
                    self.cibred2[pnred2].set_p( (self.cibred2[pnred2].get_p() + self.cibred[i].get_p()) )
                else:
                    if (self.cibred2[pnred2].get_p() < self.cibred[i].get_p()):
                        self.cibred2[pnred2].set(self.cibred[i].get_x(),self.cibred[i].get_y(),self.cibred[i].get_p())
            else:
                pnred2 = pnred2 + 1
                self.cibred2.append( self.cibred[i] )

    # End reduc2
    # ------------------------------------------------------------------


    # ##################################################################### #
    # Borne
    # ##################################################################### #

    def borne(self):
        """ borne.
            Principes:
            calcul borne G (D)  si 1ere (derniere) cible est
            ( > (debut_voisement+halo) )
            ( < (fin_voisement -halo)  )
            ce pt de debut(fin) voisement  == frontiere
            cible extremite == ancre
            regression quadratique sur Hz de  [frontiere ancre]
        """
        halo = self.HALO_BORNE_TRAME
        ancre = Targets()
        borne = Targets()

        # Borne gauche
        # ------------

        # Recherche 1er voise
        premier_voise=0
        while(premier_voise < self.nval and self.hzptr[premier_voise] < self.SEUILV):
            premier_voise = premier_voise + 1

        if( int(self.cibred2[0].get_x()) > (premier_voise + halo) ):
            # origine des t : ancre.x, et des y : ancre.y
            ancre = self.cibred2[0]

            sx2y = 0.
            sx4  = 0.

            j = 0
            for i in range( int(ancre.get_x()),0):
                if (self.hzptr[i] > self.SEUILV):
                    x2 = float(j)*float(j)
                    sx2y = sx2y + (x2* (self.hzptr[i] - ancre.get_y()))
                    sx4 = sx4 + (x2*x2)
                j = j + 1

            frontiere = float(premier_voise)
            a = 0.
            if sx4 > 0.:
                a = sx2y / sx4

            borne.set_x( frontiere - (ancre.get_x() - frontiere ) )
            borne.set_y( ancre.get_y() + (2 * a * (ancre.get_x() - frontiere)*(ancre.get_x() - frontiere)) )

        # recherche dernier voisement
        dernier_voise = self.nval - 1
        while ( dernier_voise >=0 and self.hzptr[dernier_voise] < self.SEUILV):
            dernier_voise = dernier_voise - 1


        # ################################################################## #

        #nred2 = len(self.cibred2)
        #if( int(self.cibred2[nred2-1].get_x()) < (dernier_voise - halo)):
            # origine des t : ancre.x, et des y : ancre.y
            #ancre = self.cibred2[nred2-1]

            #sx2y = 0.
            #sx4 = 0.
            #j = 0
            #for i in range( int(ancre.get_x()),self.nval):
                #if (self.hzptr[i] > self.SEUILV):
                    #x2 = float(j) * float(j)
                    #sx2y = sx2y + (x2 * (self.hzptr[i] - ancre.get_y()))
                    #sx4 = sx4 + (x2*x2)
                #j = j + 1
            #frontiere = float(dernier_voise)
            #a = 0.
            #if (sx4 > 0.):
                #a = sx2y / sx4

            #borne.set_x( frontiere + (frontiere - ancre.get_x()) )
            #borne.set_y( ancre.get_y() + (2. * a * (ancre.get_x() - frontiere)*(ancre.get_x() - frontiere)) )

    # End borne
    # ------------------------------------------------------------------


    def run_momel(self, pitchvalues):
        """ Apply momel from a vector of pitch values, one each 0.01sec.
            Write result in a text file and/or a TextGrid file.
            Parameters:
                pitch is the list of pitch values
            Return:      A list of targets
            Exceptions:  Exception
        """
        # Get pitch values
        self.initialize()
        self.set_pitch_array( pitchvalues )

        if (self.ELIM_GLITCH==True):
            self.elim_glitch()

        try:
            self.cible()
        except Exception as e:
            raise Exception("Momel.Cible.\n"+str(e))

        try:
            self.reduc()
        except Exception as e:
            raise Exception("Momel.Reduc.\n"+str(e))
        else:
            self.reduc2()
            if (len(self.cibred2))==0:
                raise Exception("Momel.reduc2.\n"+str(e))

        try:
            self.borne()
        except Exception as e:
            raise Exception("Momel::Borne.\n"+str(e))

        return self.cibred2

    # End run
    # ------------------------------------------------------------------



class sppasMomel( Momel ):
    """ SPPAS inplementation of Momel.
    """

    def __init__(self, logfile=None):
        Momel.__init__(self)
        self.PAS_TRAME = 10.
        self.logfile = logfile

    # End __init__
    # ------------------------------------------------------------------


    def set_pitch(self, inputfilename):
        """ Take pitch values from a file.
            Return:      A list of pitch values (one value each 10 ms).
            Exceptions;  Exception
        """
        try:
            pitch = annotationdata.io.read( inputfilename )
            pitchlist = pitch.get_pitch_list()
            if len(pitchlist)==0:
                raise IOError('sppasMomel::Pitch. Error while reading '+inputfilename+'\nEmpty pitch tier.\n')
            return pitchlist
        except Exception as e:
            raise IOError('sppasMomel::Pitch. Error while reading '+inputfilename+'\n'+str(e)+'\n')
    # End set_pitch
    # ------------------------------------------------------------------

    def __print_tgts(self, targets, output):
        for i in range(len(targets)):
            output.write( str( "%g"%(targets[i].get_x() * self.PAS_TRAME) ) )
            output.write( " " )
            output.write( str( "%g"%targets[i].get_y() ) )
            output.write( "\n" )

    def print_targets(self, targets, outputfile=None, trs=None):
        """ Print the set of selected targets.
            Return:      None
        """
        if outputfile is not None:
            if outputfile is "STDOUT":
                output=sys.stdout
                self.__print_tgts(targets, output)
            elif outputfile.lower().endswith('momel') is True:
                output = open(outputfile,"w")
                self.__print_tgts(targets, output)
                output.close()

        if trs is not None:
            # Attention: time in targets is in milliseconds!
            tier = trs.NewTier(name="Momel")
            for i in range(len(targets)):
                try:
                    _time  = targets[i].get_x() * (0.001*self.PAS_TRAME)
                    _label = str("%d"%(targets[i].get_y()))
                    tier.Append(Annotation(TimePoint(_time), Label(_label)))
                except Exception as e:
                    if self.logfile is not None:
                        self.logfile.print_message("Ignore target: time="+str(_time)+" and value="+_label, indent=2,status=3)

            if outputfile is not None and outputfile.lower().endswith('.pitchtier'):
                trsp=Transcription()
                trsp.Add(tier)
                try:
                    annotationdata.io.write(outputfile, trsp)
                except Exception as e:
                    if self.logfile is not None:
                        self.logfile.print_message("Can't write PitchTier output file.",status=-1)
            return tier

    # End print_targets
    # ------------------------------------------------------------------


    def fix_options(self, options):
        for opt in options:
            if "lfen1" == opt.get_key():
                self.set_option_win1( opt.get_value() )
            elif "hzinf" == opt.get_key():
                self.set_option_lo( opt.get_value() )
            elif "hzsup" == opt.get_key():
                self.set_option_hi( opt.get_value() )
            elif "maxec" == opt.get_key():
                self.set_option_maxerr( opt.get_value() )
            elif "lfen2" == opt.get_key():
                self.set_option_win2( opt.get_value() )
            elif "seuildiff_x" == opt.get_key():
                self.set_option_mind( opt.get_value() )
            elif "seuildiff_y" == opt.get_key():
                self.set_option_minr( opt.get_value() )
            elif "glitch" == opt.get_key():
                self.set_option_elim_glitch( opt.get_value() )


    def run(self, inputfilename, trsoutput=None, outputfile=None):
        """ Apply momel and intsint (if any) from a pitch file.
            Write result in a text file and/or a TextGrid file.
            Parameters:
                - inputfilename
                - trsoutput
                - outputfile
            Return:      None
        """
        # Get pitch values from the input
        pitch = self.set_pitch( inputfilename )
        # Selected values (Target points) for this set of pitch values
        targets = []

        # List of pitch values of one **estimated** Inter-Pausal-Unit (ipu)
        ipupitch = []
        # Number of consecutive null F0 values
        nbzero  = 0
        # Current time value
        curtime = 0
        # For each f0 value of the wav file
        for p in pitch:
            if p == 0:
                nbzero += 1
            else:
                nbzero = 0
            ipupitch.append( p )

            # If the number of null values exceed 300ms,
            # we consider this is a silence and estimate Momel
            # on the recorded list of pitch values of the **estimated** IPU.
            if (nbzero*self.PAS_TRAME) > 299:
                if len(ipupitch)>0 and ( len(ipupitch) > nbzero):
                    # Estimates the real start time of the IPU
                    ipustarttime = curtime - ( len(ipupitch) ) + 1
                    try:
                        # It is supposed ipupitch starts at time = 0.
                        iputargets = self.run_momel( ipupitch )
                    except Exception as e:
                        if self.logfile is not None:
                            self.logfile.print_message('No Momel annotation between time '+ str(ipustarttime*0.01) +" and "+ str(curtime*0.01)+" due to the following error: " +str(e),indent=2,status=-1)
                        else:
                            print "Momel Error: " + str(e)
                        iputargets = []
                        pass
                    # Adjust time values in the targets
                    for i in range( len(iputargets) ):
                        x = iputargets[i].get_x()
                        iputargets[i].set_x( ipustarttime + x )
                    # add this targets to the targets list
                    targets = targets + iputargets
                    del ipupitch[:]

            curtime += 1

        # last ipu
        if len(ipupitch)>0 and ( len(ipupitch) > nbzero):
            try:
                iputargets = self.run_momel( ipupitch )
            except Exception as e:
                if self.logfile is not None:
                    self.logfile.print_message('No Momel annotation between time '+ str(ipustarttime*0.01) +" and "+ str(curtime*0.01)+" due to the following error: " +str(e),indent=2,status=-1)
                else:
                    print "error: " + str(e)
                    iputargets = []
                pass
            ipustarttime = curtime - ( len(ipupitch) )
            # Adjust time values
            for i in range( len(iputargets) ):
                x = iputargets[i].get_x()
                iputargets[i].set_x(ipustarttime + x)
            targets = targets + iputargets


        # Print results and/or estimate INTSINT (if any)
        try:
            if trsoutput:
                trsm = Transcription("TrsMomel")
                if outputfile:
                    momeltier = self.print_targets(targets, outputfile, trs=trsm)
                else:
                    momeltier = self.print_targets(targets, outputfile=None, trs=trsm)
                if self.logfile is not None:
                    self.logfile.print_message(str(len(targets))+ " targets found.",indent=2,status=3)

                momeltier.SetRadius(0.005) # because one pitch estimation each 10ms...

                try:
                    try:
                        intsint = Intsint( momeltier )
                        intsinttier = intsint.run()
                        intsinttier.SetRadius(0.005) # BECAUSE IT WAS LOST BY INTSINT!!!!!!
                        trsm.Add( intsinttier )
                        trsm._hierarchy.addLink("TimeAssociation", momeltier, intsinttier)
                    except Exception as e:
                        if self.logfile is not None:
                            self.logfile.print_message("Problem with INTSINT: "+str(e),indent=2,status=-1)
                        else:
                            sys.stderr.write("INTSINT ERROR\n")
                            sys.stderr.write(str(e))
                        pass
                    annotationdata.io.write( trsoutput, trsm )
                except Exception as e:
                    if self.logfile is not None:
                        self.logfile.print_message("Failed to save: %s"%str(e),indent=2,status=-1)
                    else:
                        sys.stderr.write("sppasMomel::Print error.\n")
                    pass
            elif outputfile:
                self.print_targets(targets, outputfile, trs=None)
            else:
                self.print_targets(targets, outputfile='STDOUT', trs=None)
        except Exception as e:
            raise Exception("Momel::Print targets. Error: "+str(e))

    # End run
    # ------------------------------------------------------------------

