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

from utilities import debug_flags

from PM.PM_Colors import getPalette
from PM.PM_Colors import pmGrpBoxButtonBorderColor
from PM.PM_Colors import pmGrpBoxButtonTextColor
from PM.PM_Colors import pmGrpBoxExpandedIconPath
from PM.PM_Colors import pmGrpBoxCollapsedIconPath
from PM.PM_Colors import pmGrpBoxColor
from PM.PM_Colors import pmGrpBoxBorderColor
from PM.PM_Colors import pmGrpBoxButtonColor

from PM.PM_Constants import PM_GROUPBOX_SPACING
from PM.PM_Constants import PM_GROUPBOX_VBOXLAYOUT_MARGIN
from PM.PM_Constants import PM_GROUPBOX_VBOXLAYOUT_SPACING
from PM.PM_Constants import PM_GROUPBOX_GRIDLAYOUT_MARGIN
from PM.PM_Constants import PM_GROUPBOX_GRIDLAYOUT_SPACING

from PM.PM_Constants import PM_GRIDLAYOUT_MARGIN
from PM.PM_Constants import PM_GRIDLAYOUT_SPACING

from PM.PM_Constants import PM_LABEL_LEFT_ALIGNMENT, PM_LABEL_RIGHT_ALIGNMENT

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

from widgets.widget_helpers import QColor_to_Hex
from utilities.icon_utilities import geticon, getpixmap

#This import is only used in isinstance check--
from PM.PM_CheckBox import PM_CheckBox

