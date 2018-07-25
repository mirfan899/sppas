## IPUscriber

`IPUscriber` is useful to perform manual orthographic transcription. 
When an audio file is checked in the list of files, the program search for a file
with the IPUs Segmentation, i.e. a file with the same name (in the same directory) 
with a known extension like .xra, .TextGrid, etc. If this file is not found,
an error message is displayed. Otherwise, the audio file is opened and the
annotated file is loaded in a new page of the notebook.

![IPUscriber: for manual orthographic transcription](etc/screenshots/IPUscriber.png)

Silences are hidden and the IPUs are displayed in a list of boxes with:

- at left: the name of the tier followed by the number of the interval, then the
  time values of start and end of the interval, and the duration of the interval
  between parenthesis.
- at right: the content text of the IPU.

At the bottom of the tab, green buttons perform actions on the audio file:
get information, play, auto-play, make pause and stop playing.
The following keyboard shortcuts can also be used:

- TAB: Play
- ESC: Stop
- F6: Rewind
- F7: Pause
- F8: Next

By default, only 50 IPUs are displayed at a time in a tab. To get access to 
the next/previous IPUs, 4 small buttons in gray allow to navigate in the 
pages.

To transcribe an IPU, click on the IPU text box, play sound and write 
the corresponding text: refer to the transcription convention of 
this document.
