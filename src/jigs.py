# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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
"""

from VQT import *
from drawer import drawsphere, drawcylinder, drawline, drawaxes
from drawer import segstart, drawsegment, segend, drawwirecube
from shape import *
from chem import *
import OpenGL.GLUT as glut
from Utility import *
from RotaryMotorProp import *
from LinearMotorProp import *
from GroundProp import *
from StatProp import *
from ThermoProp import *
from HistoryWidget import redmsg
from povheader import povpoint #bruce 050413

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
    
    #e we should sometime clean up the normcolor and color attributes, but it's hard,
    # since they're used strangly in the *Prop.py files and in our pick and unpick methods.
    # But at least we'll give them default values for the sake of new jig subclasses. [bruce 050425]
    color = normcolor = (0.5, 0.5, 0.5)
    
    def __init__(self, assy, atomlist):
        "each subclass needs to call this, at least sometime before it's used as a Node"
        Node.__init__(self, assy, gensym("%s." % self.sym))
        self.atoms = list(atomlist) # this is always [] for some subclasses
            # but is apparently required to be always nonempty for others
            # bruce 050316: copy it (precaution in case caller modifies it later)
        # [note: the following is what our setAtoms method does for some jigs]
        #e should we split this jig if attached to more than one mol??
        # not necessarily, tho the code to update its appearance
        # when one of the atoms move is not yet present. [bruce 041202]
        for a in atomlist:
            a.jigs += [self]
        #e it might make sense to init other attrs here too, like color
        ## this is now the default for all Nodes [050505]: self.disabled_by_user_choice = False #bruce 050421
        return

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
            a.jigs += [self]
            
    def copy(self, dad):
        self.assy.w.history.message( redmsg("Jigs cannot yet be copied"))
        #bruce 050420 comment: see comments in Csys.copy.
        return None
        
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
        if not self.atoms:
            self.kill()
        return
    
    def kill(self):
        # bruce 050215 modified this to remove self from our atoms' jiglists, via rematom
        for atm in self.atoms[:]: #bruce 050316: copy the list (presumably a bugfix)
            self.rematom(atm) # the last one removed kills the jig recursively!
        Node.kill(self) # might happen twice, that's ok

    # bruce 050125 centralized pick and unpick (they were identical on all Jig
    # subclasses -- with identical bugs!), added comments; didn't yet fix the bugs.
    #bruce 050131 for Alpha: more changes to it (still needs review after Alpha is out)
    
    def pick(self): 
        """select the Jig"""
        if self.assy is not None:
            #bruce 050419 add 'if' as quick safety hack re bug 451-9 (not a real fix, but removes the traceback) ###@@@
            self.assy.w.history.message(self.getinfo()) 
        if not self.picked: #bruce 050131 added this condition (maybe good for history.message too?)
            Node.pick(self) #bruce 050131 for Alpha: using Node.pick
            self.normcolor = self.color # bug if this is done twice in a row! [bruce 050131 maybe fixed now due to the 'if']
            self.color = self.pickcolor
        return

    def unpick(self):
        """unselect the Jig"""
        if self.picked:
            Node.unpick(self) # bruce 050126 -- required now
            self.color = self.normcolor

    def move(self, offset):
        #bruce 050208 made this default method. Is it ever called, in any subclasses??
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

    def mmp_record(self, mapping = None):
        #bruce 050422 factored this out of all the existing Jig subclasses, changed arg from ndix to mapping
        #e could factor some code from here into mapping methods
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
        if mapping:
            ndix = mapping.atnums
        else:
            ndix = None
        nums = self.atnums_or_None( ndix)
        del ndix
        if nums is None or (self.is_disabled() and mapping.not_yet_past_where_sim_stops_reading_the_file()):
            # We need to return a forward ref record now, and set up mapping object to write us out for real, later.
            # This means figuring out when to write us... and rather than ask atnums_or_None for more help on that,
            # we use a variant of the code that used to actually move us before writing the file (since that's easiest for now).
            # But at least we can get mapping to do most of the work for us, if we tell it which nodes we need to come after,
            # and whether we insist on being invisible to the simulator even if we don't have to be
            # (since all our atoms are visible to it).
            ref_id = mapping.node_ref_id(self) #e should this only be known to a mapping method which gives us the fwdref record??
            mmprectype_name = "%s (%s)" % (self.mmp_record_name, self.name)
            fwd_ref_to_return_now = "forward_ref (%s) # %s\n" % (str(ref_id), mmprectype_name) # the stuff after '#' is just a comment
            after_these = self.node_must_follow_what_nodes()
            assert after_these # but this alone does not assert that they weren't all already written out! The next method should do that.
            mapping.write_forwarded_node_after_nodes( self, after_these, force_disabled_for_sim = self.is_disabled() )
            return fwd_ref_to_return_now , False
        atnums_list = " ".join(map(str,nums))
        if self.picked:
            c = self.normcolor
            # [bruce 050422 comment: this code looks weird, but i guess it undoes pick effect on color]
        else:
            c = self.color
        color = map(int,A(c)*255)
        mmprectype_name_color = "%s (%s) (%d, %d, %d)" % (self.mmp_record_name, self.name, color[0], color[1], color[2])
        midpart = self.mmp_record_jigspecific_midpart()
        if not midpart:
            # because '  ' fails where ' ' is required (in the mmp file parser), we have to handle this case specially!
            return mmprectype_name_color + " " + atnums_list + "\n" , True
        return mmprectype_name_color + " " + midpart + " " +  atnums_list + "\n" , True

    def mmp_record_jigspecific_midpart(self):
        """#doc
        (see rmotor's version's docstring for details)
        [some subclasses need to override this]
        """
        return ""

    def atnums_or_None(self, ndix):
        """Return list of atnums to write, as ints(??) (using ndix to encode them),
        or None if some atoms were not yet written to the file.
        (If ndix not supplied, as when we're called by __repr__, use atom keys for atnums.)
        [Jig method; overridden by some subclasses]
        """
        if ndix:
            try:
                nums = map((lambda a: ndix[a.key]), self.atoms)
            except KeyError: # assume this is from ndix not containing a.key
                # too soon to write this jig -- would require forward ref to an atom, which mmp format doesn't support
                return None
        else:
            nums = map((lambda a: a.key), self.atoms)
        return nums

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
                #e We might want to loosen this for a Ground (and only disable the atoms in a different Part),
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

    def draw(self, win, dispdef): #bruce 050421 added this wrapper method and renamed the subclass methods it calls. ###@@@writepov too
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
            self._draw(win, dispdef)
        except:
            print_compact_traceback("exception in drawing jig ignored: ") #bruce 050518
            # this is verbose, but it's a true serious error that needs to be known about
        
        if disabled:
            glEnable(GL_CULL_FACE)
            glEnable(GL_LIGHTING)
            glPolygonMode(GL_FRONT, GL_FILL)
            glDisable(GL_LINE_STIPPLE)
        return

    #e there might be other common methods to pull into here

    pass # end of class Jig

# == Motors

class RotaryMotor(Jig):
    '''A Rotary Motor has an axis, represented as a point and
       a direction vector, a stall torque, a no-load speed, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''
    
    sym = "Rotary Motor"
    icon_names = ["rmotor.png", "rmotor-hide.png"]

    # create a blank Rotary Motor not connected to anything    
    def __init__(self, assy):
        Jig.__init__(self, assy, [])
        self.torque = 0.0 # in nN * nm
        self.speed = 0.0 # in gHz
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self._initial_posns = None #bruce 050518
            # We need to reset _initial_posns to None whenever we recompute
            # self.axis from scratch or change the atom list in any way (even reordering it).
            # For now, we do this everywhere it's needed "by hand",
            # rather than in some (not yet existing) systematic and general way.
        self.color = self.normcolor = (0.5, 0.5, 0.5) # default color = gray
        self.length = 10.0 # default length of Rotary Motor cylinder
        self.radius = 2.0 # default cylinder radius
        self.sradius = 0.5 #default spoke radius
        # Should self.cancelled be in RotaryMotorProp.setup? - Mark 050109
        self.cancelled = True # We will assume the user will cancel
        self.cntl = RotaryMotorProp(self, assy.o)

    # set the properties for a Rotary Motor read from a (MMP) file
    def setProps(self, name, color, torque, speed, center, axis, length, radius, sradius):
        self.name = name
        self.color = color
        self.torque = torque
        self.speed = speed
        self.center = center
        self.axis = norm(axis)
        self._initial_posns = None #bruce 050518
        self.length = length
        self.radius = radius
        self.sradius = sradius

    # for a motor read from a file, the "shaft" record
    def setShaft(self, shft):
        self.setAtoms(shft) #bruce 041105 code cleanup
        self._initial_posns = None #bruce 050518

    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shft, los):
        self.setAtoms(shft) #bruce 041105 code cleanup
        # array of absolute atom positions
        self.recompute_center_axis(los)
        self.edit()

    def recompute_center_axis(self, los = None): #bruce 050518 split this out of findCenter, for use in a new cmenu item
        if los is None:
            los = self.assy.o.lineOfSight
        shft = self.atoms
        # remaining code is a kluge, according to the comment above findcenter;
        # note that it depends on order of atoms, presumably initially derived
        # from the selatoms dict and thus arbitrary (not even related to order
        # in which user selected them or created them). [bruce 050518 comment]
        pos=A(map((lambda a: a.posn()), shft))
        self.center=sum(pos)/len(pos)
        relpos=pos-self.center
        if len(shft) == 1:
            self.axis = norm(los)
        elif len(shft) == 2:
            self.axis = norm(cross(relpos[0],cross(relpos[1],los)))
        else:
            guess = map(cross, relpos[:-1], relpos[1:])
            guess = map(lambda x: sign(dot(los,x))*x, guess)
            self.axis=norm(sum(guess))
        self._initial_posns = None
        return

    def recenter_on_atoms(self):
        "called from model tree cmenu command"
        self.recompute_center_axis()
        #e maybe return whether we moved??
        return
    
    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    def move(self, offset): #k can this ever be called?
        self.center += offset

    def posn(self):
        return self.center

    def axen(self):
        return self.axis
   
    def _getinfo(self):
        return "[Object: Rotary Motor] [Name: " + str(self.name) + "] [Torque = " + str(self.torque) + "] [Speed = " +str(self.speed) + "]"
        
    def getstatistics(self, stats):
        stats.nrmotors += 1

    def rematom(self, *args, **opts): #bruce 050518
        self._initial_posns = None
        super = Jig
        return super.rematom(self, *args, **opts)

    def norm_project_posns(self, posns):
        """[Private helper for getrotation]
        Given a Numeric array of position vectors relative to self.center,
        project them along self.axis and normalize them (and return that --
        but we take ownership of posns passed to us, so we might or might not
        modify it and might or might not return the same (modified) object.
        """
        axis = self.axis
        dots = dot(posns, axis)
        ## axis_times_dots = axis * dots #  guess from this line: exceptions.ValueError: frames are not aligned
        axis_times_dots = A(len(dots) * [axis]) * reshape(dots,(len(dots),1)) #k would it be ok to just use axis * ... instead?
        posns -= axis_times_dots
        ##posns = norm(posns) # some exception from this
        posns = A(map(norm, posns))
            # assumes no posns are right on the axis! now we think they are on a unit circle perp to the axis...
        # posns are now projected to a plane perp to axis and centered on self.center, and turned into unit-length vectors.
        return posns # (note: in this implem, we did modify the mutable argument posns, but are returning a different object anyway.)
        
    def getrotation(self): #bruce 050518 new feature for showing rotation of rmotor in its cap-arrow
        """Return a rotation angle for the motor. This is arbitrary, but rotates smoothly
        with the atoms, averaging out their individual thermal motion.
        It is not history-dependent -- e.g. it will be consistent regardless of how you jump around
        among the frames of a movie. But if we ever implement remaking or revising the motor position,
        or if you delete some of the motor's atoms, this angle is forgotten and essentially resets to 0.
        (That could be fixed, and the angle even saved in the mmp file, if desired. See code comments
        for other possible improvements.)
        """
        # possible future enhancements:
        # - might need to preserve rotation when we forget old posns, by setting an arb offset then;
        # - might need to preserve it in mmp file??
        # - might need to draw it into PovRay file??
        # - might need to preserve it when we translate or rotate entire jig with its atoms (doing which is NIM for now)
        # - could improve and generalize alg, and/or have sim do it (see comments below for details).
        #
        posns = A(map( lambda a: a.posn(), self.atoms ))
        posns -= self.center
        if self._initial_posns is None:
            # (we did this after -= center, so no need to forget posns if we translate the entire jig)
            self._initial_posns = posns # note, we're storing *relative* positions, in spite of the name!
            self._initial_quats = None # compute these the first time they're needed (since maybe never needed)
            return 0.0 # returning this now (rather than computing it below) is just an optim, in theory
        assert len(self._initial_posns) == len(posns), "bug in invalidating self._initial_posns when rmotor atoms change"
        if not (self._initial_posns != posns): # have to use not(x!=y) rather than (x==y) due to Numeric semantics!
            # no (noticable) change in positions - return quickly
            # (but don't change stored posns, in case this misses tiny changes which could accumulate over time)
            # (we do this before the subsequent stuff, to not waste redraw time when posns don't change;
            #  just re correctness, we could do it at a later stage)
            return 0.0
        # now we know the posns are different, and we have the old ones to compare them to.
        posns = self.norm_project_posns( posns) # this might modify posns object, and might return same or different object
        quats = self._initial_quats
        if quats is None:
            # precompute a quat to rotate new posns into a standard coord system for comparison to old ones
            # (Q args must be orthonormal and right-handed)
            oldposns = + self._initial_posns # don't modify those stored initial posns
                # (though it probably wouldn't matter if we did -- from now on,
                #  they are only compared to None and checked for length, as of 050518)
            oldposns = self.norm_project_posns( oldposns)
            axis = self.axis
            quats = self._initial_quats = [ Q(axis,pos1,cross(axis,pos1)) for pos1 in oldposns ]
        angs = []
        for qq, pos2 in zip( self._initial_quats, posns):
            npos2 = qq.unrot(pos2)
            # now npos2 is in yz plane, and pos1 (if transformed) would just be the y axis in that plane;
            # just get its angle in that plane (defined so that if pos2 = pos1, ie npos2 = (0,1,0), then angle is 0)
            ang = angle(npos2[1], npos2[2]) # in degrees
            angs.append(ang)
        # now average these angles, paying attention to their being on a circle
        # (which means the average of 1 and 359 is 0, not 180!)
        angs.sort()
            # Warning: this sort is only correct since we know they're in the range [0,360] (inclusive range is ok).
            # It might be correct for any range that covers the circle exactly once, e.g. [-180,180]
            # (not fully analyzed for that), but it would definitely be wrong for e.g. [-0.001, 360.001]!
            # So be careful if you change how angle() works.
        angs = A(angs)
        gaps = angs[1:] - angs[:-1]
        gaps = [angs[0] - angs[-1] + 360] + list(gaps)
        i = argmax(gaps)
        ##e Someday we should check whether this largest gap is large enough for this to make sense (>>180);
        # we are treating the angles as "clustered together in the part of the circle other than this gap"
        # and averaging them within that cluster. It would also make sense to discard outliers,
        # but doing this without jittering the rotation angle (as individual points become closer
        # to being outliers) would be challenging. Maybe better to just give up unless gap is, say, >>340.
        ##e Before any of that, just get the sim to do this in a better way -- interpret the complete set of
        # atom motions as approximating some overall translation and rotation, and tell us this, so we can show
        # not only rotation, but axis wobble and misalignment, and so these can be plotted.
        angs = list(angs)
        angs = angs[i:] + angs[:i] # start with the one just after the largest gap
        relang0 = angs[0]
        angs = A(angs) - relang0 # be relative to that, when we average them
        # but let them all be in the range [0,360)!
        angs = (angs + 720) % 360
            # We need to add 720 since Numeric's mod produces negative outputs
            # for negative inputs (unlike Python's native mod, which is correct)!
            # How amazingly ridiculous.
        ang = (sum(angs) / len(angs)) + relang0
        ang = ang % 360 # this is Python mod, so it's safe
        return ang
        
    # Rotary Motor is drawn as a cylinder along the axis,
    #  with a spoke to each atom
    def _draw(self, win, dispdef):
        bCenter = self.center - (self.length / 2.0) * self.axis
        tCenter = self.center + (self.length / 2.0) * self.axis
        drawcylinder(self.color, bCenter, tCenter, self.radius, 1 )
        for a in self.atoms:
            drawcylinder(self.color, self.center, a.posn(), self.sradius)
        rotby = self.getrotation() #bruce 050518
            # if exception in getrotation, just don't draw the rotation sign
            # (safest now that people might believe what it shows about amount of rotation)
        drawRotateSign((0,0,0), bCenter, tCenter, self.radius, rotation = rotby)
        return
    
    # Write "rmotor" and "spoke" records to POV-Ray file in the format:
    # rmotor(<cap-point>, <base-point>, cylinder-radius, <r, g, b>)
    # spoke(<cap-point>, <base-point>, scylinder-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        c = self.posn()
        a = self.axen()
        file.write("rmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + povpoint(c-(self.length / 2.0)*a)  + "," + str (self.radius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn()) + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
    
    # Returns the jig-specific mmp data for the current Rotary Motor as:
    #    torque speed (cx, cy, cz) (ax, ay, az) length radius sradius \n shaft
    mmp_record_name = "rmotor"
    def mmp_record_jigspecific_midpart(self):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        dataline = "%.2f %.2f (%d, %d, %d) (%d, %d, %d) %.2f %.2f %.2f" % \
           (self.torque, self.speed,
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]),
            self.length, self.radius, self.sradius   )
        return dataline + "\n" + "shaft"
    
    pass # end of class RotaryMotor

def angle(x,y): #bruce 050518; see also atan2 (noticed used in VQT.py) which might do roughly the same thing
    """Return the angle above the x axis of the line from 0,0 to x,y,
    in a numerically stable way, assuming vlen(V(x,y)) is very close to 1.0.
    """
    if y < 0: return 360 - angle(x,-y)
    if x < 0: return 180 - angle(-x,y)
    if y > x: return 90 - angle(y,x)
    #e here we could normalize length if we felt like it,
    # and/or repair any glitches in continuity at exactly 45 degrees
    res = asin(y)*180/pi
    #print "angle(%r,%r) -> %r" % (x,y,res) 
    if res < 0:
        return res + 360 # should never happen
    return res

# ==

class LinearMotor(Jig):
    '''A Linear Motor has an axis, represented as a point and
       a direction vector, a force, a stiffness, and
       a set of atoms connected to it
       To Be Done -- selecting & manipulation'''

    sym = "Linear Motor"
    icon_names = ["lmotor.png", "lmotor-hide.png"]

    # create a blank Linear Motor not connected to anything
    def __init__(self, assy):
        Jig.__init__(self, assy, [])
        
        self.force = 0.0
        self.stiffness = 0.0
        self.center = V(0,0,0)
        self.axis = V(0,0,0)
        self.color = self.normcolor = (0.5, 0.5, 0.5) # default color = gray
        self.length = 10.0 # default length of Linear Motor box
        self.width = 2.0 # default box width
        self.sradius = 0.5 #default spoke radius
        self.cancelled = True # We will assume the user will cancel
        self.cntl = LinearMotorProp(self, assy.o)

    # set the properties for a Linear Motor read from a (MMP) file
    def setProps(self, name, color, force, stiffness, center, axis, length, width, sradius):
        self.name = name
        self.color = color
        self.force = force
        self.stiffness = stiffness
        self.center = center
        self.axis = norm(axis)
        self.length = length
        self.width = width
        self.sradius = sradius

    # for a linear motor read from a file, the "shaft" record
    def setShaft(self, shaft):
        self.setAtoms(shaft) #bruce 041105 code cleanup
 
    # for a motor created by the UI, center is average point and
    # axis (kludge) is the average of the cross products of
    # vectors from the center to successive points
    # los is line of sight into the screen
    def findCenter(self, shft, los):
        self.setAtoms(shft) #bruce 041105 code cleanup
        # array of absolute atom positions
        # can't use xyz, might be from different molecules
        pos=A(map((lambda a: a.posn()), shft))
        self.center=sum(pos)/len(pos)
        relpos=pos-self.center
        if len(shft) == 1:
            self.axis = norm(los)
        elif len(shft) == 2:
            self.axis = norm(cross(relpos[0],cross(relpos[1],los)))
        else:
            guess = map(cross, relpos[:-1], relpos[1:])
            guess = map(lambda x: sign(dot(los,x))*x, guess)
            self.axis=norm(sum(guess))
        self.edit()

    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()
        
    def move(self, offset):
        self.center += offset

    def posn(self):
        return self.center

    def axen(self):
        return self.axis
   
    def _getinfo(self):
        return "[Object: Linear Motor] [Name: " + str(self.name) + \
                    "] [Force = " + str(self.force) + \
                    "] [Stiffness = " +str(self.stiffness) + "]"

    def getstatistics(self, stats):
        stats.nlmotors += 1
   
    # drawn as a gray box along the axis,
    # with a thin cylinder to each atom 
    def _draw(self, win, dispdef):
        drawbrick(self.color, self.center, self.axis, self.length, self.width, self.width)
        drawLinearSign((0,0,0), self.center, self.axis, self.length, self.width, self.width)
        for a in self.atoms:
            drawcylinder(self.color, self.center, a.posn(), self.sradius)

            
    # Write "lmotor" and "spoke" records to POV-Ray file in the format:
    # lmotor(<cap-point>, <base-point>, box-width, <r, g, b>)
    # spoke(<cap-point>, <base-point>, sbox-radius, <r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        c = self.posn()
        a = self.axen()
        file.write("lmotor(" + povpoint(c+(self.length / 2.0)*a) + "," + 
                    povpoint(c-(self.length / 2.0)*a)  + "," + str (self.width / 2.0) + 
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
        for a in self.atoms:
            file.write("spoke(" + povpoint(c) + "," + povpoint(a.posn())  + "," + str (self.sradius) +
                    ",<" + str(self.color[0]) + "," + str(self.color[1]) + "," + str(self.color[2]) + ">)\n")
    
    # Returns the jig-specific mmp data for the current Linear Motor as:
    #    stiffness force (cx, cy, cz) (ax, ay, az) length width sradius \n shaft
    mmp_record_name = "lmotor"
    def mmp_record_jigspecific_midpart(self):
        cxyz = self.posn() * 1000
        axyz = self.axen() * 1000
        dataline = "%.2f %.2f (%d, %d, %d) (%d, %d, %d) %.2f %.2f %.2f" % \
           (self.stiffness, self.force, 
            int(cxyz[0]), int(cxyz[1]), int(cxyz[2]),
            int(axyz[0]), int(axyz[1]), int(axyz[2]),
            self.length, self.width, self.sradius    )
        return dataline + "\n" + "shaft"
    
    pass # end of class LinearMotor

# == Ground

class Ground(Jig):
    '''a Ground just has a list of atoms that are anchored in space'''

    sym = "Ground"
    icon_names = ["ground.png", "ground-hide.png"]

    # create a blank Ground with the given list of atoms
    def __init__(self, assy, list):
        Jig.__init__(self, assy, list)
        self.color = (0.0, 0.0, 0.0)
        self.normcolor = (0.0, 0.0, 0.0) # set default color of ground to black
        self.cntl = GroundProp(self, assy.o)

    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    # it's drawn as a wire cube around each atom (default color = black)
    def _draw(self, win, dispdef):
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            drawwirecube(self.color, a.posn(), rad)
            
    # Write "ground" record to POV-Ray file in the format:
    # ground(<box-center>,box-radius,<r, g, b>)
    def writepov(self, file, dispdef):
        if self.hidden: return
        if self.is_disabled(): return #bruce 050421
        if self.picked: c = self.normcolor
        else: c = self.color
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
            grec = "ground(" + povpoint(a.posn()) + "," + str(rad) + ",<" + str(c[0]) + "," + str(c[1]) + "," + str(c[2]) + ">)\n"
            file.write(grec)

    def _getinfo(self):
        return "[Object: Ground] [Name: " + str(self.name) + "] [Total Grounds: " + str(len(self.atoms)) + "]"

    def getstatistics(self, stats):
        stats.ngrounds += len(self.atoms)

    mmp_record_name = "ground"
    def mmp_record_jigspecific_midpart(self): # see also fake_Ground_mmp_record [bruce 050404]
        return ""

    def anchors_atom(self, atm): #bruce 050321; revised 050423 (warning: quadratic time for large ground jigs in Minimize)
        "does this jig hold this atom fixed in space? [overrides Jig method]"
        return (atm in self.atoms) and not self.is_disabled()
    
    pass # end of class Ground

def fake_Ground_mmp_record(atoms, mapping): #bruce 050404 utility for Minimize Selection
    """Return an mmp record (one or more lines with \n at end)
    for a fake Ground jig for use in an mmp file meant only for simulator input.
       Note: unlike creating and writing out a new real Ground object,
    which adds itself to each involved atom's .jigs list (perhaps just temporarily),
    perhaps causing unwanted side effects (like calling some .changed() method),
    this function has no side effects.
    """
    ndix = mapping.atnums
    c = black
    color = map(int,A(c)*255)
    s = "ground (%s) (%d, %d, %d) " % ("name", color[0], color[1], color[2])
    nums = map((lambda a: ndix[a.key]), atoms)
    return s + " ".join(map(str,nums)) + "\n"

# == Stat and Thermo

class Jig_onChunk_by1atom( Jig ):
    """Subclass for Stat and Thermo, which are on one atom in cad code,
    but on its whole chunk in simulator,
    by means of being written into mmp file as the min and max atnums in that chunk
    (whose atoms always occupy a contiguous range of atnums, since those are remade per writemmp event),
    plus the atnum of their one user-visible atom.
    """
    def atnums_or_None(self, ndix):
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
                return None
            nums = [min(nums), max(nums), nums[0]]
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

    # create a blank Stat with the given list of atoms, set to 300K
    def __init__(self, assy, list):
        # ideally len(list) should be 1, but in case code in files_mmp uses more
        # when supporting old Stat records, all I assert here is that it's at
        # least 1, but I only store the first atom [bruce 050210]
        assert len(list) >= 1
        list = list[0:1]
        Jig.__init__(self, assy, list)
        # set default color of new stat to blue
        self.color = self.normcolor = (0.0, 0.0, 1.0) 
        self.temp = 300
        self.cntl = StatProp(self, assy.o)
    
    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    # it's drawn as a wire cube around each atom (default color = blue)
    def _draw(self, win, dispdef):
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
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
        return "(%d)" % int(self.temp)

    pass # end of class Stat


class Thermo(Jig_onChunk_by1atom):
    '''A Thermo is a thermometer which measures the temperature of a chunk
    during a simulation. A Thermo is defined and drawn on a single
    atom, but its record in an mmp file includes 3 atoms and applies to all
    atoms in the same chunk; for details see Stat docstring.
    '''
    #bruce 050210 for Alpha-2: fixed same bug as in Stat.
    sym = "Thermo"
    icon_names = ["thermo.png", "thermo-hide.png"]

    # creates a thermometer for a specific atom. "list" contains only one atom.
    def __init__(self, assy, list):
        # ideally len(list) should be 1, but in case code in files_mmp uses more
        # when supporting old Thermo records, all I assert here is that it's at
        # least 1, but I only store the first atom [bruce 050210]
        assert len(list) >= 1
        list = list[0:1]
        Jig.__init__(self, assy, list)
        # set default color of new thermo to dark red
        self.color = self.normcolor = (0.6, 0.0, 0.2) 
        self.cntl = ThermoProp(self, assy.o)
    
    def edit(self):
        self.cntl.setup()
        self.cntl.exec_loop()

    # it's drawn as a wire cube around each atom (default color = purple)
    def _draw(self, win, dispdef):
        for a in self.atoms:
            disp, rad = a.howdraw(dispdef)
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

# ===

class jigmakers_Mixin: #bruce 050507 moved these here from part.py
    """Provide Jig-making methods to class Part.
    These should be refactored into some common code
    and new methods in the specific Jig subclasses.
    """

    def makeRotaryMotor(self, sightline):
        """Creates a Rotary Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = RotaryMotor(self.assy)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Rotary Motory Dialog.
            del(m) #bruce comment 050223: this statement has no effect.
                # bruce 050415: I suspect it might cause bugs to not kill the jig now... untested.
                # [same issue exists for some other jigs too]
            return
        self.unpickatoms()
        self.place_new_jig(m)
      
    def makeLinearMotor(self, sightline):
        """Creates a Linear Motor connected to the selected atoms.
        There is a limit of 30 atoms.  Any more will choke the file parser
        in the simulator.
        """
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = LinearMotor(self.assy)
        m.findCenter(self.selatoms.values(), sightline)
        if m.cancelled: # user hit Cancel button in Linear Motory Dialog.
            del(m) #bruce comment 050223: this statement has no effect.
            return
        self.unpickatoms()
        self.place_new_jig(m)

    def makeground(self):
        """Grounds (anchors) all the selected atoms so that 
        they will not move during a simulation run.
        There is a limit of 30 atoms per Ground.  Any more will choke the file parser
        in the simulator. To work around this, just make more Grounds.
        """
        # [bruce 050210 modified docstring]
        if not self.selatoms: return
        if len(self.selatoms) > 30: return
        m = Ground(self.assy, self.selatoms.values())
        self.unpickatoms()
        self.place_new_jig(m)

    def makestat(self):
        """Attaches a Langevin thermostat to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m = Stat(self.assy, self.selatoms.values())
        self.unpickatoms()
        self.place_new_jig(m)
        
    def makethermo(self):
        """Attaches a thermometer to the single atom selected.
        """
        if not self.selatoms: return
        if len(self.selatoms) != 1: return
        m = Thermo(self.assy, self.selatoms.values())
        self.unpickatoms()
        self.place_new_jig(m)

    pass # end of class jigmakers_Mixin
    
# end of module jigs.py
