## DataRoamer

`DataRoamer` displays detailed information about annotated files and allows 
to manage the tiers: cut/copy/paste/rename/duplicate tiers, move a tier from 
one file to another one, etc.

![DataRoamer: explore annotated files](./etc/screenshots/DataRoamer.png)


When an annotated file is checked in the list of files, the file is opened
in a new panel of the current tab of the notebook and information about this
file are displayed. At top, the name of the file is in dark green color. It 
is turned to blue color if some changes were applied. 
Below the name of the file, each tier is represented in a row of a spreadsheet:

- 1st column is a check box: select/deselect the tier;
- 2nd column indicates the number of the tier;
- 3rd column indicated the name of the tier;
- 4th column indicates the lower time value of the annotations;
- 5th column indicates the higher time values of the annotations;
- 6th column is the type of the tier: either "Interval" or "Point";
- last column is the number of annotations in the tier.

The buttons of the toolbar can be applied on the tier(s) selected in the same
tab of the notebook. For example, it is possible to copy a tier of a file and
to paste it in another file only if they are both open in the same tab.

- Rename: Fix a new name to the selected tier. If the given name is already 
  assigned to a tier in the same file, a number is automatically appended to
  the end of the new name.
- Delete: Definitively delete the selected tier. To recover the tier, the only 
  way is to close the file without saving changes and to re-open it.
- Cut: Delete the tier of the file and put it in the dashboard.
- Copy: Copy the selected tier into the dashboard.
- Paste: Paste the content of the dashboard into the currently selected file.
- Duplicate: Duplicate the selected tier in the file. A number is automatically 
  appended to the end of name of the copy.
- Move Up: Move the selected tier up in the list of tiers of the file.
- Move Down: Move the selected tier down in the list of tiers of the file.
- Radius: Fix the radius value of each localization of each annotation. A radius 
  value indicates the vagueness around the point. It is commonly ranging from 1ms
  for very (very) precise annotations up to 40ms for annotations of videos for
  example. This value is safely saved only in XRA format. Other formats don't
  consider vagueness.
- View: Open a window and display the annotations of the tier.

Only the `Delete` and `Radius` actions can be applied on several selected tiers
at a time. The other actions can be applied only on one selected tier.

