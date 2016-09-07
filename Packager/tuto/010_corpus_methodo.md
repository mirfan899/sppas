# Tutorial 1: Corpus creation methodology


## The workflow

![Corpus creation and annotation: methodology](./etc/figures/methodo.png)

------------------------------------------------------------------------


## Step 1: Recording speech

* One channel per speaker
* Anechoic room, or an environment with no/low noise
* Audio: for automatic annotation tools:
    - Any un-compressed file format, commonly WAVE
    - 16000Hz / 16bits is enough
* Audio: for manual annotation tools:
    - Any un-compressed file format
    - 48000Hz / 32bits is of high quality

------------------------------------------------------------------------


## Step 2: IPUs Segmentation


* Automatic segmentation in Inter-Pausal Units
    * is also called Silence/Speech segmentation
* Parameters to define manually:
    * fix the minimum silence duration
    * fix the minimum speech duration
* As results: 
    * speech and silences are time-aligned automatically
    * a manual verification is highly recommended

------------------------------------------------------------------------


## Step 3: Orthographic Transcription

* Any transcription must follow a convention
* In speech (particularly in spontaneous speech), many phonetic variations occur:
    - some of these phonologically known variants are predictable
    - but many others are still unpredictable (especially invented words, 
    regional words or words borrowed from another language)
* The orthographic transcription must be enriched: 
    - it must be a representation of what is “perceived” in the signal. 

------------------------------------------------------------------------


## Step 4: Phonemes/Tokens time-alignment

* A problem divided into 3 tasks:
    1. tokenization 
        - text normalization, word segmentation
    2. phonetization 
        - grapheme to phoneme conversion
    3. alignment 
        - speech segmentation

------------------------------------------------------------------------


## Other steps: 

On the basis of the time-aligned phonemes/tokens, other automatic annotations:
* Syntax
* Syllables
* Repetitions
* TGA
* ...

