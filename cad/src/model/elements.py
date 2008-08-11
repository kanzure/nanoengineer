# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
elements.py -- elements, periodic table, element display prefs

@author: Josh
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

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

Bruce 071105 modularized the creation of different kinds of elements,
except for the central list of all the kinds in this file (implicit
in the list of init_xxx_elements functions we call),
so chemical, PAM3, and PAM5 elements are created by separate modules.

Bruce 071106 removed a few useless and unused methods (one of which
had a bug -- getElemBondCount didn't honor its atomtype argument).
To access public attributes of elements, just use getElement()
and then access the attribute directly.
"""

from foundation.preferences import prefs_context

from model.Elem import Elem
from model.atomtypes import AtomType

from model.elements_data import init_chemical_elements
from model.elements_data_other import init_other_elements

from dna.model.elements_data_PAM3 import init_PAM3_elements
from dna.model.elements_data_PAM5 import init_PAM5_elements

# ==

class _ElementPeriodicTable(object):
    """
    Represents a table of all possible elements (including pseudoelements)
    that can be used in Atoms. (Initially contains no elements; caller
    should add all the ones it needs before use, by calling
    addElements one or more times.)

    Normally used as a singleton, but I [bruce 071101] don't know whether
    that's obligatory.
    """
    def __init__(self):
        self._periodicTable = {} # maps elem.eltnum to elem (an Elem)
        self._eltName2Num = {} # maps elem.name to elem.eltnum
        self._eltSym2Num = {} # maps elem.symbol to elem.eltnum
        #bruce 071105 added the color tables:
        self._defaultRadiusAndColor = {} # maps elem.symbol to (radius, color) pairs
        self._alternateRadiusAndColor = {} # alternate rad/color values (ok if incomplete)
                
        # bruce 050419 add public attributes to count changes
        # to any element's color or rvdw; the only requirement is that
        # each one changes at least once per user event which
        # changes their respective attributes for one or more elements.
        self.color_change_counter = 1
        self.rvdw_change_counter = 1
        return

    def addElements(self,
                    elmTable,
                    defaultRadiusAndColor,
                    alternateRadiusAndColor,
                    atomTypeData,
                    directional_bond_elements = (),
                    default_options = {}
                   ):
        #bruce 071105 modified from def _createElements(self, elmTable):
        """
        Create elements for all members of <elmTable> (list of tuples).
        (Ok to call this more than once for non-overlapping elmTables
        (unique element symbols).
        
        Use preference value for radius and color of each element,
        if available (using element symbol as prefs key);
        otherwise, use values from defaultRadiusAndColor dictionary,
        which must have values for all element symbols in elmTable.
        (Make sure it has the value, even if we don't need it due to prefs.)

        Also store all values in defaultRadiusAndColor, alternateRadiusAndColor tables
        for later use by loadDefaults or loadAlternates methods.
        
        @param elmTable: a list of elements to create, as tuples of a format
                         documented in elements_data.py.

        @param defaultRadiusAndColor: a dictionary of radius, color pairs,
                                  indexed by element symbol. Must be complete.
                                  Used now when not overridden by prefs.
                                  Stored for optional later use by loadDefaults.

        @param alternateRadiusAndColor: an alternate dictionary of radius, color pairs.
                              Need not be complete; missing entries are
                              effectively taken from defaultRadiusAndColor.
                              Stored for optional later use by loadAlternates.

        @param atomTypeData: array of initialization data for each
                             AtomType.  See description in elements_data.py.

        @param directional_bond_elements: a list of elements in elmTable
                                           which support directional bonds.
        """
        prefs = prefs_context()
        symbols = {}
        for elm in elmTable:
            options = dict(default_options)
            assert len(elm) in (5, 6)
            if len(elm) >= 6:
                options.update(elm[5])
            symbols[elm[0]] = 1 # record element symbols seen in this call
            rad_color = prefs.get(elm[0], defaultRadiusAndColor[elm[0]])
            el = Elem(elm[2], elm[0], elm[1], elm[3],
                      rad_color[0], rad_color[1], elm[4],
                      ** options)
            assert not self._periodicTable.has_key(el.eltnum), \
                   "duplicate def of element number %r (prior: %r)" % \
                   (el.eltnum, self._periodicTable[el.eltnum] )
            assert not self._eltName2Num.has_key(el.name), \
                   "duplicate def of element name %r" % (el.name,)
            assert not self._eltSym2Num.has_key(el.symbol), \
                   "duplicate def of element symbol %r" % (el.symbol,)
            self._periodicTable[el.eltnum] = el
            self._eltName2Num[el.name] = el.eltnum
            self._eltSym2Num[el.symbol] = el.eltnum
            if elm[0] in directional_bond_elements: #bruce 071015
                # TODO: put this in the options field? or infer it from
                # pam and role?
                el.bonds_can_be_directional = True
            assert el.bonds_can_be_directional == (el.symbol == 'X' or el.role == 'strand')
                # once this works, we can clean up the code to not hardcode those list args
                # [bruce 080117]
        for key in defaultRadiusAndColor.iterkeys():
            assert key in symbols
        for key in alternateRadiusAndColor.iterkeys():
            assert key in symbols
        self._defaultRadiusAndColor.update(defaultRadiusAndColor)
        self._alternateRadiusAndColor.update(alternateRadiusAndColor)

        for aType in atomTypeData:
            at_symbol = aType[0]
            at_hybridizationName = aType[1]
            at_formalCharge = aType[2]
            at_electronsNeeded = aType[3]
            at_electronsProvided = aType[4]
            at_covalentRadius = aType[5]
            at_geometry = aType[6]

            elt = self.getElement(at_symbol)

            elt.addAtomType(AtomType(elt,
                                     at_hybridizationName,
                                     at_formalCharge,
                                     at_electronsNeeded,
                                     at_electronsProvided,
                                     at_covalentRadius,
                                     at_geometry));

        return
    
    def _loadTableSettings(self, elSym2rad_color ):
        """
        Load a table of element radius/color settings into self. 

        @param elSym2rad_color: A dictionary of (eleSym : (rvdw, [r,g,b])).
                [r,g,b] can be None or missing, in which case use color from
                self._defaultRadiusAndColor; or the entire entry for eleSym
                can be missing, in which case use both color and radius
                from self._defaultRadiusAndColor.
        """
        self.rvdw_change_counter += 1
        self.color_change_counter += 1
        for elm in self._periodicTable.values():
            # TODO: recode this to not use try/except to test the table format
            try:
                e_symbol = elm.symbol
                rad_color = elSym2rad_color[e_symbol]
                elm.rvdw = rad_color[0]
                if len(rad_color) == 1:
                    rad_color = self._defaultRadiusAndColor[e_symbol]
                elm.color = rad_color[1]
                    # guess: this is what will routinely fail if [r,g,b] is None
            except:                
                rad_color = self._defaultRadiusAndColor[e_symbol]
                elm.rvdw = rad_color[0]
                elm.color = rad_color[1]
                pass
        return
    
    def loadDefaults(self):
        """
        Update the elements properties in self from self._defaultRadiusAndColor.
        """
        self. _loadTableSettings( self._defaultRadiusAndColor)
        
    def loadAlternates(self):
        """
        Update the elements properties in self from self._alternateRadiusAndColor;
        for missing or partly-missing values, use self._defaultRadiusAndColor.
        """
        self. _loadTableSettings( self._alternateRadiusAndColor)
        
    def deepCopy(self):
        """
        Deep copy the current settings of element rvdw/color,
        and return in a form that can be passed to resetElemTable.
        Typical use is in case user cancels modifications being done
        by an interactive caller which can edit this table.
        """
        copyPTable = {}
        for elm in self._periodicTable.values():
            if type(elm.color) != type([1, 1, 1]):
                print "Error: ", elm
            copyPTable[elm.symbol] = (elm.rvdw, elm.color[:])
        return copyPTable
    
    def resetElemTable(self, elmTable):
        """
        Set the current table of element settings to equal those in <elmTable>
        """
        self._loadTableSettings(elmTable)
    
    def setElemColors(self, colTab):
        """
        Set a list of element colors. 

        @param colTab: A list of tuples in the form of <elNum, r, g, b>
        """
        assert type(colTab) == type([1, 1, 1, 1])
        self.color_change_counter += 1
        for elm in colTab:
            self._periodicTable[elm[0]].color = [elm[1], elm[2], elm[3]]
        return
    
    def setElemColor(self, eleNum, c):
        """
        Set element <eleNum> color as <c>
        """
        assert type(eleNum) == type(1)
        assert eleNum >= 0
        assert type(c) == type([1, 1, 1])
        self.color_change_counter += 1
        self._periodicTable[eleNum].color = c
        
    def getElemColor(self, eleNum):
        """
        Return the element color as a triple list for <eleNum>
        """
        assert type(eleNum) == type(1)
        assert eleNum >= 0
        return self._periodicTable[eleNum].color
    
    def getPTsenil(self):
        """
        Return a nested list of elements for use in Passivate,
        consisting of the reversed right ends of the top 4 rows (?)
        of the standard periodic table of the chemical elements.
        """
        pTsenil = [
            [self._periodicTable[2], self._periodicTable[1]],
            
            [self._periodicTable[10], self._periodicTable[9],
             self._periodicTable[8], self._periodicTable[7],
             self._periodicTable[6]],
            
            [self._periodicTable[18], self._periodicTable[17],
             self._periodicTable[16], self._periodicTable[15],
             self._periodicTable[14]],
            
            [self._periodicTable[36], self._periodicTable[35],
             self._periodicTable[34], self._periodicTable[33],
             self._periodicTable[32]]
         ]
        return pTsenil
    
    def getAllElements(self):
        """
        Return the whole list of elements of periodic table as a dictionary.
        The caller should not modify this dictionary.
        """
        return self._periodicTable
    
    def getElement(self, num_or_name_or_symbol):
        """
        Return the element for <num_or_name_or_symbol>,
        which is either the index, name or symbol of the element.
        """
        s = num_or_name_or_symbol
        if s in self._eltName2Num:
            s = self._eltName2Num[s]
        elif s in self._eltSym2Num:
            s = self._eltSym2Num[s]
        elif type(s) != type(1):
            assert 0, "don't recognize element name or symbol %r" % (s,)
        return self._periodicTable[s]
            
    def close(self):
        # The 'def __del__(self)' is not guaranteed to be called.
        # It is not called in my try on Windows. [Huaicai]
        """
        Save color/radius preference before deleting
        """
        prefs = prefs_context()
        elms = {}
        for elm in self._periodicTable.values():
            elms[elm.symbol] = (elm.rvdw, elm.color)
        prefs.update(elms)
        #print "__del__() is called now."

    pass # end of class _ElementPeriodicTable

# ==

# init code and global definitions

PeriodicTable  = _ElementPeriodicTable() # initially empty

init_chemical_elements( PeriodicTable) # including Singlet == element 0

init_other_elements( PeriodicTable)

init_PAM3_elements( PeriodicTable)
init_PAM5_elements( PeriodicTable)


Hydrogen = PeriodicTable.getElement(1)
Carbon = PeriodicTable.getElement(6)
Nitrogen = PeriodicTable.getElement(7)
Oxygen = PeriodicTable.getElement(8)

Singlet = PeriodicTable.getElement(0)

Vs0 = PeriodicTable.getElement('Vs0') #bruce 080520

Pl5 = PeriodicTable.getElement('Pl5') #bruce 080312 for convertToPam3plus5
Ss5 = PeriodicTable.getElement('Ss5')
Ax5 = PeriodicTable.getElement('Ax5')
Gv5 = PeriodicTable.getElement('Gv5')

Ss3 = PeriodicTable.getElement('Ss3')
Ax3 = PeriodicTable.getElement('Ax3')

# == test code

if __name__ == '__main__':
    # UNTESTED since Singleton superclass removed or init code revised [071105]
    pt1 = _ElementPeriodicTable()
    init_chemical_elements( PeriodicTable)

    assert pt1.getElement('C') == pt1.getElement(6)
    assert pt1.getElement('Oxygen') == pt1.getElement(8)

    print pt1.getElement(6)
    print pt1.getElement(18)

    pt1.deepCopy() 

# end
