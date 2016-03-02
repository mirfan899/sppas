##Other Programs

Some scripts are also available to be used with the Command-Line Interface.
They are located in the `scripts` sub-directory.

###Merge annotation files

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: trsmerge.py -i file -o file [options]

optional arguments:
  -h, --help  show this help message and exit
  -i file     Input annotated file name (as many as wanted)
  -o file     Output annotated file name
  --quiet     Disable the verbosity

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


###Convert annotation files

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: trsconvert.py -i file -o file [options]

optional arguments:
  -h, --help  show this help message and exit
  -i file     Input annotated file name
  -o file     Output annotated file name
  -t value    A tier number (use as many -t options as wanted). Positive or
              negative value: 1=first tier, -1=last tier.
  --quiet     Disable the verbosity
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


###Get information about a tier of an annotated file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: tierinfo.py -i file [options]

optional arguments:
  -h, --help  show this help message and exit
  -i file     Input annotated file file name
  -t value    Tier number (default: 1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



###extract.py

This script extract the channel chosen from the input file and
write it in an output file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: extract.py -w inputfile -o outputfile -c channel
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
   -h, --help      show this help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



###reformat.py

This script extract the channel chosen from input file and
write the result in an output file. It can be:

* change framerate (-r)
* change sample width (-s)
* multiply by a factor each frame (-m)
* bias each frame by a value (-b)

or any combination of such options.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: reformat.py -w inputfile -o outputfile [options] 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
	-h, --help      show this help message and exit
	-c 				Channel (default 1)
	-r 				Framerate
	-s				Sample width
	-m				Factor to multiply each frame
	-b				Value to bias each frame
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



###equalize.py

This script equalize the number of frames of each mono channel input files
and write the results in output files.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: equalize.py -w inputfile [inputfile]* 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
   -h, --help      show this help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



###channelsmixer.py

This script mix all channels from mono input files and
write the channel result in an output file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: channelsmixer.py -w input_file [inputfile]* -o outputfile
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
   -h, --help      show this help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


###channelsmixersimulator.py

This script simulate a mix of all channels from input files and
print the maximum value of the result.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: channelsmixer.py -w input_file [inputfile]*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
   -h, --help      show this help message and exit
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


###fragmentextracter.py

This script extract a fragment from an audio file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: ./scripts/fragmentextracter.py -w inputfile -o outputfile [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
	-h, --help      show this help message and exit
	-bs				The position (in seconds) when begins the mix
	-bf				The position (in number of frames) when begins the mix
	-es				The position (in seconds) when ends the mix
	-ef				The position (in number of frames) when ends the mix
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of use:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: ./scripts/fragmentextracter.py -w audiofile.wav -o fragment.wav -bs 2 -es 4
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



###audiotoaster

This script performs a mix according to the settings given in parameter.
A factor permits to attenuate the separation between the two output channels
(the value is from 0 to 1).

Settings file must have the requered format:

* a header: **file speaker volume panoramic**
* a line by channel for example: **TRACK0_0.wav	HB	100	R100**

The programm will look for each file by the filename found on each line.
Audio files have to be in the same folder as the settings file.

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: ./scripts/audiotoaster.py -s settingfile -o outputfile [options]
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
optional arguments:
	-h, --help      show this help message and exit
	-l				Factor to attenuate the difference between the two output
                    channels. (default value : 0)
					x = 0 will perform two channels as asked in the settings
					0 < x < 1 will attenuate the difference
					x = 1 will perform two identical channels
	-b				The position (in seconds) when begins the mix
	-e				The position (in seconds) when ends the mix
	-v				Verbosity level: 0, 1 or 2 (default=1)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example of use:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
usage: ./scripts/audiotoaster.py -s ./samples/settings.txt -o mix.wav -l 0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
