# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
TransformControl.py -- A local coordinate frame for a set of CSDLs.

@author: Russ
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:
Originally written by Russ Fish; designed together with Bruce Smith.

================================================================

See design comments on:
* GL contexts, CSDLs and DrawingSet in DrawingSet.py
* TransformControl in TransformControl.py
* VBOs, IBOs, and GLPrimitiveBuffer in GLPrimitiveBuffer.py
* GLPrimitiveSet in GLPrimitiveSet in GLPrimitiveSet.py

== TransformControl ==

* CSDLs are now created with a TransformControl reference as an argument
  (and are internally listed in it while they exist).

  - This TransformControl reference is constant (although the transform in the
     TransformControl is mutable.)

  - For convenience, the TransformControl argument can be left out if you don't
    want to use a TransformControl to move the CSDL. This has the same effect as
    giving a TransformControl whose transform remains as the identity matrix.

* A TransformControl controls where a set of CSDLs appear, with a common
  coordinate transform giving the local coordinate system for the objects in the
  CSDLs.

* A TransformControl gains and loses CSDLs, as they are created in it, or
  destroyed.

* The API need not provide external access to, or direct modification of, the
  set of CSDLs in a TransformControl.

* The transform is mutable, represented by a quaternion and a translation vector
  (or the equivalent).  (Later, we may have occasion to add a scale as well.)

* Interactions like dragging can be efficiently done by drawing the drag
  selection as a separate DrawingSet, viewed through an incremental modeling
  transform controlled by mouse drag motion.  Afterward, the drag transform will
  be combined with the transform in the TransformControls for the selected CSDLs
  (using changeAllTransforms, below).

* Since there is no matrix stack to change in the middle of a batched draw,
  TransformControl transforms are stored in the graphics card RAM for use by
  vertex shaders, either in texture memory or constant memory, indexed by a
  transform_id.  Transform_ids are stored in per-vertex attribute VBOs.

** If this proves too slow or unworkable on some drivers which could otherwise
   be supported, there is a fallback option of modifying VBO vertex coordinates
   after transforms change (lazily, as needed for drawing).

* The parameters for primitives are stored in per-vertex attribute VBOs as well,
  in local coordinates relative to the TransformControl transform.

* DrawingSet.changeAllTransforms(transform) combines a given transform with
  those stored in the TransformControls of all CSDLs in this DrawingSet. (Note
  that this affects all CSDLs in those TransformControls, even if they are not
  in this DrawingSet.)
