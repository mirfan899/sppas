## File List Panel

The File List Panel (FLP) consists of:

- a file explorer: a tree-style set of files and directories.
- at top, a toolbar: a set of buttons to perform actions.

![File List Panel (FLP)](./etc/screenshots/FLP.png)


### The file explorer

The list contains Directories and Files the user added, but only files that 
SPPAS can deal with (depending on the file extension).

To select:

* a single click on a file name highlights and selects the chosen file (displayed in the list).
* a single click on a directory name highlights and selects the chosen directory (displayed in the list).

Like in any other file explorer, while clicking and pressing the "CTRL" key 
("COMMAND" on MacOS) on the keyboard, you can select multiple files and/or 
directories. Idem with the "SHIFT" key.


### The toolbar


#### Add file(s).

A single-click on the `Add File` button opens a frame that allows to select
the files to get. By default, only "wav" files are proposed.
If you select *a wav file(s)*, all files with the same name will be 
automatically added into the file explorer. It is possible to change the 
wildcard of this frame and to select each file to add. 
In both cases, only files with an appropriate extension will be added in the 
file explorer.

![Adding specific files](./etc/screenshots/FLP-Add.png)

>Remark: The files are added in the list, but they are not opened.


#### Add a directory.

A single-click on the `Add Dir` button opens a frame that allows to select
the directory to get. 
Each wav file, and all related files (i.e. with the same name and with an 
appropriate extension) will be added into the file explorer.


#### Remove file(s).

A single-click on the `Remove` button removes the selected files/directories.

Notice that files are not deleted from the disk, they are just removed 
of the FLP.


#### Delete file(s).

A single-click on the `Delete` button deletes definitively the selected 
files/directories of your computer, and remove them of the FLP.
Notice that there is no way to get them back!

A dialogue frame will open, and you'll have to confirm or cancel the 
definitive file(s) deletion.


#### Copy file(s).

A single-click on the `Copy` button allows to copy the selected file(s), 
change their name and/or change the location (eventually, change the file
extension).


#### Export file(s).

Export annotated files in an other format (csv, txt, ...):

![Export: Check the expected format in the list](./etc/screenshots/FLP-Export.png)

After the export, a new frame will open to report if file(s) were exported
successfully or not.
