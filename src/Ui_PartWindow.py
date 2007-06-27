# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PartWindow.py provides the part window class.

$Id$

History: 

- PartWindow and GridPosition classes moved here from MWSemantics.py.
  Mark 2007-06-27
"""

from PyQt4.Qt import *
from GLPane import GLPane
from PropMgr_Constants import pmDefaultWidth, pmMaxWidth, pmMinWidth, pmColor
from Utility import geticon
from modelTree import modelTree
from qt4transition import qt4warnDestruction, qt4todo
import platform, env
from PropMgrBaseClass import printSizePolicy, printSizeHints, getPalette

class PartWindow(QWidget):
    def __init__(self, assy, parent):
        QWidget.__init__(self, parent)
        self.parent = parent
        self.setWindowTitle("My Part Window")
	self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
	
        pwHBoxLayout = QHBoxLayout(self)
        pwHSplitter = QSplitter(Qt.Horizontal)
        pwHSplitter.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Expanding)
        pwHBoxLayout.addWidget(pwHSplitter)

        #########################

	# <leftChannelWidget> - the container of all widgets left of the vertical splitter, 
	# next to the GLPane. 
        leftChannelWidget = QWidget(parent)
        leftChannelWidget.setMinimumWidth(pmMinWidth) # Mark 2007-05-24
	leftChannelWidget.setMaximumWidth(pmMaxWidth)
	
	leftChannelWidget.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Minimum),
                            QSizePolicy.Policy(QSizePolicy.Expanding))) #@ No affect?
			    
	leftChannelWidget.resize(pmDefaultWidth, leftChannelWidget.sizeHint().height())
        
        leftChannelVBoxLayout = QVBoxLayout(leftChannelWidget)
        leftChannelVBoxLayout.setMargin(0)
        leftChannelVBoxLayout.setSpacing(0)
        
	pwHSplitter.addWidget(leftChannelWidget)
	
        # Feature Manager - the QTabWidget that contains the MT and PropMgr.
	# I'll rename this later. --Mark

        self.featureManager = QTabWidget()
        self.featureManager.setCurrentIndex(0)
	self.featureManager.setAutoFillBackground(True)	
	
	#@ pmColor = 230,231,230. Fix this.
	self.featureManager.setPalette(
	    getPalette(None, QPalette.ColorRole(10), pmColor)) 
	
	#@ TEST CODE
	if 1:
	    self.featureManager.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Minimum),
                            QSizePolicy.Policy(QSizePolicy.Expanding))) #@ No affect?
			    
	    self.featureManager.resize(pmDefaultWidth, leftChannelWidget.sizeHint().height())
	#@ END TEST CODE
	
        self.modelTreeTab = QWidget()
        self.featureManager.addTab(self.modelTreeTab,geticon("ui/modeltree/Model_Tree"), "") 
	
        modelTreeTabLayout = QVBoxLayout(self.modelTreeTab)
        modelTreeTabLayout.setMargin(0)
        modelTreeTabLayout.setSpacing(0)
			
        self.propertyManagerTab = QWidget()
	
	self.propertyManagerScrollArea = QScrollArea(self.featureManager)
	self.propertyManagerScrollArea.setWidget(self.propertyManagerTab)
	self.propertyManagerScrollArea.setWidgetResizable(True) # Eureka! 
	# setWidgetResizable(True) will resize the Property Manager (and its contents)
	# correctly when the scrollbar appears/disappears. It even accounts correctly for 
	# collapsed/expanded groupboxes! Mark 2007-05-29
	
		
	self.featureManager.addTab(self.propertyManagerScrollArea, geticon("ui/modeltree/Property_Manager"), "")       
        leftChannelVBoxLayout.addWidget(self.featureManager)

        # Create the model tree (MT).

        self.modelTree = modelTree(self.modelTreeTab, parent)
        modelTreeTabLayout.addWidget(self.modelTree.modelTreeGui)

	pwVSplitter = QSplitter(Qt.Vertical, pwHSplitter)
        self.glpane = GLPane(assy, self, 'glpane name', parent)		    	
	qt4warnDestruction(self.glpane, 'GLPane of PartWindow')
        pwVSplitter.addWidget(self.glpane)
	
		
	from HistoryWidget import HistoryWidget
	
        histfile = platform.make_history_filename() #@@@ ninad 061213 This is likely a new bug for multipane concept 
	#as each file in a session will have its own history widget
	qt4todo('histfile = platform.make_history_filename()')
	
        #bruce 050913 renamed self.history to self.history_object, and deprecated direct access
        # to self.history; code should use env.history to emit messages, self.history_widget
        # to see the history widget, or self.history_object to see its owning object per se
        # rather than as a place to emit messages (this is rarely needed).
        self.history_object = HistoryWidget(self, filename = histfile, mkdirs = 1)
            # this is not a Qt widget, but its owner;
            # use self.history_widget for Qt calls that need the widget itself.
        self.history_widget = self.history_object.widget
	self.history_widget.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)
	
            #bruce 050913, in case future code splits history widget (as main window subwidget)
            # from history message recipient (the global object env.history).
        
        env.history = self.history_object #bruce 050727, revised 050913
	
	pwVSplitter.addWidget(self.history_widget)
	
	self.glpane.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Expanding),
                            QSizePolicy.Policy(QSizePolicy.Expanding)))
	
	#@self.history_widget.setSizePolicy(
        #@        QSizePolicy(QSizePolicy.Policy(QSizePolicy.Expanding),
        #@                    QSizePolicy.Policy(QSizePolicy.Preferred)))
	#@self.history_widget.resize(pmDefaultWidth, leftChannelWidget.sizeHint().height())
	
	pwHSplitter.addWidget(pwVSplitter)
	

    def setRowCol(self, row, col):
        self.row, self.col = row, col
	
    def updatePropertyManagerTab(self, tab): #Ninad 061207
	"Update the Properties Manager tab with 'tab' "
	
	if self.propertyManagerScrollArea.widget():
	    #The following is necessary to get rid of those c object deleted errors (and the resulting bugs)
	    lastwidgetobject = self.propertyManagerScrollArea.takeWidget() 
	    if lastwidgetobject:
		try:
		    lastwidgetobject.update_props_if_needed_before_closing()
		except:
		    if platform.atom_debug:
			msg1 = "Last PropMgr doesn't have method updatePropsBeforeClosing."
			msg2 =  " That is OK (for now,only implemented in GeometryGenerators)"
			msg3 = "Ignoring Exception"
			print_compact_traceback(msg1 + msg2 + msg3)
					    
	    lastwidgetobject.hide() # @ ninad 061212 perhaps hiding the widget is not needed
	       
	self.featureManager.removeTab(self.featureManager.indexOf(self.propertyManagerScrollArea))

	#Set the PropertyManager tab scroll area to the appropriate widget .at
	self.propertyManagerScrollArea.setWidget(tab)
		
	self.featureManager.addTab(self.propertyManagerScrollArea, 
				   geticon("ui/modeltree/Property_Manager"), "")
				   
	self.featureManager.setCurrentIndex(self.featureManager.indexOf(self.propertyManagerScrollArea))
	

    def dismiss(self):
        self.parent.removePartWindow(self)

class GridPosition:
    def __init__(self):
        self.row, self.col = 0, 0
        self.availableSlots = [ ]
        self.takenSlots = { }

    def next(self, widget):
        if len(self.availableSlots) > 0:
            row, col = self.availableSlots.pop(0)
        else:
            row, col = self.row, self.col
            if row == col:
                # when on the diagonal, start a new self.column
                self.row = 0
                self.col = col + 1
            elif row < col:
                # continue moving down the right edge until we're about
                # to hit the diagonal, then start a new bottom self.row
                if row == col - 1:
                    self.row = row + 1
                    self.col = 0
                else:
                    self.row = row + 1
            else:
                # move right along the bottom edge til you hit the diagonal
                self.col = col + 1
        self.takenSlots[widget] = (row, col)
        return row, col

    def removeWidget(self, widget):
        rc = self.takenSlots[widget]
        self.availableSlots.append(rc)
        del self.takenSlots[widget]
	
def printSizeInfo(widgets):
    """Used to print the sizeHints and sizePolicy of left channel widgets.
    I'm using this to help resolve bug 2424:
    "Allow resizing of splitter between Property Manager and Graphics window."
    -- Mark
    """
    for widget in widgets:
	printSizePolicy(widget)
	printSizeHints(widget)
	
def setWidgetSizePolicy(widget):
    """Used to set the width and sizePolicy of left channel widgets.
    I'm using this to help resolve bug 2424:
    "Allow resizing of splitter between Property Manager and Graphics window."
    -- Mark
    """
    pmWdiget = self.featureManager
    widget.setSizePolicy(
	QSizePolicy(QSizePolicy.Policy(QSizePolicy.Minimum),
		    QSizePolicy.Policy(QSizePolicy.Expanding)))
			    
    widget.resize(pmDefaultWidth, widget.sizeHint().height())

