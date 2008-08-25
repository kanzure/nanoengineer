# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
BuildAtoms_GraphicsMode.py 

The GraphicsMode part of the BuildAtoms_Command. It provides the  graphicsMode 
object for its Command class. The GraphicsMode class defines anything related to
the *3D Graphics Area* -- 
For example: 
- Anything related to graphics (Draw method), 
- Mouse events
- Cursors, 
- Key bindings or context menu 

                        
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

TODO: [as of 2008-01-04]
- Items mentioned in Select_GraphicsMode.py 
- Some items mentioned in BuildAtoms_Command.py 

History:
See history for depositMode.py 
Ninad 2008-01-04: Created new Command and GraphicsMode classes from 
                  the old class depositMode and moved the 
                  GraphicsMode related methods into this class from 
                  depositMode.py
"""


import math
from Numeric import dot

from OpenGL.GL import GL_FALSE
from OpenGL.GL import glDepthMask
from OpenGL.GL import GL_TRUE
from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glColor4fv
from OpenGL.GL import GL_BLEND
from OpenGL.GL import GL_ONE_MINUS_SRC_ALPHA
from OpenGL.GL import GL_SRC_ALPHA
from OpenGL.GL import glBlendFunc
from OpenGL.GL import glTranslatef
from OpenGL.GL import glRotatef
from OpenGL.GL import GL_QUADS
from OpenGL.GL import glBegin
from OpenGL.GL import glVertex
from OpenGL.GL import glEnd
from OpenGL.GL import glDisable
from OpenGL.GL import glEnable
from OpenGL.GL import glPushMatrix
from OpenGL.GL import glPopMatrix

from OpenGL.GLU import gluUnProject


from PyQt4.Qt import Qt

import foundation.env as env
from utilities import debug_flags

from platform_dependent.PlatformDependent import fix_plurals

from model.chunk import Chunk
from model.chem import Atom
from model.chem import oneUnbonded
from model.elements import Singlet
from geometry.VQT import Q, A, norm, twistor

from graphics.drawing.CS_draw_primitives import drawline

from foundation.Group import Group
from foundation.Utility import Node
from commands.Select.Select_GraphicsMode import DRAG_STICKINESS_LIMIT
from graphics.behaviors.shape import get_selCurve_color

from model.bonds import bond_atoms, bond_at_singlets
from model.bond_constants import V_SINGLE

from utilities.debug import print_compact_stack

from utilities.constants import elemKeyTab
from utilities.constants import diINVISIBLE
from utilities.constants import diTUBES

from model.bond_constants import btype_from_v6
from model.bond_constants import V_DOUBLE
from model.bond_constants import V_GRAPHITE
from model.bond_constants import V_TRIPLE
from model.bond_constants import V_AROMATIC

from utilities.prefs_constants import buildModeSelectAtomsOfDepositedObjEnabled_prefs_key
from utilities.prefs_constants import buildModeWaterEnabled_prefs_key

from utilities.Log import orangemsg, redmsg

from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_basicGraphicsMode

_superclass = SelectAtoms_basicGraphicsMode

class BuildAtoms_basicGraphicsMode(SelectAtoms_basicGraphicsMode):
    """
    """
    bondclick_v6 = None
    gridColor = 74/255.0, 186/255.0, 226/255.0
    
    #Command will be set in BuildAtoms_GraphicsMode.__init__ . 
    command = None
        
    def reset_drag_vars(self):
        # called in Enter and at start of (super's) leftDown
        _superclass.reset_drag_vars(self)
        
        self.pivot = None
        self.pivax = None
        self.line = None
            # endpoints of the white line drawn between the cursor and a bondpoint when 
            # dragging a singlet.
        self.transdepositing = False
            # used to suppress multiple win_updates and history msgs when 
            #trans-depositing.
    
    def getCoords(self, event):
        """
        Retrieve the object coordinates of the point on the screen
        with window coordinates(int x, int y) 
        """
        # bruce 041207 comment: only called for depositMode leftDown in empty
        # space, to decide where to place a newly deposited chunk.
        # So it's a bit weird that it calls findpick at all!
        # In fact, the caller has already called a similar method indirectly
        # via update_selatom on the same event. BUT, that search for atoms might
        # have used a smaller radius than we do here, so this call of findpick
        # might sometimes cause the depth of a new chunk to be the same as an
        # existing atom instead of at the water surface. So I will leave it
        # alone for now, until I have a chance to review it with Josh [bug 269].
        # bruce 041214: it turns out it's intended, but only for atoms nearer
        # than the water! Awaiting another reply from Josh for details.
        # Until then, no changes and no reviews/bugfixes (eg for invisibles).
        # BTW this is now the only remaining call of findpick 
        # [still true 060316].
        # Best guess: this should ignore invisibles and be limited by water
        # and near clipping; but still use 2.0 radius. ###@@@

        # bruce 041214 comment: this looks like an inlined mousepoints...
        # but in fact [060316 addendum] it shares initial code with mousepoints,
        # but not all of mousepoints's code, so it makes sense to leave it as a
        # separate code snippet for now.
        x = event.pos().x()
        y = self.o.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.0))
        p2 = A(gluUnProject(x, y, 1.0))

        at = self.o.assy.findpick(p1,norm(p2-p1),2.0)
        if at:
            pnt = at.posn()
        else:
            pnt = - self.o.pov
        k = (dot(self.o.lineOfSight,  pnt - p1) /
             dot(self.o.lineOfSight, p2 - p1))

        return p1+k*(p2-p1) # always return a point on the line from p1 to p2
    
    # == LMB event handling methods ====================================
        
    def leftDouble(self, event): # mark 060126.
        """
        Double click event handler for the left mouse button. 
        """
        self.ignore_next_leftUp_event = True # Fixes bug 1467. mark 060307.
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            if self.o.tripleClick: # Fixes bug 2568. mark 2007-10-21
                return
            if self.o.modkeys != 'Shift+Control': # Fixes bug 1503.  mark 060224.
                deposited_obj = self.deposit_from_MMKit(self.getCoords(event)) # does win_update().
                if deposited_obj:
                    self.set_cmdname('Deposit ' + deposited_obj)
            return
            
        _superclass.leftDouble(self, event)
        
        return
        
    # == end of LMB event handler methods
    
    #====KeyPress =================
    
    def keyPress(self, key):
        for sym, code, num in elemKeyTab: 
            # Set the atom type in the MMKit and combobox.
            if key == code:
                self.command.setElement(num)
                # = REVIEW: should we add a 'return' here, to prevent the 
                # superclass from taking more actions from the same keyPress?
                #[bruce question 071012]
        
        # Pressing Escape does the following:
        # 1. If a Bond Tool or the Atom Selection Filter is enabled, 
        #  pressing Escape will activate the Atom Tool
        # and disable the Atom Selection Filter. The current selection remains 
        #unchanged, however.
        # 2. If the Atom Tool is enabled and the Atom Selection Filter is 
        #    disabled, Escape will clear the 
        #    current selection (when it's handled by our superclass's 
        #    keyPress method).
        # Fixes bug (nfr) 1770. mark 060402
        if key == Qt.Key_Escape and self.w.selection_filter_enabled:
            if hasattr(self.command, 'disable_selection_filter'):
                self.command.disable_selection_filter()
                return
      
        _superclass.keyPress(self, key)
        
        return
    
    
    def bond_change_type(self, 
                         b, 
                         allow_remake_bondpoints = True,
                         supress_history_message = False): 
        #bruce 050727; revised 060703
        """
        Change bondtype of bond <b> to new bondtype determined by the dashboard 
        (if allowed).
        @see: BuildAtoms_Command._convert_bonds_bet_selected_atoms()
        """
        #This value is later changed based on what apply_btype_to_bond returns
        #the caller of this function can then use this further to determine
        #various things.
        #@see: BuildAtoms_Command._convert_bonds_bet_selected_atoms()
        
        bond_type_changed = True
        # renamed from clicked_on_bond() mark 060204.
        v6 = self.bondclick_v6
        if v6 is not None:
            self.set_cmdname('Change Bond')
            btype = btype_from_v6( v6)
            from operations.bond_utils import apply_btype_to_bond
            
            bond_type_changed = apply_btype_to_bond( 
                btype, 
                b, 
                allow_remake_bondpoints = allow_remake_bondpoints,
                supress_history_message = supress_history_message
            )
                # checks whether btype is ok, and if so, new; emits history 
                #message; does [#e or should do] needed invals/updates
            ###k not sure if that subr does gl_update when needed... this method
            ##does it, but not sure how
            # [or maybe only its caller does?]
        return bond_type_changed
    
    def bond_singlets(self, s1, s2):
        """
        Bond singlets <s1> and <s2> unless they are the same singlet.
        """
        #bruce 050429: it'd be nice to highlight the involved bonds and atoms, 
        # too...
        # incl any existing bond between same atoms. (by overdraw, for speed, 
        #or by more lines) ####@@@@ tryit
        #bruce 041119 split this out and added checks to fix bugs #203
        # (for bonding atom to itself) and #121 (atoms already bonded).
        # I fixed 121 by doing nothing to already-bonded atoms, but in
        # the future we might want to make a double bond. #e
        if s1.singlet_neighbor() is s2.singlet_neighbor():
            # this is a bug according to the subroutine [i.e. bond_at_singlets,
            #i later guess], but not to us
            print_error_details = 0
        else:
            # for any other error, let subr print a bug report,
            # since we think we caught them all before calling it
            print_error_details = 1
        flag, status = bond_at_singlets(s1, s2, move = False, \
                         print_error_details = print_error_details, 
                         increase_bond_order = True)

        # we ignore flag, which says whether it's ok, warning, or error
        env.history.message("%s: %s" % (self.command.get_featurename(), status))
        return
           
    def setBond1(self, state):
        "Slot for Bond Tool Single button."
        self.setBond(V_SINGLE, state)
        
    def setBond2(self, state):
        "Slot for Bond Tool Double button."
        self.setBond(V_DOUBLE, state)
    
    def setBond3(self, state):
        "Slot for Bond Tool Triple button."
        self.setBond(V_TRIPLE, state )
        
    def setBonda(self, state):
        "Slot for Bond Tool Aromatic button."
        self.setBond(V_AROMATIC, state)

    def setBondg(self, state): #mark 050831
        "Slot for Bond Tool Graphitic button."
        self.setBond(V_GRAPHITE, state)
        
    def setBond(self, v6, state, button = None):
        """
        #doc; v6 might be None, I guess, though this is not yet used
        """
        if state:
            if self.bondclick_v6 == v6 and button is not None and v6 is not None:
                # turn it off when clicked twice -- BUG: this never happens,
                #maybe due to QButtonGroup.setExclusive behavior
                self.bondclick_v6 = None
                button.setChecked(False) # doesn't work?
            else:
                self.bondclick_v6 = v6
            if self.bondclick_v6:
                name = btype_from_v6(self.bondclick_v6)
                env.history.statusbar_msg("click bonds to make them %s" % name)
                if self.command.propMgr:
                    self.command.propMgr.updateMessage() # Mark 2007-06-01
                  
            else:
                # this never happens (as explained above)
                #####@@@@@ see also setAtom, which runs when Atom Tool is 
                ##clicked (ideally this might run as well, but it doesn't)
                # (I'm guessing that self.bondclick_v6 is not relied on for 
                # action effects -- maybe the button states are??)
                # [bruce 060702 comment]
                env.history.statusbar_msg(" ") # clicking bonds now does nothing
                ## print "turned it off"
        else:
            pass # print "toggled(false) for",btype_from_v6(v6) 
                 # happens for the one that was just on,unless you click sameone
        
        self.update_cursor()
        
        return
    

    #== Draw methods
    
    def Draw(self):
        _superclass.Draw(self) # this includes self.o.assy.draw(self.o) 
        #[bruce 060724 comment]
        if self.line:
            color = get_selCurve_color(0,self.o.backgroundColor) 
                # Make sure line color has good contrast with bg. mark 060305.
            drawline(color, self.line[0], self.line[1])
            ####@@@@ if this is for a higher-order bond, draw differently
        ## self.o.assy.draw(self.o) # THIS WAS REDUNDANT [bruce 060724 removed it as a speedup]
        #bruce 050610 moved self.surface() call elsewhere [it's in Draw_after_highlighting]
        return

    def Draw_after_highlighting(self, pickCheckOnly=False): #bruce 050610
        # added pickCheckOnly arg.  mark 060207.
        """
        Do more drawing, after the main drawing code has completed its 
        highlighting/stenciling for selobj.Caller will leave glstate in standard
        form for Draw. Implems are free to turn off depth buffer read or write.
        Warning: anything implems do to depth or stencil buffers will affect the
        standard selobj-check in bareMotion.
        [New method in mode API as of bruce 050610. General form not yet defined
        -- just a hack for Build mode's water surface. Could be used for 
        transparent drawing in general.]
        """
        _superclass.Draw_after_highlighting(self, pickCheckOnly) #Draw possible other translucent objects. [huaicai 9/28/05]
        
        glDepthMask(GL_FALSE)
            # disable writing the depth buffer, so bareMotion selobj check measures depths behind it,
            # so it can more reliably compare them to water's constant depth. (This way, roundoff errors
            # only matter where the model hits the water surface, rather than over all the visible
            # water surface.)
            # (Note: before bruce 050608, depth buffer remained writable here -- untypical for transparent drawing,
            #  but ok then, since water was drawn last and bareMotion had no depth-buffer pixel check.)
        self.surface() 
        glDepthMask(GL_TRUE)
        return
        
    def surface(self):
        """
        Draw the water's surface -- a sketch plane to indicate where the new atoms will sit by default,
        which also prevents (some kinds of) selection of objects behind it.
        """
        if not env.prefs[buildModeWaterEnabled_prefs_key]:
            return
            
        glDisable(GL_LIGHTING)
        glColor4fv(self.gridColor + (0.6,))
            ##e bruce 050615 comment: if this equalled bgcolor, some bugs would go away;
            # we'd still want to correct the surface-size to properly fit the window (bug 264, just now fixed below),
            # but the flicker to bgcolor bug (bug number?) would be gone (defined and effective bgcolor would be same).
            # And that would make sense in principle, too -- the water surface would be like a finite amount of fog,
            # concentrated into a single plane.
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # the grid is in eyespace
        glPushMatrix()
        q = self.o.quat
        glTranslatef(-self.o.pov[0], -self.o.pov[1], -self.o.pov[2])
        glRotatef(- q.angle*180.0/math.pi, q.x, q.y, q.z)

##        # The following is wrong for wide windows (bug 264).
##      # To fix it requires looking at how scale is set (differently
##      # and perhaps wrongly (related to bug 239) for tall windows),
##      # so I'll do it later, after fixing bug 239.
##      # Warning: correctness of use of x vs y below has not been verified.
##      # [bruce 041214] ###@@@
##      # ... but for Alpha let's just do a quick fix by replacing 1.5 by 4.0.
##      # This should work except for very wide (or tall??) windows.
##      # [bruce 050120]
##      
##        ## x = y = 4.0 * self.o.scale # was 1.5 before bruce 050120; still a kluge
        
        #bruce 050615 to fix bug 264 (finally! but it will only last until someone changes what self.o.scale means...):
        # here are presumably correct values for the screen boundaries in this "plane of center of view":
        y = self.o.scale # always fits height, regardless of aspect ratio (as of 050615 anyway)
        x = y * (self.o.width + 0.0) / self.o.height
        # (#e Ideally these would be glpane attrs so we wouldn't have to know how to compute them here.)
        # By test, these seem exactly right (tested as above and after x,y *= 0.95),
        # but for robustness (in case of roundoff errors restoring eyespace matrices)
        # I'll add an arbitrary fudge factor (both small and overkill at the same time!):
        x *= 1.1
        y *= 1.1
        x += 5
        y += 5
        glBegin(GL_QUADS)
        glVertex(-x,-y,0)
        glVertex(x,-y,0)
        glVertex(x,y,0)
        glVertex(-x,y,0)
        glEnd()
        glPopMatrix()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
        return
    
    # == Singlet helper methods

    def singletLeftDown(self, s, event):
        if self.o.modkeys == 'Shift+Control':
            self.cursor_over_when_LMB_pressed = 'Empty Space'
            self.select_2d_region(event)
        else:
            self.cursor_over_when_LMB_pressed = 'Singlet'
            self.singletSetup(s)

    def singletSetup(self, a):
        """
        Setup for a click, double-click or drag event for singlet <a>.
        """
        self.objectSetup(a)
        self.only_highlight_singlets = True
        
        self.singlet_list = self.o.assy.getConnectedSinglets([a])
            # get list of all singlets that we can reach from any sequence of bonds to <a>.
            # used in doubleLeft() if the user clicks on

            # note: it appears that self.singlet_list is never used, tho another routine computes it
            # locally under the same name and uses that. [bruce 070411 comment, examining Qt3 branch]
        
        pivatom = a.neighbors()[0]
        self.baggage, self.nonbaggage = pivatom.baggage_and_other_neighbors() #bruce 051209
        neigh = self.nonbaggage

        self.baggage.remove(a) # always works since singlets are always baggage
        if neigh:
            if len(neigh)==2:
                self.pivot = pivatom.posn()
                self.pivax = norm(neigh[0].posn()-neigh[1].posn())
                self.baggage = [] #####@@@@@ revise nonbaggage too??
                #bruce suspects this might be a bug, looks like it prevents other singlets from moving, eg in -CX2- drag X
            elif len(neigh)>2:
                self.pivot = None
                self.pivax = None
                self.baggage = []#####@@@@@ revise nonbaggage too??
            else: # atom on a single stalk
                self.pivot = pivatom.posn()
                self.pivax = norm(self.pivot-neigh[0].posn())
        else: # no non-baggage neighbors
            self.pivot = pivatom.posn()
            self.pivax = None


    def singletDrag(self, bondpoint, event):
        """
        Drag a bondpoint.

        @param bondpoint: a bondpoint to drag
        @type bondpoint: some instances of class Atom
        
        @param event: a drag event
        """
        if bondpoint.element is not Singlet:
            return
         
        apos0 = bondpoint.posn()

        px = self.dragto_with_offset(bondpoint.posn(),
                                     event,
                                     self.drag_offset )
            #bruce 060316 attempt to fix bug 1474 analogue;
            # untested and incomplete since nothing is setting drag_offset
            # when this is called (except to its default value V(0,0,0))!
        
        if self.pivax:
            # continue pivoting around an axis
            quat = twistor(self.pivax,
                           bondpoint.posn() - self.pivot,
                           px - self.pivot)
            for at in [bondpoint] + self.baggage:
                at.setposn(quat.rot(at.posn() - self.pivot) + self.pivot)
        
        elif self.pivot:
            # continue pivoting around a point
            quat = Q(bondpoint.posn() - self.pivot, px - self.pivot)
            for at in [bondpoint] + self.baggage:
                at.setposn(quat.rot(at.posn() - self.pivot) + self.pivot)

        # highlight bondpoints we might bond this one to
        self.update_selatom(event, singOnly = True)

            #bruce 051209: to fix an old bug, don't call update_selatom
            # when dragging a real atom -- only call it here in this method,
            # when dragging a bondpoint. (Related: see warnings about
            # update_selatom's delayed effect, in its docstring or in leftDown.)
            # Q: when dragging a real atom, in some other method,
            # do we need to reset selatom instead?
            # [bruce 071025 rewrote that comment for its new context and for
            #  clarity, inferring meaning from other code & comments here;
            #  also rewrote the old comments below, in this method]
        
            #bruce 060726 question: why does trying singOnly = False here
            # have no visible effect? The only highlightings during drag
            # are the singlets, and real atoms that have singlets.
            # Where is the cause of this? I can't find any code resetting
            # selobj then. The code in update_selatom also looks like it
            # won't refrain from storing anything in selobj, based on
            # singOnly -- this only affects what it stores in selatom.
            # [later, 071025: wait, I thought it never stored anything in
            # selobj at all. Is its doc wrong, does it call update_selobj
            # and do that?]
            # Guesses about what code could be doing that (REVIEW):
            # selobj_still_ok? hicolor/selobj_highlight_color?
            # Also, note that not all drag methods call update_selobj at all.
            # (I think they then leave the old selobj highlighted --
            # dragging a real atom seems to do that.)
            #
            # My motivations for wanting to understand this: a need to let
            # self.drag_handler control what gets highlighted (and its color),
            # and unexplained behavior of testdraw.py after leftDown.

        # update the endpoints of the white rubberband line
        self.line = [bondpoint.posn(), px]
        
        apos1 = bondpoint.posn()
        if apos1 - apos0:
            msg = "pulling bondpoint %r to %s" % (bondpoint, 
                                                  self.posn_str(bondpoint))
            this_drag_id = (self.current_obj_start, 
                            self.__class__.leftDrag)
            env.history.message(msg, transient_id = this_drag_id)
            
        self.o.gl_update()
        return
        
    def singletLeftUp(self, s1, event):
        """
        Finish operation on singlet <s1> based on where the cursor is when the 
        LMB was released:
        - If the cursor is still on <s1>, deposit an object from the MMKit on it
          [or as of 060702, use a bond type changing tool if one is active, to
          fix bug 833 item 1 ###implem unfinished?]
        - If the cursor is over a different singlet, bond <s1> to it.
        - If the cursor is over empty space, do nothing.
        <event> is a LMB release event.
        @see:self._singletLeftUp_joinDnaStrands()
        """
        self.line = None 
        # required to erase white rubberband line on next 
        # gl_update. [bruce 070413 moved this before tests]

        if not s1.is_singlet():
            return

        if len(s1.bonds) != 1:
            return #bruce 070413 precaution

        neighbor = s1.singlet_neighbor()

        s2 = self.get_singlet_under_cursor(
            event, 
            reaction_from = neighbor.element.symbol,
            desired_open_bond_direction = s1.bonds[0].bond_direction_from(s1) #bruce 080403 bugfix
            )
            ####@@@@ POSSIBLE BUG: s2 is not deterministic if cursor is over a 
            ##real atom w/ >1 singlets (see its docstring);
            # this may lead to bond type changer on singlet sometimes but not 
            # always working, if cursor goes up over its base atom; or it may 
            #lead to nondeterministic remaining bondpoint
            # position or bondorder when bonding s1 to another atom.
            #   When it doesn't work (for bond type changer), it'll try to 
            #  create a bond between singlets on the same base atom; the code 
            #  below indicates it won't really do it, but may erroneously 
            # set_cmdname then (but if nothing changes this may not cause a bug 
            # in Undo menu text).
            # I tried to demo the basic bug (sometime-failure of bond type 
            # changer) but forgot to activate that tool.
            # But I found that debug prints and behavior make it look like 
            # something prevents highlighting s1's base atom,
            # [later: presumably that was the only_highlight_singlets feature]
            # but permits highlighting of other real atoms, during s1's drag. 
            # Even if that means this bug can't happen, the code needs to be
            # clarified. [bruce 060721 comment]
            #update 080403: see also new desired_open_bond_direction code in
            # get_singlet_under_cursor.
        
        if s2:
            if s2 is s1: # If the same singlet is highlighted...
                if self.command.isBondsToolActive():
                    #bruce 060702 fix bug 833 item 1 (see also bondLeftUp)
                    b = s1.bonds[0]
                    self.bond_change_type(b, allow_remake_bondpoints = False) 
                    # does set_cmdname
                    self.o.gl_update() # (probably good for highlighting, even 
                    # if bond_change_type refused)
                    # REVIEW (possible optim): can we use gl_update_highlight 
                    # when only highlighting was changed? [bruce 070626]
                else:
                    # ...deposit an object (atom, chunk or library part) from 
                    # MMKit on the singlet <s1>.
                    if self.mouse_within_stickiness_limit(
                        event, 
                        DRAG_STICKINESS_LIMIT): # Fixes bug 1448. mark 060301.
                        deposited_obj = self.deposit_from_MMKit(s1)
                            # does its own win_update().
                        if deposited_obj:
                            self.set_cmdname('Deposit ' + deposited_obj)
            else: # A different singlet is highlighted...
                # If the singlets s1 & s2 are 3' and 5' or 5' and 3' bondpoints
                # of DNA strands, merge their strand chunks...
                open_bond1 = s1.bonds[0]
                open_bond2 = s2.bonds[0]
                
                # Cannot DND 3' open bonds onto 3' open bonds.  
                if open_bond1.isThreePrimeOpenBond() and \
                   open_bond2.isThreePrimeOpenBond():
                    if self.command.propMgr:
                        msg = redmsg("Cannot join strands on 3' ends.")
                        self.command.propMgr.updateMessage(msg)
                    return
                # Cannot DND 5' open bonds onto 5' open bonds. 
                if open_bond1.isFivePrimeOpenBond() and \
                   open_bond2.isFivePrimeOpenBond():
                    if self.command.propMgr:
                        msg = redmsg("Cannot join strands on 5' ends.")                    
                        self.command.propMgr.updateMessage(msg) 
                    return
                # Ok to DND 3' onto 5' or 5' onto 3'.
                
                if (open_bond1.isThreePrimeOpenBond() and \
                    open_bond2.isFivePrimeOpenBond()) or \
                   (open_bond1.isFivePrimeOpenBond()  and \
                    open_bond2.isThreePrimeOpenBond()):
                    
                    self._singletLeftUp_joinDnaStrands(s1,s2,
                                                   open_bond1, open_bond2)
                    return #don't proceed further
                                
                # ... now bond the highlighted singlet <s2> to the first 
                # singlet <s1>
                self.bond_singlets(s1, s2)
                self.set_cmdname('Create Bond')
                self.o.gl_update()
                if self.command.propMgr:
                    self.command.propMgr.updateMessage() 
        else: # cursor on empty space
            self.o.gl_update() # get rid of white rubber band line.
            # REVIEW (possible optim): can we make 
            # gl_update_highlight cover this? [bruce 070626]
            
        self.only_highlight_singlets = False
        
    def _singletLeftUp_joinDnaStrands(self, 
                                      s1, 
                                      s2, 
                                      open_bond1,
                                      open_bond2
                                      ):
        """
        Only to be called from self.singletLeftUp
        """
        #This was split out of self.singletLeftUp()
        
        # Ok to DND 3' onto 5' or 5' onto 3' . We already check the 
        #if condition in self
        
        if (open_bond1.isThreePrimeOpenBond() and \
            open_bond2.isFivePrimeOpenBond()) or \
           (open_bond1.isFivePrimeOpenBond()  and \
            open_bond2.isThreePrimeOpenBond()):
            a1 = open_bond1.other(s1)
            a2 = open_bond2.other(s2)
            # We rely on merge() to check that mols are not the same.
            # merge also results in making the strand colors the same.
            
            #The following fixes bug 2770
            #Set the color of the whole dna strandGroup to the color of the
            #strand, whose bondpoint, is dropped over to the bondboint of the 
            #other strandchunk (thus joining the two strands together into
            #a single dna strand group) - Ninad 2008-04-09
            color = a1.molecule.color 
            if color is None:
                color = a1.element.color
            strandGroup1 = a1.molecule.parent_node_of_class(self.win.assy.DnaStrand)
            
            #Temporary fix for bug 2829 that Damian reported. 
            #Bruce is planning to fix the underlying bug in the dna updater 
            #code. Once its fixed, The following block of code under 
            #"if DEBUG_BUG_2829" can be deleted -- Ninad 2008-05-01
            
            DEBUG_BUG_2829 = True
            
            if DEBUG_BUG_2829:            
                strandGroup2 = a2.molecule.parent_node_of_class(
                    self.win.assy.DnaStrand)                
                if strandGroup2 is not None:
                    #set the strand color of strandGroup2 to the one for 
                    #strandGroup1. 
                    strandGroup2.setStrandColor(color)
                    strandChunkList = strandGroup2.getStrandChunks()
                    for c in strandChunkList:
                        if hasattr(c, 'invalidate_ladder'):
                            c.invalidate_ladder()
                            
            if not DEBUG_BUG_2829:    
                #merging molecules is not required if you invalidate the ladders
                #in DEBUG_BUG_2829 block
                a1.molecule.merge(a2.molecule)   
                
            # ... now bond the highlighted singlet <s2> to the first 
            # singlet <s1>
            self.bond_singlets(s1, s2)
            
            if not DEBUG_BUG_2829:
                #No need to call update_parts() if you invalidate ladders 
                #of strandGroup2 as done in DEBUG_BUG_2829 fix (Tested)
                
                #Run the dna updater -- important to do it otherwise it won't update
                #the whole strand group color
                self.win.assy.update_parts()  
                
            self.set_cmdname('Create Bond')
            
            if strandGroup1 is not None:
                strandGroup1.setStrandColor(color) 
            
            self.o.gl_update()
            if self.command.propMgr:
                self.command.propMgr.updateMessage() 
                
            self.only_highlight_singlets = False
            
            return
        
    def get_singlet_under_cursor(self, event,
                                 reaction_from = None,
                                 desired_open_bond_direction = 0 ):
        """
        If the object under the cursor is a singlet, return it.  
        If the object under the cursor is a real atom with one or more singlets,
        return one of its singlets, preferring one with the
        desired_open_bond_direction (measured from base atom to singlet)
        if it's necessary to choose. Otherwise, return None.
        """
        del reaction_from # not yet used
        atom = self.get_obj_under_cursor(event)
        if isinstance(atom, Atom):
            if atom.is_singlet():
                return atom
            # Update, bruce 071121, about returning singlets bonded to real
            # atoms under the cursor, but not themselves under it:
            # Note that this method affects what happens
            # on leftup, but is not used to determine what gets highlighted
            # during mouse motion. A comment below mentions that
            # selobj_highlight_color is related to that. It looks like it has
            # code for this in SelectAtoms_Command._getAtomHighlightColor.
            # There is also a call
            # to update_selatom with singOnly = True, which doesn't have this
            # special case for non-bondpoints, but I don't know whether it's
            # related to what happens here.
            # All this may or may not relate to bug 2587.
            #update, bruce 080320: removed nonworking code that used
            # element symbols 'Pl' and 'Sh' (with no '5' appended).
            # (Obsolete element symbols may also appear elsewhere in *Mode.py.)
            #
            #revised, bruce 080403 (bugfix): use desired_open_bond_direction
            # to choose the best bondpoint to return.
            candidates = []
            for bond in atom.bonds:
                other = bond.other(atom)
                if other.is_singlet():
                    dir_to_other = bond.bond_direction_from(atom) # -1, 0, or 1
                    badness = abs(desired_open_bond_direction - dir_to_other)
                        # this means: for directional bond-source,
                        # prefer same direction, then none, then opposite.
                        # for non-directional source, prefer no direction, then either direction.
                        # But we'd rather be deterministic, so in latter case we'll prefer
                        # direction -1 to 1, accomplished by including dir_to_other in badness:
                    badness = (badness, dir_to_other)
                    candidates.append( (badness, other.key, other) )
                        # include key to sort more deterministically
                continue
            if candidates:
                candidates.sort()
                return candidates[0][-1] # least badness
            pass
##            if atom.singNeighbors():
##                if len(atom.singNeighbors()) > 1:
##                    if env.debug():
##                        #bruce 060721, cond revised 071121, text revised 080403
##                        print "debug warning: get_singlet_under_cursor returning an arbitrary bondpoint of %r" % (atom,)
##                return atom.singNeighbors()[0]
        return None
    
    #==========
    
    def _createBond(self, s1, a1, s2, a2):
        """
        Create bond between atom <a1> and atom <a2>, <s1> and <s2>
        are their singlets. No rotation/movement involved.
        """
        # Based on method actually_bond() in bonds.py--[Huaicai 8/25/05]
        ### REVIEW: the code this is based on has, since then, been modified --
        # perhaps bugfixed, perhaps just cleaned up. This code ought to be fixed
        # in the same way, or (better) common helper code factored out and used.
        # Not urgent, but keep in mind if this code might have any bugs.
        # [bruce 080320 comment]
        
        try: # use old code until new code works and unless new code is needed;
            # CHANGE THIS SOON #####@@@@@
            v1, v2 = s1.singlet_v6(), s2.singlet_v6() # new code available
            assert v1 != V_SINGLE or v2 != V_SINGLE # new code needed
        except:
            # old code can be used for now
            s1.kill()
            s2.kill()
            bond_atoms(a1,a2)
            return
        
        vnew = min(v1, v2)
        bond = bond_atoms(a1, a2, vnew, s1, s2) # tell it the singlets to replace or
            # reduce; let this do everything now, incl updates
        return


    def transdepositPreviewedItem(self, singlet):
        """
        Trans-deposit the current object in the preview groupbox of the 
        property manager  on all singlets reachable through 
        any sequence of bonds to the singlet <singlet>.
        """
        
        if not singlet.is_singlet(): 
            return
        
        singlet_list = self.o.assy.getConnectedSinglets([singlet])
        
        modkeys = self.o.modkeys # save the modkeys state
        if self.o.modkeys is None and \
           env.prefs[buildModeSelectAtomsOfDepositedObjEnabled_prefs_key]:
            # Needed when 'Select Atoms of Deposited Object' pref is enabled. 
            # mark 060314.
            self.o.modkeys = 'Shift'    
            self.o.assy.unpickall_in_GLPane() 
            # [was unpickatoms; this (including Nodes) might be an 
            #  undesirable change -- bruce 060721]
        
        self.transdepositing = True
        nobjs = 0
        ntried = 0 
        msg_deposited_obj = None
        for s in singlet_list: 
            # singlet_list built in singletSetup() 
            #[not true; is that a bug?? bruce 060412 question]
            if not s.killed(): # takes care of self.obj_doubleclicked, too.
                deposited_obj = self.deposit_from_MMKit(s)
                ntried += 1
                if deposited_obj is not None:
                    #bruce 060412 -- fix part of bug 1677 
                    # -- wrong histmsg 'Nothing Transdeposited' and lack of
                    # mt_update
                    msg_deposited_obj = deposited_obj 
                    # I think these will all be the same, so we just use the 
                    # last one
                    nobjs += 1
        self.transdepositing = False
        self.o.modkeys = modkeys # restore the modkeys state to real state.

        del deposited_obj
        
        if msg_deposited_obj is None: 
            # Let user know nothing was trandeposited. Fixes bug 1678.
            # mark 060314.
            # (This was incorrect in bug 1677 since it assumed all deposited_obj
            # return values were the same,
            #  but in that bug (as one of several problems in it) the first 
            #  retval was not None but the last one was,so this caused a wrong 
            #  message and a failure to update the MT. Fixed those parts of 
            #  bug 1677 by introducing msg_deposited_obj and using that here 
            #  instead of deposited_obj. Fixed other parts of it
            #  in MMKit and elsewhere in this method. [bruce 060412])
            env.history.message('Nothing Transdeposited')
            return
            
        self.set_cmdname('Transdeposit ' + msg_deposited_obj)
        msg_deposited_obj += '(s)'
        
        info = fix_plurals( "%d %s deposited." % (nobjs, msg_deposited_obj) )
        if ntried > nobjs:
            # Note 1: this will be true in bug 1677 (until it's entirely fixed)
            # [bruce 060412]
            # Note 2: this code was tested and worked, before I fully fixed 
            # bug 1677;
            # now that bug is fully fixed above (in the same commit as this 
            # code),
            # so this code is not known to ever run,
            # but I'll leave it in in case it mitigates any undiscovered bugs.
            info += " (%d not deposited due to a bug)" % (ntried - nobjs)
            info = orangemsg(info)
        env.history.message(info)
        self.w.win_update()
        
        
    #=======Deposit Atom helper methods 
    def deposit_from_MMKit(self, atom_or_pos): #mark circa 051200; revised by bruce 051227
        """
        Deposit a new object based on the current selection in the 
        MMKit/dashboard,  which is either an atom, a chunk on the clipboard, or 
        a part from the library.
        
        If 'atom_or_pos' is a singlet, then it will bond the object to that 
        singlet if it can.        
        If 'atom_or_pos' is a position, then it will deposit the object at that 
        coordinate.
        
        Return string <deposited_obj>, where:
            'Atoms' - an atom from the Atoms page was deposited.
            'Chunk' - a chunk from the Clipboard page was deposited.
            'Part' - a library part from the Library page was deposited.

        Note: 
        This is overridden in some subclasses (e.g. PasteFromClipboard_Command, PartLibrary_Command),
        but the default implementation is also still used [as of 071025].
        """
        
        deposited_obj = None 
            #& deposited_obj is probably misnamed, since it is a string, not an object.  
            #& Would be nice if this could be an object. Problem is that clipboard and library
            #& both deposit chunks. mark 060314.
        
        # no Shift or Ctrl modifier key , also make sure that 'selection lock' 
        #is not ON.
        if self.o.modkeys is None and not self.selection_locked(): 
            self.o.assy.unpickall_in_GLPane() # Clear selection. [was unpickatoms -- bruce 060721]
        
        if self.w.depositState == 'Atoms':
            deposited_stuff, status = self.deposit_from_Atoms_page(atom_or_pos) # deposited_stuff is a chunk
            deposited_obj = 'Atom'            
            
        else:
            print_compact_stack('Invalid depositState = "' + str(self.w.depositState) + '" ')
            return
            
        self.o.selatom = None ##k could this be moved earlier, or does one of those submethods use it? [bruce 051227 question]
            
        # now fix bug 229 part B (as called in comment #2),
        # by making this new chunk (or perhaps multiple chunks, in 
        # deposited_stuff) visible if it otherwise would not be.
        # [bruce 051227 is extending this fix to depositing Library parts, whose
        # initial implementation reinstated the bug.
        #  Note, Mark says the following comment is in 2 places but I can't find
        # the other place, so not removing it yet.]
        ## We now have bug 229 again when we deposit a library part while in 
        ##"invisible" display mode.
        ## Ninad is reopening bug 229 and assigning it to me.  This comment is 
        ##in 2 places. Mark 051214.
        ##if not library_part_deposited:  
        ##Added the condition [Huaicai 8/26/05] [bruce 051227 removed it, 
        ##added a different one]

        if self.transdepositing:
            if not deposited_stuff:
                # Nothing was transdeposited.  Needed to fix bug 1678. 
                #mark 060314.
                return None
            return deposited_obj
        
        if deposited_stuff:
            self.w.win_update() 
                #& should we differentimate b/w win_update (when deposited_stuff
                #is a new chunk added) vs. 
                #& gl_update (when deposited_stuff is added to existing chunk). 
                #Discuss with Bruce. mark 060210.
            status = self.ensure_visible( deposited_stuff, status) #bruce 041207
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) # nothing deposited
        
        return deposited_obj

    def deposit_from_Atoms_page(self, atom_or_pos):
        """
        Deposits an atom of the selected atom type from the MMKit Atoms page, or
        the Clipboard (atom and hybridtype) comboboxes on the dashboard, 
        which are the same atom.
        If 'atom_or_pos' is a singlet, bond the atom to the singlet.
        Otherwise, set up the atom at position 'atom_or_pos' to be dragged 
        around.
        Returns (chunk, status)
        """
        
        assert hasattr(self.command, 'pastable_atomtype')
        
        atype = self.command.pastable_atomtype() # Type of atom to deposit
        
        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet: # bond an atom of type atype to the singlet
                a0 = a.singlet_neighbor() # do this before <a> (the singlet) 
                #is killed!(revised by bruce 050511)
                # if 1: # during devel, at least
                
                from commands.BuildAtoms.build_utils import AtomTypeDepositionTool
                deptool = AtomTypeDepositionTool( atype)
                
                if hasattr(self.command, 'isAutoBondingEnabled'):
                    autobond = self.command.isAutoBondingEnabled()
                else:
                    # we're presumably a subclass with no propMgr or
                    # a different one
                    autobond = True
                    
                a1, desc = deptool.attach_to(a, autobond = autobond)
                        #e this might need to take over the generation of the 
                        #following status msg...
                ## a1, desc = self.attach(el, a)
                if a1 is not None:
                    if self.pickit(): 
                        a1.pick()
                    #self.o.gl_update() #bruce 050510 moved this here from 
                    #inside what's now deptool. The only callers, 
                    # deposit_from_MMKit() and transdepositPreviewedItem() are
                    #responsible for callinggl_update()/win_update(). 
                    #mark 060314.
                    status = "replaced bondpoint on %r with new atom %s at %s" % (a0, desc, self.posn_str(a1))
                    chunk = a1.molecule #bruce 041207
                else:
                    status = desc
                    chunk = None #bruce 041207
                del a1, desc

        else: # Deposit atom at the cursor position and prep it for dragging
            cursorPos = atom_or_pos
            a = self.o.selatom = oneUnbonded(atype.element, 
                                             self.o.assy, 
                                             cursorPos, 
                                             atomtype = atype)
            self.objectSetup(a)
            self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
            if self.pickit(): 
                self.o.selatom.pick()
            status = "made new atom %r at %s" % (self.o.selatom, 
                                                 self.posn_str(self.o.selatom))
            chunk = self.o.selatom.molecule #bruce 041207
        
        return chunk, status
    
        
    def ensure_visible(self, stuff, status):
        """
        If any chunk in stuff (a node, or a list of nodes) is not visible now, 
        make it visible by changing its display mode, and append a warning about
        this to the given status message, which is returned whether or not it's
        modified.

        Suggested revision: if some chunks in a library part are explicitly 
        invisible and some are visible, I suspect this behavior is wrong and it 
        might be better to require only that some of them are visible, and/or to
        only do this when overall display mode was visible. [bruce 051227]

        Suggested revision: maybe the default display mode for deposited stuff 
        should also be user-settable. [bruce 051227]
        """
        # By bruce 041207, to fix bug 229 part B (as called in comment #2),
        # by making each deposited chunk visible if it otherwise would not be.
        # Note that the chunk is now (usually?) the entire newly deposited 
        # thing, but after future planned changes to the code, it might instead 
        # be a preexisting chunk which was extended. Either way, we'll make the
        # entire chunk visible if it's not.
        #bruce 051227 revising this to handle more general deposited_stuff, 
        #for deposited library parts.
        n = self.ensure_visible_0( stuff)
        if n:
            status += " (warning: gave it Tubes display mode)"
            #k is "it" correct even for library parts? even when not all 
            #deposited chunks were changed?
        return status

    def ensure_visible_0(self, stuff): 
        """
        [private recursive worker method for ensure_visible;
        returns number of things whose display mode was modified]
        """
        if not stuff:
            return 0 #k can this happen? I think so, 
                    #since old code could handle it. [bruce]
        if isinstance(stuff, Chunk):
            chunk = stuff
            if chunk.get_dispdef(self.o) == diINVISIBLE:
                # Build mode's own default display mode--
                chunk.setDisplay(diTUBES) 
                
                return 1
            return 0
        elif isinstance(stuff, Group):
            return self.ensure_visible_0( stuff.members)
        elif isinstance(stuff, type([])):
            res = 0
            for m in stuff:
                res += self.ensure_visible_0( m)
            return res
        else:
            assert isinstance(stuff, Node) # presumably Jig
            ##e not sure how to handle this or whether we need to 
            ##[bruce 051227]; leave it out and await bug report?
            # [this will definitely occur once there's a partlib part which 
            # deposits a Jig or Comment or Named View;
            #  for Jigs should it Unhide them? For that matter, what about for 
            # Chunks? What if the hiddenness or invisibility came from the 
            #partlib?]
            if debug_flags.atom_debug:
                print "atom_debug: ignoring object of unhandled type (Jig? Comment? Named View?) in ensure_visible_0", stuff
            return 0
        pass
    
    def pickit(self):
        """
        Determines if the a deposited object should have its atoms automatically
        picked. Returns True or False based on the current modkey state.
        If modkey is None (no modkey is pressed), it will unpick all currently
        picked atoms.
        """
        if self.selection_locked():
            return False
        
        if self.o.modkeys is None:
            self.o.assy.unpickall_in_GLPane() 
            # [was unpickatoms; this is a guess, 
            #I didn't review the calls -- bruce 060721]
            if env.prefs[buildModeSelectAtomsOfDepositedObjEnabled_prefs_key]:
                # Added NFR 1504.  mark 060304.
                return True
            return False
        if self.o.modkeys == 'Shift':
            return True
        if self.o.modkeys == 'Control':
            return False
        else: # Delete
            return False
        
    #===HotSpot related methods
    
    def setHotSpot_clipitem(self): 
        #bruce 050416; duplicates some code from setHotSpot_mainPart
        """
        Set or change hotspot of a chunk in the clipboard
        """
        selatom = self.o.selatom
        if selatom and selatom.element is Singlet:
            selatom.molecule.set_hotspot( selatom) ###e add history message??
            self.o.set_selobj(None)  #bruce 050614-b: fix bug703-related older 
            #bug (need to move mouse to see new-hotspot color)
            self.o.gl_update() 
            #bruce 050614-a: fix bug 703 (also required 
            #having hotspot-drawing code in chunk.py ignore selatom)
            # REVIEW (possible optim): can gl_update_highlight cover this? 
            # It doesn't now cover chunk.selatom drawing,
            # but (1) it could be made to do so, and (2) we're not always 
            #drawing chunk.selatom anyway. [bruce 070626]
        ###e also set this as the pastable??
        return        
        
    def setHotSpot_mainPart(self): 
        """
        Set hotspot on a main part chunk and copy it (with that hotspot) 
        into clipboard
        """
        # revised 041124 to fix bug 169, by mark and then by bruce
        selatom = self.o.selatom
        if selatom and selatom.element is Singlet:
            selatom.molecule.set_hotspot( selatom)
            
            new = selatom.molecule.copy_single_chunk(None) # None means no dad yet
            #bruce 050531 removing centering:
            ## new.move(-new.center) # perhaps no longer needed [bruce 041206]
            #bruce 041124: open clipboard, so user can see new pastable there
            self.w.mt.open_clipboard()
            
            # now add new to the clipboard
            
                       
            # bruce 041124 change: add new after the other members, not before.
            # [bruce 050121 adds: see cvs for history (removed today from this 
            #  code)of how this code changed as the storage order of 
            # Group.members changed(but out of sync,so that bugs often existed)]
            
            self.o.assy.shelf.addchild(new) # adds at the end
            self.o.assy.update_parts() 
            # bruce 050316; needed when adding clipboard items.
                    
            # bruce 050121 don't change selection anymore; it causes too many 
            # bugs to have clipboard items selected. Once my new model tree code
            # is committed, we could do this again and/or highlight the pastable
            # there in some other way.
            ##self.o.assy.shelf.unpick() # unpicks all shelf items too
            ##new.pick()

            #Keep the depositState to 'Atoms'. Earlier the depositState was
            #changed to 'Clipboard' because  'Set hotspot and copy' used to 
            #open the clipboard tab in the 'MMKit'. This implementation has 
            #been replaced with a separate 'Paste Mode' to handle Pasting 
            #components. So always keep depositState to Atoms while in 
            #depositMode.  (this needs further cleanup) -- ninad 2007-09-04
            self.w.depositState = 'Atoms'
            
            
            self.w.mt.mt_update() # since clipboard changed
            #bruce 050614 comment: in spite of bug 703 
            # (fixed in setHotSpot_mainPart),
            # I don't think we need gl_update now in this method,
            # since I don't think main glpane shows hotspots and since the
            # user's intention here is mainly to make one in the clipboard copy,
            #  not in the main model; and in case it's slow, we shouldn't 
            #  repaint if we don't need to.Evidently I thought the same thing in
            #  this prior comment, when I removed a glpane update
            # (this might date from before hotspots were ever visible 
            # -- not sure):
            ## also update glpane if we show pastable someday; not needed now
            ## [and removed by bruce 050121]
                            
        return
    
    # cursor update methods
    
    def update_cursor_for_no_MB_selection_filter_disabled(self):
        """
        Update the cursor for 'Build Atoms' mode, when no mouse button is 
        pressed.
        """
        
        cursor_id = 0
        if hasattr(self.w, "current_bondtool_button") and \
           self.w.current_bondtool_button is not None:
            cursor_id = self.w.current_bondtool_button.index
        
        if hasattr(self.command, 'get_cursor_id_for_active_tool' ):
            cursor_id = self.command.get_cursor_id_for_active_tool() 
        if self.o.modkeys is None:             
            self.o.setCursor(self.w.BondToolCursor[cursor_id])
        elif self.o.modkeys == 'Shift':
            self.o.setCursor(self.w.BondToolAddCursor[cursor_id])
        elif self.o.modkeys == 'Control':
            self.o.setCursor(self.w.BondToolSubtractCursor[cursor_id])
        elif self.o.modkeys == 'Shift+Control':
            self.o.setCursor(self.w.DeleteCursor)
        else:
            print "Error in update_cursor_for_no_MB(): Invalid modkey=", self.o.modkeys
        return


class BuildAtoms_GraphicsMode(BuildAtoms_basicGraphicsMode):
    """
    @see: SelectAtoms_GraphicsMode
    """
    ##### START of code copied from SelectAtoms_GraphicsMode (except that the 
    ##### superclass name is different. 
    
    def __init__(self, command):
        self.command = command
        glpane = self.command.glpane 
        BuildAtoms_basicGraphicsMode.__init__(self, glpane)
        return
        
    # (the rest would come from GraphicsMode if post-inheriting it worked,
    #  or we could split it out of GraphicsMode as a post-mixin to use there 
    #  and here)

    def _get_commandSequencer(self):
        return self.command.commandSequencer

    commandSequencer = property(_get_commandSequencer)

    def set_cmdname(self, name):
        self.command.set_cmdname(name)
        return
  
    
    def _get_highlight_singlets(self):
        return self.command.highlight_singlets

    def _set_highlight_singlets(self, val):
        self.command.highlight_singlets = val

    highlight_singlets = property(_get_highlight_singlets, 
                                          _set_highlight_singlets)
    
    ##### END of code copied from SelectAtoms_GraphicsCommand
    

    
