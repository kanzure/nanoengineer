# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
test_commands.py -- try out using mode classes as command classes for a command stack;
 find out the minimal needs for a command with PM (and improve them);
 prototype a command stack
 
$Id$


Misc bugs:

- [fixed] leaving this mode, at least for Build Atoms or itself, has weird exception in disconnecting signals, not yet understood
  (as if one was not connected when we entered, which i guess is possible, but if so, why only us?)
  
- userSetMode compares modename, does nothing if same -- will this break immediate reuse of this command if i changed the code?
  ### don't know

- PM is not removed when entering testmode

Cosmetic bugs:

- closing groupboxes makes them flash

- [fixed] tooltip for sponsor button appears everywhere in the PM, even in its bg (annoying) [fixed in PMBC]

TODO:

When cleaning up PropMgrBaseClass etc, note some other things Mark wants to work on soon:

- add message boxes to users of PropertyManagerMixin, in a way easily moved over to PropMgrBaseClass when they use that

- port more modes over to PropMgrBaseClass, e.g. extrudeMode

- split some PMs/modes into more than one smaller PM (especially MMKit)

"""

from modes import basicMode
from selectAtomsMode import selectAtomsMode

from PropMgrBaseClass import PropMgrBaseClass, PropMgrGroupBox, PropMgrComboBox, PropMgrDoubleSpinBox
from GeneratorBaseClass import GeneratorBaseClass

from debug import register_debug_menu_command

from GLPane import GLPane # maybe for an isinstance assertion only
import time

class ExampleCommand1(selectAtomsMode):
    """Example command, which uses behavior similar to selectAtomsMode. [Which in future may inherit class Command.]
    """
    modename = 'ExampleCommand1-modename' # internal #e fix init code in basicMode to get it from classname?
    default_mode_status_text = "ExampleCommand1"
    #e define msg_modename, or fix init code in basicMode to get it from default_mode_status_text or classname or...
    # note: that init code won't even run now, since superclas defs it i think -- actually, not sure abt that, probably it doesn't

    def init_gui(self):
        print "init_gui in", self ####

        win = self.win
        self.__PM = pm = ExampleCommand1_PM(win)
        pm.show()
        selectAtomsMode.init_gui(self) # this fixed the "disconnect without connect" bug
            #k will we need to do this first not last? or not do all of it? seems ok so far.
        return

    def restore_gui(self):
        print "restore_gui in", self ####

        self.__PM.hide() # this works (PM area becomes blank), but doesn't remove the PM tab or change to the MT tab
            ##e should find existing code for doing that and make a common routine in the featureManager to do it (if not one already)
        selectAtomsMode.restore_gui(self) # this apparently worked even when it called init_gui by mistake!!
        return
    
    pass # end of class ExampleCommand1


class ExampleCommand2(selectAtomsMode):
    "same but use GBC"
    modename = 'ExampleCommand2-modename'
    default_mode_status_text = "ExampleCommand2"

    def init_gui(self):
        print "init_gui in", self ####

        win = self.win
        self.__PM = pm = ExampleCommand2_PM(win)
        pm.show()
        selectAtomsMode.init_gui(self)
        return

    def restore_gui(self):
        print "restore_gui in", self ####

        self.__PM.hide()
        selectAtomsMode.restore_gui(self)
        return
    
    pass # end of class ExampleCommand2

# ==

class _eg_pm_widgets:
    "[private] some PM widgets common to several examples here"
    # contains some code copied from AtomGeneratorDialog.py

    #k all needed?
    _sMinCoordinateValue   = -30.0
    _sMaxCoordinateValue   =  30.0
    _sStepCoordinateValue  =  0.1
    _sCoordinateDecimals   =  4
    _sCoordinateUnit       =  'Angstrom'
    _sCoordinateUnits      =  _sCoordinateUnit + 's'
    _sElementSymbolList    =  ["H","O","C","S"]

    def _eg_init_stuff(self):
        self.setPropMgrIcon( self.iconPath )
        self.setPropMgrTitle( self.title )
        self.addGroupBoxes()
        self.add_whats_this_text()

        
        msg = "Example command created at %s" % time.asctime()
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault = False )

    def addGroupBoxes(self):
        """Add the groupboxes for this Property Manager."""

        self.pmGroupBox1  =  PropMgrGroupBox(
                                    self, 
                                    title        =  "Atom Parameters",
                                    titleButton  =  True )

        self.loadGroupBox1(self.pmGroupBox1)
               
    def loadGroupBox1(self, inPmGroupBox):
        """Load widgets into groupbox 1."""

        # User input to specify what type of element/atom to generate
        elementComboBoxItems  =  self._sElementSymbolList
        self.elementComboBox  =  \
            PropMgrComboBox( inPmGroupBox,
                             label         =  "Elements :",
                             choices       =  elementComboBoxItems,
                             idx           =  0,
                             setAsDefault  =  True,
                             spanWidth     =  False )
        
        # User input to specify x-coordinate 
        # of the generated atom's position.
        self.xCoordinateField  =  \
            PropMgrDoubleSpinBox(
                            inPmGroupBox,
                            label         =  "x :",
                            val           =  0.0,
                            setAsDefault  =  True,
                            min           =  self._sMinCoordinateValue,
                            max           =  self._sMaxCoordinateValue,
                            singleStep    =  self._sStepCoordinateValue,
                            decimals      =  self._sCoordinateDecimals,
                            suffix        =  ' ' + self._sCoordinateUnits )
        
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager."""
        
        self.xCoordinateField.setWhatsThis("<b>x</b><p>: The x-coordinate (up to </p>"
                                           + str( self._sMaxCoordinateValue )
                                           + self._sCoordinateUnits
                                           + ") of the Atom in "
                                           + self._sCoordinateUnits + '.')
    pass # end of class _eg_pm_widgets

