# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
depositMode.py -- Build mode.

$Id$

- bruce 050513 optims: using 'is' and 'is not' rather than '==', '!='
  for atoms, elements, atomtypes, in several places (not all commented individually); 050513

- bruce 050913 used env.history in some places.
"""
__author__ = "Josh"

from Numeric import *
#from modes import *
from selectMode import *
from VQT import *
from chem import *
import drawer
from constants import elemKeyTab, GL_FAR_Z
import platform
from debug import print_compact_traceback
from elements import PeriodicTable
from Utility import imagename_to_pixmap
from HistoryWidget import orangemsg

from bonds import bond_atoms
from bond_constants import V_SINGLE

from prefs_constants import HICOLOR_singlet
    ##e should replace this with a prefs get or so [bruce 050805]

import env

HICOLOR_singlet_bond = white ## ave_colors( 0.5, HICOLOR_singlet, HICOLOR_real_bond)
    # note: HICOLOR_singlet_bond is no longer used (unless there are bugs),
    # since singlet-bond is part of singlet for selobj purposes [bruce 050708]

_count = 0

DRAG_STICKINESS_LIMIT = 0.06 #& Make it a user pref.  Mark 060212.

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
    
HIDE_PASTE_WIDGETS_FOR_A7 = True #& Should this be a user pref for A7? mark 060211.

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
    # The first group is what to do when you click on an open bond or in empty space -- deposit atom or
    # paste object (same as before). The second group is what to do when you click on a bond;
    # it would be nice to add one more choice for "do nothing" but I'm not sure how best to do that.
    #    Also we should replace QPushButton with QToolButton, since the Qt docs for QPushButton make it clear that
    # this is correct based on how these are used. But I can't get QToolButton to work right, so I won't do this now.

    w.depositAtomDashboard.addSeparator()
    bg2 = QButtonGroup(w.depositAtomDashboard)
    bg2.setExclusive(1)
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
    QToolTip.add(w.depositAtomDashboard.buildBtn, qApp.translate("MainWindow","Build Mode", None))
    
    w.depositAtomDashboard.atomBtn = QToolButton(bg2, "")
    w.depositAtomDashboard.atomBtn.setPixmap(imagename_to_pixmap('atom.png'))
    w.depositAtomDashboard.atomBtn.setToggleButton(1)
    w.depositAtomDashboard.atomBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.atomBtn, qApp.translate("MainWindow","Change Atom Mode", None))
    
    w.depositAtomDashboard.bond1Btn = QToolButton(bg2, "")
    w.depositAtomDashboard.bond1Btn.setPixmap(imagename_to_pixmap('bond1.png'))
    w.depositAtomDashboard.bond1Btn.setToggleButton(1)
    w.depositAtomDashboard.bond1Btn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bond1Btn, qApp.translate("MainWindow","Single Bond Mode", None))
    
    w.depositAtomDashboard.bond2Btn = QToolButton(bg2, "")
    w.depositAtomDashboard.bond2Btn.setPixmap(imagename_to_pixmap('bond2.png'))
    w.depositAtomDashboard.bond2Btn.setToggleButton(1)
    w.depositAtomDashboard.bond2Btn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bond2Btn, qApp.translate("MainWindow","Double Bond Mode", None))
    
    w.depositAtomDashboard.bond3Btn = QToolButton(bg2, "")
    w.depositAtomDashboard.bond3Btn.setPixmap(imagename_to_pixmap('bond3.png'))
    w.depositAtomDashboard.bond3Btn.setToggleButton(1)
    w.depositAtomDashboard.bond3Btn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bond3Btn, qApp.translate("MainWindow","Triple Bond Mode", None))
    
    w.depositAtomDashboard.bondaBtn = QToolButton(bg2, "")
    w.depositAtomDashboard.bondaBtn.setPixmap(imagename_to_pixmap('bonda.png'))
    w.depositAtomDashboard.bondaBtn.setToggleButton(1)
    w.depositAtomDashboard.bondaBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bondaBtn, qApp.translate("MainWindow","Aromatic Bond Mode", None))
    
    w.depositAtomDashboard.bondgBtn = QToolButton(bg2, "")
    w.depositAtomDashboard.bondgBtn.setPixmap(imagename_to_pixmap('bondg.png'))
    w.depositAtomDashboard.bondgBtn.setToggleButton(1)
    w.depositAtomDashboard.bondgBtn.setAutoRaise(1)
    QToolTip.add(w.depositAtomDashboard.bondgBtn, qApp.translate("MainWindow","Graphitic Bond Mode", None))

    w.depositAtomDashboard.addSeparator()
    
    w.depositAtomDashboard.autobondCB = QCheckBox("Autobond", w.depositAtomDashboard)
    w.depositAtomDashboard.autobondCB.setChecked(env.prefs[buildModeAutobondEnabled_prefs_key])
    
    w.depositAtomDashboard.waterCB = QCheckBox("Water", w.depositAtomDashboard)
    w.depositAtomDashboard.waterCB.setChecked(env.prefs[buildModeWaterEnabled_prefs_key])
    
    w.depositAtomDashboard.highlightingCB = QCheckBox("Highlighting", w.depositAtomDashboard)
    w.depositAtomDashboard.highlightingCB.setChecked(env.prefs[buildModeHighlightingEnabled_prefs_key])
    
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
    msg_modename = "Build mode" 
    default_mode_status_text = "Mode: Build"

    def __init__(self, glpane):
        selectAtomsMode.__init__(self, glpane)
        self.pastables_list = [] #k not needed here?
        self.water_enabled = env.prefs.get( buildModeWaterEnabled_prefs_key) # mark 060203.
            # if True, only atoms and bonds above the water surface can be 
            # highlighted and selected.
            # if False, all atoms and bonds can be highlighted and selected, and the water 
            # surface is not displayed.

    # methods related to entering this mode
    
    dont_update_gui = True
    def Enter(self):
        #Huaicai 2/28: Move the following statement to surface(), which will
        # be called by Draw() and then by paintGL(), so it will make sure 
        # self.makeCurrent() is called before any OpenGL call.
        #glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        selectAtomsMode.Enter(self)
        #self.o.assy.unpickatoms() 
            # Leave atoms picked. It is very useful to be able to make rect/lasso
            # selections in Select Atoms mode and then move them around
            # in Build mode. I'd like to implement a keypress in Build mode
            # that would switch the user to Select Atoms mode to do a
            # quick rect/lasso selection and switch back when the key is released. 
            # This is very desirable for A7. mark 060201.
        self.o.assy.unpickparts()
        self.o.assy.permit_pick_atoms() #bruce 050517 revised API of this call
#        self.saveDisp = self.o.display # Get display mode from selectAtomsMode. mark 060207.
#        self.o.setDisplay(diTUBES)
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
        #self.modkey = None #& moved to superclass.  mark 060209.
            # The current mod key that is pressed.  It is either None, 'Shift', or 'Control'
        self.ignore_next_leftUp_event = False
            # Set to True in leftDouble() and checked by the left*Up() event handlers
            # to determine whether they should ignore the (second) left*Up event
            # generated by the second LMB up/release event in a double click. 

    def reset_drag_vars(self):
        #bruce 041124 split this out of Enter; as of 041130,
        # required bits of it are inlined into Down methods as bugfixes
        self.cursor_over_when_LMB_pressed = None
            # <cursor_over_when_LMB_pressed> keeps track of what the cursor was over 
            # when the LMB was pressed, which can be one of:
            #   'Empty Space'
            #   'Picked Atom'
            #   'Unpicked Atom'
            #   'Singlet'
            #   'Bond'
        self.drag_multiple_atoms = False
            # set to True when we are dragging a movable unit of 2 or more atoms.
        self.dragatom = None
            # dragatom is the atom dragged by the cursor.
        self.dragatoms = []
            # dragatoms is constructed in setupDragAtoms() and contains all 
            # the selected atoms (except selected baggage atoms) 
            # that are dragged around as a group in dragAtoms().
            # Selected atoms that are baggage are placed in self.baggage
            # along with non-selected baggage atoms connected to dragatoms.
            # See setupDragAtoms() for more information.
        self.pivot = None
        self.pivax = None
        self.baggage = []
            # baggage contains singlets and/or monovalent atoms (i.e. H, O(sp2), F, Cl, Br)
            # which are connected to a dragged atom and get dragged around with it.
            # Also, no atom which has baggage can also be baggage.
        self.nonbaggage = []
            # nonbaggage contains atoms which are bonded to a dragged atom but 
            # are not dragged around with it. Their own baggage atoms are moved when a 
            # single atom is dragged in dragAtom().
        self.line = None
            # endpoints of the white line drawn between the cursor and an open bond when 
            # dragging a singlet.
        self.dragatom_clicked = False 
            # dragatom_clicked is used to determine if a lit up atom was picked (clicked)
            # or not picked (dragged). It must be set to False here so that a newly 
            # deposited atom doesn't pick itself right away.
            # dragatom_clicked is set to True in setupDragAtom() and setupDragChunk()
            # before it gets dragged (if it does at all). If it is dragged, it is set to False
            # in leftDrag() and leftShiftDrag().
            # leftUp() and leftShiftUp() then check it to determine whether the atom 
            # gets picked or not. mark 060125.
        self.obj_doubleclicked = None
            # used by leftDouble() to determine the object that was double clicked.
        self.bond_clicked = None
            # bond that was clicked by LMB during leftDown.
        self.drag_stickiness_limit_exceeded = False
            # used in leftDrag() to determine if the drag stickiness limit was exceeded.
        
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
        self.o.setCursor(self.w.SelectAtomsCursor) # changed from DepositAtomCursor. mark 060202.
        # load default cursor
        self.w.toolsDepositAtomAction.setOn(1) # turn on the Deposit Atoms icon

        self.pastable = None # by bruce 041124, for safety

        update_hybridComboBox(self.w) #bruce 050606; not sure this is the best place for it

        self.bondclick_v6 = None
        self.update_bond_buttons()
        
        # connect signals (these all need to be disconnected in restore_gui) [bruce 050728 revised this]
        self.connect_or_disconnect_signals(True)
        
        self.w.depositAtomDashboard.show() # show the Deposit Atoms dashboard
        
        self.w.zoomToolAction.setEnabled(0) # Disable "Zoom Tool"
        self.w.panToolAction.setEnabled(0) # Disable "Pan Tool"
        self.w.rotateToolAction.setEnabled(0) # Disable "Rotate Tool"

        self.dont_update_gui = False
        
        # Huaicai 7/29/05: Open the MMKit every time entering this mode.
        self.MMKit = self.w.modifyMMKit()
        
        # This is a workaround for a bug caused by the way in which the MMKit is created.
        # This should be fixed when the MMKit code gets cleaned up.  Mark 051216.
        self.MMKit.elemGLPane.change_bg_color(self.backgroundColor, self.backgroundGradient)

        return # the caller will now call update_gui(); we rely on that [bruce 050122]

    def connect_or_disconnect_signals(self, connect): #bruce 050728
        if connect:
            change_connect = self.w.connect
        else:
            change_connect = self.w.disconnect
        change_connect(self.w.pasteComboBox,SIGNAL("activated(int)"),
                       self.setPaste)
        change_connect(self.w.elemChangeComboBox,SIGNAL("activated(int)"),
                       self.setAtom)
            # Qt doc about SIGNAL("activated(int)"): This signal is not emitted
            # if the item is changed programmatically, e.g. using setCurrentItem().
            # Good! [bruce 050121 comment]
        change_connect(self.w.depositAtomDashboard.pasteBtn,
                       SIGNAL("pressed()"), self.setPaste)
        change_connect(self.w.depositAtomDashboard.depositBtn,
                       SIGNAL("pressed()"), self.setAtom)
        
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
        
        # Slots for the Water and Highlight checkboxes. mark 060202.    
        change_connect(self.w.depositAtomDashboard.waterCB,
                        SIGNAL("toggled(bool)"),self.setWater)
        change_connect(self.w.depositAtomDashboard.highlightingCB,
                        SIGNAL("toggled(bool)"),self.setHighlight)
                        
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
            print "update_gui returns since self.dont_update_gui" ####@@@@
            # Getting msg after depositing an atom, then selecting an open bond and 
            # "Select Hotspot and Copy" from the GLPane menu.
            # Is it a bug??? Mark 051212.
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
    
    # restore_gui handles all the GUI display when leaving this mode
    # [mark 041004]
    def restore_gui(self):
        # disconnect signals which were connected in init_gui [bruce 050728]
        self.connect_or_disconnect_signals(False)
        
        self.w.depositAtomDashboard.hide() # Stow away dashboard
        self.w.zoomToolAction.setEnabled(1) # Enable "Zoom Tool"
        self.w.panToolAction.setEnabled(1) # Enable "Pan Tool"
        self.w.rotateToolAction.setEnabled(1) # Enable "Rotate Tool"
        
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
        if self.w.hybridComboBox.isVisible():
            acKeys = [Qt.Key_3, Qt.Key_2, Qt.Key_1, Qt.Key_4]
            num = self.w.hybridComboBox.count()
            if key in acKeys[:num]:
                hybridId = acKeys.index(key)
                self.w.hybridComboBox.setCurrentItem(hybridId)
                self.w.hybridComboBox.emit(SIGNAL("activated"), (hybridId,))
        
        selectAtomsMode.keyPress(self,key) # bruce 050128
        
        if self.o.selobj and self.modkey == 'Delete':
            # If something is under the cursor and we just came out of "delete" mode, 
            # repaint to update its correct (normal) highlight color.
            #& print "depositMode.keyRelease: updating GLPane"
            self.o.gl_update()
        
        return

    def keyRelease(self,key):
        selectAtomsMode.keyRelease(self, key)
        if self.o.selobj and self.prev_modkey == 'Delete':
            # If something is under the cursor and we just came out of "delete" mode, 
            # repaint to update its correct (normal) highlight color.
            #& print "depositMode.keyRelease: updating GLPane"
            self.o.gl_update()

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

    def bareMotion(self, event): #bruce 050610 revised this
        """called for motion with no button down
        [should not be called otherwise -- call update_selatom or update_selobj directly instead]
        """
        self.update_selobj(event)
        # note: this routine no longer updates glpane.selatom. For that see self.update_selatom().

    def selobj_highlight_color(self, selobj): #bruce 050612 added this to mode API
        """[mode API method]
        If we'd like this selobj to be highlighted on mouseover
        (whenever it's stored in glpane.selobj), return the desired highlight color.
        If we'd prefer it not be highlighted (though it will still be stored
        in glpane.selobj and prevent any other objs it obscures from being stored there
        or highlighted), return None. (Warning: exceptions are ignored and cause the
        default highlight color to be used. #e should clean that up sometime)
        """
        if not self.w.depositAtomDashboard.highlightingCB.isChecked():
            return None
        
        if isinstance(selobj, Atom):
            if selobj.is_singlet():
                return HICOLOR_singlet ###@@@ this one is not yet in prefs db
            else:
                if self.modkey == 'Delete':
                    return darkred  
                        # Highlight the atom in darkred if the control key is pressed and it is not picked.
                        # The delete_mode color should be a user pref.  Wait until A8, though.  mark 060129.
                else:
                    return env.prefs.get( atomHighlightColor_prefs_key) ## was HICOLOR_real_atom before bruce 050805
        elif isinstance(selobj, Bond):
            #bruce 050822 experiment: debug_pref to control whether to highlight bonds
            # (when False they'll still obscure other things -- need to see if this works for Mark ####@@@@)
            # ###@@@ PROBLEM with this implem: they still have a cmenu and can be deleted by cmd-del (since still in selobj);
            # how would we *completely* turn this off? Need to see how GLPane decides whether a drawn thing is highlightable --
            # maybe just by whether it can draw_with_abs_coords? Maybe by whether it has a glname (not toggleable instantly)?
            # ... now i've modified GLPane to probably fix that...
            from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
            highlight_bonds = debug_pref("highlight bonds", Choice_boolean_True)
            if not highlight_bonds:
                return None
            ###@@@ use checkbox to control this; when false, return None
            if selobj.atom1.is_singlet() or selobj.atom2.is_singlet():
                # note: HICOLOR_singlet_bond is no longer used, since singlet-bond is part of singlet for selobj purposes [bruce 050708]
                return HICOLOR_singlet_bond
            else:
                if self.modkey == 'Delete': 
                    return darkred # Highlight the bond in darkred if the control key is pressed.
                else:
                    return env.prefs.get( bondHighlightColor_prefs_key) ## was HICOLOR_real_bond before bruce 050805
        elif isinstance(selobj, Jig): #bruce 050729 bugfix (for some bugs caused by Huaicai's jig-selection code)
            return None # (jigs aren't yet able to draw themselves with a highlight-color)
        else:
            print "unexpected selobj class in depmode.selobj_highlight_color:", selobj
            return blue
        
    def update_selobj(self, event): #bruce 050610
        """Keep glpane.selobj up-to-date, as object under mouse, or None
        (whether or not that kind of object should get highlighted).
           Return True if selobj is already updated when we return, or False if that will not happen until the next paintGL.
           Warning: if selobj needs to change, this routine does not change it (or even reset it to None);
        it only sets flags and does gl_update, so that paintGL will run soon and will update it properly,
        and will highlight it if desired ###@@@ how is that controlled? probably by some statevar in self, passed to gl flag?
           This means that old code which depends on selatom being up-to-date must do one of two things:
        - compute selatom from selobj, whenever it's needed;
        - hope that paintGL runs some callback in this mode when it changes selobj, which updates selatom
          and outputs whatever statusbar message is appropriate. ####@@@@ doit... this is not yet fully ok.
        """
        #e see also the options on update_selatom;
        # probably update_selatom should still exist, and call this, and provide those opts, and set selatom from this,
        # but see the docstring issues before doing this ####@@@@

        # bruce 050610 new comments for intended code (#e clean them up and make a docstring):
        # selobj might be None, or might be in stencil buffer.
        # Use that and depthbuffer to decide whether redraw is needed to look for a new one.
        # Details: if selobj none, depth far or under water is fine, any other depth means look for new selobj (set flag, glupdate).
        # if selobj not none, stencil 1 means still same selobj (if no stencil buffer, have to guess it's 0);
        # else depth far or underwater means it's now None (repaint needed to make that look right, but no hittest needed)
        # and another depth means set flag and do repaint (might get same selobj (if no stencil buffer or things moved)
        #   or none or new one, won't know yet, doesn't matter a lot, not sure we even need to reset it to none here first).
        # Only goals of this method: maybe glupdate, if so maybe first set flag, and maybe set selobj none, but prob not
        # (repaint sets new selobj, maybe highlights it).
        # [some code copied from modifyMode]
        glpane = self.o
        glpane.grabKeyboard() 
            # fixes an undocumented bug when depositing a clipboard or library part with modkey pressed. mark 060211.
        wX = event.pos().x()
        wY = glpane.height - event.pos().y()
        selobj = orig_selobj = glpane.selobj
        if selobj is not None:
            if glpane.stencilbits >= 1:
                # optimization: fast way to tell if we're still over the same object as last time
                # (warning: for now glpane.stencilbits is 1 even when true number of bits is higher; easy to fix when needed)
                stencilbit = glReadPixelsi(wX, wY, 1, 1, GL_STENCIL_INDEX)[0][0]
                    # Note: if there's no stencil buffer in this OpenGL context, this gets an invalid operation exception from OpenGL.
                    # And by default there isn't one -- it has to be asked for when the QGLWidget is initialized.
                # stencilbit tells whether the highlighted drawing of selobj got drawn at this point on the screen
                # (due to both the shape of selobj, and to the depth buffer contents when it was drawn)
            else:
                stencilbit = 0 # the correct value is "don't know"; 0 is conservative
                #e might collapse this code if stencilbit not used below;
                #e and/or might need to record whether we used this conservative value
            if stencilbit:
                return True # same selobj, no need for gl_update to change highlighting
        # We get here for no prior selobj,
        # or for a prior selobj that the mouse has moved off of the visible/highlighted part of,
        # or for a prior selobj when we don't know whether the mouse moved off of it or not
        # (due to lack of a stencil buffer, i.e. very limited graphics card or OpenGL implementation).
        #
        # We have to figure out selobj afresh from the mouse position (using depth buffer and/or GL_SELECT hit-testing).
        # It might be the same as before (if we have no stencil buffer, or if it got bigger or moved)
        # so don't set it to None for now (unless we're sure from the depth that it should end up being None) --
        # let it remain the old value until the new one (perhaps None) is computed during paintGL.
        #
        # Specifically, if this method can figure out the correct new setting of glpane.selobj (None or some object),
        # it should set it (###@@@ or call a setter? neither -- let end-code do this) and set new_selobj to that
        # (so code at method-end can repaint if new_selobj is different than orig_selobj);
        # and if not, it should set new_selobj to instructions for paintGL to find selobj (also handled by code at method-end).
        ###@@@ if we set it to None, and it wasn't before, we still have to redraw!
        ###@@@ ###e will need to fix bugs by resetting selobj when it moves or view changes etc (find same code as for selatom).
            
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)[0][0]
            # depth (range 0 to 1, 0 is nearest) of most recent drawing at this mouse position
        new_selobj_unknown = False
            # following code should either set this True or set new_selobj to correct new value (None or an object)
        if wZ >= GL_FAR_Z: ## Huaicai 8/17/05 for blue sky plane z value
            # far depth (this happens when no object is touched)
            new_selobj = None
        else:
            # compare to water surface depth
            cov = - glpane.pov # center_of_view (kluge: we happen to know this is where the water surface is drawn)
            try:
                junk, junk, cov_depth = gluProject( cov[0], cov[1], cov[2] )
            except:
                print_compact_traceback( "gluProject( cov[0], cov[1], cov[2] ) exception ignored, for cov == %r: " % (cov,) )
                cov_depth = 2 # too deep to matter (depths range from 0 to 1, 0 is nearest to screen)
            water_depth = cov_depth
            if self.water_enabled and wZ >= water_depth:
                #print "behind water: %r >= %r" % (wZ , water_depth)
                new_selobj = None
                    # btw, in constrast to this condition for a new selobj, an existing one will
                    # remain selected even when you mouseover the underwater part (that's intentional)
            else:
                # depth is in front of water
                new_selobj_unknown = True
        if new_selobj_unknown:
            # Only the next paintGL call can figure out the selobj (in general),
            # so set glpane.glselect_wanted to the command to do that and the necessary info for doing it.
            # Note: it might have been set before and not yet used;
            # if so, it's good to discard that old info, as we do.
            glpane.glselect_wanted = (wX, wY, wZ) # mouse pos, depth
                ###e and soon, instructions about whether to highlight selobj based on its type (as predicate on selobj)
                ###e should also include current count of number of times
                # glupdate was ever called because model looks different,
                # and inval these instrs if that happens again before they are used
                # (since in that case wZ is no longer correct)
            # don't change glpane.selobj (since it might not even need to change) (ok??#k) -- the next paintGL will do that
            glpane.gl_update()
        else:
            # it's known (to be a specific object or None)
            if new_selobj is not orig_selobj:
                # this is the right test even if one or both of those is None.
                # (Note that we never figure out a specific new_selobj, above,
                #  except when it's None, but that might change someday
                #  and this code can already handle that.)
                glpane.set_selobj( new_selobj, "depmode")
                    #e use setter func, if anything needs to observe changes to this?
                    # or let paintGL notice the change (whether it or elseone does it) and report that?
                    # Probably it's better for paintGL to report it, so it doesn't happen too often or too soon!
                    # And in the glselect_wanted case, that's the only choice, so we needed code for that anyway.
                    # Conclusion: no external setter func is required; maybe glpane has an internal one and tracks prior value.
                glpane.gl_update() # this might or might not highlight that selobj ###e need to tell it how to decide??
        #####@@@@@ we'll need to do this in a callback when selobj is set:
        ## self.update_selatom(event, msg_about_click = True)
        return not new_selobj_unknown # from update_selobj

    def update_selatom(self, event, singOnly = False, msg_about_click = False, resort_to_prior = True): #bruce 050610 rewrote this
        "keep selatom up-to-date, as atom under mouse; ###@@@ correctness after rewrite not yet proven, due to delay until paintGL"
        # bruce 050124 split this out of bareMotion so options can vary
        glpane = self.o
        if event is None:
            # event (and thus its x,y position) is not known [bruce 050612 added this possibility]
            known = False
        else:
            known = self.update_selobj(event) # this might do gl_update (but the paintGL triggered by that only happens later!),
                # and (when it does) might not know the correct obj...
                # so it returns True iff it did know the correct obj (or None) to store into glpane.selobj, False if not.
        assert known in [False,True]
        # If not known, use None or use the prior one? This is up to the caller
        # since the best policy varies. Default is resort_to_prior = True since some callers need this
        # and I did not yet scan them all and fix them. ####@@@@ do that
        selobj = glpane.selobj
        ## print "known %r, selobj %r" % (known, selobj)
        if not known:
            if resort_to_prior:
                pass # stored one is what this says to use, and is what we'll use
                ## print "resort_to_prior using",glpane.selobj
                    # [this is rare, I guess since paintGL usually has time to run after bareMotion before clicks]
            else:
                selobj = None
        oldselatom = glpane.selatom
        atm = selobj
        if not isinstance(atm, Atom):
            atm = None
        if atm is not None and (atm.element is Singlet or not singOnly):
            pass # we'll use this atm as the new selatom
        else:
            atm = None # otherwise we'll use None
        glpane.selatom = atm
        if msg_about_click: # [always do this, since many things can change what it should say]
            # come up with a status bar message about what we would paste now.
            # [bruce 050124 new feature, to mitigate current lack of model tree highlighting of pastable]
            msg = self.describe_leftDown_action( glpane.selatom)
            env.history.statusbar_msg( msg)
        if glpane.selatom is not oldselatom:
            # update display (probably redundant with side effect of update_selobj; ok if it is, and I'm not sure it always is #k)
            glpane.gl_update() # draws selatom too, since its chunk is not hidden [comment might be obs, as of 050610]
        return
    
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
            cmd = "%s onto open bond at %s" % (what, self.posn_str(selatom))
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
    
    def _depositLibraryPart(self, newPart, hotspotAtom, atom_or_pos): # probably by Huaicai; revised by bruce 051227
        '''This method serves as an overloaded method, <atom_or_pos> is 
           the Singlet atom or the empty position that the new part <newPart> will be attached to or placed at.
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
                attch2Atom = attch2Singlet.singlet_neighbor() # atttch to atom

                rotCenter = newMol.center
                rotOffset = Q(ha.posn()-hs.posn(), attch2Singlet.posn()-attch2Atom.posn())
                newMol.rot(rotOffset)
                
                moveOffset = attch2Singlet.posn() - hs.posn()
                newMol.move(moveOffset)
                
                self.__createBond(hs, ha, attch2Singlet, attch2Atom)
                
                self.o.assy.addmol(newMol)
                stuff.append(newMol)
                
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
                    moveOffset = placedPos - newPart.molecules[0].center
        
        if attach2Bond: # Connect part to an open bond of an existing chunk
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
            for m in newPart.molecules:
                newMol = m.copy(None)
                newMol.setAssy(self.o.assy) #bruce 051227 revised this
                
                newMol.move(moveOffset)
                
                self.o.assy.addmol(newMol)
                stuff.append(newMol)
        self.o.assy.update_parts() #bruce 051227 see if this fixes the atom_debug exception in checkparts
        return stuff, "deposited library part" ####@@@@ should revise this message (stub is by bruce 051227)

# == LMB event handling methods ====================================
#
# The following sections include all the LMB event handling methods for depositMode
# The section is organized in the following order and includes the following methods:
#
#   - LMB down-click (button press) methods
#       leftShiftDown()
#       leftCntlDown()
#       leftDown()
#
#   - LMB drag methods
#       leftShiftDrag()
#       leftDrag()
# 
#   - LMB up-click (button release) methods
#       leftShiftUp()
#       leftCntlUp()
#       leftUp()
#
#   - LMB double-click method (only one)
#       leftDouble()
#
# == LMB down-click (button press) methods

    def leftShiftDown(self, event):
        '''Process a Shift + Left Mouse Button (Shift+LMB) down/press event.  What happens is
        dependant on what is currently under the cursor and what is under the cursor when 
        releasing the LMB.  In general, this is what happens for each of the following situations:
            
        Cursor on Empty Space:
            Shift+LMB+click: Do nothing.
            Shift+LMB+Drag: Do nothing.
        
        Cursor on an Unpicked Atom:
            Shift+LMB click: pick the atom, adding it to the selection.
            Shift+LMB+Drag: drag the atom around, along with any singlets or monovalent bonded to it.
            Shift+LMB+Double click: picks the atom and all atoms reachable through any sequence of 
                    bonds to it.

        Cursor on a Picked Atom:
            Shift+LMB click: Do nothing.
            Shift+LMB+Drag: drag the atom and all other selected atoms around, along with any 
                    singlets or monovalent bonded to them.
            Shift+LMB+Double click: picks the atom and all atoms reachable through any sequence of 
                    bonds to it.

        Cursor on a Singlet:
            Shift+LMB click: try to deposit and bond a new object (atom, clipboard chunk or library part) 
                    to the singlet. If the new object does not have a hotspot, do nothing.
            Shift+LMB+Drag: draw a white rubber band line between the singlet and the cursor position.
                    - the bond(s) will also rotate/move as the mouse is dragged.
                    - if the LMB button is released while the same singlet is highlighted, 
                      deposit an object (atom, clipboard chunk or library part) bonded to the singlet.
                    - if the LMB is released while highlighting a different singlet, bond the two singlets.
                    - if the LMB is released in empty space, do not deposit an object. Leave the 
                      bond in place (do not move it back to its original position).

        Cursor on a Bond:
            Shift+LMB click: change the bond to a new bond type determined by the dashboard.
            Shift+LMB+Drag: change the bond to a new bond type determined by the dashboard.
        '''
        # Adding picked atoms to the selection is handled by leftUp(). mark 060203
        self.leftDown(event)
    
    def leftCntlDown(self, event):
        '''Process a Control + Left Mouse Button (Control+LMB) down/press event.  What happens is
        dependant on what is currently under the cursor and what is under the cursor when 
        releasing the LMB.  In general, this is what happens for each of the following situations:
            
        Cursor on Empty Space:
            Control+LMB+click: Do nothing.
            Control+LMB+Drag: Do nothing.
        
        Cursor on an Unpicked Atom:
            Control+LMB click: delete the atom.
            Control+LMB+Drag: do nothing.

        Cursor on a Picked Atom:
            Control+LMB click: unpick the atom.
            Control+LMB+Drag: do nothing.
            Control+LMB+Double click: unpicks the atom and unpicks any picked atoms reachable 
                    through any sequence of bonds to it.

        Cursor on a Singlet:
            Control+LMB click: do nothing.
            Control+LMB+Drag: do nothing.

        Cursor on a Bond:
            Control+LMB click: break the bond.
            Control+LMB+Drag: do nothing.
        '''
        # Removing picked atoms from the selection is handled by leftUp(). mark 060203
        self.leftDown(event)
        
    def leftDown(self, event):
        """Process a Left Mouse Button (LMB) down/press event.  What happens is
        dependant on what is currently under the cursor and what is under the cursor when 
        releasing the LMB.  In general, this is what happens for each of the following situations:
            
        Cursor on Empty Space:
            LMB+click: deposit a new object (atom, clipboard chunk or library part).
            LMB+Drag: On the LMB release, deposit a new object (atom, clipboard chunk 
                    or library part).
        
        Cursor on an Unpicked Atom:
            LMB click: pick the atom.
            LMB+Drag: drag the atom around, along with any singlets or monovalent bonded to it.
            LMB+Double click: picks the atom and all atoms reachable through any sequence of 
                    bonds to it.

        Cursor on a Picked Atom:
            LMB click: pick the atom.
            LMB+Drag: drag the atom and all other selected atoms around, along with any 
                    singlets or monovalent bonded to them.
            LMB+Double click: picks the atom and all atoms reachable through any sequence of 
                    bonds to it.

        Cursor on a Singlet:
            LMB click: try to deposit and bond a new object (atom, clipboard chunk or library part) 
                    to the singlet. If the new object does not have a hotspot, do nothing.
            LMB+Drag: draw a white rubber band line between the singlet and the cursor position.
                    - the bond(s) will also rotate/move as the mouse is dragged.
                    - if the LMB button is released while the same singlet is highlighted, 
                      deposit an object (atom, clipboard chunk or library part) bonded to the singlet.
                    - if the LMB is released while highlighting a different singlet, bond the two singlets.
                    - if the LMB is released in empty space, do not deposit an object. Leave the 
                      bond in place (do not move it back to its original position).

        Cursor on a Bond:
            LMB click: change the bond to a new bond type determined by the dashboard.
            LMB+Drag: change the bond to a new bond type determined by the dashboard.
        """

        if 1: #bruce 060124 undo-debugging code; should be safe for all users ####@@@@
            self.o.assy.current_command_info(cmdname = "BuildClick") #e cmdname should be set more precisely later, instead
        
        # mark 051214 revised docstring
        # bruce 050124 warning: update_selatom now copies lots of logic from here;
        # see its comments if you change this
        self.reset_drag_vars()
        env.history.statusbar_msg(" ") # get rid of obsolete msg from bareMotion [bruce 050124; imperfect #e]
        
        self.current_modkey = self.modkey
            #& self.current_modkey is very important, but NIY.  If the user let's go of the modkey during a
            # 2d region selection, unexpected things may happen. mark 060209.
            
        self.LMB_press_event = QMouseEvent(event) # Save this event.  
            # We need it later when we change our mind and start selecting a 2D region in leftDrag().
            
        self.LMB_press_pt, junk = self.o.mousepoints(event, just_beyond = 0.01)
            # <LMB_press_pt> is the position of the mouse when the LMB was pressed. Used in leftDrag().
            
        a = self.get_obj_under_cursor(event) # mark 060206.
            # <a> can be None and yet we still selected something (i.e. a bond), which is determined by self.o.selobj.
            
        if not a and not self.o.selobj: # Cursor over empty space.
            self.cursor_over_when_LMB_pressed = 'Empty Space'
            self.select_2d_region(event)
            return

        self.modified = 1
        self.o.assy.changed()
        
        if a:
            if a.element is Singlet: # Cursor over a singlet
                if self.modkey != 'Delete':
                    self.cursor_over_when_LMB_pressed = 'Singlet'
                    self.setupDragSinglet(a)
                else: # If the 'Shift' or 'Control' mod keys are pressed, simulate empty space.
                    self.cursor_over_when_LMB_pressed = 'Empty Space'
                    self.select_2d_region(event)
            else: # Cursor over a real atom
                if not a.picked and self.modkey is None:
                    self.o.assy.unpickatoms()
                    a.pick()
                if not a.picked and self.modkey is 'Shift':
                    a.pick()
                if a.picked and len(self.o.assy.selatoms_list()) > 1:
                    # now called when two or more atoms are selected.  mark 060202.
                    self.cursor_over_when_LMB_pressed = 'Picked Atom'
                    self.drag_multiple_atoms = True
                    self.setupDragAtoms(a)
                else:
                    if a.picked:
                        self.cursor_over_when_LMB_pressed = 'Picked Atom'
                    else:
                        self.cursor_over_when_LMB_pressed = 'Unpicked Atom'
                    self.drag_multiple_atoms = False
                    self.setupDragAtom(a)
        
        elif isinstance(self.o.selobj, Bond) and not self.o.selobj.is_open_bond(): # Cursor over a bond.
            # self.o.selobj not updated by findAtomUnderMouse(), so bonds cannot be picked
            # when highlighting is turned off.
            self.cursor_over_when_LMB_pressed = 'Bond'
            self.setupClickedBond(self.o.selobj)

        else: # Cursor is over something else other than an atom, singlet or bond. 
            # The program never executes lines in this else statement since
            # get_obj_under_cursor() only returns atoms and singlets, and
            # self.o.selobj can only be an atom/singlet or a bond as of now.  mark 060206.
            pass

        self.w.win_update()
        return

# == LMB drag methods

    def leftShiftDrag(self, event):
        self.leftDrag(event)
        
    def leftCntlDrag(self, event):
        self.leftDrag(event)
        
    def leftDrag(self, event):
        '''Drag around <dragatom>, which is either an atom or a singlet.
        '''
        
        # Do not change the order of the following conditionals unless you know
        # what you're doing.  mark 060208.
        
        if self.bond_clicked:
            # If a LMB+Drag event has happened after selecting a bond in left*Down(),
            # do a 2D region selection as if the bond were absent. This takes care of 
            # both Shift and Control mod key cases.
            self.cursor_over_when_LMB_pressed = 'Empty Space'
            self.select_2d_region(self.LMB_press_event)
            self.bond_clicked = None
            return
            
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.continue_selection_curve(event)
            return
            
        if self.modkey is not None: #& What happens if the user lets go of Shift or Control?
            # If a Control+LMB+Drag event has happened after the cursor was over an atom 
            # during leftCntlDown(), do a 2D region selection as if the atom were absent.
            self.cursor_over_when_LMB_pressed = 'Empty Space'
            self.select_2d_region(self.LMB_press_event)
            return
            
        if not self.dragatom: return
        
        # We are dragging around a singlet or a real atom.
        
        # Check how far the mouse has been dragged.
        if self.mouse_within_stickiness_limit(event):
            return

        a = self.dragatom
        apos0 = a.posn()
        
        # Drag something.
        if a.element is Singlet:
            self.dragSinglet(a,event)
        else:
            if self.drag_multiple_atoms:
                self.dragAtoms(a, event)
            else:
                self.dragAtom(a, event)
            
        #bruce 041130 added status bar message with new coordinates
        apos1 = a.posn()
        if apos1 - apos0:
            ##k does this ever overwrite some other message we want to keep??
            if a.element is Singlet:
                # this message might not be useful enough to be worthwhile...
                msg = "pulling open bond %r to %s" % (a, self.posn_str(a))
            else:
                msg = "dragged atom %r to %s" % (a, self.posn_str(a))
                self.dragatom_clicked = False # atom was dragged. mark 060125.
            this_drag_id = (self.dragobj_start, self.__class__.leftDrag)
            env.history.message(msg, transient_id = this_drag_id)
        
        self.o.gl_update()
        
# == LMB up-click (button release) methods
        
    def leftShiftUp(self, event):
        self.leftUp(event)
    
    def leftCntlUp(self, event):
        self.leftUp(event)
    
    def leftUp(self, event):
        env.history.flush_saved_transients() # flush any transient message it saved up
        
        if self.ignore_next_leftUp_event: # This event is the second leftUp of a double click, so ignore it.
            self.ignore_next_leftUp_event = False
            return
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.end_selection_curve(event)
            return
            
        self.o.assy.unpickparts() # Fixes bug 1400.  mark 060126.
            #& Should this go further to the top? mark
            
        if self.bond_clicked: 
            # Select or unselect the bond's atoms, or delete the bond, based on the current modkey.
            self.modkeyBond(self.bond_clicked, event)
            return
            
        if not self.dragatom: # No atom or singlet was dragged (or clicked); return.
            return
        
        a = self.dragatom
        
        if self.selCurve_length/self.o.scale < 0.03:
            # didn't move much, call it a click
            event = self.LMB_press_event
        
        if self.dragatom_clicked:
            # Select, unselect or delete the atom based on the current modkey.
            self.modkeyAtom(a, event)
        
        if a.is_singlet():
            # Finish singlet operation.
            self.modkeySinglet(a, event)
        
        self.baggage = []
        self.dragatom = None #bruce 041130 fix bug 230
        self.o.selatom = None #bruce 041208 for safety in case it's killed
        #bruce 041130 comment: it forgets selatom, but doesn't repaint,
        # so selatom is still visible; then the next event will probably
        # set it again; all this seems ok for now, so I'll leave it alone.
        #bruce 041206: I changed my mind, since it seems dangerous to leave
        # it visible (seemingly active) but not active. So I'll repaint here.
        # In future we can consider first simulating a update_selatom at the
        # current location (to set selatom again, if appropriate), but it's
        # not clear this would be good, so *this* is what I won't do for now.
        #self.o.gl_update() #& Now handled in modkey*() methods. mark 060210.
        
# == LMB double-click method
        
    def leftDouble(self, event): # mark 060126.
        '''Double click event handler for the left mouse button. 
        If an atom was double-clicked, select all the atoms reachable through 
        any sequence of bonds to that atom.
        If the Control modkey is pressed, unselect all the atoms.
        '''
        
        if self.cursor_over_when_LMB_pressed == 'Empty Space':
            self.deposit_from_MMKit(self.getCoords(event)) # does win_update().
            return
        
        if isinstance(self.obj_doubleclicked, Atom):
            if self.obj_doubleclicked.is_singlet():
                modkey = self.modkey # save the modkey state
                if self.modkey is None:
                    self.modkey = 'Shift'
                    # needed for trans-deposit selection consistency when no modifier key is pressed.
                for s in self.singlet_list[:]:
                    if s is not self.obj_doubleclicked:
                        #& singlets from deposited obj will autobond with singlets in singlet_list[].
                        #& this is a known bug; to be fixed after talking with Bruce.  mark 060212.
                        self.deposit_from_MMKit(s)
                self.modkey = modkey # restore the modkey state to real state.
            
            else: # real atom
                if self.modkey == 'Control':
                    op = 'Unselect'
                    atomlist = [ self.obj_doubleclicked ]
                elif self.modkey == 'Delete':
                    op = 'Delete'
                    atomlist = self.neighbors_of_last_deleted_atom
                else:
                    op = 'Select'
                    atomlist = [ self.obj_doubleclicked ]
            
                self.o.assy.selectConnected( atomlist, op )
            
        if isinstance(self.obj_doubleclicked, Bond):
            if self.modkey == 'Control':
                op = 'Unselect'
                atomlist = [ self.obj_doubleclicked.atom1 ]
            elif self.modkey == 'Delete':
                op = 'Delete'
                atomlist = [ self.obj_doubleclicked.atom1, self.obj_doubleclicked.atom2 ]
            else:
                op = 'Select'
                atomlist = [ self.obj_doubleclicked.atom1 ]
            
            #print "-------------\nop=", op
            #print "atomlist=",atomlist
            if self.w.depositAtomDashboard.buildBtn.isOn() or self.w.depositAtomDashboard.atomBtn.isOn():
                self.o.assy.selectConnected( atomlist, op )
            else:
                self.change_bondtype(self.bond_clicked)
            
        self.ignore_next_leftUp_event = True

# == end of LMB event handler methods

    def mouse_within_stickiness_limit(self, event):
        '''Returns True if the mouse hasn't exceeded the distance determined by the "stickiness limit".
        Returns False if the mouse has exceeded the limit.
        '''
        if self.drag_stickiness_limit_exceeded:
            return False
        
        LMB_drag_pt, junk = self.o.mousepoints(event, 0.01)
        self.drag_distance = vlen(LMB_drag_pt - self.LMB_press_pt)
        if self.drag_distance/self.o.scale < DRAG_STICKINESS_LIMIT:
            return True
        else:
            self.drag_stickiness_limit_exceeded = True
            return False

    def modkeyBond(self, b, event):
        '''Select or unselect the bond <b>'s atoms, or delete bond <b>, based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>'s two atoms.
        - If Shift modkey is pressed, pick <b>'s two atoms, adding them to the current selection.
        - If Ctrl modkey is pressed,  unpick <b>'s two atoms, removing them from the current selection.
        - If Delete (Shift+Control) modkey is pressed, delete bond <b>.
        '''
        #& To do: check if anything changed (picked/unpicked) before calling gl_update(). 
        #& mark 060210.
        if self.modkey is None:
            # Maintain selection behavior consistency between Standard and Non-standard.
            if env.prefs[selectionBehavior_prefs_key] == A6_SELECTION_BEHAVIOR:
                self.o.assy.unpickatoms() # Clear selection.
            b.atom1.pick()
            b.atom2.pick()
            #& Bond class needs a getinfo() method to be called here. mark 060209.
                
        elif self.modkey == 'Shift':
            b.atom1.pick()
            b.atom2.pick()
            #& Bond class needs a getinfo() method to be called here. mark 060209.
            
        elif self.modkey == 'Control':
            b.atom1.unpick()
            b.atom2.unpick()
            #env.history.message("unpicked %r and %r" % (self.bond_clicked.atom1, self.bond_clicked.atom2))
            #& Not necessary to print history msg.  mark 060210.
                
        elif self.modkey == 'Delete':
            self.break_bond(event)
            
        else:
            print "Error in modkeyBond(): Invalid self.modkey=", self.modkey
            #& Use debug method.  mark 060210.
            return
            
        self.o.gl_update()
        

    def modkeyAtom(self, a, event):
        '''Select, unselect or delete the atom <a> based on the current modkey.
        - If no modkey is pressed, clear the selection and pick atom <a>.
        - If Shift modkey is pressed, pick <a>, adding it to the current selection.
        - If Ctrl modkey is pressed,  unpick <a>, removing it from the current selection.
        - If Delete (Shift+Control) modkey is pressed, delete atom <a>.
        '''
        nochange = False
        
        if self.modkey is None:
            # Maintain selection behavior consistency between Standard and Non-standard.  mark 060125.
            if env.prefs[selectionBehavior_prefs_key] == A6_SELECTION_BEHAVIOR:
                self.o.assy.unpickatoms() # Clear selection.
            if a.picked:
                nochange = True
            else:
                a.pick()
            env.history.message(a.getinfo())

        elif self.modkey == 'Shift':
            if a.picked: 
                nochange = True
            else:
                a.pick()
            env.history.message(a.getinfo())
                
        elif self.modkey == 'Control':
            if a.picked:
                a.unpick()
                env.history.message("unpicked %r" % a)
            else: # Already unpicked.
                nochange = True
            
        elif self.modkey == 'Delete':
            result = self.delete_atom_and_baggage(event)
            env.history.message_no_html(result)
            return # delete_atom_and_baggage() calls win_update.
                
        else:
            print "Error in modkeyAtom(): Invalid self.modkey=", self.modkey
            #& Use debug method.  mark 060210.
            return
            
        if nochange: return
        self.o.gl_update()

    def modkeySinglet(self, s1, event):
        '''Finish operation on singlet <s1> based on where the cursor is when the LMB was released:
        - If the cursor is still on <s1>, deposit an object from the MMKit on it
        - If the cursor is over a different singlet, bond <s1> to it.
        - If the cursor is over empty space, do nothing.
        '''
        if not s1.is_singlet(): return
        
        self.line = None # required to erase white rubberband line on next gl_update.
        
        s2 = self.get_singlet_under_cursor(event)
        if s2:
            if s2 is s1: # If the same singlet is highlighted...
                # ...deposit an object (atom, chunk or library part) from MMKit on the singlet <s1>.
                self.deposit_from_MMKit(s1) 
                    # does its own win_update().
            else: # A different singlet is highlighted...
                # ... so bond the highlighted singlet <s2> to the first singlet <s1>
                self.bond_singlets(s1, s2)
                self.o.gl_update()
        else: # cursor on empty space
            self.o.gl_update() # get rid of white rubber band line.

    def select_2d_region(self, event):
        '''Start 2D selection of a region.
        '''
        if self.modkey is None:
            self.start_selection_curve(event, START_NEW_SELECTION)
        if self.modkey == 'Shift':
            self.start_selection_curve(event, ADD_TO_SELECTION)
        if self.modkey == 'Control':
            self.start_selection_curve(event, SUBTRACT_FROM_SELECTION)
        if self.modkey == 'Delete': # To be implemented soon.  mark 060211.
             self.start_selection_curve(event, DELETE_SELECTION)
        return
            

    def break_bond(self, event):
        '''If the object under the cursor is a bond, break it.
        '''
        self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
            # see warnings about update_selatom's delayed effect, in its docstring or in leftDown. [bruce 050705 comment]
        selobj = self.o.selobj # only used if selatom is None
        if isinstance( selobj, Bond) and not selobj.is_open_bond(): #bruce 050727 new feature
            env.history.message_no_html("breaking bond %s" % selobj)
                ###e %r doesn't show bond type, but %s doesn't work in history since it contains "<-->" which looks like HTML.
                ###e Should fix with a utility to quote HTML-active chars, to call here on the message.
            self.o.selobj = None # without this, the bond remains highlighted even after it's broken (visible if it's toolong)
            selobj.bust() # this fails to preserve the bond type on the open bonds -- not sure if that's bad, but probably it is
            self.o.assy.changed() #k needed?
            
            self.w.win_update()
    
    # get_obj_under_cursor(), get_atom_under_cursor() and get_singlet_under_cursor()
    # should probably be merged into one method with a selection filter arg.  mark 060206.
    def get_obj_under_cursor(self, event):
        '''Return the object under the cursor.  If nothing is under the cursor, return None.
        '''
        if self.w.depositAtomDashboard.highlightingCB.isChecked():
            self.update_selatom(event) #bruce 041130 in case no update_selatom happened yet
        # Warning: if there was no GLPane repaint event (i.e. paintGL call) since the last bareMotion,
        # update_selatom can't make selobj/selatom correct until the next time paintGL runs.
        # Therefore, the present value might be out of date -- but it does correspond to whatever
        # highlighting is on the screen, so whatever it is should not be a surprise to the user,
        # so this is not too bad -- the user should wait for the highlighting to catch up to the mouse
        # motion before pressing the mouse. [bruce 050705 comment]
            a = self.o.selatom # a "lit up" atom or singlet
        else: # No hover highlighting
            a = self.o.assy.findAtomUnderMouse(event, self.water_enabled, singlet_ok = True)
            # Note: findAtomUnderMouse() only returns atoms and singlets, not bonds or jigs.
            # This means that bonds can never be selected when highlighting is turned off.
        return a
            
    def get_atom_under_cursor(self, event):
        '''If the object under the cursor is a real atom, return it.  Otherwise, return None.
        '''
        if self.w.depositAtomDashboard.highlightingCB.isChecked():
            self.update_selatom(event)
            # would be nice if there was an argument for update_selatom to return a real atom only.
            a = self.o.selatom
        else: # No hover highlighting
            a = self.o.assy.findAtomUnderMouse(event, self.water_enabled) # Only returns atoms w/o singlet_ok flag.
        if a and a.is_singlet():
            # if <a> is a singlet, return None
            return None
        return a # <a> is either a real atom or None.
        
    def get_singlet_under_cursor(self, event):
        '''If the object under the cursor is a singlet, return it.  Otherwise, return None.
        '''
        if self.w.depositAtomDashboard.highlightingCB.isChecked():
            self.update_selatom(event, singOnly = True)
            s = self.o.selatom
        else: # No hover highlighting
            s = self.o.assy.findAtomUnderMouse(event, self.water_enabled, singlet_ok = True)
            # would be nice if there was an argument for findAtomUnderMouse to return a singlet only.
        if s and not s.is_singlet():
            return None
        return s


    def unpick_or_delete_atom_OBS(self, event): #& obsolete.  mark 060209.
        '''If the object under the cursor is an atom and it is picked, unpick it.
        If it is not picked, delete it.  Return the result of what happened.
        '''
        a = self.get_atom_under_cursor(event)

        if a is None:
            return None
        
        if a.picked:
            a.unpick()
            result = "unpicked %r" % a
        else:
            # If the atom is not picked, delete it.
            a.deleteBaggage()
            result = "deleted %r" % a
            a.kill()
            self.o.selatom = None #bruce 041130 precaution
            self.o.assy.changed()
        self.w.win_update()
        return result
        
    def delete_atom_and_baggage(self, event):
        '''If the object under the cursor is an atom, delete it and any baggage.  
        Return the result of what happened.
        '''
        a = self.get_atom_under_cursor(event)

        if a is None:
            return None
        
        a.deleteBaggage()
        result = "deleted %r" % a
        self.neighbors_of_last_deleted_atom = a.realNeighbors()
        a.kill()
        self.o.selatom = None #bruce 041130 precaution
        self.o.assy.changed()
        self.w.win_update()
        return result
            
    def change_bondtype(self, bond): #bruce 050727
        '''Change <bond> to new bondtype determined by the dashboard (if allowed).
        '''
        # renamed from clicked_on_bond() mark 060204.
        v6 = self.bondclick_v6
        if v6 is not None:
            btype = btype_from_v6( v6)
            from bond_utils import apply_btype_to_bond
            apply_btype_to_bond( btype, bond)
                # checks whether btype is ok, and if so, new; emits history message; does [#e or should do] needed invals/updates
            ###k not sure if that subr does gl_update when needed... this method does it, but not sure how #######@@@@@@@
        return
        
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
        if perp is None:
            perp = self.o.out
        point2 = planeXline(point, perp, p1, norm(p2-p1)) # args are (ppt, pv, lpt, lv)
        if point2 is None:
            # should never happen, but use old code as a last resort:
            point2 = ptonline(point, p1, norm(p2-p1))
        return point2

# == Deposit methods
        
    def deposit_from_MMKit(self, atom_or_pos): #mark circa 051200; revised by bruce 051227
        '''Deposit a new object based on the current selection in the MMKit/dashboard, 
        which is either an atom, a chunk on the clipboard, or a part from the library.
        If 'atom_or_pos' is a singlet, then it will bond the object to that singlet if it can.
        If 'atom_or_pos' is a position, then it will deposit the object at that coordinate.
        '''
        
        if self.modkey is None: # no Shift or Ctrl modifier key.
            # Maintain selection behavior consistency between Standard and Non-standard.  mark 060125.
            if env.prefs[selectionBehavior_prefs_key] == A6_SELECTION_BEHAVIOR:
                self.o.assy.unpickatoms() # Clear selection.
        
        if self.w.depositState == 'Atoms':
            deposited_stuff, status = self.deposit_from_Atoms_page(atom_or_pos) # deposited_stuff is a chunk
            
        elif self.w.depositState == 'Clipboard':
            deposited_stuff, status = self.deposit_from_Clipboard_page(atom_or_pos) # deposited_stuff is a chunk
                
        elif self.w.depositState == 'Library':
            #bruce 051227 revised this case and its subrs as part of fix of reopened bug 229;
            # deposited_stuff might be a chunk, node, list, etc.
            # Not sure if subrs still print redundant history messages besides the one
            # newly returned here (status).
            deposited_stuff, status = self.deposit_from_Library_page(atom_or_pos)
            if deposited_stuff and self.pickit():
                deposited_stuff[0].pickatoms()
            
        else:
            print "Error. depositState unknown:", self.w.depositState
            return
            
        self.o.selatom = None ##k could this be moved earlier, or does one of those submethods use it? [bruce 051227 question]
            
        # now fix bug 229 part B (as called in comment #2),
        # by making this new chunk (or perhaps multiple chunks, in deposited_stuff) visible if it otherwise would not be.
        # [bruce 051227 is extending this fix to depositing Library parts, whose initial implementation reinstated the bug.
        #  Note, Mark says the following comment is in 2 places but I can't find the other place, so not removing it yet.]
##        # We now have bug 229 again when we deposit a library part while in "invisible" display mode.
##        # Ninad is reopening bug 229 and assigning it to me.  This comment is in 2 places. Mark 051214.
##        if not library_part_deposited:  ##Added the condition [Huaicai 8/26/05] [bruce 051227 removed it, added a different one]
        if deposited_stuff:
            self.w.win_update() 
                #& should we differentiate b/w win_update (when deposited_stuff is a new chunk added) vs. 
                #& gl_update (when deposited_stuff is added to existing chunk).  Discuss with Bruce. mark 060210.
            status = self.ensure_visible( deposited_stuff, status) #bruce 041207
            env.history.message(status)
        else:
            env.history.message(orangemsg(status)) # nothing deposited
        return
            
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
                    #    msg = "To bond this part, you must pick a hotspot by left-clicking on an open bond  " \
                    #            "of the library part in the Modeling Kit's 3D thumbview."
                    #else:
                    #    msg = "The library part cannot be bonded because it has no open bonds."
                    msg = "The library part cannot be bonded because either it has no open bonds"\
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
                        ## status = "replaced open bond on %r with %s (%s)" % (a0, chunk.name, desc)
                        status = "replaced open bond on %r with %s" % (a0, desc) # is this better? [bruce 050121]
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
                    self.o.gl_update() #bruce 050510 moved this here from inside what's now deptool
                    status = "replaced open bond on %r with new atom %s at %s" % (a0, desc, self.posn_str(a1))
                    chunk = a1.molecule #bruce 041207
                else:
                    status = desc
                    chunk = None #bruce 041207
                del a1, desc

        else: # Deposit atom at the cursor position and prep it for dragging
                cursorPos = atom_or_pos
                a = self.o.selatom = oneUnbonded(atype.element, self.o.assy, cursorPos, atomtype = atype)
                self.initDragObject(a)
                self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
                if self.pickit(): self.o.selatom.pick()
                status = "made new atom %r at %s" % (self.o.selatom, self.posn_str(self.o.selatom) )
                chunk = self.o.selatom.molecule #bruce 041207
        
        return chunk, status

        
        
    def setupDragChunk(self, a):
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
        self.initDragObject(a)
        self.dragatom_clicked = True # mark 060125.
        
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
            
    def initDragObject(self, a):
        self.dragatom = a
        # we need to store something unique about this event;
        # we'd use serno or time if it had one... instead this _count will do.
        global _count
        _count = _count + 1
        self.dragobj_start = _count
            
    def dragChunk(self, a, event):
        """Drag a chunk around by atom <a>.
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

    
    def setupClickedBond(self, b):
        '''Setup for a clicked bond <b>.
        '''
        self.bond_clicked = b
        self.obj_doubleclicked = b
        
    def setupDragAtom(self, a):
        '''Setup dragging of real atom <a>.
        '''
        self.initDragObject(a)
        self.dragatom_clicked = True
        self.obj_doubleclicked = a
        self.baggage = []
        self.nonbaggage = []
        self.baggage, self.nonbaggage = a.baggage_and_other_neighbors()
        
    def setupDragAtoms(self, a):
        '''Setup dragging of real atom <a> and all other currently selected atoms.
        '''
        self.initDragObject(a)
        self.dragatom_clicked = True
        self.obj_doubleclicked = a
        self.baggage = []
        self.nonbaggage = []
        #all_nonbaggage = [] # NIY. mark 060202.
        
        selatoms = self.o.assy.selatoms_list()
        
        # Accumulate all the baggage from the selected atoms, which can include
        # selected atoms if a selected atom is another selected atom's baggage.
        # BTW, it is not possible for an atom to end up in self.baggage twice.
        for at in selatoms[:]:
            baggage, nonbaggage = at.baggage_and_other_neighbors()
            self.baggage += baggage # the baggage we'll keep.
            #all_nonbaggage += nonbaggage
        
        # dragatoms contains all the selected atoms minus atoms that are also 
        # baggage. It is critical that dragatoms does not contain any baggage 
        # atoms or they will be moved twice in dragAtoms(), so we removed them here.
        for at in selatoms[:]:
            if not at in self.baggage: # no baggage atoms in dragatoms.
                self.dragatoms.append(at)
        
        # Accumulate all the nonbaggage bonded to the selected atoms.
        # We also need to keep a record of which selected atom belongs to
        # each nonbaggage atom.  This is not implemented yet, but will be needed
        # to get dragAtoms() to work properly.  I'm commenting it out for now.
        # mark 060202.
        #for at in all_nonbaggage[:]:
        #    if not at in self.dragatoms:
        #        self.nonbaggage.append(at)
        
        # Debugging print statements.  mark 060202.
        #print "dragatoms = ", self.dragatoms
        #print "baggage = ", self.baggage    
        #print "nonbaggage = ", self.nonbaggage

    def dragAtom(self, a, event):
        """Drag an atom <a>, which is never a singlet.
        """
        px = self.dragto(a.posn(), event)
        apo = a.posn()
        delta = px - apo # xyz delta between new and current position of <a>.
        
        n = self.nonbaggage
            # n = real atoms bonded to <a> that are not singlets or monovalent atoms.
            # they need to have their own baggage adjusted below.
        
        old = V(0,0,0)
        new = V(0,0,0)
            # old and new are used to compute the delta quat for the average 
            # non-baggage bond and apply it to <a>'s baggage
        
        for at in n:
            # Since adjBaggage() doesn't change at.posn(), I switched the order for readability.
            # It is now more obvious that <old> and <new> have no impact on at.adjBaggage(). 
            # mark 060202.
            at.adjBaggage(a, px) # Adjust the baggage of nonbaggage atoms.
            old += at.posn()-apo
            new += at.posn()-px
        
        # Handle baggage differently if <a> has nonbaggage atoms.
        if n: # If <a> has nonbaggage atoms, move and rotate its baggage atoms.
            q=Q(old,new)
            for at in self.baggage:
                at.setposn(q.rot(at.posn()-apo)+px)
        else: # If <a> has no nonbaggage atoms, just move each baggage atom (no rotation).
            for at in self.baggage:
                at.setposn(at.posn()+delta)
        # [Josh wrote, about the following "a.setposn(px)":]
        # there's some weirdness I don't understand
        # this doesn't work if done before the loop above
        a.setposn(px)
        # [bruce 041108 writes:]
        # This a.setposn(px) can't be done before the at.adjBaggage(a, px)
        # in the loop before it, or adjBaggage (which compares a.posn() to
        # px) would think atom <a> was not moving.
        
    def dragAtoms(self, a, event):
        """Drag the atom <a> and all picked atoms.
        """
        # dragAtoms() behaves differently than dragAtom() in that nonbaggage atoms 
        # and their own baggage are not used or moved in any way. I used to think this 
        # was a feature and not a bug, but I'm pretty sure I was wrong about that since
        # other programs behave like dragAtom() when dragging two or more atoms.
        # The current implementation is still better than nothing and might be OK for A7.
        # I'm guessing we'll want to change it, though.  If so, I have a good idea how to 
        # code it, but it will take a day to get it working properly. mark 060201.
        
        # Note: <a> gets moved in one of the two 'for' loops below.  
        # If <a> is a baggage atom, it will be in the baggage list.  
        # Otherwise, it will be in dragatoms. mark 060201.
        
        px = self.dragto(a.posn(), event)
        apo = a.posn()
        delta = px - apo # xyz delta between new and current position of <a>.

        # Move dragatoms.
        for at in self.dragatoms[:]:
            at.setposn(at.posn()+delta)
        
        # Move baggage.
        for at in self.baggage[:]:
            at.setposn(at.posn()+delta)
      
    def setupDragSinglet(self, a):
        '''Setup dragging of singlet <a>.
        '''
        self.initDragObject(a)
        self.obj_doubleclicked = a # for trans-deposit implem (soon). mark 060211.
        
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


    def dragSinglet(self, a, event):
        """Drag a singlet.
        """
        if a.element is not Singlet: return

        px = self.dragto(a.posn(), event)
        
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
        if self.pickit():
            numol.pickatoms()
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
        "called from radiobutton presses and spinbox changes" #k really from spinbox changes? I doubt it...#bruce 050121
        self.pastable = None # but spinbox records it... but not if set of pastables is updated! so maybe a bad idea? ##k
        self.w.depositState = 'Atoms'
        self.w.update_depositState_buttons()
        self.UpdateDashboard() #bruce 050121 added this

    bondclick_v6 = None
    
    def setBond1(self, state):
        self.setBond(V_SINGLE, state, self.w.depositAtomDashboard.bond1Btn )
        
    def setBond2(self, state):
        self.setBond(V_DOUBLE, state, self.w.depositAtomDashboard.bond2Btn )
    
    def setBond3(self, state):
        self.setBond(V_TRIPLE, state, self.w.depositAtomDashboard.bond3Btn )
        
    def setBonda(self, state):
        self.setBond(V_AROMATIC, state, self.w.depositAtomDashboard.bondaBtn )

    def setBondg(self, state): #mark 050831
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
        return
        
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
        
    def setHighlight(self, on):
        '''Turn hover highlighting on/off.
        if <on> is True, atoms and bonds are highlighted as the cursor passes over them.
        if <on> is False, atoms are not highlighted until they are selected (with LMB click).
        Bonds are not highlighted either, but they cannot be selected when highlighting is turned off.
        '''
        if on:
            msg = "Highlighting turned on."
        else:
            msg = "Highlighting turned off."
        env.history.message(msg)
    
    def Draw(self):
        """ Draw 
        """
        selectAtomsMode.Draw(self)
        if self.line:
            drawline(white, self.line[0], self.line[1])
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

    call_makeMenus_for_each_event = True #bruce 050416/050420 using new feature for dynamic context menus

    def update_selatom_and_selobj(self, event = None): #bruce 050705
        """update_selatom (or cause this to happen with next paintGL);
        return consistent pair (selatom, selobj);
        atom_debug warning if inconsistent
        """
        #e should either use this more widely, or do it in selatom itself, or convert entirely to using only selobj.
        self.update_selatom( event) # bruce 050612 added this -- not needed before since bareMotion did it (I guess).
            ##e It might be better to let set_selobj callback (NIM, but needed for sbar messages) keep it updated.
            #
            # See warnings about update_selatom's delayed effect, in its docstring or in leftDown. [bruce 050705 comment]
        selatom = self.o.selatom
        selobj = self.o.selobj #bruce 050705 -- #e it might be better to use selobj alone (selatom should be derived from it)
        if selatom is not None:
            if selobj is not selatom:
                if platform.atom_debug:
                    print "atom_debug: selobj %r not consistent with selatom %r -- using selobj = selatom" % (selobj, selatom)
                selobj = selatom # just for our return value, not changed in GLPane (self.o)
        else:
            pass #e could check that selobj is reflected in selatom if an atom, but might as well let update_selatom do that,
                # esp. since it behaves differently for singlets
        return selatom, selobj
        
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

        # local minimize - experimental, nim [bruce 051011, 051207]
        if selatom is not None and not selatom.is_singlet():
            ## self.Menu_spec.append(( 'Minimize atom %s' % selatom, selatom.minimize_1_atom )) # older pseudocode
            # experimental. if we leave in these options, some of them might want a submenu.
            # or maybe the layer depth is a dashboard control? or have buttons instead of menu items?
            self.Menu_spec.append(( 'Minimize atom %s' % selatom, lambda e1=None,a=selatom: self.localmin(a,0) ))
            self.Menu_spec.append(( 'Minimize 1 layer', lambda e1=None,a=selatom: self.localmin(a,1) ))
            self.Menu_spec.append(( 'Minimize 2 layers', lambda e1=None,a=selatom: self.localmin(a,2) ))
        
        # offer to clean up singlet positions (not sure if this item should be so prominent)
        if selatom is not None and not selatom.is_singlet():
            sings = selatom.singNeighbors() #e when possible, use baggageNeighbors() here and remake_baggage below. [bruce 051209]
            if sings or selatom.bad():
                if sings:
                    text = 'Reposition open bonds'
                        # - this might be offered even if they don't need repositioning;
                        # not easy to fix, but someday we'll always reposition them whenever needed
                        # and this menu command can be removed then.
                        # - ideally we'd reposition H's too (i.e. call remake_baggage below)
                else:
                    text = 'Add open bonds' # this text is only used if it doesn't have enough
                self.Menu_spec.append(( text, selatom.remake_singlets )) #e should finish and use remake_baggage (and baggageNeighbors)

        # separator and changers to other modes
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
            ('(change pastable element:)', noop, 'disabled'), #bruce 050510
            ('Carbon(sp3)', self.setCarbon_sp3), #e could make this a method on the atomtype, and give that a name or find it here
            ('Carbon(sp2)', self.setCarbon_sp2),
            ('Hydrogen', self.w.setHydrogen),
            ('Oxygen', self.w.setOxygen),
            ('Nitrogen', self.w.setNitrogen) ]

        # Ninad says this is redundant, but I left it in; Josh should decide
        # for this mode [bruce 041103]
        # (If this remains, shouldn't these cmds also first select just the selatom's chunk? [bruce 050510])
        self.Menu_spec_control = [
            ('Passivate', self.o.assy.modifyPassivate),
            ('Hydrogenate', self.o.assy.modifyHydrogenate),
            ('Dehydrogenate', self.o.assy.modifyDehydrogenate) ]

        return # from makeMenus

    def localmin(self, atom, nlayers): #bruce 051207 #e might generalize to take a list or pair of atoms, other options
        if platform.atom_debug:
            print "atom_debug: reloading runSim on each use, for development [localmin %s, %d]" % (atom, nlayers)
            import runSim
            reload(runSim)
        from runSim import LocalMinimize_function
        LocalMinimize_function( [atom], nlayers )
        return
        
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

# end