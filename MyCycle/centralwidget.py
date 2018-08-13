"""
Make single widget containing personal best and csv data QTextEdits.
This widget will be set as the main window's central widget.
"""

from PyQt5.QtWidgets import (QTextEdit, QWidget, QVBoxLayout)
from processcsv import csv_to_html 
from analysedata import get_best_session, get_best_month


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


class CentralWidget(QWidget):
    
    def __init__(self, data):
        super().__init__()
        self.initUI(data)
        
    def initUI(self, data):   
        
        self.data = data

        layout = QVBoxLayout()
        
        self.pb = QTextEdit(readOnly=True)
        self.ad = QTextEdit(readOnly=True)
        
        layout.addWidget(self.pb)
        layout.addWidget(self.ad)
        
        layout.setStretchFactor(self.pb, 1)
        layout.setStretchFactor(self.ad, 2)
        
        self.setLayout(layout)
        
        
    def setHtml(self):
        """ Set text in both Personal Best and All CSV Data widgets. """
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
        pb_session = self.getPBsession()
        pb_month = self.getPBmonth()
        
        best_session = tag('b', 'Best Session:')
        best_session = tag('div', best_session, 'style="font-size:18px"')
        
        best_month = tag('b', 'Best Month:')
        best_month = tag('div', best_month, 'style="font-size:18px"')
        
        text = '\n' + best_session# + '\n<br>\n'
        text += tag('div', pb_session, 'style="font-size:16px"') #+ '\n<br>\n' 
        text += best_month + tag('div', pb_month,  'style="font-size:16px"') 
        
        return text
        
    def getPBsession(self):
        # get best session
        best, when = get_best_session(self.data)
        text = bold('{:.3f} km/h'.format(best))
        text += ' achieved on {}'.format(when)
        
        return text
    
    def getPBmonth(self):
        # get best month
        best, when, time, cal = get_best_month(self.data)
        text = '{}: '.format(when)
        text += bold(' {:.2f} km'.format(best)) 
        text += ', total time: ' + bold(time) 
        text += ', calories: ' + bold('{:.2f}'.format(cal))
        
        return text
    