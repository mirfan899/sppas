## Repetitions

### Overview

This automatic detection focus on word repetitions, which can be an exact
repetition (named strict echo) or a repetition with variation
(named non-strict echo).

SPPAS implements *self-repetitions* and *other-repetitions* detection (Bigi
et al. 2014). The system is based only on lexical criteria.
The proposed algorithm is focusing on the detection of the source.

The Graphical User Interface only allows to detect self-repetitions.
Use the Command-Line User Interface if you want to get other-repetitions.

This process requires a list of stop-words, and a dictionary with lemmas (the
system can process without it, but the result is better with it). Both lexicons
are located in the "vocab" folder of the "resources" directory.

### Perform Repetitions with the GUI

The automatic annotation takes as input a file with (at least) one
tier containing the time-aligned tokens of the speaker (and another file/tier
for other-repetitions).
The annotation provides one annotated file with 2 tiers: Sources and Repetitions.

![Repetition detection workflow](./etc/figures/repetworkflow.bmp)

Click on the Self-Repetitions activation button, select the language and click
on the "Configure..." blue text to fix options.

### Perform Repetitions with the CLI

`repetition.py` is the program to perform automatic detection of
self-repetitions or other-repetitions if a second speaker is given.

It can be language-dependent (better results) or language-independent.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: repetition.py -i file [options]

optional arguments:
  -h, --help  show this help message and exit
  -i file     Input file name with time-aligned tokens of the self-speaker
  -r folder   Directory with resources
  -l lang     Language code in iso639-3
  -I file     Input file name with time-aligned tokens of the echoing-speaker
              (if ORs)
  -o file     Output file name
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

