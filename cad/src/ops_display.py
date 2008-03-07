# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_display.py provides displaySlotsMixin for MWsemantics,
with display slot methods and related helper methods.

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

mark 2008-02-02 split this out of MWsemantics.py.
"""

import foundation.env as env

# Keep these in the same order that they are defined in constants.py.
# It really helps since some lists are dependent on the display mode order.
# Mark 2008-02-13.
from constants import diDEFAULT
from constants import diINVISIBLE
from constants import diLINES
from constants import diTUBES
from constants import diBALL
from constants import diTrueCPK
from constants import diDNACYLINDER
from constants import diCYLINDER
from constants import diSURFACE

from PyQt4.Qt import Qt, QColorDialog, QColor

from utilities.Log import greenmsg, redmsg, orangemsg

from commands.ElementColors.elementColors import elementColors

elementColorsWin = None

class displaySlotsMixin:
    """
    Mixin class to provide display-related methods for class MWsemantics.
    Has slot methods and their helper methods.
    """
    # set display formats in whatever is selected,
    # or the GLPane global default if nothing is
    def dispDefault(self):
        """
        Sets the selected chunks or atoms to I{Default} display mode. 
        If nothing is selected when called, then the default display is 
        changed to the display style defined in user preferences.
        """
        self.setDisplay(diDEFAULT, True)

    def dispInvis(self):
        """
        Sets the selected chunks or atoms to I{Invisible} display mode. 
        If nothing is selected when called, then the default display is 
        changed to Invisible display mode.
        """
        self.setDisplay(diINVISIBLE)

    def dispLines(self):
        """
        Sets the selected chunks or atoms to I{Lines} display mode. 
        If nothing is selected when called, then the default display is 
        changed to Lines display mode.
        """
        self.setDisplay(diLINES)

    def dispTubes(self):
        """
        Sets the selected chunks or atoms to I{Tubes} display mode. 
        If nothing is selected when called, then the default display is 
        changed to Tubes display mode.
        """
        self.setDisplay(diTUBES)
        
    def dispBall(self): #e this slot method (here and in .ui file) renamed from dispCPK to dispBall [bruce 060607]
        """
        Sets the selected chunks or atoms to I{Ball and Stick} display mode. 
        If nothing is selected when called, then the default display is 
        changed to Ball and Stick display mode.
        """
        self.setDisplay(diBALL)
        
    def dispCPK(self): #e this slot method (here and in .ui file) renamed from dispVdW to dispCPK [bruce 060607]
        """
        Sets the selected chunks or atoms to I{CPK} (space fill) display mode. 
        If nothing is selected when called, then the default display is 
        changed to CPK display mode.
        """
        self.setDisplay(diTrueCPK)
        
    def dispDnaCylinder(self):
        """
        Sets the selected chunks to I{DNA Cylinder} display mode. If nothing
        is selected, then the default display is changed to DNA Cylinder
        display mode.
        """
        # This code was copied from dispCylinder(). Mark 2008-02-13.
        cmd = greenmsg("Set Display DNA Cylinder: ")
        if self.assy and self.assy.selatoms:
            env.history.message(cmd + "Selected atoms cannot have their display mode set to DNA Cylinder.")
            return
        self.setDisplay(diDNACYLINDER)

    def dispCylinder(self):
        """
        Sets the selected chunks to I{Cylinder} display mode. If nothing
        is selected, then the default display is changed to Cylinder
        display mode.
        
        @note: I{Cylinder} is an experimental display style. It is disabled
        by default. It can be enabled setting the debug (menu) pref
        "enable CylinderChunks next session?" to True.
        """
        cmd = greenmsg("Set Display Cylinder: ")
        if self.assy and self.assy.selatoms:
            # Fixes bug 2005. Mark 060702.
            env.history.message(cmd + "Selected atoms cannot have their display mode set to Cylinder.")
            return #ninad 061003  fixed bug 2286... Note: Once atoms and chunks are allowed to be sel at the same 
            #time , this fix might need further mods. 
        self.setDisplay(diCYLINDER)
    
    def dispSurface(self):
        """
        Sets the selected chunks to I{Surface} display mode. If nothing
        is selected, then the default display is changed to Surface
        display mode.
        
        @note: I{Surface} is an experimental display style. It is disabled
        by default. It can be enabled setting the debug (menu) pref
        "enable CylinderChunks next session?" to True.
        """
        cmd = greenmsg("Set Display Surface: ")
        if self.assy and self.assy.selatoms:
            # Fixes bug 2005. Mark 060702.
            env.history.message(cmd + "Selected atoms cannot have their display mode set to Surface.")
            return #ninad 061003 fixed bug 2286
        self.setDisplay(diSURFACE)
        
    def dispHybrid(self): #@@ Ninad 070308
        print "Hybrid display is  Implemented yet"
        pass
    
    # Hide/unhide 
    def dispHide(self):
        """
        Slot for "Hide" which hides the current selection. 
        This operation works on atoms, chunks and/or any other object that
        can be hidden.
        """
        self.assy.hideSelection()
        
    def dispUnhide(self):
        """
        Slot for "Unhide" which unhides the current selection. 
        This operation works on atoms, chunks and/or any other object that
        can be hidden.
        """
        self.assy.unhideSelection()

    def setDisplay(self, form, default_display = False):
        """
        Set the display of the selection to 'form'.  If nothing is selected, then change
        the GLPane's current display to 'form'.
        """
        if self.assy and self.assy.selatoms:
            for ob in self.assy.selatoms.itervalues():
                ob.setDisplay(form)
        elif self.assy and self.assy.selmols:
            for ob in self.assy.selmols:
                ob.setDisplay(form)
        else:
            if self.glpane.displayMode == form:
                pass ## was 'return' # no change needed
                # bruce 041129 removing this optim, tho correct in theory,
                # since it's not expensive to changeapp and repaint if user
                # hits a button, so it's more important to fix any bugs that
                # might be in other code failing to call changeapp when needed.
            self.glpane.setDisplay(form, default_display) # See docstring for info about default_display
        self.win_update() # bruce 041206, needed for model tree display mode icons, as well as glpane
        return
    
    def dispObjectColor(self, initialColor = None):
        """
        Sets the color of the selected chunks and/or jigs to a color the user 
        chooses.

        @param initialColor: the initial color to display in the color chooser
                             dialog, or None or missing to use the default (white).
                             Not used if only one chunk or one jig is selected
                             (in those cases the object's current color is used).
        @type  initialColor: QColor

        @note: Need better method name (i.e. setObjectColor()).
        """        
        if initialColor is None:
            initialColor = Qt.white
        else:
            assert isinstance(initialColor, QColor)
        
        _cmd = greenmsg("Change Color: ")

        from ops_select import objectSelected, ATOMS, CHUNKS, JIGS
        if not objectSelected(self.assy, objectFlags = CHUNKS | JIGS):
            if objectSelected(self.assy, objectFlags = ATOMS):
                _msg = redmsg("Cannot change color of individual atoms.")
            else:
                _msg = redmsg("Nothing selected.")
            env.history.message(_cmd + _msg)
            return

        _numSelectedObjects = self.assy.getNumberOfSelectedChunks() \
                            + self.assy.getNumberOfSelectedJigs()

        if _numSelectedObjects == 1 and self.assy.getNumberOfSelectedChunks() == 1:
            # If only one object is selected, and it's a chunk, 
            # assign initialColor its color.
            _selectedChunkColor = self.assy.selmols[0].color
            if _selectedChunkColor:
                from widgets.widget_helpers import RGBf_to_QColor
                initialColor = RGBf_to_QColor(_selectedChunkColor)

        elif _numSelectedObjects == 1 and self.assy.getNumberOfSelectedJigs() == 1:
            # If only one object is selected, and it's a jig, 
            # assign initialColor its color.
            _selectedJig = self.assy.getSelectedJigs()
            _selectedJigColor = _selectedJig[0].normcolor
            if _selectedJigColor:
                from widgets.widget_helpers import RGBf_to_QColor
                initialColor = RGBf_to_QColor(_selectedJigColor)

        _c = QColorDialog.getColor(initialColor, self)
        if _c.isValid():
            from widgets.widget_helpers import QColor_to_RGBf
            _newColor = QColor_to_RGBf(_c)
            list = []
            for ob in self.assy.selmols:
                ob.setcolor(_newColor)
                list.append(ob)

            for ob in self.assy.getSelectedJigs():
                ob.color = _newColor # Need jig.setColor() method! --mark
                ob.normcolor =  _newColor
                list.append(ob)

            # Ninad 070321: Since the chunk is selected as a colored selection, 
            # it should be unpicked after changing its color. 
            # The user has most likely selected the chunk to change its color 
            # and won't like it still shown 'green'(the selection color) 
            # even after changing the color. so deselect it. 	
            # The chunk is NOT unpicked IF the color is changed via chunk 
            # property dialog. see ChunkProp.change_chunk_color for details.
            # This is intentional.

            for ob in list: 		
                ob.unpick()

            self.win_update()

    def dispResetChunkColor(self):
        """
        Resets the selected chunk's atom colors to the current element colors.
        """
        if not self.assy.selmols: 
            env.history.message(redmsg("Reset Chunk Color: No chunks selected."))
            return

        for chunk in self.assy.selmols:
            chunk.setcolor(None)
        self.glpane.gl_update()

    def dispResetAtomsDisplay(self):
        """
        Resets the display setting for each atom in the selected chunks or
        atoms to Default display mode.
        """

        cmd = greenmsg("Reset Atoms Display: ")
        msg = "No atoms or chunks selected."

        if self.assy.selmols: 
            self.assy.resetAtomsDisplay()
            msg = "Display setting for all atoms in selected chunk(s) reset" \
                " to Default (i.e. their parent chunk's display mode)."

        if self.assy.selectionContainsAtomsWithOverriddenDisplay():
            for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display != diDEFAULT:
                    a.setDisplay(diDEFAULT)

            msg = "Display setting for all selected atom(s) reset to Default" \
                " (i.e. their parent chunk's display mode)."

        env.history.message(cmd + msg)

    def dispShowInvisAtoms(self):
        """
        Resets the display setting for each invisible atom in the selected
        chunks or atoms to Default display mode.
        """

        cmd = greenmsg("Show Invisible Atoms: ")

        if not self.assy.selmols and not self.assy.selatoms:
            msg = "No atoms or chunks selected."
            env.history.message(cmd + msg)
            return

        nia = 0 # nia = Number of Invisible Atoms

        if self.assy.selmols:
            nia = self.assy.showInvisibleAtoms()

        if self.assy.selectionContainsInvisibleAtoms():
            for a in self.assy.selatoms.itervalues(): #bruce 060707 itervalues
                if a.display == diINVISIBLE: 
                    a.setDisplay(diDEFAULT)
                    nia += 1

        msg = cmd + str(nia) + " invisible atoms found."
        env.history.message(msg)

    def changeBackgroundColor(self):
        """
        Let user change the background color of the 3D Graphics Area,
        aka "the glpane" to the developers.
        """
        self.userPrefs.showDialog(pagename='General')

    # pop up Element Color Selector dialog
    def dispElementColorSettings(self):
        """
        Slot for 'Display > Element Color Settings...' menu item.
        """
        self.showElementColorSettings()

    def showElementColorSettings(self, parent = None):
        """
        Opens the Element Color Setting dialog, allowing the user to change 
        default colors of elements and bondpoints, and save them to a file.

        @param parent: The parent of the Element Color Setting dialog.
                       This allows the caller (i.e. Preferences dialog) to 
                       make it modal.
        @type  parent: U{B{QDialog}<http://doc.trolltech.com/4/qdialog.html>}
        """
        global elementColorsWin
        # Huaicai 2/24/05: Create a new element selector window each time,  
        # so it will be easier to always start from the same states.
        # Make sure only a single element window is shown
        if elementColorsWin and elementColorsWin.isVisible(): 
            return 

        if not parent:
            parent = self

        elementColorsWin = elementColors(parent)
        elementColorsWin.setDisplay(self.Element)
        # Sync the thumbview bg color with the current mode's bg color.  Mark 051216.
        elementColorsWin.elemGLPane.setBackgroundColor(
            self.glpane.backgroundColor, 
            self.glpane.backgroundGradient
        )
        elementColorsWin.show()

    def dispLighting(self):
        """
        Allows user to change lighting brightness.
        """
        self.userPrefs.showDialog('Lighting') # Show Preferences | Lighting.

    pass # end of class displaySlotsMixin

# end
