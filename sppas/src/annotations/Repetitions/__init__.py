#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ######################################################################### #
#                                                                           #
# File:    __init__.py                                                      #
# Author:  Brigitte Bigi                                                    #
# Date:    2012-03-29                                                       #
# Brief:   SPPAS syllabification step                                       #
#                                                                           #
# Licence: GPL                                                              #
#   This file is part of SPPAS.                                             #
#                                                                           #
#   SPPAS is free software: you can redistribute it and/or modify           #
#   it under the terms of the GNU General Public License as published by    #
#   the Free Software Foundation, either version 3 of the License, or       #
#   any later version.                                                      #
#                                                                           #
#   SPPAS is distributed in the hope that it will be useful,                #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#   GNU General Public License for more details.                            #
#                                                                           #
#   You should have received a copy of the GNU General Public License       #
#   along with SPPAS.  If not, see <http://www.gnu.org/licenses/>.          #
#                                                                           #
# ######################################################################### #
""" This package deals with the syllabification annotation.

    The syllabification of phonemes is performed with a rule-based system.
    This RBS phoneme-to-syllable segmentation system is based on 2 main 
    principles:
        - a syllable contains a vowel, and only one.
        - a pause is a syllable boundary. 
    These two principles focus the problem of the task of finding a syllabic
    boundary between two vowels.
    As in state-of-the-art systems, phonemes were grouped into classes and 
    rules established to deal with these classes.
"""
# Fix the list of public classes
__all__ = ['syll', 'syllabification', 'rules']
