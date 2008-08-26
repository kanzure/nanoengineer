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

DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND = False

_superclass = SelectChunks_GraphicsMode
class BuildNanotube_GraphicsMode(SelectChunks_GraphicsMode):
    """
    """

    def chunkLeftUp(self, aChunk, event):
        """
        Upon chunkLeftUp, it enters the segment edit command
        This is an alternative implementation. As of 2008-03-03,
        we have decided to change this implementation. Keeping the
        related methods alive if, in future, we want to switch to this
        implementation and/or add a user preference to do this.
        """
        _superclass.chunkLeftUp(self, aChunk, event)

        if DEBUG_CLICK_ON_OBJECT_ENTERS_ITS_EDIT_COMMAND:
            if aChunk.picked:
                segmentGroup = aChunk.parent_node_of_class(NanotubeSegment)
                if segmentGroup is not None:
                    segmentGroup.edit()

    def _is_cntGroup_highlighting_enabled(self):
        """
        Overrides SelectChunks_GraphicsMode._is_cntGroup_highlighting_enabled()

        Returns a boolean that decides whether to highlight the whole
        NanotubeGroup or just the chunk of the glpane.selobj.
        Example: In default mode (SelectChunks_graphicsMode) if the cursor is
        over an atom or a bond which belongs to a NanotubeGroup, the whole
        NanotubeGroup is highlighted. But if you are in buildCnt mode, the
        individual strand and axis chunks will be highlighted in this case.
        Therefore, subclasses of SelectChunks_graphicsMode should override this
        method to enable or disable the NanotubeGroup highlighting. (the Default
        implementation returns True)
        @see: self._get_objects_to_highlight()
        @see: self.drawHighlightedChunk()
        @see : self.drawHighlightedObjectUnderMouse()
        """
        return False


    def _drawCursorText(self):
        """
        Draw the text near the cursor. It gives information about number of
        basepairs/bases being added or removed, length of the segment (if self.struct
        is a strand etc.
        @see: DnaSegment_GraphicsMode,  DnaStrand_GraphicsMode  (subclasses of
        this class where this is being used.
        """
        if hasattr(self.command, 'grabbedHandle') and hasattr(self.command,
                                                              'getCursorText'):
            if self.command.grabbedHandle is not None:
                #Draw the text next to the cursor that gives info about
                #number of base pairs etc

                text , textColor = self.command.getCursorText()
                self.glpane.renderTextNearCursor(text,
                                                 offset = 30,
                                                 textColor = textColor)








