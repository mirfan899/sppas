## Overview

Automatic annotations included in SPPAS are implemented with
language-independent algorithms. This means that adding a new language
into SPPAS only consists in adding resources related to the annotation
(like lexicons, dictionaries, models, set of rules, etc).

> All resources can be edited, modified, changed or deleted by users.

To know what the resources are for and other information, refer to 
chapter 3 of this documentation: Each resource is used by an 
automatic annotation.

The resources are language dependent and the name of the files are based on 
the ISO639-3 international standard. See <http://www-01.sil.org/iso639-3/> 
for the list of all languages and codes.

In the next sections, the table indicates the list of phonemes that are 
included in the resources required for phonetization, alignment and 
syllabification of a given language. The first column represents the symbols
used by SPPAS and the other columns are intended to help users to better
understand what it means.

The encoding of phonemes in SPPAS resources is based on a computer-readable
phonetic list of 7-bit printable ASCII characters: X-SAMPA. 
This Extended Speech Assessment Methods Phonetic Alphabet was developed in 
1995 by John C. Wells, professor of phonetics at the University of London.
X-SAMPA is a language-independent notation covering the entire 
International Phonetic Alphabet - IPA repertoire.
A plugin allows to convert time-aligned phonemes from X-SAMPA to IPA.

The acoustic models created by the author, Brigitte Bigi, were trained using
the HTK toolbox, version 3.4.1. 
"HTK has been developed by the Machine Intelligence Laboratory
(formerly know as the Speech Vision Robotics Group) at the
[Cambridge University Engineering Department](http://mi.eng.cam.ac.uk) (CUED)
and [Entropic Ltd](http://www.entropic.com).
Microsoft has now licensed HTK back to CUED and is providing support so 
that CUED can redistribute HTK and provide development support via the 
HTK3 web site." (source: <http://htk.eng.cam.ac.uk/>)
Notice that HTK is available for free download after registration and users 
must first agree to the license. Notice that the section 2.2 of the license 
terms mentions that HTK "either in whole or in part can not be distributed
or sub-licensed to any third party in any form."
