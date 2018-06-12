""" 
Dialogs required by Timesheet when adding or removing data.
Supplies AddLineDialog, NewRateDialog, and RemoveLineDialog.
"""

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QAbstractItemView, QAction, QDialog, 
                             QDialogButtonBox, QGridLayout, QGroupBox, 
                             QHBoxLayout, QLabel, QLineEdit, 
                             QMessageBox, QPushButton, QTableWidget, 
                             QTableWidgetItem, QVBoxLayout)

from str_to_date import str_to_date
from format_dur import format_duration

import abc

datefmt = '%d %b %Y'

class QDialog_CTRL_Q(QDialog):
    """ QDialog subclass with CRTL+Q shortcut to close window.
    
        Standard QDialog close shortcut is ESC, which still applies here.
    """
    
    def __init__(self):
        
        super().__init__()
        
        self.exitAct = QAction("E&xit", self, 
                               shortcut="CTRL+Q",
                               statusTip="Exit the application", 
                               triggered=self.close)
        self.addAction(self.exitAct)
        

class AddLineDialog(QDialog_CTRL_Q):
    
    def __init__(self, data, columnLabels):
        """ Add lines to csv file. 
            
            Parameters
            ----------
            data : Data object
                object which holds all the csv data
                
            columnLabels : list
                list of columns headers
        """
        super().__init__()
        
        self.initUI(data, columnLabels)
        
        
    def initUI(self, data, columnLabels):
        
        # 'data' is the csv data object
        self.data = data
        
        self.rows = []
        
        # message for main window status bar
        self.msg = ''
        
        # set labels
        labels = tuple(QLabel(label) for label in columnLabels)

        # get number of columns
        self.ncols = len(labels)
        
        editButtonSize = 80
        
        newButton = QPushButton(QIcon.fromTheme('list-add'), '')
        newButton.setMinimumWidth(editButtonSize)
        newButton.setShortcut("CTRL+N")
        newButton.clicked.connect(self.addLine)

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | 
                                     QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.set_new_values)
        buttonBox.rejected.connect(self.reject)
        
        # make GroupBox for new, ok and cancel buttons
        groupBoxBtn = QGroupBox()
        # don't draw a frame
        groupBoxBtn.setFlat(True)
        
        # make HBoxLayout and add the buttons
        dialogBtnBox = QHBoxLayout()
        dialogBtnBox.addWidget(newButton)
        dialogBtnBox.addWidget(buttonBox)
        
        # put the HBox in the GroupBox
        groupBoxBtn.setLayout(dialogBtnBox)
        groupBoxBtn.setFixedSize(270,50)
        
        # make GroupBox for the line labels and edit boxes
        groupBoxEdit = QGroupBox()
        # don't draw a frame
        groupBoxEdit.setFlat(True)
        
        # make GridLayout and add the labels
        self.editGrid = QGridLayout()
        # have class member for row, so that new rows can be added on the fly
        self.row = 0
        # put labels in Grid
        for n in range(self.ncols):
            self.editGrid.addWidget(labels[n], self.row, n)

        # put the GridLayout in the GroupBox
        groupBoxEdit.setLayout(self.editGrid)

        # overall dialog layout is VBox
        layout = QVBoxLayout()
        # add the GroupBoxes to the VBox
        layout.addWidget(groupBoxBtn)
        layout.addWidget(groupBoxEdit)
        
        # add LineEdit objects
        self.addLine()
        
        # set the VBox as the layout
        self.setLayout(layout)
        
        self.resize(570, 130)
        self.setWindowTitle('Add data')
        

    @property
    def shape(self):
        """ Return tuple of (width, height) """
        return self.size().width(), self.size().height()
        
    def makeLine(self):
        """ Make and initialise QLineEdit objects """
        
        edits = list(QLineEdit(self) for n in range(self.ncols))
        
        # set today's set in the Date column
        edits[0].setText(str_to_date('').strftime(datefmt))
            
        return tuple(edits)


    def addLine(self):
        """ Add new line to Dialog """
        
        # make new row
        fields = self.makeLine()
        # keep all rows in a list, so their contents can be accessed
        self.rows.append(fields)
        
        # increment row
        self.row += 1
        
        for n in range(self.ncols):
            self.editGrid.addWidget(fields[n], self.row, n)
        
        
    def set_new_values(self):
        """ Put new csv data into Data object. """
        
        new_rows = []
        
        error = False
        
        # get text from every QLineEdit
        for row in self.rows:
            
            line = [field.text() for field in row]
            
            if '' not in line:
            
                # format date and duration
                # catch any exception thrown if the value entered cannot be parsed
                try:
                    line[0] = str(str_to_date(line[0]))
                except ValueError:
                    self.invalid_value_message(line[0])
                    error = True
                    
                try:
                    line[1] = format_duration(line[1])
                except ValueError:
                    self.invalid_value_message(line[1])
                    error = True
                    
                new_rows.append(line)
                    
        if not error:
            for row in new_rows:
                self.data.addRow(row)
            self.accept()
        
    def empty_value_message(self, line):
        title = 'Could not add line!'
        message = 'Empty fields in entry. This line will not be added.'
        QMessageBox.warning(self, title, message)
        
    def invalid_value_message(self, value):
        title = 'Could not add line!'
        message = "'{}' contains an invalid value.".format(value)
        QMessageBox.warning(self, title, message)


