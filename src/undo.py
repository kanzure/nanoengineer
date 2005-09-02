# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
undo.py

Experimental Undo code. Might turn into a real source file.

Creates some debug menu commands which we'll remove before releasing A7.

$Id$
'''
__author__ = 'bruce'

###@@@ import this module from a better place than we do now!

from cPickle import dump, load, HIGHEST_PROTOCOL
import env
from debug import register_debug_menu_command ###@@@ don't put all those commands in there -- use a submenu, use atom-debug,
    # or let them only show up if a related flag is set, or so...

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

def time_taken(func):
    "call func and measure how long this takes. return a triple (real-time-taken, cpu-time-taken, result-of-func)."
    from time import time, clock
    t1c = clock()
    t1t = time()
    res = func()
    t2c = clock()
    t2t = time()
    return (t2t - t1t, t2c - t1c, res)

def saveposns(part, filename):
    env.history.message( "save main part atom posns to file: " + filename )
    def doit():
        save_atpos_list(part, filename)
    call_func_with_timing_histmsg( doit)

def call_func_with_timing_histmsg( func):
    realtime, cputime, res = time_taken(func)
    env.history.message( "done; took %s real secs, %s cpu secs" % (realtime, cputime) )
    return res

def saveposns_cmd( target): # arg is the widget that has this debug menu
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "X"
    saveposns(part, filename)
    return

register_debug_menu_command("save atom posns", saveposns_cmd) # put this command into debug menu

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

register_debug_menu_command("load atom posns", loadposns_cmd)

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

register_debug_menu_command("save atom element numbers", saveelts_cmd)

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

register_debug_menu_command("save bond type v6 ints", savebtypes_cmd)

# ==

# this depends on undotest.pyx having been compiled by Pyrex ####@@@@

def count_bonds_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    mols = part.molecules
    env.history.message( "count bonds (twice each) in %d mols:" % len(mols) )
    from undotest import nbonds # count bonds (twice each) in a sequence of molecules
    def doit():
        return nbonds(mols)
    nb = call_func_with_timing_histmsg( doit)
    env.history.message("count was %d, half that is %d" % (nb, nb/2) )
    return

register_debug_menu_command("count bonds", count_bonds_cmd)

# ==

class xxx:
    def open(self):
        assert os.path.isdir(self.dirname)
    def close(self):
        pass
    pass

#end
