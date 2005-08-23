# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
'''
undo.py

experimental Undo code. Might turn into a real source file.

$Id$
'''
__author__ = 'bruce'

###@@@ import this module from somewhere!

from cPickle import dump, load, HIGHEST_PROTOCOL
import env
from debug import register_debug_menu_command

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
    "call func and measure how long this takes. return a pair (time-taken, result-of-func)."
    from time import time as clock
    t1 = clock()
    res = func()
    t2 = clock()
    return (t2 - t1, res)

def saveposns(part, filename):
    env.history.message( "save main part atom posns to file: " + filename )
    def doit():
        save_atpos_list(part, filename)
    time, junk = time_taken(doit)
    env.history.message( "done; took %s" % time )
    return

def saveposns_cmd( target): # arg is the widget that has this debug menu
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "X"
    saveposns(part, filename)
    return

register_debug_menu_command("save atom posns", saveposns_cmd) # put this command into debug menu

def loadposns( part, filename): # doesn't move atoms (just a file-reading speed test, for now)
    env.history.message( "load atom posns from file (discards them, doesn't move atoms): " + filename )
    def doit():
        return load_obj(filename)
    time, posns_junk = time_taken(doit)
    env.history.message( "done; took %s" % time )
    return

def loadposns_cmd( target):
    win = target.topLevelWidget()
    assy = win.assy
    part = assy.tree.part
    filename = assy.filename + "X"
    loadposns(part, filename)
    return

register_debug_menu_command("load atom posns", loadposns_cmd)

#end
