## Inter-Pausal Units (IPUs) segmentation

### Overview

After recording, the first annotation to perform is IPUs segmentation. 
At the early first stage, the Inter-Pausal Units (IPUs) must be automatically
detected in the audio signal. IPUs are blocks of speech bounded by silent 
pauses of more than X ms. An annotated file with the bounds of IPUs is then
created. This segmentation should be verified manually: the better recording
quality, thus the better IPUs segmentation.

The "IPUs segmentation" automatic annotation can perform 3 actions:

1. find silences/ipus of a recorded file.
2. find silences/ipus of a recorded file when the utterances are given in a `txt` file.
3. split/save a recorded file into multiple files, depending on segments
   indicated in a time-aligned file.

![IPU Segmentation workflow](etc/figures/segmworkflow.bmp)

>Notice that all time values are indicated in seconds.

### Silence/Speech segmentation

The IPUs Segmentation is a semi-automatic annotation process. It performs a 
silence detection from a recorded file. This segmentation provides an annotated 
file with one tier named "IPU". The silence intervals are labelled with the 
"#" symbol, and IPUs intervals are labelled with "ipu_" followed by the IPU 
number.

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
systematically added to ipus boundaries, to enlarge the ipus interval,
and as a consequence, the neighboring silences are reduced.

The following options are also available to configure the annotation:
* Add the IPU index in each interval of the Transcription tier
* Split the audio file into tracks (only if silence/ipus segmentation is already available)
* Save tracks as annotation files  (only if silence/ipus segmentation is already available)

The procedure outcome report indicates the values (volume, minimum durations)
that was used by the system for each sound file given as input. It also mentions
the name of the result file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 ... IPUs Segmentation of file oriana1.wav
 ...  ... [   INFO   ] A transcription was found, perform Silence/Speech segmentation 
 time-aligned with a transcription oriana1.txt
 ...  ... Options: 
 ...  ...  ...  - save_as_trs: False
 ...  ...  ...  - dirtracks: False
 ...  ...  ...  - addipuidx: True
 ...  ... Diagnostic: 
 ...  ...  ...  - oriana1.wav: Valide. 
 ...  ...  ... Threshold volume value:     122
 ...  ...  ... Threshold silence duration: 0.3
 ...  ...  ... Threshold speech duration:  0.5
 ...  ... [    OK    ] oriana1.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The resulting annotated file has to be checked manually. 
It can be viewed with the SPPAS Visualizer tool, or it can be viewed/revised with Praat. 

If the option values were not relevant enough: delete the annotated file that was
previously created, change such values and re-annotate.

![Result of IPUs Segmentation: silence detection](etc/screenshots/ipu-seg-result1.png)

Notice that the speech segments can be transcribed using the SPPAS "IPUScriber" tool.

![Orthographic transcription based on IPUs Segmentation](etc/screenshots/IPUscribe-2.png)


### Silence/Speech segmentation time-aligned with a transcription

Inter-Pausal Units segmentation can also consist in aligning macro-units of a
document with the corresponding sound.

SPPAS identifies silent pauses in the signal and attempts to align them with
the utterances proposed in the transcription file, under the assumption
that each such unit is separated by a silent pause.
This algorithm is language-independent: it can work on any language.

In the transcription file, **silent pauses must be indicated** using both
solutions, which can be combined:

* with the symbol '#'
* with newlines.

A recorded speech file must strictly correspond to a `txt` file of the transcription.
The segmentation provides an annotated file with one tier named "IPU".
The silence intervals are labelled with the "#" symbol,
as ipus intervals are labelled with "ipu_" followed by the IPU number
then the corresponding transcription.

The same parameters than those indicated in the previous section must be fixed.

> Important:
> This segmentation was tested on documents no longer than one paragraph
> (about 1 minute speech).

![Silence/Speech segmentation with orthographic transcription](etc/screenshots/ipu-seg-result2.png)


### Split into multiple files

IPUs segmentation can split the sound into multiple files (one per IPU), and it
creates a text file for each of the tracks. By default, the names of the output
files are "track_0001", "track_0002", etc.
Optionally, if the input annotated file contains a tier with name exactly "Name",
then the content of this tier will be used to fix output file names.

![Data to split](etc/screenshots/ipu-seg-result3.png)

In the example above, the automatic process will create 6 files:
FLIGTH.wav, FLIGHT.txt, MOVIES.wav, MOVIES.txt, SLEEP.wav and SLEEP.txt.
It is up to the user to perform another IPUs segmentation of these files
to get another file format than txt (xra, TextGrid, ...). Refer to the
previous section "Silence/Speech segmentation time-aligned with a transcription".

![Data split](etc/screenshots/ipu-seg-result3-files.png)


### Perform IPUs Segmentation with the GUI

Click on the IPUs Segmentation activation button and on the "Configure..." blue
text to fix options.


### Perform IPUs Segmentation with the CLI

`wavsplit.py` is the program to perform the IPUs segmentation, i.e.
silence/ipus segmentation.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: wavsplit.py -w file [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generic options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -w file		    audio input file name
    -d delta shift	Add this time value to each start
                    bound of the IPUs
    -D delta shift	Add this time value to each end
                    bound of the IPUs
    -h, --help      Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options that can be fixed for the silence/ipus segmentation:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -r float 	Window size to estimate rms, in seconds
                (default value is: 0.010)
    -m value 	Drop speech shorter than m seconds long
                (default value is: 0.300)
    -s value 	Drop silences shorter than s seconds long
                (default value is: 0.200)
    -v value 	Assume that a rms lower than v is a silence
                (default value is: 0 which means to auto-adjust)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options that can be fixed for the silence/ipus segmentation with
a given orthographic transcription. It must be choose one of -t or -n options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -t file 	Input transcription file (default: None)
    -n value 	Input transcription tier number (default: None)
    -N 		    Adjust the volume cap until it splits
                into nb tracks (default: 0=automatic)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Output options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -o dir		Output directory name       (default: None)
    -e ext		Output tracks extension     (default: txt)
    -p file		File with the segmentation  (default: None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of use to get each IPU in a separate wav file and 
its corresponding transcription in a textgrid file:

Step1: find silences/ipus
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/wavsplit.py -w ./samples/samples-eng/oriana1.wav
-d 0.01
-D 0.01
-t ./samples/samples-eng/oriana1.txt
-p ./samples/samples-eng/oriana1.xra
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Step2: split ipus into individual tracks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
./sppas/bin/wavsplit.py -w ./samples/samples-eng/oriana1.wav
-t ./samples/samples-eng/oriana1.xra
-o ./samples/samples-eng/oriana1
-e textgrid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
