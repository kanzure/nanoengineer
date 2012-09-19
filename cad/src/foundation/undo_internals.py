# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
undo_internals.py - wrap our Qt slot methods with Undo checkpoints.

See also: undo_archive.py, undo_manager.py, undo_UI.py,
def wrap_callable_for_undo, and perhaps some undo-related
code in env.py, changes.py, HistoryWidget.py.

@author: Bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

Module classification: foundation.
"""

import foundation.env as env
from utilities.debug import register_debug_menu_command
from PyQt4.Qt import QObject ## , QWidget, SIGNAL
from utilities import debug_flags # for atom_debug
import utilities.EndUser as EndUser

# debug print options

DEBUG_PRINT_UNDO = False # DO NOT COMMIT with True -- causes lots of debug prints regardless of atom_debug

DEBUG_FEWER_ARGS_RETRY = True # debug prints for fewer-args retries; now True since these are deprecated [bruce 071004]

DEBUG_GETARGSPEC = False # DO NOT COMMIT with True -- debug prints related to USE_GETARGSPEC (only matters when that's true)

DEBUG_USE_GETARGSPEC_TypeError = False # print the few cases which args_info can't yet handle (### TODO: fix it for these ASAP)

# options that change behavior

USE_GETARGSPEC = True # bruce 071004

_use_hcmi_hack = True # enable signal->slot call intercepting code, to check for bugs that mess up other things [bruce 050922]
    # i suspect this now has to be true (undo won't work without it) -- if true, remove this [bruce 071003 comment]

if not EndUser.enableDeveloperFeatures():
    # end user case
    DISABLE_SLOT_ARGCOUNT_RETRY = False
        # be looser for end-users until we're sure we fixed all the bugs
        # this would expose and turn into exceptions, as explained in the
        # long comment in the other case.
        # [bruce 071004, per team call]
    NONERROR_STDERR_OK = False # in case we're on a Windows install for which prints to sys.stderr cause exceptions
        # (that issue ought to be fixed more generally than in this file)
else:
    # developer case
    DISABLE_SLOT_ARGCOUNT_RETRY = True # bruce 071004 -- WHEN True, THIS WILL EXPOSE SOME BUGS as new TypeError exceptions.
    #
    # (see also a change to this for endusers, below.)
    #
    # To fix the bugs this exposes, add the proper argument declarations to slot
    # methods which are raising TypeError due to being passed too many args by a
    # signal connection inside fbmethod_0args.
    #
    # Or to temporarily work around them, set this flag to False in your local
    # sources, in this case or below it (but be sure not to commit that change).
    #
    # Details:
    #
    #  When True, this simulates a proposed simplification
    # in which we only try calling slot methods with all the available args
    # passed to them by PyQt.
    #
    #  When False, as has always been effectively the case as of 071004, we
    # retry them with fewer arguments if they raise TypeError to complain about
    # too many (or, unfortunately, if they raise it for some other reason), in
    # order to imitate a similar (but probably safer) behavior documented by
    # PyQt3.
    NONERROR_STDERR_OK = True

## DISABLE_SLOT_ARGCOUNT_RETRY = False # DO NOT COMMIT with this line enabled -- for testing of end user case code

if EndUser.enableDeveloperFeatures():
    print "DISABLE_SLOT_ARGCOUNT_RETRY =", DISABLE_SLOT_ARGCOUNT_RETRY

# ==

def reload_undo(target = None):
    # does this work at all, now that undo_UI was split out of undo_manager? [bruce 071217 Q]
    import foundation.undo_archive as undo_archive
    reload(undo_archive)
    import foundation.undo_manager as undo_manager
    reload(undo_manager)
    import foundation.undo_internals as undo_internals
    reload(undo_internals)
    print "\nreloaded 3 out of 4 undo_*.py files; open a new file and we'll use them\n" #e (works, but should make reopen automatic)

register_debug_menu_command("reload undo", reload_undo)

# ==

def keep_under_key(thing, key, obj, attr):
    """
    obj.attr[key] = thing, creating obj.attr dict if necessary
    """
    if DEBUG_PRINT_UNDO and 0:
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
    """
    WARNING: the details in this docstring are obsolete as of sometime before 071004.

       Hold a boundmethod for a slot, and return callables (for various arglists)
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
    # default values of instance variables
    args_info_result = None # cached return value from args_info
    need_runtime_test = True # whether we need to test whether our signal passed too many args to our slot, at runtime

    def __init__(self, slotboundmethod, sender = None, signal = ""):
        self.slotboundmethod = slotboundmethod
        if USE_GETARGSPEC:
            # Print a warning if it looks like the signal and slot argument counts don't match;
            # if DEBUG_GETARGSPEC then always print something about the analysis result.
            # Also try to save info on self, so args_info needn't be called at runtime.
            from utilities.debug import print_compact_traceback
            try:
                self.args_info_result = args_info(slotboundmethod)
                success, minargs, maxargs, any_kws_ok = self.args_info_result
                if success:
                    # if DEBUG_GETARGSPEC, args_info already printed basic info
                    if any_kws_ok and DEBUG_GETARGSPEC:
                        print "DEBUG_GETARGSPEC: surprised to see **kws in a slot method; ignoring this issue: %r" % (slotboundmethod,)
                    del any_kws_ok
                    signal_args = guess_signal_argcount(signal)
                    strict = True # whether our test is not certain (i.e. too loose); might be set to false below
                    if minargs is None:
                        # maybe this can never happen as of 071004
                        minargs = 0
                        strict = False
                    if maxargs is None:
                        if DEBUG_GETARGSPEC:
                            print "DEBUG_GETARGSPEC: note: %r accepts **args, unusual for a slot method" % (slotboundmethod,)
                        maxargs = max(999999, signal_args + 1)
                        strict = False
                    assert type(minargs) == type(1)
                    assert type(maxargs) == type(1)
                    ok = (minargs <= signal_args <= maxargs)
                    if not ok:
                        # print the warning which is the point of USE_GETARGSPEC
                        if minargs != maxargs:
                            print "\n * * * WARNING: we guess %r wants from %d to %d args, but signal %r passes %d args" % \
                                  (slotboundmethod, minargs, maxargs, signal, signal_args)
                        else:
                            print "\n * * * WARNING: we guess %r wants %d args, but signal %r passes %d args" % \
                                  (slotboundmethod, maxargs, signal, signal_args)
                    elif DEBUG_GETARGSPEC:
                        if minargs != maxargs:
                            print "DEBUG_GETARGSPEC: %r and %r agree about argcount (since %d <= %d <= %d)" % \
                                  (slotboundmethod, signal, minargs, signal_args, maxargs)
                        else:
                            assert signal_args == minargs
                            print "DEBUG_GETARGSPEC: %r and %r agree about argcount %d" % \
                                  (slotboundmethod, signal, minargs)
                    self.need_runtime_test = (not ok) or (not strict)
                        # REVIEW: also say "or any_kws_ok", or if kws passed at runtime?
                else:
                    # args_info failed; it already printed something if DEBUG_GETARGSPEC
                    pass
            except:
                print_compact_traceback("USE_GETARGSPEC code failed for %r: " % slotboundmethod)
            pass
        self.__sender = sender #060121
        self.__signal = signal #060320 for debugging
        return # from __init__
    def fbmethod_0args(self, *args, **kws):
        """
        fake bound method with any number of args (misnamed)
        """
        slotboundmethod = self.slotboundmethod
        #e we'll replace these prints with our own begin/end code that's standard for slots;
        # or we might call methods passed to us, or of known names on an obj passed to us;
        # or we might call a func passed to us, passing it a callback to us which does the slot call.
        if kws:
            print "unexpected but maybe ok: some keywords were passed to a slot method:", slotboundmethod, kws # maybe never seen
        if DEBUG_PRINT_UNDO:
            print "(#e begin) calling wrapped version (with %d args) of" % len(args), slotboundmethod
        mc = self.begin()
        try:
            if DISABLE_SLOT_ARGCOUNT_RETRY:
                # call slotmethod with exactly the same args we were passed
                # (this is known to often fail as of 071004, but we hope to fix that)
                res = slotboundmethod(*args, **kws)
            else:
                # deprecated case to be removed soon, but in the meantime, rewritten to be more
                # reliable [bruce 071004]
                # try calling slotmethod with exactly the args we were passed,
                # but if we get a TypeError, assume this probably means the slot method accepts
                # fewer args than the signal passes, so try again with fewer and fewer args until
                # we get no TypeError.
                # If USE_GETARGSPEC and not self.need_runtime_test, assume self.args_info_result
                # can be trusted to specify the possible numbers of args to pass;
                # otherwise assume it could be any number (as the code before 071004 always did).
                try:
                    res = slotboundmethod(*args, **kws)
                except TypeError:
                    # it might be that we're passing too many args. Try to find out and fix. First, for debugging, print more info.
                    if DEBUG_FEWER_ARGS_RETRY:
                        print "args for %r from typeerror: args %r, kws %r" % (slotboundmethod, args, kws)
                    if USE_GETARGSPEC and not self.need_runtime_test:
                        if self.args_info_result is None:
                            self.args_info_result = args_info(slotboundmethod)
                        success, minargs, maxargs, any_kws_ok = self.args_info_result
                        del any_kws_ok # ignored for now
                        assert success
                        del success
                        assert type(minargs) == type(maxargs) == type(1)
                        # use minargs and maxargs to limit the calls we'll try
                    else:
                        # try any reduced number of args
                        minargs = 0
                        maxargs = len(args)
                    # Construct arglists to use for retrying this call.
                    # Note that there is no guarantee that the original TypeError was caused by an excessive arglist;
                    # if it was caused by some other bug, these repeated calls could worsen that bug.
                    arglists_to_try = [] # will hold pairs of (args, kws) to try calling it with.
                    if kws:
                        # first try zapping all the keywords (note: as far as I know, none are ever passed in the first place)
                        arglists_to_try.append(( args, {} ))
                    while args:
                        # then zap the args, one at a time, from the end (but consider minargs and maxargs)
                        args = args[:-1]
                        if minargs <= len(args) <= maxargs:
                            arglists_to_try.append(( args, kws ))
                    # Retry it with those arglists (zero or more of them to try)
                    worked = False
                    from utilities.debug import print_compact_traceback
                    for args, kws in arglists_to_try:
                        try:
                            res = slotboundmethod(*args, **kws)
                            worked = True
                            if DEBUG_FEWER_ARGS_RETRY:
                                print " retry with fewer args (%d) worked" % len(args)
                            break # if no exceptions
                        except TypeError:
                            # guessing it's still an arg problem
                            if DEBUG_FEWER_ARGS_RETRY:
                                if NONERROR_STDERR_OK:
                                    print_compact_traceback("assuming this is a slot argcount problem: ")
                                print "args for %r from typeerror, RETRY: args %r, kws %r" % (slotboundmethod, args, kws)
                            continue
                        # other exceptions are treated as errors, below
                    if not worked:
                        # TODO (maybe): retry with first arglist? more likely to be the real error...
                        print "will try to reraise the last TypeError" # always print this, since we're about to print a traceback
                        raise
                        assert 0, "tried to reraise the last TypeError"
                    pass
                pass
            pass
        except:
            self.error()
            self.end(mc)
            if DEBUG_PRINT_UNDO:
                print "(#e end) it had an exception"
            print "bug: exception in %r%r (noticed in its undo wrapper); reraising it:" % (slotboundmethod, args)
            raise   #k ok? optimal??
        else:
            self.end(mc)
            if DEBUG_PRINT_UNDO:
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
        ## cp_fn = None # None, or a true thing enabling us to call undo_checkpoint_after_command
        if 1: #060127
            in_event_loop = env._in_event_loop
            mc = env.begin_op("(wr)") # should always change env._in_event_loop to False (or leave it False)
            assert not env._in_event_loop
        if in_event_loop: #060121, revised 060127 and cond changed from 1 to in_event_loop
            #e if necessary we could find out whether innermost op_run in changes.py's stack still *wants* a cmdname to be guessed...
            # this would be especially important if it turns out this runs in inner calls and guesses it wrong,
            # overwriting a correct guess from somewhere else...
            # also don't we need to make sure that the cmd_seg we're guessing for is the right one, somehow???
            # doesn't that mean the same as, this begin_op is the one that changed the boundary? (ie call came from event loop?)
            sender = self.__sender
            ##print "sender",sender # or could grab its icon for insertion into history
            from foundation.whatsthis_utilities import map_from_id_QAction_to_featurename
            fn = map_from_id_QAction_to_featurename.get(id(sender))
                # When we used sender rather than id(sender), the UI seemed noticably slower!!
                # Possible problem with using id() is for temporary items -- when they're gone,
                # newly allocated ones with same id might seem to have those featurenames.
                # Perhaps we need to verify the name is still present in the whatsthis text?
                # But we don't have the item itself here! We could keep it in the value, and then
                # it would stick around forever anyway so its id wouldn't be reused,
                # but we'd have a memory leak for dynamic menus. Hmm... maybe we could add our own
                # key attribute to these items? And also somehow remove temporary ones from this dict
                # soon after they go away, or when new temp items are created for same featurename?
                # ... Decision [nim]: use our own key attr, don't bother removing old items from dict,
                # the leak per-cmenu is smaller than others we have per-user-command. ####@@@@ DOIT
            if fn:
                if 1: #experiment 060121
                    from utilities.debug import print_compact_traceback
                    try:
                        win = env.mainwindow()
                        assert win.initialised # make sure it's not too early
                        assy = win.assy
                    except:
                        if debug_flags.atom_debug:
                            print_compact_traceback("atom_debug: fyi: normal exception: ")
                        pass # this is normal during init... or at least I thought it would be -- I never actually saw it yet.
                    else:
