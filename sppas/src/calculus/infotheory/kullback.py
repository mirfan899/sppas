#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /        Automatic
#           \__   |__/  |__/  |___| \__      Annotation
#              \  |     |     |   |    \     of
#           ___/  |     |     |   | ___/     Speech
#           =============================
#
#           http://sldr.org/sldr000800/preview/
#
# ---------------------------------------------------------------------------
# developed at:
#
#       Laboratoire Parole et Langage
#
#       Copyright (C) 2011-2015  Brigitte Bigi
#
#       Use of this software is governed by the GPL, v3
#       This banner notice must not be removed
# ---------------------------------------------------------------------------
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
# File: kullback.py
# ----------------------------------------------------------------------------

import math

from utilit import log2
from utilit import MAX_NGRAM
from utilit import symbols_to_items

# ----------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi (brigitte.bigi@gmail.com)"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------

EPSILON = 0.000001

# ----------------------------------------------------------------------------
# Class Kullback
# ----------------------------------------------------------------------------

class Kullback:
    """
    @authors: Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL, v3
    @summary: Kullback-Leibler distance estimation.

    In probability theory and information theory, the Kullback–Leibler
    divergence (also called relative entropy) is a measure of the difference
    between two probability distributions P and Q. It is not symmetric in P
    and Q.
    Specifically, the Kullback–Leibler divergence of Q from P, denoted DKL(P‖Q),
    is a measure of the information gained when one revises ones beliefs from
    the prior probability distribution Q to the posterior probability
    distribution P.

    However, the Kullback class estimates the KL diatance, i.e. the
    symmetric Kullback-Leibler divergence.

    This Kullback class implements the Kullback-Leibler distance estimation
    between a model and a moving window on data, as described in:

    Brigitte Bigi, Renato De Mori, Marc El-Bèze, Thierry Spriet (1997).
    Combined models for topic spotting and topic-dependent language modeling
    IEEE Workshop on Automatic Speech Recognition and Understanding Proceedings
    (ASRU), Edited by S. Furui, B. H. Huang and Wu Chu, IEEE Signal Processing
    Society Publ, NY, pages 535-542.

    This KL distance can also be used to estimate the distance between
    documents for text categorization, as proposed in:

    Brigitte Bigi (2003).
    Using Kullback-Leibler Distance for Text Categorization.
    Lecture Notes in Computer Science, Advances in Information Retrieval,
    ISSN 0302-9743, Fabrizio Sebastiani (Editor), Springer-Verlag (Publisher), pages 305--319, Pisa (Italy).

    How to use Kullback class?

    We suppose model to be a dictionary with:
    - key is an ngram,
    - value is a probability.

    We suppose a window to be a list of ngrams.

    """

    def __init__(self, model=None, ngrams=None):
        """
        Create a Kullback instance with a list of symbols.

        @param model is a dictionary with key=ngram, value=probability

        """
        self.ngrams  = []
        self.model   = {}
        self.epsilon = EPSILON

        if model:  self.set_model(model)
        if ngrams: self.set_ngrams(ngrams)

    # -----------------------------------------------------------------------

    def set_model(self, model):
        """
        Set the model.

        @param model (dict) Probability distribution of the model.

        """
        if model is None or len(model)==0:
            raise ValueError('To estimate the Kullback-Leibler distance, the input model must contain at least one probability.')
        sump = sum(model.values())
        if round(sump,6) != 1.:
            raise ValueError('To estimate the Kullback-Leibler distance, the input model must contain probabilities (must sum to one).')

        self.model = model

    # -----------------------------------------------------------------------

    def set_model_from_data(self, data):
        """
        Set the model from a given set of observations.

        @param data (list) List of observed ngrams.

        """
        if data is None or len(data)==0:
            raise ValueError('To estimate the Kullback-Leibler distance, the input data must contain at least one observation.')

        model = {}
        for obs in data:
            if not obs in model:
                model[obs] = data.count(obs)
        n = float(len(data))
        for obs in model:
            model[obs] = float(model[obs]) / n

        self.model = model

    # -----------------------------------------------------------------------

    def set_ngrams(self, ngrams):
        """
        Fix the set of observed ngrams.

        @param ngrams (list) The list of observed ngrams in a document.

        """
        if ngrams is None or len(ngrams)==0:
            raise ValueError('To estimate the Kullback-Leibler distance, the input data must contain at least one observation.')
        self.ngrams = ngrams

    # -----------------------------------------------------------------------


    def set_epsilon(self, eps):
        """
        Fix the linear back-off value for unknown ngrams.
        The optimal value for this coefficient is the product of the size
        of both model and ngrams to estimate the KL.

        """
        if eps < 0. or eps > 1.:
            raise ValueError('the linear back-off value for unknown ngrams is expected to be a probability.')
        self.epsilon = eps

    # -----------------------------------------------------------------------

    def __distance(self):
        """
        Kullback-Leibler Distance between the model and an observation.
        We expect a model, an observation, epsilon, alpha and beta
        already estimated properly.

        """
        dist = 0.

        # Estimates the distance using each of the ngrams
        for x in self.ngrams:
            probamodel = self.epsilon
            if x in self.model:
                probamodel = self.alpha * self.model[x]
            probangram = self.beta * (float(self.ngrams.count(x))/float(len(self.ngrams)))
            d = ( (probamodel-probangram) * log2(probamodel/probangram) )
            #print "   - ",x,": probangram=",probangram," probamodel=",probamodel, " d=",d
            dist += d
        # Estimates the distance using ngrams in the model
        for x in self.model:
            if not x in self.ngrams:
                probamodel = self.alpha * self.model[x]
                dist += ( (probamodel-self.epsilon) * log2(probamodel/self.epsilon) )

        return dist

    # -----------------------------------------------------------------------

    def __distance_emptyobservation(self):
        """
        Distance between model and an empty observation.
        We expect a model, epsilon and beta already estimated properly.

        """
        dist = 0.
        for x in self.ngrams:
            probangram = self.beta * (float(self.ngrams.count(x))/float(len(self.ngrams)))
            dist += ( (self.epsilon-probangram) * log2(self.epsilon/probangram) )
        return dist

    # -----------------------------------------------------------------------

    def __distance_emptymodel(self):
        """
        Distance between an empty model and an observation.
        We expect an observation, epsilon and alpha already estimated properly.

        """
        dist = 0.
        for x in self.model:
            probamodel = self.alpha * self.model[x]
            dist += ( (probamodel) * log2(self.epsilon/self.epsilon) )
        return dist

    # -----------------------------------------------------------------------

    def get(self):
        """
        Estimates the Kullback-Leibler distance between a model and an observation.

        @return float value

        """
        if self.model is None:
            raise Exception('A probability model must be fixed to estimate the distance.')
        if self.ngrams is None:
            raise Exception('A list of observed ngrams must be fixed to estimate the distance.')

        na = 0
        nb = 0
        for x in self.ngrams:
            if x in self.model:
                nb = nb + 1
            else:
                na = na + 1
        self.alpha = 1. - (na*self.epsilon) # coeff applied to the model
        self.beta  = 1. - (nb*self.epsilon) # coeff applied to the observed ngrams

        dist = self.__distance()

        return dist

    # -----------------------------------------------------------------------

