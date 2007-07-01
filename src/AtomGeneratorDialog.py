# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""

An example of a structure generator's user interface 
meant to be a template developers.

The AtomGeneratorDialog class is an example of how PropMgrBaseClass 
is used to build a structure generator's user interface (dialog) in 
NanoEngineer-1.  The key points of interest are the methods: __init__, 
addGroupBoxes and add_whats_this_text.  They all **must always** be 
overriden when a new structure generator dialog class is defined.

The class variables title and iconPath should be changed to fit the 
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
"""
        
__author__ = "Jeff"

from Utility import geticon, getpixmap
from bonds import CC_GRAPHITIC_BONDLENGTH
from PropMgrBaseClass import PropMgrBaseClass
from PropMgrBaseClass import PropMgrGroupBox
from PropMgrBaseClass import PropMgrComboBox
from PropMgrBaseClass import PropMgrDoubleSpinBox

class AtomPropertyManager(object, PropMgrBaseClass):
    """ Implements user interface to specify properties of an atom """

    # <title> - the title that appears in the property manager header.
    title = "Atom Generator"
    # <propmgr_name> - the name of this property manager. This will be set to
    # the name of the PropMgr (this) object via setObjectName().
    propmgr_name = "pm" + title
    # <iconPath> - full path to PNG file that appears in the header.
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
    _sElementSymbolList    =  ["H","O","C","S"]

    def __init__(self):
        """Construct the Atom Property Manager.
        """
        PropMgrBaseClass.__init__( self, self.propmgr_name )
        self.setPropMgrIcon( self.iconPath )
        self.setPropMgrTitle( self.title )
        self.addGroupBoxes()
        self.add_whats_this_text()
        
        msg = "Edit the Atom parameters and select <b>Preview</b> to \
        preview the structure. Click <b>Done</b> to insert the atom \
        into the model."
        
        # This causes the "Message" box to be displayed as well.
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
    
    def addGroupBoxes(self):
        """
        Add the 1 groupbox for the Atom Property Manager.
        """

        self.pmGroupBox1  =  PropMgrGroupBox( \
                                    self, 
                                    title        =  "Atom Parameters",
                                    titleButton  =  True )

        self.loadGroupBox1(self.pmGroupBox1)
               
    def loadGroupBox1(self, inPmGroupBox):
        """
        Load widgets into groupbox 1.
        """

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
            PropMgrDoubleSpinBox( \
                            inPmGroupBox,
                            label         =  "x :",
                            val           =  0.0,
                            setAsDefault  =  True,
                            min           =  self._sMinCoordinateValue,
                            max           =  self._sMaxCoordinateValue,
                            singleStep    =  self._sStepCoordinateValue,
                            decimals      =  self._sCoordinateDecimals,
                            suffix        =  ' ' + self._sCoordinateUnits )

        # User input to specify y-coordinate
        # of the generated atom's position.
        self.yCoordinateField  =  \
            PropMgrDoubleSpinBox( \
                            inPmGroupBox,
                            label         =  "y :",
                            val           =  0.0,
                            setAsDefault  =  True,
                            min           =  self._sMinCoordinateValue,
                            max           =  self._sMaxCoordinateValue,
                            singleStep    =  self._sStepCoordinateValue,
                            decimals      =  self._sCoordinateDecimals,
                            suffix        =  ' ' + self._sCoordinateUnits )

        # User input to specify z-coordinate 
        # of the generated atom's position.
        self.zCoordinateField = \
            PropMgrDoubleSpinBox( \
                            inPmGroupBox,
                            label         =  "z :",
                            val           =  0.0,
                            setAsDefault  =  True,
                            min           =  self._sMinCoordinateValue,
                            max           =  self._sMaxCoordinateValue,
                            singleStep    =  self._sStepCoordinateValue,
                            decimals      =  self._sCoordinateDecimals,
                            suffix        =  ' ' + self._sCoordinateUnits )
        
        
    def add_whats_this_text(self):
        """
        What's This... text for some of the widgets in the 
        Atom Property Manager.
        :Jeff 2007-05-30:
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