##                        begin_retval = assy.undo_checkpoint_before_command(fn)
##                        cp_fn = fn, begin_retval #e this should include a retval from that method, but must also always be true
                        if 1: #060127
                            # note, ideally this assy and the one that subscribes to command_segment changes
                            # should be found in the same way (ie that one should sub to this too) -- could this just iterate over
                            # same list and call it differently, with a different flag?? ##e
                            assy.current_command_info(cmdname = fn) #e cmdname might be set more precisely by the slot we're wrapping
                if 0:
                    print " featurename =", fn
                    # This works! prints correct names for toolbuttons and main menu items.
                    # Doesn't work for glpane cmenu items, but I bet it will when we fix them to have proper WhatsThis text.
                    # Hmm, how will we do that? There is presently no formal connection between them and the usual qactions
                    # or toolbuttons or whatsthis features for the main UI for the same method. We might have to detect the
                    # identity of the bound method they call as a slot! Not sure if this is possible. If not, we have to set
                    # command names from inside the methods that implement them (not the end of the world), or grab them from
                    # history text (doable).
            else:
                #060320 debug code; note, this shows signals that might not need undo cp's, but for almost all signals,
                # they might in theory need them in the future for some recipients, so it's not usually safe to exclude them.
                # Instead, someday we'll optimize this more when no changes actually occurred (e.g. detect that above).
                if 0 and env.debug():
                    print "debug: wrappedslot found no featurename, signal = %r, sender = %r" % (self.__signal, sender)
        ## return cp_fn, mc  #060123 revised retval
        return mc
    def error(self):
        """
        called when an exception occurs during our slot method call
        """
        ###e mark the op_run as having an error, or at least print something
        if debug_flags.atom_debug:
            print "atom_debug: unmatched begin_op??"
        return
    def end(self, mc):
        ## cp_fn, mc = fn_mc
        env.end_op(mc)
