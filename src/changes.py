# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
changes.py

A fast general-purpose change-tracker, and related utilities.

$Id$

This will eventually be used to help with Undo, among other things.

Its initial use is to help fix up Part membership of Nodes after they move.
[As of 050504 these are used only as stubs, I think, but later they'll be
 used in an essential way to help with Undo, and maybe with other things,
 so I'll leave them around for now.]

[This module is owned by Bruce until further notice.]

#doc
"""

__author__ = "Bruce"

import os, sys, time # needed?
from debug import print_compact_traceback, print_compact_stack

# ==

class pairmatcher:
    """Keep two forever-growing lists,
    and call a specified function on each pair of items in these lists,
    in a deterministic order,
    as this becomes possible due to the lists growing.
    Normally this function should return None;
    otherwise it should return special codes which
    control our behavior (see the code for details).
    """
    def __init__(self, func, debug_name = "?"):
        self.d1s = []
        self.d2s = []
        self.func = func #e will this func ever need to be changed, after we're made?
        self.debug_name = debug_name
    def another_dim2(self, d2):
        for d1 in self.d1s:
            self.doit(d1,d2) # doit for existing d1s
        self.d2s.append(d2) # and for future d1s
    def another_dim1(self, d1):
        for d2 in self.d2s:
            self.doit(d1,d2) # doit for existing d2s
        self.d1s.append(d1) # and for future d2s
    def doit(self, d1, d2):
        try:
            retcode = self.func(d1,d2)
            if retcode:
                if retcode == "remove d1":
                    # note: we might or might not be iterating over d1s right now!
                    self.d1s = list(self.d1s) # in case we are, modify a fresh copy
                    self.d1s.remove(d1)
                elif retcode == "remove d2":
                    self.d2s = list(self.d2s)
                    self.d2s.remove(d2)
                else:
                    print_compact_stack( "bug (ignored): unrecognized return code %r in pairmatcher %r: " % \
                                         (retcode, self.debug_name))
            #e any other use for retval??
        except:
            print_compact_traceback( "exception in pairmatcher %r ignored: " % self.debug_name)
        return
    pass

class MakerDict:
    "A read-only dict with a function for constructing missing elements"
    def __init__( self, func):
        self.data = {}
        self.func = func
    def __getitem__(self, key): # (no need for __setitem__ or other dict methods)
        try:
            return self.data[key]
        except KeyError:
            self.data[key] = self.func(key)
            return self.data[key]
    pass

# A place for objects of one kind of register themselves under some name,
# so that objects of another kind can meet all of them using a pairmatcher (#doc better?)

def postinit_func( d1, d2):
    """after d1 is inited, tell it about d2
    (meant to be called for every d1 of one kind,
     and every d2 of another kind,
     registered below under the same name)
    """
    try:
        d1.postinit_item(d2)
    except:
        # blame d1
        print_compact_traceback( "exception in d1.postinit_item(d2) ignored; removing d1: ") #e objnames? safe_repr(obj)?
        return "remove d1" # special code recognized by the pairmatcher

postinit_pairmatchers = MakerDict( lambda name: pairmatcher( postinit_func, debug_name = name) )

# the public functions:

# (for main window Jig menu items we'll use the typename "Jigs menu items" since maybe other things will have Jigs menus)

def register_postinit_object( typename, object):
    """Cause object to receive the method-call object.postinit_item(item)
    for every postinit item registered under the same typename,
    in the order of their registration,
    whether item is already registered or will be registered in the future.
    """
    pairmatcher = postinit_pairmatchers[ typename]
    pairmatcher.another_dim1( object)

def register_postinit_item( typename, item):
    """Cause every object registered with register_postinit_object
    under the same typename (whether registered already or in the future,
    and in their order of registration)
    to receive the method call object.postinit_item(item) for this item.
    """
    pairmatcher = postinit_pairmatchers[ typename]
    pairmatcher.another_dim2( item)    

# ==

_keep_these_forever = {}

def keep_forever(thing):
    "a place to put stuff if you need to make sure it's never deallocated by Python"
    _keep_these_forever[id(thing)] = thing

# ==

# Objects to record changes as they're reported, fairly efficiently.

class changed_aspect_tracker:
    """Support one changeable aspect of one set of objects of one type.
    Help those objects record which of them changed, in this aspect,
    since the last "update", or since any specific prior update.
    [Right now it only records the set of changed objects since an update.
     It might do more in the future, e.g. help maintain
     a stack of nested change-records, or propogate change-consequences.]
    """
    def __init__(self, aspect_name = "??", debug_print = False):
        """#doc ...
        Notes:
        - self.changedobjs is a public attribute, but use of
        self.changed_objects() is preferred when it's sufficient.
        - aspect_name, if supplied, should be a nonempty string
        (useable as the end of a python identifier)
        which names the aspect of objects whose changes we help track.
        This might be an attribute name, but is often an informal name
        for an otherwise unnamed aspect of these objects.
        Note that the default value is not usable in a python identifier.
        (Presently [050303], this is only used for debugging, so it doesn't
         yet matter whether it can be used in an identifier name.)
        - If an object has a "change method" used to tell us that a change just occurred
        to an aspect X of that object, that method is conventionally named
        "changed_X". This is purely a convention; the client code is responsible
        for defining that method and having it call this object's record method.
        """
        self.aspect_name = aspect_name # for debug messages only, i think
        self.debug_print = debug_print # flag
        self.changedobjs = {}
        return
    def record(self, obj): # used to be called record_obj_changed
        """Helper function for conventional changed_X methods:
        record that obj changed, wrt our aspect;
        ok if this runs more than once for one obj.
           For now, this doesn't record any inferred changes that are a
        consequence of this one; that can be done when the set of all changes
        to this aspect is analyzed. It would be easy to add "realtime inferred
        change recording" if that was desired, though. #e
        """
        if self.debug_print:
            print "%r.record(%r)" % (self,obj)
        # record the fact of the change (but not its "value" or "diff" --
        # the client code can do that separately if it wants to)
        self.changedobjs[ id(obj) ] = obj
            # This is a strongref, so it keeps obj alive until changes are
            # next processed; that's good. It also means it's safe to use the
            # Python built-in id() as a key, even though the same id might be
            # reused for another object after its first object dies.
        return
    def __repr__(self):
        return "<%s for %r, %d changed objs>" % (
            self.__class__.__name__,
            self.aspect_name,
            len(self.changedobjs)
        )
    def changed_objects(self):
        return self.changedobjs.values()
    def reset_changes(self):
        """Call this after you're done contemplating one round of changes,
        as stored in self.changedobjs, and want to clear it and start another
        cycle of recording.
        """
        self.changedobjs.clear()
            # (this is where finished objs die from lack of references)
        return
    def grab_and_reset_changed_objects(self): #e the name 'pop' is misleading if self is stacked
        objs = self.changed_objects()
        self.reset_changes()
        return objs
    ###e more methods, to help analyze the changes, or save the old ones too??
    pass # end of class changed_aspect_tracker; used to be called changeable_aspect


# == an object to hold all the changed_aspect_trackers of interest

# typical client code:
##from changes import changed # not yet set up for runtime reload during debugging
##... changed.dads.record(child)
##... changed.members.record(parent)

class _global_changes: pass

changed = _global_changes()

changed.dads = changed_aspect_tracker("dads")
changed.members = changed_aspect_tracker("members")

#e someday we might let these change_trackers get pushed and popped,
# either individually or as a set. This is not yet needed.

# ==

# code for fixing up parts from changed.dads... doesn't belong in this file.

# ==

###e guess: these will change into more kinds of begin/end, so subcommands work on same stack

# maybe: superclass for doing the handler stacking, and talking to changed_aspect_tracker stacks;
# subclasses for specific kinds of state to worry about and kinds of change-events
# to package it all into (undoable, what invariants are maintained, etc; relates to what
# objs changed, but even more to what *kind* of objs changed and how this code thinks of them.)
#  so for a user event, unlike others, we make a whole undoable, print history, update screen, etc.
# but for smaller pieces of commands (like elements of a script) we'd still record changes of
# each one, at least sometimes. And for invariant-maintenance, we'd lock objs, and fix them up
# when we unlock, based on recorded changes (e.g. for commit to a database? not sure what in nE-1
# might need this, but maybe consistency of chunk state, as we rotate, might need it....)
# ... eventually we'll build user events into bigger things (drags, undoables-as-a-unit),
# and divide them into smaller things (individual debugger-visible events, incl script commands),
# but we don't need any of that for immediate purposes. Invariants need maintenance more often
# but not in a nested way -- though nesting helps you not forgot to fix them up when you're done.
# So let's have begin/end for internal commands, and have end fix invariants, and have begin/end
# for user events too, and some other scheme to help build drags and undoables from those.
# I wonder if begin/end have the class (user event or not) as a *parameter*.... 

class event_handler:
    def __init__( self, whats_running, prior_handler):
        self.whats_running = whats_running
        self.prior_handler = prior_handler
        self.begin() #e unless optional arg says to defer this so can be done separately
    def begin(self):
        pass
    def end(self):
        return self.prior_handler
    pass

handler = None # dynamic variable -- current handler [not sure if public (so anyone can send it tracking records) or private]

def begin_event_handler( whats_running = None):
    """Start tracking everything needed when the UI handles one user-event.
    whats_running is presently an optional command-name for debugging or messages;
    someday it might be an object which is overseeing one run of a high-level command
    which is the command which user event was interpreted as needing to do.
       Return value MUST be passed to end_event_handler at the end of the user-event
    (or perhaps in another user event, as needed for mouse-drags -- this is not yet decided).
       Present stub callers do their own updates after end_event_handler returns,
    but the future plan is that end_event_handler itself will do all needed updates,
    as well as printing high-level summaries of changes to the history, etc.
    """
    global handler
    #k handler should normally be None now... ##k
    handler = event_handler( whats_running, handler)
    return handler

def end_event_handler(eh):
    global handler
    while handler is not None and handler is not eh: #bruce 050516 'is not'
        handler = handler.end_was_forgotten()
    if handler:
        handler = handler.end()
    else:
        print_compact_stack("error: end_event_handler finds no corresponding begin: ")
    return

# end
