## The development phase


### SPPAS-1.6.9 

(2015, 14th May)

The installation of dependencies is simplified: `sox` is unnecessary.
Python 2.7.x, WxPython and Julius are the only remaining dependencies.

#### Development:

- package annotationdata.filter updated to support last changes in
  annotationdata: multiple labels and numerical labels.
- package annotationdata.io:

    - praat.py newly created. Support of TextGrid, PitchTier and
      IntensityTier files completely re-written
    - htk.py newly created to support .lab and .mlf files
    - sclite.py newly created to support .stm and .ctm files
    - signaix.py newly created to support .hz files
    - SPPAS native format XRA upgraded to version 1.1 to support
      improvements of the library.
      
- package annotationdata:

    - updated object Transcription to support more/different input data
    - updated hierarchy
    - updated meta-data
    
- package signal: partially re-written. As a consequence, sox won't
be neither used, but the file conversion (if required) is slower.

#### GUI:

- DataFilter component partially re-written to facilitate its use
- Preview frame modified


### SPPAS-1.7.0 

(2015, 3th July)

#### Development:

- package annotationdata.io:
    - add support of subtitles: sub, srt
    - elan.py created to replace eaf.py: allows a full support of Elan annotations
    - transcriber.py created to replace trs.py for a better support of Transcriber files
    - anvil.py allows to import anvil files
    
- package annotationdata:
    - updated hierarchy (simplified)
    - updated meta-data
    
- package signal:
    - support of audio files re-written: can open/save wav, aiff and au files
    - add a lot of possibilities to manage one channel of an audio file

#### GUI:

- DataFilter component finalized: can deal with alternative labels,
  and typed labels (string, number, boolean)
- Statistics component fully re-written to facilitate its use
- SndRoamer displays more properties of audio files (min, mean and max added)

#### Annotations:

- IPUs Segmentation produces 2 tiers if a transcription is given:
  the IPUs segmentation itself, and the Transcription time-aligned
  at the IPUs level.


### SPPAS-1.7.1 

(2015, 5th August)

#### Development:

- package re-organization:
     - package signal is now standalone
     - package resources is now standalone
     - package presenters created
     
- updated statistics estimations

- package annotationdata:

     - add Media object
     - add CtrlVocab object
     - add inheritance of MetaObject for Annotation
     
- package annotationdata.io:

     - full debug of all file formats
     - add comments and documentation
     - add also some tests
     - add Media/CtrlVocab in some file formats
     - add Annotation Pro support of antx files (in API)

#### Components:

- add Time Group Analyser (TGA) in Statistics
- add Kappa estimation on labels of 2 tiers with the same number of intervals

#### Annotations:

- New version of XRA: 1.2
- Make XRA the default input/output file format


### SPPAS-1.7.2 

(2015, 3th September)

#### Development:

- updated XRA reader/writer to solve problems with upper/lower cases of elements
- updated Elan reader to be compatible with format 2.8
- updated Praat reader/writer for single/double quotes
- support of AnnotationPro antx files in the GUI
- add the julius score in PhonAlign annotation (can be seen only if XRA)
- remove tk dependency


### SPPAS-1.7.3 

(2015, 9th October)

#### Resources:

- New word-based vocab for Cantonese
- New word-based dict for Cantonese
- New phoneme-based acoustic model for Cantonese

#### Development:

- Descriptive statistics debugged for detailed panels.


### SPPAS-1.7.4 

(2015, 6th November)

#### Resources:

- Add a vocab for Portuguese
- Add a dict for Portuguese
- Add an acoustic model for Portuguese. It has to be noticed that
  it was constructed from French/Spanish/Italian models, not trained
  from data.

#### Samples:

- Add Portuguese
- Change some samples in various languages

#### Development:

- Debug of the Tokenizer.


### SPPAS-1.7.5 

(2015, 11th December)

#### Development:

- Add vagueness to the annotation duration estimation
- Bug correction while saving the procedure outcome report in the GUI

#### GUI:

- Changed all pictures to remove the problem with colorset of some of them
- Add a christmast theme for the pictures of tips
- IPUscribe improvements:

    - add keyboard shortcuts to play/pause/stop the sound
    - add a new button to auto-play the sound


### SPPAS-1.7.6 

(2016, 28th January)

Web site host has changed: <http://www.sppas.org/>

#### Development:

- IPU segmentation:

     - bug correction with option "split into tracks"
     - new option to add or not add the IPU index of each IPU into the
        transcription tier
        
- Tokenization:

     - bug correction in input tier selection
     - bug correction for replacements

#### Resources:

- add a vocabulary of Korean
- add an acoustic model for Korean (made from the English and the Taiwanese ones).

#### GUI:

- DataRoamer: bug correction of "Duplicate"

#### Others:

- Add a sample in Korean
- Updated references to cite SPPAS in publications


### SPPAS-1.7.7 

(2016, 30th March)

#### Resources:

- Correction of errors in most of the acoustics models,
  for /@@/ and /dummy/ models
- New vocabulary and pronunciation dictionary for Mandarin Chinese.

#### GUI:

- Dialogs are customized
- DataRoamer debug and changes: save buttons moved in the main toolbar.
- HelpSystem is (welcome) back!

#### Development:

- Add the API and a script to train acoustic models with HTK.
- Add Kullback-Leibler distance estimator.
- Add a script to compare segmentation of 2 tiers.
- Classes of the package resources are debugged, improved and extended.
- Alignment: bug correction if input starts by an empty interval.
- `sppas.command` modified for MacOS-X (use python if python2 not available)
- GUIs in `bin` directory are updated (test of python, wxpython, and so on).


### SPPAS-1.7.8 

(2016, 5th May)

#### Resources:

- Add a pronunciation mapping table `eng-fra.map`: to be used for the
  speech segmentation for French speakers reading an English text.

#### Development:

- Phonetization is extended: it can take into account a mapping table of
  phones to generate new pronunciation variants.
- Phonetization: use of minus instead of dots to separate phones as
  recommended in X-SAMPA standard.
- Alignment is restructured and extended: it can take into account two
  acoustics models and mix them.
- Filter is extended: Relations can be based on a delay between the intervals
- annotationdata: add Xtrans reader (extension: .tdf)
- Code cleaning in several packages.

#### GUI:

- Automatic annotations: more explicit log messages.


### SPPAS-1.7.9 

(2016, 3th June)

#### GUI:

- Some debug in SppasEdit
- SndPlayer renamed AudioRoamer because new functionalities were added:

    - See detailed information about each channel of an audio file
    - Can extract/save a channel or a fragment of channel
    - Can modify the frame rate and the sample width of a channel
    - Can add a bias on amplitude values of a channel
    - Can multiply amplitude values of a channel
    - Can remove the offset of amplitude values of a channel

#### Automatic annotations:

- IPUs Segmentation fully re-implemented.
    - Silence/speech segmentation improved for both quality and fastness
    - Package code cleaning and re-organization.
