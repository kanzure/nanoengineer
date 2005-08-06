# Copyright (c) 2005 Nanorex, Inc.  All rights reserved.
"""
changes.py

A fast general-purpose change-tracker, and related utilities.

[This module is owned by Bruce until further notice.]

$Id$

This will eventually be used to help with Undo, among other things.

Its initial use is to help fix up Part membership of Nodes after they move
(but as of 050803 I think it's not used for that except as stub code).

bruce 050803 new features to help with graphics updates when preferences are changed 

"""

__author__ = "Bruce"

import os, sys, time # needed?
from debug import print_compact_traceback, print_compact_stack, compact_stack
import env
from constants import noop
import platform

# == Usage tracking.

class OneTimeSubsList: #bruce 050804
    """This object corresponds to (one momentary value of) some variable or aspect whose uses can be tracked
    (causing a ref to this object to get added to a set of used things).
       What the value-user can do to this object, found in its list of things used during some computation,
    is to subscribe some function (eg an invalidator for the results of that computation,
     which might be another variable, or a side effect like the results of drawing something)
    to "the next change to this value", ie to the event of this value itself becoming invalid.
    That subscription will be fulfilled at most once, ASAP after the corresponding value is known to be invalid.
    Exceptions in fulfilling it might be debug-reported but will cause no harm to this object.
       The value-user can also remove that subscription before it gets fulfilled
    (or even after? not sure, esp re duplicate funcs provided).
       In fact, this object's implem seems general enough for any one-time-only subslist,
    even though this docstring is about the application to usage-tracking and next-change-subscription. ###e what to do about that?
       ###k Does it permit resubs while fulfilling them (as in changed_members)?? Is it reusable at all??
    """
    def __init__(self):
        self._subs = {}
            # map from id(func) to list of (zero or more identical elements) func (which are of course strongrefs to func).
            # (We need the dict for efficient removal, and multiple copies of func in case duplicate funcs are provided
            #  (which is quite possible), but that doesn't need to be optimized for, so using a list of copies seems simplest.
            #  Implem note if we ever do this in C: could replace id(func) with hash(id(func)), i.e. not distinguish between
            #  equal funcs and funcs with same hashcode.)
    def subscribe(self, func):
        try:
            subs = self._subs
        except AttributeError:
            # our event already occurred (as indicated by fulfill_all removing this attribute).
            # [not sure if this ever happens in initial uses of this class]
            # (note: if subscribe could come before __init__, e.g. due to some sort of bug
            #  in which this obj got unpickled, this could also happen.)
            if platform.atom_debug: #e remove if happens routinely
                print "atom_debug: fyi: %r's event already occurred, fulfilling new subs %r immediately" % (self, func)
            self._fulfill1(func)
        else:
            lis = subs.setdefault( id(func), [])
            lis.append(func)
        return #e return a unique "removal code" for this subs?? or None if we just fulfilled it now.
    def fulfill_all(self):
        """Fulfill all our subscriptions now (and arrange to immediately fulfill any subscriptions that come in later).
        You must only call this once.
        """
        subs = self._subs
        del self._subs # (this would expose the class's definition of _subs, if there is one; presently there's not)
            # Does this make it illegal to subscribe to this object ever again? No!
            # It causes such a subs to be immediately fulfilled.
        for sublis in subs.itervalues():
            for sub1 in sublis:
                # note: fulfilling at most one elt might be acceptable if we redefined API to permit that
                # (since all elts are identical),
                # but it wouldn't much simplify the code, since the list length can legally be zero.
                self._fulfill1(sub1)
            pass
        return
    def _fulfill1(self, sub1):
        # note: the only use of self is in the debug msg.
        try:
            sub1() #e would an arg of self be useful?
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: exception ignored by %r from %r: " % (self, sub1) )
        return        
    def remove_subs(self, func): # this might not ever be used
        """Make sure (one subscribed instance of) func will never be fulfilled.
        WARNING: calling this on a subs (a specific instance of func) that was already fulfilled is an UNDETECTED ERROR.
        But it's ok to subscribe the same func eg 5 times, let 2 of those be fulfilled, and remove the other 3.
        """
        # optimize by assuming it's there -- if not, various exceptions are possible.
        self._subs[id(func)].pop()
            # (this can create a 0-length list which remains in the dict. seems ok provided self is not recycled.)
        return
    def remove_all_instances(self, func):
        """#doc; legal even if no instances, but only if an instance once existed (but this might not be checked for).
        """
        try:
            del self._subs[id(func)]
        except KeyError:
            pass # not sure this ever happens, but it's legal (if we call this multiple times on one func)
        except AttributeError:
            if 0 and platform.atom_debug:
                print "atom_debug: fyi: %r's event already occurred, in remove_all_instances( %r)" % (self, func)
            pass # this happens routinely after fulfill_all removes self._subs,
                # since our recipient is too lazy to only remove its other subs when one gets fulfilled --
                # it just removes all the subs it had, including the one that got fulfilled.
        except:
            # this detected the following bug during development (since fixed):
            # bug: self._subs is None: exceptions.TypeError: object does not support item deletion
            print_compact_traceback("bug: self._subs is %r: " % (self._subs,) )
        return
    pass # end of class OneTimeSubsList

