"""
$Id$
"""

# debug/test functions (in other submenu of debug menu) which won't be kept around.
# [moved out of undo.py by bruce 071004]

# not all of these are needed, perhaps:
from cPickle import dump, load, HIGHEST_PROTOCOL
import foundation.env as env
from utilities.debug import register_debug_menu_command, register_debug_menu_command_maker
    ###@@@ don't put all those commands in there -- use a submenu, use atom-debug,
    # or let them only show up if a related flag is set, or so...
from PyQt4.Qt import SIGNAL, QObject, QWidget #k ok to do these imports at toplevel? I hope so, since we need them in several places.
from utilities.constants import genKey, noop
from utilities import debug_flags # for atom_debug [bruce 060128, suggested by Mark;
    # if this works, we should simplify some defs which worry if it's too early for this]


from utilities.debug import call_func_with_timing_histmsg

def atpos_list(part):
    "Return a list of atom-position arrays, one per chunk in part. Warning: might include shared mutable arrays."
    res = []
    for m in part.molecules:
        res.append( m.atpos)
    return res

def save_atpos_list(part, filename):
    save_obj( atpos_list(part), filename)

def save_obj( thing, filename):
    file = open(filename, "wb")
    dump( thing, file, HIGHEST_PROTOCOL) # protocols: 0 ascii, 1 binary, 2 (new in 2.3) better for new style classes
    file.close()

def load_obj(filename):
    file = open(filename, "rb")
    res = load(file)
    file.close()
    return res

def saveposns(part, filename):
    env.history.message( "save main part atom posns to file: " + filename )
    def doit():
        save_atpos_list(part, filename)
    call_func_with_timing_histmsg( doit)

def saveposns_cmd( target): # arg is the widget that has this debug menu
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "X"
    saveposns(part, filename)
    return

## register_debug_menu_command("save atom posns", saveposns_cmd) # put this command into debug menu

# ==

def loadposns( part, filename): # doesn't move atoms (just a file-reading speed test, for now)
    env.history.message( "load atom posns from file (discards them, doesn't move atoms): " + filename )
    def doit():
        return load_obj(filename)
    posns = call_func_with_timing_histmsg( doit)
    return

def loadposns_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "X"
    loadposns(part, filename)
    return

## register_debug_menu_command("load atom posns", loadposns_cmd)

# ==

from Numeric import concatenate, array, UnsignedInt8

def atom_array_of_part(part):
    "Return an Array of all atoms in the Part. Try to be linear time."
    res = []
    for m in part.molecules:
        res.append( array(m.atlist) )
    # concatenate might fail for chunks with exactly 1 atom -- fix later ####@@@@
    return concatenate(res) ###k

def saveelts( part, filename):
    env.history.message( "save main part element symbols -- no, atomic numbers -- to file: " + filename )
    def doit():
        atoms = atom_array_of_part(part)
        ## elts = [atm.element.symbol for atm in atoms]
        elts = [atm.element.eltnum for atm in atoms]
        env.history.message( "%d element nums, first few are %r" % (len(elts), elts[:5] ) )
        thing = array(elts)
        save_obj(thing, filename)
    call_func_with_timing_histmsg( doit)
    return

def saveelts_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "E" # E, not X
    saveelts(part, filename)
    return

## register_debug_menu_command("save atom element numbers", saveelts_cmd)

# ==

def savebtypes( part, filename):
    env.history.message( "save main part bond type v6 ints to file: " + filename )
    def doit():
        atoms = atom_array_of_part(part)
        res = []
        for atm in atoms:
            for b in atm.bonds:
                # don't worry for now about hitting each bond twice... well, do, and see if this makes it slower, as i guess.
                if b.atom1 is atm:
                    res.append(b.v6) # a small int
        env.history.message( "%d btype ints, first few are %r" % (len(res), res[:5] ) )
        thing = array(res, UnsignedInt8) # tell it to use a smaller type; see numpy.pdf page 14 on typecodes.
            # update, bruce 070612: we still use Numeric Python (not numarray or numpy). I am not sure what URL
            # is referred to by "numpy.pdf" above, but it is probably (and should be) about Numeric Python.
        save_obj(thing, filename)
    call_func_with_timing_histmsg( doit)
    return

def savebtypes_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "B" # B, not E or X
    savebtypes(part, filename)
    return

## register_debug_menu_command("save bond type v6 ints", savebtypes_cmd)

# ==

# moved to pyrex_test.py

### this depends on undotest.pyx having been compiled by Pyrex ####@@@@
##
##def count_bonds_cmd( target):
##    win = target.topLevelWidget()
##    assy = win.assy
##    part = assy.tree.part
##    mols = part.molecules
##    env.history.message( "count bonds (twice each) in %d mols:" % len(mols) )
##    from undotest import nbonds # count bonds (twice each) in a sequence of molecules
##    def doit():
##        return nbonds(mols)
##    nb = call_func_with_timing_histmsg( doit)
##    env.history.message("count was %d, half that is %d" % (nb, nb/2) )
##    return
##
##register_debug_menu_command("count bonds", count_bonds_cmd)

# ==

def blerg_try1(mols):
    dict1 = {}
    for m in mols:
        atlist = m.atlist
        atpos = m.atpos
        keys = map( lambda a: a.key, atlist )
        # now efficiently loop over both those lists. I think there's a better way in python
        # (and surely it should be done in pyrex or Numeric anyway), but try easy way first:
        for key, pos in zip(keys, atpos):
            dict1[key] = pos
    # now dict1 maps key->pos for every atom in the system
    return len(dict1), 0 # untested retval

def update_keyposdict_keyv6dict_from_mol( dict1, dictb, m):
    atlist = m.atlist
    atpos = m.atpos
    ## keys = map( lambda a: a.key, atlist )
    # now efficiently loop over both those lists. I think there's a better way in python
    # (and surely it should be done in pyrex or Numeric anyway), but try easy way first:
    for atm, pos in zip(atlist, atpos):
        ## dict1[id(atm)] = pos
        dict1[atm.key] = pos
        for b in atm.bonds:
            # use id(b) -- not ideal but good enough test for now
            # (before 080229 this code used b.bond_key, which was usually but not entirely unique,
            #  and now has frequent collisions; note, it was already in outtakes on that date)
            dictb[id(b)] = b.v6 # this runs twice per bond
    return

def diff_keyposdict_from_mol( dict1, dict2, m):
    """Like update_keyposdict_from_mol, but use dict1 as old state, and store in dict2 just the items that differ.
    Deleted atoms must be handled separately -- this won't help find them even when run on all mols.
    [Could change that by having this delete what it found from dict1, at further substantial speed cost -- not worth it.]
    """
    atlist = m.atlist
    atpos = m.atpos
    for atm, pos in zip(atlist, atpos):
        key = atm.key
        if pos != dict1.get(key): # Numeric compare -- might be slow, we'll see
            dict2[key] = pos
    return

def blerg(mols):
    dict1 = {}
    dict2 = {}
    dictb = {}
    for m in mols:
        update_keyposdict_keyv6dict_from_mol( dict1, dictb, m)
        diff_keyposdict_from_mol( dict1, dict2, m)
    # now dict1 maps key->pos for every atom in the system
    # and dictb has all v6's of all bonds (mapping from id(bond))
    return len(dict1), len(dictb)

def blerg_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    mols = part.molecules
    env.history.message( "blorg in %d mols:" % len(mols) )
    def doit():
        return blerg(mols)
    na, nb = call_func_with_timing_histmsg( doit)
    env.history.message("count was %d, %d" % (na,nb,) )
    return

## register_debug_menu_command("make key->pos dict", blerg_cmd)
