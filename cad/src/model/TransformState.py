# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
TransformState.py -- mutable transform classes, shared by TransformNodes

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.
"""


from foundation.state_utils import StateMixin
from utilities.Comparison import same_vals

_IDENTITY_TRANSLATION = V(0, 0, 0)
_IDENTITY_ROTATION = Q(1, 0, 0, 0)
    # review: let these be class attrs of the types, or of the classes V and Q?
    # REVIEW: does same_vals think 0 and 0.0 are the same? if not, should we use 0.0 here?
    # TEST whether anything looks like identity... note that if initial values use 0 this might be ok

class TransformState(StateMixin, object): # review: this class name ok? # review: where to file this? geometry? but it's a model object...
    ### SharedTransformSlot? SharedTransform? TransformSlot? TransformState?
    # not a slot, since it doesn't literally hold a transform (as separate data). TransformState?
    # shared is true, but anything might be shared.

    
    # todo: if object superclass, register with same_vals? note that this is a state-holding object, not a data one
    """
    A mutable orthonormal 3d transform, represented as a rotation followed by
    a translation (with the rotation and translation being undoable state).

    Changes to the transform value can be subscribed to.
    """
    # review:
    # - should some transforms own TransformControls and keep them up to date?
    #   - or should external client code handle that itself, by subscribing?
    #   (Note that external code has to manage the set of these in a complex way,
    #    in order to conserve the number of TransformControls.)
    # - can you subscribe separately to changes to its translation and rotation?
    #   - if so, are they public usagetracked attrs?
    # - make value accessible as data object? (if so, let it be an attr self.value)
    #   (note: a ref to this would autosubscribe to the two components; or we could cache constructed object)
    # - permit comparison as if we were data? (no, buggy if someone uses '==' when they mean 'is')
    
    # todo:
    # - undoable state for the data, ops to change the data (move, rotate, etc),
    # - make sure the data (or overall value only?) can be subscribed to

    rotation = State(Quaternion)

    translation = State(Vector3D)
    
        ### IMPLEM:
        # - how do we make State work here? ###REVIEW how we do it in Test_ConnectWithState, funmode
        #   - and how do we let it be undoable state? compatible with _s_attr decls?? ###
        # - get default value from type;
        # - define these type names
        ### REVIEW:
        # - review type name: Vector vs Vector3 vs Vector3D ? Or just use V and Q?

    value = TransformData( rotation, translation ) # REVIEW expr name, whether this formula def is appropriate

    
    # TODO: add formula for matrix?
    # TODO: somehow, integrate with TransformControl (or let this be used as one)
    
    def move(self, vector):
        self.translation = self.translation + vector

    def rotate(self, quat):
        """
        Rotate self around its own current origin.
        """
        self.rotation = self.rotation + quat # review operation order, compare with chunk.py --
            ### also compare default choice of center, THIS MIGHT BE WRONG

    def pivot(self, quat, center = None): ### REVIEW: merge with rotate? probably yes if default center is the same
        """
        Rotate self around a specified center.
        """
        nim, see chunk.py

    def is_identity(self): # review: optimize? special fast case if data never modified?
        return same_vals( (self.translation, self.rotation),
                          (_IDENTITY_TRANSLATION, _IDENTITY_ROTATION) )
    pass


class StaticTransform( TransformState):
    def nodecount(self):
        """
        Return the number of nodes we belong to.
        """
        nim
    pass
