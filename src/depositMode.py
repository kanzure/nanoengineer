# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
depositMode.py -- Build mode.

$Id$

- bruce 050513 optims: using 'is' and 'is not' rather than '==', '!='
  for atoms, elements, atomtypes, in several places (not all commented individually); 050513

- bruce 050913 used env.history in some places.
"""
__author__ = "Mark" 
    # Josh was the original author, but this has been largely rewritten by Mark. mark 060214.

from Numeric import *
from selectMode import *
from VQT import *
from chem import *
import drawer
from constants import elemKeyTab, GL_FAR_Z
import platform
from debug import print_compact_traceback
from elements import PeriodicTable
from Utility import imagename_to_pixmap
from HistoryWidget import orangemsg, redmsg

from bonds import bond_atoms, bond_at_singlets
from bond_constants import V_SINGLE

import env

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
        return False, "no bondpoints in %r (only pastable in empty space)" % obj.name
    elif len(obj.singlets) > 1 and not obj.hotspot:
        return False, "%r has %d bondpoints, but none has been set as its hotspot" % (obj.name, len(obj.singlets))
    else:
        return True, obj.hotspot or obj.singlets[0]
    pass
    
HIDE_PASTE_WIDGETS_FOR_A7 = True # mark 060211.

def do_what_MainWindowUI_should_do(w):

    w.depositAtomDashboard.clear()

    w.depositAtomLabel = QLabel(w.depositAtomDashboard,"Build")
    w.depositAtomLabel.setText(" Build ")
    w.depositAtomDashboard.addSeparator()

    w.pasteComboBox = QComboBox(0,w.depositAtomDashboard, "pasteComboBox")
    # bruce 041124: that combobox needs to be wider, or to grow to fit items
    # (before this change it had width 100 and minimumWidth 0):
    w.pasteComboBox.setMinimumWidth(160) # barely holds "(clipboard is empty)"

    if not HIDE_PASTE_WIDGETS_FOR_A7:
        w.depositAtomDashboard.addSeparator()

    w.elemChangeComboBox = QComboBox(0,w.depositAtomDashboard, "elemChangeComboBox")

    w.hybridComboBox = QComboBox(0,w.depositAtomDashboard, "hybridComboBox") #bruce 050606 for choice of atomtypes
    
    # Set the width of the hybrid drop box.  Mark 050810.
    width = w.hybridComboBox.fontMetrics().width(" sp2(graphitic) ")
    w.hybridComboBox.setMinimumSize ( QSize (width, 0) )

    ## not needed, I hope:
    ## w.connect(w.hybridComboBox,SIGNAL("activated(int)"),w.elemChange_hybrid) #bruce 050606
    w.hybridComboBox_elem = None
    
#    w.modifySetElementAction.addTo(w.depositAtomDashboard) # Element Selector.  Obsolete as of 050726.
    w.modifyMMKitAction.addTo(w.depositAtomDashboard) # Molecular Modeling Toolkit.  Mark 050726

    if not HIDE_PASTE_WIDGETS_FOR_A7:
        w.depositAtomDashboard.addSeparator()

    bg = QButtonGroup(w.depositAtomDashboard)
    bg.setExclusive(1)
    lay = QHBoxLayout(bg)
    lay.setAutoAdd(True)
    
    # Changed the radio buttons to push buttons.  Should change the RB suffix to Button.
    # Added bond1, bond2, bond3 and bonda to the button group.
    # Mark 050727.
    
    #bruce 050727 changes: split this into two button groups, mainly so I can implement the actions
    # more quickly and reliably for Alpha6 -- later we can discuss whether this design change is good or bad.
    # The first group is what to do when you click on a bondpoint or in empty space -- deposit atom or
    # paste object (same as before). The second group is what to do when you click on a bond;
    # it would be nice to add one more choice for "do nothing" but I'm not sure how best to do that.
    #    Also we should replace QPushButton with QToolButton, since the Qt docs for QPushButton make it clear that
    # this is correct based on how these are used. But I can't get QToolButton to work right, so I won't do this now.

    w.depositAtomDashboard.addSeparator()
    bg2 = w.depositAtomDashboard.submode_btngrp = QButtonGroup(w.depositAtomDashboard)
    bg2.setExclusive(True)
    lay2 = QHBoxLayout(bg2)
    lay2.setAutoAdd(True)

    # QToolButton property "setAutoRaise" looks much better on Linux and Windows.
    # It also looks good on Panther.  Maybe this will solve the problem on Tiger?
    # Let's ask Bruce.  Mark 050809
    
    w.depositAtomDashboard.pasteBtn = QToolButton(bg,"")
    w.depositAtomDashboard.pasteBtn.setPixmap(imagename_to_pixmap('paste1.png'))
    w.depositAtomDashboard.pasteBtn.setToggleButton(1)
    w.depositAtomDashboard.pasteBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.pasteBtn, qApp.translate("MainWindow","Paste", None))
    
    w.depositAtomDashboard.depositBtn = QToolButton(bg,"")
    w.depositAtomDashboard.depositBtn.setPixmap(imagename_to_pixmap('deposit.png'))
    w.depositAtomDashboard.depositBtn.setToggleButton(1)
    w.depositAtomDashboard.depositBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.depositBtn, qApp.translate("MainWindow","Deposit", None))
    
    w.depositAtomDashboard.buildBtn = QToolButton(bg2, "")
    w.depositAtomDashboard.buildBtn.setPixmap(imagename_to_pixmap('buildmode.png'))
    w.depositAtomDashboard.buildBtn.setToggleButton(1)
    w.depositAtomDashboard.buildBtn.setAutoRaise(1)
    w.depositAtomDashboard.buildBtn.setOn(1)
    QToolTip.add(w.depositAtomDashboard.buildBtn, qApp.translate("MainWindow","Atom Tool", None))
    
    #& Reinstate in A8.  mark 060301.
    #w.depositAtomDashboard.atomBtn = QToolButton(bg2, "")
    #w.depositAtomDashboard.atomBtn.setPixmap(imagename_to_pixmap('atom.png'))
    #w.depositAtomDashboard.atomBtn.setToggleButton(1)
    #w.depositAtomDashboard.atomBtn.setAutoRaise(1)
    #QToolTip.add(w.depositAtomDashboard.atomBtn, qApp.translate("MainWindow","Change Atom Mode", None))
    
    w.depositAtomDashboard.bond1Btn = QToolButton(bg2, "")
    w.depositAtomDashboard.bond1Btn.setPixmap(imagename_to_pixmap('bond1.png'))
    w.depositAtomDashboard.bond1Btn.setToggleButton(1)
    w.depositAtomDashboard.bond1Btn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bond1Btn, qApp.translate("MainWindow","Single Bond Tool", None))
    
    w.depositAtomDashboard.bond2Btn = QToolButton(bg2, "")
    w.depositAtomDashboard.bond2Btn.setPixmap(imagename_to_pixmap('bond2.png'))
    w.depositAtomDashboard.bond2Btn.setToggleButton(1)
    w.depositAtomDashboard.bond2Btn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bond2Btn, qApp.translate("MainWindow","Double Bond Tool", None))
    
    w.depositAtomDashboard.bond3Btn = QToolButton(bg2, "")
    w.depositAtomDashboard.bond3Btn.setPixmap(imagename_to_pixmap('bond3.png'))
    w.depositAtomDashboard.bond3Btn.setToggleButton(1)
    w.depositAtomDashboard.bond3Btn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bond3Btn, qApp.translate("MainWindow","Triple Bond Tool", None))
    
    w.depositAtomDashboard.bondaBtn = QToolButton(bg2, "")
    w.depositAtomDashboard.bondaBtn.setPixmap(imagename_to_pixmap('bonda.png'))
    w.depositAtomDashboard.bondaBtn.setToggleButton(1)
    w.depositAtomDashboard.bondaBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bondaBtn, qApp.translate("MainWindow","Aromatic Bond Tool", None))
    
    w.depositAtomDashboard.bondgBtn = QToolButton(bg2, "")
    w.depositAtomDashboard.bondgBtn.setPixmap(imagename_to_pixmap('bondg.png'))
    w.depositAtomDashboard.bondgBtn.setToggleButton(1)
    w.depositAtomDashboard.bondgBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bondgBtn, qApp.translate("MainWindow","Graphitic Bond Tool", None))

    w.depositAtomDashboard.addSeparator()
    w.depositAtomDashboard.filterCB = QCheckBox("Select Only :", w.depositAtomDashboard)
    w.depositAtomDashboard.filterCB.setChecked(0)
    w.depositAtomDashboard.filterlistLE = QLineEdit(w.depositAtomDashboard,"filter_syms_list")
    w.depositAtomDashboard.filterlistLE.setReadOnly(1)
    w.depositAtomDashboard.filterlistLE.setEnabled(0)
    
    w.depositAtomDashboard.addSeparator()
    w.depositAtomDashboard.transmuteBtn = QPushButton("Transmute", w.depositAtomDashboard)
    w.depositAtomDashboard.transmuteCB = QCheckBox(" Force to Keep Bonds", w.depositAtomDashboard)
    
    w.depositAtomDashboard.addSeparator()
    w.depositAtomDashboard.autobondCB = QCheckBox("Autobond", w.depositAtomDashboard)
    w.depositAtomDashboard.autobondCB.setChecked(env.prefs[buildModeAutobondEnabled_prefs_key])

    w.depositAtomDashboard.highlightingCB = QCheckBox("Highlighting", w.depositAtomDashboard)
    w.depositAtomDashboard.waterCB = QCheckBox("Water", w.depositAtomDashboard)

    w.depositAtomDashboard.addSeparator()
    w.toolsDoneAction.addTo(w.depositAtomDashboard)
    w.depositAtomDashboard.setLabel("Build")
    w.elemChangeComboBox.clear()
    # WARNING [comment added by bruce 050511]:
    # these are identified by *position*, not by their text, using corresponding entries in eCCBtab1;
    # this is done by win.elemChange even though nothing but depositMode calls that;
    # the current element is stored in win.Element (as an atomic number ###k).
    # All this needs cleanup so it's safer to modify this and so atomtype can sometimes be included.
    # Both eCCBtab1 and eCCBtab2 are set up and used in MWsemantics but should be moved here,
    # or perhaps with some part moved into elements.py if it ought to share code with elementSelector.py
    # and elementColors.py (though it doesn't now).
    w.elemChangeComboBox.insertItem("Hydrogen")
    w.elemChangeComboBox.insertItem("Helium")
    w.elemChangeComboBox.insertItem("Boron")
    w.elemChangeComboBox.insertItem("Carbon") # will change to two entries, Carbon(sp3) and Carbon(sp2) -- no, use separate combobox
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
    
    if HIDE_PASTE_WIDGETS_FOR_A7:
        w.pasteComboBox.hide()
        w.elemChangeComboBox.hide()
        w.hybridComboBox.hide()
        bg.hide()
        w.depositAtomDashboard.pasteBtn.hide()
        w.depositAtomDashboard.depositBtn.hide()
        #w.depositAtomDashboard.atomBtn.hide() # Not supported for A7.  mark 060214.
    
    from whatsthis import create_whats_this_descriptions_for_depositMode
    create_whats_this_descriptions_for_depositMode(w)

def update_hybridComboBox(win, text = None): #bruce 050606
    "put the names of the current element's hybridization types into win.hybridComboBox; select the specified one if provided"
    # I'm not preserving current setting, since when user changes C(sp2) to N, they might not want N(sp2).
    # It might be best to "intelligently modify it", or at least to preserve it when element doesn't change,
    # but even the latter is not obvious how to do in this code (right here, we don't know the prior element).
    #e Actually it'd be easy if I stored the element right here, since this is the only place I set the items --
    # provided this runs often enough (whenever anything changes the current element), which remains to be seen.
    
    elem = PeriodicTable.getElement(win.Element) # win.Element is atomic number
    if text is None and win.hybridComboBox_elem is elem:
        # Preserve current setting (by name) when possible, and when element is unchanged (not sure if that ever happens).
        # I'm not preserving it when element changes, since when user changes C(sp2) to N, they might not want N(sp2).
        # [It might be best to "intelligently modify it" (to the most similar type of the new element) in some sense,
        #  or it might not (too unpredictable); I won't try this for now.]
        text = str(win.hybridComboBox.currentText() )
    win.hybridComboBox.clear()
    win.hybridComboBox_elem = elem
    atypes = elem.atomtypes
    if len(atypes) > 1:
        for atype in atypes:
            win.hybridComboBox.insertItem( atype.name)
            if atype.name == text:
                win.hybridComboBox.setCurrentItem( win.hybridComboBox.count() - 1 ) #k sticky as more added?
        if HIDE_PASTE_WIDGETS_FOR_A7:
            win.hybridComboBox.hide()
        else:
            win.hybridComboBox.show()
    else:
        win.hybridComboBox.hide()
    return


class depositMode(selectAtomsMode):
    """ This class is used to manually add atoms to create any structure.
       Users know it as "Build mode".
    """
    
    # class constants
    backgroundColor = 74/255.0, 186/255.0, 226/255.0
    gridColor = 74/255.0, 186/255.0, 226/255.0
    modename = 'DEPOSIT' 
    msg_modename = "Build Mode" # Capitalized 'Mode'. Fixes bugs 612-1.2 and 1.3. mark 060323
    default_mode_status_text = "Mode: Build"
    highlight_singlets = True # Always highlight singlets in depositMode. Mark 060220.

    def __init__(self, glpane):
        selectAtomsMode.__init__(self, glpane)
        self.pastables_list = [] #k not needed here?
        self.water_enabled = env.prefs[buildModeWaterEnabled_prefs_key] # mark 060203.
            # if True, only atoms and bonds above the water surface can be 
            # highlighted and selected.
            # if False, all atoms and bonds can be highlighted and selected, and the water 
            # surface is not displayed.
        self.hover_highlighting_enabled = env.prefs[buildModeHighlightingEnabled_prefs_key]
            # Moved here as part of fix for bug 1620.  mark 060322
    # methods related to entering this mode
    
    dont_update_gui = True
    def Enter(self):
        selectAtomsMode.Enter(self)
        
        #self.o.assy.permit_pick_atoms() #bruce 050517 revised API of this call
            # moved permit_pick_atoms() to selectAtomsMode.Enter().  mark 060219.
        self.pastable = None #k would it be nicer to preserve it from the past??
            # note, this is also done redundantly in init_gui.
        self.pastables_list = [] # should be ok, since update_gui comes after this...
        self.reset_drag_vars()
        self.w.depositAtomDashboard.filterCB.setChecked(0) # generates signal.

    def reset_drag_vars(self):
        selectAtomsMode.reset_drag_vars(self)
        
        self.pivot = None
        self.pivax = None
        self.line = None
            # endpoints of the white line drawn between the cursor and a bondpoint when 
            # dragging a singlet.
        self.transdepositing = False
            # used to suppress multiple win_updates and history msgs when trans-depositing.
    
    def init_gui(self):
        """called once each time the mode is entered;
        should be called only by code in modes.py
        """
        self.dont_update_gui = True # redundant with Enter, I think; changed below
            # (the possible orders of calling all these mode entering/exiting
            #  methods is badly in need of documentation, if not cleanup...
            #  [says bruce 050121, who is to blame for this])

        self.w.toolsDepositAtomAction.setOn(1) # turn on the Deposit Atoms icon

        self.pastable = None # by bruce 041124, for safety

        update_hybridComboBox(self.w) #bruce 050606; not sure this is the best place for it

        self.bondclick_v6 = None
        self.update_bond_buttons()
        
        # Do these before connecting signals or we'll get history msgs.  Part of fix for bug 1620. mark 060322
        self.w.depositAtomDashboard.highlightingCB.setChecked(self.hover_highlighting_enabled)
        self.w.depositAtomDashboard.waterCB.setChecked(self.water_enabled)
        
        # connect signals (these all need to be disconnected in restore_gui) [bruce 050728 revised this]
        self.connect_or_disconnect_signals(True)
        
        self.w.depositAtomDashboard.show() # show the Deposit Atoms dashboard

        self.dont_update_gui = False
        
        # Huaicai 7/29/05: Open the MMKit every time entering this mode.
        self.MMKit = self.w.modifyMMKit()
        
        # This is a workaround for a bug caused by the way in which the MMKit is created.
        # This should be fixed when the MMKit code gets cleaned up.  Mark 051216.
        self.MMKit.elemGLPane.change_bg_color(self.backgroundColor, self.backgroundGradient)
        
        self.w.depositAtomDashboard.buildBtn.setOn(1) # Fixes bug 1537. mark 060301.

        return # the caller will now call update_gui(); we rely on that [bruce 050122]

    def connect_or_disconnect_signals(self, connect): #bruce 050728
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        change_connect(self.w.pasteComboBox,SIGNAL("activated(int)"),
                       self.setPaste) #widget hidden in A7. mark 060327
        change_connect(self.w.elemChangeComboBox,SIGNAL("activated(int)"),
                       self.setAtom) #widget hidden in A7. mark 060327
            # Qt doc about SIGNAL("activated(int)"): This signal is not emitted
            # if the item is changed programmatically, e.g. using setCurrentItem().
            # Good! [bruce 050121 comment]
        change_connect(self.w.depositAtomDashboard.pasteBtn,
                       SIGNAL("pressed()"), self.setPaste) #widget hidden in A7. mark 060327
        change_connect(self.w.depositAtomDashboard.depositBtn,
                       SIGNAL("pressed()"), self.setAtom) #widget hidden in A7. mark 060327
        
        # New bond slots connections to the bond buttons on the dashboard. [mark 050727]
        change_connect(self.w.depositAtomDashboard.bond1Btn,
                       SIGNAL("toggled(bool)"), self.setBond1) #bruce 050727 changed "pressed()" to "toggled(bool)"
        change_connect(self.w.depositAtomDashboard.bond2Btn,
                       SIGNAL("toggled(bool)"), self.setBond2)
        change_connect(self.w.depositAtomDashboard.bond3Btn,
                       SIGNAL("toggled(bool)"), self.setBond3)
        change_connect(self.w.depositAtomDashboard.bondaBtn,
                       SIGNAL("toggled(bool)"), self.setBonda)
        change_connect(self.w.depositAtomDashboard.bondgBtn,
                       SIGNAL("toggled(bool)"), self.setBondg)
        change_connect(self.w.depositAtomDashboard.buildBtn,
                       SIGNAL("toggled(bool)"), self.setAtom) 
                       # This was missing. Might have been cause of bug 1545. Theory not tested (try in A8).
                       # This is needed to update cursor when buildBtn (Atom Tool) is selected.
                       # See fix_submodes_btngrp() for more info. mark 060327
                       
        change_connect(self.w.depositAtomDashboard.transmuteBtn,
                        SIGNAL("clicked()"),self.transmutePressed)
        
        # Slots for the Water and Highlight checkboxes. mark 060202.    
        change_connect(self.w.depositAtomDashboard.waterCB,
                        SIGNAL("toggled(bool)"),self.setWater)
        change_connect(self.w.depositAtomDashboard.highlightingCB,
                        SIGNAL("toggled(bool)"),self.set_hoverHighlighting)
        change_connect(self.w.depositAtomDashboard.filterCB,
                        SIGNAL("toggled(bool)"),self.set_selection_filter)
        
        # Workaround for Qt bug. See more info in fix_submodes_btngrp() docstring. mark 060301.      
        change_connect(self.w.depositAtomDashboard.submode_btngrp,
                        SIGNAL("released(int)"),self.fix_submodes_btngrp)
                        
        return

    def update_bond_buttons(self): #bruce 050728 (should this be used more widely?); revised 050831
        "make the dashboard one-click-bond-changer state buttons match whatever is stored in self.bondclick_v6"
        self.w.depositAtomDashboard.bond1Btn.setOn( self.bondclick_v6 == V_SINGLE)
        self.w.depositAtomDashboard.bond2Btn.setOn( self.bondclick_v6 == V_DOUBLE)
        self.w.depositAtomDashboard.bond3Btn.setOn( self.bondclick_v6 == V_TRIPLE)
        self.w.depositAtomDashboard.bondaBtn.setOn( self.bondclick_v6 == V_AROMATIC)
        self.w.depositAtomDashboard.bondgBtn.setOn( self.bondclick_v6 == V_GRAPHITE)
        return
    
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
            pass ## print "update_gui returns since self.dont_update_gui" ####@@@@
            # Getting msg after depositing an atom, then selecting a bondpoint and 
            # "Select Hotspot and Copy" from the GLPane menu.
            # Is it a bug??? Mark 051212.
            # bruce 060412 replies: I don't know; it might be. Perhaps we should do what MMKit does as of today,
            # and defer all UpdateDashboard actions until another event handler (here, or better in basicMode).
            # But for now I'll disable the debug print and we can defer this issue unless it becomes suspected
            # in specific bugs.
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
        # when it set depositState to 'Atoms' or 'Library' (tho I don't think that other code really
        # needs to do that). This is safe even if called "too early". But if it's
        # already set, don't change it, so callers of UpdateDashboard can set it
        # to the value they want, even if that value is not yet in the spinbox
        # (see e.g. setHotSpot_mainPart).
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
        # one equal to self.pastable (when self.depositState == 'Clipboard' and this is current mode)
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
        
        # This is needed since changing the spinbox item sets self.w.depositState.
        self.w.update_depositState_buttons()
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
            self.MMKit.update_clipboard_items() # Fixes bugs 1569, 1570, 1572 and 1573. mark 060306.
                # Note and bugfix, bruce 060412: doing this now was also causing traceback bugs 1726, 1629,
                # and the traceback part of bug 1677, and some related (perhaps unreported) bugs.
                # The problem was that this is called during pasteBond's addmol (due to its addchild), before it's finished,
                # at a time when the .part structure is invalid (since the added mol's .part has not yet been set).
                # To fix bugs 1726, 1629 and mitigate bug 1677, I revised the interface to MMKit.update_clipboard_items
                # (in the manner which was originally recommented in call_after_next_changed_members's docstring) 
                # so that it only sets a flag and updates (triggering an MMKit repaint event), deferring all UI effects to
                # the next MMKit event.
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

    def StateDone(self):
        return None
    # we never have undone state, but we have to implement this method,
    # since our haveNontrivialState can return True

    def StateCancel(self):
        # to do this correctly, we'd need to remove the atoms we added
        # to the assembly; we don't attempt that yet [bruce 040923,
        # verified with Josh]
        change_desc = "your changes are"
        msg = "%s Cancel not implemented -- %s still there.\n\
        You can only leave this mode via Done." % \
              ( self.msg_modename, change_desc )
        self.warning( msg, bother_user_with_dialog = 1)
        return True # refuse the Cancel
    
    # restore_gui handles all the GUI display when leaving this mode
    # [mark 041004]
    def restore_gui(self):
        # disconnect signals which were connected in init_gui [bruce 050728]
        self.connect_or_disconnect_signals(False)
        
        self.w.depositAtomDashboard.hide() # Stow away dashboard
        
        self.MMKit.close() # Close the MMKit when leaving Build mode.

# Now uses superclass method selectAtomsMode.restore_patches(). mark 060207.
#    def restore_patches(self):
#        self.o.setDisplay(self.saveDisp) #bruce 041129; see notes for bug 133
#        self.o.selatom = None

    def clear(self):
        self.new = None

    # event methods
    
    def keyPress(self,key):
        # bruce comment 041220:
        # doesn't call basicMode method, so Delete key is not active. Good??
        # bruce 050128: no, not good. And it shows selection anyway... so do it below.
        for sym, code, num in elemKeyTab: # Set the atom type in the MMKit and combobox.
            if key == code:
                self.w.setElement(num) ###@@@ does this update our own spinbox too??
        
        ## Huaicai 8/5/05 Add accelerate key for bond hybrid comboBox
        #if self.w.hybridComboBox.isVisible():
        if 1: # Kluge fix for bug 1553.  Will be fixed properly in A8 with MMKit cleanup. Mark 060304.
            acKeys = [Qt.Key_3, Qt.Key_2, Qt.Key_1, Qt.Key_4]
            num = self.w.hybridComboBox.count()
            if key in acKeys[:num]:
                hybridId = acKeys.index(key)
                self.w.hybridComboBox.setCurrentItem(hybridId)
                self.w.hybridComboBox.emit(SIGNAL("activated"), (hybridId,))
                
        # Pressing Escape does the following:
        # 1. If a Bond Tool or the Atom Selection Filter is enabled, pressing Escape will activate the Atom Tool
        # and disable the Atom Selection Filter. The current selection remains unchanged, however.
        # 2. If the Atom Tool is enabed and the Atom Selection Filter is disabled, Escape will clear the 
        # current selection.
        # Fixes bug (nfr) 1770. mark 060402
        if key == Qt.Key_Escape:
            if not self.w.depositAtomDashboard.buildBtn.isOn() or self.w.selection_filter_enabled:
                # Uncheck (disable) the Atom Selection Filter and activate the Atom Tool.
                self.w.depositAtomDashboard.filterCB.setChecked(0) # generates signal.
                self.w.depositAtomDashboard.buildBtn.setOn(1)
                return
        
        selectAtomsMode.keyPress(self,key) # bruce 050128
        
        return
        
    def update_cursor_for_no_MB_selection_filter_disabled(self):
        '''Update the cursor for 'Build' mode (when no mouse button is pressed).
        '''
        cursor_id = self.w.depositAtomDashboard.submode_btngrp.selectedId()
        
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
        # BTW this is now the only remaining call of findpick [still true 060316].
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
        if at: pnt = at.posn()
        else: pnt = - self.o.pov
        k = (dot(self.o.lineOfSight,  pnt - p1) /
             dot(self.o.lineOfSight, p2 - p1))

        return p1+k*(p2-p1) # always return a point on the line from p1 to p2

    def OLD_OBS_update_selatom(self, event, singOnly = False, msg_about_click = False): # no longer used as of 050610
        # bruce 041206 optimized redisplay (for some graphics chips)
        # by keeping selatom out of its chunk's display list,
        # so no changeapp is needed when selatom changes.
        # bruce 041213 fixed several bugs using new findAtomUnderMouse,
        # including an unreported one for atoms right at the eyeball position.
        
        oldselatom = self.o.selatom
        # warning: don't change self.o.selatom yet, since findAtomUnderMouse uses
        # its current value to support hysteresis for its selection radius.
        atm = self.o.assy.findAtomUnderMouse(event, water_cutoff = True, singlet_ok = True) # note, this is not the only call!
        assert oldselatom is self.o.selatom
        if atm is not None and (atm.element is Singlet or not singOnly):
            pass # we'll use this atm as the new selatom
        else:
            atm = None
        self.o.selatom = atm
        if msg_about_click: # [always do this, since many things can change what it should say]
            # come up with a status bar message about what we would paste now.
            # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable]
            msg = self.describe_leftDown_action( self.o.selatom)
            env.history.statusbar_msg( msg)
        if self.o.selatom is not oldselatom:
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
            cmd = "%s onto bondpoint at %s" % (what, self.posn_str(selatom))
            #bruce 050416 also indicate hotspot if we're on clipboard
            # (and if this hotspot will be drawn in special color, since explaining that
            #  special color is the main point of this statusbar-text addendum)
            if selatom is selatom.molecule.hotspot and not self.viewing_main_part():
                # also only if chunk at toplevel in clipboard (ie pastable)
                # (this is badly in need of cleanup, since both here and chunk.draw
                #  should not hardcode the cond for that, they should all ask the same method here)
                if selatom.molecule in self.o.assy.shelf.members: 
                    cmd += " (hotspot)"
        elif selatom is not None:
            cmd = "click to drag %r" % selatom
            cmd += " (%s)" % selatom.atomtype.fullname_for_msg() # nested parens ###e improve    
        else:
            cmd = "%s at \"water surface\"" % what
            #e cmd += " at position ..."
        return cmd
        
    def describe_paste_action(self, onto_open_bond): # bruce 050124; added onto_open_bond flag, 050127
        "return a description of what leftDown would paste or deposit (and how user could do that), if done now"
        #e should be split into "determine what to paste" and "describe it"
        # so the code for "determine it" can be shared with leftDown
        # rather than copied from it as now
        if self.w.depositState == 'Clipboard':
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
            atype = self.pastable_atomtype()
            return "click to deposit %s" % atype.fullname_for_msg()

    def pastable_element(self):
        return PeriodicTable.getElement(self.w.Element)

    _pastable_atomtype = None
    def set_pastable_atomtype(self, name):
        current_element = self.pastable_element()
        self._pastable_atomtype = current_element.find_atomtype(name)
            # store entire atomtype object; only used if element remains correct (not an error if it doesn't)
        # update comboboxes - the element one must be up to date (it controls self.w.Element which our subr above reads)
        update_hybridComboBox(self.w, self._pastable_atomtype.name )
            # update of its item list is probably not needed, but this also sets the current one properly
        return

    def pastable_atomtype(self): #bruce 050511 ###@@@ use more?
        "return the current pastable atomtype"
        #e we might extend this to remember a current atomtype per element... not sure if useful
        current_element = self.pastable_element()
        if len(current_element.atomtypes) > 1: #bruce 050606
            try: 
                hybname = self.w.hybridComboBox.currentText()
                atype = current_element.find_atomtype(hybname)
                if atype is not None:
                    self._pastable_atomtype = atype
            except:
                print_compact_traceback("exception (ignored): ") # error, but continue
            pass
        if self._pastable_atomtype is not None and self._pastable_atomtype.element is current_element:
            return self._pastable_atomtype
        self._pastable_atomtype = current_element.atomtypes[0]
        return self._pastable_atomtype

    def ensure_visible(self, stuff, status):
        """if any chunk in stuff (#doc format) is not visible now, make it visible by changing its
        display mode, and append a warning about this to the given status message,
        which is returned whether or not it's modified.
           Suggested revision: if some chunks in a library part are explicitly invisible and some are visible, I suspect this
        behavior is wrong and it might be better to require only that some of them are visible,
        and/or to only do this when overall display mode was visible. [bruce 051227]
           Suggested revision: maybe the default display mode for deposited stuff should also be user-settable. [bruce 051227]
        """
        # By bruce 041207, to fix bug 229 part B (as called in comment #2),
        # by making each deposited chunk visible if it otherwise would not be.
        # Note that the chunk is now (usually?) the entire newly deposited thing,
        # but after future planned changes to the code, it might instead be a
        # preexisting chunk which was extended. Either way, we'll make the
        # entire chunk visible if it's not.
        #bruce 051227 revising this to handle more general deposited_stuff, for deposited library parts.
        n = self.ensure_visible_0( stuff)
        if n:
            status += " (warning: gave it Tubes display mode)"
            #k is "it" correct even for library parts? even when not all deposited chunks were changed?
        return status

    def ensure_visible_0(self, stuff): #bruce 051227 split out and generalized
        "[private recursive worker method for ensure_visible; returns number of things whose display mode was modified]"
        if not stuff:
            return 0 #k can this happen? I think so, since old code could handle it.
        from chunk import Chunk #k might not be needed
        if isinstance(stuff, Chunk):
            chunk = stuff
            if chunk.get_dispdef(self.o) == diINVISIBLE:
                chunk.setDisplay(diTUBES) # Build mode's own default display mode
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
            ##e not sure how to handle this or whether we need to [bruce 051227]; leave it out and await bug report?
            if platform.atom_debug:
                print "atom_debug: ignoring object of unhandled type (Jig?) in ensure_visible_0", stuff
            return 0
        pass
    
    def __createBond(self, s1, a1, s2, a2):
        '''Create bond between atom <a1> and atom <a2>, <s1> and <s2> are their singlets. No rotation/movement involved. Based on
           a method 'actually_bond()' in bonds.py--[Huaicai 8/25/05] '''
        
        try: # use old code until new code works and unless new code is needed; CHANGE THIS SOON #####@@@@@
            v1, v2 = s1.singlet_v6(), s2.singlet_v6() # new code available
            assert v1 != V_SINGLE or v2 != V_SINGLE # new code needed
        except:
            # old code can be used for now
            s1.kill()
            s2.kill()
            bond_atoms(a1,a2)
            return
        
        vnew = min(v1,v2)
        bond = bond_atoms(a1,a2,vnew,s1,s2) # tell it the singlets to replace or reduce; let this do everything now, incl updates
        return
    
    def _depositLibraryPart(self, newPart, hotspotAtom, atom_or_pos): # probably by Huaicai; revised by bruce 051227, 060627
        '''This method serves as an overloaded method, <atom_or_pos> is 
           the Singlet atom or the empty position that the new part <newPart> [an assy?] will be attached to or placed at.
           [If <atom_or_pos> is a singlet, <hotspotAtom> should be an atom in some chunk in <newPart>.]
           Currently, it doesn't consider group or jigs in the <newPart>. Not so sure if my attempt to copy a part into
           another assembly is all right. [It wasn't, so bruce 051227 revised it.]
           Copies all molecules in the <newPart>, change their assy attribute to current assembly, move them into <pos>.
           [bruce 051227 new feature:] return a list of new nodes created, and a message for history (currently almost a stub).
           [not sure if subrs ever print history messages... if they do we'd want to return those instead.]
        '''
        attach2Bond = False
        stuff = [] # list of deposited nodes [bruce 051227 new feature]
        
        if isinstance(atom_or_pos, Atom):
            attch2Singlet = atom_or_pos
            if hotspotAtom and hotspotAtom.is_singlet() and attch2Singlet .is_singlet():
                newMol = hotspotAtom.molecule.copy(None)
                newMol.setAssy(self.o.assy) #bruce 051227 revised this
                hs = newMol.hotspot
                ha = hs.singlet_neighbor() # hotspot neighbor atom
                attch2Atom = attch2Singlet.singlet_neighbor() # attach to atom

                rotCenter = newMol.center
                rotOffset = Q(ha.posn()-hs.posn(), attch2Singlet.posn()-attch2Atom.posn())
                newMol.rot(rotOffset)
                
                moveOffset = attch2Singlet.posn() - hs.posn()
                newMol.move(moveOffset)
                
                self.__createBond(hs, ha, attch2Singlet, attch2Atom)
                
                self.o.assy.addmol(newMol)
                stuff.append(newMol)

                #e if there are other chunks in <newPart>, they are apparently copied below. [bruce 060627 comment]
                
            else: ## something is wrong, do nothing
                return stuff, "internal error"
            attach2Bond = True
        else:
            placedPos = atom_or_pos
            if hotspotAtom:
                hotspotAtomPos = hotspotAtom.posn()
                moveOffset = placedPos - hotspotAtomPos
            else:
                if newPart.molecules:
                    moveOffset = placedPos - newPart.molecules[0].center #e not the best choice of center [bruce 060627 comment]
        
        if attach2Bond: # Connect part to a bondpoint of an existing chunk
            for m in newPart.molecules:
              if not m is hotspotAtom.molecule: 
                newMol = m.copy(None)
                newMol.setAssy(self.o.assy) #bruce 051227 revised this
                
                ## Get each of all other chunks' center movement for the rotation around 'rotCenter'
                coff = rotOffset.rot(newMol.center - rotCenter)
                coff = rotCenter - newMol.center + coff 
                
                # The order of the following 2 statements doesn't matter
                newMol.rot(rotOffset)
                newMol.move(moveOffset + coff)
                
                self.o.assy.addmol(newMol)
                stuff.append(newMol)
        else: # Behaves like dropping a part anywhere you specify, independent of existing chunks.
            nodes = newPart.molecules
            #bruce 060627 new code: fix bug 2028 (non-hotspot case only) about interchunk bonds being broken
            import ops_copy as hmm
            import debug
            debug.reload_once_per_event(hmm) # only reloads if atom_debug is set, and tolerates failure (I think)
            from ops_copy import copied_nodes_for_DND
            newnodes = copied_nodes_for_DND(nodes)
            if newnodes is None:
                print "bug: newnodes should not be None; nodes was %r (saved in debug._bugnodes)" % (nodes,)
                debug._bugnodes = nodes
                newnodes = [] # kluge
            for newMol in newnodes:
                # some of the following probably only work for Chunks,
                # though coding them for other nodes would not be hard
                newMol.setAssy(self.o.assy)
                newMol.move(moveOffset)
                self.o.assy.addmol(newMol)
                stuff.append(newMol)
##            # old code, breaks interchunk bonds since it copies chunks one at a time (bug 2028)
##            for m in nodes:
##                newMol = m.copy(None)
##                newMol.setAssy(self.o.assy) #bruce 051227 revised this
##                
##                newMol.move(moveOffset)
##                
##                self.o.assy.addmol(newMol)
##                stuff.append(newMol)
##            pass
        self.o.assy.update_parts() #bruce 051227 see if this fixes the atom_debug exception in checkparts
        return stuff, "deposited library part" ####@@@@ should revise this message (stub is by bruce 051227)

# == LMB event handling methods ====================================
        
    def leftDouble(self, event): # mark 060126.
        '''Double click event handler for the left mouse button. 
        '''
        
        self.ignore_next_leftUp_event = True # Fixes bug 1467. mark 060307.
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            if self.o.modkeys != 'Shift+Control': # Fixes bug 1503.  mark 060224.
                deposited_obj = self.deposit_from_MMKit(self.getCoords(event)) # does win_update().
                if deposited_obj:
                    self.set_cmdname('Deposit ' + deposited_obj)
            return
            
        selectAtomsMode.leftDouble(self, event)
        
        return

# == end of LMB event handler methods

    def MMKit_clipboard_part(self): #bruce 060412; implem is somewhat of a guess, based on the code of self.deposit_from_MMKit
        "If the MMKit is currently set to a clipboard item, return that item's Part, else return None."
        if self.w.depositState != 'Clipboard':
            return None
        if not self.pastable:
            return None
        return self.pastable.part
    
    def transdeposit_from_MMKit(self, singlet):
        '''Trans-deposit the current object in the MMKit on all singlets reachable through 
        any sequence of bonds to the singlet <singlet>.
        '''

        if not singlet.is_singlet(): 
            return

        # bruce 060412: fix bug 1677 (though this fix's modularity should be improved;
        #  perhaps it would be better to detect this error in deposit_from_MMKit).
        # See also other comments dated today about separate fixes of some parts of that bug.
        mmkit_part = self.MMKit_clipboard_part() # a Part or None
        if mmkit_part and self.o.assy.part is mmkit_part:
            env.history.message(redmsg("Can't transdeposit the MMKit's current clipboard item onto itself."))
            return
        
        singlet_list = self.o.assy.getConnectedSinglets([singlet])
        
        modkeys = self.o.modkeys # save the modkeys state
        if self.o.modkeys is None and env.prefs[buildModeSelectAtomsOfDepositedObjEnabled_prefs_key]:
            # Needed when 'Select Atoms of Deposited Object' pref is enabled. mark 060314.
            self.o.modkeys = 'Shift'    
            self.o.assy.unpickatoms()
        
        self.transdepositing = True
        nobjs = 0
        ntried = 0 
        msg_deposited_obj = None
        for s in singlet_list: # singlet_list built in singletSetup() [not true; is that a bug?? bruce 060412 question]
            if not s.killed(): # takes care of self.obj_doubleclicked, too.
                deposited_obj = self.deposit_from_MMKit(s)
                ntried += 1
                if deposited_obj is not None:
                    #bruce 060412 -- fix part of bug 1677 -- wrong histmsg 'Nothing Transdeposited' and lack of mt_update
                    msg_deposited_obj = deposited_obj # I think these will all be the same, so we just use the last one
                    nobjs += 1
        self.transdepositing = False
        self.o.modkeys = modkeys # restore the modkeys state to real state.

        del deposited_obj
        
        if msg_deposited_obj is None: 
            # Let user know nothing was trandeposited. Fixes bug 1678. mark 060314.
            # (This was incorrect in bug 1677 since it assumed all deposited_obj return values were the same,
            #  but in that bug (as one of several problems in it) the first retval was not None but the last one was,
            #  so this caused a wrong message and a failure to update the MT. Fixed those parts of bug 1677
            #  by introducing msg_deposited_obj and using that here instead of deposited_obj. Fixed other parts of it
            #  in MMKit and elsewhere in this method. [bruce 060412])
            env.history.message('Nothing Transdeposited')
            return
            
        self.set_cmdname('Transdeposit ' + msg_deposited_obj)
        msg_deposited_obj += '(s)'
        
        info = fix_plurals( "%d %s deposited." % (nobjs, msg_deposited_obj) )
        if ntried > nobjs:
            # Note 1: this will be true in bug 1677 (until it's entirely fixed) [bruce 060412]
            # Note 2: this code was tested and worked, before I fully fixed bug 1677;
            # now that bug is fully fixed above (in the same commit as this code),
            # so this code is not known to ever run,
            # but I'll leave it in in case it mitigates any undiscovered bugs.
            info += " (%d not deposited due to a bug)" % (ntried - nobjs)
            info = orangemsg(info)
        env.history.message(info)
        self.w.win_update()

    def bondLeftUp(self, b, event): # was bondClicked(). mark 060220.
        '''Bond <b> was clicked, so select or unselect its atoms or delete bond <b> 
        based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s two atoms.
        - If Shift is pressed, pick <b>'s two atoms, adding them to the current selection.
        - If Ctrl is pressed,  unpick <b>'s two atoms, removing them from the current selection.
        - If Shift+Control (Delete) is pressed, delete bond <b>.
        <event> is a LMB release event.
        '''

        if self.o.modkeys is None:
            if not self.w.depositAtomDashboard.buildBtn.isOn():
            #&if not self.w.depositAtomDashboard.buildBtn.isOn() and not self.w.depositAtomDashboard.atomBtn.isOn():
            #& Reinstate in A8.  mark 060301.
                self.bond_change_type(b)
                self.o.gl_update()
                return
        
        selectAtomsMode.bondLeftUp(self, b, event)
            
    def bond_change_type(self, b): #bruce 050727
        '''Change bondtype of bond <b> to new bondtype determined by the dashboard (if allowed).
        '''
        # renamed from clicked_on_bond() mark 060204.
        v6 = self.bondclick_v6
        if v6 is not None:
            btype = btype_from_v6( v6)
            from bond_utils import apply_btype_to_bond
            apply_btype_to_bond( btype, b)
            self.set_cmdname('Change Bond')
                # checks whether btype is ok, and if so, new; emits history message; does [#e or should do] needed invals/updates
            ###k not sure if that subr does gl_update when needed... this method does it, but not sure how #######@@@@@@@
        return

# == Deposit methods

    def pickit(self):
        '''Determines if the a deposited object (atom, clipboard node or library part) should have 
        its atoms automatically picked. Returns True or False based on the current modkey state.
        If modkey is None (no modkey is pressed), it will unpick all currently picked atoms.
        '''
        if self.o.modkeys is None:
            self.o.assy.unpickatoms()
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
        
    def deposit_from_MMKit(self, atom_or_pos): #mark circa 051200; revised by bruce 051227
        '''Deposit a new object based on the current selection in the MMKit/dashboard, 
        which is either an atom, a chunk on the clipboard, or a part from the library.
        If 'atom_or_pos' is a singlet, then it will bond the object to that singlet if it can.
        If 'atom_or_pos' is a position, then it will deposit the object at that coordinate.
        Return string <deposited_obj>, where:
            'Atoms' - an atom from the Atoms page was deposited.
            'Chunk' - a chunk from the Clipboard page was deposited.
            'Part' - a library part from the Library page was deposited.
        '''
        
        deposited_obj = None 
            #& deposited_obj is probably misnamed, since it is a string, not an object.  
            #& Would be nice if this could be an object. Problem is that clipboard and library
            #& both deposit chunks. mark 060314.
        
        if self.o.modkeys is None: # no Shift or Ctrl modifier key.
            self.o.assy.unpickatoms() # Clear selection.
        
        if self.w.depositState == 'Atoms':
            deposited_stuff, status = self.deposit_from_Atoms_page(atom_or_pos) # deposited_stuff is a chunk
            deposited_obj = 'Atom'
            
        elif self.w.depositState == 'Clipboard':
            deposited_stuff, status = self.deposit_from_Clipboard_page(atom_or_pos) # deposited_stuff is a chunk
            deposited_obj = 'Chunk'
                
        elif self.w.depositState == 'Library':
            #bruce 051227 revised this case and its subrs as part of fix of reopened bug 229;
            # deposited_stuff might be a chunk, node, list, etc.
            # Not sure if subrs still print redundant history messages besides the one
            # newly returned here (status).
            deposited_stuff, status = self.deposit_from_Library_page(atom_or_pos)
            deposited_obj = 'Part'
            if deposited_stuff and self.pickit():
                for d in deposited_stuff[:]:
                    d.pickatoms() # Fixes bug 1510. mark 060301.
            
        else:
            print_compact_stack('Invalid depositState = "' + str(self.w.depositState) + '" ')
            return
            
        self.o.selatom = None ##k could this be moved earlier, or does one of those submethods use it? [bruce 051227 question]
            
        # now fix bug 229 part B (as called in comment #2),
        # by making this new chunk (or perhaps multiple chunks, in deposited_stuff) visible if it otherwise would not be.
        # [bruce 051227 is extending this fix to depositing Library parts, whose initial implementation reinstated the bug.
        #  Note, Mark says the following comment is in 2 places but I can't find the other place, so not removing it yet.]
##        # We now have bug 229 again when we deposit a library part while in "invisible" display mode.
##        # Ninad is reopening bug 229 and assigning it to me.  This comment is in 2 places. Mark 051214.
##        if not library_part_deposited:  ##Added the condition [Huaicai 8/26/05] [bruce 051227 removed it, added a different one]

        if self.transdepositing:
            if not deposited_stuff:
                # Nothing was transdeposited.  Needed to fix bug 1678. mark 060314.
                return None
            return deposited_obj
        
        if deposited_stuff:
            self.w.win_update() 
                #& should we differentiate b/w win_update (when deposited_stuff is a new chunk added) vs. 
                #& gl_update (when deposited_stuff is added to existing chunk).  Discuss with Bruce. mark 060210.
            status = self.ensure_visible( deposited_stuff, status) #bruce 041207
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) # nothing deposited
        
        return deposited_obj
            
    def deposit_from_Library_page(self, atom_or_pos): #mark circa 051200; retval revised by bruce 051227 re bug 229
        '''Deposit a copy of the selected part from the MMKit Library page.
        If 'atom_or_pos' is a singlet, try bonding the part to the singlet by its hotspot.
        Otherwise, deposit the part at the position 'atom_or_pos'.
        Return (deposited_stuff, status_msg_text), whether or not deposition was successful.
        ''' 
        newPart, hotSpot = self.MMKit.getPastablePart()
        
        if not newPart: # Make sure a part is selected in the MMKit Library.
            # Whenever the MMKit is closed with the 'Library' page open,
            # MMKit.closeEvent() will change the current page to 'Atoms'.
            # This ensures that this condition never happens if the MMKit is closed.
            # Mark 051213.
            ## env.history.message(orangemsg("No library part has been selected to paste.")) [bruce 051227 zapped this, caller does it]
            return False, "No library part has been selected to paste." # nothing deposited
        
        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if hotSpot : # bond the part to the singlet.
                    return self._depositLibraryPart(newPart, hotSpot, a) #bruce 051227 revised retval
                
                else: # part doesn't have hotspot.
                    #if newPart.has_singlets(): # need a method like this so we can provide more descriptive msgs.
                    #    msg = "To bond this part, you must pick a hotspot by left-clicking on a bondpoint  " \
                    #            "of the library part in the Modeling Kit's 3D thumbview."
                    #else:
                    #    msg = "The library part cannot be bonded because it has no bondpoints."
                    msg = "The library part cannot be bonded because either it has no bondpoints"\
                            " or its hotspot hasn't been specified in the Modeling Kit's 3D thumbview"
                    ## env.history.message(orangemsg(msg)) [bruce 051227 zapped this, caller does it]
                    return False, msg # nothing deposited
            
            else: # atom_or_pos was an atom, but wasn't a singlet.  Do nothing. [bruce 051227 added debug message in retval]
                return False, "internal error: can't deposit onto a real atom %r" % a
        
        else:
            # deposit into empty space at the cursor position
            #bruce 051227 note: looks like subr repeats these conds; are they needed here?
            return self._depositLibraryPart(newPart, hotSpot, atom_or_pos) #bruce 051227 revised retval
        assert 0, "notreached"
        pass

    def deposit_from_Clipboard_page(self, atom_or_pos):
        '''Deposits a copy of the selected object (chunk) from the MMKit Clipboard page, or
        the Clipboard (paste) combobox on the dashboard, which are the same object.
        If 'atom_or_pos' is a singlet, try bonding the object to the singlet by its hotspot.
        Otherwise, deposit the object at the position 'atom_or_pos'.
        Returns (chunk, status)
        '''
        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet:
                if self.pastable: # bond clipboard object to the singlet
                    a0 = a.singlet_neighbor() # do this before <a> (the singlet) is killed
                    chunk, desc = self.pasteBond(a)
                    if chunk:
                        ## status = "replaced bondpoint on %r with %s (%s)" % (a0, chunk.name, desc)
                        status = "replaced bondpoint on %r with %s" % (a0, desc) # is this better? [bruce 050121]
                    else:
                        status = desc
                        # bruce 041123 added status message, to fix bug 163,
                        # and added the rest of them to describe what we do
                        # (or why we do nothing)
                else:
                    # Nothing selected from the Clipboard to paste, so do nothing
                    status = "nothing selected to paste" #k correct??
                    chunk = None #bruce 041207
        
        else:
            if self.pastable: # deposit into empty space at the cursor position
                chunk, desc = self.pasteFree(atom_or_pos)
                status = "pasted %s (%s) at %s" % (chunk.name, desc, self.posn_str(atom_or_pos))
            else:
                # Nothing selected from the Clipboard to paste, so do nothing
                status = "nothing selected to paste" #k correct??
                chunk = None #bruce 041207
                
        return chunk, status
        

    def deposit_from_Atoms_page(self, atom_or_pos):
        '''Deposits an atom of the selected atom type from the MMKit Atoms page, or
        the Clipboard (atom and hybridtype) comboboxes on the dashboard, which are the same atom.
        If 'atom_or_pos' is a singlet, bond the atom to the singlet.
        Otherwise, set up the atom at position 'atom_or_pos' to be dragged around.
        Returns (chunk, status)
        '''
        atype = self.pastable_atomtype() # Type of atom to deposit
        
        if isinstance(atom_or_pos, Atom):
            a = atom_or_pos
            if a.element is Singlet: # bond an atom of type atype to the singlet
                a0 = a.singlet_neighbor() # do this before <a> (the singlet) is killed!
                # (revised by bruce 050511)
                # if 1: # during devel, at least
                if platform.atom_debug: # Need this for A6 package builder to work.  Mark 050811.
                    import build_utils
                    reload(build_utils)
                from build_utils import AtomTypeDepositionTool
                deptool = AtomTypeDepositionTool( atype)
                autobond = self.w.depositAtomDashboard.autobondCB.isChecked() #bruce 050831
                a1, desc = deptool.attach_to(a, autobond = autobond)
                        #e this might need to take over the generation of the following status msg...
                ## a1, desc = self.attach(el, a)
                if a1 is not None:
                    if self.pickit(): a1.pick()
                    #self.o.gl_update() #bruce 050510 moved this here from inside what's now deptool
                        # The only callers, deposit_from_MMKit() and transdeposit_from_MMKit()
                        # are responsible for calling gl_update()/win_update(). mark 060314.
                    status = "replaced bondpoint on %r with new atom %s at %s" % (a0, desc, self.posn_str(a1))
                    chunk = a1.molecule #bruce 041207
                else:
                    status = desc
                    chunk = None #bruce 041207
                del a1, desc

        else: # Deposit atom at the cursor position and prep it for dragging
                cursorPos = atom_or_pos
                a = self.o.selatom = oneUnbonded(atype.element, self.o.assy, cursorPos, atomtype = atype)
                self.objectSetup(a)
                self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
                if self.pickit(): self.o.selatom.pick()
                status = "made new atom %r at %s" % (self.o.selatom, self.posn_str(self.o.selatom) )
                chunk = self.o.selatom.molecule #bruce 041207
        
        return chunk, status


    def chunkSetup_OBS(self, a): #&& Not used.  Marked for removal.  mark 060214.
        '''Setup dragging of a chunk by one of its atoms, atom <a>.
        If the chunk is not bonded to any chunks, drag it around loosely, which means
        the chunk follows atom <a> around.
        If the chunk is bonded to 1 other chunk, the chunk will pivot around the
        bond to the neighoring chunk.
        If the chunk is bonded to 2 chunks, the chunk will pivot around an axis
        defined by the two bonds of the neighboring chunks.
        If the chunk is bonded to 3 or more chunks, drag it rigidly, which means
        translate the chunk in the plane of the screen.
        '''
        self.objectSetup(a)
        
        if a.realNeighbors(): # probably part of larger molecule
                    ###e should this be nonbaggageNeighbors? Need to understand the comments below. [bruce 051209] ###@@@
            e=a.molecule.externs # externs are number of bonds to other chunks.
            
            if len(e)==0: # no bonds to other chunks, so just drag it around "loosely" (follow <a>)
                self.pivot = None
                self.pivax = True #k might have bugs if realNeighbors in other mols??
                #bruce 041130 tried using this case for 1-atom mol as well,
                # but it made singlet highlighting wrong (due to pivax??).
                # (Could that mean there's some sort of basepos-updating bug
                # in mol.pivot? ###@@@)
                # I tried to reproduce the bug described above without success.  Sure it's still there?
                # Mark 051213.
                
            elif len(e)==1: # bonded to 1 chunk; pivot around the single bond
                self.pivot = e[0].center
                # warning: Bond.center is only in abs coords since
                # this is an external bond [bruce 050516 comment]
                self.pivax = None
                
            elif len(e)==2: # bonded to 2 other chunks; pivot around the 2 bonds
                self.pivot = e[0].center
                self.pivax = norm(e[1].center-e[0].center)
                
            else: # more than 2 other chunks, drag it "rigidly" (translate the chunk)
                self.pivot = None
                self.pivax = None
        
        # Keep the comments below for now.  From Bruce's comments, it may be needed later.  Mark 051213.
        
        ##elif len(a.molecule.atoms) == 1 + len(a.bonds):
                #bruce 041130 added this case to let plain left drag work to
                # drag a 1-real-atom mol, not only a larger mol as before; the
                # docstring makes me think this was the original intention, and
                # the many "invalid bug reports" whose authors assume this will
                # work imply this feature is desired and intuitively expected.
            ##self.dragmol = a.molecule # self.dragmol decommissioned on 051213.  Mark
            # fall thru
        ##else:
                #bruce 041130 added this case too:
                # no real neighbors, but more than just the singlets in the mol
                # (weird but possible)... for now, just do the same, though if
                # there are 1 or 2 externs it might be better to do pivoting. #e
            ##self.dragmol = a.molecule # self.dragmol decommissioned on 051213.  Mark
            # fall thru
            
    def chunkDrag_OBS(self, a, event): # not used.  Marked for removal. mark 060214.
        """Drag a chunk around by atom <a>. <event> is a drag event.
        """
        m = a.molecule
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
        
#== Singlet helper methods

    def singletLeftDown(self, s, event):
        if self.o.modkeys == 'Shift+Control':
            self.cursor_over_when_LMB_pressed = 'Empty Space'
            self.select_2d_region(event)
        else:
            self.cursor_over_when_LMB_pressed = 'Singlet'
            self.singletSetup(s)

    def singletSetup(self, a):
        '''Setup for a click, double-click or drag event for singlet <a>.
        '''
        self.objectSetup(a)
        self.only_highlight_singlets = True
        
        self.singlet_list = self.o.assy.getConnectedSinglets([a])
            # get list of all singlets that we can reach from any sequence of bonds to <a>.
            # used in doubleLeft() if the user clicks on 
        
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


    def singletDrag(self, a, event):
        """Drag a singlet. <event> is a drag event.
        """
        if a.element is not Singlet: return
        
        apos0 = a.posn()

        px = self.dragto_with_offset(a.posn(), event, self.drag_offset )
            #bruce 060316 attempt to fix bug 1474 analogue; untested and incomplete since nothing is setting drag_offset
            # when this is called (except to its default value V(0,0,0))! ###@@@
        
        if self.pivax: # continue pivoting around an axis
            quat = twistor(self.pivax, a.posn()-self.pivot, px-self.pivot)
            for at in [a]+self.baggage:
                at.setposn(quat.rot(at.posn()-self.pivot) + self.pivot)
        
        elif self.pivot: # continue pivoting around a point
            quat = Q(a.posn()-self.pivot, px-self.pivot)
            for at in [a]+self.baggage:
                at.setposn(quat.rot(at.posn()-self.pivot) + self.pivot)
        
        #bruce 051209 brought update_selatom inside this conditional, to fix an old bug; 
        # need to reset it in other case???###@@@
        self.update_selatom(event, singOnly = True) # indicate singlets we might bond to
        #bruce 041130 asks: is it correct to do that when a is real? 051209: no. now i don't, that's the bugfix.
        # see warnings about update_selatom's delayed effect, in its docstring or in leftDown. [bruce 050705 comment]
        self.line = [a.posn(), px] # This updates the endpoints of the white rubberband line.
        
        apos1 = a.posn()
        if apos1 - apos0:
            msg = "pulling bondpoint %r to %s" % (a, self.posn_str(a))
            this_drag_id = (self.current_obj_start, self.__class__.leftDrag)
            env.history.message(msg, transient_id = this_drag_id)
            
        self.o.gl_update()
        
    def singletLeftUp(self, s1, event):
        '''Finish operation on singlet <s1> based on where the cursor is when the LMB was released:
        - If the cursor is still on <s1>, deposit an object from the MMKit on it
        - If the cursor is over a different singlet, bond <s1> to it.
        - If the cursor is over empty space, do nothing.
        <event> is a LMB release event.
        '''
        if not s1.is_singlet(): return
        
        self.line = None # required to erase white rubberband line on next gl_update.
        
        s2 = self.get_singlet_under_cursor(event)

        if s2:
            if s2 is s1: # If the same singlet is highlighted...
                # ...deposit an object (atom, chunk or library part) from MMKit on the singlet <s1>.
                if self.mouse_within_stickiness_limit(event, DRAG_STICKINESS_LIMIT): # Fixes bug 1448. mark 060301.
                    deposited_obj = self.deposit_from_MMKit(s1)
                        # does its own win_update().
                    if deposited_obj:
                        self.set_cmdname('Deposit ' + deposited_obj)
            else: # A different singlet is highlighted...
                # ... so bond the highlighted singlet <s2> to the first singlet <s1>
                self.bond_singlets(s1, s2)
                self.set_cmdname('Create Bond')
                self.o.gl_update()
        else: # cursor on empty space
            self.o.gl_update() # get rid of white rubber band line.
            
        self.only_highlight_singlets = False
        
    def get_singlet_under_cursor(self, event):
        '''If the object under the cursor is a singlet, return it.  If the object under the cursor is a
        real atom with one or more singlets, return one of its singlets. Otherwise, return None.
        '''
        a = self.get_obj_under_cursor(event)
        if isinstance(a, Atom):
            if a.is_singlet():
                return a
            if a.singNeighbors():
                return a.singNeighbors()[0]
        return None

    def bond_singlets(self, s1, s2):
        '''Bond singlets <s1> and <s2> unless they are the same singlet.
        '''
        #bruce 050429: it'd be nice to highlight the involved bonds and atoms, too...
        # incl any existing bond between same atoms. (by overdraw, for speed, or by more lines) ####@@@@ tryit
        #bruce 041119 split this out and added checks to fix bugs #203
        # (for bonding atom to itself) and #121 (atoms already bonded).
        # I fixed 121 by doing nothing to already-bonded atoms, but in
        # the future we might want to make a double bond. #e
        if s1.singlet_neighbor() is s2.singlet_neighbor():
            # this is a bug according to the subroutine [i.e. bond_at_singlets, i later guess], but not to us
            print_error_details = 0
        else:
            # for any other error, let subr print a bug report,
            # since we think we caught them all before calling it
            print_error_details = 1
        flag, status = bond_at_singlets(s1, s2, move = False, \
                         print_error_details = print_error_details, increase_bond_order = True)

        # we ignore flag, which says whether it's ok, warning, or error
        env.history.message("%s: %s" % (self.msg_modename, status))
        return


    ###################################################################
    #==   Cutting and pasting
    ###################################################################
    
    def pasteBond(self, sing):
        """If self.pastable has an unambiguous hotspot,
        paste a copy of self.pastable onto the given singlet;
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
        if self.pickit():
            numol.pickatoms()
            #bruce 060412 worries whether pickatoms is illegal or ineffective (in both pasteBond and pasteFree)
            # given that numol.part is presumably not yet set (until after addmol). But these seem to work
            # (assuming I'm testing them properly), so I'm not changing this. [Why do they work?? ###@@@]
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
        if self.pickit():
            numol.pickatoms()
            #bruce 060412 worries whether pickatoms is illegal or ineffective (in both pasteBond and pasteFree)
            # before addmol... for more info see the same comment in pasteBond.
        self.o.assy.addmol(numol) 
        return numol, "copy of %r" % pastable.name


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
        "called from button presses and spinbox changes"
        self.update_pastable()
        if 1:
            ###@@@ always do this, since old code did this
            # and I didn't yet analyze changing cond to self.pastable
            self.w.depositState = 'Clipboard'
            self.w.update_depositState_buttons()
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
##                ## env.history.message("Ready to paste %r" % self.pastable.name)
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
        "Slot for Atoms Tool dashboard button." 
        self.pastable = None # but spinbox records it... but not if set of pastables is updated! so maybe a bad idea? ##k
        self.update_cursor()
        self.w.depositState = 'Atoms'
        self.w.update_depositState_buttons()
        self.UpdateDashboard() #bruce 050121 added this

    bondclick_v6 = None
    
    def setBond1(self, state):
        "Slot for Bond Tool Single dashboard button."
        self.setBond(V_SINGLE, state, self.w.depositAtomDashboard.bond1Btn )
        
    def setBond2(self, state):
        "Slot for Bond Tool Double dashboard button."
        self.setBond(V_DOUBLE, state, self.w.depositAtomDashboard.bond2Btn )
    
    def setBond3(self, state):
        "Slot for Bond Tool Triple dashboard button."
        self.setBond(V_TRIPLE, state, self.w.depositAtomDashboard.bond3Btn )
        
    def setBonda(self, state):
        "Slot for Bond Tool Aromatic dashboard button."
        self.setBond(V_AROMATIC, state, self.w.depositAtomDashboard.bondaBtn )

    def setBondg(self, state): #mark 050831
        "Slot for Bond Tool Graphitic dashboard button."
        self.setBond(V_GRAPHITE, state, self.w.depositAtomDashboard.bondgBtn )
        
    def setBond(self, v6, state, button = None):
        "#doc; v6 might be None, I guess, though this is not yet used"
        if state:
            if self.bondclick_v6 == v6 and button is not None and v6 is not None:
                # turn it off when clicked twice -- BUG: this never happens, maybe due to QButtonGroup.setExclusive behavior
                self.bondclick_v6 = None
                button.setOn(False) # doesn't work?
            else:
                self.bondclick_v6 = v6
            if self.bondclick_v6:
                name = btype_from_v6(self.bondclick_v6)
                env.history.statusbar_msg("click bonds to make them %s" % name) # name is 'single' etc
            else:
                # this never happens (as explained above)
                env.history.statusbar_msg(" ") # clicking bonds now does nothing
                ## print "turned it off"
        else:
            pass # print "toggled(false) for",btype_from_v6(v6) # happens for the one that was just on, unless you click same one
        self.update_cursor()
        return
    
    def fix_submodes_btngrp(self, button_id):
        '''Makes sure the button that was pressed in the submodes_bg QButtonGroup gets selected.
        This is a workaround for a bug in Qt and fixes bug 1545.  mark 060301.
        '''
        #print "button_id=", button_id
        #print "selectedId=", self.w.depositAtomDashboard.submode_btngrp.selectedId()
        # Uncommenting the print statements above confirms bug 1545 as a Qt bug. 
        # button_id will be the actual id of the button pressed, but the button will not be toggled on. 
        # In this rare case, selectedId will be -1. mark 060301.
        self.w.depositAtomDashboard.submode_btngrp.setButton(button_id)
        
    def setWater(self, on):
        '''Turn water surface on/off.
        if <on> is True, only atoms and bonds above the water surface can be highlighted and selected.
        if <on> is False, all atoms and bonds can be highlighted and selected, and the water surface is not displayed.
        '''
        if on:
            self.water_enabled = True
            msg = "Water surface enabled."
        else:
            self.water_enabled = False
            msg = "Water surface disabled."
        env.history.message(msg)
        self.o.gl_update()
        
    #== Atom Selection Filter helper methods
        
    def set_selection_filter(self, enabled):
        '''Slot for Atom Selection Filter checkbox. Prints history message when selection filter is
        enabled/disabled and updates the cursor.
        '''
        
        if enabled != self.w.selection_filter_enabled:
            if enabled:
                env.history.message("Atom Selection Filter enabled.")
            else:
                env.history.message("Atom Selection Filter disabled.")
        
        self.w.selection_filter_enabled = enabled

        #print "update_selection_filter_list(): self.w.filtered_elements=", self.w.filtered_elements
        
        self.update_selection_filter_list_widget()
        self.w.depositAtomDashboard.filterlistLE.setEnabled(enabled)
        self.update_cursor()
    
    def update_selection_filter_list(self):
        '''Adds/removes the element selected in the MMKit to/from Atom Selection Filter
        based on what modifier key is pressed (if any).
        '''
        eltnum = self.w.Element
        
        if self.o.modkeys is None:
            self.w.filtered_elements = []
            self.w.filtered_elements.append(PeriodicTable.getElement(eltnum))
        if self.o.modkeys == 'Shift':
            if not PeriodicTable.getElement(eltnum) in self.w.filtered_elements[:]:
                self.w.filtered_elements.append(PeriodicTable.getElement(eltnum))
        elif self.o.modkeys == 'Control':
            if PeriodicTable.getElement(eltnum) in self.w.filtered_elements[:]:
                self.w.filtered_elements.remove(PeriodicTable.getElement(eltnum))
                
        self.update_selection_filter_list_widget()
        
    def update_selection_filter_list_widget(self):
        '''Updates the list of elements displayed in the Atom Selection Filter List.
        '''
        filtered_syms=''
        for e in self.w.filtered_elements[:]:
            if filtered_syms: filtered_syms += ", "
            filtered_syms += e.symbol
        self.w.depositAtomDashboard.filterlistLE.setText(filtered_syms)
    
    #== Transmute helper methods
    
    def get_atomtype_from_MMKit(self):
        '''Return the current atomtype selected in the MMKit.
        Note: While this does actually return the atomtype based on what is selected in
        the MMKit, the hybrid is determined by hybridComboBox (hidden).
        '''
        elm = PeriodicTable.getElement(self.w.Element)
        atomtype = None
        if len(elm.atomtypes) > 1: 
            try: 
                hybname = self.w.hybridComboBox.currentText()
                atype = elm.find_atomtype(hybname)
                if atype is not None:
                    atomtype = atype
            except:
                print_compact_traceback("exception (ignored): ") # error, but continue
            pass
        if atomtype is not None and atomtype.element is elm:
            return atomtype
            
        # For element that doesn't support hybridization
        return elm.atomtypes[0]
        
    def transmutePressed(self):
        '''Slot for "Transmute" button. '''
        force = self.w.depositAtomDashboard.transmuteCB.isChecked()
        atomType = self.get_atomtype_from_MMKit()
        self.w.assy.modifyTransmute(self.w.Element, force = force, atomType=atomType)
        
    #== Draw methods
    
    def Draw(self):
        """ Draw 
        """
        selectAtomsMode.Draw(self)
        if self.line:
            color = get_selCurve_color(0,self.backgroundColor) 
                # Make sure line color has good contrast with bg. mark 060305.
            drawline(color, self.line[0], self.line[1])
            ####@@@@ if this is for a higher-order bond, draw differently
        self.o.assy.draw(self.o)
        #bruce 050610 moved self.surface() call elsewhere
        return

    def Draw_after_highlighting(self, pickCheckOnly=False): #bruce 050610
        # added pickCheckOnly arg.  mark 060207.
        """Do more drawing, after the main drawing code has completed its highlighting/stenciling for selobj.
        Caller will leave glstate in standard form for Draw. Implems are free to turn off depth buffer read or write.
        Warning: anything implems do to depth or stencil buffers will affect the standard selobj-check in bareMotion.
        [New method in mode API as of bruce 050610. General form not yet defined -- just a hack for Build mode's
         water surface. Could be used for transparent drawing in general.]
        """
        selectAtomsMode.Draw_after_highlighting(self, pickCheckOnly) #Draw possible other translucent objects. [huaicai 9/28/05]
        
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
        
    def surface(self): #bruce 050610 revised docstring
        """Draw the water's surface -- a sketch plane to indicate where the new atoms will sit by default,
        which also prevents (some kinds of) selection of objects behind it.
        """
        if not self.w.depositAtomDashboard.waterCB.isChecked():
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
        glRotatef(- q.angle*180.0/pi, q.x, q.y, q.z)

##        # The following is wrong for wide windows (bug 264).
##	# To fix it requires looking at how scale is set (differently
##	# and perhaps wrongly (related to bug 239) for tall windows),
##	# so I'll do it later, after fixing bug 239.
##	# Warning: correctness of use of x vs y below has not been verified.
##	# [bruce 041214] ###@@@
##	# ... but for Alpha let's just do a quick fix by replacing 1.5 by 4.0.
##	# This should work except for very wide (or tall??) windows.
##	# [bruce 050120]
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

    def viewing_main_part(self): #bruce 050416 ###e should refile into assy
        return self.o.assy.current_selgroup_iff_valid() is self.o.assy.tree
        
    def makeMenus(self): #bruce 050705 revised this to support bond menus
        "#doc"
        selatom, selobj = self.update_selatom_and_selobj( None)
            # bruce 050612 added this [as an update_selatom call] -- not needed before since bareMotion did it (I guess).
            # [replaced with update_selatom_and_selobj, bruce 050705]
        
        self.Menu_spec = []
        ###e could include disabled chunk & selatom name at the top, whether selatom is singlet, hotspot, etc.
        
        # figure out which Set Hotspot menu item to include, and whether to disable it or leave it out
        if self.viewing_main_part():
            text, meth = ('Set Hotspot and Copy', self.setHotSpot_mainPart)
                # bruce 050121 renamed this from "Set Hotspot" to "Set Hotspot and Copy as Pastable".
                # bruce 050511 shortened that to "Set Hotspot and Copy".
                # If you want the name to be shorter, then change the method
                # to do something simpler! Note that the locally set hotspot
                # matters if we later drag this chunk to the clipboard.
                # IMHO, the complexity is a sign that the design
                # should not yet be considered finished!
        else:
            text, meth = ('Set Hotspot of clipboard item', self.setHotSpot_clipitem)
                ###e could check if it has a hotspot already, if that one is different, etc
                ###e could include atom name in menu text... Set Hotspot to X13
        if selatom is not None and selatom.is_singlet():
            item = (text, meth)
        elif selatom is not None:
            item = (text, meth, 'disabled')
        else:
            item = None
        if item:
            self.Menu_spec.append(item)
        
        # Add the trans-deposit menu item.
        if selatom is not None and selatom.is_singlet():
            self.Menu_spec.append(( 'Trans-deposit from MMKit', lambda dragatom=selatom: self.transdeposit_from_MMKit(dragatom) ))

        # figure out Select This Chunk item text and whether to include it
        ##e (should we include it for internal bonds, too? not for now, maybe not ever. [bruce 050705])
        if selatom is not None:
            name = selatom.molecule.name
            item = ('Select Chunk %r' % name, self.select)
                # bruce 050121 changed Select to a more explicit name, Select This Chunk.
                # bruce 050416 using actual chunk name. (#e Should we worry about it being too long?)
                #e should rename self.select method, once I'm sure it's not called elsewhere (not easy to confirm)
                #e maybe should disable this or change to checkmark item (with unselect action) if it's already selected??
            self.Menu_spec.append(item)

        ##e add something similar for bonds, displaying their atoms, and the bonded chunk or chunks?

        if selatom is not None:
            is_singlet = selatom.is_singlet() and len(selatom.bonds) == 1 #k is 2nd cond redundant with is_singlet()?
        else:
            is_singlet = False

        # add submenu to change atom hybridization type [initial kluge]
        atomtypes = (selatom is None) and ['fake'] or selatom.element.atomtypes
            # kluge: ['fake'] is so the idiom "x and y or z" can pick y;
            # otherwise we'd use [] for 'y', but that doesn't work since it's false.
##        if selatom is not None and not selatom.is_singlet():
##            self.Menu_spec.append(( '%s' % selatom.atomtype.fullname_for_msg(), noop, 'disabled' )) 
        if len(atomtypes) > 1: # i.e. if elt has >1 atom type available! (then it must not be Singlet, btw)
            # make a submenu for the available types, checkmarking the current one, disabling if illegal to change, sbartext for why
            # (this code belongs in some more modular place... where exactly? it's part of an atom-type-editor for use in a menu...
            #  put it with Atom, or with AtomType? ###e)
            submenu = []
            for atype in atomtypes:
                submenu.append(( atype.fullname_for_msg(), lambda arg1=None, arg2=None, atype=atype: atype.apply_to(selatom),
                                 # Notes: the atype=atype is required -- otherwise each lambda refers to the same
                                 # localvar 'atype' -- effectively by reference, not by value --
                                 # even though it changes during this loop!
                                 #   Also at least one of the arg1 and arg2 are required, otherwise atype ends up being an int,
                                 # at least acc'd to exception we get here. Why is Qt passing this an int? Nevermind for now. ###k
                             (atype is selatom.atomtype) and 'checked' or None,
                             (not atype.ok_to_apply_to(selatom)) and 'disabled' or None
                           ))
            self.Menu_spec.append(( 'Atom Type: %s' % selatom.atomtype.fullname_for_msg(), submenu ))
##            self.Menu_spec.append(( 'Atom Type', submenu ))

        ###e offer to change element, too (or should the same submenu be used, with a separator? not sure)

        # for a highlighted bond, add submenu to change bond type, if atomtypes would permit that;
        # or a menu item to just display the type, if not. Also add summary info about the bond...
        # all this is returned (as a menu_spec sublist) by one external helper method.
        
        if is_singlet:
            selbond = selatom.bonds[0]
        else:
            selbond = selobj # might not be a Bond (could be an Atom or None)
        
        try:
            method = selbond.bond_menu_section
        except AttributeError:
            # selbond is not a Bond
            pass
        else:
            glpane = self.o
            quat = glpane.quat
            try:
                menu_spec = method(quat = quat) #e pass some options??
            except:
                print_compact_traceback("exception in bond_menu_section for %r, ignored: " % (selobj,))
            else:
                if menu_spec:
                    self.Menu_spec.extend(menu_spec)
                pass
            pass

        # This is duplicated in selectMode.makeMenus(). mark 060314.
        # local minimize - experimental, nim [bruce 051011, 051207]
        if selatom is not None and not selatom.is_singlet() and self.w.simSetupAction.isEnabled():
            # if simSetupAction is not enabled, a sim process is running.  Fixes bug 1283. mark 060314.
            ## self.Menu_spec.append(( 'Adjust atom %s' % selatom, selatom.minimize_1_atom )) # older pseudocode
            # experimental. if we leave in these options, some of them might want a submenu.
            # or maybe the layer depth is a dashboard control? or have buttons instead of menu items?
            self.Menu_spec.append(( 'Adjust atom %s' % selatom, lambda e1=None,a=selatom: self.localmin(a,0) ))
            self.Menu_spec.append(( 'Adjust 1 layer', lambda e1=None,a=selatom: self.localmin(a,1) ))
            self.Menu_spec.append(( 'Adjust 2 layers', lambda e1=None,a=selatom: self.localmin(a,2) ))
        
        # offer to clean up singlet positions (not sure if this item should be so prominent)
        if selatom is not None and not selatom.is_singlet():
            sings = selatom.singNeighbors() #e when possible, use baggageNeighbors() here and remake_baggage below. [bruce 051209]
            if sings or selatom.bad():
                if sings:
                    text = 'Reposition bondpoints'
                        # - this might be offered even if they don't need repositioning;
                        # not easy to fix, but someday we'll always reposition them whenever needed
                        # and this menu command can be removed then.
                        # - ideally we'd reposition H's too (i.e. call remake_baggage below)
                else:
                    text = 'Add bondpoints' # this text is only used if it doesn't have enough
                self.Menu_spec.append(( text, selatom.remake_singlets )) #e should finish and use remake_baggage (and baggageNeighbors)
        
        # selobj-specific menu items.  This is duplicated in selectMode.makeMenus().
        # [bruce 060405 added try/except, and generalized this from Jig-specific to selobj-specific items,
        #  by replacing isinstance(selobj, Jig) with hasattr(selobj, 'make_selobj_cmenu_items'),
        #  so any kind of selobj can provide more menu items using this API.
        #  Note that the only way selobj could customize its menu items to the calling mode
        #  would be by assuming that was the current glpane.mode. Someday we might extend the API
        #  to pass it glpane, so we can support multiple glpanes, each in a different mode. #e]
        if selobj is not None and hasattr(selobj, 'make_selobj_cmenu_items'):
            try:
                selobj.make_selobj_cmenu_items(self.Menu_spec)
            except:
                print_compact_traceback("bug: exception (ignored) in make_selobj_cmenu_items for %r: " % selobj)
            
        # separator and other mode menu items.
        if self.Menu_spec:
            self.Menu_spec.append(None)
        
        # Enable/Disable Jig Selection.  
        # This is duplicated in selectMode.makeMenus() and selectMolsMode.makeMenus().
        if self.o.jigSelectionEnabled:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'checked')])
        else:
            self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'unchecked')])
            
        self.Menu_spec.extend( [
            # mark 060303. added the following:
            None,
            ('Change Background Color...', self.w.dispBGColor),
            ])

        return # from makeMenus

    def setCarbon_sp3(self):
        self.w.setCarbon() # MWsemantics shouldn't really be involved in this at all... at some point this will get revised
        self.set_pastable_atomtype('sp3')
    
    def setCarbon_sp2(self):
        self.w.setCarbon()
        self.set_pastable_atomtype('sp2')
            
    def setHotSpot_clipitem(self): #bruce 050416; duplicates some code from setHotSpot_mainPart
        "set or change hotspot of a chunk in the clipboard"
        selatom = self.o.selatom
        if selatom and selatom.element is Singlet:
            selatom.molecule.set_hotspot( selatom) ###e add history message??
            self.o.set_selobj(None)  #bruce 050614-b: fix bug703-related older bug (need to move mouse to see new-hotspot color)
            self.o.gl_update() #bruce 050614-a: fix bug 703 (also required having hotspot-drawing code in chunk.py ignore selatom)
        ###e also set this as the pastable??
        return        
        
    def setHotSpot_mainPart(self): #bruce 050121 revised this and renamed its menu item #bruce 050614 renamed it
        "set hotspot on a main part chunk and copy it (with that hotspot) into clipboard"
        # revised 041124 to fix bug 169, by mark and then by bruce
        selatom = self.o.selatom
        if selatom and selatom.element is Singlet:
            selatom.molecule.set_hotspot( selatom)
            
            new = selatom.molecule.copy(None) # None means no dad yet
            #bruce 050531 removing centering:
            ## new.move(-new.center) # perhaps no longer needed [bruce 041206]
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
                # Is this soon enough for UpdateDashboard?? or does it matter if it comes first? ####@@@@
            
            # bruce 050121 don't change selection anymore; it causes too many bugs
            # to have clipboard items selected. Once my new model tree code is
            # committed, we could do this again and/or highlight the pastable
            # there in some other way.
            ##self.o.assy.shelf.unpick() # unpicks all shelf items too
            ##new.pick()
            self.w.depositState = 'Clipboard'
            self.pastable = new # do this again, to influence the following:
            self.UpdateDashboard()
                # (also called by shelf.addchild(), but only after my home mods
                #  to Utility.py get committed, i.e. not yet -- bruce 050121)

            self.w.mt.mt_update() # since clipboard changed
            #bruce 050614 comment: in spite of bug 703 (fixed in setHotSpot_mainPart),
            # I don't think we need gl_update now in this method,
            # since I don't think main glpane shows hotspots and since the user's intention here
            # is mainly to make one in the clipboard copy, not in the main model;
            # and in case it's slow, we shouldn't repaint if we don't need to.
            #   Evidently I thought the same thing in this prior comment, when I removed a glpane update
            # (this might date from before hotspots were ever visible -- not sure):
            ## also update glpane if we show pastable someday; not needed now
            ## [and removed by bruce 050121]
            
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
        if not self.pastable is pastable:
            #k (probably this implies self.pastable is None,
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
            #self.o.assy.pickParts() #& Replaced by permit_pick_parts(). Marked for deletion.  mark 060218.
            self.o.assy.permit_pick_parts()
            self.o.assy.unpickparts()
            self.o.selatom.molecule.pick()
            self.w.win_update()
                                    
    def skip(self):
        pass

    pass # end of class depositMode

# end
