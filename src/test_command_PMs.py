# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
test_command_PMs.py - property manager classes for test_commands.py.
See that file for more info.

$Id$
"""

from PropMgrBaseClass import PropMgrBaseClass, PropMgrGroupBox, PropMgrComboBox, PropMgrDoubleSpinBox
from PyQt4.Qt import QDialog

from GeneratorBaseClass import GeneratorBaseClass

import time

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
        print "ok_btn_clicked, nim except for Done in", self
##        ## probably wrong: self.parent.Done() ###k both parent and Done
##        print "parent is",self.parent ## parent is <built-in method parent of ExampleCommand1_PM object at 0x203774b0>
##            # parent is a *method*?? does it come from Qt?? (QDialog?) but it's *also* a propmgr attr, or propmgr widget attr...
        self.commandrun.Done() ###k both commandrun and Done
        pass
    def abort_btn_clicked(self):
        print "abort_btn_clicked, nim except for Done in", self
        self.commandrun.Done() ###k both commandrun and Done
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
    
    def __init__(self, win, commandrun = None):
        print "creating", self ####
        self.commandrun = commandrun

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
    
    def __init__(self, win, commandrun = None):
        print "creating", self ####
        self.commandrun = commandrun

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

    def ok_btn_clicked(self):
        print "ok_btn_clicked, doing super then Done (kluge)", self
        GeneratorBaseClass.ok_btn_clicked(self)
        self.commandrun.Done() ###k both commandrun and Done -- and, kluge, instead GBC should call a done method in self.commandrun
        pass
    def abort_btn_clicked(self):
        print "abort_btn_clicked, doing super then Done (kluge)", self
        GeneratorBaseClass.abort_btn_clicked(self)
        self.commandrun.Done()
        pass

    pass # end of class ExampleCommand2_PM

class ExampleCommand2E_PM( ExampleCommand2_PM ):
    """Property Manager for Example Command 2E"""
    title = "Example Command 2E"
    pass

# end
