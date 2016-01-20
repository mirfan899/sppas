## Main and important recommendations


### About files

There is a list of important things to keep in mind while using SPPAS.
They are summarized as follows and detailed in chapters of this documentation:

1. Speech files:

    - only `wav`, `aiff` and `au` audio files
    - only mono (= one channel)
    - frame rates preferably: 16000hz, 32000hz, 48000hz
    - bit rate preferably: 16 bits
    - good recording quality is expected. It is of course required to
    never convert from a compressed file (as mp3 for example).

2. Annotated files:

    - UTF-8 encoding only
    - it is recommended to NOT use accentuated characters in file names
    nor in paths



### About automatic annotations

The quality of the results for most of the automatic annotations is highly
influenced by the quality of the data the annotation takes in input
(this is a politically correct way to say: **Garbage in, garbage out!**)

Annotations are based on the use of **resources**, that are freely available
in the SPPAS package.
The quality of the automatic annotations is also largely influenced by such
resources.
Fortunately... all the resources can be modified/improved/shared by any user!