# ==

from PyQt4.Qt import QDialog
from PropMgrBaseClass import PropMgrBaseClass

class ExampleCommand1_PM( _eg_pm_widgets, QDialog, PropMgrBaseClass): # these supers are needed (but 'object' is evidently not needed)
    """Property Manager for Example Command 1 -- simplest that doesn't use GBC; buttons are noops"""
    
    # <title> - the title that appears in the property manager header.
    title = "Example Command 1"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName(). ###k used only for debugging??
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Toolbars/Smart/Deposit_Atoms.png" ###e REVISE

    # bruce added these to make it work w/o GBC.
    # (It doesn't need restore_defaults_btn_clicked because PropMgrBaseClass defines that itself.
    #  So does GBC, but to a noop method. So GBC better be inherited *after* PropMgrBaseClass!)
    def ok_btn_clicked(self):
        print "ok_btn_clicked", self
        pass
    def abort_btn_clicked(self):
        print "abort_btn_clicked", self
        pass
    def preview_btn_clicked(self):
        print "preview_btn_clicked", self
        pass
    def enter_WhatsThisMode(self):
        print "enter_WhatsThisMode", self
        pass
    # should get these from SponsorableMixin, or (probably better) teach PropMgrBaseClass to get them from there:
    def open_sponsor_homepage(self):
        print "open_sponsor_homepage", self
        pass
    def setSponsor(self):
        print "setSponsor", self
        pass
    
    def __init__(self, win):
        print "creating", self ####

        QDialog.__init__(self, win)
        PropMgrBaseClass.__init__( self, self.propmgr_name )
        if 1: # bruce added these, otherwise various AttributeErrors
            self.win = win # needed in PropMgrBaseClass.show
            self.pw = win.activePartWindow() # same

        self._eg_init_stuff()
        return
    
    pass # end of class ExampleCommand1_PM

class ExampleCommand2_PM( _eg_pm_widgets, QDialog, PropMgrBaseClass, GeneratorBaseClass): # it's simpler if you use GBC
    """Property Manager for Example Command 2 -- simplest that uses GBC; generates a comment (ignores widget values)"""
    
    title = "Example Command 2"
    propmgr_name = "pm" + title
    iconPath = "ui/actions/Toolbars/Smart/Deposit_Atoms.png" #e REVISE

    # need these, at least to use Done:
