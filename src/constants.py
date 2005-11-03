# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
constants.py

Various constants used in more than one module, and a few global variables.

Names defined here should be suitable for being imported (thus "used up")
in all modules.

$Id$
"""

from qt import Qt

DIAMOND_BOND_LENGTH = 1.544
    #bruce 051102 added this based on email from Damian Allis:
    # > The accepted bond length for diamond is 1.544 ("Interatomic  
    # > Distances,' The Chemical Society, London, 1958, p.M102)....

leftButton = 1
rightButton = 2
# in Qt/Mac, control key with left mouse button simulates right mouse button.
midButton = 4
shiftButton = 256
cntlButton = 512
# in Qt/Mac, this flag indicates the command key rather than the control key.

altButton = 1024 # in Qt/Mac, this flag indicates the Alt/Option modifier key.

# Note: it would be better if we replaced the above by the equivalent
# named constants provided by Qt. Before doing this, we have to find
# out how they correspond on each platform -- for example, I don't
# know whether Qt's named constant for the control key will have the
# same numeric value on Windows and Mac, as our own named constant
# 'cntlButton' does. So no one should replace the above numbers by
# Qt's declared names before they check this out on each platform. --
# bruce 040916


# debugButtons should be an unusual combination of modifier keys, used
# to bring up an undocumented debug menu intended just for developers
# (if a suitable preference is set). The following value is good for
# the Mac; someone on Windows or Linux can decide what value would be
# good for those platforms, and make this conditional on the
# platform. (If that's done, note that sys.platform on Mac might not
# be what you'd guess -- it can be either "darwin" or "mac" (I think),
# depending on the python installation.)  -- bruce 040916

debugButtons = cntlButton | shiftButton | altButton
# on the mac, this really means command-shift-alt


# Trivial functions that might be needed early during app startup
# (good to put here to avoid recursive import problems involving other modules)
# or in many modules.
# (Only a very few functions are trivial enough to be put here,
#  and their names always need to be suitable for using up in every module.)

def noop(*args,**kws): pass

def genKey(start = 1): #bruce 050922 moved this here from chem.py and Utility.py, added start arg
    """ produces generators that count indefinitely """
    i = start
    while 1:
        yield i
        i += 1
    pass

# display modes:
## These are arranged in order of increasing thickness of the bond representation
## Josh 11/2
diDEFAULT = 0
diINVISIBLE = 1
diVDW = 2
diLINES = 3
diCPK = 4
diTUBES = 5

dispNames = ["def", "inv", "vdw", "lin", "cpk", "tub"]
dispLabel = ["Default", "Invisible", "VdW", "Lines", "CPK", "Tubes"]

# display mode for new glpanes (#e should be a user preference) [bruce 041129]
default_display_mode = diVDW # Now in user prefs db, set in GLPane.__init__ [Mark 050715]

TubeRadius = 0.3

# ave_colors() logically belongs in some "color utilities file",
# but is here so it is defined early enough for use in computing default values
# of user preferences in prefs_constants.py.

def ave_colors(weight, color1, color2): #bruce 050805 moved this here from handles.py, and revised it
    """Return a weighted average of two colors,
    where weight gives the amount of color1 to include.
    (E.g., weight of 1.0 means use only color1, 0.0 means use only color2,
    and ave_colors(0.8, color, black) makes color slightly darker.)
       Color format is a 3-tuple of RGB components from 0.0 to 1.0
    (e.g. black is (0.0, 0.0, 0.0), white is (1.0, 1.0, 1.0)).
    This is also the standard format for colors in our preferences database
    (which contains primitive Python objects encoded by the shelve module).
       Input color components can be ints, but those are coerced to floats,
    NOT treated as in the range [0,255] like some other color-related functions do.
    Output components are always floats.
       Input colors can be any 3-sequences (including Numeric arrays);
    output color is always a tuple.
    """
    #e (perhaps we could optimize this using some Numeric method)
    weight = float(weight)
    return tuple([weight * c1 + (1-weight)*c2 for c1,c2 in zip(color1,color2)])

# colors [some of the ones whose names describe their function
# are default values for user preferences]

black =  (0.0, 0.0, 0.0)
blue =   (0.0, 0.0, 0.6)
aqua =   (0.15, 1.0, 1.0)
orange = (1.0, 0.25, 0.0)
red =    (1.0, 0.0, 0.0)
yellow = (1.0, 1.0, 0.0)
green =  (0.0, 1.0, 0.0)
darkgreen =  (0.0, 0.6, 0.0)
magenta = (1.0, 0.0, 1.0)
white =  (1.0, 1.0, 1.0)
gray =   (0.5, 0.5, 0.5)
navy =   (0.0, 0.09, 0.44)
darkred = (0.6, 0.0, 0.2) 
violet = (0.6, 0.1, 0.9) # Will change this to purple later.  Mark 050730

LEDoff = (0.8, 0.0, 0.0)
LEDon = pink = (0.8, 0.4, 0.4) ##bruce 050610 darkened this and added the name 'pink'; old value was (1.0, 0.5, 0.5)

PickedColor = (0.0, 0.0, 1.0)
ErrorPickedColor = (1.0, 0.0, 0.0) #bruce 041217 (used to indicate atoms with wrong valence, etc)

globalParms = {}
globalParms['WorkingDirectory'] = "."

def logicColor(logic):
    if logic==0: return orange
    if logic==1: return navy
    if logic==2: return yellow

elemKeyTab =  [('H', Qt.Key_H, 1),
               ('B', Qt.Key_B, 5),
               ('C', Qt.Key_C, 6),
               ('N', Qt.Key_N, 7),
               ('O', Qt.Key_O, 8),
               ('F', Qt.Key_F, 9),
               ('Al', Qt.Key_A, 13),
               ('Si', Qt.Key_Q, 14),
               ('P', Qt.Key_P, 15),
               ('S', Qt.Key_S, 16),
               ('Cl', Qt.Key_L, 17)]

# values for assy.selwhat variable [moved here from assembly.py by bruce 050519]

# bruce 050308 adding named constants for selwhat values;
# not yet uniformly used (i.e. most code still uses hardcoded 0 or 2,
#  and does boolean tests on selwhat to see if chunks can be selected);
# not sure if these would be better off as assembly class constants:
# values for assy.selwhat: what to select: 0=atoms, 2 = molecules
SELWHAT_ATOMS = 0
SELWHAT_CHUNKS = 2
SELWHAT_NAMES = {SELWHAT_ATOMS: "Atoms", SELWHAT_CHUNKS: "Chunks"} # for use in messages

# Keys for user preferences for A6 [moved into prefs_constants.py by Bruce 050805]

from prefs_constants import * #e when it's practical after A6, this import should be removed

# The far clipping plane normalized z value, actually it's a little closer than the actual far clipping 
# plane to the eye. This is used to draw the blue sky backround polygon, and also used to check if user
# click on empty space on the screen.
GL_FAR_Z = 0.999

# end
