# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
TreeModel_api.py - API class for a TreeModel needed by ModelTreeGui

@author: Will, Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from modelTree.Api import Api

class TreeModel_api(Api):
    """
    API (and some default method implementations) for a TreeModel object,
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
    
    def make_cmenuspec_for_set(self, nodeset, optflag):
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
    
    def topmost_selected_nodes(self): # in class TreeModel_api
        """
        @return: a list of all selected nodes which are not inside selected Groups
        """
        ### MAYBE TODO: redefine this in terms of recurseOnNodes and get_current_part_topnode
        # (not easy to do unless func can return something to recurseOnNodes to stop the recursion! add option for that?)
        # [bruce 081217 comment]
        raise Exception("overload me")

    pass # end of class TreeModel_api

# end
