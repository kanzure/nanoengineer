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
    env.history.message( "done; took %0.4f real secs, %0.4f cpu secs" % (realtime, cputime) )
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
            # use b.key -- not ideal but good enough test for now 
            dictb[b.key] = b.v6 # this runs twice per bond
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
    # and dictb has all v6's of all bonds
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

register_debug_menu_command("make key->pos dict", blerg_cmd)

# ==

def reload_undo(target=None):
    import undo
    reload(undo)
    print "reloaded undo.py"

register_debug_menu_command("reload undo.py", reload_undo)

# ==

def keep_under_key(thing, key, obj, attr):
    "obj.attr[key] = thing, creating obj.attr dict if necessary"
    if not hasattr(obj, attr):
        setattr(obj, attr, {})
    dict1 = getattr(obj, attr)
    dict1[key] = thing
    return

def wrapslot(target, signal, slotboundmethod, keepcache_object = None):
    """Caller is about to make a connection from target's signal to slotboundmethod.
    Based on target and signal, decide whether we want to wrap slotboundmethod with our own code.
       If so, return the wrapped slot (a python callable taking same args as slotboundmethod),
    but first make sure it won't be dereferenced too early by storing it in a dict
    at keepcache_object._keep_wrapslots (keepcache_object defaults to target)
    using a key formed from the names(??) of signal and slotboundmethod.
       If not, just return slotboundmethod unchanged.
    """
    # want to wrap it?
    if signal != SIGNAL("activated()"):
        if platform.atom_debug:
            print "don't know %r, not wrapping %s for %s" % (signal,slotboundmethod,target) ###@@@
        return slotboundmethod # don't know what args the fake method needs
    # make object which can wrap it
    wr = wrappedslot(slotboundmethod)
    # decide which api to call it with (#e this might be done inside the wrapper class)
    if signal == SIGNAL("activated()"):
        method = wr.fbmethod_0args
    else:
        assert 0 # use other methods
    # keep things that PyQt might need but not hold its own refs to
    keepkey = (signal, slotboundmethod.__name__) #k
    if platform.atom_debug:
            print "keepkey:",keepkey###@@@
    # We keep wr, in case method's ref to it is not enough at some future time (eg if method dies and wr is still wanted).
    # And we keep method, since we does not contain a ref to it, since bound methods are remade each time they're asked for.
    # For now, the code would work even if we didn't keep wr, but keeping method is essential.
    keepwhat = (wr, method)
    keep_under_key(keepwhat, keepkey, keepcache_object or target, '_keep_wrapslots')
    # return the wrapped slotboundmethod
    return method

class wrappedslot:
    """Hold a boundmethod for a slot, and return callables (for various arglists)
    which call it with our own code wrapping the call.
       We don't just return a callable which accepts arbitrary args, and pass them on,
    because we use this with PyQt which we suspect counts the accepted args
    in order to decide how many args to pass,
    and if we accepted all it had, some of our wrapped slots would receive more args
    than they can handle.
       Come to think of it, this probably won't be enough, because it *still* might
    pass us too many based on the ones listed in the signal name. We might have to
    revise this to count the args accepted by our saved slotboundmethod in __init__. ###k
    """
    def __init__(self, slotboundmethod):
        self.slotboundmethod = slotboundmethod
    def fbmethod_0args(self):
        "fake bound method with 0 args"
        slotboundmethod = self.slotboundmethod
        #e we'll replace these prints with our own begin/end code that's standard for slots;
        # or we might call methods passed to us, or of known names on an obj passed to us;
        # or we might call a func passed to us, passing it a callback to us which does the slot call.
        print "calling wrapped version of", slotboundmethod
        res = slotboundmethod()
        print "it returned", res
        return res
    pass

