# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.

"""
elements.py -- elements, periodic table, element display prefs

[bruce 041221 split this module out of chem.py]

$Id$
"""
__author__ = "Josh"

from VQT import *

# == Elements, and periodic table

Elno = 0

class elem:
    """one of these for each element type --
    warning, order of creation matters, since it sets eltnum member!"""
    def __init__(self, sym, n, m, rv, col, bn):
        """called from a table in the source
        
        sym = (e.g.) "H"
        n = (e.g.) "Hydrogen"
        m = atomic mass in e-27 kg
        rv = van der Waals radius
        col = color (RGB, 0-1)
        bn = bonding info: list of triples:
             # of bonds in this form
             covalent radius (units of 0.01 Angstrom)
             info about angle between bonds, as an array of vectors
        """
        # bruce 041216 modified the above docstring
        global Elno
        self.eltnum = Elno
        Elno += 1
        self.symbol = sym
        self.name = n
        self.color = col
        self.mass = m
        self.rvdw = rv
        self.rcovalent = bn and bn[0][1]/100.0
        if not self.rcovalent:
            self.rcovalent = 0.0
        # (Note: rcovalent used to be None for nonbonding elements like Helium,
        # which made most uses of it errors (e.g. when drawing bonds to Helium).
        # Once we decided such bonds should be allowed to exist, we made it act
        # like 0.0 in the drawing code, then replaced that with this more
        # general change to 0.0, hoping to avoid possible other (hypothetical)
        # bugs. As far as I know this is ok, but I have not fully analyzed every
        # possible consequence of this change. [bruce 041217])
        self.bonds = bn
        self.numbonds = bn and bn[0][0]
        if not self.numbonds:
            self.numbonds = 0 # similar reason as above [bruce 041217]
        self.base = None
        self.quats = [] # ends up one shorter than self.numbonds [bruce 041217]
        if bn and bn[0][2]:
            s = bn[0][2][0]
            self.base = s
            for v in bn[0][2][1:]:
                self.quats += [Q(s,v)]

    def __repr__(self):
        return "<Element: " + self.symbol + "(" + self.name + ")>"

# the formations of bonds -- standard offsets
uvec = norm(V(1,1,1))
tetra4 = uvec * A([[1,1,1], [-1,1,-1], [-1,-1,1], [1,-1,-1]])
tetra3 = uvec * A([[-1,1,-1], [-1,-1,1], [1,-1,-1]])
oxy2 = A([[-1,0,0], [0.2588, -0.9659, 0]])
tetra2 = A([[-1,0,0], [0.342, -0.9396, 0]])
straight = A([[-1,0,0], [1,0,0]])
flat = A([[-0.5,0.866,0], [-0.5,-0.866,0], [1,0,0]])

