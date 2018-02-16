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
