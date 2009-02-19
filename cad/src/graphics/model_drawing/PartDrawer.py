# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
PartDrawer.py -- class PartDrawer, for drawing a Part

@author: Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.


History:

Written over several years as part of class Part in part.py.

Bruce 090218 split this out of class Part.

TODO: also move part of before_drawing_model, after_drawing_model,
and draw into here from Part; add DrawingSet features.
"""


from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glDisable
from OpenGL.GL import GL_DEPTH_TEST
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix
from OpenGL.GL import glEnable

from PyQt4.Qt import Qt
from PyQt4.Qt import QFont, QString

# ==

class PartDrawer(object):
    """
    Drawing code needed by class Part, as a cooperating object.
    """

    def __init__(self, part):
        self._part = part #k needed?
        return

    def destroy(self):
        self._part = None
        return

    # note: the Part methods draw, before_drawing_model, after_drawing_model
    # are not sensible to define here for now, but they can call methods
    # in self.
    
    def draw_text_label(self, glpane, text):
        """
        #doc; called from GLPane.paintGL just after it calls mode.Draw()
        """
        # caller catches exceptions, so we don't have to bother

        del self

        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
            # Note: disabling GL_DEPTH_TEST properly affects 2d renderText
            # (as used here), but not 3d renderText. For more info see
            # today's comments in Guides.py. [bruce 081204 comment]
        glPushMatrix() # REVIEW: needed? [bruce 081204 question]
        font = QFont(QString("Helvetica"), 24, QFont.Bold)
        glpane.qglColor(Qt.red) # this needs to be impossible to miss -- not nice-looking!
            #e tho it might be better to pick one of several bright colors
            # by hashing the partname, so as to change the color when the part changes.
        # this version of renderText uses window coords (0,0 at upper left)
        # rather than model coords (but I'm not sure what point on the string-image
        # we're setting the location of here -- guessing it's bottom-left corner):
        glpane.renderText(25,40, QString(text), font)
        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        return

    def draw_drawingsets(self):
        """
        Using info collected in self._part.drawing_frame,
        update our cached DrawingSets for this frame;
        then draw them.
        """
        drawing_frame = self._part.drawing_frame
        for intent, csdls in drawing_frame.get_drawingset_intent_csdl_dicts().items():
            # stub: make drawingset from these csdls, then draw it based on intent
            print "draw_drawingsets stub:", intent, len( csdls ) ####
        return
    
    pass

# end
