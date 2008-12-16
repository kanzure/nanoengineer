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

    # helper methods -- strictly speaking these are now part of the API,
    # but they have default implems based on more primitive methods
    # (which need never be overridden, and maybe should never be overridden)
    # [moved them into this class from modelTreeGui, bruce 070529]
    
    def recurseOnNodes(self, func, topnode = None,
                       fake_nodes_to_mark_groups = False,
                       visible_only = False ):
        """
        """
        # note: used only in itself and in ModelTreeGui.mt_update
        #bruce 070509 new features:
        # - fake_nodes_to_mark_groups [not used as of 080306],
        # - visible_only [always true as of 080306]
        assert visible_only # see above comment
        if topnode is None:
            for topnode in self.get_topnodes():
                self.recurseOnNodes(func, topnode,
                                    fake_nodes_to_mark_groups = fake_nodes_to_mark_groups,
                                    visible_only = visible_only)
                continue
        else:
            func(topnode)
            
            #bruce 080306 use MT_kids, not .members, to fix some bugs
            # (at least the one about lots of extra scroll height when
            #  a large DnaGroup is in the MT). Note, MT_kids is always
            # defined; it's a length 0 sequence on leaf nodes.
            if visible_only:
                if topnode.open and topnode.openable():
                    members = topnode.MT_kids()
                        # note: we're required to not care what MT_kids returns
                        # unless topnode.open and topnode.openable() are true.
                else:
                    members = ()
            else:
                assert 0 # not well defined what this means, due to MT_kids vs members issue [bruce 080306]
            
            if members:
                if fake_nodes_to_mark_groups:
                    func(0)
                for child in members:
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
        raise Exception("overload me")

    pass # end of class TreeModel_api

# end
