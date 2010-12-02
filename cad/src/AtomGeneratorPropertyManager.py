# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

An example of a structure generator's user interface meant to be a template
for developers.

The AtomGeneratorDialog class is an example of how the Property Manager 
module is used to build a structure generator's user interface (dialog) in 
NanoEngineer-1.  The key points of interest are the methods: __init__() 
and _addGroupBoxes().  They **must always** be overriden when a new structure 
generator dialog class is defined.

The class variables <title> and <iconPath> should be changed to fit the 
new structure generator's role.

The class static variables (prefixed with _s) and their accessor 
methods (Get.../Set...)are purely for the sake of example and may 
be omitted from any new implementation.

@author: Jeff Birac
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.
@version: 0.1

$Id$

History:
  Jeff 2007-05-29: Based on Mark Sims' GrapheneGeneratorDialog.py, v1.17

            Convention of variables' names:

                   variable's role     prefix      examples
                  -----------------   --------    ----------
                - incoming parameter    in...      inData
                                                   inObjectPointer

                - outgoing parameter               outBufferPointer
                  or function return    out...     outCalculation
                   
                - I/O parameter         io...      ioDataBuffer

                - static variable       s...       sDefaultValue

                - local variable        the...     theUserName
                                                   theTempValue

                - class member          m...       mObjectName
                  (aka attribute or                mPosition
                  instance variable)               mColor
                  
  Mark 2007-07-24: Uses new PM module.
  
