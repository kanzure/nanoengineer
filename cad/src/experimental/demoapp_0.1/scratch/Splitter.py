# splitter directions
SPLITTER_H = 1 # cares about y coordinate == pos[1]
SPLITTER_V = 0 # cares about x coordinate == pos[0]

class Splitter(PaneWithChildren):
    "abstract class for HSplitter and VSplitter"
    direction = None # SPLITTER_H or SPLITTER_V in subclasses
    def __init__(self, children):
        assert children # must have children at birth, for now
        self._main_children = children # WRONG, not updated if anyone calls addChild... is that allowed?
        for child in children:
            self.addChild(child) # or super addChild?
        for child1, child2 in zip(children[:-1], children[1:]):
            self.addChild(_SplitterBar(self, child1, child2))
        self._recompute_layout()
    def _recompute_layout(self):
        "set child.rect from self.rect, non-incrementally"
            # btw what is self.rect for a Window? it has get_size, properties width, height.
        # stub - distribute size evenly
        amount = self.size[direction]
        num_children = len(self._main_children)
        total = amount + BAR_SIZE
        for i in range(num_children):
            child = self._main_children[i]
            child.size =
##    def subpanes_for_draw(self):
##        "yield sequence of (region, transform, subpane)"
##            # or equiv objects? something that filters/transforms events...
##        for child in
##    def subpanes_for_hit_test(self):
##        return self.subpanes_for_draw()
##    def pane_children(...)
    pass

class VSplitter(Splitter):
    direction = SPLITTER_V

class HSplitter(Splitter):
    direction = SPLITTER_H

class _SplitterBar(object):#k super? it's a control, has handlers, gets drawn...
    def __init__(self, splitter, child1, child2):
        self.splitter = splitter
        self.children = [child1, child2] # in order of increasing coordinate values...
    def want_size(self, w, h):
        "w and h is available, how much do you want?" # guess... need to see parent alg
        available = [w, h]
        available[self.splitter.direction] = 5
        return available
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        direction = self.splitter.direction
        delta = (dx, dy)[direction] # desired effect on child1 size
        smaller_child = self.children[delta > 0]
        available = smaller_child.size - smaller_child.min_size[direction]
        if delta > available:
            delta = available
        elif delta < - available:
            delta = - available
        full_delta = [0,0]
        full_delta[direction] = delta
        full_delta = A(full_delta)
        child1, child2 = self.children
        child1.size += full_delta
        child2.size -= full_delta
        return EVENT_HANDLED
    def draw(self):
        pass # draw a couple of lines; get pos from children; or draw nothing if children have rectframes
    pass


class MyPane(Pane): # example use of VSplitter
    def _cmenu_splitV(self, pos):
        "add a vertical split at this point"
        # contents is some sort of view on some sort of model;
        # replace it with two copies of view on same model
        child1 = self.view.copy() # does view contain model?
        child2 = self.view.copy()
        self.view = VSplitter([child1, child2], [pos])
        # hmm, if we did this in untransformed coords,
        # we'd get one possible desired effect re the two views,
        # where they initially show adjacent parts, same as before.
    pass


