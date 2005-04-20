# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
depositMode.py

Build mode.

$Id$
"""
__author__ = "Josh"

from Numeric import *
from modes import *
from VQT import *
from chem import *
import drawer
from constants import elemKeyTab
import platform
from debug import print_compact_traceback
from elements import PeriodicTable

_count = 0

#bruce 050121 split out hotspot helper functions, for slightly more general use

def is_pastable(obj): #e refile and clean up
    "whether to include a clipboard object on Build's pastable spinbox"
    #bruce 050127 make this more liberal, so it includes things which are
    # not pastable onto singlets but are still pastable into free space
    # (as it did before my changes of a few days ago)
    # but always run is_pastable_onto_singlet in case it has a klugy bugfixing side-effect
    return is_pastable_onto_singlet(obj) or is_pastable_into_free_space(obj)

# these separate is_pastable_xxx functions make a distinction which might not yet be used,
# but which should be used soon to display these kinds of pastables differently
# in the model tree and/or spinbox [bruce 050127]:

def is_pastable_into_free_space(obj):#bruce 050127
    return isinstance(obj, molecule) # for now; later we might include Groups too

def is_pastable_onto_singlet(obj): #bruce 050121 (renamed 050127)
    # this might have a klugy bugfixing side-effect -- not sure
    ok, spot_or_whynot = find_hotspot_for_pasting(obj)
    return ok

def find_hotspot_for_pasting(obj):
    """Return (True, hotspot) or (False, reason),
    depending on whether obj is pastable in Build mode
    (i.e. on whether a copy of it can be bonded to an existing singlet).
    In the two possible return values,
    hotspot will be one of obj's singlets, to use for pasting it
    (but the one to actually use is the one in the copy made by pasting),
    or reason is a string (for use in an error message) explaining why there isn't
    a findable hotspot. For now, the hotspot can only be found for certain
    chunks (class molecule), but someday it might be defined for certain
    groups, as well, or anything else that can be bonded to an existing singlet.
    """
    if not isinstance(obj, molecule):
        return False, "only chunks can be pastable" #e for now
##    fix_bad_hotspot(obj)
    if len(obj.singlets) == 0:
        return False, "no open bonds in %r (only pastable in empty space)" % obj.name
    elif len(obj.singlets) > 1 and not obj.hotspot:
        return False, "%r has %d open bonds, but none has been set as its hotspot" % (obj.name, len(obj.singlets))
    else:
        return True, obj.hotspot or obj.singlets[0]
    pass

    #bruce 050217: fix_bad_hotspot won't be needed anymore, since I'm making mol.hotspot use getattr to fix other bugs
##def fix_bad_hotspot(mol): # bug workaround [guessing it'll fix a bug I noticed, but this is speculative so far -- bruce 050121]
##    if mol.hotspot and (mol.hotspot not in mol.singlets):
##        if platform.atom_debug:
##            print "atom_debug: fix_bad_hotspot removed a bad hotspot from %r" % mol
##        mol.hotspot = None
##    return

def do_what_MainWindowUI_should_do(w):
    w.depositAtomDashboard.clear()

#    w.depositAtomDashboard.addSeparator()

    w.depositAtomLabel = QLabel(w.depositAtomDashboard,"Build")
    w.depositAtomLabel.setText(" Build ")
    w.depositAtomDashboard.addSeparator()

    w.pasteComboBox = QComboBox(0,w.depositAtomDashboard,
                                     "pasteComboBox")
    # bruce 041124: that combobox needs to be wider, or to grow to fit items
    # (before this change it had width 100 and minimumWidth 0):
    w.pasteComboBox.setMinimumWidth(160) # barely holds "(clipboard is empty)"

    w.depositAtomDashboard.addSeparator()

    w.elemChangeComboBox = QComboBox(0,w.depositAtomDashboard,
                                     "elemChangeComboBox")
    
    w.modifySetElementAction.addTo(w.depositAtomDashboard)

    w.depositAtomDashboard.addSeparator()

    bg = QButtonGroup(w.depositAtomDashboard)
    lay = QHBoxLayout(bg)
    lay.setAutoAdd(True)
    w.depositAtomDashboard.pasteRB = QRadioButton("Paste", bg)
    w.depositAtomDashboard.atomRB = QRadioButton("Atom", bg)
    
    w.depositAtomDashboard.addSeparator()
    w.toolsDoneAction.addTo(w.depositAtomDashboard)
    w.depositAtomDashboard.setLabel("Build")
    w.elemChangeComboBox.clear()
    w.elemChangeComboBox.insertItem("Hydrogen")
    w.elemChangeComboBox.insertItem("Helium")
    w.elemChangeComboBox.insertItem("Boron")
    w.elemChangeComboBox.insertItem("Carbon")
    w.elemChangeComboBox.insertItem("Nitrogen")
    w.elemChangeComboBox.insertItem("Oxygen")
    w.elemChangeComboBox.insertItem("Fluorine")
    w.elemChangeComboBox.insertItem("Neon")
    w.elemChangeComboBox.insertItem("Aluminum")
    w.elemChangeComboBox.insertItem("Silicon")
    w.elemChangeComboBox.insertItem("Phosphorus")
    w.elemChangeComboBox.insertItem("Sulfur")
    w.elemChangeComboBox.insertItem("Chlorine")
    w.elemChangeComboBox.insertItem("Argon")
    w.elemChangeComboBox.insertItem("Germanium")
    w.elemChangeComboBox.insertItem("Arsenic")
    w.elemChangeComboBox.insertItem("Selenium")
    w.elemChangeComboBox.insertItem("Bromine")
    w.elemChangeComboBox.insertItem("Krypton")
    #w.elemChangeComboBox.insertItem("Antimony")
    #w.elemChangeComboBox.insertItem("Tellurium")
    #w.elemChangeComboBox.insertItem("Iodine")
    #w.elemChangeComboBox.insertItem("Xenon")
    w.connect(w.elemChangeComboBox,SIGNAL("activated(int)"),w.elemChange)

class depositMode(basicMode):
    """ This class is used to manually add atoms to create any structure.
       Users know it as "Build mode".
    """
    
    # class constants
    backgroundColor = 74/255.0, 186/255.0, 226/255.0
    gridColor = 74/255.0, 186/255.0, 226/255.0
    modename = 'DEPOSIT' 
    msg_modename = "Build mode" 
    default_mode_status_text = "Mode: Build"

    def __init__(self, glpane):
        basicMode.__init__(self, glpane)
        self.pastables_list = [] #k not needed here?

    # methods related to entering this mode
    
    dont_update_gui = True
    def Enter(self):
        #Huaicai 2/28: Move the following statement to surface(), which will
        # be called by Draw() and then by paintGL(), so it will make sure 
        # self.makeCurrent() is called before any OpenGL call.
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        basicMode.Enter(self)
        self.o.assy.unpickatoms()
        self.o.assy.unpickparts()
        self.saveDisp = self.o.display
        self.o.setDisplay(diTUBES)
        self.o.assy.selwhat = 0
        self.new = None # bruce 041124 suspects this is never used
        self.modified = 0 # bruce 040923 new code
        self.pastable = None #k would it be nicer to preserve it from the past??
            # note, this is also done redundantly in init_gui.
        self.o.selatom = None
        self.reset_drag_vars()
        self.pastables_list = [] # should be ok, since update_gui comes after this...
        self.dont_update_gui = True # until changed in init_gui
##        self.UpdateDashboard # ... but it was not happening, not sure why,
##            # so let's force it to happen -- i hope this is ok! Maybe not.
##            # seems to have no effect... probably init_gui happens after it;
##            # at least it does in _enterMode. ####@@@@

    def reset_drag_vars(self):
        #bruce 041124 split this out of Enter; as of 041130,
        # required bits of it are inlined into Down methods as bugfixes
        self.dragatom = None
        self.dragmol = None
        self.pivot = None
        self.pivax = None
        self.baggage = []
        self.line = None
    
    # init_gui does all the GUI display when entering this mode [mark 041004]
    
    # bruce comment 041124 -- init_gui was also being used to update the gui
    # within the mode. That's wrong (especially when it makes someone think
    # that external code should ever call init_gui), so I split out from it an
    # update_gui method, which should be defined here but not called directly
    # except by the internal mode code in modes.py; this file or other files
    # can call mode.UpdateDashboard() when they think that's necessary,
    # which might call mode.update_gui(), or might "invalidate the dashboard"
    # so that mode.update_gui()
    # gets called sometime before the user-event processing is done.
    
    def init_gui(self):
        """called once each time the mode is entered;
        should be called only by code in modes.py
        """
        self.dont_update_gui = True # redundant with Enter, I think; changed below
            # (the possible orders of calling all these mode entering/exiting
            #  methods is badly in need of documentation, if not cleanup...
            #  [says bruce 050121, who is to blame for this])
        self.o.setCursor(self.w.DepositAtomCursor)
        # load default cursor
        self.w.toolsDepositAtomAction.setOn(1) # turn on the Deposit Atoms icon

        self.pastable = None # by bruce 041124, for safety

        # connect signals (these ought to be disconnected in restore_gui ##e)
        self.w.connect(self.w.pasteComboBox,SIGNAL("activated(int)"),
                       self.setPaste)
        self.w.connect(self.w.elemChangeComboBox,SIGNAL("activated(int)"),
                       self.setAtom)
            # Qt doc about SIGNAL("activated(int)"): This signal is not emitted
            # if the item is changed programmatically, e.g. using setCurrentItem().
            # Good! [bruce 050121 comment]
        self.w.connect(self.w.depositAtomDashboard.pasteRB,
                       SIGNAL("pressed()"), self.setPaste)
        self.w.connect(self.w.depositAtomDashboard.atomRB,
                       SIGNAL("pressed()"), self.setAtom)
        
        self.w.depositAtomDashboard.show() # show the Deposit Atoms dashboard
        
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"

        self.dont_update_gui = False

        return # the caller will now call update_gui(); we rely on that [bruce 050122]
    
    def update_gui(self): #bruce 050121 heavily revised this [called by basicMode.UpdateDashboard]
        """can be called many times during the mode;
        should be called only by code in modes.py
        """
##        if not self.now_using_this_mode_object():
##            print "update_gui returns since not self.now_using_this_mode_object"
##            return #k can this ever happen? yes, when the mode is entered!
##            # this was preventing the initial update_gui in _enterMode from running...
        
        # avoid unwanted recursion [bruce 041124]
        # [bruce 050121: this is not needed for reason it was before,
        #  but we'll keep it (in fact improve it) in case it's needed now
        #  for new reasons -- i don't know if it is, but someday it might be]
        if self.dont_update_gui:
            print "update_gui returns since self.dont_update_gui" ####@@@@
            return
        # now we know self.dont_update_gui == False, so ok that we reset it to that below (I hope)
        self.dont_update_gui = True
        try:
            self.update_gui_0()
        except:
            print_compact_traceback("exception from update_gui_0: ")
        self.dont_update_gui = False
        self.resubscribe_to_clipboard_members_changed()
        return

    def update_gui_0(self): #bruce 050121 split this out and heavily revised it
        # [Warning, bruce 050316: when this runs, new clipboard items might not yet have
        # their own Part, or the correct Part! So this code should not depend
        # on the .part member of any nodes it uses. If this matters, a quick
        # (but inefficient) fix would be to call that method right here...
        # except that it might not be legal to do so! Instead, we'd probably need
        # to arrange to do the actual updating (this method) only at the end of
        # the current user event. We'll need that ability pretty soon for other
        # reasons (probably for Undo), so it's ok if we need it a bit sooner.]
        
        # update the contents of self.w.pasteComboBox
        # to match the set of pastable objects on the clipboard,
        # which is cached in pastables_list for use when spinbox is "spun",
        # and update the current item to be what it used to be (if that is
        # still available in the list), else the last item (if there are any items).

        # First, if self.pastable is None, set it to the current value from
        # the spinbox and prior list, in case some other code set it to None
        # when it set pasteP to False (tho I don't think that other code really
        # needs to do that). This is safe even if called "too early". But if it's
        # already set, don't change it, so callers of UpdateDashboard can set it
        # to the value they want, even if that value is not yet in the spinbox
        # (see e.g. setHotspot).
        if not self.pastable:
            self.update_pastable()
        
        # update the list of pastable things - candidates are all objects
        # on the clipboard
        members = self.o.assy.shelf.members[:]
        ## not needed or correct since some time ago [bruce 050110]:
        ##   members.reverse() # bruce 041124 -- model tree seems to have them backwards
        self.pastables_list = filter( is_pastable, members)

        # experiment 050122: mark the clipboard items to influence their appearance
        # in model tree... not easy to change their color, so maybe we'll let this
        # change their icon (just in chunk.py for now). Not yet done. We'd like the
        # one equal to self.pastable (when self.pasteP and this is current mode)
        # to look the most special. But that needs to be recomputed more often
        # than this runs. Maybe we'll let the current mode have an mtree-icon-filter??
        # Or, perhaps, let it modify the displayed text in the mtree, from node.name. ###@@@
        for mem in members:
            mem._note_is_pastable = False # set all to false...
        for mem in self.pastables_list:
            mem._note_is_pastable = True # ... then change some of those to true
        
        # update the spinbox contents to match that
        self.w.pasteComboBox.clear()
        for ob in self.pastables_list:
            self.w.pasteComboBox.insertItem(ob.name)
        if not self.pastables_list:
            # insert a text label saying why spinbox is empty [bruce 041124]
            if members:
                whynot = "(no clips are pastable)" # this text should not be longer than the one below, for now
            else:
                whynot = "(clipboard is empty)"
            self.w.pasteComboBox.insertItem( whynot)
            #e Should we disable this item? we can't (acc'd to Qt doc for combobox),
            # but it might work to change font for all items using box.setFont,
            # but I didn't yet find out if that could be used to gray them out.
            # But maybe it will work to disable or enable the entire widget?
            # No. Maybe some other QWidget method? Look later, not urgent.
            # [bruce 050121]
            self.pastable = None
            enabled = 0
        else:
            # choose the best current item for self.pastable and spinbox position
            # (this is the same pastable as before, if it's still available)
            if self.pastable not in self.pastables_list: # (works even if self.pastable is None)
                self.pastable = self.pastables_list[-1]
                # use the last one (presumably the most recently added)
                # (no longer cares about selection of clipboard items -- bruce 050121)
            assert self.pastable # can fail if None is in the list or "not in" doesn't work right for None
            cx = self.pastables_list.index(self.pastable)
            self.w.pasteComboBox.setCurrentItem(cx)
                # Q. does that activate it and tell us it changed, as if user changed it?
                # A: no -- Qt doc about SIGNAL("activated(int)"): This signal is not emitted
                # if the item is changed programmatically, e.g. using setCurrentItem().
                # Good!
            enabled = 1
        
        self.w.pasteComboBox.setEnabled(enabled)
        
        #e future: if model tree indicates self.pastable somehow, e.g. by color of
        # its name, update it. (It might as well also show "is_pastables" that way.) ###@@@ good idea...
        
        # Q: If not self.pastable, should we call setAtom to disable pasting??
        # A: I don't think so, since user might not want atom-depositing enabled,
        #    and they must have explicitly chosen paste mode even though there are
        #    no pastable items.
        # Update the radio buttons to match pasteP (which we did not change!).
        # This is needed since changing the spinbox item sets pasteP.
        if self.w.pasteP:
            self.w.depositAtomDashboard.pasteRB.setOn(True)
        else:
            self.w.depositAtomDashboard.atomRB.setOn(True)
        return

    def clipboard_members_changed(self, clipboard): #bruce 050121
        "we'll subscribe this method to changes to shelf.members, if possible"
        if self.now_using_this_mode_object():
            self.UpdateDashboard()
                #e ideally we'd set an inval flag and call that later, but when?
                # For now, see if it works this way. (After all, the old code called
                # UpdateDashboard directly from certain Node or Group methods.)
            ## call this from update_gui (called by UpdateDashboard) instead,
            ## so it will happen the first time we're setting it up, too:
            ## self.resubscribe_to_clipboard_members_changed()
        return

    def resubscribe_to_clipboard_members_changed(self):
        try:
            ###@@@@ need this to avoid UnboundLocalError: local variable 'shelf' referenced before assignment
            # but that got swallowed the first time we entered mode!
            # but i can't figure out why, so neverind for now [bruce 050121]
            shelf = self.o.assy.shelf
            shelf.call_after_next_changed_members # does this method exist?
        except AttributeError:
            # this is normal, until I commit new code to Utility and model tree! [bruce 050121]
            pass
        except:#k should not be needed, but I'm not positive, in light of bug-mystery above
            raise
        else:
            shelf = self.o.assy.shelf
            func = self.clipboard_members_changed
            shelf.call_after_next_changed_members(func, only_if_new = True)
                # note reversed word order in method names (feature, not bug)
        return
    
    # methods related to exiting this mode [bruce 040922 made these from
    # old Done method, and added new code; there was no Flush method]

    def haveNontrivialState(self):
        return False
        #return self.modified # bruce 040923 new code

    def StateDone(self):
        return None
    # we never have undone state, but we have to implement this method,
    # since our haveNontrivialState can return True

    def StateCancel(self):
        # to do this correctly, we'd need to remove the atoms we added
        # to the assembly; we don't attempt that yet [bruce 040923,
        # verified with Josh]
        change_desc = "your changes are"
            #e could use the count of changes in self.modified,
            #to say "%d changes are", or "change is"...
        msg = "%s Cancel not implemented -- %s still there.\n\
        You can only leave this mode via Done." % \
              ( self.msg_modename, change_desc )
        self.warning( msg, bother_user_with_dialog = 1)
        return True # refuse the Cancel
    
    # restore_gui handles all the GUI display when leavinging this mode
    # [mark 041004]
    def restore_gui(self):
        self.w.depositAtomDashboard.hide() # Stow away dashboard
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"


    def restore_patches(self):
    	self.o.setDisplay(self.saveDisp) #bruce 041129; see notes for bug 133
        self.o.selatom = None

    def clear(self):
        self.new = None

    # event methods
    
    def keyPress(self,key):
        # bruce comment 041220:
        # doesn't call basicMode method, so Delete key is not active. Good??
        # bruce 050128: no, not good. And it shows selection anyway... so do it below.
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.KillCursor)
        for sym, code, num in elemKeyTab:
            if key == code:
                self.w.setElement(num) ###@@@ does this update our own spinbox too??
        basicMode.keyPress(self,key) # bruce 050128
        return

    def keyRelease(self,key):
        basicMode.keyRelease(self, key)
        if key == Qt.Key_Control:
            self.o.setCursor(self.w.DepositAtomCursor)

    def rightCntlDown(self, event):          
            basicMode.rightCntlDown(self, event)
            self.o.setCursor(self.w.DepositAtomCursor)

    def getCoords(self, event):
        """ Retrieve the object coordinates of the point on the screen
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
        # BTW this is now the only remaining call of findpick.
        # Best guess: this should ignore invisibles and be limited by water
        # and near clipping; but still use 2.0 radius. ###@@@

        # bruce 041214 comment: this looks like an inlined mousepoints...
        x = event.pos().x()
        y = self.o.height - event.pos().y()

        p1 = A(gluUnProject(x, y, 0.0))
        p2 = A(gluUnProject(x, y, 1.0))
        at = self.o.assy.findpick(p1,norm(p2-p1),2.0)
        if at: pnt = at.posn()
        else: pnt = - self.o.pov
        k = (dot(self.o.lineOfSight,  pnt - p1) /
             dot(self.o.lineOfSight, p2 - p1))

        return p1+k*(p2-p1) # always return a point on the line from p1 to p2

    def bareMotion(self, event): # bruce 050124 split update_selatom from this
        """called for motion with no button down
        [should not be called otherwise -- call update_selatom directly instead]
        """
        self.update_selatom(event, msg_about_click = True)
        return
    
    def update_selatom(self, event, singOnly = False, msg_about_click = False):
        "keep selatom up-to-date, as atom under mouse"
        # bruce 050124 split this out of bareMotion so options can vary
        
        # bruce 041206 optimized redisplay (for some graphics chips)
        # by keeping selatom out of its chunk's display list,
        # so no changeapp is needed when selatom changes.
        # bruce 041213 fixed several bugs using new findAtomUnderMouse,
        # including an unreported one for atoms right at the eyeball position.
        
        oldselatom = self.o.selatom
        # warning: don't change self.o.selatom yet, since findAtomUnderMouse uses
        # its current value to support hysteresis for its selection radius.
        atm = self.o.assy.findAtomUnderMouse(event, water_cutoff = True, singlet_ok = True)
        assert oldselatom == self.o.selatom
        if atm and (atm.element==Singlet or not singOnly):
            pass # we'll use this atm as the new selatom
        else:
            atm = None
        self.o.selatom = atm
        if msg_about_click: # [always do this, since many things can change what it should say]
            # come up with a status bar message about what we would paste now.
            # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable]
            msg = self.describe_leftDown_action( self.o.selatom)
            self.w.history.transient_msg( msg) # uses status bar #e rename that method
        if self.o.selatom != oldselatom:
            # update display
            self.o.gl_update() # draws selatom too, since its chunk is not hidden
        return

    def describe_leftDown_action(self, selatom): # bruce 050124
        # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable;
        #  this copies a lot of logic from leftDown, which is bad, should be merged somehow --
        #  maybe as one routine to come up with a command object, with a str method for messages,
        #  called from here to say potential cmd or from leftDown to give actual cmd to do ##e]
        # WARNING: this runs with every bareMotion (even when selatom doesn't change),
        # so it had better be fast.
        onto_open_bond = selatom and selatom.is_singlet()
        try:
            what = self.describe_paste_action(onto_open_bond) # always a string
            if what and len(what) > 60: # guess at limit
                what = what[:60] + "..."
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: describe_paste_action failed: ")
            what = "click to paste"
        if onto_open_bond:
            cmd = "%s onto open bond at %s" % (what, self.posn_str(selatom))
            #bruce 050416 also indicate hotspot if we're on clipboard
            # (and if this hotspot will be drawn in special color, since explaining that
            #  special color is the main point of this statusbar-text addendum)
            if selatom == selatom.molecule.hotspot and not self.viewing_main_part():
                # also only if chunk at toplevel in clipboard (ie pastable)
                # (this is badly in need of cleanup, since both here and chunk.draw
                #  should not hardcode the cond for that, they should all ask the same method here)
                if selatom.molecule in self.o.assy.shelf.members: 
                    cmd += " (hotspot)"
        elif selatom:
            cmd = "click to drag %r" % selatom
        else:
            cmd = "%s at \"water surface\"" % what
            #e cmd += " at position ..."
        return cmd
        
    def describe_paste_action(self, onto_open_bond): # bruce 050124; added onto_open_bond flag, 050127
        "return a description of what leftDown would paste or deposit (and how user could do that), if done now"
        #e should be split into "determine what to paste" and "describe it"
        # so the code for "determine it" can be shared with leftDown
        # rather than copied from it as now
        if self.w.pasteP:
            p = self.pastable
            if p:
                if onto_open_bond:
                    ok = is_pastable_onto_singlet( p) #e if this is too slow, we'll memoize it
                else:
                    ok = is_pastable_into_free_space( p) # probably always true, but might as well check
                if ok:
                    return "click to paste %s" % self.pastable.name
                else:
                    return "can't paste %s" % self.pastable.name
            else:
                return "nothing to paste" # (trying would be an error)
        else:
            el =  PeriodicTable.getElement(self.w.Element)
            return "click to deposit %s" % el.name
            
    def posn_str(self, atm): #bruce 041123
        """return the position of an atom
        as a string for use in our status messages
        (also works if given an atom's position vector itself -- kluge, sorry)
        """
        try:
            x,y,z = atm.posn()
        except AttributeError:
            x,y,z = atm # kluge to accept either arg type
        return "(%.2f, %.2f, %.2f)" % (x,y,z)

    def ensure_visible(self, chunk, status):
        """if chunk is not visible now, make it visible by changing its
        display mode, and append a warning about this to the given status message
        """
        # By bruce 041207, to fix bug 229 part B (as called in comment #2),
        # by making each deposited chunk visible if it otherwise would not be.
        # Note that the chunk is now (usually?) the entire newly deposited thing,
        # but after future planned changes to the code, it might instead be a
        # preexisting chunk which was extended. Either way, we'll make the
        # entire chunk visible if it's not.
        if chunk and chunk.get_dispdef(self.o) == diINVISIBLE:
            chunk.setDisplay(diTUBES) # Build mode's own default display mode
            status += " (warning: gave it Tubes display mode)"
        elif platform.atom_debug:
            pass ## status += " (atom_debug: already visible)"
        return status
        
    def leftDown(self, event):
        """If there's nothing nearby, deposit a new atom.
        If cursor is on a singlet, deposit an atom bonded to it.
        If it is a real atom, drag it around.
        """
        # bruce 050124 warning: update_selatom now copies lots of logic from here;
        # see its comments if you change this
        self.w.history.transient_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]
        self.pivot = self.pivax = self.dragmol = None #bruce 041130 precautions
        self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
        a = self.o.selatom
        el =  PeriodicTable.getElement(self.w.Element)
        self.modified = 1
        self.o.assy.changed()
        if a: # if something was "lit up"
            ## self.w.history.message("%r" % a) #bruce 041208 to zap leftover msgs
            if a.element == Singlet:
                a0 = a.singlet_neighbor() # do this before a is killed!
                if self.w.pasteP:
                    # user wants to paste something
                    if self.pastable:
                        chunk, desc = self.pasteBond(a)
                        if chunk:
                            ## status = "replaced open bond on %r with %s (%s)" % (a0, chunk.name, desc)
                            status = "replaced open bond on %r with %s" % (a0, desc) # is this better? [bruce 050121]
                        else:
                            status = desc
                            # bruce 041123 added status message, to fix bug 163,
                            # and added the rest of them to describe what we do
                            # (or why we do nothing)
                    else:
                        # do nothing
                        status = "nothing selected to paste" #k correct??
                        chunk = None #bruce 041207
                else:
                    # user wants to create an atom of element el
                    a1, desc = self.attach(el, a)
                    if a1 != None:
                        status = "replaced open bond on %r with new atom %s at %s" % (a0, desc, self.posn_str(a1))
                        chunk = a1.molecule #bruce 041207
                    else:
                        status = desc
                        chunk = None #bruce 041207
                    del a1, desc
                self.o.selatom = None
                self.dragmol = None
                status = self.ensure_visible(chunk, status) #bruce 041207
                self.w.history.message(status)
                self.w.win_update()
                return # don't move a newly bonded atom
            # else we've grabbed an atom
            elif a.realNeighbors(): # probably part of larger molecule
                self.dragmol = a.molecule
                e=a.molecule.externs
                if len(e)==1: # pivot around one bond
                    self.pivot = e[0].center
                    self.pivax = None
                    return
                elif len(e)==2: # pivot around 2 bonds
                    self.pivot = e[0].center
                    self.pivax = norm(e[1].center-e[0].center)
                    return
                elif len(e)==0: # drag it around
                    self.pivot = None
                    self.pivax = True #k might have bugs if realNeighbors in other mols??
                    #bruce 041130 tried using this case for 1-atom mol as well,
                    # but it made singlet highlighting wrong (due to pivax??).
                    # (Could that mean there's some sort of basepos-updating bug
                    # in mol.pivot? ###@@@)
                    return
                # more than 2 externs -- fall thru
            elif len(a.molecule.atoms) == 1 + len(a.bonds):
                #bruce 041130 added this case to let plain left drag work to
                # drag a 1-real-atom mol, not only a larger mol as before; the
                # docstring makes me think this was the original intention, and
                # the many "invalid bug reports" whose authors assume this will
                # work imply this feature is desired and intuitively expected.
                self.dragmol = a.molecule
                # fall thru
            else:
                #bruce 041130 added this case too:
                # no real neighbors, but more than just the singlets in the mol
                # (weird but possible)... for now, just do the same, though if
                # there are 1 or 2 externs it might be better to do pivoting. #e
                self.dragmol = a.molecule
                # fall thru
        else:
            # nothing was "lit up" -- we're in empty space;
            # create something and (if an atom) drag it rigidly
            atomPos = self.getCoords(event)
            if self.w.pasteP:
                if self.pastable:
                    chunk, desc = self.pasteFree(atomPos)
                    self.dragmol = None
                    status = "pasted %s (%s) at %s" % (chunk.name, desc, self.posn_str(atomPos))
                else:
                    # do nothing
                    status = "nothing selected to paste" #k correct??
                    chunk = None #bruce 041207
            else:
                self.o.selatom = oneUnbonded(el, self.o.assy, atomPos)
                self.dragmol = self.o.selatom.molecule
                status = "made new atom %r at %s" % (self.o.selatom, self.posn_str(self.o.selatom) )
                chunk = self.o.selatom.molecule #bruce 041207
            # now fix bug 229 part B (as called in comment #2),
            # by making this new chunk visible if it otherwise would not be
            status = self.ensure_visible(chunk, status) #bruce 041207
            self.w.history.message(status)
            # fall thru
        # move the molecule rigidly (if self.dragmol and self.o.selatom were set)
        self.pivot = None
        self.pivax = None
        self.w.win_update()
    
    def dragto(self, point, event, perp = None):
        """Return the point to which we should drag the given point,
        if event is the drag-motion event and we want to drag the point
        parallel to the screen (or perpendicular to the given direction "perp"
        if one is passed in). (Only correct for points, not extended objects,
        unless you use the point which was clicked on (not e.g. the center)
        as the dragged point.)
        """
        #bruce 041123 split this from two methods, and bugfixed to make dragging
        # parallel to screen. (I don't know if there was a bug report for that.)
        # Should be moved into modes.py and used in modifyMode too. ###e
        p1, p2 = self.o.mousepoints(event)
        if perp == None:
            perp = self.o.out
        point2 = planeXline(point, perp, p1, norm(p2-p1)) # args are (ppt, pv, lpt, lv)
        if point2 == None:
            # should never happen, but use old code as a last resort:
            point2 = ptonline(point, p1, norm(p2-p1))
        return point2
        
    def leftDrag(self, event):
        """ drag a new atom or an old atom's molecule
	"""
        #bruce 041130 revised docstring
        if not (self.dragmol and self.o.selatom): return
        m = self.dragmol
        a = self.o.selatom
        px = self.dragto(a.posn(), event)
        if self.pivot:
            po = a.posn() - self.pivot
            pxv = px - self.pivot
        if self.pivot and self.pivax:
            m.pivot(self.pivot, twistor(self.pivax, po, pxv))
        elif self.pivot:
            q1 = twistor(self.pivot-m.center, po, pxv)
            q2 = Q(q1.rot(po), pxv)
            m.pivot(self.pivot, q1+q2)
        elif self.pivax:
            m.rot(Q(a.posn()-m.center,px-m.center))
            m.move(px-a.posn())
        else:
            m.move(px-a.posn())
        #e bruce 041130 thinks this should be given a new-coordinates-message,
        # like in leftShiftDrag but starting with the atom-creation message
        # (but the entire mol gets dragged, so the msg should reflect that)
        # ###@@@
        self.o.gl_update()

    def leftUp(self, event):
        self.dragmol = None
        self.o.selatom = None
        #bruce 041130 comment: it forgets selatom, but doesn't repaint,
        # so selatom is still visible; then the next event will probably
        # set it again; all this seems ok for now, so I'll leave it alone.
        #bruce 041206: I changed my mind, since it seems dangerous to leave
        # it visible (seemingly active) but not active. So I'll repaint here.
        # In future we can consider first simulating a update_selatom at the
        # current location (to set selatom again, if appropriate), but it's
        # not clear this would be good, so *this* is what I won't do for now.
        self.o.gl_update()
	
    def leftShiftDown(self, event):
        """If there's nothing nearby, do nothing. If cursor is on a
        singlet, drag it around, rotating the atom it's bonded to if
        possible.  If it is a real atom, drag it around (but not
        the real atoms it's bonded to).
        """
        #bruce 041130 revised docstring
        self.w.history.transient_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]
        self.pivot = self.pivax = self.line = None #bruce 041130 precaution
        self.baggage = [] #bruce 041130 precaution
        self.dragatom = None #bruce 041130 fix bug 230 (1 of 2 redundant fixes)
        self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
        a = self.o.selatom
        if not a: return
        # now, if something was "lit up"
        ## self.w.history.message("%r" % a) #bruce 041208 to zap leftover msgs
        self.modified = 1
        self.o.assy.changed()
        if a.element == Singlet:
            pivatom = a.neighbors()[0]
            neigh = pivatom.realNeighbors()
            self.baggage = pivatom.singNeighbors()
            self.baggage.remove(a)
            if neigh:
                if len(neigh)==2:
                    self.pivot = pivatom.posn()
                    self.pivax = norm(neigh[0].posn()-neigh[1].posn())
                    self.baggage = []
                elif len(neigh)>2:
                    self.pivot = None
                    self.pivax = None
                    self.baggage = []
                else: # atom on a single stalk
                    self.pivot = pivatom.posn()
                    self.pivax = norm(self.pivot-neigh[0].posn())
            else: # no real neighbors
                self.pivot = pivatom.posn()
                self.pivax = None
        else: # we've grabbed an atom
            self.pivot = None
            self.pivax = None
            self.baggage = a.singNeighbors()
        self.dragatom = a
        # we need to store something unique about this event;
        # we'd use serno or time if it had one... instead this _count will do.
        global _count
        _count = _count + 1
        self.dragatom_start = _count
        self.w.win_update()
        return
                        

    def leftShiftDrag(self, event):
        """ drag the atom around
	"""
        if not self.dragatom: return
        a = self.dragatom
        apos0 = a.posn()
        px = self.dragto(a.posn(), event)
        if a.element != Singlet and not self.pivot:
            # no pivot, just dragging it around
            apo = a.posn()
            # find the delta quat for the average real bond and apply
            # it to the singlets
            n = a.realNeighbors()
            old = V(0,0,0)
            new = V(0,0,0)
            for at in n:
                old += at.posn()-apo
                new += at.posn()-px
                at.adjSinglets(a, px)
            delta = px - apo
            if n:
                q=Q(old,new)
                for at in self.baggage:
                    at.setposn(q.rot(at.posn()-apo)+px)
            else: 
                for at in self.baggage:
                    at.setposn(at.posn()+delta)
            # [Josh wrote, about the following "a.setposn(px)":]
            # there's some weirdness I don't understand
            # this doesn't work if done before the loop above
            a.setposn(px)
            # [bruce 041108 writes:]
            # This a.setposn(px) can't be done before the at.adjSinglets(a, px)
            # in the loop before it, or adjSinglets (which compares a.posn() to
            # px) would think atom a was not moving.
        elif self.pivax: # pivoting around an axis
            quat = twistor(self.pivax, a.posn()-self.pivot, px-self.pivot)
            for at in [a]+self.baggage:
                at.setposn(quat.rot(at.posn()-self.pivot) + self.pivot)
        elif self.pivot: # pivoting around a point
            quat = Q(a.posn()-self.pivot, px-self.pivot)
            for at in [a]+self.baggage:
                at.setposn(quat.rot(at.posn()-self.pivot) + self.pivot)
        self.update_selatom(event, singOnly = True) # indicate singlets we might bond to
            #bruce 041130 asks: is it correct to do that when a is real?
        if a.element == Singlet:
            self.line = [a.posn(), px]
        #bruce 041130 added status bar message with new coordinates
        apos1 = a.posn()
        if apos1 - apos0:
            ##k does this ever overwrite some other message we want to keep??
            if a.element == Singlet:
                # this message might not be useful enough to be worthwhile...
                msg = "pulling open bond %r to %s" % (a, self.posn_str(a))
            else:
                msg = "dragged atom %r to %s" % (a, self.posn_str(a))
            this_drag_id = (self.dragatom_start, self.__class__.leftShiftDrag)
            self.w.history.message(msg, transient_id = this_drag_id)
        self.o.gl_update()
        return

    def leftShiftUp(self, event):
        self.w.history.flush_saved_transients()
            # flush any transient message it saved up
        if not self.dragatom: return
        self.baggage = []
        self.line = None
        self.update_selatom(event, singOnly = True)
        if self.dragatom.is_singlet():
            if self.o.selatom and self.o.selatom != self.dragatom:
                dragatom = self.dragatom
                selatom = self.o.selatom
                if selatom.is_singlet(): #bruce 041119, just for safety
                    self.dragged_singlet_over_singlet(dragatom, selatom)
        self.dragatom = None #bruce 041130 fix bug 230 (1 of 2 redundant fixes)
        self.o.selatom = None #bruce 041208 for safety in case it's killed
        self.o.gl_update()

    def dragged_singlet_over_singlet(self, dragatom, selatom):
        #bruce 041119 split this out and added checks to fix bugs #203
        # (for bonding atom to itself) and #121 (atoms already bonded).
        # I fixed 121 by doing nothing to already-bonded atoms, but in
        # the future we might want to make a double bond. #e
        if selatom.singlet_neighbor() == dragatom.singlet_neighbor():
            # this is a bug according to the subroutine, but not to us
            print_error_details = 0
        else:
            # for any other error, let subr print a bug report,
            # since we think we caught them all before calling it
            print_error_details = 1
        flag, status = bond_at_singlets(dragatom, selatom, \
                         print_error_details = print_error_details)
        # we ignore flag, which says whether it's ok, warning, or error
        self.w.history.message("%s: %s" % (self.msg_modename, status))
        return

    ## delete with cntl-left mouse
    def leftCntlDown(self, event):
        self.w.history.transient_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]
        self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
        a = self.o.selatom
        if a:
            # this may change hybridization someday
            if a.element == Singlet: return
            self.w.history.message("deleting %r" % a) #bruce 041208
            a.kill()
            self.o.selatom = None #bruce 041130 precaution
            self.o.assy.changed()
        self.w.win_update()