class hacked_connect_method_installer: #e could be refactored into hacked-method-installer and hacked-method-code to call origmethod
    """Provide methods which can hack the connect method of some class (assumed to be QWidget)
    by replacing it with our own version, which calls original version but perhaps with modified args.
    Other methods or public attrs let the client control what we do
    or see stats about how many times we intercepted a connect-method call.
    """
    def __init__(self):
        self.conns = {} # place to keep stats for debug
    def hack_connect_method(self, qclass):
        "Call this on QWidget class -- ONLY ONCE -- to hack its connect method." #e in __init__?
        self.qclass = qclass #k not yet used in subsequent methods
        methodname = 'connect'
        self.old_connect_method = getattr(qclass, methodname)
        fakemethod = self.fake_connect_method
        setattr(qclass, methodname, fakemethod)
        return
    def fake_connect_method(self, *args):
        "This gets called instead of qclass.connect, with the same args, and must pretend to do the same thing."
        # keep stats on len(args)
        self.conns.setdefault(len(args),0)
        self.conns[len(args)] += 1
        # call self.old_connect_method, perhaps wrapped with our own code
        if len(args) != 3:
            print "args not len 3:",args###@@@
            newargs = args
        else:
            # figure out what connection is being made, and whether we might to wrap its slot
            target, signal, slotboundmethod = args
            newmethod = wrapslot(target, signal, slotboundmethod) #e should wrapslot be a method of self?
                # newmethod is either slotboundmethod, or wraps it and is already kept (no need for us to preserve a ref to it)
            newargs = target, signal, newmethod
        res = self.old_connect_method(*newargs)
        if res is not True:
            print "connect retval is not True:",res
        return res
    def debug_print_stats(self, msg = '?'):
        self.stage = msg
        #e change to debug print only, but how soon can we import platform?
        print "hcmi %r: %r" % (self.stage, self.conns)
    pass

_hcmi = None

def hack_qwidget_pre_win_init(): # call this once, or more if you can't help it
    global _hcmi
    if _hcmi:
        print "redundant call of hack_qwidget_pre_win_init ignored"
        return
    _hcmi = hacked_connect_method_installer()
    from qt import QWidget
    qclass = QWidget
    _hcmi.hack_connect_method(qclass)
    return

# app startup code must call these at the right times:

_use_hcmi_hack = False # experimental code, DO NOT COMMIT with True until it works [bruce 050919]

def call_asap_after_QWidget_and_platform_imports_are_ok():
    import qt
    import platform # make sure these imports can be done now; platform will be needed later for atom_debug
    if not _use_hcmi_hack: return
    hack_qwidget_pre_win_init()
    _hcmi.debug_print_stats('first call')
    return

def just_before_mainwindow_super_init():
    if not _use_hcmi_hack: return
    _hcmi.debug_print_stats('just before mwsem super init')
    return

def just_after_mainwindow_super_init():
    if not _use_hcmi_hack: return
    _hcmi.debug_print_stats('just after mwsem super init')
    return

def just_before_mainwindow_init_returns():
    if not _use_hcmi_hack: return
    _hcmi.debug_print_stats('mwsem init is returning')
    return

# ==

class xxx:
    def open(self):
        assert os.path.isdir(self.dirname)
    def close(self):
        pass
    pass

# refactoring of above messy stuff

class wrapped2:
    "private helper class for replace_method_in_class" #e make this a descriptor? by defining its __get__ ... no, let it return one
    def __init__(self, origmethod, insertedfunc):
        self.args = origmethod, insertedfunc
        self.fbm = xxxthingy(self.fbm_inst) ### use special thingy to make this act like a whatever... so it picks up the instance when retrieved
    def fbm_inst(self, instance, *args, **kws):
        origmethod, insertedfunc = self.args
        return insertedfunc(origmethod, instance, *args, **kws)
    pass

def replace_method_in_class(clas, methodname, insertedfunc):
    """Replace a class's instance-method (clas.methodname) with a new one,
    or with an equivalent callable or descriptor (created herein),
    which intercepts all calls meant for the original method --
    these have the form instance.methodname(*args, **kws) for some instance of clas or a subclass --
    and instead calls insertedfunc(origmethod, instance, *args, **kws)
    (and returns what it returns, or raises any exceptions it raises).
       Return the pair (origmethod, keepthese),
    where keepthese is an object or list which the caller might need to keep a reference to
    in case clas itself won't keep a reference to methods we insert into it.
    """
    origmethod = getattr(clas, methodname) # an unbound instance-method object (#k official name of that type??)
    wr = wrapped2(origmethod, insertedfunc) #implem
    fbm = wr.fbm #implem
    keepthese  = [wr, fbm]
    setattr(clas, methodname, fbm)
    return origmethod, keepthese

def connect_insertedfunc( origmethod, instance, *args):
    """origmethod is QWidget.connect (i.e. an unbound instance method).
    instance is a QWidget.
    *args were passed to its connect method.
    Do the right thing, which includes calling origmethod with perhaps-modified args.
    """
    print 1
    res = origmethod( instance, *args)
    print 2
    return res

#end
