#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edit my cycling data
"""

import sys
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (QAction, QApplication, QDesktopWidget, 
                             QMainWindow, QMessageBox, QTextEdit)

from dataobject import Data
from editdialogs import AddLineDialog, RemoveLineDialog, EditLineDialog
from plotdialog import PlotDialog
from processcsv import csv_to_html  
    
class MyCycle(QMainWindow):
    
    def __init__(self):
        
        super().__init__()
        
        self.initUI()
        
    def initUI(self):
        
        self.data = Data('../data/me.csv')

        self.textEdit = QTextEdit(readOnly=True)
        
        # display text (as html)
        self.update_display()

        self.setCentralWidget(self.textEdit)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        
        self.statusBar()
        self.statTimeout = 1000
        
        self.setWindowIcon(QIcon(''))  
        self.setWindowTitle('MyCycle')
        self.resize(500, 500)
        self.centre()
        
        self.show()
        
    def centre(self):
        """ Centre window on screen. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def update_display(self):
        """ Update text and window title """
        print('update_display')
        self.textEdit.setHtml(csv_to_html(self.data.csv_data))
        print(self.data.csv_data)
        if self.data.modified:
            self.statusBar().showMessage('Updated', self.statTimeout)
            
    def plotData(self):
        """ Plot graph. """
        scheme = self.getColourScheme()
        self.pld = PlotDialog(self.data, scheme)
        self.pld.show()
        
    def getColourScheme(self):
        """ Set light or dark colour scheme for plotData """
        
        system_theme = QIcon.themeName()
        if 'dark' in system_theme:
            scheme = 'dark'
        else:
            scheme = 'light'
        return scheme
            
    def addLine(self):
        """ Add line(s) to csv. """
        self.ald = AddLineDialog(self.data, self.data.columns)
        self.ald.show()
        self.ald.accepted.connect(self.update_display)
        
    def removeLine(self):
        """ Remove line(s) from csv. """
        self.rld = RemoveLineDialog(self.data)
        self.rld.show()
        self.rld.accepted.connect(self.update_display)
            
    def editEntries(self):
        """ Edit csv data. """
        self.ed = EditLineDialog(self.data)
        self.ed.show()
        self.ed.accepted.connect(self.update_display)

    def save(self):
        # use Data's save method
        if self.data.save():
            self.statusBar().showMessage('Saved', self.statTimeout)
            
    def closeEvent(self, event):
        # save the csv file and close the window
        self.save()
        event.accept()
                
    def about(self):
        QMessageBox.about(self, "About MyCycle", 
                          "Update and plot my cycling stats.")
 
    def createActions(self):
        
        self.saveAct = QAction(QIcon.fromTheme('document-save'), "&Save", self,
                               shortcut=QKeySequence.Save,
                               statusTip="Save the csv", triggered=self.save)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                               statusTip="Exit the application", 
                               triggered=self.close)
        
        self.plotAct = QAction(QIcon.fromTheme('image-x-generic'), "&Plot",  
                               self, shortcut=QKeySequence("P"), 
                               statusTip="Plot the data", 
                               triggered=self.plotData)

        self.abtAct  = QAction("&About", self,
                               statusTip="Show the application's About box",
                               triggered=self.about)
        
        self.addAct  = QAction(QIcon.fromTheme('list-add'), "Add", self,
                               shortcut=QKeySequence("N"), 
                               statusTip="Add new data",
                               triggered=self.addLine)
        
        self.rmvAct  = QAction(QIcon.fromTheme('list-remove'), 
                               "Remove", self, shortcut="Ctrl+R", 
                               statusTip="Remove data", 
                               triggered=self.removeLine)
        
        self.editAct = QAction(QIcon.fromTheme(''), "Edit", self,
                               shortcut="Ctrl+E", statusTip="Edit data",
                               triggered=self.editEntries)


    def createMenus(self):
        
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.plotAct)
        self.fileMenu.addSeparator();
        self.fileMenu.addAction(self.exitAct)
        
        self.editMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.addAct)
        self.editMenu.addAction(self.rmvAct)
        self.editMenu.addAction(self.editAct)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.abtAct)

    def createToolBars(self):
        
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addAction(self.plotAct)
        
        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.addAct)
#        self.editToolBar.addAction(self.rmvAct)
    

if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    window = MyCycle()
    sys.exit(app.exec_())