# removed by bruce 041217:
##    def middleDouble(self, event):
##        """ End deposit mode
##	"""
##	self.Done()

    ###################################################################
    #   Cutting and pasting                                           #
    ###################################################################
    
    def pasteBond(self, sing):
        """If self.pastable has an unambiguous hotspot,
        paste a copy of it onto the given singlet;
        return (the copy, description) or (None, whynot)
        """
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable! See comments in pasteFree.
        # bruce 041123 added return values (and guessed docstring).
        # bruce 050121 using subr split out from this code
        ok, hotspot_or_whynot = find_hotspot_for_pasting(pastable)
        if not ok:
            whynot = hotspot_or_whynot
            return None, whynot
        hotspot = hotspot_or_whynot
        
        numol = pastable.copy(None)
        # bruce 041116 added (implicitly, by default) cauterize = 1
        # to mol.copy() above; change this to cauterize = 0 here if unwanted,
        # and for other uses of mol.copy in this file.
        # For this use, there's an issue that new singlets make it harder to
        # find a default hotspot! Hmm... I think copy should set one then.
        # So now it does [041123].
        hs = numol.hotspot or numol.singlets[0] #e should use find_hotspot_for_pasting again
        bond_at_singlets(hs,sing) # this will move hs.molecule (numol) to match
        # bruce 050217 comment: hs is now an invalid hotspot for numol, and that
        # used to cause bug 312, but this is now fixed in getattr every time the
        # hotspot is retrieved (since it can become invalid in many other ways too),
        # so there's no need to explicitly forget it here.
        self.o.assy.addmol(numol) # do this last, in case it computes bbox
        return numol, "copy of %r" % pastable.name
        
    # paste the pastable object where the cursor is (at pos)
    # warning: some of the following comment is obsolete (read all of it for the details)
    # ###@@@ should clean up this comment and code
    # - bruce 041206 fix bug 222 by recentering it now --
    # in fact, even better, if there's a hotspot, put that at pos.
    # - bruce 050121 fixing bug in feature of putting hotspot on water
    # rather than center. I was going to remove it, since Ninad disliked it
    # and I can see problematic aspects of it; but I saw that it had a bug
    # of picking the "first singlet" if there were several (and no hotspot),
    # so I'll fix that bug first, and also call fix_bad_hotspot to work
    # around invalid hotspots if those can occur. If the feature still seems
    # objectionable after this, it can be removed (or made a nondefault preference).
    # ... bruce 050124: that feature bothers me, decided to remove it completely.
    def pasteFree(self, pos):
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable!
            # (if we're operating in the same clipboard item it's stored in,
            #  and if adding numol makes that item no longer pastable.)
            # And someday the copy operation itself might auto-addmol, for some reason;
            # so to be safe, save pastable here before we change current part at all.
        numol = pastable.copy(None)
        #bruce 050217 fix_bad_hotspot no longer needed
        # [#e should we also remove the hotspot copied by mol.copy? I don't think so.]
