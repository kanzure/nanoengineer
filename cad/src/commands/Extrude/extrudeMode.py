# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
extrudeMode.py - Extrude mode, including its internal "rod" and "ring" modes.
Unfinished [as of 050518], especially ring mode.

@author: Bruce
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

by bruce, 040924/041011/041015... 050107...

ninad 070110: retired extrude dashboard  (in Qt4 branch). It was
replaced with its 'Property Manager' (see Ui_ExtrudePropertyManager,
ExtrudePropertyManager)

ninad 20070725: code cleanup to create a propMgr object for extrude mode.
Moved many ui helper methods to class ExtrudePropertyManager .

Ninad 2008-09-22: ported ExtrudeMode class to use new command API
(developed in August - September 2008) .

TODO as of 2008-09-22:
Extrude mode is a class developed early days of NanoEngineer-1. Lots of things
have changed since then (example: Qt framework, major architectural changes etc)
In genral it needs a major cleanup. Some items are listed below:
- split it into command/GM parts
- refactor and move helper functions in this file into their own modules.
- several update methods need to be in central update methods in command
  and PM classes
"""

_EXTRUDE_LOOP_DEBUG = False # do not commit with True

import math
from utilities import debug_flags
import foundation.env as env
import foundation.changes as changes

from Numeric import dot

from OpenGL.GL import GL_CW
from OpenGL.GL import glFrontFace
from OpenGL.GL import GL_CCW
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import GL_BLEND
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_FALSE
from OpenGL.GL import glColorMask
from OpenGL.GL import glEnable
from OpenGL.GL import GL_TRUE
from OpenGL.GL import glDisable

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QCursor

from utilities.debug_prefs import debug_pref, Choice, Choice_boolean_False

from command_support.modes import basicMode
from utilities.debug import print_compact_traceback, print_compact_stack
from model.bonds import bond_at_singlets
from utilities.icon_utilities import geticon
from utilities.Log import redmsg

from geometry.VQT import check_posns_near, check_quats_near
from geometry.VQT import V, Q, norm, vlen, cross

from commands.Extrude.ExtrudePropertyManager import ExtrudePropertyManager

from graphics.drawing.CS_draw_primitives import drawline
from model.chunk import Chunk
from graphics.behaviors.shape import get_selCurve_color

from graphics.drawables.handles import repunitHandleSet
from graphics.drawables.handles import niceoffsetsHandleSet
from graphics.drawables.handles import draggableHandle_HandleSet
from utilities.constants import blue
from utilities.constants import green
from utilities.constants import common_prefix

from ne1_ui.NE1_QWidgetAction import NE1_QWidgetAction
from ne1_ui.toolbars.Ui_ExtrudeFlyout import ExtrudeFlyout

# ==

_MAX_NCOPIES = 360 # max number of extrude-unit copies.
    # Motivation is to avoid "hangs from slowness".
    # Should this be larger?

_KEEP_PICKED = False # whether to keep the repeated-unit copies all picked
    # (selected), or all unpicked, during the mode

# ==

def reinit_extrude_controls(win, glpane = None, length = None, attr_target = None):
    """
    Reinitialize the extrude controls; used whenever we enter the mode;
    win should be the main window (MWSemantics object).
    """
    self = win

    dflt_ncopies_rod = debug_pref("Extrude: initial N", Choice([2,3,4,5,6,10,20], defaultValue = 3),
                                  prefs_key = True, non_debug = True ) #bruce 070410
        # minor bug in that: it happens too early for a history message, so if it has its non-default value
        # when first used, the user doesn't get the usual orange history warning.

    #e refile these
    self.extrudeSpinBox_n_dflt_per_ptype = [dflt_ncopies_rod, 30]
        # default N depends on product type... not yet sure how to use this info
        ## in fact we can't use it while the bugs in changing N after going to a ring, remain...
    dflt_ncopies = self.extrudeSpinBox_n_dflt_per_ptype[0] #e 0 -> a named constant, it's also used far below

    self.propMgr.extrudeSpinBox_n.setValue(dflt_ncopies)

    x,y,z = 5,5,5 # default dir in modelspace, to be used as a last resort
    if glpane:
        # use it to set direction
        try:
            right = glpane.right
            x,y,z = right # use default direction fixed in eyespace
            if not length:
                length = 7.0 #k needed?
        except:
            print "fyi (bug?): in extrude: x,y,z = glpane.right failed"
            pass
    if length:
        # adjust the length to what the caller desires [Enter passes this]
        #######, based on the extrude unit (if provided); we'll want to do this more sophisticatedly (??)
        ##length = 7.0 ######
        ll = math.sqrt(x*x + y*y + z*z) # should always be positive, due to above code
        rr = float(length) / ll
        x,y,z = (x * rr, y * rr, z * rr)
    self.propMgr.set_extrude_controls_xyz((x,y,z))


    for toggle in self.propMgr.extrude_pref_toggles:
        if attr_target and toggle.attr: # do this first, so the attrs needed by the slot functions are there
            setattr(attr_target, toggle.attr, toggle.default) # this is the only place I initialize those attrs!
    ##for toggle in self.propMgr.extrude_pref_toggles:
        ##toggle.setChecked(True) ##### stub; change to use its sense & default if it has one -- via a method on it

    #e bonding-slider, and its label, showing tolerance, and # of bonds we wouldd make at current offset\
    tol = self.propMgr.extrudeBondCriterionSlider_dflt / 100.0
    self.propMgr.set_bond_tolerance_and_number_display(tol)
    self.propMgr.set_bond_tolerance_slider(tol)
    ### bug: at least after the reload menu item, reentering mode did not reinit slider to 100%. don\'t know why.\

    self.propMgr.extrude_productTypeComboBox.setCurrentIndex(0)

    self.updateMessage()

    return

# ==

_superclass = basicMode

class extrudeMode(basicMode):
    """
    Extrude mode.
    """

    # class constants

    #Property Manager
    PM_class = ExtrudePropertyManager

    #Flyout Toolbar
    FlyoutToolbar_class = ExtrudeFlyout

    commandName = 'EXTRUDE'
    featurename = "Extrude Mode"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING


    # initial values of some instance variables.
    # note: some of these might be set by external code (e.g. in self.propMgr).
    # see self.togglevalue_changed() and ExtrudePropertyManager.connect_or_disconnect_signals()
    # methods for more info.

    mergeables = {} # in case not yet initialized when we Draw (maybe not needed)

    show_bond_offsets = False
    show_entire_model = True
    whendone_make_bonds = True
    whendone_all_one_part = True
    whendone_merge_selection = True

    final_msg_accum = ""

    # no __init__ method needed

    # methods related to entering this mode

    def ptype_value_changed(self, val):
        # note: uses val, below; called from ExtrudePropertyManager.py
        if not self.isCurrentCommand():
            return
        old = self.product_type
        new = self.propMgr.extrude_productTypeComboBox_ptypes[val]

        if new != old:
            # print "product_type = %r" % (new,)
            self.product_type = new
            ## i will remove those "not neededs" as soon as this is surely past the josh demo snapshot [041017 night]
            self.needs_repaint = 1 #k not needed since update_from_controls would do this too, i hope!
            self.update_from_controls()
            ## not yet effective, even if we did it: self.recompute_bonds()
            self.repaint_if_needed() #k not needed since done at end of update_from_controls
            self.updateMessage()
        return

    bond_tolerance = -1.0 # this initial value can't agree with value computed from slider

    def slider_value_changed(self, valjunk):
        """
        Slot method: The bond tolerance slider value changed.
        """
        del valjunk
        ######k why don't we check suppress_value_changed? maybe we never set its value with that set?
        if not self.isCurrentCommand():
            return
        old = self.bond_tolerance
        new = self.propMgr.get_bond_tolerance_slider_val()
        if new != old:
            self.needs_repaint = 1 # almost certain, from bond-offset spheres and/or bondable singlet colors
            self.bond_tolerance = new
            # one of the hsets has a radius_multiplier which must be patched to self.bond_tolerance
            # (kluge? not compared to what I was doing a few minutes ago...)
            try:
                hset = self.nice_offsets_handleset
            except AttributeError:
                print "must be too early to patch self.nice_offsets_handleset -- " \
                      "could be a problem, it will miss this event" ###@@@
            else:
                hset.radius_multiplier = self.bond_tolerance

            # number of resulting bonds not yet known, will be set later
            self.propMgr.set_bond_tolerance_and_number_display(self.bond_tolerance)
            self.recompute_bonds() # re-updates set_bond_tolerance_and_number_display when done
            self.repaint_if_needed()
                ##e merge with self.update_offset_bonds_display, call that instead?? no need for now.
        return

    def toggle_value_changed(self, valjunk):
        del valjunk
        if not self.isCurrentCommand():
            return
        self.needs_repaint = 0
        for toggle in self.propMgr.extrude_pref_toggles:
            val = toggle.isChecked()
            attr = toggle.attr
            repaintQ = toggle.repaintQ
            if attr:
                old = getattr(self,attr,val)
                if old != val:
                    setattr(self, attr, val)
                    if repaintQ:
                        self.needs_repaint = 1
            else:
                # bad but tolerable: a toggle with no attr, but repaintQ,
                # forces repaint even when some *other* toggle changes!
                # (since we don't bother to figure out whether it changed)
                if repaintQ:
                    self.needs_repaint = 1
                    print "shouldn't happen in current code - needless repaint"
            pass
        self.repaint_if_needed()

    def command_ok_to_enter(self):
        #bruce 080924 de-inlined _refuseEnter (since this was its only call)
        warn = True
        ok, mol = assy_extrude_unit(self.o.assy, really_make_mol = 0)
        if not ok:
            whynot = mol
            if warn:
                from utilities.Log import redmsg
                env.history.message(redmsg("%s refused: %r" % (self.get_featurename(), whynot,)))
                    # Fixes bug 444. mark 060323
            self.w.toolsExtrudeAction.setChecked(False)
                # this needs to be refactored away, somehow,
                # but is tolerable for now [bruce 080806 comment]
            return False
        else:
            # mol is nonsense, btw
            return True
        pass


    def command_entered(self):
        """
        Extends superclass method.
        @see: basecommand.command_entered() for documentation.
        """
        #NOTE: Most of the code below is copied (with some changes) from the
        #following methods that existed in the old command API
        #on or before 2008-09-22:
        #self.init_gui(), self.Enter(), self._command_entered_effects()
        #self.clear_command_state()
        # [-- Ninad Comment]

        _superclass.command_entered(self)

        #Copying all the code originally in self.Enter() that existed
        #on or before  2008-09-19 [--Ninad comment ]
        self.status_msg("preparing to enter %s..." % self.get_featurename())
                # this msg won't last long enough to be seen, if all goes well

        #Clear command states
        self.mergeables = {}
        self.final_msg_accum = ""
        self.dragdist = 0.0
        self.have_offset_specific_data = 0 #### also clear that data itself...
        self.bonds_for_current_offset_and_tol = (17,) # impossible value -- ok??
        self.offset_for_bonds = None
        self.product_type = "straight rod" #e someday have a combobox for this
        self.circle_n = 0
        self.__old_ptype = None
        self.singlet_color = {}

        self.initial_down = self.o.down
        self.initial_out = self.o.out
        initial_length = debug_pref("Extrude: initial offset length (A)",
                                    Choice([3.0, 7.0, 15.0, 30.0],
                                           defaultValue = 7.0 ),
                                    prefs_key = True,
                                    non_debug = True ) #bruce 070410

        # Disable Undo/Redo actions, and undo checkpoints, during this mode
        # (they *must* be reenabled in command_will_exit).
        # We do this as late as possible before modifying the model [moved this code, bruce 080924],
        # so as not to do it if there are exceptions in the rest of the method,
        # since if it's done and never undone, Undo/Redo won't work for the rest of the session.
        # [bruce 060414, to mitigate bug 1625; same thing done in some other modes]
        import foundation.undo_manager as undo_manager
        undo_manager.disable_undo_checkpoints('Extrude')
        undo_manager.disable_UndoRedo('Extrude', "during Extrude")
            # this makes Undo menu commands and tooltips look like
            # "Undo (not permitted during Extrude)" (and similarly for Redo)

        self._command_entered_effects() # note: this modifies the model

        reinit_extrude_controls(self, self.o, length = initial_length, attr_target = self)

        #Bruce's old comment from before this was refactored 080922:
        # i think this [self.updateCommandToolbar and self.connect_or_disconnect_signals]
        # is safer *after* the first update_from_controls, not before it...
        # but i won't risk changing it right now (since tonight's bugfixes
        # might go into josh's demo). [041017 night]

        self.update_from_controls()
        return

    def command_will_exit(self):
        """
        Extends superclass method.
        """
        #NOTE: Most of the code below is copied (with some changes )from the
        #following methods that existed in the old command API
        #on or before 2008-09-22:
        #self.stateDone(), self.stateCancel(), self.haveNonTrivialState(),
        #self._stateDoneOrCancel(), self.restore_gui()
        # [-- Ninad Comment]

        # Reenable Undo/Redo actions, and undo checkpoints (disabled in init_gui);
        # do it first to protect it from exceptions in the rest of this method
        # (since if it never happens, Undo/Redo won't work for the rest of the session)
        # [bruce 060414; same thing done in some other modes]
        import foundation.undo_manager as undo_manager
        undo_manager.reenable_undo_checkpoints('Extrude')
        undo_manager.reenable_UndoRedo('Extrude')
        self.set_cmdname('Extrude') # this covers all changes while we were in the mode
            # (somewhat of a kluge, and whether this is the best place to do it is unknown;
            #  without this the cmdname is "Done")

        if self.commandSequencer.exit_is_forced:
            if self.ncopies != 1:
                self._warnUserAboutAbandonedChanges()
        else:
            if self.commandSequencer.exit_is_cancel:
                cancelling = True
                self.propMgr.extrudeSpinBox_n.setValue(1)
                    #e should probably do this in our subroutine instead of here
            else:
                cancelling = False

            #bugfix after changes in rev 14435. Always make sure to call
            #update from controls while exiting the command. (This should
            #be in an command_update_* method when extrude modeis refactored)
            self.update_from_controls()

            #Following code is copied from old method self._stateDoneOrCancel
            #(that method existed before 2008-09-25)
            ## self.update_from_controls() #k 041017 night - will this help or hurt?
            # since hard to know, not adding it now.
            # restore normal appearance [bruce 070407 revised this in case each mol is not a Chunk]
            for mol in self.molcopies:
                # mol might be Chunk, fake_merged_mol, or fake_copied_mol [bruce 070407]
                for chunk in true_Chunks_in(mol):
                    try:
                        del chunk._colorfunc
                            # let class attr [added 050524] be visible again; exception if it already was
                        #e also unpatch info from the atoms? not needed but might as well [nah]
                    except:
                        pass
                    else:
                        #bruce 060308 revision: do this outside the try/except,
                        # in case bugs would be hidden otherwise
                        chunk.changeapp(0)
                continue

            self.finalize_product(cancelling = cancelling)
                # this also emits status messages and does some cleanup of broken_externs...
            self.o.assy.update_parts()
                #bruce 050317: fix some of the bugs caused by user dragging some
                # repeat units into a different Part in the MT, deleting them, etc.
                # (At least this should fix bug 371 comment #3.)
                # This is redundant with the fix for that in make_inter_unit_bonds,
                # but is still the only place we catch the related bug when rebonding
                # the base unit to whatever we unbonded it from at the start (if anything).
                # (That bug is untested and this fix for it is untested.)

        _superclass.command_will_exit(self)

    def _command_entered_effects(self):
        """
        [private] common code for self.command_entered()
        """
        #Note: The old command API code was striped out on 2008-09-25. But keeping
        #this method instead of inlining it with command_entered, because
        #it makes command_entered easier to read - Ninad 2008-09-25

        ###
        # find out what's selected, which if ok will be the repeating unit we will extrude...
        # explore its atoms, bonds, externs...
        # what's selected should be its own molecule if it isn't already...
        # for now let's hope it is exactly one (was checked in command_ok_to_enter, but not anymore).

        ok, mol = assy_extrude_unit(self.o.assy)
        if not ok:
            # after 041222 this should no longer happen, since checked in command_ok_to_enter
            whynot = mol
            self.status_msg("%s refused: %r" % (self.get_featurename(), whynot,))
            return 1 # refused!
        assert isinstance(mol, fake_merged_mol) #bruce 070412
        self.basemol = mol
        #bruce 070407 set self.separate_basemols; all uses of it must be read,
        # to fully understand fake_merged_mol semantics
        self.separate_basemols = true_Chunks_in(mol) # since mol might be a Chunk or a fake_merged_mol

        #bruce 080626 new feature: figure out where we want to add whatever new
        # nodes we create
        self.add_new_nodes_here = self._compute_add_new_nodes_here( self.separate_basemols)

        ## partly done new code [bruce 041222] ###@@@
        # temporarily break bonds between our base unit (mol) and the rest
        # of the model; record the pairs of singlets thus formed,
        # both for rebonding when we're done, and to rule out unit-unit bonds
        # incompatible with that rebonding.
        self.broken_externs = [] # pairs of singlets from breaking of externs
        self.broken_extern_s2s = {}
        for bond in list(mol.externs):
            s1, s2 = bond.bust() # these will be rebonded when we're done
            assert s1.is_singlet() and s2.is_singlet()
            # order them so that s2 is in mol, s1 not in it [bruce 070514 Qt4: revised to fix bug 2311]
            if mol.contains_atom(s1):
                (s1,s2) = (s2,s1)
                assert s1 != s2 # redundant with following, but more informative
            assert mol.contains_atom(s2)
            assert not mol.contains_atom(s1)
            self.broken_externs.append((s1,s2))
            self.broken_extern_s2s[s2] = s1 # set of keys; values not used as of 041222
            # note that the atoms we unbonded (the neighbors of s1,s2)
            # might be neighbors of more than one singlet in this list.
        ####@@@ see paper notes - restore at end, also modify singlet-pairing alg

        # The following is necessary to work around a bug in this code, which is
        # its assumption (wrong, in general) that mol.copy_single_chunk().quat == mol.quat.
        # A better fix would be to stop using set_basecenter_and_quat, replacing
        # that with an equivalent use of mol.pivot and/or move and/or rot.
        self.basemol.full_inval_and_update()
        mark_singlets(self.separate_basemols, self.colorfunc) ###@@@ make this behave differently for broken_externs
        # now set up a consistent initial state, even though it will probably
        # be modified as soon as we look at the actual controls
        self.offset = V(15.0,16.0,17.0) # initial value doesn't matter
        self.ncopies = 1
        self.molcopies = [self.basemol]
            #e if we someday want to also display "potential new copies" dimly,
            # they are not in this list
            #e someday we might optimize by not creating separate molcopies,
            # only displaying the same mol in many places
            # (or, having many mols but making them share their display lists --
            #  could mol.copy do that for us??)

        try:
            self.recompute_for_new_unit() # recomputes whatever depends on self.basemol
        except:
            msg = "in Enter, exception in recompute_for_new_unit"
            print_compact_traceback(msg + ": ")
            self.status_msg("%s refused: %s" % (self.get_featurename(), msg,))
            return 1 # refused!

        self.recompute_for_new_bend() # ... and whatever depends on the bend
            # from each repunit to the next (varies only in ring mode)
            # (still nim as of 080727)

        return


    def command_enter_misc_actions(self):
        self.w.toolsExtrudeAction.setChecked(True)
        # Disable some QActions that will conflict with this mode.
        self.w.disable_QActions_for_extrudeMode(True)

    def command_exit_misc_actions(self):
        self.w.toolsExtrudeAction.setChecked(False)
        self.w.disable_QActions_for_extrudeMode(False)

    def _compute_add_new_nodes_here(self, nodes): #bruce 080626
        """
        If we are copying the given nodes, figure out where we'd like
        to add new nodes (as a group to call addchild on).
        """
        assert nodes
        def _compute_it():
            return common_prefix( *[self._ok_groups_for_copies_of_node(node)
                                    for node in nodes] )
        groups = _compute_it()
        if not groups:
            nodes[0].part.ensure_toplevel_group()
            groups = _compute_it()
            assert groups
        return groups[-1]

    def _ok_groups_for_copies_of_node(self, node): #bruce 080626
        """
        Considering node alone, which groups (outermost first)
        do we think are ok as a place to add copies of it?

        @note: return value might be empty. If this is an issue,
               caller may want to call node.part.ensure_toplevel_group(),
               but it might cause bugs to do that in this method,
               since it should have no side effects on the node tree.
        """
        res = node.containing_groups(within_same_part = True) # innermost first
        res = res[::-1] # outermost first
        while res and not res[-1].permit_addnode_inside():
            res = res[:-1]
        return res

    def updateMessage(self):
        """
        Update the message box win property manager with an informative message.
        """
        self.propMgr.updateMessage()

    singlet_color = {} # we also do this in clear_command_state()

    def colorfunc(self, atom): # uses a hack in chem.py atom.draw to use mol._colorfunc
        return self.singlet_color.get(atom.info) # ok if this is None

    def asserts(self):
        assert len(self.molcopies) == self.ncopies
        assert self.molcopies[0] == self.basemol

    circle_n = 0 # we also do this in clear_command_state()
        # note: circle_n is still used (in ring mode), even though "revolve"
        # as separate mode is nim/obs/removed [bruce 080727 comment]

    def spinbox_value_changed(self, valjunk):
        """
        Call this when any extrude spinbox value changed, except length.
        Note that this doesn't update the 3D workspace. For updating the workspace
        user needs to hit Preview or hit Enter.
        @see: self.update_from_controls()
        @see: ExtrudePropertyManager.keyPressEvent()
        @see: ExtrudePropertyManager.preview_btn_clicked()
        """
        del valjunk

        if self.propMgr.suppress_valuechanged:
            return
        if not self.isCurrentCommand():
            #e we should be even more sure to disconnect the connections causing this to be called
            ##print "fyi: not isCurrentCommand"
            ##    # this happens when you leave and reenter mode... need to break qt connections
            return
        self.propMgr.update_length_control_from_xyz()

    def length_value_changed(self, valjunk):
        """
        Call this when the length spinbox changes.
        Note that this doesn't update the 3D workspace. For updating the workspace
        user needs to hit Preview or hit Enter.
        @see: self.update_from_controls()
        @see: ExtrudePropertyManager.keyPressEvent()
        @see: ExtrudePropertyManager.preview_btn_clicked()
        """
        del valjunk
        if self.propMgr.suppress_valuechanged:
            return
        if not self.isCurrentCommand():
            ##print "fyi: not isCurrentCommand"
            return
        self.propMgr.update_xyz_controls_from_length()



    should_update_model_tree = 0 # avoid doing this when we don't need to (like during a drag)

    def want_center_and_quat(self, ii, ptype = None):
        """
        Return desired basecenter and quat of molcopies[ii], relative to
        original ones, assuming they're same as in basemol.
        """
        #  update 070407: if self.basemol is a fake_merged_mol, we use the basecenter of its first true Chunk
        # (arbitrary choice which chunk, but has to be consistent with fake_copied_mol.set_basecenter_and_quat).
        # This is then compensated for in fake_copied_mol.set_basecenter_and_quat (for center -- it assumes all quats
        # are the same, true since they are all Q(1,0,0,0) due to full_inval_and_update).
        #  At first I planned to revise this method to return info for passing to mov/rot/pivot instead -- but we'd have to do that
        # relative to initial orientation, not prior one, or risk buildup of roundoff errors, but there's no good way to think
        # of a chunk as "rotated from initial orientation" except via its basecenter & quat.
        #  An improvement would be to officially temporarily disable re-choosing basecenter & quat in all these chunks,
        # rather than on relying on it not to happen "by luck" (since it only happens when we do ops we're not doing here --
        # but note that nothing currently prevents user from doing them during this mode, unless UI tool disables do).
        # Meanwhile, the current scheme should be as correct for multiple base-chunks as it was for one.
        #  See also the comments in fake_copied_mol.set_basecenter_and_quat, especially about how this affects ring mode.
        # Update, bruce 070411, fixing this now for fake_copied_mol ring mode:
        # - why does this use .center when what we set later is basecenter? guess: only ok since full_inval_and_update
        # sets basecenter to center. So if we return a new kind of center from fake_merged_mol, we need to preserve that relation,
        # treating center as the "default basecenter" from that thing, to which requested new ones are relative.
        offset = self.offset
        cn = self.circle_n ### does far-below code have bugs when ii >= cn?? that might explain some things i saw...
        basemol = self.basemol
        if not ptype:
            ptype = self.product_type
        #e the following should become the methods of product-type classes
        if ptype == "straight rod": # default for Extrude
            centerii = basemol.center + ii * offset
            # quatii = Q(1,0,0,0)
            quatii = basemol.quat
        elif ptype == "closed ring":
            self.update_ring_geometry()
                # TODO: only call this once, for all ii in a loop of calls of this method
            # extract some of the results saved by update_ring_geometry
            c_center = self.circle_center

            # use them for spoke number ii
            quatii_rel, spoke_vec = self._spoke_quat_and_vector(ii)
            quatii = basemol.quat + quatii_rel
                # [i'm not sure what the following old comment means -- bruce 070928]
                # (i think) this doesn't depend on where we are around the circle!
            centerii = c_center + spoke_vec
        else:
            self.status_msg("bug: unimplemented product type %r" % ptype)
            return self.want_center_and_quat(ii, "straight rod")
        if ii == 0:
            ###e we should warn if retvals are not same as basemol values;
            # need a routine to "compare center and quat",
            # like our near test for floats;
            # Numeric can help for center, but we need it for quat too
            if debug_flags.atom_debug:
                #bruce 050518 added this condition, at same time as bugfixing the checkers to not be noops
                check_posns_near( centerii, basemol.center )
                check_quats_near( quatii, basemol.quat )
            pass
        return centerii, quatii

    def update_ring_geometry(self, emit_messages = True): #bruce 070928 split this out of want_center_and_quat
        """
        Recompute and set ring geometry attributes of self,
        namely self.circle_center, self.axis_dir, self.radius_vec,
        which depend on self.basemol, self.circle_n, and self.offset,
        and are used by self.want_center_and_quat(...)
        and by some debug drawing code.
        """
        #e We store self.o.down (etc) when we enter the mode...
        # now we pick a circle in plane of that and current offset.
        # If this is ambiguous, we favor a circle in plane of initial down and out.

        # these are constants throughout the mode:
        down = self.initial_down
        out = self.initial_out
        basemol = self.basemol

        # these vary:
        offset = self.offset
        cn = self.circle_n

        tangent = norm(offset)
        axis = cross(down,tangent) # example, I think: left = cross(down,out)  ##k
        if vlen(axis) < 0.001: #k guess
            axis = cross(down,out)
            if emit_messages:
                self.status_msg("error: offset too close to straight down, picking down/out circle")
            # worry: offset in this case won't quite be tangent to that circle. We'll have to make it so. ###NIM
        axis = norm(axis) # direction only
        # note: negating this direction makes the circle head up rather than down,
        # but doesn't change whether bonds are correct.
        towards_center = cross(offset,axis)
            # these are perp, axis is unit, so only cn is needed to make this correct length
        neg_radius_vec = towards_center * cn / (2 * math.pi)
        c_center = basemol.center + neg_radius_vec # circle center
        self.circle_center = c_center # be able to draw the axis
        self.axis_dir = axis
        radius_vec = - neg_radius_vec
        self.radius_vec = radius_vec # be able to draw "spokes", useful in case the axis is off-screen
        return

    def _spoke_quat_and_vector(self, ii): #bruce 070928 split this out of want_center_and_quat
        """
        Assuming self.product_type == 'closed ring',
        and assuming self.update_ring_geometry() has just been called
        (unverifiable, but bugs if this is not true!),
        return a tuple (quatii_rel, spoke_vec)
        containing a quat which rotates self.radius_vec into spoke_vec,
        and spoke_vec itself, a "spoke vector" which should translate self.circle_center
        to the desired center of repeat unit ii
        (where unit 0 is self.basemol).
        """
        cn = self.circle_n
        # extract results saved by assumed call of update_ring_geometry
        axis = self.axis_dir
        radius_vec = self.radius_vec
        c_center = self.circle_center

        quatii_rel = Q(axis, 2 * math.pi * ii / cn) * -1.0
        spoke_vec = quatii_rel.rot( radius_vec )
        return (quatii_rel, spoke_vec)

    __old_ptype = None # hopefully not needed in clear_command_state(), but i'm not sure, so i added it

    def update_from_controls(self):
        """
        Make the number and position of the copies of basemol what they should be, based on current control values.
        Never modify the control values! (That would infloop.)
        This should be called in Enter and whenever relevant controls might change.
        It's also called during a mousedrag event if the user is dragging one of the repeated units.

        We optimize by checking which controls changed and only recomputing what might depend on those.
        When that's not possible (e.g. when no record of prior value to compare to current value),
        we'd better check an invalid flag for some of what we compute,
        and/or a changed flag for some of the inputs we use.
        @see: ExtrudePropertyManager.keyPressEvent() (the caller)
        @see: ExtrudePropertyManager.preview_btn_clicked() (the caller)
        """
        self.asserts()

        # get control values
        want_n = self.propMgr.extrudeSpinBox_n.value()

        want_cn = 0 # sometimes changed below

        # limit N for safety
        ncopies_wanted = want_n
        ncopies_wanted = min(_MAX_NCOPIES, ncopies_wanted) # upper limit (in theory, also enforced by the spinbox)
        ncopies_wanted = max(1, ncopies_wanted) # always at least one copy ###e fix spinbox's value too?? also think about it on exit...
        if ncopies_wanted != want_n:
            msg = "ncopies_wanted is limited to safer value %r, not your requested value %r" % (ncopies_wanted, want_n)
            self.status_msg(msg)

        want_n = ncopies_wanted # redundant -- sorry for this unclear code

        # figure out, and store, effective circle_n now (only matters in ring mode, but always done)
        if not want_cn:
            want_cn = want_n
            # otherwise the cn control overrides the "use N" behavior
        cn_changed = (self.circle_n != want_cn) #### if we again used the sep slot method for that spinbox, this might be wrong
        self.circle_n = want_cn

        # note that self.ncopies is not yet adjusted to the want_n value,
        # and (if want_n > self.ncopies) self.ncopies will only be adjusted gradually
        # as we create new copies! So it should not be relied on as giving the final number of copies.
        # But it's ok for that to be private to this code, since what other code needs to know is the
        # number of so-far-made copies (always equals self.ncopies) and the params that affect their
        # location (which never includes self.ncopies, only ptype, self.offset, self.circle_n and someday some more). [041017 night]

            ######@@@ to complete the bugfix:
        # + don't now have someone else store circle_n,
        # + or fail to use it!
        # + [mostly] check all uses of ncopies for not affecting unit pos/rot.
        # and later, rewrite code to keep that stuff in self.want.x and self.have.x,
        # and do all update from this routine (maybe even do that part now).
        # + check product_type or ptype compares.

        (want_x, want_y, want_z) = self.propMgr.get_extrude_controls_xyz()

        offset_wanted = V(want_x, want_y, want_z) # (what are the offset units btw? i guess angstroms, but verify #k)

        # figure out whether product type might have changed -- affects pos/rot of molcopies
        ptype_changed = 0
        if self.__old_ptype != self.product_type:
            ptype_changed = 1
            self.__old_ptype = self.product_type

        # update the state:
        # first move the copies in common (between old and new states),
        # if anything changed which their location (pos/rot) might depend on.

        ncopies_common = min( ncopies_wanted, self.ncopies) # this many units already exist and will still exist
        #e rename to self.ncopies_have? no, just rename both of these to self.want.ncopies and self.have.ncopies.

        if offset_wanted != self.offset or cn_changed or ptype_changed: #e add more params if new ptypes use new params
            # invalidate all memoized data which is specific to these params
            self.have_offset_specific_data = 0 #misnamed
            self.offset = offset_wanted
            junk = self.want_center_and_quat(0) # this just asserts (inside the function) that the formulas don't want to move basemol
            for ii in range(1, ncopies_common):
                if 0: # this might accumulate position errors - don't do it:
                    motion = (offset_wanted - self.offset)*ii
                    self.molcopies[ii].move(motion) #k does this change picked state????
                else:
                    c, q = self.want_center_and_quat(ii)
                    self.molcopies[ii].set_basecenter_and_quat( c, q)
        # now delete or make copies as needed (but don't adjust view until the end)
        while self.ncopies > ncopies_wanted:
            # delete a copy we no longer want
            self.should_update_model_tree = 1
            ii = self.ncopies - 1
            self.ncopies = ii
            old = self.molcopies.pop(ii)
            old.unpick() # work around a bug in assy.killmol [041009] ##### that's fixed now -- verify, and remove this
            old.kill() # might be faster than self.o.assy.killmol(old)
            self.asserts()
        while self.ncopies < ncopies_wanted:
            # make a new copy we now want
            self.should_update_model_tree = 1
            #e the fact that it shows up immediately in model tree would permit user to change its color, etc;
            #e but we'll probably want to figure out a decent name for it, make a special group to put these in, etc
            ii = self.ncopies
            self.ncopies = ii + 1
            # pre-050216 code:
            ## newmols = assy_copy(self.o.assy, [self.basemol]) # fyi: offset is redundant with mol.set_basecenter_and_quat (below)
            ## new = newmols[0]
            # new code 050216:
            new = self.basemol.copy_single_chunk(None)
                # None is the dad, and as of 050214 or so, passing any other dad is deprecated for now.
                #bruce 080314 using copy_single_chunk in place of copy.
                # This is a bug if self.basemol can be anything other than a Chunk or a
                # fake_merged_mol. I'm sure it can't be. In fact, it is almost certain that
                # self.basemol is always a fake_merged_mol, not a Chunk;
                # if true, this method could be renamed to copy_single_fake_merged_mol.
                # The point is to make it easy to find all uses and implems of copy methods
                # that need revision. The need for revision in this case is to generalize
                # what the extrude unit can be.
            if isinstance(new, fake_copied_mol):#bruce 070407 kluge
                ## new_nodes = [new._group]
                new_nodes = new._mols
            else:
                new_nodes = [new]
            for node in new_nodes:
                self.addnode(node)
                    #e this is inefficient when adding many mols at once, needs change to inval system
                    #e this is probably not the best place in the MT to add it
                    #
                    # Note: by test, in current code (using fake_copied_mol)
                    # this is redundant, since the nodes have already been added
                    # when the copy was made. But it's harmless so I'll leave it
                    # in, in case there are some conditions in which that hasn't
                    # happened. Also, soon I'll revise this to add it in a
                    # better place, so it will no longer be redundant
                    # (unless the addmol in copy_single_chunk is also fixed).
                    # [bruce 080626 comment]
                # end 050216 changes
                if _KEEP_PICKED:
                    pass ## done later: self.basemol.pick()
                else:
                    ## self.basemol.unpick()
                    node.unpick() # undo side effect of assy_copy #k maybe no longer needed [long before 050216]
            self.molcopies.append(new)
            c, q = self.want_center_and_quat(ii)
            self.molcopies[ii].set_basecenter_and_quat( c, q)
            self.asserts()
        if _KEEP_PICKED:
            self.basemol.pick() #041009 undo an unwanted side effect of assy_copy (probably won't matter, eventually)
                    #k maybe no longer needed [long before 050216]
        else:
            self.basemol.unpick() # do this even if no copies made (matters e.g. when entering the mode)
                    #k maybe no longer needed [long before 050216]

        ###@@@ now this looks like a general update function... hmm

        self.needs_repaint = 1 # assume this is always true, due to what calls us
        self.update_offset_bonds_display()

    def addnode(self, node): #bruce 080626 split this out
        """
        Add node to the current part, in the best place
        for the purposes of this command. It's ok if this
        is called more than once on the same node.
        """
        group = self.add_new_nodes_here #bruce 080626 new feature
        if group:
            group.addchild(node)
        else:
            self.o.assy.addnode(node)
                # note: addnode used to be called addmol
        return

    def update_offset_bonds_display(self):
        # should be the last function called by some user event method (??)... not sure if it always is! some weird uses of it...
        """
        Update whatever is needed of the offset_specific_data, the bonds,
        and the display itself.
        """
        ###### now, if needed, recompute (or start recomputing) the offset-specific data
        #####e worry about whether to do this with every mousedrag event... or less often if it takes too long
        ##### but ideally we do it, so as to show bonding that would happen at current offset
        if not self.have_offset_specific_data:
            self.have_offset_specific_data = 1 # even if the following has an exception
            try:
                self.recompute_offset_specific_data()
            except:
                print_compact_traceback("error in recompute_offset_specific_data: ")
                return # no more updates #### should just raise, once callers cleaner
            pass
        #obs comment in this loc?
        #e now we'd adjust view, or make drawing show if stuff is out of view;
        # make atom overlaps transparent or red; etc...

        # now update bonds (needed by most callers (not ncopies change!), so don't bother to have an invalid flag, for now...)
        if 1:
            self.recompute_bonds() # sets self.needs_repaint if bonds change; actually updates bond-specific ui displays

        # update model tree and/or glpane, as needed
        if self.should_update_model_tree:
            self.should_update_model_tree = 0 # reset first, so crashing calls are not redone
            self.needs_repaint = 0
            self.w.win_update() # update glpane and model tree
        elif self.needs_repaint: # merge with self.repaint_if_needed() ###@@@
            self.needs_repaint = 0
            self.o.gl_update() # just update glpane
        return

    # ==

    # These methods recompute things that depend on other things named in the methodname.
    # call them in the right order (this order) and at the right time.
    # If for some of them, we should only invalidate and not recompute until later (eg on buttonpress),
    # I did not yet decide how that will work.

    def recompute_for_new_unit(self):
        """
        Recompute things which depend on the choice of rep unit (for now we use
        self.basemol to hold that).
        """
        # for now we use self.basemol,
        #e but later we might not split it from a larger mol, but have a separate mol for it

        # these are redundant, do we need them?
        self.have_offset_specific_data = 0
        self.bonds_for_current_offset_and_tol = (17,)

        self.show_bond_offsets_handlesets = [] # for now, assume no other function wants to keep things in this list
        hset = self.basemol_atoms_handleset = repunitHandleSet(target = self)
        for mol in self.separate_basemols:#bruce 070407
            for atom in mol.atoms.values():
                # make a handle for it... to use in every copy we show
                pos = atom.posn() ###e make this relative?
                dispdef = mol.get_dispdef(self.o)
                disp, radius = atom.howdraw(dispdef)
                info = None #####
                hset.addHandle(pos, radius, info)
        self.basemol_singlets = list(self.basemol.singlets) #bruce 041222 precaution: copy list
        hset = self.nice_offsets_handleset = niceoffsetsHandleSet(target = self)
        hset.radius_multiplier = abs(self.bond_tolerance) # kluge -- might be -1 or 1 initially! (sorry, i'm in a hurry)
            # note: hset is used to test offsets via self.nice_offsets_handleset,
            # but is drawn and click-tested due to being in self.show_bond_offsets_handlesets
        # make a handle just for dragging self.nice_offsets_handleset
        hset2 = self.nice_offsets_handle = draggableHandle_HandleSet( \
            motion_callback = self.nice_offsets_handleset.move ,
            statusmsg = "use magenta center to drag the clickable suggested-offset display"
        )
        hset2.addHandle( V(0,0,0), 0.66, None)
        hset2.addHandle( self.offset, 0.17, None) # kluge: will be kept patched with current offset
        hset.special_pos = self.offset # ditto
        self.show_bond_offsets_handlesets.extend([hset,hset2])
            # (use of this list is conditioned on self.show_bond_offsets)
        ##e quadratic, slow alg; should worry about too many singlets
        # (rewritten from the obs functions explore, bondable_singlet_pairs_proto1)
        # note: this code will later be split out, and should not assume mol1 == mol2.
        # (but it does, see comments)
        mergeables = self.mergeables = {}
        sings1 = sings2 = self.basemol_singlets
        transient_id = (self, self.__class__.recompute_for_new_unit, "scanning all pairs")
        for i1 in range(len(sings1)):
            env.call_qApp_processEvents() #bruce 050908 replaced qApp.processEvents()
                # [bruce 050114, copied from movie.py]
                # Process queued events [enough to get statusbar msgs to show up]
                ###@@@ #e for safety we might want to pass the argument: QEventLoop::ExcludeUserInput;
                #e OTOH we'd rather have some way to let the user abort this if it takes too long!
                # (we don't yet have any known or safe way to abort it...)
            if i1 % 10 == 0 or i1 < 10:
                #bruce 050118 try only every 10th one, is it faster?
                #e should processEvents be in here too??
                ###e would be more sensible: compare real time passed...
                env.history.message("scanning open bond pairs... %d/%d done" % (i1, len(sings1)) ,
                                    transient_id = transient_id
                                    ) # this is our slowness warning
            ##e should correct that message for effect of i2 < i1 optim, by reporting better numbers...
            for i2 in range(len(sings2)):
                if i2 < i1:
                    continue # results are negative of swapped i1,i2, SINCE MOLS ARE THE SAME
                    # this order makes the slowness warning conservative... ie progress seems to speed up at the end
                    ### warning: this optim is only correct when mol1 == mol2
                    # and (i think) when there is no "bend" relating them.
                # (but for i1 == i2 we do the calc -- no guarantee mol1 is identical to mol2.)
                s1 = sings1[i1]
                s2 = sings2[i2]
                (ok, ideal, err) = mergeable_singlets_Q_and_offset(s1, s2)
                if _EXTRUDE_LOOP_DEBUG:
                    print "extrude loop %d, %d got %r" % (i1, i2, (ok, ideal, err))
                if ok:
                    mergeables[(i1,i2)] = (ideal, err)
        #e self.mergeables is in an obs format... but we still use it to look up (i1,i2) or their swapped form

        # final msg with same transient_id
        msg = "scanned %d open-bond pairs..." % ( len(sings1) * len(sings2) ,) # longer msg below
        env.history.message( msg, transient_id = transient_id, repaint = 1 )
        env.history.message("") # make it get into history right away
        del transient_id

        # make handles from mergeables.
        # Note added 041222: the handle (i1,i2) corresponds to the possibility
        # of bonding singlet number i1 in unit[k] to singlet number i2 in unit[k+1].
        # As of 041222 we have self.broken_externs, list of (s1,s2) where s1 is
        # something outside, and s2 is in the baseunit. We assume (without real
        # justification) that all this outside stuff should remain fixed and bound
        # to the baseunit; to avoid choosing unit-unit bonds which would prevent
        # that, we exclude (i1,i2) when singlet[i1] = s2 for some s2 in
        # self.broken_externs -- if we didn't, singlet[i1] in base unit would
        # need to bond to unit2 *and* to the outside stuff.
        excluded = 0
        for (i1,i2),(ideal,err) in mergeables.items():
            pos = ideal
            radius = err
            radius *= (1.1/0.77) * 1.0 # see a removed "bruce 041101" comment for why
            info = (i1,i2)
            if self.basemol_singlets[i1] not in self.broken_extern_s2s:
                hset.addHandle(pos, radius, info)
            else:
                excluded += 1
            if i2 != i1:
                # correct for optimization above
                pos = -pos
                info = (i2,i1)
                if self.basemol_singlets[i2] not in self.broken_extern_s2s:
                    hset.addHandle(pos, radius, info)
                else:
                    excluded += 1
            else:
                print "fyi: singlet %d is mergeable with itself (should never happen, except maybe in ring mode)" % i1
            # handle has dual purposes: click to change the offset to the ideal,
            # or find (i1,i2) from an offset inside the (pos, radius) ball.
        msg = "scanned %d open-bond pairs; %d pairs could bond at some offset (as shown by bond-offset spheres)" % \
            ( len(sings1) * len(sings2) , len(hset.handles) )
        self.status_msg(msg)
        if excluded:
            print "fyi: %d pairs excluded due to external bonds to extruded unit" % excluded ###@@@
        return

    def recompute_for_new_bend(self):
        """
        Recompute things which depend on the choice of bend between units
        (for ring mode).
        """
        pass

    have_offset_specific_data = 0 # we do this in clear_command_state() too

    def recompute_offset_specific_data(self):
        """
        Recompute whatever depends on offset but not on tol or bonds --
        nothing at the moment.
        """
        pass

    def redo_look_of_bond_offset_spheres(self):
        # call to us moved from recompute_offset_specific_data to recompute_bonds
        """
        #doc;
        depends on offset and tol and len(bonds)
        """
        # kluge:
        try:
            # teensy magenta ball usually shows position of offset rel to the white balls (it's also draggable btw)
            if len( self.bonds_for_current_offset_and_tol ) >= 1: ### worked with > 1, will it work with >= 1? ######@@@
                teensy_ball_pos = V(0,0,0) # ... but make it not visible if there are any bonds [#e or change color??]
                #e minor bug: it sometimes stays invisible even when there is only one bond again...
                # because we are not rerunning this when tol changes, but it depends on tol. Fix later. #######
            else:
                teensy_ball_pos = self.offset #k i think this is better than using self.offset_for_bonds
            hset2 = self.nice_offsets_handle
            hset2.handle_setpos( 1, teensy_ball_pos ) # positions the teensy magenta ball
            hset = self.nice_offsets_handleset
            hset.special_pos = self.offset_for_bonds # tells the white balls who contain this offset to be slightly blue
        except:
            print "fyi: hset2/hset kluge failed"
        # don't call recompute_bonds, our callers do that if nec.
        return

    bonds_for_current_offset_and_tol = (17,) # we do this in clear_command_state() too
    offset_for_bonds = None

    def recompute_bonds(self):
        """
        Call this whenever offset or tol changes.
        """

        ##k 041017 night: temporary workaround for the bonds being wrong for anything but a straight rod:
        # in other products, use the last offset we used to compute them for a rod, not the current offset.
        # even better might be to "or" the sets of bonds created for each offset tried... but we won't get
        # that fancy for now.
        if self.product_type == "straight rod":
            self.offset_for_bonds = self.offset
        else:
            if not self.offset_for_bonds:
                msg = "error: bond-offsets not yet computed, but computing them for %r is not yet implemented" % self.product_type
                env.history.message(msg, norepeat_id = msg)
                return
            else:
                msg = "warning: for %r, correct bond-offset computation is not yet implemented;\n" \
                    "using bond-offsets computed for \"rod\", at last offset of the rod, not current offset" % \
                    self.product_type
                env.history.message(msg, norepeat_id = msg)
            #e we could optim by returning if only offset but not tol changed, but we don't bother yet

        self.redo_look_of_bond_offset_spheres() # uses both self.offset and self.offset_for_bonds

        # recompute what singlets to show in diff color, what bonds to make...

        # basic idea: see which nice-offset-handles contain the offset, count them, and recolor singlets they come from.
        hset = self.nice_offsets_handleset #e revise this code if we cluster these, esp. if we change their radius
        hh = hset.findHandles_containing(self.offset_for_bonds)
            # semi-kluge: this takes into account self.bond_tolerance, since it was patched into hset.radius_multiplier
        # kluge for comparing it with prior value; depends on order stability of handleset, etc
        hh = tuple(hh)
        if hh != self.bonds_for_current_offset_and_tol:
            self.needs_repaint = 1 # usually true at this point
            ##msg = "new set of %d nice bonds: %r" % (len(hh), hh)
            ##print msg ## self.status_msg(msg) -- don't obscure the scan msg yet #######
            self.bonds_for_current_offset_and_tol = hh
            # change singlet color dict(??) for i1,i2 in ..., proc(i1, col1), proc(i2,col2)...
            self.singlet_color = {}
            for mol in self.molcopies:
                mol.changeapp(0)
                ##e if color should vary with bond closeness, we'd need changeapp for every offset change;
                # then for speed, we'd want to repeatedly draw one mol, not copies like now
                # (maybe we'd like to do that anyway).
            for (pos,radius,info) in hh:
                i1,i2 = info
                ####stub; we need to worry about repeated instances of the same one (as same of i1,i2 or not)
                def doit(ii, color):
                    basemol_singlet = self.basemol_singlets[ii]
                    mark = basemol_singlet.info
                    self.singlet_color[mark] = color # when we draw atoms, somehow they find self.singlet_color and use it...
                doit(i1, blue)
                doit(i2, green)
                ###e now how do we make that effect the look of the base and rep units? patch atom.draw?
                # but as we draw the atom, do we look up its key? is that the same in the mol.copy??
        nbonds = len(hh)
        self.propMgr.set_bond_tolerance_and_number_display(
            self.bond_tolerance, nbonds)

        ###e ideally we'd color the word "bonds" funny, or so, to indicate that offset_for_bonds != offset or that ptype isn't rod...
        #e repaint, or let caller do that (perhaps aftermore changes)? latter - only repaint at end of highest event funcs.
        return

    def draw_bond_lines(self, unit1, unit2): #bruce 050203 experiment ####@@@@ PROBABLY NEEDS OPTIMIZATION
        """
        draw white lines showing the bonds we presently propose to make
        between the given adjacent units
        """
        # works now, but probably needs optim or memo of find_singlets before commit --
        # just store a mark->singlet table in the molcopies -- once when each one is made should be enough i think.
        hh = self.bonds_for_current_offset_and_tol
        self.prep_to_make_inter_unit_bonds() # needed for find_singlet; could be done just once each time bonds change, i think
        bondline_color = get_selCurve_color(0,self.o.backgroundColor) # Color of bond lines. mark 060305.
        for (pos,radius,info) in hh:
            i1,i2 = info
            ## not so simple as this: p1 = unit1.singlets[i1].posn()
            s1 = self.find_singlet(unit1,i1) # this is slow! need to optimize this (or make it optional)
            s2 = self.find_singlet(unit2,i2)
            p1 = s1.posn()
            p2 = s2.posn()
            drawline(bondline_color, p1, p2)
            ## #bruce 050324 experiment, worked:
            ## s1.overdraw_with_special_color(magenta)
            ## s2.overdraw_with_special_color(yellow)
        return

    # methods related to exiting this mode

    def finalize_product(self, cancelling = False): #bruce 050228 adding cancelling=0 to help fix bug 314 and unreported bugs
        """
        if requested, make bonds and/or join units into one part;
        cancelling = True means just do cleanup, use diff msgs
        """
        if not cancelling:
            desc = " (N = %d)" % self.ncopies  #e later, also include circle_n if different and matters; and more for other product_types
            ##self.final_msg_accum = "extrude done: "
            self.final_msg_accum = "%s making %s%s: " % (self.get_featurename().split()[0], self.product_type, desc) # first word of commandName
            msg0 = "leaving mode, finalizing product..." # if this lasts long enough to read, something went wrong
            self.status_msg(self.final_msg_accum + msg0)
            # bruce 070407 not printing this anymore:
            ## print "fyi: extrude params not mentioned in statusbar: offset = %r, tol = %r" % (self.offset, self.bond_tolerance)
        else:
            msg = "%s cancelled (warning: might not fully restore initial state)" % (self.get_featurename().split()[0],)
            self.status_msg( msg)

        if self.whendone_make_bonds and not cancelling:
            # NIM - rebond base unit with its home molecule, if any [###@@@ see below]
            #  (but not if product is a closed ring, right? not sure, actually, deps on which singlets are involved)
            #e even the nim-warning msg is nim...
            #e (once we do this, maybe do it even when not self.whendone_make_bonds??)

            # unit-unit bonds:
            bonds = self.bonds_for_current_offset_and_tol
            if not bonds:
                bonds_msg = "no bonds to make"
            else:
                bonds_msg = "making %d bonds per unit..." % len(bonds)
            self.status_msg(self.final_msg_accum + bonds_msg)
            if bonds:
                self.prep_to_make_inter_unit_bonds()
                for ii in range(1, self.ncopies): # 1 thru n-1 (might be empty range, that's ok)
                    # bond unit ii with unit ii-1
                    self.make_inter_unit_bonds( self.molcopies[ii-1], self.molcopies[ii], bonds ) # uses self.basemol_singlets, etc
                if self.product_type == "closed ring" and not cancelling:
                    # close the ring ###@@@ what about broken_externs? Need to modify bonding for ring, for this reason... ###@@@
                    self.make_inter_unit_bonds( self.molcopies[self.ncopies-1], self.molcopies[0], bonds )
                bonds_msg = "made %d bonds per unit" % len(bonds)
                self.status_msg(self.final_msg_accum + bonds_msg)
            self.final_msg_accum += bonds_msg

        #bruce 050228 fix an unreported(?) bug -- do the following even when not whendone_make_bonds:
        # merge base back into its fragmented ancestral molecule...
        # but not until the end, for fear of messing up unit-unit bonding
        # (could be dealt with, but easier to skirt the issue).
        if not self.product_type == "closed ring":
            # 041222 finally implementing this...
            ###@@@ closed ring case has to be handled differently earlier... [but isn't yet, which is a probably-unreported bug]
            for s1,s2 in self.broken_externs:
                try:
                    bond_at_singlets(s1, s2, move = False)
                except:#050228
                    print_compact_traceback("error fixing some broken bond, ignored: ") # can happen in ring mode, at least

        # 070410: if not cancelling, here is where we merge original selection (and each copy)
        # into a single chunk (or turn it into a group), if desired by a new debug_pref
        # (or dashboard checkbox (nim)).
        self.whendone_merge_each_unit = self.get_whendone_merge_each_unit()

        if self.whendone_merge_each_unit and not cancelling:
            for unit in self.molcopies:
                assert not isinstance(unit, Chunk) #bruce 070412
                try:
                    unit.internal_merge()
                except AttributeError:
                    print "following exception in unit.internal_merge() concerns unit = %r" % (unit,)
                    raise
            self.basemol = self.molcopies[0]
            self.separate_basemols = [self.basemol] # needed only if still used (unlikely); but harmless, so do it to be safe
            ###e other internal updates needed??

        if self.whendone_all_one_part and not cancelling:
            # update, bruce 070410: "whendone_all_one_part" is now misnamed, since it's independent with "merge selection",
            # so it's now called Merge Copies in the UI (Qt3, desired for Qt4) rather than Merge Chunks.

            # rejoin base unit with its home molecule, if any -- NIM [even after 041222]
            #e even the nim-warning msg is nim...
            #e (once we do this, maybe do it even when not self.whendone_all_one_part??)

            # join all units into basemol
            self.final_msg_accum += "; "
            join_msg = "joining..." # this won't be shown for long, if no error
            self.status_msg(self.final_msg_accum + join_msg)
            product = self.basemol #e should use home mol, but that's nim
            for unit in self.molcopies[1:]: # all except basemol
                product.merge(unit) # also does unit.kill()
            self.product = product #e needed?
            if self.ncopies > 1:
                join_msg = "joined into one part"
            else:
                join_msg = "(one unit, nothing to join)"
            #e should we change ncopies and molcopies before another redraw could occur?
            self.final_msg_accum += join_msg
            self.status_msg(self.final_msg_accum)
        else:
            if self.ncopies > 1:
                self.final_msg_accum += " (left units as separate parts)"
            else:
                pass # what is there to say?
            if not cancelling:
                self.status_msg(self.final_msg_accum)
        return

    def get_whendone_merge_each_unit(self): #bruce 070410
        # split this out so it can be exercised in Enter to make sure the pref appears in the menu,
        # and so there's one method to change if we make this a checkbox.
        #
        # update, bruce 070411, Qt4 only: I'm hooking this up to a checkbox, Qt4 branch only.
        # (The attr this accesses is created by reinit_extrude_controls.) (I also removed the
        #  early call in self.Enter, since it's not needed after this change.)
##        return debug_pref("Extrude: merge selection?", Choice_boolean_False,
##                          non_debug = True, prefs_key = True)
        return self.whendone_merge_selection # this is set/reset automatically when a PM checkbox is changed

    def prep_to_make_inter_unit_bonds(self):
        self.i1_to_mark = {}
        #e keys are a range of ints, could have used an array -- but entire alg needs revision anyway
        for i1, s1 in zip(range(len(self.basemol_singlets)), self.basemol_singlets):
            self.i1_to_mark[i1] = s1.info # used by self.find_singlet
            #e find_singlet could just look directly in self.basemol_singlets *right now*,
            # but not after we start removing the singlets from basemol!
        return

    def make_inter_unit_bonds(self, unit1, unit2, bonds = ()):
        # you must first call prep_to_make_inter_unit_bonds, once
        #e this is quadratic in number of singlets, sorry; not hard to fix
        ##print "bonds are %r",bonds
        if isinstance(unit1, Chunk):
            #bruce 070407 kluge: don't bother supporting this uncommon error message yet for fake_copied_mols etc.
            # To support it we'd have to scan & compare every true chunk.
            # Sometime it'd be good to do this... #e
            from utilities.Log import redmsg
            if (not unit1.assy) or (not unit2.assy): ###@@@ better test for mol.killed?
                #bruce 050317: don't bond to deleted units (though I doubt this
                # is sufficient to avoid bugs from user deleting them in the MT during this mode)
                ###@@@ this 'then clause', and the condition being inclusive enough, is untested as of 050317
                msg = "warning: can't bond deleted repeat-units"
                    #e should collapse several warnings into one
                env.history.message( redmsg( msg))
                return
            if unit1.part != unit2.part:
                #bruce 050317: avoid making inter-part bonds (even if merging units could fix that)
                msg = "warning: can't bond repeat-units in different Parts"
                    ###e could improve, name the parts, collapse several to 1 or name the units
                    # (but not high priority, since we haven't documented this as a feature)
                env.history.message( redmsg( msg))
                return
        for (offset,permitted_error,(i1,i2)) in bonds:
            # ignore offset,permitted_error; i1,i2 are singlet indices
            # assume no singlet appears twice in this list!
            # [not yet justified, 041015 1207p]
            s1 = self.find_singlet(unit1,i1)
            s2 = self.find_singlet(unit2,i2)
            if s1 and s2:
                # replace two singlets (perhaps in different mols) by a bond between their atoms
                bond_at_singlets(s1, s2, move = False)
            else:
                #e will be printed lots of times, oh well
                print "extrude warning: one or both of singlets %d,%d slated to bond in more than one way, not all bonds made" % (i1,i2)
        return

    def find_singlet(self, unit, i1):
        """
        Find the singlet #i1 in unit, and return it,
        or None if it's not there anymore
        (should someday never happen, but can for now)
        (arg called i1 could actually be i1 or i2 in bonds list)
        (all this singlet-numbering is specific to our current basemol)
        (only works if you first once called prep_to_make_inter_unit_bonds)
        """
        mark = self.i1_to_mark[i1]
            # note: mark is basemol key [i guess that means: singlet's Atom.key in basemol],
            # but unrelated to other mols' keys
        for unitmol in true_Chunks_in(unit):
            for atm in unitmol.atoms.itervalues(): #e optimize this someday -- its speed can probably matter
                if atm.info == mark:
                    return atm
        print "extrude bug (trying to ignore it): singlet not found",unit,i1
        # can happen until we remove dup i1,i2 from bonds
        return None


    # mouse events

    def leftDown(self, event):
        """
        Move the touched repunit object, or handle (if any), in the plane of
        the screen following the mouse, or in some other way appropriate to
        the object.
        """
        ####e Also highlight the object? (maybe even do that on mouseover ####) use bareMotion
        self.o.SaveMouse(event) # saves in self.o.MousePos, used in leftDrag
        thing = self.dragging_this = self.touchedThing(event)
        if thing:
            self.dragged_offset = self.offset
            # fyi: leftDrag directly changes only self.dragged_offset;
            # then recompute from controls (sp?) compares that to self.offset, changes that
            msg = thing.leftDown_status_msg()
            if not msg:
                msg = "touched %s" % (thing,)
            self.status_msg(msg)
            self.needs_repaint = 1 # for now, guess that this is always true (tho it's only usually true)
            thing.click() # click handle in appropriate way for its type (#e in future do only on some mouseups)
            self.repaint_if_needed() # (sometimes the click method already did the repaint, so this doesn't)
        return

    def status_msg(self, text): # bruce 050106 simplified this
        env.history.message(text)

    show_bond_offsets_handlesets = [] # (default value) the handlesets to be visible iff self.show_bond_offsets

    def touchedThing(self, event):
        """
        Return None or the thing touched by this event.
        """
        touchable_molecules = True
        if self.product_type != "straight rod":
            touchable_molecules = False
            # old comment:
            #  This function won't work properly in this case.
            # Be conservative until that bug is fixed. It's not even safe to permit
            # a click on a handle (which this code is correct in finding),
            # since it might be obscured on the screen
            # by some atom the user is intending to click on.
            #  The only safe thing to find in this case would be something purely draggable
            # with no hard-to-reverse effects, e.g. the "draggable magenta handle",
            # or the base unit (useful only once we permit dragging the model using it).
            #  I might come back and make those exceptions here,
            # if I don't fix the overall bug soon enough. [bruce 041017]
            #
            # newer comment:
            #  Only disable dragging repunits, don't disable dragging or clicking bond-offset spheres
            # (even though they might be clicked by accident when visually behind a repunit of the ring).
            # [bruce 041019]
##            self.status_msg("(click or drag not yet implemented for product type %r; sorry)" % self.product_type)
##            return None
        p1, p2 = self.o.mousepoints(event) # (no side effect. p1 is just at near clipping plane; p2 in center of view plane)
        ##print "touchedthing for p1 = %r, p2 = %r" % (p1,p2)
        res = [] # (dist, handle) pairs, arb. order, but only the frontmost one from each handleset
        if self.show_bond_offsets:
            for hset in self.show_bond_offsets_handlesets:
                dh = hset.frontDistHandle(p1, p2) # dh = (dist, handle)  #######@@@ needs to use bond_tolerance, or get patched
                if dh:
                    res.append(dh)
        #e scan other handlesets here, if we have any
        if touchable_molecules:
            #e now try molecules (if we have not coded them as their own handlesets too) -- only the base and rep units for now
            hset = self.basemol_atoms_handleset
            for ii in range(self.ncopies):
                ##print "try touch",ii
                offset = self.offset * ii
                dh = hset.frontDistHandle(p1, p2, offset = offset, copy_id = ii)
                if dh:
                    res.append(dh) #e dh's handle contains copy_id, a code for which repunit
        if res:
            res.sort()
            dh = res[0]
            handle = dh[1]
            ##print "touched %r" % (handle,)
            return handle
        # nothing touched... need to warn?
        if not touchable_molecules:
            msg = redmsg("Dragging of repeat units not yet implemented for <b>Ring</b> product type.")
            self.propMgr.MessageGroupBox.insertHtmlMessage( msg, setAsDefault  =  False )
            self.status_msg("(dragging of repeat units not yet implemented for product type %r; sorry)" % self.product_type)
        return None

    def leftDrag(self, event):
        """
        Move the touched objects as determined by leftDown(). ###doc
        """
        if self.dragging_this:
            self.doDrag(event, self.dragging_this)

    needs_repaint = 0

    def doDrag(self, event, thing):
        """
        drag thing, to new position in event.
        thing might be a handle (pos,radius,info) or something else... #doc
        """
        # determine motion to apply to thing being dragged.
        #Current code is taken from  TranslateChunks_GraphicsMode.
        # bruce question -- isn't this only right in central plane?
        # if so, we could fix it by using mousepoints() again.
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))

        self.o.SaveMouse(event) # sets MousePos, for next time

        self.needs_repaint = 1 # for now, guess that this is always true (tho it's only usually true)
        thing.move(move) # move handle in the appropriate way for its type
            #e this needs to set self.needs_repaint = 1 if it changes any visible thing!
            ##### how does it know?? ... so for now we always set it *before* calling;
            # that way a repaint during the call can reset the flag.
        ## was: self.o.assy.movesel(move)
        self.repaint_if_needed()

    def repaint_if_needed(self):
        # see also the end of update_offset_bonds_display -- we're inlined ######fix
        if self.needs_repaint:
            self.needs_repaint = 0
            self.o.gl_update()
        return

    def drag_repunit(self, copy_id, motion):
        """
        Drag a repeat unit (copy_id > 0) or the base unit (id 0).
        """
        assert type(copy_id) == type(1) and copy_id >= 0
        if copy_id:
            # move repunit #copy_id by motion
            # compute desired motion for the offset which would give
            # this motion to the repunit
            # bug note -- the code that supplies motion to us is wrong,
            # for planes far from central plane -- fix later.
            motion = motion * (1.0 / copy_id)
            # store it, but not in self.offset, that's reserved for
            # comparison with the last value from the controls
            self.dragged_offset = self.dragged_offset + motion
            #obs comment?? i forget what it meant: #e recompute_for_new_offset
            self.force_offset_and_update( self.dragged_offset)
        else:
            pass##print "dragging base unit moves entire model (not yet implemented)"
        return

    def force_offset_and_update(self, offset):
        """
        Change the controls to reflect offset, then update from the controls.
        """
        x,y,z = offset
        self.propMgr.call_while_suppressing_valuechanged(
            lambda: self.propMgr.set_extrude_controls_xyz( (x, y, z) ) )

        #e worry about too-low resolution of those spinbox numbers?
        # at least not in self.dragged_offset...
        #e status bar msg? no, caller can do it if they want to.
        self.update_from_controls() # this does a repaint at the end
            # (at least if the offset in the controls changed)

    def click_nice_offset_handle(self, handle):
        (pos,radius,info) = handle
        i1,i2 = info
        try:
            ideal, err = self.mergeables[(i1,i2)]
        except KeyError:
            ideal, err = self.mergeables[(i2,i1)]
            ideal = -1 * ideal
        self.force_offset_and_update( ideal)

    def leftUp(self, event):
        if self.dragging_this:
            ## self.doDrag(event, self.dragging_this) ## good idea? not sure. probably not.
            self.dragging_this = None
            #####e update, now that we know the final position of the dragged thing
            del self.dragged_offset
        return

    # ==

    def leftShiftDown(self, event):
        pass ##self.StartDraw(event, 0)

    def leftCntlDown(self, event):
        pass ##self.StartDraw(event, 2)

    def leftShiftDrag(self, event):
        pass ##self.ContinDraw(event)

    def leftCntlDrag(self, event):
        pass ##self.ContinDraw(event)

    def leftShiftUp(self, event):
        pass ##self.EndDraw(event)

    def leftCntlUp(self, event):
        pass ##self.EndDraw(event)

    def update_cursor_for_no_MB(self): # Fixes bug 1638. mark 060312.
        """
        Update the cursor for 'Extrude' mode (extrudeMode).
        """
        self.o.setCursor(QCursor(Qt.ArrowCursor))

    # == drawing helper methods (called by Draw API methods below)

    def _draw_hsets_transparent_before_model(self):
        """
        """
        #bruce 09010 split this out, and into two large pieces
        # before and after _draw_model

        #kluge, and messy experimental code [bruce 050218];
        # looks good w/ crystal, bad w/ dehydrogenated hoop moiety...
        # probably better to compute colors, forget transparency.
        # or it might help just to sort them by depth... and/or
        # let hits of several work (hit sees transparency); not sure
        hset1 = self.nice_offsets_handle # opaque
        hset2 = self.nice_offsets_handleset # transparent

        # draw back faces of hset2 into depth buffer
        # (so far this also draws a color - which one? or does it? yes, white.)
        ## glCullFace(GL_FRONT)
        glFrontFace(GL_CW)
        ## glDisable(GL_LIGHTING)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        try:
            hset2.draw(self.o, color = list(self.o.backgroundColor))##green)
                # alpha factor inside draw method will be 0.25 but won't matter
                ###e wrong when the special_color gets mixed in
            # bugs 1139pm: the back faces are not altering depth buffer,
            # when invis, but are when color = green... why?
            # is it list vs tuple? does tuple fail for a vector?
            # they are all turning white or blue in synch, which is
            # wrong (and they are blue when *outside*, also wrong)
            # generally it's not working as expected... let alone
            # looking nice
            # If i stop disabling lighting above, then it works
            # better... confirms i'm now showing only insides of spheres
            # (with color = A(green), ) does A matter btw? seems not to.
            # ah, maybe the materialfv call in drawsphere assumes lighting...
            # [this never ended up being diagnosed, but it never came back
            #  after i stopped disabling lighting]
        except:
            print_compact_traceback("exc in hset2.draw() backs: ")
        ## glCullFace(GL_BACK)
        glFrontFace(GL_CCW)
        glEnable(GL_LIGHTING)
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)

        # draw front faces (default) of hset2, transparently, not altering depth buffer
        ## hsets = [hset2]
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # this fails since the symbols are not defined, tho all docs say they should be:
##                const_alpha = 0.25
##                glBlendColor(1.0,1.0,1.0,const_alpha) # sets the CONSTANT_ALPHA to const_alpha
##                glBlendFunc(GL_CONSTANT_ALPHA, GL_ONE_MINUS_CONSTANT_ALPHA) # cf. redbook table 6-1 page 228
        # so instead, I hacked hset2.draw to use alpha factor of 0.25, for now
        # it looked bad until I remembered that I also need to disable writing the depth buffer.
        # But the magenta handle should have it enabled...
        glDepthMask(GL_FALSE)
        try:
            hset2.draw(self.o)
        except:
            print_compact_traceback("exc in hset2.draw() fronts with _TRANSPARENT: ")
        glDisable(GL_BLEND)
        glDepthMask(GL_TRUE)

        # draw front faces again, into depth buffer only
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE)
        try:
            hset2.draw(self.o)
        except:
            print_compact_traceback("exc in hset2.draw() fronts depth: ")
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)

        # draw model (and hset1) here, so it's obscured by those
        # invisible front and (less importantly) back faces
        # (this is done in _draw_model and then the following method;
        #  it's split this way due to splitting of Draw in GM API, bruce 090310)
        return

    def _draw_model(self): #bruce 050218 split this out
        """
        Draw the entire model including our base and repeat units,
        or just our base and repeat units, depending on settings.
        """
        try:
            part = self.o.assy.part # "the model"
            if self.show_entire_model:
                part.draw(self.o) # includes before_drawing_model, etc
            else:
                part.before_drawing_model() #bruce 070928 fix predicted bug
                try:
                    for mol in self.molcopies:
                        #e use per-repunit drawing styles...
    ##                    dispdef = mol.get_dispdef( self.o) # not needed, since...
                        dispdef = 'bug'
                        mol.draw(self.o, dispdef) # ...dispdef arg not used (041013)
                            # update, bruce 070407: now that mol can also be a fake_copied_mol,
                            # it's simplest to just use a fake dispdef here.
                finally:
                    part.after_drawing_model() #bruce 070928 fix predicted bug
            try: #bruce 050203
                for unit1,unit2 in zip(self.molcopies[:-1],self.molcopies[1:]):
                    self.draw_bond_lines(unit1,unit2)
            except:
                print_compact_traceback("exception in draw_bond_lines, ignored: ")
                print_compact_stack("stack from that exception was: ")
        except:
            print_compact_traceback("exception in _draw_model, ignored: ")
        return

    def _draw_hsets_transparent_after_model(self):
        """
        """
        #bruce 09010 split this out, and into two large pieces
        # before and after _draw_model
        hset1 = self.nice_offsets_handle # opaque
        try:
            hset1.draw(self.o) # opaque
        except:
            print_compact_traceback("exc in hset1.draw(): ")
        return

    def _draw_ring_axis_and_spokes(self): #bruce 09010 split this out
        """
        """
        if self.product_type == 'closed ring':
            try:
                from utilities.constants import red
                self.update_ring_geometry(emit_messages = False)
                    # emit_messages = False to fix infinite redraw loop
                    # when it chooses z-y plane and prints a message about that
                    # [bruce 071001]
                center = self.circle_center # set by update_ring_geometry
                axis = self.axis_dir # ditto
                radius_vec = self.radius_vec # ditto
                # draw axis
                drawline( red, center, center + axis * 10, width = 2)
                for ii in range(self.circle_n):
                    # draw spoke ii
                    quatii_rel_junk, spoke_vec = self._spoke_quat_and_vector(ii)
                    color = (ii and green) or blue
                    drawline(color, center, center + spoke_vec, width = 2)
                pass
            except:
                msg = "exception using debug_pref(%r) ignored" % \
                    "Extrude: draw ring axis"
                print_compact_traceback(msg + ": ")
                pass
            pass
        return

    # ==

    _TRANSPARENT = True
        #bruce 050218 experiment -- set to True for "transparent bond-offset
        # spheres" (works but doesn't always look good)
        #bruce 050222 update - Mark wants this "always on" for now...
        # but I ought to clean up the code sometime soon

    def Draw_other_before_model(self):
        """
        Do non-CSDL/DrawingSet drawing, *before* Draw_model.
        """
        _superclass.Draw_other_before_model(self)
        if self.show_bond_offsets:
            hsets = self.show_bond_offsets_handlesets
            if self._TRANSPARENT and len(hsets) == 2:
                hset1 = self.nice_offsets_handle
                hset2 = self.nice_offsets_handleset
                assert hset1 in hsets
                assert hset2 in hsets
                self._draw_hsets_transparent_before_model()
                pass
            pass
        return

    def Draw_model(self):
        """
        Draw the model (using only CSDL/DrawingSet drawing).
        """
        _superclass.Draw_model(self)
        self._draw_model()
            ### REVIEW: I'm not sure if this follows the rule of only using
            # CSDLs (not plain drawprimitives or immediate-mode OpenGL)
            # for drawing. (It does if it only calls Chunk draw methods,
            # except for ways in which ChunkDrawer still violates that rule,
            # but that will be fixed in ChunkDrawer.) [bruce 090311 comment]
        return

    def Draw_other(self):
        """
        Do non-CSDL/DrawingSet drawing, *after* Draw_model.
        """
        _superclass.Draw_other(self)
        if self.show_bond_offsets:
            hsets = self.show_bond_offsets_handlesets
            if self._TRANSPARENT and len(hsets) == 2:
                hset1 = self.nice_offsets_handle
                hset2 = self.nice_offsets_handleset
                assert hset1 in hsets
                assert hset2 in hsets
                self._draw_hsets_transparent_after_model()
            else:
                #pre-050218 code
                for hset in hsets:
                    try:
                        hset.draw(self.o)
                    except:
                        print_compact_traceback("exc in some hset.draw(): ")
                    continue
                pass
            pass
        if debug_pref("Extrude: draw ring axis and spokes",
                      Choice_boolean_False,
                      prefs_key = True ): #bruce 070928
            # [this used to happen before Draw_model, but its order
            #  shouldn't matter. [bruce 090310]]
            self._draw_ring_axis_and_spokes()
        return

    # ==

    ## Added this method to fix bug 1043 [Huaicai 10/04/05]
    def Draw_after_highlighting(self, pickCheckOnly = False):
        """
        Only draw translucent parts of the whole model when we are
        requested to draw the whole model.
        """
        if self.show_entire_model:
            return _superclass.Draw_after_highlighting(self, pickCheckOnly)
        return

    # ==

    call_makeMenus_for_each_event = True #bruce 050914 enable dynamic context menus [fixes bug 971]

    def makeMenus(self): #e not yet reviewed for being good choices of what needs including in extrude cmenu

        self.Menu_spec = [
            ('Cancel', self.command_Cancel),
            ('Start Over', self.StartOver),
            ('Done', self.command_Done), #bruce 041217
        ]

        self.debug_Menu_spec = [
            ('debug: reload module', self.extrude_reload),
        ]

        self.Menu_spec_control = [
            ('Invisible', self.w.dispInvis),
            None,
            ('Default', self.w.dispDefault),
            ('Lines', self.w.dispLines),
            ('Ball & Stick', self.w.dispBall),
            ('Tubes', self.w.dispTubes),
            ('CPK', self.w.dispCPK),
            None,
            ('Color', self.w.dispObjectColor) ]

        return

    def extrude_reload(self):
        """
        for debugging: try to reload extrudeMode.py and patch your glpane
        to use it, so no need to restart Atom. Might not always work.
        [But it did work at least once!]
        """
        global extrudeMode
        print "extrude_reload: here goes.... (not fully working as of 080805)"

        # status as of 080805: mostly works, but:
        # - warns about duplicate featurename;
        # - extrude refuses entry since nothing is selected (should select repunit to fix);
        # - has some dna updater errors if it was extruding dna (might be harmless).

        try:
            self.propMgr.extrudeSpinBox_n.setValue(1)
            self.update_from_controls()
            print "reset ncopies to 1, to avoid dialog from exit_is_forced, and ease next use of the mode"
        except:
            print_compact_traceback("exception in resetting ncopies to 1 and updating, ignored: ")

##        try:
##            self.restore_gui()
##        except:
##            print_compact_traceback("exception in self.restore_gui(), ignored: ")

        self.commandSequencer.exit_all_commands() #bruce 080805

##        for clas in [extrudeMode]:
##            try:
##                self.commandSequencer.mode_classes.remove(clas) # was: self.__class__
##            except ValueError:
##                print "a mode class was not in _commandTable (normal if last reload of it had syntax error)"
        self.commandSequencer.remove_command_object( self.commandName) #bruce 080805

        import graphics.drawables.handles as handles
        reload(handles)
        import commands.Extrude.extrudeMode as _exm
        reload(_exm)
        from commands.Extrude.extrudeMode import extrudeMode # note global declaration above

##        try:
##            do_what_MainWindowUI_should_do(self.w) # remake interface (dashboard), in case it's different [041014]
##        except:
##            print_compact_traceback("exc in new do_what_MainWindowUI_should_do(), ignored: ")

##        ## self.commandSequencer._commandTable['EXTRUDE'] = extrudeMode
##        self.commandSequencer.mode_classes.append(extrudeMode)

        self.commandSequencer.register_command_class( self.commandName, extrudeMode ) #bruce 080805
            # note: this does NOT do whatever recreation of a cached command
            # object might be needed (that's done only in _reinit_modes)

        print "about to reset command sequencer"
        # need to revise following to use some cleaner interface
        self.commandSequencer._reinit_modes() # leaves mode as nullmode as of 050911
        self.commandSequencer.start_using_initial_mode( '$DEFAULT_MODE' )
            ###e or could use commandName of prior self.commandSequencer.currentCommand
        print "done with _reinit_modes, now we'll try to reenter extrudeMode"
        self.commandSequencer.userEnterCommand( self.commandName) #bruce 080805
        return

    pass # end of class extrudeMode

# ==

# helper functions for extrudeMode.Enter

def assy_merge_mols(assy, mollist):
    """
    merge multiple mols (Chunks) in assy (namely, the elements of sequence mollist)
    into one mol in assy [destructively modifying the first mol in mollist to be the one],
    and return it
    """
    # note: doesn't use assy arg, but assumes all mols in mollist are in same assy and Part [070408 comment]
    mollist = list(mollist) # be safe in case it's identical to assy.selmols,
        # which we might modify as we run
    assert len(mollist) >= 1
    ## mollist.sort() #k ok for mols? should be sorted by name, or by
    ## # position in model tree groups, I think...
    ## for now, don't sort, use selection order instead.
    res = mollist[0]
    if 1: ## debug_pref("Extrude: leave base-chunks separate", Choice_boolean_False, non_debug = True, prefs_key = True):
        #bruce 070410 making this always happen now (but Enter should call
        # get_whendone_merge_each_unit to exercise debug pref);
        # when we're done we will do the merge differently
        # according to "merge selection" checkbox or debug_pref, in finalize_product,
        # not here when we enter the mode!
        #
        # could optim by not doing this when only one member,
        # but that might hide bugs and doesn't matter otherwise, so nevermind.
        res = fake_merged_mol(res)
    for mol in mollist[1:]: # ok if no mols in this loop
        res.merge(mol) #041116 new feature
        # note: this will unpick mol (modifying assy.selmols) and kill it
    return res

def assy_fix_selmol_bugs(assy):
    """
    Work around bugs in other code that prevent extrude from entering.
    """
    # 041116 new feature; as of 041222, runs but don't know if it catches bugs
    # (maybe they were all fixed).
    # Note that selected chunks might be in clipboard, and as of 041222
    # they are evidently also in assy.molecules, and extrude operates on them!
    # It even merges units from main model and clipboard... not sure that's good,
    # but ignore it until we figure out the correct model tree selection semantics
    # in general.
    for mol in list(assy.selmols):
        if (mol not in assy.molecules) or (not mol.dad) or (not mol.assy):
            try:
                it = " (%r) " % mol
            except:
                it = " (exception in its repr) "
            print "fyi: pruning bad mol %s left by prior bugs" % it
            try:
                mol.unpick()
            except:
                pass
            # but don't kill it (like i did before 041222)
            # in case it's in clipboard and user wants it still there
    #e worry about selatoms too?
    return

def assy_extrude_unit(assy, really_make_mol = 1):
    """
    If we can find a good extrude unit in assy,
    make it a molecule in there, and return (True, mol)
    [as of 070412 bugfixes, mol is always a fake_merged_mol];
    else return (False, whynot).
    Note: we might modify assy even if we return False in the end!!!
    To mitigate that (for use in command_ok_to_enter), caller can pass
    really_make_mol = 0, and then we will not change anything in assy
    (unless it has bugs caught by assy_fix_selmol_bugs),
    and we'll return either (True, "not a mol") or (False, whynot).
    """
    # bruce 041222: adding really_make_mol flag.

    ## not needed (and not good) after assy/part split, 050309:
    ## assy.unselect_clipboard_items() #bruce 050131 for Alpha

    assy_fix_selmol_bugs(assy)
    resmol = "not a mol"
    if assy.selmols:
        assert type(assy.selmols) == type([]) # assumed by this code; always true at the moment
        if really_make_mol:
            resmol = assy_merge_mols( assy, assy.selmols) # merge the selected mols into one
        return True, resmol
            #e in future, better to make them a group? or use them in parallel?
    elif assy.selatoms:
        if really_make_mol:
            res = []
            def new_old(new, old):
                # new = fragment of selected atoms, old = rest of their mol
                assert new.atoms
                res.append(new) #e someday we might use old too, eg for undo or
                    # for heuristics to help deal with neighbor-atoms...
            assy.modifySeparate(new_old_callback = new_old) # make the selected atoms into their own mols
                # note: that generates a status msg (as of 041222).
            assert res, "what happened to all those selected atoms???"
            resmol = assy_merge_mols( assy, res) # merge the newly made mol-fragments into one
                #e or for multiple mols, should we do several extrudes in parallel? hmm, might be useful...
        return True, resmol
    elif len(assy.molecules) == 1:
        # nothing selected, but exactly one molecule in all -- just use it
        if really_make_mol:
            resmol = assy.molecules[0]
            resmol = fake_merged_mol(resmol) #bruce 070412 bugfix, might be redundant
                # with another one or might fix other uncaught bugs
        return True, resmol
    else:
        ## print 'assy.molecules is',`assy.molecules` #debug
        return False, "Nothing selected to extrude."
    pass

# ==

#e between two molecules, find overlapping atoms/bonds ("bad") or singlets ("good") --
# as a function of all possible offsets
# (in future, some cases of overlapping atoms might be ok,
#  since those atoms could be merged into one)

# (for now, we notice only bondable singlets, nothing about
#  overlapping atoms or bonds)

cosine_of_permitted_noncollinearity = 0.5 #e we might want to adjust this parameter

def mergeable_singlets_Q_and_offset(s1, s2, offset2 = None, tol = 1.0):
    """
    Figure out whether singlets s1 and s2, presumed to be in different
    molecules (or in different copies, if now in the same molecule), could
    reasonably be merged (replaced with one actual bond), if s2.molecule was
    moved by approximately offset2 (or considering all possible offset2's
     if this arg is not supplied); and if so, what would be the ideal offset
    (slightly different from offset2) after this merging.
       Return (False, None, None) or (True, ideal_offset2, error_offset2),
    where error_offset2 gives the radius of a sphere of reasonable offset2
    values, centered around ideal_offset2.
       The tol option, default 1.0, can be given to adjust
    the error_offset2 (by multiplying the standard value), both for returning
    it and for deciding whether to return (False,...) or (True,...).
    Larger tol values make it more likely that s1,s2 are considered bondable.
       To perform actual bonding, see bonds.bond_at_singlets. But note that
    it is quite possible for the same s1 to be considered bondable to more
    than one s2 (or vice versa), even for tol = 1.0 and especially for larger
    tol values.
    """
    #bruce 050324 added tol option [###@@@ untested] for use by Mark in Fuse Chunks;
    # it's not yet used in extrudeMode, but could be if we changed to
    # recalculating bondable pairs more often, e.g. to fix bugs in ring mode.

    #e someday we might move this to a more general file
    #e once this works, we might need to optimize it,
    # since it redoes a lot of the same work
    # when called repeatedly for the same extrudable unit.
    res_bad = (False, None, None)
    a1 = s1.singlet_neighbor()
    a2 = s2.singlet_neighbor()
    r1 = a1.atomtype.rcovalent
    r2 = a2.atomtype.rcovalent
    dir1 = norm(s1.posn()-a1.posn())
    dir2 = norm(s2.posn()-a2.posn())
    # the open bond directions (from their atoms) should point approximately
    # opposite to each other -- per Josh suggestion, require them to be
    # within 60 deg. of collinear.
    closeness = - dot(dir1, dir2) # ideal is 1.0, terrible is -1.0
    if closeness < cosine_of_permitted_noncollinearity:
        if _EXTRUDE_LOOP_DEBUG and closeness >= 0.0:
            print "rejected nonneg closeness of %r since less than %r" % \
                  (closeness, cosine_of_permitted_noncollinearity)
        return res_bad
    # ok, we'll merge. Just figure out the offset. At the end, compare to offset2.
    # For now, we'll just bend the half-bonds by the same angle to make them
    # point at each other, ignoring other bonds on their atoms.
    new_dir1 = norm( (dir1 - dir2) / 2 )
    new_dir2 = - new_dir1 #e needed?
    a1_a2_offset = (r1 + r2) * new_dir1 # ideal offset, just between the atoms
    a1_a2_offset_now = a2.posn() - a1.posn() # present offset between atoms
    ideal_offset2 = a1_a2_offset - a1_a2_offset_now # required shift of a2
    error_offset2 = (r1 + r2) / 2.0 # josh's guess (replaces 1.0 from the initial tests)
    error_offset2 *= tol # bruce 050324 new feature, untested ###@@@
    if offset2 is not None: #bruce 050328 bugfix: don't use boolean test of offset2 #050513 != -> is not
        if vlen(offset2 - ideal_offset2) > error_offset2:
            return res_bad
    return (True, ideal_offset2, error_offset2)

# ==

# detect reloading
try:
    _already_loaded
except:
    _already_loaded = 1
else:
    print "reloading extrudeMode.py"
pass

def mark_singlets(separate_basemols, colorfunc):
    for basemol in separate_basemols:#bruce 070407 [#e or could use true_Chunks_in]
        for a in basemol.atoms.itervalues():
            ## a.info = a.key
            a.set_info(a.key) #bruce 060322
        basemol._colorfunc = colorfunc # maps atoms to colors (due to a hack i will add)
    return

def true_Chunks_in(mol): #bruce 070407
    if isinstance(mol, Chunk):
        return [mol]
    else:
        return list(mol._mols)
    pass

# not done:
# for (i1,i2) in bonds:
            # assume no singlet appears twice in this list!
# this is not yet justified, and if false will crash it when it makes bonds

# ==

# bruce 070407 new stuff for making it possible to not merge the mols in assy_extrude_unit

class virtual_group_of_Chunks:
    """
    private superclass for sets of chunks treated in some ways as if they were
    one chunk.
    """
    # Note: we don't define __init__ since it differs in each subclass.
    # But it's always required to somehow create a list, self._mols.
    # Note: we define some methods here even if only one subclass needs them,
    # when they'd clearly be correct for any virtual group of Chunks.
    def draw(self, glpane, dispdef):
        for mol in self._mols:
            mol.draw(glpane, dispdef)
    def changeapp(self, *args):
        for mol in self._mols:
            mol.changeapp(*args)
    def _get_externs(self):
        """
        Get a list of bonds which bridge atoms in one of our chunks to atoms
        not in one of them.
        """
        # alg: this is a subset of the union of the sets of externs of our chunks.
        ourmols = dict([(mol,1) for mol in self._mols]) #e could cache this, but not important
        is_ourmol = lambda mol: mol in ourmols
        res = []
        for mol in self._mols:
            for bond in mol.externs:
                if not (is_ourmol(bond.atom1.molecule) and is_ourmol(bond.atom2.molecule)):
                    res.append(bond)
        return res
    def _get_singlets(self):
        res = []
        for mol in self._mols:
            res.extend(mol.singlets)
        return res
    def get_dispdef(self):
        assert 0, "need to zap all direct uses of get_dispdef in class %r" % (self.__class__.__name__)
    def unpick(self):
        for mol in self._mols:
            mol.unpick()
        return
    def kill(self):
        for mol in self._mols:
            mol.kill()
        return
    def internal_merge(self):
        """
        Merge each of our chunks into the first one.
        """
        first = self._mols[0]
        others = self._mols[1:]
        for other in others:
            first.merge(other)
        return
    pass # end of class virtual_group_of_Chunks

class fake_merged_mol( virtual_group_of_Chunks): #e rename? 'extrude_unit_holder'
    """
    private helper class for use in Extrude,
    to let it treat a set of chunks (comprising the extrude unit)
    as if they were merged into one chunk, without actually merging them.
    """
    def __init__(self, mols):
        self._mols = []
        try:
            mols = list(mols)
        except:
            mols = [mols] # kluge(?) -- let mols be a single mol or a list of them
        for mol in mols:
            self.merge(mol)
    def merge(self, mol):
        """
        Unlike Chunk.merge(mol) (for mol being another chunk),
        only remember mol, don't steal its atoms and kill it.
        Also let mol be a Group, not just a Chunk
        (though we may define fewer methods correctly in that case,
         since we define just barely enough to get by in the current private use).
        We will let Extrude call this method and think it's really merging, though it's not.
        NOTE: it calls this not only in assy_extrude_unit, but in merging the copies
        to create the final product. We detect that (by class of mol) and act differently.
        """
        if isinstance(mol, fake_copied_mol):
            # assume it's a copy of us, and this is during extrude's "final product merge";
            # merge its mols into ours, in order
            assert len(self._mols) == len(mol._mols)
            for ourmol, itsmol in zip(self._mols, mol._mols):
                ourmol.merge(itsmol)
        else:
            # assume we're being initially built up by assy_merge_mols, so mol is a Chunk
            assert isinstance(mol, Chunk)
            self._mols.append(mol)
        return
    def __getattr__(self, attr): # in class fake_merged_mol
        if attr.startswith('__'):
            raise AttributeError, attr
        if attr == 'externs':
            return self._get_externs() # don't cache, since not constant (too slow?? ###)
        if attr == 'singlets':
            return self._get_singlets() # don't cache, since not constant
        if attr == 'quat':
            return getattr(self._mols[0], attr)
        # update 070411: self.center is computed and cached in full_inval_and_update;
        # before that, it's illegal to ask for it
        raise AttributeError, "%r has no %r" % (self, attr)
##    def copy(self, dad):
##        self.copy_single_chunk(dad)
    def copy_single_chunk(self, dad):
        """
        copy our mols and store them in a new fake_copied_mol (which might make a Group from them, fyi)
        """
        #bruce 080314 renamed (here and in class Chunk), added copy glue; see comment where it's called here
        assert dad is None
        ## copies = [mol.copy_single_chunk(None) for mol in self._mols]
            # this is wrong when there are bonds between these mols!
        # WARNING: the following code after our call to copy_nodes_in_order is similar to
        # other code after calls to the related function copied_nodes_for_DND, e.g. in depositMode.py.
        # A higher-level utility routine which does all this post-processing should be added to ops_copy.py. ###e
        from operations.ops_copy import copy_nodes_in_order
            #bruce 070525 precaution: use this instead of copied_nodes_for_DND, since order
            # (in fact, precise 1-1 orig-copy correspondence) matters here.
        oldnodes = self._mols
        newnodes = copy_nodes_in_order(list(self._mols)) #k list() wrapper is just a precaution, probably not needed
            # note: these copies are not yet added to the model (assy.tree).
        assert type(newnodes) == type([])
        assert len(newnodes) == len(oldnodes)
            #k can one of these fail if we try to copy a jig w/o its atoms? probably yes! (low-pri bug)
            # (I don't know if extrude is documented to work for jigs, but it ought to,
            #  but I'm sure there are several other things it's doing that also don't work in jigs.) [bruce 070412]
        ###k are these nodes renamed?? if not we'll have to do that now...
        assy = oldnodes[0].assy
        for newMol in newnodes:
            if newMol is not None: #bruce 070525 precaution
                from model.chunk import mol_copy_name
                newMol.name = mol_copy_name(newMol.name, assy)
                    # this should work for any kind of node, unless it has an update bug for some of them,
                    # but since the node doesn't yet have a dad, that's very unlikely.
                assy.addmol(newMol)
                    # Note: this might not be the best location in assy,
                    # but the caller can fix that. This might be easier
                    # than fixing it here (if not, maybe we'll revise this).
                    # (Maybe it's best to put this in the same DnaGroup
                    #  if there is one? Or, in the same Group except for
                    #  Groups with a controlled membership, like
                    #  DnaStrandOrSegment?)
                    # REVIEW: it is necessary to add newMol to assy anywhere?
                    # The method we override on class Chunk probably doesn't.
                    # [bruce 080626]
            else:
                # can this ever happen? if so, we'll print way too much here...
                print "warning: extrude ignoring failed copy"
        ###k will we also need assy.update_parts()??
        copies = newnodes
        return fake_copied_mol(copies, self)
            # self is needed for .center and for basecenters of originals (._mols), due to a kluge
    def full_inval_and_update(self):
        for mol in self._mols:
            mol.full_inval_and_update()
            assert mol.quat == Q(1,0,0,0) # KLUGE, but much here depends on this [bruce 070411]
            assert not (mol.center != mol.basecenter) # ditto [bruce 070411]
                # note: this "not !=" is how you have to compare Numeric arrays [bruce 070411]
                # note: this will fail if Chunk has user_specified_center (nim at the moment),
                # and Chunk.set_basecenter_and_quat may not be correct then anyway (not sure).
        # compute self.center as weighted average of component centers
        centers = [mol.center for mol in self._mols]
        weights = [mol.center_weight for mol in self._mols]
        self.center = weighted_average(weights, centers)
        return
    def contains_atom(self, atom): #bruce 070514, added to Node API 080305
        """
        [imitates Node API method]
        """
        mol = atom.molecule
        assert mol.contains_atom(atom)
            # Note: this fact is not needed here, but this assert is the only test
            # of that implem of the new method contains_atom. It can be removed
            # once something else uses that method (or when we have a regression
            # test for it).
        return (mol in self._mols)

    pass # end of class fake_merged_mol

    # the methods/attrs we need to handle on the baseunit are:

    ##fake_merged_mol will delegate attr 'externs' + [needed to bust them so singlets have definite .info attr, preserved on copy]
    ##fake_merged_mol will delegate attr 'full_inval_and_update' + [needed to reset quats to 0, i think -- maybe since done by copy??]
    ##fake_merged_mol will delegate attr 'atoms' - not needed -- was in mark_singlets and another, both rewritten as loops
    ##fake_merged_mol will delegate attr 'get_dispdef' -- zapped the uses
    ##fake_merged_mol will delegate attr 'singlets' + [used in recompute_for_new_unit]
    ##fake_merged_mol will delegate attr 'center' - 1st mol ok
    ##fake_merged_mol will delegate attr 'quat' - 1st mol ok

    ##fake_merged_mol will delegate attr 'copy' +
    ##fake_merged_mol will delegate attr 'unpick' +
    ##fake_merged_mol will delegate attr 'changeapp' +
    ##fake_merged_mol will delegate attr 'draw' +

def weighted_average(weights, centers): #bruce 070930 split this out #e refile? #e replace with preexisting implem?
    """
    Centers and weights must be sequences of the same length;
    return the weighted average of centers using the given weights.
    The centers can be of any data type which works with sum(sequence) and has scalar * and /.
    The weights should be summable and convertable to floats.
    """
    assert len(weights) == len(centers) >= 1
    weighted_centers = [weights[i] * centers[i] for i in range(len(weights))]
    res = sum(weighted_centers) / float( sum(weights) )
        # bug 2508 was evidently caused by effectively using sum(centers) here
        # instead of sum(weighted_centers) [bruce 070930]
##    if len(weights) == 1:
##        # sanity check [bruce 070928]
##        # ideally we'd assert that the following values are very close:
##        print "debug note re bug 2508: these points should be close: %r and %r" % (res , centers[0])
    return res

class fake_copied_mol( virtual_group_of_Chunks): #e rename? 'extrude_unit_copy_holder'
    """
    private helper class for extrude, to serve as a "rep-unit" copy of a fake_merged_mol instance.
    Holds a list of copied mols (chunks) made by copying extrude's basemol when it's a fake_merged_mol,
    and (if desired) a Group made from them (for use in MT).

    @warning: our client extrudeMode will also do isinstance tests on this class,
    and peer into our private attrs like self._mols,
    so some of our semantics comes from client code that depends on our class.
    """
    def __init__(self, copies, _a_fake_merged_mol):
        self._parent = _a_fake_merged_mol
        self._mols = copies # list of mol copies, made by an instance of fake_merged_mol, corresponding with its mols
        self._originals = _a_fake_merged_mol._mols # needed only in set_basecenter_and_quat (due to a kluge)
        assy = copies[0].assy
##        self._group = Group('extruded', assy, None, copies) # not yet in MT; OBSOLETE except for delegation;
            # I worried that it might cause dad-conflict bugs in the members, but evidently it doesn't...
            # even so, safer to remove both this and __getattr__ (not only this, or __getattr__ infrecurs)
        return
    def set_basecenter_and_quat(self, c, q):
        std_basecenter = self._parent.center
        for mol, orig in zip(self._mols, self._originals):
            # Compute correct c for how our basemol differs from first one
            # (for explanation, see long comment in want_center_and_quat).
            #
            # Note: this is not ideal behavior for ring mode, in which q varies -- we should correct c for that, too,
            # but we don't [update, 070411: fixing that now],
            # which means we make several parallel rings (one per element of self._mols),
            # rather than one ring with a common center. To fix this, we'd correct c for q here,
            # and also compute an overall center in fake_merged_mol rather than just delegating it
            # to one of the components.
            c1 = c - std_basecenter
            # The caller's intent is to rotate self by q around its center, then shift self by c1,
            # all relative to self's starting point, as the caller recorded earlier (self.center and self.quat),
            # either on self or on its parent (from which self was copied, after full_inval_and_update).
            # Internally we do the same, except we correct for a different center of rotation.
            #
            # ... if we want self center to be *here*, where do we want component center to be?
            orig_offset = orig.center - std_basecenter
            net_offset = q.rot(orig_offset) - orig_offset
            c1 = c1 + net_offset
            mol.set_basecenter_and_quat(orig.basecenter + c1, q)
        return
    pass # end of class fake_copied_mol

# end