class PM_GroupBox( QGroupBox ):
    """
    The PM_GroupBox widget provides a group box container with a 
    collapse/expand button and a title button.
    
    PM group boxes can be nested by supplying an existing PM_GroupBox as the 
    parentWidget of a new PM_GroupBox (as an argument to its constructor).
    If the parentWidget is a PM_GroupBox, no title button will be created
    for the new group box.
    
    @cvar setAsDefault: Determines whether to reset the value of all
                        widgets in the group box when the user clicks
                        the "Restore Defaults" button. If set to False,
                        no widgets will be reset regardless thier own 
                        I{setAsDefault} value.
    @type setAsDefault: bool
       
    @cvar labelWidget: The Qt label widget of this group box.
    @type labelWidget: U{B{QLabel}<http://doc.trolltech.com/4/qlabel.html>}
    
    @cvar expanded: Expanded flag.
    @type expanded: bool
    
    @cvar _title: The group box title.
    @type _title: str
    
    @cvar _widgetList: List of widgets in the group box 
                      (except the title button).
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
    labelWidget  = None
    expanded     = True
    
    _title         = ""
    _widgetList    = []
    _rowCount      = 0
    _groupBoxCount = 0
    _lastGroupBox  = None
    titleButtonRequested = True
    
    def __init__(self, 
                 parentWidget, 
                 title          = '', 
                 connectTitleButton = True,
                 setAsDefault   = True
                 ):
        """
        Appends a PM_GroupBox widget to I{parentWidget}, a L{PM_Dialog} or a 
        L{PM_GroupBox}.
        
        If I{parentWidget} is a L{PM_Dialog}, the group box will have a title 
        button at the top for collapsing and expanding the group box. If 
        I{parentWidget} is a PM_GroupBox, the title will simply be a text 
        label at the top of the group box.
        
        @param parentWidget: The parent dialog or group box containing this
                             widget.
        @type  parentWidget: L{PM_Dialog} or L{PM_GroupBox}
        
        @param title: The title (button) text. If empty, no title is added.
        @type  title: str
        
        @param connectTitleButton: If True, this class will automatically 
                      connect the title button of the groupbox to send signal
                      to expand or collapse the groupbox. Otherwise, the caller
                      has to connect this signal by itself. See:
                      B{Ui_MovePropertyManager.addGroupBoxes} and 
                      B{MovePropertyManager.connect_or_disconnect_signals} for
                      examples where the client connects this slot. 
        @type  connectTitleButton: bool
               
        
        @param setAsDefault: If False, no widgets in this group box will have 
                             thier default values restored when the B{Restore 
                             Defaults} button is clicked, regardless thier own 
                             I{setAsDefault} value.
        @type  setAsDefault: bool
        
        @see: U{B{QGroupBox}<http://doc.trolltech.com/4/qgroupbox.html>}
        """
      
        QGroupBox.__init__(self)
        
        self.parentWidget = parentWidget
        
        # Calling addWidget() here is important. If done at the end,
        # the title button does not get assigned its palette for some 
        # unknown reason. Mark 2007-05-20.
        # Add self to PropMgr's vBoxLayout
        if parentWidget:
            parentWidget._groupBoxCount += 1
            parentWidget.vBoxLayout.addWidget(self)
            parentWidget._widgetList.append(self)
            
        _groupBoxCount = 0
        self._widgetList = []
        self._title = title
        self.setAsDefault = setAsDefault
        
        self.setAutoFillBackground(True)
        self.setStyleSheet(self._getStyleSheet())
        
        # Create vertical box layout which will contain two widgets:
        # - the group box title button (or title) on row 0.
        # - the container widget for all PM widgets on row 1.
        self._vBoxLayout = QVBoxLayout(self)
        self._vBoxLayout.setMargin(0)
        self._vBoxLayout.setSpacing(0)
        
        # _containerWidget contains all PM widgets in this group box.
        # Its sole purpose is to easily support the collapsing and
        # expanding of a group box by calling this widget's hide()
        # and show() methods.
        self._containerWidget = QWidget()
        self._vBoxLayout.insertWidget(0, self._containerWidget)
        
        # Create vertical box layout
        self.vBoxLayout = QVBoxLayout(self._containerWidget)
        self.vBoxLayout.setMargin(PM_GROUPBOX_VBOXLAYOUT_MARGIN)
        self.vBoxLayout.setSpacing(PM_GROUPBOX_VBOXLAYOUT_SPACING)
        
        # Create grid layout
        self.gridLayout = QGridLayout()
        self.gridLayout.setMargin(PM_GRIDLAYOUT_MARGIN)
        self.gridLayout.setSpacing(PM_GRIDLAYOUT_SPACING)
        
        # Insert grid layout in its own vBoxLayout
        self.vBoxLayout.addLayout(self.gridLayout)
        
        # Add title button (or just a title if the parent is not a PM_Dialog).
        if not parentWidget or isinstance(parentWidget, PM_GroupBox):
            self.setTitle(title)
        else: # Parent is a PM_Dialog, so add a title button.
            if not self.titleButtonRequested:
                self.setTitle(title)
            else:
                self.titleButton = self._getTitleButton(self, title)
                self._vBoxLayout.insertWidget(0, self.titleButton)
                if connectTitleButton:
                    self.connect( self.titleButton, 
                                  SIGNAL("clicked()"),
                                  self.toggleExpandCollapse)
            
        # Fixes the height of the group box. Very important. Mark 2007-05-29
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self._addBottomSpacer()
        return
        
    def _addBottomSpacer(self):
        """
        Add a vertical spacer below this group box.
        
        Method: Assume this is going to be the last group box in the PM, so set
        its spacer's vertical sizePolicy to MinimumExpanding. We then set the 
        vertical sizePolicy of the last group box's spacer to Fixed and set its
        height to PM_GROUPBOX_SPACING.
        """
        # Spacers are only added to groupboxes in the PropMgr, not
        # nested groupboxes.
        
##        from PM.PM_Dialog import PM_Dialog
##        if not isinstance(self.parentWidget, PM_Dialog):
        
        if not self.parentWidget or isinstance(self.parentWidget, PM_GroupBox):
            #bruce 071103 revised test to remove import cycle; I assume that
            # self.parentWidget is either a PM_GroupBox or a PM_Dialog, since
            # comments about similar code in __init__ imply that.
            #
            # A cleaner fix would involve asking self.parentWidget whether to
            # do this, with instances of PM_GroupBox and PM_Dialog giving
            # different answers, and making them both inherit an API class
            # which documents the method or attr with which we ask them that
            # question; the API class would be inherited by any object to
            # which PM_GroupBox's such as self can be added.
            #
            # Or, an even cleaner fix would just call a method in
            # self.parentWidget to do what this code does now (implemented
            # differently in PM_GroupBox and PM_Dialog).
            self.verticalSpacer = None
            return
        
        if self.parentWidget._lastGroupBox:
            # _lastGroupBox is no longer the last one. <self> will be the
            # _lastGroupBox, so we must change the verticalSpacer height 
            # and sizePolicy of _lastGroupBox to be a fixed
            # spacer between it and <self>.
            defaultHeight = PM_GROUPBOX_SPACING
            self.parentWidget._lastGroupBox.verticalSpacer.changeSize(
                10, defaultHeight, 
                QSizePolicy.Fixed,
                QSizePolicy.Fixed)
            self.parentWidget._lastGroupBox.verticalSpacer.defaultHeight = \
                defaultHeight
            
        # Add a 1 pixel high, MinimumExpanding VSpacer below this group box.
        # This keeps all group boxes in the PM layout squeezed together as 
        # group boxes  are expanded, collapsed, hidden and shown again.
        defaultHeight = 1
        self.verticalSpacer = QSpacerItem(10, defaultHeight, 
                                        QSizePolicy.Fixed,
                                        QSizePolicy.MinimumExpanding)
        
        self.verticalSpacer.defaultHeight = defaultHeight
        
        self.parentWidget.vBoxLayout.addItem(self.verticalSpacer)
        
        # This groupbox is now the last one in the PropMgr.
        self.parentWidget._lastGroupBox = self
        return
        
    def restoreDefault (self):
        """
        Restores the default values for all widgets in this group box.
        """
        for widget in self._widgetList:
            if debug_flags.atom_debug:
                print "PM_GroupBox.restoreDefault(): widget =", \
                      widget.objectName()
            widget.restoreDefault()
            
        return
    
    def getTitle(self):
        """
        Returns the group box title.
        
        @return: The group box title.
        @rtype:  str
        """
        return self._title
    
    def setTitle(self, title):
        """
        Sets the groupbox title to <title>.
        
        @param title: The group box title.
        @type  title: str
        
        @attention: This overrides QGroupBox's setTitle() method.
        """
        
        if not title:
            return
        
        # Create QLabel widget.
        if not self.labelWidget:
            self.labelWidget = QLabel()
            self.vBoxLayout.insertWidget(0, self.labelWidget)
            labelAlignment = PM_LABEL_LEFT_ALIGNMENT
            self.labelWidget.setAlignment(labelAlignment)
        
        self._title = title
        self.labelWidget.setText(title)
        return
        
    def getPmWidgetPlacementParameters(self, pmWidget):
        """
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
            spanWidth = pmWidget.spanWidth
            
            if not spanWidth:
                # Set the widget's row and column parameters.
                widgetRow      = row
                widgetColumn   = pmWidget.widgetColumn
                widgetSpanCols = 1
                widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                rowIncrement   = 1
                #set a virtual label
                labelRow       = row
                labelSpanCols  = 1
                labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
                            
                if widgetColumn == 0:
                    labelColumn   = 1                              
                elif widgetColumn == 1:
                    labelColumn   = 0
            else:                
                # Set the widget's row and column parameters.
                widgetRow      = row
                widgetColumn   = pmWidget.widgetColumn
                widgetSpanCols = 2
                widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                rowIncrement   = 1
                #no label 
                labelRow       = 0
                labelColumn    = 0
                labelSpanCols  = 0
                labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
                
            
            return widgetRow, \
               widgetColumn, \
               widgetSpanCols, \
               widgetAlignment, \
               rowIncrement, \
               labelRow, \
               labelColumn, \
               labelSpanCols, \
               labelAlignment
        
       
        label       = pmWidget.label            
        labelColumn = pmWidget.labelColumn
        spanWidth   = pmWidget.spanWidth
        
        if not spanWidth: 
            # This widget and its label are on the same row
            labelRow       = row
            labelSpanCols  = 1
            labelAlignment = PM_LABEL_RIGHT_ALIGNMENT
            # Set the widget's row and column parameters.
            widgetRow      = row
            widgetColumn   = 1
            widgetSpanCols = 1
            widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
            rowIncrement   = 1
            
            if labelColumn == 1:
                widgetColumn   = 0
                labelAlignment = PM_LABEL_LEFT_ALIGNMENT
                widgetAlignment = PM_LABEL_RIGHT_ALIGNMENT
                        
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
                
            labelAlignment = PM_LABEL_LEFT_ALIGNMENT
            widgetAlignment = PM_LABEL_LEFT_ALIGNMENT
                
        return widgetRow, \
               widgetColumn, \
               widgetSpanCols, \
               widgetAlignment, \
               rowIncrement, \
               labelRow, \
               labelColumn, \
               labelSpanCols, \
               labelAlignment
    
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
        labelAlignment = \
            self.getPmWidgetPlacementParameters(pmWidget)
        
        if pmWidget.labelWidget: 
            #Create Label as a pixmap (instead of text) if a valid icon path 
            #is provided
            labelPath = str(pmWidget.label)
            if labelPath and labelPath.startswith("ui/"): #bruce 080325 revised
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

        if widgetAlignment == PM_LABEL_LEFT_ALIGNMENT:
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
                                       widgetAlignment
                                     )

        self._widgetList.append(pmWidget)
        
        self._rowCount += rowIncrement
        return
    
    def getRowCount(self):
        """
        Return the row count of gridlayout of L{PM_Groupbox}
        
        @return: The row count of L{self.gridlayout}
        @rtype: int
        """
        return self._rowCount
    
    def incrementRowCount(self, increment = 1):
        """
        Increment the row count of the gridlayout of L{PM_groupBox}
        @param increment: The incremental value
        @type  increment: int
        """
        self._rowCount += increment
        return
        
    def addQtWidget(self, qtWidget, column = 0, spanWidth = False):
        """
        Add a Qt widget to this group box.
        
        @param qtWidget: The Qt widget to add.
        @type  qtWidget: QWidget
        
        @warning: this method has not been tested yet.
        """
        # Set the widget's row and column parameters.
        widgetRow      = self._rowCount
        widgetColumn   = column
        if spanWidth:
            widgetSpanCols = 2
        else:
            widgetSpanCols = 1
        
        self.gridLayout.addWidget( qtWidget,
                                   widgetRow, 
                                   widgetColumn,
                                   1, 
                                   widgetSpanCols )
        
        self._rowCount += 1
        return
    
    def collapse(self):
        """
        Collapse this group box i.e. hide all its contents and change the look 
        and feel of the groupbox button. 
        """
        self.vBoxLayout.setMargin(0)
        self.vBoxLayout.setSpacing(0)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        # The styleSheet contains the expand/collapse.
        styleSheet = self._getTitleButtonStyleSheet(showExpanded = False)
        self.titleButton.setStyleSheet(styleSheet)
        self._containerWidget.hide()
        self.expanded = False 
        return
    
    def expand(self):
        """
        Expand this group box i.e. show all its contents and change the look 
        and feel of the groupbox button. 
        """       
        self.vBoxLayout.setMargin(PM_GROUPBOX_VBOXLAYOUT_MARGIN)
        self.vBoxLayout.setSpacing(PM_GROUPBOX_VBOXLAYOUT_SPACING)
        self.gridLayout.setMargin(PM_GROUPBOX_GRIDLAYOUT_MARGIN)
        self.gridLayout.setSpacing(PM_GROUPBOX_GRIDLAYOUT_SPACING)
            
        # The styleSheet contains the expand/collapse.
        styleSheet = self._getTitleButtonStyleSheet(showExpanded = True)
        self.titleButton.setStyleSheet(styleSheet)
        self._containerWidget.show()
        self.expanded = True
        return

    def hide(self):
        """
        Hides the group box .
        
        @see: L{show}
        """
        QWidget.hide(self)
        if self.labelWidget:
            self.labelWidget.hide() 
        
        # Change the spacer height to zero to "hide" it unless
        # self is the last GroupBox in the Property Manager.
        if self.parentWidget._lastGroupBox is self:
            return
        
        if self.verticalSpacer:
            self.verticalSpacer.changeSize(10, 0)
        return
            
    def show(self):
        """
        Unhides the group box.
        
        @see: L{hide}
        """
        QWidget.show(self)
        if self.labelWidget:
            self.labelWidget.show() 
        
        if self.parentWidget._lastGroupBox is self:
            return
        
        if self.verticalSpacer:
            self.verticalSpacer.changeSize(10, 
                                           self.verticalSpacer.defaultHeight)
        return

    # Title Button Methods #####################################
    
    def _getTitleButton(self, 
                        parentWidget = None,
                        title        = '', 
                        showExpanded = True ):
        """
        Return the group box title push button. The push button is customized 
        such that it appears as a title bar at the top of the group box. 
        If the user clicks on this 'title bar' it sends a signal to open or 
        close the group box.
        
        @param parentWidget: The parent dialog or group box containing this 
                             widget.
        @type  parentWidget: PM_Dialog or PM_GroupBox
        
        @param title: The button title.
        @type  title: str 
        
        @param showExpanded: dDetermines whether the expand or collapse image is 
                             displayed on the title button.
        @type  showExpanded: bool
                             
        @see: L{_getTitleButtonStyleSheet()}
        
        @Note: Including a title button should only be legal if the parentWidget
               is a PM_Dialog.
        """
        
        button  = QPushButton(title, parentWidget)
        button.setFlat(False)
        button.setAutoFillBackground(True)
        
        button.setStyleSheet(self._getTitleButtonStyleSheet(showExpanded))     
        
        return button
    
    def _getTitleButtonStyleSheet(self, showExpanded = True):
        """
        Returns the style sheet for a group box title button (or checkbox).
        
        @param showExpanded: Determines whether to include an expand or
                             collapse icon.
        @type  showExpanded: bool
        
        @return: The title button style sheet.
        @rtype:  str
        """
        
        # Need to move border color and text color to top 
        # (make global constants).
        if showExpanded:        
            styleSheet = \
                       "QPushButton {"\
                       "border-style: outset; "\
                       "border-width: 2px; "\
                       "border-color: #%s; "\
                       "border-radius: 2px; "\
                       "background-color: #%s; "\
                       "font: bold 12px 'Arial'; "\
                       "color: #%s; "\
                       "min-width: 10em; "\
                       "background-image: url(%s); "\
                       "background-position: right; "\
                       "background-repeat: no-repeat; "\
                       "text-align: left; "\
                       "}" % (QColor_to_Hex(pmGrpBoxButtonBorderColor),
                              QColor_to_Hex(pmGrpBoxButtonColor),
                              QColor_to_Hex(pmGrpBoxButtonTextColor),
                              pmGrpBoxExpandedIconPath
                              )
                              
        else:
            # Collapsed.
            styleSheet = \
                       "QPushButton {"\
                       "border-style: outset; "\
                       "border-width: 2px; "\
                       "border-color: #%s; "\
                       "border-radius: 2px; "\
                       "background-color: #%s; "\
                       "font: bold 12px 'Arial'; "\
                       "color: #%s; "\
                       "min-width: 10em; "\
                       "background-image: url(%s); "\
                       "background-position: right; "\
                       "background-repeat: no-repeat; "\
                       "text-align: left; "\
                       "}" % (QColor_to_Hex(pmGrpBoxButtonBorderColor),
                              QColor_to_Hex(pmGrpBoxButtonColor),
                              QColor_to_Hex(pmGrpBoxButtonTextColor),
                              pmGrpBoxCollapsedIconPath
                              )
        return styleSheet
            
    def toggleExpandCollapse(self):
        """
        Slot method for the title button to expand/collapse the group box.
        """
        if self._widgetList:
            if self.expanded:
                self.collapse()
            else: # Expand groupbox by showing all widgets in groupbox.
                self.expand()         
        else:
            print "Clicking on the group box button has no effect "\
                   "since it has no widgets."
        return
    
    # GroupBox palette and stylesheet methods. ##############################
    
    def _getPalette(self):
        """
        Return a palette for this group box. The color should be slightly 
        darker (or lighter) than the property manager background.
        
        @return: The group box palette.
        @rtype:  U{B{QPalette}<http://doc.trolltech.com/4/qpalette.html>}
        """
        return getPalette( None, QPalette.Window, pmGrpBoxColor )
    
    def _getStyleSheet(self):
        """
        Return the style sheet for the groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
         - background color
        
        @return: The group box style sheet.
        @rtype:  str
        """
        
        styleSheet = \
                   "QGroupBox {"\
                   "border-style: solid; "\
                   "border-width: 1px; "\
                   "border-color: #%s; "\
                   "border-radius: 0px; "\
                   "background-color: #%s; "\
                   "min-width: 10em; "\
                   "}" % ( QColor_to_Hex(pmGrpBoxBorderColor), 
                           QColor_to_Hex(pmGrpBoxColor)
                           )
        return styleSheet

# End of PM_GroupBox ############################