##        fix_bad_hotspot(numol) # works around some possible bugs in other code
        cursor_spot = numol.center
##        if numol.hotspot:
##            cursor_spot = numol.hotspot.posn()
##        elif len(numol.singlets) == 1:
##            cursor_spot = numol.singlets[0].posn()
##        else:
##            cursor_spot = numol.center
        numol.move(pos - cursor_spot)
        self.o.assy.addmol(numol) 
        return numol, "copy of %r" % pastable.name


    ###################################################################
    #  Oh, ye acolytes of klugedom, feast your eyes on the following  #
    ###################################################################

    # singlet is supposedly the lit-up singlet we're pointing to.
    # make a new atom of el.
    # bond the new atom to it, and any other ones around you'd
    # expect it to form bonds with
    # [bruce comment 041115: only bonds to singlets in same molecule; why?
    #  more info 041203:
    #  answer from josh: that's a bug, but we won't fix it for alpha.
    #  bruce thinks it has a recent bug number (eg 220-230) but forgets what it is.
    #  Update 041215: fixed it below!
    # ]
    # bruce comments 041215: also makes new singlets to reach desired total
    # number of bonds. Note that these methods don't use self except to
    # find each other... could be turned into functions for general use. #e
    # To help fix bug 131 I'm splitting each of the old code's methods
    # bond1 - bond4 into a new
    # method to position and make the new atom (for any number of bonds)
    # and methods moved to class atom to add more singlets as needed.
    
    # bruce 041123 new features:
    # return the new atom and a description of it, or None and the reason we made nothing.
    def attach(self, el, singlet):
        if not el.numbonds:
            return (None, "%s makes no bonds; can't attach one to an open bond" % el.name)
        spot = self.findSpot(el, singlet)
        pl = [(singlet, spot)] # will grow to a list of pairs (s, its spot)
            # bruce change 041215: always include this one in the list
            # (probably no effect, but gives later code less to worry about;
            #  before this there was no guarantee singlet was in the list
            #  (tho it probably always was), or even that the list was nonempty,
            #  without analyzing the subrs in more detail than I'd like!)
        rl = [singlet.singlet_neighbor()]
            # list of real neighbors of singlets in pl [for bug 232 fix]
        mol = singlet.molecule
        cr = el.rcovalent

        # bruce 041215: might as well fix the bug about searching for open bonds
        # in other mols too, since it's easy; search in this one first, and stop
        # when you find enough atoms to bond to.
        searchmols = list(self.o.assy.molecules)
        searchmols.remove(singlet.molecule)
        searchmols.insert(0, singlet.molecule)
        # max number of real bonds we can make (now this can be more than 4)
        maxpl = el.numbonds
        
        for mol in searchmols:
          for s in mol.nearSinglets(spot, cr * 1.9):
              #bruce 041216 changed 1.5 to 1.9 above (it's a heuristic);
              # see email discussion (ninad, bruce, josh)
            #bruce 041203 quick fix for bug 232:
            # don't include two singlets on the same real atom!
            # (It doesn't matter which one we pick, in terms of which atom we'll
            #  bond to, but it might affect the computation in the bonding
            #  method of where to put the new atom, so ideally we'd do something
            #  more principled than just using the findSpot output from the first
            #  singlet in the list for a given real atom -- e.g. maybe we should
            #  average the spots computed for all singlets of the same real atom.
            #  But this is good enough for now.)
            ###@@@ bruce 050221: bug 372: sometimes s is not a singlet. how can this be??
            # guess: mol.singlets is not always invalidated when it should be. But even that theory
            # doesn't seem to fully explain the bug report... so let's find out a bit more, at least:
            try:
                real = s.singlet_neighbor() 
            except:
                print_compact_traceback("bug 372 caught red-handed: ")
                print "bug 372-related data: mol = %r, mol.singlets = %r" % (mol, mol.singlets)
                continue
            if real not in rl:
                pl += [(s, self.findSpot(el, s))]
                rl += [real]
          # after we're done with each mol (but not in the middle of any mol),
          # stop if we have as many open bonds as we can use
          if len(pl) >= maxpl:
            break
        del mol, s, real
        
        n = min(el.numbonds, len(pl)) # number of real bonds to make; always >= 1
        pl = pl[0:n] # discard the extra pairs (old code did this too, implicitly)
        
        # bruce 041215 change: for n > 4, old code gave up now;
        # new code makes all n bonds for any n, tho it won't add singlets
        # for n > 4. (Both old and new code don't know how to add enough
        # singlets for n >= 3 and numbonds > 4. They might add some, tho.)
        # Note: new_bonded_n uses len(pl) as its n.
        atm = self.new_bonded_n(el,pl)
        atm.make_enough_singlets() # (tries its best, but doesn't always make enough)
        desc = "%r (in %r)" % (atm, atm.molecule.name)
        #e what if caller renames atm.molecule??
        if n > 1: #e really: if n > (number of singlets clicked on at once)
            desc += " (%d bonds made)" % n
        self.o.gl_update() ##e probably should be moved to caller
        return atm, desc

    # given an element and a singlet, find the place an atom of the
    # element would like to be if bonded at the singlet
    def findSpot(self, el, singlet):
        obond = singlet.bonds[0]
        a1 = obond.other(singlet)
        cr = el.rcovalent
        pos = singlet.posn() + cr*norm(singlet.posn()-a1.posn())
        return pos
        
    def new_bonded_n(self, el, lis):
        """[private method; ignores self:]
        make and return an atom (of element el) bonded to the n singlets in lis,
        which is a list of n pairs (singlet, pos), where each pos is the ideal
        position for a new atom bonded to its singlet alone.
        The new atom will always have n real bonds and no singlets.
        We don't check whether n is too many bonds for el, nor do we care what
        kind of bond positions el would prefer. (This is up to the caller, if
        it matters; since the singlets typically already existed, there's not
        a lot that could be done about the bonding pattern, anyway, though we
        could imagine finding a position that better matched it. #e)
        """
        # bruce 041215 made this from the first parts of the older methods bond1
        # through bond4; the rest of each of those have become atom methods like
        # make_singlets_when_2_bonds. The caller (self.attach) has been revised
        # to use these, and the result is (I think) equivalent to the old code,
        # except when el.numbonds > 4, when it does what it can rather than
        # doing nothing. The purpose was to fix bug 131 by using the new atom
        # methods by themselves.
        s1, p1 = lis[0]
        mol = s1.molecule # (same as its realneighbor's mol)
        totpos = + p1 # (copy it, so += can be safely used below)
        for sk, pk in lis[1:]: # 0 or more pairs after the first
            totpos += pk # warning: += can modify a mutable totpos
        pos = totpos / (0.0 + len(lis)) # use average of ideal positions
        atm = atom(el.symbol, pos, mol)
        for sk, pk in lis:
            sk.bonds[0].rebond(sk, atm)
        return atm

    ####################
    # buttons
    ####################

    ## bruce 050302 removed this to fix bug 130, after discussion with Josh
