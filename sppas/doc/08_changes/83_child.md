## The childhood of SPPAS


### SPPAS 1.6.4 (2014, 5th December)

From this version, SPPAS requires wxpython to be updated to version 3.0, 
particularly for MacOS users, and they need to install the 64 bits version.
It is recommended to Windows users to install Python 2.7 and wxpython 
in 32bits.

Development:

- Package re-organized!
- Phonetization of unknown words improved
- Support of upper/lower of the extension of speech files (wav, WAV)
- Tokenization of languages with dictionaries in upper case (eng, ita): bug fixed.
- Creates systematically a dump file of resources for a faster load at the next use
- Read TextGrid files exported by Elan: bug fixed.
- `sppas.command` checks the system and run either in 32 or 64 bits (MacOS)

Components:

- IPUscribe replaces IPUTranscriber mainly for the support of large files:
tested with a file of 1 hour speech (143 Go) and 800 IPUs.
- SndRoamer replaces WavPlayer
- Dataroamer has also a new version


### SPPAS 1.6.5 (2014, 17th December)

This is primarily a bug-fix release.

Development:

- all programs in "bin" and "scripts" sub-directories were revised and
tested, or removed.

Annotation:

- Tokenization: code cleaning and re-organisation.

GUI:

- Procedure outcome report: print a warning message in the log file if no
file is matching the expected extension


### SPPAS 1.6.6 (2015, 19th January)

Web site host has changed: <http://sldr.org/sldr00800/preview/>

Documentation completed and updated. Now, only the documentation of all the
components is missing.

Annotations:

- log messages more explicit and status printed with intuitive colors.
- management of input/output file format re-done: now easier for the user.

Development:

- package architecture revised: mainly "sppasgui" and "components" merged
in "wxgui", and many other changes.
- thread removed in automatic annotation process.
- debug of alignment: if too short units.
- radius value properly fixed in most of the automatic annotations.

GUI:

- GUI is more homogeneous and pretty (hope!)
- Show the date in the status bar
- New Settings frame:

     * 4 icon themes available
     * Choice of foreground and background colours
     * Choice of the font
     * Choice of the input/output file format of annotations
     
- New in Help menu:

     - access to the project homepage
     - access to the online documentation
     
- New Feedback window
- New Help browser
- Add Keyboard shortcuts:

     - ALT+F4 to exit,
     - CTRL+A to add files in FLP
     - SHIFT+CTRL+A to add a directory in FLP
     - Del to remove selected files of the FLP
     - SHIFT+Del to erase selected files of the FLP
     - CTRL+C to copy files
     - CTRL+E to export files
     - F5 to refresh the FLP
     - F1 to open the help browser
     - F2 to open the "About" frame

Components:

- GUI design unified for DataRoamer, SndPlayer, IPUscribe and SppasEdit
- New Tier Preview frame (still under development)
- SndPlayer print information about a sound file with colors:

     - Green: the information corresponds to the SPPAS requirements
     - Orange: the information does not exactly corresponds to the requirements
        however SPPAS is able to deal with (after conversion)
     - Red: SPPAS does not support. It must be converted before using it!


### SPPAS-1.6.7 (2015, 16th February)

Automatic Annotations:

- By default, tokenization produces only one tier. Check an option to get
  TokensStd and TokensFaked, in case of EOT.
- radius value properly fixed in most of the automatic annotations.

GUI:

- Tested and debugged on MacOS (version 10.9.5, with wxpython 3.0.2)

Development:

- Tier hierarchy partly implemented: TimeAlignement and TimeAssociation are
  two "links" that can be fixed between tiers.

Annotations:

- Add Polish support


### SPPAS-1.6.8 (2015, 9th April)

Resources:

- new French acoustic model
- new English acoustic model (VoxForge nightly build of March, 15th, 2015)
- add phoneset mapping tables

Development:

- Add a phoneme mapping in models, to allow both the dictionary to include
  real X-SAMPA symbols and the acoustic model to be compatible with Hvite
  requirements (only ASCII).
- annotationdata bug correction with min and max values
- IPUs Segmentation:

     - bug correction when split into tracks with a tier "Name"
     - add the ipu number in speech segments if silence/speech segmentation

- Self-repetitions debug in finding the repetition interval

GUI:

- DataRoamer: "New" button debugged
- DataRoamer: Add a button "Radius" to adjust manually the vagueness of each bounday of a tier
