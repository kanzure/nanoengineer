# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
GLPane_minimal.py -- common superclass for GLPane-like widgets.

$Id$

History:

bruce 070914 made this to remind us that GLPane and ThumbView
need a common superclass (and have common code that needs merging).
It needs to be in its own file to avoid import loop problems.
"""

from PyQt4.Qt import QGLWidget

class GLPane_minimal(QGLWidget): #bruce 070914
    """
    Stub superclass, just so GLPane and ThumbView can have a common superclass.
    TODO:
    They share a lot of code, which ought to be merged into this superclass.
    Once that happens, it might as well get renamed.
    """
    def should_draw_valence_errors(self):
        """
        Return a boolean to indicate whether valence error
        indicators (of any kind) should ever be drawn in self.
        (Each specific kind may also be controlled by a prefs
        setting, checked independently by the caller. As of 070914
        there is only one kind, drawn by class Atom.)
        """
        return False
    
    pass

# end
