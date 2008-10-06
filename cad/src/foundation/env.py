# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
env.py - for global variables and functions treated as "part of the environment".

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details. 

This module is for various global or "dynamic" variables,
which can be considered to be part of the environment of the code
that asks for them (thus the module name "env"). This is for variables
which are used by lots of code, but which would be inconvenient to pass
as arguments (since many routines would need to pass these through
without using them), and which some code might want to change dynamically
to provide a modified environment for some of the code it calls.

(Many of these variables will need to be thread-specific if we ever have threads.)

Also, certain basic routines for using/allocating some of these global variables.


Usage:

'import foundation.env as env'

   ... use env.xxx as needed ...
   # Don't say "from env import xxx" since env.xxx might be reassigned dynamically.
   # Variables that never change (and are importable when the program is starting up)
   # can be put into constants.py


Purpose and future plans:

Soon we should move some more variables here from platform, assy, and/or win.

We might also put some "dynamic variables" here, like the current Part --
this is not yet decided.

Generators used to allocate things also might belong here, whether or not
we have global dicts of allocated things. (E.g. the one for atom keys.)

One test of whether something might belong here is whether there will always be at most one
of them per process (or per active thread), even when we support multiple open files,
multiple main windows, multiple glpanes and model trees, etc.


History:

bruce 050610 made this module (since we've needed it for awhile), under the name "globals.py"
(since "global" is a Python keyword).

bruce 050627 renamed this module to "env.py", since "globals" is a Python builtin function.

bruce 050803 new features to help with graphics updates when preferences are changed

bruce 050913 converted most or all remaining uses of win.history to env.history,
and officially deprecated win.history.

bruce 080220 split glselect_name_dict.py out of env.py so we can make it per-assy.
"""

_mainWindow = None


# Initialize the 'prefs' value. It is redefined in preference.py
# see preferences.init_prefs_table for details. 
# Initializing it here, should fix this error that pylint output shows in  
# a number of files -- " 'Module 'env' has no 'prefs' member"  
prefs = None

def setMainWindow(window):
    """
    Set the value which will be returned by env.mainwindow().  Called
    by MWsemantics on creation of the (currently one and only) main
    window.
    """
    global _mainWindow
    assert _mainWindow is None, "can only setMainWindow once"
    assert not window is None
    _mainWindow = window

def mainwindow(): #bruce 051209
    """
    Return the main window object (since there is exactly one, and it
    contains some global variables).  Fails if called before main
    window is inited (and it and assy point to each other).
    """

    # sanity check, and makes sure it's not too early for these things
    # to have been set up
    assert not _mainWindow is None, "setMainWindow not called yet"
    assert _mainWindow.assy.w is _mainWindow 

    return _mainWindow

mainWindow = mainwindow # alias which should become the new name of that function [bruce 080605]

def debug(): #bruce 060222
    """
    Should debug checks be run, and debug messages be printed, and debug options offered in menus?
    [This just returns the current value of debug_flags.atom_debug, which is this code's conventional flag
     for "general debugging messages and checks". Someday we might move that flag itself into env,
     but that's harder since we'd have to edit lots of code that looks for it in platform,
     or synchronize changes to two flags.]
    """
    from utilities import debug_flags # don't do this at toplevel in this module, in case we don't want it imported so early
    return debug_flags.atom_debug

# ==

try:
    _things_seen_before # don't reset this on reload (not important yet, since env.py doesn't support reload) 
except:
    _things_seen_before = {}

def seen_before(thing): #bruce 060317
    """
    Return True if and only if thing has never been seen before (as an argument passed to this function).
    Useful for helping callers do things only once per session.
    """
    res = _things_seen_before.get(thing, False)
    _things_seen_before[thing] = True
    return res

# ==

try:
    _once_per_event_memo
except:
    _once_per_event_memo = {}

def once_per_event(*args, **kws): #bruce 060720 ###@@@ should use this in debug's reload function
    """
    Return True only once per user event (actually, per glpane redraw),
    for the given exact combination of args and keyword args.
    All arg values must be hashable as dict keys.
    """
    assert args or kws, "some args or kws are required, otherwise the result would be meaninglessly global"
    if kws:
        items = kws.items()
        items.sort()
        key1 = (args, tuple(items))
    else:
        # optim the usual case
        # (it should be ok that this can, in theory, overlap the kws case,
        #  since callers ought to be each passing distinct strings anyway)
        key1 = args
    # this version (untested) would work, but might accumulate so much memo data as to be a memory leak
    ## key2 = ("once_per_event", redraw_counter, key1)
    ## return not seen_before( key2)
    # so use this version instead:
    old = _once_per_event_memo.get(key1, -1)
    if redraw_counter == old:
        return False # fast case
    else:
        _once_per_event_memo[key1] = redraw_counter
        return True
    pass

# ==

# This module defines stub functions which are replaced with different implementations
# by the changes module when it's imported.
# So this module should not import the changes module, directly or indirectly.
# But in case it does, by accident or if in future it needs to,
# we'll define those stub functions as early as possible.
# (One motivation for this (not yet made use of as of 050908)
#  is to enable stripped-down code to call these functions
#  even if the functionality of the changes module is never needed.
#  The immediate motivation is to allow them to be called arbitrarily early during init.)

def track(thing): #bruce 050804
    """
    Default implementation -- will be replaced at runtime
    as soon as changes.py module is imported (if it ever is)
    """
    from utilities import debug_flags
    if debug_flags.atom_debug:
        print "atom_debug: fyi (from env module): something asked to be tracked, but nothing is tracking: ", thing
        # if this happens and is not an error, then we'll zap the message.
    return

#bruce 050908 stubs for Undo  ####@@@@

def begin_op(*args):
    """
    Default implementation -- will be replaced at runtime
    as soon as changes.py module is imported (if it ever is)
    """
    return "fake begin" #k needed?

def end_op(*args):
    """
    Default implementation -- will be replaced at runtime
    as soon as changes.py module is imported (if it ever is)
    """
    pass

in_op = begin_op
after_op = end_op
begin_recursive_event_processing = begin_op
end_recursive_event_processing = end_op

command_segment_subscribers = [] #bruce 060127 for Undo

_in_event_loop = True #bruce 060127

# end of stubs to be replaced by changes module

def call_qApp_processEvents(*args): #bruce 050908
    """
    No other code should directly call qApp.processEvents --
    always call it via this function.
    """
    from PyQt4.Qt import qApp #k ??
    mc = begin_recursive_event_processing()
    try:
        res = qApp.processEvents(*args)
        # Qt doc says: Processes pending events, for 3 seconds or until there
        # are no more events to process, whichever is shorter.
        # (Or it can take one arg, int maxtime (in milliseconds), to change the timing.)
    finally:
        end_recursive_event_processing(mc)
    return res
    
# ==

class pre_init_fake_history_widget: #bruce 050901 moved this here from MWsemantics.py
    too_early = 1
        # defined so insiders can detect that it's too early (using hasattr on history)
        # and not call us at all (though it'd be better for them to check something else,
        # like win.initialised, and make sure messages sent to this object get saved up
        # and printed into the widget once it exists) [bruce 050913 revised comment]
    def message(self, msg, **options):
        """
        This exists to handle messages sent to win.history [deprecated] or env.history during
        win.__init__, before the history widget has been created!
        Someday it might save them up and print them when that becomes possible.
        """
##        from utilities import debug_flags
##        if debug_flags.atom_debug:
        # bruce 071018 print this always, and clarify the text:
        print "fyi: this history message was produced too early to show up in the History Widget:"
        print msg
        # REVIEW: should we use print_compact_stack instead, if atom_debug is set?
        return
    redmsg = orangemsg = greenmsg = message #bruce 080220
    pass

history = pre_init_fake_history_widget() # this will be changed by MWsemantics.__init__ [bruce 050727]

last_history_serno = 0 #bruce 060301 (maintained by HistoryWidget, to be looked at by Undo checkpoints)

redraw_counter = 0 #bruce 050825

# ==

_change_checkpoint_counter = 0 #bruce 060123 for Undo and other uses
    # almost any change-counter record can work (in part) by incrementing this if necessary to make it odd,
    # then saving its value on changed things, if all observing-code for it increments it if necessary to make it even;
    # this way it's easy to compare any change (odd saved value)
    # with anything that serves as a state-checkpoint (even saved value),
    # but we can still optimize saving this on all parents/containers of an object in low-level change-tracking code,
    # by stopping the ascent from changed child to changed parent as soon as it would store the same value of this on the parent.

def change_counter_checkpoint():
    """
    Call this to get a value to save in state-snapshots or the like,
    for comparison (using >, not ==) with stored values.
    """
    global _change_checkpoint_counter
    if _change_checkpoint_counter & 1:
        _change_checkpoint_counter += 1 # make it even, when observed
    return _change_checkpoint_counter

def change_counter_for_changed_objects():
    """
    Call this to get a value to store on changed objects and all their
    containers; see comment for important optimization.
    """
    global _change_checkpoint_counter
    if _change_checkpoint_counter & 1 == 0:
        _change_checkpoint_counter += 1 # make it odd, when recording a change
    return _change_checkpoint_counter

# ==

# temporary compatibility functions

# [bruce 080220 split out the originals, and will remove these soon,
#  replacing them with per-assy instances of glselect_name_dict;
#  as an intermediate state, this one is shared by each assy,
#  so code can be incrementally switched to access it through assy
#  or glpane; when all code does that, these will be removed
#  and each assy will make its own glselect_name_dict.]
# [bruce 080917: mostly completing this, but see comment in
#  Assembly._init_glselect_name_dict for what remains.]

from graphics.drawing.glselect_name_dict import glselect_name_dict

_shared_glselect_name_dict = glselect_name_dict() # still used in class Assembly

##obj_with_glselect_name = _shared_glselect_name_dict.obj_with_glselect_name
##    # client code should be revised to use assy.object_for_glselect_name
##    # in place of env.obj_with_glselect_name.get
##
##alloc_my_glselect_name = _shared_glselect_name_dict.alloc_my_glselect_name
##
##dealloc_my_glselect_name = _shared_glselect_name_dict.dealloc_my_glselect_name

# ==

# support for post_event_updater functions of various kinds

# Note: we separate the kinds because we need to do them in a certain order
# (model updaters before UI updaters), and because future refactoring
# is likely to move responsibility for maintaining the list of updaters,
# and for calling them, to different modules or objects, based on their kind.

_post_event_model_updaters = []

def register_post_event_model_updater(function):
    """
    Add a function to the list of model updaters called whenever
    do_post_event_updates is called.

    The function should take a single boolean argument,
    warn_if_needed.  If the function is called with warn_if_needed
    True, and the function determines that it needs to take any
    action, the function may issue a warning.  This helps catch code which
    failed to call do_post_event_updates when it needed to.

    The function's return value is ignored.

    WARNING: the functions are called in the order added; when order matters,
    the application initialization code needs to make sure they're added
    in the right order.

    USAGE NOTE: there is intentionally no way to remove a function from this
    list. Application layers should add single functions to this list in the
    right order at startup time, and those should maintain their own lists
    of registrants if dynamic add/remove is needed within those layers.

    See also: register_post_event_ui_updater.
    """
    assert not function in _post_event_model_updaters
        # Rationale: since order matters, permitting transparent multiple inits
        # would be inviting bugs. If we ever need to support reload for
        # developers, we should let each added function handle that internally,
        # or provide a way of clearing the list or replacing a function in-place.
        #  (Note: it's possible in theory that one update function would need
        # to be called in two places within the list. If that ever happens,
        # remove this assert, or work around it by using a wrapper function.)
    _post_event_model_updaters.append( function)
    return

_post_event_ui_updaters = []

def register_post_event_ui_updater(function):
    """
    Add a function to the list of ui updaters called whenever
    do_post_event_updates is called. All ui updaters are called
    (in the order of registration) after all model updaters.

    The function should take no arguments. Its return value is ignored.

    WARNING & USAGE NOTE: same as for register_post_event_model_updater,
    though ui updaters are much less likely than model updaters
    to have order dependencies within themselves.
    """
    assert not function in _post_event_ui_updaters
    _post_event_ui_updaters.append( function)
    return


def do_post_event_updates( warn_if_needed = False ):
    """
    [public function]
       This should be called at the end of every user event which changes
    model or selection state. WARNING: In present code (070925), it is very likely
    not called that often, but this is mitigated by the precautionary calls mentioned
    below.
       This can also be called at the beginning of user events, such as redraws or saves,
    which want to protect themselves from event-processors which should have called this
    at the end, but forgot to. Those callers should pass warn_if_needed = True, to permit
    a debug-only warning to be emitted if the call was necessary (but there is no guarantee
    that such a warning is always emitted). (The updaters registered to be called by this
    function should be designed to be fast when called more times than necessary.)

    @see: _master_model_updater
    """
    # Note: exceptions in one of these updaters can prevent redrawing
    # for the rest of the session, so better protection is needed,
    # but it doesn't fully work if added right here (at least for an AttributeError
    # in the dna sequence editor in Edit Dna Strand Properties).
    # It would be good to add it at a higher level at some point.
    #
    # Details: catching exceptions here and not propogating them upwards
    # may make some bugs worse by turning them into infinite recursions
    # (for reasons not yet analyzed). Or it may be that those bugs were
    # *already* infinite recursions, since at least one such case is known
    # (though it's not testable in current code, since Ninad fixed it thismorning).
    # To reproduce that bug, this might work (untested):
    # - remove def setComplementSequence from DnaSequenceEditor
    #   (what was tested was having a ProteinSequenceEditor erroneously residing
    #    in the private win attr meant for the DnaSequenceEditor)
    # - edit a dna strand using the PM button of that name in Build DNA.
    # 
    # [bruce 080725 comment]

    # note: importing from utilities.debug here adds an import cycle.
    # This is not needed now (see above comment), but if ever needed,
    # it could be fixed by moving this and nearby functions into a new module.
    # [bruce 080725 comment]

    # do all model updaters before any ui updaters
    for function in _post_event_model_updaters:
        (function)(warn_if_needed)
    for function in _post_event_ui_updaters:
        (function)()

    # make sure any change_counter values, saved by those updaters,
    # will not be seen again if subsequent real changes occur
    # [bruce 080805; should make model_change_indicator more useful
    #  by making it change for every drag event during a drag
    #  and not depend on undo checkpointing, but needs testing for
    #  unanticipated bugs or performance impact]
    change_counter_checkpoint()
    
    return

# ==

def node_departing_assy(node, assy): #bruce 060315 for Undo
    """
    If assy is an assembly, warn it that node (with all its child atoms)
    is leaving it.
    """
    try:
        um = assy.undo_manager
    except AttributeError:
        # for assy is None or a certain string constant
        assert assy is None or type(assy) == type("") and "assembly" in assy # could be more specific
        return
    if um is not None:
        um.node_departing_assy(node, assy)
    return

# end
