## Fill in Inter-Pausal Units (IPUs)

### Overview

This automatic annotation consists in aligning macro-units of a
document with the corresponding sound.

IPUs are blocks of speech bounded by silent pauses of more than X ms.
This annotation searches for a silences/IPUs segmentation of
a recorded file (see previous section) and fill in the IPUs with the 
transcription given in a `txt` file.

### How does it work

SPPAS identifies silent pauses in the signal and attempts to align them with
the units proposed in the transcription file, under the assumption
that each such unit is separated by a silent pause. It is based on the
search of silences described in the previous section, but in this 
case, the number of units to find is known. The system adjusts automatically
the volume threshold and the minimum durations of silences/IPUs to
get the right number of units. The content of the units has no regard, 
because SPPAS does not interpret them: it can be the orthographic 
transcription, a translation, numbers, ...
This algorithm is language-independent: it can work on any language.

In the transcription file, **silent pauses must be indicated** using both
solutions, which can be combined:

* with the symbol '#';
* with newlines.

A recorded speech file must strictly correspond to a `txt` file of the 
transcription. The annotation provides an annotated file with one tier
named "Transcription". The silence intervals are labelled with the "#" symbol,
as IPUs are labelled with "ipu_" followed by the IPU number then the 
corresponding transcription.

The same parameters than those indicated in the previous section must be fixed.

> Remark:
> This annotation was tested on read speech no longer than a few sentences
> (about 1 minute speech) and on recordings of very good quality.

![Fill in IPUs](etc/screenshots/ipu-seg-result2.png)


### Perform "Fill in IPUs" with the GUI

Click on the "Fill in IPUs" activation button and on the "Configure..." blue
text to fix options.


### Perform "Fill in IPUs" with the CLI

`fillipus.py` is the program to perform the IPUs segmentation, i.e.
silence/ipus segmentation.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: fillipus.py -w file [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generic options:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -w file		    audio input file name
    -t file         input transcription file name
    -h, --help      Show the help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Options that can be fixed for the silence/ipus segmentation:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    -m value 	Initial value to drop speech shorter 
                than m seconds long
                (default value is: 0.300)
    -s value 	Initial value to drop silences shorter 
                than s seconds long
                (default value is: 0.200)
    -o file		File with the segmentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
