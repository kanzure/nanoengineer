# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
test_connectWithState_PM.py -- Property Manager for test_connectWithState command.

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

070830 bruce split this out of test_command_PMs.py
"""

# This is scratch code for testing and demonstrating the "connectWithState" feature.
# It can be used with various types of state whose uses and changes are tracked in
# a standard way. For now, that kind of state includes only:
# - env.prefs[prefs_key] values (some examples below);
# - instance variables defined with the State macro in suitably defined classes (some examples below);
# - internal state in exprs created by the exprs module.
# Later we will add to that:
# - all state tracked by Undo
# and we'll also optimize the State macro and make it easier to use.


from widgets.prefs_widgets import Preferences_StateRef, Preferences_StateRef_double # TODO: remove these imports, get the refs from the model

from widgets.prefs_widgets import ObjAttr_StateRef # TODO: shorter or clearer name -- attribute_ref ?

from prototype.test_connectWithState_constants import CYLINDER_HEIGHT_PREFS_KEY, CYLINDER_HEIGHT_DEFAULT_VALUE
from prototype.test_connectWithState_constants import CYLINDER_ROUND_CAPS_PREFS_KEY, CYLINDER_ROUND_CAPS_DEFAULT_VALUE # TODO: get prefs refs from model so these are not needed here
##from test_connectWithState_constants import CYLINDER_VERTICAL_DEFAULT_VALUE
##from test_connectWithState_constants import CYLINDER_WIDTH_DEFAULT_VALUE

from prototype.test_command_PMs import ExampleCommand1_PM

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_PushButton    import PM_PushButton
from PM.PM_CheckBox      import PM_CheckBox

# ===

class test_connectWithState_PM( ExampleCommand1_PM):

    # does not use GBC; at least Done & Cancel should work

    title = "test connectWithState"

    def _addGroupBoxes(self):
        """
        Add the groupboxes for this Property Manager.
        """
        self.pmGroupBox1 = PM_GroupBox( self, title =  "settings")
        self._loadGroupBox1(self.pmGroupBox1)
        self.pmGroupBox2 = PM_GroupBox( self, title =  "commands")
        self._loadGroupBox2(self.pmGroupBox2)
        return

    _sMaxCylinderHeight = 20 ### TODO: ask the stateref for this

    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets into groupbox 1 (passed as pmGroupBox).
        """
        # cylinder height (a double, stored as a preferences value)

        cylinderHeight_stateref = Preferences_StateRef_double(
            CYLINDER_HEIGHT_PREFS_KEY,
            CYLINDER_HEIGHT_DEFAULT_VALUE )
            ### TODO: ask model object for this ref; this code should not need to know what kind it is (from prefs or model)

        self.cylinderHeightSpinbox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "cylinder height:",
##                              value         =  CYLINDER_HEIGHT_DEFAULT_VALUE,
##                              # guess: default value or initial value (guess they can't be distinguished -- bug -- yes, doc confirms)
##                              setAsDefault  =  True,
                              ### TODO: get all the following from the stateref, whenever the connection to state is made
                              minimum       =  3,
                              maximum       =  self._sMaxCylinderHeight,
                              singleStep    =  0.25,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )
        # REVIEW: is it ok that the above will set some wrong defaultValue,
        # to be immediately corrected by the following connection with state?
        self.cylinderHeightSpinbox.connectWithState(
            cylinderHeight_stateref,
            debug_metainfo = True
         )

        # ==

        # cylinder width (a double, stored in the command object,
        #  defined there using the State macro -- note, this is not yet a good
        #  enough example for state stored in a Node)

        cylinderWidth_stateref = ObjAttr_StateRef( self.command, 'cylinderWidth')

        ## TEMPORARY: just make sure it's defined in there
        junk = cylinderWidth_stateref.defaultValue

        self.cylinderWidthSpinbox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "cylinder width:",
##                              value         =  defaultValue,
##                              setAsDefault  =  True,
##                                  ### REVISE: the default value should come from the cylinderWidth_stateref
                                  # (and so, probably, should min, max, step, units...)
                              minimum       =  0.1,
                              maximum       =  15.0,
                              singleStep    =  0.1,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )

        self.cylinderWidthSpinbox.connectWithState(
                                cylinderWidth_stateref,
                                debug_metainfo = True )

        # ==

        # cylinder round caps (boolean)

        cylinderRoundCaps_stateref = Preferences_StateRef( CYLINDER_ROUND_CAPS_PREFS_KEY,
                                                           CYLINDER_ROUND_CAPS_DEFAULT_VALUE ) ### TODO: get from model
        ## TEMPORARY: just make sure it's defined in there
        junk = cylinderRoundCaps_stateref.defaultValue

        self.cylinderRoundCapsCheckbox = PM_CheckBox(pmGroupBox, text = 'round caps on cylinder')
##        self.cylinderRoundCapsCheckbox.setDefaultValue(CYLINDER_ROUND_CAPS_DEFAULT_VALUE)
##            # note: setDefaultValue is an extension to the PM_CheckBox API, not yet finalized
        self.cylinderRoundCapsCheckbox.connectWithState(
                                cylinderRoundCaps_stateref,
                                debug_metainfo = True )

        # ==

        # cylinder vertical or horizontal (boolean)
        cylinderVertical_stateref = ObjAttr_StateRef( self.command, 'cylinderVertical' )

        self.cylinderVerticalCheckbox = PM_CheckBox(pmGroupBox, text = 'cylinder is vertical')
##        self.cylinderVerticalCheckbox.setDefaultValue(CYLINDER_VERTICAL_DEFAULT_VALUE)
##            ### REVISE: the default value should come from the stateref
        self.cylinderVerticalCheckbox.connectWithState(
                                cylinderVertical_stateref,
                                debug_metainfo = True )

        return # from _loadGroupBox1

    def _loadGroupBox2(self, pmGroupBox): ### RENAME button attrs
        self.startButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "Bigger",
                           spanWidth = False ) ###BUG: button spans PM width, in spite of this setting
        self.startButton.setAction( self.button_Bigger, cmdname = "Bigger")

        self.stopButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "Smaller",
                           spanWidth = False )
        self.stopButton.setAction( self.button_Smaller, cmdname = "Smaller")

        return

    def button_Bigger(self):
        self.command.cmd_Bigger()

    def button_Smaller(self):
        self.command.cmd_Smaller()

    def _addWhatsThisText(self):
        """
        What's This text for some of the widgets in the Property Manager.
        """
        self.cylinderHeightSpinbox.setWhatsThis("cylinder height (stored in prefs)")
        self.cylinderWidthSpinbox.setWhatsThis("cylinder width (stored as State in the command object)")
        return

    pass # end of class

# end
