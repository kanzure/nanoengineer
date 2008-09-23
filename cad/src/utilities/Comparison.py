# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
utilities/Comparison.py - provides same_vals, for correct equality comparison.
See also state_utils.py, which contains the closely related copy_val.

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details. 

History:

same_vals was written as part of state_utils.py [bruce]

moved same_vals into utilities/Comparison.py to break an import cycle
[ericm 071005]

moved SAMEVALS_SPEEDUP and "import samevals" along with it
(but left the associated files in cad/src, namely samevals.c [by wware],
setup2.py [now in outtakes], and part of Makefile) [bruce 071005]
"""

from types import InstanceType # use this form in inner loops

_haveNumeric = True

try:
    from Numeric import array, PyObject
except:
    # this gets warned about in state_utils
    _haveNumeric = False

import foundation.env as env

_debug_same_vals = False #bruce 060419; relates to bug 1869

SAMEVALS_SPEEDUP = True
    # If true, try to use the C extension version in samevals.c
    # [which is not yet fully correct, IIRC -- bruce 071005 comment];
    # will be set to False if "import samevals" fails below.
    
    # Note: samevals.c [by wware] is still built and resides in cad/src,
    # not cad/src/utilities, as of 071005, but that should not
    # prevent import samevals from working here. If samevals.c is moved
    # here into utilities/, then setup2.py [now in outtakes, nevermind]
    # and part of Makefile need to be moved along with it. [bruce 071005 comment]
    #bruce 080403 update: samevals.c has been replaced by samevals.pyx
    # and samevalshelp.c, built by Makefile, all still at toplevel.

if SAMEVALS_SPEEDUP:
    try:
        # If we're using the samevals extension, we need to tell the
        # extension what a Numeric array looks like, since the symbol
        # PyArray_Type was not available at link time when we built
        # the extension. [wware]

        from samevals import setArrayType
        import Numeric
        setArrayType(type(Numeric.array((1,2,3))))
        print "SAMEVALS_SPEEDUP is True, and import samevals succeeded"
    except ImportError:
        # Note: this error could be from importing samevals
        # (an optional dll built from samevals.c) or Numeric.
        # If the latter, it was avoidable using _haveNumeric,
        # but I don't know whether samevals.c permits use when
        # setArrayType was never called, so I'll let this code
        # continue to disable SAMEVALS_SPEEDUP in either case.
        # [bruce 071005]
        print "samevals.so/dll or Numeric not available, not using SAMEVALS_SPEEDUP"
        SAMEVALS_SPEEDUP = False

# ==

def same_vals(v1, v2): #060303
    """
    (Note: there is a C version of this method which is normally used by NE1.
     It has the same name as this method and overwrites this one
     due to an assignment near the end of this method's source file.
     This method is the reference version, coded in Python.
     This version is used by some developers who don't build the C version
     for some reason.)
    
    Efficiently scan v1 and v2 in parallel to determine whether they're the same, for purposes of undoable state
    or saved state.
       The only reason we really need this (as opposed to just using Python '==' or '!=' and our own __eq__ methods)
    is because Numeric.array.__eq__ is erroneously defined, and if we were using '==' or '!=' on a Python tuple containing 
    a Numeric array, we'd have no way of preventing this issue from making '==' or '!=' come out wrong on the tuple.

    (For details, see bruce email to 'all' of 060302, partially included below.)

    [...]
    It turns out that you can safely naively use != on Numeric arrays,
    but not ==, since they both act elementwise, and this only 
    does what you usually want with != . I knew this in the past
    (and fixed some weird bugs caused by it) but forgot it recently,
    so Undo was thinking that atom position arrays had not changed
    provided at least one coordinate of one atom had not changed.
    [...]
    - Bruce

    In particular:

    a = Numeric.array((1, 2, 3))
    b = Numeric.array((1, 2, 3))
    assert a == b                  # result: [1 1 1], interpreted as True
    assert not a != b              # result: [0 0 0], interpreted as False
    b = Numeric.array((1, 4, 5))
    assert a != b                  # result: [1 0 0], interpreted as True
    assert not a == b              # result: [0 1 1], interpreted as True
    # the last assertion fails!

    Do the maintainers of Numeric consider this to be correct
    behavior?!?!?!?  Probably.

    What they should have done was define a new ufunc for equality
    testing, and made the semantics of __eq__ and __ne__ work as
    expected.  Probably too late to expect them to change this now.

       As long as we have it, we might as well make it a bit more stringent than Python '==' in other ways too,
    like not imitating the behaviors (which are good for '==') of 1.0 == 1, array([1]) == [1], etc. The only reason
    we'll count non-identical objects as equal is that we're not interested in their addresses or in whether someone
    will change one of them and not the other (for whole objects or for their parts).
       ###doc for InstanceType... note that we get what we want by using __eq__ for the most part...
    """

    if v1 is v2:
        # Optimization:
        # this will happen in practice when whole undoable attrvals are immutable
        # (so that we're comparing originals, not different copies),
        # therefore it's probably common enough to optimize for.
        # It's just as well we're not doing it in the recursive helper,
        # since it would probably slow us down when done at every level. [060303 11pm]
        return True 
    try:
        _same_vals_helper(v1, v2)
    except _NotTheSame:
        if _debug_same_vals and not (v1 != v2):
            print "debug_same_vals: same_vals says False but 'not !=' says True, for",v1,v2
                # happens for bug 1869 (even though it's fixed; cause is understood)
        return False
    if _debug_same_vals and (v1 != v2):
        print "debug_same_vals: same_vals says True but '!=' also says True, for",v1,v2 ##@@ remove when pattern seen
    return True

class _NotTheSame(Exception): pass

def _same_list_helper(v1, v2):
    n = len(v1)
    if n != len(v2):
        raise _NotTheSame
    for i in xrange(n):
        _same_vals_helper(v1[i], v2[i])
    return

_same_tuple_helper = _same_list_helper

def _same_dict_helper(v1, v2):
    if len(v1) != len(v2):
        raise _NotTheSame
    for key, val1 in v1.iteritems():
        if not v2.has_key(key):
            raise _NotTheSame
        _same_vals_helper(val1, v2[key])
    # if we get this far, no need to check for extra keys in v2, since lengths were the same
    return

# Choice 1:
# no need for _same_InstanceType_helper; we set them up so that their __eq__ method is good enough;
# this only works if we assume that any container-like ones (which compare their parts) are ones we wrote,
# so they don't use == on Numeric arrays or != on general values...
# Choice 2:
# on naive objects, we just require id(v1) == id(v2).
### UNDECIDED. For now, doing nothing is equivalent to Choice 1.
# but note that choice 2 is probably safer.
# in fact, if I do that, i'd no longer need _eq_id_mixin just due to StateMixin. (only when __getattr__ and someone calls '==')
# [060303]
# Update 060306: some objects will need _s_same_as(self, other) different from __eq__,
# since __eq__ *might* want to compare some components with != (like int and float) rather than be as strict as same_vals.
# Even __eq__ needs to try to avoid the "Numeric array in list" bug, which in some cases will force it to also call same_vals,
# but when types are known it's plausible that it won't have to, so the distinct methods might be needed.
# When we first need _s_same_as, that will force use of a new _same_InstanceType_helper func.
# Do we need it before then? Not sure. Maybe not; need to define __eq__ better in GAMESS Jig (bug 1616) but _s_same_as
# can probably be the same method. OTOH should we let DataMixin be the thing that makes _s_same_as default to __eq__?? ###
######@@@@@@
# update, bruce 060419, after thinking about bug 1869 (complaint about different bonds with same key):
# - The Bond object needs to use id for sameness, in Undo diffs at least (only caller of same_vals?) (but can't use id for __eq__ yet).
#   - Q: What is it about Bond that decides that -- Bond? StateMixin? not DataMixin?
#     A: The fact that scan_children treats it as a "child object", not as a data object (see obj_is_data method).
#     That's what makes Undo change attrs in it, which only makes sense if Undo treats refs to it (in values of other attrs,
#      which it's diffing) as the same iff their id is same.
# Conclusion: we need to use the same criterion in same_vals, via a new _same_InstanceType_helper -- *not* (only) a new method
# as suggested above and in a comment I added to bug 1869 report. For now, we don't need the new method at all.

def _same_InstanceType_helper(obj1, obj2): #bruce 060419, relates to bug 1869; see detailed comment above
    if obj1 is obj2:
        return # not just an optimization -- remaining code assumes obj1 is not obj2
    # We might like to ask classify_instance(obj1).obj_is_data, but we have no canonical object-classifier to ask,
    # so for A7 (no time to clean this up) we'lljust duplicate its code instead (and optimize it too).
    class1 = obj1.__class__
    ###k don't check copiers_for_InstanceType_class_names.has_key(class1.__name__), since that's always False for now.
    obj_is_data = hasattr(class1, '_s_isPureData')
    if obj_is_data:
        if obj1 != obj2: # rely on our implem of __eq__
            raise _NotTheSame
        else:
            return
    else:
        # otherwise the 'is' test above caught sameness
        raise _NotTheSame
    pass


def _same_Numeric_array_helper(obj1, obj2):
    if obj1.typecode() != obj2.typecode():
        raise _NotTheSame
    if obj1.shape != obj2.shape:
        raise _NotTheSame
    if obj1.typecode() == PyObject:
        if env.debug():
            print "atom_debug: ran _same_Numeric_array_helper, PyObject case" # remove when works once ###@@@
        # assume not multi-dimensional (if we are, this should work [untested] but it will be inefficient)
        for i in xrange(len(obj1)):
            _same_vals_helper(obj1[i], obj2[i]) # two PyObjects (if obj1 is 1-dim) or two lower-dim Numeric arrays
    else:
##        if env.debug():
##            print "atom_debug: ran _same_Numeric_array_helper, non-PyObject case" # remove when works once ###@@@
        if obj1 != obj2:
            # take pointwise !=, then boolean value of that (correct, but is there a more efficient Numeric function?)
            # note: using '==' here (and negating boolean value of result) would NOT be correct
            raise _NotTheSame
    return

_known_type_same_helpers = {}

_known_type_same_helpers[type([])] = _same_list_helper
_known_type_same_helpers[type({})] = _same_dict_helper
_known_type_same_helpers[type(())] = _same_tuple_helper
_known_type_same_helpers[ InstanceType ] = _same_InstanceType_helper

if (_haveNumeric):
    # note: related code exists in state_utils.py.
    numeric_array_type = type(array(range(2))) # __name__ is 'array', but Numeric.array itself is a built-in function, not a type
    assert numeric_array_type != InstanceType
    _known_type_same_helpers[ numeric_array_type ] = _same_Numeric_array_helper
    del numeric_array_type

def _same_vals_helper(v1, v2): #060303
    """
    [private recursive helper for same_vals] raise _NotTheSame if v1 is not the same as v2
    (i.e. if their type or structure differs, or if any corresponding parts are not the same)
    """
    typ = type(v1)
    if typ is not type(v2):
        raise _NotTheSame
    same_helper = _known_type_same_helpers.get(typ) # this is a fixed public dictionary
    if same_helper is not None:
        same_helper(v1, v2) # we optimize by not storing any scanner for atomic types, or a few others.
        return
    # otherwise we assume v1 and v2 are things that can't be or contain a Numeric array, so it's sufficient to use !=.
    # (If not for Numeric arrays of type PyObject, we could safely use != right here on a pair of Numeric arrays --
    #  just not on things that might contain them, in case their type's != method used == on the Numeric arrays,
    #  whose boolean value doesn't correctly say whether they're equal (instead it says whether one or more
    #  corresponding elements are equal). Another difference is that 1 == 1.0, but we'll say those are not the same,
    #  but that aspect of our specification doesn't matter much.)
    if v1 != v2:
        raise _NotTheSame
    ###k is it reasonable to treat naive non-InstanceType objects as the same if they are merely __eq__ ?
    # guess: yes, and is even good, but it's not obviously good nor obviously necessary. See also the comments
    # above _same_InstanceType_helper. [bruce 060419]
    return

# ==

if SAMEVALS_SPEEDUP:
    # Replace definition above with the extension's version.
    # (This is done for same_vals here in utilities/Comparison.py,
    #  and for copy_val in state_utils.py.)
    from samevals import same_vals
        # this overwrites the public global which other modules import
    # note: there is no point in saving the python version before this
    # assignment (e.g. for testing), since it uses this global for its
    # recursion, so after this import it would be recursing into the
    # C version instead of into itself. Fixing this would require
    # modifying the global before each test -- not presently worth
    # the trouble. [bruce 080922 comment]
    pass
    
# end
