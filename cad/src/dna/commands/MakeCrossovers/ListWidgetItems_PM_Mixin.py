# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
See ListWidgetItems_Command_Mixin for details.

@see: MakeCrossovers_PropertyManager
      ListWidgetItems_Command_Mixin
      ListWidgetItems_GraphicsMode_Mixin
"""
from PM.PM_SelectionListWidget import PM_SelectionListWidget
from utilities.constants import lightred_1, lightgreen_2
from PyQt4.Qt import Qt
from PM.PM_ToolButton    import PM_ToolButton
from PM.PM_WidgetRow     import PM_WidgetRow

class ListWidgetItems_PM_Mixin:
    
    
    def _loadSegmentListWidget(self, pmGroupBox):
        self.segmentListWidget = PM_SelectionListWidget(
            pmGroupBox,
            self.win,
            label = "",
            heightByRows = 12)
      
        self.segmentListWidget.setFocusPolicy(Qt.StrongFocus)
        self.segmentListWidget.setFocus()
        self.setFocusPolicy(Qt.StrongFocus)       
        
        self.addSegmentsToolButton = PM_ToolButton(
                        pmGroupBox, 
                        text = "Add segments to the list",
                        iconPath  = "ui/actions/Properties Manager"\
                        "/AddSegment_To_ResizeSegmentList.png",
                        spanWidth = True  )
        self.addSegmentsToolButton.setCheckable(True)
        self.addSegmentsToolButton.setAutoRaise(True)
        
        self.removeSegmentsToolButton = PM_ToolButton(
                        pmGroupBox, 
                        text = "Remove segments from the list",
                        iconPath  = "ui/actions/Properties Manager"\
                        "/RemoveSegment_From_ResizeSegmentList.png",
                        spanWidth = True  )
        self.removeSegmentsToolButton.setCheckable(True)
        self.removeSegmentsToolButton.setAutoRaise(True)
        
        #Widgets to include in the widget row. 
        widgetList = [
            ('QLabel', "  Add/Remove Segments:", 0),
            ('QSpacerItem', 5, 5, 1),
            ('PM_ToolButton', self.addSegmentsToolButton, 2),
             ('QSpacerItem', 5, 5, 3),
            ('PM_ToolButton', self.removeSegmentsToolButton, 4),                      
            ('QSpacerItem', 5, 5, 5) ]
        
        widgetRow = PM_WidgetRow(pmGroupBox,
                                 title     = '',
                                 widgetList = widgetList,
                                 label = "",
                                 spanWidth = True )
    
    def listWidgetHasFocus(self):
        """
        Checks if the list widget that lists dnasegments (that will undergo 
        special operations such as 'resizing them at once or making 
        crossovers between the segments etc) has the 
        Qt focus. This is used to just remove items from the list widget 
        (without actually 'deleting' the corresponding Dnasegment in the GLPane)
        @see: MultipleDnaSegment_GraphicsMode.keyPressEvent() where it is called
        """
        if self.segmentListWidget.hasFocus():
            return True        
        return False
    
    
    def updateListWidgets(self):
        self.updateSegmentListWidget()
    
    def updateSegmentListWidget(self):
        """
        Update the list of segments shown in the segments list widget
        @see: self.updateListWidgets, self.updateStrandListWidget
        """
        
        segmentList = []
        
        segmentList = self.command.getSegmentList()   
        
        
        if segmentList:
            self.segmentListWidget.insertItems(
                row = 0,
                items = segmentList)
        else:
            self.segmentListWidget.clear()
            
        

    def isAddSegmentsToolActive(self): 
        """
        Returns True if the add segments tool (which adds the segments to the 
        list of segments) is active
        """
            
        if self.addSegmentsToolButton.isChecked():
            #For safety
            if not self.removeSegmentsToolButton.isChecked():         
                return True   
            
        return False            
    
    def isRemoveSegmentsToolActive(self):
        """
        Returns True if the remove segments tool (which removes the segments 
        from the list of segments ) is active
        """
        if self.removeSegmentsToolButton.isChecked():
            if not self.addSegmentsToolButton.isChecked():
                #For safety
                return True               
        return False
    
    def activateAddSegmentsTool(self,enable):
        """
        Change the appearance of the list widget (that lists the dna segments 
        ) so as to indicate that the add dna segments tool is 
        active 
        @param enable: If True, changes the appearance of list widget to 
                       indicate that the add segments tool is active.
        @type  enable: bool
        """
        if enable:
            if not self.addSegmentsToolButton.isChecked():
                self.addSegmentsToolButton.setChecked(True)
            if self.removeSegmentsToolButton.isChecked():
                self.removeSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(False)
            self.segmentListWidget.setColor(lightgreen_2) 
            self.command.logMessage('ADD_SEGMENTS_ACTIVATED')
        else:
            if self.addSegmentsToolButton.isChecked():
                self.addSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(True)
            self.segmentListWidget.resetColor()
                
    def activateRemoveSegmentsTool(self,enable):
        """
        Change the appearance of the list widget (that lists the dna segments 
        ) so as to indicate that the REMOVE dna segments tool is 
        active 
        @param enable: If True, changes the appearance of list widget to 
                       indicate that the REMOVE segments tool is active.
        @type  enable: bool
        """
        if enable:
            if not self.removeSegmentsToolButton.isChecked():
                self.removeSegmentsToolButton.setChecked(True)
            if self.addSegmentsToolButton.isChecked():
                self.addSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(False)
            self.command.logMessage('REMOVE_SEGMENTS_ACTIVATED')            
            self.segmentListWidget.setColor(lightred_1)            
        else:
            if self.removeSegmentsToolButton.isChecked():
                self.removeSegmentsToolButton.setChecked(False)
            self.segmentListWidget.setAlternatingRowColors(True)
            self.segmentListWidget.resetColor()
    
            
    def _deactivateAddRemoveSegmentsTool(self):
        """
        Deactivate tools that allow adding or removing the segments to the 
        segment list in the Property manager. This can be simply done by 
        resetting the state of toolbuttons to False. 
        Example: toolbuttons that add or remove 
        segments to the segment list in the Property manager. When self.show
        is called these need to be unchecked. 
        @see: self.isAddSegmentsToolActive()
        @see:self.isRemoveSegmentsToolActive()
        @see: self.show()
        """
        self.addSegmentsToolButton.setChecked(False)
        self.removeSegmentsToolButton.setChecked(False)
    
    def removeListWidgetItems(self):
        """
        Removes selected itoms from the dna segment list widget 
        Example: User selects a bunch of items in the list widget and hits 
        delete key  to remove the selected items from the list
        IMPORTANT NOTE: This method does NOT delete the correspoinging model 
        item in the GLPane (i.e. corresponding dnasegment). It just 'removes'
        the item from the list widget 
        This is intentional. 
        """
        self.segmentListWidget.deleteSelection()
        itemDict = self.segmentListWidget.getItemDictonary()           
        self.command.setSegmentList(itemDict.values())
        self.updateListWidgets()            
        self.win.win_update() 
