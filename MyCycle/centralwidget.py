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
        
        self.pb.setFixedSize(500, 90)
        
        layout.addWidget(self.pb)
        layout.addWidget(self.ad)
        
        self.setLayout(layout)

        
    def setHtml(self):
        self.ad.setHtml(csv_to_html(str(self.data)))
        
        
    def setPB(self):
        pb_text = self.getPB()
        self.pb.setHtml(pb_text)
        
        
    def getPB(self):
        
        pb_session = self.getPBsession()
        pb_month = self.getPBmonth()
        
        text = '\n' + tag('b', 'Personal best') + '\n<br>\n'
        text += pb_session + '\n<br>\n' + pb_month
        text = tag('font', text, 'size=4')
        
        return text
        
        
    def getPBsession(self):
        
        best, when = get_best_session(self.data)
        text = bold('{:.3f} km/h'.format(best))
        text += ' achieved on {}'.format(when)
        
        return text
        
    
    def getPBmonth(self):
        
        best, when, time, cal = get_best_month(self.data)
        text = '{}: '.format(when)
        text += bold(' {:.2f} km'.format(best)) 
        text += ', total time: ' + bold(time) 
        text += ', calories: ' + bold('{:.2f}'.format(cal))
        
        return text
    