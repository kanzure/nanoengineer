# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PM_GroupBox.py

@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-07-22: Split PropMgrGroupBox out of PropMgrBaseClass.py into this 
file and renamed it PM_GroupBox.
"""

import platform

from debug import print_compact_traceback

from PM_Colors import getPalette
from PM_Colors import pmGrpBoxButtonBorderColor
from PM_Colors import pmGrpBoxButtonTextColor
from PM_Colors import pmGrpBoxExpandedIconPath
from PM_Colors import pmGrpBoxCollapsedIconPath
from PM_Colors import pmGrpBoxColor
from PM_Colors import pmGrpBoxBorderColor
from PM_Colors import pmGrpBoxButtonColor

from PM_Constants import pmGroupBoxSpacing
from PM_Constants import pmGrpBoxVboxLayoutMargin
from PM_Constants import pmGrpBoxVboxLayoutSpacing
from PM_Constants import pmGrpBoxGridLayoutMargin
from PM_Constants import pmGrpBoxGridLayoutSpacing

from PM_Constants import pmGridLayoutMargin
from PM_Constants import pmGridLayoutSpacing

from PM_Constants import pmLeftAlignment, pmRightAlignment
from PM_Constants import pmLeftColumn, pmRightColumn

from PyQt4.Qt import Qt
from PyQt4.Qt import QGroupBox
from PyQt4.Qt import QGridLayout
from PyQt4.Qt import QLabel
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QPalette
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL

from Utility import geticon

class PM_GroupBox( QGroupBox ):
    """
    The PM_GroupBox widget provides a group box container with a 
    collapse/expand button and a title. All PM widgets must be inside
    of a PM_GroupBox.
    
    @cvar defaultValue: The default value of the group box.
    @type defaultValue: float
    
    @cvar setAsDefault: Determines whether to reset the value of all
                        widgets in the group box when the user clicks
                        the "Restore Defaults" button. If set to False,
                        no widgets will be reset regardless thier own 
                        I{setAsDefault} value.
    @type setAsDefault: bool
    
    @cvar hidden: Hide flag.
    @type hidden: bool
    
    @cvar labelWidget: The Qt label widget of this group box.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    
    @cvar expanded: Expanded flag.
    @type expanded: bool
    
    @cvar _widgetList: List of widgets in the group box (except the title button).
    @type _widgetList: list
    
    @cvar _rowCount: Number of rows in the group box.
    @type _rowCount: int
    
    @cvar _groupBoxCount: Number of group boxes in this group box.
    @type _groupBoxCount: int
    
    @cvar _lastGroupBox: The last group box in this group box (i.e. the
                         most recent PM group box added).
    @type _lastGroupBox: PM_GroupBox
    """
    
    setAsDefault = True
    hidden       = False
    labelWidget  = None
    expanded     = True
    
    _widgetList    = []
    _rowCount      = 0
    _groupBoxCount = 0
    _lastGroupBox  = None
    
    def __init__( self, 
                  parentWidget, 
                  title          = '', 
                  addTitleButton = False, 
                  setAsDefault   = True ):
        """
        PM_GroupBox constructor.
        
        Appends a QGroupBox widget to <parentWidget>, a PM_Dialog or a PM_GroupBox.
        
        Arguments:
        
        @param parentWidget: the parent dialog or group box containing this widget.
        @type  parentWidget: PM_Dialog or PM_GroupBox
        
        @param title: the title on the group box button
        @type  title: str
        
        @param addTitleButton: if True, a titleButton is added to the
                top of the GroupBox with the label <title>. The titleButton
                is used to collapse and expand the GroupBox.
                If False, no titleButton is added. <title> will be used as 
                the GroupBox title and the GroupBox will not be 
                collapsable/expandable.
        @type  addTitleButton: bool
        
        @param setAsDefault: if False, no widgets in this groupbox will have thier
                default values restored when the Restore Defaults 
                button is clicked, regardless thier own <setAsDefault> value.
        @type  setAsDefault: bool
        
        @see: U{B{QGroupBox}<http://doc.trolltech.com/4/qgroupbox.html>}
        """
      
        QGroupBox.__init__(self)
        
        self.parentWidget = parentWidget
        parentWidget._groupBoxCount += 1
        _groupBoxCount = 0
                
        self.setAsDefault = setAsDefault
        
        # Calling addWidget() here is important. If done at the end,
        # the title button does not get assigned its palette for some 
        # unknown reason. Mark 2007-05-20.
        parentWidget.VBoxLayout.addWidget(self) # Add self to PropMgr's VBoxLayout
        
        self._widgetList = []
        parentWidget._widgetList.append(self)
        
        self.setAutoFillBackground(True) 
        self.setPalette(self._getPalette())
        self.setStyleSheet(self._getStyleSheet())
        
        # Create vertical box layout
        self.VBoxLayout = QVBoxLayout(self)
        self.VBoxLayout.setMargin(pmGrpBoxVboxLayoutMargin)
        self.VBoxLayout.setSpacing(pmGrpBoxVboxLayoutSpacing)
        
        # Create grid layout
        self.GridLayout = QGridLayout()
        self.GridLayout.setMargin(pmGridLayoutMargin)
        self.GridLayout.setSpacing(pmGridLayoutSpacing)
        
        # Insert grid layout in its own VBoxLayout
        self.VBoxLayout.addLayout(self.GridLayout)
        
        if addTitleButton: # Add title button to GroupBox
            self.titleButton = self._getTitleButton(self, title)
            self.VBoxLayout.insertWidget(0, self.titleButton)
            self.connect( self.titleButton, 
                          SIGNAL("clicked()"),
                          self.toggleExpandCollapse)
        else:
            self.setTitle(title)
            
        # Fixes the height of the groupbox. Very important. Mark 2007-05-29
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self._addBottomSpacer()
        
    def _addBottomSpacer( self ):
        """
        Add a vertical spacer below this groupbox <self>.
        Assume <self> is going to be the last groupbox in this PropMgr, so set
        its spacer's vertical sizePolicy to MinimumExpanding. We then set the 
        vertical sizePolicy of the last groupbox's spacer to Fixed and set its
        height to pmGroupBoxSpacing.
        """
        # Spacers are only added to groupboxes in the PropMgr, not
        # nested groupboxes.
        from PM_Dialog import PM_Dialog
        if not isinstance(self.parentWidget, PM_Dialog):
            self.VSpacerWidget = None
            return
        
        if self.parentWidget._lastGroupBox:
            # _lastGroupBox is no longer the last one. <self> will be the
            # _lastGroupBox, so we must change the VSpacerWidget height 
            # and sizePolicy of _lastGroupBox to be a fixed
            # spacer between it and <self>.
            defaultHeight = pmGroupBoxSpacing
            self.parentWidget._lastGroupBox.VSpacerWidget.changeSize(
                10, defaultHeight, 
                QSizePolicy.Fixed,
                QSizePolicy.Fixed)
            self.parentWidget._lastGroupBox.VSpacerWidget.defaultHeight = defaultHeight
            
        # Add a 1 pixel high, MinimumExpanding VSpacer below this GroupBox.
        # This keeps the PropMgr layout squeezed together as groupboxes 
        # are expanded, collapsed, hidden and shown again.
        defaultHeight = 1
        self.VSpacerWidget = QSpacerItem(10, defaultHeight, 
                                        QSizePolicy.Fixed,
                                        QSizePolicy.MinimumExpanding)
        
        self.VSpacerWidget.defaultHeight = defaultHeight
        
        self.parentWidget.VBoxLayout.addItem(self.VSpacerWidget)
        
        # This groupbox is now the last one in the PropMgr.
        self.parentWidget._lastGroupBox = self
        
    def restoreDefault ( self ):
        """
        Restores the default values for all widgets in this groupbox.
        """
        for widget in self._widgetList:
            if platform.atom_debug:
                print "PM_GroupBox.restoreDefault(): widget =", widget.objectName()
            widget.restoreDefault()
        
    def setTitle( self, 
                  title ):
        """
        Sets the groupbox title to <title>.
        This overrides QGroupBox's setTitle() method.
        """
        # Create QLabel widget.
        self.labelWidget = QLabel()
        labelAlignment = pmLeftAlignment
        self.labelWidget.setAlignment(labelAlignment)
        self.labelWidget.setText(title)
        self.VBoxLayout.insertWidget(0, self.labelWidget)
        
    def getPmWidgetPlacementParameters( self, pmWidget ):
        """
        Returns all the layout parameters needed to place 
        a PM_Widget in the group box grid layout.
        """
        
        label       = pmWidget.label
        labelColumn = pmWidget.labelColumn
        spanWidth   = pmWidget.spanWidth
        row         = self._rowCount
        
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
                
        return widgetRow, \
               widgetColumn, \
               widgetSpanCols, \
               widgetAlignment, \
               rowIncrement, \
               labelRow, \
               labelColumn, \
               labelSpanCols, \
               labelAlignment
    
    def addPmWidget( self, pmWidget ):
        """
        Add a PM widget and its label to this group box.
        
        @param pmWidget: The PM widget to add.
        @type  pmWidget: PM_Widget
        """
        
        # Gather all the widget and label layout parameters.
        widgetRow, \
        widgetColumn, \
        widgetSpanCols, \
        widgetAlignment, \
        rowIncrement, \
        labelRow, \
        labelColumn, \
        labelSpanCols, \
        labelAlignment = \
            self.getPmWidgetPlacementParameters(pmWidget)
        
        if pmWidget.labelWidget:            
            self.GridLayout.addWidget( pmWidget.labelWidget,
                                       labelRow, 
                                       labelColumn,
                                       1, 
                                       labelSpanCols,
                                       labelAlignment )
        
        # The following is a workaround for a Qt bug. If addWidth()'s 
        # <alignment> argument is not supplied, the widget spans the full 
        # column width of the grid cell containing it. If <alignment> 
        # is supplied, this desired behavior is lost an there is no 
        # value that can be supplied to maintain the behavior (0 doesn't 
        # work). The workaround is to call addWidget() without the <alignment>
        # argument. Mark 2007-07-27.
        if widgetAlignment == pmLeftAlignment:
            self.GridLayout.addWidget( pmWidget,
                                       widgetRow, 
                                       widgetColumn,
                                       1, 
                                       widgetSpanCols ) 
                                       # aligment = 0 doesn't work.
        else:
            self.GridLayout.addWidget( pmWidget,
                                       widgetRow, 
                                       widgetColumn,
                                       1, 
                                       widgetSpanCols, 
                                       widgetAlignment )
        
        self._widgetList.append(pmWidget)
        
        self._rowCount += rowIncrement
    
    def collapse( self ):
        """
        Hides the group box when its parent group box 
        is collapsed.
        """
        QWidget.hide(self) # Hide self.
        if self.labelWidget :# Hide self's label if it has one.
            self.labelWidget.hide()
        
    def expand( self ):
        """
        Displays the group box when its parent group box
        is expanded, unless the group box was "permanently" hidden via
        L{hide()}. In that case, the group box will remain hidden until 
        L{show()} is called.
        """
        if self.hidden: return
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show()
            
    def hide( self ):
        """
        Hides the group box . If hidden, the group box will not be 
        displayed when its parent group box is expanded.
        Call L{show()} to unhide the group box.
        
        @see: L{show}
        """
        self.hidden = True
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide() 
        
        # Change the spacer height to zero to "hide" it unless
        # self is the last GroupBox in the Property Manager.
        if self.VSpacerWidget:
            self.VSpacerWidget.changeSize(10, 0)
            
    def show( self ):
        """
        Unhide the group box. The group box will remain (temporarily) hidden
        if its parent group box is collapsed, but will be displayed again when
        the group box is expanded.
        
        @see: L{hide}
        """
        self.hidden = False
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show() 
            
        if self.VSpacerWidget:
            self.VSpacerWidget.changeSize(10, self.VSpacerWidget.defaultHeight)

    # Title Button Methods #####################################
    
    def _getTitleButton( self, 
                         parentWidget = None,
                         title        = '', 
                         showExpanded = True ):
        """
        Return the group box title push button. The push button is customized 
        such that it appears as a title bar at the top of the group box. 
        If the user clicks on this 'title bar' it sends a signal to open or close
        the group box.
        
        @param parentWidget: the parent dialog or group box containing this widget.
        @type  parentWidget: PM_Dialog or PM_GroupBox
        
        @param title: the title on the button
        @type  title: str 
        
        @param showExpanded: determines whether the expand or collapse image is 
                             displayed on the title button
                             
        @see: _getTitleButtonStyleSheet ()
        """
        
        button  = QPushButton(title, parentWidget)
        button.setFlat(False)
        button.setAutoFillBackground(True)
        
        button.setStyleSheet(self._getTitleButtonStyleSheet(showExpanded))     
        
        self.titleButtonPalette = self._getTitleButtonPalette()
        button.setPalette(self.titleButtonPalette)
        
        # ninad 070221 set a non-existant 'Ghost Icon' for this button.
        # By setting this icon, the button text left aligns! 
        # (which what we want :-) )
        # So this might be a bug in Qt4.2.  If we don't use the following kludge, 
        # there is no way to left align the push button text but to subclass it. 
        # (could means a lot of work for such a minor thing).  So OK for now.
        
        button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
        
        return button
    
    def _getTitleButtonPalette( self ):
        """
        Return a palette for the title button. 
        """
        return getPalette(None, QPalette.Button, pmGrpBoxButtonColor)
    
    
    def _getTitleButtonStyleSheet( self, showExpanded = True ):
        """
        Returns the style sheet for a groupbox title button (or checkbox).
        If <showExpanded> is True, the style sheet includes an expanded icon.
        If <showExpanded> is False, the style sheet includes a collapsed icon.
        """
        
        # Need to move border color and text color to top (make global constants).
        if showExpanded:        
            styleSheet = "QPushButton {border-style:outset;\
            border-width: 2px;\
            border-color: " + pmGrpBoxButtonBorderColor + ";\
            border-radius:2px;\
            font:bold 12px 'Arial'; \
            color: " + pmGrpBoxButtonTextColor + ";\
            min-width:10em;\
            background-image: url(" + pmGrpBoxExpandedIconPath + ");\
            background-position: right;\
            background-repeat: no-repeat;\
            }"       
        else:
            
            styleSheet = "QPushButton {border-style:outset;\
            border-width: 2px;\
            border-color: " + pmGrpBoxButtonBorderColor + ";\
            border-radius:2px;\
            font: bold 12px 'Arial'; \
            color: " + pmGrpBoxButtonTextColor + ";\
            min-width:10em;\
            background-image: url(" + pmGrpBoxCollapsedIconPath + ");\
            background-position: right;\
            background-repeat: no-repeat;\
            }"
            
        return styleSheet
    
    def toggleExpandCollapse( self ):
        """
        Slot method for the title button to expand/collapse the groupbox.
        """
        if self._widgetList:
            if self.expanded: # Collapse groupbox by hiding all widgets in groupbox.
                self.GridLayout.setMargin(0)
                self.GridLayout.setSpacing(0)
                # The styleSheet contains the expand/collapse.
                styleSheet = self._getTitleButtonStyleSheet(showExpanded = False)
                self.titleButton.setStyleSheet(styleSheet)
                # Why do we have to keep resetting the palette?
                # Does assigning a new styleSheet reset the button's palette?
                # If yes, we should add the button's color to the styleSheet.
                # Mark 2007-05-20
                self.titleButton.setPalette(self._getTitleButtonPalette())
                self.titleButton.setIcon(
                    geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for widget in self._widgetList:
                    if platform.atom_debug:
                        if widget.objectName():
                            print "widget name = ", widget.objectName()
                    
                    widget.collapse()
                self.expanded = False 
            else: # Expand groupbox by showing all widgets in groupbox.
                from PM_MessageGroupBox import PM_MessageGroupBox
                if isinstance(self, PM_MessageGroupBox):
                    # If we don't do this, we get a small space b/w the 
                    # title button and the MessageTextEdit widget.
                    # Extra code unnecessary, but more readable. 
                    # Mark 2007-05-21
                    self.GridLayout.setMargin(0)
                    self.GridLayout.setSpacing(0)
                else:
                    self.GridLayout.setMargin(pmGrpBoxGridLayoutMargin)
                    self.GridLayout.setSpacing(pmGrpBoxGridLayoutSpacing)
                # The styleSheet contains the expand/collapse.
                styleSheet = self._getTitleButtonStyleSheet(showExpanded = True)
                self.titleButton.setStyleSheet(styleSheet)
                # Why do we have to keep resetting the palette?
                # Does assigning a new styleSheet reset the button's palette?
                # If yes, we should add the button's color to the styleSheet.
                # Mark 2007-05-20
                self.titleButton.setPalette(self._getTitleButtonPalette())
                self.titleButton.setIcon(
                    geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for widget in self._widgetList:
                    widget.expand()
                self.expanded = True         
        else:
            print "Groupbox has no widgets. Clicking on groupbox button has no effect"
    
    # GroupBox palette and stylesheet methods. ##############################3
    
    def _getPalette( self ):
        """
        Return a palette for this groupbox. 
        The color should be slightly darker (or lighter) than the property manager background.
        """
        return getPalette( None, QPalette.Window, pmGrpBoxColor )
    
    def _getStyleSheet( self ):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        The background color for a groupbox is set using getPalette()."""
        
        styleSheet = "QGroupBox {border-style:solid;\
        border-width: 1px;\
        border-color: " + pmGrpBoxBorderColor + ";\
        border-radius: 0px;\
        min-width: 10em; }" 
        
        ## For Groupboxs' Pushbutton : 
        ##Other options not used : font:bold 10px;  
        
        return styleSheet

# End of PM_GroupBox ############################