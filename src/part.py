# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.

"""
part.py

Provides class Part, for all chunks and jigs in a single physical space,
together with their selection state and grouping structure (shown in the model tree).

TEMPORARILY OWNED BY BRUCE 050202 for the Part/assembly split ####@@@@

$Id$

see assembly.py docstring, some of which is really about this module. ###@@@ revise

==

This module also contains a lot of code for specific operations on sets of molecules,
which are all in the current part. Some of this code might ideally be moved to some
other file.

==

History: split out of assembly.py (the file, and more importantly the class)
by bruce 050222. The Part/assembly distinction was introduced by bruce 050222
(though some of its functionality was anticipated by the "current selection group"
introduced earlier, just before Alpha-1). [I also rewrote this entire docstring then.]

The Part/assembly distinction is unfinished, particularly in how it relates to some modes and to movie files.

Prior history of assembly.py (and thus of much code in this file) unclear;
assembly.py was almost certainly originated by Josh.

"""

###e imports

class Part:
    """
    One Part object is created to hold any set of chunks and jigs whose
    coordinates are intended to lie in the same physical space.
    When new clipboard items come into being, new Parts are created as needed
    to hold them; and they should be destroyed when those clipboard items
    no longer exist as such (even if the chunks inside them still exist in
    some other Part).
       Note that parts are not Nodes (or at least, they are not part of the same node-tree
    as the chunks/jigs they contain); each Part has a toplevel node self.tree,
    and a reference to the shared (per-assy) clipboard to use, self.shelf [###k].
    """

    def __init__(self, assy):
        self.assy = assy

        ###e need: tree, root(??)
        # _modified??
        # coord sys stuff? data? lastCsys homeCsys xy yz zx
        # name? no, at least not yet, until there's a Part Tree Widget.
        # filename? might need one for helping store associated files... could share assy.filename for now.
        
        ## moved from assy init, not yet edited for here; some of these will be inval/update vars ###@@@
        # list of chem.molecule's
        self.molecules=[]
        # list of the atoms, only valid just after read or write
        self.alist = [] #None
        # to be shrunk, see addmol
        self.bbox = BBox()
        self.center=V(0,0,0)
        # dictionary of selected atoms (indexed by atom.key)
        self.selatoms={}
        # list of selected molecules
        self.selmols=[]
        # level of detail to draw
        self.drawLevel = 2
        # the Movie object. ###@@@ might need revision for use in clipboard item parts... esp when it uses filename...
        self.m=Movie(self)
        # movie ID, for future use.
        self.movieID=0
        # ppa = previous picked atoms. ###@@@ not sure per-part; should reset when change mode or part
        self.ppa2 = self.ppa3 = None
        
        ### Some information needed for the simulation or coming from mmp file
        self.temperature = 300
        self.waals = None

        return # from Part.__init__

    # attrnames to delegate to self.assy (ideally for writing as well as reading, until all using-code is upgraded)
    assy_attrs = ['w','o','mt']
    assy_attrs_temporary = ['changed']
    assy_attrs_review = ['selwhat','shelf']
        #e in future, we'll split out our own methods for some of these, incl .changed
        #e and for others we'll edit our own methods' code to not call them on self but on self.assy (incl selwhat)
    assy_attrs_all = assy_attrs + assy_attrs_temporary + assy_attrs_review
    
    def __getattr__(self, attr):
        if attr.startswith('_'): # common case, be fast
            raise AttributeError, attr
        if attr in assy_attrs_all:
            # delegate to self.assy
            return getattr(self.assy, attr) ###@@@ detect error of infrecur, since assy getattr delegates to here??
        raise AttributeError, attr
    
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
        if self.selwhat:
            for m in self.molecules:
                m.pick()
        else:
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
        if self.selwhat:
            newpicked = filter( lambda m: not m.picked, self.molecules )
            self.unpickparts()
            for m in newpicked:
                m.pick()
        else:
            for m in self.molecules:
                for a in m.atoms.itervalues():
                    if a.picked: a.unpick()
                    else: a.pick()
        self.w.win_update()

    def selectConnected(self):
        """Select any atom that can be reached from any currently
        selected atom through a sequence of bonds.
        """ ###@@@ should make sure we don't traverse interspace bonds, until all bugs creating them are fixed
        if not self.selatoms:
            self.w.history.message(redmsg("Select Connected: No atom(s) selected."))
            return
        
        alreadySelected = len(self.selatoms.values())
        self.marksingle()
        self.w.history.message(greenmsg("Select Connected:"))
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d connected atom(s) selected." % totalSelected)
        
        if totalSelected > alreadySelected:
            ## Otherwise, that just means no new atoms selected, so no update necessary    
            #self.w.win_update()
            self.o.gl_update()
        
    def selectDoubly(self):
        """Select any atom that can be reached from any currently
        selected atom through two or more non-overlapping sequences of
        bonds. Also select atoms that are connected to this group by
        one bond and have no other bonds.
        """ ###@@@ same comment about interspace bonds as in selectConnected
        if not self.selatoms:
            self.w.history.message(redmsg("Select Doubly: No atom(s) selected."))
            return
            
        QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
        self.w.history.message(greenmsg("Select Doubly:"))
        
        self.w.history.message("Working.  Please wait...")
        alreadySelected = len(self.selatoms.values())
        self.markdouble()
        totalSelected = len(self.selatoms.values())
        self.w.history.message("%d doubly connected atom(s) selected." % totalSelected)
        
        QApplication.restoreOverrideCursor() # Restore the cursor
        
        if totalSelected > alreadySelected:
            ## otherwise, means nothing new selected. Am I right? ---Huaicai, not analyze the markdouble() algorithm yet 
            #self.w.win_update()
            self.o.gl_update()

    ###@@@ what calls these? they do win_update but they don't change which select mode is in use.
    
    def selectAtoms(self):
        self.unpickparts()
        self.selwhat = 0
        self.w.win_update()
            
    def selectParts(self):
        self.pickParts()
        self.w.win_update()

    def pickParts(self):
        self.selwhat = 2
        lis = self.selatoms.values()
        self.unpickatoms()
        for atm in lis:
            atm.molecule.pick()

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
            if self.selwhat:
                if not self.selmols:
                    self.selmols = []
                    # bruce 041214 added that, since pickpart used to do it and
                    # calls of that now come here; in theory it's never needed.
                atm.molecule.pick()
                self.w.history.message(atm.molecule.getinfo())
            else:
                atm.pick()
                self.w.history.message(atm.getinfo())
        return
    
    def onlypick_at_event(self, event): #renamed from onlypick; modified
        """Unselect everything in the glpane; then select whatever visible atom
        or chunk (depending on self.selwhat) is under the mouse at event.
        If no atom or chunk is under the mouse, nothing in glpane is selected.
        """
        if self.selwhat:
            self.unpickparts() # (fyi, this unpicks in clipboard as well)
        else:
            self.unpickatoms()
        self.pick_at_event(event)
    
    def unpick_at_event(self, event): #renamed from unpick; modified
        """Make whatever visible atom or chunk (depending on self.selwhat)
        is under the mouse at event get un-selected,
        but don't change whatever else is selected.
        """
        atm = self.findAtomUnderMouse(event)
        if atm:
            if self.selwhat:
                atm.molecule.unpick()
            else:
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
        if not self.selwhat:
            self.unpickatoms()
            self.selwhat = 2
        return
    
    # deselect any selected molecules or groups #####@@@@@ needs review
    def unpickparts(self):
        self.root.unpick() # root contains self.tree and self.shelf
        self.data.unpick()

    # for debugging
    def prin(self):
        for a in self.selatoms.itervalues():
            a.prin()