onebond = A([[1,0,0]]) # for use with valence-1 elements
# [bruce 041119-23; Josh has reviewed "onebond", and approves it in principle]
#e [note that this one-bond-direction is in model space; it might be better to
#   change the code that deposits "onebond" atoms to always use screen-right]
#      sym   name          mass    rVdW  color
#      [[Nbonds, radius, angle] ...]
Mendeleev=[ \
 elem("X", "Singlet",      0.001,  1.1,  [0.8, 0.0, 0.0],
      [[1, 0, None]]),
# elem("H",  "Hydrogen",    1.6737, 1.135,  [1.0, 1.0, 1.0],  # John Burch values - Mark [04-12-05]
 elem("H",  "Hydrogen",    1.6737, 1.2,  [0.0, 0.6, 0.6], # Original values
      [[1, 30, onebond]]),
 elem("He", "Helium",      6.646,  1.4,  [0.42, 0.45, 0.55],
      None),
 elem("Li", "Lithium",    11.525,  4.0,  [0.0, 0.5, 0.5],
      [[1, 152, None]]),
 elem("Be", "Beryllium",  14.964,  3.0,  [0.98, 0.67, 1.0],
      [[2, 114, None]]),
# elem("B",  "Boron",      17.949,  1.64,  [0.5, 0.5, 0.0], # John Burch values
 elem("B",  "Boron",      17.949,  2.0,  [0.25, 0.25, 0.7], # Original values
      [[3, 90, flat]]),
# elem("C",  "Carbon",     19.925,  1.462, [0.46, 0.46, 0.46], # John Burch values
 elem("C",  "Carbon",     19.925,  1.84, [0.25, 0.4, 0.0], # Original values
      [[4, 77, tetra4], [3, 71, flat], [2, 66, straight], [1, 59, None]]),
# elem("N",  "Nitrogen",   23.257,  1.4, [0.25, 0.25, 0.7], # John Burch values
 elem("N",  "Nitrogen",   23.257,  1.55, [0.84, 0.37, 1.0], # Original values
      [[3, 70, tetra3], [2, 62, tetra2], [1, 54.5, None] ]),
# elem("O",  "Oxygen",     26.565,  1.32, [0.6, 0.2, 0.2], # John Burch values
 elem("O",  "Oxygen",     26.565,  1.74, [0.6, 0.2, 0.2], # Original values
      [[2, 66, oxy2], [1, 55, None]]),
 elem("F",  "Fluorine",   31.545,  1.65, [0.0, 0.8, 0.34],
      [[1, 64, onebond]]),
 elem("Ne", "Neon",       33.49,   1.82, [0.42, 0.45, 0.55],
      None),
 elem("Na", "Sodium",     38.1726, 4.0,  [0.0, 0.4, 0.4],
      [[1, 186, None]]),
 elem("Mg", "Magnesium",  40.356,  3.0,  [0.88, 0.6, 0.9],
      [[2, 160, None]]),
 elem("Al", "Aluminum",   44.7997, 2.5,  [0.4, 0.4, 0.75],
      [[3, 143, flat]]),
# elem("Si", "Silicon",    46.6245, 1.825, [0.42, 0.36, 0.5], # John Burch values
 elem("Si", "Silicon",    46.6245, 2.25, [0.3, 0.3, 0.3], # Original values
      [[4, 117, tetra4]]),
 elem("P",  "Phosphorus", 51.429,  2.11, [0.4, 0.1, 0.5],
      [[3, 110, tetra3]]),
 elem("S",  "Sulfur",     53.233,  2.11, [1.0, 0.65, 0.0],
      [[2, 104, tetra2]]),
 elem("Cl", "Chlorine",   58.867,  2.03, [0.3, 0.5, 0.0],
      [[1, 99, onebond]]),
 elem("Ar", "Argon",      66.33,   1.88, [0.42, 0.45, 0.55],
      None),
 # not used after this
 elem("K",  "Potassium",  64.9256, 5.0,  [0.0, 0.3, 0.3],
      [[1, 231, None]]),
 elem("Ca", "Calcium",    66.5495, 4.0,  [0.79, 0.55, 0.8],
      [[2, 197, tetra2]]),
 elem("Sc", "Scandium",   74.646,  3.7,  [0.417, 0.417, 0.511],
      [[3, 160, tetra3]]),
 elem("Ti", "Titanium",   79.534,  3.5,  [0.417, 0.417, 0.511],
      [[4, 147, tetra4]]),
 elem("V",  "Vanadium",   84.584,  3.3,  [0.417, 0.417, 0.511],
      [[5, 132, None]]),
 elem("Cr", "Chromium",   86.335,  3.1,  [0.417, 0.417, 0.511],
      [[6, 125, None]]),
 elem("Mn", "Manganese",  91.22,   3.0,  [0.417, 0.417, 0.511],
      [[7, 112, None]]),
 elem("Fe", "Iron",       92.729,  3.0,  [0.417, 0.417, 0.511],
      [[3, 124, None]]),
 elem("Co", "Cobalt",     97.854,  3.0,  [0.417, 0.417, 0.511],
      [[3, 125, None]]),
 elem("Ni", "Nickel",     97.483,  3.0,  [0.417, 0.417, 0.511],
      [[3, 125, None]]),
 elem("Cu", "Copper",    105.513,  3.0,  [0.417, 0.417, 0.511],
      [[2, 128, None]]),
 elem("Zn", "Zinc",      108.541,  2.9,  [0.417, 0.417, 0.511],
      [[2, 133, None]]),
 elem("Ga", "Gallium",   115.764,  2.7,  [0.6, 0.6, 0.8],
      [[3, 135, None]]),
# elem("Ge", "Germanium", 120.53,   1.980,  [0.4, 0.45, 0.1], # John Burch values
 elem("Ge", "Germanium", 120.53,   2.5,  [0.4, 0.45, 0.1], # Original values
      [[4, 122, tetra4]]),
 elem("As", "Arsenic",   124.401,  2.2,  [0.6, 0.26, 0.7],
      [[5, 119, tetra3]]),
 elem("Se", "Selenium",  131.106,  2.1,  [0.9, 0.35, 0.0],
      [[6, 120, tetra2]]),
 elem("Br", "Bromine",   132.674,  2.0,  [0.0, 0.4, 0.3],
      [[1, 119, onebond]]),
 elem("Kr", "Krypton",   134.429,  1.9,  [0.42, 0.45, 0.55],
      None)]

