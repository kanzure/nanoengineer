# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_select.py -- operations and internal methods for changing what's selected
and maintaining other selection-related state. (Not well-organized.)

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.
"""

from assembly import SELWHAT_CHUNKS, SELWHAT_ATOMS
from elements import Singlet
from VQT import V, A, norm, cross, transpose, dot

class ops_select_Mixin:
    "Mixin class for providing these methods to class Part"

    # functions from the "Select" menu
    # [these are called to change the set of selected things in this part,
    #  when it's the current part; these are event handlers which should
    #  do necessary updates at the end, e.g. win_update, and should print
    #  history messages, etc]

    def selectAll(self):
        """Select all parts if nothing selected.
        If some parts are selected, select all atoms in those parts.
        If some atoms are selected, select all atoms in the parts
        in which some atoms are selected.
        [bruce 050201 observes that this docstring is wrong.]
        """ ###@@@
        if self.selwhat == SELWHAT_CHUNKS:
            for m in self.molecules:
                m.pick()
        else:
            assert self.selwhat == SELWHAT_ATOMS
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    a.pick()
        self.w.win_update()

    def selectNone(self):
        self.unpickatoms()
        self.unpickparts()
        self.w.win_update()

    def selectInvert(self):
        """If some parts are selected, select the other parts instead.
        If some atoms are selected, select the other atoms instead
        (even in chunks with no atoms selected, which end up with
        all atoms selected). (And unselect all currently selected
        parts or atoms.)
        """
        # revised by bruce 041217 after discussion with Josh;
        # previous version inverted selatoms only in chunks with
        # some selected atoms.
        if self.selwhat == SELWHAT_CHUNKS:
            newpicked = filter( lambda m: not m.picked, self.molecules )
            self.unpickparts()
            for m in newpicked:
                m.pick()
        else:
            assert self.selwhat == SELWHAT_ATOMS
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    if a.picked: a.unpick()
                    else: a.pick()
        self.w.win_update()

    ###@@@ what calls these? they do win_update but they don't change which select mode is in use.
    
    def selectAtoms(self):
        self.unpickparts()
        self.assy.selwhat = SELWHAT_ATOMS
        self.w.win_update()
        
    def selectParts(self):
        self.pickParts()
        self.w.win_update()

    def pickParts(self):
        self.assy.selwhat = SELWHAT_CHUNKS
        lis = self.selatoms.values()
        self.unpickatoms()
        for atm in lis:
            atm.molecule.pick()
        return
    
    # == selection functions using a mouse position
    ###@@@ move to glpane??
    
    # (Not toplevel event handlers ###k some aren't anyway)

    # dumb hack: find which atom the cursor is pointing at by
    # checking every atom...
    # [bruce 041214 comment: findpick is now mostly replaced by findAtomUnderMouse;
    #  its only remaining call is in depositMode.getcoords, which uses a constant
    #  radius other than the atoms' radii, and doesn't use iPic or iInv,
    #  but that too might be replaced in the near future, once bug 269 response
    #  is fully decided upon.
    #  Meanwhile, I'll make this one only notice visible atoms, and clean it up.
    #  BTW it's now the only caller of atom.checkpick().]
    
    def findpick(self, p1, v1, r=None):
        distance = 1000000
        atom = None
        for mol in self.molecules:
            if mol.hidden: continue
            disp = mol.get_dispdef()
            for a in mol.atoms.itervalues():
                if not a.visible(disp): continue
                dist = a.checkpick(p1, v1, disp, r, None)
                if dist:
                    if dist < distance:
                        distance = dist
                        atom = a
        return atom

    # bruce 041214, for fixing bug 235 and some unreported ones:
    def findAtomUnderMouse(self, event, water_cutoff = False, singlet_ok = False):
        """Return the atom (if any) whose front surface should be visible at the
        position of the given mouse event, or None if no atom is drawn there.
        This takes into account all known effects that affect drawing, except
        bonds and other non-atom things, which are treated as invisible.
        (Someday we'll fix this by switching to OpenGL-based hit-detection. #e)
           Note: if several atoms are drawn there, the correct one to return is
        the one that obscures the others at that exact point, which is not always
        the one whose center is closest to the screen!
           When water_cutoff is true, also return None if the atom you would
        otherwise return (more precisely, if the place its surface is touched by
        the mouse) is under the "water surface".
           Normally never return a singlet (though it does prevent returning
        whatever is behind it). Optional arg singlet_ok permits returning one.
        """
        p1, p2 = self.o.mousepoints(event, 0.0)
        z = norm(p1-p2)
        x = cross(self.o.up,z)
        y = cross(z,x)
        matrix = transpose(V(x,y,z))
        point = p2
        cutoffs = dot( A([p1,p2]) - point, matrix)[:,2]
        near_cutoff = cutoffs[0]
        if water_cutoff:
            far_cutoff = cutoffs[1]
            # note: this can be 0.0, which is false, so an expression like
            # (water_cutoff and cutoffs[1] or None) doesn't work!
        else:
            far_cutoff = None
        z_atom_pairs = []
        for mol in self.molecules:
            if mol.hidden: continue
            pairs = mol.findAtomUnderMouse(point, matrix, \
                far_cutoff = far_cutoff, near_cutoff = near_cutoff )
            z_atom_pairs.extend( pairs)
        if not z_atom_pairs:
            return None
        z_atom_pairs.sort() # smallest z == farthest first; we want nearest
        res = z_atom_pairs[-1][1] # nearest hit atom
        if res.element == Singlet and not singlet_ok:
            return None
        return res

    #bruce 041214 renamed and rewrote the following pick_event methods, as part of
    # fixing bug 235 (and perhaps some unreported bugs).
    # I renamed them to distinguish them from the many other "pick" (etc) methods
    # for Node subclasses, with common semantics different than these have.
    # I removed some no-longer-used related methods.
    
    def pick_at_event(self, event): #renamed from pick; modified
        """Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get selected,
        in addition to whatever already was selected.
        You are not allowed to select a singlet.
        Print a message about what you just selected (if it was an atom).
        """
        # [bruce 041227 moved the getinfo status messages here, from the atom
        # and molecule pick methods, since doing them there was too verbose
        # when many items were selected at the same time. Original message
        # code was by [mark 2004-10-14].]
        atm = self.findAtomUnderMouse(event)
        if atm:
            if self.selwhat == SELWHAT_CHUNKS:
                if not self.selmols:
                    self.selmols = []
                    # bruce 041214 added that, since pickpart used to do it and
                    # calls of that now come here; in theory it's never needed.
                atm.molecule.pick()
                self.w.history.message(atm.molecule.getinfo())
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.pick()
                self.w.history.message(atm.getinfo())
        return
    
    def onlypick_at_event(self, event): #renamed from onlypick; modified
        """Unselect everything in the glpane; then select whatever visible atom
        or chunk (depending on self.selwhat) is under the mouse at event.
        If no atom or chunk is under the mouse, nothing in glpane is selected.
        """
        if self.selwhat == SELWHAT_CHUNKS:
            self.unpickparts() # (fyi, this unpicks in clipboard as well)
        else:
            assert self.selwhat == SELWHAT_ATOMS
            self.unpickatoms()
        self.pick_at_event(event)
    
    def unpick_at_event(self, event): #renamed from unpick; modified
        """Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get un-selected,
        but don't change whatever else is selected.
        """
        atm = self.findAtomUnderMouse(event)
        if atm:
            if self.selwhat == SELWHAT_CHUNKS:
                atm.molecule.unpick()
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.unpick()
        return

    # == internal selection-related routines
    
    # deselect any selected atoms
    def unpickatoms(self):
        if self.selatoms:
            for a in self.selatoms.itervalues():
                # this inlines and optims atom.unpick
                a.picked = 0
                a.molecule.changeapp(1)
            self.selatoms = {}

    def permit_pick_parts(self): #bruce 050125
        "ensure it's legal to pick chunks"
        if self.assy.selwhat != SELWHAT_CHUNKS:
            self.unpickatoms()
            self.assy.selwhat = SELWHAT_CHUNKS
        return
    
    # deselect any selected molecules or groups
    def unpickparts(self):
        self.topnode.unpick()
        # before assy/part split, this was root, i.e. assy.tree and assy.shelf

    # ==
    
    def selection(self): #bruce 050404 experimental feature for initial use in Minimize Selection
        "return an object which represents the contents of the current selection, independently of part attrs... how long valid??"
        # the idea is that this is a snapshot of selection even if it changes
        # but it's not clear how valid it is after the part contents itself starts changing...
        # so don't worry about this yet, consider it part of the experiment...
        return Selection( self, self.selatoms, self.selmols )

    def selection_for_all(self): #bruce 050419 for use in Minimize All
        "return a selection object referring to all our atoms (regardless of the current selection, and not changing it)"
        return Selection( self, {}, self.molecules )

    pass # end of class ops_select_Mixin

# ==

class Selection: #bruce 050404 experimental feature for initial use in Minimize Selection
    def __init__(self, part, selatoms, selmols): #e revise init args
        self.part = part
        self.topnode = part.topnode # might change...
        self.selatoms = dict(selatoms) # copy the dict
        self.selmols = list(selmols) # copy the list
        assert not (self.selatoms and self.selmols) #e could this change? try not to depend on it
        #e jigs?
        return
    def nonempty(self): #e make this the object's boolean value too?
        # assume that each selmol has some real atoms, not just singlets! Should always be true.
        return self.selatoms or self.selmols
    def atomslist(self):
        "return a list of all selected real atoms, whether selected as atoms or in selected chunks; no singlets or jigs"
        #e memoize this!
        # [bruce 050419 comment: memoizing it might matter for correctness
        #  if mol contents change, not only for speed. But it's not yet needed,
        #  since in the only current use of this, the atomslist is grabbed once
        #  and stored elsewhere.]
        if self.selmols:
            res = dict(self.selatoms) # dict from atom keys to atoms
            for mol in self.selmols:
                # we'll add real atoms and singlets, then remove singlets
                # (probably faster than only adding real atoms, since .update is one bytecode
                #  and (for large mols) most atoms are not singlets)
                res.update(mol.atoms)
                for s in mol.singlets:
                    del res[s.key]
        else:
            res = self.selatoms
        items = res.items()
        items.sort() # sort by atom key; might not be needed
        return [atom for key, atom in items]
    pass # end of class Selection

# end
