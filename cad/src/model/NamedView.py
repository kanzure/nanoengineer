# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
NamedView.py -- a named view (including coordinate system for viewing)

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Mark wrote this in Utility.py.

bruce 071026 moved it from Utility into a new file.

Mark renamed Csys to NamedView, on or after 2008-02-03.

Bruce 080303 simplified NamedView.__init__ arg signature and some calling code.
"""

from utilities.constants import gensym
from geometry.VQT import V, Q, vlen
from utilities.icon_utilities import imagename_to_pixmap
from foundation.Utility import SimpleCopyMixin
from foundation.Utility import Node
from utilities import debug_flags
import foundation.env as env
from utilities.Log import greenmsg

class NamedView(SimpleCopyMixin, Node):
    """
    The NamedView is used to store all the parameters needed to save and restore a view.
    It is used in several distinct ways:
        1) as a Named View created by the user and visible as a node in the model tree
        2) internal use for storing the LastView and HomeView for every part
        3) internal use by Undo for saving the view that was current when a change was made
    """

    sym = "View"
    featurename = "Named View"

    copyable_attrs = Node.copyable_attrs + ('scale', 'pov', 'zoomFactor', 'quat')
        # (note: for copy, this is redundant with _um_initargs (that's ok),
        #  but for Undo, it's important to list these here or give them _s_attr decls.
        #  This fixes a presumed bug (perhaps unreported -- now bug 1942) in Undo of Set_to_Current_View.
        #  Bug 1369 (copy) is fixed by _um_initargs and SimpleCopyMixin, not by this.)

    scale = pov = zoomFactor = quat = None # Undo might require these to have default values (not sure) [bruce 060523]

    def __init__(self, assy, name, scale, pov, zoomFactor, wxyz):
        """
        @param pov: the inverse of the "center of view" in model coordinates
        @type pov: position vector (Numeric.array of 3 ints or floats, as made
                   by V(x,y,z))

        @param wxyz: orientation of view
        @type wxyz: a Quaternion (class VQT.Q), or a sequence of 4 floats
                    which can be passed to that class to make one, e.g.
                    Q(W, x, y, z) is the quaternion with axis vector x,y,z
                    and sin(theta/2) = W
        """
        self.const_pixmap = imagename_to_pixmap("modeltree/NamedView.png")
        if not name:
            name = gensym("%s" % self.sym, assy)
        Node.__init__(self, assy, name)
        self.scale = scale
        assert type(pov) is type(V(1, 0, 0))
        self.pov = V(pov[0], pov[1], pov[2])
        self.zoomFactor = zoomFactor
        self.quat = Q(wxyz)
            #bruce 050518/080303 comment: wxyz is passed as an array of 4 floats
            # (in same order as in mmp file's csys record), when parsing
            # csys mmp records, or with wxyz a quat in other places.
        return

    def _um_initargs(self): #bruce 060523 to help make it copyable from the UI (fixes bug 1369 along with SimpleCopyMixin)
        """
        #doc

        @warning: see comment where this is called in this class --
                  it has to do more than its general spec requires
        """
        # (split out of self.copy)
        if "a kluge is ok since I'm in a hurry":
            # the data in this NamedView might not be up-to-date, since the glpane "caches it"
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
        """
        [overrides Node method]
        """
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
        if 0 and debug_flags.atom_debug:
            print "atom_debug: copying namedView:", self
        return NamedView( *args, **kws )

    def __str__(self):
        #bruce 050420 comment: this is inadequate, but before revising it
        # I'd have to verify it's not used internally, like Jig.__repr__ used to be!!
        return "<namedView " + self.name + ">"

    def ModelTree_plain_left_click(self):
        #bruce 080213 bugfix: override this new API method, not Node.pick.
        """
        [overrides Node method]
        Change to self's view, if not animating.
        """
        # Precaution. Don't change view if we're animating.
        if self.assy.o.is_animating:
            return

        self.change_view()
        return

    def ModelTree_context_menu_section(self): #bruce 080225, for Mark to review and revise
        """
        Return a menu_spec list to be included in the Model Tree's context
        menu for this node, when this is the only selected node
        (which implies the context menu is specifically for this node).

        [extends superclass implementation]
        """
        # start with superclass version
        menu_spec = Node.ModelTree_context_menu_section(self)

        # then add more items to it, in order:

        # Change to this view

        text = "Change to '%s' (left click)" % (self.name,)
        command = self.ModelTree_plain_left_click
        disabled = self.sameAsCurrentView()
        menu_spec.append( (text, command, disabled and 'disabled' or None) )

        # Replace saved view with current view

        text = "Replace '%s' with the current view" % (self.name,)
            # (fyi, I don't know how to include bold text here, or whether it's possible)
        command = self._replace_saved_view_with_current_view
        disabled = self.sameAsCurrentView()
        menu_spec.append( (text, command, disabled and 'disabled' or None) )

        # Return to previous view (NIM) [mark 060122]

        # @note: This is very helpful when the user accidentally clicks
        # a Named View node and needs an easy way to restore the previous view.

        if 0:
            text = "Return to previous View"
            command = self.restore_previous_view
            disabled = True # should be: disabled if no previous view is available
            menu_spec.append( (text, command, disabled and 'disabled' or None) )

        # Note: we could also add other items here instead of defining them in __CM methods.
        # If they never need to be disabled, just use menu_spec.append( (text, command) ).

        return menu_spec

    def change_view(self): #mark 060122
        """
        Change the view to self.
        """
        self.assy.o.animateToView(self.quat, self.scale, self.pov, self.zoomFactor, animate=True)

        cmd = greenmsg("Change View: ")
        msg = 'Current view is "%s".' % (self.name)
        env.history.message( cmd + msg )

    def _replace_saved_view_with_current_view(self): #bruce 080225 split this out
        """
        Replace self's saved view with the current view, if they differ.
        """
        if not self.sameAsCurrentView():
            self._set_to_current_view()
        return

    def restore_previous_view(self):
        """
        Restores the previous view.

        @warning: Not implemented yet. Mark 2008-02-14
        """
        print "Not implemented yet."
        return

    def _set_to_current_view(self): #mark 060122
        """
        Set self to current view, marks self.assy as changed,
        and emits a history message. Intended for use on
        user-visible Named View objects in the model tree.
        Does not check whether self is already the current view
        (for that, see self.sameAsCurrentView()).

        @see: setToCurrentView, for use on internal view objects.
        """
        #bruce 080225 revised this to remove duplicated code,
        # made it private, revised related docstrings
        self.setToCurrentView( self.assy.glpane)
        self.assy.changed()
            # maybe: make this check whether it really changed (or will Undo do that?)

        cmd = greenmsg("Set View: ")
        msg = 'View "%s" now set to the current view.' % (self.name)
        env.history.message( cmd + msg )

    def move(self, offset): # in class NamedView [bruce 070501, used when these are deposited from partlib]
        """
        [properly implements Node API method]
        """
        self.pov = self.pov - offset # minus, because what we move is the center of view, defined as -1 * self.pov
        self.changed()
        return

    def setToCurrentView(self, glpane):
        """
        Save the current view in self, but don't mark self.assy as changed
        or emit any history messages. Can be called directly on internal
        view objects (e.g. glpane.HomeView), or as part of the implementation
        of replacing self with the current view for user-visible Named View
        objects in the model tree.

        @param glpane: the 3D graphics area.
        @type  glpane: L{GLPane)
        """
        assert glpane

        self.quat = Q(glpane.quat)
        self.scale = glpane.scale
        self.pov = V(glpane.pov[0], glpane.pov[1], glpane.pov[2])
        self.zoomFactor = glpane.zoomFactor

    def sameAsCurrentView(self, view = None):
        """
        Tests if self is the same as I{view}, or the current view if I{view}
        is None (the default).

        @param view: A named view to compare with self. If None (the default),
                     self is compared to the current view (i.e. the 3D graphics
                     area).
        @type  view: L{NamedView}

        @return: True if they are the same. Otherwise, returns False.
        @rtype:  boolean
        """
        # Note: I'm guessing this could be rewritten to be more
        # efficient/concise. For example, it seems possible to implement
        # this using a simple conditional like this:
        #
        # if self == view:
        #    return True
        # else:
        #    return False
        #
        # It occurs to me that the GPLane class should use a NamedView attr
        # along with (or in place of) quat, scale, pov and zoomFactor attrs.
        # That would make this method (and possibly other code) easier to
        # write and understand.
        #
        # Ask Bruce about all this.
        #
        # BTW, this code was originally copied/borrowed from
        # GLPane.animateToView(). Mark 2008-02-03.

        # Make copies of self parameters.
        q1 = Q(self.quat)
        s1 = self.scale
        p1 = V(self.pov[0], self.pov[1], self.pov[2])
        z1 = self.zoomFactor

        if view is None:
            # use the graphics area in which self is displayed
            # (usually the main 3D graphics area; code in this class
            #  has not been reviewed for working in other GLPane_minimal instances)
            view = self.assy.glpane

        # Copy the parameters of view for comparison
        q2 = Q(view.quat)
        s2 = view.scale
        p2 = V(view.pov[0], view.pov[1], view.pov[2])
        z2 = view.zoomFactor

        # Compute the deltas
        deltaq = q2 - q1
        deltap = vlen(p2 - p1)
        deltas = abs(s2 - s1)
        deltaz = abs(z2 - z1)

        if deltaq.angle + deltap + deltas + deltaz == 0:
            return True
        else:
            return False

    pass # end of class NamedView

# bruce 050417: commenting out class Datum (and ignoring its mmp record "datum"),
# since it has no useful effect.
# bruce 060523: removing the commented out code. In case it's useful for
# Datum Planes, it can be found in cvs rev 1.149 or earlier of Utility.py,
# and commented out
# references to it remain in other files. It referred to cad/images/datumplane.png.

# end
