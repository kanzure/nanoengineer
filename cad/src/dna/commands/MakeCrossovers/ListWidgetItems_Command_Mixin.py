# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ListWidgetItems_Command_Mixin.py

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-05-27 -2008-05-29 Created and modified.

TODO as of 2008-06-01:
- Rename this class and others like ListWidgetItems_*_Mixin to a better name
- At the moment used only by MakeCrossOvers_* classes, need refactoring of
MultipleDnaSegmentResize classes so that they also implement this API
OR refactor these classes so that they are wrap the functionality and are used
as an object in the classes such as MakeCrossovers_*.
- Move this and other related classes to possibly dna.command_support
- These classes refer to MultipleDnaSegmentResize classes because this was 
originally implemented there (see also dna.command_support.DnaSegmentList)

@see: MakeCrossovers_Command
      ListWidgetItems_GraphicsMode_Mixin
      ListWidgetItems_PM_Mixin      
"""

class ListWidgetItems_Command_Mixin:

    #A list of all dnasegments that will be scanned for potential
    #crossover sites. 
    _structList = []

    def command_entered(self):
        """
        @see baseCommand.command_entered() for documentation
        @see MakeCrossovers_Command.command_entered()
        """
        self._structList = []  
        
        
    def itemLimitForSegmentListWidget(self):
        """
        Maximum number of items allowed in the segment list widet.(For 
        performance reasons)
        """
        return 30
        
        
    def ensureSegmentListItemsWithinLimit(self, segments):
        """
        Subclasses should override this method.
        """
        pass
    
    
    def logMessage(self, type = ''):
        """
        Subclasses should override this
        """
        pass
    
    
    def activateAddSegmentsTool(self, enableFlag = True):
        """
        """        
        if self.propMgr is None:
            return False

        return self.propMgr.activateAddSegmentsTool(enableFlag)

    def isAddSegmentsToolActive(self):
        """
        Returns True if the Add segments tool in the PM, that allows adding 
        dna segments from the segment list,  is active. 
        @see: MultipleDnaSegmentResize_GraphicsMode.chunkLeftUp()
        @see: MultipleDnaSegmentResize_GraphicsMode.end_selection_from_GLPane()
        @see: self.isRemoveSegmentsToolActive()
        @see: self.addSegmentToResizeSegmentList()
        """
        if self.propMgr is None:
            return False

        return self.propMgr.isAddSegmentsToolActive()


    def activateRemoveSegmentsTool(self, enableFlag = True):
        if self.propMgr is None:
            return
        self.propMgr.activateRemoveSegmentsTool(enableFlag)

    def isRemoveSegmentsToolActive(self):
        """
        Returns True if the Remove Segments tool in the PM, that allows removing 
        dna segments from the segment list, is active. 
        @see: MultipleDnaSegmentResize_GraphicsMode.chunkLeftUp()
        @see: MultipleDnaSegmentResize_GraphicsMode.end_selection_from_GLPane()
        @see: self.isAddSegmentsToolActive()
        @see: self.removeSegmentFromResizeSegmentList()
        """
        if self.propMgr is None:
            return False

        return self.propMgr.isRemoveSegmentsToolActive()

    def addSegmentToSegmentList(self, segment):
        """
        Adds the given segment to the segment list
        @param segment: The DnaSegment to be added to the segment list.
        Also does other things such as updating handles etc.
        @type sement: B{DnaSegment}
        @see: self.isAddSegmentsToolActive()
        @TODO: This allows ONLY PAM3 DNA segments to be added to the 
        segment list. NEEDS REVISION
        """
        if segment.is_PAM3_DnaSegment() and segment not in self._structList:
            self._structList.append(segment)

    def removeSegmentFromSegmentList(self, segment):
        """
        Removes the given segment from the segment list
        @param segment: The DnaSegment to be removed from the segment 
        list. Also does other things such as updating handles etc.
        @type sement: B{DnaSegment}
        @see: self.isRemoveSegmentsToolActive()
        """
        if segment in self._structList:
            self._structList.remove(segment)

    def getSegmentList(self):
        return self._structList

    def updateSegmentList(self):
        """
        Update the structure list, removing the invalid items in the structure
        @see:MultipleDnaSegmentResize_PropertyManager.model_changed()
        @see: self.getstructList()
        """
        #@TODO: Should this always be called in self.getStructList()??? But that 
        #could be SLOW because that method gets called too often by
        #the edit command's graphics mode. 
        def func(struct):
            if struct is not None and not struct.killed():
                if not struct.isEmpty():
                    return True

            return False                

        new_list = filter( lambda struct:
                           func(struct) , 
                           self._structList )        

        if len(new_list) != len(self._structList):        
            self._structList = new_list
            
    def setSegmentList(self, structList):
        """
        Replaces the list of segments with the 
        given segmentList. Calls the related method of self.struct. 
        @param structList: New list of segments. 
        @type  structList: list
        @see: DnaSegmentList.setResizeStructList()
        """
        self._structList = structList



