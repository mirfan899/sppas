## Getting started

The current chapter describes how to use the Graphical User Interface.

Under Windows, once the SPPAS package is opened in the File Explorer,
*double-click on the `sppas.bat` file*.

Under MacOS or Linux, once the SPPAS package is opened in the 
Finder/File Explorer, *double-click on the `sppas.command` file*. The program
will first check the version of wxpython and eventually ask to update.

Then, two windows will open automatically.

1. Above, a window with a tips aims at displaying messages to help users to 
discover SPPAS capabilities.

2. Below, the main frame: to perform automatic annotations, get statistics, 
filter data, view wav/annotated data, etc.


### The Tips Frame

This frame picks up randomly and prints a message to help users.
Click on the button `Next Tip` to read another message, or click on the `Close` 
button to close the frame. 

![The Tips Frame](./etc/screenshots/tips.png)

The `Settings` frame also allows to show/hide the Tips frame at start-up.

If you want to suggest new tips (to help the other users), send them by 
e-mail to the author at `brigitte.bigi@gmail.com`. They will be included in 
the next version.



### The main frame

The main frame is made of a menu, a toolbar and the main content. All of them
are described in the next sub-sections.

![The Main Frame of version 1.7.6](./etc/screenshots/sppas-1-7-6.png)

#### The menu

It allows to access to all functions of the GUI, and to manage it.

The "File" menu can be used to manage files (add, remove, ...) and to exit the program.

In the "Preferences" menu, check boxes allow to show/hide the toolbar 
and the status bar, and to fix settings (see below for details).

The "Help" menu includes an item to open the SPPAS website
in a web browser, to access inline documentation, to declare a bug and to send
feedback to the author. In the latter case, replace the text "Describe what you
did here..." by your own comment, question or suggestion and choose how to send
the e-mail: with your own default mailer, with gmail (opened in your web browser)
or by another e-mail client. Then, close the frame by clicking on the "Close"
button.

![The Feedback Frame](./etc/screenshots/feedback.png)


#### The toolbar

The toolbar includes 5 buttons: 

1. Exit;
2. Settings;
3. Plug-in;
4. About;
5. Help.

The look of the toolbar can change depending of the Theme of the icons.

![Main toolbar, with Default icon theme](./etc/screenshots/toolbar-default.png)

![Main toolbar, with Metro icon theme](./etc/screenshots/toolbar-metro.png)

![Main toolbar, with CrystalClear icon theme](./etc/screenshots/toolbar-crystalclear.png)


The `Exit` button closes all SPPAS frames *properly*. 
Please, do not kill SPPAS by clicking on the arrow of the windows manager!
**Use this Exit button** to close SPPAS. 

To fix new settings, click on the `Settings` icon, then choose your
preferred options: 

- General: fix background colour, font colour and font of the GUI, and enable/disable tips at start-up.
- Theme: fix the icons of the GUI. 
- Annotations: fix automatic annotations parameters.

![Settings is used to manage user preferences](./etc/screenshots/settings.png)

The Settings can be saved in a file to be used each time SPPAS is executed. 
To close the frame, click on:

- "Cancel" button to ignore changes,
- "Close" to apply changes then close the frame.


The `Plug-in` button allows to install a new plugin.

The `About` button opens a new frame which gives the main information about
SPPAS: authors, license, web site URL, etc.

The `Help` button opens the documentation and allows to browse in the chapters
and sections.

![The Help Browser Frame](./etc/screenshots/helpbrowser.png)


#### The content of the frame.

The content of the main frame is made of 4 main panels:

1. the file list panel (FLP), at left;
2. the automatic annotation panel (AAP); at middle-top;
3. the components panel (CCP), at middle-bottom;
4. the plug-ins panel (P&P), at right.
