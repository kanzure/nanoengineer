# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
constants.py -- constants and trivial functions used in multiple modules.

Everything defined here must require no imports except from builtin
modules or PyQt, and use names that we don't mind reserving throughout NE1.

(Ideally this module would also contain no state; probably we should move
gensym out of it for that reason.)

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4.Qt import Qt

# ==

#Urmi 20080617: grid origin related constants: UM 20080616
LOWER_LEFT = 0
LOWER_RIGHT = 1
UPPER_LEFT = 2
UPPER_RIGHT = 3
LABELS_ALONG_ORIGIN = 0
LABELS_ALONG_PLANE_EDGES = 1

MULTIPANE_GUI = True # enable some code which was intended to permit the main window
    # to contain multiple PartWindows. Unfortunately we're far from that being possible,
    # but we're also (I strongly suspect, but am not sure) now dependent on this
    # value being True, having not maintained the False case for a long time.
    # If this is confirmed, we should remove the code for the False case and remove
    # this flag, and then decide whether the singleton partWindow should continue
    # to exist. [bruce 071008, replacing a debug_pref with this flag]

GLPANE_IS_COMMAND_SEQUENCER = True
    # This indicates that the GLPane and Command Sequencer are the same object.
    # This is true for now, and False is not yet supported, but will someday
    # only be False (and then this constant flag can be removed). It exists now
    # mainly to mark code which is known to need changing when this can be False.
    # [bruce 071010]

DIAMOND_BOND_LENGTH = 1.544
    #bruce 051102 added this based on email from Damian Allis:
    # > The accepted bond length for diamond is 1.544 ("Interatomic  
    # > Distances,' The Chemical Society, London, 1958, p.M102)....

# ==

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

# ==

# Trivial functions that might be needed early during app startup
# (good to put here to avoid recursive import problems involving other modules)
# or in many modules.
# (Only a very few functions are trivial enough to be put here,
#  and their names always need to be suitable for using up in every module.)


def noop(*args,**kws): pass

def intRound(num): #bruce 080521
    """
    Round a number (int or float) to the closest int.

    @warning: int(num + 0.5) is *not* a correct formula for this
              (when num is negative), since Python int() rounds
              towards zero, not towards negative infinity
              [http://docs.python.org/lib/built-in-funcs.html].
    """
    return int(round(num))

def str_or_unicode(qstring): #bruce 080529
    """
    Return str(qstring), unless that fails with UnicodeEncodeError,
    in which case return unicode(qstring).

    @param qstring: anything, but typically a QString object.
    """
    try:
        return str(qstring)
    except UnicodeEncodeError:
        return unicode(qstring)
    pass

def genKey(start = 1):
    #bruce 050922 moved this here from chem.py and Utility.py, added start arg
    """
    produces generators that count indefinitely
    """
    i = start
    while 1:
        yield i
        i += 1
    pass

atKey = genKey(start = 1)
    # generator for atom.key attribute, also used for fake atoms.
    # [moved here from chem.py to remove import cycle, bruce 080510]
    # As of bruce 050228, we now make use of the fact that this produces keys
    # which sort in the same order as atoms are created (e.g. the order they're
    # read from an mmp file), so we now require this in the future even if the
    # key type is changed. [Note: this comment appears in two files.]

# ==

_gensym_counters = {} #bruce 070603; has last-used value for each fixed prefix (default 0)

def _fix_gensym_prefix(prefix): #bruce 070604
    """
    [private helper function for gensym and relatives]
    """
    assert type(prefix) in (type(""), type(u""))
    if prefix and prefix[-1].isdigit():
        # This special behavior guarantees that every name gensym returns is unique.
        # As of bruce 070603, I think it never happens, based on the existing calls of gensym.
        # Note: someday we might change the added char to ' ' if prefix contains ' ',
        # and/or also do this if prefix ends with a letter (so most gensym callers
        # can rely on this rule rather than adding '-' themselves).
        # NOTE: this special rule is still needed, even if we never want default
        # new node names to contain '-' or ' '. It's ok since they also won't
        # include digits in the prefix, so this rule won't happen. [bruce 080407 comment]
        prefix = prefix + '-' 
    return prefix