class SelfUsageTrackingMixin: #bruce 050804
    """You can mix this into classes which need to let all other code track uses and changes
    of their "main value" (what value that means is up to them).
    (If they need to permit tracking of more than one value or aspect they own,
     they should instead use one UsageTracker object for each trackable value, in the way described here.)
       To accomplish the tracking, their objects must notice all uses and changes of that main value,
    and call (respectively, for uses and changes):
    - self.track_use() to track that that value is being used [must be called on every use, not just first one after a change];
    - self.track_change() to tell everything which noticed that it used our prior value
      (and which then subscribed to this event) that our prior value is no longer current.
       Note: this needs to track not just changes, but invalidations, of our current value. ###e so rename it? not sure.
    WARNING: The way Formula uses track_change only works when it comes after new value is available,
    but when using it to report an invalidation, that's not possible!
    ####@@@@ this design flaw needs to be corrected somehow. See also comments near one of preferences.py's uses of track_change.
       If something is "killed" or in some other way becomes unusable, it only needs to call track_change
    if a use after that is theoretically possible (which is usually the case, since bugs in callers can cause that),
    and if a use after that would have a different effect because it had been killed.
    (I think it's always safe to call it then, and not even an anti-optimization, but I'm not 100% sure.)
    (Typically, other changes occur when something is killed which themselves call track_change(),
     so whether it's called directly doesn't matter anyway.)
    """
    def track_use(self):
        """#doc
        [some callers might inline this method]
        [must be called on every use, not just first one after a change,
         in case env.track points to different objects for different uses]
        """
        try:
            subslist = self.__subslist
        except AttributeError:
            # this is the only way self.__subslist gets created;
            # it means this is the first call of track_use ever, or since track_change was last called
            subslist = self.__subslist = OneTimeSubsList() # (more generally, some sort of unique name for self's current value era)
        # (Should we now return subslist.subscribe(func)? No -- that's what the value-user should do *after* subslist
        #  gets entered here into its list of used objs, and value-user later finds it there.)
        env.track( subslist)
            ###@@@ #e:
            # - is it right that the name of this function doesn't imply it's specific to usage-tracking?
            #   can it be used for tracking other things too?? [guess: no and no -- rename it ###@@@.]
            # - (Wouldn't it be faster to save self, not self.__subslist, and then at the end to create and use the subslist?
            #    Yes, but it would be wrong, since one self has several subslists in succession as its value changes!)
            # - Maybe some callers can inline this method using essentially only a line like this:
            #     env.used_value_sublists[id(subslist)] = subslist
        return
    def track_change(self): #e add args? e.g. "why" (for debugging), nature of change (for optims), etc...
        # ... or args about inval vs change-is-done (see comments in class's docstring)
        try:
            subslist = self.__subslist
        except AttributeError: # this is common
            return # optimization (there were no uses of the current value, or, they were already invalidated)
        del self.__subslist
        subslist.fulfill_all()
    pass # end of class SelfUsageTrackingMixin

class UsageTracker( SelfUsageTrackingMixin): #bruce 050804 #e rename?
    "Ownable version of that mixin class, for owners that have more than one aspect whose usage can be tracked."
    pass

# ==