##    # add hydrogen atoms to each dangling bond above the water
##    def modifyHydrogenate(self):
##        pnt = - self.o.pov
##        z = self.o.out
##        x = cross(self.o.up,z)
##        y = cross(z,x)
##        mat = transpose(V(x,y,z))
##
##        for mol in self.o.assy.molecules:
##            if not mol.hidden:
##                for a in mol.findAllSinglets(pnt, mat, 10000.0, -TubeRadius):
##                    a.Hydrogenate()
##        self.o.gl_update()


    ## dashboard things

    def update_pastable(self): #bruce 050121 split this out of my revised setPaste
        "update self.pastable from the current spinbox position"
        try:
            cx = self.w.pasteComboBox.currentItem()
            self.pastable = self.pastables_list[cx] # was self.o.assy.shelf.members
        except: # various causes, mostly not errors
            self.pastable = None
        ##e future: update model tree if it wants to show which clipboard item is now self.pastable,
        # but only in a way which is efficient if done multiple times, since some callers are about
        # to immediately change self.pastable again
        return
    
    def setPaste(self): #bruce 050121 heavily revised this
        "called from radiobutton presses and spinbox changes"
        self.update_pastable()
        if 1:
            ###@@@ always do this, since old code did this
            # and I didn't yet analyze changing cond to self.pastable
            self.w.pasteP = True
            self.w.depositAtomDashboard.pasteRB.setOn(True)
        else:
            pass
            ###@@@ should we do the opposite of the above when not self.pastable?
            # (or if it's no longer pastable?) guess: no.
        self.UpdateDashboard() #bruce 050121 added this
        return
        
