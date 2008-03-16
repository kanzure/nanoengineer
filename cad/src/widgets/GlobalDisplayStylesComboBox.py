"""
GlobalDisplayStylesComboBox.py - Provides a combo box with all the global display
styles.

@author: Mark
@version: $Id:$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

To do (for Mark):
- Add tooltip and What's This text.
- Change "Default Display Style" in the preferences dialog (Mode page) to
"Global Display Style at start up"
"""

import os
import foundation.env as env
from PyQt4.Qt import SIGNAL, QComboBox

from utilities.constants import diDEFAULT ,diTrueCPK, diLINES
from utilities.constants import diBALL, diTUBES, diDNACYLINDER
from foundation.env import currentpart
from utilities.prefs_constants import defaultDisplayMode_prefs_key
from utilities.icon_utilities import geticon

# Should DNA Cylinder be a global display style? Selecting it makes everything
# else invisibles. If we leave it in the list, we must document this confusing
# behavior in the "What's This" text.
# --Mark 2008-03-16
displayIndexes = [diLINES, diTUBES, diBALL, diTrueCPK, diDNACYLINDER]
displayNames   = ["Lines", "Tubes", "Ball and Stick", "CPK", "DNA Cylinder"]
displayIcons   = ["Lines", "Tubes", "Ball_and_Stick", "CPK", "DNACylinder" ]

displayIconsDict = dict(zip(displayNames, displayIcons))
displayNamesDict = dict(zip(displayIndexes, displayNames))

class GlobalDisplayStylesComboBox(QComboBox):
    """
    The GlobalDisplayStylesComboBox widget provides a combobox with all 
    the standard NE1 display styles.
    """
    
    def __init__(self, parent):
        """
        Constructs a combobox with all the display styles.
        """
        QComboBox.__init__(self, parent)
        self._setup()
    
    def _setup(self, disp = diDEFAULT):
        """
        Private method. Populates self and sets the current display style.
        """
        
        if disp == diDEFAULT:
            disp = env.prefs[ defaultDisplayMode_prefs_key ]
            
        self.disconnect( self,
                         SIGNAL("currentIndexChanged(int)"),
                         self._setDisplayStyle )
        self.clear()
        
        ADD_DEFAULT_TEXT = False
        
        for displayName in displayNames:
            
            # Append "(Default)" to the item that is the global display style.
            # IMHO, this isn't needed. In fact, it is confusing to the user.
            # I suggest removing it permanantly. I will discuss with Bruce 
            # and Ninad. --Mark 2008-03-15
            if ADD_DEFAULT_TEXT:
                if displayNamesDict[disp] == displayName:
                    defaultText = " (Default)"
                else:
                    defaultText = "          "
            else:
                defaultText = ""
            iconPath = os.path.join("ui/actions/View/Display/", 
                                    displayIconsDict[displayName])
            self.addItem(geticon(iconPath), displayName + defaultText)

        self.setCurrentIndex(displayIndexes.index(disp))
        
        self.connect( self,
                      SIGNAL("currentIndexChanged(int)"),
                      self._setDisplayStyle )
    
    def getDisplayStyleIndex(self):
        """
        Returns the current global display style.
        
        @return: the current global display style (i.e. diDEFAULT, diTUBES, etc)
        @rtype:  int
        """
        return displayIndexes[self.currentIndex()]
        
    def _setDisplayStyle(self, index):
        """
        Private slot method. Only called when self's index changes (i.e when
        the user selects a new global display style via self).
        
        @param index: the combobox index
        @type  index: int
        """
        glpane = currentpart().glpane
            # Not wrongheaded IMHO since it provides an easy, consistent way
            # to get the assy and/or glpane objects. --Mark 2008-03-14
        glpane.setDisplay(displayIndexes[index])
        glpane.gl_update()
        
    def setDisplayStyle(self, disp):
        """
        Public method. Sets the display style to I{disp}.
        """
        
        if 0:# default_display:
            # This is only needed if we decide to append "(Default)" to the 
            # item in self that represents the default display style.
            self._setup(disp, default_display)
        
        # If self is already set to disp, return.
        if self.currentIndex() == displayIndexes.index(disp):
            return
        
        self.setCurrentIndex(displayIndexes.index(disp)) # Generates signal!