def gensym(prefix, assy = None):
    #bruce 070603 rewrite, improved functionality (replaces three separate similar definitions)
    #bruce 080407: new option to pass assy, used for names_to_avoid
    """
    Return prefix with a number appended, where the number is 1 more
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

    @param prefix: prefix for generated name.

    @param assy: if provided and not None, don't duplicate any node name
                 presently used in assy.
    """
    prefix = _fix_gensym_prefix(prefix)
    names_to_avoid = {} # maps name -> anything, for 0 or more names we don't want to generate
    # fill names_to_avoid with node names from assy, if provided
    import debug_flags # might be an import cycle, but probably ok for now
        ### TODO: move this function elsewhere; it violates this module's
        # import policy [bruce 080711 comment]
    if assy is not None:
        try:
            # the try/except is not needed unless this new code has bugs
            def avoid_my_name(node):
                names_to_avoid[node.name] = None
            assy.root.apply2all( avoid_my_name )
                # could optim and not delve inside nodes that hide contents
        except:
            # can't import print_compact_traceback in this file
            # (todo: move gensym into its own file in utilities, so we can;
            #  or, move this code into a new method in class Assembly (better))
            if debug_flags.atom_debug:
                print "bug: exception in gensym(%r, %r) filling names_to_avoid, reraising since atom_debug set:" % (prefix, assy)
                raise # make debugging possible
            else:
                print "bug: ignoring exception (discarded) in gensym(%r, %r) filling names_to_avoid" % (prefix, assy)
            pass
        pass
    new_value = _gensym_counters.get(prefix, 0) + 1
    name = prefix + str(new_value)
    while name in names_to_avoid:
        new_value += 1
        name = prefix + str(new_value)
    _gensym_counters[prefix] = new_value
    return name

