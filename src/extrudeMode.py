# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
THIS FILE IS PRESENTLY OWNED BY BRUCE -- please don't change it in any way,
however small, unless this is necessary to make Atom work properly for other developers.
[bruce 040921]

$Id$

Stub file for Extrude mode. It's getting less and less identical to cookieMode.

-- bruce 040924/041011
"""

extrude_loop_debug = 0 # do not commit with 1, change back to 0

from platform import *

from modes import *
from qt import QSpinBox, QDoubleValidator

from handles import *
from debug import print_compact_traceback

class FloatSpinBox(QSpinBox):
    "spinbox for a coordinate in angstroms -- permits negatives, floats"
    range_angstroms = 1000.0 # value can go to +- this many angstroms
    precision_angstroms = 100 # with this many detectable units per angstrom
    min_length = 0.1 # prevent problems with 0 or negative lengths provided by user
    max_length = 2 * range_angstroms # longer than possible from max xyz inputs
    def __init__(self, *args, **kws):
        #k why was i not allowed to put 'for_a_length = 0' into this arglist??
        for_a_length = kws.pop('for_a_length',0)
        assert not kws, "keyword arguments are not supported by QSpinBox"
        QSpinBox.__init__(self, *args) #k #e note, if the args can affect the range, we'll mess that up below
        ## self.setValidator(0) # no keystrokes are prevented from being entered
            ## TypeError: argument 1 of QSpinBox.setValidator() has an invalid type -- hmm, manual didn't think so -- try None? #e
        self.setValidator( QDoubleValidator( - self.range_angstroms, self.range_angstroms, 2, self ))
            # QDoubleValidator has a bug: it turns 10.2 into 10.19! But mostly it works. Someday we'll need our own. [bruce 041009]
        if not for_a_length:
            self.setRange( - int(self.range_angstroms * self.precision_angstroms),
                             int(self.range_angstroms * self.precision_angstroms) )
        else:
            self.setRange( int(self.min_length * self.precision_angstroms),
                           int(self.max_length * self.precision_angstroms) )
        self.setSteps( self.precision_angstroms, self.precision_angstroms * 10 ) # set linestep and pagestep
    def mapTextToValue(self):
        text = self.cleanText()
        text = str(text) # since it's a qt string
        ##print "fyi: float spinbox got text %r" % text
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

class TogglePrefCheckBox(QCheckBox):
    def __init__(self, *args, **kws):
        self.sense = kws.pop('sense', True) # whether checking the box makes our value (seen by callers) True or False
        self.default = kws.pop('default', True) # whether our default value (*not* default checked-state) is True or False
        self.tooltip = kws.pop('tooltip', "") # tooltip to show ###e NIM
        # public attributes:
        self.attr = kws.pop('attr', None) # name of mode attribute (if any) which this should set
        self.repaintQ = kws.pop('repaintQ', False) # whether mode might need to repaint if this changes
        assert not kws, "keyword arguments are not supported by QCheckBox"
        QCheckBox.__init__(self, *args)
        #e set tooltip - how? see .py file made from .ui to find out (qt assistant didn't say).
    def value(self):
        if self.isChecked():
            return self.sense
        else:
            return not self.sense
    def setValue(self, bool1):
        if self.sense:
            self.setChecked( bool1)
        else:
            self.setChecked( not bool1)
    def initValue(self):
        self.setValue(self.default)
    pass
        
MAX_NCOPIES = 100 # max number of extrude-unit copies. Should be larger. ####e

# bruce 040920: until MainWindow.ui does the following, I'll do it manually:
# (FYI: I will remove this, and the call to this, after MainWindowUI does the same stuff.
#  But first I will be editing this function a lot to get the dashboard contents that I need.)
def do_what_MainWindowUI_should_do(self):
    "self should be the main MWSemantics object -- at the moment this is a function, not a method"

    ##print "extrude debug: do_what_MainWindowUI_should_do"

    from qt import SIGNAL, QToolBar, QLabel, QLineEdit, QSpinBox

    # 2. make a toolbar to be our dashboard, similar to the cookieCutterToolbar
    # (based on the code for cookieCutterToolbar in MainWindowUI)

    self.extrudeDashboard = QToolBar(QString(""),self,Qt.DockBottom)
    self.extrudeToolbar = self.extrudeDashboard # bruce 041007 so I don't have to rename this in MWsemantics.py yet

    self.extrudeDashboard.setGeometry(QRect(0,0,515,29)) ### will probably be wrong once we modify the contents
    self.extrudeDashboard.setBackgroundOrigin(QToolBar.WidgetOrigin)

    self.textLabel_extrude_toolbar = QLabel(self.extrudeDashboard,"textLabel_extrude_toolbar")
    # below was "Extrude Mode", in two places in the file ########
    self.textLabel_extrude_toolbar.setText(self._MainWindow__tr("Extrude")) # see note below about __tr

    self.extrudeDashboard.addSeparator()

    # make it convenient to revise nested vbox, hbox structures for the UI
    where = [self.extrudeDashboard]
    def parent_now():
        "put things inside this instead of self.extrudeDashboard"
        return where[-1]
    def begin(thing): # start a QVBox or QHBox
        box = thing(parent_now())
        where.append(box)
        return 1 # so you can say "if begin(): ..." if you want to use python indentation
    def end():
        where.pop()
    
    def insertlabel(text):
        label = QLabel(parent_now(), "extrude_label_"+text.strip()) # [parent, name
        label.setText(self._MainWindow__tr(text)) # initial text
        return label # caller doesn't usually need this, except to vary the text

    insertlabel(" N ")
    self.extrudeSpinBox_n = QSpinBox(self.extrudeDashboard, "extrudeSpinBox_n")
    self.extrudeSpinBox_n.setRange(1,MAX_NCOPIES)
    self.extrudeDashboard.addSeparator()

    if begin(QVBox):
        if begin(QHBox):
            insertlabel(" X ") # number of spaces is intentionally different on different labels
            self.extrudeSpinBox_x = FloatSpinBox(parent_now(), "extrudeSpinBox_x")
        end()
        if begin(QHBox):
            insertlabel(" Z ")
            self.extrudeSpinBox_z = FloatSpinBox(parent_now(), "extrudeSpinBox_z")
        end()
    end()
    if begin(QVBox):
        if begin(QHBox):
            insertlabel("      Y ")
            self.extrudeSpinBox_y = FloatSpinBox(parent_now(), "extrudeSpinBox_y")
        end()
        if begin(QHBox):
            insertlabel(" length ") # units?
            self.extrudeSpinBox_length = FloatSpinBox(parent_now(), "extrudeSpinBox_length", for_a_length = 1)
        end()
    end()

    self.extrudeDashboard.addSeparator()

    # == prefs things, don't work on reload if at end, don't know why

    if begin(QVBox):
        if begin(QHBox):
            insertlabel("show: ")
            # these have keyword args of sense (dflt True), in case you
            # rename them in a way which inverts meaning of True/False,
            # and default, to specify the initial value of the program
            # value (not nec. that of the checkbox, if sense = False!).
            self.extrudePref1 = TogglePrefCheckBox("whole model", parent_now(), "extrudePref1",
                                                   default = False, attr = 'show_whole_model', repaintQ = True )
            self.extrudePref2 = TogglePrefCheckBox("bond-offset spheres", parent_now(), "extrudePref2",
                                                   default = True,  attr = 'show_bond_offsets', repaintQ = True )
        end()
        if begin(QHBox):
            insertlabel("when done: ")
            # these only affect what we do at the end -- no repaint needed
            self.extrudePref3 = TogglePrefCheckBox("all one part", parent_now(), "extrudePref3", attr = 'whendone_all_one_part')
            self.extrudePref4 = TogglePrefCheckBox("relax bonds", parent_now(), "extrudePref4", attr = 'whendone_relax_bonds')
        end()
    end()

#e smaller font? how?
#e tooltips?

##        if begin(QHBox):
##            if begin(QVBox):
##                self.extrudePref1 = QCheckBox("show whole model,", parent_now(), "extrudePref1")
##                self.extrudePref2 = QCheckBox("bond-offset spheres", parent_now(), "extrudePref2") 
##            end()
##            if begin(QVBox):
##                self.extrudePref3 = QCheckBox("one mol. when done", parent_now(), "extrudePref3")
##                self.extrudePref4 = QCheckBox("relax bonds when done", parent_now(), "extrudePref4")
##            end()
##        end()

##        self.extrudePref2.setChecked(False)
##        self.extrudePref3.setChecked(True)
##        print "self.extrudePref2.isChecked()",self.extrudePref2.isChecked()
##        print "self.extrudePref3.isChecked()",self.extrudePref3.isChecked()
        
    self.extrudeDashboard.addSeparator()

    if begin(QVBox):
        global lambda_tol_nbonds
        lbl = insertlabel(lambda_tol_nbonds(1.0,-1)) # text changed later
        self.extrudeBondCriterionLabel = lbl
        self.extrudeBondCriterionLabel_lambda_tol_nbonds = lambda_tol_nbonds
        self.extrudeBondCriterionSlider_dflt = dflt = 100
        # int minValue, int maxValue, int pageStep, int value, orientation, parent, name:
        self.extrudeBondCriterionSlider = QSlider(0,300,5,dflt,Qt.Horizontal,parent_now()) # 100 = the built-in criterion
    end()
    ##lbl = insertlabel("<nnn>") # display of number of bonds, not editable
    ##self.extrudeBondCriterion_ResLabel = lbl

    self.extrudeDashboard.addSeparator()
    
    # == dashboard tools shared with other modes [did not test removing these wrt missing things at end bug, since exc caused]
    self.toolsBackUpAction.addTo(self.extrudeDashboard) #e want this??
    self.toolsStartOverAction.addTo(self.extrudeDashboard)
    self.toolsDoneAction.addTo(self.extrudeDashboard)
    self.toolsCancelAction.addTo(self.extrudeDashboard)

    # note: python name-mangling would turn __tr, within class MainWindow, into _MainWindow__tr (I think... seems to be right)
    self.extrudeDashboard.setLabel(self._MainWindow__tr("Extrude")) # "Extrude Mode" was wider than I liked... space is tight

    # stuff *after* the dashboard... make it on the right? prefs settings. experimental.
    # QCheckBox::QCheckBox ( const QString & text, QWidget * parent, const char * name = 0 )

    ##print "extrude debug: do_what_MainWindowUI_should_do 3"

    # slider (& all else) failed to appear when it was created here, don't know why
    
    # fyi: caller hides the toolbar, we don't need to

    reinit_extrude_controls(self) # moved to end, will that fix the reload issues??
    
    return

def lambda_tol_nbonds(tol, nbonds):
    if nbonds == -1:
        nbonds_str = "?"
    else:
        nbonds_str = "%d" % (nbonds,)
    tol_str = ("      %d" % int(tol*100.0))[-3:]
    # fixed-width (3 digits) but using initial spaces
    # (doesn't have all of desired effect, due to non-fixed-width font)
    tol_str = tol_str + "%"
    return "tolerance: %s => %s bonds" % (tol_str,nbonds_str)

import math

def reinit_extrude_controls(win, glpane = None, length = None, attr_target = None):
    "reinitialize the extrude controls; used whenever we enter the mode; win should be the main window (MWSemantics object)"
    self = win
    self.extrudeSpinBox_n.setValue(3)
    x,y,z = 5,5,5 # default dir in modelspace, to be used as a last resort
    if glpane:
        # use it to set direction
        try:
            right = glpane.right
            x,y,z = right # use default direction fixed in eyespace
            if not length:
                length = 7.0 ######e needed?
        except:
            print "fyi (bug?): in extrude: x,y,z = glpane.right failed"
            pass
    if length:
        # adjust the length to what the caller desires
        #######, based on the extrude unit (if provided); we'll want to do this more sophisticatedly (??)
        ##length = 7.0 ######
        ll = math.sqrt(x*x + y*y + z*z) # should always be positive, due to above code
        rr = float(length) / ll
        x,y,z = (x * rr, y * rr, z * rr)
    set_extrude_controls_xyz(win, (x,y,z))
    self.extrude_pref_toggles = [self.extrudePref1, self.extrudePref2, self.extrudePref3, self.extrudePref4]
    for toggle in self.extrude_pref_toggles:
        if attr_target and toggle.attr: # do this first, so the attrs needed by the slot functions are there
            setattr(attr_target, toggle.attr, toggle.default) # this is the only place I initialize those attrs!
    for toggle in self.extrude_pref_toggles:
        ##toggle.setChecked(True) ##### stub; change to use its sense & default if it has one -- via a method on it
        toggle.initValue() # this might call the slot function!

    #e bonding-slider, and its label, showing tolerance, and # of bonds we'd make at current offset
    tol = self.extrudeBondCriterionSlider_dflt / 100.0
    set_bond_tolerance_and_number_display( win, tol)
    set_bond_tolerance_slider( win, tol)
    ### bug: at least after the reload menu item, reentering mode did not reinit slider to 100%. don't know why.
    return

def set_bond_tolerance_and_number_display(win, tol, nbonds = -1): #e -1 indicates not yet known ###e '?' would look nicer
    self = win
    lambda_tol_nbonds = self.extrudeBondCriterionLabel_lambda_tol_nbonds
    self.extrudeBondCriterionLabel.setText(lambda_tol_nbonds(tol,nbonds))
    
def set_bond_tolerance_slider(win, tol):
    self = win
    self.extrudeBondCriterionSlider.setValue(int(tol * 100)) # this will send signals!
    
def get_bond_tolerance_slider_val(win):
    self = win
    ival = self.extrudeBondCriterionSlider.value()
    return ival / 100.0
    
def set_extrude_controls_xyz_nolength(win, (x,y,z) ):
    self = win
    self.extrudeSpinBox_x.setFloatValue(x)
    self.extrudeSpinBox_y.setFloatValue(y)
    self.extrudeSpinBox_z.setFloatValue(z)

def set_extrude_controls_xyz(win, (x,y,z) ):
    set_extrude_controls_xyz_nolength( win, (x,y,z) )
    update_length_control_from_xyz(win)

def get_extrude_controls_xyz(win):
    self = win
    x = self.extrudeSpinBox_x.floatValue()
    y = self.extrudeSpinBox_y.floatValue()
    z = self.extrudeSpinBox_z.floatValue()
    return (x,y,z)

suppress_valuechanged = 0

def call_while_suppressing_valuechanged(func):
    global suppress_valuechanged
    old_suppress_valuechanged = suppress_valuechanged
    suppress_valuechanged = 1
    try:
        res = func()
    finally:
        suppress_valuechanged = old_suppress_valuechanged
    return res

def update_length_control_from_xyz(win):
    x,y,z = get_extrude_controls_xyz(win)
    ll = math.sqrt(x*x + y*y + z*z)
    if ll < 0.1: # prevent ZeroDivisionError
        set_controls_minimal(win)
        return
    self = win
    call_while_suppressing_valuechanged( lambda: self.extrudeSpinBox_length.setFloatValue(ll) )
    
def update_xyz_controls_from_length(win):
    x,y,z = get_extrude_controls_xyz(win)
    ll = math.sqrt(x*x + y*y + z*z)
    if ll < 0.1: # prevent ZeroDivisionError
        set_controls_minimal(win)
        return
    length = self.extrudeSpinBox_length.floatValue()
    rr = float(length) / ll
    call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz_nolength( win, (x * rr, y * rr, z * rr) ) )

def set_controls_minimal(win): #e would be better to try harder to preserve xyz ratio
    ll = 0.1 # kluge, but prevents ZeroDivisionError
    x = y = 0.0
    z = ll
    self = win
    call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz_nolength( win, (x, y, z) ) )
    call_while_suppressing_valuechanged( lambda: self.extrudeSpinBox_length.setFloatValue(ll) )
    ### obs comment?: this is not working as I expected, but it does seem to prevent that
    # ZeroDivisionError after user sets xyz each to 0 by typing in them

# ==

class extrudeMode(basicMode):

    # class constants
    backgroundColor = 200/256.0, 100/256.0, 100/256.0 # different than in cookieMode
    modename = 'EXTRUDE'
    default_mode_status_text = "Mode: Extrude"
    keeppicked = 0 # whether to keep the units all picked, or all unpicked, during the mode

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

        for toggle in self.w.extrude_pref_toggles:
            self.w.connect(toggle, SIGNAL("stateChanged(int)"), self.toggle_value_changed)

        slider = self.w.extrudeBondCriterionSlider
        self.w.connect(slider, SIGNAL("valueChanged(int)"), self.slider_value_changed)
        return

    bond_tolerance = -1.0 # initial value can't agree with slider
    def slider_value_changed(self):
        if not self.now_using_this_mode_object():
            return
        old = self.bond_tolerance
        new = get_bond_tolerance_slider_val(self.w)
        if new != old:
            self.needs_repaint = 1 # almost certain, from bond-offset spheres and/or bondable singlet colors
            self.bond_tolerance = new
            # one of the hsets has a radius_multiplier which must be patched to self.bond_tolerance
            # (kluge? not compared to what I was doing a few minutes ago...)
            try:
                hset = self.nice_offsets_handleset
            except AttributeError:
                print "must be too early to patch self.nice_offsets_handleset -- could be a problem, it will miss this event #####" #######@@@
            else:
                hset.radius_multiplier = self.bond_tolerance
            set_bond_tolerance_and_number_display(self.w, self.bond_tolerance) # number of resulting bonds not yet known, will be set later
            self.recompute_bonds() # re-updates set_bond_tolerance_and_number_display when done
            self.repaint_if_needed() ##e merge with self.update_offset_bonds_display, call that instead?? no need for now.
        return
            
    def toggle_value_changed(self):
        if not self.now_using_this_mode_object():
            return
        self.needs_repaint = 0
        for toggle in self.w.extrude_pref_toggles:
            val = toggle.value()
            attr = toggle.attr
            repaintQ = toggle.repaintQ
            if attr:
                old = getattr(self,attr,val)
                if old != val:
                    setattr(self, attr, val)
                    if repaintQ:
                        self.needs_repaint = 1
            else:
                # bad but tolerable: a toggle with no attr, but repaintQ,
                # forces repaint even when some *other* toggle changes!
                # (since we don't bother to figure out whether it changed)
                if repaintQ:
                    self.needs_repaint = 1
                    print "shouldn't happen in current code - needless repaint"
            pass
        self.repaint_if_needed()
        ##print "self.w.extrudePref1.isChecked() = %r" % self.w.extrudePref1.isChecked()

    def now_using_this_mode_object(self): ###e refile this in modes.py basicMode?
        "return true if the glpane is presently using this mode object (not just a mode object with the same name!)"
        return self.o.mode == self ###k 041009
        
    def Enter(self):
        self.status_msg("entering extrude mode...")
          # this msg won't last long enough to be seen, if all goes well
        self.clear() ##e see comment there
        reinit_extrude_controls(self.w, self.o, length = 7.0, attr_target = self)
        basicMode.Enter(self)
        assy = self.o.assy
        self.assy = assy #k i assume this never changes during one use of this mode!

        ###
        # find out what's selected, which if ok will be the repeating unit we will extrude... explore its atoms, bonds, externs...
        # what's selected should be its own molecule if it isn't already...
        # for now let's hope it is exactly one (was checked in refuseEnter, but not anymore).

        ok, mol = assy_extrude_unit(self.assy)
        if not ok:
            whynot = mol
            #e show the reason why not in a dialog??
            self.status_msg("extrude mode refused: %r" % (whynot,)) #e improve
            return 1 # refused!
        self.basemol = mol
        mark_singlets(self.basemol, self.colorfunc)
        offset = V(15.0,16.0,17.0) # initial value doesn't matter
        self.offset = offset
        
        self.ncopies = 1
        #obs comment?? might not be true if we reenter the mode with one copy selected! ignore that issue for now.
        # note, nothing makes sure the new mol is visible in the window except keeping ncopies small!!
        # now see if we can copy it, moved over a bit, and add that to the assembly

        self.molcopies = [self.basemol] # if we have any potential mols to show dimly, they are not in here
        #e we might optimize by not creating these molcopies, only displaying them, but i ignore this issue for now

        ######e these exceptions not preventing Enter are just to help me debug it -- remove the 'try', later
        try:
            self.recompute_for_new_unit() # recomputes whatever depends on self.basemol
        except:
            print_compact_traceback("in Enter, exception in recompute_for_new_unit (entering anyway!!): ")
        self.recompute_for_new_bend() # ... and whatever depends on the bend from each repunit to the next (varies only in Revolve)

        self.connect_controls()
        try:
            self.update_from_controls()
        except:
            print_compact_traceback("in Enter, exception in update_from_controls (entering anyway!!): ")

        
        import __main__
        __main__.mode = self

        
        print "fyi: extrude debug instructions: __main__.mode = this extrude mode obj; use debug window; has members assy, etc"
        print "also, use Menu1 entries to run debug code, like explore() to check out singlet pairs in self.basemol"

    singlet_color = {}
    def colorfunc(self, atom): # uses a hack in chem.py atom.draw to use mol.colorfunc
        return self.singlet_color.get(atom.info) # ok if this is None

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
            ##print "fyi: not now_using_this_mode_object" # this happens when you leave and reenter mode... need to break qt connections
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
            ##print "fyi: not now_using_this_mode_object"
            return
        update_xyz_controls_from_length(self.w)
        self.update_from_controls()

    should_update_model_tree = 0 # avoid doing this when we don't need to (like during a drag)
    
    def update_from_controls(self):
        """make the number and position of the copies of basemol what they should be, based on current control values.
        Never modify the control values! (That would infloop.)
        This should be called in Enter and whenever relevant controls might change.
        It's also called during a mousedrag event if the user is dragging one of the repeated units.
        """
        self.asserts()
        
        # get control values
        want_n = self.w.extrudeSpinBox_n.value()
        (want_x, want_y, want_z) = get_extrude_controls_xyz(self.w)
        ncopies_wanted = want_n
        ncopies_wanted = min(20,ncopies_wanted) # low upper limit, for safety, for now ### even less than MAX_NCOPIES
        ncopies_wanted = max(1,ncopies_wanted) # always at least one copy ###e fix spinbox's value too?? also think about it on exit...
        if ncopies_wanted != want_n:
            print "fyi, ncopies_wanted is limited to safe value %r, not your requested value %r" % (ncopies_wanted, want_n)

        offset_wanted = V(want_x, want_y, want_z) # (what are the offset units btw? i guess angstroms, but verify #k)

        # update the state:
        # first move the copies in common, if offset changed
        ncopies_common = min(ncopies_wanted,self.ncopies)
        if offset_wanted != self.offset:
            ####### clear all memoized data which is specific to the offset, like which singlets you might join
            self.have_offset_specific_data = 0 # this just invalidates it
            for ii in range(ncopies_common):
                if ii:
                    motion = (offset_wanted - self.offset)*ii
                    self.molcopies[ii].move(motion) #### does this change picked state????
                    ####### we might accumulate position errors if we do it this way!   ########## ###@@@ set from basemol pos
            self.offset = offset_wanted
        # now delete or make copies as needed (but don't adjust view until the end)
        while self.ncopies > ncopies_wanted:
            # delete a copy we no longer want
            self.should_update_model_tree = 1
            ii = self.ncopies - 1
            self.ncopies = ii
            old = self.molcopies.pop(ii)
            old.unpick() # work around a bug in assy.killmol [041009] ##### that's fixed now -- verify, and remove this
            self.assy.killmol(old)
            self.asserts()
        while self.ncopies < ncopies_wanted:
            # make a new copy we now want
            self.should_update_model_tree = 1
            #e the fact that it shows up immediately in model tree would permit user to change its color, etc;
            #e but we'll probably want to figure out a decent name for it, make a special group to put these in, etc
            ii = self.ncopies
            self.ncopies = ii + 1
            newmols = assy_copy(self.assy, [self.basemol], offset = self.offset * ii)
            new = newmols[0]
            if self.keeppicked:
                pass ## done later: self.basemol.pick()
            else:
                ## self.basemol.unpick()
                new.unpick() # undo side effect of assy_copy
            self.molcopies.append(new)
            self.asserts()
        if self.keeppicked:
            self.basemol.pick() #041009 undo an unwanted side effect of assy_copy (probably won't matter, eventually)
        else:
            self.basemol.unpick() # do this even if no copies made (matters e.g. when entering the mode)

        ###@@@ now this looks like a general update function... hmm

        self.needs_repaint = 1 # assume this is always true, due to what calls us
        self.update_offset_bonds_display()

    def update_offset_bonds_display(self):
        # should be the last function called by some user event method (??)... not sure if it always is! some weird uses of it...
        "update whatever is needed of the offset_specific_data, the bonds, and the display itself"
        ###### now, if needed, recompute (or start recomputing) the offset-specific data
        #####e worry about whether to do this with every mousedrag event... or less often if it takes too long
        ##### but ideally we do it, so as to show bonding that would happen at current offset
        if not self.have_offset_specific_data:
            self.have_offset_specific_data = 1 # even if the following has an exception
            try:
                self.recompute_offset_specific_data()
            except:
                print_compact_traceback("error in recompute_offset_specific_data: ")
                return # no more updates #### should just raise, once callers cleaner
            pass
        #obs comment in this loc?
        #e now we'd adjust view, or make drawing show if stuff is out of view; make atom overlaps transparent or red; etc...

        # now update bonds (needed by most callers (not ncopies change!), so don't bother to have an invalid flag, for now...)
        if 1:
            self.recompute_bonds() # sets self.needs_repaint if bonds change; actually updates bond-specific ui displays
        
        # update model tree and/or glpane, as needed
        if self.should_update_model_tree:
            self.should_update_model_tree = 0 # reset first, so crashing calls are not redone
            self.needs_repaint = 0
            self.w.update() # update glpane and model tree
        elif self.needs_repaint: ###### merge with self.repaint_if_needed() #######@@@
            self.needs_repaint = 0
            self.o.paintGL() # just update glpane
        return

    # ==

    # These methods recompute things that depend on other things named in the methodname.
    # call them in the right order (this order) and at the right time.
    # If for some of them, we should only invalidate and not recompute until later (eg on buttonpress),
    # I did not yet decide how that will work.

    def recompute_for_new_unit(self):
        "recompute things which depend on the choice of rep unit (for now we use self.basemol to hold that)"
        # for now we use self.basemol,
        #e but later we might not split it from a larger mol, but have a separate mol for it

        # these are redundant, do we need them?
        self.have_offset_specific_data = 0
        self.bonds_for_current_offset_and_tol = (17,)
        
        self.show_bond_offsets_handlesets = [] # for now, assume no other function wants to keep things in this list
        hset = self.basemol_atoms_handleset = repunitHandleSet(target = self)
        for atom in self.basemol.atoms.itervalues():
            # make a handle for it... to use in every copy we show
            pos = atom.posn() ###e make this relative?
            dispdef = molecule_dispdef(self.basemol, self.o)
            disp, radius = atom.howdraw(dispdef)
            info = None #####
            hset.addHandle(pos, radius, info)
        self.basemol_singlets = mol_singlets(self.basemol)
        hset = self.nice_offsets_handleset = niceoffsetsHandleSet(target = self)
        hset.radius_multiplier = abs(self.bond_tolerance) # kluge -- might be -1 or 1 initially! (sorry, i'm in a hurry)
          # note: hset is used to test offsets via self.nice_offsets_handleset,
          # but is drawn and click-tested due to being in self.show_bond_offsets_handlesets
        # make a handle just for dragging self.nice_offsets_handleset
        hset2 = self.nice_offsets_handle = draggableHandle_HandleSet( \
                    motion_callback = self.nice_offsets_handleset.move ,
                    statusmsg = "use purple center to drag the clickable suggested-offset display"
                )
        hset2.addHandle( V(0,0,0), 0.66, None)
        hset2.addHandle( self.offset, 0.17, None) # kluge: will be kept patched with current offset
        self.show_bond_offsets_handlesets.extend([hset,hset2])
           # (use of this list is conditioned on self.show_bond_offsets)
        ##e quadratic, slow alg; should worry about too many singlets
        # (rewritten from the obs functions explore, bondable_singlet_pairs_proto1)
        # note: this code will later be split out, and should not assume mol1 == mol2.
        # (but it does, see comments)
        mergeables = self.mergeables = {}
        sings1 = sings2 = self.basemol_singlets
        for i1 in range(len(sings1)):
            self.status_msg("scanning all pairs of open bonds... %d/%d done" % (i1, len(sings1)) ,
                             suppress_rapidfire_repeats = "scanning all pairs"
                            ) # this is our slowness warning
            ##e should correct that message for effect of i2 < i1 optim, by reporting better numbers...
            for i2 in range(len(sings2)):
                if i2 < i1:
                    continue # results are negative of swapped i1,i2, SINCE MOLS ARE THE SAME
                    # this order makes the slowness warning conservative... ie progress seems to speed up at the end
                    ### warning: this optim is only correct when mol1 == mol2
                    # and (i think) when there is no "bend" relating them.
                # (but for i1 == i2 we do the calc -- no guarantee mol1 is identical to mol2.)
                s1 = sings1[i1]
                s2 = sings2[i2]
                (ok, ideal, err) = mergeable_singlets_Q_and_offset(s1, s2)
                if extrude_loop_debug:
                    print "extrude loop %d, %d got %r" % (i1, i2, (ok, ideal, err))
                if ok:
                    mergeables[(i1,i2)] = (ideal, err)
        print "extrude fyi: len(mergeables) = %d" % len(mergeables)
        #e self.mergeables is in an obs format... but we still use it to look up (i1,i2) or their swapped form
        msg = "scanned %d open-bond pairs..." % ( len(sings1) * len(sings2) ,) # longer msg below
        self.status_msg(msg)
        # make handles from mergeables
        for (i1,i2),(ideal,err) in mergeables.items():
            pos = ideal
            radius == err
            info = (i1,i2)
            hset.addHandle(pos, radius, info)
            if i2 != i1:
                # correct for optimization above
                pos = -pos
                info = (i2,i1)
                hset.addHandle(pos, radius, info)
            else:
                print "fyi: singlet %d is mergeable with itself (should never happen for extrude; ok for revolve)" % i1
            # handle has dual purposes: click to change the offset to the ideal,
            # or find (i1,i2) from an offset inside the (pos, radius) ball.
        msg = "scanned %d open-bond pairs; %d pairs could bond at some offset (as shown by bond-offset spheres)" % \
              ( len(sings1) * len(sings2) , len(hset.handles) )
        self.status_msg(msg)
        return
    
    def recompute_for_new_bend(self):
        "recompute things which depend on the choice of bend between units (for revolve)"
        ##print "recompute_for_new_bend(): pass" ######
        pass

    have_offset_specific_data = 0 # we do this in clear() too

    def recompute_offset_specific_data(self):
        "#doc"
        # kluge:
        try:
            hset2 = self.nice_offsets_handle
            hset2.handle_setpos( 1, self.offset )
        except:
            print "fyi: hset2 kluge failed" ###
        # don't call recompute_bonds, our callers do that if nec.
        return 

    bonds_for_current_offset_and_tol = (17,) # we do this in clear() too
    def recompute_bonds(self):
        # recompute what singlets to show in diff color, what bonds to make...
        # call when offset or tol changes
        
        # basic idea: see which nice-offset-handles contain the offset, count them, and recolor singlets they come from.
        hset = self.nice_offsets_handleset #e revise this code if we cluster these, esp. if we change their radius
        hh = hset.findHandles_containing(self.offset)
            # semi-kluge: this takes into account self.bond_tolerance, since it was patched into hset.radius_multiplier
        # kluge for comparing it with prior value; depends on order stability of handleset, etc
        hh = tuple(hh)
        if hh != self.bonds_for_current_offset_and_tol:
            self.needs_repaint = 1 # usually true at this point
            ##msg = "new set of %d nice bonds: %r" % (len(hh), hh)
            ##print msg ## self.status_msg(msg) -- don't obscure the scan msg yet #######
            self.bonds_for_current_offset_and_tol = hh
            # change singlet color dict(??) for i1,i2 in ..., proc(i1, col1), proc(i2,col2)...
            self.singlet_color = {}
            for mol in self.molcopies:
                mol.changeapp()
                ##e if color should vary with bond closeness, we'd need changeapp for every offset change;
                # then for speed, we'd want to repeatedly draw one mol, not copies like now
                # (maybe we'd like to do that anyway).
            for (pos,radius,info) in hh:
                i1,i2 = info
                ####stub; we need to worry about repeated instances of the same one (as same of i1,i2 or not)
                def doit(ii, color):
                    basemol_singlet = self.basemol_singlets[ii]
                    mark = basemol_singlet.info
                    self.singlet_color[mark] = color # when we draw atoms, somehow they find self.singlet_color and use it...
                doit(i1, blue)
                doit(i2, green)
                ###e now how do we make that affect the look of the base and rep units? patch atom.draw?
                # but as we draw the atom, do we look up itskey? is that the same in the mol.copy??
        nbonds = len(hh)
        set_bond_tolerance_and_number_display(self.w, self.bond_tolerance, nbonds)
        #e repaint, or let caller do that (perhaps aftermore changes)? latter - only repaint at end of highest event funcs.
        return
    
    # == this belongs higher up...
    
    def init_gui(self):
        self.o.setCursor(QCursor(Qt.ArrowCursor)) #bruce 041011 copying a change from cookieMode, choice of cursor not reviewed ###
        self.w.toolsExtrudeAction.setOn(1) # make the Extrude tool icon look pressed (and the others not)
        self.w.extrudeDashboard.show()

    # methods related to exiting this mode [bruce 040922 made these from old Done and Flush methods]

    def haveNontrivialState(self):
        return self.ncopies != 1 # more or less...

    def StateDone(self):
        for mol in self.molcopies:
            try:
                del mol.colorfunc
                mol.changeapp()
            except:
                pass
        self.status_msg("extrude warning: bonding/merging of product (%d units) not yet implemented" % len(self.molcopies) )
        ###e make bonds if not yet done, merge base and rep units,
        # merge base back into its fragmented ancestral molecule...
        return None

    def StateCancel(self):
        self.w.extrudeSpinBox_n.setValue(1)
        self.update_from_controls()
        return self.StateDone() # closest we can come to cancelling
    
    def restore_gui(self):
        self.w.extrudeDashboard.hide()    

    # mouse events ### wrong -- i should let you drag one of the repeated units; see code in move mode which does similar

    def leftDown(self, event):
        """Move the touched repunit object, or handle (if any), in the plane of
        the screen following the mouse, or in some other way appropriate to
        the object.
        """
        ####e Also highlight the object? (maybe even do that on mouseover ####) use bareMotion
        self.o.SaveMouse(event) # saves in self.o.MousePos, used in leftDrag
        thing = self.dragging_this = self.touchedThing(event)
        if thing:
            self.dragged_offset = self.offset
            # fyi: leftDrag directly changes only self.dragged_offset;
            # then recompute from controls (sp?) compares that to self.offset, changes that
            msg = thing.leftDown_status_msg()
            if not msg:
                msg = "touched %s" % (thing,)
            self.status_msg(msg)
            self.needs_repaint = 1 # for now, guess that this is always true (tho it's only usually true)
            thing.click() # click handle in appropriate way for its type (#e in future do only on some mouseups)
            self.repaint_if_needed() # (sometimes the click method already did the repaint, so this doesn't)
        return

    _last_status_text = ""
    _last_status_now = ""
    _last_status_counter = 0
    def status_msg(self, text, suppress_rapidfire_repeats = None):
        import time
        now = time.asctime()
        suppress_print = 0
        if suppress_rapidfire_repeats:
            # consider not printing it (or using \r rather than \n??), but always put it into the statusbar!
            if self._last_status_text.startswith(suppress_rapidfire_repeats) and self._last_status_now == now:
                suppress_print = 1
            self._last_status_text = text
            self._last_status_now = now
        else:
            self._last_status_text = "" # only compress when they are adjacent
        if not suppress_print:
            if self._last_status_counter:
##                sys.stdout.write("\n") # \n after 1 or more "."s #### right place? need flush?
##                sys.stdout.flush() #### this is still not coming out soon enough -- why? never mind for now ##########
                self._last_status_counter = 0 #### wrong place
            print "statusbar: %r:" % now, text
        else:
            if 0: #### experiment -- didn't work
                print "statusbar: %r: " % now, text.replace('\n','\r')
            else:
                if not self._last_status_counter:
                    ## sys.stdout.write("statusbar: %r: %s... -- suppressing repeated msgs" % (now, suppress_rapidfire_repeats))
                    print "statusbar: %r: %s... -- suppressing repeated msgs at same time" % (now, suppress_rapidfire_repeats)
                self._last_status_counter = self._last_status_counter + 1
##                sys.stdout.write(".")
##                sys.stdout.flush()
        assert type(text) in [type(""), type(u"")] # only after we print it...
        self.w.msgbarLabel.setText(text)

    show_bond_offsets_handlesets = [] # (default value) the handlesets to be visible iff self.show_bond_offsets
    
    def touchedThing(self, event):
        "return None or the thing touched by this event"
        p1, p2 = self.o.mousepoints(event) # (no side effect. p1 is just beyond near clipping plane; p2 in center of view plane)
        ##print "touchedthing for p1 = %r, p2 = %r" % (p1,p2)
        res = [] # (dist, handle) pairs, arb. order, but only the frontmost one from each handleset
        if self.show_bond_offsets:
            for hset in self.show_bond_offsets_handlesets:
                dh = hset.frontDistHandle(p1, p2) # dh = (dist, handle)  #######@@@ needs to use bond_tolerance, or get patched
                if dh:
                    res.append(dh)
        #e scan other handlesets here, if we have any
        #e now try molecules (if we have not coded them as their own handlesets too) -- only the base and rep units for now
        hset = self.basemol_atoms_handleset
        for ii in range(self.ncopies):
            ##print "try touch",ii
            offset = self.offset * ii
            dh = hset.frontDistHandle(p1, p2, offset = offset, copy_id = ii)
            if dh:
                res.append(dh) #e dh's handle contains copy_id, a code for which repunit
        if res:
            res.sort()
            dh = res[0]
            handle = dh[1]
            ##print "touched %r" % (handle,)
            return handle
        return None

    def leftDrag(self, event):
        """Move the touched objects as determined by leftDown(). ###doc
        """
        if self.dragging_this:
            self.doDrag(event, self.dragging_this)

    needs_repaint = 0
    def doDrag(self, event, thing):
        """drag thing, to new position in event.
        thing might be a handle (pos,radius,info) or something else... #doc
        """
        # determine motion to apply to thing being dragged. Current code is taken from modifyMode.
        # bruce question -- isn't this only right in central plane?
        # if so, we could fix it by using mousepoints() again.
        w=self.o.width+0.0
        h=self.o.height+0.0
        deltaMouse = V(event.pos().x() - self.o.MousePos[0],
                       self.o.MousePos[1] - event.pos().y(), 0.0)
        move = self.o.quat.unrot(self.o.scale * deltaMouse/(h*0.5))
        
        self.o.SaveMouse(event) # sets MousePos, for next time

        self.needs_repaint = 1 # for now, guess that this is always true (tho it's only usually true)
        thing.move(move) # move handle in the appropriate way for its type
          #e this needs to set self.needs_repaint = 1 if it changes any visible thing!
          ##### how does it know?? ... so for now we always set it *before* calling;
          # that way a repaint during the call can reset the flag.
        ## was: self.o.assy.movesel(move)
        self.repaint_if_needed()
    
    def repaint_if_needed(self): # see also the end of update_offset_bonds_display -- we're inlined ######fix
        if self.needs_repaint:
            self.needs_repaint = 0
            self.o.paintGL()
        return
    
    def drag_repunit(self, copy_id, motion):
        "drag a repeat unit (copy_id > 0) or the base unit (id 0)"
        assert type(copy_id) == type(1) and copy_id >= 0
        if copy_id:
            # move repunit #copy_id by motion
            # compute desired motion for the offset which would give this motion to the repunit
            # bug note -- the code that supplies motion to us is wrong, for planes far from central plane -- fix later.
            motion = motion * (1.0 / copy_id)
            # store it, but not in self.offset, that's reserved for comparison with the last value from the controls
            self.dragged_offset = self.dragged_offset + motion
            #obs comment?? i forget what it meant: #e recompute_for_new_offset
            self.force_offset_and_update( self.dragged_offset)
        else:
            pass##print "dragging base unit moves entire model (not yet implemented)"
        return

    def force_offset_and_update(self, offset):
        "change the controls to reflect offset, then update from the controls"
        x,y,z = offset
        call_while_suppressing_valuechanged( lambda: set_extrude_controls_xyz( self.w, (x, y, z) ) )
        #e worry about too-low resolution of those spinbox numbers? at least not in self.dragged_offset...
        #e status bar msg? no, caller can do it if they want to.
        self.update_from_controls() # this does a repaint at the end (at least if the offset in the controls changed)
        
    def click_nice_offset_handle(self, handle):
        (pos,radius,info) = handle
        i1,i2 = info
        try:
            ideal, err = self.mergeables[(i1,i2)]
        except KeyError:
            ideal, err = self.mergeables[(i2,i1)]
            ideal = -1 * ideal
        self.force_offset_and_update( ideal)
    
    def leftUp(self, event):
        if self.dragging_this:
            ## self.doDrag(event, self.dragging_this) ## good idea? not sure. probably not.
            self.dragging_this = None
            #####e update, now that we know the final position of the dragged thing
            del self.dragged_offset
        return
    
    #==
    
    def leftShiftDown(self, event):
        pass##self.StartDraw(event, 0)

    def leftCntlDown(self, event):
        pass##self.StartDraw(event, 2)

    def leftShiftDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftCntlDrag(self, event):
        pass##self.ContinDraw(event)
    
    def leftShiftUp(self, event):
        pass##self.EndDraw(event)
    
    def leftCntlUp(self, event):
        pass##self.EndDraw(event)

    mergeables = {} # in case not yet initialized when we Draw (maybe not needed)
    moused_over = None

    def clear(self): ###e should modes.py also call this before calling Enter? until it does, call it in Enter ourselves
        self.mergeables = {}
        self.moused_over = None #k?
        self.dragdist = 0.0
        self.have_offset_specific_data = 0 #### also clear that data itself...
        self.bonds_for_current_offset_and_tol = (17,) # impossible value -- ok??
        #e lots more ivars too
        return

    ## toggle attrs, no need to init:
    ## show_whole_model, show_bond_offsets
    
    def Draw(self):
        basicMode.Draw(self) # draw axes, if displayed
        if self.show_whole_model:
            self.o.assy.draw(self.o)
        else:
            for mol in self.molcopies:
                #e use per-repunit drawing styles...
                dispdef = molecule_dispdef(mol, self.o) # not needed, since...
                mol.draw(self.o, dispdef) # ...dispdef arg not used (041013)
        if self.show_bond_offsets:
            for hset in self.show_bond_offsets_handlesets:
                # one of the hsets' radius_multiplier was patched to self.bond_tolerance... ####NIM ###@@@
                try:
                    hset.draw(self.o)
                except:
                    print_compact_traceback("exc in some hset.draw(): ")
##        if self.mergeables:
##            draw_mergeables(self.mergeables, self.o)
        return
   
    def makeMenus(self): ### mostly not yet reviewed for extrude mode
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

        #bruce 041010 experiment -- try letting those other menus also be submenus of this one
        self.Menu1 = self.makemenu([('Cancel', self.Cancel),
                                    ('Start Over', self.StartOver),
                                    ('Backup', self.Backup),
                                    None,
                                    ('Move', self.move),
                                    ('Copy', self.copy),
                                    ## ('debug: EXTRUDE-UPDATE (obsolete!)', self.extrude_update),
                                    ('debug: EXTRUDE-RELOAD', self.extrude_reload),####experimental
                                    None,
                                    # note: use platform.py functions so names work on Mac or non-Mac,
                                    # e.g. "Control-Shift Menu" vs. "Right-Shift Menu",
                                    # or   "Control-Command Menu" vs. "Right-Control Menu".
                                    # [bruce 041014]
                                    ('%s-%s Menu' % (context_menu_prefix(), shift_name()), self.Menu2),
                                    ('%s-%s Menu' % (context_menu_prefix(), control_name()), self.Menu3),
                                   ])
        return

##    def extrude_update(self):
##        print "extrude_update -- this is obs, might mess up other stuff"
##        try:
##            ## explore(self.basemol, self.basemol, self) ###e arg order; make it a method
##            self.mergeables = bondable_singlet_pairs_proto1(self.basemol, self.basemol)
##        except:
##            raise # let Qt print traceback, for now
##        print "extrude_update done"
##        return ### for now

    def extrude_reload(self):
        """for debugging: try to reload extrudeMode.py and patch your glpane
        to use it, so no need to restart Atom. Might not always work.
        [But it did work at least once!]
        """
        print "extrude_reload: here goes...."
        try:
            self.w.extrudeSpinBox_n.setValue(1)
            self.update_from_controls()
            print "reset ncopies to 1, to avoid dialog from Abandon, and ease next use of the mode"
        except:
            print_compact_traceback("exc in resetting ncopies to 1 and updating, ignored: ")
        try:
            self.restore_gui()
        except:
            print_compact_traceback("exc in self.restore_gui(), ignored: ")
        try:
            self.o.other_mode_classes.remove(self.__class__)
        except ValueError:
            print "mode class was not in modetab (normal if last reload of it had syntax error)"
        import handles
        reload(handles)
        import extrudeMode
        reload(extrudeMode)
        from extrudeMode import extrudeMode, do_what_MainWindowUI_should_do
        try:
            do_what_MainWindowUI_should_do(self.w) # remake interface (dashboard), in case it's different [041014]
        except:
            print_compact_traceback("exc in new do_what_MainWindowUI_should_do(), ignored: ")
        ## self.o.modetab['EXTRUDE'] = extrudeMode
        self.o.other_mode_classes.append(extrudeMode)
        print "about to reinit modes"
        self.o._reinit_modes()
        print "done with reinit modes, now see if you can select the reloaded mode"
        return
    
    def copy(self):
        print 'NYI'

    def move(self):
        print 'NYI'

    pass # end of class extrudeMode

# ==

# should be a method in assembly (tho it also uses my local customizations to mol.copy and atom.copy)
def assy_copy(assy, mols, offset = V(10.0, 10.0, 10.0)):
    """in assy, copy the mols in the list of mols; return list of new mols.
    The code is modified from pre-041007 assembly.copy [is that code used? correct? it doesn't do anything with nulist].
    But then extended to handle post-041007 by bruce, 041007-08
    Note, as a side effect (of molecule.copy), the new mols are picked and the old mols are unpicked. ####k [not anymore 041014]
    """
    self = assy
    if mols:
        self.modified = 1
        nulist=[]
        for mol in mols[:]: # copy the list in case it happens to be self.selmols (needed??)
            ##numol=mol.copy(mol.dad,offset)
            numol = mol_copy( mol, mol.dad, offset)
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

# ==

#e between two molecules, find overlapping atoms/bonds ("bad") or singlets ("good") -- as a function of all possible offsets
# (in future, some cases of overlapping atoms might be ok, since those atoms could be merged into one)

# ==

###### lots of experimental code below here

cosine_of_permitted_noncollinearity = 0.5 #e we might want to adjust this parameter

def mergeable_singlets_Q_and_offset(s1, s2, offset2 = None):
    """figure out whether singlets s1 and s2, presumed to be in different
    molecules (or in different copies, if now in the same molecule), could
    reasonably be merged (replaced with one actual bond), if s2.molecule was
    moved by approximately offset2 (or considering all possible offset2's
     if this arg is not supplied); and if so, what would be the ideal offset
    (slightly different from offset2) after this merging.
    Return (False, None, None) or (True, ideal_offset2, error_offset2),
    where error_offset2 gives the radius of a sphere of reasonable offset2
    values, centered around ideal_offset2.
    """
    #e once this works, we might need to optimize it,
    # since it redoes a lot of the same work
    # when called repeatedly for the same extrudable unit.
    res_bad = (False, None, None)
    a1 = singlet_atom(s1)
    a2 = singlet_atom(s2)
    e1 = a1.element
    e2 = a2.element
    r1 = e1.rcovalent
    r2 = e2.rcovalent
    dir1 = norm(s1.posn()-a1.posn())
    dir2 = norm(s2.posn()-a2.posn())
    # the open bond directions (from their atoms) should point approximately
    # opposite to each other -- per Josh suggestion, require them to be
    # within 60 deg. of collinear.
    closeness = - dot(dir1, dir2) # ideal is 1.0, terrible is -1.0
    if closeness < cosine_of_permitted_noncollinearity:
        if extrude_loop_debug and closeness >= 0.0:
            print "rejected nonneg closeness of %r since less than %r" % (closeness, cosine_of_permitted_noncollinearity)
        return res_bad
    # ok, we'll merge. Just figure out the offset. At the end, compare to offset2.
    # For now, we'll just bend the half-bonds by the same angle to make them
    # point at each other, ignoring other bonds on their atoms.
    new_dir1 = norm( (dir1 - dir2) / 2 )
    new_dir2 = - new_dir1 #e needed?
    a1_a2_offset = (r1 + r2) * new_dir1 # ideal offset, just between the atoms
    a1_a2_offset_now = a2.posn() - a1.posn() # present offset between atoms
    ideal_offset2 = a1_a2_offset - a1_a2_offset_now # required shift of a2
    error_offset2 = (r1 + r2) / 2.0 # josh's guess (replaces 1.0 from the initial tests)
    if offset2:
        if vlen(offset2 - ideal_offset2) > error_offset2:
            return res_bad
    return (True, ideal_offset2, error_offset2)

# ==

def singlet_atom(singlet):
    "return the atom a singlet is bonded to"
    obond = singlet.bonds[0]
    atom = obond.other(singlet)
    assert atom.element != Singlet, "bug: a singlet is bonded to another singlet!!"
    return atom

# detect reloading
try:
    _already_loaded
except:
    _already_loaded = 1
else:
    print "reloading extrudeMode.py"
pass

#e this will soon be obs, replaced by something called when the offset changes...
# find it by it also calling mergeable_singlets_Q_and_offset
def bondable_singlet_pairs_proto1(mol1, mol2): ## was: def explore(mol1, mol2, self)
    "for bondable pairs of singlets in mol1 and mol2 (if mol2 can be arbitrarily translated), ... #doc"
    sings1 = mol_singlets(mol1) 
    sings2 = mol_singlets(mol2)
    ##e quadratic, slow alg; worry about too many singlets
    mergeables = {}
    for i1 in range(len(sings1)):
        for i2 in range(len(sings2)):
            if i2 > i1:
                continue # results are negative of swapped i1,i2
            # (but for i1 == i2 we do the calc -- no guarantee mol1 is identical to mol2.)
            s1 = sings1[i1]
            s2 = sings2[i2]
            (ok, ideal, err) = mergeable_singlets_Q_and_offset(s1, s2)
            if extrude_loop_debug:
                print "extrude loop %d, %d got %r" % (i1, i2, (ok, ideal, err))
            #### more code, once we test the above
            if ok:
                mergeables[(i1,i2)] = (ideal, err)
    print "len(mergeables) = %d" % len(mergeables)
    return mergeables



draw_mergeables_debug = 0

def draw_mergeables(mergeables, glpane): #### obs, use HandleSet.draw() -- even if i have to change radius etc.
    assert 0, "using draw_mergeables, should be using self.nice_offsets_handleset.draw()"
    color = (0.5,0.5,0.5)
    radius = 0.33
    detailLevel = 0 # just an icosahedron
    drawer.drawsphere(purple, V(0,0,0), radius * 2, detailLevel) # show the center -- make this draggable??
    if draw_mergeables_debug:
        print "draw_mergeables, number of them is %d" % len(mergeables)
    for (i1,i2),(ideal,error) in mergeables.items():
        pos = ideal
        #e (i might prefer an octahedron, or a miniature-convex-hull-of-extrude-unit)
        drawer.drawsphere(color, pos, radius, detailLevel)
        drawer.drawsphere(color, - pos, radius, detailLevel)
    return

def mol_singlets(mol):
    "return a sequence of the singlets of molecule mol"
    #e see also mol.singlpos, an array of the singlet positions,
    # which could speed up our "explore" method for a specific offset2
    try:
        return mol.singlets
    except AttributeError:
        if not mol.atoms:
            print "fyi, mol_singlets(mol) returns [] since mol %r has no atoms" % (mol,)
            return []
        else:
            mol.shakedown() # this sets singlets = array(singlets, PyObject),
             # but only if mol has any atoms
            return mol.singlets
    pass

# should be a method on molecule:
def molecule_dispdef(mol, glpane):
    # copied out of molecule.draw
    self = mol
    o = glpane
    if self.display != diDEFAULT: disp = self.display
    else: disp = o.display
    return disp

# custom-modified versions of atom and molecule copy methods

def atom_copy(self, numol):
    """create a copy of the atom
    (to go in numol, a copy of its molecule)
    """
    nuat = atom(self.element.symbol, 'no', numol)
    nuat.index = self.index
    nuat.info = self.info # bruce
    return nuat

def mol_copy(self, dad=None, offset=V(0,0,0)):
    """Copy the molecule to a new molecule.
    offset tells where it will go relative to the original.
    """
    pairlis = []
    ndix = {}
    numol = molecule(self.assy, gensym(self.name))
    for a in self.atoms.itervalues():
        ## na = a.copy(numol)
        na = atom_copy(a, numol) # bruce; also copies a.info
        pairlis += [(a, na)]
        ndix[a.key] = na
    for (a, na) in pairlis:
        for b in a.bonds:
            if b.other(a).key in ndix:
                numol.bond(na,ndix[b.other(a).key])
    numol.curpos = self.curpos+offset
    numol.shakedown()
    numol.setDisplay(self.display)
    numol.dad = dad
    numol.colorfunc = self.colorfunc # bruce
    return numol

def mark_singlets(basemol, colorfunc):
    for a in basemol.atoms.itervalues():
        a.info = a.key
    basemol.colorfunc = colorfunc # maps atoms to colors (due to a hack i will add)
    return

#end
 # remember to unpatch colorfunc from the mols when i'm done
# and info from the atoms? not needed but might as well