######@@@@@@ GOT TO HERE
            
    #bruce 050131/050201 for Alpha (really for bug 278 and maybe related ones):
    # sanitize_for_clipboard, for cut and copy and other things that add clipboard items
    # ####@@@@ need to use in sethotspot too??
    
    def sanitize_for_clipboard(self, ob): 
        """Prepare ob for addition to the clipboard as a new toplevel item;
        should be called just before adding ob to shelf, OR for entire toplevel items already in shelf
        (or both; should be ok, though slower, to call more than once per item).
        NOT SURE IF OK to call when ob still has a dad in its old location.
        (Nor if it ever is thus called, tho i doubt it.)
        """
        self.sanitize_for_clipboard_0( ob) # recursive version handles per-chunk, per-group issues
        #e now do things for the shelf-item as a whole, if any, e.g. fix bug 371 about interspace bonds
        #e 050202: someday, should we do a version of the jig-moving workaround_for_bug_296?
        # that function itself is not reviewed for safety when called from here,
        # but it might be ok, tho better to consolidate its messages into one
        # (as in the "extension of that fix to the clipboard" it now comments about).
        if 0 and platform.atom_debug: #bruce 050215 this is indeed None for mols copied by mol.copy
            print "atom_debug: fyi: sanitize_for_clipboard sees selgroup of ob is %r" % ob.find_selection_group()
            ###e if this is None, then I'll have an easy way to break bonds from this item to stuff in the main model (bug 371)
            #e i.e. break_wormholes() or break_interspace_bonds()
        return
    
    def sanitize_for_clipboard_0(self, ob): #bruce 050131 for Alpha (really for bug 278 and maybe related ones)
        """[private method:]
        The recursive part of sanitize_for_clipboard:
        keep clipboard items (or chunks inside them) out of assy.molecules,
        so they can't be selected from glpane
        """
        #e should we do ob.unpick_top() as well?
        if ob.assy != self: #bruce 050202, and replaced ob.assy.molecules with self.molecules
            ob.assy = self # for now! in beta this might be its selgroup.
            if platform.atom_debug:
                print "sanitize_for_clipboard_0: node had wrong assy! fixed it:", ob
        if isinstance(ob, molecule):
            if self.selatoms:
                # bruce 050201 for Alpha: worry about selected atoms in chunks in clipboard
                # [no bugs yet reported on this, but maybe it could happen #k]
                #e someday ought to print atom_debug warning if this matters, to find out...
                try:
                    for atm in ob.atoms.values():
                        atm.unpick()
                except:
                    print_compact_traceback("sanitize_for_clipboard_0 ignoring error unpicking atoms: ")
                    pass
            try:
                self.molecules.remove(ob)
                # note: don't center the molecule here -- that's only appropriate
                # for each toplevel cut object as a whole!
            except:
                pass
        elif isinstance(ob, Group): # or any subclass! e.g. the Clipboard itself (deprecated to call this on that tho).
            for m in ob.members:
                self.sanitize_for_clipboard_0(m)
        return

    # bruce 050131/050201 revised these Cut and Copy methods to fix some Alpha bugs;
    # they need further review after Alpha, and probably could use some merging. ###@@@
    # See also assy.kill (Delete operation).
    
    def cut(self):
        self.w.history.message(greenmsg("Cut:"))
        if self.selatoms:
            #bruce 050201-bug370 (2nd commit here, similar issue to bug 370):
            # changed condition to not use selwhat, since jigs can be selected even in Select Atoms mode
            self.w.history.message(redmsg("Cutting selected atoms is not yet supported.")) #bruce 050201
            ## return #bruce 050201-bug370: don't return yet, in case some jigs were selected too.
            # note: we will check selatoms again, below, to know whether we emitted this message
        new = Group(gensym("Copy"),self,None)
            # bruce 050201 comment: this group is usually, but not always, used only for its members list
        if self.tree.picked:
            #bruce 050201 to fix catchall bug 360's "Additional Comments From ninad@nanorex.com  2005-02-02 00:36":
            # don't let assy.tree itself be cut; if that's requested, just cut all its members instead.
            # (No such restriction will be required for assy.copy, even when it copies entire groups.)
            self.tree.unpick_top()
            ## self.w.history.message(redmsg("Can't cut the entire Part -- cutting its members instead.")) #bruce 050201
            self.w.history.message("Can't cut the entire Part; copying its toplevel Group, cutting its members.") #bruce 050201
            # new code to handle this case [bruce 050201]
            self.tree.apply2picked(lambda(x): x.moveto(new))
            use = new
            use.name = self.tree.name # not copying any other properties of the Group (if it has any)
            new = Group(gensym("Copy"),self,None)
            new.addmember(use)
        else:
            self.tree.apply2picked(lambda(x): x.moveto(new))
            # bruce 050131 inference from recalled bug report:
            # this must fail in some way that addmember handles, or tolerate jigs/groups but shouldn't;
            # one difference is that for chunks it would leave them in assy.molecules whereas copy would not;
            # guess: that last effect (and the .pick we used to do) might be the most likely cause of some bugs --
            # like bug 278! Because findpick (etc) uses assy.molecules. So I fixed this with sanitize_for_clipboard, below.
        
        self.changed() # bruce 050131 resisted temptation to make this conditional on new.members; 050201 moved it earlier
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members:
                # bruce 050131 try fixing bug 278 in a limited, conservative way
                # (which won't help the underlying problem in other cases like drag & drop, sorry),
                # based on the theory that chunks remaining in assy.molecules is the problem:
                self.sanitize_for_clipboard(ob)
                self.shelf.addmember(ob) # add new member(s) to the clipboard [incl. Groups, jigs -- won't be pastable]
                # if the new member is a molecule, move it to the center of its space
                if isinstance(ob, molecule): ob.move(-ob.center)
            ## ob.pick() # bruce 050131 removed this
            nshelf_after = len(self.shelf.members) #bruce 050201
            self.w.history.message( fix_plurals("Cut %d item(s)" % (nshelf_after - nshelf_before)) + "." ) #bruce 050201
                ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
        else:
            if not self.selatoms:
                #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                self.w.history.message(redmsg("Nothing to cut.")) #bruce 050201
        
        self.w.win_update()

    # copy any selected parts (molecules) [making a new clipboard item... #doc #k]
    #  Revised by Mark to fix bug 213; Mark's code added by bruce 041129.
    #  Bruce's comments (based on reading the code, not all verified by test):
    #    0. If groups are not allowed in the clipboard (bug 213 doesn't say,
    #  but why else would it have been a bug to have added a group there?),
    #  then this is only a partial fix, since if a group is one of the
    #  selected items, apply2picked will run its lambda on it directly.
    #    1. The group 'new' is now seemingly used only to hold
    #  a list; it's never made a real group (I think). So I wonder if this
    #  is now deviating from Josh's intention, since he presumably had some
    #  reason to make a group (rather than just a list).
    #    2. Is it intentional to select only the last item added to the
    #  clipboard? (This will be the topmost selected item, since (at least
    #  for now) the group members are in bottom-to-top order.)
    def copy(self):
        self.w.history.message(greenmsg("Copy:"))
        if self.selatoms:
            #bruce 050201-bug370: revised this in same way as for assy.cut (above)
            self.w.history.message(redmsg("Copying selected atoms is not yet supported.")) #bruce 050131
            ## return
        new = Group(gensym("Copy"),self,None)
            # bruce 050201 comment: this group is always (so far) used only for its members list
        # x is each node in the tree that is picked. [bruce 050201 comment: it's ok if self.tree is picked.]
        # [bruce 050131 comments (not changing it in spite of bugs):
        #  the x's might be chunks, jigs, groups... but maybe not all are supported for copy.
        #  In fact, Group.copy returns 0 and Jig.copy returns None, and addmember tolerates that
        #  and does nothing!!
        #  About chunk.copy: it sets numol.assy but doesn't add it to assy,
        #  and it sets numol.dad but doesn't add it to dad's members -- so we do that immediately
        #  in addmember. So we end up with a members list of copied chunks from assy.tree.]
        self.tree.apply2picked(lambda(x): new.addmember(x.copy(None))) #bruce 050215 changed mol.copy arg from new to None

        # unlike for cut, no self.changed() should be needed
        
        if new.members:
            nshelf_before = len(self.shelf.members) #bruce 050201
            for ob in new.members[:]:
                # [bruce 050215 copying that members list, to fix bug 360 comment #6 (item 5),
                # which I introduced in Alpha-2 by making addmember remove ob from its prior home,
                # thus modifying new.members during this loop]
                self.sanitize_for_clipboard(ob) # not needed on 050131 but might be needed soon, and harmless
                self.shelf.addmember(ob) # add new member(s) to the clipboard
                # if the new member is a molecule, move it to the center of its space
                if isinstance(ob, molecule): ob.move(-ob.center)
            ## ob.pick() # bruce 050131 removed this
            nshelf_after = len(self.shelf.members) #bruce 050201
            self.w.history.message( fix_plurals("Copied %d item(s)" % (nshelf_after - nshelf_before)) + "." ) #bruce 050201
                ###e fix_plurals can't yet handle "(s)." directly. It needs improvement after Alpha.
        else:
            if not self.selatoms:
                #bruce 050201-bug370: we don't need this if the message for selatoms already went out
                self.w.history.message(redmsg("Nothing to Copy.")) #bruce 050201

        self.w.win_update()

    def paste(self, node):
        pass # to be implemented

    def unselect_clipboard_items(self): #bruce 050131 for Alpha
        "to be called before operations which are likely to fail when any clipboard items are selected"
        self.set_current_selection_group( self.tree)

    # move any selected parts in space ("move" is an offset vector)
    def movesel(self, move):
        for mol in self.selmols:
            self.changed()
            mol.move(move)
 
 
    # rotate any selected parts in space ("rot" is a quaternion)
    def rotsel(self, rot):
        for mol in self.selmols:
            self.changed()
            mol.rot(rot)
             

    def kill(self): # bruce 041118 simplified this after shakedown changes
        #bruce 050201 for Alpha: revised this to fix bug 370
        "delete whatever is selected from this assembly [except the PartGroup node itself]"
        self.w.history.message(greenmsg("Delete:"))
        ###@@@ #e this also needs a results-message, below.
        if self.selatoms:
            self.changed()
            for a in self.selatoms.values():
                a.kill()
            self.selatoms = {} # should be redundant
        if 1:
            ## bruce 050201 removed the condition "self.selwhat == 2 or self.selmols"
            # since selected jigs no longer force selwhat to be 2.
            # (Maybe they never did, but my guess is they did; anyway I think they shouldn't.)
            # self.changed() is not needed since removing Group members should do it (I think),
            # and would be wrong here if nothing was selected.
            self.tree.unpick_top() #bruce 050201: prevent deletion of entire part (no msg needed)
            self.tree.apply2picked(lambda o: o.kill())
            # Also kill anything picked in the clipboard
            # [revised by bruce 050131 for Alpha, see cvs rev 1.117 for historical comments]
            self.shelf.apply2picked(lambda o: o.kill()) # kill by Mark(?), 11/04
        self.setDrawLevel() #e should this update bbox too?? or more? [bruce 050214 comment]
        return


