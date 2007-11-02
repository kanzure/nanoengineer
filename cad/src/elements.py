# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
elements.py -- elements, periodic table, element display prefs

@author: Josh
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:

Initially by Josh as part of chem.py.

Bruce 041221 split this module out of chem.py,
and (around then) added support for alternate color/radius tables.

Huaicai circa 050309 revised outer levels of structure, added support
for loading and saving color/radius tables into files, added preferences code.
[This comment added by bruce 050509.]

Bruce 050509 did some reformatting, corrected some out-of-date comments or
docstrings, removed some obsolete commented-out code. (Committed 050510.)

Bruce 050510 made some changes for "atomtypes" with their own bonding patterns.

Bruce 071101 split class Elem into its own module, removed Singleton superclass,
and split elements_data.py out of elements.py.

TODO:

In elements.py and Elem.py,
modularize the creation of different kinds of elements,
to help permit specialized modules and Elem/Atom subclasses
for PAM3 and PAM5 (etc). (Should we define new Elem subclasses for them?)
"""

from preferences import prefs_context
from debug_prefs import debug_pref, Choice_boolean_False, Choice_boolean_True

from Elem import Elem

from elements_data import _defaultRad_Color
from elements_data import _altRad_Color
from elements_data import _mendeleev

# ==

# _DIRECTIONAL_BOND_ELEMENTS lists the symbols of elements which permit
# "directional bonds" (between two such elements).
#
# Note: this list is private, used only when creating the Elems in the
# periodic table object. External code can look at the value of the boolean
# per-element constant, elem.bonds_can_be_directional, instead.
# [bruce 071015]

_DIRECTIONAL_BOND_ELEMENTS = ('Ss5', 'Pl5', 'Sj5', 'Pe5', 'Sh5', 'Hp5',
                              'Ss3', 'Pl3', 'Sj3', 'Se3', 'Sh3', 'Hp3')

#bruce 071018 revised menu text of the following, and made it default True;
# old text was "draw PAM3 bondpoints as directional bond arrows? (next session)"

if debug_pref("Bonds: permit directional open bonds? (next session)", 
              Choice_boolean_True, 
              non_debug = True,
              prefs_key = "A9 devel/draw PAM3 singlets as arrows"):

    # (Code by mark 071014, comment by bruce 071016:)
    # This might soon become the usual case, with the debug_pref removed.
    # Code which needs to know whether this occurred should (for now)
    # test the boolean flag Singlet.bonds_can_be_directional,
    # not the debug_pref itself.
    
    print "Adding 'X' (bondpoint) to _DIRECTIONAL_BOND_ELEMENTS tuple."
    
    _DIRECTIONAL_BOND_ELEMENTS = _DIRECTIONAL_BOND_ELEMENTS + ('X',) # mark 071014

    pass
    
# ==

class _ElementPeriodicTable(object):
    """
    Represents a table of all possible elements (including pseudoelements)
    that can be used in Atoms.

    Normally a singleton, but I [bruce 071101] don't know whether that's
    obligatory.
    """
    def __init__(self):
        self._periodicTable = {} # maps elem.eltnum to elem (elem is an instance of Elem)
        self._eltName2Num = {} # maps elem.name to elem.eltnum
        self._eltSym2Num = {} # maps elem.symbol to elem.eltnum
        
        self._createElements(_mendeleev)
        # bruce 050419 add public attributes to count changes
        # to any element's color or rvdw; the only requirement is that
        # each one changes at least once per user event which
        # changes their respective attributes for one or more elements.
        self.color_change_counter = 1
        self.rvdw_change_counter = 1
        return
           
    def _createElements(self, elmTable):
        """
        Create elements for all member of <elmTable>.
        Use preference value of each element if available, otherwise, use default value.  
        <Param> elmTable: a list of elements needed to create
        """
        prefs = prefs_context()
        for elm in elmTable:
            rad_color = prefs.get(elm[0], _defaultRad_Color[elm[0]])
            el = Elem(elm[2], elm[0], elm[1], elm[3], rad_color[0], rad_color[1], elm[4])
            self._periodicTable[el.eltnum] = el
            self._eltName2Num[el.name] = el.eltnum
            self._eltSym2Num[el.symbol] = el.eltnum
            if elm[0] in _DIRECTIONAL_BOND_ELEMENTS: #bruce 071015
                # print "_DIRECTIONAL_BOND_ELEMENTS affects", el
                el.bonds_can_be_directional = True
        return
    
    def _loadTableSettings(self, elSym2rad_color, changeNotFound = True ):
        """Load a table of elements rad/color setting into the current set _periodicTable. 
        <Param> elnum2rad_color:  A dictionary of (eleSym : (rvdw, [r,g,b])).
                [r,g,b] can be None, which requires color from default setting
        """
        self.rvdw_change_counter += 1
        self.color_change_counter += 1
        for elm in self._periodicTable.values():
            try:
                e_symbol = elm.symbol
                rad_color = elSym2rad_color[e_symbol]
                elm.rvdw = rad_color[0]
                if len(rad_color) == 1:
                    rad_color = _defaultRad_Color[e_symbol]
                elm.color = rad_color[1]
            except:
                if changeNotFound:
                    rad_color = _defaultRad_Color[e_symbol]
                    elm.rvdw = rad_color[0]
                    elm.color = rad_color[1]
                pass
        return
    
    def loadDefaults(self):
        """Update the elements properties in the _periodicalTable as that from _defaultRad_Color"""
        self. _loadTableSettings(_defaultRad_Color)
        
    def loadAlternates(self):
        """Update the elements properties in the _periodicalTable as that from _altRad_Color,
        if not find, load it from default."""
        self. _loadTableSettings(_altRad_Color)
        
    def deepCopy(self):
        """Deep copy the current setting of elements rvdw/color,
        in case user cancel the modifications """
        copyPTable = {}
        for elm in self._periodicTable.values():
            if type(elm.color) != type([1,1,1]):
                print "Error: ", elm
            copyPTable[elm.symbol] = (elm.rvdw, elm.color[:])
        return copyPTable
    
    def resetElemTable(self, elmTable):
        """Set the current table of elments setting as <elmTable> """
        self. _loadTableSettings(elmTable)
    
    def setElemColors(self, colTab):
        """Set a list of elements color 
        <param>colTab: A list of tuples in the form of <elNum, r, g, b> """
        assert type(colTab) == type([1,1, 1,1])
        self.color_change_counter += 1
        for elm in colTab:
            self._periodicTable[elm[0]].color = [elm[1], elm[2], elm[3]]
        return
    
    def setElemColor(self, eleNum, c):
        """Set element <eleNum> color as <c> """
        assert type(eleNum) == type(1)
        assert eleNum >= 0
        assert type(c) == type([1,1,1])
        self.color_change_counter += 1
        self._periodicTable[eleNum].color = c
        
    def getElemColor(self, eleNum):
        """Return the element color as a triple list for <eleNum> """
        assert type(eleNum) == type(1)
        assert eleNum >= 0
        return self._periodicTable[eleNum].color
    
    def getPTsenil(self):
        """Reverse right ends of top 4 lines for passivating """
        pTsenil = [[self._periodicTable[2], self._periodicTable[1]],
           [self._periodicTable[10], self._periodicTable[9], self._periodicTable[8],
           self._periodicTable[7], self._periodicTable[6]],
           [self._periodicTable[18], self._periodicTable[17], self._periodicTable[16],
           self._periodicTable[15], self._periodicTable[14]],
           [self._periodicTable[36], self._periodicTable[35], self._periodicTable[34],
            self._periodicTable[33], self._periodicTable[32]]]
        return pTsenil
    
    def getAllElements(self):
        """Return the whole list of elements of periodic table as dictionary object """
        return self._periodicTable
    
    def getElement(self, num_or_name_or_symbol):
        """Return the element for <num_or_name_or_symbol>,
        which is either the index, name or symbol of the element """
        s = num_or_name_or_symbol
        if s in self._eltName2Num:
            s = self._eltName2Num[s]
        elif s in self._eltSym2Num:
            s = self._eltSym2Num[s]
        elif type(s) != type(1):
            assert 0, s
        return self._periodicTable[s]
            
    def getElemRvdw(self, eleNum):
        """Return the element rvdw  for <eleNum> """
        return self._periodicTable[eleNum].rvdw
    
    def getElemMass(self, eleNum):
        """Return the mass for element <eleNum> """
        return self._periodicTable[eleNum].mass
    
    def getElemName(self, eleNum):
        """Return the name for element <eleNum> """
        return self._periodicTable[eleNum].name
        
    def getElemBondCount(self, eleNum, atomtype = None):
        """Return the number of open bonds for element <eleNum> (with no real bonds).
        If atomtype is provided, use that atomtype, otherwise use the default atomtype
        (i.e. assume all the open bonds should be single bonds).
        """
        elem = self._periodicTable[eleNum]
        return elem.atomtypes[0].numbonds
    
    def getElemSymbol(self, eleNum):
        """ <Param> eleNum: element index
            <Return>  the symbol for the element
        """
        assert type(eleNum) == type(1)
        try:
            elem = self._periodicTable[eleNum]
            return elem.symbol
        except:
            print "Can't find element: ", eleNum
            return None
     
    def close(self):
        ## The 'def __del__(self)' is not guaranteed to be called. It is not called in my try on Windows.
        """Save color/radius preference before deleting"""
        prefs = prefs_context()
        elms = {}
        for elm in self._periodicTable.values():
            elms[elm.symbol] = (elm.rvdw, elm.color)
        prefs.update(elms)
        #print "__del__() is called now."

    pass # end of class _ElementPeriodicTable

# ==

# Some global definitions

PeriodicTable  = _ElementPeriodicTable()

Hydrogen = PeriodicTable.getElement(1)
Carbon = PeriodicTable.getElement(6)
Nitrogen = PeriodicTable.getElement(7)
Oxygen = PeriodicTable.getElement(8)

Singlet = PeriodicTable.getElement(0)

# == test code

if __name__ == '__main__':
    pt1 = _ElementPeriodicTable()

    assert pt1.getElement('C') == pt1.getElement(6)
    assert pt1.getElement('Oxygen') == pt1.getElement(8)

    print pt1.getElement(6)
    print pt1.getElement(18)

    print pt1.getElemSymbol(12)

    pt1.deepCopy() # UNTESTED since Singleton superclass removed

# end
