""" 
Dialogs required by Timesheet when adding or removing data.
Supplies AddLineDialog, NewRateDialog, and RemoveLineDialog.
"""

from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtCore import Qt
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
    
    def __init__(self, data):
        """ Add lines to csv file. 
            
            Parameters
            ----------
            data : Data object
                object which holds all the csv data
        """
        super().__init__()
        
        self.initUI(data)
        
        
    def initUI(self, data):
        
        # 'data' is the csv/config data object
        self.data = data
        
        self.newData = ''
        
        self.rows = []
        
        # message for main window status bar
        self.msg = ''
        
        newButton = QPushButton(QIcon.fromTheme('list-add'), '')
        newButton.setMinimumWidth(70)
        newButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        newButton.clicked.connect(self.addLine)
        
        rmvButton = QPushButton(QIcon.fromTheme('list-remove'), '')
        rmvButton.setMinimumWidth(70)
        rmvButton.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
        rmvButton.clicked.connect(self.rmvLine)
        
        self.dateLabel = QLabel('Date')
        self.timeLabel = QLabel('Time')
        self.distLabel = QLabel('Distance (km)')
        self.calLabel = QLabel('Calories') 
        self.odoLabel = QLabel('Odometer (km)') 

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
#        dialogBtnBox.addWidget(rmvButton)
        dialogBtnBox.addWidget(buttonBox)
        
        # put the HBox in the GroupBox
        groupBoxBtn.setLayout(dialogBtnBox)
        groupBoxBtn.setFixedSize(260,50)
        
        # make GroupBox for the line labels and edit boxes
        groupBoxEdit = QGroupBox()
        # don't draw a frame
        groupBoxEdit.setFlat(True)
        
        # make GridLayout and add the labels
        self.editGrid = QGridLayout()
        # have class member for row, so that new rows can be added on the fly
        self.row = 0
        self.editGrid.addWidget(self.dateLabel, self.row, 0)
        self.editGrid.addWidget(self.timeLabel, self.row, 1)
        self.editGrid.addWidget(self.distLabel, self.row, 2)
        self.editGrid.addWidget(self.calLabel,  self.row, 3)
        self.editGrid.addWidget(self.odoLabel,  self.row, 4)
        
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
        
        self.width = 570
        self.resize(self.width, 130)
        self.setWindowTitle('Add data')
        

    @property
    def shape(self):
        return self.size().width(), self.size().height()
        
    def makeLine(self):
        """ Make and initialise QLineEdit objects. """
        
        self.dateEdit = QLineEdit(self)
        self.timeEdit = QLineEdit(self)
        self.distEdit = QLineEdit(self)
        self.calEdit  = QLineEdit(self)
        self.odoEdit  = QLineEdit(self)
        
        # display today's date and default rate
        self.dateEdit.setText((str_to_date('').strftime(datefmt)))
        self.timeEdit.setText('')
        self.distEdit.setText('')
        self.calEdit.setText('')
        self.odoEdit.setText('')

        return (self.dateEdit, self.timeEdit, self.distEdit, self.calEdit,
                self.odoEdit)
            
    def addLine(self):
        """ Add new line to Dialog """
        
        # make new row
        fields = self.makeLine()
        # keep all rows in a list, so their contents can be accessed
        self.rows.append(fields)
        # unpack QLineEdits
        da, t, di, c, o = fields
        
        # increment row
        self.row += 1
        
        self.editGrid.addWidget(da, self.row, 0)
        self.editGrid.addWidget(t, self.row, 1)
        self.editGrid.addWidget(di, self.row, 2)
        self.editGrid.addWidget(c, self.row, 3)
        self.editGrid.addWidget(o, self.row, 4)
        
#        print('Add: {}, {}'.format(*self.shape))
#        print('rowCount: {}'.format(self.editGrid.rowCount()))
        
        
    def rmvLine(self):
        
        try:
            self.rows.pop(-1)
        
            for col in range(5):
                item = self.editGrid.itemAtPosition(self.row, col)
                widget = item.widget()
                self.editGrid.removeWidget(widget)
                
            self.row -= 1
            
            lineHeight = widget.size().height()
            
            width, height = self.shape
            
            self.resize(width, height-lineHeight)
            
#            print('Rmv: {}, {}'.format(*self.shape))
#            print('rowCount: {}'.format(self.editGrid.rowCount()))
            
        except IndexError:
            title = 'Could not remove line'
            message = 'There are no more lines to remove!' 
            QMessageBox.warning(self, title, message)
            
        
    def set_new_values(self):
        """ Put new csv data into Data object. """
        
        self.newData = ''
        
        error = False
        
        # get text from every QLineEdit
        for row in self.rows:
            
            line = [field.text() for field in row]
            
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
            
            try:
                line = ','.join(line)
                self.newData += line + '\n'
            except TypeError:
                self.empty_value_message(line)
            
        if not error:
            self.data.add_new(self.newData)
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
        
        self.num_rows = len(self.data.csv_df)
        self.num_cols = len(self.data.columns)

        # make table
        self.table = QTableWidget(self.num_rows, self.num_cols)
        # remove numbers from rows
        self.table.verticalHeader().setVisible(False)
        # set headers
        self.table.setHorizontalHeaderLabels(self.data.columns)

        # put data in table
        for row, data in enumerate(self.data.csv_df):
            
            date, time, dist, cal, odo = data.split(',')
            
            item0 = QTableWidgetItem(date)
            item1 = QTableWidgetItem(time)
            item2 = QTableWidgetItem(dist)
            item3 = QTableWidgetItem(cal)
            item4 = QTableWidgetItem(odo)
            self.table.setItem(row, 0, item0)
            self.table.setItem(row, 1, item1)
            self.table.setItem(row, 2, item2)
            self.table.setItem(row, 3, item3)
            self.table.setItem(row, 4, item4)
            
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | 
                                     QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.apply_changes)
        buttonBox.rejected.connect(self.reject)
        
        for i in range(self.num_rows):
           self.table.setColumnWidth(i, 110)
        
        # for some reason, self.table.width() returns a number larger than
        # it should be
        width = 5.05*self.table.columnWidth(0)
        
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
        
        rows = set(item.row() for item in self.selected)
        
        for idx in rows:
            self.data.remove_line(idx)

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
        
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                item = self.table.item(row, col)
                
                if item is not None:
                    # cast to float/string, as for some reason, items that
                    # appear to be the same return False when == is applied
                    try:
                        t = float(item.text())
                        d = float(self.data[row,col])
                    except ValueError:
                        t = str(item.text())
                        d = str(self.data[row,col])
                        
                    # if item in table is different from item in csv, write
                    # to csv
                    if t != d:
                        self.data[row, col] = t
                    
        self.accept()
        
