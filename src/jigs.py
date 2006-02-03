# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
jigs.py -- Classes for motors and other jigs, and their superclass, Jig.

$Id$

History: Mostly written as gadgets.py (I'm not sure by whom);
renamed to jigs.py by bruce 050414; jigs.py 1.1 should be an
exact copy of gadgets.py rev 1.72,
except for this module-docstring and a few blank lines and comments.

bruce 050507 pulled in the jig-making methods from class Part.

bruce 050513 replaced some == with 'is' and != with 'is not', to avoid __getattr__
on __xxx__ attrs in python objects.

bruce circa 050518 made rmotor arrow rotate along with the atoms.

050901 bruce used env.history in some places. 

050927 moved motor classes to jigs_motors.py and plane classes to jigs_planes.py

mark 051104 Changed named of Ground jig to Anchor.
"""

from VQT import *
from shape import *
from chem import *
import OpenGL.GLUT as glut
from Utility import *
from StatProp import *
from ThermoProp import *
from HistoryWidget import redmsg, greenmsg
from povheader import povpoint #bruce 050413
from debug import print_compact_stack, print_compact_traceback
import env #bruce 050901

Gno = 0
def gensym(string):
    # warning, there is also a function like this in chem.py
    # but with its own global counter!
    """return string appended with a unique number"""
    global Gno
    Gno += 1
    return string + str(Gno)

class Jig(Node):
    "abstract superclass for all jigs"
    
    # Each Jig subclass must define the class variables:
    # - icon_names -- a list of two icon basenames (one normal and one "hidden") (unless it overrides node_icon)
    #
    # and the class constants:
    # - mmp_record_name (if it's ever written to an mmp file)
    #
    # and can optionally redefine some of the following class constants:
    sym = "Jig" # affects name-making code in __init__
    pickcolor = (1.0, 0.0, 0.0) # color in glpane when picked (default: red)
    mmp_record_name = "#" # if not redefined, this means it's just a comment in an mmp file
    featurename = "" # wiki help featurename for each Jig (or Node) subclass, or "" if it doesn't have one yet [bruce 051201]
        # (Each Jig subclass should override featurename with a carefully chosen name; for a few jigs it should end in "Jig".)

    # class constants used as default values of instance variables:
    
    #e we should sometime clean up the normcolor and color attributes, but it's hard,
    # since they're used strangly in the *Prop.py files and in our pick and unpick methods.
    # But at least we'll give them default values for the sake of new jig subclasses. [bruce 050425]
    color = normcolor = (0.5, 0.5, 0.5)
    
    # "Enable Minimize" is only supported for motors.  Otherwise, it is ignored.  Mark 051006.
    # [I suspect the cad code supports it for all jigs, but only provides a UI to set it for motors. -- bruce 051102]
    enable_minimize = False # whether a jig should apply forces to atoms during Minimize
        # [should be renamed 'enable_in_minimize', but I'm putting this off since it affects lots of files -- bruce 051102]
    
    atoms = None
    cntl = None # see set_cntl method (creation of these deferred until first needed, by bruce 050526)
    
    copyable_attrs = Node.copyable_attrs + ('pickcolor', 'normcolor', 'color') # this extends the tuple from Node
        # most Jig subclasses need to extend this further
    
    def __init__(self, assy, atomlist): # Warning: some Jig subclasses require atomlist in __init__ to equal [] [revised circa 050526]
        "each subclass needs to call this, at least sometime before it's used as a Node"
        Node.__init__(self, assy, gensym("%s-" % self.sym)) # Changed from "." to "-". mark 060107
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
        self.glname = env.alloc_my_glselect_name( self) 
        
        return

    def _um_initargs(self): #bruce 051013
        """Return args and kws suitable for __init__.
        [Overrides an undo-related superclass method; see its docstring for details.]
        """
        return (self.assy, self.atoms), {} # This should be good enough for most Jig subclasses.

    def node_icon(self, display_prefs): #bruce 050425 simplified this
        "a subclass should override this if it needs to choose its icons differently"
        return imagename_to_pixmap( self.icon_names[self.hidden] )
        
    def setAtoms(self, atomlist):
        # [as of 050415 (and long before) this is only used for motors; __init__ does same thing for other jigs]
        if self.atoms:
            print "fyi: bug? setAtoms overwrites existing atoms on %r" % self
            #e remove them? would need to prevent recursive kill.
        self.atoms = list(atomlist) # bruce 050316: copy the list
        for a in atomlist:
            a.jigs.append(self)

    def needs_atoms_to_survive(self): #bruce 050526
        return True # for all Jigs that exist so far
    
    # == copy methods [default values or common implems for Jigs,
    # == when these differ from Node methods] [bruce 050526 revised these]
    
    def will_copy_if_selected(self, sel):
        "[overrides Node method]"
        # Copy this jig if asked, provided the copy will refer to atoms if necessary.
        # Whether it's disabled (here and/or in the copy, and why) doesn't matter.
        if not self.needs_atoms_to_survive():
            return True
        for atom in self.atoms:
            if sel.picks_atom(atom):
                return True
        # Tell user reason why not.  Mark 060125.
        msg = "Didn't copy %s since none of its atoms were copied." % (self.name)
        env.history.message(orangemsg(msg))
        return False

    def will_partly_copy_due_to_selatoms(self, sel):
        "[overrides Node method]"
        return True # this is correct for jigs that say yes to jig.confers_properties_on(atom), and doesn't matter for others.

    def copy_full_in_mapping(self, mapping):
        clas = self.__class__
        new = clas(self.assy, []) # don't pass any atoms yet (maybe not all of them are yet copied)
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
        """[Private method]
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
    
    # josh 10/26 to fix bug 85
    # bruce 050215 added docstring and added removal of self from atm.jigs
    def rematom(self, atm):
        "remove atom atm from this jig, and remove this jig from atom atm [called from atom.kill]"
        self.atoms.remove(atm)
        #bruce 050215: also remove self from atm's list of jigs
        try:
            atm.jigs.remove(self) # assume no need to notify atm of this
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: ignoring exception in rematom: ")
        # should check and delete the jig if no atoms left
        if not self.atoms and self.needs_atoms_to_survive():
            self.kill()
        return
    
    def kill(self):
        # bruce 050215 modified this to remove self from our atoms' jiglists, via rematom
        for atm in self.atoms[:]: #bruce 050316: copy the list (presumably a bugfix)
            self.rematom(atm) # the last one removed kills the jig recursively!
        Node.kill(self) # might happen twice, that's ok

    def destroy(self): #bruce 050718, for bonds code
        # not sure if this ever needs to differ from kill -- probably not; in fact, you should probably override kill, not destroy
        self.kill()

    # bruce 050125 centralized pick and unpick (they were identical on all Jig
    # subclasses -- with identical bugs!), added comments; didn't yet fix the bugs.
    #bruce 050131 for Alpha: more changes to it (still needs review after Alpha is out)
    
    def pick(self): 
        """select the Jig"""
        env.history.message(self.getinfo())
            #bruce 050901 revised this; now done even if jig is killed (might affect fixed bug 451-9)
        if not self.picked: #bruce 050131 added this condition (maybe good for history.message too?)
            Node.pick(self) #bruce 050131 for Alpha: using Node.pick
            self.normcolor = self.color # bug if this is done twice in a row! [bruce 050131 maybe fixed now due to the 'if']
            self.color = self.pickcolor
        return

    def unpick(self):
        """unselect the Jig"""
        if self.picked:
            Node.unpick(self) # bruce 050126 -- required now
            self.color = self.normcolor # see also a copy method which has to use the same statement to compensate for this kluge

    def move(self, offset):
        #bruce 050208 made this default method. Is it ever called, in any subclasses??
        pass
    

    def rot(self, quat):
        pass

    
    def moved_atom(self, atom): #bruce 050718, for bonds code
        """FYI (caller is saying to this jig),
        we have just changed atom.posn() for one of your atoms.
        [Subclasses should override this as needed.]
        """
        pass

    def changed_structure(self, atom): #bruce 050718, for bonds code
        """FYI (caller is saying to this jig),
        we have just changed the element, atomtype, or bonds for one of your atoms.
        [Subclasses should override this as needed.]
        """
        pass
    
    def break_interpart_bonds(self): #bruce 050316 fix the jig analog of bug 371; 050421 undo that change for Alpha5 (see below)
        "[overrides Node method]"
        #e this should be a "last resort", i.e. it's often better if interpart bonds
        # could split the jig in two, or pull it into a new Part.
        # But that's NIM (as of 050316) so this is needed to prevent some old bugs.
        #bruce 050421 for Alpha5 decided to permit all Jig-atom interpart bonds, but just let them
        # make the Jig disabled. That way you can drag Jigs out and back into a Part w/o losing their atoms.
        # (And we avoid bugs from removing Jigs and perhaps their clipboard-item Parts at inconvenient times.)
        #bruce 050513 as long as the following code does nothing, let's speed it up ("is not") and also comment it out.
##        for atm in self.atoms[:]:
##            if self.part is not atm.molecule.part and 0: ###@@@ try out not doing this; jigs will draw and save inappropriately at first...
##                self.rematom(atm) # this might kill self, if we remove them all
        return

    def anchors_atom(self, atm): #bruce 050321, renamed 050404
        "does this jig hold this atom fixed in space? [should be overridden by subclasses as needed]"
        return False # for most jigs

    def node_must_follow_what_nodes(self): #bruce 050422 made Node and Jig implems of this from function of same name
        """[overrides Node method]
        """
        mols = {} # maps id(mol) to mol [bruce 050422 optim: use dict, not list]
        for atm in self.atoms:
            mol = atm.molecule
            if id(mol) not in mols:
                mols[id(mol)] = mol
        return mols.values()

    def writemmp(self, mapping): #bruce 050322 revised interface to use mapping
        "[overrides Node.writemmp; could be overridden by Jig subclasses, but isn't (as of 050322)]"
         #bruce 050322 made this from old Node.writemmp, but replaced nonstandard use of __repr__
        line, wroteleaf = self.mmp_record(mapping) # includes '\n' at end
        if line:
            mapping.write(line)
            if wroteleaf:
                self.writemmp_info_leaf(mapping)
                # only in this case, since other case means no node was actually written [bruce 050421]
        else:
            Node.writemmp(self, mapping) # just writes comment into file and atom_debug msg onto stdout
        return
    
    def writemmp_info_leaf(self, mapping): #bruce 051102
        "[extends superclass method]"
        Node.writemmp_info_leaf(self, mapping)
        if self.enable_minimize:
            mapping.write("info leaf enable_in_minimize = True\n") #bruce 051102
        return

    def readmmp_info_leaf_setitem( self, key, val, interp ): #bruce 051102
        "[extends superclass method]"
        if key == ['enable_in_minimize']:
            # val should be "True" or "False" (unrecognized vals are treated as False)
            val = (val == 'True')
            self.enable_minimize = val
        else:
            Node.readmmp_info_leaf_setitem( self, key, val, interp)
        return
    
    def _mmp_record_front_part(self, mapping):
        # [Huaicai 9/21/05: split mmp_record into front-middle-last 3 parts, so the each part can be different for a diffent jig.
        
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
        '''Last part of the record. Subclass can override this method to provide specific version of this part.
         Note: If it returns anything other than empty, make sure to put one extra space character at the front.'''
        # [Huaicai 9/21/05: split this from mmp_record, so the last part can be different for a jig like ESP Image, which is none.
        if mapping is not None:
            ndix = mapping.atnums
            minflag = mapping.min # writing this record for Minimize? [bruce 051031]
        else:
            ndix = None
            minflag = False
        nums = self.atnums_or_None( ndix, return_partial_list = minflag )
        
        return " " + " ".join(map(str,nums))
        

    def mmp_record(self, mapping = None): 
        #bruce 050422 factored this out of all the existing Jig subclasses, changed arg from ndix to mapping
        #e could factor some code from here into mapping methods
        #bruce 050718 made this check for mapping is not None (2 places), as a bugfix in __repr__
        #bruce 051031 revised forward ref code, used mapping.min
        """Returns a pair (line, wroteleaf)
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
            assert after_these # but this alone does not assert that they weren't all already written out! The next method should do that.
            mapping.write_forwarded_node_after_nodes( self, after_these, force_disabled_for_sim = self.is_disabled() )
            return fwd_ref_to_return_now , False
        
        frontpart = self._mmp_record_front_part(mapping)
        midpart = self.mmp_record_jigspecific_midpart()
        lastpart = self._mmp_record_last_part(mapping) # note: this also calls atnums_or_None

        if lastpart == " ": # kluge! should return a flag instead [bruce 051102 for "enable minimize"]
            # this happens during "minimize selection" if a jig is enabled for minimize but none of its atoms are being minimized.
            return "# jig with no selected atoms skipped for minimize\n", False
        
        return frontpart + midpart + lastpart + "\n" , True



    def mmp_record_jigspecific_midpart(self):
        """#doc
        (see rmotor's version's docstring for details)
        [some subclasses need to override this]
        Note: If it returns anything other than empty, make sure add one more extra 'space' at the front.
        """
        return ""

    # Added "return_partial_list" after a discussion with Bruce about enable minimize jigs.
    # This would allow a partial atom list to be returned.
    # [Mark 051006 defined return_partial_list API; bruce 051031 revised docstring and added implem,
    #  here and in one subclass.]
    def atnums_or_None(self, ndix, return_partial_list = False):
        """Return list of atnums to write, as ints(??) (using ndix to encode them),
        or None if some atoms were not yet written to the file and return_partial_list is False.
        (If return_partial_list is True, then missing atoms are just left out of the returned list.
        Callers should check whether the resulting list is [] if that matters.)
        (If ndix not supplied, as when we're called by __repr__, use atom keys for atnums;
        return_partial_list doesn't matter in this case since all atoms have keys.)
        [Jig method; overridden by some subclasses]
        """
        res = []
        for atm in self.atoms:
            key = atm.key
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
            line, wroteleaf = self.mmp_record()
            assert wroteleaf
        except: #bruce 050422
            print_compact_traceback( "bug in Jig.__repr__ call of self.mmp_record() ignored: " )
            line = None
        if line:
            return line
        else:
            return "<%s at %#x>" % (self.__class__.__name__, id(self)) # untested
        pass


    def is_disabled(self): #bruce 050421 experiment related to bug 451-9
        "[overrides Node method]"
        return self.disabled_by_user_choice or self.disabled_by_atoms()


    def disabled_by_atoms(self): #e rename?
        "is this jig necessarily disabled (due to some atoms being in a different part)?"
        part = self.part
        for atm in self.atoms:
            if part is not atm.molecule.part:
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

    def _getinfo(self):
        "Return a string for display in history or Properties [subclasses should override this]"
        return "[%s: %s]" % (self.sym, self.name)

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
        self.cntl.setup()
        self.cntl.exec_loop()

    #e there might be other common methods to pull into here

    pass # end of class Jig

# == Anchor (was Ground)

class Anchor(Jig):
    '''an Anchor (Ground) just has a list of atoms that are anchored in space'''

    sym = "Anchor"
    icon_names = ["anchor.png", "anchor-hide.png"]
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
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o) 

    # it's drawn as a wire cube around each atom (default color = black)

    def _draw(self, glpane, dispdef):
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "anchor" record to POV-Ray file in the format:
    # anchor(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            grec = "anchor(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(grec)

    def _getinfo(self):
        return "[Object: Anchor] [Name: " + str(self.name) + "] [Total Anchors: " + str(len(self.atoms)) + "]"

    def getstatistics(self, stats):
        stats.nanchors += len(self.atoms)

    mmp_record_name = "ground" # Will change to "anchor" for A7.  Mark 051104.
    def mmp_record_jigspecific_midpart(self): # see also fake_Anchor_mmp_record [bruce 050404]
        return ""

    def anchors_atom(self, atm): #bruce 050321; revised 050423 (warning: quadratic time for large anchor jigs in Minimize)
        "does this jig hold this atom fixed in space? [overrides Jig method]"
        return (atm in self.atoms) and not self.is_disabled()

    def confers_properties_on(self, atom): # Anchor method
        """[overrides Node method]
        Should this jig be partly copied (even if not selected)
        when this atom is individually selected and copied?
        (It's ok to assume without checking that atom is one of this jig's atoms.)
        """
        return True
    
    pass # end of class Anchor

def fake_Anchor_mmp_record(atoms, mapping): #bruce 050404 utility for Minimize Selection
    """Return an mmp record (one or more lines with \n at end)
    for a fake Anchor (Ground) jig for use in an mmp file meant only for simulator input.
       Note: unlike creating and writing out a new real Anchor (Ground) object,
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
    """Subclass for Stat and Thermo, which are on one atom in cad code,
    but on its whole chunk in simulator,
    by means of being written into mmp file as the min and max atnums in that chunk
    (whose atoms always occupy a contiguous range of atnums, since those are remade per writemmp event),
    plus the atnum of their one user-visible atom.
    """
    def setAtoms(self, atomlist):
        "[Overrides Jig method; called by Jig.__init__]"
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
        """return list of atnums to write, or None if some atoms not yet written
        [overrides Jig method]
        """
        assert len(self.atoms) == 1
        atm = self.atoms[0]
        if ndix:
            # for mmp file -- return numbers of first, last, and defining atom
            atomkeys = [atm.key] + atm.molecule.atoms.keys() # arbitrary order except first list element
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
    '''A Stat is a Langevin thermostat, which sets a chunk to a specific
    temperature during a simulation. A Stat is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms:
    - first_atom: the first atom of the chunk to which it is attached.
    - last_atom: the last atom of the chunk to which it is attached.
    - boxed_atom: the atom in the chunk the user selected. A box is drawn
    around this atom.
       Note that the simulator applies the Stat to all atoms in the entire chunk
    to which it's attached, but in case of merging or joining chunks, the atoms
    in this chunk might be different each time the mmp file is written; even
    the atom order in one chunk might vary, so the first and last atoms can be
    different even when the set of atoms in the chunk has not changed.
    Only the boxed_atom is constant (and only it is saved, as self.atoms[0]).
    '''
    #bruce 050210 for Alpha-2: fix bug in Stat record reported by Josh to ne1-users    
    sym = "Stat"
    icon_names = ["stat.png", "stat-hide.png"]
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

    # it's drawn as a wire cube around each atom (default color = blue)
    def _draw(self, glpane, dispdef):
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "stat" record to POV-Ray file in the format:
    # stat(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            srec = "stat(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(srec)

    def _getinfo(self):
        return  "[Object: Thermostat] "\
                    "[Name: " + str(self.name) + "] "\
                    "[Temp = " + str(self.temp) + "K]" + "] "\
                    "[Attached to: " + str(self.atoms[0].molecule.name) + "] "

    def getstatistics(self, stats):
        stats.nstats += len(self.atoms)

    mmp_record_name = "stat"
    def mmp_record_jigspecific_midpart(self):
        return " " + "(%d)" % int(self.temp)

    pass # end of class Stat


# == Thermo

class Thermo(Jig_onChunk_by1atom):
    '''A Thermo is a thermometer which measures the temperature of a chunk
    during a simulation. A Thermo is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms and applies to all
    atoms in the same chunk; for details see Stat docstring.
    '''
    #bruce 050210 for Alpha-2: fixed same bug as in Stat.
    sym = "Thermo"
    icon_names = ["thermo.png", "thermo-hide.png"]
    featurename = "Thermometer" #bruce 051203

    # creates a thermometer for a specific atom. "list" contains only one atom.
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list) # note: this calls Jig_onChunk_by1atom.setAtoms method
        # set default color of new thermo to dark red
        self.color = darkred # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = darkred # This is the normal (unselected) color.

    def set_cntl(self): #bruce 050526 split this out of __init__ (in all Jig subclasses)
        self.cntl = ThermoProp(self, self.assy.o)

    # it's drawn as a wire cube around each atom.
    def _draw(self, glpane, dispdef):
        for a in self.atoms:
            # Using dispdef of the atom's chunk instead of the glpane's dispdef fixes bug 373. mark 060122.
            chunk = a.molecule
            dispdef = chunk.get_dispdef(glpane)
            disp, rad = a.howdraw(dispdef)
            # wware 060203 selected bounding box bigger, bug 756
            if self.picked: rad *= 1.01
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "thermo" record to POV-Ray file in the format:
    # thermo(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            srec = "thermo(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(srec)

    def _getinfo(self):
        return  "[Object: Thermometer] "\
                    "[Name: " + str(self.name) + "] "\
                    "[Attached to: " + str(self.atoms[0].molecule.name) + "] "

    def getstatistics(self, stats):
        #bruce 050210 fixed this as requested by Mark
        stats.nthermos += len(self.atoms)

    mmp_record_name = "thermo"
    def mmp_record_jigspecific_midpart(self):
        return ""
    
    pass # end of class Thermo


# == AtomSet

class AtomSet(Jig):
    '''an Atom Set just has a list of atoms that can be easily selected by the user'''

    sym = "Atom Set"
    icon_names = ["atomset.png", "atomset-hide.png"]
    featurename = "Atom Set" #bruce 051203

    # create a blank AtomSet with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        # set default color of new set atom to black
        self.color = black # This is the "draw" color.  When selected, this will become highlighted red.
        self.normcolor = black # This is the normal (unselected) color.

    def set_cntl(self):
        # Fixed bug 1011.  Mark 050927.
        from JigProp import JigProp
        self.cntl = JigProp(self, self.assy.o)

    # it's drawn as a wire cube around each atom (default color = black)
    def _draw(self, glpane, dispdef):
        '''Draws a red wire frame cube around each atom, only if the jig is select.
        '''
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

    def getstatistics(self, stats):
        stats.natoms += 1 # Count only the atom set itself, not the number of atoms in the set.

    mmp_record_name = "atomset"
    def mmp_record_jigspecific_midpart(self):
        return ""
        
#    def _mmp_record_front_part(self, mapping):
#        
#        if mapping is not None:
#            name = mapping.encode_name(self.name)
#        else:
#            name = self.name
#        
#        if self.picked:
#            c = self.normcolor
#        else:
#            c = self.color
#        mmprectype_name_color = "%s (%s) " % (self.mmp_record_name, name)
#        return mmprectype_name_color

    def anchors_atom(self, atm):
        "does this jig hold this atom fixed in space? [overrides Jig method]"
        return False # Not sure this method is needed.  Ask Bruce.  Mark 050925.

    def confers_properties_on(self, atom): # Atom Set method
        """[overrides Node method]
        Should this jig be partly copied (even if not selected)
        when this atom is individually selected and copied?
        (It's ok to assume without checking that atom is one of this jig's atoms.)
        """
        return False # Need to ask Bruce about this, too.  Mark 050925.
    
    pass # end of class AtomSet

class jigmakers_Mixin: #bruce 050507 moved these here from part.py
    """Provide Jig-making methods to class Part.
    These should be refactored into some common code
    and new methods in the specific Jig subclasses.
    """

    def makeRotaryMotor(self, sightline):
        """Creates a Rotary Motor connected to the selected atoms.
        """

        del sightline
        glpane = self.assy.o #e this should be an argument. to be fixed soon. [bruce 060120]
        "glpane is used for its point-of-view attributes" #e and after A7 a new "view object" should be passed instead.
                
        cmd = greenmsg("Rotary Motor: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change
        
        if len(atoms) < 2: # wware 051216, bug 1114, need >= 2 atoms for rotary motor
            env.history.message(cmd + redmsg("You must select at least two atoms to create a Rotary Motor."))
            return
            
        # Print warning if over 200 atoms are selected.
        if atom_limit_exceeded_and_confirmed(self.assy.w, len(atoms), limit=200):
            return
        
        from jigs_motors import RotaryMotor
        m = RotaryMotor(self.assy)
        m.findCenterAndAxis(atoms, glpane) # also puts up dialog
        if m.cancelled: # user hit Cancel button in Rotary Motory Dialog.
            #bruce 050415/050701: old code had del(m), perhaps hoping to destroy the jig here,
            # but in fact that statement would do nothing, so I removed it. But it might be good
            # to actually destroy the jig object here (for all jigs which can be cancelled, not
            # only this one), to avoid a memory leak. Presently, jigs don't have a destroy method.
            env.history.message(cmd + "Cancelled")
            return
        self.unpickatoms()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Motor created")
        self.assy.w.win_update()
      
    def makeLinearMotor(self, sightline):
        """Creates a Linear Motor connected to the selected atoms.
        """

        del sightline
        glpane = self.assy.o # see comments in RotaryMotor case [bruce 060120]
        "glpane is used for its point-of-view attributes"
        
        cmd = greenmsg("Linear Motor: ")
        
        atoms = self.assy.selatoms_list() #bruce 051031 change

        if not atoms:
            env.history.message(cmd + redmsg("At least one atom must be selected to create a Linear Motor."))
            return
            
        # Print warning if over 200 atoms are selected.
        if atom_limit_exceeded_and_confirmed(self.assy.w, len(atoms), limit=200):
            return
        
        from jigs_motors import LinearMotor
        m = LinearMotor(self.assy)
        m.findCenterAndAxis(atoms, glpane)
        if m.cancelled: # user hit Cancel button in Linear Motory Dialog.
            env.history.message(cmd + "Cancelled")
            return
        self.unpickatoms()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Motor created")
        self.assy.w.win_update()

    def makegamess(self):
        """Makes a GAMESS jig...
        """
        # [bruce 050210 modified docstring]
        
        cmd = greenmsg("Gamess: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change
        
        if not atoms:
            env.history.message(cmd + redmsg("At least one atom must be selected to create a Gamess Jig."))
            return
        
        # Make sure that no more than 200 atoms are selected.
        nsa = len(atoms)
        if nsa > 200: 
            env.history.message(cmd + redmsg(str(nsa) + " atoms selected.  The limit is 200.  Try again."))
            return
        
        # Bug 742.    Mark 050731.
        if nsa > 50:
            ret = QMessageBox.warning( self.assy.w, "Large GAMESS Jig",
                "GAMESS Jigs with more than 50 atoms may take an\n"
                "excessively long time to compute (days or weeks).\n"
                "Are you sure you want to continue?",
                "&Continue", "Cancel", None,
                0, 1 )
                
            if ret==1: # Cancel
                return
                
        from jig_Gamess import Gamess
        m = Gamess(self.assy, atoms)
        m.edit() #bruce 050701 split edit method out of the constructor,
            # so the dialog doesn't show up when the jig is read from an mmp file
        if m.cancelled: # User hit 'Cancel' button in the jig dialog.
            #bruce 050701 comment: I haven't reviewed this for correctness since the above change.
            env.history.message(cmd + "Cancelled")
            return
        self.unpickatoms()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Gamess Jig created")
        self.assy.w.win_update()
        
    def makeAnchor(self):
        """Anchors the selected atoms so that they will not move during a minimization or simulation run.
        """
        # [bruce 050210 modified docstring]
        # [mark 051104 modified docstring]
        
        cmd = greenmsg("Anchor: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change
        
        if not atoms:
            env.history.message(cmd + redmsg("You must select at least one atom to create an Anchor."))
            return
        
        # Print warning if over 200 atoms are selected.
        if atom_limit_exceeded_and_confirmed(self.assy.w, len(atoms), limit=200):
            return

        m = Anchor(self.assy, atoms)
        self.unpickatoms()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Anchor created")
        self.assy.w.win_update()

    def makestat(self):
        """Attaches a Langevin thermostat to the single atom selected.
        """
        cmd = greenmsg("Thermostat: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change
        
        if not atoms:
            msg = redmsg("You must select an atom on the molecule you want to associate with a Thermostat.")
            env.history.message(cmd + msg)
            return
        
        # Make sure only one atom is selected.
        if len(atoms) != 1: 
            msg = redmsg("To create a Thermostat, only one atom may be selected.  Try again.")
            env.history.message(cmd + msg)
            return
        m = Stat(self.assy, atoms)
        self.unpickatoms()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Thermostat created")
        self.assy.w.win_update()
        
    def makethermo(self):
        """Attaches a thermometer to the single atom selected.
        """
        
        cmd = greenmsg("Thermometer: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change
        
        if not atoms:
            msg = redmsg("You must select an atom on the molecule you want to associate with a Thermometer.")
            env.history.message(cmd + msg)
            return
        
        # Make sure only one atom is selected.
        if len(atoms) != 1: 
            msg = redmsg("To create a Thermometer, only one atom may be selected.  Try again.")
            env.history.message(cmd + msg)
            return
        
        m = Thermo(self.assy, atoms)
        self.unpickatoms()
        self.place_new_jig(m)
        
        env.history.message(cmd + "Thermometer created")
        self.assy.w.win_update()
        
        
    def makeGridPlane(self):
        cmd = greenmsg("Grid Plane: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change
        
        if not atoms:
            msg = redmsg("You must select 3 or more atoms to create a Grid Plane.")
            env.history.message(cmd + msg)
            return
        
        # Make sure only one atom is selected.
        if len(atoms) < 3: 
            msg = redmsg("To create a Grid Plane, at least 3 atoms must be selected.  Try again.")
            env.history.message(cmd + msg)
            return
        
        from jigs_planes import GridPlane
        m = GridPlane(self.assy, atoms)
        m.edit()
        if m.cancelled: # User hit 'Cancel' button in the jig dialog.
            #bruce 050701 comment: I haven't reviewed this for correctness since the above change.
            env.history.message(cmd + "Cancelled")
            return 
        
        self.unpickatoms()
        self.place_new_jig(m)
        
        #After placing the jig, remove the atom list from the jig.
        m.atoms = []
      
        env.history.message(cmd + "Grid Plane created")
        self.assy.w.win_update()
        
        
    def makeESPImage(self):
        cmd = greenmsg("ESP Image: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change

        if len(atoms) < 3:
            msg = redmsg("You must select at least 3 atoms to create an ESP Image.")
            env.history.message(cmd + msg)
            return
        
        from jigs_planes import ESPImage
        m = ESPImage(self.assy, atoms)
        m.edit()
        if m.cancelled: # User hit 'Cancel' button in the jig dialog.
            env.history.message(cmd + "Cancelled")
            return 
        
        self.unpickatoms()
        self.place_new_jig(m)
        
        #After placing the jig, remove the atom list from the jig.
        m.atoms = []
        
        env.history.message(cmd + "ESP Image created.")
        self.assy.w.win_update()
           
        
    def makeAtomSet(self):
        cmd = greenmsg("Atom Set: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change

        if not atoms:
            env.history.message(cmd + redmsg("You must select at least one atom to create an Atom Set."))
            return
            
        # Print warning if over 200 atoms are selected.
        if atom_limit_exceeded_and_confirmed(self.assy.w, len(atoms), limit=200):
            return
        
        m = AtomSet(self.assy, atoms)
        
        self.place_new_jig(m)
        m.pick() # This is required to display the Atom Set wireframe boxes.
        
        env.history.message(cmd + "Atom Set created.")
        self.assy.w.win_update()
        

    def makeMeasureDistance(self):
        """Creates a Measure Distance jig between two selected atoms.
        """
        
        cmd = greenmsg("Measure Distance Jig: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change

        if len(atoms) != 2:
            msg = redmsg("You must select 2 atoms to create a Distance jig.")
            env.history.message(cmd + msg)
            return
        
        from jigs_measurements import MeasureDistance
        d = MeasureDistance(self.assy, atoms)
        self.unpickatoms()
        self.place_new_jig(d)
        
        env.history.message(cmd + "Measure Distance jig created")
        self.assy.w.win_update()


    def makeMeasureAngle(self): # Not implemented yet.  Mark 051030.
        """Creates a Measure Angle jig connected to three selected atoms.
        """
	# not disabled any more.  wware 051031
        
        cmd = greenmsg("Measure Angle Jig: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change

        if len(atoms) != 3:
            msg = redmsg("You must select 3 atoms to create an Angle jig.")
            env.history.message(cmd + msg)
            return
        
        from jigs_measurements import MeasureAngle
        d = MeasureAngle(self.assy, atoms)
        self.unpickatoms()
        self.place_new_jig(d)
        
        env.history.message(cmd + "Measure Angle jig created")
        self.assy.w.win_update()

    def makeMeasureDihedral(self): # Not implemented yet.  Mark 051030.
        """Creates a Measure Dihedral jig connected to three selected atoms.
        """
        cmd = greenmsg("Measure Dihedral Jig: ")

        atoms = self.assy.selatoms_list() #bruce 051031 change

        if len(atoms) != 4:
            msg = redmsg("You must select 4 atoms to create a Dihedral jig.")
            env.history.message(cmd + msg)
            return
        
        from jigs_measurements import MeasureDihedral
        d = MeasureDihedral(self.assy, atoms)
        self.unpickatoms()
        self.place_new_jig(d)
        
        env.history.message(cmd + "Measure Dihedral jig created")
        self.assy.w.win_update()
        
    pass # end of class jigmakers_Mixin

def atom_limit_exceeded_and_confirmed(parent, natoms, limit=200):
    '''Displays a warning message if 'natoms' exceeds 'limit'.
    Returns False if the number of atoms does not exceed the limit or if the 
    user confirms that the jigs should still be created even though the limit was 
    exceeded.
    If parent is 0, the message box becomes an application-global modal dialog box. 
    If parent is a widget, the message box becomes modal relative to parent. 
    '''
    
    if natoms < limit:
        return False # Atom limit not exceeded.

    # Is this warning message OK? Ask Bruce and Ninad what they think.  Mark 051122.
    wmsg = "Warning: Creating a jig with " + str(natoms) \
        + " atoms may degrade performance.\nDo you still want to add the jig?"
    
    dialog = QMessageBox("Warning", wmsg, 
                    QMessageBox.Warning, 
                    QMessageBox.Yes, 
                    QMessageBox.No, 
                    QMessageBox.NoButton, 
                    parent)

    # We want to add a "Do not show this message again." checkbox to the dialog like this:
    #     checkbox = QCheckBox("Do not show this message again.", dialog)
    # The line of code above works, but places the checkbox in the upperleft corner of the dialog, 
    # obscuring important text.  I'll fix this later. Mark 051122.

    ret = dialog.exec_loop()

    if ret != QMessageBox.Yes:
        return True
    
    # Print warning msg in history widget whenever the user adds new jigs with more than 'limit' atoms.
    wmsg = "Warning: " + str(natoms) + " atoms selected.  A jig with more than " \
        + str(limit) + " atoms may degrade performance."
    env.history.message(orangemsg(wmsg))
        
    return False
            
# end of module jigs.py
