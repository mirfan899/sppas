## GUI Main frame


### Launch SPPAS

Under Windows, once the SPPAS package is opened in the File Explorer,
*double-click on the `sppas.bat` file*.

Under MacOS or Linux, once the SPPAS package is opened in the 
Finder/File Explorer, *double-click on the `sppas.command` file*. The program
will first check the version of wxpython and eventually ask to update.

Then, the main windows will open automatically. It is made of a menu, a title, 
the tips, the list of files and the action buttons.

![SPPAS Main Frame of version 1.8.0](./etc/screenshots/sppas-1-8-0.png)


### The tips

![The tips included in the main frame](./etc/screenshots/tips.png)

The frame includes message tips that are picked up randomly and printed to 
help users. Click on the button `Next Tip` to read another message, or click 
on the top-left button to close the tips frame. 
The `Settings` allows to show/hide tips at start-up.
If a user wants to suggest new tips to help the other users, they have to be
sent to the author by e-mail. They will be included in the next version.


### The menu

It allows to exit the program, declare an issue and contact the author.

The `Exit` button closes all SPPAS frames *properly*. 
Please, do not kill SPPAS by clicking on the arrow of the windows manager!
**Use this Exit button** to close SPPAS. 

To declare an issue, click on the bug button of the menu, then your default
web browser will be opened at the appropriate URL to do this.

To contact the author, replace the text "Describe what you did here..." by 
your own comment, question or suggestion and choose how to send the e-mail: 
with your own default mailer, with gmail (opened in your web browser)
or by another e-mail client. Then, close the frame by clicking on the "Close"
button.

![The Feedback Frame](./etc/screenshots/feedback.png)


### The file explorer

![File List Panel (FLP)](./etc/screenshots/FLP.png)

The list contains directories and files the user added, but only files 
that SPPAS can deal with, e.g. depending on the file extension.

To select:

* a single click on a file name highlights and selects the chosen file (displayed in the list).
* a single click on a directory name highlights and selects the chosen directory (displayed in the list).

Like in any other file explorer, while clicking and pressing the "CTRL" key 
("COMMAND" on MacOS) on the keyboard, you can select multiple files and/or 
directories. Idem with the "SHIFT" key.
The "F5" shortcut allows to refresh the list.

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


### Settings

To change preferences, click on the `Settings` icon, then choose your
preferred options: 

- General: fix background color, font color and font of the GUI, and enable/disable tips at start-up.
- Theme: fix the icons of the GUI. 
- Annotations: fix automatic annotations parameters.

![Settings is used to manage user preferences](./etc/screenshots/settings.png)

The Settings can be saved in a file to be used each time SPPAS is executed. 
To close the frame, click on:

- "Cancel" button to ignore changes,
- "Close" to apply changes then close the frame.


### About

The `About` action button allows to display the main information about SPPAS: 
authors, license, web site URL, etc.


### Help

The `Help` action button opens the documentation and allows to browse in the chapters
and sections.

![The Help Browser Frame](./etc/screenshots/helpbrowser.png)


### Plugins 

#### Installing a Plugin

To install a plugin, follow this workflow:

1. Download and unpack the Plugin package in a new folder (this folder will
be removed after the plugin installation).
2. Execute SPPAS.
3. Click on the 'Plugin' icon of the toolbar: it will open a new frame.
4. Indicate the folder of the new Plugin in the text entry.
5. Follow the Plugin instructions (if any).
6. See the new Plugin icon in the Plugins panel of the main frame.

![Installing a new Plugin](./etc/figures/plugin-workflow.bmp)


#### Using a Plugin

To execute a plug-in, select file(s) in the File explorer, click on the 
icon of the plug-in and follow instructions of the plugged program.

![Plugins Panel with two plug-ins: TierMapping and MarsaTag](./etc/screenshots/PPP.png)
