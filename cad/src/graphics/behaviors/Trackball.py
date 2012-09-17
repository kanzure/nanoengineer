# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Trackball.py - one kind of Trackball.

class Trackball produces incremental quaternions using a mapping of the screen
onto a sphere, tracking the cursor on the sphere.

@author: Josh
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

Note: bruce 071216 moved class Trackball into its own file, from VQT.py.
"""

import foundation.env as env
from utilities.prefs_constants import mouseSpeedDuringRotation_prefs_key

from geometry.VQT import Q
from geometry.VQT import proj2sphere

class Trackball:
    """
    A trackball object.
    """
    #bruce 060514 revisions:
    # - add/revise some docstrings and comments
    # - compare vectors and quats to None rather than using boolean tests (possible bugfix)
    # - clean up some duplicated code
    # Planned generalizations (nim): let a global setting control the trackball algorithm.
    # (In principle, that should be supplied by the caller, since it's associated with
    #  the interface in which the trackball is being used.)
    def __init__(self, wide, high):
        """
        Create a Trackball object.
        Arguments are window width and height in pixels (the same as for self.rescale()),
        or can be guesses if the caller will call self.rescale() with correct arguments
        before the trackball is used.
        """
        self.rescale(wide, high)
        self.quat = Q(1,0,0,0)
        self.oldmouse = None
            # note: oldmouse and newmouse are not mouse positions; they come out of proj2sphere.
            # I think they're related to a non-incremental trackball goal; not sure yet. [bruce 060514 comment]
        self.mouseSpeedDuringRotation = None

    def rescale(self, wide, high):
        """
        This should be called when the trackball's window or pane has been resized
        to the given values (window width and height in pixels).
        """
        self.w2 = wide / 2.0
        self.h2 = high / 2.0
        self.scale = 1.1 / min( wide / 2.0, high / 2.0)

    def start(self, px, py):
        """
        This should be called in a mouseDown binding, with window coordinates of the mouse.
        """
        # ninad060906 initializing the factor 'mouse speed during rotation'
        # here instead of init so that it will come into effect immediately
        self.mouseSpeedDuringRotation = \
            env.prefs[ mouseSpeedDuringRotation_prefs_key]

        self.oldmouse = proj2sphere( (px - self.w2) * self.scale * self.mouseSpeedDuringRotation,
                                     (self.h2 - py) * self.scale * self.mouseSpeedDuringRotation )

    def update(self, px, py, uq = None):
        """
        This should be called in a mouseDrag binding, with window coordinates of the mouse;
        return value is an incremental quat, to be used in conjunction with uq as explained below.
           For trackballing the entire model space (whose orientation is stored in (for example) glpane.quat),
        caller should not pass uq, and should increment glpane.quat by the return value (i.e. glpane.quat += retval).
           For trackballing an object with orientation obj.quat, drawn subject to (for example) glpane.quat,
        caller should pass uq = glpane.quat, and should increment obj.quat by the return value.
        (If caller didn't pass uq in that case, our retval would be suitable for incrementing obj.quat + glpane.quat,
         or glpane.quat alone, but this is not the same as a retval suitable for incrementing obj.quat alone.)
        """
        #bruce 060514 revised this code (should be equivalent to the prior code), added docstring
        #ninad 060906 added 'rotation sensitivity to this formula. the rotation sensitivity will be used
        #while middle drag rotating the model. By default a lower value is set for this and can be adjusted
        #via a user preference. This helps mitigate bug 1856
        newmouse = proj2sphere((px - self.w2) * self.scale * self.mouseSpeedDuringRotation,
                               (self.h2 - py) * self.scale * self.mouseSpeedDuringRotation)
        if self.oldmouse is not None:
            quat = Q(self.oldmouse, newmouse)
            if uq is not None:
                quat = uq + quat - uq
        else:
            print "warning: trackball.update sees oldmouse is None (should not happen)" #bruce 060514
            quat = Q(1,0,0,0)
        self.oldmouse = newmouse
        return quat

    pass # end of class Trackball

# end