# Antimony is element 51
appendix = [
 elem("Sb", "Antimony",   124.401,  2.2,  [0.6, 0.26, 0.7],
      [[3, 119, tetra3]]),
 elem("Te", "Tellurium",  131.106,  2.1,  [0.9, 0.35, 0.0],
      [[2, 120, tetra2]]),
 elem("I", "Iodine",   132.674,  2.0,  [0.0, 0.5, 0.0],
      [[1, 119, onebond]]),
 elem("Xe", "Xenon",   134.429,  1.9,  [0.4, 0.45, 0.55],
      None)]

# note mass is in e-27 kg, not amu

# the elements, indexed by symbol (H, C, O ...)
PeriodicTable={}
EltNum2Sym={}
EltName2Num={}
EltSym2Num={}
for el in Mendeleev:
    PeriodicTable[el.eltnum] = el
    EltNum2Sym[el.eltnum] = el.symbol
    EltName2Num[el.name] = el.eltnum
    EltSym2Num[el.symbol] = el.eltnum

Elno = 51
for el in appendix:
    PeriodicTable[el.eltnum] = el
    EltNum2Sym[el.eltnum] = el.symbol
    EltName2Num[el.name] = el.eltnum
    EltSym2Num[el.symbol] = el.eltnum
    

Hydrogen = PeriodicTable[1]
Carbon = PeriodicTable[6]
Nitrogen = PeriodicTable[7]
Oxygen = PeriodicTable[8]

Singlet = PeriodicTable[0]

# reversed right ends of top 4 lines for passivating
PTsenil = [[PeriodicTable[2], PeriodicTable[1]],
           [PeriodicTable[10], PeriodicTable[9], PeriodicTable[8],
            PeriodicTable[7], PeriodicTable[6]],
           [PeriodicTable[18], PeriodicTable[17], PeriodicTable[16],
            PeriodicTable[15], PeriodicTable[14]],
           [PeriodicTable[36], PeriodicTable[35], PeriodicTable[34],
            PeriodicTable[33], PeriodicTable[32]]]

# ==

# Klugy facility for Alpha to permit more than one choice of atom radii and colors.
#
# We represent a set of prefs for that as some sort of dict, of which we here create
# two instances, in a hardcoded way; instance 1 from the code's element table above,
# instance 2 from values desired by John Burch for his animation.
# (Having more instances, or reading one of these from a file, would not be hard to add later.)
#
# Then we provide commands to change which set of prefs we're using, and update things accordingly.
#
# Maybe we'll also add a change of radius display ratio... that's not here yet though.
#
# -- bruce 041221

def sym_or_name_or_num_to_num(sym_or_name_or_num):
    "given 'H' or 'Hydrogen' or '1', return 1; etc"
    # note, the arg can't be an elem instance itself!
    s = sym_or_name_or_num
    if s in PeriodicTable:
        assert type(s) == type(1)
        return s
    elif s in EltName2Num:
        return EltName2Num[s]
    elif s in EltSym2Num:
        return EltSym2Num[s]
    else:
        assert 0, s
        
