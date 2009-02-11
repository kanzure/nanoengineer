# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
TransformState.py -- mutable transform classes, shared by TransformNodes

NOT YET USED as of 090204

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.
"""


from foundation.state_utils import StateMixin
from foundation.state_utils import copy_val

from utilities.Comparison import same_vals

# ==

ORIGIN = V(0, 0, 0)
_IDENTITY_TRANSLATION = V(0, 0, 0)
_IDENTITY_ROTATION = Q(1, 0, 0, 0)
    # review: let these be class attrs of the types, or of the classes V and Q?
    # REVIEW: does same_vals think 0 and 0.0 are the same? if not, should we use 0.0 here?
    # TEST whether anything looks like identity... note that if initial values use 0 this might be ok

# ==

class TransformState(StateMixin, object):
    """
    A mutable orthonormal 3d transform, represented as a rotation followed by
    a translation (with the rotation and translation being undoable state).

    Changes to the transform value can be subscribed to. ###doc how
    """
    # REVIEW:
    # - can you subscribe separately to changes to its translation and rotation?
    #   - if so, are they public usagetracked attrs?
    # - make value accessible as data object? (if so, let it be an attr self.value)
    #   (note: a ref to this would autosubscribe to the two components; or we could cache constructed object)
    # - permit comparison as if we were data? (no, buggy if someone uses '==' when they mean 'is')
    
    # todo:
    # - undoable state for the data
    # - finish nim ops to change the data (translate, rotate, etc),
    # - make sure the data (or overall value only?) can be subscribed to

    # TODO: make the State version work... initially we just use hand-invals, below.
    # but we'll need to make State work here as soon as we need to usage-track these
    # for purposes of properly implementing the DrawingSet graphics API.
    #
    ##rotation = State(Quaternion)
    ##
    ##translation = State(Vector3D)
    ##
    ##    ### IMPLEM:
    ##    # - how do we make State work here? ###REVIEW how we do it in Test_ConnectWithState, funmode
    ##    #   - and how do we let it be undoable state? compatible with _s_attr decls?? ###
    ##    # - get default value from type;
    ##    # - define these type names
    ##    ### REVIEW:
    ##    # - review type name: Vector vs Vector3 vs Vector3D ? Or just use V and Q?

    rotation = _IDENTITY_ROTATION
    translation = _IDENTITY_TRANSLATION
    
    # not yet needed:
    ## value = TransformData( rotation, translation ) # REVIEW expr name, whether this formula def is appropriate

    
    # TODO: add formula for matrix? (to help merge with TransformControl?)


    def _kluge_manual_inval(self):
        """
        Kluge: manually invalidate our overall transform value.

        @note: calls only needed until we support State decls for
               self.rotation and self.translation;
               implem only needed in some subclasses
        """
        return
    
    def applyDataFrom(self, other):
        """
        """
        self.rotate( other.rotation, center = ORIGIN)
        self.translate( other.translation)
        
    def translate(self, vector): # see also 'def move' in other classes
        self.translation = self.translation + vector
        self._kluge_manual_inval()

    def rotate(self, quat, center = None):
        """
        Rotate self around self.translation, or around the specified center.
        """
        self.rotation = self.rotation + quat # review operation order, compare with chunk.py --
            ### also compare default choice of center, THIS MIGHT BE WRONG
        if center is not None:
            offset = self.translation - center
            self.translate( quat.rot(offset) - offset ) # REVIEW - compare with chunk.py
        self._kluge_manual_inval()
        return

    def is_identity(self): # review: optimize? special fast case if data never modified?
        return same_vals( (self.translation, self.rotation),
                          (_IDENTITY_TRANSLATION, _IDENTITY_ROTATION) )
    pass

# ==

class StaticTransform( TransformState):
    """
    A subclass of TransformState that keeps track of which nodes it belongs to,
    and owns a TransformControl, and maintains it to always hold the same transform
    value as self.
    """
    # REVIEW: merge this class with TransformControl?
    ### IMPLEM: intercept changes and inval or update our TC... and its own subscribers in the graphics code...

    transformControl = None
    
    def __init__(self, value = None, tc = None):
        self._nodes = {}
        if value is not None:
            # copy our value from the given value or TransformState
            if isinstance(value, TransformState):
                self.rotation = copy_val(value.rotation)
                self.translation = copy_val(value.translation)
            else:
                assert 0 # nim
        assert tc ### probably required by other code... REVIEW
        if tc is not None:
            self.transformControl = tc ### IMPLEM proper fields/effects and maintenance of the relationship
        return
    
    def add_node(self, node):
        self._nodes[node] = node
        return

    def del_node(self, node):
        del self._nodes[node]
        return
    
    def nodecount(self):
        """
        Return the number of nodes we belong to.
        """
        return len(self._nodes)

    def iternodes(self):
        """
        yield the nodes we belong to
        """
        return self._nodes.itervalues()
    
    pass

# ==

class DynamicTransform( TransformState):
    """
    A subclass of TransformState that keeps track of which objects bridge
    between nodes which have it and nodes which don't have it, and passes
    its value invalidations on to those objects.
    """
    def __init__(self, nodes):
        """
        Initialize self, and add self to the given nodes.
        """
        TransformState.__init__(self)
        self._nodes = nodes # list, not dict -- no need to modify or index
            # only needed for self.destroy();
            # not needed for determining whether node-bridging objects added
            # later are self-bridging, since our nodes point to us too
            # (and anyway, AFAIK we never add bridging objects later)
        for node in nodes:
            node.dynamic_transform = self ### REVIEW; needs to inval subscribers
        self._bridging_objects = self._get_bridging_objects()
        # note: if our initial value wasn't identity, we'd also need to call
        # self._invalidate_transform_value() here.
        return

    def _get_bridging_objects(self):
        # Anything on one of our nodes which bridges *anything*,
        # is also known to be on self, therefore one of *our* bridging objects.
        # More precisely: it's on self; it's not only on self (or not bridging);
        # thus it's a self-bridging object (a node on self, a node not on self).
        res = []
        for node in self.nodes:
            res.extend( node.bridging_objects() )
            ### REVIEW: can one be included more than once? if so, use a dict...
            # guess: yes, once we have multi-node ones. ### 
        return res

    def _kluge_manual_inval(self):
        TransformState._kluge_manual_inval(self)
        self._invalidate_transform_value()
        
    def _invalidate_transform_value(self):
        for bo in self._bridging_objects:
            bo.invalidate_distortion()
        return

    pass

# end
