# Copyright 2009 Nanorex, Inc.  See LICENSE file for details. 
"""
DrawingSetCache.py -- cache of DrawingSets with associated drawing intents

@author: Bruce
@version: $Id$
@copyright: 2009 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce 090313 moved into its own file, from GLPane_drawingset_methods.py.

TODO: add usage tracking.
"""

class DrawingSetCache(object): #bruce 090227
    """
    A persistent cache of DrawingSets, one for each "drawing intent"
    ever passed to glpane.draw_csdl (as presently used by
    GLPane_drawingset_methods).

    The drawing sets are public for incremental construction and for
    drawing, as is our dictionary of them, self.dsets.

    All attributes and methods are public.
    """
    # default values of instance variables
    
    saved_change_indicator = None #bruce 090309
        # public for set and compare (by '==')
    
    def __init__(self, cachename, temporary):
        self.cachename = cachename
        self.temporary = temporary
        self.dsets = {} # maps drawing intent to DrawingSet;
            # public for access and modification, and so are the dsets it contains
        return
    
    def destroy(self):
        for dset in self.dsets.values():
            dset.destroy()
        self.dsets = {}
        self.saved_change_indicator = None
        return

    pass

# end
