# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
elements.py -- elements, periodic table, element display prefs

$Id$

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
"""
__author__ = "Josh"

from VQT import *
from preferences import prefs_context
from atomtypes import AtomType

# == Elements, and periodic table

class Elem: # bruce 050510 renamed this from 'elem' (not using 'Element' since too common in strings/comments)
    """There is exactly one of these objects for each supported element in the periodic table.
    Its identity (as a python object) never changes during the run.
    Instead, if prefs changes are made in color, radius, or perhaps bonding pattern,
    this object's contents will be modified accordingly.
    """
    def __init__(self, eltnum, sym, name, mass, rvdw, color, bn):
        """called from a table in the source

        eltnum = atomic number (e.g. H is 1, C is 6); for Singlet this is 0
        sym = (e.g.) "H"
        name = (e.g.) "Hydrogen"
        mass = atomic mass in e-27 kg
        rvdw = van der Waals radius
            [warning: vdw radius is used for display, and is changeable as a display preference!
             If we ever need to use it for chemical purposes, we'll need a separate unchanging copy
             for that!]
        color = color (RGB, 0-1)
        bn = bonding info: list of triples:
             # of bonds in this form
             covalent radius (units of 0.01 Angstrom)
             info about angle between bonds, as an array of vectors
             optional 4th item in the "triple": name of this bonding pattern, if it has one
        """
        # bruce 041216 and 050510 modified the above docstring
        self.eltnum = eltnum
        self.symbol = sym
        self.name = name
        self.color = color
        self.mass = mass
        self.rvdw = rvdw
        ## self.bonds = bn # not needed anymore, I hope
        if not bn: # e.g. Helium
            bn = [[0, 0, None]]
        valence = bn[0][0]
        assert type(valence) == type(1)
        assert valence in [0,1,2,3,4,5,6,7] # in fact only up to 4 is properly supported
        self.atomtypes = map( lambda bn_triple: AtomType( self, bn_triple, valence ), bn ) # creates cyclic refs, that's ok
            # This is a public attr. Client code should not generally modify it!
            # But if we someday have add_atomtype method, it can append or insert,
            # as long as it remembers that client code treats index 0 as the default atomtype for this element.
            # Client code is not allowed to assume a given atomtype's position in this list remains constant!
        return

    def find_atomtype(self, atomtype_name): #bruce 050511
        """Given an atomtype name or fullname (or an atomtype object itself)
        for this element, return the atomtype object.
        Raise an exception (various exception types are possible)
        if no atomtype for this element matches the name (or equals the passed object).
        Given None, return this element's default atomtype object.
        """
        if not atomtype_name: # permit None or "" for now
            return self.atomtypes[0]
        for atomtype in self.atomtypes: # in order from [0], though this should not matter since at most one should match
            if atomtype.name == atomtype_name or atomtype.fullname == atomtype_name or atomtype == atomtype_name:
                return atomtype # we're not bothering to optimize for atomtype_name being the same obj we return
        assert 0, "%r is not a valid atomtype name or object for %s" % (atomtype_name, self.name)

    def __repr__(self):
        return "<Element: " + self.symbol + "(" + self.name + ")>"


class Singleton(object):
    """Base class of Singleton, each subclass will only create 1 single instance.
    Note: If subclass has __init__(), it will be called multiple times whenever
    you want to create an instance of the sub-class, although only the same
    single instance will be returned.
    """
    _singletons = {}
    def __new__(cls, *args, **kwds):
        if not cls._singletons.has_key(cls):
            cls._singletons[cls] = object.__new__(cls)
        return cls._singletons[cls]

class ElementPeriodicTable(Singleton):
    """Implement all elements related properties and functionality. Only one instance
    will be availabe for the whole application. It's better to have 'class Elem' as an
    inner class, so user will not be able to create an element him/her-self, which
    normally will cause trouble. By doing that, it makes our code more modular and
    bugs more localized, easier to test. Whenever any element color/rad changes,
    it will depend on the user who use the element to update its display---Huaicai 3/8/05
    """
    # the formations of bonds -- standard offsets
    uvec = norm(V(1,1,1))
    tetra4 = uvec * A([[1,1,1], [-1,1,-1], [-1,-1,1], [1,-1,-1]])
    tetra3 = uvec * A([[-1,1,-1], [-1,-1,1], [1,-1,-1]])
    oxy2 = A([[-1,0,0], [0.2588, -0.9659, 0]])
    tetra2 = A([[-1,0,0], [0.342, -0.9396, 0]])
    straight = A([[-1,0,0], [1,0,0]])
    flat = A([[-0.5,0.866,0], [-0.5,-0.866,0], [1,0,0]])
    onebond = A([[1,0,0]]) # for use with valence-1 elements
    
    _defaultRad_Color = {"X": (1.1,  [0.8, 0.0, 0.0]), "H" : (1.2,  [0.0, 0.6, 0.6]),
     "He" : (1.4,  [0.42, 0.45, 0.55]), "Li" : (4.0,  [0.0, 0.5, 0.5]),
     "Be" : (3.0,  [0.98, 0.67, 1.0]),  "B" : (2.0,  [0.25, 0.25, 0.7]),
     "C" : (1.84, [0.25, 0.4, 0.0]),   "N" : (1.55, [0.84, 0.37, 1.0]),
     "O" : (1.74, [0.6, 0.2, 0.2]),  "F" : (1.65, [0.0, 0.8, 0.34]),
     "Ne" : (1.82, [0.42, 0.45, 0.55]), "Na" : (4.0,  [0.0, 0.4, 0.4]),
     "Mg" : (3.0,  [0.88, 0.6, 0.9]),  "Al" : (2.5,  [0.4, 0.4, 0.75]),
     "Si" : (2.25, [0.3, 0.3, 0.3]),   "P" : (2.11, [0.4, 0.1, 0.5]),
     "S" : (2.11, [1.0, 0.65, 0.0]),  "Cl" : (2.03, [0.3, 0.5, 0.0]),
     "Ar" : (1.88, [0.42, 0.45, 0.55]),  "K" : (5.0,  [0.0, 0.3, 0.3]),
     "Ca" : (4.0,  [0.79, 0.55, 0.8]),  "Sc" : (3.7,  [0.417, 0.417, 0.511]),
     "Ti" : (3.5,  [0.417, 0.417, 0.511]),  "V" : (3.3,  [0.417, 0.417, 0.511]),
     "Cr" : (3.1,  [0.417, 0.417, 0.511]),  "Mn" : (3.0,  [0.417, 0.417, 0.511]),
     "Fe" : (3.0, [0.417, 0.417, 0.511]),  "Co" : (3.0,  [0.417, 0.417, 0.511]),
     "Ni" : (3.0,  [0.417, 0.417, 0.511]),  "Cu" : (3.0,  [0.417, 0.417, 0.511]),
     "Zn" : (2.9,  [0.417, 0.417, 0.511]),  "Ga" : (2.7,  [0.6, 0.6, 0.8]),
     "Ge" : (2.5,  [0.4, 0.45, 0.1]),   "As" : (2.2,  [0.6, 0.26, 0.7]),
     "Se" : (2.1,  [0.9, 0.35, 0.0]),  "Br" : (2.0,  [0.0, 0.4, 0.3]),
     "Kr" : (1.9,  [0.42, 0.45, 0.55]), "Sb" : (2.2,  [0.6, 0.26, 0.7]),
     "Te" : (2.1,  [0.9, 0.35, 0.0]),  "I" : (2.0,  [0.0, 0.5, 0.0]),
     "Xe" : (1.9,  [0.4, 0.45, 0.55])}
      
    _altRad_Color = {"Al" : (2.050,), "As" : (2.050,),
                        "B" :  (1.461,), "Be" :  (1.930,),
                        "Br" :  ( 1.832,), "C" : (1.431, [0.4588, 0.4588, 0.4588]),
                        "Ca" :  ( 1.274, ), "Cl" :  ( 1.688,),
                        "Co" :  ( 1.970, ), "Cr" :  ( 2.150,),
                        "Cu" :  ( 1.870,), "F" :  ( 1.293,),
                        "Fe" :  ( 2.020,),  "Ga" :  ( 2.300,),
                        "Ge" : (1.980,),  "H" :  (1.135, [1.0, 1.0, 1.0]),
                        "I" :   ( 1.967,), "K" :  ( 1.592,),
                        "Li" :  (  0.971,), "Mg" :  ( 1.154,),
                        "Mn" :  (1.274,), "N" :  ( 1.392,),
                        "Na" :  (1.287,),  "Ni" :  ( 1.920,),
                        "O" :  (1.322,), "P" :  ( 1.784,),
                        "S" :  (1.741,), "Sb" :  ( 2.200,),
                        "Se" :  (  1.881,), "Si" :  ( 1.825, [0.4353, 0.3647, 0.5216]),
                        "Ti" :  ( 2.300,)
                     }
                     
# Format of _mendeleev:
# Symbol, Element Name, atomic mass in 10-27 kg, 
# [ open bonds, covalent radius (pm), atomic geometry, hybridization ]

    _mendeleev = [("X",  "Singlet",     0.001,  [[1, 0, None, 'sp']]), #bruce 050630 made X have atomtype name 'sp'; might revise again later
                  ("H",  "Hydrogen",    1.6737, [[1, 30, onebond]]),
                  ("He", "Helium",      6.646,  None),
                  ("Li", "Lithium",    11.525,  [[1, 152, None]]),
                  ("Be", "Beryllium",  14.964,  [[2, 114, None]]),
                  ("B",  "Boron",      17.949,  [[3, 90, flat, 'sp2']]), #bruce 050706 added 'sp2' name, though all bonds are single
                  ("C",  "Carbon",     19.925,  [[4, 77, tetra4, 'sp3'],
                                                 [3, 71, flat, 'sp2'],
                                                 [2, 66, straight, 'sp'],
                                                 ## [1, 59, None]
                                                 #e name? what is this anyway?
                                                 # I don't know how it could bond... let's leave it out for now. [bruce 050510]
                                                 ]),
                  ("N",  "Nitrogen",   23.257,  [[3, 70, tetra3, 'sp3'],
                                                 [2, 62, flat[:2], 'sp2'], # bruce 050630 replaced tetra2 with flat[:2]
                                                     #e note there is also an sp2 with 3 single bonds (graphitic)... how to rep it here?
                                                 [1, 54.5, onebond, 'sp'],
                                                 [3, 62, flat, 'sp2(graphitic)'], # this is just a guess! (for graphitic N) (and the 62 is made up)
                                                 ]),
                  ("O",  "Oxygen",     26.565,  [[2, 66, oxy2, 'sp3'],
                                                 [1, 55, onebond, 'sp2']]), # sp2?
                  ("F",  "Fluorine",   31.545,  [[1, 64, onebond]]),
                  ("Ne", "Neon",       33.49,   None),
                  ("Na", "Sodium",     38.1726, [[1, 186, None]]),
                  ("Mg", "Magnesium",  40.356,  [[2, 160, None]]),
                  ("Al", "Aluminum",   44.7997, [[3, 143, flat]]),
                  ("Si", "Silicon",    46.6245, [[4, 117, tetra4]]),
                  ("P",  "Phosphorus", 51.429,  [[3, 110, tetra3]]),
                  ("S",  "Sulfur",     53.233,  [[2, 104, tetra2, 'sp3'],
                                                 [1, 104, onebond, 'sp2']]), #bruce 050706 added this, and both names; length is wrong
                  ("Cl", "Chlorine",   58.867,  [[1, 99, onebond]]),
                  ("Ar", "Argon",      66.33,   None),
                  ("K",  "Potassium",  64.9256, [[1, 231, None]]),
                  ("Ca", "Calcium",    66.5495, [[2, 197, tetra2]]),
                  ("Sc", "Scandium",   74.646,  [[3, 160, tetra3]]),
                  ("Ti", "Titanium",   79.534,  [[4, 147, tetra4]]),
                  ("V",  "Vanadium",   84.584,  [[5, 132, None]]),
                  ("Cr", "Chromium",   86.335,  [[6, 125, None]]),
                  ("Mn", "Manganese",  91.22,   [[7, 112, None]]),
                  ("Fe", "Iron",       92.729,  [[3, 124, None]]),
                  ("Co", "Cobalt",     97.854,  [[3, 125, None]]),
                  ("Ni", "Nickel",     97.483,  [[3, 125, None]]),
                  ("Cu", "Copper",    105.513,  [[2, 128, None]]),
                  ("Zn", "Zinc",      108.541,  [[2, 133, None]]),
                  ("Ga", "Gallium",   115.764,  [[3, 135, None]]),
                  ("Ge", "Germanium", 120.53,   [[4, 122, tetra4]]),
                  ("As", "Arsenic",   124.401,  [[5, 119, tetra3]]),
                  ("Se", "Selenium",  131.106,  [[6, 120, tetra2]]),
                  ("Br", "Bromine",   132.674,  [[1, 119, onebond]]),
                  ("Kr", "Krypton",   134.429,  None)
                ]
    # Antimony is element 51
    _appendix = [ ("Sb", "Antimony",  124.401,  [[3, 119, tetra3]]),
                  ("Te", "Tellurium", 131.106,  [[2, 120, tetra2]]),
                  ("I",  "Iodine",    132.674,  [[1, 119, onebond]]),
                  ("Xe", "Xenon",     134.429,  None)
                ]
    _perodicalTable = {}
    _eltName2Num = {}
    _eltSym2Num = {}
    
    def __init__(self):
        #if win: self.w = win
        if  not self._perodicalTable:
           self._createElements(0, self._mendeleev)
           self._createElements(51, self._appendix)
           #bruce 050419 add public attributes to count changes
           # to any element's color or rvdw; the only requirement is that
           # each one changes at least once per user event which
           # changes their respective attributes for one or more elements.
           self.color_change_counter = 1
           self.rvdw_change_counter = 1
           
    def _createElements(self, startIndex, elmTable):
        """Create elements for all member of <elmTable>.
        Use preference value of each element if available, otherwise, use default value.  
        <Param> startIndex: the starting element index
        <Param> elmTable: a list of elements needed to create
        """
        prefs = prefs_context()
        for elm in elmTable:
                rad_color = prefs.get(elm[0], self._defaultRad_Color[elm[0]])
                el = Elem(startIndex, elm[0], elm[1], elm[2], rad_color[0], rad_color[1], elm[3])
                startIndex += 1
                self. _perodicalTable[el.eltnum] = el
                self._eltName2Num[el.name] = el.eltnum
                self._eltSym2Num[el.symbol] = el.eltnum               
    
    def _loadTableSettings(self, elSym2rad_color, changeNotFound = True ):
        """Load a table of elements rad/color setting into the current set _perodicalTable. 
        <Param> elnum2rad_color:  A dictionary of (eleSym : (rvdw, [r,g,b])).
                [r,g,b] can be None, which requires color from default setting
        """
        self.rvdw_change_counter += 1
        self.color_change_counter += 1
        for elm in self._perodicalTable.values():
            try:
                e_symbol = elm.symbol
                rad_color = elSym2rad_color[e_symbol]
                elm.rvdw = rad_color[0]
                if len(rad_color) == 1:
                    rad_color = self._defaultRad_Color[e_symbol]
                elm.color = rad_color[1]
            except:
                if changeNotFound:
                    rad_color = self._defaultRad_Color[e_symbol]
                    elm.rvdw = rad_color[0]
                    elm.color = rad_color[1]
                pass
                    
        #self._updateModelDisplay()
                
    def loadDefaults(self):
        """Update the elements properties in the _periodicalTable as that from _defaultRad_Color"""
        self. _loadTableSettings(self._defaultRad_Color)
        
    def loadAlternates(self):
        """Update the elements properties in the _periodicalTable as that from _altRad_Color,
        if not find, load it from default."""
        self. _loadTableSettings(self._altRad_Color)
        
    def deepCopy(self):
        """Deep copy the current setting of elements rvdw/color,
        in case user cancel the modifications """
        copyPTable = {}
        for elm in self._perodicalTable.values():
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
            self._perodicalTable[elm[0]].color = [elm[1], elm[2], elm[3]]
        #self._updateModelDisplay()
    
    def setElemColor(self, eleNum, c):
        """Set element <eleNum> color as <c> """
        assert type(eleNum) == type(1)
        assert type(c) == type([1,1,1])
        self.color_change_counter += 1
        self._perodicalTable[eleNum].color = c
        #self._updateModelDisplay()
        
    def getElemColor(self, eleNum):
        """Return the element color as a triple list for <eleNum> """
        assert type(eleNum) == type(1)
        return self._perodicalTable[eleNum].color
    
    def getPTsenil(self):
        """Reverse right ends of top 4 lines for passivating """
        pTsenil = [[self._perodicalTable[2], self._perodicalTable[1]],
           [self._perodicalTable[10], self._perodicalTable[9], self._perodicalTable[8],
           self._perodicalTable[7], self._perodicalTable[6]],
           [self._perodicalTable[18], self._perodicalTable[17], self._perodicalTable[16],
           self._perodicalTable[15], self._perodicalTable[14]],
           [self._perodicalTable[36], self._perodicalTable[35], self._perodicalTable[34],
            self._perodicalTable[33], self._perodicalTable[32]]]
        return pTsenil
    
    def getAllElements(self):
        """Return the whole list of elements of periodic table as dictionary object """
        return self._perodicalTable
    
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
        return self._perodicalTable[s]
            
    def getElemRvdw(self, eleNum):
        """Return the element rvdw  for <eleNum> """
        return self._perodicalTable[eleNum].rvdw
    
    def getElemMass(self, eleNum):
        """Return the mass for element <eleNum> """
        return self._perodicalTable[eleNum].mass
    
    def getElemName(self, eleNum):
        """Return the name for element <eleNum> """
        return self._perodicalTable[eleNum].name
        
    def getElemBondCount(self, eleNum, atomtype = None): #bruce 050511 fixed for atomtype changes, added atomtype option
        """Return the number of open bonds for element <eleNum> (with no real bonds).
        If atomtype is provided, use that atomtype, otherwise use the default atomtype
        (i.e. assume all the open bonds should be single bonds).
        """
        elem = self._perodicalTable[eleNum]
        return elem.atomtypes[0].numbonds
    
    def getElemSymbol(self, eleNum):
        """ <Param> eleNum: element index
            <Return>  the symbol for the element
        """
        assert type(eleNum) == type(1)
        try:
            elem = self._perodicalTable[eleNum]
            return elem.symbol
        except:
            print "Can't find element: ", eleNum
            return None
     
    #def _updateModelDisplay(self):
    #    """Update model display """
    #     for mol in self.w.assy.molecules: 
    #        mol.changeapp(1)
        
   #      self.w.glpane.gl_update()
    
    def close(self):
          ## The 'def __del__(self)' is not guranteed to be called. It is not called in my try on Windows. 
          """Save color/radius preference before deleting"""
          prefs = prefs_context()
          elms = {}
          for elm in self._perodicalTable.values():
              elms[elm.symbol] = (elm.rvdw, elm.color)
          prefs.update(elms)
          #print "__del__() is called now."    

###Some global definitons, it's not necessary, but currently I don't want
### to change a lot of code ---Huaicai 3/9/05

PeriodicTable  = ElementPeriodicTable()
Hydrogen = PeriodicTable.getElement(1)
Carbon = PeriodicTable.getElement(6)
Nitrogen = PeriodicTable.getElement(7)
Oxygen = PeriodicTable.getElement(8)
Singlet = PeriodicTable.getElement(0)

##Test          
if __name__ == '__main__':
        pt1 = ElementPeriodicTable()
        pt2 = ElementPeriodicTable()
        
        assert pt1 == pt2
        
        assert pt1.getElement('C') == pt2.getElement(6)
        assert pt2.getElement('Oxygen') == pt1.getElement(8)
        
        print pt1.getElement(6)
        print pt1.getElement(18)
        
        print pt1.getElemSymbol(12)
        
        pt1.deepCopy()