def permit_gensym_to_reuse_name(prefix, name): #bruce 070604
    """
    This gives gensym permission to reuse the given name which it returned based on the given prefix,
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

# ==

def average_value(seq, default = 0.0): #bruce 070412; renamed and moved from selectMode.py to constants.py 070601
    """
    Return the numerical average value of seq (a Python sequence or equivalent),
    or (by default) 0.0 if seq is empty.

    Note: Numeric contains a function named average, which is why we don't use that name.
    """
    #e should typetest seq if we can do so efficiently
    if not seq:
        return default
    return sum(seq) / len(seq) # WARNING: this uses <built-in function sum>, not Numeric.sum.

# ==

def common_prefix( seq1, *moreseqs ):
    """
    Given one or more python sequences (as separate arguments),
    return the initial common prefix of them (determined by != of elements)
    (as a list and/or the sequence type of the first of these sequences --
     which of these sequence types to use is not defined by this function's
     specification, but it will be one of those three types)
    (it's also undefined whether the retval might be the same mutable object
     as the first argument!)
    """
    #bruce 080626, modified from a version in node_indices.py
    length_ok = len(seq1)
    for seq2 in moreseqs:
        if len(seq2) < length_ok:
            length_ok = len(seq2)
        for i in xrange(length_ok):
            if seq1[i] != seq2[i]:
                length_ok = i
                break
    return seq1[0:length_ok] # might be all or part of seq1, or 0-length

# ==

# Display styles (aka display modes)

# Note: this entire section ought to be split into its own file.
# BUT, the loop below, initializing ATOM_CONTENT_FOR_DISPLAY_STYLE,
# needs to run before dispNames, or (preferably) on a copy of it
# from before it's modified, by external init code. [bruce 080324 comment]

remap_atom_dispdefs = {} #bruce 080324 moved this here from displaymodes.py

# These are arranged in order of increasing thickness of the bond representation.
# They are indices of dispNames and dispLabel.
# Josh 11/2
diDEFAULT = 0 # the fact that diDEFAULT == 0 is public. [bruce 080206]
diINVISIBLE = 1
diTrueCPK = 2 # CPK [renamed from old name diVDW, bruce 060607; corresponding UI change was by mark 060307]
    # (This is not yet called diCPK, to avoid confusion, since that name was used for diBALL until today.
    #  After some time goes by, we can rename this to just diCPK.)
diLINES = 3
diBALL = 4 # "Ball and Stick" [renamed from old incorrect name diCPK, bruce 060607; corresponding UI change was by mark 060307]
diTUBES = 5
# WARNING (kluge):
# the order of the following constants has to match how the lists dispNames and
# dispLabel (defined below) are extended by side effects of imports of
# corresponding display styles in startup_misc.py. (Needs cleanup.)
# [bruce 080212 comment; related code has comments with same signature]
diDNACYLINDER = 6
diCYLINDER = 7
diSURFACE = 8
diPROTEIN = 9

# note: some of the following lists are extended later at runtime. [as of bruce 060607]
dispNames = ["def", "inv", "vdw", "lin", "cpk", "tub"]
    # these dispNames can't be easily revised, since they are used in mmp files; cpk and vdw are misleading as of 060307.
    # NOTE: as of bruce 080324, dispNames is now private.
    # Soon it will be renamed and generalized to permit aliases for the names.
    # Then it will become legal to read (but not yet to write) the new forms
    # of the names which are proposed in bug 2662.

_new_dispNames = ["def", "Invisible", "CPK", "Lines", "BallAndStick", "Tubes"]
    #bruce 080324 re bug 2662; permit for reading, but don't write them yet

def get_dispName_for_writemmp(display): #bruce 080324, revised 080328
    """
    Turn a display-style code integer (e.g. diDEFAULT; as stored in Atom.display
    or Chunk.display) into a display-style code string as used in the current
    writing format for mmp files.
    """
    if 1:
        # temporary import cycle. Should be ok, and will be removed soon.
        # But do move it since it violates this module's import policy. (TODO)
        # Might need to be a relative import to work, so use one.
        # Surely needs to be a runtime import, and only run in this function.
        # [bruce 080328]
        from GlobalPreferences import debug_pref_write_new_display_names
        if debug_pref_write_new_display_names():
            return _new_dispNames[display]
    return dispNames[display]

def interpret_dispName(dispname, defaultValue = diDEFAULT, atom = True): #bruce 080324
    """
    Turn a display-style code string (a short string constant used in mmp files
    for encoding atom and chunk display styles) into the corresponding
    display-style code integer (its index in dispNames, as extended at runtime).

    If dispname is not a valid display-style code string, return defaultValue,
    which is diDEFAULT by default.

    If atom is true (the default), only consider "atom display styles" to be
    valid; otherwise, also permit "chunk display styles".
    """
    def _return(res):
        if res > diTUBES and atom and remap_atom_dispdefs.has_key(res):
            # note: the initial res > diTUBES is an optimization kluge
            return defaultValue
        return res

    try:
        res = dispNames.index(dispname)
    except ValueError:
        # not found, in first array (the one with old names, and that gets extended)
        pass
    else:
        return _return(res)

    from GlobalPreferences import debug_pref_read_new_display_names
        # see comment for similar import -- temporary [bruce 080328]

    if debug_pref_read_new_display_names():
        try:
            res = _new_dispNames.index(dispname)
        except ValueError:
            # not found, in 2nd array (new names, which are aliases for old ones)
            pass
        else:
            return _return(res)

    return defaultValue # from interpret_dispName

# <properDisplayNames> used by write_qutemol_pdb_file() in qutemol.py only.
# Set qxDNACYLINDER to "def" until "dnacylinder" is supported in QuteMolX.
qxDNACYLINDER = "def" 
properDisplayNames = ["def", "inv", "cpk", "lin", "bas", "tub", qxDNACYLINDER]

#dispLabel = ["Default", "Invisible", "VdW", "Lines", "CPK", "Tubes"]
dispLabel = ["Default", "Invisible", "CPK", "Lines", "Ball and Stick", "Tubes"]
# Changed "CPK" => "Ball and Stick" and "VdW" => "CPK".  mark 060307.

def _f_add_display_style_code( disp_name, disp_label, allowed_for_atoms):
    """
    [friend function for displaymodes.py]
    """
    #bruce 080324 split this out of displaymodes.py, to permit making
    # these globals (dispNames, dispLabel) private soon
    if disp_name in dispNames:
        # this is only legal [nim] if the classname is the same;
        # in that case, we ought to replace things (useful for reload
        # during debugging)
        assert 0, "reload during debug for display modes " \
               "is not yet implemented; or, non-unique " \
               "mmp_code %r (in dispNames)" % (disp_name,)
    if disp_name in _new_dispNames: #bruce 080415
        # same comment applies as above
        assert 0, "reload during debug for display modes " \
               "is not yet implemented; or, non-unique " \
               "mmp_code %r (in _new_dispNames)" % (disp_name,)
    assert len(dispNames) == len(dispLabel)
    assert len(dispNames) == len(_new_dispNames) #bruce 080415
    dispNames.append(disp_name)
    _new_dispNames.append(disp_name) #bruce 080415 fix bug 2809 in saving nodes with "chunk display styles" set (not in .rc1)
    dispLabel.append(disp_label)
    ind = dispNames.index(disp_name) # internal value used by setDisplay
        # note: this always works, since we appended the same disp_name to *both*
        # dispNames and _new_dispNames [bruce 080415 comment]
    if not allowed_for_atoms:
        remap_atom_dispdefs[ind] = diDEFAULT # kluge?
    return ind

# ==

# display style for new glpanes (#e should be a user preference) [bruce 041129]
# Now in user prefs db, set in GLPane.__init__ [Mark 050715]
# WARNING: this is no longer used as the default global display style,
# and now has a different value from that, but it is still used in other ways,
# which would need analysis in order to determine whether they can be replaced
# with the actual default global display style. Needs cleanup.
# [bruce 080606 comment]
default_display_mode = diTUBES

TubeRadius = 0.3 # (i.e. "TubesSigmaBondRadius")
diBALL_SigmaBondRadius = 0.1
diDNACYLINDER_SigmaBondRadius = 1.3

# ==

# atom content flags [bruce 080306]

# (so far, we only have these for display style, but more might be added
#  for other aspects of atoms, such as kind of element, whether selected,
#  whether highlighted, whether has error, etc;
#  in spite of the term "atom content" we might also add some for nodes,
#  e.g. all the same ones mentioned for atoms.)

ATOM_CONTENT_FOR_DISPLAY_STYLE = [] # modified by the loop below to be same length as dispNames
AC_HAS_INDIVIDUAL_DISPLAY_STYLE = 1
AC_INVISIBLE = 1 << diINVISIBLE # note: fewer bits than ATOM_CONTENT_FOR_DISPLAY_STYLE[diINVISIBLE]
for _disp in range(len(dispNames)):
    # WARNING:
    # - must run before dispNames is modified by external code
    # - assumes no styles defined in displaymodes.py can apply to atoms
    if not _disp:
        assert _disp == diDEFAULT
        _content_for_disp = 0
    elif _disp == diINVISIBLE:
        # don't redundantly count this as "individual display style"
        _content_for_disp = AC_INVISIBLE 
    else:
        _content_for_disp = \
                          (AC_HAS_INDIVIDUAL_DISPLAY_STYLE + (1 << _disp))
        # this uses bits 1 through len(dispNames) - 1, plus bit 0 for "any of those"
    ATOM_CONTENT_FOR_DISPLAY_STYLE.append(_content_for_disp)

# ==

# constants related to bounding boxes containing atoms and bonds [piotr 080402]

# The estimated maximum sphere radius in any display style.
# The maximum VdW atom radius is 5.0 A.
# It can be increased by 25% in User Preferences.
# Highlighting increases this radius by 0.2A.
# Total = 5.0A * 1.25 + 0.2A = 6.2A 
MAX_ATOM_SPHERE_RADIUS = 6.2

# Margin value for bounding box (used in BoundingBox.py)
BBOX_MARGIN = 1.8

# The minimal bounding sphere radius for a single atom of VdW radius = 0.0,
# calculated as follows: BB_MIN_RADIUS = sqrt(3 * (BBOX_MARGIN) ^ 2)
BBOX_MIN_RADIUS = 3.118

# ==

# PAM models. (Possible values of atom.element.pam, besides None,
#  and of some "info chunk" attributes in the mmp format, besides "".
#  Values must never be changed (unless info chunk read/write code
#  is revised to hide the change), since they are part of mmp format.)
#
# [bruce 080321]

MODEL_PAM3 = 'PAM3'
MODEL_PAM5 = 'PAM5'

PAM_MODELS = (MODEL_PAM3, MODEL_PAM5)

MODEL_MIXED = 'PAM_MODEL_MIXED' # review: good this is not in PAM_MODELS?

# Dna constants presently needed outside of dna package.
# After sufficient refactoring, these could be moved inside it.

Pl_STICKY_BOND_DIRECTION = 1 # should be 1 or -1;
    # the bond direction from Pl to the Ss it wants to stay with when possible.
    # (This value (1) is consistent with which strand-ends get Pls
    #  in the PAM5 generator as of 080312, and with other evidence #doc)
    # [bruce 080118/080326] #e rename?

# ==

# constants for bondpoint_policy [bruce 080603]

BONDPOINT_LEFT_OUT = "BONDPOINT_LEFT_OUT"
BONDPOINT_UNCHANGED = "BONDPOINT_UNCHANGED" # not yet specifiable
BONDPOINT_ANCHORED = "BONDPOINT_ANCHORED" # not yet specifiable
BONDPOINT_REPLACED_WITH_HYDROGEN = "BONDPOINT_REPLACED_WITH_HYDROGEN"

# ==

# constants for readmmp
SUCCESS = 'SUCCESS'
ABORTED = 'ABORTED'
READ_ERROR = 'READ ERROR'

# ==

def filesplit(pathname):
    """
    Splits pathname into directory part (not ending with '/'),
    basename, and extension (including '.', or can be "")
    and returns them in a 3-tuple.
    For example, filesplit('~/foo/bar/gorp.xam') ==> ('~/foo/bar', 'gorp', '.xam').
    Compare with _fileparse (deprecated), whose returned dir ends with '/'.
    """
    #bruce 050413 _fileparse variant: no '/' at end of dirname
    #bruce 071030 moved this from movieMode to constants
    import os
    dir, file = os.path.split(pathname)
    base, ext = os.path.splitext(file)
    return dir, base, ext

# ==

def remove_prefix(str1, prefix): 
    # TODO: put this into a new file, utilities.string_utils?
    """
    Remove an optional prefix from a string:
    if str1 starts with prefix, remove it (and return the result),
    otherwise return str1 unchanged.

    @param str1: a string that may or may not start with prefix.
    @type str1: string

    @param prefix: a string to remove if it occurs at the beginning of str1.
    @type prefix: string

    @return: a string, equal to str1 with prefix removed, or to str1.
    """
    if str1.startswith(prefix):
        return str1[len(prefix):]
    else:
        return str1

# ==

# ave_colors() logically belongs in some "color utilities file",
# but is here so it is defined early enough for use in computing default values
# of user preferences in prefs_constants.py.

def ave_colors(weight, color1, color2): #bruce 050805 moved this here from handles.py, and revised it
    """
    Return a weighted average of two colors,
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

