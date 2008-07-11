"""
GlobalDisplayStylesComboBox.py - Provides a combo box with all the global display
styles.

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

To do (for Mark):
- Add tooltip and What's This text.
- Change "Default Display Style" in the preferences dialog (Mode page) to
"Global Display Style at start up"
"""

import os
from PyQt4.Qt import SIGNAL, QComboBox
import foundation.env as env
from utilities.constants import diDEFAULT ,diTrueCPK, diLINES
from utilities.constants import diBALL, diTUBES, diDNACYLINDER, diPROTEIN
from utilities.prefs_constants import startupGlobalDisplayStyle_prefs_key
from utilities.icon_utilities import geticon

# Should DNA Cylinder be a global display style? Selecting it makes everything
# except DNA invisible. If we leave it in the list, we must document this 
# confusing behavior in the "What's This" text.
# --Mark 2008-03-16

displayIndexes = [diLINES, diTUBES, diBALL, diTrueCPK, diDNACYLINDER, diPROTEIN]
displayNames   = ["Lines", "Tubes", "Ball and Stick", "CPK", "DNA Cylinder", "Protein"]
displayIcons   = ["Lines", "Tubes", "Ball_and_Stick", "CPK", "DNACylinder", "Protein"]

displayIconsDict = dict(zip(displayNames, displayIcons))
displayNamesDict = dict(zip(displayIndexes, displayNames))

class GlobalDisplayStylesComboBox(QComboBox):
    """
    The GlobalDisplayStylesComboBox widget provides a combobox with all 
    the standard NE1 display styles.
    """
    
    def __init__(self, win):
        """
        Constructs a combobox with all the display styles.
        
        @param win: The NE1 mainwindow.
        @type  win: L{Ui_MainWindow}
        """
        QComboBox.__init__(self, win)
        self.win = win
        self._setup(disconnect = False)
    
    def _setup(self, display_style = diDEFAULT, disconnect = True):
        """
        Private method. Populates self and sets the current display style.
        """

        from utilities.debug_prefs import debug_pref, Choice_boolean_False
        
        # Add a new experimental Protein display style
        # if the Enable proteins debug pref is set to True.
        # piotr 080710
        from protein.model.Protein import enableProteins
            
        if display_style == diDEFAULT:
            display_style = env.prefs[ startupGlobalDisplayStyle_prefs_key ]
        
        if disconnect:
            self.disconnect( self,
                             SIGNAL("currentIndexChanged(int)"),
                             self._setDisplayStyle )
        self.clear()
        
        ADD_DEFAULT_TEXT = False
        
        for displayName in displayNames:

            # Experimental display style for Proteins.
            if displayName == "Protein" and \
               not enableProteins:
                # Skip the Proteins style.
                continue
            
            basename = displayIconsDict[displayName] + ".png"
            iconPath = os.path.join("ui/actions/View/Display/", 
                                    basename)
            self.addItem(geticon(iconPath), displayName)

        self.setCurrentIndex(displayIndexes.index(display_style))
        
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
        assert index in range(self.count())
        
        glpane = self.win.assy.glpane
        glpane.setDisplay(displayIndexes[index])
        glpane.gl_update()
        
    def setDisplayStyle(self, display_style):
        """
        Public method. Sets the display style to I{display_style}.
        
        @param display_style: display style code (i.e. diTUBES, diLINES, etc.)
        @type  display_style: int
        """
        assert display_style in displayIndexes
        
        # If self is already set to display_style, return.
        if self.currentIndex() == displayIndexes.index(display_style):
            return
        
        self.setCurrentIndex(displayIndexes.index(display_style)) # Generates signal!
