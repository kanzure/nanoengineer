# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
THIS FILE IS PRESENTLY OWNED BY BRUCE -- please don't change it in any way,
however small, unless this is necessary to make Atom work properly for other developers.
[bruce 040921]

$Id$

Stub file for Extrude mode. For now, this works, but it's almost identical to cookieMode,
except for a different background color.
-- bruce 040924
"""

from modes import *
from qt import QSpinBox, QDoubleValidator

class FloatSpinBox(QSpinBox):
    "spinbox for a coordinate in angstroms -- permits negatives, floats"
    range_angstroms = 1000.0 # value can go to +- this many angstroms
    precision_angstroms = 100 # with this many detectable units per angstrom
    def __init__(self, *args, **kws):
        assert not kws, "keyword arguments are not supported by QSpinBox"
        QSpinBox.__init__(self, *args) #k #e note, if the args can affect the range, we'll mess that up below
        ## self.setValidator(0) # no keystrokes are prevented from being entered
            ## TypeError: argument 1 of QSpinBox.setValidator() has an invalid type -- hmm, manual didn't think so -- try None? #e
        self.setValidator( QDoubleValidator( - self.range_angstroms, self.range_angstroms, 2, self ))
            # QDoubleValidator has a bug: it turns 10.2 into 10.19! But mostly it works. Someday we'll need our own. [bruce 041009]
        self.setRange( - int(self.range_angstroms * self.precision_angstroms),
                         int(self.range_angstroms * self.precision_angstroms) )
        self.setSteps( self.precision_angstroms, self.precision_angstroms * 10 ) # set linestep and pagestep
    def mapTextToValue(self):
        text = self.cleanText()
        print "fyi: float spinbox got text %r" % text # what datatype is this?
        text = str(text) # in case it's a qt string
        try:
            fval = float(text)
            ival = int(fval * self.precision_angstroms) # 2-digit precision
            return ival, True
        except:
            return 0, False
    def mapValueToText(self, ival):
        fval = float(ival)/self.precision_angstroms
        return str(fval) #k should not need to make it a QString
    def floatValue(self):
        return float( self.value() ) / self.precision_angstroms
    def setFloatValue(self, fval):
        self.setValue( int( fval * self.precision_angstroms ) )
    pass

MAX_NCOPIES = 100 # max number of extrude-unit copies. Should be larger. ####e

# bruce 040920: until MainWindow.ui does the following, I'll do it manually:
# (FYI: I will remove this, and the call to this, after MainWindowUI does the same stuff.
#  But first I will be editing this function a lot to get the dashboard contents that I need.)
def do_what_MainWindowUI_should_do(self):
        "self should be the main MWSemantics object -- at the moment this is a function, not a method"

        from qt import SIGNAL, QToolBar, QLabel, QLineEdit, QSpinBox

        # 1. connect the mode-entering button to its MWSemantics method 
        ## bugfix: no longer needed as of 040928 when Mark evidently added this to the .ui file! Removed by bruce 040929.
        ## self.connect(self.toolsExtrudeAction,SIGNAL("activated()"),self.toolsExtrude)
            # fyi, this is modelled after: 
            # self.connect(self.toolsCookieCutAction,SIGNAL("activated()"),self.toolsCookieCut)

        # 2. make a toolbar to be our dashboard, similar to the cookieCutterToolbar
        # (based on the code for cookieCutterToolbar in MainWindowUI)

        self.extrudeDashboard = QToolBar(QString(""),self,Qt.DockBottom)
        self.extrudeToolbar = self.extrudeDashboard # bruce 041007 so I don't have to rename this in MWsemantics.py yet

        self.extrudeDashboard.setGeometry(QRect(0,0,515,29)) ### will probably be wrong once we modify the contents
        self.extrudeDashboard.setBackgroundOrigin(QToolBar.WidgetOrigin)

        self.textLabel_extrude_toolbar = QLabel(self.extrudeDashboard,"textLabel_extrude_toolbar")
        self.textLabel_extrude_toolbar.setText(self._MainWindow__tr("Extrude Mode (stub)")) # see note below about __tr

        # these are the wrong actions to add... should cause no harm for now, tho
        self.extrudeDashboard.addSeparator()
##        self.ccGraphiteAction.addTo(self.extrudeDashboard)
##        self.extrudeDashboard.addSeparator()
##        self.orient100Action.addTo(self.extrudeDashboard)
##        self.orient110Action.addTo(self.extrudeDashboard)
##        self.orient111Action.addTo(self.extrudeDashboard)
##        self.extrudeDashboard.addSeparator()
##        self.ccAddLayerAction.addTo(self.extrudeDashboard)
##        self.extrudeDashboard.addSeparator()

        # ideally these should be known only to the mode, not be members of the main window object --
        # but once the .ui file does this, that might be the only place it can easily put them, so we live with that.
        # and what we need is different... ok for now
        ##self.extrudeLineEdit = QLineEdit(self.extrudeDashboard,"extrudeLineEdit")
        # these need labels; some of them need float values
        def insertlabel(text):
            label = QLabel(self.extrudeDashboard,"extrude_label_"+text.strip())
            label.setText(self._MainWindow__tr(text))
            #e don't bother retaining it (ok??)
        insertlabel(" N ")
        self.extrudeSpinBox_n = QSpinBox(self.extrudeDashboard,"extrudeSpinBox_n")
        self.extrudeSpinBox_n.setRange(1,MAX_NCOPIES)
        self.extrudeDashboard.addSeparator()
        insertlabel(" X ") # number of spaces is intentionally different on different labels
        self.extrudeSpinBox_x = FloatSpinBox(self.extrudeDashboard,"extrudeSpinBox_x")
        insertlabel("  Y ")
        self.extrudeSpinBox_y = FloatSpinBox(self.extrudeDashboard,"extrudeSpinBox_y")
        insertlabel("  Z ")
        self.extrudeSpinBox_z = FloatSpinBox(self.extrudeDashboard,"extrudeSpinBox_z")
        self.extrudeDashboard.addSeparator()
        insertlabel(" length ") # units?
        self.extrudeSpinBox_length = FloatSpinBox(self.extrudeDashboard,"extrudeSpinBox_length")

        reinit_extrude_controls(self)
        
        self.extrudeDashboard.addSeparator()

        # dashboard tools shared with other modes
        self.toolsBackUpAction.addTo(self.extrudeDashboard) #e want this??
        self.toolsStartOverAction.addTo(self.extrudeDashboard)
        self.toolsDoneAction.addTo(self.extrudeDashboard)
        self.toolsCancelAction.addTo(self.extrudeDashboard)

        # note: python name-mangling would turn __tr, within class MainWindow, into _MainWindow__tr (I think... seems to be right)
        self.extrudeDashboard.setLabel(self._MainWindow__tr("Extrude Mode"))
        

        # fyi: caller hides the toolbar, we don't need to
        
        return

import math

def reinit_extrude_controls(win):
    "reinitialize the extrude controls; used whenever we enter the mode; win should be the main window (MWSemantics object)"
    win.extrudeSpinBox_n.setValue(3)
    set_extrude_controls_xyz(win, (5,5,5)) # this default should (at least) be fixed in eyespace, not modelspace as it is here

def set_extrude_controls_xyz_nolength(win, (x,y,z) ):
    win.extrudeSpinBox_x.setFloatValue(x)
    win.extrudeSpinBox_y.setFloatValue(y)
    win.extrudeSpinBox_z.setFloatValue(z)

def set_extrude_controls_xyz(win, (x,y,z) ):
    set_extrude_controls_xyz_nolength( win, (x,y,z) )
    update_length_control_from_xyz(win)

def get_extrude_controls_xyz(win):
    x = win.extrudeSpinBox_x.floatValue()
    y = win.extrudeSpinBox_y.floatValue()
    z = win.extrudeSpinBox_z.floatValue()
    return (x,y,z)

suppress_valuechanged = 0

def call_while_suppressing_valuechanged(func):
    global suppress_valuechanged
    old_suppress_valuechanged = suppress_valuechanged
    suppress_valuechanged = 1
    try:
        func()
    finally:
        suppress_valuechanged = old_suppress_valuechanged

def update_length_control_from_xyz(win):
    x,y,z = get_extrude_controls_xyz(win)
    ll = math.sqrt(x*x + y*y + z*z)
    call_while_suppressing_valuechanged( lambda: win.extrudeSpinBox_length.setFloatValue(ll) )
    
def update_xyz_controls_from_length(win):
    x,y,z = get_extrude_controls_xyz(win)
    ll = math.sqrt(x*x + y*y + z*z)
    length = win.extrudeSpinBox_length.floatValue()
    rr = float(length) / ll
    ## if rr != 1.0: #e sensible? works to prevent infloop? (i doubt it, due to truncation to 2-digit precision)
    call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz_nolength( win, (x * rr, y * rr, z * rr) ) )

# ==

class extrudeMode(basicMode):

    # class constants
    backgroundColor = 200/256.0, 100/256.0, 100/256.0 # different than in cookieMode
    modename = 'EXTRUDE'
    default_mode_status_text = "Mode: Extrude"

    # default initial values
    ###

    # no __init__ method needed
    
    # methods related to entering this mode

##    def refuseEnter(self, warn):
##        "if we'd refuse to enter this mode, then (iff warn) tell user why, and (always) return true."
##        from debug import print_compact_stack # re-import each time, so reload(debug) is effective at runtime
##        print_compact_stack("refuseEnter")
##        assy = self.o.assy
##        if len(assy.selmols) != 1:
##            if warn:
##                self.warning("extrude mode stub requires exactly 1 molecule to be selected, for now (sorry)")
##            return 1
##        return 0

    def connect_controls(self):
        "connect the dashboard controls to their slots in this method"
        ###e we'll need to disconnect these when we're done, but we don't do that yet
        # (predict this is a speed hit, but probably not a bug)

        
        ## from some other code:
        ## self.connect(self.NumFramesWidget,SIGNAL("valueChanged(int)"),self.NumFramesValueChanged)
        ## but we should destroy conn when we exit the mode... but i guess i can save that for later... since spinbox won't be shown then
        # and since redundant conns will not kill me for now.
        # self.w is a guess for where to put the conn, not sure it matters as long as its a Qt object
        self.w.connect(self.w.extrudeSpinBox_n,SIGNAL("valueChanged(int)"),self.spinbox_value_changed) #####k
        self.w.connect(self.w.extrudeSpinBox_x,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_y,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_z,SIGNAL("valueChanged(int)"),self.spinbox_value_changed)
        self.w.connect(self.w.extrudeSpinBox_length,SIGNAL("valueChanged(int)"),self.length_value_changed) # needs its own slot

        return

    def now_using_this_mode_object(self): ###e refile this in modes.py basicMode?
        "return true if the glpane is presently using this mode object (not just a mode object with the same name!)"
        return self.o.mode == self ###k 041009
        
    def Enter(self):
        reinit_extrude_controls(self.w)
        basicMode.Enter(self)
        ###
        # find out what's selected, which if ok will be the repeating unit we will extrude... explore its atoms, bonds, externs...
        # what's selected should be its own molecule if it isn't already...
        # for now let's hope it is exactly one (was checked in refuseEnter, but not anymore).
        assy = self.o.assy
        self.assy = assy ##k i hope this never changes during one use of this mode! probably this mode controls it then, right?

        ok, mol = assy_extrude_unit(self.assy)
        if not ok:
            whynot = mol
            #e show the reason why not?
            print "why not: %r" % (whynot,) ###e improve
            return 1 # refused!
        ##mol = assy.selmols[0]
        self.basemol = mol
        offset = V(15.0,16.0,17.0) #e this will be editable (what are the offset units btw?)
        self.offset = offset
        
        self.ncopies = 1 # might not be true if we reenter the mode with one copy selected! ignore that issue for now.
        ### note, nothing makes sure the new mol is visible in the window except keeping this small!!
        # now see if we can copy it, moved over a bit, and add that to the assembly

        self.molcopies = [self.basemol] # if we have any potential mols to show dimly, they are not in here

        self.connect_controls()
        self.update_from_controls()

        
        ###e we might optimize by not creating these, only displaying them, but i ignore this issue for now
        
##        print "adding a copy of your selected molecule"
##        mols = [mol]
##        newmols = assy_copy(assy, mols, offset = offset)
##        newmol = newmols[0]
        
        ## wrong i guess: assy.addmol(newmol)
        ###### do we need to tell it to repaint???? don't know yet
        ##### need to add some selection behavior
        ### and make the spinbox set the number of copies
        ### and change the scaleas needed for that. or show the copies that are not visible somehow, like an arrow pointing to them...
        import __main__
        __main__.mode = self
        print "extrude debug instructions: __main__.mode = this extrude mode obj; use debug window; has members assy, etc"
        #### .assy

    def asserts(self):
        assert len(self.molcopies) == self.ncopies
        assert self.molcopies[0] == self.basemol

    def spinbox_value_changed(self, val):
        "call this when any spinbox value changed, except length."
        global suppress_valuechanged
        if suppress_valuechanged:
            return
        if not self.now_using_this_mode_object():
            #e we should be even more sure to disconnect the connections causing this to be called
            print "fyi: not now_using_this_mode_object" ####### i predict this will happen, after you load a new file...
            return
        update_length_control_from_xyz(self.w)
        self.update_from_controls()
            # use now-current value, not the one passed
            # (hoping something collapsed multiple signals into one event...)
            #e probably that won't happen unless we do something here to
            # generate an event.... probably doesn't matter anyway,
            #e unless code to adjust to one more or less copy is way to slow.

    def length_value_changed(self, val):
        "call this when the length spinbox changes"
        global suppress_valuechanged
        if suppress_valuechanged:
            return
        if not self.now_using_this_mode_object():
            print "fyi: not now_using_this_mode_object"
            return
        update_xyz_controls_from_length(self.w)
        self.update_from_controls()

    def update_from_controls(self):
        """make the number and position of the copies of basemol what they should be, based on current control values.
        Never modify the control values! (That would infloop.)
        This should be called in Enter and whenever relevant controls might change.
        """
        self.asserts()

        want_n = self.w.extrudeSpinBox_n.value()
        (want_x, want_y, want_z) = get_extrude_controls_xyz(self.w)
        ##wrong: set_extrude_controls_xyz(self.w, (want_x, want_y, want_z)) # also fixes length
        ##print "update_from_controls: want %d, have %d" % (want_n, self.ncopies) #debug
        ncopies_wanted = want_n
        ncopies_wanted = min(20,ncopies_wanted) # low upper limit, for safety, for now ### even less than MAX_NCOPIES
        ncopies_wanted = max(1,ncopies_wanted) # always at least one copy ###e fix spinbox's value too?? also think about it on exit...
        if ncopies_wanted != want_n:
            print "fyi, ncopies_wanted is limited to safe value %r, not your requested value %r" % (ncopies_wanted, want_n)

        offset_wanted = V(want_x, want_y, want_z) # (what are the offset units btw? i guess angstroms, but verify #k)

        # update:
        # first move the copies in common, if offset changed (which is pretty unlikely while it's hardcoded to a constant :-)
        ncopies_common = min(ncopies_wanted,self.ncopies)
        ## ncopies_new = ncopies_wanted - ncopies_common # might not need this count
        ## ncopies_obs = self.ncopies - ncopies_common # ditto
        if offset_wanted != self.offset:
            for ii in range(ncopies_common):
                if ii:
                    motion = (offset_wanted - self.offset)*ii
                    mol0 = self.molcopies[ii]
                    ##print "moving %r by %r" % (mol0, motion) #debug
                    mol0.move(motion)
            self.offset = offset_wanted
        # now delete or make copies as needed (but don't adjust view until the end)
        while self.ncopies > ncopies_wanted:
            # delete a copy we no longer want
            ii = self.ncopies - 1
            self.ncopies = ii
            old = self.molcopies.pop(ii)
            ##print "killmol"#debug
            old.unpick() # work around a bug in assy.killmol [041009]
            self.assy.killmol(old)
            self.asserts()
        while self.ncopies < ncopies_wanted:
            # make a new copy we now want
            #e the fact that it shows up immediately in model tree would permit user to change its color, etc;
            #e but we'll probably want to figure out a decent name for it, make a special group to put these in, etc
            ii = self.ncopies
            self.ncopies = ii + 1
            newmols = assy_copy(self.assy, [self.basemol], offset = self.offset * ii)
            self.basemol.pick() #041009 undo an unwanted side effect of assy_copy (probably won't matter, eventually)
            new = newmols[0]
            self.molcopies.append(new)
            self.asserts()
        ####
        pass
        # now we'd adjust view, or make drawing show if stuff is out of view; make atom overlaps transparent or red; etc...
        ##self.o.paintGL() ######## extend for model tree; but this should be enough for the glpane!
        self.w.update() # update glpane and model tree
        return
        
    def init_gui(self):
        self.w.extrudeDashboard.show()

    # methods related to exiting this mode [bruce 040922 made these from old Done and Flush methods]

##    def haveNontrivialState(self): ### wrong
##        ###
##        return self.o.shape != None # note that this is stored in the glpane, but not in its assembly.
##
##    def StateDone(self): ### wrong
##        if self.o.shape:
##            self.o.assy.molmake(self.o.shape)
##        self.o.shape = None
##        return None
##
##    def StateCancel(self): ### wrong
##        self.o.shape = None
##        # it's mostly a matter of taste whether to put this statement into StateCancel, restore_patches, or clear()...
##        # it probably doesn't matter in effect, in this case. To be safe (e.g. in case of Abandon), I put it in more than one place.
##        return None
    
    def restore_gui(self):
        self.w.extrudeDashboard.hide()

##    def restore_patches(self): ### wrong
##        self.o.shape = None
        
    # other dashboard methods (not yet revised by bruce 040922 ###e)
    
##    def Backup(self): ### wrong
##        if self.o.shape:
##            self.o.shape.undo()
##        self.o.paintGL()

    # mouse events ### wrong -- i should let you drag one of the repeated units; see code in move mode which does similar
    
    def leftDown(self, event):
        pass##self.StartDraw(event, 1)
    
    def leftShiftDown(self, event):
        pass##self.StartDraw(event, 0)

    def leftCntlDown(self, event):
        pass##self.StartDraw(event, 2)

    def leftDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftShiftDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftUp(self, event):
        pass##self.EndDraw(event)
    
    def leftShiftUp(self, event):
        pass##self.EndDraw(event)
    
    def leftCntlUp(self, event):
        pass##self.EndDraw(event)


    def Draw(self): ### wrong
        basicMode.Draw(self) # axes, if displayed
        self.o.assy.draw(self.o) ##### copied from selectMode.draw(). But the code inside this looks pretty weird!!!
   
    def makeMenus(self): ### not yet reviewed for extrude mode
        self.Menu1 = self.makemenu([('Cancel', self.Cancel),
                                    ('Start Over', self.StartOver),
                                    ('Backup', self.Backup),
                                    None,
                                    ('Move', self.move),
                                    ('Copy', self.copy)])
        
        self.Menu2 = self.makemenu([('Kill', self.o.assy.kill),
                                    ('Copy', self.o.assy.copy),
                                    ('Separate', self.o.assy.modifySeparate),
                                    ('Bond', self.o.assy.Bond),
                                    ('Unbond', self.o.assy.Unbond),
                                    ('Stretch', self.o.assy.Stretch)])
        
        self.Menu3 = self.makemenu([('Default', self.w.dispDefault),
                                    ('Lines', self.w.dispLines),
                                    ('CPK', self.w.dispCPK),
                                    ('Tubes', self.w.dispTubes),
                                    ('VdW', self.w.dispVdW),
                                    None,
                                    ('Invisible', self.w.dispInvis),
                                    None,
                                    ('Color', self.w.dispObjectColor)])

    def copy(self):
        print 'NYI'

    def move(self):
        print 'NYI'

    pass # end of class extrudeMode

# ==

# should be a method in assembly:
def assy_copy(assy, mols, offset = V(10.0, 10.0, 10.0)):
    """in assy, copy the mols in the list of mols; return list of new mols.
    The code is modified from pre-041007 assembly.copy [is that code used? correct? it doesn't do anything with nulist].
    But then extended to handle post-041007 by bruce, 041007-08
    Note, as a side effect (of molecule.copy), the new mols are picked and the old mols are unpicked. ####k
    """
    self = assy
    if mols:
        self.modified = 1
        nulist=[]
        for mol in mols[:]: # copy the list in case it happens to be self.selmols (needed??)
            numol=mol.copy(mol.dad,offset)
            nulist += [numol]
            self.addmol(numol)
    return nulist

# should be a method in assembly (maybe there is one like this already??)
def assy_merge_mols(assy, mollist):
    "merge multiple mols in assy into one mol in assy, and return it"
    assert len(mollist) == 1, "can't yet handle general merge"
    return mollist[0]

# this can remain a local function
def assy_extrude_unit(assy):
    """if we can find a good extrude unit in assy,
       make it a molecule in there, and return (True, mol);
       else return (False, whynot).
       Note: we might modify assy even if we return False in the end!!!
       #e Fix that later.
       Best solution: make a nondet version that just returns the flag, for use in refuseEnter. Should be easy enough.
    """
    if assy.selmols:
        assert type(assy.selmols) == type([]) # assumed by this code; always true at the moment
        ###e should merge the selected mols into one? or a group? or use them all each time? for now, require exactly one.
        if len(assy.selmols) > 1:
            print 'assy.selmols is',`assy.selmols` #debug
            return False, "more than one molecule selected (and stub code can't yet merge them)"
        else:
            return True, assy.selmols[0] #e later use assy_merge_mols
    elif assy.selatoms:
        res = []
        def new_old(new, old):
            assert new.atoms
            res.append(new) #e someday we might use old too, eg for undo or for heuristics to help deal with neighbor-atoms...
        assy.modifySeparate(new_old_callback = new_old) # make the selected atoms into their own mols
        assert res, "what happened to all those selected atoms???"
        if len(res) > 1:
            return False, "more than one mol contains selected atoms, and stub code can't yet merge them"
        else:
            return True, res[0] #e later use assy_merge_mols
        #e or for multiple mols, should we do several extrudes in parallel? hmm, might be useful...
    elif len(assy.molecules) == 1:
        # nothing selected, but exactly one molecule in all -- just use it
        return True, assy.molecules[0]
    else:
        print 'assy.molecules is',`assy.molecules` #debug
        return False, "nothing selected, and not exactly one mol in all; stub code gives up" #e someday might merge multiple mols...
    pass

