# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
files_mmp.py -- reading MMP files

See also: files_mmp_writing.py, files_mmp_registration.py

@author: Josh, others
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050414 pulled this out of fileIO.py, cvs rev. 1.97
(of which it was the major part),
since I am splitting that into separate modules for each file format.

bruce 080304 split out the mmp writing part into its own file,
files_mmp_writing.py. That also contains the definition of
MMP_FORMAT_VERSION_TO_WRITE and the history of its values
and refers to the documentation for when to change it.
[Later that stuff was moved to mmpformat_versions.py.]

bruce 080304 split out the registration code, to avoid import cycles,
since anything should be able to import that, but the main reading code
(remaining in this file) needs to import a variety of model classes
for constructing them (since not everything uses the registration scheme
or should have to).
"""

import re, time

import foundation.env as env
from utilities import debug_flags

from model.chem import Atom
from model.jigs import AtomSet
from model.jigs import Anchor
from model.jigs import Stat
from model.jigs import Thermo
from model.jigs_motors import RotaryMotor
from model.jigs_motors import LinearMotor
from model.jigs_planes import GridPlane
from analysis.ESP.ESPImage import ESPImage
from model.jigs_measurements import MeasureAngle
from model.jigs_measurements import MeasureDihedral
from geometry.VQT import V, Q, A
from utilities.Log import redmsg, orangemsg, quote_html
from model.elements import PeriodicTable
from model.elements import Pl5
from model.bonds import bond_atoms
from model.chunk import Chunk
from foundation.Utility import Node
from foundation.Group import Group
from model.NamedView import NamedView # for reading one, and for isinstance

from utilities.debug import print_compact_traceback
from utilities.debug import print_compact_stack

from utilities.constants import gensym
from utilities.constants import interpret_dispName
from utilities.constants import SUCCESS, ABORTED, READ_ERROR

from model.bond_constants import find_bond
from model.bond_constants import V_SINGLE
from model.bond_constants import V_DOUBLE
from model.bond_constants import V_TRIPLE
from model.bond_constants import V_AROMATIC
from model.bond_constants import V_GRAPHITE
from model.bond_constants import V_CARBOMERIC

from model.Plane import Plane

from files.mmp.files_mmp_registration import find_registered_parser_class
from files.mmp.mmpformat_versions import parse_mmpformat, mmp_date_newer

# the following imports and the assignment they're used in
# should be replaced by some registration scheme
# (not urgent) [bruce 080115]
from dna.model.DnaGroup import DnaGroup
from dna.model.DnaSegment import DnaSegment
from dna.model.DnaStrand import DnaStrand
from cnt.model.NanotubeGroup import NanotubeGroup
from cnt.model.NanotubeSegment import NanotubeSegment

from dna.updater.fix_after_readmmp import will_special_updates_after_readmmp_do_anything

# ==

# KNOWN_INFO_KINDS lists the legal "kinds" of info encodable in info records.
# (Note: an "info kind" is a way of finding which object the info is about;
#  it's not related to the data type of the encoded info.)
#
# This is declared here, and checked in set_info_object,
# to make sure that the known info kinds are centrally listed,
# so that that aspect of the mmp format remains documented in this file.
#
# We also include comments about who & when added a specific info kind.
# (The dates might later be turned into code and used for some form of mmp file
#  version compatibility checking.)
#
# [bruce 071023]

KNOWN_INFO_KINDS = (
    'chunk',       #bruce 050217
    'opengroup',   #bruce 050421
    'leaf',        #bruce 050421
    'atom',        #bruce 050511
    'gamess',      #bruce 050701
    'espimage',    #mark 060108
    'povrayscene', #mark 060613
    'plane',
 )

# ==

# GROUP_CLASSIFICATIONS maps a "group classification identifier"
# (a string containing no whitespace) usable in the group mmp record
# (as of 080115) to a constructor function (typically a subclass of Group)
# whose API is the same as that of Group (when used as a constructor).
#
# THIS MUST BE KEPT CONSISTENT with the class constant assignments
# of _mmp_group_classifications in subclasses of Group.
#
# This assignment and the imports that support it ought to be replaced
# by a registration scheme. Not urgent. Alternatively, we could let these
# values depend on the assy being read into (a good thing to do in principle)
# and ask the assy to map these names to classes). [bruce 080115/080310]

_GROUP_CLASSIFICATIONS = { 
    'DnaGroup'         : DnaGroup,
    'DnaSegment'       : DnaSegment,
    'DnaStrand'        : DnaStrand,
    'Block'            : Group,
        #bruce 080331 changed this from Block -> Group, since Block is
        # deprecated; it should remain in this list indefinitely so reading
        # old mmp files continues to work.
    'NanotubeGroup'    : NanotubeGroup,
    'NanotubeSegment'  : NanotubeSegment,
 }

# == patterns for reading mmp files

#bruce 050414 comment: these pat constants are not presently used in any other files.

_name_pattern = re.compile(r"\(([^)]*)\)")
    # this has a single pattern group which matches a parenthesized string
    
old_csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
new_csyspat = re.compile("csys \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
namedviewpat = re.compile("namedview \((.+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+)\)")
datumpat = re.compile("datum \((.+)\) \((\d+), (\d+), (\d+)\) (.*) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)")
keypat = re.compile("\S+")
## molpat = re.compile("mol \(.*\) (\S\S\S)")
molpat = re.compile("mol \(.*\) (\w+)")
atom1pat = re.compile("atom (\d+) \((\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")
##atom2pat = re.compile("atom \d+ \(\d+\) \(.*\) (\S\S\S)")
atom2pat = re.compile("atom \d+ \(\d+\) \(.*\) (\w+)") # \w == [a-zA-Z0-9_]

# Old Rotary Motor record format: 
# rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
old_rmotpat = re.compile("rmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

# New Rotary Motor record format: 
# rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az) length radius spoke_radius
new_rmotpat = re.compile("rmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) (-?\d+\.\d+)")

# Old Linear Motor record format: 
# lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
old_lmotpat = re.compile("lmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\)")

# New Linear Motor record format: 
# lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az) length width spoke_radius
new_lmotpat = re.compile("lmotor \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+), (-?\d+), (-?\d+)\) \((-?\d+), (-?\d+), (-?\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) (-?\d+\.\d+)")

#Grid Plane record format:
#gridplane (name) (r, g, b) width height (cx, cy, cz) (w, x, y, z) grid_type line_type x_space y_space (gr, gg, gb) 
gridplane_pat = re.compile("gridplane \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) (\d+) (\d+) (-?\d+\.\d+) (-?\d+\.\d+) \((\d+), (\d+), (\d+)\)")

#Plane record format:
#plane (name) (r, g, b) width height (cx, cy, cz) (w, x, y, z)
plane_pat = re.compile("plane \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\)")

# ESP Image record format:
# espimage (name) (r, g, b) width height resolution (cx, cy, cz) (w, x, y, z) trans (fr, fg, fb) show_bbox win_offset edge_offset 
## esppat = re.compile("espimage \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) (\d+) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) (-?\d+\.\d+) \((\d+), (\d+), (\d+)\) (\d+) (-?\d+\.\d+) (-?\d+\.\d+)")
#bruce 060207 generalize pattern so espwindow is also accepted (to help fix bug 1357); safe forever, but can be removed after A7
esppat = re.compile("[a-z]* \((.+)\) \((\d+), (\d+), (\d+)\) (-?\d+\.\d+) (-?\d+\.\d+) (\d+) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) \((-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\) (-?\d+\.\d+) \((\d+), (\d+), (\d+)\) (\d+) (-?\d+\.\d+) (-?\d+\.\d+)")

# atomset (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}
atomsetpat = re.compile("atomset \((.+)\) \((\d+), (\d+), (\d+)\)")

# ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}
#bruce 060228 generalize pattern so "anchor" is also accepted; see also _read_anchor
groundpat = re.compile("[a-z]* \((.+)\) \((\d+), (\d+), (\d+)\)")

# stat (name) (r, g, b) (temp) first_atom last_atom boxed_atom
statpat = re.compile("stat \((.+)\) \((\d+), (\d+), (\d+)\) \((\d+)\)" )

# thermo (name) (r, g, b) first_atom last_atom boxed_atom
thermopat = re.compile("thermo \((.+)\) \((\d+), (\d+), (\d+)\)" )

# general jig pattern #bruce 050701
jigpat = re.compile("\((.+)\) \((\d+), (\d+), (\d+)\)")

# more readable regexps, wware 051103
# font names NEVER have parentheses in them, ala Postscript
nameRgbFontnameFontsize = ("\((.+)\) " +                    # (name)
                           "\((\d+), (\d+), (\d+)\) " +     # (r, g, b)
                           "\((.+)\) " +                    # (font_name)
                           "(\d+)")                         # font_size
_oneAtompat = " (\d+)"

# mdistance (name) (r, g, b) (font_name) font_size a1 a2
mdistancepat = re.compile("mdistance " + nameRgbFontnameFontsize +
                          _oneAtompat + _oneAtompat)

# mangle (name) (r, g, b) (font_name) font_size a1 a2 a3
manglepat = re.compile("mangle " + nameRgbFontnameFontsize +
                       _oneAtompat + _oneAtompat + _oneAtompat)

# mdihedral (name) (r, g, b) (font_name) font_size a1 a2 a3 a4
mdihedralpat = re.compile("mdihedral " + nameRgbFontnameFontsize +
                          _oneAtompat + _oneAtompat + _oneAtompat + _oneAtompat)

# == reading mmp files

_MMP_FORMAT_VERSION_WE_CAN_READ__MOST_CONSERVATIVE = '050920 required; 080321 preferred'
    # ideally, this should be identical to MMP_FORMAT_VERSION_TO_WRITE,
    # and should just be called _MMP_FORMAT_VERSION_WE_CAN_READ,
    # but sometimes it can temporarily differ (in either direction),
    # so we don't use the same constant.
    #
    # Note: this value is based on all the code that contributes to mmp reading,
    # not only the code in this file. That includes methods on model objects
    # for parsing info records, and registered mmp record parsers.
    # [bruce 080328 new feature and comment]

def _mmp_format_version_we_can_read(): # bruce 080328, revised 080410 (should it be a method?)
    from utilities.GlobalPreferences import debug_pref_read_bonds_compactly
    from utilities.GlobalPreferences import debug_pref_read_new_display_names
    
    if debug_pref_read_bonds_compactly() and debug_pref_read_new_display_names():
        # this is the default, as of 080328, still true 080410 and for upcoming
        # release of NE1 1.0.0; revised to a newer one, 080523, 080529
        res = '080328 required; 080529 preferred' # i.e. MMP_FORMAT_VERSION_TO_WRITE__WITH_COMPACT_BONDS_AND_NEW_DISPLAY_NAMES
    elif debug_pref_read_new_display_names():
        # this is the default which we *write*, as of 080410 and for upcoming
        # release of NE1 1.0.0; revised to a newer one, 080523, 080529
        # note: setting prefs to only read this high is only useful for testing
        res = '080327 required; 080529 preferred' # i.e. MMP_FORMAT_VERSION_TO_WRITE__WITH_NEW_DISPLAY_NAMES
    else:
        # setting prefs to only read this high is only useful for testing
        res = _MMP_FORMAT_VERSION_WE_CAN_READ__MOST_CONSERVATIVE
    return res

# ==

def decode_atom_coordinate(coord_string): #bruce 080521
    """
    Decode an atom coordinate string as used in the atom record
    of an mmp file (in the traditional format as of 080521).
    Return a float, in Angstroms.
    """
    # note: this is inlined in decode_atom_coordinates
    return float(coord_string) / 1000.0 # in Angstroms

def decode_atom_coordinates(xs, ys, zs): #bruce 080521
    """
    Decode three atom coordinate strings as used in the atom record
    of an mmp file (in the traditional format as of 080521).
    Interpret them as x, y, z coordinates respectively.
    Return a Numeric array of three floats, in Angstroms
    (which is the NE1 internal standard for representing a
     model space position).
    """
    # this would be correct (untested):
    ## return A(map( decode_atom_coordinate, [xs, ys, zs]))
    # but it's better to optimize by inlining decode_atom_coordinate:
    return V(float(xs), float(ys), float(zs)) / 1000.0

# ==

class _readmmp_state:
    """
    Hold the state needed by _readmmp between lines;
    and provide some methods to help with reading the lines.
    [See also the classes mmp_interp (another read-helper)
     and writemmp_mapping.]
    """
    #bruce 050405 made this class from most of _readmmp to help generalize it
    # (e.g. for reading sim input files for minimize selection)

    # initial values of instance variables
    # TODO: some or all of these are private -- rename them to indicate that [bruce 071023 comment]
    prevatom = None # the last atom read, if any
    prevcard = None # used in reading atoms and bonds [TODO: doc, make private]
    prevchunk = None # the current Chunk being built, if any [renamed from self.mol, bruce 071023]
    prevmotor = None # the last motor jig read, if any (used by shaft record)
    
    def __init__(self, assy, isInsert):
        self.assy = assy
            #bruce 060117 comment: self.assy is only used to pass to Node constructors (including _MarkerNode),
            # and to set assy.temperature and assy.mmpformat (only done if not isInsert, which looks like only use of isInsert here).
        self.isInsert = isInsert
        #bruce 050405 made the following from old _readmmp localvars, and revised their comments
        self.ndix = {}
        topgroup = Group("__opengroup__", assy, None)
            #bruce 050405 topgroup holds toplevel groups (or other items) as members; replaces old code's grouplist
        self.groupstack = [topgroup]
            #bruce 050405 revised this -- no longer stores names separately, and current group is now at end
            # stack (top at end) to store all unclosed groups
            # (the only group which can accept children, as we read the file, is always self.groupstack[-1];
            #  in the old code this was called opengroup [bruce 050405])
        self.sim_input_badnesses_so_far = {} # helps warn about sim-input files
        self.markers = {} #bruce 050422 for forward_ref records
        self._info_objects = {} #bruce 071017 for info records
            # (replacing attributes of self named by the specific kinds)
        self._registered_parser_objects = {} #bruce 071017
        self.listOfAtomsInFileOrder = []
        return

    def destroy(self):
        self.assy = self.ndix = self.groupstack = self.markers = None
        self.prevatom = None
        self.prevcard = None
        self.prevchunk = None
        self.prevmotor = None
        self.sim_input_badnesses_so_far = None
        self._info_objects = None
        self._registered_parser_objects = None
        self.listOfAtomsInFileOrder = None
        return

    def extract_toplevel_items(self):
        """
        for use only when done: extract the list of toplevel items
        (removing them from our artificial Group if any);
        but don't verify they are Groups or alter them, that's up to the caller.
        """
        for marker in self.markers.values():
            marker.kill() #bruce 050422; semi-guess
        self.markers = None
        if len(self.groupstack) > 1:
            self.warning("mmp file had %d unclosed groups" % (len(self.groupstack) - 1))
        topgroup = self.groupstack[0]
        self.groupstack = "error if you keep reading after this"
        res = topgroup.members[:]
        for m in res:
            topgroup.delmember(m)
        return res

    def warning(self, msg):
        msg = quote_html(msg)
        env.history.message( redmsg( "Warning: " + msg))

    def format_error(self, msg): ###e use this more widely?
        msg = quote_html(msg)
        env.history.message( redmsg( "Warning: mmp format error: " + msg))
            ###e and say what we'll do? review calls; syntax error

    def bug_error(self, msg):
        msg = quote_html(msg)
        env.history.message( redmsg( "Bug: " + msg))
    
    def readmmp_line(self, card):
        """
        returns None, or error msg(#k), or raises exception
        on bugs or maybe some syntax errors
        """
        key_m = keypat.match(card)
        if not key_m:
            # ignore blank lines (does this also ignore some erroneous lines??) #k
            return
        recordname = key_m.group(0)
        # recordname should now be the mmp record type, e.g. "group" or "mol"

        linemethod, errmsg = self._find_linemethod(recordname)

        if errmsg or not linemethod:
            return errmsg

        # if linemethod itself has an exception, best to let the caller handle it
        # (only it knows whether the line passed to us was made up or really in the file)
        return linemethod(card)

    def _find_linemethod(self, recordname):
        """
        [private]
        
        Look for a method for parsing one mmp file line
        which starts with recordname.
        
        @return: the tuple (linemethod, errmsg), where linemethod is a callable
                 which takes one argument (the entire line ### with \n or not??)
                 and returns None or an error message string, and errmsg is
                 None or an error message string from the process of looking
                 for the linemethod.
        """
        errmsg = None # will be changed below if an error message is needed
        linemethod = None # will be changed below when an mmp-line parser method is found
        
        # first look for a registered parser for this recordname
        
        parser = self._find_registered_parser_object(recordname)
        if parser:
            linemethod = parser.read_record
                # probably this is never None, but this code supports it being None
            if linemethod:
                return linemethod, errmsg

        # if there was no registered record parser, look for a built-in method to do it,
        # as a specially-named method of self, based on the recordname
        # (this is safe, since the prefix means arbitrary input can't find unintended methods)
        methodname = "_read_" + recordname # e.g. _read_group, _read_mol, ...
        try:
            linemethod = getattr(self, methodname, None)
        except:
            # I don't know if an exception can happen (e.g. from non-identifier chars in recordname),
            # and if it can, whether it would always be an AttributeError.
            ###e TODO: print_compact_traceback until i know
            linemethod = None
            errmsg = "syntax error or bug" ###e improve message
        else:
            if linemethod is None:
                # unrecognized mmp recordname -- not an error,
                # but [bruce 050217 new debug feature]
                # print a debug-only warning except for a comment line
                # (TODO: maybe only do this the first time we see it?)
                if debug_flags.atom_debug and recordname != '#':
                    print "atom_debug: fyi: unrecognized mmp record type ignored (not an error): %r" % recordname
            pass

        return linemethod, errmsg

    def _find_registered_parser_object(self, recordname):
        """
        Return an instance of the registered record-parser class for this recordname
        (cached for reuse while reading the one mmp file self will be used for),
        or None if no parser was registered for this recordname.
        """
        try:
            return self._registered_parser_objects[recordname]
        except KeyError:
            clas = find_registered_parser_class(recordname)
                # just one global registry, for now
            if clas:
                instance = clas(self, recordname)
            else:
                instance = None
                    # cache None too -- the query might be repeated
                    # just as much as if we had a parser for it
            self._registered_parser_objects[recordname] = instance
            return instance
        pass

    def get_name(self, card, default):
        """
        Get the object name from an mmp record line
        which represents the name in the usual way
        (as a parenthesized string immediately after the recordname),
        but don't decode it (see decode_name for that).

        @return: name
        @rtype: string

        @see: get_decoded_name_and_rest
        """
        # note: code also used in get_decoded_name_and_rest
        x = _name_pattern.search(card)
        if x:
            return x.group(1)
        print "warning: mmp record without a valid name field: %r" % (card,) #bruce 071019
        return gensym(default)
            # Note: I'm not sure it's safe/good to pass an assy argument
            # to this gensym, and I also think this probably never happens,
            # so it's best to be safe and not pass one. [bruce 080407 comment]
    
    def get_decoded_name_and_rest(self, card, default = None): #bruce 080115
        """
        Get the object name from an mmp record line
        which represents the name in the usual way
        (as an encoded parenthesized string immediately after the recordname).
        Return the tuple ( decoded name, stripped rest of record),
        or ( default, "" ) if the record line has the wrong format.
        
        @param card: the entire mmp record
        @type card: string
        
        @param default: what to return for the name (or pass to gensym
                        if a string) if the record line
                        has the wrong format; default value is None
                        (typically an error in later stages of the caller)
        @type default: anything, usually string or None
        
        @return: ( decoded name, stripped rest of record )
        @rtype: tuple of (string, string)

        @see: get_name
        """
        # note: copies some code from get_name
        x = _name_pattern.search(card)
        if x:
            # match succeeded
            name = self.decode_name( x.group(1) )
            rest = card.split(')', 1)[1]
            rest = rest.strip()
        else:
            # format error
            print "warning: mmp record without a valid name field: %r" % (card,) #bruce 071019
            if type(default) == type(""):
                name = gensym(default)
                    # Note: I'm not sure it's safe/good to pass an assy argument
                    # to this gensym, so I won't. [bruce 080407 comment]
            else:
                name = default
            rest = ""
        return ( name, rest)
    
    def decode_name(self, name): #bruce 050618 part of fixing part of bug 474
        """
        Invert the transformation done by the writer's encode_name method.
        """
        name = name.replace("%28",'(') # most of these replacements can be done in any order...
        name = name.replace("%29",')')
        name = name.replace("%25",'%') # ... but this one must be done last.
        return name

    # the remaining methods are parsers for specific records (soon to be split out
    # and registered -- bruce 071017), mixed with helper functions for their use
    
    def _read_group(self, card): # group: begins any kind of Group
        """
        Read the mmp record which indicates the beginning of a Group object
        (for Group or any of its specialized subclasses).

        Subsequent mmp records (including nested groups)
        will be read as members of this group,
        until a matching egroup record is read.
        
        @see: self._read_egroup
        """
        #bruce 080115 generalized this to use or save group classifications
        name, rest = self.get_decoded_name_and_rest(card, "Grp")
        assert name is not None
        old_opengroup = self.groupstack[-1]
        constructor = Group
        extra_classifications = []
        for classification in rest.split(): # from general to specific
            if classification in _GROUP_CLASSIFICATIONS:
                constructor = _GROUP_CLASSIFICATIONS[ classification ]
                    # assume this will always write out a classification
                    # sufficient to regenerate it; if that's ever not true
                    # we should save classification into extra_classifications
                    # here
                extra_classifications = []
            else:
                extra_classifications.append( classification )
            continue # use the last one we recognize; save and rewrite the extra ones
        new_opengroup = constructor(name, self.assy, old_opengroup)
            # this includes addchild of new group to old_opengroup (so don't call self.addmember)
        if extra_classifications:
            # make sure they can get written out again
            new_opengroup.set_extra_classifications( extra_classifications )
        self.groupstack.append(new_opengroup)

    def _read_egroup(self, card): # egroup: ends any kind of Group
        """
        Read the mmp record which indicates the end of a Group object
        (for Group or any of its specialized subclasses).
        
        @see: self._read_group
        """        
        name = self.get_name(card, "Grp")
        assert name is not None
        name = self.decode_name(name)
        if len(self.groupstack) == 1:
            return "egroup %r when no groups remain unclosed" % (name,)
        curgroup = self.groupstack.pop()
        curname = curgroup.name
        if name != curname:
            # note, unlike old code we've already popped a group; shouldn't matter [bruce 050405]
            return "mismatched group records: egroup %r tried to match group %r" % (name, curname)
        return None # success
    
    def _read_mol(self, card): # mol: start a Chunk
        name = self.get_name(card, "Mole")
        name = self.decode_name(name)
        mol = Chunk(self.assy,  name)
        self.prevchunk = mol
            # so its atoms, etc, can find it (might not be needed if they'd search for it) [bruce 050405 comment]
            # now that I removed _addMolecule, this is less often reset to None,
            # so we'd detect more errors if they did search for it [bruce 050405]
        disp = molpat.match(card)
        if disp:
            mol.setDisplayStyle(interpret_dispName(disp.group(1), atom = False)) #bruce 080324 revised
        self.addmember(mol) #bruce 050405; removes need for _addMolecule

    def _read_atom(self, card):
        m = atom1pat.match(card)
        if not m:
            print card
        n = int(m.group(1))
        try:
            element = PeriodicTable.getElement(int(m.group(2)))
            sym = element.symbol
        except:
            # catch unsupported element error [bruce 080115] [untested?]
            # todo: improve getElement so we can narrow down exception type,
            # or turn this into a special return value; or perhaps better,
            # permit creating an atom of an unknown element
            # (by transparently extending getElement to create one)
            sym = "C"
            errmsg = "unsupported element in this mmp line; using %s: %s" % (sym, card,)
            self.format_error(errmsg)
        ## xyz = A(map(float, [m.group(3), m.group(4), m.group(5)])) / 1000.0
        xyz = decode_atom_coordinates( m.group(3), m.group(4), m.group(5) ) #bruce 080521
        if self.prevchunk is None:
            #bruce 050405 new feature for reading new bare sim-input mmp files
            self.guess_sim_input('missing_group_or_chunk')
            self.prevchunk = Chunk(self.assy,  "sim chunk")
            self.addmember(self.prevchunk)
        a = Atom(sym, xyz, self.prevchunk) # sets default atomtype for the element [behavior of that was revised by bruce 050707]
        self.listOfAtomsInFileOrder.append(a)
        a.unset_atomtype() # let it guess atomtype later from the bonds read from subsequent mmp records [bruce 050707]
        disp = atom2pat.match(card)
        if disp:
            a.setDisplayStyle(interpret_dispName(disp.group(1))) #bruce 080324 revised
        self.ndix[n] = a
        self.prevatom = a
        self.prevcard = card
        return

    def _read_bond1(self, card):
        return self.read_bond_record(card, V_SINGLE)
        
    def _read_bond2(self, card):
        return self.read_bond_record(card, V_DOUBLE)
        
    def _read_bond3(self, card):
        return self.read_bond_record(card, V_TRIPLE)
        
    def _read_bonda(self, card):
        return self.read_bond_record(card, V_AROMATIC)
        
    def _read_bondg(self, card):
        return self.read_bond_record(card, V_GRAPHITE)
        
    def _read_bondc(self, card): #bruce 050920 added this
        return self.read_bond_record(card, V_CARBOMERIC)

    def read_bond_record(self, card, valence):
        list1 = map(int, re.findall("\d+", card[5:])) # note: this assumes all bond mmp-record-names are the same length, 5 chars.
        try:
            for a in map((lambda n: self.ndix[n]), list1):
                bond_atoms( self.prevatom, a, valence, no_corrections = True) # bruce 050502 revised this
        except KeyError:
            print "error in MMP file: atom ", self.prevcard
            print card
            #e better error action, like some exception?

    def _read_bond_direction(self, card): #bruce 070415
        atomcodes = card.strip().split()[1:] # note: these are strings, but self.ndix needs ints
        assert len(atomcodes) >= 2
        atoms = map((lambda nstr: self.ndix[int(nstr)]), atomcodes)
        for atom1, atom2 in zip(atoms[:-1], atoms[1:]):
            bond = find_bond(atom1, atom2)
            bond.set_bond_direction_from(atom1, 1)
        return

    def _read_bond_chain(self, card): #bruce 080328
        from utilities.GlobalPreferences import debug_pref_read_bonds_compactly
        if not debug_pref_read_bonds_compactly():
            summary_format = "Error: input file contains [N] bond_chain record(s) we can't read"
            env.history.deferred_summary_message( redmsg(summary_format))
            return
        fields = card.strip().split()[1:]
        assert len(fields) >= 2 # beginning and ending atom code
            # (ignore extra fields for upwards compatibility)
        # note: following code is similar in two methods
        atoms_in_range = self.atoms_in_range(fields[0], fields[1])
        if len(atoms_in_range) > 1: # not sure if this test is required for correctness
            for atom1, atom2 in zip( atoms_in_range[:-1], atoms_in_range[1:] ):
                bond_atoms( atom1, atom2, V_SINGLE, no_corrections = True)
            pass
        return

    def _read_directional_bond_chain(self, card): #bruce 080328
        from utilities.GlobalPreferences import debug_pref_read_bonds_compactly
        if not debug_pref_read_bonds_compactly():
            summary_format = "Error: input file contains [N] directional_bond_chain record(s) we can't read"
            env.history.deferred_summary_message( redmsg(summary_format))
            return
        fields = card.strip().split()[1:]
        assert len(fields) >= 3 # beginning and ending atom code, and bond direction
            # (ignore extra fields for upwards compatibility;
            #  optional 4th field might be sequence info [nim], default 'X')
        # note: following code is similar in two methods
        atoms_in_range = self.atoms_in_range(fields[0], fields[1])
        bond_dir = int(fields[2])
        assert bond_dir in (1, -1)
        if len(atoms_in_range) > 1: # not sure if this test is required for correctness
            for atom1, atom2 in zip( atoms_in_range[:-1], atoms_in_range[1:] ):
                bond = bond_atoms( atom1, atom2, V_SINGLE, no_corrections = True)
                bond.set_bond_direction_from(atom1, bond_dir)
            pass
        if len(fields) >= 4:
            # store optional dna base sequence info
            # (allowed to be shorter than needed, but not longer;
            #  X or missing letter is not stored, so it won't override
            #  an earlier per-atom info record specifying the dnaBaseName)
            sequence = fields[3]
            assert sequence.isalpha()
            pointer = 0 # to next unused character within sequence
            for atom in atoms_in_range:
                if pointer >= len(sequence):
                    break
                if atom.element.role == 'strand' and not atom.element is Pl5:
                    # atom is a strand_sugar
                    letter = sequence[pointer]
                    pointer += 1
                    if letter != 'X':
                        atom.setDnaBaseName(letter)
                continue
            if pointer < len(sequence):
                assert 0, "extra sequence info: only %d of %d chars were assigned from %r" % \
                       (pointer, len(sequence), card)
            pass    
        return

    def _read_dna_rung_bonds(self, card): #bruce 080328
        from utilities.GlobalPreferences import debug_pref_read_bonds_compactly
        if not debug_pref_read_bonds_compactly():
            summary_format = "Error: input file contains [N] dna_rung_bonds record(s) we can't read"
            env.history.deferred_summary_message( redmsg(summary_format))
            return
        fields = card.strip().split()[1:]
        assert len(fields) >= 4 # beginning and ending atom codes, for chunk1 and chunk2
            # (ignore extra fields for upwards compatibility)
        atoms_in_range1 = self.atoms_in_range(fields[0], fields[1])
        atoms_in_range2 = self.atoms_in_range(fields[2], fields[3])
        def ok(atom):
            assert isinstance(atom, Atom)
            return atom.element.role == 'axis' or \
                   (atom.element.role == 'strand' and not atom.element is Pl5)
        atoms1 = filter(ok, atoms_in_range1)
        atoms2 = filter(ok, atoms_in_range2)
        assert len(atoms1) == len(atoms2), \
               "qualifying atom counts %d and %d don't match in %r" % \
               (len(atoms1), len(atoms2), card)
        for atom1, atom2 in zip(atoms1, atoms2):
            bond_atoms( atom1, atom2, V_SINGLE, no_corrections = True)
        return

    def atoms_in_range(self, start, end): #bruce 080328
        """
        Return all the atoms whose atomcodes in self are between start and end,
        inclusive. Start and end can be equal, meaning return one atom.
        """
        start = int(start)
        end = int(end)
        assert 1 <= start <= end
        res = [self.ndix[code] for code in range(start, end+1)]
            # that will fail if any atom in that range wasn't yet read
        return res
    
    # == jig reading methods.

    # Note that there are at least three different ways various jigs handle
    # reading their atom list: in a separate shaft record which occurs after
    # their main mmp record, whose atoms are passed to jig.setShaft;
    # or in the same record, passed to the constructor;
    # or in the same record, but passed to setProps after the jig is made.
    # This ought to be cleaned up sometime.
    # See also self.read_new_jig, which is the beginning of a partial cleanup.
    # [bruce 080227 comment]
    
    # Read the MMP record for a Rotary Motor as either:
    # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az) length, radius, spoke_radius
    # rmotor (name) (r, g, b) torque speed (cx, cy, cz) (ax, ay, az)
    # (note: the atoms are read separately from a subsequent shaft record)
    def _read_rmotor(self, card):
        m = new_rmotpat.match(card) # Try to read card with new format
        if not m:
            m = old_rmotpat.match(card) # If that didn't work, read card with old format
        ngroups = len(m.groups()) # ngroups = number of fields found (12 = old, 15 = new)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )
        torq = float(m.group(5))
        sped = float(m.group(6))
        cxyz = A(map(float, [m.group(7), m.group(8), m.group(9)])) / 1000.0
        axyz = A(map(float, [m.group(10), m.group(11), m.group(12)])) / 1000.0
        if ngroups == 15: # if we have 15 fields, we have the length, radius and spoke radius.
            length = float(m.group(13))
            radius = float(m.group(14))
            sradius = float(m.group(15))
        else: # if not, set the default values for length, radius and spoke radius.
            length = 10.0
            radius = 2.0
            sradius = 0.5
        motor = RotaryMotor(self.assy)
        props = name, col, torq, sped, cxyz, axyz, length, radius, sradius
        motor.setProps(props)
        self.addmotor(motor)

    def addmotor(self, motor): #bruce 050405 split this out
        self.addmember(motor)
        self.prevmotor = motor # might not be needed if we just looked for it when we need it [bruce 050405 comment]

    def _read_shaft(self, card):
        list1 = map(int, re.findall("\d+", card[6:]))
        list1 = map((lambda n: self.ndix[n]), list1)
        self.prevmotor.setShaft(list1)
          
    # Read the MMP record for a Linear Motor as:
    # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az) length, width, spoke_radius
    # lmotor (name) (r, g, b) force stiffness (cx, cy, cz) (ax, ay, az)
    # (note: the atoms are read separately from a subsequent shaft record)
    def _read_lmotor(self, card):
        m = new_lmotpat.match(card) # Try to read card with new format
        if not m:
            m = old_lmotpat.match(card) # If that didn't work, read card with old format
        ngroups = len(m.groups()) # ngroups = number of fields found (12 = old, 15 = new)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )
        force = float(m.group(5))
        stiffness = float(m.group(6))
        cxyz = A(map(float, [m.group(7), m.group(8), m.group(9)])) / 1000.0
        axyz = A(map(float, [m.group(10), m.group(11), m.group(12)])) / 1000.0
        if ngroups == 15: # if we have 15 fields, we have the length, width and spoke radius.
            length = float(m.group(13))
            width = float(m.group(14))
            sradius = float(m.group(15))
        else: # if not, set the default values for length, width and spoke radius.
            length = 10.0
            width = 2.0
            sradius = 0.5
        motor = LinearMotor(self.assy)
        props = name, col, force, stiffness, cxyz, axyz, length, width, sradius
        motor.setProps(props)
        self.addmotor(motor)

    def _read_gridplane(self, card):
        """
        Read the MMP record for a Grid Plane jig as:
        
        gridplane (name) (r, g, b) width height (cx, cy, cz) (w, x, y, z) grid_type line_type x_space y_space (gr, gg, gb) 
        """
        m = gridplane_pat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        border_color = map(lambda (x): int(x) / 255.0, [m.group(2), m.group(3), m.group(4)])
        width = float(m.group(5)); height = float(m.group(6)); 
        center = A(map(float, [m.group(7), m.group(8), m.group(9)]))
        quat = A(map(float, [m.group(10), m.group(11), m.group(12), m.group(13)]))
        grid_type = int(m.group(14)); line_type = int(m.group(15)); x_space = float(m.group(16)); y_space = float(m.group(17))
        grid_color = map(lambda (x): int(x) / 255.0, [m.group(18), m.group(19), m.group(20)])
        
        gridPlane = GridPlane(self.assy, [], READ_FROM_MMP = True)
        gridPlane.setProps(name, border_color, width, height, center, quat, grid_type, \
                           line_type, x_space, y_space, grid_color)
        self.addmember(gridPlane)
    
    #Read mmp record for a Reference Plane
    def _read_plane(self, card):
        """
        Read the MMP record for a Reference Plane as:

        plane (name) (r, g, b) width height (cx, cy, cz) (w, x, y, z) 
        """
        m = plane_pat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        #border_color = color of the border for front side of the reference plane. 
        #user can't set it for now. -- ninad 20070104
        border_color = map(lambda (x): int(x) / 255.0, [m.group(2), m.group(3), m.group(4)])
        width = float(m.group(5)); height = float(m.group(6)); 
        center = A(map(float, [m.group(7), m.group(8), m.group(9)]))
        quat = A(map(float, [m.group(10), m.group(11), m.group(12), m.group(13)]))
        
        #@@HACK: Plane.setProps() accepts a tuple that must also contain values 
        #for the grid related attrs such as gridColor, gridLineType etc. 
        #But as of 2008-06-25 those (new) attrs are set using self.set_info_object 
        #(see Plane.readmmp_info_plane_setitem)  because they are a part of 
        #'info' record (which allows upward and backword compatibility for reading
        #mmp files of different versions.) There is a spacial (old) code 
        # to handle those info records. To satisfy that code as well as the 
        #Plane.setProps() API method, we do the following -- 1. We pass 'None' 
        #for the items, in the  'props' tuple that are a part of info record 
        #2. Note that the info record will be read afterwords in this method
        #3. Plane.setProps takes extra precaution to check if the passed 
        #parameter is None (and set its attrs only when that param is not None)
        # --  Ninad 2008-06-25
        gridColor = None        
        gridLineType = None
        gridXSpacing = None
        gridYSpacing = None
        originLocation = None
        displayLabelStyle = None
        
        plane = Plane(self.assy.w, READ_FROM_MMP = True)
        props = (name, border_color, width, height, center, quat,  
                 gridColor, gridLineType, gridXSpacing, gridYSpacing, 
                 originLocation, displayLabelStyle)
        plane.setProps(props)
        self.addmember(plane)
        
        #This sets the Plane attrs such as gridColor, gridLineType etc. 
        self.set_info_object('plane', plane)

    # Read the MMP record for a Atom Set as:
    # atomset (name) atom1 atom2 ... atom_n {no limit}

    def _read_atomset(self, card):
        m = atomsetpat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )

        # Read in the list of atoms
        card = card[card.index(")") + 1:] # skip past the color field
        list1 = map(int, re.findall("\d+", card[card.index(")") + 1:]))
        list1 = map((lambda n: self.ndix[n]), list1)
        
        as = AtomSet(self.assy, list1) # create atom set and set props
        as.name = name
        as.color = col
        self.addmember(as)
        
    def _read_espimage(self, card):
        """
        Read the MMP record for an ESP Image jig as:

        espimage (name) (r, g, b) width height resolution (cx, cy, cz) 
        (w, x, y, z) trans (fr, fg, fb) show_bbox win_offset edge_offset.
        """
        m = esppat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        border_color = map(lambda (x): int(x) / 255.0, [m.group(2), m.group(3), m.group(4)])
        width = float(m.group(5)); height = float(m.group(6)); resolution = int(m.group(7))
        center = A(map(float, [m.group(8), m.group(9), m.group(10)]))
        quat = A(map(float, [m.group(11), m.group(12), m.group(13), m.group(14)]))
        trans = float(m.group(15))
        fill_color = map(lambda (x): int(x) / 255.0, [m.group(16), m.group(17), m.group(18)])
        show_bbox = int(m.group(19))
        win_offset = float(m.group(20)); edge_offset = float(m.group(21))
        
        espImage = ESPImage(self.assy, [], READ_FROM_MMP = True)
        espImage.setProps(name, border_color, width, height, resolution, center, quat, trans, fill_color, show_bbox, win_offset, edge_offset)
        self.addmember(espImage)

        # for interpreting "info espimage" records:
        self.set_info_object('espimage', espImage)
        return

    _read_espwindow = _read_espimage
        #bruce 060207 help fix bug 1357 (read older mmprecord for ESP Image, for compatibility with older bug report attachments)
        # (the fix also required a change to esppat)
        # (this can be removed after A7 is released, but for now it's convenient to have it so old bug reports remain useful)
    
    # Read the MMP record for a Ground (Anchor) as:
    # ground (name) (r, g, b) atom1 atom2 ... atom25 {up to 25}

    def _read_ground(self, card): # see also _read_anchor
        m = groundpat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )

        # Read in the list of atoms
        card = card[card.index(")") + 1 :] # skip past the color field
        list1 = map(int, re.findall("\d+", card[card.index(")") + 1 :]))
        list1 = map((lambda n: self.ndix[n]), list1)
        
        gr = Anchor(self.assy, list1) # create ground and set props
        gr.name = name
        gr.color = col
        self.addmember(gr)

    _read_anchor = _read_ground #bruce 060228 (part of making anchor work when reading future mmp files, before prerelease snapshots)

    # Read the MMP record for a MeasureDistance, wware 051103
    # mdistance (name) (r, g, b) (font_name) font_size a1 a2
    # no longer modeled on motor, wware 051103
    def _read_mdistance(self, card):
        from model.jigs_measurements import MeasureDistance
        m = mdistancepat.match(card) # Try to read card
        assert len(m.groups()) == 8
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )
        font_name = m.group(5)
        font_size = int(m.group(6))
        atomlist = map(int, [m.group(7), m.group(8)])
        lst = map(lambda n: self.ndix[n], atomlist)
        mdist = MeasureDistance(self.assy, [ ])
        mdist.setProps(name, col, font_name, font_size, lst)
        self.addmember(mdist)

    # Read the MMP record for a MeasureAngle, wware 051103
    # mangle (name) (r, g, b) (font_name) font_size a1 a2 a3
    # no longer modeled on motor, wware 051103
    def _read_mangle(self, card):
        m = manglepat.match(card) # Try to read card
        assert len(m.groups()) == 9
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )
        font_name = m.group(5)
        font_size = int(m.group(6))
        atomlist = map(int, [m.group(7), m.group(8), m.group(9)])
        lst = map(lambda n: self.ndix[n], atomlist)
        mang = MeasureAngle(self.assy, [ ])
        mang.setProps(name, col, font_name, font_size, lst)
        self.addmember(mang)

    # Read the MMP record for a MeasureDistance, wware 051103
    # mdihedral (name) (r, g, b) (font_name) font_size a1 a2 a3 a4
    # no longer modeled on motor, wware 051103
    def _read_mdihedral(self, card):
        m = mdihedralpat.match(card) # Try to read card
        assert len(m.groups()) == 10
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )
        font_name = m.group(5)
        font_size = int(m.group(6))
        atomlist = map(int, [m.group(7), m.group(8), m.group(9), m.group(10)])
        lst = map(lambda n: self.ndix[n], atomlist)
        mdih = MeasureDihedral(self.assy, [ ])
        mdih.setProps(name, col, font_name, font_size, lst)
        self.addmember(mdih)

    def read_new_jig(self, card, constructor): #bruce 050701
        """
        Helper method to read any sort of sufficiently new jig from an mmp file
        and add it to self.assy using self.addmember.
        
        Args are:
        card - the mmp file line.
        constructor - function that takes assy and atomlist and makes a new jig, without putting up any dialog.
        """
        # this method will give one place to fix things in the future (for new jig types),
        # like the max number of atoms per jig.
        recordname, rest = card.split(None, 1)
        del recordname
        card = rest
        
        m = jigpat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )

        # Read in the list of atoms
        # [max number of atoms used to be limited by max mmp-line length
        #  of 511 bytes; I think that limit was removed long ago
        #  but this should be verified (in cad and sim readers)
        #  [bruce 080227 comment]]
        card = card[card.index(")") + 1:] # skip past the color field
        list1 = map(int, re.findall("\d+", card[card.index(")") + 1:]))
        list1 = map((lambda n: self.ndix[n]), list1)
        
        jig = constructor(self.assy, list1) # create jig and set some properties -- constructor must not put up a dialog
        jig.name = name
        jig.color = col
            # (other properties, if any, should be specified later in the file by some kind of "info" records)
        self.addmember(jig)
        return jig
        
    # Read the MMP record for a Thermostat as:
    # stat (name) (r, g, b) (temp) first_atom last_atom box_atom
    
    def _read_stat(self, card):
        m = statpat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )
        temp = m.group(5)

        # Read in the list of atoms
        card = card[card.index(")") + 1:] # skip past the color field
        card = card[card.index(")") + 1:] # skip past the temp field
        list1 = map(int, re.findall("\d+", card[card.index(")") + 1:]))
        
        # We want "list1" to contain only the 3rd item, so let's remove 
        # first_atom (1st item) and last_atom (2nd item) in list1.
        # They will get regenerated in the Thermo constructor.  
        # Mark 050129
        if len(list1) > 2:
            del list1[0:2]
        
        # Now remove everything else from list1 except for the boxed_atom.
        # This would happen if we loaded an old part with more than 3 atoms listed.
        if len(list1) > 1:
            del list1[1:]
            msg = "a thermostat record was found (" + name + ") in the part which contained extra atoms.  They will be ignored."
            self.warning(msg)
            
        list1 = map((lambda n: self.ndix[n]), list1)

        sr = Stat(self.assy, list1) # create stat and set props
        sr.name = name
        sr.color = col
        sr.temp = temp
        self.addmember(sr)

    # Read the MMP record for a Thermometer as:
    # thermo (name) (r, g, b) first_atom last_atom box_atom
            
    def _read_thermo(self, card):
        m = thermopat.match(card)
        name = m.group(1)
        name = self.decode_name(name)
        col = map(lambda (x): int(x) / 255.0,
                  [m.group(2), m.group(3), m.group(4)] )

        # Read in the list of atoms
        card = card[card.index(")") + 1:] # skip past the color field
        list1 = map(int, re.findall("\d+", card[card.index(")") + 1:]))
        
        # We want "list1" to contain only the 3rd item, so let's remove 
        # first_atom (1st item) and last_atom (2nd item) in list1.
        # They will get regenerated in the Thermo constructor.  
        # Mark 050129
        if len(list1) > 2:
            del list1[0:2]
        
        # Now remove everything else from list1 except for the boxed_atom.
        # This would happen if we loaded an old part with more than 3 atoms listed.
        if len(list1) > 1:
            del list1[1:]
            msg = "a thermometer record was found in the part which contained extra atoms.  They will be ignored."
            self.warning(msg)
            
        list1 = map((lambda n: self.ndix[n]), list1)

        sr = Thermo(self.assy, list1) # create stat and set props
        sr.name = name
        sr.color = col
        self.addmember(sr)
    
    def _read_namedview(self, card):
        """
        Read the MMP record for a I{namedview} as:

        namedview (name) (quat.w, quat.x, quat.y, quat.z) (scale) (pov.x, pov.y, pov.z) (zoom factor)
        
        @note: Currently, "namedview" records are treated as an alias for the
        "csys" record. The writer NamedView.writemmp() will switch to writing
        "namedview" records (instead of "csys") soon.
        Mark 2008-02-07.
        """
        #bruce 050418 revising this to not have side effects on assy.
        # Instead, caller can do that by scanning the group these are read into.
        # This means we can now ignore the isInsert flag and always return
        # these records. Finally, I'll return them all, not just the ones with
        # special names we recognize (the prior code only called self.addmember
        # if the namedview name was HomeView or LastView); caller can detect 
        # those special names when it needs to.       
        m = namedviewpat.match(card)      
        name = m.group(1)
        name = self.decode_name(name)
        wxyz = A(map(float, [m.group(2), m.group(3), m.group(4), m.group(5)]))
        scale = float(m.group(6))
        pov = A(map(float, [m.group(7), m.group(8), m.group(9)]))
        zoomFactor = float(m.group(10))
        namedView = NamedView(self.assy, name, scale, pov, zoomFactor, wxyz)
        self.addmember(namedView) 
            # regardless of name; no side effects on assy (yet) for any name,
            # though later code will recognize the names HomeView and LastView
            # and treat them specially.
            # (050421 extension: also some related names, for Part views)
                
    def _read_csys(self, card): # csys -- really a named view.
        """
        Read the MMP record for a I{csys} as:
        
        csys (name) (quat.w, quat.x, quat.y, quat.z) (scale) (pov.x, pov.y, pov.z) (zoom factor)
        
        @note: Currently, "namedview" records are treated as an alias for the
        "csys" record. The writer NamedView.writemmp() will switch to writing
        "namedview" records (instead of "csys") soon.
        Mark 2008-02-07.
        """
        #bruce 050418 revising this to not have side effects on assy.
        # Instead, caller can do that by scanning the group these are read into.
        # This means we can now ignore the isInsert flag and always return
        # these records. Finally, I'll return them all, not just the ones with
        # special names we recognize (the prior code only called self.addmember
        # if the csys name was HomeView or LastView); caller can detect those
        # special names when it needs to.
        ## if not self.isInsert: #Skip this record if inserting
        ###Huaicai 1/27/05, new file format with home view 
        ### and last view information        
        m = new_csyspat.match(card)
        if m:        
            name = m.group(1)
            name = self.decode_name(name)
            wxyz = A(map(float, [m.group(2), m.group(3),
                                 m.group(4), m.group(5)] ))
            scale = float(m.group(6))
            pov = A(map(float, [m.group(7), m.group(8), m.group(9)]))
            zoomFactor = float(m.group(10))
            namedView = NamedView(self.assy, name, scale, pov, zoomFactor, wxyz)
            self.addmember(namedView) 
                # regardless of name; no side effects on assy (yet) for any
                # name, though later code will recognize the names HomeView and 
                # LastView and treat them specially
                # (050421 extension: also some related names, for Part views)
        else:
            m = old_csyspat.match(card)
            if m:
                name = m.group(1)
                name = self.decode_name(name)
                wxyz = A(map(float, [m.group(2), m.group(3),
                                     m.group(4), m.group(5)] ))
                scale = float(m.group(6))
                homeView = NamedView(self.assy, "OldVersion", scale, V(0,0,0), 1.0, wxyz)
                    #bruce 050417 comment
                    # (about Huaicai's preexisting code, some of which I moved into this file 050418):
                    # this name "OldVersion" is detected in fix_assy_and_glpane_views_after_readmmp
                    # (called from MWsemantics.fileOpen, one of our callers)
                    # and changed to "HomeView", also triggering other side effects on glpane at that time.
                lastView = NamedView(self.assy, "LastView", scale, V(0,0,0),
                                     1.0, A([0.0, 1.0, 0.0, 0.0]) )
                self.addmember(homeView)
                self.addmember(lastView)
            else:
                print "bad format in csys record, ignored:", card
        return

    def _read_datum(self, card): # datum -- Datum object -- old version deprecated by bruce 050417
        pass # don't warn about an unrecognized mmp record, even when atom_debug

    def addmember(self, thing): #bruce 050405 split this out
        self.groupstack[-1].addchild(thing)
        
    def _read_waals(self, card): # waals -- van der Waals Interactions
        pass # code was wrong -- to be implemented later
        
    def _read_kelvin(self, card): # kelvin -- Temperature in Kelvin (simulation parameter)
        if not self.isInsert: # Skip this record if inserting
            m = re.match("kelvin (\d+)", card)
            n = int(m.group(1))
            self.assy.temperature = n
            
    def _read_mmpformat(self, card): # mmpformat -- MMP File Format. Mark 050130
        # revised by bruce 080328
        m = re.match("mmpformat (.*)", card)
        mmpformat = m.group(1)
        if not self.isInsert: # Skip this side effect if inserting
            self.assy.mmpformat = mmpformat
        # warn if format might be too new, or if we can't understand
        # mmpformat record at all [new feature, bruce 080328]
        okjunk, can_read_required, can_read_preferred = parse_mmpformat( _mmp_format_version_we_can_read() )
        assert okjunk
        msg = ""
        wrapper = None
        try:
            ok, required, preferred = parse_mmpformat(mmpformat)
        except:
            print_compact_traceback("exception or syntax error while parsing [%s]: " % card.strip())
            msg = "Error: bug or syntax error in mmpformat record, file corrupt or too new: [%s]" % \
                      quote_html(card.strip())
            wrapper = redmsg
        else:
            if not ok:
                msg = "Warning: can't parse mmpformat record, file might be too new: [%s]" % \
                      quote_html(card.strip())
                wrapper = redmsg # intentional, not a typo: a red "Warning"
            elif mmp_date_newer(required, can_read_required):
                msg = "Warning: mmpformat requires newer reading code; essential data might be unreadable: [%s]" % \
                      quote_html(card.strip())
                wrapper = redmsg
            elif mmp_date_newer(preferred, can_read_preferred):
                msg = "Note: mmpformat prefers newer reading code for some data: [%s]" % \
                      quote_html(card.strip())
                wrapper = orangemsg
            pass
        if wrapper:
            msg = wrapper(msg)
        if msg:
            env.history.message(msg)
        return

    def _read_end1(self, card): # end1 -- End of main tree
        pass

    def _read_end(self, card): # end -- end of file
        pass
    
    def _read_info(self, card):
        #bruce 050217 new mmp record, for optional info about
        # various types of objects which occur earlier in the file
        # (what I mean by "optional" is that it's never an error for the
        #  specified type of thing or type of info to not be recognized,
        #  as can happen when a new file is read by older code)
        
        # Find current chunk -- how we do this depends on details of
        # the other mmp-record readers in this big if/elif statement,
        # and is likely to need changing sometime. It's self.prevchunk.
        # Now make dict of all current items that info record might refer to.
        currents = dict(
            chunk = self.prevchunk,
            opengroup = self.groupstack[-1], #bruce 050421
            leaf = ([None] + self.groupstack[-1].members)[-1], #bruce 050421
            atom = self.prevatom, #bruce 050511
        )
        currents.update( self._info_objects) #bruce 071017 
        interp = mmp_interp(self.ndix, self.markers) #e could optim by using the same object each time [like 'self']
        readmmp_info(card, currents, interp) # has side effect on object referred to by card
        return

    def set_info_object(self, kind, model_component): #bruce 071017
        if kind not in KNOWN_INFO_KINDS:
            # for motivation, see comment next to definition of KNOWN_INFO_KINDS
            # [bruce 071023]
            print_compact_stack( "warning: unrecognized info kind, %r: " % (kind,) )
        self._info_objects[kind] = model_component
        return
    
    def _read_forward_ref(self, card):
        """
        forward_ref (%s) ...
        """
        # add a marker which can be used later to insert the target node in the right place,
        # and also remember the marker here in the mapping (so we can offer that service) ###doc better
        lp_id_rp = card.split()[1]
        assert lp_id_rp[0] + lp_id_rp[-1] == "()"
        ref_id = lp_id_rp[1:-1]
        marker = _MarkerNode(self.assy, ref_id) # note: we remove this if not used, so its node type might not matter much.
        self.addmember(marker)
        self.markers[ref_id] = marker

    def guess_sim_input(self, type): #bruce 050405
        """
        Caller finds (and will correct) weird structure which makes us guess
        this is a sim input file of the specified type;
        warn user if you have not already given the same warning
        (normally only one such warning should appear, so warn about that as well).
        """
        # once we see how this is used, we'll revise it to be more like a "state machine"
        # knowing the expected behavior for the various types of files.
        bad_to_worse = ['no_shelf','one_part','missing_group_or_chunk'] # order is not yet used
        badness = bad_to_worse.index(type)
        if badness not in self.sim_input_badnesses_so_far:
            self.sim_input_badnesses_so_far[badness] = type
            if type == 'missing_group_or_chunk' or type == 'one_part':
                # (this message is a guess, since erroneous files could give rise to this too)
                # (#e To narrow down the cmd that wrote it, we'd need more info than type or
                #  even file comment, from old files -- sorry; maybe we should add an mmp record for
                #  the command that made the file! Will it be bad that file contents are nondet (eg for md5)?
                #  Probably not, since they were until recently anyway, due to dict item arb order.)
                msg = "mmp file probably written by Adjust or Minimize or Simulate -- " \
                      "lacks original file's chunk/group structure and display modes; " \
                      "unreadable by pre-Alpha5 versions unless resaved." #e revise version name
            elif type == 'no_shelf':
                # (this might not happen at all for files written by Alpha5 and beyond)
                # comment from old code's fix_grouplist:
                #bruce 050217 upward-compatible reader extension (needs no mmpformat-record change):
                # permit missing 3rd group, so we can read mmp files written as input for the simulator
                # (and since there is no good reason not to!)
                msg = "this mmp file was written as input for the simulator, and contains no clipboard items" #e add required version
            else:
                msg = "bug in guess_sim_input: missing message for %r" % type
            self.warning( msg)
            # normally only one of these warnings will occur, so we also ought to warn if that is not what happens...
            if len(self.sim_input_badnesses_so_far) > 1:
                self.format_error("the prior warnings should not appear together for the same file")
        return
    
    pass # end of class _readmmp_state

# helper for forward_ref

class _MarkerNode(Node):
    def __init__(self, assy, ref_id):
        name = ref_id
        Node.__init__(self, assy, name) # will passing no assy be legal? I doubt it... so don't bother trying.
        return
    pass

# helpers for _read_info method:

class mmp_interp: #bruce 050217; revised docstrings 050422
    """
    helps translate object refs in mmp file to their objects, while reading the file
    [compare to class writemmp_mapping, which helps turn objs to their refs while writing the file]
    [but also compare to class _readmmp_state... maybe this should be the same object as that. ###k]
    [also has decode methods, and some external code makes one of these just to use those (which is a kluge).]
    """
    # make these helper functions available as if they were methods,
    # to permit clients to avoid import cycles
    # which would occur if they imported them directly from this file
    decode_atom_coordinate = staticmethod( decode_atom_coordinate)
    decode_atom_coordinates = staticmethod( decode_atom_coordinates)
    
    def __init__(self, ndix, markers):
        self.ndix = ndix # maps atom numbers to atoms (??)
        self.markers = markers
    def atom(self, atnum):
        """
        map atnum string to atom, while reading mmp file
        (raises KeyError if that atom-number isn't recognized,
         which is an mmp file format error)
        """
        return self.ndix[int(atnum)]
    def move_forwarded_node( self, node, val):
        """
        find marker based on val, put node after it, and then del the marker
        """
        try:
            marker = self.markers.pop(val) # val is a string; should be ok since we also read it as string from forward_ref record
        except KeyError:
            assert 0, "mmp format error: no forward_ref was written for this forwarded node" ###@@@ improve errmsg
        marker.addsibling(node)
        marker.kill()
    def decode_int(self, val): #bruce 050701; should be used more widely
        """
        helper method for parsing info records; returns an int or None;
        warns of unrecognized values only if ATOM_DEBUG is set
        """
        try:
            assert val.isdigit() or (val[0] == '-' and val[1:].isdigit())
            return int(val)
        except:
            # several kinds of exception are possible here, which are not errors
            if debug_flags.atom_debug:
                print "atom_debug: fyi: some info record wants an int val but got this non-int (not an error): " + repr(val)
                # btw, the reason it's not an error is that the mmp file format might be extended to permit it, in that info record.
            return None
        pass
    def decode_bool(self, val): #bruce 050701; should be used more widely
        """
        helper method for parsing info records; returns True or False or None;
        warns of unrecognized values only if ATOM_DEBUG is set
        """
        val = val.lower()
        if val in ['0','no','false']:
            return False
        if val in ['1','yes','true']:
            return True
        if debug_flags.atom_debug:
            print "atom_debug: fyi: some info record wants a boolean val but got this instead (not an error): " + repr(val)
        return None
    pass # end of class mmp_interp

def mmp_interp_just_for_decode_methods(): #bruce 050704
    """
    Return an mmp_interp object usable only for its decode methods (kluge)
    """
    return mmp_interp("not used", "not used")

def readmmp_info( card, currents, interp ): #bruce 050217; revised 050421, 050511
    """
    Handle an info record 'card' being read from an mmp file;
    currents should be a dict from thingtypes to the current things of those types,
    for all thingtypes which info records can give info about
    (including 'chunk', 'opengroup', 'leaf', 'atom');
    interp should be an mmp_interp object #doc.

    The side effect of this function, when given "info <type> <name> = <val>",
    is to tell the current thing of type <type> (that is, the last one read from this file)
    that its optional info <name> has value <val>,
    using a standard info-accepting method on that thing.
    <type> should be a "word";
    <name> should be one or more "words"
    (it's supplied as a python list of strings to the info-accepting method);
    <val> can be (for now) any string with no newlines,
    and no whitespace at the ends; its permissible syntax might be further restricted later.
    """
    #e interface will need expanding when info can be given about non-current things too
    what, val = card.split('=', 1)
    key = "info"
    what = what[len(key):]
    what = what.strip() # e.g. "chunk xxx" for info of type xxx about the current chunk
    val = val.strip()
    what = what.split() # e.g. ["chunk", "xxx"], always 2 or more words
    type = what[0] # as of 050511 this can be 'chunk' or 'opengroup' or 'leaf' or 'atom'
    name = what[1:] # list of words (typically contains exactly one word, an attribute-name)
    thing = currents.get(type)
    if thing: # can be false if type not recognized, or if current one was None
        # record info about the current thing of type <type>
        try:
            meth = getattr(thing, "readmmp_info_%s_setitem" % type) # should be safe regardless of the value of 'type'
        except AttributeError:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: object %r doesn't accept \"info %s\" keys (like %r); ignoring it (not an error)" \
                      % (thing, type, name)
        else:
            try:
                meth( name, val, interp )
            except:
                print_compact_traceback("internal error in %r interpreting %r, ignored: " % (thing, card) )
    elif debug_flags.atom_debug:
        print "atom_debug: fyi: no object found for \"info %s\"; ignoring info record (not an error)" % (type,)
    return

# ==

_readmmp_aborted = False

_reference_to_readmmp_abort_function = None #bruce 080606 precaution

def _readmmp(assy, filename, isInsert = False, showProgressDialog = False): 
    """
    Read an mmp file, print errors and warnings to history,
    modify assy in various ways (a bad design, see comment in insertmmp)
    (but don't actually add file contents to assy -- let caller do that if and
    where it prefers), and return (as part of a larger tuple described below)
    either None (after an error for which caller should store no file contents
    at all) or a list of 3 Groups, which caller should treat as having roles
    "viewdata", "tree", "shelf", regardless of how many toplevel items were
    in the file, or of whether they were groups.
    (We handle normal mmp files with exactly those 3 groups, old sim-input
    files with only the first two, and newer sim-input files for Parts 
    (one group) or for minimize selection (maybe no groups at all). And most 
    other weird kinds of mmp files someone might create.)

    @warning: the optional arguments are sometimes passed positionally.
    
    @param assy: the assembly the file contents are being added into
    @type  assy: assembly.assembly
    
    @param filename: where the data will be read from
    @type  filename: string
    
    @param isInsert: if True, the file contents are being added to an
                     existing assembly, otherwise the file contents are being
                     used to initialize a new assembly.
    @type  isInsert: boolean
    
    @param showProgressDialog: if True, display a progress dialog while reading
                               a file. Default is False.
    @type  showProgressDialog: boolean

    @return: the tuple (ok, grouplist or None, listOfAtomsInFileOrder), where
             ok is one of the string constants named (in utilities.constants)
             SUCCESS, ABORTED, or READ_ERROR. (If ok is not SUCCESS, grouplist
             will be None and listOfAtomsInFileOrder will be [], but callers
             will be cleaner if they don't rely on this.)
    @rtype: (string, list, list)
    """
    #bruce 050405 revised code & docstring
    #ericm 080409 revised return value to contain listOfAtomsInFileOrder
    #bruce 080502 documented return value; fixed it when file is empty
    
    state = _readmmp_state( assy, isInsert)
    
    # The following code is experimental. It reads an mmp file that is contained
    # within a ZIP file. To test, create a zipfile (i.e. "part.zip") which
    # contains an MMP file named "main.mmp", then rename "part.zip" to 
    # "part.mmp". Set the constant READ_MAINMMP_FROM_ZIPFILE = True,
    # then run NE1 and open "part.mmp" using "File > Open...". 
    # Mark 2008-02-03
    READ_MAINMMP_FROM_ZIPFILE = False # Don't commit with True.
    
    if READ_MAINMMP_FROM_ZIPFILE:
        # Experimental. Read "main.mmp", a standard mmp file contained within 
        # a zipfile opened via "File > Open...".
        from zipfile import ZipFile
        _zipfile = ZipFile(filename, 'r')
        _bytes = _zipfile.read("main.mmp")
        lines = _bytes.splitlines()
    else:
        # The normal way to read an MMP file.
        try:
            lines = open(filename,"rU").readlines()
            # 'U' in filemode is for universal newline support
        except:
            return READ_ERROR, None, []
    
    # Commented this out since the assy.filename should be (and is) set by 
    # another caller based on success.
    #if not isInsert:
    #    assy.filename = filename ###e would it be better to do this at the end, and not at all if we fail?

    global _readmmp_aborted
    global _reference_to_readmmp_abort_function

    _readmmp_aborted = False #bruce 080606 bugfix or precaution
    
    # Create and display a Progress dialog while reading the MMP file. 
    # One issue with this implem is that QProgressDialog always displays 
    # a "Cancel" button, which is not hooked up. I think this is OK for now,
    # but later we should either hook it up or create our own progress
    # dialog that doesn't include a "Cancel" button. --mark 2007-12-06
    if showProgressDialog:
        kluge_main_assy = env.mainwindow().assy
            # see comment about kluge_main_assy elsewhere in this file
            # [bruce 080319]
        assert not kluge_main_assy.assy_valid #bruce 080117
        _progressValue = 0
        _progressFinishValue = len(lines)
        win = env.mainwindow()
        win.progressDialog.setLabelText("Reading file...")
        win.progressDialog.setRange(0, _progressFinishValue)
        _progressDialogDisplayed = False
        _timerStart = time.time()
        
        def abort_readmmp():
            """
            This slot is called when the user aborts opening a large
            MMP file by pressing the "Cancel" button in the progress dialog.
            """
            try:
                print "cancelled reading file"
                global _readmmp_aborted
                _readmmp_aborted = True
                win.disconnect(win.progressDialog, SIGNAL("canceled()"), abort_readmmp)
                    # review: why no NameError for this abort_readmmp?
                    # guess: it's a legal read-only reference into the
                    # outer function's scope. But it's also possible that we have
                    # an exception and don't see it, so I'm adding some prints to
                    # find out, and try/except. These can remain since they are
                    # harmless. [bruce 080606]
                print " (returning from abort_readmmp)"
            except:
                print_compact_traceback("exception in abort_readmmp ignored: ")
            return
        
        from PyQt4.Qt import SIGNAL
        win.connect(win.progressDialog, SIGNAL("canceled()"), abort_readmmp)

        _reference_to_readmmp_abort_function = abort_readmmp
            # make sure abort_readmmp doesn't get deallocated before use
            # [bruce 080606 precaution]

        pass
    
    for card in lines:
        if _readmmp_aborted: # User aborted while reading the MMP file.
            _readmmp_aborted = False # (precaution, not really needed, since not
                # sufficient to replace the reset earlier in this function)
            return ABORTED, None, []
        try:
            errmsg = state.readmmp_line( card) # None or an error message
        except:
            # note: the following two error messages are similar but not identical
            errmsg = "bug while reading this mmp line: %s" % (card,) #e include line number; note, two lines might be identical
            print_compact_traceback("bug while reading this mmp line:\n  %s\n" % (card,) )
        #e assert errmsg is None or a string
        if errmsg:
            ###e general history msg for stopping early on error
            ###e special return value then??
            break
        
        if showProgressDialog: # Update the progress dialog.
            _progressValue += 1
            if _progressValue >= _progressFinishValue:
                win.progressDialog.setLabelText("Building model...")
            elif _progressDialogDisplayed:
                win.progressDialog.setValue(_progressValue)
                    # WARNING: this can directly call glpane.paintGL!
                    # So can the other 2 calls here of progressDialog.setValue.
                    # To prevent bugs or slowdowns from drawing incomplete
                    # models or from trying to run updaters (or take undo
                    # checkpoints?) before drawing them, the GLPane now checks
                    # kluge_main_assy.assy_valid to prevent redrawing when this happens.
                    # (Does ThumbView also need this fix?? ### REVIEW)
                    # [bruce 080117 comment / bugfix]                    
            else:
                _timerDuration = time.time() - _timerStart
                if _timerDuration > 0.25: 
                    # Display progress dialog after 0.25 seconds
                    win.progressDialog.setValue(_progressValue)
                    _progressDialogDisplayed = True
        
    grouplist = state.extract_toplevel_items() # for a normal mmp file this has 3 Groups, whose roles are viewdata, tree, shelf

    # now fix up sim input files and other nonstandardly-structured files;
    # use these extra groups if necessary, else discard them:
    viewdata = Group("Fake View Data", assy, None) # name is never used or stored
    shelf = Group("Clipboard", assy, None) # name might not matter since caller resets it
    
    for g in grouplist:
        if not g.is_group(): # might happen for files that ought to be 'one_part', too, I think, if clipboard item was not grouped
            state.guess_sim_input('missing_group_or_chunk') # normally same warning already went out for the missing chunk 
            tree = Group("tree", assy, None, grouplist)
            grouplist = [ viewdata, tree, shelf ]
            break
    if len(grouplist) == 0:
        state.format_error("nothing in file")
        return SUCCESS, None, []
            ### REVIEW: this is really a file format error;
            # what return code is best? need a new one?
            # guess: READ_ERROR would be best; needs analysis.
            # [bruce 080606 Q]
    elif len(grouplist) == 1:
        state.guess_sim_input('one_part')
            # note: 'one_part' gives same warning as 'missing_group_or_chunk' as of 050406
        tree = Group("tree", assy, None, grouplist) #bruce 050406 removed [0] to fix bug in last night's new code
        grouplist = [ viewdata, tree, shelf ]
    elif len(grouplist) == 2:
        state.guess_sim_input('no_shelf')
        grouplist.append( shelf)
    elif len(grouplist) > 3:
        state.format_error("more than 3 toplevel groups -- treating them all as in the main part")
            #bruce 050405 change; old code discarded all the data
        tree = Group("tree", assy, None, grouplist)
        grouplist = [ viewdata, tree, shelf ]
    else:
        pass # nothing was wrong!
    assert len(grouplist) == 3

    listOfAtomsInFileOrder = state.listOfAtomsInFileOrder
    
    state.destroy() # not before now, since it keeps track of which warnings we already emitted
    
    if showProgressDialog: # Make the progress dialog go away.
        win.progressDialog.setValue(_progressFinishValue)

    _reference_to_readmmp_abort_function = None
    
    return SUCCESS, grouplist, listOfAtomsInFileOrder # from _readmmp

def readmmp(assy,
            filename,
            isInsert = False,
            showProgressDialog = False,
            returnListOfAtoms = False):
    """
    Read an mmp file to create a new model (including a new
    Clipboard).  Returns a tuple described below, which
    contains a grouplist tuple of (viewdata, tree, shelf). If
    isInsert is False (the default), assy will be modified to include
    the new items. (If caller wants assy to be marked as "not modified"
    afterwards, it's up to caller to handle this, e.g. using
    assy.reset_changed().)

    @note: mmp stands for Molecular Machine Part.

    @param assy: the assembly object which the file contents are being added to
    @type  assy: instance of assembly.Assembly
    
    @param filename: where the data will be read from
    @type  filename: string
    
    @param isInsert: if True, the file contents are being added to an
                     existing assembly, otherwise the file contents are being
                     used to initialize a new assembly. When this is true,
                     some behavior is not done, e.g. calling assy.update_parts
                     and all the updaters it normally calls. Doing that
                     (or tolerating not doing it) is up to the caller.
    @type  isInsert: boolean
    
    @param showProgressDialog: if True, display a progress dialog while reading
                               a file. Default is False.
    @type  showProgressDialog: boolean

    @param returnListOfAtoms: if True, return value contains a list of all
                              atoms in the file, in the order they
                              appeared.  If False (the default),
                              return value contains the group list.
                              See return value doc for details.
    @type  returnListOfAtoms: boolean
    
    @return: the tuple (ok, grouplist) or (ok, listOfAtoms)
             (depending on the returnListOfAtoms option)
             where ok is one of the following named string constants
             defined in utilities.constants:
             - SUCCESS
             - ABORTED
             - READ_ERROR
    @rtype:  (string, atom list) or (string, grouplist or None)
    """
    # todo: This interface needs revising and clarifying. Ideally, it should take only
    # a filename as parameter, and return a single data structure (of the same
    # class which we use for "the contents of a model file", more or less)
    # representing the contents of that file, and a success code.
    # (Whether it's practical for the data not to point to "its assy" is
    #  questionable, but can be thought of as an independent issue,
    #  except perhaps for performance considerations for Insert.)
    # Maybe the listOfAtoms should be accessible from the data structure
    # even if it's not identical to "all the atoms ultimately in that
    # structure"; if that's not wise, then returning it separately is ok.
    # [comment probably by EricM; revised/extended by bruce 080606]

    # TODO: clean up return value format to return a tuple of three values,
    # always in the same format (ok, grouplist, listOfAtoms)
    # (just like _readmmp does now). [bruce 080606 suggestion]

    kluge_main_assy = env.mainwindow().assy
        # use this instead of assy to fix logic bug in use of assy_valid flag
        # (explained where it's used in master_model_updater)
        # which would be a potential bug during partlib mmpread
        # [bruce 080319]
    assert kluge_main_assy.assy_valid
    kluge_main_assy.assy_valid = False # disable updaters during _readmmp
        # [bruce 080117/080124, revised 080319]
    try:
        ok, grouplist, listOfAtomsInFileOrder = _readmmp(assy,
                                                         filename,
                                                         isInsert,
                                                         showProgressDialog)
            # warning: can show a dialog, which can cause paintGL calls.
    finally:
        kluge_main_assy.assy_valid = True
    if (not isInsert):
        # NOTE: we want to call this even if ok != SUCCESS,
        # since it detects grouplist is None in that case
        # and has side effects on assy which might be required
        # (needs review to see if they are really required).
        # [bruce 080606 comment]
        _reset_grouplist(assy, grouplist)
            # note: handles grouplist is None (though not very well)
            # note: runs all updaters when done, and sets per-part viewdata
    if (returnListOfAtoms):
        return ok, listOfAtomsInFileOrder
    return ok, grouplist
    
def _reset_grouplist(assy, grouplist):
    """
    [private]

    Stick a new just-read grouplist into assy, within readmmp.

    If grouplist is None, indicating file had bad format,
    do some but not all of the usual side effects.
    [appropriateness of behavior for grouplist is None is unreviewed]

    Otherwise grouplist must be a list of exactly 3 Groups
    (though this is not fully checked here),
    which we treat as viewdata, tree, shelf.

    Changed viewdata behavior 050418:
    We used to assume (if necessary) that viewdata contains Csys records
    which, when parsed during _readmmp, had side effects of storing themselves in assy
    (which was a bad design).
    Now we scan it and perform those side effects ourselves.
    """
    #bruce 050302 split this out of readmmp;
    # it should be entirely rewritten and become an assy method
    #bruce 050418: revising this for assy/part split
    if grouplist is None:
        # do most of what old code did (most of which probably shouldn't be done,
        # but this needs more careful review (especially in case old code has
        # already messed things up by clearing assy), and merging with callers,
        # which don't even check for any kind of error return from readmmp),
        # except (as of 050418) don't do any side effects from viewdata.
        # Note: this is intentionally duplicated with code from the other case,
        # since the plan is to clean up each case independently.
        assy.shelf.name = "Clipboard"
        assy.shelf.open = False
        assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
        assy.kluge_patch_toplevel_groups()
        assy.update_parts()
        return
    viewdata, tree, shelf = grouplist
        # don't yet store these in any Part, since those will all be replaced
        # with new ones by update_parts, below!
    assy.tree = tree
    assy.shelf = shelf
        # below, we'll scan viewdata for Csys records to store into mainpart
    assy.shelf.name = "Clipboard"
    if not assy.shelf.open_specified_by_mmp_file: #bruce 050421 added condition
        assy.shelf.open = False
    assy.root = Group("ROOT", assy, None, [assy.tree, assy.shelf])
    assy.kluge_patch_toplevel_groups()
    
    assy.update_parts( do_special_updates_after_readmmp = True)
        #bruce 080319 added do_special_updates_after_readmmp = True
        # (note: we don't test will_special_updates_after_readmmp_do_anything()
        #  since we have to call this even if they won't.)
        #
        # Note: by the time this is called, our callers as of 080319
        # will have restored kluge_main_assy.assy_valid = True,
        # so updaters run by update_parts (such as dna updater)
        # will *not* be disabled. [bruce 080319 comment]
        #
        #bruce 050309 for assy/part split;
        # 080117 added do_post_event_updates = False;
        # 080124 removed that option (and revised when caller restores
        # kluge_main_assy.assy_valid) to fix recent bug in which all newly read
        # files are recorded as modified; at the time I thought that option was
        # needed for safety, like the disabling of updaters during paintGL is,
        # but a closer analysis of the following code shows that it's not.
        # NOTE: ideally the dna updater would mark the assy as modified even
        # during readmmp, if it had to do "irreversible changes" to fix a pre-
        # updater mmp file containing dna-related objects. To implement that
        # without restoring the just-fixed bug would require the dna updater
        # to know and record the difference in status of the different kinds
        # of updates it does; it would also require some new scheme in this
        # code for having that affect the ultimate value of assy._modified
        # (presently determined by code in our callers). Neither is trivial,
        # both are doable -- not yet clear if it's worth the trouble.
        # [bruce comment 080124]
    
    # Now the parts exist, so it's safe to store the viewdata into the mainpart;
    # this imitates what the pre-050418 code did when the csys records were parsed;
    # note that not all mmp files have anything at all in viewdata
    # (e.g. some sim-input files don't).
    mainpart = assy.tree.part
    for m in viewdata.members:
        if isinstance(m, NamedView):
            if m.name == "HomeView" or m.name == "OldVersion":
                    # "OldVersion" will be changed to "HomeView" later... see comment elsewhere
                mainpart.homeView = m
            elif m.name == "LastView":
                mainpart.lastView = m
            elif m.name.startswith("HomeView"):
                _maybe_set_partview(assy, m, "HomeView", 'homeView')
            elif m.name.startswith("LastView"):
                _maybe_set_partview(assy, m, "LastView", 'lastView')
    return

def _maybe_set_partview( assy, namedView, nameprefix, namedViewattr): #bruce 050421; docstring added 050602
    """
    [private helper function for _reset_grouplist]

    If namedView.name == nameprefix plus a decimal number, store namedView as the attr named namedViewattr
    of the .part of the clipboard item indexed by that number
    (starting from 1, using purely positional indices for clipboard items).
    """
    partnodes = assy.shelf.members
    for i in range(len(partnodes)): #e inefficient if there are a huge number of shelf items...
        if namedView.name == nameprefix + "%d" % (i+1):
            part = partnodes[i].part
            setattr(part, namedViewattr, namedView)
            break
    return

def insertmmp(assy, filename):
    """
    Read an mmp file and insert its main part into the existing model.
    Discards other info from the file it reads, like the clipboard.

    @note: does not emit a history message about its result.
           The caller must do that if desired.

    @return: success_code, which is one of these named string constants
             defined in utilities.constants:
             - SUCCESS
             - ABORTED
             - READ_ERROR
    """
    #bruce 050405 revised to fix one or more assembly/part bugs, I hope
    #bruce 080606 revised to return success code (but didn't yet fix
    # callers to make use of it)
    
    # Note: this is a normal user operation, so there is no need
    # to refrain from setting assy's modified flag.
    kluge_main_assy = env.mainwindow().assy
        # use this instead of assy to fix logic bug in use of assy_valid flag
        # (explained where it's used in master_model_updater)
        # which would be a potential bug during partlib mmpread
        # [bruce 080319]
    assert kluge_main_assy.assy_valid
    kluge_main_assy.assy_valid = False # disable updaters during insert [bruce 080117]
    ok = READ_ERROR
    try:
        ok, grouplist, listOfAtomsInFileOrder = _readmmp(assy, 
                                                         filename, 
                                                         isInsert = True,
                                                         showProgressDialog = True)
        del listOfAtomsInFileOrder        
        
            # isInsert = True prevents most side effects on assy;
            # a better design would be to let the caller do them (or not)
        if ok == SUCCESS and grouplist:
            #bruce 080606 added ok == SUCCESS condition (precaution or cleanup)
            ### TODO: NEEDS ERROR MESSAGE OTHERWISE
            viewdata, mainpart, shelf = grouplist
            del viewdata
            ## not yet (see below): del shelf
            assy.addnode( mainpart) #bruce 060604
    ##        assy.part.ensure_toplevel_group()
    ##        assy.part.topnode.addchild( mainpart )
            #bruce 050425 to fix bug 563:
            # Inserted mainpart might contain jigs whose atoms were in clipboard of inserted file.
            #   Internally, right now, those atoms exist, in legitimate chunks in assy
            # (with a chain of dads going up to 'shelf' (the localvar above), which has no dad),
            # and have not been killed. Bug 563 concerns these jigs being inserted with no provision
            # for their noninserted atoms. It's not obvious what's best to do in this case, but a safe
            # simple solution seems to be to pretend to insert and then delete the shelf we just read,
            # thus officially killing those atoms, and removing them from those jigs, with whatever
            # effects that might have (e.g. removing those jigs if all their atoms go away).
            #   (When we add history messages for jigs which die from losing all atoms,
            # those should probably differ in this case and in the usual case,
            # but those are NIM for now.)
            #   I presume it's ok to kill these atoms without first inserting them into any Part...
            # at least, it seems unlikely to mess up any specific Part, since they're not now in one.
            #e in future -- set up special history-message behavior for jigs killed by this:
            
            shelf.kill()
        

            #e in future -- end of that special history-message behavior

            # run special updaters for readmmp, but (as optim for usual case)
            # only if necessary, since otherwise the normal updater run after
            # we return (which happens since this is a normal user op)
            # will be sufficient. For big files this might be a significant
            # optim (in spite of incremental nature of updater) (guess).
            #
            # note: for readmmp this is done in _reset_grouplist, in a call
            # of update_parts which is always required.
            # [bruce 080319]
            if will_special_updates_after_readmmp_do_anything(assy):
                assy.update_parts( do_special_updates_after_readmmp = True)
            pass
        pass
    finally:
        kluge_main_assy.assy_valid = True
    return ok

def fix_assy_and_glpane_views_after_readmmp( assy, glpane):
    """
    #doc; does gl_update but callers should not rely on that
    """
    #bruce 050418 moved this code (written by Huaicai) out of MWsemantics.fileOpen
    # (my guess is it should mostly be done by readmmp itself);
    # here is Huaicai's comment about it:
    # Huaicai 12/14/04, set the initial orientation to the file's home view orientation 
    # when open a file; set the home view scale = current fit-in-view scale
    #bruce 050418 change this for assembly/part split (per-part Csys attributes)
    mainpart = assy.tree.part
    assert assy.part is mainpart # necessary for glpane view funcs to refer to it (or was at one time)
    if mainpart.homeView.name == "OldVersion": ## old version of mmp file
        mainpart.homeView.name = "HomeView"
        glpane.set_part(mainpart) # also sets view, but maybe not fully correctly in this case ###k
        glpane.quat = Q( mainpart.homeView.quat) # might be redundant with above
        glpane.setViewFitToWindow()
    else:    
        glpane.set_part(mainpart)
        ## done by that: glpane._setInitialViewFromPart( mainpart)
    return

# end