##        if 1: #060123
##            if cp_fn:
##                fn, begin_retval = cp_fn
##                win = env.mainwindow()
##                assy = win.assy
##                assy.undo_checkpoint_after_command( begin_retval)
        return
    pass

class hacked_connect_method_installer: #e could be refactored into hacked-method-installer and hacked-method-code to call origmethod
    """
    Provide methods which can hack the connect and disconnect methods of some class (assumed to be QWidget or QObject)
    by replacing them with our own version, which calls original version but perhaps with modified args.
    Other methods or public attrs let the client control what we do
    or see stats about how many times we intercepted a connect-method call.
    """
    def __init__(self):
        self.conns = {} # place to keep stats for debug
    def hack_connect_method(self, qclass):
        """
        Call this on QWidget or QObject class -- ONLY ONCE -- to hack its connect method.
        """
        #e in __init__?
        self.qclass = qclass #k not yet used in subsequent methods, only in this one
        replace_static_method_in_class( qclass, 'connect', self.fake_connect_method )
        replace_static_method_in_class( qclass, 'disconnect', self.fake_disconnect_method )
        return
    def fake_connect_method(self, origmethod, *args):
        """
        This gets called on all QWidgets instead of the static method QObject.connect,
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
            if DEBUG_PRINT_UNDO:
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
            if DEBUG_PRINT_UNDO:
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
            try:
                lis = slotmap[key] # fails only if there's a disconnect with no prior connect
            except KeyError:
                # this case added by bruce 070615
                print "likely bug: disconnect with no prior connect", key #e need better info?
                newargs = args # still call disconnect -- ok?? I guess so -- it returns False, but no other apparent problem.
            else:
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
        if DEBUG_PRINT_UNDO:
            print "hcmi %r: %r" % (self.stage, self.conns)
    def maybe_wrapslot(self, sender, signal, slotboundmethod, keepcache_object = None):
        """
        Caller is about to make a connection from sender's signal to slotboundmethod.
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
            if DEBUG_PRINT_UNDO:
                print "not wrapping %s from %s to %s" % (signal,sender,slotboundmethod) ###@@@
            return slotboundmethod
        # make object which can wrap it
        wr = wrappedslot(slotboundmethod, sender = sender, signal = signal) #060121 added sender arg #060320 added signal arg
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
        """
        should we wrap the slot for this signal when it's sent from this sender?
        """
        if 'treeChanged' in str(signal): ###@@@ kluge: knowing this [bruce 060320 quick hack to test-optimize Undo checkpointing]
            if env.debug():
                ###@@@ kluge: assuming what we're used for, in this message text
                print "debug: note: not wrapping this signal for undo checkpointing:", signal
            return False
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
    # note, misnamed now -- called when its "init in spirit" returns, not its __init__ [060223 comment]
    if 1:
        #bruce 060223; logically this would be better to call directly from MWsemantics, but I don't want to modify that file right now
        import foundation.env as env
        win = env.mainwindow()
        win.assy.clear_undo_stack() # necessary to tell it it's safe to make its initial checkpoint, and start recording more
    #k is the following still active? [060223 question]
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
    """
    [private helper class for replace_static_method_in_class]
    """
    def __init__(self, origmethod, insertedfunc):
        self.args = origmethod, insertedfunc
        self.fsm = self._fake_static_method_implem
            # memoize one copy of this self-bound method,
            # which pretends to be another class's static method
    def fake_static_method_and_keep_these(self):
        """
        Return the pair (fake_static_method, keep_these) [see calling code for explanation].
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
        """
        this is what runs in place of origmethod(*args, **kws)
        """
        origmethod, insertedfunc = self.args
        return insertedfunc(origmethod, *args, **kws) # or pass on any exceptions it might raise
    pass

def replace_static_method_in_class(clas, methodname, insertedfunc):
    """
    Replace a class's static instance-method (clas.methodname) with a new one (created herein)
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
    """
    normalize whitespace in signal string, which should be SIGNAL(xx) or (untested) PYSIGNAL(xx)
    """
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
##        if signal != res and DEBUG_PRINT_UNDO and 0:
##            print "hack converted %r to %r" % (signal, res) # they all look ok
        return res
    pass

