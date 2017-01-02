## CLI 

A command-line interface (CLI), also known as command-line user interface, 
is a means of interacting with a computer program where the user issues 
commands to the program in the form of successive lines of text (command lines).
Command-line interfaces provide a more concise and powerful means to 
control the program than the GUI.
Operating system command line interfaces are called a command-line interpreter, 
command processor or shell. It displays a prompt, accept a "command line" 
typed by the user terminated by the Enter key, then execute the specified 
command and provide textual display of results or error messages.
When a shell is active a program is typically invoked by typing its name 
followed by command-line arguments (if any).

Such programs are located in the `bin` folder of the `sppas` directory
included in the SPPAS package.
All these programs are written with the programming language Python 2.7.


It is usual for a program to be able to display a brief summary of its
parameters. Each program included in SPPAS provides its usage by using the
option `--help`, as for example:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
bin> annotation.py --help
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are 2 types of programs in the `sppas` directory then `bin` folder:

1. programs to execute an automatic annotation; 
2. programs to execute an analysis tool.

Moreover, the program "plugin.py" allows to install, execute and
remove a plugin of SPPAS.

