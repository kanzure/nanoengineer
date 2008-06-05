# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
prefsTree.py -- experimental code related to showing
user preferences in the model tree
(not presently used as of 050612, but works; very incomplete)

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050613 started this.

Module classification: [bruce 071215]

Tentatively, "model", though arguably it also contains ui code.
Used by model_tree but also in assembly (which is in "model").
Perhaps ought to be split into two files?
"""

import os
from foundation.Utility import Node
from foundation.Group import Group
from model.part import Part
from utilities.constants import noop, dispLabel, default_display_mode
import foundation.env as env

_debug_prefstree = True # safe for commit even when True

class PrefNode(Node):
    """
    Leaf node for storing a local change to a single preference attribute
    """
    #e or is PrefsGroup the same class? not sure...
    ## no_selgroup_is_ok = True
    def __init__(self, assy, name = "prefnode"):
        Node.__init__(self, assy, name)
        return
    def __CM_Add_Node(self):
        self.addsibling( PrefNode(self.assy, "prefnode") )
    pass

class PrefChoiceNode(PrefNode):
    """
    A PrefNode which lets the user choose one of a small finite set of choices
    using its cmenu (or maybe in other ways too?)
    """
    def __init__(self, assy, name, choices = None, default_name = None, defaultValue = None, typename = None ):
        PrefNode.__init__(self, assy, name)
        self.choices = choices or [('No choices!', None)]
        self.choicedict = {}
        self.typename = typename #k not used?
        for name, val in self.choices:
            self.choicedict[name] = val
        if default_name is not None:
            self.default_name = default_name
            self.defaultValue = self.choicedict[default_name] # it better be in there!
        elif defaultValue is not None or None in self.choicedict.values():
            for name, val in self.choices:
                if val == defaultValue:
                    self.default_name = name
                    self.defaultValue = val
                    break
        else:
            self.default_name, self.defaultValue = self.choices[0]
        return
    def __cmenu_items(self): ###IMPLEM a call of this
        submenu = []
        for choice in self.choicelist:
            submenu.append((choice, noop)) ###noop -> lambda
        res = []
        res.append(("choices",submenu))
        return res
    pass

# these exprs are of the form [ class, opts( opt1 = val1, ... ) ]

def opts(**kws):
    return dict(kws)

bool_choice = [ PrefChoiceNode, opts(
                  typename = "boolean", #??
                  choices = [('True', True), ('False', False)],
                  default_name = 'False'
               )]
    # not very useful, better to use checkmark presence or not on the pref item itself, not this submenu from it
    # (that requires using the QListViewItem subclass with a checkmark)
    # or alternatively, having a submenu with some boolean toggle items in it (our menu_spec could offer that option)

dispmode_choice = [ PrefChoiceNode, opts(
                      typename = "display mode",
                      choices = zip( dispLabel, range(len(dispLabel)) ),
                      defaultValue = default_display_mode
                   )]

# ==

class PrefsGroup(Group):
    """
    Group node for storing a set of local changes to preference attributes
    """
    ## no_selgroup_is_ok = True
    def __init__(self, assy, name): # arg order is like Node, not like Group
        dad = None
        Group.__init__(self, name, assy, dad)
            # dad arg is required (#e should not be) and arg order is inconsistent (should not be)
    def __CM_Add_Node(self):
        self.addchild( PrefNode(self.assy, "prefnode") )
        self.assy.w.mt.mt_update() #k why needed? (and does it help?)
    pass

# ==

# print _node._MainPrefsGroup__CM_Save_Prefs()

def prefsPath(assy):
    return os.path.join( assy.w.tmpFilePath, "Preferences", "prefs.mmp" ) #e use common code for the dir

class MainPrefsGroup(PrefsGroup): # kind of like PartGroup; where do we say it's immortal? in the part, not the node.
    def is_top_of_selection_group(self): return True
    def rename_enabled(self): return False
    def drag_move_ok(self): return False
    def permits_ungrouping(self): return False
    def description_for_history(self):
        """
        [overridden from Group method]
        """
        return "Preferences"
    def __CM_Save_Prefs(self):
        """
        [temporary kluge, should autosave whenever changed, or from dialog buttons]
        save this node's part into a constant-named mmp file in prefs dir
        (for now -- details of where/how it saves them is private and might change)
        """
        path = prefsPath(self.assy)
        self.part.writemmpfile( path) ####@@@@ need options? their defaults were changed on 051209 w/o reviewing this code.
        env.history.message( "saved Preferences Group" )
    # kluge: zap some useless cmenu items for this kind of node (activates special kluge in mtree cmenu maker)
    __CM_Hide = None
    __CM_Group = None
    __CM_Ungroup = None
    pass

class MainPrefsGroupPart(Part):
    """
    [public, meant to be imported and used by code in assembly.py]
    """
    def immortal(self): return True
    def glpane_text(self):
        return "(preferences area; not in the mmp file)"
    def location_name(self):
        return "prefs tree" #k used??
    def movie_suffix(self):
        """
        what suffix should we use in movie filenames? None means don't permit making them.
        """
        None #k does this still work?
    pass

def prefsTree(assy):
    """
    Make or return the prefsTree object for the given assy
    """
    #e really there should be a single one per session, but this should work
    try:
        ## assert isinstance(assy.prefsTree, prefsTree_class) # multiple ways this can fail, and that's normal
        # above messes up reloading, so do this instead:
        assert assy.prefsTree.__class__.__name__ == "prefsTree_class"
        return assy.prefsTree
    except:
        if _debug_prefstree:
            print "remaking prefsTree object for", assy # this is normal
        pass
    assy.prefsTree = prefsTree_class(assy)
    assy.prefs_node = assy.prefsTree.topnode #e might be better for assy to look it up this way itself
    assy.update_parts()
        # this will set assy.prefs_node.part to a MainPrefsGroupPart instance, if it has no .part yet (as we expect)
    return assy.prefsTree

class prefsTree_class:
    topnode = None
    def __init__(self, assy):
        self.assy = assy
        self.topnode = MainPrefsGroup(assy, "Preferences")
        path = prefsPath(self.assy)
        stuff = read_mmp_single_part( assy, path) # a list of one ordinary group named Preferences
        (prefsgroup,) = stuff
        mems = prefsgroup.steal_members()
        for mem in mems:
            self.topnode.addchild( mem)
    pass

def read_mmp_single_part(assy, filename):
    from files.mmp.files_mmp import readmmp
    # start incredible kluge block
    history = env.history
        #bruce 050901 revised this.
        # It depends on there being only one active history object at a time.
        # (Before 050913, that object was stored as both env.history and win.history.)
    oldmessage = history.message
    from utilities.constants import noop
    history.message = noop # don't bother user with this file being nonstd (bad, should pass a flag, so other errors seen)
    try:
        ok, grouplist  = readmmp(assy, filename, isInsert = True)
    finally:
        history.message = oldmessage
    if grouplist:
        viewdata, mainpart, shelf = grouplist
        return mainpart.steal_members() # a python list of whatever toplevel stuff was in the mmp file
    return None

# need object to describe available state in the program, and its structure as a tree
# (eg list of modes available; widget layout; rendering loop -- this is partly user-mutable and partly not)
# and then the prefsnodes are an interface to that object,
# and can load their state from it or save their state to it.
# it might also be nodes, not sure

# ==

# remaking nodes destroys any renames I did for them, would mess up DND results too --
# need to keep them around and update them instead (ok if I remake the owner object, though)
# or perhaps let them be proxies for other state (harder, but might be needed anyway, to save that state)

# end
