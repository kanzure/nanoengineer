class TrivalentGraphDrawingTool_OBS(Tool): # REVIEW: can it turn into HuntForNode with node = None to save coding?
    #doc - Active means we know the parent (pane or widget) as self.pane;
    # the pane is also what distributes events... it does so through the tool, on its event handler stack

    # handlers for when we're applied to a pane
    def on_mouse_press(self, x, y, button, modifiers):
        # todo: care about button, modifiers
        # todo: if an edge is being drawn, complete it? no, some other handler did that, then returned None to pass event to us.
        pane = self.pane
        model = pane.model #k
        obj = pane.find_object(x, y) # TODO: move this into COMMON CODE with an on_draw_handle method
        node = None # node we hit or made
        if not obj:
            # empty space
            node = model.cmd_addNode(x, y)
        elif isinstance(obj, model.Node):
            node = obj
        elif isinstance(obj, model.Edge):
            node = model.cmd_addNodeOnEdge(x, y, obj)
        # drag this node around, while mouse is down,
        # then (in some cases) draw an edge from it when mouse is up
        should_draw_edge = len(node.edges) < 3
            # todo: better: if hit node you are already indirectly connected to, draw edge and stop;
            # otherwise draw edge and continue.
        ## handler = DragNodeThenHuntForNode(node, x, y)
        # define handlers here in order in which they execute in time:
        handler1 = DragNode(pane, node, x, y)
        if should_draw_edge:
            handler2 = HuntForNode(pane, node)
            pane.push_handlers(handler2)
        pane.push_handlers(handler1) # this runs, then pops to uncover other one
            #k: what if 1st one changes mind about running 2nd one?
            #e clearly we need some sort of expr for a state diagram for things to run in pane...
        return EVENT_HANDLED
    def on_mouse_motion(self, x, y, dx, dy):
        # todo: highlight
        pass
    pass

                       ###k syntax for this "command description" (DragNode, CMD_RETVAL) (a class with some init args)
                       # DECIDE: should we just return something like tool.DragNode(self.node) instead?
                       # that's already an instance, but it's inactive until put into the right place...
                       # but as optim, note that this is usually discarded (during mouse motion)...
                       # otoh that class would not be too slow to instantiate.
                       # BUT it can't say self.node, it needs CMD_RETVAL and later subst of that...
                       # so nevermind for now.
