# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_ReportsDockWidget.py

@author: Mark
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id:$

History:
Mark 2008-01-05: Created.
"""
from HistoryWidget import HistoryWidget
from PyQt4.Qt import Qt, QDockWidget, QWidget, QVBoxLayout, QTabWidget
from PyQt4.Qt import QPalette, QSizePolicy
from PM.PM_Colors import pmGrpBoxColor
from PM.PM_Colors import getPalette
from PlatformDependent import make_history_filename
from qt4transition import qt4todo
import env

class Ui_ReportsDockWidget(QDockWidget):
    """
    The Ui_ReportsDockWidget class provides a DockWidget containing a tabbed
    widget providing convenient access to "reports". It is docked at the 
    bottom of the NE1 main window.
    
    Currently, the history widget is the only report available. 
    
    Future ideas for inclusion:
    - Python command line tab
    - NE1 command line tab
    - NE1 Job Manager tab
    """
    _title         =  "Reports"
    
    def __init__(self, win):
        """
        Constructor for Ui_ReportsDockWidget.
        @param win: The main window
        @type  win: QMainWindow
        """
        QDockWidget.__init__(self, win)
        
        #Define layout
        self._containerWidget = QWidget()
        self.setWidget(self._containerWidget)        
        
        # Create vertical box layout
        self.vBoxLayout = QVBoxLayout(self._containerWidget)
        vBoxLayout = self.vBoxLayout
        vBoxLayout.setMargin(0)
        vBoxLayout.setSpacing(0)
        
        self.setEnabled(True) 
        self.setFloating(False)
        self.setVisible(True)
        self.setWindowTitle(self._title)
        self.setAutoFillBackground(True)
        self.setPalette(getPalette( None,
                                    QPalette.Window,
                                    pmGrpBoxColor))
        
        # Create the reports tabwidget. It will contain the history tab
        # and possibly other tabs containing reports.
        self.reportsTabWidget = QTabWidget()
        self.reportsTabWidget.setObjectName("reportsTabWidget")
        self.reportsTabWidget.setCurrentIndex(0)
        self.reportsTabWidget.setAutoFillBackground(True)
        vBoxLayout.addWidget(self.reportsTabWidget)

        # Create the history tab. It will contain the history widget.
        self.historyTab = QWidget()
        self.historyTab.setObjectName("historyTab")
        self.reportsTabWidget.addTab(self.historyTab, "History") 

        self.historyTabLayout = QVBoxLayout(self.historyTab)
        historyTabLayout = self.historyTabLayout
        historyTabLayout.setMargin(0)
        historyTabLayout.setSpacing(0)
        
        self._addHistoryWidget()
        
        self.setMinimumHeight(100)
        self.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Expanding),
                            QSizePolicy.Policy(QSizePolicy.Expanding)))
        
        win.addDockWidget(Qt.BottomDockWidgetArea, self)
        
    def _addHistoryWidget(self):
        """
        Sets up and adds the history widget.
        """
        histfile = make_history_filename() 
            #@@@ ninad 061213 This is likely a new bug for multipane concept 
            # as each file in a session will have its own history widget
        qt4todo('histfile = make_history_filename()')

        #bruce 050913 renamed self.history to self.history_object, and
        # deprecated direct access to self.history; code should use env.history
        # to emit messages, self.history_widget to see the history widget,
        # or self.history_object to see its owning object per se
        # rather than as a place to emit messages (this is rarely needed).
        self.history_object = HistoryWidget(self, filename = histfile, mkdirs = 1)
            # this is not a Qt widget, but its owner;
            # use self.history_widget for Qt calls that need the widget itself.
        self.history_widget = self.history_object.widget
        self.history_widget.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
            # bruce 050913, in case future code splits history widget 
            # (as main window subwidget) from history message recipient
            # (the global object env.history).
        env.history = self.history_object #bruce 050727, revised 050913
        
        self.historyTabLayout.addWidget(self.history_widget)