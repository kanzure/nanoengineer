# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
ops_select.py -- operations and internal methods for changing what's selected
and maintaining other selection-related state. (Not well-organized.)

$Id$

History:

bruce 050507 made this by collecting appropriate methods from class Part.

bruce 050913 used env.history in some places.
"""

from assembly import SELWHAT_CHUNKS, SELWHAT_ATOMS
from elements import Singlet
from VQT import V, A, norm, cross, transpose, dot
import env
from constants import *
from HistoryWidget import redmsg, greenmsg, orangemsg

class ops_select_Mixin:
    "Mixin class for providing these methods to class Part"

    # functions from the "Select" menu
    # [these are called to change the set of selected things in this part,
    #  when it's the current part; these are event handlers which should
    #  do necessary updates at the end, e.g. win_update, and should print
    #  history messages, etc]

    def getSelectedJigs(self):
        '''Find all selected jigs in current part. Currently only 'RectGadget' is supported, but it expects
           to extend to other types of jigs in the near future.        [Huaicai 9/15/05]'''
        
        selJigs = []
        
        from jigs import RectGadget
        def addSelectedJig(obj, jigs=selJigs):
            if isinstance(obj, RectGadget): jigs += [obj]
        
        self.topnode.apply2picked(addSelectedJig)
        
        return selJigs

    
    def getMovables(self):
        '''Return the list of movable objects, currently including selected chunks and jigs.
        [Huaicai 9/16/05]'''
        return self.selmols + self.getSelectedJigs()    
    

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
        cmd = "Invert Selection: "
        env.history.message(greenmsg(cmd))
        
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
        
        # Print summary msg to history widget.  Always do this before win/gl_update.
        env.history.message("Selection Inverted")
        
        self.w.win_update()
        
    def selectExpand(self):
        """Select any atom that is bonded to any currently selected atom.
        """
        # Eric really needed this.  Added by Mark 050923.
        
        cmd = "Expand Selection: "
        env.history.message(greenmsg(cmd))
        
        if not self.selatoms:
            env.history.message(greenmsg(cmd) + redmsg("No atoms selected."))
            return
        
        num_picked = 0 # Number of atoms picked in the expand selection.
        
        for a in self.selatoms.values():
            if a.picked: 
                for n in a.neighbors():
                    if not n.picked:
                        n.pick()
                        num_picked += 1
        
        # Print summary msg to history widget.  Always do this before win/gl_update.
        from platform import fix_plurals
        msg = fix_plurals(str(num_picked) + " atom(s) selected.")
        env.history.message(msg)
        
        self.w.win_update()
        
    def selectContract(self):
        """Unselects any atom which has a bond to an unselected atom, or which has any open bonds.
        """
        # Added by Mark 050923.
        
        cmd = "Contract Selection: "
        env.history.message(greenmsg(cmd))
        
        if not self.selatoms:
            env.history.message(greenmsg(cmd) + redmsg("No atoms selected."))
            return
            
        contract_list = [] # Contains list of atoms to be unselected.
            
        assert self.selwhat == SELWHAT_ATOMS
        for a in self.selatoms.values():
            if a.picked: 
                # If a select atom has an unpicked neighbor, it gets added to the contract_list
                # Bruce mentions: you can just scan realNeighbors if you want to only scan
                # the non-singlet atoms. Users may desire this behavour - we can switch it on/off
                # via a dashboard checkbox or user pref if we want.  Mark 050923.
                for n in a.neighbors():
                    if not n.picked:
                        contract_list.append(a)
                        break
        
        # Unselect the atom in the contract_list
        for a in contract_list:
            a.unpick()
            
        # Print summary msg to history widget.  Always do this before win/gl_update.
        from platform import fix_plurals
        msg = fix_plurals(str(len(contract_list)) + " atom(s) unselected.")
        env.history.message(msg)
        
        self.w.win_update()
        
    # these next methods (selectAtoms and selectParts) are not for general use:
    # they do win_update but they don't change which select mode is in use.
    
    def selectAtoms(self):
        """change this Part's assy to permit selected atoms, not chunks;
        then win_update
        """
        # This is called only by selectAtomsMode.Enter.
        # (Does it actually need the update? I doubt it, I bet caller of Enter does it.)
        # BTW, MainWindow has unused slot with same name.
        # [bruce 050517 comment, and added docstring]
        self.permit_pick_atoms()
##        self.unpickparts()
##        self.assy.set_selwhat(SELWHAT_ATOMS) #bruce 050517 revised API of this call
        self.w.win_update()
        
    def selectParts(self):
        """change this Part's assy to permit selected chunks, not atoms,
        but select all chunks which contained selected atoms;
        then win_update
        """
        # This is called only by modifyMode.Enter.
        # (Why not selectChunksMode? because selectMolsMode calls it w/o update, instead:
        #   self.o.assy.pickParts() # josh 10/7 to avoid race in assy init
        # )
        # BTW, MainWindow has unused slot with same name.
        # [bruce 050517 comment, and added docstring]        
        self.pickParts()
        self.w.win_update()

    def pickParts(self): # see also permit_pick_parts
        """change this Part's assy to permit selected chunks, not atoms,
        but select all chunks which contained selected atoms; do no updates
        """
        #bruce 050517 added docstring
        lis = self.selatoms.values()
        self.unpickatoms()
        for atm in lis:
            atm.molecule.pick()
        self.assy.set_selwhat(SELWHAT_CHUNKS) #bruce 050517 revised API of this call
            #bruce 050517: do this at the end, to avoid worry about whether
            # it is later given the side effect of unpickatoms.
            # It's redundant only if lis has any atoms.
        return

    def permit_pick_parts(self): #bruce 050125; see also pickParts, but that can leave some chunks initially selected
        "ensure it's legal to pick chunks using mouse selection, and deselect any selected atoms (if picking chunks does so)"
        if self.assy.selwhat != SELWHAT_CHUNKS:
            self.unpickatoms()
            self.assy.set_selwhat(SELWHAT_CHUNKS) #bruce 050517 revised API of this call
        return

    def permit_pick_atoms(self): #bruce 050517 added this for use in some mode Enter methods -- but not sure they need it!
        "ensure it's legal to pick atoms using mouse selection, and deselect any selected chunks (if picking atoms does so)"
        ## if self.assy.selwhat != SELWHAT_ATOMS:
        if 1: # this matters, to callers who might have jigs selected
            self.unpickparts() # besides unpicking chunks, this also unpicks jigs and groups -- ok?
            self.assy.set_selwhat(SELWHAT_ATOMS) #bruce 050517 revised API of this call
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
                env.history.message(atm.molecule.getinfo())
            else:
                assert self.selwhat == SELWHAT_ATOMS
                atm.pick()
                env.history.message(atm.getinfo())
        
        # Added Chem3D selection behavour.  This code unselects everything
        # if no atom/chunk was selected.  Mark 050924.
        else: 
            if env.prefs[selectionBehavour_prefs_key] == CHEM3D:
                if self.selwhat == SELWHAT_CHUNKS:
                    self.unpickparts()
                else:
                    self.unpickatoms()
        return
    
    def onlypick_at_event(self, event): #renamed from onlypick; modified
        """Unselect everything in the glpane; then select whatever visible atom
        or chunk (depending on self.selwhat) is under the mouse at event.
        If no atom or chunk is under the mouse, nothing in glpane is selected.
        """
        if self.selwhat == SELWHAT_CHUNKS:
            self.unpickparts()
        else:
            assert self.selwhat == SELWHAT_ATOMS
            self.unpickparts() # Fixed bug 606, partial fix for bug 365.  Mark 050713.
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
    
    def unpickatoms(self):
        "Deselect any selected atoms (but don't change selwhat or do any updates)" #bruce 050517 added docstring
        if self.selatoms:
            for a in self.selatoms.itervalues():
                # this inlines and optims atom.unpick
                a.picked = 0
                a.molecule.changeapp(1)
            self.selatoms = {}
    
    def unpickparts(self):
        """Deselect any selected nodes (chunks, Jigs, Groups) in this part
        (but don't change selwhat or do any updates)
        """ #bruce 050517 added docstring
        self.topnode.unpick()
        # before assy/part split, this was done on assy.root, i.e. on assy.tree and assy.shelf

    # ==
    
    def selection_from_glpane(self): #bruce 050404 experimental feature for initial use in Minimize Selection; renamed 050523
        """Return an object which represents the contents of the current selection,
        independently of part attrs... how long valid?? Include the data generally used
        when doing an op on selection from glpane (atoms and chunks); see also selection_from_MT().
        """
        # the idea is that this is a snapshot of selection even if it changes
        # but it's not clear how valid it is after the part contents itself starts changing...
        # so don't worry about this yet, consider it part of the experiment...
        part = self
        return selection_from_glpane( part)

    def selection_for_all(self): #bruce 050419 for use in Minimize All; revised 050523
        "return a selection object referring to all our atoms (regardless of the current selection, and not changing it)"
        part = self
        return selection_for_entire_part( part)

    def selection_from_MT(self): #bruce 050523; might not yet be used
        "#doc"
        part = self
        return selection_from_MT( part)

    pass # end of class ops_select_Mixin (used in class Part)

# ==

def topmost_selected_nodes(nodes): #bruce 050523 split this out from the same-named TreeWidget method, and optimized it
    "return a list of all selected nodes (without looking inside selected Groups) in or under the given list of nodes"
    res = []
    func = res.append
    for node in nodes:
        node.apply2picked( func)
    return res

# ==

def selection_from_glpane( part): #bruce 050523 split this out as intermediate helper function; revised 050523
    return Selection( part, atoms = part.selatoms, chunks = part.selmols )

def selection_from_MT( part): #bruce 050523; might not yet be used
    return Selection( part, atoms = {}, nodes = topmost_selected_nodes([part.topnode]) )

def selection_from_part( part, use_selatoms = True): #bruce 050523
    if use_selatoms:
        atoms = part.selatoms
    else:
        atoms = {}
    return Selection( part, atoms = atoms, nodes = topmost_selected_nodes([part.topnode]) )

def selection_for_entire_part( part): #bruce 050523 split this out, revised it
    return Selection( part, atoms = {}, chunks = part.molecules )

class Selection: #bruce 050404 experimental feature for initial use in Minimize Selection; revised 050523
    """Represent a "snapshot-by-reference" of the contents of the current selection.
    Warning: this is valid if the selection-state changes
    but might become invalid if the Part contents themselves change in any way!
    """
    def __init__(self, part, atoms = {}, chunks = [], nodes = []):
        "Create a snapshot-by-reference of whatever objects are passed. Objects should not be passed redundantly."
        # note: topnodes might not always be provided;
        # when provided it should be a list of nodes in the part compatible with selmols
        # but containing groups and jigs as well as chunks, and not containing members of groups it contains
        # (those are implicit)
        self.part = part
        ## I don't think self.topnode is used or needed [bruce 050523]
        ## self.topnode = part.topnode # might change...
        self.selatoms = dict(atoms) # copy the dict; it's ok that this does not store atoms inside chunks or nodes
        # For now, we permit passing chunks or nodes list but not both.
        if nodes:
            # nodes were passed -- store them, but let selmols be computed lazily
            assert not chunks, "don't pass both chunks and nodes arguments to Selection"
            self.topnodes = list(nodes)
            # selmols will be computed lazily if needed
            # (to avoid needlessly computing it, we don't assert not (self.selatoms and self.selmols))
        else:
            # chunks (or no chunks and no nodes) were passed -- store as both selmols and topnodes
            self.selmols = list(chunks) # copy the list
            self.topnodes = self.selmols
            assert not (self.selatoms and self.selmols) #e could this change? try not to depend on it
        return
    def nonempty(self): #e make this the object's boolean value too?
        # assume that each selmol has some real atoms, not just singlets! Should always be true.
        return self.selatoms or self.topnodes #revised 050523
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
    def __getattr__(self, attr):
        if attr == 'selmols':
            # compute from self.topnodes -- can't assume selection state of self.part
            # is same as during our init, or even know whether it was relevant then.
            res = []
            from chunk import molecule
            def func(node):
                if isinstance(node, molecule):
                    res.append(node)
                return # from func
            for node in self.topnodes:
                node.apply2all(func)
            self.selmols = res
            return res
        elif attr == 'selmols_dict': #bruce 050526
            res = {}
            for mol in self.selmols:
                res[id(mol)] = mol
            self.selmols_dict = res
            return res
        raise AttributeError, attr
    def picks_atom(self, atom): #bruce 050526
        "Does this selection include atom, either directly or via its chunk?"
        return atom.key in self.selatoms or id(atom.molecule) in self.selmols_dict
    def describe_objects_for_history(self):
        """Return a string like "5 items" but more explicit if possible, for use in history messages"""
        from platform import fix_plurals
        if self.topnodes:
            res = fix_plurals( "%d item(s)" % len(self.topnodes) )
            #e could figure out their common class if any (esp. useful for Jig and below); for Groups say what they contain; etc
        elif self.selmols:
            res = fix_plurals( "%d chunk(s)" % len(self.selmols) )
        else:
            res = ""
        if self.selatoms:
            if res:
                res += " and "
            res += fix_plurals( "%d atom(s)" % len(self.selatoms) )
            #e could say "other atoms" if the selected nodes contain any atoms
        return res
    pass # end of class Selection

# end