

see also model/prefsTree.py
since then moved to outtakes

=====

from modelTree/TreeModel.py:



_DEBUG_PREFTREE = False # bruce 050602 experiment; do not commit with True


from end of get_topnodes in TreeModel

        if _DEBUG_PREFTREE: #bruce 050602
            try:
                from foundation.Utility import Node
                ## print "reloading prefsTree"
                import model.prefsTree as _X
                reload(_X)
                from model.prefsTree import prefsTree # constructor for an object which has a tree of nodes and controls them
                self.pt = prefsTree(self.assy) # guess; guessing it's ok to remake it each time
                ptnode = self.pt.topnode
                assert ptnode is not None
                assert isinstance(ptnode, Node)
                topnodes.append(ptnode)
            except:
                print_compact_traceback("error importing prefsTree or making one: ")


 from TreeModel.make_cmenuspec... just before copy, cut, delete

        # Customize command [bruce 050602 experiment -- unfinished and commented out ###@@@]
        # [later comment, bruce 050704: I think this was intended to suggest PrefsNodes applicable to the selected item or items,
        #  and to make them and group them with it. Or (later) to put up a dialog whose end result might be to do that.]
        # Provide this when all items are in the same group? no, any items could be grouped...
        # so for initial experiments, always provide it. If it's a submenu, the selected items might affect
        # what's in it, and some things in it might be already checkmarked if PrefsNodes are above them ...
        # for very initial experiment let's provide it only for single items.
        # Do we ask them what can be customized about them? I guess so.
##unfinished...
##        if _DEBUG_PREFTREE and len(nodeset) == 1:
##            mspec = nodeset[0].customize_menuspec()
##            submenu = []



======

from assembly.py


from model.prefsTree import MainPrefsGroupPart


in class Assembly:

        prefs_node = None #bruce 050602; default value of instance variable; experimental


near end of topnode_partmaker_pairs:

        if self.prefs_node is not None:
            res.append(( self.prefs_node, MainPrefsGroupPart ))

near end of topnodes_with_own_parts

        if self.prefs_node is not None:
            res.append( self.prefs_node)

in valid_selgroup:

        if not (self.root.is_ascendant(sg) or self.prefs_node is sg): #bruce 050602 kluge: added prefs_node
            return False # can this ever happen??

