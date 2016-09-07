# Tutorial 2: Data preparation for automatic annotations

## Recording Speech

-----------------

### Recording audio 

* The resolution of the capture devices (microphones, framerate, file format, software)
has a determining influence on the quality of the corpus, and so on the annotations.

![](./etc/images/no_phone.jpg) ![](./etc/images/H4N.jpg) ![](./etc/images/H4N_video.jpg)

* The number of devices is also important.

* Lack of standardization means that fewer researchers will be able to work with those signals.

-----------------

### Recording audio: software tools

A short list of software tool we already tested and checked:

- audacity [http://audacity.sourceforge.net/](http://audacity.sourceforge.net/)
- sox [http://sox.sourceforge.net/](http://sox.sourceforge.net/)

![](./etc/images/logo_audacity.jpg)
![](./etc/images/logo_sox.png)

-----------------

### Recording speech: SPPAS requirements

* `wav`, `aiff` and `au` audio file formats 

* only one channel (mono) per file

* good recording quality is expected

![Example of recorded speech](./etc/screenshots/signal.png)




## Transcribing Speech

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

![](./media/AG_track_0529.wav)

* Manual orthographic transcription:

> donc + i- i(l) prend la è- recette et tout bon i(l) vé- i(l) dit bon [okay, k]

* Automatically extracted standard orthograph: 
    - donc il prend la recette et tout bon il dit bon okay
* Automatically extracted faked orthograph:
    - donc + i i prend la è recette et tout bon i vé i dit bon k

-----------------

### Transcription example 2 (Conversational speech)

![](./media/AP_track_0968.wav)

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

![](./media/grenelleII-systemiques.wav)

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


