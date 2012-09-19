# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
changedicts.py - utilities related to dictionaries of changed objects

@author: Bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 071106 split this out of changes.py

Current status:

This code appears to be active and essential for undo updating;
details unclear, as is whether it's used for any other kind of updating,
e.g. bond_updater -- guess, no (though some of the same individual dicts
might be). [bruce 071106 comment]

Update 071210: since that comment, it's also been used in the dna updater.
"""

from utilities.debug import print_compact_traceback

from foundation.changes import register_postinit_item

DEBUG_CHANGEDICTS = False # do not commit with True

# ==

class changedict_processor:
    """
    Allow a single transient changedict to be observed by multiple subscribers
    who periodically (at independent times) want to become up to date regarding it
    (which they do by calling our process_changes method),
    and who don't mind becoming forcibly up to date at other times as well,
    so that the dict can be cleared out each time any subscriber wants to be updated
    (by having all its items given to all the subscribers at once).
    """
    #bruce 060329 moved/modified from chem.py prototype
    # (for Undo differential scanning optim).
    # Note: as of 071106, this class is used only by register_changedict
    # in this file (i.e. it could be private).
    def __init__(self, changedict, changedict_name = "<some changedict>"):
        self.subscribers = {}
            # public dict from owner-ids to subscribers; their update
            # methods are called by self.process_changes
        assert type(changedict) == type({}) #k needed?
        self.changedict = changedict
        self.changedict_name = changedict_name
        return
    def subscribe(self, key, dictlike):
        """
        subscribe dictlike (which needs a dict-compatible .update method)
        to self.changedict [#doc more?]
        """
        assert not self.subscribers.has_key(key)
        self.subscribers[key] = dictlike
            # note: it's ok if it overrides some other sub at same key,
            # since we assume caller owns key
        return
    def unsubscribe(self, key):
        del self.subscribers[key]
        return
    def process_changes(self):
        """
        Update all subscribers to self.changedict by passing it to their
        update methods (which should not change its value)
        (typically, subscribers are themselves just dicts); then clear it.

        Typically, one subscriber calls this just before checking its
        subscribing dict, but other subscribers might call it at arbitrary
        other times.
        """
        sublist = self.subscribers
            # note: this is actually a dict, not a list,
            # but 'subdict' would be an unclear name for a
            # local variable (imho)
        if DEBUG_CHANGEDICTS:
            print "DEBUG_CHANGEDICTS: %r has %d subscribers" % (self, len(sublist))
        changedict = self.changedict
        changedict_name = self.changedict_name
        len1 = len(changedict)
        for subkey, sub in sublist.items():
            try:
                unsub = sub.update( changedict)
                    # kluge: this API is compatible with dict.update()
                    # (which returns None).
            except:
                #e reword the name in this? include %r for self, with id?
                print_compact_traceback(
                    "bug: exception (ignored but unsubbing) in .update " \
                    "of sub (key %r) in %s: " % (subkey, changedict_name) )
                unsub = True
            if unsub:
                try:
                    del sublist[subkey]
                except KeyError:
                    pass
            len2 = len(changedict)
            if len1 != len2:
                #e reword the name in this? include %r for self, with id?
                print "bug: some sub (key %r) in %s apparently changed " \
                      "its length from %d to %d!" % (subkey, changedict_name, len1, len2)
                len1 = len2
            continue
        changedict.clear()
        assert changedict is self.changedict
        return
    pass # end of class changedict_processor


_dictname_for_dictid = {} # maps id(dict) to its name;
    # truly private, used here in both register_ functions;
    # it's ok for multiple dicts to have the same name;
    # never cleared (memory leak is ok since it's small)

_cdproc_for_dictid = {} # maps id(dict) to its changedict_processor;
    # not sure if leak is ok, and/or if this could be used to provide names too
    # WARNING: the name says it's private, but it's directly referenced in
    # undo_archive.get_and_clear_changed_objs and
    # undo_archive.sub_or_unsub_to_one_changedict;
    # it's used here only in register_changedict
    # [bruce 071106 comment]

def register_changedict( changedict, its_name, related_attrs ):
    #bruce 060329 not yet well defined what it should do ###@@@
    #e does it need to know the involved class?
    cdp = changedict_processor( changedict, its_name )
    del related_attrs # not sure these should come from an arg at all,
        # vs per-class decls... or if we even need them...
    #stub?
    dictid = id(changedict)
    ## assert not _dictname_for_dictid.has_key(dictid)
        # this is not valid to assert, since ids can be recycled if dicts are freed
    _dictname_for_dictid[dictid] = its_name
    _cdproc_for_dictid[dictid] = cdp
    return

_changedicts_for_classid = {} # maps id(class) to map from dictname to dict
    ### [what about subclass/superclass? do for every leafclass?]
    # WARNING: the name says it's private, but it's directly referenced in
    # undo_archive._archive_meet_class; used here only in register_class_changedicts
    # [bruce 071106 comment]

def register_class_changedicts( class1, changedicts ):
    """
    This must be called exactly once, for each class1 (original or reloaded),
    to register it as being changetracked by the given changedicts, each of
    which must have been previously passed to register_changedict.
    """
    classid = id(class1)
    # make sure class1 never passed to us before; this method is only
    # legitimate since we know these classes will be kept forever
    # (by register_postinit_item below), so id won't be recycled
    assert not _changedicts_for_classid.has_key(classid), \
           "register_class_changedicts was passed the same class " \
           "(or a class with the same id) twice: %r" % (class1,)
    assert not hasattr(changedicts, 'get'), \
           "register_class_changedicts should be passed a sequence of dicts, not a dict"
        # kluge (not entirely valid): make sure we were passed a list or tuple,
        # not a dict, to work around one of Python's few terrible features,
        # namely its ability to iterate over dicts w/o complaining
        # (by iterating over their keys)
    for changedict in changedicts:
        changedict_for_name = _changedicts_for_classid.setdefault(classid, {})
        dictname = _dictname_for_dictid[id(changedict)]
            # if this fails (KeyError), it means dict was not
            # registered with register_changedict
        changedict_for_name[dictname] = changedict
    # in future we might be able to auto-translate old-class objects
    # to new classes... so (TODO, maybe) store classname->newestclass map,
    # so you know which objects to upgrade and how...

    # This is needed now, and has to be done after all the changedicts were
    # stored above:
    register_postinit_item( '_archive_meet_class', class1)

    # Note: we could instead pass a tuple of (class1, other_useful_info)
    # if necessary. All undo_archives (or anything else wanting to change-
    # track all objects it might need to) should call
    # register_postinit_object( '_archive_meet_class', self )
    # when they are ready to receive callbacks (then and later) on
    # self._archive_meet_class for all present-then and future classes of
    # objects they might need to changetrack.
    #
    #   Note: those classes will be passed to all new archives and will
    # therefore still exist (then and forever), and this system therefore
    # memory-leaks redefined (obsolete) classes, even if all their objects
    # disappear, but that should be ok, and (in far future) we can even
    # imagine it being good if their objects might have been saved to files
    # (it won't help in future sessions, which means user/developer should
    # be warned, but it will help in present one and might let them upgrade
    # and resave, i.e. rescue, those objects).

    return

#e now something to take class1 and look up the changedicts and their names
#e and let this run when we make InstanceClassification

##e class multiple_changedict_processor?

# ==

class refreshing_changedict_subscription(object): #bruce 071116; TODO: rename
    """
    Helper class, for one style of subscribing to a changedict_processor
    """
    cdp = None
    def __init__(self, cdp):
        self.cdp = cdp # a changedict_processor (public?)
        self._key = id(self)
        self._dict = {}
        self._subscribe()
    def _subscribe(self):
        self.cdp.subscribe( self._key, self._dict)
    def _unsubscribe(self):
        self.cdp.unsubscribe( self._key)
    def get_changes_and_clear(self):
        self.cdp.process_changes()
        res = self._dict # caller will own this when we return it
        #e optim, when works without it:
        ## if not res:
        ##     return {} # note: it would be wrong to return res!
        self._unsubscribe()
        self._dict = {} # make a new dict, rather than copying/clearing old one
        self._subscribe()
        return res
    def __del__(self):
        # When we're gone, we no longer own id(self) as a key in self.cdp!
        # So free it. (Also presumably an optim.)
        if self.cdp:
            try:
                self._unsubscribe()
            except:
                print_compact_traceback("bug, ignored: error during __del__: ")
                pass
        return
    pass

# end
