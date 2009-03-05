# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
jigs.py -- Classes for motors and other jigs, and their superclass, Jig.

@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.

History:

Mostly written as gadgets.py (I'm not sure by whom);
renamed to jigs.py by bruce 050414; jigs.py 1.1 should be an
exact copy of gadgets.py rev 1.72,
except for this module-docstring and a few blank lines and comments.

bruce 050507 pulled in the jig-making methods from class Part.

bruce 050513 replaced some == with 'is' and != with 'is not',
to avoid __getattr__ on __xxx__ attrs in python objects.

bruce circa 050518 made rmotor arrow rotate along with the atoms.

050927 moved motor classes to jigs_motors.py and plane classes to jigs_planes.py

mark 051104 Changed named of Ground jig to Anchor.

bruce 080305 changed Jig superclass from Node to NodeWith3DContents
"""

from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import glEnable
from OpenGL.GL import GL_FRONT
from OpenGL.GL import GL_LINE
from OpenGL.GL import glPolygonMode
from OpenGL.GL import GL_BACK
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glDisable
from OpenGL.GL import GL_CULL_FACE
from OpenGL.GL import glPushName
from OpenGL.GL import glPopName
from OpenGL.GL import GL_FILL


from utilities import debug_flags

from utilities.icon_utilities import imagename_to_pixmap

from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key

from utilities.constants import gensym
from utilities.constants import blue
from utilities.constants import darkred
from utilities.constants import black

from utilities.Log import orangemsg

from utilities.debug import print_compact_stack, print_compact_traceback


from geometry.VQT import A


import foundation.env as env
from foundation.Utility import NodeWith3DContents
from foundation.state_constants import S_REFS


from graphics.rendering.povray.povheader import povpoint

from graphics.drawing.drawers import drawwirecube

from graphics.drawing.patterned_drawing import isPatternedDrawing
from graphics.drawing.patterned_drawing import startPatternedDrawing
from graphics.drawing.patterned_drawing import endPatternedDrawing

from graphics.drawables.Selobj import Selobj_API


from commands.ThermostatProperties.StatProp import StatProp
from commands.ThermometerProperties.ThermoProp import ThermoProp

# ==

_superclass = NodeWith3DContents #bruce 080305 revised this

class Jig(NodeWith3DContents, Selobj_API):
    """
    Abstract superclass for all jigs.

    @note: some jigs refer to atoms, but no jigs *contain* atoms.

    @note: most jigs don't really have "3D content", since they derive
           this implicitly from their atoms. But some do, so as long as
           they are all inheriting one class, that class needs to
           inherit NodeWith3DContents rather than just Node.
    """
    
    # Each Jig subclass must define the class variables:
    # - icon_names -- a list of two icon basenames (one normal and one "hidden")
    #   to be passed to imagename_to_pixmap
    #   (unless that Jig subclass overrides node_icon)
    icon_names = ("missing", "missing-hidden") # will show up as blank icons if not overridden
        # (see also: "modeltree/junk.png", which exists, but has no hidden form)
    
    #
    # and the class constants:
    # - mmp_record_name (if it's ever written to an mmp file)
    mmp_record_name = "#" # if not redefined, this means it's just a comment in an mmp file

    #
    # and can optionally redefine some of the following class constants:
    
    sym = "Jig" # affects name-making code in __init__

    featurename = "" # wiki help featurename for each Jig (or Node) subclass, or "" if it doesn't have one yet [bruce 051201]
        # (Each Jig subclass should override featurename with a carefully chosen name; for a few jigs it should end in "Jig".)

    _affects_atom_structure = True # whether adding or removing this jig
        # to/from an atom should record a structural change to that atom
        # (in _changed_structure_Atoms) for purposes of undo and updaters.
        # Unclear whether it ever needs to be True, but for historical
        # compatibility, it's True except on certain new jig classes.
        # (For more info see comments where this is used in class Atom.)
        # OTOH it's also possible this is needed on all jigs, even internal ones,
        # to prevent undo bugs (when undoing changes to a jig's atoms).
        # Until that's reviewed, it should not be overridden on any jig.
        # [bruce 071128]
    
    # class constants used as default values of instance variables:
    
    #e we should sometime clean up the normcolor and color attributes, but it's hard,
    # since they're used strangly in the *Prop.py files and in our pick and unpick methods.
    # But at least we'll give them default values for the sake of new jig subclasses. [bruce 050425]

    color = normcolor = (0.5, 0.5, 0.5)
    
    # "Enable in Minimize" is only supported for motors.  Otherwise, it is ignored.  Mark 051006.
    # [I suspect the cad code supports it for all jigs, but only provides a UI to set it for motors. -- bruce 051102]

    enable_minimize = False # whether a jig should apply forces to atoms during Minimize
        # [should be renamed 'enable_in_minimize', but I'm putting this off since it affects lots of files -- bruce 051102]
        # WARNING: this is added to copyable_attrs in some subclasses, rather than here
        # (which is bad style, IMHO, but I won't change it for now). [bruce 060228 comment]
        # (update, bruce 060421: it may be bad style, but in current copy & undo code it also saves memory & time
        #  if there are lots of jigs. I don't know if there can yet be lots of jigs in practice, in ways that affect those things,
        #  since I forget the details of pi_bond_sp_chain jigs.)

    dampers_enabled = True # whether a jig which can have dampers should actually have them (default True in cad and sim)
        # (only used in rotary motor sim & UI so far, but supported for read & write for all jigs,
        #  and for copy for rotary and linear motors) [bruce 060421 for A7]
    
    atoms = None
    cntl = None # see set_cntl method (creation of these deferred until first needed, by bruce 050526)
    propmgr = None # see set_propmgr method in RotaryMotor class. Mark 2007-05-28.
    
    copyable_attrs = _superclass.copyable_attrs + ('normcolor', 'color')
        # added in some subclasses: 'enable_minimize', 'dampers_enabled'
        # most Jig subclasses need to extend this further

    _s_attr_atoms = S_REFS #bruce 060228 fix bug 1592 [untested]
    
    def __init__(self, assy, atomlist):
        """
        Each subclass needs to call this, either in its own __init__ method
        or at least sometime before it's used as a Node.

        @warning: any subclass which overrides this and changes the argument signature
                  may need to override _um_initargs as well.

        [extends superclass method]
        """
        # Warning: some Jig subclasses require atomlist in __init__ to equal [] [revised circa 050526]
        _superclass.__init__(self, assy, gensym("%s" % self.sym, assy))
        self.setAtoms(atomlist) #bruce 050526 revised this; this matters since some subclasses now override setAtoms
            # Note: the atomlist fed to __init__ is always [] for some subclasses
            # (with the real one being fed separately, later, to self.setAtoms)
            # but is apparently required to be always nonempty for other subclasses.
        #e should we split this jig if attached to more than one mol??
        # not necessarily, tho the code to update its appearance
        # when one of the atoms move is not yet present. [bruce 041202]
        #e it might make sense to init other attrs here too, like color
        ## this is now the default for all Nodes [050505]: self.disabled_by_user_choice = False #bruce 050421

        # Huaicai 7/15/05: support jig graphically select
        self.glname = self.assy.alloc_my_glselect_name( self) #bruce 080917 revised
            ### REVIEW: is this ok or fixed if this chunk is moved to a new assy
            # (if that's possible)? [bruce 080917 Q]
        
        return

    def _um_initargs(self):
        """
        Return args and kws suitable for __init__.
        [Overrides an undo-related superclass method; see its docstring for details.]
        """
        # [as of 060209 this is probably well-defined and correct (for most Jig subclasses), ...]
        # [as of 071128 it looks like it's only used in nodes that inherit SimpleCopyMixin,
        #  but is slated to become used more widely when copy code is cleaned up.
        #  It is also not currently correct for RotaryMotor and LinearMotor.]
        return (self.assy, self.atoms), {} # This should be good enough for most Jig subclasses.

    def node_icon(self, display_prefs):
        """
        a subclass should override this if it needs to choose its icons differently
        """
        return imagename_to_pixmap( self.icon_names[self.hidden] )
        
    def setAtoms(self, atomList):
        """
        Set self's atoms to the atoms in atomList, and append self to atom.jigs
        for each such atom, doing proper invalidations on self and those atoms.

        If self already has atoms when this is called, first remove them (which
        includes removing self from atom.jigs for each such atom, doing proper
        invalidations on that atom).

        Report errors if self's membership in atom.jigs lists is not as expected.

        Subclasses can override this if they need to take special action
        when their atomlist is initialized. (It's called in Jig.__init__
        and in Jig._copy_fixup_at_end.)

        @param atomList: List of atoms to which this jig needs to be attached. 
        @type  atomList: list
        
        @see: L{self._remove_all_atoms}
        @see: L{RotaryMotor_EditCommand._modifyStructure} for an example use
        @see: L{self.setShaft} (for certain subclasses)
        """
        if self.atoms:
            # intended to fix bug 2561 more safely than the prior change [bruce 071010]
            self._remove_all_atoms() 
        self.atoms = list(atomList) # copy the list
        for atom in atomList:
            if self in atom.jigs:
                print "bug: %r is already in %r.jigs, just before we want" \
                      " to add it" % (self, atom)
            else:
                atom._f_jigs_append(self,
                            changed_structure = self._affects_atom_structure )
        return

    def is_glpane_content_itself(self): #bruce 080319
        # note: some code which tests for "Chunk or Jig" might do better
        # to test for this method's return value.
        """
        @see: For documentation, see Node method docstring.

        @rtype: boolean

        [overrides Node method, but as of 080319 has same implem]
        """
        # Note: we may want this False return value even if self *is* shown
        # and if this does get called in practice (see Node docstring
        # for context of this comment). The effect of this being False
        # for things visible in GLPane is that in some cases they
        # would be picked automatically due to things in the same Groups
        # being picked. If we don't decide to revise this behavior for most Jigs,
        # and if it matters due to this being called for normal Groups
        # (not just inside special Dna groups of various kinds),
        # it probably means this method is misnamed or misdescribed.
        # [bruce 080319]
        return False
    
    def needs_atoms_to_survive(self):
        return True # for most Jigs
    
    def _draw(self, glpane, dispdef):
        """
        Draws the jig in the normal way.
        """
        # russ 080530: Support for patterned selection drawing modes.
        selected = self.picked and not self.is_disabled()
        patterned = isPatternedDrawing(select = selected)
        if patterned:
            # Patterned selection drawing needs the normal drawing first.
            self._draw_jig(glpane, self.normcolor)
            startPatternedDrawing(select = True)
            pass
        # Draw solid color (unpatterned) or overlay pattern in the selection color.
        self._draw_jig(glpane,
                       (selected and env.prefs[selectionColor_prefs_key]
                        or self.color))
        if patterned:
            # Reset from patterned drawing mode.
            endPatternedDrawing(select = True)
            pass
        return
        
    def draw_in_abs_coords(self, glpane, color):
        """
        Draws the jig in the highlighted way.
        """
        # russ 080530: Support for patterned highlighting drawing modes.
        patterned = isPatternedDrawing(highlight = True)
        if patterned:
            # Patterned highlighting drawing needs the normal drawing first.
            self._draw_jig(glpane, self.normcolor, 1)
            startPatternedDrawing(highlight = True)
            self._draw_jig(glpane,
                           env.prefs[hoverHighlightingColor_prefs_key], 1)
            endPatternedDrawing(highlight = True)
        else:
            self._draw_jig(glpane, color, 1)
            pass
        return
        
    def _draw_jig(self, glpane, color, highlighted = False):
        """
        This is the main drawing method for a jig,
        which Jig subclasses may want to override.
        (The public methods which call it, draw -> _draw -> _draw_jig
        and draw_in_abs_coords -> _draw_jig, do useful things
        that should be common to most jig drawing.)

        Note that the current code [080118] is a mess in terms of exactly which
        drawing methods are overridden by various jigs. I don't know if this
        is justified by the "common code" being harmful in some cases,
        or just carelessness. Either way, it needs cleanup.
        
        By default, this method draws a wireframe box around each of the jig's atoms.
        This method should be overridden by subclasses that want to do more than
        simply draw wireframe boxes around each of the jig's atoms.
        For a good example, see the MeasureAngle._draw_jig().
        """
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked:
                rad *= 1.01
            drawwirecube(color, a.posn(), rad)
    
    # == copy methods [default values or common implems for Jigs,
    # == when these differ from Node methods] [bruce 050526 revised these]
    
    def will_copy_if_selected(self, sel, realCopy):
        """
        [overrides Node method]
        """
        # Copy this jig if asked, provided the copy will refer to atoms if necessary.
        # Whether it's disabled (here and/or in the copy, and why) doesn't matter.
        if not self.needs_atoms_to_survive():
            return True
        for atom in self.atoms:
            if sel.picks_atom(atom):
                return True
        if realCopy:
            # Tell user reason why not.  Mark 060125.
            # [bruce 060329 revised this, to make use of wware's realCopy arg.
            #  See also bugs 1186, 1665, and associated email.
            msg = "Didn't copy [%s] since none of its atoms were copied." % (self.name)
            env.history.message(orangemsg(msg))
        return False

    def will_partly_copy_due_to_selatoms(self, sel):
        """
        [overrides Node method]
        """
        return True # this is correct for jigs that say yes to jig.confers_properties_on(atom), and doesn't matter for others.

    def copy_full_in_mapping(self, mapping): #bruce 070430 revised to honor mapping.assy
        clas = self.__class__
        new = clas(mapping.assy, []) # don't pass any atoms yet (maybe not all of them are yet copied)
            # [Note: as of about 050526, passing atomlist of [] is permitted for motors, but they assert it's [].
            #  Before that, they didn't even accept the arg.]
        # Now, how to copy all the desired state? We could wait til fixup stage, then use mmp write/read methods!
        # But I'd rather do this cleanly and have the mmp methods use these, instead...
        # by declaring copyable attrs, or so.
        new._orig = self
        new._mapping = mapping
        new.name = "[being copied]" # should never be seen
        mapping.do_at_end( new._copy_fixup_at_end)
        #k any need to call mapping.record_copy??
        # [bruce comment 050704: if we could easily tell here that none of our atoms would get copied,
        #  and if self.needs_atoms_to_survive() is true, then we should return None (to fix bug 743) here;
        #  but since we can't easily tell that, we instead kill the copy
        #  in _copy_fixup_at_end if it has no atoms when that func is done.]
        return new

    def _copy_fixup_at_end(self): # warning [bruce 050704]: some of this code is copied in jig_Gamess.py's Gamess.cm_duplicate method.
        """
        [Private method]
        This runs at the end of a copy operation to copy attributes from the old jig
        (which could have been done at the start but might as well be done now for most of them)
        and copy atom refs (which has to be done now in case some atoms were not copied when the jig itself was).
        Self is the copy, self._orig is the original.
        """
        orig = self._orig
        del self._orig
        mapping = self._mapping
        del self._mapping
        copy = self
        orig.copy_copyable_attrs_to(copy) # replaces .name set by __init__
        self.own_mutable_copyable_attrs() # eliminate unwanted sharing of mutable copyable_attrs
        if orig.picked:
            # clean up weird color attribute situation (since copy is not picked)
            # by modifying color attrs as if we unpicked the copy
            self.color = self.normcolor
        nuats = []
        for atom in orig.atoms:
            nuat = mapping.mapper(atom)
            if nuat is not None:
                nuats.append(nuat)
        if len(nuats) < len(orig.atoms) and not self.name.endswith('-frag'): # similar code is in chunk, both need improving
            self.name += '-frag'
        if nuats or not self.needs_atoms_to_survive():
            self.setAtoms(nuats)
        else:
            #bruce 050704 to fix bug 743
            self.kill()
        #e jig classes with atom-specific info would have to do more now... we could call a 2nd method here...
        # or use list of classnames to search for more and more specific methods to call...
        # or just let subclasses extend this method in the usual way (maybe not doing those dels above).
        return
    
    # ==

    def _remove_all_atoms(self): #bruce 071010
        """
        Remove all of self's atoms, but don't kill self
        even if that would normally happen then.
        (For internal use, when new atoms are about to be added.)
        @see: L{self.setAtoms}
        """
        # TODO: could be optimized by inlining remove_atom
        for atom in list(self.atoms):
            self.remove_atom(atom, _kill_if_no_atoms_left_but_needs_them = False)
        return
    
    def remove_atom(self, atom, _kill_if_no_atoms_left_but_needs_them = True):
        """
        Remove atom from self, and remove self from atom
        [called from Atom.kill]

        Also kill self if it loses all its atoms but it needs them to survive,
        unless the private option to prevent that is passed.

        WARNING: extended by some subclasses to call Node.kill (not Jig.kill)
        on self.

        WARNING: extended by some subclasses to do invalidations
        on attrs of self that depend on the atoms list. TODO: A better way
        would be for this to call an optional _changed_atoms method on self.

        See also: methods self.moved_atom and self.changed_structure,
        which are passed an atom and tell us it changed in some way.

        See also: self._remove_all_atoms method
        """
        #bruce 071127 renamed this Jig API method, rematom -> remove_atom
        self.atoms.remove(atom)
        # also remove self from atom's list of jigs
        atom._f_jigs_remove(self,
                            changed_structure = self._affects_atom_structure )
        if _kill_if_no_atoms_left_but_needs_them:
            if not self.atoms and self.needs_atoms_to_survive():
                self.kill()
        return
    
    def kill(self):
        """
        [extends superclass method]
        """
        # bruce 050215 modified this to remove self from our atoms' jiglists, via remove_atom
        for atom in self.atoms[:]: #bruce 050316: copy the list (presumably a bugfix)
            self.remove_atom(atom) # the last one removed kills the jig recursively!
        _superclass.kill(self) # might happen twice, that's ok

    def destroy(self): #bruce 050718, for bonds code
        # not sure if this ever needs to differ from kill -- probably not; in fact, you should probably override kill, not destroy
        self.kill()

    # bruce 050125 centralized pick and unpick (they were identical on all Jig
    # subclasses -- with identical bugs!), added comments; didn't yet fix the bugs.
    #bruce 050131 for Alpha: more changes to it (still needs review after Alpha is out)
    
    def pick(self): 
        """
        select the Jig

        [extends superclass method]
        """
        from utilities.debug_prefs import debug_pref_History_print_every_selected_object
        if debug_pref_History_print_every_selected_object(): #bruce 070504 added this condition
            env.history.message(self.getinfo())
                #bruce 050901 revised this; now done even if jig is killed (might affect fixed bug 451-9)
        if not self.picked:
            _superclass.pick(self)
            self.normcolor = self.color # bug if this is done twice in a row! [bruce 050131 maybe fixed now due to the 'if']
            self.color = env.prefs[selectionColor_prefs_key] # russ 080603: pref.
        return

    def unpick(self):
        """
        unselect the Jig

        [extends superclass method]
        """
        if self.picked:
            _superclass.unpick(self) # bruce 050126 -- required now
            self.color = self.normcolor # see also a copy method which has to use the same statement to compensate for this kluge

    def rot(self, quat):
        pass

    def moved_atom(self, atom): #bruce 050718, for bonds code
        """
        FYI (caller is saying to this jig),
        we have just changed atom.posn() for one of your atoms.
        [Subclasses should override this as needed.]
        """
        pass

    def changed_structure(self, atom): #bruce 050718, for bonds code
        """
        FYI (caller is saying to this jig),
        we have just changed the element, atomtype, or bonds for one of your atoms.
        [Subclasses should override this as needed.]
        """
        pass
    
    def break_interpart_bonds(self): #bruce 050316 fix the jig analog of bug 371; 050421 undo that change for Alpha5 (see below)
        """
        [overrides Node method]
        """
        #e this should be a "last resort", i.e. it's often better if interpart bonds
        # could split the jig in two, or pull it into a new Part.
        # But that's NIM (as of 050316) so this is needed to prevent some old bugs.
        #bruce 050421 for Alpha5 decided to permit all Jig-atom interpart bonds, but just let them
        # make the Jig disabled. That way you can drag Jigs out and back into a Part w/o losing their atoms.
        # (And we avoid bugs from removing Jigs and perhaps their clipboard-item Parts at inconvenient times.)
        #bruce 050513 as long as the following code does nothing, let's speed it up ("is not") and also comment it out.
##        for atom in self.atoms[:]:
##            if self.part is not atom.molecule.part and 0: ###@@@ try out not doing this; jigs will draw and save inappropriately at first...
##                self.remove_atom(atom) # this might kill self, if we remove them all
        return

    def anchors_atom(self, atom): #bruce 050321, renamed 050404
        """
        does this jig hold this atom fixed in space?
        [should be overridden by subclasses as needed, but only Anchor needs to]
        """
        return False # for most jigs

    def node_must_follow_what_nodes(self): #bruce 050422 made Node and Jig implems of this from function of same name
        """
        [overrides Node method]
        """
        mols = {} # maps id(mol) to mol [bruce 050422 optim: use dict, not list]
        for atom in self.atoms:
            mol = atom.molecule
            if id(mol) not in mols:
                mols[id(mol)] = mol
        return mols.values()

    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        """
        [extends Node.writemmp; could be overridden by Jig subclasses, but isn't (as of 050322)]
        """
        #bruce 050322 made this from old Node.writemmp, but replaced nonstandard use of __repr__
        line, wroteleaf = self.mmp_record(mapping) # includes '\n' at end
        if line:
            mapping.write(line)
            if wroteleaf:
                self.writemmp_info_leaf(mapping)
                # only in this case, since other case means no node was actually written [bruce 050421]
        else:
            _superclass.writemmp(self, mapping) # just writes comment into file and atom_debug msg onto stdout
        return
    
    def writemmp_info_leaf(self, mapping): #bruce 051102
        """
        [extends superclass method]
        """
        _superclass.writemmp_info_leaf(self, mapping)
        if self.enable_minimize:
            mapping.write("info leaf enable_in_minimize = True\n") #bruce 051102
        if not self.dampers_enabled:
            mapping.write("info leaf dampers_enabled = False\n") #bruce 060421
        return

    def readmmp_info_leaf_setitem( self, key, val, interp ): #bruce 051102
        """
        [extends superclass method]
        """
        if key == ['enable_in_minimize']:
            # val should be "True" or "False" (unrecognized vals are treated as False)
            val = (val == 'True')
            self.enable_minimize = val
        elif key == ['dampers_enabled']:
            # val should be "True" or "False" (unrecognized vals are treated as True)
            val = (val != 'False')
            self.dampers_enabled = val
        else:
            _superclass.readmmp_info_leaf_setitem( self, key, val, interp)
        return
    
    def _mmp_record_front_part(self, mapping):
        # [Huaicai 9/21/05: split mmp_record into front-middle-last 3 parts, so each part can be different for a different jig.
        if mapping is not None:
            name = mapping.encode_name(self.name) #bruce 050729 help fix some Jig.__repr__ tracebacks (e.g. part of bug 792-1)
        else:
            name = self.name
        
        if self.picked:
            c = self.normcolor
            # [bruce 050422 comment: this code looks weird, but i guess it undoes pick effect on color]
        else:
            c = self.color
        color = map(int, A(c)*255)
        mmprectype_name_color = "%s (%s) (%d, %d, %d)" % (self.mmp_record_name, name,
                                                               color[0], color[1], color[2])
        return mmprectype_name_color
    
    def _mmp_record_last_part(self, mapping):
        """
        Last part of the mmp record. By default, this lists self's atoms,
        encoded by mapping. In some cases it lists a subset of self's atoms.

        Subclass can override this method if needed.
        As of long before 080317, some subclasses do that to work around bugs
        or kluges in class Jig methods which cause problems when they have
        no atoms.
        
        @note: If this returns anything other than empty, make sure to put
               one extra space character at the front. [As of long before 080317,
               it is likely that this is done by caller and therefore
               no longer needed in this method. ###review]
        """
        #Huaicai 9/21/05: split this from mmp_record, so the last part
        # can be different for a jig like ESP Image, which has no atoms.
        if mapping is not None:
            ndix = mapping.atnums
            minflag = mapping.min # writing this record for Minimize? [bruce 051031]
        else:
            ndix = None
            minflag = False
        nums = self.atnums_or_None( ndix, return_partial_list = minflag )
        assert nums is not None # bruce 080317
            # caller must ensure this by calling this with mapping.min set
            # or when all atoms are encodable. [bruce comment 080317]
        
        return " " + " ".join(map(str, nums))
        
    def mmp_record(self, mapping = None): 
        #bruce 050422 factored this out of all the existing Jig subclasses, changed arg from ndix to mapping
        #e could factor some code from here into mapping methods
        #bruce 050718 made this check for mapping is not None (2 places), as a bugfix in __repr__
        #bruce 051031 revised forward ref code, used mapping.min
        """
        Returns a pair (line, wroteleaf)
        where line is the standard MMP record for any jig
        (one string containing one or more lines including their \ns):
            jigtype (name) (r, g, b) ... [atnums-list]\n
        where ... is defined by a jig-specific submethod,
        and (as a special kluge) might contain \n and start
        another mmp record to hold the atnums-list!
        And, where wroteleaf is True iff this line creates a leaf node (susceptible to "info leaf") when read.
           Warning: the mmp file parser for most jigs cares that the data fields are separated
        by exactly one blank space. Using two spaces makes it fail!
           If mapping is supplied, then mapping.ndix maps atom keys to atom numbers (atnums)
        for use only in this writemmp event; if not supplied, just use atom keys as atnums,
        since we're being called by Jig.__repr__.
           [Subclasses could override this to return their mmp record,
        which must consist of 1 or more lines (all in one string which we return) each ending in '\n',
        including the last line; or return None to force caller to use some default value;
        but they shouldn't, because we've pulled all the common code for Jigs into here,
        so all they need to override is mmp_record_jigspecific_midpart.]
        """
        if mapping is not None:
            ndix = mapping.atnums				           
            name = mapping.encode_name(self.name)
            # flags related to what we can do about atoms on this jig which have no encoding in mapping
            permit_fwd_ref = not mapping.min #bruce 051031 (kluge, mapping should say this more directly)
            permit_missing_jig_atoms = mapping.min #bruce 051031 (ditto on kluge)
            assert not (permit_fwd_ref and permit_missing_jig_atoms) # otherwise wouldn't know which one to do with missing atoms!
        else:
            ndix = None	
            name = self.name
            permit_fwd_ref = False #bruce 051031
            permit_missing_jig_atoms = False # guess [bruce 051031]

        want_fwd_ref = False # might be modified below
        if mapping is not None and mapping.not_yet_past_where_sim_stops_reading_the_file() and self.is_disabled():
            # forward ref needed due to self being disabled
            if permit_fwd_ref:
                want_fwd_ref = True
            else:
                return "# disabled jig skipped for minimize\n", False
        else:
            # see if forward ref needed due to not all atoms being written yet
            if permit_fwd_ref: # assume this means that missing atoms should result in a forward ref
                nums = self.atnums_or_None( ndix)
                    # nums is used only to see if all atoms have yet been written, so we never pass return_partial_list flag to it
                want_fwd_ref = (nums is None)
                del nums
            else:
                pass # just let missing atoms not get written
        del ndix
        
        if want_fwd_ref:
            assert mapping # implied by above code
            # We need to return a forward ref record now, and set up mapping object to write us out for real, later.
            # This means figuring out when to write us... and rather than ask atnums_or_None for more help on that,
            # we use a variant of the code that used to actually move us before writing the file (since that's easiest for now).
            # But at least we can get mapping to do most of the work for us, if we tell it which nodes we need to come after,
            # and whether we insist on being invisible to the simulator even if we don't have to be
            # (since all our atoms are visible to it).
            ref_id = mapping.node_ref_id(self) #e should this only be known to a mapping method which gives us the fwdref record??
            mmprectype_name = "%s (%s)" % (self.mmp_record_name, name)
            fwd_ref_to_return_now = "forward_ref (%s) # %s\n" % (str(ref_id), mmprectype_name) # the stuff after '#' is just a comment
            after_these = self.node_must_follow_what_nodes()
            assert after_these # but this alone does not assert that they
                # weren't all already written out! The next method should
                # do that. [### need to assert they are not killed??]
            mapping.write_forwarded_node_after_nodes( self, after_these, force_disabled_for_sim = self.is_disabled() )
            return fwd_ref_to_return_now , False
        
        frontpart = self._mmp_record_front_part(mapping)
        midpart = self.mmp_record_jigspecific_midpart()
        lastpart = self._mmp_record_last_part(mapping) # note: this also calls atnums_or_None

        if lastpart == " ": # bruce 051102 for "enable in minimize"
            # kluge! should return a flag instead.
            # this happens during "minimize selection" if a jig is enabled
            # for minimize but none of its atoms are being minimized.
            if not self.atoms:
                #bruce 080317 add this case as a bugfix;
                # this might mean some of the existing subclass overrides of
                # _mmp_record_last_part are no longer needed (###review).
                # KLUGE, to work around older kluge which was causing bugs:
                # this value of lastpart is normal in this case.
                # But warn in the file if this looks like a bug.
                if self.needs_atoms_to_survive():
                    # untested?
                    print "bug? %r being written with no atoms, but needs them" % self
                    lastpart += "# bug? no atoms, but needs them"
                # now use lastpart in return value as usual
                pass
            else:
                # (before bruce 080317 bugfix, this was what we did
                #  even when not self.atoms)
                # return a comment instead of the entire mmp record:
                return "# jig with no selected atoms skipped for minimize\n", False
            pass
        
        return frontpart + midpart + lastpart + "\n" , True

    def mmp_record_jigspecific_midpart(self):
        """
        #doc
        (see rmotor's version's docstring for details)
        [some subclasses need to override this]
        Note: If it returns anything other than empty, make sure add one more extra 'space' at the front.
        """
        return ""

    # Added "return_partial_list" after a discussion with Bruce about "enable in minimize" jigs.
    # This would allow a partial atom list to be returned.
    # [Mark 051006 defined return_partial_list API; bruce 051031 revised docstring and added implem,
    #  here and in one subclass.]
    def atnums_or_None(self, ndix, return_partial_list = False):
        """
        Return list of atnums to write, as ints(??) (using ndix to encode them),
        or None if some atoms were not yet written to the file and return_partial_list is False.
        (If return_partial_list is True, then missing atoms are just left out of the returned list.
        Callers should check whether the resulting list is [] if that matters.)
        (If ndix not supplied, as when we're called by __repr__, use atom keys for atnums;
        return_partial_list doesn't matter in this case since all atoms have keys.)
        [Jig method; overridden by some subclasses]
        """
        res = []
        for atom in self.atoms:
            key = atom.key
            if ndix:
                code = ndix.get(key, None) # None means don't add it, and sometimes also means return early
                if code is None and not return_partial_list:
                    # typical situation (as we're called as of 051031):
                    # too soon to write this jig -- would require forward ref to an atom, which mmp format doesn't support
                    return None
                if code is not None:
                    res.append(code)
            else:
                res.append(key)
        return res

    def __repr__(self): #bruce 050322 compatibility method, probably not needed, but affects debugging
        try:
            line, wroteleaf = None, None # for debug print, in case not assigned
            line, wroteleaf = self.mmp_record()
            assert wroteleaf
            # BTW, is wroteleaf false for jigs whose mmp line is a comment? Does it need to be? [bruce 071205 Q]
        except: #bruce 050422
            msg = "bug in Jig.__repr__ call of self.mmp_record() ignored, " \
                  "which returned (%r, %r)" % (line, wroteleaf)
            print_compact_traceback( msg + ": " )
            line = None
        if line:
            return line
                # review: is this precise retval still required
                # by mmp writing code? I hope not... if not, change it
                # to be a better version of __repr__. [bruce 071205 comment]
        else:
            return "<%s at %#x>" % (self.__class__.__name__, id(self))
        pass

    def is_disabled(self): #bruce 050421 experiment related to bug 451-9
        """
        [overrides Node method]
        """
        return self.disabled_by_user_choice or self.disabled_by_atoms()

    def disabled_by_atoms(self): #e rename?
        """
        is this jig necessarily disabled (due to some atoms being in a different part)?
        """
        part = self.part
        for atom in self.atoms:
            if part is not atom.molecule.part:
                return True # disabled (or partly disabled??) due to some atoms not being in the same Part
                #e We might want to loosen this for an Anchor/Ground (and only disable the atoms in a different Part),
                # but for initial bugfixing, let's treat all atoms the same for all jigs and see how that works.
        return False

    def getinfo(self): #bruce 050421 added this wrapper method and renamed the subclass methods it calls.
        sub = self._getinfo()
        disablers = []
        if self.disabled_by_user_choice:
            disablers.append("by choice")
        if self.disabled_by_atoms():
            if self.part.topnode is self.assy.tree:
                why = "some atoms on clipboard"
            else:
                why = "some atoms in a different Part"
            disablers.append(why)
        if len(disablers) == 2:
            why = disablers[0] + ", and by " + disablers[1]
        elif len(disablers) == 1:
            why = disablers[0]
        else:
            assert not disablers
            why = ""
        if why:
            sub += " [DISABLED (%s)]" % why
        return sub

    def _getinfo(self):#ninad060825
        """
        Return a string for display in history or Properties
        [subclasses should override this]
        """
        return "[%s: %s]" % (self.sym, self.name)
    
    def getToolTipInfo(self):
        """
        public method that returns a string for display in Dynamic Tool tip
        """
        return self._getToolTipInfo() 
            
    def _getToolTipInfo(self):
        """
        Return a string for display in Dynamic Tool tip
        [subclasses should override this]
        """
        return "%s <br><font color=\"#0000FF\"> Jig Type:</font> %s" % (self.name, self.sym)
        
    def draw(self, glpane, dispdef): #bruce 050421 added this wrapper method and renamed the subclass methods it calls. ###@@@writepov too
        if self.hidden:
            return
        disabled = self.is_disabled()
        if disabled:
            # use dashed line (see drawer.py's drawline for related code)
            glLineStipple(1, 0xE3C7) # 0xAAAA dots are too small; 0x3F07 assymetrical; try dashes len 4,6, gaps len 3, start mid-6
            glEnable(GL_LINE_STIPPLE)
            # and display polys as their edges (see drawer.py's drawwirecube for related code)
            glPolygonMode(GL_FRONT, GL_LINE)
            glPolygonMode(GL_BACK, GL_LINE)
            glDisable(GL_LIGHTING)
            glDisable(GL_CULL_FACE) # this makes motors look too busy, but without it, they look too weird (which seems worse)

        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing Jig %r: " % self)
        else:
            glPopName()
            
        if disabled:
            glEnable(GL_CULL_FACE)
            glEnable(GL_LIGHTING)
            glPolygonMode(GL_FRONT, GL_FILL)
            glPolygonMode(GL_BACK, GL_FILL) #bruce 050729 precaution related to bug 835; could probably use GL_FRONT_AND_BACK
            glDisable(GL_LINE_STIPPLE)
        return
    
    def edit(self): #bruce 050526 moved this from each subclass into Jig, and let it handle missing cntl
        if self.cntl is None:
            #bruce 050526: had to defer this until first needed, so I can let some jigs temporarily be in a state
            # where it doesn't work, during copy. (The Stat & Thermo controls need the jig to have an atom during their init.)
            self.set_cntl()
            assert self.cntl is not None
        if self is self.assy.o.selobj:
            self.assy.o.selobj = None
            # If the Properties dialog was selected from the GLPane's context
            # menu, selobj will typically be self and the jig will appear
            # highlighted. That is inconvenient if we want to change its color
            # from the Properties dialog, since we can't see the color we're
            # changing, either before or after we change it. So reset selobj
            # to None here to avoid this problem.
            # [mark 060312 revision; comment rewritten by bruce 090106]
        self.cntl.setup()
        self.cntl.exec_()
        
    def toggleJigDisabled(self):
        """
        Enable/Disable jig.
        """
        # this is wrong, doesn't do self.changed():
        ## self.disabled_by_user_choice = not self.disabled_by_user_choice
        self.set_disabled_by_user_choice( not self.disabled_by_user_choice )
            #bruce 060313 use correct call, to fix bug 1671 (and related unreported bugs)
        if self is self.assy.o.selobj:
            # Without this, self will remain highlighted until the mouse moves.
            self.assy.o.selobj = None ###e shouldn't we use set_selobj instead?? [bruce 060726 question]
        self.assy.w.win_update()
        
    def mouseover_statusbar_message(self): # Fixes bug 1642. mark 060312
        return self.name
        
    def make_selobj_cmenu_items(self, menu_spec):
        """
        Add jig specific context menu items to <menu_spec> list when self is the selobj.
        This method should be overridden by subclasses that want to add more/different
        menu items. For a good example, see the Motor.make_selobj_cmenu_items().
        """
        item = ('Hide', self.Hide)
        menu_spec.append(item)
        if self.disabled_by_user_choice:
            item = ('Disabled', self.toggleJigDisabled, 'checked')
        else:
            item = ('Disable', self.toggleJigDisabled, 'unchecked')
        menu_spec.append(item)
        menu_spec.append(None) # Separator
        item = ('Edit Properties...', self.edit)
        menu_spec.append(item)

    def nodes_containing_selobj(self): #bruce 080507
        """
        @see: interface class Selobj_API for documentation
        """
        # safety check in case of calls on out of date selobj:
        if self.killed():
            return []
        return self.containing_nodes()

    #e there might be other common methods to pull into here

    pass # end of class Jig

# == Anchor (was Ground)

class Anchor(Jig):
    """
    an Anchor (Ground) just has a list of atoms that are anchored in space
    """
    sym = "Anchor"
    icon_names = ["modeltree/anchor.png", "modeltree/anchor-hide.png"]
    featurename = "Anchor" # wiki help featurename [bruce 051201; note that for a few jigs this should end in "Jig"]
    
    # create a blank Anchor with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        # set default color of new anchor to black
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.

    def set_cntl(self): #bruce 050526 split this out of __init__ (in all Jig subclasses)
        # Changed from GroundProp to more general JigProp, which can be used for any simple jig
        # that has only a name and a color attribute changable by the user. JigProp supersedes GroundProp.
        # Mark 050928.
        from command_support.JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)
            
    # Write "anchor" record to POV-Ray file in the format:
    # anchor(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden:
            return
        if self.is_disabled():
            return
        if self.picked:
            c = self.normcolor
        else:
            c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            grec = "anchor(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(grec)

    def _getinfo(self):
        return "[Object: Anchor] [Name: " + str(self.name) + "] [Total Anchors: " + str(len(self.atoms)) + "]"
                    
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        attachedAtomCount = "<font color=\"#0000FF\"> Total Anchors:</font> %d "%(len(self.atoms))
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Anchor"\
        + "<br>"  + str(attachedAtomCount)

    def getstatistics(self, stats):
        stats.nanchors += len(self.atoms)

    mmp_record_name = "ground" # Will change to "anchor" for A7.  Mark 051104.
    def mmp_record_jigspecific_midpart(self): # see also fake_Anchor_mmp_record [bruce 050404]
        return ""

    def anchors_atom(self, atom): #bruce 050321; revised 050423 (warning: quadratic time for large anchor jigs in Minimize)
        """
        does this jig hold this atom fixed in space? [overrides Jig method]
        """
        return (atom in self.atoms) and not self.is_disabled()

    def confers_properties_on(self, atom): # Anchor method
        """
        [overrides Node method]
        Should this jig be partly copied (even if not selected)
        when this atom is individually selected and copied?
        (It's ok to assume without checking that atom is one of this jig's atoms.)
        """
        return True
    
    pass # end of class Anchor

def fake_Anchor_mmp_record(atoms, mapping): #bruce 050404 utility for Minimize Selection
    """
    Return an mmp record (one or more lines with \n at end)
    for a fake Anchor (Ground) jig for use in an mmp file meant only for simulator input.

    @note: unlike creating and writing out a new real Anchor (Ground) object,
    which adds itself to each involved atom's .jigs list (perhaps just temporarily),
    perhaps causing unwanted side effects (like calling some .changed() method),
    this function has no side effects.
    """
    ndix = mapping.atnums
    c = black
    color = map(int,A(c)*255)
    # Change to "anchor" for A7.  Mark 051104.
    s = "ground (%s) (%d, %d, %d) " % ("name", color[0], color[1], color[2])
    nums = map((lambda a: ndix[a.key]), atoms)
    return s + " ".join(map(str,nums)) + "\n"

# == Stat and Thermo

class Jig_onChunk_by1atom(Jig):
    """
    Subclass for Stat and Thermo, which are on one atom in cad code,
    but on its whole chunk in simulator,
    by means of being written into mmp file as the min and max atnums in that chunk
    (whose atoms always occupy a contiguous range of atnums, since those are remade per writemmp event),
    plus the atnum of their one user-visible atom.
    """
    def setAtoms(self, atomlist):
        """
        [Overrides Jig method; called by Jig.__init__]
        """
        # old comment:
        # ideally len(list) should be 1, but in case code in files_mmp uses more
        # when supporting old Stat records, all I assert here is that it's at
        # least 1, but I only store the first atom [bruce 050210]
        # addendum, bruce 050526: can't assert that anymore due to copying code for this jig.
        ## assert len(atomlist) >= 1
        atomlist = atomlist[0:1] # store at most one atom
        super = Jig
        super.setAtoms(self, atomlist)
        
    def atnums_or_None(self, ndix, return_partial_list = False): #bruce 051031 added return_partial_list implem
        """
        return list of atnums to write, or None if some atoms not yet written
        [overrides Jig method]
        """
        assert len(self.atoms) == 1
        atom = self.atoms[0]
        if ndix:
            # for mmp file -- return numbers of first, last, and defining atom
            atomkeys = [atom.key] + atom.molecule.atoms.keys() # arbitrary order except first list element
                # first key occurs twice, that's ok (but that it's first matters)
                # (this is just a kluge so we don't have to process it thru ndix separately)
            try:
                nums = map((lambda ak: ndix[ak]), atomkeys)
            except KeyError:
                # too soon to write this jig -- would require forward ref to an atom, which mmp format doesn't support
                if return_partial_list:
                    return [] # kluge; should be safe since chunk atoms are written all at once [bruce 051031]
                return None
            nums = [min(nums), max(nums), nums[0]] # assumes ndix contains numbers, not number-strings [bruce 051031 comment]
        else:
            # for __repr__ -- in this case include only our defining atom, and return key rather than atnum
            nums = map((lambda a: a.key), self.atoms)
        return nums
    pass
    
class Stat( Jig_onChunk_by1atom ):
    """
    A Stat is a Langevin thermostat, which sets a chunk to a specific
    temperature during a simulation. A Stat is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms:
    - first_atom: the first atom of the chunk to which it is attached.
    - last_atom: the last atom of the chunk to which it is attached.
    - boxed_atom: the atom in the chunk the user selected. A box is drawn
    around this atom.
       Note that the simulator applies the Stat to all atoms in the entire chunk
    to which it is attached, but in case of merging or joining chunks, the atoms
    in this chunk might be different each time the mmp file is written; even
    the atom order in one chunk might vary, so the first and last atoms can be
    different even when the set of atoms in the chunk has not changed.
    Only the boxed_atom is constant (and only it is saved, as self.atoms[0]).
    """
    #bruce 050210 for Alpha-2: fix bug in Stat record reported by Josh to ne1-users    
    sym = "Stat"
    icon_names = ["modeltree/Thermostat.png", "modeltree/Thermostat-hide.png"]
    featurename = "Thermostat" #bruce 051203

    copyable_attrs = Jig_onChunk_by1atom.copyable_attrs + ('temp',)
    
    # create a blank Stat with the given list of atoms, set to 300K
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list) # note: this calls Jig_onChunk_by1atom.setAtoms method
        # set default color of new stat to blue
        self.color = blue # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = blue # This is the normal (unselected) color.
        self.temp = 300

    def set_cntl(self): #bruce 050526 split this out of __init__ (in all Jig subclasses)
        self.cntl = StatProp(self, self.assy.o)
        ## self.cntl = None #bruce 050526 do this later since it needs at least one atom to be present
            
    # Write "stat" record to POV-Ray file in the format:
    # stat(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden:
            return
        if self.is_disabled():
            return
        if self.picked:
            c = self.normcolor
        else:
            c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            srec = "stat(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(srec)

    def _getinfo(self):
        return  "[Object: Thermostat] "\
                    "[Name: " + str(self.name) + "] "\
                    "[Temp = " + str(self.temp) + "K]" + "] "\
                    "[Attached to: " + str(self.atoms[0].molecule.name) + "] "
                                        
    def _getToolTipInfo(self): #ninad060825
        "Return a string for display in Dynamic Tool tip "
        #ninad060825 We know that stat has only one atom  May be we should use try - except to be safer?
        attachedChunkInfo = ("<font color=\"#0000FF\">Attached to chunk </font>[%s]") %(self.atoms[0].molecule.name) 
        
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Thermostat"\
        + "<br>"  + "<font color=\"#0000FF\"> Temperature:</font>" + str(self.temp) + " K"\
        + "<br>" + str(attachedChunkInfo)

    def getstatistics(self, stats):
        stats.nstats += len(self.atoms)

    mmp_record_name = "stat"
    def mmp_record_jigspecific_midpart(self):
        return " " + "(%d)" % int(self.temp)

    pass # end of class Stat


# == Thermo

class Thermo(Jig_onChunk_by1atom):
    """
    A Thermo is a thermometer which measures the temperature of a chunk
    during a simulation. A Thermo is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms and applies to all
    atoms in the same chunk; for details see Stat docstring.
    """
    #bruce 050210 for Alpha-2: fixed same bug as in Stat.
    sym = "Thermo"
    icon_names = ["modeltree/Thermometer.png", "modeltree/Thermometer-hide.png"]
    featurename = "Thermometer" #bruce 051203

    # creates a thermometer for a specific atom. "list" contains only one atom.
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list) # note: this calls Jig_onChunk_by1atom.setAtoms method
        # set default color of new thermo to dark red
        self.color = darkred # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = darkred # This is the normal (unselected) color.

    def set_cntl(self): #bruce 050526 split this out of __init__ (in all Jig subclasses)
        self.cntl = ThermoProp(self, self.assy.o)
            
    # Write "thermo" record to POV-Ray file in the format:
    # thermo(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden:
            return
        if self.is_disabled():
            return
        if self.picked:
            c = self.normcolor
        else:
            c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            srec = "thermo(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(srec)

    def _getinfo(self):
        return  "[Object: Thermometer] "\
                    "[Name: " + str(self.name) + "] "\
                    "[Attached to: " + str(self.atoms[0].molecule.name) + "] "
                    
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        attachedChunkInfo = ("<font color=\"#0000FF\">Attached to chunk </font>[%s]") %(self.atoms[0].molecule.name)
            #ninad060825 We know that stat has only one atom... Maybe we should use try/except to be safer?
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Thermometer"\
        + "<br>" + str(attachedChunkInfo)

    def getstatistics(self, stats):
        stats.nthermos += len(self.atoms)

    mmp_record_name = "thermo"
    def mmp_record_jigspecific_midpart(self):
        return ""
    
    pass # end of class Thermo


# == AtomSet

class AtomSet(Jig):
    """
    An Atom Set just has a list of atoms that can be easily selected by the user.
    """
    sym = "AtomSet" # Was "Atom Set" (removed space). Mark 2007-05-28
    icon_names = ["modeltree/Atom_Set.png", "modeltree/Atom_Set-hide.png"]
    featurename = "Atom Set" #bruce 051203

    # create a blank AtomSet with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        # set default color of new set atom to black
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.

    def set_cntl(self):
        # Fixed bug 1011.  Mark 050927.
        from command_support.JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

    # it's drawn as a wire cube around each atom (default color = black)
    def _draw(self, glpane, dispdef):
        """
        Draws a red wire frame cube around each atom, only if the jig is select.
        """
        if not self.picked:
            return
            
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
        
    def _getinfo(self):
        return "[Object: Atom Set] [Name: " + str(self.name) + "] [Total Atoms: " + str(len(self.atoms)) + "]"
                    
    def _getToolTipInfo(self): #ninad060825
        """
        Return a string for display in Dynamic Tool tip
        """
        attachedAtomCount ="<font color=\"#0000FF\">Total  Atoms: </font>%d"%(len(self.atoms))
        return str(self.name) + "<br>" +  "<font color=\"#0000FF\"> Jig Type:</font>Atom Set"\
        + "<br>"  + str(attachedAtomCount)

    def getstatistics(self, stats):
        stats.natoms += 1 # Count only the atom set itself, not the number of atoms in the set.

    mmp_record_name = "atomset"
    def mmp_record_jigspecific_midpart(self):
        return ""
        
    pass # end of class AtomSet

# end
