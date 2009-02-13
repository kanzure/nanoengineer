# Copyright 2005-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
changes.py - utilities for tracking changes, usage, nested events, etc.

@author: Bruce
@version: $Id$
@copyright: 2005-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

original features were stubs and have mostly been removed.

bruce 050803 new features to help with graphics updates when
preferences are changed.

bruce 061022 soon some of this will be used in the new exprs module.
Later it will need optimization for that use.

...

bruce 071106 split changedicts.py out of changes.py

"""

from utilities.debug import print_compact_traceback, print_compact_stack
import foundation.env as env
from utilities.constants import noop
from utilities import debug_flags
from utilities.Comparison import same_vals #bruce 060306

# == Usage tracking.

_print_all_subs = False # can be set to True by debuggers or around bits of code being debugged

class OneTimeSubsList: #bruce 050804; as of 061022, looks ok for use in new exprs module (and being used there); doc revised 061119
    """
    This object corresponds to (one momentary value of) some variable or aspect whose uses (as inputs to
    other computations) can be tracked (causing a ref to this object to get added to a set of used things).
       When the user of the value corresponding to this object finds this object in the list of all such things
    it used during some computation, it can subscribe some function (eg an invalidator for the result of that
    computation, which (result) might be another variable, or a side effect like the effect of drawing something)
    to the event of that value becoming invalid. [See SubUsageTrackingMixin and usage_tracker_obj for how this is done.]
       That subscription will be fulfilled (by self) at most once, ASAP after the corresponding value is known to be invalid.
    Exceptions in fulfilling it might be debug-reported but will cause no harm to this object (since it's important
    that they don't prevent this object from fulfilling its other subscriptions).
       The value-user can also remove that subscription before it gets fulfilled
    (or even after? not sure, esp re duplicate funcs provided).
       Note: this object's implem seems general enough for any one-time-only subslist,
    even though this docstring is only about its application to usage-tracking and inval-subscription.
    [###e what to do about that? Is it really reusable??]
    [###k Does it permit resubs while fulfilling them (as in changed_members)??]
    [Does SelfUsageTrackingMixin make a new one each time it fulfills old one? Yes [verified 061119].] 
    """
    def __init__(self, debug_name = None):
        self.debug_name = debug_name #061118
        self._subs = {}
            # map from id(func) to list of (zero or more identical elements) func (which are of course strongrefs to func).
            # (We need the dict for efficient removal, and multiple copies of func in case duplicate funcs are provided
            #  (which is quite possible), but that doesn't need to be optimized for, so using a list of copies seems simplest.
            #  Implem note if we ever do this in C: could replace id(func) with hash(id(func)), i.e. not distinguish between
            #  equal funcs and funcs with same hashcode.)
    def __repr__(self): #061118
        return "<%s%s at %#x>" % (self.__class__.__name__, self.debug_name and ("(%s)" % self.debug_name) or '', id(self))
    def subscribe(self, func):
        try:
            subs = self._subs
        except AttributeError:
            # our event already occurred (as indicated by fulfill_all removing this attribute).
            # [not sure if this ever happens in initial uses of this class]
            # (note: if subscribe could come before __init__, e.g. due to some sort of bug
            #  in which this obj got unpickled, this could also happen.)
            if debug_flags.atom_debug:
                #e Remove this debug print if this non-error happens routinely (and turns out not to reveal a bug).
                # It never happened enough to notice until circa 061118 in exprs module; I don't yet know why it happens there,
                # but it started after an LvalUnset exception was added and some exception-ignorers were changed to pass that on;
                # it is also associated (but not always) with the same invals happening twice.
                print_compact_stack( "atom_debug: fyi: %r's event already occurred, fulfilling new subs %r immediately: " % (self, func))
            self._fulfill1(func)
        else:
            lis = subs.setdefault( id(func), [])
            lis.append(func)
        return #e return a unique "removal code" for this subs?? or None if we just fulfilled it now.
    def fulfill_all(self, debug = False):
        """
        Fulfill all our subscriptions now (and arrange to immediately
        fulfill any subscriptions that come in later).
        You must only call this once.
        """
        subs = self._subs
        del self._subs # (this would expose the class's definition of _subs, if there is one; presently there's not)
            # Does this make it illegal to subscribe to this object ever again? No!
            # It causes such a subs to be immediately fulfilled.
        for sublis in subs.values(): #bruce 060405 precaution: itervalues -> values (didn't analyze whether needed)
            for sub1 in sublis:
                # note: fulfilling at most one elt might be acceptable if we redefined API to permit that
                # (since all elts are identical),
                # but it wouldn't much simplify the code, since the list length can legally be zero.
                self._fulfill1(sub1, debug = debug)
            pass
        return
    def _list_of_subs(self): #bruce 070109
        """
        For debugging: return a newly made list of our subscriptions
        (not removing duplicates), without changing or fulfilling them.
        """
        res = []
        subs = self._subs
        for sublis in subs.itervalues():
            res.extend(sublis)
        return res
    def remove_all_subs(self): #bruce 070109 experimental (for trying to fix a bug in exprs module), might become normal
        """
        [private while experimental]
        WARNING: I'm not sure makes sense except on an owning obj
        since we are a 'one time' sublist
        """
        try:
            self._subs.clear() # does self._subs always exist when this is called? I think so but I'm not sure, so check for this.
        except AttributeError:
            print "no _subs in %r so nothing to clear in remove_all_subs" % (self,)
        return
    def _fulfill1(self, sub1, debug = False):
        # note: the only use of self is in the debug msg.
        try:
            if debug or _print_all_subs:
                print "%r: fulfilling sub1 %r" % (self, sub1)
            sub1() #e would an arg of self be useful?
        except:
            # We have no choice but to ignore the exception, even if it's always a bug (as explained in docstring).
            # The convention should be to make sure sub1 won't raise an exception (to make bugs more noticable),
            # so this is always a likely bug, so we print it; but only when atom_debug, in case it might get printed
            # a lot in some circumstances. [revised, see below]
            if True or debug or debug_flags.atom_debug:
                #bruce 070816 included True in that condition, to avoid silently discarding exceptions indicating real bugs.
                print_compact_traceback("bug: exception in subs %r ignored by %r: " % (sub1, self) )
                print_compact_stack(" note: here is where that exception occurred: ", skip_innermost_n = 1) #bruce 080917 revised
        return        
    def remove_subs(self, func): # note: this has never been used as of long before 061022, and looks potentially unsafe (see below)
        """
        Make sure (one subscribed instance of) func will never be fulfilled.
        WARNING: calling this on a subs (a specific instance of func) that was already fulfilled is an UNDETECTED ERROR.
        But it's ok to subscribe the same func eg 5 times, let 2 of those be fulfilled, and remove the other 3.
        """
        # optimize by assuming it's there -- if not, various exceptions are possible.
        # [Note, bruce 061022: this assumption looks like a bug, in light of the use of remove_all_instances.
        # At least, it would be an error to use both of them on the same sublis within self,
        # which means in practice that it would be hard to safely use both of them on the same OneTimeSubsList object.]
        self._subs[id(func)].pop()
            # (this can create a 0-length list which remains in the dict. seems ok provided self is not recycled.)
        return
    def remove_all_instances(self, func):
        """
        #doc; legal even if no instances, but only if an instance
        once existed (but this might not be checked for).
        """
        try:
            del self._subs[id(func)]
        except KeyError:
            pass # not sure this ever happens, but it's legal (if we call this multiple times on one func)
        except AttributeError:
            if 0 and debug_flags.atom_debug:
                print "atom_debug: fyi: %r's event already occurred, in remove_all_instances( %r)" % (self, func)
            pass # this happens routinely after fulfill_all removes self._subs,
                # since our recipient is too lazy to only remove its other subs when one gets fulfilled --
                # it just removes all the subs it had, including the one that got fulfilled.
        except:
            # this detected the following bug during development (subsequently fixed):
            # bug: self._subs is None: exceptions.TypeError: object does not support item deletion
            print_compact_traceback("bug: self._subs is %r: " % (self._subs,) )
        return
    pass # end of class OneTimeSubsList

# ==

class SelfUsageTrackingMixin: #bruce 050804; docstring revised 090212
    """
    You can mix this into client classes which need to let all other code
    track uses and changes (or invalidations) of their "main value".

    What "main value" means is up to the client class. Usually it's the value
    returned by accessing some "get method" (in the client class instance
    itself, or if that class implements a "high-level slot", then in an instance
    of the slot's client), but it can instead be an externally stored value
    or implicit value, or even something like the side effects that a
    certain method would perform, or the cumulative side effects that would
    have occurred over all calls of a certain method if it was called again
    now (e.g. a method to keep something up to date). In the more complex cases
    of what value is being tracked, there is still usually a method that must
    be called by external code to indicate a use of that value (and sometimes
    to return a related quantity such as a change indicator), which can be
    considered to be a kind of "get method" even though it doesn't actually
    return the tracked value.
    
    If a client class needs to permit tracking of more than one value or aspect,
    it should use more than one instance of this class or a client class,
    one for each tracked value. (Our subclass UsageTracker can be used as a
    "stand-alone instance of this class".)

    To accomplish the tracking, the client class instances must notice all
    uses and changes of the "main value" they want to track, and call the
    following methods whenever these occur:

    * for uses, call self.track_use() (must be called on every use, not just
      the first use after a change, in case the using entity is different);

    * for changes or invalidations, call self.track_change() or
      self.track_inval() (these are presently synonyms but might not always be).

    For more info see the docstrings of the specific methods.

    See also code comments warning about an issue in correctly using this
    in conjunction with class Formula, and after client objects are killed.
    """
    # note: as of 061022 this was used only in class Chunk and
    # (via UsageTracker) in preferences.py; more uses were added later.

    ### REVIEW the status of these old comments, and clarify them:
    
    # WARNING: The way Formula uses track_change only works when the call of
    # track_change comes after the new value is available,
    # but when using track_change to report an invalidation, that's not
    # possible in general! ###@@@ this design flaw needs to be corrected
    # somehow. See also comments near one of preferences.py's uses of
    # track_change.

    # note about whether to call track_change after something is "killed":
    # If something is "killed" or in some other way becomes unusable,
    # it only needs to call track_change if a use after that is theoretically
    # possible (which is usually the case, since bugs in callers can cause
    # that), and if a use after that would have a different effect because it
    # had been killed. (I think it's always safe to call it then, and not even
    # an anti-optimization, but I'm not 100% sure.) (Typically, other changes,
    # which themselves call track_change(), occur when something is killed,
    # so whether it's called directly doesn't matter anyway.)

    def track_use(self):
        """
        This must be called whenever the "get method" for the value we're
        tracking is called, or more generally whenever that value is "used"
        (see class docstring for background).

        @note: This must be called on every use, not just the first use after
               a change, in case the using entity is different, since all users
               need to know about the next change or invalidation.

        This works by telling cooperating users (clients of SubUsageTrackingMixin ###VERIFY)
        what they used, so they can subscribe to invalidations or changes of all
        values they used.
        
        [some callers might inline this method]
        """
        if getattr(self, '_changes__debug_print', False):
            ####REVIEW: can we give _changes__debug_print a default value
            # as an optim? Note that since we're a mixin class, it would end up
            # defined in arbitrary client classes, but its mangled-like name
            # ought to make that ok. [bruce 090212 comment]
            print_compact_stack( "\n_changes__debug_print: track_use of %r: " % self )
        try:
            subslist = self.__subslist
        except AttributeError:
            # note: this is the only way self.__subslist gets created;
            # it happens on the first call of track_use (on self),
            # and on the first call after each call of track_change/track_inval
            debug_name = debug_flags.atom_debug and ("%r" % self) or None #061118; TODO: optimize
            subslist = self.__subslist = OneTimeSubsList(debug_name)
                # (more generally, some sort of unique name for self's current value era)
        # (design note: Should we now return subslist.subscribe(func)? No --
        #  that's what the value-user should do *after* subslist gets entered
        #  here into its list of used objects, and value-user later finds it
        #  there.)
        env.track( subslist)
            ###@@@ REVIEW:
            # - is it right that the name of this function doesn't imply it's specific to usage-tracking?
            #   can it be used for tracking other things too?? [guess: no and no -- rename it ###@@@.]
            # - (Wouldn't it be faster to save self, not self.__subslist, and then at the end to create and use the subslist?
            #    Yes, but it would be wrong, since one self has several subslists in succession as its value changes!
            #    [addendum 061022: i'm suspicious of that reasoning -- doesn't it happen too soon for the subslist to change??])
            # - Maybe some callers can inline this method using essentially only a line like this:
            #     env.used_value_sublists[id(subslist)] = subslist
        return

    def track_change(self):
        """
        This method (which implements both track_change and track_inval)
        must be called whenever something changes or invalidates the value
        self is tracking (see class docstring for background).

        It tells everything which tracked a use of self's value that
        self's value is no longer valid (unless this would be redundant
        since it already told them this since they last subscribed).

        (What the recipients do with that message is up to them,
        but typically includes propogating further invalidations to
        their own subscribers, directly marking their own value as invalid
        (using another instance of this class or anything analogous to it),
        and/or adding themselves to a set of objects that need later updates.)

        Note that in typical use cases, there are several distinct
        reasons to call this method -- all of them which apply must be done,
        which typically means two or three kinds of calls of this method
        can occur for each instance of self:

        * the tracked value is explicitly set

        * something used to compute the tracked value has changed (or been
          invalidated), so the tracked value needs to be invalidated
          (to ensure it will be recomputed when next needed).
          
          (This differs from the tracked value changing by being set,
          since we don't yet know the new value, or even (in general) whether
          it's definitely different than the old value. But this class doesn't
          yet behave differently in those cases -- in general, it's rare for
          there to be a simple correct way to take advantage of knowing the new
          value, except for comparing it to an old value and avoiding
          propogating an invalidation if they're equivalent, but in all cases
          where that can be done simply and correctly, it can be done by our
          client before calling this method. [###todo: refer to external docs
          which elaborate on this point, discussing why this comparison-optim
          can't be propogated in general in any simple way.])

          This kind of call has two subcases:

          * done manually by the client, since it knows some value
            used in that computation has changed (this is the only way to handle
            it for values it uses which are not automatically tracked
            by the system used by this class);

          * done automatically, since something the client usage-tracked
            (via the system used by this class)
            while last recomputing that value has changed -- this case
            is called "propogating an invalidation" (propogating it
            from the other value usage-tracked by our client during its
            recomputation, to the value directly tracked by our client).
        """
        ### REVIEW: rename to track_inval?? see class docstring and other
        # comments for discussion

        # review: add args? e.g. "why" (for debugging), nature of change
        # (for optims), etc...
        debug = getattr(self, '_changes__debug_print', False)
        if debug:
            print_compact_stack( "\n_changes__debug_print: track_change of %r: " % self )
        try:
            subslist = self.__subslist
        except AttributeError:
            # this is common [TODO: optimize by replacing with boolean test]
            return # optimization (there were no uses of the current value, or,
                   # they were already invalidated)
        del self.__subslist
        subslist.fulfill_all(debug = debug)
        return

    track_inval = track_change
        #bruce 061022 added track_inval to API, though I don't know if it ever
        # needs to have a different implem. ### REVIEW: does each client use the
        # appropriate one of track_inval vs. track_change?
    
    pass # end of class SelfUsageTrackingMixin

# ==

class UsageTracker( SelfUsageTrackingMixin): #bruce 050804 #e rename?
    """
    Ownable version of SelfUsageTrackingMixin, for owners that have
    more than one aspect whose usage can be tracked, or which want to use
    a cooperating class rather than a mixin class for clarity.
    """
    # note: as of 061022 this is used only in _tracker_for_pkey (preferences.py);
    # this or its superclass might soon be used in exprs/lvals.py
    pass

# ===

class begin_end_matcher: #bruce 050804
    """
    Maintain a stack of objects (whose constructor is a parameter of this object)
    which are created/pushed and popped by calls of our begin/end methods, which must occur in
    properly nested matching pairs. Try to detect and handle the error of nonmatching begin/end calls.
    (This only works if the constructor promises to return unique objects, since we use their id()
    to detect matching.)
    """
    active = False # flag to warn outside callers that we're processing a perhaps-nonreentrant method [bruce 050909]
    def __init__(self, constructor, stack_changed_func = None):
        """
        Constructor is given all args (including keyword args) to self.begin(),
        and from them should construct objects with begin(), end(), and error(text) methods
        which get stored on self.stack while they're active.
        Or constructor can be None, which means begin should always receive one arg, which is the object to use.
           Stack_changed_func (or noop if that is None or not supplied)
        is called when we're created and after every change to our stack,
        with arg1 self, and arg2 a dict of info (keyword:value pairs) about the nature of the stack change
        (see dict() calls herein for its keywords, including popped, pushed, errmsg).
        """
        self.constructor = constructor or (lambda arg: arg)
        self.stack_changed = stack_changed_func or noop
        self.stack = []
        self.active_apply( self.stack_changed, (self, dict()) ) # self.stack_changed(self, dict())
            # callers depend on stack_changed being called when we're first created
            #k is active_apply needed here??
    def active_apply(self, func, args, kws = {}):
        self.active = True
        try:
            return apply(func, args, kws)
        finally:
            self.active = False
    def begin(self, *args, **kws):
        """
        Construct a new object using our constructor;
        activate it by calling its .begin() method [#k needed??] [before it's pushed onto the stack];
        push it on self.stack (and inform observers that self.stack was modified);
        return a currently-unique match_checking_code which must be passed to the matching self.end() call.
        """
        self.active = True
        try:
            newobj = self.constructor(*args, **kws) # exceptions in this mean no change to our stack, which is fine
            newobj.begin()
            self.stack.append(newobj)
            self.stack_changed(self, dict(pushed = newobj))
            # for debugging, we could record compact_stack in newobj, and print that on error...
            # but newobj __init__ can do this if it wants to, without any help from this code.
            return id(newobj) # match_checking_code
        finally:
            self.active = False
    def end(self, match_checking_code):
        """
        This must be passed the return value from the matching self.begin() call.
        Verify begin/end matches, pop and deactivate (using .end(), after it's popped) the matching object, return it.
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
            self.active = True
            try:
                self.stack_changed(self, dict(popped = doneobj))
                doneobj.end() # finalize doneobj
            finally:
                self.active = False
            return doneobj
        # some kind of error
        ids = map( id, stack )
        if match_checking_code in ids:
            # some subroutines did begin and no end, but the present end has a begin -- we can recover from this error
            doneobj = stack.pop()
            while id(doneobj) != match_checking_code:
                self.active = True
                try:
                    errmsg = "begin, with no matching end by the time some outer begin got its matching end"
                    self.stack_changed(self, dict(popped = doneobj, errmsg = errmsg))
                        # stack_change is needed here in case doneobj.end() looks at something this updates from self.stack
                    doneobj.error(errmsg)
                    doneobj.end() # might be needed -- in fact, it might look at stack and send messages to its top
                finally:
                    self.active = False
                doneobj = stack.pop()
            # now doneobj is correct
            self.active = True
            try:
                self.stack_changed(self, dict(popped = doneobj))
                doneobj.end()
            finally:
                self.active = False
            return doneobj
        # otherwise the error is that this end doesn't match any begin, so we can't safely pop anything from the stack
        print_compact_stack( "bug, ignored for now: end(%r) with no matching begin, in %r: " % (match_checking_code, self) )
        return None # might cause further errors as caller tries to use the returned object
    pass # end of class begin_end_matcher

# ==

def default_track(thing): #bruce 050804; see also the default definition of track in env module
    """
    Default implementation -- will be replaced at runtime whenever usage of certain things is being tracked.
    """
##    if debug_flags.atom_debug:
##        print "atom_debug: fyi (from changes module): something asked to be tracked, but nothing is tracking: ", thing
##        # if this happens and is not an error, then we'll zap the message.
    return

def _usage_tracker_stack_changed( usage_tracker, infodict): #bruce 050804
    """
    [private]
    called when usage_tracker's begin/end stack is created,
    and after every time it changes
    """
    # getting usage_tracker arg is necessary (and makes better sense anyway),
    # since when we're first called, the global usage_tracker is not yet defined
    # (since its rhs, in the assignment below, is still being evaluated).
    del infodict
    stack = usage_tracker.stack
    if stack:
        env.track = stack[-1].track
    else:
        env.track = default_track
    return

usage_tracker = begin_end_matcher( None, _usage_tracker_stack_changed )
    # constructor None means obj must be passed to each begin

usage_tracker._do_after_current_tracked_usage_ends = {} #070108

def after_current_tracked_usage_ends(func):# new feature 070108 [tested and works, but not currently used]
    """
    Do func at least once after the current usage-tracked computation ends.

    WARNING: if func invalidates something used during that computation, it will cause
    an immediate inval of the entire computation, which in most cases would lead to
    excessive useless recomputation. For an example of incorrect usage of this kind,
    see Lval_which_recomputes_every_time in exprs/lvals.py (deprecated).

    (There may be legitimate uses which do something other than a direct inval,
    such as making a note to compare something's current and new value at some later time,
    for possible inval just before it's next used in a tracked computation.
    So this function itself is not deprecated. But it's been tested only in the deprecated
    Lval_which_recomputes_every_time.)
    """
    assert usage_tracker.stack, "error: there is no current usage-tracked computation"
    # we use a dict to optim for lots of equal funcs (reducing RAM usage, at least)
    # (note that in the case where this comes up, Lval_which_recomputes_every_time in exprs/lvals.py,
    #  they might be equivalent but non-identical bound methods)
    usage_tracker._do_after_current_tracked_usage_ends[ func] = func
    return

class SubUsageTrackingMixin: #bruce 050804; as of 061022 this is used only in class Chunk, class GLPane, class Formula
    # [note, 060926: this doesn't use self at all [later: except for debug messages].
    #  Does it need to be a mixin?? addendum 061022: maybe for inval propogation??]
    """
    ###doc - for doing usagetracking in whatever code we call when we
    remake a value, and handling results of that;
    see class usage_tracker_obj for a related docstring

    @note: this is often used in conjunction with SelfUsageTrackingMixin,
           in which case (for a client class which inherits this class and
           that one together) the invalidator passed to self.end_tracking_usage
           can often be self.track_inval or a client method that calls it.
    """
    def begin_tracking_usage(self): #e there's a docstring for this in an outtakes file, if one is needed
        debug_name = debug_flags.atom_debug and ("%r" % self) or None #061118
        obj = usage_tracker_obj(debug_name)
        match_checking_code = usage_tracker.begin( obj)
            # don't store match_checking_code in self -- that would defeat the error-checking
            # for bugs in how self's other code matches up these begin and end methods
            # [later, 060926: would it be good to combine id(self) into the match-checking code,
            #  thereby enforcing that the same object calls the matching begin & end methods?
            #  I doubt it's needed, since the match_checking_code is already unique,
            #  and it's hard to see how the correct one could be passed by accident
            #  (except by code written to use some bad kluge, which might need that kluge).
            #  And it might be legitimate. So don't add a restriction like that.]
        return match_checking_code
    def end_tracking_usage(self, match_checking_code, invalidator, debug = False):
        """
        #doc;
        returns the usage_tracker_obj
        """
        # new feature 070109, mainly for debugging-related uses
        obj = usage_tracker.end( match_checking_code)
        obj.standard_end( invalidator, debug = debug)
            ##e or we could pass our own invalidator which wraps that one,
            # so it can destroy us, and/or do more invals, like one inside the other mixin class if that exists
        # support after_current_tracked_usage_ends [070108]
        if not usage_tracker.stack:
            dict1 = usage_tracker._do_after_current_tracked_usage_ends
            if dict1: # condition is optim
                usage_tracker._do_after_current_tracked_usage_ends = {}
                for func in dict1.itervalues():
                    try:
                        func()
                    except:
                        print_compact_traceback(
                            "after_current_tracked_usage_ends: error: exception in call of %r (ignored): " % (func,))
                        pass
                    continue
                pass
            pass
        return obj
    pass # end of class SubUsageTrackingMixin

class usage_tracker_obj: #bruce 050804; docstring added 060927
    """
    ###doc [private to SubUsageTrackingMixin, mostly]
    This object corresponds to one formula being evaluated,
    or to one occurrence of some other action which needs to know what it uses
    during a defined period of time while it calculates something.
       At the start of that action, the client should create this object and make it accessible within env
    so that when a trackable thing is used, its inval-subslist is passed to self.track (self being this object),
    which will store it in self.
    [This can be done by calling SubUsageTrackingMixin.begin_tracking_usage().]
       At the end of that action, the client should make this object inaccessible
    (restoring whatever tracker was active previously, if any),
    then call self.standard_end(invalidator) with a function it wants called
    the next time one of the things it used becomes invalid.
    [This can be done by calling SubUsageTrackingMixin.end_tracking_usage() with appropriate args.]
    Self.standard_end will store invalidator in self, and subscribe self.standard_inval to the invalidation
    of each trackable thing that was used.
       This usage_tracker_obj lives on as a record of the set of those subscriptions, and as the recipient
    of invalidation-signals from them (via self.standard_inval), which removes the other subscriptions
    before calling invalidator. (Being able to remove them is the only reason this object needs to live on,
    or that the inval signal needs to be something other than invalidator itself. Perhaps this could be fixed
    in the future, using weak pointers somehow. #e)
    """
    # [note, 060926: for some purposes, namely optim of recompute when inputs don't change [#doc - need ref to explanation of why],
    #  we might need to record the order of first seeing the used things,
    #  and perhaps their values or value-version-counters ###e]
    # 061022 review re possible use in exprs/lvals.py:
    # - a needed decision is whether inval propogation is the responsibility of each invalidator, or this general system.
    # - it seems like SubUsageTrackingMixin might need self to tie it to SelfUsageTrackingMixin for inval propogation. (guess)
    #   - which might mean we need variants of that, perhaps varying in this class, usage_tracker_obj:
    #     - a variant to propogate invals;
    #     - a variant to track in order (see below);
    #     - a variant to immediately signal an error (by raising an exception) if any usage gets tracked; used to assert none does.
    # - as mentioned above, one variant will need to keep an order of addition of new items, in self.track.
    # - and self.track is called extremely often and eventually needs to be optimized (and perhaps recoded in C).
    # Other than that, it can probably be used directly, with the invalidator (from client code) responsible for inval propogation.
    def __init__(self, debug_name = None):
        self.debug_name = debug_name #061118
    def __repr__(self): #061118
        return "<%s%s at %#x>" % (self.__class__.__name__, self.debug_name and ("(%s)" % self.debug_name) or '', id(self))
    def begin(self):
        self.data = {}
    def track(self, subslist): 
        """
        This gets called (via env.track) by everything that wants to record one use of its value.
        The argument subslist is a subscription-list object which permits subscribing to future changes
        (or invalidations) to the value whose use now is being tracked.
        [This method, self.track, gets installed as env.track, which is called often, so it needs to be fast.]
        """
        # For now, just store subslist, at most one copy. Later we'll subscribe just once to each one stored.
        self.data[id(subslist)] = subslist
    def error(self, text):
        print "bug: error in usage_tracker_obj:", text #e stub
    def end(self):
        pass # let the caller think about self.data.values() (eg filter or compress them) before subscribing to them
    def standard_end(self, invalidator, debug = False):
        """
        some callers will find this useful to call, shortly after
        self.end gets called; see the class docstring for more info
        """
        self.invalidator = invalidator # this will be called only by our own standard_inval
        whatweused = self.whatweused = self.data.values() # this list is saved for use in other methods called later
        self.last_sub_invalidator = inval = self.standard_inval
            # save the exact copy of this bound method object which we use now, so comparison with 'is' will work for unsubscribes
            # (this might not be needed if they compare using '==' [###k find out])
            # note: that's a self-referential value, which would cause a memory leak, except that it gets deleted
            # in standard_inval (so it's ok). [060927 comment]
        if debug:
            print "changes debug: %r.standard_end subscribing %r to each of %r" % (self, inval, whatweused) #bruce 070816
        for subslist in whatweused:
            subslist.subscribe( inval ) #e could save retvals to help with unsub, if we wanted
        self.data = 222 # make further calls of self.track() illegal [#e do this in self.end()??]
        return
    def standard_inval(self):
        """
        This is used to receive the invalidation signal,
        and call self.invalidator after some bookkeeping.
        See class docstring for more info.
        It also removes all cyclic or large attrs of self,
        to prevent memory leaks.
        """
        already = self.unsubscribe_to_invals('standard_inval')
        if already:
            pass # error message was already printed
        else:
            invalidator = self.invalidator
            del self.invalidator
            invalidator()
                # calling this twice might cause a bug if "something called standard_inval twice",
                # depending on the client object which receives it,
                # so we don't, and the error message above should be retained [070110 comment]
        return
    def unsubscribe_to_invals(self, why): #070110 split this out and revised caller (leaving it equivalent) and added a caller
        """
        if we already did this, print an error message mentioning why
        we did it before and return 1, else do it and return 0
        """
        # this needs to remove every subs except the one which is being fulfilled by calling it.
        # But it doesn't know which subs that is! So it has to remove them all, even that one,
        # so it has to call a remove method which is ok to call even for a subs that was already fulfilled.
        # The only way for that method to always work ok is for its semantics to be that it removes all current subs (0 or more)
        # which have the same fulfillment function (like subslist.remove_all_instances does).
        # That is only ok since our subs (self.standard_inval) is unique to this object, and this object
        # makes sure to give only one copy of it to one thing. (Another reason it could be ok is if it doesn't
        # matter how many times self.invalidator is called, once it's called once. This is true in all current uses [061119]
        # but perhaps not guaranteed.)
        inval = self.last_sub_invalidator
        self.last_sub_invalidator = 'hmm' # this value is also tested in another method
            # 061119 do this rather than using del, to avoid exception when we're called twice; either way avoids a memory leak
        self.last_sub_invalidator_why = why
        if inval == 'hmm':
            # we already did this
            if self.last_sub_invalidator_why == 'standard_inval' and why == 'standard_inval':
                # Something called standard_inval twice. This can happen (for reasons not yet clear to me) when some tracked state
                # is set and later used, all during the same computation -- normally, state used by a computation should never be set
                # during it, only before it (so as to trigger it, if the same computation used the same state last time around).
                # Maybe the problem is that sets of default values, within "initialization on demand", should be considered pure uses
                # but are being considered sets? Not sure yet -- this debug code only shows me a later event. ###k [061121 comment]
                # ... update 061207: this is now happening all the time when I drag rects using exprs.test.testexpr_19c,
                # so until it's debugged I need to lower the verbosity, so I'm putting it under control of flags I can set from other code.
                if _debug_standard_inval_twice: ## was debug_flags.atom_debug:
                    msg = "debug: fyi: something called standard_inval twice (not illegal but weird -- bug hint?) in %r" % self
                    if _debug_standard_inval_twice_stack:
                        print_compact_stack(msg + ": ",
                                            ## frame_repr = _std_frame_repr, #bruce 061120, might or might not be temporary, not normally seen
                                            linesep = '\n')
                    else:
                        print msg
            else:
                print "likely bug: %r unsubscribe_to_invals twice, whys are %r and %r" % (self, self.last_sub_invalidator_why, why)
                #e print stack?
            return 1
        elif _debug_standard_inval_nottwice_stack:
            print_compact_stack("debug: fyi: something called standard_inval once (totally normal) in %r: " % self)
        # the actual unsubscribe:
        whatweused = self.whatweused
        self.whatweused = 444 # not a sequence (cause bug if we call this again)
        for subslist in whatweused:
            ## can't use subslist.remove( self.last_sub_invalidator ), as explained above
            subslist.remove_all_instances( inval )
                ####e should add debug code to make sure this actually removes some, except in at most one call;
                # in fact, I need code to somehow verify they get removed by comparing lengths
                # since a bug in removing them properly at all is a possibility [070110 comment]
        return 0
    def got_inval(self):#070110
        """
        Did we get an inval yet (or make them illegal already)?
        (if we did, we no longer subscribe to any others, in theory --
         known to be not always true in practice)
        """
        return (self.last_sub_invalidator == 'hmm')
    def make_invals_illegal(self, obj_for_errmsgs = None):#070110, experimental -- clients ought to call it before another begin_tracking_usage... ##e
        # if not self.got_inval():
            # if it still subscribes to any invals:
            # + remove those subs
            # + in case that fails, arrange to complain if they are ever fulfilled,
            #   or better yet, prevent them from being fulfilled, by changing the invalidator
            # - print a message (if atom_debug) since it might indicate a bug (or did, anyway, before we removed the subs)
        # else:
            # - it supposedly doesn't subscribe to any invals, but what if it gets one anyway?
            # tell it to not call our invalidator in that case (change it?);
            # no need to print a message unless it would have called it
        if not self.got_inval():
            if 1: ## self.whatweused:
                if _debug_old_invalsubs:
                    # not necessarily a bug if they would never arrive -- I don't really know yet --
                    # it might (in fact it does routinely) happen in GLPane for reasons I'm not sure about...
                    # I should find out if it happens in other subusagetracking objects. ###e
                    # What I do know -- it's large and normal (for glpane) as if inval unsubs never happened; it's never 0;
                    # but the zapping fixes my continuous redraw bug in exprs module!
                    # [bruce 070110; more info and cleanup to follow when situation is better understood --
                    #  could it be a bug in the removal of subs which makes it never happen at all?!? ###k]
                    print "fyi: %r still has %d subs of its invalidator to things it used; zapping/disabling them" % \
                          (obj_for_errmsgs or self, len(self.whatweused))
            already = self.unsubscribe_to_invals('standard_inval')
            if already:
                # error message was already printed -- but, I don't think this can ever happen, so print *that*
                print "(should never happen in make_invals_illegal)"
        else:
            # if an inval comes (to self.standard_inval), we'll find out, since it'll complain (I think) 
            pass
        return
    pass # end of class usage_tracker_obj

_debug_old_invalsubs = False #070110
_debug_standard_inval_twice = debug_flags.atom_debug # whether to warn about this at all
_debug_standard_inval_twice_stack = False # whether to print_compact_stack in that warning [untested since revised by bruce 061207]
_debug_standard_inval_nottwice_stack = False # whether to print_compact_stack in an inval that *doesn't* give that warning [untested]

# ==

class begin_disallowing_usage_tracking(SubUsageTrackingMixin):
    """
    Publicly, this class is just a helper function, used like this:
    
        mc = begin_disallowing_usage_tracking(whosays) # arg is for use in debug prints and exception text
        try:
            ... do stuff in which usage tracking would be an error or indicate a bug
        finally:
            end_disallowing_usage_tracking(mc)
        pass
    """
    def __init__(self, whosays, noprint = False):
        self.whosays = "%r" % (whosays,) #k %r??
        self.noprint = noprint
        self.mc = self.begin_tracking_usage()
            ###e SHOULD do that in a nonstandard way so we notice each usage that occurs and complain, w/ exception;
            #e and we should not actually subscribe
    def _end_disallowing_usage_tracking(self):
        self.end_tracking_usage(self.mc, self.inval) # this shouldn't subscribe us to anything, once implem is finished properly
        # now warn if we actually subscribed to anything -- done in our overridden version of that method
        # someday, self.destroy(), but for now [until implem is done], stick around for things to call our inval.
        return
    def inval(self):
        #e don't use noprint, since this implies a bug in self, tho for now, that's a known bug, always there, til implem is done
        print "bug (some time ago): something that %r should not have subscribed to (but did - also a bug) has changed" % self
    def __repr__(self):
        return "<%s at %#x for %r>" % (self.__class__.__name__, id(self), self.whosays)
    def end_tracking_usage(self, match_checking_code, invalidator):
        """
        [THIS OVERRIDES the method from SubUsageTrackingMixin]
        """
        obj = usage_tracker.end( match_checking_code) # same as in mixin
        obj.standard_end( invalidator) # same as in mixin, but we'll remove this later, so don't just call the mixin version here
        if obj.whatweused: # a private attr of obj (a usage_tracker_obj), that we happen to know about, being a friend of it
            msg = "begin_disallowing_usage_tracking for %s sees some things were used: %r" % (self.whosays, obj.whatweused,)
            if not self.noprint:
                print msg
            assert 0, msg ##e should be a private exception so clients can catch it specifically; until then, noprint is not useful
        return obj #070110 be compatible with new superclass API
    pass

def end_disallowing_usage_tracking(mc):
    mc._end_disallowing_usage_tracking()
    return

# ==

def _std_frame_repr(frame): #bruce 061120 #e refile into debug.py? warning: dup code with lvals.py and [g4?] changes.py
    """
    return a string for use in print_compact_stack
    """
    # older eg: frame_repr = lambda frame: " %s" % (frame.f_locals.keys(),), linesep = '\n'
    locals = frame.f_locals
    dfr = locals.get('__debug_frame_repr__')
    if dfr:
        return ' ' + dfr(locals)
    co_name = frame.f_code.co_name
    res = ' ' + co_name
    self = locals.get('self')
    if self is not None:
        res +=', self = %r' % (self,)
    return res
    # locals.keys() ##e sorted? limit to 25? include funcname of code object? (f_name?)
    # note: an example of dir(frame) is:
    ['__class__', '__delattr__', '__doc__', '__getattribute__', '__hash__',
    '__init__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
    '__setattr__', '__str__', 'f_back', 'f_builtins', 'f_code',
    'f_exc_traceback', 'f_exc_type', 'f_exc_value', 'f_globals', 'f_lasti',
    'f_lineno', 'f_locals', 'f_restricted', 'f_trace']
    # and of dir(frame.f_code) is:
    ['__class__', '__cmp__', '__delattr__', '__doc__', '__getattribute__',
    '__hash__', '__init__', '__new__', '__reduce__', '__reduce_ex__',
    '__repr__', '__setattr__', '__str__', 'co_argcount', 'co_cellvars',
    'co_code', 'co_consts', 'co_filename', 'co_firstlineno', 'co_flags',
    'co_freevars', 'co_lnotab', 'co_name', 'co_names', 'co_nlocals',
    'co_stacksize', 'co_varnames']

# ==

class Formula( SubUsageTrackingMixin): #bruce 050805 [not related to class Expr in exprs/Exprs.py, informally called formulae]
    """
    """
    killed = False
    def __init__( self, value_lambda, action = None, not_when_value_same = False, debug = False ):
        """
        Create a formula which tracks changes to the value of value_lambda (by tracking what's used to recompute it),
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
        [WARNING: the code for the not_when_value_same = True option is untested as of 060306, since nothing uses it yet.]
        """
        self.debug = debug #bruce 070816
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
        debug = self.debug
        print_errors = True or debug or debug_flags.atom_debug
            #bruce 070816 included True in that condition, since prior code could
            # silently discard exceptions which indicated real bugs.
        if debug:
            print "\n_changes__debug_print: %r.recompute() calling %r" % \
                  ( self, self.value_lambda )
        error = False
        match_checking_code = self.begin_tracking_usage()
        try:
            newval = self.value_lambda()
        except:
            error = True
            newval = None
            if print_errors:
                print_compact_traceback( "bug: exception in %r value_lambda %r: " % (self, self.value_lambda) )
        self.end_tracking_usage( match_checking_code, self.need_to_recompute, debug = debug )
        if not error and (not self.not_when_value_same or self.first_time or not self.values_same( self.oldval, newval) ):
            # do the action
            try:
                self.action( newval)
            except:
                error = True
                if print_errors:
                    print_compact_traceback( "bug: exception in %r action %r: " % (self, self.action) )
        self.first_time = False
        if not error and self.not_when_value_same:
            # save self.oldval for the comparison we might need to do next time
            self.oldval = newval
        if error:
            self.destroy()
            if print_errors:
                print_compact_stack( "note: destroyed %r due to bug reported above: " % self )
        return
    def need_to_recompute(self):
        if not self.killed:
            self.recompute()
        return
    def values_same(self, val1, val2): #bruce 060306; untested, since self.not_when_value_same is apparently never True ###@@@
        """
        Determine whether two values are the same, for purposes of the option 'not_when_value_same'.
        Override this in a subclass that needs a different value comparison, such as 'not !='
        (or change the code to let the caller pass a comparison function).

        WARNING: The obvious naive comparison (a == b) is buggy for Numeric arrays,
        and the fix for that, (not (a != b)), is buggy for Python container classes
        (like list or tuple) containing Numeric arrays. The current implem uses a slower and stricter comparison,
        state_utils.same_vals, which might be too strict for some purposes.
        """
        return same_vals(val1, val2)
    pass # end of class Formula

# ==
# As of 050803, many of the facilities after this point are used only as stubs,
# though some might be used soon, e.g. as part of recent files menu,
# custom jigs, Undo, or other things.
# [as of 060330 pairmatcher is used in Undo; maybe keep_forever is used somewhere;
#  a lot of Undo helpers occur below too]

class pairmatcher:
    """
    Keep two forever-growing lists,
    and call a specified function on each pair of items in these lists,
    in a deterministic order,
    as this becomes possible due to the lists growing.

    Normally that specified function should return None;
    otherwise it should return special codes which
    control this object's behavior (see the code for details).
    """
    def __init__(self, func, typearg, debug_name = None):
        self.d1s = []
        self.d2s = []
        self.func = func #e will this func ever need to be changed, after we're made?
        self.typearg = typearg # public, thus visible to each call of func, since we now pass self [bruce 060330 new feature]
        self.debug_name = debug_name or str(typearg) or "?" #revised 060330
    def another_dim2(self, d2):
##        print self,'getsg5h6 d2',d2
        for d1 in self.d1s:
            self.doit(d1,d2) # doit for existing d1s
        self.d2s.append(d2) # and for future d1s
    def another_dim1(self, d1):
##        print self,'getsg5h6 d1',d1
        for d2 in self.d2s:
            self.doit(d1,d2) # doit for existing d2s
        self.d1s.append(d1) # and for future d2s
    def doit(self, d1, d2):
        try:
            retcode = self.func(d1,d2,self) #bruce 060330 new feature -- pass self [##k should we catch exception in func??]
            if retcode:
                if retcode == "remove d1":
                    # note: we might or might not be iterating over d1s right now!
                    # if we are iterating over d2, we might have already removed d1!
                    # we should probably stop that loop in that case, but that feature is nim.
                    # at least don't mind if we did already remove it...
                    # [060330 temp kluge -- really we ought to stop the loop ###@@@]
                    self.d1s = list(self.d1s) # in case we are, modify a fresh copy
                    try:
                        self.d1s.remove(d1)
                    except ValueError:
                        pass
                elif retcode == "remove d2":
                    self.d2s = list(self.d2s)
                    try:
                        self.d2s.remove(d2)
                    except ValueError:
                        pass
                else:
                    print_compact_stack( "bug (ignored): unrecognized return code %r in pairmatcher %r: " % \
                                         (retcode, self.debug_name))
            #e any other use for retval??
        except:
            print_compact_traceback( "exception in %r ignored: " % self)#revised 060330
        return
    def __repr__(self): #060330, untested
        return "<%s at %#x, debug_name = %r>" % (self.__class__.__name__, id(self), self.debug_name)
    pass

class MakerDict:
    """
    A read-only dict with a function for constructing missing elements.
    """
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

def postinit_func( d1, d2, matcher): #bruce 060330 add matcher arg
    """
    After d1 is inited, tell it about d2.
    (This is meant to be called for every d1 of one kind,
     and every d2 of another kind,
     registered below under the same name.)
    """
    if 1:
        #bruce 060330 kluge, but might be reasonable -- let method name be encoded in typename for type of postinit object
        #e (if speed of this ever matters, we might memoize the following in an our-private attr of matcher)
        typename = matcher.typearg
        if typename.startswith('_'):
            ###e should assert it's legit as attrname?
            methodname = typename
        else:
            methodname = 'postinit_item' # compatibility with old code, still used as of 060330 for "Jig menu items" or so
    try:
        method = getattr(d1, methodname)
        method(d2)
    except:
        # blame d1, for error in either statement above
        print_compact_traceback( "exception in calling (or finding method for) d1.%s(d2) ignored; removing d1: " % (methodname,))
            #e objnames? safe_repr(obj)?
        return "remove d1" # special code recognized by the pairmatcher

postinit_pairmatchers = MakerDict( lambda typename: pairmatcher( postinit_func, typename ) )

# the public functions:

# (for main window Jig menu items we'll use the typename "Jigs menu items" since maybe other things will have Jigs menus)

#e [later, 060330: this API suffers from the methodname postinit_item being fixed, rather than depending on typename,
#   which matters if this is used for lots of purposes and the same object might participate in more than one purpose.]

def register_postinit_object( typename, object):
    """
    Cause object to receive the method-call object.postinit_item(item)
    for every postinit item registered under the same typename,
    in the order of their registration,
    whether item is already registered or will be registered in the future.
    """
    pairmatcher = postinit_pairmatchers[ typename]
    pairmatcher.another_dim1( object)

def register_postinit_item( typename, item):
    """
    Cause every object registered with register_postinit_object
    under the same typename (whether registered already or in the future,
    and in their order of registration)
    to receive the method call object.postinit_item(item) for this item.
    """
    pairmatcher = postinit_pairmatchers[ typename]
    pairmatcher.another_dim2( item)    

# ==

_keep_these_forever = {}

def keep_forever(thing):
    """
    a place to put stuff if you need to make sure it's never deallocated by Python
    """
    _keep_these_forever[id(thing)] = thing

# ==

_op_id = 0

debug_begin_ops = False #bruce 051018 changed from debug_flags.atom_debug

class op_run:
    """
    Track one run of one operation or suboperation, as reported to
    env.begin_op and env.end_op in nested pairs
    """
    def __init__(self, op_type = None, in_event_loop = False, typeflag = ''): #bruce 060321 added typeflag
        #bruce 060127 adding in_event_loop for Undo
        """
        [this gets all the args passed to env.begin_op()]
        """
        self.op_type = op_type # this might be almost anything, mainly meant for humans to see
        self.in_event_loop = in_event_loop
        self.typeflag = typeflag # this is one of a small set of constants which control how this is treated by undo (at least)
        global _op_id
        _op_id += 1
        self.op_id = _op_id
    def begin(self):
        if debug_begin_ops:
            self.printmsg( "%sbegin op_id %r, op_type %r" % (self.indent(), self.op_id, self.op_type) )
        pass # not sure it's good that begin_end_matcher requires us to define this
    def end(self):
        if debug_begin_ops:
            self.printmsg( "%send op_id %r, op_type %r" % (self.indent(), self.op_id, self.op_type) )
        pass
    def error(self, errmsg_text):
        """
        called for begin_op with no matching end_op, just before our .end() and the next outer end_op is called
        """
        if debug_begin_ops: # 
            self.printmsg( "%serror op_id %r, op_type %r, errmsg %r" % (self.indent(), self.op_id, self.op_type, errmsg_text) )
        pass
    def printmsg(self, text):
        if debug_begin_ops:
            # print "atom_debug: fyi: %s" % text
            env.history.message( "debug: " + text ) # might be recursive call of history.message; ok in theory but untested ###@@@
    def indent(self):
        """
        return an indent string based on the stack length; we assume the stack does not include this object
        """
        #e (If the stack did include this object, we should subtract 1 from its length. But for now, it never does.)
        return "| " * len(op_tracker.stack)
    pass

_in_event_loop = True #bruce 060127; also keep a copy of this in env; probably that will become the only copy #e
env._in_event_loop = _in_event_loop

def _op_tracker_stack_changed( tracker, infodict ): #bruce 050908 for Undo
    """
    [private]
    called when op_tracker's begin/end stack is created, and after every time it changes
    """
    #e we might modify some sort of env.prefs object, or env.history (to filter out history messages)...
    #e and we might figure out when outer-level ops happen, as part of undo system
    #e and we might install something to receive reports about possible missing begin_op or end_op calls
    #
    #bruce 060127 new code:
    new_in_event_loop = True # when nothing is on this op_run stack, we're in Qt's event loop
    if tracker.stack:
        new_in_event_loop = tracker.stack[-1].in_event_loop
    global _in_event_loop, _last_typeflag
    changed = False # will be set to whether in_event_loop changed
    if _in_event_loop != new_in_event_loop:
        # time for a checkpoint
##        if _in_event_loop:
##            print "begin command segment"
##        else:
##            print "end command segment"
        changed = True
        beginflag = _in_event_loop
    _in_event_loop = new_in_event_loop
    env._in_event_loop = _in_event_loop
    if changed:
        for sub in env.command_segment_subscribers[:]: # this global list might be changed during this loop
            unsub = False
            try:
                #e ideally we should prevent any calls into op_tracker here...
                # infodict is info about the nature of the stack change, passed from the tracker [bruce 060321 for bug 1440 et al]
                unsub = sub( beginflag, infodict, tracker ) # (we can't always pass tracker.stack[-1] -- it might not exist!)
            except:
                print_compact_traceback("bug in some element of env.command_segment_subscribers (see below for more): ")
                #e discard it?? nah. (we'd do so by unsub = True)
                """ note: during Quit, we got this, when we tried to update the menu items no longer present (enable a QAction);
                this could be related to the crashes on Quit reported recently;
                so we should try to get the assy to unsubscribe (clear and deinit) when we're about to quit. [bruce 060127]
                  bug in some element of env.command_segment_subscribers: exceptions.RuntimeError:
                  underlying C/C++ object has been deleted
                  [changes.py:607] [undo_manager.py:115] [undo_manager.py:154] [undo_manager.py:128] [undo_manager.py:238]
                """
                print_compact_stack(" the call that led to that bug: ", skip_innermost_n = 1) # bruce 080917
            if unsub:
                try:
                    env.command_segment_subscribers.remove(sub)
                except ValueError:
                    pass
                pass
            pass
    return

op_tracker = begin_end_matcher( op_run, _op_tracker_stack_changed )

def env_begin_op(*args, **kws):
    return op_tracker.begin(*args, **kws)

def env_end_op(mc):
    return op_tracker.end(mc) #e more args?

env.begin_op = env_begin_op
env.end_op = env_end_op

global_mc = None
_in_op_recursing = False

def env_in_op(*args, **kws): # (disabled, separately, bruce 060127)
    # [note 060320: it's still called directly just below, in env_begin_recursive_event_processing; does it do anything then??]
    """
    This gets called by various code which might indicate that an operation is ongoing,
    to detect ops in legacy code which don't yet call env.begin_op when they start.
       The resulting "artificial op" will continue until the next GLPane repaint event
    (other than one known to occur inside recursive event processing,
     which should itself be wrapped by begin_op/end_op [with a special flag ###doc? or just in order to mask the artificial op?]),
    which will end it.
       This system is subject to bugs if recursive event processing is not wrapped,
    and some op outside of that has begin but no matching end -- then a redraw during
    the unwrapped recursive event processing might terminate this artificial op too early,
    and subsequent ends will have no begin (since their begin got terminated early as if it had no end)
    and (presently) print debug messages, or (in future, perhaps) result in improperly nested ops.
    """
    global global_mc, _in_op_recursing
    if not op_tracker.stack and not _in_op_recursing and not op_tracker.active:
        _in_op_recursing = True # needed when env_begin_op (before pushing to stack) calls env.history.message calls this func
        try:
            assert global_mc is None
            global_mc = env_begin_op(*args, **kws)
        finally:
            _in_op_recursing = False
    return

def env_after_op(): # (disabled, separately, bruce 060127)
    """
    This gets called at the start of GLPane repaint events
    [#e or at other times not usually inside user-event handling methods],
    which don't occur during an "op" unless there is recursive Qt event processing.
    """
    global global_mc
    if global_mc is not None and len(op_tracker.stack) == 1:
        #e might want to check whether we're inside recursive event processing (if so, topmost op on stack should be it).
        # for now, assume no nonmatch errors, and either we're inside it and nothing else was wrapped
        # (impossible if the wrapper for it first calls env_in_op),
        # or we're not, so stack must hold an artificial op.
        mc = global_mc
        global_mc = None #k even if following has an error??
        env_end_op(mc)
    return

# disable these, bruce 060127
##env.in_op = env_in_op
##env.after_op = env_after_op

def env_begin_recursive_event_processing():
    """
    call this just before calling qApp.processEvents()
    """
    env_in_op('(env_begin_recursive_event_processing)')
    return env_begin_op('(recursive_event_processing)', in_event_loop = True, typeflag = 'beginrec') #bruce 060321 added typeflag
        #bruce 060127 added in_event_loop = True

def env_end_recursive_event_processing(mc):
    """
    call this just after calling qApp.processEvents()
    """
    return env_end_op(mc) #bruce 060321: no typeflag needed (or allowed), gets it from matching begin_op

env.begin_recursive_event_processing = env_begin_recursive_event_processing
env.end_recursive_event_processing = env_end_recursive_event_processing

#e desired improvements:
# - begin_op could look at existing stack frames, see which ones are new, sometimes do artificial begin_ops on those,
#   with the end_ops happening either from __del__ methods, or if that doesn't work (due to saved tracebacks),
#   from every later stack-scan realizing those frames are missing and doing something about it
#   (like finding the innermost still-valid stack-frame-op and then the next inner one and ending its stack-suffix now).
#   (If we can run any code when tracebacks are created, that would help too. I don't know if we can.)
#   This should give you valid begin/end on every python call which contained any begin_op call which did this
#   (so it might be important for only some of them to do this, or for the results to often be discarded).
#   It matters most for history message emission (to understand py stack context of that). [050909]

# end
