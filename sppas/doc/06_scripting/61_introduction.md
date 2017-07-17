## Introduction

SPPAS implements an Application Programming Interface (API), named 
*annotationdata*, to deal with annotated files.
 
*annotationdata* API is a free and open source Python library to access and 
search data from annotated data of any of the supported formats (xra, TextGrid, 
eaf...). *annotationdata* is based on the Programming Language Python 2.7.
It won't work with Python 3.x. Notice that this API will be fully 
re-implemented in the scope of 1/ compatibility with Python > 3.3, 2/ PEP8 and
PEP257 compliance and 3/ internationalization of the message. The new version
will available in the middle of 2018 but the current one will be maintained
until the end of 2018 or later.

In this chapter, it is assumed that Python 2.7 is already installed and
configured. It is also assumed that the Python IDLE is ready-to-use.
For more details about Python, see:

> The Python Website: <http://www.python.org>

This chapter firstly introduces basic programming concepts, then it 
gradually introduces how to write scripts with Python. Those who are familiar 
with programming in Python can directly go to the last section related to the 
description of the *annotationdata* API and how to use it in Python scripts.

This API can convert file formats like Elan’s EAF, Praat's TextGrid and 
others into a `Transcription` object and convert this object into any of 
these formats. This object allows unified access to linguistic data from 
a wide range sources.

    This chapter includes exercises. The solution programs are included in 
    the package directory *documentation*, then in the folder *solutions*.
