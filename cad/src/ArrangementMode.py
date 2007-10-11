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

    Provides the declarations that make a command temporary,
    a binding from Escape key to Done method,
    and a Draw method which delegates to the Draw method
    of the prior command (commandSequencer.prevMode).
    """
    command_can_be_suspended = False #bruce 071011
    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)
    
    def keyPress(self, key):
        # ESC - Exit mode.
        if key == Qt.Key_Escape: 
            self.Done()
        ### REVIEW: should we add an 'else' here?
        basicMode.keyPress(self, key) # Fixes bug 1172. mark 060321
        
    def Draw(self): ### verify same as in others
        # bruce 070813 revised this to use prevMode -- clean up and commit, and
        # share w/ others
        glpane = self.glpane
        try:
            # can be mode object or (deprecated and worse, but common) modename
            # string; or None
            prevMode = glpane.prevMode
        except AttributeError:
            prevMode = None
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
