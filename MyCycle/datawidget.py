"""
Make single widget containing personal best and csv data QTextEdits.
This widget will be set as the main window's central widget.
"""

from PyQt5.QtWidgets import (QTextEdit, QWidget, QVBoxLayout, QSizePolicy,
                             QMessageBox)
from processcsv import csv_to_html 
from analysedata import get_best_session, get_best_month, get_best_days


def tag(tag, s, attr=''):
    """ Wrap a string in an html tag
    
        Paramters
        ---------
        tag : str
            html tag
        s : str
            string to be wrapped
        attr : str, optional
            atrribute string
    """
    return '<'+tag+' '+attr+'>' + s + '</'+tag+'>'

def bold(s):
    """ Wrap a string in html bold tag """
    return tag('b', s)


class DataWidget(QWidget):
    
    def __init__(self, data):
        super().__init__()
        self.initUI(data)
        
    def initUI(self, data):   
        
        self.data = data

        layout = QVBoxLayout()
        
        self.pb = QTextEdit(readOnly=True)
        self.ad = QTextEdit(readOnly=True)
        
        self.pb.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.ad.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        layout.addWidget(self.pb)
        layout.addWidget(self.ad)
        
        self.setLayout(layout)
        
        self.pb_session, _ = self.getPBsession()
        self.pb_month, _ = self.getPBmonth()
        self.pb_days, _ = self.getPBdays()
        
        
    def setHtml(self):
        """ Set text in both Personal Best and All CSV Data widgets. """
        if len(self.data) > 0:
            self.setCsvData()
            self.setPB()
        
    def setCsvData(self):
        # set csv data QTextEdit
        ad_text = csv_to_html(str(self.data))
        self.ad.setHtml(ad_text)
        
    def setPB(self):
        # set Personal Best QTextEdit
        pb_text = self.getPB()
        self.pb.setHtml(pb_text)

    def getPB(self):
        # get all Personal Best data
        pb_session, pb_session_text = self.getPBsession()
        pb_month, pb_month_text = self.getPBmonth()
        pb_days, pb_days_text = self.getPBdays()
        
        best_session = tag('b', 'Best Session:')
        best_session = tag('div', best_session, 'style="font-size:18px"')
        
        best_month = tag('b', 'Best Month:')
        best_month = tag('div', best_month, 'style="font-size:18px"')
        
        best_days = tag('b', 'Longest streak:')
        best_days = tag('div', best_days, 'style="font-size:18px"')
        
        text = '\n' + best_session# + '\n<br>\n'
        text += tag('div', pb_session_text, 'style="font-size:16px"') #+ '\n<br>\n' 
        text += best_month + tag('div', pb_month_text, 'style="font-size:16px"') 
        text += best_days + tag('div', pb_days_text, 'style="font-size:16px"')
        
        self._comparePB(pb_session, pb_month, pb_days)
        
        self.pb_session = pb_session
        self.pb_month = pb_month
        self.pb_days = pb_days
        
        return text
    
    
    def _comparePB(self, pb_session, pb_month, pb_days):
        
        changes = {}
        
        if pb_session != self.pb_session:
            changes['session'] = pb_session
        
        if pb_month != self.pb_month:
            changes['month'] = pb_month
        
        if pb_days != self.pb_days:
            changes['days'] = pb_days
            
        if changes:
            pl = 's' if len(changes) > 0 else ''
            text = f"Congratulations! New PB{pl} set!\n"
            for key, value in changes.items():
                text += f"{key.capitalize()}: {value}\n"
            self.msgbox = QMessageBox(QMessageBox.NoIcon, 'New personal best!', 
                                      text, QMessageBox.Ok)
            self.msgbox.exec()
        
    def getPBsession(self):
        # get best session
        best, when = get_best_session(self.data)
        text = bold('{:.3f} km/h'.format(best))
        text += ' achieved on {}'.format(when)
        
        return best, text
    
    def getPBmonth(self):
        # get best month
        best, when, time, cal = get_best_month(self.data)
        text = f'{when}: '
        text += bold(f' {best:.2f} km') 
        text += ', total time: ' + bold(time) 
        text += ', calories: ' + bold(f'{cal:.2f}')
        
        return best, text
    
    def getPBdays(self):
        best, first, last = get_best_days(self.data)
        text = bold(f'{best} days') 
        text += f', from {first} to {last}'
        return best, text