# Data preparation for automatic annotations

## (Step 1) Recording Speech

-----------------

### Recording audio 

* The resolution of the capture devices (microphones, framerate, file format, software)
has a determining influence on the quality of the corpus, and so on the annotations.
* Lack of standardization means that fewer researchers will be able to work with those signals.

![](./etc/images/no_phone.jpg) ![](./etc/images/H4N.jpg) ![](./etc/images/H4N_video.jpg)


-----------------

### Recording audio: software tools

* A short list of software tool we already tested and checked:
    - audacity [http://audacity.sourceforge.net/](http://audacity.sourceforge.net/)
    - sox [http://sox.sourceforge.net/](http://sox.sourceforge.net/)

![](./etc/images/logo_audacity.jpg)
![](./etc/images/logo_sox.png)

-----------------

### Recording speech: SPPAS requirements

* `wav` and `au` audio file formats 

* only one channel (mono) per file

* good recording quality is expected

![](./etc/media/ENG_M15_ENG_T02.wav)

![Example of recorded speech](./etc/screenshots/signal.png)

-----------------

## (Step 2) IPUs segmentation

-----------------

### Inter-Pausal Units

* The orthographic transcription must be pre-segmented

![Orthographic transcription into the IPUs](./etc/screenshots/ipu-seg-result2.png)

-----------------

### How to do?

* SPPAS can automatically perform the IPUs segmentation
    - manual check
    - see the related tutorial and/or the documentation for details
* IPUs must be segmented manually (for example while transcribing):
    - if the audio signal is of poor quality;
    - if there are more than one speaker in the same channel.

-----------------

## (Step 3) Transcribing Speech

-----------------

### Orthographic transcription:

*  must include:
    - Filled pauses
    - Short pauses
    - Repeats
    - Truncated words
    - Noises
    - Laughter
*  should include:
    - un-regular elisions
    - un-regular liaisons
    - specific pronunciations
*  may include:
    - all elisions

-----------------

### Orthographic transcription: SPPAS convention

* truncated words, noted as a ’-’ at the end of the token string (an ex- example)
* noises, noted by a ’*’
* laughs, noted by a ’@’
* short pauses, noted by a ’+’
* elisions, mentioned in parenthesis
* specific pronunciations, noted with brackets [example,eczap]
* comments are noted inside braces or brackets without using comma {this} or [this and this]
* liaisons, noted between ’=’ (an =n= example)
* morphological variants with \<like,lie ok\>
* proper name annotation, like \$John S. Doe\$

-----------------

### Transcription example 1 (Conversational speech)

![](./etc/media/AG_track_0529.wav)

* Manual orthographic transcription:

> donc + i- i(l) prend la è- recette et tout bon i(l) vé- i(l) dit bon [okay, k]

* Automatically extracted standard orthograph: 
    - donc il prend la recette et tout bon il dit bon okay
* Automatically extracted faked orthograph:
    - donc + i i prend la è recette et tout bon i vé i dit bon k

-----------------

### Transcription example 2 (Conversational speech)

![](./etc/media/AP_track_0968.wav)

* Manual orthographic transcription:

> ah mais justement c'était pour vous vendre bla bla bla bl(a) le mec i(l) te l'a 
emboucané + en plus i(l) lu(i) a [acheté,acheuté] le truc et le mec il est parti 
j(e) dis putain le mec i(l) voulait

* Automatically extracted standard orthograph: 
    - ah mais justement c'était pour vous vendre bla bla bla bla le mec il te l'a 
emboucané en plus il lui a acheté le truc et le mec il est parti je dis putain 
le mec il voulait
* Automatically extracted faked orthograph:
    - ah mais justement c'était pour vous vendre bla bla bla bl le mec i te l'a 
emboucané + en plus i lu a acheuté le truc et le mec il est parti 
j dis putain le mec i voulait

-----------------

### Transcription example 3 (GrenelleII)

![](./etc/media/grenelleII-systemiques.wav)

* Manual orthographic transcription:

> euh les apiculteurs + et notamment b- on ne sait pas très bien + quelle est 
la cause de mortalité des abeilles m(ais) enfin il y a quand même + euh peut-êt(r)e 
des attaques systémiques

* Automatically extracted standard orthograph: 
    - les apiculteurs et notamment on ne sait pas très bien quelle est la cause de 
mortalité des abeilles mais enfin il y a quand même peut-être des attaques systémiques
* Automatically extracted faked orthograph:
    - euh les apiculteurs + et notamment b on ne sait pas très bien + quelle est 
la cause de mortalité des abeilles m enfin il y a quand même + euh peut-ête 
des attaques systémiques

-----------------

## Annotated files: recommendations

* UTF-8 encoding only
* No accentuated characters in file names (nor in the path)
* Supported file formats to open/save (software, extension):

    - SPPAS: xra
    - Praat: TextGrid, PitchTier, IntensityTier
    - Elan: eaf
    - AnnotationPro: antx
    - HTK: lab, mlf
    - Sclite: ctm, stm
    - Phonedit: mrk
    - Excel/OpenOffice/R/...: csv
    - Subtitles: sub, srt

* Supported file formats to import (software, extension):
    - Transcriber: trs
    - Anvil: anvil
    - Xtrans: tdf
    - Audacity: txt

----------------

### Supported file formats

![](./etc/figures/sppas-formats.png)


-----------------

## To keep in mind...

>Garbage in, garbage out

--------------

### 

[Back to tutorials](./tutorial.html)
