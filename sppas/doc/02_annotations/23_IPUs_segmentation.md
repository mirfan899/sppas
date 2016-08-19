## Inter-Pausal Units (IPUs) segmentation

After recording, the first annotation to perform is IPUs segmentation. Indeed,
at a first stage, the audio signal must be automatically segmented in 
Inter-Pausal Units (IPUs) which are blocks of speech bounded by silent pauses
of more than X ms. This X duration depends on the language and it is commonly
set to 200ms for French and 250ms for English. IPUs are time-aligned on the 
speech signal. This segmentation should be verified manually, depending on the
quality of the recording: the better quality, thus the better IPUs segmentation.

The "IPUs segmentation" automatic annotation can perform 3 actions:

1. find silence/speech segmentation of a recorded file,
2. find silence/speech segmentation of a recorded file including 
   the time-alignment of utterances of a transcription file, 
3. split/save a recorded file into multiple files, depending on segments 
   indicated in a time-aligned file.

![IPU Segmentation workflow](./etc/figures/segmworkflow.bmp)


### Silence/Speech segmentation

The IPUs Segmentation annotation performs a silence detection from a
recorded file. This segmentation provides an annotated file with one tier 
named "IPU". The silence intervals are labelled with the "#" symbol, 
as speech intervals are labelled with "ipu_" followed by the IPU number.   

The following parameters must be fixed:

* Minimum volume value (in seconds):  
If this value is set to zero, the minimum volume is automatically adjusted 
for each sound file. Try with it first, then if the automatic value is not 
correct, fix it manually. The Procedure Outcome Report indicates the value
the system choose. The SndRoamer component can also be of great help: it
indicates min, max and mean volume values of the sound.

* Minimum silence duration (in seconds):
By default, this is fixed to 0.2 sec., an appropriate value for French.
This value should be at least 0.25 sec. for English.

* Minimum speech duration (in seconds):
By default, this value is fixed to 0.3 sec. The most relevent value depends on
the speech style: for isolated sentences, probably 0.5 sec should be better,
but it should be about 0.1 sec for spontaneous speech.

* Speech boundary shift (in seconds): a duration which is systematically added
to speech boundaries, to enlarge the speech interval.
 
The procedure outcome report indicates the values (volume, minimum durations)
that was used by the system for each sound file given as input. It also mentions
the name of the output file (the resulting file). The file format can be fixed
in the Settings of SPPAS (xra, TextGrid, eaf, ...).

![Procedure outcome report of IPUs Segmentation](./etc/screenshots/ipu-seg-log.png)

The annotated file can be checked manually (preferably in Praat than Elan nor Anvil).
If such values was not correct, then, delete the annotated file that was 
previously created, change the default values and re-annotate.

![Result of IPUs Segmentation: silence detection](./etc/screenshots/ipu-seg-result1.png)

Notice that the speech segments can be transcribed using the "IPUScribe" component.

![Orthographic transcription based on IPUs Segmentation](./etc/screenshots/IPUscribe-2.png)


### Silence/Speech segmentation time-aligned with a transcription

Inter-Pausal Units segmentation can also consist in aligning macro-units of a 
document with the corresponding sound.

SPPAS identifies silent pauses in the signal and attempts to align them with
the inter-pausal units proposed in the transcription file, under the assumption
that each such unit is separated by a silent pause.
This algorithm is language-independent: it can work on any language.

In the transcription file, **silent pauses must be indicated** using both 
solutions, which can be combined: 

* with the symbol '#',
* with newlines.

A recorded speech file must strictly correspond to a transcription, except
for the extension expected as .txt for this latter.
The segmentation provides an annotated file with one tier named "IPU". 
The silence intervals are labelled with the "#" symbol, 
as speech intervals are labelled with "ipu_" followed by the IPU number
then the corresponding transcription.

The same parameters than those indicated in the previous section must be fixed.

    Important: 
    This segmentation was tested on documents no longer than one paragraph 
    (about 1 minute speech). 

![Silence/Speech segmentation with orthographic transcription](./etc/screenshots/ipu-seg-result2.png)


### Split into multiple files 

IPU segmentation can split the sound into multiple files (one per IPU), and it
creates a text file for each of the tracks. The output file names are
"track_0001", "track_0002", etc.

Optionally, if the input annotated file contains a tier named exactly "Name", 
then the content of this tier will be used to fix output file names.

![Data to split](./etc/screenshots/ipu-seg-result3.png)

In the example above, the automatic process will create 6 files: 
FLIGTH.wav, FLIGHT.txt, MOVIES.wav, MOVIES.txt, SLEEP.wav and SLEEP.txt.
It is up to the user to perform another IPU segmentation of these files
to get another file format than txt (xra, TextGrid, ...) thanks to the
previous section "Silence/Speech segmentation time-aligned with a transcription".

![Data split](./etc/screenshots/ipu-seg-result3-files.png)
