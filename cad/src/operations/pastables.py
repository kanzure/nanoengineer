# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
pastables.py -- identifying and using nodes that can be pasted

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

Bruce circa 050121 split these out of existing code in depositMode,
probably by Josh, and generalized them (but left them in that file)

Ninad 2007-08-29 moved them into Utility.py and extended or
modified them

bruce 071026 moved them from Utility into a new file

TODO:

- All these functions probably need cleanup and generalization.
More importantly, they need to be methods in the Node API with
implementations on a few subclasses of Node.

- A longstanding NFR is to be able to define a hotspot in a Group
and paste it onto a bondpoint.
"""

from model.chunk import Chunk # only for isinstance
from foundation.Group import Group # only for isinstance

def is_pastable(obj):
    """
    whether to include a clipboard object on Build's pastable spinbox
    """
    #bruce 050127 make this more liberal, so it includes things which are
    # not pastable onto singlets but are still pastable into free space
    # (as it did before my changes of a few days ago)
    # but always run is_pastable_onto_singlet in case it has a klugy bugfixing side-effect
    return is_pastable_onto_singlet(obj) or is_pastable_into_free_space(obj)

# these separate is_pastable_xxx functions make a distinction which might not yet be used,
# but which should be used soon to display these kinds of pastables differently
# in the model tree and/or spinbox [bruce 050127]
# (they're only used in this file, but that comment suggests
#  they ought to be public anyway)

def is_pastable_into_free_space(obj):#bruce 050127
    return isinstance(obj, Chunk) or isinstance(obj, Group)

def is_pastable_onto_singlet(obj): #bruce 050121 (renamed 050127)
    # this might have a klugy bugfixing side-effect -- not sure
    ok, spot_or_whynot = find_hotspot_for_pasting(obj)
    return ok

def find_hotspot_for_pasting(obj):
    """
    Return (True, hotspot) or (False, reason),
    depending on whether obj is pastable in Build mode
    (i.e. on whether a copy of it can be bonded to an existing singlet).
    In the two possible return values,
    hotspot will be one of obj's singlets, to use for pasting it
    (but the one to actually use is the one in the copy made by pasting),
    or reason is a string (for use in an error message) explaining why there isn't
    a findable hotspot. For now, the hotspot can only be found for certain
    chunks, but someday it might be defined for certain groups, as well,
    or anything else that can be bonded to an existing singlet.
    """
    #Note: method modified to support group pasting -- ninad 2007-08-29

    if not (isinstance(obj, Chunk) or isinstance(obj, Group)):
        return False, "only chunks or groups can be pasted" #e for now
    if isinstance(obj, Chunk):
        ok, spot_or_whynot = _findHotspot(obj)
        return ok, spot_or_whynot
    elif isinstance(obj, Group):
        groupChunks = []
        def func(node):
            if isinstance(node, Chunk):
                groupChunks.append(node)

        obj.apply2all(func)

        if len(groupChunks):
            for m in groupChunks:
                ok, spot_or_whynot = _findHotspot(m)
                if ok:
                    return ok, spot_or_whynot
        return False, "no hotspot in group's chunks"
    pass

def _findHotspot(obj):
    if isinstance(obj, Chunk):
        if len(obj.singlets) == 0:
            return False, "no bondpoints in %r (only pastable in empty space)" % obj.name
        elif len(obj.singlets) > 1 and not obj.hotspot:
            return False, "%r has %d bondpoints, but none has been set as its hotspot" % (obj.name, len(obj.singlets))
        else:
            return True, obj.hotspot or obj.singlets[0]
    pass

# end