class TableLineDiaolg(QDialog_CTRL_Q):
    
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, data):
        """ Base class for displaying the timesheet as a table for editing.
        
            Implementations of `customise()` and `apply_changes()` will need
            to be provided.
            You may wish to set `self.explain.setText()` and 
            `self.setWindowTitle()` in `customise()`.
            
            Parameters
            ----------
            data : Data object
                object which holds all the csv data
        """
        super().__init__()
        
        self.initUI(data)
        
        self.customise()
        
    def initUI(self, data):
        
        self.data = data
        
        self.nrows, self.ncols = self.data.shape

        # make table
        self.table = QTableWidget(self.nrows, self.ncols)
        # remove numbers from rows
        self.table.verticalHeader().setVisible(False)
        # set headers
        self.table.setHorizontalHeaderLabels(self.data.columns)

        # put data in table (in reverse order)
        for row in range(self.nrows):
            d = self.data[self.nrows-row-1]
            for n, datum in enumerate(d):
                item = QTableWidgetItem(str(datum))
                self.table.setItem(row, n, item)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | 
                                     QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.apply_changes)
        buttonBox.rejected.connect(self.reject)
        
        for i in range(self.nrows):
           self.table.setColumnWidth(i, 110)
        
        # for some reason, self.table.width() returns a number larger than
        # it should be
        # and just using ncols * columnWidth puts a scrollbar on the bottom,
        # which is annoying, so I've widened it slightly
        width = (self.ncols + 0.05) * self.table.columnWidth(0)
        
        # exaplin how this window works
        # self.explain.setText() should be applied in the derived classes
        self.explain = QLabel(wordWrap=True)
        self.explain.setMinimumWidth(width)
        self.explain.setText('')
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.explain)
        self.layout.addWidget(self.table)
        self.layout.addWidget(buttonBox)

        self.resize(width, 400)
        
        self.setLayout(self.layout)
        
        self.setWindowTitle('Table dialog')
    
    @abc.abstractmethod    
    def customise(self): pass
    
    @abc.abstractmethod
    def apply_changes(self): pass
    
        
class RemoveLineDialog(TableLineDiaolg):
    
    def __init__(self, data):
        """ Remove lines from the csv file.
        
            Parameters
            ----------
            data : Data object
                object which holds all the csv data
        """
        super().__init__(data)
        
        
    def customise(self):
        # only select rows
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        self.explain.setText('Select rows and click "OK" to remove them from '
                             'the csv file.\nThis cannot be undone, so please '
                             'be careful!')
        
        self.setWindowTitle('Remove entries')
        
        
    def apply_changes(self):
        """ Remove selected rows from the csv file. """
        self.selected = self.table.selectedItems()
        
        rows = list(set(item.row() for item in self.selected))
        rows.sort()
        
        for idx in rows:
            idx = self.nrows - idx - 1
            self.data.removeRow(idx)

        self.accept()
        
        
class EditLineDialog(TableLineDiaolg):
    
    def __init__(self, data):
        """ Edit lines in the csv file.
        
            Parameters
            ----------
            data : Data object
                object which holds all the csv data
        """
        super().__init__(data)
        
    def customise(self):
        
        self.explain.setText('Edit rows in the csv file.')
        self.setWindowTitle('Edit entries')

    def apply_changes(self):
        # check every item in the table against the csv data 
        
        for row in range(self.nrows):
            for col in range(self.ncols):
                item = self.table.item(row, col)
                
                df_row = self.nrows - row - 1
                
                if item is not None:
                    # cast to float/string, as for some reason, items that
                    # appear to be the same return False when == is applied
                    try:
                        t = float(item.text())
                        d = float(self.data[df_row,col])
                    except ValueError:
                        t = str(item.text())
                        d = str(self.data[df_row,col])
                        
                    # if item in table is different from item in csv, write
                    # to csv
                    if t != d:
                        self.data[df_row, col] = t
                    
        self.accept()
        