def color_difference(color1, color2, minimum_difference = 0.5):
    """
    Return True if the difference between color1 and color2 is greater than
    minimum_difference (0.5 by default). Otherwise, return False.
    """
    # [probably by Mark, circa 080710]
    # [revised by bruce 080711 to remove import cycle involving VQT]
    # Note: this function name is misleading, since it does not return
    # the color difference. [bruce 080711 comment]
    color_diff_squared = sum([(color2[i] - color1[i])**2 for i in (0,1,2)])
    if color_diff_squared > minimum_difference ** 2:
        return True
    return False

# colors
# [note: some of the ones whose names describe their function
#  are default values for user preferences]

black =  (0.0, 0.0, 0.0)
white =  (1.0, 1.0, 1.0)
darkblue =  (0.0, 0.0, 0.6) # Was blue. Mark 2008-06-27
blue = (0.0, 0.0, 1.0)
aqua =   (0.15, 1.0, 1.0)
orange = (1.0, 0.25, 0.0)
darkorange = (0.6, 0.3, 0.0)
red =    (1.0, 0.0, 0.0)
lightred_1 = (0.99, 0.501, 0.505) #reddish pink color
yellow = (1.0, 1.0, 0.0)
green =  (0.0, 1.0, 0.0)
lightgreen = (0.45, 0.8, 0.45) # bruce 080206
lightgreen_2 = (0.596, 0.988, 0.596)
darkgreen =  (0.0, 0.6, 0.0)
magenta = (1.0, 0.0, 1.0)
cyan = (0.0, 1.0, 1.0)
lightgray = (0.8, 0.8, 0.8)
gray =   (0.5, 0.5, 0.5)
darkgray = (0.3, 0.3, 0.3)
navy =   (0.0, 0.09, 0.44)
darkred = (0.6, 0.0, 0.2) 
violet = (0.6, 0.1, 0.9)
purple = (0.4, 0.0, 0.6)
darkpurple = (0.3, 0.0, 0.3)
pink = (0.8, 0.4, 0.4) 
olive = (0.3, 0.3, 0.0)
steelblue = (0.3, 0.4, 0.5)
brass = (0.5, 0.5, 0.0)
copper = (0.3, 0.3, 0.1)
mustard = (0.78, 0.78, 0.0)
applegreen = (0.4, 0.8, 0.4)
banana = (0.8901, 0.8117, 0.3411)
silver = (0.7529, 0.7529, 0.7529)
gold = (1, 0.843, 0)
ivory = (1, 1, 0.9411)
#ninad20060922 using it while drawing origin axis
lightblue = ave_colors(0.03, white, blue)
    # Note: that color is misnamed -- it's essentially just blue.
    # Or maybe the definition has a typo?
    # This needs cleanup... in the meantime,
    # consider also lighterblue
