## Main and important recommendations


### About files

There is a list of important things to keep in mind while using SPPAS.
They are summarized as follows and detailed in the chapters of this 
documentation:

1. Speech audio files:

    - only `wav`, `aiff` and `au` audio files
    - only mono (= one channel)
    - frame rates preferably: 16000hz, 32000hz, 48000hz
    - bit rate preferably: 16 bits
    - good recording quality is expected. It is of course required to
    never convert from a compressed file (as mp3 for example).

2. Annotated data files:

    - UTF-8 encoding only
    - it is recommended to use ony US-ASCII characters in file names (including their path)


### About automatic annotations

The quality of the results for most of the automatic annotations is highly
influenced by the quality of the data the annotation takes in input.
This is a politically correct way to say: **Garbage in, garbage out!**

Annotations are based on the use of **resources**, that are gently shared and
freely available in the SPPAS package. 
The quality of the automatic annotations is largely influenced by such 
resources, and the users can contribute to improve them. In that sense, 
users need automatic tools and such tools need users.
Users are of crucial importance for resource development. They can contribute 
to improve them, and the author releases the improvements to the public, so 
that the whole community benefits. Resources are distributed under the terms 
of public licenses, so that SPPAS users are "free": 
free to study the source code and the resources of the software they use, 
free to share the software and resources with other people, 
free to modify the software and resources, and 
free to publish their modified versions of the software and resources.
