# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
TreeModel_api.py - API class for a TreeModel needed by ModelTreeGui

@author: Will, Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from modelTree.Api import Api

from operations.ops_select import topmost_selected_nodes

class TreeModel_api(Api):
    """
    API (and some base class implementations) for a TreeModel object,
    suitable to be displayed and edited by a ModelTreeGui as its treemodel

    @warning: perhaps not all API methods are documented here.
    """
    #bruce 081216 split this out of ModelTree_api, which has since been removed,
    # and then moved it into its own file
    
    def get_topnodes(self):
        """
        Return a list of the top-level nodes, typically assy.tree and assy.shelf for an assembly.
        """
        raise Exception("overload me")

    def get_nodes_to_highlight(self): #bruce 080507
        """
        Return a dictionary of nodes which should be drawn as highlighted right now.
        (The keys are those nodes, and the values are arbitrary.)
        """
        return {}

    def get_current_part_topnode(self): #bruce 070509 added this to API ##e rename?
        """
        Return a node guaranteed to contain all selected nodes, and be fast.
        """
        raise Exception("overload me")
    
    def make_cmenuspec_for_set(self, nodeset, nodeset_whole, optflag):
        """
        Return a Menu_spec list (of a format suitable for makemenu_helper)
        for a context menu suitable for nodeset, a list of 0 or more selected nodes
        (which includes only the topmost selected nodes, i.e. it includes no
        children of selected nodes even if they are selected).
           <optflag> can be 'Option' or None, in case menus want to include
        additional items when it's 'Option'.
           Subclasses should override this to provide an actual menu spec.
        The subclass implementation can directly examine the selection status of nodes
        below those in nodeset, if desired, and can assume every node in nodeset is picked,
        and every node not in it or under something in it is not picked
        (or at least, will be unpicked when the operation occurs,
         which happens for picked nodes inside unpicked leaf-like Groups
         such as DnaStrand).
        [all subclasses should override this]
        """
        raise Exception("overload me")
    
    def recurseOnNodes(self,
                       func,
                       topnode = None,
                       fake_nodes_to_mark_groups = False,
                       visible_only = False ):
        """
        Call func on every node on or under topnode,
        or if topnode is None, on every node in or under
        all nodes in self.get_topnodes();
        but only descend into openable nodes
        (further limited to open nodes, if visible_only is true).

        @param fake_nodes_to_mark_groups: bracket sequences of calls
               of func on child node lists with calls of func(0) and func(1)
        @type fake_nodes_to_mark_groups: boolean

        @param visible_only: only descend into open nodes
        @type visible_only: boolean

        @return: None

        @note: a node is open if node.open is true.
        @note: a node is openable if node.openable() is true.

        @see: node.MT_kids() for node's list of child nodes
              (defined and meaningful whenever it's openable)
        @see: topmost_selected_nodes
        """
        # note: used only in itself and in ModelTreeGui.mt_update
        #bruce 070509 new features:
        # - fake_nodes_to_mark_groups [not used as of 080306],
        # - visible_only [always true as of 080306] [can be False as of 081217]
        # review, low priority: would this be more useful as a generator?
        
        if topnode is None:
            for topnode in self.get_topnodes():
                self.recurseOnNodes(func, topnode,
                                    fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                    visible_only = visible_only)
                continue
        else:
            func(topnode)
            
            if visible_only and not topnode.open:
                children = ()
            elif not topnode.openable():
                children = ()
            else:
                children = topnode.MT_kids()
                    #bruce 080306 use MT_kids, not .members, to fix some bugs
                    # note: we're required to not care what MT_kids returns
                    # unless topnode.openable() is true, but as of 081217
                    # we can use it regardless of node.open.
            if children:
                if fake_nodes_to_mark_groups:
                    func(0)
                for child in children:
                    self.recurseOnNodes(func, child,
                                        fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                        visible_only = visible_only)
                    continue
                if fake_nodes_to_mark_groups:
                    func(1)
            pass
        return
    
    def topmost_selected_nodes(self, topnode = None, whole_nodes_only = False):
        """
        @return: list of all selected nodes which are not inside selected Groups

        @param topnode: if provided, limit return value to nodes on or under it
        @type topnode: a Node or None
        
        @param whole_nodes_only: if True (NOT the default), don't descend inside
                               non-openable groups (which means, picked nodes
                               inside unpicked non-openable Groups, aka "partly
                               picked whole nodes", will not be included in our
                               return value)
        @type whole_nodes_only: boolean

        @see: deselect_partly_picked_whole_nodes

        @see: recurseOnNodes
        """
        #bruce 081218 revising this, adding options, re bug 2948
        # REVIEW: should this be defined in the implem class instead?
        # (either way, it needs to be in the API)
        # TODO: factor out common code with recurseOnNodes, using a generator?
        if topnode is None:
            topnode = self.get_current_part_topnode()
        
        if not whole_nodes_only:
            # old version, still used for many operations;
            # REVIEW: might need better integration with new version
            # (this one uses .members rather than MT_kids)
            res = topmost_selected_nodes( [topnode] ) # defined in ops_select
        else:
            res = []
            def func(node):
                if node.picked:
                    res.append(node)
                elif node.openable():
                    children = node.MT_kids() # even if not open
                    for child in children:
                        func(child)
                return
            func(topnode)
        return res

    def deselect_partly_picked_whole_nodes(self): #bruce 081218
        """
        Deselect the topmost selected nodes which are not "whole nodes"
        (i.e. which are inside non-openable nodes).
        """
        keep_selected = self.topmost_selected_nodes( whole_nodes_only = True)
        all_selected = self.topmost_selected_nodes()
        deselect_these = dict([(n,n) for n in all_selected]) # modified below
        for node in keep_selected:
            del deselect_these[node]
        for node in deselect_these:
            node.unpick()
        return
        # note: the first implem caused visual glitches due to
        # intermediate updates in both MT and GLPane:
        ## self.unpick_all()
        ## for node in keep_selected:
        ##     node.pick()

    def unpick_all(self): #bruce 081218 moved this here from ModelTreeGUI
        for node in self.topmost_selected_nodes( whole_nodes_only = False):
            node.unpick()
        return

    pass # end of class TreeModel_api

# end