"""

import graphics.drawing.drawing_globals as drawing_globals

from geometry.VQT import V, Q, A
import Numeric
import math

from OpenGL.GL import glTranslatef, glRotatef

def floatIdent(size):
    return Numeric.asarray(Numeric.identity(size), Numeric.Float)

def qmat4x4(quat):
    """
    Convert the 3x3 matrix from a quaternion into a 4x4 matrix.
    """
    mat = floatIdent(4)
    mat[0:3, 0:3] = quat.matrix
    return mat

_transform_id_counter = -1

class TransformControl:
    """
    Store a shared mutable transform value for a set of CSDLs sharing a
    common local coordinate frame, and help the graphics subsystem
    render those CSDLs using that transform value. (This requires also storing
    that set of CSDLs.)

    The 4x4 transform matrix we store starts out as the identity, and can be
    modified using the rotate() and translate() methods, or reset using the
    setRotateTranslate() method.
    
    If you want self's transform expressed as the composition of a rotation
    quaternion and translation vector, use the getRotateTranslate method.
    """
    # REVIEW: document self.transform and self.transform_id as public attributes?
    # Any others? TODO: Whichever are not public, rename as private.
    
    # Implementation note:
    # Internally, we leave the transform in matrix form since that's what we'll
    # need for drawing primitives in shaders.
    # (No quaternion or even rotation matrix functions are built in over there.)
    
    def __init__(self):
        # A unique integer ID for each TransformControl.
        global _transform_id_counter
        _transform_id_counter += 1
        self.transform_id = _transform_id_counter

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this transform matrix was last changed.
        ### REVIEW: I think we only need a valid flag, not any timestamps --
        # at least for internal use. If we have clients but not subscribers,
        # then they could make use of our changed timestamp. [bruce 090203]
        self.changed = drawing_globals.eventStamp()
        self.cached = drawing_globals.NO_EVENT_YET

        self.transform = floatIdent(4)

        # Use the integer IDs of the CSDLs as keys in a dictionary.
        self.CSDLs = {}

        return

    # ==
        
    def rotate(self, quat):
        """
        Post-multiply self's transform with a rotation given by a quaternion.
        """
        self.transform = Numeric.matrixmultiply(self.transform, qmat4x4(quat))
        self.changed = drawing_globals.eventStamp()
        return

    def translate(self, vec):
        """
        Post-multiply the transform with a translation given by a 3-vector.
        """
        # This only affects the fourth row x,y,z elements.
        self.transform[3, 0:3] += vec
        self.changed = drawing_globals.eventStamp()
        return
        
    def setRotateTranslate(self, quat, vec):
        """
        Replace self's transform with the composition of a rotation quat (done
        first) and a translation vec (done second).
        """
        ## self.transform = floatIdent(4)
        ## self.rotate(quat)
        # optimize that:
        self.transform = qmat4x4(quat)
        self.translate(vec) # this also sets self.changed
        return
    
    def getRotateTranslate(self):
        """
        @return: self's transform value, as the tuple (quat, vec), representing
                 the translation 3-vector vec composed with the rotation
                 quaternion quat (rotation to be done first).
        @rtype: (quat, vec) where quat is of class Q, and vec is a length-3
                sequence of undocumented type.
        
        If self is being used to transform a 3d model, the rotation should be
        applied to the model first, to orient it around its presumed center;
        then the translation, to position the rotated model with its center in
        the desired location. This means that the opposite order should be used
        to apply them to the GL matrices (which give the coordinate system for
        drawing), i.e. first glTranslatef, then glRotatef.
        """
        # With no scales, skews, or perspective the right column is [0, 0, 0,
        # 1].  The upper right 3x3 is a rotation matrix giving the orientation
            ####         ^^^^^
            #### REVIEW: should this 'right' be 'left'?
            #### [bruce 090203 comment]
        # of the new right-handed orthonormal local coordinate frame, and the
        # left-bottom-row 3-vector is the translation that positions the origin
        # of that frame.
        quat = Q(self.transform[0, 0:3],
                 self.transform[1, 0:3],
                 self.transform[2, 0:3])
        vec = self.transform[3, 0:3]
        return (quat, vec)

    def applyTransform(self):
        """
        Apply self's transform to the GL matrix stack.
        (Pushing/popping the stack, if needed, is the caller's responsibility.)

        @note: this is used for display list primitives in CSDLs,
               but not for shader primitives in CSDLs.
        """
        (q, v) = self.getRotateTranslate()
        glTranslatef(v[0], v[1], v[2])
        glRotatef(q.angle * 180.0 / math.pi, q.x, q.y, q.z)
        return

    def updateSince(self, sinceStamp):
        """
        Do any updating necessary on cached drawing transforms.
        """
        ### REVIEW: I think passing or needing sinceStamp is a LOGIC BUG.
        # See comment in caller. [bruce 090203]
        if self.changed > sinceStamp or self.changed > self.cached:
            # XXX Update transforms in graphics card RAM here...
            pass
        return

    # ==

    # A subset of the set-type API.
    
    def addCSDL(self, csdl):
        """
        Add a CSDL to self.
        """
        self.CSDLs[csdl.csdl_id] = csdl
        return

    def removeCSDL(self, csdl):
        """
        Remove a CSDL from self.
        Raises KeyError if not present.
        """
        del self.CSDLs[csdl.csdl_id]  # May raise KeyError.
        return

    def discardCSDL(self, csdl):
        """
        Discard a CSDL from self, if present.
        No error if it isn't.
        """
        if csdl.csdl_id in self.CSDLs:
            del self.CSDLs[csdl.csdl_id]
            pass

        return
    
    pass # end of class TransformControl

