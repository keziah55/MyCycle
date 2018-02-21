# MyCycle

Edit and plot my cycling stats.

MyCycle provides a better interface for inputting
csv data than a spreadsheet or a plain text editor.

It will also plot my average distance per minute and
total distance cycled in a Matplotlib figure, which 
can be exported as a pdf.

Most of the GUI for handling the csv data is from 
[TimeAfterTime](https://github.com/keziah55/TimeAfterTime),
with a few tweaks and an expansion of the `Data` class into
a larger structure with `__getitem__` and `__setitem__` 
methods.
The implementation of this probably needs a rethink; which is
the fundamental representation of `Data`: the string as read
from file or the 'dataframe'?


## Branch summary

### remove_line

Code for removing lines added in the NewLineDialog (i.e. unnecessary 
empty lines). My code to remove the lines and any data in them 
works, but the display goes weird: it appears that the last line
isn't being removed (that it, the line at the bottom doesn't disappear
and the data in it doesn't change, although the data from it is being
removed from the Data object). So it seems to be some kind of QGridLayout 
thing. Tried updating display on every removal, didn't work.

Also, EditLineDialog has the opposite problem: can edit data in the dialog,
but it won't update the Data object. Think this will come out in the wash
with the next branch...


### dataobject

Refactor the dataobject code, so it is stored as a list of lists (or possibly
Pandas dataframe, although that seems like overkill and I like my access 
functions), with a `__str__` method to convert to string for display.


