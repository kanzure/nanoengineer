# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-12 created.

TODO 2008-08-12:
- This uses global pref keys (hardcoded) because the preference is supposed
to remain in all commands. Other option is to ask the command or parentWidget
for the prefs_key. If we want to support local prefs keys (e.g. turn on the labels
while in certain commands only, then perhaps it should ask for prefs keys from
the command. (and there needs an API method in command so that its implemented for all
command classes. The latter seems unncecessary at this time,
"""
import foundation.env as env
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_ComboBox import PM_ComboBox
from PM.PM_ColorComboBox import PM_ColorComboBox

from utilities.prefs_constants import dnaBaseNumberLabelColor_prefs_key
from utilities.prefs_constants import dnaBaseNumberingOrder_prefs_key
from utilities.prefs_constants import dnaBaseNumberLabelChoice_prefs_key

from PyQt4.Qt import SIGNAL
from widgets.prefs_widgets import connect_comboBox_with_pref

_superclass = PM_GroupBox

class PM_DnaBaseNumberLabelsGroupBox(PM_GroupBox):
    """
    """
    def __init__(self,
                 parentWidget,
                 command,
                 title = 'Base Number Labels' ):
        """
        """

        self.command = command
        self.win = self.command.win

        _superclass.__init__(self, parentWidget, title = title)
        self._loadWidgets()

    def connect_or_disconnect_signals(self, isConnect):
        """
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect

        change_connect(self._baseNumberLabelColorChooser,
                      SIGNAL("editingFinished()"),
                      self._colorChanged_dnaBaseNumberLabel)

        self._connect_widgets_with_prefs_keys()



    def _connect_widgets_with_prefs_keys(self):
        """
        Connect various widgets with a prefs_key
        """
        prefs_key = dnaBaseNumberLabelChoice_prefs_key
        connect_comboBox_with_pref(self._baseNumberComboBox,
                                   prefs_key )

        prefs_key = dnaBaseNumberingOrder_prefs_key
        connect_comboBox_with_pref(self._baseNumberingOrderComboBox ,
                                   prefs_key )


    def _loadWidgets(self):
        """
        Load the widgets in the Groupbox
        """
        baseNumberChoices = ('None (default)',
                             'Strands and segments',
                             'Strands only',
                             'Segments only')

        self._baseNumberComboBox = \
            PM_ComboBox( self,
                         label         =  "Base numbers:",
                         choices       =  baseNumberChoices,
                         setAsDefault  =  True)

        numberingOrderChoices = ('5\' to 3\' (default)',
                           '3\' to 5\'' )

        self._baseNumberingOrderComboBox = \
            PM_ComboBox( self,
                         label         =  "Base numbers:",
                         choices       =  numberingOrderChoices,
                         setAsDefault  =  True)

        prefs_key = dnaBaseNumberLabelColor_prefs_key
        self._baseNumberLabelColorChooser = \
            PM_ColorComboBox(self,
                             color      = env.prefs[prefs_key])


    def _colorChanged_dnaBaseNumberLabel(self):
        """
        Choose custom color for 5' ends
        """
        color = self._baseNumberLabelColorChooser.getColor()
        prefs_key = dnaBaseNumberLabelColor_prefs_key
        env.prefs[prefs_key] = color
        self.win.glpane.gl_update()
        return

    def _updateColor_dnaBaseNumberLabel(self):
        """
        Update the color in the base number label combobox while calling
        self.show()
        @see: self.show().
        """
        prefs_key = dnaBaseNumberLabelColor_prefs_key
        color = env.prefs[prefs_key]
        self._baseNumberLabelColorChooser.setColor(color)
        return

    def updateWidgets(self):
        """
        Called in BreakorJoinstrands_PropertyManager.show()
        """
        #@TODO: revise this.
        #Ideally the color combobox  should be connected with state.
        #(e.g. 'connect_colorCombobox_with_state' , which will make the
        #following update call unncessary. but connecting with state
        #for the color combobox has some issues not resolved yet.
        #(e.g. the current index changed won't always allow you to set the
        #proper color -- because the 'Other color' can be anything)
        #--Ninad 2008-08-12
        self._updateColor_dnaBaseNumberLabel()
