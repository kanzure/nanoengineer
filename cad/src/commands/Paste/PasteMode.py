# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PasteMode.py

PasteMode allows depositing clipboard items into the 3D workspace. 
Its property manager lists the'pastable' clipboard items and also shows the 
current selected item in its 'Preview' box. User can return to previous mode by 
hitting 'Escape' key or pressing 'Done' button in the Paste mode. 

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
Ninad 2007-08-29: Created. 
Ninad 2008-01-02: Moved several methods originally in class depositMode to 
                  PasteMode. 
"""

from PyQt4.Qt import SIGNAL
from PyQt4.Qt import Qt

import foundation.env as env
import foundation.changes as changes

from utilities.Log import orangemsg, redmsg
from foundation.Group import Group
from model.chem import Atom
from model.chunk import Chunk
from model.elements import Singlet
from operations.pastables import is_pastable
from commands.BuildAtoms.depositMode import depositMode

from operations.pastables import find_hotspot_for_pasting
from model.bonds import bond_at_singlets

from commands.Paste.PastePropertyManager import PastePropertyManager

_superclass = depositMode

class PasteMode(depositMode):
    """
    PasteMode allows depositing clipboard items into the 3D workspace. 
    Its property manager lists the 'pastable' clipboard items and also shows the 
    current selected item in its 'Preview' box. User can return to previous mode 
    by hitting 'Escape' key  or pressing 'Done' button in the Paste mode. 
    """
    commandName = 'PASTE' 
    msg_commandName = "Paste" 
    default_mode_status_text = "Paste Command"
    featurename = "Paste"

    command_can_be_suspended = True #bruce 071011, 
                                    #GUESS ### REVIEW whether correct when 
                                    #entering Zoom/Pan/Rotate

    #Don't resume previous mode (buggy if set to True) [ninad circa 080102]
    command_should_resume_prevMode = False

    #See Command.anyCommand for details about the following flag
    command_has_its_own_gui = True

    def __init__(self, glpane):
        """
        Constructor for the class PasteMode. PasteMode allows depositing 
        clipboard items into the 3D workspace. Its property manager lists the
        'pastable' clipboard items and also shows the current selected item 
        in its 'Preview' box. User can return to previous mode by hitting 
        'Escape' key  or pressing 'Done' button in the Paste mode. 
        @param glpane: GLPane object 
        @type  glpane: L{GLPane} 
        """
        self.pastables_list = [] #@note: not needed here?
        
        _superclass.__init__(self, glpane)
    
    def Enter(self):
        """
        """
        _superclass.Enter(self)
        self.pastable = None #k would it be nicer to preserve it from the past??
            # note, this is also done redundantly in init_gui.
        self.pastables_list = [] # should be ok, since update_gui comes after 
        #this...
       
    def init_gui(self):
        """
        Do changes to the GUI while entering this mode. This includes opening 
        the property manager, updating the command toolbar, connecting widget 
        slots etc. 

        Called once each time the mode is entered; should be called only by code 
        in modes.py

        @see: L{self.restore_gui}
        """
        self.enable_gui_actions(False)
        self.dont_update_gui = True
        self.pastable = None 

        if not self.propMgr:
            self.propMgr = PastePropertyManager(self)
            changes.keep_forever(self.propMgr)

        self.propMgr.show()     

        self.connect_or_disconnect_signals(True)
        self.updateCommandToolbar(bool_entering = True)

        #Following is required to make sure that the 
        #clipboard groupbox in paste mode is updated 
        #(This is done by calling depositeMode.update_gui method 
        #Not only that, but the above mentioned method also defines 
        #self.pastable_list which is needed to paste items! This needs a 
        #separate code clean up in depositmode.py -- Ninad 20070827
        self.dont_update_gui = False


    def connect_or_disconnect_signals(self, isConnect): 
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect

        change_connect(self.exitModeAction, 
                       SIGNAL("triggered()"), 
                       self.w.toolsDone)

        self.propMgr.connect_or_disconnect_signals(isConnect)


    def restore_gui(self):
        """
        Do changes to the GUI while exiting this mode. This includes closing 
        this mode's property manager, updating the command toolbar, 
        disconnecting widget slots etc. 
        @see: L{self.init_gui}
        """
        self.propMgr.close()
        self.connect_or_disconnect_signals(False)
        self.enable_gui_actions(True)
        self.updateCommandToolbar(bool_entering = False)

    def update_gui(self):
        """
        """
        _superclass.update_gui(self)
        self.resubscribe_to_clipboard_members_changed()

    def update_gui_0(self): #bruce 050121 split this out and heavily revised it
        # [Warning, bruce 050316: when this runs, new clipboard items might not
        # yet have
        # their own Part, or the correct Part! So this code should not depend
        # on the .part member of any nodes it uses. If this matters, a quick
        # (but inefficient) fix would be to call that method right here...
        # except that it might not be legal to do so! Instead, we'd probably 
        # need
        # to arrange to do the actual updating (this method) only at the end of
        # the current user event. We'll need that ability pretty soon for other
        # reasons (probably for Undo), so it's ok if we need it a bit sooner.]

        # Subclasses update the contents of self.propMgr.clipboardGroupBox
        # (Note; earlier depositMode used to update self.w.pasteComboBox items,
        # but this implementation has been changed since 2007-09-04 after 
        # introduction of L{PasteMode}) 
        # to match the set of pastable objects on the clipboard,
        # which is cached in pastables_list for use,
        # and update the current item to be what it used to be (if that is
        # still available in the list), else the last item (if there are any 
        # items).

        # First, if self.pastable is None, set it to the current value from
        # the spinbox and prior list, in case some other code set it to None
        # when it set depositState to 'Atoms' or 'Library' (tho I don't think 
        # that other code really
        # needs to do that). This is safe even if called "too early". But if 
        # it's
        # already set, don't change it, so callers of UpdateDashboard can set it
        # to the value they want, even if that value is not yet in the spinbox
        # (see e.g. setHotSpot_mainPart).
        if not self.pastable:
            self.update_pastable()

        # update the list of pastable things - candidates are all objects
        # on the clipboard
        members = self.o.assy.shelf.members[:]
        ## not needed or correct since some time ago [bruce 050110]:
        ##   members.reverse() # bruce 041124 -- model tree seems to have them 
        ##backwards
        self.pastables_list = filter( is_pastable, members)

        # experiment 050122: mark the clipboard items to influence their 
        #appearance
        # in model tree... not easy to change their color, so maybe we'll let 
        # this
        # change their icon (just in chunk.py for now). Not yet done. We'd 
        # like the
        # one equal to self.pastable (when self.depositState == 'Clipboard'
        # and this is current mode)
        # to look the most special. But that needs to be recomputed more often
        # than this runs. Maybe we'll let the current mode have an 
        # mtree-icon-filter??
        # Or, perhaps, let it modify the displayed text in the mtree, 
        # from node.name. ###@@@
        for mem in members:
            mem._note_is_pastable = False # set all to false...
        for mem in self.pastables_list:
            mem._note_is_pastable = True # ... then change some of those to true

        if not self.pastables_list:
            # insert a text label saying why spinbox is empty [bruce 041124]
            if members:
                whynot = "(no clips are pastable)" # this text should not be 
                #longer than the one below, for now
            else:
                whynot = "(clipboard is empty)"            
            self.pastable = None
        else:
            # choose the best current item for self.pastable and spinbox
            # position
            # (this is the same pastable as before, if it's still available)
            if self.pastable not in self.pastables_list: # (works even if 
                #self.pastable is None)
                self.pastable = self.pastables_list[-1]
                # use the last one (presumably the most recently added)
                # (no longer cares about selection of clipboard items 
                #-- bruce 050121)
            assert self.pastable # can fail if None is in the list or "not in" 
            #doesn't work right for None

        #e future: if model tree indicates self.pastable somehow, e.g. by color 
        #of its name, update it. (It might as well also show "is_pastables" 
        #that way.) ###@@@ good idea...

        return

    
    def _init_flyoutActions(self):
        """
        Defines the actions to be added in the flyout toolbar section of the 
        Command Explorer.
        """

        depositMode._init_flyoutActions(self)        

        self.exitModeAction.setText("Exit Paste")


    def getFlyoutActionList(self):
        """ 
        Returns a tuple that contains mode spcific actionlists in the 
        added in the flyout toolbar of the mode. 

        @return: A tuple that contains 3 lists: subControlAreaActionList, 
               commandActionLists and allActionsList
        @rtype: tuple
        @see: L{CommandToolbar._createFlyoutToolBar} which calls this. 
        """

        subControlAreaActionList = []
        commandActionLists   = []
        allActionsList  = []

        subControlAreaActionList.append(self.exitModeAction)   

        lst = []
        commandActionLists.append(lst)      
        allActionsList.append(self.exitModeAction)

        params = (subControlAreaActionList, commandActionLists, allActionsList)

        return params

    def deposit_from_MMKit(self, atom_or_pos):
        """
        Deposit the clipboard item being previewed into the 3D workspace
        Calls L{self.deposit_from_Clipboard_page}
        @attention: This method needs renaming. L{depositMode} still uses it 
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_Clipboard_page}
        """

        if self.o.modkeys is None: # no Shift or Ctrl modifier key.
            self.o.assy.unpickall_in_GLPane()

        deposited_stuff, status = \
                       self.deposit_from_Clipboard_page(atom_or_pos) 
        deposited_obj = 'Chunk'

        self.o.selatom = None 

        if deposited_stuff:
            self.w.win_update()                
            status = self.ensure_visible( deposited_stuff, status) 
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) 

        return deposited_obj


    def deposit_from_Clipboard_page(self, atom_or_pos):
        """
        Deposit the clipboard item being previewed into the 3D workspace
        Called in L{self.deposit_from_MMKit}
        @attention: This method needs renaming. L{depositMode} still uses this 
        so simply overriden here. B{NEEDS CLEANUP}.
        @see: L{self.deposit_from_MMKit}        
        """     
        self.update_pastable()

        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if self.pastable: # bond clipboard object to the singlet
                    # do the following before <a> (the singlet) is killed
                    a0 = a.singlet_neighbor() 
                    chunk, desc = self.pasteBond(a)
                    if chunk:
                        status = "replaced bondpoint on %r with %s" % (a0, desc) 
                    else:
                        status = desc                       
                else:
                    #Nothing selected from the Clipboard to paste, so do nothing
                    status = "nothing selected to paste" #k correct??
                    chunk = None 
        else:
            if self.pastable: 
                # deposit into empty space at the cursor position
                chunk, status = self.pasteFree(atom_or_pos)
            else:
                # Nothing selected from the Clipboard to paste, so do nothing
                status = "Nothing selected to paste" 
                chunk = None 

        return chunk, status

    def update_pastable(self):
        """
        Update self.pastable based on current selected pastable 
        in the clipboard
        """
        members = self.o.assy.shelf.members[:]
        self.pastables_list = filter( is_pastable, members)

        try:
            cx = self.propMgr.clipboardGroupBox.currentRow()
            self.pastable = self.pastables_list[cx] 
        except: # various causes, mostly not errors
            self.pastable = None        
        return 

    def MMKit_clipboard_part(self): #bruce 060412; implem is somewhat of a 
        #guess, based on the code of self.deposit_from_MMKit
        """
        If the MMKit is currently set to a clipboard item, return that item's 
        Part, else return None.
        """
        if not self.pastable:
            return None
        return self.pastable.part

    def transdepositPreviewedItem(self, singlet):
        """
        Trans-deposit the current object in the preview groupbox of the 
        property manager  on all singlets reachable through 
        any sequence of bonds to the singlet <singlet>.
        """

        # bruce 060412: fix bug 1677 (though this fix's modularity should be 
        # improved; perhaps it would be better to detect this error in 
        # deposit_from_MMKit).
        # See also other comments dated today about separate fixes of some 
        # parts of that bug.
        mmkit_part = self.MMKit_clipboard_part() # a Part or None
        if mmkit_part and self.o.assy.part is mmkit_part:
            env.history.message(redmsg("Can't transdeposit the MMKit's current"\
                                       " clipboard item onto itself."))
            return

        _superclass.transdepositPreviewedItem(self, singlet)

    def resubscribe_to_clipboard_members_changed(self):
        try:
            ###@@@@ need this to avoid UnboundLocalError: local variable 'shelf'
            ##referenced before assignment
            # but that got swallowed the first time we entered mode!
            # but i can't figure out why, so neverind for now [bruce 050121]
            shelf = self.o.assy.shelf
            shelf.call_after_next_changed_members # does this method exist?
        except AttributeError:
            # this is normal, until I commit new code to Utility and model tree!
            #[bruce 050121]
            pass
        except:#k should not be needed, but I'm not positive, in light of 
            #bug-mystery above
            raise
        else:
            shelf = self.o.assy.shelf
            func = self.clipboard_members_changed
            shelf.call_after_next_changed_members(func, only_if_new = True)
                # note reversed word order in method names (feature, not bug)
        return

    def clipboard_members_changed(self, clipboard): #bruce 050121
        """
        we'll subscribe this method to changes to shelf.members, if possible
        """
        if self.isCurrentCommand():
            self.UpdateDashboard()
                #e ideally we'd set an inval flag and call that later, but when?
                # For now, see if it works this way. (After all, the old code 
                # called
                # UpdateDashboard directly from certain Node or Group methods.)
            ## call this from update_gui (called by UpdateDashboard) instead,
            ## so it will happen the first time we're setting it up, too:
            ## self.resubscribe_to_clipboard_members_changed()
            self.propMgr.update_clipboard_items() 
            # Fixes bugs 1569, 1570, 1572 and 1573. mark 060306.
            # Note and bugfix, bruce 060412: doing this now was also causing 
            # traceback bugs 1726, 1629,
            # and the traceback part of bug 1677, and some related 
            #(perhaps unreported) bugs.
            # The problem was that this is called during pasteBond's addmol 
            #(due to its addchild), before it's finished,
            # at a time when the .part structure is invalid (since the added 
            # mol's .part has not yet been set).
            # To fix bugs 1726, 1629 and mitigate bug 1677, I revised the 
            # interface to MMKit.update_clipboard_items
            # (in the manner which was originally recommented in 
            #call_after_next_changed_members's docstring) 
            # so that it only sets a flag and updates (triggering an MMKit 
            # repaint event), deferring all UI effects to
            # the next MMKit event.
        return

    # paste the pastable object where the cursor is (at pos)
    # warning: some of the following comment is obsolete (read all of it for 
    # the details)
    # ###@@@ should clean up this comment and code
    # - bruce 041206 fix bug 222 by recentering it now --
    # in fact, even better, if there's a hotspot, put that at pos.
    # - bruce 050121 fixing bug in feature of putting hotspot on water
    # rather than center. I was going to remove it, since Ninad disliked it
    # and I can see problematic aspects of it; but I saw that it had a bug
    # of picking the "first singlet" if there were several (and no hotspot),
    # so I'll fix that bug first, and also call fix_bad_hotspot to work
    # around invalid hotspots if those can occur. If the feature still seems
    # objectionable after this, it can be removed (or made a nondefault
    # preference).
    # ... bruce 050124: that feature bothers me, decided to remove it 
    #completely.
    def pasteFree(self, pos):
        self.update_pastable()
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable!
            # (if we're operating in the same clipboard item it's stored in,
            #  and if adding numol makes that item no longer pastable.)
            # And someday the copy operation itself might auto-addmol, for 
            # some reason; so to be safe, save pastable here before we change
            # current part at all.

        chunk, status = self.o.assy.paste(pastable, pos)
        return chunk, status

    def pasteBond(self, sing):
        """
        If self.pastable has an unambiguous hotspot,
        paste a copy of self.pastable onto the given singlet;
        return (the copy, description) or (None, whynot)
        """
        self.update_pastable()
        pastable = self.pastable
            # as of 050316 addmol can change self.pastable! See comments in 
            #pasteFree.
        # bruce 041123 added return values (and guessed docstring).
        # bruce 050121 using subr split out from this code
        ok, hotspot_or_whynot = find_hotspot_for_pasting(pastable)
        if not ok:
            whynot = hotspot_or_whynot
            return None, whynot

        hotspot = hotspot_or_whynot

        if isinstance(pastable, Chunk):
            numol = pastable.copy_single_chunk(None)
            #bruce 080314 use new name copy_single_chunk
            # bruce 041116 added (implicitly, by default) cauterize = 1
            # to mol.copy() above; change this to cauterize = 0 here if 
            # unwanted, and for other uses of mol.copy in this file.
            # For this use, there's an issue that new singlets make it harder to
            # find a default hotspot! Hmm... I think copy should set one then.
            # So now it does [041123].
            hs = numol.hotspot or numol.singlets[0] #e should use 
            #find_hotspot_for_pasting again
            bond_at_singlets(hs,sing) # this will move hs.molecule (numol) to 
            #match
            # bruce 050217 comment: hs is now an invalid hotspot for numol, 
            # and that used to cause bug 312, but this is now fixed in getattr 
            # every time the
            # hotspot is retrieved (since it can become invalid in many other
            # ways too),so there's no need to explicitly forget it here.
            if self.pickit():
                numol.pickatoms()
                #bruce 060412 worries whether pickatoms is illegal or 
                #ineffective (in both pasteBond and pasteFree)
                # given that numol.part is presumably not yet set (until after 
                #addmol). But these seem to work
                # (assuming I'm testing them properly), so I'm not changing 
                #this. [Why do they work?? ###@@@]
            self.o.assy.addmol(numol) # do this last, in case it computes bbox
            return numol, "copy of %r" % pastable.name
        elif isinstance(pastable, Group):
            msg = "Pasting a group with hotspot onto a bond point " \
                  "is not implemented"
            return None, msg
            ##if debug_flags.atom_debug:     
                ###@@@ EXPERIMENTAL CODE TO PASTE a GROUP WITH A HOTSPOT  
                ##if 0:
                    ### hotspot neighbor atom
                    ##attch2Singlet = atom_or_pos
                    ##hotspot_neighbor = hotspot.singlet_neighbor()
                    ### attach to atom
                    ##attch2Atom = attch2Singlet.singlet_neighbor() 
                    ##rotOffset = Q(hotspot_neighbor.posn() - hotspot.posn(), 
                                  ##attch2Singlet.posn() - attch2Atom.posn())

                    ##rotCenter = newMol.center
                    ##newMol.rot(rotOffset)

                    ##moveOffset = attch2Singlet.posn() - hs.posn()
                    ##newMol.move(moveOffset)

                    ##self.graphicsMode._createBond(hotspot, 
                                      ##hotspot_neighbor, 
                                      ##attch2Singlet, 
                                      ##attch2Atom)
                    ##self.o.assy.addmol(newMol)
                    ##########
                    ####newGroup = self.pasteGroup(pos, pastable)      
                    ##return newGroup, "copy of %r" % newGroup.name   
