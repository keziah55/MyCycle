"""
Plot cycling data
"""

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QAction, QDesktopWidget, QFileDialog, QGroupBox, 
                             QHBoxLayout, QPushButton, QRadioButton, 
                             QVBoxLayout, QWidget)

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg, 
                                                NavigationToolbar2QT)
import numpy as np
from datetime import datetime


class PlotDialog(QWidget):
    def __init__(self, data, scheme='dark'):
        super().__init__()
        
        self.data = data
        self.scheme = scheme

        # a figure instance to plot on
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvasQTAgg(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar2QT(self.canvas, self)        
        
        schemeBtn1 = QRadioButton('dark')
        schemeBtn2 = QRadioButton('light')
        
        if self.scheme == 'dark':
            schemeBtn1.setChecked(True)
            self.set_scheme_dark()
        elif self.scheme == 'light':
            schemeBtn2.setChecked(True)
            self.set_scheme_light()
        else:
            raise ValueError("'scheme' should be 'dark' or 'light'")
        
        schemeBtn1.toggled.connect(self.set_scheme_dark)
        schemeBtn2.toggled.connect(self.set_scheme_light)       
        
        groupBox = QGroupBox() 
        
        groupBoxRadio = QGroupBox()
        
        schemeBtnBox = QHBoxLayout()
        schemeBtnBox.addWidget(schemeBtn1)
        schemeBtnBox.addWidget(schemeBtn2)
        
        groupBoxRadio.setLayout(schemeBtnBox)
        groupBoxRadio.setFixedSize(180,35)
        
        self.exportBtn = QPushButton("&Export pdf")
        self.exportBtn.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_E))
        self.exportBtn.clicked.connect(self.export)
        
        allBox = QHBoxLayout()
        allBox.addWidget(groupBoxRadio)
        allBox.addWidget(self.exportBtn)
        
        groupBox.setLayout(allBox)
        groupBox.setFixedSize(300,50)

        # set the layout
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(groupBox)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
        self.resize(650,650)
        self.centre()
        
        self.setWindowTitle('Plot stats')
        
        self.exitAct = QAction("E&xit", self, 
                               shortcut=QKeySequence(Qt.CTRL + Qt.Key_Q),
                               statusTip="Exit the application", 
                               triggered=self.close)
        self.addAction(self.exitAct)
        
    def centre(self):
        """ Centre window on screen. """
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        
    def set_scheme_dark(self):
        self.scheme = 'dark'
        self.plot()
        
    def set_scheme_light(self):
        self.scheme = 'light'
        self.plot()
        
    def export(self):
        facecolor = self.colour_schemes[self.scheme]['bg_col']
        
        filename, _ = QFileDialog.getSaveFileName(self, 'Export pdf',
            'cycling.pdf', 'PDF Files (*.pdf)', options=QFileDialog.Options())
        
        if filename:
            self.figure.savefig(filename, format='pdf', facecolor=facecolor)
            self.figure.clf()

    def plot(self):
        
        self.figure.clf()
        
        dflen = len(self.data)
        
        time_sec = np.array(list(self._minsec_to_sec(time) 
                            for time in self.data.getColumn('Time')))
        
        dist_norm = np.array(list(self._normalise(time_sec[n], 
                                                  self.data[n,'Distance (km)'],
                                                  wrt='hr') 
                             for n in range(dflen)))
            
        cal_norm = np.array(list(self._normalise(time_sec[n], 
                                                 self.data[n,'Calories']) 
                            for n in range(dflen)))
            
        dates = list(datetime.strptime(date, '%Y-%m-%d').date() 
                     for date in self.data.getColumn('Date'))
        
        # TODO staircase doesn't quite work yet: the last one doesn't appear
        dates_long = [dates[0]] + [i for i in dates[1:] for n in range(2)]
        
        odo = self.data.getColumn('Odometer (km)')
        odo_long = [i for i in odo[:-1] for n in range(2)]
        
        fill_style = ['mountain', 'staircase']
        background_fill = fill_style[0]
        
        # make axes
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()
        
        # define colour schemes
        light_colours = {'ax1_col':'green', 'ax2_col1':'lightskyblue',
                         'ax2_col2':'dodgerblue', 'bg_col':'white', 
                         'fg_col':'black'}
        dark_colours  = {'ax1_col':'lime', 'ax2_col1':'dodgerblue',
                         'ax2_col2':'dodgerblue', 'bg_col':'#393f45', 
                         'fg_col':'white'}
        
        self.colour_schemes = {'light':light_colours, 'dark':dark_colours}

        ax1_col = self.colour_schemes[self.scheme]['ax1_col']
        ax2_col1 = self.colour_schemes[self.scheme]['ax2_col1']
        ax2_col2 = self.colour_schemes[self.scheme]['ax2_col2']
        bg_col = self.colour_schemes[self.scheme]['bg_col']
        fg_col = self.colour_schemes[self.scheme]['fg_col']
        
        ax1.tick_params(axis='x', colors=fg_col)
        ax1.spines['bottom'].set_color(fg_col)
        ax1.spines['top'].set_color(fg_col) 
        ax1.spines['right'].set_color(fg_col)
        ax1.spines['left'].set_color(fg_col)
        
        self.figure.patch.set_facecolor(bg_col)
        ax1.set_facecolor(bg_col)
        
        # ax1 y data
        ax1.plot_date(dates, dist_norm, color=ax1_col, marker='x')
        ax1.set_ylabel('Avg. speed (km/h)', color=ax1_col)
        ax1.tick_params('y', color=ax1_col, labelcolor=ax1_col)
        
        # ax2 y data
        if background_fill == 'mountain':
            ax2.plot_date(dates, odo, color=ax2_col1, marker='', xdate=True) 
            ax2.fill_between(dates, odo, facecolor=ax2_col1)
        
        elif background_fill == 'staircase':
            ax2.plot_date(dates_long, odo_long, color=ax2_col1, marker='') 
            ax2.fill_between(dates_long, 0, odo_long, facecolor=ax2_col1)
            
#        ax2.set_ylim(bottom=75)
        ax2.set_ylabel('Total distance (km)', color=ax2_col2)
        ax2.tick_params('y', colors=ax2_col2, labelcolor=ax2_col2)
        
        
        # put ax1 in front of ax2
        ax1.set_zorder(ax2.get_zorder()+1)
        ax1.patch.set_visible(False) # hide the 'canvas' 
        
        # x axis settings
        ax1.set_xlabel('Date', color=fg_col)
        ax1.tick_params('x', labelrotation=70)
        
        # make sure dates don't go off the bottom of the figure
        self.figure.tight_layout()
    
        # refresh canvas
        self.canvas.draw()
            
    @staticmethod
    def _minsec_to_sec(s):
        
        s_spl = s.split(':')
        s_spl = list(map(int, s_spl))
        
        try:
            mns, sec = s_spl
        except ValueError:
            mns = s_spl[0]
            sec = 0
            
        total = 60 * mns + sec
        
        return total
    
    @staticmethod
    def _normalise(time, value, wrt='min'):
        # Normalise a value 
        # `time` should be in seconds
        # `wrt` should be 'sec', 'min' or 'hr'
        
        factor = {'sec':1, 'min':60, 'hr':3600}
        
        mult = factor[wrt]
        
        return mult * value / time

