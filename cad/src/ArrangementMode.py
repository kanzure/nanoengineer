# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
Part arrangement mode functionality.

@author:    Mark Sims
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id: $
@license:   GPL
"""

from PyQt4.Qt import Qt
from modes import basicMode


class ArrangementMode(basicMode): #bruce 070813 split this out
    """
    Common superclass for arrangement modes such as for the Pan, Rotate, and
    Zoom tools.
    """

    # a safe way for now to override Done:
    def Done(self, new_mode = None):
        """
        [overrides basicMode.Done; this is deprecated, so doing it here
        is a temporary measure for Alpha, to be reviewed by Bruce ASAP after
        Alpha goes out; see also the removal of Done from weird_to_override
        in modes.py. [bruce and mark 050130]
        """
        ## [bruce's symbol to get him to review it soon: ####@@@@]
        resuming = False
        if new_mode is None:
            try:
                m = self.glpane.prevMode
                new_mode = m
                resuming = True
            except:
                pass

        #bruce 070813 added resuming arg
        return basicMode.Done(self, new_mode, resuming = resuming)

        
    def keyPress(self, key):
        # ESC - Exit mode.
        if key == Qt.Key_Escape: 
            self.Done()
        ### REVIEW: else, here?
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
        else:
            basicMode.Draw(self)   
            self.glpane.assy.draw(self.glpane)
            if prevMode:
                print "should no longer happen: prevMode is not None or a basicMode, but %r" % (prevMode,)
        return

