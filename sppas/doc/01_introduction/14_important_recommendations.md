## Main and important recommendations


### About files

There is a list of important things to keep in mind while using SPPAS.
They are summarized as follows and detailed in the chapters of this 
documentation:

1. Speech audio files:

    - only `wav` and `au` files
    - only mono (= one channel)
    - frame rates: 16000hz
    - bit rate: 16 bits
    - good recording quality is expected. It is obviously required to
    never convert from a compressed file, as mp3 for example.

2. Annotated data files:

    - *UTF-8* encoding only
    - it is recommended to use only US-ASCII characters in file names (including the path)

Other frame rates and bit rates are accepted: the audio file is converted in
16 bits/16000Hz in a copy of the file then SPPAS is using this latter.


### About automatic annotations

The quality of the results for most of the automatic annotations is highly
influenced by **the quality of the data the annotation takes in input**.
This is a politically correct way to say: *Garbage in, garbage out!*

Annotations are based on the use of linguistic resources. Resources for
several languages are gently shared and freely available in the SPPAS package. 
The quality of the automatic annotations is largely influenced by **the
quality of the linguistic resources**. The users can contribute to improve them. 


### About linguistic resources 

**Users are of crucial importance for resource development**. 
They can contribute to improve them, and the author releases the improvements 
to the public, so that the whole community benefits. Resources are distributed 
under the terms of public licenses, so that SPPAS users are "free": 

- free to study the source code and the resources of the software they use, 
- free to share the software and resources with other people, 
- free to modify the software and resources, and 
- free to publish their modified versions of the software and resources.
