## Search for Inter-Pausal Units (IPUs)

### Overview

The Search for IPUs is a semi-automatic annotation process. It performs a 
silence detection from a recorded file. This segmentation provides an annotated 
file with one tier named "IPUs". The silence intervals are labelled with the 
"#" symbol, and IPUs intervals are labelled with "ipu_" followed by the IPU 
number. This annotation is semi-automatic: **it should be verified manually**.
Notice that the better recording quality, thus the better IPUs segmentation.

### How does it work

The following parameters must be properly fixed:

* Minimum volume value (in seconds):
If this value is set to zero, the minimum volume is automatically adjusted
for each sound file. Try with it first, then if the automatic value is not
correct, set it manually. The Procedure Outcome Report indicates the value
the system choose. The AudioRoamer component can also be of great help: it
indicates min, max and mean volume values of the sound.

* Minimum silence duration (in seconds):
By default, this is fixed to 0.2 sec. This duration mostly depends on the
language. It is commonly fixed to at least 0.2 sec for French and at least 
0.25 seconds for English language.

* Minimum speech duration (in seconds):
By default, this value is fixed to 0.3 sec. A relevant value depends on the 
speech style: for isolated sentences, probably 0.5 sec should be better,
but it should be about 0.1 sec for spontaneous speech.

* IPUs boundary shift (in seconds) for start or end: a duration which is 
systematically added to IPUs boundaries, to enlarge the IPUs interval,
and as a consequence, the neighboring silences are reduced.

The procedure outcome report indicates the values (volume, minimum durations)
that were used by the system for each sound file. 

### Perform "Search for IPUs" with the GUI

Click on the "Search IPUs" activation button and on the "Configure..." blue
text to fix options.

In case the option values were not relevant enough, it is possible to delete
the newly created file, to change such values and to re-annotate.

![Example of result](etc/screenshots/ipu-seg-result1.png)

Notice that the speech segments can be transcribed using the 
"IPUScriber" analysis tool.

![Orthographic transcription based on IPUs](etc/screenshots/IPUscribe-2.png)


### Perform "Search for IPUs" with the CLI

`searchipus.py` is the program to perform this semi-automatic annotation, i.e.
silence/IPUs segmentation.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: searchipus.py -w file [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -w file		    audio input file name
    -d delta shift	Add this time value to each start
                    bound of the IPUs
    -D delta shift	Add this time value to each end
                    bound of the IPUs
    -h, --help      Show the help message and exit
    -r float 	Window size to estimate rms, in seconds
                (default value is: 0.020)
    -m value 	Drop speech shorter than m seconds long
                (default value is: 0.300)
    -s value 	Drop silences shorter than s seconds long
                (default value is: 0.200)
    -v value 	Assume that a rms lower than v is a silence
                (default value is: 0 which means to auto-adjust)
    -o file		File with the segmentation 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
