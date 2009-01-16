# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

History:

TODO:
See ListWidgetItems_Command_Mixin for details.

@see: MakeCrossovers_GraphicsMode
      ListWidgetItems_Command_Mixin
      ListWidgetItems_PM_Mixin
"""

class ListWidgetItems_GraphicsMode_Mixin:

    def update_cursor_for_no_MB(self):
        """
        Update the cursor for no mouse button pressed
        """  
        if self.command:
            if self.command.isAddSegmentsToolActive():
                self.o.setCursor(self.win.addSegmentToResizeSegmentListCursor)
                return
            if self.command.isRemoveSegmentsToolActive():
                self.o.setCursor(self.win.removeSegmentFromResizeSegmentListCursor)
                return

    def chunkLeftUp(self, a_chunk, event):
        """
        Overrides superclass method. If add or remove segments tool is active, 
        upon leftUp, when this method gets called, it modifies the list 
        of segments by self.command.
        @see: self.update_cursor_for_no_MB()
        @see: self.end_selection_from_GLPane()
        """
        if self.command.isAddSegmentsToolActive() or \
           self.command.isRemoveSegmentsToolActive():            
            if a_chunk.isAxisChunk():   
                segmentGroup = a_chunk.parent_node_of_class(
                    self.win.assy.DnaSegment)
                if segmentGroup is not None:
                    if self.command.isAddSegmentsToolActive():
                        segmentList = [segmentGroup]
                        self.command.ensureSegmentListItemsWithinLimit(segmentList)
                    if self.command.isRemoveSegmentsToolActive():
                        self.command.removeSegmentFromSegmentList(segmentGroup)

            self.end_selection_from_GLPane()
            return


    def end_selection_from_GLPane(self):
        """
        Overrides superclass method.  In addition to selecting  or deselecting 
        the chunk, if  a tool that adds Dna segments to the segment list in 
        the property manager is active, this method also adds 
        the selected dna segments to that list. Example, if user selects 
        'Add Dna segments' tool and does a lasso selection , then this also
        method adds the selected segments to the list. Opposite behavior if 
        the 'remove segments from segment list too, is active)
        """       
        selectedSegments = self.win.assy.getSelectedDnaSegments()
        if self.command.isAddSegmentsToolActive():
            self.command.ensureSegmentListItemsWithinLimit(selectedSegments)
        if self.command.isRemoveSegmentsToolActive():
            for segment in selectedSegments:
                self.command.removeSegmentFromSegmentList(segment)

