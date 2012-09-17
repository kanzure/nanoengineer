# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details.
"""
BuildProtein_GraphicsMode.py

@author: Mark
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.

"""
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_GraphicsMode
from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT

DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND = True

_superclass = SelectChunks_GraphicsMode
class BuildProtein_GraphicsMode(SelectChunks_GraphicsMode):
    """
    Graphics mode for Build Protein command.
    """

    def Enter_GraphicsMode(self):
        _superclass.Enter_GraphicsMode(self)
        return

    def chunkLeftUp(self, aChunk, event):
        """
        Upon chunkLeftUp, it enters the protein edit command
        This is an alternative implementation. As of 2008-03-03,
        we have decided to change this implementation. Keeping the
        related methods alive if, in future, we want to switch to this
        implementation and/or add a user preference to do this.
        """

        _superclass.chunkLeftUp(self, aChunk, event)

        if self.glpane.modkeys is not None:
            #Don't go further if some modkey is pressed. We will call the
            #edit method of the protein only if no modifier key is
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
                if aChunk.isProteinChunk():
                    aChunk.protein.edit(self.win)
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

    pass