"""
        
__author__ = "Jeff"

from PyQt4.Qt import Qt, SIGNAL

from PM.PM_Dialog             import PM_Dialog
from PM.PM_GroupBox           import PM_GroupBox
from PM.PM_DoubleSpinBox      import PM_DoubleSpinBox
from PM.PM_ElementChooser     import PM_ElementChooser

class AtomGeneratorPropertyManager(PM_Dialog):
    """
    The AtomGeneratorPropertyManager class provides a Property Manager 
    for the "Build > Atom" command.
    
    @cvar title: The title that appears in the property manager header.
    @type title: str
    
    @cvar pmName: The name of this property manager. This is used to set
                  the name of the PM_Dialog object via setObjectName().
    @type name: str
    
    @cvar iconPath: The relative path to the PNG file that contains a
                    22 x 22 icon image that appears in the PM header.
    @type iconPath: str
    """
    title    = "Atom Generator"
    pmName   = title
    iconPath = "ui/actions/Toolbars/Smart/Deposit_Atoms.png"

    # Jeff 20070530:
    # Private static variables (prefixed with '_s') are used to assure consistency 
    # between related widgets and simplify code revision.
    # Example: The unit for coordinates is specified by _sCoordinateUnit.  All
    # widgets related to coordinates should refer to _sCoordinateUnit rather than
    # hardcoding the unit for each coordinate widget.  The advantage comes when 
    # a later revision uses different units (or chosen possibly via a user
    # preference), the value of only _sCoordinateUnit (not blocks of code)
    # needs to be changed.  All related widgets follow the new choice for units.

    _sMinCoordinateValue   = -30.0
    _sMaxCoordinateValue   =  30.0
    _sStepCoordinateValue  =  0.1
    _sCoordinateDecimals   =  4
    _sCoordinateUnit       =  'Angstrom'
    _sCoordinateUnits      =  _sCoordinateUnit + 's'

    def __init__(self):
        """
        Constructor for the Atom Generator Property Manager.
        """
        PM_Dialog.__init__( self, self.pmName, self.iconPath, self.title )
        self._addGroupBoxes()
        self._addWhatsThisText()
        
        msg = "Edit the Atom parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert the atom \
        into the model."
        
        # This causes the message box to be displayed as well.
        self.MessageGroupBox.insertHtmlMessage( msg, setAsDefault = False )
        
    def getCartesianCoordinates():
        """
        Gets the cartesian coordinates for the position of the atom
        specified in the coordinate spin boxes of the Atom Generator
        property manager.
        """
        return ( self.xCoordinateField.value, 
                 self.yCoordinateField.value, 
                 self.zCoordinateField.value )

    def getMinCoordinateValue(self):
        """
        Get the minimum value allowed in the coordinate spin boxes 
        of the Atom Generator property manager.
        """
        return self.sel_sMinCoordinateValue
    
    def getMaxCoordinateValue(self):
        """
        Get the maximum value allowed in the coordinate 
        spin boxes of the Atom Generator property manager.
        """
        return self._sMaxCoordinateValue

    def getStepCoordinateValue(self):
        """
        Get the value by which a coordinate increases/decreases 
        when the user clicks an arrow of a coordinate spin box 
        in the Atom Generator property manager.
        """
        return self._sStepCoordinateValue

    def getCoordinateDecimals(self):
        """
        Get the number of decimal places given for a value in a 
        coordinate spin box in the Atom Generator property manager.
        """
        return self._sStepCoordinateValue

    def getCoordinateUnit(self):
        """
        Get the unit (of measure) for the coordinates of the 
        generated atom's position.
        """
        return self._sCoordinateUnit
    
    def setCartesianCoordinates( self, inX, inY, inZ ):
        """
        Set the cartesian coordinates for the position of the atom
        specified in the coordinate spin boxes of the Atom Generator
        property manager.
        """
        # We may want to restrict 
        self.xCoordinateField.value  =  inX
        self.yCoordinateField.value  =  inY
        self.zCoordinateField.value  =  inZ

    def setMinCoordinateValue( self, inMin ):
        """
        Set the minimum value allowed in the coordinate spin boxes 
        of the Atom Generator property manager.
        """
        self._sMinCoordinateValue  =  inMin
    
    def setMaxCoordinateValue( self, inMax ):
        """
        Set the maximum value allowed in the coordinate 
        spin boxes of the Atom Generator property manager.
        """
        self._sMaxCoordinateValue  =  inMax

    def setStepCoordinateValue( self, inStep ):
        """
        Set the value by which a coordinate increases/decreases 
        when the user clicks an arrow of a coordinate spin box 
        in the Atom Generator property manager.
        """
        self._sStepCoordinateValue  =  inStep

    def setCoordinateDecimals( self, inDecimals ):
        """
        Set the number of decimal places given for a value in a 
        coordinate spin box in the Atom Generator property manager.
        """
        self._sStepCoordinateValue  =  inDecimals

    def setCoordinateUnit( self, inUnit ):
        """
        Set the unit(s) (of measure) for the coordinates of the 
        generated atom's position.
        """
        self._sCoordinateUnit   =  inUnit
        self._sCoordinateUnits  =  inUnit + 's'
    
    def _addGroupBoxes(self):
        """
        Add the 2 group boxes for the Atom Property Manager.
        """

        # Group box 1 contains the XYZ widgets.
        self.pmGroupBox1 = PM_GroupBox( self, title =  "Atom Position" )
        self._loadGroupBox1(self.pmGroupBox1)
        
        # Group box 2 is an Element Chooser widget.
        self.pmElementChooser =  PM_ElementChooser(self)
    
    def _loadGroupBox1(self, inPmGroupBox):
        """
        Load widgets into group box 1.
        """
        
        # User input to specify x-coordinate 
        # of the generated atom's position.
        self.xCoordinateField  =  \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "X:",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )

        # User input to specify y-coordinate
        # of the generated atom's position.
        self.yCoordinateField  =  \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "Y:",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )

        # User input to specify z-coordinate 
        # of the generated atom's position.
        self.zCoordinateField = \
            PM_DoubleSpinBox( inPmGroupBox,
                              label         =  "Z:",
                              value         =  0.0,
                              setAsDefault  =  True,
                              minimum       =  self._sMinCoordinateValue,
                              maximum       =  self._sMaxCoordinateValue,
                              singleStep    =  self._sStepCoordinateValue,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )
    
    def _addWhatsThisText(self):
        """
        What's This... text for some of the widgets in the Property Manager.
        """
        
        self.xCoordinateField.setWhatsThis("<b>x</b><p>: The x-coordinate (up to </p>" \
                                           + str( self._sMaxCoordinateValue ) \
                                           + self._sCoordinateUnits \
                                           + ") of the Atom in " \
                                           + self._sCoordinateUnits + '.')
        
        self.yCoordinateField.setWhatsThis("<b>y</b><p>: The y-coordinate (up to </p>"\
                                           + str( self._sMaxCoordinateValue ) \
                                           + self._sCoordinateUnits \
                                           + ") of the Atom in " \
                                           + self._sCoordinateUnits + '.')
        
        self.zCoordinateField.setWhatsThis("<b>z</b><p>: The z-coordinate (up to </p>" \
                                           + str( self._sMaxCoordinateValue )
                                           + self._sCoordinateUnits \
                                           + ") of the Atom in " 
                                           + self._sCoordinateUnits + '.')