lighterblue = ave_colors( 0.5, white, blue)

# Following color is used to draw the back side of a reference plane. 
#Better call it brownish yellow or greenish brown?? lets just call it brown 
#(or suggest better name by looking at it. ) - ninad 20070615
brown = ave_colors(0.5, black, yellow) 

# The background gradient types/values.
# Gradient values are one more than the gradient constant values in Preferences.py.
# (i.e. bgEVENING_SKY =  BG_EVENING_SKY + 1)
bgSOLID = 0
bgEVENING_SKY = 1 
bgBLUE_SKY = 2
bgSEAGREEN = 3
eveningsky = (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 0.3), (0.0, 0.0, 0.3) # GLPane "Evening Sky" gradient
bluesky = (0.9, 0.9, 0.9), (0.9, 0.9, 0.9), (0.33, 0.73, 1.0), (0.33, 0.73, 1.0) # GLPane "Blue Sky" gradient
bg_seagreen = (0.905, 0.905, 0.921), (0.905, 0.905, 0.921), (0.6, 0.8, 0.8), (0.6, 0.8, 0.8) # GLPane "Sea Green" gradient

bg_seagreen_UNUSED_FOR_DEBUG = (0.894, 0.949, 0.894), (0.862, 0.929, 0.862), (0.686, 0.843, 0.843), (0.905, 0.905, 0.921), \
(0.862, 0.929, 0.862), (0.839, 0.921, 0.839), (0.67, 0.835, 0.835), (0.686, 0.843, 0.843), \
(0.686, 0.843, 0.843), (0.67, 0.835, 0.835), (0.6, 0.8, 0.8), (0.6, 0.8, 0.8), \
(0.905, 0.905, 0.921), (0.686, 0.843, 0.843), (0.6, 0.8, 0.8), (0.701, 0.85, 0.85) # GLPane "Evening Sky" gradient

