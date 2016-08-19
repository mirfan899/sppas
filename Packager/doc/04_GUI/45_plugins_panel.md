## Plugins 

This panel includes the icons of plugins that were previously installed. 
To execute a plug-in, select file(s) in the File explorer, click on the icon
of the plug-in and follow instructions of the plugged program.

![Plugins Panel with two plug-ins: TierMapping and MarsaTag](./etc/screenshots/PPP.png)


### Installing a Plugin

To install a plugin, follow this workflow:

1. Download and unpack the Plugin package in a new folder (this folder will
be removed after the plugin installation).
2. Execute SPPAS.
3. Click on the 'Plugin' icon of the toolbar: it will open a new frame.
4. Indicate the folder of the new Plugin in the text entry.
5. Follow the Plugin instructions (if any).
6. See the new Plugin icon in the Plugins panel of the main frame.

![Installing a new Plugin](./etc/figures/plugin-workflow.bmp)


### Marsatag-Plugin

MarsaTag-Plugin is a plugin to use the French POS-tagger *MarsaTag* 
directly from SPPAS. Using this plugin offers two main advantages:

1. the POS-Tags are time-aligned; and
2. MarsaTag is ready-to-use: all steps to execute MarsaTag are pre-configured.

Notice that you must install MarsaTag first: 
<http://sldr.org/sldr000841>


### TierMapping

This plugin allows to create new tiers by mapping the labels of an existing 
tier, with new labels. Some mapping-tables are included in the plugin:

- map the phonemes of the tier "PhonAlign" from SAMPA to IPA,
- map the phonemes of the tier "PhonAlign" to their articulatory properties.

Furthermore, any user can easily create a mapping table. The only requirements
are that all tables must be UTF-8 encoded in a CSV file, with columns 
separated by semi-columns. 
These tables can be imported/modified/saved with OpenOffice, LibreOffice, Excel, ... 
The most important is to not change its properties (UTF8, semi-columns) 
and location (inside the `resources` directory of the plug-in directory).

![Plug-in: TierMapping](./etc/screenshots/TierMapping.png)
