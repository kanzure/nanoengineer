# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
test_command_PMs.py - property manager classes for test_commands.py.
See that file for more info.

$Id$
"""

##from PropMgrBaseClass import PropMgrBaseClass, PropMgrGroupBox, PropMgrComboBox, PropMgrDoubleSpinBox
##from PyQt4.Qt import QDialog

from PyQt4.Qt import SIGNAL

from PM.PM_Dialog        import PM_Dialog
from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_ComboBox      import PM_ComboBox
from PM.PM_SpinBox       import PM_SpinBox
from PM.PM_TextEdit      import PM_TextEdit
from PM.PM_PushButton    import PM_PushButton
from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_RadioButton   import PM_RadioButton

from GeneratorBaseClass import GeneratorBaseClass

import time

class PM_Dialog_with_example_widgets( PM_Dialog):
    "[private] PM_Dialog with some PM widgets common to several examples here"
    # NOTE: contains some code copied (and perhaps modified) from AtomGeneratorDialog.py

    # these class constants should be defined by each specific PM subclass
    # (we don't define them here, since we want errors to occur if you don't override them)
    #   title = "title"
    #   pmName = "pm" + title
    #   iconPath = "path-to-some-icon.png"

    #k all needed?
    _sMinCoordinateValue   = -30.0
    _sMaxCoordinateValue   =  30.0
    _sStepCoordinateValue  =  0.1
    _sCoordinateDecimals   =  4
    _sCoordinateUnit       =  'Angstrom'
    _sCoordinateUnits      =  _sCoordinateUnit + 's'
    _sElementSymbolList    =  ["H","O","C","S"]

    def __init__(self):
##    def _eg_init_stuff(self): @@@
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        self.addGroupBoxes()
        self.add_whats_this_text()
        
        msg = "Example command created at %s" % time.asctime()
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault = False )
        return

    def addGroupBoxes(self):
        """Add the groupboxes for this Property Manager."""

        self.pmGroupBox1 = \
            PM_GroupBox( self, 
                         title           =  "Atom Parameters",
##                         addTitleButton  =  True
                         )

        self.loadGroupBox1(self.pmGroupBox1)
        return
    
    def loadGroupBox1(self, inPmGroupBox):
        """
        Load widgets into groupbox 1.
        """

        # User input to specify what type of element/atom to generate
        elementComboBoxItems  =  self._sElementSymbolList
        self.elementComboBox  =  \
            PM_ComboBox( inPmGroupBox,
                         label         =  "Elements :",
                         choices       =  elementComboBoxItems,
                         index         =  0,
                         setAsDefault  =  True,
                         spanWidth     =  False )
        
        # User input to specify x-coordinate 
        # of the generated atom's position.
        self.xCoordinateField  =  \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "x :",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )
        return
        
    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Property Manager."""
        
        self.xCoordinateField.setWhatsThis("<b>x</b><p>: The x-coordinate (up to </p>"
                                           + str( self._sMaxCoordinateValue )
                                           + self._sCoordinateUnits
                                           + ") of the Atom in "
                                           + self._sCoordinateUnits + '.')
    pass # end of class PM_Dialog_with_example_widgets

# ==

class ExampleCommand1_PM( PM_Dialog_with_example_widgets): # these supers are needed (but 'object' is evidently not needed)
    """Property Manager for Example Command 1 -- simplest that doesn't use GBC; buttons are noops"""
    
    # <title> - the title that appears in the property manager header.
    title = "Example Command 1"
    # <pmName> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName(). ###k used only for debugging??
    pmName = "pm" + title
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

        PM_Dialog_with_example_widgets.__init__( self ) ## ok before the next lne? @@@
        if 1: # bruce added these, otherwise various AttributeErrors
            self.win = win # needed in PropMgrBaseClass.show
            self.pw = win.activePartWindow() # same
        return
    
    pass # end of class ExampleCommand1_PM

class ExampleCommand2_PM( PM_Dialog_with_example_widgets, GeneratorBaseClass):
    """Property Manager for Example Command 2 -- simplest that uses GBC; generates a comment (ignores widget values)"""
    
    title = "Example Command 2"
    pmName = "pm" + title
    iconPath = "ui/actions/Toolbars/Smart/Deposit_Atoms.png" #e REVISE

    # need these, at least to use Done:
##    create_name_from_prefix = True ##e we ought to give this a default value in GBC
    prefix = "Thing2" # for names created by GBC [required when create_name_from_prefix is true (not sure about otherwise)]
    cmdname = "Generate a Thing2" # Undo/history cmdname used by GBC [optional, but affects history messages]
    
    def __init__(self, win, commandrun = None):
        print "creating", self ####
        self.commandrun = commandrun

        PM_Dialog_with_example_widgets.__init__( self )
        GeneratorBaseClass.__init__( self, win)        
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