# ==

def _count(substring, signal):
    """
    return the number of times substring occurs in signal
    """
    return len(signal.split(substring)) - 1

def guess_signal_argcount(signal):
    """
    guess the number of arguments in a Qt signal string such as
    "func()" or "func(val)" or "func(val, val)"
    """
    assert signal and type(signal) == type("")
    commas = _count(',', signal)
    if commas:
        return commas + 1
    # if no commas, is it () or (word)?
    # a quick kluge to ignore whitespace:
    signal = ''.join(signal.split())
    if _count("()", signal):
        return 0
    else:
        return 1
    pass

def args_info(func1): #bruce 071004 revised implem and return value format
    """
    Given a function or method object, try to find out what argument lists
    it can accept (ignoring the issue of the names of arguments that could
    be passed either positionally or by name).
       Return value is a tuple (success, minargs, maxargs, any_kws_ok),
    where success is a boolean saying whether we succeeded in finding out anything for sure
    (if not, the other tuple elements are "loose guesses" or are None);
    minargs is the minimum number of positional args the function can be called with;
    maxargs is the maximum number of positional args the function can be called with
    (assuming no keyword arguments fill those positions);
    and any_kws_ok says whether the function can accept arbitrary keyword arguments
    due to use of **kws in its argument declaration.
    If we can't determine any of those values, they are None; as of 071004 this can only
    happen when success is True for maxargs (due to use of *args in the declaration).
    """
    DEFAULT_RETVAL = False, None, None, True
    if USE_GETARGSPEC:
        # try using inspect.getargspec.
        # TODO: there might be a smarter wrapper
        # for that function (which knows about bound methods specifically)
        # in some other introspection module.
        from utilities.debug import print_compact_traceback
        try:
            import inspect
            try:
                res = inspect.getargspec(func1)
            except TypeError:
                # failed for <built-in method setEnabled of QGroupBox object at 0x7e476f0>:
                # exceptions.TypeError: arg is not a Python function
                # (happens for close, quit, setEnabled)
                if DEBUG_USE_GETARGSPEC_TypeError:
                    print "USE_GETARGSPEC TypeError for %r: " % (func1,)
                return DEFAULT_RETVAL
            else:
                if DEBUG_GETARGSPEC:
                    print "inspect.getargspec(%r) = %r" % (func1, res)
                # now analyze the results to produce our return value
                args,  varargs, varkw, defaults = res
                    # Python 2.1 documentation:
                    # args is a list of the argument names (it may contain nested lists).
                    # varargs and varkw are the names of the * and  ** arguments or None.
                    # defaults is a tuple of default argument values or None if there are no default arguments;
                    # if this tuple has n elements, they correspond to  the last n elements listed in args.
                if args and args[0] == 'self':
                    # kluge: assume it's a bound method in this case
                    ### TODO: verify this by type check,
                    # or better, use type check to test this in the first place
                    args0 = args
                    args = args[1:]
                    if defaults is not None and len(defaults) == len(args0):
                        # a default value for self in a bound method would be too weird to believe
                        print "USE_GETARGSPEC sees default value for self in %r argspec %r" % (func1, res)
                        # but handle it anyway
                        defaults = defaults[1:]
                    if DEBUG_GETARGSPEC:
                        print "removed self, leaving %r" % ((args,  varargs, varkw, defaults),) # remove when works
                    pass
                else:
                    assert type(args) == type([])
                    # first arg is missing (no args) or is not 'self'
                    if DEBUG_GETARGSPEC:
                        print "USE_GETARGSPEC sees first arg not self:", args # other info was already printed

                # now use args, varargs, varkw, defaults to construct return values
                success = True
                maxargs = minargs = len(args)
                if defaults:
                    minargs -= len(defaults)
                if varargs:
                    maxargs = None # means infinity or "don't know" (infinity in this case)
                any_kws_ok = not not varkw
                return success, minargs, maxargs, any_kws_ok
        except:
            print_compact_traceback("USE_GETARGSPEC failed for %r: " % (func1,) )
        pass
    # if we didn't return something above, just return the stub value
    # which represents complete uncertainty
    return DEFAULT_RETVAL

# end
