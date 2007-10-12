# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
Part arrangement mode functionality.

@author:    Mark and Bruce
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id: $
@license:   GPL
"""

from PyQt4.Qt import Qt
from modes import basicMode


class ArrangementMode(basicMode): #bruce 070813 split this out
    """
    Common superclass for temporary view-change commands
    such as the Pan, Rotate, and Zoom tools.

    TemporaryCommand_OverlayDrawing ?

    Provides the declarations that make a command temporary,
    a binding from Escape key to Done method,
    and a Draw method which delegates to the Draw method
    of the prior command (commandSequencer.prevMode).
    Otherwise inherits from basicMode.
    """
    # == Command part

    command_can_be_suspended = False #bruce 071011
    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)

    # == GraphicsMode part
    
    def keyPress(self, key):
        # ESC - Exit mode.
        if key == Qt.Key_Escape: 
            self.Done()
        else:
            #bruce 071012 bugfix: add 'else' to prevent letting basicMode
            # also handle Key_Escape and do assy.selectNone.
            # I think that was a bug, since you might want to pan or zoom etc
            # in order to increase the selection. Other ways of changing
            # the viewpoint (eg trackball) don't deselect everything.
            basicMode.keyPress(self, key) # Fixes bug 1172 (F1 key). mark 060321
        
    def Draw(self): 
        # bruce 070813 revised this to use prevMode
        # TODO soon: move this into a new method in the command sequencer, Draw_by_prior_command or so;
        # have it return whether it called a draw method or not (so we know whether to call our fallback drawing code)
        
        glpane = self.glpane # really command sequencer
        try:
            # prevMode can be mode object or (deprecated and worse, but common -- no, should never happen anymore) modename
            # string; or None
            prevMode = glpane.prevMode
        except AttributeError:
            prevMode = None # should never happen anymore
        if prevMode and isinstance(prevMode, basicMode):
            # fixes bug in which it doesn't show the right things for cookie or
            # extrude modes [partly; untested]
            prevMode.Draw()
            # WARNING/TODO: this assumes there is at most one saved command
            # which should be drawn. If this changes, we'll need to replace
            # .prevMode with a deeper command stack in the Command Sequencer
            # which provides a way to draw whatever each suspended command
            # thinks it needs to; or we'll need to arrange for prevMode
            # to *be* that stack, delegating Draw to each stack element in turn.
            # Either way, it might be clearest to just call a new CommandSequencer
            # method to "draw the stuff from all the saved commands".
            # Most of the code around this comment would become part of that method.
            # [bruce 071011]
        else:
            basicMode.Draw(self)   
            self.glpane.assy.draw(self.glpane)
            if prevMode:
                print "should no longer happen: prevMode is not None or a basicMode, but %r" % (prevMode,)
        return

    pass

# end