if __name__ == "__main__":

    print "Test 1:"
    print "-------"

    data = list('00000011000101010000100101000101000001000100000001100000')
    kl = Kullback( )
    kl.set_epsilon( 1.0 / (10.*len(data)))
    kl.set_model_from_data(data)

    print "The model:"
    for k,v in kl.model.items():
        print "  --> P(",k,") =",v

    observation=list('000')
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get()

    observation=list('010')
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    observation=list('011')
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    observation=list('111')
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )


    print
    print "Test 2:"
    print "-------"

    model = {}
    model[(0,0)] = 0.80
    model[(0,1)] = 0.08
    model[(1,0)] = 0.08
    model[(1,1)] = 0.04

    print "The model:"
    for k,v in model.items():
        print "  --> P(",k,") =",v

    kl = Kullback( model )
    kl.set_epsilon( 1.0 / 1000.)

    observation = []

    observation.append( (0,0) )
    observation.append( (0,0) )
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    observation.pop(0)
    observation.append((0,1))
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    observation.pop(0)
    observation.append((0,1))
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    observation.pop(0)
    observation.append((1,1))
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    observation.pop(0)
    observation.append((1,1))
    print "With the observation: ",observation
    kl.set_ngrams(observation)
    print "KL Dist = ",kl.get( )

    # --------
