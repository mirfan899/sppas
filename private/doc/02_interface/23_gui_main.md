## GUI Main frame


### Launch SPPAS

Under Windows, once the SPPAS package is opened in the File Explorer,
double-click on the `sppas.bat` file.
In recent versions of Windows (e.g. 10), the first time you try 
to run SPPAS you may get a window with title "Windows protected your PC"
and the following message: "Windows SmartScreen prevented an unrecognized 
app from starting. Running this app might put your PC at risk. More info".
Click `More info` message and then `Run anyway` button. 
The file will now run SPPAS, and you will now no longer get a Windows 
protected your PC prompt when you run this specific file next time.
This warning message comes from the fact that SPPAS is a free software
and we did not paid to Microsoft commercial fees which would remove the 
"Unknown Publisher" warnings. 

Under MacOS, once the SPPAS package is opened in the Finder, double-click 
on the `sppas.command` file. In recent versions of MacOs X (e.g. from 10.11 
El Capitan), the first time you try to run SPPAS you may get a message:
"sppas.command can't be opened because it is from an unidentified developer.".
This warning message comes from the fact that SPPAS is a free software
and we did not paid to Apple commercial fees. The solution is to run SPPAS 
with a right click (alt-click) on sppas.command file. This time you will get
a message: "sppas.command is from an unidentified developer. Are you sure 
you want to open it?" Then click on `Open`. 
It will also now work each time you run it.

Under Linux, once the SPPAS package is opened in the 
Finder/File Explorer, double-click on the `sppas.command` file.

The program will first check the version of wxpython and eventually ask to 
update. It will then check if the julius program can be accessed.

The main windows will open automatically. It is made of a menu (left), 
a title (top), 
the tips (middle), 
the list of files (left-middle),
and the action buttons (right).

![Main Frame of version 1.9.0](./etc/screenshots/sppas-1-8-0.png)


### The tips

![The tips included in the main frame](./etc/screenshots/tips.png)

The frame includes message tips that are picked up randomly and printed to 
help users. Click on the button `Next Tip` to read another message, or click 
on the top-left button to close the tips frame. 
The `Settings` allows to show/hide tips at start-up.
Anyone can suggest new tips to help other users. They have to be
sent to the author by e-mail so that they will be included in the next 
version.


### The menu

The menu is located at the left-side of the window.
At top, a button allows to exit the program, and at bottom
you can declare an issue or contact the author.

The `Exit` button closes all SPPAS frames properly. 

To declare an issue, click on the bug button of the menu, then your default
web browser will be opened at the appropriate URL. Take a quick look at the 
list of already declared issues and if any, click on the green button "New
Issue".

To contact the author, replace the text "Describe what you did here..." by 
your own comment, question or suggestion and choose how to send the e-mail: 
with your own default mailer, with gmail opened in your web browser,
or by another e-mail client. Then, close the frame by clicking on the "Close"
button.

![The Feedback Frame](./etc/screenshots/feedback.png)


### The file explorer

![File explorer](./etc/screenshots/FLP.png)

The list contains directories and files the user added. However, only files 
that SPPAS can deal with, e.g. depending on the file extension, can be appended 
to the list. Files with an unknown extension are rejected.

>Remark: The files are added in the list, but they are not opened.


#### Select file(s)

To select a single file, all files of a directory or several files:

* a single click on a file name highlights and selects the chosen file. If other files or directories were previously selected, they are deselected.
* a single click on a directory name highlights the chosen directory and selects all files. If other files or directories were previously selected, they are deselected.
* to select several files or directories, the `ctrl` key (Linux/Windows) or `CMD` key (Apple) must be pressed while clicking each file or directory.
* to select several files or directories, the `shift` key can be pressed while clicking two files or directories.


#### Add file(s)

A single-click on the `Add files` button opens a window that allows to select
the files to get. By default, only files with ".wav" extensions are proposed.
When audio file(s) is/are selected, all files with the same name are 
automatically added into the file explorer. 

The wildcard of this window can be changed to some other specific file extensions
and then other files can be selected. 

In both cases, only files with an appropriate extension will be added in the 
file explorer.

![Adding specific files](./etc/screenshots/FLP-Add.png)


#### Add a directory

A single-click on the `Add dir` button opens a window that allows to select
the directory to get. 
Each audio file, and all related files - i.e. with the same name and with an 
appropriate extension, will be added into the file explorer.


#### Remove file(s)

A single-click on the `Remove` button removes the selected files/directories
of the list. Notice that files are not deleted from the disk.


#### Delete file(s)

A single-click on the `Delete` button deletes *definitively* the selected 
files/directories of your computer, and remove them of the list.
Notice that there is no way to get them back!

A dialogue window will open, and you have to confirm or cancel the 
definitive file(s) deletion.


#### Copy file(s)

A single-click on the `Copy` button allows to copy the selected file(s), 
change their name and/or change the location. It is also possible to 
change the file format by assigning the appropriate file extension. 


#### Export file(s)

Export annotated files in an other format (csv, txt, ...):

![Export: Check the expected format in the list](./etc/screenshots/FLP-Export.png)

After the export, a new window opens to report whether the file(s) were 
exported successfully or not. Actually, an export fails if:
- the given file is not in UTF-8 encoding;
- the given file contains several tiers and the output format supports only one;
- the given file contains corrupted annotations.


### Settings

To change user preferences, click on the `Settings` icon, then choose your
preferred options in the tabs: 

- General: fix background color, font color and font of the GUI, and enable/disable tips at start-up.
- Theme: fix how the icons of the GUI will look like. 
- Annotations: fix automatic annotations parameters.

![Settings is used to manage user preferences](./etc/screenshots/settings.png)

These preferences can be saved in a file to be used each time SPPAS is executed. 
Finally, to close the settings window, click on:

- "Cancel" button to ignore changes;
- "Close" to apply changes then close the window.


### About

The `About` action button allows to display the main information about SPPAS: 
author, license, a link to the web site, etc.


### Help

No longer available. Use this documentation instead.


### Plugins 

Installing plugins is a very useful solution to extend the features
of SPPAS. Several plugins are available for download in the main site
of SPPAS. The plugins of SPPAS are installed in a folder with name "plugins"
in the main directory of SPPAS.

> The plugin system of SPPAS was fully changed at version 1.8.2;
> and plugins were all updated at version 1.9.0.
> Old plugins and new ones are not compatibles.


#### Installing a plugin

To install a plugin, simply follow this workflow:

1. Download the plugin package - e.g. a zip file.
2. Execute SPPAS.
3. Click on the 'Plugin' icon then click on the 'Install' button of the toolbar.
4. Browse to indicate the plugin package.
5. See the new plugin icon in the plugins list.

![Installing a new Plugin](./etc/figures/plugin-workflow.png)


#### Deleting a plugin

To delete a plugin, click on the "Delete" button of the toolbar.
Choose the plugin in the given list then click on the "OK" button.
Notice that the plugin is definitively deleted of the disk.


#### Using a plugin

To execute a plug-in, select file(s) in the File explorer, click on the 
icon of the plug-in and follow instructions of the plugged program.
