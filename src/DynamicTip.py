# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
DynamicTip.py -- 

For the support of dynamic, informative tooltips of a highligthed object in the GLPane. 

History: 
060817 Mark created dynamicTip class
060818 Ninad moved DynamiceTip class into this file DynamicTip.py


$Id$

"""
from qt import QToolTip, QRect
import time
import env
import preferences
from prefs_constants import dynamicToolTipWakeUpDelay_prefs_key
from selectMode import *



class DynamicTip(QToolTip): # Mark and Ninad 060817.
    """For the support of dynamic, informative tooltips of a highligthed object in the GLPane. 
    """
    def __init__(self, parent):
        QToolTip.__init__(self, parent)
        self.glpane = parent
        
        # <toolTipShown> is a flag set to True when a tooltip is currently displayed for the 
        # highlighted object under the cursor.
        self.toolTipShown = False
     
    def maybeTip(self, cursorPos):
        """Determines if this tooltip should be displayed. The tooltip will be displayed at
        <cusorPos> if an object is highlighted and the mouse hasn't moved for 
        some period of time, called the "wake up delay" period, which is a user pref
        (not yet implemented in the Preferences dialog) currently set to 1 second.
        
        <cursorPos> is the current cursor position in the GLPane's local coordinates.
        
        maybeTip() is called by GLPane.timerEvent() whenever the cursor is not moving to 
        determine if the tooltip should be displayed.
        
        For more details about this member, see Qt documentation on QToolTip.maybeTip().
        """
        
        # <motionlessCursorDuration> is the amount of time the cursor (mouse) has been motionless.
        motionlessCursorDuration = time.time()- self.glpane.cursorMotionlessStartTime
        
        # Don't display the tooltip yet if <motionlessCursorDuration> hasn't exceeded the "wake up delay".
        # The wake up delay is currently set to 1 second in prefs_constants.py. Mark 060818.
        if motionlessCursorDuration < env.prefs[dynamicToolTipWakeUpDelay_prefs_key]:
            self.toolTipShown = False
            return
        
        selobj = self.glpane.selobj
        
        # If an object is not currently highlighted, don't display a tooltip.
        if not selobj:
            return
        
        # If the highlighted object is a singlet, don't display a tooltip for it.
        if isinstance(selobj, atom) and (selobj.element is Singlet):
            return
            
        if self.toolTipShown:
            # The tooltip is already displayed, so return. Do not allow tip() to be called again or it will "flash".
            #print "maybeTip(): TOOLTIP ALREADY SHOWN. highlighted object = ", str(self.glpane.selobj)
            return
            
        # Position and size of QRect for tooltip.
        rect = QRect(cursorPos.x()-1, cursorPos.y()-1, 3, 3)
        #print "maybeTip(): CREATING AND DISPLAYING TOOLTIP. highlighted object = ", str(self.glpane.selobj)
            
        tipText = self.getToolTipText()
            
        self.tip(rect, tipText) # Display the tooltip for the highlighted object <self.glpane.selobj>.
            # This should always display a tooltip when called. There are times when it will not work, at least on Windows.
            # For example, if you rest the cursor over an atom until the tooltip is displayed, then highlight a different atom,
            # then move back to the first atom and rest the cursor, the tooltip will not display. Try this again, it will work. 
            # Another time, it will not work. This appears to be a Qt bug. Not serious, however, since slightly moving and
            # resting the cursor over the same atom will cause the tooltip to appear. Mark 060817.
                
        self.toolTipShown = True
                            
                            
    def getToolTipText(self): # Mark 060818, Ninad 060818
        """Return the tooltip text to display, which depends on what is selected and what is highlighted.
        
        For now:
        Return the name of the highlighted object.
        
        For later:
        If nothing is selected, return the name of the highlighted object.
        If one atom is selected, return the distance between it and the highlighted atom.
        If two atoms are selected, return the angle between them and the highlighted atom.
        If three atoms are selected, return the torsion angle between them and the highlighted atom.
        If more than three atoms as selected, return the name of the highlighted object.
        
        Damian also suggested having preferences for setting the precision (decimal place) for each measurement.
        """
        
        #@@@@@@@ ninad060818. Replace the strings "nothing selected" etc with actual conditions
        
        from ops_select import ops_select_Mixin 
        
        glpane = self.glpane
                       
        selectedAtomList = glpane.assy.getOnlyAtomsSelectedByUser()
        selectedJigList = glpane.assy.getSelectedJigs()
        
        ppa2 = glpane.assy.ppa2 # previously picked atom
        ppa2Exists = self.lastPickedInSelAtomList(ppa2, selectedAtomList)
        
        objStr = self.getHighlightedObjectName()
        
        if len(selectedAtomList) == 0: 
            return objStr
            
        #ninad060818 Give the distance info if only one atom is selected in the glpane (and is not the highlighted one)
        #If a 'last picked' atom exists (and is still selected, then it returns distance between that last picked and highlighted
        #If the highlighted atom is also selected/last picked , only give atom info don't give '0' distance info" 
        #Known bug: If many atoms selected, if ppa2 and ppa2 exists and if ppa2 is deleted, it doesn't display the distance between 
        #highlighted and ppa3. (as of 060818 it doesn't even display the atom info ..but thats not a bug just NIY that I need to 
        #handle somewhere else. 
        elif len(selectedAtomList) == 1 or ppa2Exists:
            if self.getDistHighlightedAtomAndSelectedAtom(selectedAtomList, ppa2):
                distStr = self.getDistHighlightedAtomAndSelectedAtom(selectedAtomList, ppa2)
                print "in getDistLoop"
                #ninad060818 this decides what tooltip to display
                if isinstance(glpane.selobj, atom):
                    return objStr + "\n" + distStr
                else:
                    return objStr
            else:
                return objStr
        else:
            return objStr #@@@ ninad060818 ...if we begin to support other objects (other than jig/chunk/bonds/atoms)
                                #then we need to retirn glpane.selobj
            
        '''elif "two atoms are selected":
            if self.getAngleHighlightedAtomAndSelAtoms():
                angleStr = self.getAngleHighlightedAtomAndSelAtoms()
                distStr = self.getDistHighlightedAtomAndSelectedAtom()
                return angleStr + "\n" + distStr
                
        elif "three atoms are selected":
            self
            torsionStr = self.getTorsionHighlightedAtomAndSelAtoms()
            angleStr = self.getAngleHighlightedAtomAndSelAtoms()
            distStr = self.getDistHighlightedAtomAndSelectedAtom()
            return torsionStr + "\n" + angleStr + "\n" + distStr'''
            
        
    def getHighlightedObjectName(self): 
        "Returns the name of the highlighed object"
        from bond_constants import describe_atom_and_atomtype
        #from chem import Atom
        
        glpane = self.glpane
        
        if isinstance(glpane.selobj, atom):
            atomStr = describe_atom_and_atomtype(glpane.selobj)
            elementNameStr = " (" + glpane.selobj.element.name + ")"
            xyz = glpane.selobj.posn()
            atomposn = ("X: %.3f\nY: %.3f\nZ: %.3f" %(xyz[0], xyz[1], xyz[2]))
            return atomStr + elementNameStr + "\n" + atomposn
            
        if isinstance(glpane.selobj, Bond):
            bondStr = str(glpane.selobj)
            return bondStr
            
        if isinstance(glpane.selobj, Jig):
            jigStr = "Jig"
            return jigStr
        
        #@@@ninad060818 In future if we support other object types in glpane, do we need a check for that? 
        # e.g. else: return "unknown object" .
            
        
    def getDistHighlightedAtomAndSelectedAtom(self, selectedAtomList, ppa2): 
        
        from VQT import vlen
        """
        Returns the distance between the most recently selected object (must be still selected) and the highlighted object
        If the highlighed atom is also selected, it excludes it while finding the last selected atoms.
        If there is only one atom selected and is same as highlighed atom, then it returns None.  (then the function calling this 
        routine needs to handle that case.) 
        """
       
        glpane = self.glpane
        
        if ppa2:
            selectedAtom = ppa2 #ninad060818 This handles a case when there are many atoms selected and there still exists a 'last picked' one
        else:
            selectedAtom = selectedAtomList[0]
            
        xyz = glpane.selobj.posn()
        
        #ninad060818 No need to display disance info if highlighed object and lastpicked/ only selected object are identical
        if selectedAtom is not glpane.selobj: 
            distanceStr = ("Distance %s-%s : %.2f A"%(glpane.selobj, selectedAtom,vlen(xyz - selectedAtom.posn())))
            return distanceStr
        else:
            return False
    
    def getAngleHighlightedAtomAndSelAtoms(self): 
        """
        Returns the angle between the last two selected atoms and the current highlighted atom. 
        If the highlighed atom is also selected, it excludes it while finding the last 2 selected atoms. 
        If the highlighed atom is also one of the selected atoms and there are only 2 selected  atoms other than 
         the highlighted one then it returns None.(then the function calling this routine needs to handle that case.) 
        
        """
        return False
    
    def getTorsionHighlightedAtomAndSelAtoms(self):
        """
        Return the torsion angle between the last 3 selected atoms and the highlighed atom, 
        If the highlighed atom is also selected, it excludes it while finding the last 3 selected atoms. 
        If the highlighed atom is also one of the selected atoms and there are only 2 selected  atoms other than 
        the highlighted one then it returns None. (then the function calling this routine needs to handle that case.) 
        
        
        """
        return False
        
    def lastPickedInSelAtomList(self, ppa2,selectedAtomList):
        '''Checks whether the last atom picked (ppa2) exists in the atom list
           Returns True of False. 
        '''
        if ppa2 in selectedAtomList:
            return True
        else:
            return False
    
    def lastTwoPickedInSelAtomsList(self, ppa2,ppa3):
        '''Checks whether *both* the last two picked atoms (ppa2 and ppa3) exist in the atom list
           Returns True of False. 
        '''
    
    def lastThreePickedInSelAtomsList(self, ppa2, ppa3, ppa4):
        '''Checks whether *all*  the three picked atoms (ppa2 , ppa3 and ppa4) exist in the atom list
           Returns True of False.  Note: there is no ppa4 yet - ninad060818
        '''
        
# end