## PickedColor = (0.0, 0.0, 1.0) # no longer used as of 080603
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

#bruce 060220 add some possible values for _s_attr_xxx attribute declarations (needed by Undo)
# (defining these in constants.py might be temporary)

# ==

# Keys for user preferences for A6 [moved into prefs_constants.py by Bruce 050805]

# The far clipping plane normalized z value, actually it's a little closer than the actual far clipping 
# plane to the eye. This is used to draw the blue sky backround polygon, and also used to check if user
# click on empty space on the screen.
GL_FAR_Z = 0.999

# ==

# Determine CAD_SRC_PATH.
# For developers, this is the directory containing
# NE1's toplevel Python code, namely .../cad/src;
# for users of a built release, this is the directory
# containing the same toplevel Python modules as that does,
# as they're built into NE1 and importable while running it
# (not taking into account ALTERNATE_CAD_SRC_PATH even if it's defined).
# [bruce 080111]

try:
    __file__
except:
    # CAD_SRC_PATH can't be determined (by the present code)
    # (does this ever happen?)
    print "can't determine CAD_SRC_PATH"
    CAD_SRC_PATH = None 
else:
    import os
    CAD_SRC_PATH = os.path.dirname(__file__)
    assert os.path.basename(CAD_SRC_PATH) == "utilities"
    CAD_SRC_PATH = os.path.dirname(CAD_SRC_PATH)
    #print "CAD_SRC_PATH = %r" % CAD_SRC_PATH ### REMOVE WHEN WORKS, BEFORE COMMIT
    # [review: in a built Mac release, CAD_SRC_PATH might be
    # .../Contents/Resources/Python/site-packages.zip, or a related pathname
    # containing one more directory component; but an env var RESOURCEPATH
    # (spelling?) should also be available (only in a release and only on Mac),
    # and might make more sense to use then.]
    pass


# end
