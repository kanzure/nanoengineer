# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
undo.py

Undo-related code.

$Id$

Status as of 060117:

- contains some timing test commands still cluttering up the debug menu, 

- and some real code that wraps Qt slot calls and which will probably remain in the release
for helping identify commands, make their undo checkpoints, etc.

See also undo_archive.py, undo_manager.py.

Older:

At present [050922], a lot of new undo-related code is being added here
even though some of it belongs in other modules (existing or new).
Conversely, some new undo-related code can be found in env.py, changes.py,
and perhaps HistoryWidget.py.

A result of the mess of modules might be that too much gets imported
at app-startup time (even before .atom-debug-rc gets to run).
This needs to be cleaned up, but it's probably not urgent.

'''
__author__ = 'bruce'

debug_print_undo = False # DO NOT COMMIT with True -- causes lots of debug prints regardless of atom_debug

_use_hcmi_hack = True # enable signal->slot call intercepting code, to check for bugs that mess up other things [bruce 050922]

debug_print_fewer_args_retries = False # debug prints for fewer-args retries; DO NOT COMMIT with True


###@@@ import this module from a better place than we do now!

from cPickle import dump, load, HIGHEST_PROTOCOL
import env
from debug import register_debug_menu_command, register_debug_menu_command_maker
    ###@@@ don't put all those commands in there -- use a submenu, use atom-debug,
    # or let them only show up if a related flag is set, or so...
from qt import SIGNAL, QObject, QWidget #k ok to do these imports at toplevel? I hope so, since we need them in several places.
import qt
from constants import genKey, noop

# ==

# debug/test functions (in other submenu of debug menu) which won't be kept around.

from debug import call_func_with_timing_histmsg

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

## register_debug_menu_command("make key->pos dict", blerg_cmd)

# ===  [real code starts here]


def reload_undo(target=None):
    import undo_archive
    reload(undo_archive)
    import undo_manager
    reload(undo_manager)
    import undo
    reload(undo)
    print "\nreloaded undo.py and two others; open a new file and we'll use them\n" #e (works, but should make reopen automatic)

register_debug_menu_command("reload undo.py", reload_undo)

# ==

def keep_under_key(thing, key, obj, attr):
    "obj.attr[key] = thing, creating obj.attr dict if necessary"
    if debug_print_undo and 0:
        print "keepkey:",key,"keepon_obj:",obj # also print attr to be complete
            # This shows unique keys, but just barely (name is deleg for lots of QActions)
            # so we'll have to worry about it, and maybe force all keys unique during init.
            # If some keys are not unique, result might be that some user actions
            # (or for worse bugs, internal signals) silently stop working. [bruce 050921]
    if not hasattr(obj, attr):
        setattr(obj, attr, {})
    dict1 = getattr(obj, attr)
    dict1[key] = thing
    return

class wrappedslot:
    ###@@@ try revising code and doc to just pass on all the args, see if this works. easier re signal choices.
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
    def __init__(self, slotboundmethod, sender = None):
        self.slotboundmethod = slotboundmethod
        self.__sender = sender #060121
    def fbmethod_0args(self, *args, **kws):
        "fake bound method with 0 args" ###@@@ no, any number of args - redoc ###@@@
        slotboundmethod = self.slotboundmethod
        #e we'll replace these prints with our own begin/end code that's standard for slots;
        # or we might call methods passed to us, or of known names on an obj passed to us;
        # or we might call a func passed to us, passing it a callback to us which does the slot call.
        if kws:
            print "unexpected but maybe ok: some keywords were passed to a slot method:",slotboundmethod,kws ###@@@
        if debug_print_undo:
            print "(#e begin) calling wrapped version (with %d args) of" % len(args), slotboundmethod
        mc = self.begin()
        try:
            # do our best to call this slotmethod, with given args, or if that fails, with reduced args.
            try:
                res = slotboundmethod(*args, **kws)
            except TypeError: ####@@@@
                # it might be that we're passing too many args. Try to find out and fix. First, for debugging, print more info.
                if debug_print_fewer_args_retries:
                    print "args for %r from typeerror: args %r, kws %r" % (slotboundmethod, args, kws)
                success, maxargs, kws_ok = args_info(slotboundmethod)
                if not success:
                    # We have no official info about required args -- just see if it helps to reduce the ones we tried.
                    # Note that there is no guarantee that the original TypeError was caused by an excessive arglist;
                    # if it was caused by some other bug, these repeated calls could worsen that bug.
                    # (So taking advantage of an args_info success return is preferred, once that's implemented.)
                    arglists_to_try = [] # will hold pairs of (args, kws) to try calling it with.
                    if kws:
                        # first zap all the keywords (note: as far as I know, none are ever passed in the first place)
                        kws = {}
                        arglists_to_try.append(( args, kws ))
                    while args:
                        # then zap the args, one at a time, from the end
                        args = args[:-1]
                        arglists_to_try.append(( args, kws ))
                else:
                    assert 0, "nim - use maxargs, kws_ok to figure out arglists_to_try"
                worked = False
                for args, kws in arglists_to_try:
                    try:
                        res = slotboundmethod(*args, **kws)
                        worked = True
                        if debug_print_fewer_args_retries:
                            print " retry with fewer args (%d) worked" % len(args)
                        break # if no exceptions
                    except TypeError:
                        # guessing it's still an arg problem
                        if debug_print_fewer_args_retries:
                            print "args for %r from typeerror, RETRY: args %r, kws %r" % (slotboundmethod, args, kws)
                        continue
                    # other exceptions are treated as errors, below
                if not worked:
                    print "will try to reraise the last TypeError" # always print this, since we're about to print a traceback
                    raise
                    assert 0, "tried to reraise the last TypeError"
                pass
            pass
        except:
            self.error()
            self.end(mc)
            if debug_print_undo:
                print "(#e end) it had an exception"
            raise   #k ok? optimal??
        else:
            self.end(mc)
            if debug_print_undo:
                print "(#e end) it worked" ##  it returned", res
                    # Note that slot retvals are probably ignored, except when they're called directly
                    # (not via connections), but we don't intercept direct calls anyway.
                    # So don't bother printing them for now.
            return res
        pass
    def begin(self):
##        if 1: # 060121 debug code
##            try:
##                se = self.sender() # this can only be tried when we inherit from QObject, but it always had this exception.
##            except RuntimeError: # underlying C/C++ object has been deleted [common, don't yet know why, but have a guess]
##                print "no sender"
##                pass
##            else:
##                print "sender",se
        if 1: #060121
            sender = self.__sender
            ##print "sender",sender # or could grab its icon for insertion into history
            from whatsthis import _actions
            fn = _actions.get(id(sender))
                # When we used sender rather than id(sender), the UI seemed noticably slower!!
                # Possible problem with using id() is for temporary items -- when they're gone,
                # newly allocated ones with same id might seem to have those featurenames.
                # Perhaps we need to verufy the name is still present in the whatsthis text?
                # But we don't have the item itself here! We could keep it in the value, and then
                # it would stick around forever anyway so its id wouldn't be reused
                # but we'd have a memory leak for dynamic menus. Hmm... maybe we could add our own
                # key attribute to these items? And also somehow remove temporary ones from this dict
                # soon after they go away, or when new temp items are created for same featurename?
                # ... Decision: use our own key attr, don't bother removing old items from dict,
                # the leak per-cmenu is smaller than others we have per-user-command. ####@@@@ DOIT
            if fn:
                if 1: #experiment 060121
                    from debug import print_compact_traceback
                    try:
                        win = env.mainwindow()
                        assert win.initialised # make sure it's not too early
                        assy = win.assy
                    except:
                        if platform.atom_debug:
                            print_compact_traceback("atom_debug: fyi: normal exception: ")
                        pass # this is normal during init... or at least I thought it would be -- I never actually saw it yet.
                    else:
                        assy.undo_checkpoint_before_command(fn)
                if 0: print " featurename =", fn
                    # This works! prints correct names for toolbuttons and main menu items.
                    # Doesn't work for glpane cmenu items, but I bet it will when we fix them to have proper WhatsThis text.
                    # Hmm, how will we do that? There is presently no formal connection between them and the usual qactions
                    # or toolbuttons or whatsthis features for the main UI for the same method. We might have to detect the
                    # identity of the bound method they call as a slot! Not sure if this is possible. If not, we have to set
                    # command names from inside the methods that implement them (not the end of the world), or grab them from
                    # history text (doable).
        return env.begin_op("(wr)")
    def error(self):
        "called when an exception occurs during our slot method call"
        pass ### mark the op_run as having an error
    def end(self, mc):
        env.end_op(mc)
    pass

class hacked_connect_method_installer: #e could be refactored into hacked-method-installer and hacked-method-code to call origmethod
    """Provide methods which can hack the connect and disconnect methods of some class (assumed to be QWidget or QObject)
    by replacing them with our own version, which calls original version but perhaps with modified args.
    Other methods or public attrs let the client control what we do
    or see stats about how many times we intercepted a connect-method call.
    """
    def __init__(self):
        self.conns = {} # place to keep stats for debug
    def hack_connect_method(self, qclass):
        "Call this on QWidget or QObject class -- ONLY ONCE -- to hack its connect method." #e in __init__?
        self.qclass = qclass #k not yet used in subsequent methods, only in this one
        replace_static_method_in_class( qclass, 'connect', self.fake_connect_method )
        replace_static_method_in_class( qclass, 'disconnect', self.fake_disconnect_method )
        return
    def fake_connect_method(self, origmethod, *args):
        """ This gets called on all QWidgets instead of the static method QObject.connect,
        with the original implem of that method followed by the args from the call
        (not including the instance it was called on, since it replaces a static method),
        and must pretend to do the same thing, but it actually modifies some of the args
        before calling the origmethod.
        """
        # keep stats on len(args)
        self.conns.setdefault(len(args),0)
        self.conns[len(args)] += 1
        # call origmethod, perhaps wrapped with our own code
        if len(args) != 3:
            # The last two args are an object and a slotname. We might *like* to wrap that slot,
            # but we can't, unless we figure out how to turn the object and slotname into an equivalent bound method
            # which we could use instead of those last two args.
            # So for now, let's just print the args and hope we didn't need to wrap them.
            if debug_print_undo:
                print "not wrapping connect-slot since args not len 3:",args###@@@
            newargs = args
        else:
            # figure out what connection is being made, and whether we want to wrap its slot
            sender, signal, slotboundmethod = args
            signal = normalize_signal(signal) # important for slotmap, below; better than not, for the other uses
            newmethod = self.maybe_wrapslot(sender, signal, slotboundmethod)
                # newmethod is either slotboundmethod, or wraps it and is already kept (no need for us to preserve a ref to it)
            newargs = sender, signal, newmethod
            # record mapping from old to new slot methods (counting them in case redundant conns), for use by disconnect;
            # keep this map on the sender object itself
            try:
                slotmap = sender.__slotmap
            except AttributeError:
                slotmap = sender.__slotmap = {}
            key = (signal, slotboundmethod) # slotboundmethod has different id each time, but is equal when it needs to be
            slotmap.setdefault(key, []).append( newmethod ) # ok if newmethod is slotboundmethod (in fact, better to add it than not)
                # redundant connections result in slotmap values of len > 1, presumably with functionally identical but unequal objects
        res = origmethod(*newargs) # pass on any exceptions
        if res is not True:
            print "likely bug: connect retval is not True:", res
            print " connect args (perhaps modified) were:", newargs
        return res
    def fake_disconnect_method(self, origmethod, *args):
        if len(args) != 3:
            if debug_print_undo:
                print "not wrapping DISconnect-slot since args not len 3:",args###@@@ let's hope this happens only when it did for connect
            newargs = args
        else:
            sender, signal, slotboundmethod = args
            signal = normalize_signal(signal)
            try:
                slotmap = sender.__slotmap
            except AttributeError:
                # should never happen unless there's a disconnect with no prior connect
                slotmap = sender.__slotmap = {}
            key = (signal, slotboundmethod)
            lis = slotmap[key] # fails only if there's a disconnect with no prior connect
            newmethod = lis.pop() # should never fail, due to deleting empty lists (below)
            if not lis:
                del slotmap[key] # not really needed but seems better for avoiding memory leaks
            newargs = sender, signal, newmethod
        res = origmethod(*newargs) # pass on any exceptions
        if res is not True: ##k
            print "likely bug: disconnect retval is not True:", res
            print " disconnect args (perhaps modified) were:", newargs
        return res
    def debug_print_stats(self, msg = '?'):
        self.stage = msg
        #e change to debug print only, but how soon can we import platform?
        if debug_print_undo:
            print "hcmi %r: %r" % (self.stage, self.conns)
    def maybe_wrapslot(self, sender, signal, slotboundmethod, keepcache_object = None):
        """Caller is about to make a connection from sender's signal to slotboundmethod.
        Based on sender and signal, decide whether we want to wrap slotboundmethod with our own code.
           If so, return the wrapped slot (a python callable taking same args as slotboundmethod),
        but first make sure it won't be dereferenced too early, by storing it in a dict
        at keepcache_object._keep_wrapslots (keepcache_object defaults to sender)
        using a key formed from the names(??) of signal and slotboundmethod.
           If not, just return slotboundmethod unchanged.
        """
        ## nice, but not needed, for keepkey; no longer needed for decide: signal = normalize_signal(signal)
        # want to wrap it?
        shouldwrap = self.decide(sender, signal) # always True, for now [clean up this code ###@@@]
        if not shouldwrap:
            if debug_print_undo:
                print "not wrapping %s from %s to %s" % (signal,sender,slotboundmethod) ###@@@
            return slotboundmethod
        # make object which can wrap it
        wr = wrappedslot(slotboundmethod, sender = sender) #060121 added sender arg
        # decide which api to call it with (#e this might be done inside the wrapper class)
        if 1: ## or signal == SIGNAL("activated()"):
            method = wr.fbmethod_0args
        else:
            assert 0 # use other methods
        # keep things that PyQt might need but not hold its own refs to
        keepkey = (signal, slotboundmethod.__name__) #k
        keepon = keepcache_object or sender
        # We keep wr, in case method's ref to it is not enough at some future time (eg if method dies and wr is still wanted).
        # And we keep method, since we does not contain a ref to it, since bound methods are remade each time they're asked for.
        # For now, the code would work even if we didn't keep wr, but keeping method is essential.
        keepwhat = (wr, method)
        keep_under_key(keepwhat, keepkey, keepon, '_keep_wrapslots')
        # return the wrapped slotboundmethod
        return method
    def decide(self, sender, signal):
        "should we wrap the slot for this signal when it's sent from this sender?"
        return True # try wrapping them all, for simplicity
    pass # end of class hacked_connect_method_installer

_hcmi = None

def hack_qwidget_pre_win_init(): # call this once, or more times if you can't avoid it; you must call it before main window is inited
    global _hcmi
    if _hcmi:
        print "redundant call of hack_qwidget_pre_win_init ignored"
        return
    _hcmi = hacked_connect_method_installer()
    qclass = QObject # works with QWidget; also works with QObject and probably gets more calls
    _hcmi.hack_connect_method(qclass)
    return

# ==

# app startup code must call these at the right times:

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

# Code for replacing QWidget.connect or QObject.connect
# (in either case, the same builtin static method of QObject, not a regular instance method)
# with our own function, which calls the original implem inside our own wrapping code.
# Note that the origmethod is just a builtin function, and our wrapping code has no knowledge
# of which QWidget instance it was called on, since this is not easy to get and not needed
# (or even permitted) to pass to the origmethod.

class fake_static_method_supplier:
    "[private helper class for replace_static_method_in_class]"
    def __init__(self, origmethod, insertedfunc):
        self.args = origmethod, insertedfunc
        self.fsm = self._fake_static_method_implem
            # memoize one copy of this self-bound method,
            # which pretends to be another class's static method
    def fake_static_method_and_keep_these(self):
        """Return the pair (fake_static_method, keep_these) [see calling code for explanation].
        fake_static_method need not be wrapped in staticmethod since it's not a user-defined function
        or any other object which will be turned into a bound method when retrieved from the class it
        will be installed in. (If things change and use of staticmethod becomes necessary, it should
        be done in this method, so the caller still won't need to do it.)
        """
        # terminology note: fsm is a *bound* method of this instance,
        # which is a fake *unbound, static* method of clas in replace_static_method_in_class().
        return self.fsm, self
            # self is enough for caller to keep a reference to,
            # since self has its own reference to self.fsm;
            # if we remade self.fsm on each call, we'd have to return both in keep_these.
            # (Presumably even self.fsm would be enough for caller to keep.)
    def _fake_static_method_implem(self, *args, **kws):
        "this is what runs in place of origmethod(*args, **kws)"
        origmethod, insertedfunc = self.args
        return insertedfunc(origmethod, *args, **kws) # or pass on any exceptions it might raise
    pass

def replace_static_method_in_class(clas, methodname, insertedfunc):
    """Replace a class's static instance-method (clas.methodname) with a new one (created herein)
    which intercepts all calls meant for the original method --
    these have the form instance.methodname(*args, **kws) for some instance of clas or a subclass,
    and like all static methods would have been called like origmethod(*args, **kws)
    (ignoring instance), where origmethod is the original static method we're replacing --
    and instead calls insertedfunc(origmethod, *args, **kws)
    (and returns what it returns, or raises any exceptions it raises).
       Return the pair (origmethod, keepthese),
    where keepthese is an object or list which the caller might need to keep a reference to
    in case clas itself won't keep a reference to methods we insert into it.
    """
    origmethod = getattr(clas, methodname)
        # a static method (equivalent to an ordinary function -- arglist doesn't contain the instance)
    wr = fake_static_method_supplier( origmethod, insertedfunc)
    fakemethod, keepthese = wr.fake_static_method_and_keep_these()
    setattr(clas, methodname, fakemethod)
    return origmethod, keepthese

# ==

def normalize_signal(signal):
    "normalize whitespace in signal string, which should be SIGNAL(xx) or (untested) PYSIGNAL(xx)"
    try:
        # this fails with AttributeError: normalizeSignalSlot [bruce 050921]
        return QObject.normalizeSignalSlot(signal)
            # (this should call a static method on QObject)
    except AttributeError:
        # Use my own hacked-up kluge, until the above lost method gets found.
        # I think it doesn't matter if this has same output as Qt version,
        # as long as it makes some canonical form with the same equivalence classes
        # as the Qt version, since it's only used to prepare keys for my own dicts.
        words = signal[1:].split() # this ignores whitespace at start or end of signal[1:]
        def need_space_between(w1, w2):
            def wordchar(c):
                return c in "_" or c.isalnum() #k guess
            return wordchar(w1[-1]) and wordchar(w2[0])
        res = signal[0] + words[0]
        for w1, w2 in zip(words[:-1],words[1:]):
            # for every pair of words; w1 has already been appended to res
            if need_space_between(w1, w2):
                res += ' '
            res += w2
##        if signal != res and debug_print_undo and 0:
##            print "hack converted %r to %r" % (signal, res) # they all look ok
        return res
    pass

# ==

def args_info(func1):
    """Given a function or method object, return (success, maxargs, kws_ok),
    where success is a boolean saying whether we succeeded in finding out other retvals (if not they are "loose guesses"),
    maxargs is the max number of positional args it can take, according to introspection, or None if infinite or we can't tell,
    and kws_ok says whether it can accept any keyword args whatsoever, whether of specific or arb names (or is True if we can't tell).
    """
    return False, None, True # what to return if we can't tell -- this is a stub to always return it

# ==

#end