##    create_name_from_prefix = True ##e we ought to give this a default value in GBC
    prefix = "Thing2" # for names created by GBC [required when create_name_from_prefix is true (not sure about otherwise)]
    cmdname = "Generate a Thing2" # Undo/history cmdname used by GBC [optional, but affects history messages]
    
    def __init__(self, win):
        print "creating", self ####

        QDialog.__init__(self, win)
        PropMgrBaseClass.__init__( self, self.propmgr_name )
        GeneratorBaseClass.__init__( self, win)
        
        self._eg_init_stuff()
        return

    def gather_parameters(self): ###REVIEW: the exception from this gets printed but not as a traceback... 
        return (1,2) ###e not yet grabbed from the widgets

    def build_struct(self, name, params, position):
        """ ... The return value should be the new structure, i.e. some flavor of a Node,
        which has not yet been added to the model. ...
           By convention ... the new node's name should be set to self.name,
        which the caller will have set to self.prefix appended with a serial number.
        """
        print "build_struct(", self, name, params, position, ")"###
        assert self.name == name # true by test and by examining GBC code
        # ignoring params and position for now
        assy = self.win.assy
        from Comment import Comment
        return Comment(assy, name, "comment created at " + time.asctime())

    #e bugs that remain:
    # - widget values not used for creating the thing
    # - preview for comment is not visible except in MT tab or history
    # - restore defaults does nothing useful
    # - whats this button does nothing
    # - when we leave this PM, the PM tab remains, tho it's empty
    
    pass # end of class ExampleCommand2_PM


# == generic example or debug/devel code below here

def construct_cmdrun( cmd_class, glpane):
    """Construct and return a new "CommandRun" object, for use in the given glpane.
    Don't Start it -- there is no obligation for the caller to ever start it;
    and if it does, it's allowed to do that after other user events and model changes
    happened in the meantime [REVIEW THAT, it's not good for "potential commands"] --
    but it should not be after this glpane or its underlying model (assembly object)
    get replaced (e.g. by Open File).
    """
    # (we use same interface as <mode>.__init__ for now,
    #  though passing assy might be more logical)
    cmdrun = cmd_class(glpane)
    ###e should also put it somewhere, as needed for a mode ####DOIT
    if 'kluge, might prevent malloc errors after removing pm from ui (guess)':
        import changes
        changes.keep_forever(cmdrun)
    return cmdrun

def start_cmdrun( cmdrun):
    ## ideally:  cmd.Start() #######
    glpane = cmdrun.glpane
    glpane.mode.Done(new_mode = cmdrun) # is this what takes the old mode's PM away?
    print "done with start_cmdrun for", cmdrun
        # returns as soon as user is in it, doesn't wait for it to "finish" -- so run is not a good name -- use Enter??
        # problem: Enter is only meant to be called internally by glue code in modeMixin.
        # solution: use a new method, maybe Start. note, it's not guaranteed to change to it immediately! it's like Done (newmode arg).

def enter_example_command(widget, example_command_classname):
    assert isinstance(widget, GLPane)
    glpane = widget
    if 1 and 'reload before use (this module only)': ###during devel only
        if 0 and 'try reloading preqs too': ### can't work easily, glpane stores all the mode classes (not just their names)...
            glpane._reinit_modes() # just to get out of current mode safely
            import modes
            reload(modes)
            import selectMode
            reload(selectMode)
            import selectAtomsMode
            reload(selectAtomsMode)
            glpane.mode = glpane.nullmode = modes.nullMode()
            glpane._reinit_modes() # try to avoid problems with changing to other modes later, caused by those reloads
                # wrong: uses old classes from glpane
        import test_commands
        reload(test_commands)
        from test_commands import enter_example_command_doit
    enter_example_command_doit(glpane, example_command_classname)
    return

def enter_example_command_doit(glpane, example_command_classname):
    example_command_class = globals()[example_command_classname]
    example_command_class.modename += 'x' # kluge to defeat userSetMode comparison of modename -- not sure if it works or if it's needed
    cmdrun = construct_cmdrun(example_command_class, glpane)
    start_cmdrun(cmdrun)
    return

for classname in ["ExampleCommand1", "ExampleCommand2"]:
    cmdname = classname # for now
    register_debug_menu_command( cmdname, (lambda widget, classname = classname: enter_example_command(widget, classname)) )

def register_all_entermode_commands(glpane):
    for name in glpane.modetab.keys():
        def func(glp, name = name):
            glp.mode.Done(new_mode = name)
            print "did Enter %s" % name
            return
        register_debug_menu_command( "Enter %s" % name, func )
    return

if 0:
    import env
    win = env.mainwindow()
    glpane = win.glpane
    register_all_entermode_commands(glpane)
    
# end
