# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Csys.py -- a saved named view (including coordinate system for viewing)

@author: Mark
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Mark wrote this in Utility.py.

bruce 071026 moved it from Utility into a new file.
"""

from constants import gensym
from VQT import V, Q
from icon_utilities import imagename_to_pixmap
from Utility import SimpleCopyMixin
from Utility import Node
import platform
import env
from utilities.Log import greenmsg

class Csys(SimpleCopyMixin, Node):
    """
    The Csys is used to store all the parameters needed to save and restore a view.
    It is used in several distinct ways:
        1) as a Named View created by the user and visible as a node in the model tree
        2) internal use for storing the LastView and HomeView for every part
        3) internal use by Undo for saving the view that was current when a change was made
    """
    
    sym = "View"
    featurename = "Named View" #bruce 070604 added this

    copyable_attrs = Node.copyable_attrs + ('scale', 'pov', 'zoomFactor', 'quat') #bruce 060523
        # (note: for copy, this is redundant with _um_initargs (that's ok),
        #  but for Undo, it's important to list these here or give them _s_attr decls.
        #  This fixes a presumed bug (perhaps unreported -- now bug 1942) in Undo of Set_to_Current_View.
        #  Bug 1369 (copy) is fixed by _um_initargs and SimpleCopyMixin, not by this.)

    scale = pov = zoomFactor = quat = None # Undo might require these to have default values (not sure) [bruce 060523]

    def __init__(self, assy, name, scale, pov, zoomFactor, w, x = None, y = None, z = None):
        self.const_pixmap = imagename_to_pixmap("modeltree/csys.png")
        if name:
            Node.__init__(self, assy, name)
        else:
            Node.__init__(self, assy, gensym("%s-" % self.sym))
                #bruce 070604 genViewNum -> gensym [##e can we someday teach superclass to do this?]
        self.scale = scale
        assert type(pov) is type(V(1, 0, 0))
        self.pov = V(pov[0], pov[1], pov[2])
        self.zoomFactor = zoomFactor

        #bruce 050516 probable bugfix, using "is None" rather than "if not x and not y and not z:"
        if x is None and y is None and z is None:
            self.quat = Q(w)
            #bruce 050518 comment: this form is used with w an array of 4 floats (in same order
            # as in mmp file's csys record), when parsing csys mmprecords,
            # or with w a quat in other places.
        else:
            self.quat = Q(x, y, z, w)
            #bruce 050518 question: why are these in different order than in arglist? bug?? ###k
            # ... this is used with wxyz = 0.0, 1.0, 0.0, 0.0 to initialize both views for any Part. No other uses.
            # And order is not consistent with mmp record, either. Therefore I can and should revise it. Later.
            # Looks like the main error is that the vars are misnamed/misordered, both here and in init arglist.
            # Best revision would probably just be to disallow this form! #e 
        return

    def _um_initargs(self): #bruce 060523 to help make it copyable from the UI (fixes bug 1369 along with SimpleCopyMixin)
        "#doc [warning: see comment where this is called in this class -- it has to do more than its general spec requires]"
        # (split out of self.copy)
        if "a kluge is ok since I'm in a hurry":
            # the data in this Csys might not be up-to-date, since the glpane "caches it"
            # (if we're the Home or Last View of its current Part)
            # and doesn't write it back after every user event!
            # probably it should... but until it does, do it now, before copying it!
            self.assy.o.saveLastView()
        return (self.assy, self.name, self.scale, self.pov, self.zoomFactor, self.quat), {}
    
    def show_in_model_tree(self):
        #bruce 050128; nothing's wrong with showing them, except that they are unselectable
        # and useless for anything except being renamed by dblclick (which can lead to bugs
        # if the names are still used when files_mmp reads the mmp file again). For Beta we plan
        # to make them useful and safe, and then make them showable again.
        "[overrides Node method]"
        return True # changed retval to True to support Named Views.  mark 060124.

    def writemmp(self, mapping):
        v = (self.quat.w, self.quat.x, self.quat.y, self.quat.z, self.scale,
             self.pov[0], self.pov[1], self.pov[2], self.zoomFactor)
        mapping.write("csys (" + mapping.encode_name(self.name) +
                ") (%f, %f, %f, %f) (%f) (%f, %f, %f) (%f)\n" % v)
        self.writemmp_info_leaf(mapping) #bruce 050421 (only matters once these are present in main tree)

    def copy(self, dad = None): #bruce 060523 revised this (should be equivalent)
        #bruce 050420 -- revise this (it was a stub) for sake of Part view propogation upon topnode ungrouping;
        # note that various Node.copy methods are not yet consistent, and I'm not fixing this now.
        # (When I do, I think they will not accept "dad" but will accept a "mapping", and will never rename the copy.)
        # The data copied is the same as what can be passed to init and what writemmp writes.
        # Note that the copy needs to have the same exact name, not a variant (since the name
        # is meaningful for the internal uses of this object, in the present implem).
        assert dad is None
        args, kws = self._um_initargs()
            # note: we depend on our own _um_initargs returning enough info for a full copy,
            # though it doesn't have to in general.
        if 0 and platform.atom_debug:
            print "atom_debug: copying csys:", self
        return Csys( *args, **kws )

    def __str__(self):
        #bruce 050420 comment: this is inadequate, but before revising it
        # I'd have to verify it's not used internally, like Jig.__repr__ used to be!!
        return "<csys " + self.name + ">"

    def __CM_Change_View(self): #mark 060122
        self.change_view()
        
    def change_view(self): #mark 060122
        '''Change the view to self.
        '''
        self.assy.o.animateToView(self.quat, self.scale, self.pov, self.zoomFactor, animate=True)
        
        cmd = greenmsg("Change View: ")
        msg = 'View changed to "%s".' % (self.name)
        env.history.message( cmd + msg )
        
    def __CM_Set_to_Current_View(self): #mark 060122
        self.set_to_current_view()
    
    def set_to_current_view(self): #mark 060122
        '''Set self to current view.
        '''
        self.scale = self.assy.o.scale
        self.pov = V(self.assy.o.pov[0], self.assy.o.pov[1], self.assy.o.pov[2])
        self.zoomFactor = self.assy.o.zoomFactor
        self.quat = Q(self.assy.o.quat)
        self.assy.changed() ###e we should make this check whether it really changed? (or will Undo do that??)
        
        cmd = greenmsg("Set View: ")
        msg = 'View "%s" now set to the current view.' % (self.name)
        env.history.message( cmd + msg )

    def move(self, offset): # in class Csys (Named View) [bruce 070501, used when these are deposited from partlib]
        "[properly implements Node API method]"
        self.pov = self.pov - offset # minus, because what we move is the center of view, defined as -1 * self.pov
        self.changed()
        return

    pass # end of class Csys

# bruce 050417: commenting out class Datum (and ignoring its mmp record "datum"),
# since it has no useful effect.
# bruce 060523: removing the commented out code. In case it's useful for Datum Planes,
# it can be found in cvs rev 1.149 or earlier of Utility.py, and commented out
# references to it remain in other files. It referred to cad/images/datumplane.png.

# end