class elemprefs:
    "store one set of preferences for element radii and colors"
    def __init__(self):
        "initially, copy them from the current ones in use"
        self.prefs = {}
        for eltnum, el in PeriodicTable.items():
            self.prefs[eltnum] = dict(color = el.color, rvdw = el.rvdw)
    
    def use(self):
        """change the element table to use the prefs in this set;
        does not invalidate display lists or repaint, caller needs to do that
        """
        for eltnum, dict1 in self.prefs.items():
            el = PeriodicTable[eltnum]
            el.color = dict1['color']
            el.rvdw = dict1['rvdw']
    def change(self, sym_or_name_or_num, **attrs):
        """change the specified prefs for element sym
        (will have no effect if you change attrs other than color and rvdw)
        (note, this does not affect prefs currently in use
        until you next call self.use(), even if this set is already
        the one in use; it's meant to be used when initializing a new prefs set)
        """
        eltnum = sym_or_name_or_num_to_num(sym_or_name_or_num)
        dict1 = self.prefs[eltnum]
        dict1.update(attrs)
    
    def deepCopy(self, anotherPrefs):
        """Huaicai: deep copy the contents of <param> anotherPrefs to create a new instance of elemprefs """
        assert isinstance(anotherPrefs, elemprefs)
        if anotherPrefs == self: return self
        
        self.prefs = {}
        for eleNum, dict1 in anotherPrefs.prefs.items():
            newDict = {}
            newDict['color'] = dict1['color'][:]
            newDict['rvdw'] = dict1['rvdw']
            self.prefs[eleNum] =newDict
        
        return self
    
    def getElemColor(self, sym_or_name_or_num):
        """Huaicai: Return the element color as a triple list for <sym_or_name_or_num> """
        eltnum = sym_or_name_or_num_to_num(sym_or_name_or_num)
        dict1 = self.prefs[eltnum]
        return dict1['color']
    
    def getElemRvdw(self, sym_or_name_or_num):
        """Huaicai: Return the element rvdw  for <sym_or_name_or_num> """
        eltnum = sym_or_name_or_num_to_num(sym_or_name_or_num)
        dict1 = self.prefs[eltnum]
        return dict1['rvdw']
    
    def getElemSymbol(self, eleNum):
        """ <Param> eleNum: element index
            <Return>  the symbol for the element
        """
        assert type(eleNum) == type(1)
        try:
            elem = PeriodicTable[eleNum]
            return elem.symbol
        except:
            print "Can't find element: ", eleNum
            return None
            
    pass

# our two hardcoded choices for elem drawing prefs, named 1 and 2 for now;
# plus version 3 taken from the commented-out John Burch values above
# (not presently accessible to the user)

elemtables = { 1: elemprefs(), 2: elemprefs(), 3: elemprefs() } 

# radius values from Josh circa 041221 (probably from Eric Drexler or John Burch)
_sym_rad = """\
# Ag	1.980
Al	2.050
As	2.050
# At	2.250
# Au	1.790
B	1.461
# Ba	2.780
Be	1.930
# Bi	2.300
Br	1.832	
C	1.431	
Ca	1.274
# Cd	1.940
Cl	1.688	
Co	1.970	
Cr	2.150	
# Cs	1.774	
Cu	1.870	
F	1.293
Fe	2.020	
Ga	2.300
Ge	1.980	
H	1.135 -- by itself. when bonded to another atom, 0.704
# Hf	2.160	
# Hg	1.760
I	1.967
# In	2.450
# Ir	1.870	
K	1.592
Li	0.971	
Mg	1.154	
Mn	1.274
N	1.392
Na	1.287	
Ni	1.920	
O	1.322
P	1.784
S	1.741
Sb	2.200
Se	1.881
Si	1.825	
# Sn	2.130
Ti	2.300 \
""".split('\n')

for symrad in _sym_rad:
    words = symrad.split()
    sym = words[0]
    if not sym.startswith("#"):
        rad = float(words[1])
        # there might be more words, which we ignore, e.g. for "H"
        elemtables[2].change(sym, rvdw = rad)

# color values from John Burch (in email to Mark Sims, circa 041221)
# (also has radius values redundant with above string; these are not required here)
elemtables[2].change("Hydrogen", color = [1.0, 1.0, 1.0],       rvdw = 1.135 )
elemtables[2].change("Carbon",   color = V(117, 117, 117)/255.0, rvdw = 1.431 )
elemtables[2].change("Silicon",  color = V(111,  93, 133)/255.0, rvdw = 1.825 )

##Huaicai 2/24/05 Comment out the following changes 
# commented-out John Burch values, from above 
#elemtables[3].change("Hydrogen", color = [1.0, 1.0, 1.0],       rvdw = 1.135 )
#elemtables[3].change("Carbon",   color = V(117, 117, 117)/255.0, rvdw = 1.462 )
#elemtables[3].change("Silicon",  color = V(111,  93, 133)/255.0, rvdw = 2.25  )

def set_element_table(num, assy): # called from some menu items in select modes
    "start using the element table named num; invalidate as needed, but caller has to repaint"
    elemtables[num].use() # modifies the global elem instances
    # now inval havelist and selradii, even in clipboard ###@@@
    for mol in assy.molecules: ### does this include clipboard mols?? does it need to (maybe they're fixed on copy back)? ###@@@
        mol.changeapp(1)
    return

# end