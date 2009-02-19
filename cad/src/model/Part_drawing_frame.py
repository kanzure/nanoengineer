# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Part_drawing_frame.py -- classes for use as a Part's drawing_frame

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090218 wrote this in part.py, then split into its own file
"""

# (todo: better name?)

# WARNING: The present scheme for Part._drawing_frame would not work
# if multiple threads could draw one Part, or if complex objects in
# a part (e.g. chunks) might be drawn twice in one frame. See comments
# near its use in Chunk.draw for ways we might need to generalize it.
# [bruce 070928/090218]

from utilities.debug import print_compact_stack
from utilities.prefs_constants import indicateOverlappingAtoms_prefs_key

from geometry.NeighborhoodGenerator import NeighborhoodGenerator

import foundation.env as env

class _Part_drawing_frame_superclass:
    """
    """
    # repeated_bonds_dict lets bonds (or ExternalBondSets) avoid being
    # drawn twice. It maps id(bond) to bond (for any Bond or ExternalBondSet)
    # for all bonds that might otherwise be drawn twice. It is public
    # for use and modification by anything that draws bonds, but only
    # during a single draw call (or a single draw of a subset of the model).
    #
    # Note that OpenGL drawing (draw methods) uses it only for external
    # bonds, but POV-Ray drawing (writepov methods) uses it for all
    # bonds; this is ok even if some writepov methods someday call some
    # draw methods.
    repeated_bonds_dict = None

    # These are for implementing optional indicators about overlapping atoms.
    _f_state_for_indicate_overlapping_atoms = None
    indicate_overlapping_atoms = False

    use_drawingsets = False # whether to draw CSDLs using DrawingSets

    pass

class Part_drawing_frame(_Part_drawing_frame_superclass):
    """
    One of these is created whenever drawing all or part of a Part,
    once per "drawing frame" (e.g. call of Part.draw()).

    It holds attributes needed during a single draw call
    (or, a draw of a portion of the model).

    See superclass code comments for documentation of attributes.

    For more info, see docstring of Part.before_drawing_model.
    """
    def __init__(self):
        
        self.repeated_bonds_dict = {}

        # Note: this env reference may cause undesirable usage tracking,
        # depending on when it occurs. This should cause no harm --
        # only a needless display list remake when the pref is changed.
        self.indicate_overlapping_atoms = \
            env.prefs[indicateOverlappingAtoms_prefs_key]

        if self.indicate_overlapping_atoms:
            TOO_CLOSE = 0.3 # stub, guess; needs to not be true even for
                # bonded atoms, or atoms and their bondpoints,
                # but big enough to catch "visually hard to separate" atoms.
                # (1.0 is far too large; 0.1 is ok but too small to be best.)
                # It would be much better to let this depend on the elements
                # and whether they're bonded, and not hard to implement
                # (each atom could be asked whether it's too close to each
                #  other one, and take all this into account). If we do that,
                # this value should be the largest tolerance for any pair
                # of atoms, and the code that uses this NeighborhoodGenerator
                # should do more filtering on the results. [bruce 080411]
            self._f_state_for_indicate_overlapping_atoms = \
                NeighborhoodGenerator( [], TOO_CLOSE, include_singlets = True )
            pass
        
        return

    # review: should some of the following methods be moved to PartDrawer?
    # maybe logically yes, but at least for draw_csdl_in_drawingset,
    # that would make access slower and less convenient, so not for now.
    
    def setup_for_drawingsets(self):
        # review: needed in fake_Part_drawing_frame too??
        """
        """
        self.use_drawingsets = True
        self._drawingset_contents = {}

    def draw_csdl_in_drawingset(self, csdl, intent): #### CALL IN MORE PLACES
        """
        When self.use_drawingsets is set, model component drawing code which
        wants to draw a CSDL should pass it to this method rather than
        drawing it directly.

        At the end of the current drawing frame, all csdls passed to this method
        will be added to (or maintained in) an appropriate DrawingSet,
        and all DrawingSets will be drawn, by our part's PartDrawer.

        @param csdl: a CSDL to draw later
        @type csdl: ColorSortedDisplayList

        @param intent: specifies how the DrawingSet which csdl ends up in
                       should be drawn (transform, other GL state, draw options)
        @type intent: not defined here, but must be useable as a dict key

        @return: None

        This API requires that every csdl to be drawn must be passed here in
        every frame (though the DrawingSets themselves can be persistent
        and incrementally updated, depending on how the data accumulated here
        is used). A more incremental API would probably perform better
        but would be much more complex, having to deal with chunks which
        move in and out of self, get killed, or don't get drawn for any other
        reason, and also requiring chunks to "diff" their own drawing intents
        and do incremental update themselves.
        """
        try:
            csdl_dict = self._drawingset_contents[intent]
        except KeyError:
            csdl_dict = self._drawingset_contents[intent] = {}
        csdl_dict[csdl.csdl_id] = csdl
        return

    def get_drawingset_intent_csdl_dicts(self):
        """
        A return a dict from intent to a dict from csdl.csdl_id to csdl
        (with intent and csdl having been passed to draw_csdl_in_drawingset).
        
        Meant to be used only by PartDrawer.
        """
        return self._drawingset_contents

    pass

class fake_Part_drawing_frame(_Part_drawing_frame_superclass):
    """
    Use one of these "in between draw calls" to avoid or mitigate bugs.
    """
    # todo: print a warning whenever our methods/attrs are used,
    # or create self on demand and print a warning then.
    def __init__(self):
        print_compact_stack(
            "warning: fake_Part_drawing_frame is being instantiated: " )
        # done in superclass: self.repeated_bonds_dict = None
            # This is necessary to remove any chance of self surviving
            # for more than one draw of one object (since using an actual
            # dict then would make bonds sometimes fail to be drawn).
            # Client code must tolerate this value.
    pass
        
# end