class PMWidgetsTest_PM(PM_Dialog, GeneratorBaseClass):
    """
    This is a special command for testing new widgets in the PM module
    in their own Property Manager. It does nothing except display PM group boxes
    and their widgets.
    """
    
    title = "PM Widget Test"
    pmName = title
    iconPath = "ui/actions/Properties Manager/info.png"

    def __init__(self, win, commandrun = None):
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        GeneratorBaseClass.__init__( self, win)    
        self._addGroupBoxes()
        
        msg = "This is intended to be used to test the new PM \
               widgets needed to migrate the Move Property Manager to \
               the new PM module."
        
        # This causes the "Message" box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault = False )
        return

    def _addGroupBoxes(self):
        """
        Add group boxes to the Property Manager.
        """
        self.pmGroupBox1 = PM_GroupBox( self, title =  "Translate" )
        self._loadTranslateGroupBox(self.pmGroupBox1)
        return
    
    # == Begin Translate Group Box =====================
    
    def _loadTranslateGroupBox(self, inPmGroupBox):
        """
        Populate Translate group box.
        """
        
        translateChoices = [ "Free Drag", "By Delta XYZ", "To XYZ Position" ]
        
        self.translateComboBox = \
            PM_ComboBox( inPmGroupBox,
                         label        = '', 
                         choices      = translateChoices, 
                         index        = 0, 
                         setAsDefault = False,
                         spanWidth    = True )
        
        self.connect(self.translateComboBox, 
                     SIGNAL("currentIndexChanged(int)"), 
                     self.updateTranslateGroupBoxes)
        
        self.freeDragGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadFreeDragGroupBox(self.freeDragGroupBox)
        
        self.byDeltaXyzGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadDeltaXyzGroupBox(self.byDeltaXyzGroupBox)
        
        self.toXyzPositionGroupBox = PM_GroupBox( inPmGroupBox )
        self._loadToXyzPositionGroupBox(self.toXyzPositionGroupBox)
        
        self.updateTranslateGroupBoxes(0)
    
    def _loadFreeDragGroupBox(self, inPmGroupBox):
        """
        Populate "Free Drag" (nested) group box.
        """
        self.freeDragButton = \
            PM_PushButton( inPmGroupBox,
                           label = "",
                           text  = "F" )
        
    def _loadDeltaXyzGroupBox(self, inPmGroupBox):
        """
        Populate "By XYZ Delta" (nested) group box.
        """

        self.deltaXSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "X:",
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = -100.0, 
                              maximum      =  100.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms',
                              spanWidth    = False )
        
        self.deltaYSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "Y:",
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = -100.0, 
                              maximum      =  100.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms',
                              spanWidth    = False )
        
        self.deltaZSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "Z:",
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = -100.0, 
                              maximum      =  100.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms',
                              spanWidth    = False )
        
        self.movePlusDeltaButton = \
            PM_PushButton( inPmGroupBox,
                           label = "",
                           text  = "Move Plus" )
        
        self.moveMinusDeltaButton = \
            PM_PushButton( inPmGroupBox,
                           label = "",
                           text  = "Move Minus" )
    
    def _loadToXyzPositionGroupBox(self, inPmGroupBox):
        """
        Populate "To XYZ Position" (nested) group box.
        """

        self.xSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "X:",
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = -100.0, 
                              maximum      =  100.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms',
                              spanWidth    = False )
        
        self.ySpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "Y:",
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = -100.0, 
                              maximum      =  100.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms',
                              spanWidth    = False )
        
        self.zSpinBox = \
            PM_DoubleSpinBox( inPmGroupBox, 
                              label        = "Z:",
                              value        = 0.0, 
                              setAsDefault = True,
                              minimum      = -100.0, 
                              maximum      =  100.0, 
                              singleStep   = 1.0, 
                              decimals     = 1, 
                              suffix       = ' Angstroms',
                              spanWidth    = False )
        
        self.moveButton = \
            PM_PushButton( inPmGroupBox,
                           label     = "",
                           text      = "Move Selection",
                           spanWidth = True )
        
    # == Slots for Translate group box
    
    def updateTranslateGroupBoxes(self, id):
        """
        Update the translate group boxes displayed based on the translate
        option selected.
        """
        if id is 0:
            self.toXyzPositionGroupBox.hide()
            self.byDeltaXyzGroupBox.hide()
            self.freeDragGroupBox.show()
                               
        if id is 1:
            self.freeDragGroupBox.hide()
            self.toXyzPositionGroupBox.hide()
            self.byDeltaXyzGroupBox.show()
                    
        if id is 2:
            self.freeDragGroupBox.hide()
            self.byDeltaXyzGroupBox.hide()
            self.toXyzPositionGroupBox.show()
        
    # == End of Translate Group Box =====================
    
    pass # end of class PM_Demo

# end
