# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad, Mark
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO as of 2008-05-06:
Needs Refactoring. It was originally duplicated from BuildDna_GraphicsMode
(for an experimental implementation of new Nanotube command)
There needs to be a common superclass for Build'Structure' mode and
all the edit structure modes (commands) such as DnaSegment,
DnaStrand_GraphicsMode, NanotubeSegment_GraphicsMode etc
"""

from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from cnt.model.NanotubeSegment import NanotubeSegment
from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT

DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND = True

_superclass = SelectChunks_GraphicsMode
class BuildNanotube_GraphicsMode(SelectChunks_GraphicsMode):
    """
    Graphics mode for the Build Nanotube command. 
    """

    def chunkLeftUp(self, aChunk, event):
        """
        Upon chunkLeftUp, it enters the nanotube edit command
        This is an alternative implementation. As of 2008-03-03,
        we have decided to change this implementation. Keeping the
        related methods alive if, in future, we want to switch to this
        implementation and/or add a user preference to do this.
        """

        _superclass.chunkLeftUp(self, aChunk, event)

        if self.glpane.modkeys is not None:
            #Don't go further if some modkey is pressed. We will call the
            #edit method of the nanotube only if no modifier key is
            #pressed

            return

        if not self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT):
            return

        #@TODO: If the object under mouse was double clicked, don't enter the
        #edit mode, instead do appropriate operation such as expand selection or
        #contract selection (done in superclass)
        #Note: when the object is just single clicked, it becomes editable).
        
        if self.editObjectOnSingleClick():
            if aChunk.picked:
                segmentGroup = aChunk.parent_node_of_class(NanotubeSegment)
                if segmentGroup is not None:
                    segmentGroup.edit()
        return

    def editObjectOnSingleClick(self):
        """
        Subclasses can override this method. If this method returns True,
        when you left click on a DnaSegment or a DnaStrand, it becomes editable
        (i.e. program enters the edit command of that particular object if
        that object is editable)
        @see: MakeCrossover_GraphicsMode.editObjectOnSingleClick()
        """
        if DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND:
            return True
        return False
    
    def _drawCursorText(self):
        """
        Draw the text near the cursor. It gives information about length of 
        the nanotube.
        """
        if hasattr(self.command, 'grabbedHandle') and \
           hasattr(self.command, 'getCursorText'):
            if self.command.grabbedHandle is not None:
                #Draw the text next to the cursor that gives info about
                #nanotube length, etc.
                text , textColor = self.command.getCursorText()
                self.glpane.renderTextNearCursor(text,
                                                 offset = 30,
                                                 textColor = textColor)
                pass
            pass
        return
        
    pass








