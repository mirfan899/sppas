## The early versions

Versions 1.0 to 1.3 was made only of `tcsh` and `gawk` scripts. 
It was developed under Linux system and was efficiently tested 
under Windows with Cygwin.


### Version 1.0 (2011, 9th March)

The only feature was that it was able to perform speech segmentation 
of English read speech.


### Version 1.1 (2011, 7th June)

This was mainly the debug of the previous version and some code
re-organization and cleaning.


### Version 1.2 (2011, 23th July)

The support of English, French and Italian was added: a lexicon,
a pronunciation dictionary and an acoustic model of each language
was created. Three annotations were implemented: Tokenization, 
Phonetization, Alignment.
The basis for a *multi-lingual methodology* was then already there. 


### Version 1.3 (2011, 12th December)

This is a transitional version, from the scripts language to Python
programming language. The main fixes and improvements were:

Development:
    
- MacOS support
- bugs corrected in many scripts
- check.csh -> check.py
- sppas.csh -> sppas.py
- GUI: zenity ->  pyGtk
- sox limited to the use of re-sampling audio signal
- a python library to manage wav files is added.
- IPUs segmentation automatic annotation

Resources:
    
- Italian dictionary improved
- Italian acoustic model changed (triphones trained from map-task dialogues)
- French acoustic model changed

But the program still haven't a name and isn't distributed.
