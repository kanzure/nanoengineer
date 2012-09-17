# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
state_constants.py -- definitions needed by state_utils and its client code,
including constants for declaring attributes' roles in
holding state or referring to objects that hold state. (Also some
names for the available kinds of specialcase treatment re Undo.)

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

See state_utils.py for more info and related classes/utilities.
(It's undecided whether these declarations make sense
in objects that don't inherit from one of the mixins defined in
state_utils.py.)

These declarations are used by Undo to know what attributes' changes
should be recorded and later undone, and to find objects which need to
be watched for changes.

Someday they might also be used for automatically knowing
how to save objects to files, how to copy or diff or delete them,
how to browse or edit their state from a UI, etc.

Review:

Should IdentityCopyMixin and similar small classes be moved
into this file?
"""

# NOTE: This module should not import anything non-builtin,
# or define any name unsuitable for being a global in all modules.

# ==

# Possible values for _s_attr_xxx attribute declarations (needed by Undo)

S_DATA = 'S_DATA' # for attributes whose value changes should be saved or undone.


S_CHILD = 'S_CHILD' # like S_DATA, but for attributes whose value is None or a "child object" which might also contain undoable state.

S_CHILDREN = 'S_CHILDREN' # like S_CHILD, but value might be a list or dict (etc) containing one or more child objects.

S_CHILDREN_NOT_DATA = 'S_CHILDREN_NOT_DATA' # scan for children, but not for state or diffs [bruce 060313, experimental but used]


# ref and parent options are not yet needed, and will be treated the same as S_DATA,
# which itself will be treated more like S_REFS anyway if it hits any objects.
# We'll still define them so we can see if you want to declare any attrs using them, mainly S_PARENT.

S_REF = 'S_REF' # like S_DATA, but for attributes whose value is None or a "referenced object",
    # which might or might not be encountered in a scan of undoable objects going only into children.
    # (It's not yet clear exactly how this differs from S_DATA, or whether it matters if ref'd objects are encountered
    #  in a scan into children. Are these "siblings or cousins" (like a jig's atoms) or "foreign objects" (like some QDialog)
    #  or "other state-holders" (like GLPane or MainWindow) or "constants" (like Elements and Atomtypes)?)

S_REFS = 'S_REFS' # like S_REF, but value might be a list or dict (etc) containing one or more referenced objects.


S_PARENT = 'S_PARENT' # like S_DATA, but for attributes whose value is None or a "parent object"
    # (one which should be encountered in a scan of undoable objects going only into children,
    #  and of which this object is a child or grandchild etc).

S_PARENTS = 'S_PARENTS' # like S_PARENT, but value might be a list or dict (etc) containing one or more parent objects.


S_CACHE = 'S_CACHE' # for attributes which should be deleted (or otherwise invalidated) when other attributes' changes are undone.

S_IGNORE = 'S_IGNORE' # state system should pretend this attr doesn't exist (i.e. never look at it or change it or delete it).
    # (This is equivalent to providing no state declaration for the attr, unless we add a future "default decl" for all attrs
    #  not declared individually, in which case this will let you exclude an attr from that.
    #  It's also useful for subclasses wanting to override state decls inherited from a superclass.)

# ==

# Kinds of specialcases that Undo can handle; for use as the value
# of a class constant for _s_undo_specialcase: [bruce 071114]

UNDO_SPECIALCASE_ATOM = 'UNDO_SPECIALCASE_ATOM'
UNDO_SPECIALCASE_BOND = 'UNDO_SPECIALCASE_BOND'
##UNDO_SPECIALCASE_ATOM_OWNER = 'UNDO_SPECIALCASE_ATOM_OWNER' # not sure this is right, vs CHUNK -- also it may never be needed

ATOM_CHUNK_ATTRIBUTE_NAME = 'molecule' # must match the Atom.molecule attrname

# ==

# Note: _UNSET_class should inherit from IdentityCopyMixin, but that would
# only work when IdentityCopyMixin has been split out from state_utils,
# since state_utils imports this file. Instead, we copy the methods here.

class _UNSET_class:
    """
    [private class for _UNSET_, which sometimes represents
     unset attribute values within Undo snapshots, and similar things]
    """
    # review: can we add a decl that makes the _s_attr system notice
    # the bug if it ever hits this value in a real attrval? (should we?)
    def __init__(self, name = "_???_"):
        self.name = name
    def __repr__(self):
        return self.name
    def _copyOfObject(self): # copied from IdentityCopyMixin
        return self
    def _isIdentityCopyMixin(self): # copied from IdentityCopyMixin
        pass
    pass

# ensure only one instance of _UNSET_ itself, even if we reload this module
try:
    _UNSET_
except:
    _UNSET_ = _UNSET_class("_UNSET_")

try:
    _Bugval
except:
    _Bugval = _UNSET_class("_Bugval")

# end