##        if self.o.assy.shelf.members:
##            try:
##                ## bruce 050110 guessing this should be [cx] again:
##                ## self.pastable = self.o.assy.shelf.members[-1-cx]
##                self.pastable = self.o.assy.shelf.members[cx]
##                # bruce 041124 - changed [cx] to [-1-cx] (should just fix model tree)
##                # bruce 041124: the following status bar message (by me)
##                # is a good idea, but first we need to figure out how to
##                # remove it from the statusbar when it's no longer
##                # accurate!
##                #
##                ## self.w.history.message("Ready to paste %r" % self.pastable.name)
##            except: # IndexError (or its name is messed up)
##                # should never happen, but be robust [bruce 041124]
##                self.pastable = None
##        else:
##            self.pastable = None # bruce 041124

##        # bruce 041124 adding more -- I think it's needed to fully fix bug 169:
##        # update clipboard selection status to match the spinbox,
##        # but prevent it from recursing into our spinbox updater
##        self.dont_update_gui = True
##        try:
##            self.o.assy.shelf.unpick()
##            if self.pastable:
##                self.pastable.pick()
##        finally:
##            self.dont_update_gui = False
##            self.o.assy.mt.mt_update() # update model tree
##        return
        
    def setAtom(self):
        "called from radiobutton presses and spinbox changes" #k really from spinbox changes? I doubt it...#bruce 050121
        self.w.pasteP = False
        self.pastable = None # but spinbox records it... but not if set of pastables is updated! so maybe a bad idea? ##k
        self.w.depositAtomDashboard.atomRB.setOn(True)
        self.UpdateDashboard() #bruce 050121 added this

    ####################
    # utility routines
    ####################


    def Draw(self):
        """ Draw a sketch plane to indicate where the new atoms will sit
	by default
	"""
	basicMode.Draw(self)
        if self.line: drawline(white, self.line[0], self.line[1])
        self.o.assy.draw(self.o)
        self.surface()

                           
    def surface(self):
        """The water's surface
	"""
	glDisable(GL_LIGHTING)
	glColor4fv(self.gridColor + (0.6,))
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
	# the grid is in eyespace
	glPushMatrix()
	q = self.o.quat
	glTranslatef(-self.o.pov[0], -self.o.pov[1], -self.o.pov[2])
	glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)

        # The following is wrong for wide windows (bug 264).
	# To fix it requires looking at how scale is set (differently
	# and perhaps wrongly (related to bug 239) for tall windows),
	# so I'll do it later, after fixing bug 239.
	# Warning: correctness of use of x vs y below has not been verified.
	# [bruce 041214] ###@@@
	# ... but for Alpha let's just do a quick fix by replacing 1.5 by 4.0.
	# This should work except for very wide (or tall??) windows.
	# [bruce 050120]
	
        x = y = 4.0 * self.o.scale # was 1.5 before bruce 050120; still a kluge
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

    def viewing_main_part(self): #bruce 050416 ###e should refile into assy
        return self.o.assy.current_selgroup_iff_valid() == self.o.assy.tree

    call_makeMenus_for_each_event = True #bruce 050416/050420 using new feature for dynamic context menus
    
    def makeMenus(self):
        
        self.Menu_spec = []
        ###e could include disabled chunk & selatom name at the top, whether selatom is singlet, hotspot, etc.
        
        # figure out which Set Hotspot menu item to include, and whether to disable it or leave it out
        if self.viewing_main_part():
            text, meth = ('Set Hotspot and Copy as Pastable', self.setHotSpot)
                # bruce 050121 renamed this from "Set Hotspot".
                # if you want the name to be shorter, then change the method
                # to do something simpler! Note that the locally set hotspot
                # matters if we later drag this chunk to the clipboard.
                # IMHO, the complexity is a sign that the design
                # should not yet be considered finished!
        else:
            text, meth = ('Set Hotspot of clipboard item', self.setHotSpot_clipitem) ###implem
                ###e could check if it has a hotspot already, if that one is different, etc
                ###e could include atom name in menu text... Set Hotspot to X13
        if self.o.selatom and self.o.selatom.is_singlet():
            item = (text, meth)
        elif self.o.selatom:
            item = (text, meth, 'disabled')
        else:
            item = None
        if item:
            self.Menu_spec.append(item)

        # figure out Select This Chunk item text and whether to include it
        if self.o.selatom:
            name = self.o.selatom.molecule.name
            item = ('Select Chunk %r' % name, self.select)
                # bruce 050121 changed Select to a more explicit name, Select This Chunk.
                # bruce 050416 using actual chunk name. (#e Should we worry about it being too long?)
                #e should rename self.select method, once I'm sure it's not called elsewhere (not easy to confirm)
                #e maybe should disable this or change to checkmark item (with unselect action) if it's already selected??
            self.Menu_spec.append(item)

        if self.Menu_spec:
            self.Menu_spec.append(None)
        self.Menu_spec.extend( [
            # bruce 041217 added the following, rather than just Done:
            #bruce 051213 added 'checked' and reordered these to conform with toolbar.
            ('Select Chunks', self.w.toolsSelectMolecules),
            ('Select Atoms', self.w.toolsSelectAtoms), 
            ('Move Chunks', self.w.toolsMoveMolecule),
            ('Build Atoms', self.skip, 'checked'),
        ] )

        ###e submenu for pastables, with one checked? Or use Menu_spec_control for that?

        self.debug_Menu_spec = [
            ("debug: dump", self.dump)
        ]

        # Ninad asks whether we should add more elements to this [bruce 041103]
        self.Menu_spec_shift = [
            ('Carbon', self.w.setCarbon),
            ('Hydrogen', self.w.setHydrogen),
            ('Oxygen', self.w.setOxygen),
            ('Nitrogen', self.w.setNitrogen) ]

        # Ninad says this is redundant, but I left it in; Josh should decide
        # for this mode [bruce 041103]
        self.Menu_spec_control = [
            ('Passivate', self.o.assy.modifyPassivate),
            ('Hydrogenate', self.o.assy.modifyHydrogenate),
            ('Dehydrogenate', self.o.assy.modifyDehydrogenate) ]

    def setHotSpot_clipitem(self): #bruce 050416; duplicates some code from setHotSpot
        if self.o.selatom and self.o.selatom.element == Singlet:
            self.o.selatom.molecule.set_hotspot( self.o.selatom) ###e add history message??
        ###e also set this as the pastable??
        return        
        
    def setHotSpot(self): #bruce 050121 revised this and renamed its menu item
        # revised 041124 to fix bug 169, by mark and then by bruce
        """if called on a singlet, make that singlet the hotspot for
        the molecule.  (if there's only one, it's automatically the
        hotspot) [... and copy mol onto the clipboard...]
        """
        if self.o.selatom and self.o.selatom.element == Singlet:
            self.o.selatom.molecule.set_hotspot( self.o.selatom)
            
            ###e in future, if that mol is on the clipboard, don't copy it there!
            # but that can't happen until we can display clipboard items in glpane.
            # [bruce 050121]
            
            new = self.o.selatom.molecule.copy(None) # None means no dad yet
            new.move(-new.center) # perhaps no longer needed [bruce 041206]
            #bruce 041124: open clipboard, so user can see new pastable there
            self.w.mt.open_clipboard()
            
            # now add new to the clipboard
            
            # bruce 050121: first store it in self.pastable, so it will be used
            # as the new pastable if shelf.addmember updates the dashboard,
            # as it does in my local mods to Utility.py; also repeat this down
            # below in case our manual UpdateDashboard is the only one that runs.

            self.pastable = new
            
            # bruce 041124 change: add new after the other members, not before.
            # [bruce 050121 adds: see cvs for history (removed today from this code)
            #  of how this code changed as the storage order of Group.members changed
            #  (but out of sync, so that bugs often existed).]
            
            self.o.assy.shelf.addchild(new) # adds at the end
            self.o.assy.update_parts() # bruce 050316; needed when adding clipboard items.
                # Is this soon enough for UpdateDashboard?? or does it matter if it comes first? #####@@@@@
            
            # bruce 050121 don't change selection anymore; it causes too many bugs
            # to have clipboard items selected. Once my new model tree code is
            # committed, we could do this again and/or highlight the pastable
            # there in some other way.
            ##self.o.assy.shelf.unpick() # unpicks all shelf items too
            ##new.pick()
            self.w.pasteP = True
            self.pastable = new # do this again, to influence the following:
            self.UpdateDashboard()
                # (also called by shelf.addchild(), but only after my home mods
                #  to Utility.py get committed, i.e. not yet -- bruce 050121)

            self.w.mt.mt_update() # since clipboard changed
            # also update glpane if we show pastable someday; not needed now
            # [and removed by bruce 050121]
        return

    def set_pastable(self, pastable): # no one calls this yet, but they could... [bruce 050121; untested]
        """Try to set the current pastable item to the given one
        (which must already be on the clipboard and satisfy is_pastable,
        or this will set the pastable to None, tho the old pastable would
        be a better choice I suppose).
        [Someday this might be useful to call from a model tree context menu command.]
        """
        self.update_pastable()
        oldp = self.pastable
        self.pastable = pastable
        self.UpdateDashboard()
        if not self.pastable == pastable:
            #k (probably this implies self.pastable == None,
            #   but no point in checking this)
            #e someday: history message that we failed
            self.pastable = oldp
            self.UpdateDashboard()
            # if *that* fails, nothing we can do, and it never should
            # (but might if some previously pastable thing
            #  became not pastable somehow, I suppose),
            # so don't bother checking
        return
        
    def select(self):
        "select the chunk containing the highlighted atom or singlet"
        # bruce 041217 guessed docstring from code
        if self.o.selatom:
            self.o.assy.pickParts()
            self.o.assy.unpickparts()
            self.o.selatom.molecule.pick()
            self.w.win_update()
                                    
    def skip(self):
        pass

    def dump(self):
        if self.o.selatom:
            m = self.o.selatom.molecule
            print "mol", m.name, len(m.atoms), len(m.atlist), len(m.curpos)
            print 'externs', m.externs
            for a in m.atlist:
                print a
                for b in a.bonds:
                    print '   ', b

    pass # end of class depositMode
