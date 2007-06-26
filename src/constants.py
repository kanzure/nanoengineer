# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
constants.py

Various constants used in more than one module, and a few global variables.

Names defined here should be suitable for being imported (thus "used up")
in all modules.

$Id$
"""

from PyQt4.Qt import Qt

DIAMOND_BOND_LENGTH = 1.544
    #bruce 051102 added this based on email from Damian Allis:
    # > The accepted bond length for diamond is 1.544 ("Interatomic  
    # > Distances,' The Chemical Society, London, 1958, p.M102)....

# note: these Button constants might be no longer used [bruce 070601 comment]
leftButton = 1
rightButton = 2
# in Qt/Mac, control key with left mouse button simulates right mouse button.
midButton = 4
shiftModifier = 33554432
cntlModifier = 67108864
# in Qt/Mac, this flag indicates the command key rather than the control key.

altModifier = 134217728 # in Qt/Mac, this flag indicates the Alt/Option modifier key.

# Note: it would be better if we replaced the above by the equivalent
# named constants provided by Qt. Before doing this, we have to find
# out how they correspond on each platform -- for example, I don't
# know whether Qt's named constant for the control key will have the
# same numeric value on Windows and Mac, as our own named constant
# 'cntlButton' does. So no one should replace the above numbers by
# Qt's declared names before they check this out on each platform. --
# bruce 040916


# debugModifiers should be an unusual combination of modifier keys, used
# to bring up an undocumented debug menu intended just for developers
# (if a suitable preference is set). The following value is good for
# the Mac; someone on Windows or Linux can decide what value would be
# good for those platforms, and make this conditional on the
# platform. (If that's done, note that sys.platform on Mac might not
# be what you'd guess -- it can be either "darwin" or "mac" (I think),
# depending on the python installation.)  -- bruce 040916

debugModifiers = cntlModifier | shiftModifier | altModifier
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

_gensym_counters = {} #bruce 070603; has last-used value for each fixed prefix (default 0)

def _fix_gensym_prefix(prefix): #bruce 070604
    "[private helper function for gensym and relatives]"
    assert type(prefix) in (type(""), type(u""))
    if prefix and prefix[-1].isdigit():
        # This special behavior guarantees that every name gensym returns is unique.
        # As of bruce 070603, I think it never happens, based on the existing calls of gensym.
        # Note: someday we might change the added char to ' ' if prefix contains ' ',
        # and/or also do this if prefix ends with a letter (so most gensym callers
        # can rely on this rule rather than adding '-' themselves).
        prefix = prefix + '-' 
    return prefix

def gensym(prefix): #bruce 070603 rewrite, improved functionality (replaces three separate similar definitions)
    """Return prefix with a number appended, where the number is 1 more
    than the last time we were called for the same prefix, or 1 the first time
    we see that prefix. Note that this means we maintain an independent counter
    for each different prefix we're ever called with.
       In order to ensure that every name we ever return is unique (in spite of our
    independent counters reusing the same values for different prefixes), we append
    '-' to prefix if it ends with a digit already, before looking up and appending
    the counter for that prefix.
       (The prefix is typically related to a Node classname, but can be more or less
    specialized, e.g. when making chunks of certain kinds (like DNA) or copying nodes
    or library parts.)
    """
    prefix = _fix_gensym_prefix(prefix)
    new_value = _gensym_counters.get(prefix, 0) + 1
    _gensym_counters[prefix] = new_value
    return prefix + str(new_value)

def permit_gensym_to_reuse_name(prefix, name): #bruce 070604
    """This gives gensym permission to reuse the given name which it returned based on the given prefix,
    if it can do this and still follow its other policies. It is not obligated to do this.
    """
    prefix = _fix_gensym_prefix(prefix)
    last_used_value = _gensym_counters.get(prefix, 0)
    last_used_name = prefix + str(last_used_value)
    if name == last_used_name:
        # this is the only case in which we can safely do anything.
        corrected_last_used_value = last_used_value - 1
        assert corrected_last_used_value >= 0 # can't happen if called on names actually returned from gensym
        _gensym_counters[prefix] = corrected_last_used_value
    return

def average_value(seq, default = 0.0): #bruce 070412; renamed and moved from selectMode.py to constants.py 070601
    """Return the numerical average value of seq (a Python sequence or equivalent),
    or (by default) 0.0 if seq is empty.
       Note: Numeric contains a function named average, which is why we don't use that name.
    """
    #e should typetest seq if we can do so efficiently
    if not seq:
        return default
    return sum(seq) / len(seq) # WARNING: this uses <built-in function sum>, not Numeric.sum.

# display modes:
## These are arranged in order of increasing thickness of the bond representation. They are indices of dispNames and dispLabel.
## Josh 11/2
diDEFAULT = 0
diINVISIBLE = 1
diTrueCPK = 2 # CPK [renamed from old name diVDW, bruce 060607; corresponding UI change was by mark 060307]
    # (This is not yet called diCPK, to avoid confusion, since that name was used for diBALL until today.
    #  After some time goes by, we can rename this to just diCPK.)
diLINES = 3
diBALL = 4 # "Ball and Stick" [renamed from old incorrect name diCPK, bruce 060607; corresponding UI change was by mark 060307]
diTUBES = 5
diCYLINDER = 6
diSURFACE = 7

# note: the following lists can be extended later at runtime. [as of bruce 060607]
dispNames = ["def", "inv", "vdw", "lin", "cpk", "tub"]
    # these dispNames can't be easily revised, since they are used in mmp files; cpk and vdw are misleading as of 060307.

# Mark 2007-06-25
properDisplayNames = ["def", "inv", "cpk", "lin", "bas", "tub"]

#dispLabel = ["Default", "Invisible", "VdW", "Lines", "CPK", "Tubes"]
dispLabel = ["Default", "Invisible", "CPK", "Lines", "Ball and Stick", "Tubes"]
# Changed "CPK" => "Ball and Stick" and "VdW" => "CPK".  mark 060307.

# display mode for new glpanes (#e should be a user preference) [bruce 041129]
default_display_mode = diTUBES # Now in user prefs db, set in GLPane.__init__ [Mark 050715]

TubeRadius = 0.3 # (i.e. "TubesSigmaBondRadius")
diBALL_SigmaBondRadius = 0.1

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
purple = violet #bruce 061016, just so this color name is defined -- if you have better rgb values, feel free to modify it
pink = (0.8, 0.4, 0.4) #bruce 050610 darkened this and called it 'pink'; old value was (1.0, 0.5, 0.5), called LEDon

#ninad20060922 using it while drawing origin axis
lightblue = ave_colors(0.03, white, blue) 

# Following color is used to draw the back side of a reference plane. 
#Better call it brownish yellow or greenish brown?? lets just call it brown 
#(or suggest better name by looking at it. ) - ninad 20070615
brown = ave_colors(0.5, black, yellow) 
                         
bluesky = (0.9, 0.9, 0.9), (0.9, 0.9, 0.9), (0.33, 0.73, 1.0), (0.33, 0.73, 1.0) # GLPane "Blue Sky" gradient

###bruce 061016 removed these, changed remaining uses of LEDon to pink:
##LEDoff = (0.8, 0.0, 0.0)
##LEDon = pink

PickedColor = (0.0, 0.0, 1.0)
ErrorPickedColor = (1.0, 0.0, 0.0) #bruce 041217 (used to indicate atoms with wrong valence, etc)

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

# ==

# values for assy.selwhat variable [moved here from assembly.py by bruce 050519]

# bruce 050308 adding named constants for selwhat values;
# not yet uniformly used (i.e. most code still uses hardcoded 0 or 2,
#  and does boolean tests on selwhat to see if chunks can be selected);
# not sure if these would be better off as assembly class constants:
# values for assy.selwhat: what to select: 0=atoms, 2 = molecules
SELWHAT_ATOMS = 0
SELWHAT_CHUNKS = 2
SELWHAT_NAMES = {SELWHAT_ATOMS: "Atoms", SELWHAT_CHUNKS: "Chunks"} # for use in messages

# mark 060206 adding named constants for selection shapes.
SELSHAPE_LASSO = 'LASSO'
SELSHAPE_RECT = 'RECTANGLE'

# mark 060206 adding named constants for selection logic.  
#& To do: Change these from ints to strings. mark 060211.
SUBTRACT_FROM_SELECTION = 'Subtract Inside'
OUTSIDE_SUBTRACT_FROM_SELECTION = 'Subtract Outside' # used in cookieMode only.
ADD_TO_SELECTION = 'Add'
START_NEW_SELECTION = 'New'
DELETE_SELECTION = 'Delete'
#& Keep these around for a little while for reference until I'm sure I converted everything properly.  mark 060212.
#SUBTRACT_FROM_SELECTION = 0
#ADD_TO_SELECTION = 1
#START_NEW_SELECTION = 2
#DELETE_SELECTION = 3

def get_selCurve_color(selSense, bgcolor=white):
    '''Returns line color of the selection curve. 
    Returns <black> for light colored backgrounds (and Sky Blue).
    Returns <white> for dark colored backgrounds.
    Returns <red> if <selSense> is DELETE_SELECTION mode.
    '''
    
    if selSense == DELETE_SELECTION: 
        return red
    
    get_selCurve_color = black
    
    from VQT import vlen, A
    color_diff = vlen(A(get_selCurve_color)-A(bgcolor))
    
    if color_diff < 0.5:
        return white
    else:
        return black
            
def get_selCurve_color_ORIG(selSense, bgcolor=white):
    #& Decided it was better to keep the color the same for all selSense types except 
    #& DELETE_SELECTION.
    #& Keep this here in case we want to reinstate line color based on selSense.  mark 060212. 
    if selSense == SUBTRACT_FROM_SELECTION: return gray # was orange
    if selSense == ADD_TO_SELECTION: return gray # was navy
    if selSense == START_NEW_SELECTION: return gray # was yellow
    if selSense == OUTSIDE_SUBTRACT_FROM_SELECTION: return gray # was yellow
    if selSense == DELETE_SELECTION: return red

# ==

#bruce 060220 add some possible values for _s_attr_xxx attribute declarations (needed by Undo)
# (defining these in constants.py might be temporary)

from state_constants import *

# ==

# Keys for user preferences for A6 [moved into prefs_constants.py by Bruce 050805]

from prefs_constants import * #e when it's practical after A6, this import should be removed

# The far clipping plane normalized z value, actually it's a little closer than the actual far clipping 
# plane to the eye. This is used to draw the blue sky backround polygon, and also used to check if user
# click on empty space on the screen.
GL_FAR_Z = 0.999

# end
