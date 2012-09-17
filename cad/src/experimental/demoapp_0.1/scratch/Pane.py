def rect_contains(rect, pos): #e refile, and use in an if test i have somewhere that inlines it
    x, y = pos
    x0, y0, w, h = rect
    return (x0 <= x < x0 + w and
            y0 <= y < y0 + h)


class ChildPane(object):
    # for window, use get_size
    # but for my own panes, store it...
    # and pos

    # default values of instance variables

    # pos and size can be set to move and resize child pane
    # within its parent;
    # event coords passed to child are relative to child's
    # bottom-left corner (so moving child within parent doesn't
    # require moving its subchildren).

    pos = V(0, 0)
    size = V(10, 10)

    def get_rect(self):
        x, y = self.pos
        w, h = self.size
        return x, y, w, h
    rect = property(get_rect)

    def get_x(self):
        return self.pos[0]
    x = property(get_x)

    def get_y(self):
        return self.pos[1]
    y = property(get_y)

    pass


class PaneWithChildren(Pane):
    def __init__(self, *args):
        Pane.__init__(self, args)
        self.children = [] # each child should inherit from ChildPane
        self._event_distributor = EventDistributorToChildren(self.find_child)
        self.push_handlers( self._event_distributor)
    def addChild(self, child):
        self.children.append(child)
    def draw(self):
        for child in self.children:
            child.draw()
    def find_child(self, x, y):
        for child in self.children:
            if rect_contains(child.rect, (x,y)):
                return child
    pass