class begin_end_matcher: #bruce 050804
    """Maintain a stack of objects (whose constructor is a parameter of this object)
    which are created/pushed and popped by calls of our begin/end methods, which must occur in
    properly nested matching pairs. Try to detect and handle the error of nonmatching begin/end calls.
    (This only works if the constructor promises to return unique objects, since we use their id()
    to detect matching.)
    """
    def __init__(self, constructor, stack_changed_func = None):
        """Constructor is given all args (including keyword args) to self.begin(),
        and from them should construct objects with begin(), end(), and error(text) methods
        which get stored on self.stack while they're active.
        Or constructor can be None, which means begin should always receive one arg, which is the object to use.
           Stack_changed_func (or noop if that is None or not supplied)
        is called (with arg self) when we're created and after every change to our stack.
        """
        self.constructor = constructor or (lambda arg: arg)
        self.stack_changed = stack_changed_func or noop
        self.stack = []
        self.stack_changed(self) # callers depend on this being called when we're first created
    def begin(self, *args, **kws):
        """Construct a new object using our constructor;
        activate it by calling its .begin() method [#k needed??];
        push it on self.stack (and inform observers that self.stack was modified);
        return a currently-unique match_checking_code which must be passed to the matching self.end() call.
        """
        newobj = self.constructor(*args, **kws) # exceptions in this mean no change to our stack, which is fine
        newobj.begin()
        self.stack.append(newobj)
        self.stack_changed(self)
        # for debugging, we could record compact_stack in newobj, and print that on error...
        # but newobj __init__ can do this if it wants to, without any help from this code.
        return id(newobj) # match_checking_code
    def end(self, match_checking_code):
        """This must be passed the return value from the matching self.begin() call.
        Verify begin/end matches, pop and deactivate (using .end()) the matching object, return it.
           Error handling:
           - Objects which had begin but no end recieve .error(errmsg_text) before their .end().
           - Ends with no matching begin (presumably a much rarer mistake -- only likely if some code
        with begin/end in a loop reuses a localvar holding a match_checking_code from an outer begin/end)
        just print a debug message and return None.
        """
        stack = self.stack
        if stack and id(stack[-1]) == match_checking_code:
            # usual case, no error, be fast
            doneobj = stack.pop()
            self.stack_changed(self)
            doneobj.end() # finalize doneobj
            return doneobj
        # some kind of error
        ids = map( id, stack )
        if match_checking_code in ids:
            # some subroutines did begin and no end, but the present end has a begin -- we can recover from this error
            doneobj = stack.pop()
            while id(doneobj) != match_checking_code:
                self.stack_changed(self) # needed here in case doneobj.end() looks at something this updates from self.stack
                doneobj.error("begin, with no matching end by the time some outer begin got its matching end")
                doneobj.end() # might be needed -- in fact, it might look at stack and send messages to its top
                doneobj = stack.pop()
            # now doneobj is correct
            self.stack_changed(self)
            doneobj.end()
            return doneobj
        # otherwise the error is that this end doesn't match any begin, so we can't safely pop anything from the stack
        print_compact_stack( "bug, ignored for now: end(%r) with no matching begin, in %r: " % (match_checking_code, self) )
        return None # might cause further errors as caller tries to use the returned object
    pass # end of class begin_end_matcher

# ==

def default_track(thing): #bruce 050804; see also the default definition of track in env module
    "Default implementation -- will be replaced at runtime whenever usage of certain things is being tracked."
##    if platform.atom_debug:
##        print "atom_debug: fyi (from changes module): something asked to be tracked, but nothing is tracking: ", thing
##        # if this happens and is not an error, then we'll zap the message.
    return

def _usage_tracker_stack_changed( usage_tracker ): #bruce 050804
    "[private] called when usage_tracker's begin/end stack is created, and after every time it changes"
    # getting usage_tracker arg is necessary (and makes better sense anyway),
    # since when we're first called, the global usage_tracker is not yet defined
    # (since its rhs, in the assignment below, is still being evaluated).
    stack = usage_tracker.stack
    if stack:
        env.track = stack[-1].track
    else:
        env.track = default_track
    return

usage_tracker = begin_end_matcher( None, _usage_tracker_stack_changed )
    # constructor None means obj must be passed to each begin

class SubUsageTrackingMixin: #bruce 050804
    """###doc - for doing usagetracking in whatever code we call when we remake a value, and handling results of that
    """
    def begin_tracking_usage(self): #e there's a docstring for this in an outtakes file, if one is needed
        obj = usage_tracker_obj()
        match_checking_code = usage_tracker.begin( obj)
            # don't store match_checking_code in self -- that would defeat the error-checking
            # for bugs in how self's other code matches up these begin and end methods
        return match_checking_code
    def end_tracking_usage(self, match_checking_code, invalidator):
        obj = usage_tracker.end( match_checking_code)
        obj.standard_end( invalidator)
            ##e or we could pass our own invalidator which wraps that one,
            # so it can destroy us, and/or do more invals, like one inside the other mixin class if that exists
        return
    pass