##    # actually remove a given molecule from the list [no longer used]
##    def killmol(self, mol):
##        mol.kill()
##        self.setDrawLevel()


    # bruce 050201 for Alpha:
    #    Like I did to fix bug 370 for Delete (and cut and copy),
    # make Hide and Unhide work on jigs even when in selatoms mode.
    #    Also make them work in clipboard (by changing
    # self.tree to self.root below) -- no reason
    # not to, and it's confusing when cmenu offers these choices but they do nothing.
    # It's ok for them to operate on entire Part since they only affect leaf nodes.
    
    def Hide(self):
        "Hide all selected chunks and jigs"
        self.root.apply2picked(lambda x: x.hide())
        self.w.win_update()

    def Unhide(self):
        "Unhide all selected chunks and jigs"
        self.root.apply2picked(lambda x: x.unhide())
        self.w.win_update()

    #bond atoms (cheap hack)
    def Bond(self):
        if not self.selatoms: return
        aa=self.selatoms.values()
        if len(aa)==2:
            self.changed()
            aa[0].molecule.bond(aa[0], aa[1])
            #bruce 041028 bugfix: bring following lines inside the 'if'
            aa[0].molecule.changeapp(0)
            aa[1].molecule.changeapp(0)
            self.o.gl_update()

    #unbond atoms (cheap hack)
    def Unbond(self):
        if not self.selatoms: return
        self.changed()
        aa=self.selatoms.values()
        if len(aa)==2:
            #bruce 041028 bugfix: add [:] to copy following lists,
            # since bust will modify them during the iteration
            for b1 in aa[0].bonds[:]:
                for b2 in aa[1].bonds[:]:
                    if b1 == b2: b1.bust()
        self.o.gl_update()

    #stretch a molecule
    def Stretch(self):
        if not self.selmols:
            self.w.history.message(redmsg("no selected chunks to stretch")) #bruce 050131
            return
        self.changed()
        for m in self.selmols:
            m.stretch(1.1)
        self.o.gl_update()

    #weld selected molecules together
    def weld(self):
        #bruce 050131 comment: might now be safe for clipboard items
        # since all selection is now forced to be in the same one;
        # this is mostly academic since there's no pleasing way to use it on them,
        # though it's theoretically possible (since Groups can be cut and maybe copied).
        if len(self.selmols) < 2:
            self.w.history.message(redmsg("need two or more selected chunks to weld")) #bruce 050131
            return
        self.changed() #bruce 050131 bugfix or precaution
        mol = self.selmols[0]
        for m in self.selmols[1:]:
            mol.merge(m)


    def align(self):
        if len(self.selmols) < 2:
            self.w.history.message(redmsg("need two or more selected chunks to align")) #bruce 050131
            return
        self.changed() #bruce 050131 bugfix or precaution
        ax = V(0,0,0)
        for m in self.selmols:
            ax += m.getaxis()
        ax = norm(ax)
        for m in self.selmols:
            m.rot(Q(m.getaxis(),ax))
        self.o.gl_update()
                  

    #############

    def __str__(self):
        return "<Assembly of " + self.filename + ">"

    def computeBoundingBox(self):
        """Compute the bounding box for the assembly. This should be
        called whenever the geometry model has been changed, like new
        parts added, parts/atoms deleted, parts moved/rotated(not view
        move/rotation), etc."""
        
        self.bbox = BBox()
        for mol in self.molecules:
              self.bbox.merge(mol.bbox)
        self.center = self.bbox.center()
        
    # makes a simulation movie
    def makeSimMovie(self):
        self.simcntl = runSim(self) # Open SimSetup dialog
        if self.m.cancelled: return -1 # user hit Cancel button in SimSetup Dialog.
        r = self.writemovie()
        # Movie created.  Initialize.
        if not r: 
            self.m.IsValid = True # Movie is valid.
            self.m.currentFrame = 0
        return r

    # makes a minimize movie
    def makeMinMovie(self,mtype = 2):
        """Minimize the part and display the results.
        mtype:
            1 = tell writemovie() to create a single-frame XYZ file.
            2 = tell writemovie() to create a multi-frame DPB moviefile.
        """
        r = self.writemovie(mtype) # Writemovie informs user if there was a problem.
        if r: return # We had a problem writing the minimize file.  Simply return.
        
        if mtype == 1:  # Load single-frame XYZ file.
            newPositions = self.readxyz()
            if newPositions:
                self.moveAtoms(newPositions)
            
        else: # Play multi-frame DPB movie file.
            self.m.currentFrame = 0
            # If _setup() returns a non-zero value, something went wrong loading the movie.
            if self.m._setup(): return
            self.m._play()
            self.m._close()
        
    def makeRotaryMotor(self, sightline):
        """Creates a Rotary Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m=RotaryMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Rotary Motory Dialog.
            del(m)
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()
      
    def makeLinearMotor(self, sightline):
        """Creates a Linear Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = LinearMotor(self)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Linear Motory Dialog.
            del(m)
            return
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    def makeground(self):
        """Grounds (anchors) all the selected atoms so that 
        they will not move during a simulation run.
        There is a limit of 30 atoms per Ground.  Any more will choke the file parser
        in the simulator. To work around this, just make more Grounds.
        """
        # [bruce 050210 modified docstring]
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m=Ground(self, self.selatoms.values())
        mol = self.selatoms.values()[0].molecule
        mol.dad.addmember(m)
        self.unpickatoms()

    def makestat(self):
        """Attaches a Langevin thermostat to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m=Stat(self, self.selatoms.values())
        m.atoms[0].molecule.dad.addmember(m) #bruce 050210 replaced obs .mol attr
        self.unpickatoms()
        
    def makethermo(self):
        """Attaches a thermometer to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m=Thermo(self, self.selatoms.values())
        m.atoms[0].molecule.dad.addmember(m) #bruce 050210 replaced obs .mol attr
        self.unpickatoms()
        
    # select all atoms connected by a sequence of bonds to
    # an already selected one
    def marksingle(self):
        for a in self.selatoms.values():
            self.conncomp(a, 1)
       
    # connected components. DFS is elegant!
    # This is called with go=1 from eached already picked atom
    # its only problem is relatively limited stack in Python
    def conncomp(self, atom, go=0):
        if go or not atom.picked:
            atom.pick()
            for a in atom.neighbors():
                 self.conncomp(a)

    # select all atoms connected by two disjoint sequences of bonds to
    # an already selected one. This picks stiff components but doesn't
    # cross single-bond or single-atom bearings or hinges
    # does select e.g. hydrogens connected to the component and nothing else
    def markdouble(self):
        self.father= {}
        self.stack = []
        self.out = []
        self.dfi={}
        self.p={}
        self.i=0
        for a in self.selatoms.values():
            if a not in self.dfi:
                self.father[a]=None
                self.blocks(a)
        for (a1,a2) in self.out[-1]:
            a1.pick()
            a2.pick()
        for mol in self.molecules:
            for a in mol.atoms.values():
                if len(a.bonds) == 1 and a.neighbors()[0].picked:
                    a.pick()


    # compared to that, the doubly-connected components algo is hairy.
    # cf Gibbons: Algorithmic Graph Theory, Cambridge 1985
    def blocks(self, atom):
        self.dfi[atom]=self.i
        self.p[atom] = self.i
        self.i += 1
        for a2 in atom.neighbors():
            if atom.key < a2.key: pair = (atom, a2)
            else: pair = (a2, atom)
            if not pair in self.stack: self.stack += [pair]
            if a2 in self.dfi:
                if a2 != self.father[atom]:
                    self.p[atom] = min(self.p[atom], self.dfi[a2])
            else:
                self.father[a2] = atom
                self.blocks(a2)
                if self.p[a2] >= self.dfi[atom]:
                    pop = self.stack.index(pair)
                    self.out += [self.stack[pop:]]
                    self.stack = self.stack[:pop]
                self.p[atom] = min(self.p[atom], self.p[a2])

    def modifyDeleteBonds(self):
        """Delete all bonds between selected and unselected atoms or chunks
        """
        
        if not self.selatoms and not self.selmols: # optimization, and different status msg
            msg = redmsg("Delete Bonds: Nothing selected")
            self.w.history.message(msg)
            return
        
        self.w.history.message(greenmsg("Delete Bonds:"))
        
        cutbonds = 0
        
        # Delete bonds between selected atoms and their neighboring atoms that are not selected.
        for a in self.selatoms.values():
            for b in a.bonds[:]:
                neighbor = b.other(a)
                if neighbor.element != Singlet:
                    if not neighbor.picked:
                        b.bust()
                        a.pick() # Probably not needed, but just in case...
                        cutbonds += 1

        # Delete bonds between selected chunks and chunks that are not selected.
        for mol in self.selmols[:]:
            # "externs" contains a list of bonds between this chunk and a different chunk
            for b in mol.externs[:]:
                # atom1 and atom2 are the connect atoms in the bond
                if int(b.atom1.molecule.picked) + int(b.atom2.molecule.picked) == 1: 
                    b.bust()
                    cutbonds += 1
                    
        msg = fix_plurals("%d bond(s) deleted" % cutbonds)
        self.w.history.message(msg)
        
        if self.selatoms and cutbonds:
            self.modifySeparate() # Separate the selected atoms into a new chunk
        else:
            self.w.win_update() #e do this in callers instead?
        
    #m modifySeparate needs to be changed to modifySplit.  Need to coordinate
    # this with Bruce since this is called directly from some mode modules.
    # Mark 050209
    #
    # separate selected atoms into a new molecule
    # (one new mol for each existing one containing any selected atoms)
    # do not break bonds
    def modifySeparate(self, new_old_callback = None):
        """For each molecule (named N) containing any selected atoms,
           move the selected atoms out of N (but without breaking any bonds)
           into a new molecule which we name N-frag.
           If N is now empty, remove it.
           If new_old_callback is provided, then each time we create a new
           (and nonempty) fragment N-frag, call new_old_callback with the
           2 args N-frag and N (that is, with the new and old molecules).
           Warning: we pass the old mol N to that callback,
           even if it has no atoms and we deleted it from this assembly.
        """
        # bruce 040929 wrote or revised docstring, added new_old_callback feature
        # for use from Extrude.
        # Note that this is called both from a tool button and for internal uses.
        # bruce 041222 removed side effect on selection mode, after discussion
        # with Mark and Josh. Also added some status messages.
        # Questions: is it good to refrain from merging all moved atoms into one
        # new mol? If not, then if N becomes empty, should we rename N-frag to N?
        
        if not self.selatoms: # optimization, and different status msg
            msg = "Separate: no atoms selected"
            self.w.history.message(msg)
            return
        numolist=[]
        for mol in self.molecules[:]: # new mols are added during the loop!
            numol = molecule(self, gensym(mol.name + "-frag"))
            for a in mol.atoms.values():
                if a.picked:
                    # leave the moved atoms picked, so still visible
                    a.hopmol(numol)
            if numol.atoms:
                self.addmol(numol)
                numolist+=[numol]
                if new_old_callback:
                    new_old_callback(numol, mol) # new feature 040929
        msg = fix_plurals("Separate created %d new chunk(s)" % len(numolist))
        self.w.history.message(msg)
        self.w.win_update() #e do this in callers instead?

    def copySelatomFrags(self):
        #bruce 041116, combining modifySeparate and mol.copy; for extrude
        """
           For each molecule (named N) containing any selected atoms,
           copy the selected atoms of N to make a new molecule named N-frag
           (which is not added to the assembly, self). The old mol N is unchanged.
           The copy is done as if by molecule.copy (with cauterize = 1),
           except that all bonds between selected atoms are copied, even if not in same mol.
           Return a list of pairs of new and old molecules [(N1-frag,N1),...].
           (#e Should we optionally return a list of pairs of new and old atoms, too?
           And one of new bonds or singlets and old external atoms, or the equiv?)
        """
        oldmols = {}
        for a in self.selatoms.values():
            m = a.molecule
            oldmols[id(m)] = m ###k could we use key of just m, instead??
        newmols = {}
        for old in oldmols.values():
            numol = molecule(self, gensym(mol.name + "-frag"))
            newmols[id(old)] = numol # same keys as in oldmols
        nuats = {}
        for a in self.selatoms.values():
            old = a.molecule
            numol = newmols[id(old)]
            a.info = id(a) # lets copied atoms correspond (useful??)
            nuat = a.copy() # uses new copy method as of bruce 041116
            numol.addatom(nuat)
            nuats[id(a)] = nuat
        extern_atoms_bonds = []
        for a in self.selatoms.values():
            assert a.picked
            for b in a.bonds:
                a2 = b.other(a)
                if a2.picked:
                    # copy the bond (even if it's a mol-mol bond), but only once per bond
                    if id(a) < id(a2):
                        bond_atoms(nuats[id(a)], nuats[id(a2)])
                else:
                    # make a singlet instead of this bond (when we're done)
                    extern_atoms_bonds.append( (a,b) ) # ok if several times for one 'a'
                    #e in future, might keep more info
        for a,b in extern_atoms_bonds:
            # compare to code in Bond.unbond(): ###e make common code
            nuat = nuats[id(a)]
            x = atom('X', + b.ubp(a), nuat.molecule)
            bond_atoms(nuat, x)
        res = []
        for old in oldmols.values():
            new = newmols[id(old)]
            res.append( (new,old) )
        return res
        

    # change surface atom types to eliminate dangling bonds
    # a kludgey hack
    # bruce 041215 added some comments.
    def modifyPassivate(self):
        if self.selwhat == 2:
            for m in self.selmols:
                m.Passivate(True) # arg True makes it work on all atoms in m
        else:
            for m in self.molecules:
                m.Passivate() # lack of arg makes it work on only selected atoms
                # (maybe it could just iterate over selatoms... #e)
                
        self.changed() # could be much smarter
        self.o.gl_update()

    # add hydrogen atoms to each dangling bond
    def modifyHydrogenate(self):
        self.o.mode.modifyHydrogenate()
        
    # remove hydrogen atoms from every selected atom/molecule
    def modifyDehydrogenate(self):
        self.o.mode.modifyDehydrogenate()

    # write moviefile
    def writemovie(self, mflag = 0):
        from fileIO import writemovie
        return writemovie(self, mflag)

    # read xyz file.
    def readxyz(self):
        from fileIO import readxyz
        return readxyz(self)
                    
    # end of class assembly
