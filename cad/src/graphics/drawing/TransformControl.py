# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
TransformControl.py -- A local coordinate frame for a set of CSDLs.

@author: Russ
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

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

from graphics.drawing.ColorSorter import eventStamp

from geometry.VQT import V, Q, A
import Numeric

def floatIdent(size):
    return Numeric.asarray(Numeric.identity(size), Numeric.Float)

def qmat4x4(quat):
    """
    Convert the 3x3 matrix from a quaternion into a 4x4 matrix.
    """
    mat = floatIdent(4)
    mat[0:3, 0:3] = quat.matrix
    return mat

_transform_id_counter = 0

class TransformControl:
    """
    Manage a set of CSDL's sharing a common local coordinate frame.

    The 4x4 transform matrix starts out as the identity, and gets a sequence of
    rotations and translations applied to it by the rotate() and translate()
    methods.

    You can also reset to the identity and apply a rotation and a translation in
    one operation with the identTranslateRotate() method.
    
    If you want the transform back into a rotation quaternion and translation
    vector, use the getRotTrans method.  Normally, we leave the transform in
    matrix form since that's what we'll need for drawing primitives in shaders.
    (No quaternion or even rotation matrix functions are built in over there.)
    """

    def __init__(self):
        # A unique integer ID for each TransformControl.
        global _transform_id_counter
        _transform_id_counter += 1
        self.transform_id = _transform_id_counter

        # Support for lazily updating drawing caches, namely a
        # timestamp showing when this transform matrix was last changed.
        self.changed = eventStamp()

        self.transform = floatIdent(4)

        # Use the integer IDs of the CSDLs as keys in a dictionary.
        self.CSDLs = {}

        return

    # ==
        
    def rotate(self, quat):
        """
        Post-multiply the transform with a rotation given by a quaternion.
        """
        self.transform = Numeric.matrixmultiply(self.transform, qmat4x4(quat))
        self.changed = eventStamp()
        return

    def translate(self, vec)
        """
        Post-multiply the transform with a translation given by a 3-vector.
        """
        # This only affects the fourth row x,y,z elements.
        self.transform[3, 0:3] += vec
        self.changed = eventStamp()
        return
        
    def identTranslateRotate(self, vec, quat):
        """
        Clear the transform to the product of a translate and a rotate.
        """
        self.transform = floatIdent(4)
        self.translate(vec)
        self.rotate(quat)
        return
    
    def getTranslateRotate(self):
        """
        Return the transform, decomposed into a translation 3-vector and a
        rotation quaternion.
        """
        # With no scales, skews, or perspective the right column is [0, 0, 0,
        # 1].  The upper right 3x3 is a rotation matrix giving the orientation
        # of the new right-handed orthonormal local coordinate frame, and the
        # left-bottom-row 3-vector is the translation that positions the origin
        # of that frame.
        vec = self.transform[3, 0:3]
        quat = Q(self.transform[0, 0:3],
                 self.transform[1, 0:3],
                 self.transform[2, 0:3])
        return (vec, quat)

    # ==

    # A subset of the set-type API.
    def addCSDL(self, csdl):
        """
        Add a CSDL to the TransformControl.
        """
        self.CSDLs[csdl.csdl_id] = csdl
        return

    def removeCSDL(self, csdl):
        """
        Remove a CSDL from the TransformControl.
        Raises KeyError if not present.
        """
        del self.CSDLs[csdl.csdl_id]     # May raise KeyError.
        return

    def discardCSDL(self, csdl):
        """
        Discard a CSDL from the TransformControl, if present.
        No error if it isn't.
        """
        if csdl.csdl_id in self.CSDLs:
            del self.CSDLs[csdl.csdl_id]
            pass

        return
    
    pass # End of class TransformControl.

