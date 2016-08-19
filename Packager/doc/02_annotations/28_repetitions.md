## Repetitions

This automatic detection focus on word repetitions, which can be an exact 
repetition (named strict echo) or a repetition with variation 
(named non-strict echo).

SPPAS implements *self-repetitions* and *other-repetitions* detection (Bigi
et al. 2014). The system is based only on lexical criteria. 
The proposed algorithm is focusing on the detection of the source. 

The Graphical User Interface only allows to detect self-repetitions.
Use the Command-Line User Interface if you want to get other-repetitions.

![Repetition detection workflow](./etc/figures/repetworkflow.bmp)

The automatic annotation takes as input a file with (at least) one 
tier containing the time-aligned tokens of the speaker (and another file/tier
for other-repetitions).
The annotation provides one annotated file with 2 tiers: Sources and Repetitions.

This process requires a list of stop-words, and a dictionary with lemmas (the
system can process without it, but the result is better with it). Both lexicons
are located in the "vocab" sub-directory of the "resources" directory.
