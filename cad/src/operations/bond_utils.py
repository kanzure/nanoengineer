# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
bond_utils.py -- helper functions for bond-related UI code and its operations

(should be renamed, maybe to bond_menu_helpers.py)

@author: bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

created by bruce 050705 to help with higher-order bonds for Alpha6.
"""

from geometry.VQT import Q
from utilities.constants import noop
import foundation.env as env
from utilities.Log import greenmsg, redmsg, orangemsg, quote_html
from utilities.debug import print_compact_stack

from model.bond_constants import bonded_atoms_summary
from model.bond_constants import btype_from_v6
from model.bond_constants import v6_from_btype
from model.bond_constants import bond_left_atom

def intersect_sequences(s1, s2):
    """
    Return the intersection of two sequences. If they are sorted
    in a compatible way, so will be the result.
    """
    return filter( lambda s: s in s2, s1)

def complement_sequences(big, little):
    return filter( lambda s: s not in little, big)

def possible_bond_types(bond):
    """
    Return a list of names of possible bond types for the given bond,
    in order of increasing bond order,
    based on its atoms' current elements and atomtypes.
       This list is never empty since single bonds are always deemed possible
    (even if they always induce valence errors, e.g. for H bonded to O(sp2) or in O2).
       For warnings about some choices of bond type (e.g. S=S), see the function bond_type_warning.
       [If you want to permit bonds requiring other atomtypes, when those are reachable
    by altering only open bonds on this bond's actual atoms, see possible_bond_types_for_elements
    (related to that goal, but might not do exactly that).]
       Warning: this ignores geometric issues, so it permits double bonds even if they
    would be excessively twisted, and it ignores bond length, bond arrangement in space
    around each atom, etc.
    """
    s1 = bond.atom1.atomtype.permitted_v6_list # in order of v6
    s2 = bond.atom2.atomtype.permitted_v6_list
    s12 = intersect_sequences( s1, s2 ) # order comes from s1; we depend on its coming from one of them or the other
        #e could be faster (since these lists are prefixes of a standard order), but doesn't need to be
    return map( btype_from_v6, s12)

def possible_bond_types_for_elements(bond):
    "#doc, incl details of what's permitted"
    permitted1 = bond.atom1.permitted_btypes_for_bond(bond) # dict from v6 to atomtypes which permit it
    permitted2 = bond.atom2.permitted_btypes_for_bond(bond)
    poss_v6 = intersect_sequences(permitted1.keys(), permitted2.keys()) # arbitrary order
    poss_v6.sort() # smallest bond order first
    poss2 = map( btype_from_v6, poss_v6)
    return poss2, permitted1, permitted2

#partly-obs comment:
#e should we put element rules into the above possible_bond_types, or do them separately?
# and should bonds they disallow be shown disabled, or not even included in the list?
# and should "unknown" be explicitly in the list?

def bond_type_warning(bond, btype): # 050707
    """
    Return a warning (short text suitable to be added to menu item text), or "" for no warning,
    about the use of btype (bond type name) for bond.
    This can be based on its atomtypes or perhaps on more info about the surroundings
    (#e we might need to add arguments to pass such info).
       Presently, this only warns about S=S being unstable, and about bonds whose type could not
    permit both atoms (using their current atomtypes) to have the right valence
    regardless of their other bonds (which only happens now when they have no other bonds).
       This might return warnings for illegal btypes, even though it's not presently called
    for illegal btypes for the given bond. It doesn't need to return any warning for illegal btypes.
    """
    atype1 = bond.atom1.atomtype
    atype2 = bond.atom2.atomtype
    if btype == 'double' and atype1.is_S_sp2 and atype2.is_S_sp2:
        return "unstable"
    elif btype == 'single' and (atype1.bond1_is_bad or atype2.bond1_is_bad):
        return "bad valence"
    elif btype != 'triple' and (atype1.is_N_sp or atype2.is_N_sp):
        return "bad valence"
    # if there are any other numbonds=1 atoms which show up here, they should be valence-checked too (generalizing the above)
    # (which might be easiest if atomtype stores a "valence-permitted btypes" when numbonds is 1), but I don't think there are others
    return ""

_BOND_DIR_TEXTS = {0:"unset", 1:" --->", -1:"<--- "} # see also _BOND_DIR_NAMES #e refile

def bond_menu_section(bond, quat = Q(1,0,0,0)):
    """
    Return a menu_spec subsection for displaying info about a highlighted bond,
    changing its bond_type, offering commands about it, etc.
    If given, use the quat describing the rotation used for displaying it
    to order the atoms in the bond left-to-right (e.g. in text strings).
    """
    res = []
    res.append(( bonded_atoms_summary(bond, quat = quat), noop, 'disabled' ))
    res.extend( _bond_type_menu_section(bond) )
    if bond.is_directional():
        ### REVIEW: Do we want to do this for open bonds, after mark's 071014 change
        # which allows them here? Or do we want "and not bond.is_open_bond()"?
        # (BTW, I'm not sure this gets called at all, for open bonds.)
        # Guess: open bonds would be safe here, so allow them, though I'm
        # not sure it's always a good idea. Caveat: if we treat them as non-directional
        # when the base atom has three or more directional bonds, we should probably
        # make that exception here too -- probably using a higher-level method in place
        # of is_directional, namely directional_bond_chain_status for both atoms in bond.
        # We'd want a new method on bond to call that for both atoms and look at the
        # results (perhaps there's already code like that elsewhere). Without this,
        # we may get a bug if a user can try to change direction on an open bond
        # that hits a strand but is not in it. But since I suspect the UI never allows
        # an open bond here, I won't bother to write that code just yet. [bruce 071016]
        submenu_contents = bond_direction_submenu_contents(bond, quat)
        left_atom = bond_left_atom(bond, quat) # same one that comes first in bonded_atoms_summary
            #e ideally, for mostly vertical bonds, we'd switch to an up/down distinction for the menu text about directions
            #e and whatever the direction names, maybe we should explore farther along the strand to see what they are...
            # unless it hairpins or crosses over... hmm.
        current_dir = bond.bond_direction_from(left_atom)
        current_dir_str = _BOND_DIR_TEXTS[current_dir]
        text = "strand direction (%s)" % current_dir_str
        item = (text, submenu_contents)
        res.append(item)
    return res
    
def _bond_type_menu_section(bond): #bruce 050716; replaces bond_type_submenu_spec for Alpha6
    """
    Return a menu_spec for changing the bond_type of this bond
    (as one or more checkmark items, one per permitted bond-type given the atomtypes),
    or if the bond-type is unchangeable, a disabled menu item for displaying the type
    (which looks the same as when the bond type is changeable, except for being disabled).
    (If the current bond type is not permitted, it's still present and checked, but disabled,
     and it might have a warning saying it's illegal.)
    """
    # this assert is true, but it would cause an import loop:
    ## assert isinstance(bond, Bond)
    btype_now = btype_from_v6(bond.v6)
    poss1 = possible_bond_types(bond) # a list of strings which are bond-type names, in order of increasing bond order
    poss, permitted1, permitted2 = possible_bond_types_for_elements(bond) # new feature 060703
    ##e could put weird ones (graphitic, carbomeric) last and/or in parens, in subtext below
    types = list(poss)
    for btype in poss1:
        if btype not in types:
            print "should never happen: %r not in %r" % (btype, poss) # intentional: "not in types" above, "not in poss" here
            types.append(btype)
    if btype_now not in types:
        types.append(btype_now) # put this one last, since it's illegal; warning for it is computed later
    assert len(types) > 0
    # types is the list of bond types for which to make menu items, in order;
    # now make them, and figure out which ones are checked and/or disabled;
    # we disable even legal ones iff there is only one bond type in types
    # (which means, if current type is illegal, it is disabled and the sole legal type is enabled).
    disable_legal_types = (len(types) == 1)
    res = []
    for btype in types: # include current value even if it's illegal
        subtext = "%s bond" % btype # this string might be extended below
        checked = (btype == btype_now)
        command = ( lambda arg1=None, arg2=None, btype=btype, bond=bond: apply_btype_to_bond(btype, bond) )
        warning = warning2 = ""
        if btype not in poss:
            # illegal btype (note: it will be the current one, and thus be the only checked one)
            warning = "illegal"
            disabled = True
        else:
            # legal btype
            warning = bond_type_warning(bond, btype) # might be "" (or None??) for no warning
            if btype not in poss1:
                # new feature 060703
                # try1: too long and boring (when in most menu entries):
                ## warning2 = "would change atomtypes"
                # try2: say which atomtypes we'd change to, in same order of atoms as the bond name
                v6 = v6_from_btype(btype)
                atype1 = best_atype(bond.atom1, permitted1[v6])
                atype2 = best_atype(bond.atom2, permitted2[v6])
                in_order = [atype1, atype2] ##e stub; see code in Bond.__str__
                warning2 = "%s<->%s" % tuple([atype.name for atype in in_order])
            disabled = disable_legal_types
                # might change this if some neighbor bonds are locked (nim), or if we want to show non-possible choices
        if warning2:
            subtext += " (%s)" % warning2
        if warning:
            subtext += " (%s)" % warning
        res.append(( subtext, command,
                         disabled and 'disabled' or None,
                         checked and 'checked' or None ))
    ##e if >1 legal value, maybe we should add a toggleable checkmark item to permit "locking" the bond to its current bond type;
    # this won't be needed until we have better bond inference (except maybe for bondpoints),
    # since right now [still true 060703] we never alter real bond types except when the user does an action on that specific bond.
    if not bond.is_open_bond():
        ## command = ( lambda arg1 = None, arg2 = None, bond = bond: bond.bust() )
        command = ( lambda bond = bond: delete_bond(bond) )
        res.append(None) # separator
        res.append(("Delete Bond", command))
    return res

def delete_bond(bond): #bruce 080228 to fix update bug reported by EricM
    # see also: SelectAtoms_GraphicsMode.bondDelete
    # (should we print to history like it does?)
    assy = bond.atom1.molecule.assy
    if assy.glpane.selobj is bond:
        assy.glpane.selobj = None
    bond.bust()
    assy.changed()
    assy.glpane.gl_update()
    return

##def bond_type_submenu_spec(bond): #bruce 050705 (#e add options??); probably not used in Alpha6
##    """Return a menu_spec for changing the bond_type of this bond,
##    or if that is unchangeable, a disabled menu item for displaying the type.
##    """
##    v6 = bond.v6
##    btype0 = btype_from_v6(v6)
##    poss = possible_bond_types(bond) # a list of strings which are bond-type names
##    ##e could put weird ones (graphitic, carbomeric) last and/or in parens, in subtext below
##    maintext = 'Bond Type: %s' % btype0
##    if btype0 not in poss or len(poss) > 1:
##        # use the menu
##        submenu = []
##        for btype in poss: # don't include current value if it's illegal
##            subtext = btype
##            warning = bond_type_warning(bond, btype)
##            if warning:
##                subtext += " (%s)" % warning
##            command = ( lambda arg1=None, arg2=None, btype=btype, bond=bond: apply_btype_to_bond(btype, bond) )
##            checked = (btype == btype0)
##            disabled = False # might change this if some neighbor bonds are locked, or if we want to show non-possible choices
##            submenu.append(( subtext, command,
##                             disabled and 'disabled' or None,
##                             checked and 'checked' or None ))
##        ##e if >1 legal value could add checkmark item to permit "locking" this bond type
##        return ( maintext, submenu)
##    else:
##        # only one value is possible, and it's the current value -- just show it
##        return ( maintext, noop, 'disabled' )
##    pass


#bruce 060523 unfinished aspects of new more permissive bondtype changing: ####@@@@
# - verify it can't be applied to open bonds from dashboard tools (since not safe yet)
# - make sure changing atomtypes doesn't remove bond (if open)
#   (possible implem of that: maybe remove it, set_atomtype, then add it back, then remake singlets?)
# - then it's safe to let bond cmenu have more entries (since they might be open bonds)

def apply_btype_to_bond(btype, 
                        bond, 
                        allow_remake_bondpoints = True,
                        suppress_history_message = False): #bruce 060703 added allow_remake_bondpoints for bug 833-1
    """
    Apply the given bond-type name (e.g. 'single') to the given bond, iff this is permitted by its atomtypes
    (or, new feature 060523, if it's permitted by its real atoms' possible atomtypes and their number of real bonds),
    and do whatever inferences are presently allowed [none are implemented as of 050727].
    Emit an appropriate history message. Do appropriate invals/updates.
    [#e should the inference policy and/or some controlling object be another argument? Maybe even a new first arg 'self'?]
    
    @param suppress_history_message: If True, it quietly converts the bondtypes 
            without printing any history message. 
    """
    # Note: this can be called either from a bond's context menu, or by using a Build mode dashboard tool to click on bonds
    # (or bondpoints as of 060702) and immediately change their types.
    
    #This flag will be returned by this function to tell the caller whether the
    #bond type of the given bond was changed
    bond_type_changed = True
    
    v6 = v6_from_btype(btype)
    oldname = quote_html( str(bond) )
    def changeit(also_atypes = None):
        if v6 == bond.v6:
            bond_type_changed = False
            if not suppress_history_message:
                env.history.message( "bond type of %s is already %s" % (oldname, btype))
        else:
            if also_atypes:
                # change atomtypes first (not sure if doing this first matters)
                atype1, atype2 = also_atypes
                def changeatomtype(atom, atype):
                    if atom.atomtype is not atype:
                        if not suppress_history_message:
                            msg = "changed %r from %s to %s" % (atom, 
                                                                atom.atomtype.name, 
                                                                atype.name )
                            env.history.message(msg)
                        atom.set_atomtype(atype)
                        ### note[ probably 060523]:
                        # if we're an open bond, we have to prevent this process from removing us!
                        # (this is nim, so we're not yet safe to offer on open bonds.
                        #  Thus in fix for 833-1 [060703], atomtype changes are not allowed.)
                        pass
                    return # from changeatomtype
                changeatomtype(bond.atom1, atype1)
                changeatomtype(bond.atom2, atype2)
            bond.set_v6(v6) # this doesn't affect anything else or do any checks ####k #####@@@@@ check that
            ##e now do inferences on other bonds
            bond.changed() ###k needed?? maybe it's now done by set_v6??
            if not suppress_history_message:
                env.history.message( "changed bond type of %s to %s" % (oldname,
                                                                        btype))
            ###k not sure if it does gl_update when needed... how does menu use of this do that?? ###@@@
        return # from changeit
    poss = poss1 = possible_bond_types(bond) # only includes the ones which don't change the atomtypes -- try these first
    if btype in poss1:
        changeit()
        return bond_type_changed
    # otherwise figure out if we can change the atomtypes to make this work.
    # (The following code is predicted to work for either real or open bonds,
    #  but it is not safe to offer on open bonds for other reasons (commented above in changeatomtype).
    #  But we'll still figure out the situation, so the history message can be more useful.)
    if 1:
        # this is needed for allow_remake_bondpoints,
        # or for history advice about what that could have permitted:
        poss2, permitted1, permitted2 = possible_bond_types_for_elements(bond)
            # the only purpose of having the whole sequence poss2
            # (not just one element of it, equal to btype) is the error message
        if btype in poss2:
            atype1 = best_atype(bond.atom1, permitted1[v6])
            atype2 = best_atype(bond.atom2, permitted2[v6])
    if allow_remake_bondpoints:
        poss = poss2 # poss is whichever of poss1 or poss2 was actually allowed
        if btype in poss2:
            changeit((atype1, atype2))
            return bond_type_changed
    # It failed, but a variety of situations should be handled in the error message.
    # For error messages, sort them all the same way.
    poss1.sort()
    poss2.sort()
    poss.sort() #k not really needed, it's same mutable list, but keep this in case someone changes that
    if poss2 == poss : # note, this happens if poss2 == poss1, or if they differ but allow_remake_bondpoints is true
        # permitting changing of atomtypes wouldn't make any difference
        if not suppress_history_message:
            msg = "can't change bond type of %s to %s" % (oldname, btype)
            msg2 = " -- permitted types are %s" % (poss)
                #e improve message -- %s of list looks like repr (for strings too)
            env.history.message( orangemsg( msg) + msg2 )
        bond_type_changed = False
    elif btype in poss2:
        if allow_remake_bondpoints:
            print_compact_stack( "bug: allow_remake_bondpoints should not be true here: " )
        # the only reason we refused is that the UI won't allow remaking of bondpoints;
        # explain what the user would have to do to make it work (using the things computed above as if it had been permitted)
        # (as of 060703 this happens only when you click a bond type changing tool on a bondpoint,
        #  but following code will try to cover this for a real bond as well)
        unless = ""
        for atom, atype in [(bond.atom1, atype1), (bond.atom2, atype2)]: ##e ideally, in same order as printed in bond name
            if atype != atom.atomtype:
                if atom.is_singlet():
                    # should never happen
                    if env.debug:
                        print "debug: bug: %r is bondpoint but user is advised to change its atomtype" % atom
                if not unless:
                    unless = "change atomtype of %s to %s" % (atom, atype.name)
                else:
                    # this is not expected to ever happen, when called from UI as of 060703; it's untested ##@@
                    unless += ", and of %s to %s" % (atom, atype.name)
        msg = "can't change bond type of %s to %s, " % (oldname, btype,)
        bond_type_changed = False
        if unless:
            unless_msg = greenmsg( "unless you %s" % (unless,) )
        else:
            unless_msg = redmsg( "due to a bug")
        if not suppress_history_message:
            env.history.message( orangemsg( msg) + ( unless_msg) )
            
        
    else:
        # changing atomtypes makes a difference, but either way you're not allowed to change to this bond type
        if allow_remake_bondpoints:
            print_compact_stack( "bug: allow_remake_bondpoints should not be true here: " )
        extra = complement_sequences(poss2, poss1)
        if not extra:
            print_compact_stack( "bug: extra should not be empty here: " )
            
        
        msg = "can't change bond type of %s to %s" % (oldname, btype)
        msg2 = " -- permitted types are %s, or %s if you change atomtypes" % (poss1, extra)
            #e improve message -- %s of list looks like repr (for strings too)
        bond_type_changed = False
        if not suppress_history_message:
            env.history.message( orangemsg( msg) + msg2 )
            
    return bond_type_changed # from apply_btype_to_bond

def best_atype(atom, atomtypes = None): #bruce 060523
    """
    Which atomtype for atom is best, among the given or possible ones,
    where best means the fewest number of bondpoints need removing to get to it?
    (Break ties by favoring current one (never matters as presently called, 060523)
    or those earlier in the list.)
    """
    # I don't think we have to consider types for which bondpoints would be *added*...
    # but in case we do, let those be a last resort, but for them, best means fewest added.
    # Note: this is related to Atom.best_atomtype_for_numbonds, but that has a quite different cost function
    # since it assumes it's not allowed to change the number of bondpoints, only to compare severity of valence errors.
    atomtypes = atomtypes or atom.element.atomtypes
    atomhas = len(atom.bonds)
    def cost(atype):
        atypewants = atype.numbonds
        nremove = atomhas - atypewants
        if nremove >= 0:
            cost1 = nremove
        else:
            nadd = - nremove
            cost1 = 100 + nadd
        if atype is atom.atomtype:
            cost2 = -1
        else:
            cost2 = atomtypes.index(atype)
        return (cost1, cost2)
    costitems = [(cost(atype), atype) for atype in atomtypes]
    costitems.sort()
    return costitems[0][1]

_BOND_DIR_NAMES = {0:"unset", 1:"right", -1:"left"} # see also _BOND_DIR_TEXTS #e refile

def bond_direction_submenu_contents(bond, quat): #bruce 070415
    res = []
    left_atom = bond_left_atom(bond, quat)
    direction = bond.bond_direction_from(left_atom)
##    # order will be: if this bond has a dir: this dir, opp dir, unset;
##    # or if not: unset, right, left. So current dir is always first. Not sure this is good! In fact, I'm sure it's not!
##    if direction:
##        dir_order = [direction, - direction, 0]
##    else:
##        dir_order = [0, 1, -1]
    dir_order = [1, -1, 0]
    for dir in dir_order:
        text = "make it %s" % _BOND_DIR_NAMES[dir]
            # how do we say concisely:
            # "make the bond dirs all one way along entire strand,
            #  so they're going (eg) right, when they pass thru this bond"?
        if dir == direction:
            text += " (like this bond)" #e also use checkmark, or is that confusing since it's not a noop? for now, use it.
        command = (lambda _guard = None, bond = bond, left_atom = left_atom, dir = dir:
                   bond.set_bond_direction_from(left_atom, dir, propogate = True))
        checkmark = (dir == direction) and 'checked' or None
        item = (text, command, checkmark)
        res.append(item)
    res.append(('set to fit minor groove (not implemented)', noop, 'disabled'))
    return res

# end