class usage_tracker_obj: #bruce 050804
    """###doc [private to SubUsageTrackingMixin, mostly]
    """
    def begin(self):
        self.data = {}
    def track(self, subslist): 
        """This gets called (via env.track) by everything that wants to record one use of its value.
        The argument subslist is a subscription-list object which permits subscribing to future changes
        (or invalidations) to the value whose use now is being tracked.
        [This method gets installed as env.track, which is called often, so it needs to be fast.]
        """
        # For now, just store subslist, at most one copy. Later we'll subscribe just once to each one stored.
        self.data[id(subslist)] = subslist
    def error(self, text):
        print "bug: error in usage_tracker_obj:", text #e stub
    def end(self):
        pass # let the caller think about self.data.values() (eg filter or compress them) before subscribing to them
    def standard_end(self, invalidator):
        "some callers will find this useful to call, shortly after self.end gets called"
        self.invalidator = invalidator # this will be called only by our own standard_inval
        whatweused = self.whatweused = self.data.values() # this list is saved for use in other methods called later
        self.last_sub_invalidator = inval = self.standard_inval # make sure to save the exact copy of this object which we use now
        for subslist in whatweused:
            subslist.subscribe( inval ) #e could save retvals to help with unsub, if we wanted
        self.data = 222 # make further calls of self.track() illegal [#e do this in self.end()??]
        return
    def standard_inval(self):
        # this needs to remove every subs except the one which is being fulfilled by calling it.
        # But it doesn't know which subs that is! So it has to remove them all, even that one,
        # so it has to call a remove method which is ok to call even for a subs that was already fulfilled.
        # The only way for that method to always work ok is for its semantics to be that it removes all current subs (0 or more)
        # which have the same fulfillment function. That is only ok since our subs (self.standard_inval)
        # is unique to this object, and this object makes sure to give only one copy of it to one thing.
        inval = self.last_sub_invalidator
        del self.last_sub_invalidator
        whatweused = self.whatweused
        self.whatweused = 444 # not a sequence
        for subslist in whatweused:
            ## can't use subslist.remove( self.last_sub_invalidator ), as explained above
            subslist.remove_all_instances( inval )
        invalidator = self.invalidator
        del self.invalidator
        invalidator()
        return
    pass # end of class usage_tracker_obj

# ==

class Formula( SubUsageTrackingMixin): #bruce 050805
    """
    """
    killed = False
    def __init__( self, value_lambda, action = None, not_when_value_same = False ):
        """Create a formula which tracks changes to the value of value_lambda (by tracking what's used to recompute it),
        and when created and after each change occurs, calls action with the new value_lambda return value as sole argument.
           This only works if whatever value_lambda uses, which might change and whose changes should trigger recomputation,
        uses SelfUsageTrackingMixin or the equivalent to track its usage and changes, AND (not always true!) if those things
        only report track_change after the new value is available, not just when the old value is known to be invalid.
        [About that issue, see comments in docstring of class which defines track_change. ####@@@@]
           If action is not supplied, it's a noop.
        Whether or not it's supplied, it can be changed later using self.set_action.
           Note that anything whose usage is tracked by calling value_lambda can cause action to be called,
        even if that thing does not contribute to the return value from value_lambda.
        If this bothers you, consider passing not_when_value_same = True, so that repeated calls
        only occur when the return value is not equal to what it was before.
        (The old return value is not even kept in this object unless not_when_value_same is true.)
        """
        self.value_lambda = value_lambda
        self.set_action( action)
        self.not_when_value_same = not_when_value_same
        self.first_time = True # prevents looking for self.oldval
        self.recompute()
        return
    def destroy(self):
        self.killed = True
        self.value_lambda = self.action = self.oldval = None
        #e anything else?
        return
    def set_action(self, action):
        if action is None:
            action = noop
        self.action = action
    def recompute(self):
        error = False
        match_checking_code = self.begin_tracking_usage()
        try:
            newval = self.value_lambda()
        except:
            error = True
            newval = None
            if platform.atom_debug: #e better to let a debug option control this, and give the place to put msgs
                print_compact_traceback( "atom_debug: exception in value_lambda %r: " % self.value_lambda )
        self.end_tracking_usage( match_checking_code, self.need_to_recompute )
        if not error and (not self.not_when_value_same or self.first_time or self.oldval != newval):
            # do the action
            try:
                self.action( newval)
            except:
                error = True
                if platform.atom_debug:
                    print_compact_traceback( "atom_debug: exception in formula action %r: " % self.action )
        self.first_time = False
        if not error and self.not_when_value_same:
            # save self.oldval for the comparison we might need to do next time
            self.oldval = newval
        if error:
            self.destroy()
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: destroyed %r due to error: " % self )
        #e any more??
        return
    def need_to_recompute(self):
        if not self.killed:
            self.recompute()
        return
    pass # end of class Formula

# ===
# ***
# ===

# As of 050803, the facilities after this point are used only as stubs,
# though some might be used soon, e.g. as part of recent files menu,
# custom jigs, Undo, or other things.

class pairmatcher:
    """Keep two forever-growing lists,
    and call a specified function on each pair of items in these lists,
    in a deterministic order,
    as this becomes possible due to the lists growing.
       Normally that specified function should return None;
    otherwise it should return special codes which
    control this object's behavior (see the code for details).
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

# A place for objects of one kind to register themselves under some name,
# so that objects of another kind can meet all of them using a pairmatcher (#doc better?)

def postinit_func( d1, d2):
    """after d1 is inited, tell it about d2.
    (This is meant to be called for every d1 of one kind,
     and every d2 of another kind,
     registered below under the same name.)
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
