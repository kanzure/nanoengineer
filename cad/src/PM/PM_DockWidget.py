# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_DockWidget.py

@author: Ninad
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2007-11-20: Created to implement SequenceEditor

TODO:
- Add more documentation
NOTE: methods addPmWidget and getPmWidgetPlacementParameters are duplicated from
PM_GroupBox
"""
from PyQt4.Qt import QDockWidget 
from PyQt4.Qt import QLabel, QPalette
from PyQt4.Qt import Qt, QWidget, QVBoxLayout, QGridLayout

from PM.PM_Colors    import getPalette
from PM.PM_Colors import pmGrpBoxColor
from PM.PM_CheckBox import PM_CheckBox
from PM.PM_Constants import pmLeftAlignment, pmRightAlignment
from icon_utilities import getpixmap

class PM_DockWidget(QDockWidget):
    """
    PM_DockWidget class provides a dockable widget that can either be docked 
    inside a PropertyManager OR can be docked in the MainWindow depending 
    on the <parentWidget> . see SequenceEditor.py for an example.
    The dockWidget has its own layout and containerwidget which makes it easy 
    to add various children widgets  similar to how its done in PM_GroupBox    
    """   
    labelWidget  = None    
    _title         = ""
    _widgetList    = []
    _rowCount      = 0    
    
    def __init__(self, parentWidget, title = ""):
        """
        """
        QDockWidget.__init__(self, parentWidget)
        
        self.parentWidget = parentWidget        
        
        self._title = title
        
        self.label = ''
        self.labelColumn = 0
        self.spanWidth = True
        self.labelWidget = None
        
        if self.label: # Create this widget's QLabel.
            self.labelWidget = QLabel()
            self.labelWidget.setText(self.label)
            
        self.setEnabled(True) 
        self.setFloating(False)
        self.setVisible(True)
        self.setWindowTitle(self._title)
        self.setAutoFillBackground(True)
        self.setPalette(getPalette( None,
                                    QPalette.Window,
                                    pmGrpBoxColor))

       
        self.parentWidget.addDockWidget(Qt.BottomDockWidgetArea, self)
        
        #Define layout
        self._containerWidget = QWidget()
        self.setWidget(self._containerWidget)        
        
        # Create vertical box layout
        self.vBoxLayout = QVBoxLayout(self._containerWidget)
        self.vBoxLayout.setMargin(1)
        self.vBoxLayout.setSpacing(0)
        
        # Create grid layout
        self.gridLayout = QGridLayout()
        self.gridLayout.setMargin(1)
        self.gridLayout.setSpacing(1)
        
        # Insert grid layout in its own vBoxLayout
        self.vBoxLayout.addLayout(self.gridLayout)
                         
        #self.parentWidget.addPmWidget(self)
        self._loadWidgets()
    
    def _loadWidgets(self):
        """
        Subclasses should override this method. Default implementation does 
        nothing. 
        @see: SequenceEditor._loadWidgets 
        """
        pass
    
    def getPmWidgetPlacementParameters(self, pmWidget):
        """
        NOTE: This method is duplicated from PM_GroupBox
        
        Returns all the layout parameters needed to place 
        a PM_Widget in the group box grid layout.
        
        @param pmWidget: The PM widget.
        @type  pmWidget: PM_Widget
        """        
        row = self._rowCount
        
        #PM_CheckBox doesn't have a label. So do the following to decide the 
        #placement of the checkbox. (can be placed either in column 0 or 1 , 
        #This also needs to be implemented for PM_RadioButton, but at present 
        #the following code doesn't support PM_RadioButton. 
        if isinstance(pmWidget, PM_CheckBox):
            # Set the widget's row and column parameters.
            widgetRow      = row
            widgetColumn   = pmWidget.widgetColumn
            widgetSpanCols = 1
            widgetAlignment = pmLeftAlignment
            rowIncrement   = 1
            #set a virtual label
            labelRow       = row
            labelSpanCols  = 1
            labelAlignment = pmRightAlignment
                        
            if widgetColumn == 0:
                labelColumn   = 1                              
            elif widgetColumn == 1:
                labelColumn   = 0
            
            return (widgetRow, 
                    widgetColumn, 
                    widgetSpanCols, 
                    widgetAlignment,
                    rowIncrement, 
                    labelRow, 
                    labelColumn, 
                    labelSpanCols, 
                    labelAlignment)
        
       
        label       = pmWidget.label            
        labelColumn = pmWidget.labelColumn
        spanWidth   = pmWidget.spanWidth
        
        if not spanWidth: 
            # This widget and its label are on the same row
            labelRow       = row
            labelSpanCols  = 1
            labelAlignment = pmRightAlignment
            # Set the widget's row and column parameters.
            widgetRow      = row
            widgetColumn   = 1
            widgetSpanCols = 1
            widgetAlignment = pmLeftAlignment
            rowIncrement   = 1
            
            if labelColumn == 1:
                widgetColumn   = 0
                labelAlignment = pmLeftAlignment
                widgetAlignment = pmRightAlignment
                        
        else: 
                      
            # This widget spans the full width of the groupbox           
            if label: 
                # The label and widget are on separate rows.
                # Set the label's row, column and alignment.
                labelRow       = row
                labelColumn    = 0
                labelSpanCols  = 2
                    
                # Set this widget's row and column parameters.
                widgetRow      = row + 1 # Widget is below the label.
                widgetColumn   = 0
                widgetSpanCols = 2
                
                rowIncrement   = 2
            else:  # No label. Just the widget.
                labelRow       = 0
                labelColumn    = 0
                labelSpanCols  = 0

                # Set the widget's row and column parameters.
                widgetRow      = row
                widgetColumn   = 0
                widgetSpanCols = 2
                rowIncrement   = 1
                
            labelAlignment = pmLeftAlignment
            widgetAlignment = pmLeftAlignment
                
        return (widgetRow, 
                widgetColumn, 
                widgetSpanCols, 
                widgetAlignment,
                rowIncrement, 
                labelRow, 
                labelColumn, 
                labelSpanCols, 
                labelAlignment)
        
    def addPmWidget(self, pmWidget):
        """
        Add a PM widget and its label to this group box.
        
        @param pmWidget: The PM widget to add.
        @type  pmWidget: PM_Widget
        """
        
        # Get all the widget and label layout parameters.
        widgetRow, \
        widgetColumn, \
        widgetSpanCols, \
        widgetAlignment, \
        rowIncrement, \
        labelRow, \
        labelColumn, \
        labelSpanCols, \
        labelAlignment = self.getPmWidgetPlacementParameters(pmWidget)        
        
        
        if pmWidget.labelWidget: 
            #Create Label as a pixmap (instead of text) if a valid icon path 
            #is provided
            labelPath = str(pmWidget.label)
            if labelPath:
                labelPixmap = getpixmap(labelPath)
                if not labelPixmap.isNull():
                    pmWidget.labelWidget.setPixmap(labelPixmap)
                    pmWidget.labelWidget.setText('')
               
            self.gridLayout.addWidget( pmWidget.labelWidget,
                                       labelRow, 
                                       labelColumn,
                                       1, 
                                       labelSpanCols,
                                       labelAlignment )
            
        
        # The following is a workaround for a Qt bug. If addWidth()'s 
        # <alignment> argument is not supplied, the widget spans the full 
        # column width of the grid cell containing it. If <alignment> 
        # is supplied, this desired behavior is lost and there is no 
        # value that can be supplied to maintain the behavior (0 doesn't 
        # work). The workaround is to call addWidget() without the <alignment>
        # argument. Mark 2007-07-27.
        if widgetAlignment == pmLeftAlignment:
            self.gridLayout.addWidget( pmWidget,
                                       widgetRow, 
                                       widgetColumn,
                                       1, 
                                       widgetSpanCols) 
                                       # aligment = 0 doesn't work.
        else:
            self.gridLayout.addWidget( pmWidget,
                                       widgetRow, 
                                       widgetColumn,
                                       1, 
                                       widgetSpanCols,
                                       widgetAlignment)        
        self._rowCount += rowIncrement
        