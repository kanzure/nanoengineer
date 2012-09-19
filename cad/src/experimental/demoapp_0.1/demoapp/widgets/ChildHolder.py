from pyglet.event import EVENT_HANDLED

def _rx(child, x):
    if getattr(child, 'relative', False):
        ### WARNING: not yet true for any class!
        ### todo: always define it, so no getattr needed;
        # or better, make a method on child to transform x or y.
        return x - child.x
    else:
        return x
    pass

def _ry(child, y):
    if getattr(child, 'relative', False):
        return y - child.y
    else:
        return y
    pass

class EventDistributorToChildren(object):
    """
    Pass events onto the appropriate child out of a collection of children,
    known to us only via find_child passed to our constructor,
    assuming each child has a correctly set .size and .pos.
    """
    # note: see class pyglet.window.event.WindowEventLogger for defs of all window events
    child_with_mouse = None
    child_with_drag = None
    def __init__(self, find_child):
        self.find_child = find_child # call with (x,y), returns child or None
    def on_mouse_enter(self, x, y):
        child = self.find_child(x, y)
        self._set_child_with_mouse(child, x, y)
        if child:
            return EVENT_HANDLED
    def _set_child_with_mouse(self, child, x, y):
        """
        Maintain self.child_with_mouse, and send enter/leave events to children
        when it changes.

        @param child: the child with the last unpressed mouse position in it,
                      or None if that position is not in one of our children

        @return: whether this call changed the value of self.child_with_mouse
        """
        if child is not self.child_with_mouse:
            if self.child_with_mouse:
                self.child_with_mouse.dispatch_event('on_mouse_leave',
                                                     _rx(self.child_with_mouse, x),
                                                     _ry(self.child_with_mouse, y) )
            if child:
                child.dispatch_event('on_mouse_enter', _rx(child, x), _ry(child, y))
            self.child_with_mouse = child
            return True # different child
    def on_mouse_press(self, x, y, button, modifiers):
        child = self.find_child(x, y)
        if child:
            child.dispatch_event('on_mouse_press', _rx(child, x), _ry(child, y), button, modifiers)
            self.child_with_drag = child ##k only appropriate for some children??
            return EVENT_HANDLED
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.child_with_drag:
            ## maybe todo: also only send this if distance gets high enough to count as a drag
            self.child_with_drag.dispatch_event('on_mouse_drag',
                                                _rx(self.child_with_drag, x),
                                                _ry(self.child_with_drag, y),
                                                dx, dy, buttons, modifiers )
            return EVENT_HANDLED
    def on_mouse_release(self, x, y, button, modifiers):
        if self.child_with_drag:
            self.child_with_drag.dispatch_event('on_mouse_release',
                                                _rx(self.child_with_drag, x),
                                                _ry(self.child_with_drag, y),
                                                button, modifiers )
            self.on_mouse_enter(x, y) # seems correct, though perhaps a kluge
                # REVIEW: what if x,y not in self, is this still correct?
            return EVENT_HANDLED
    def on_mouse_motion(self, x, y, dx, dy):
        child = self.find_child(x, y)
        if self._set_child_with_mouse(child, _rx(child, x), _ry(child, y)):
            # different child -- no motion event needed within one,
            # leave/enter events cover it
            pass
        else:
            # same child -- tell it about the motion
            if child:
                child.dispatch_event('on_mouse_motion', _rx(child, x), _ry(child, y), dx, dy)
        if child:
            return EVENT_HANDLED #k not sure this is accurate in all cases
    def on_mouse_leave(self, x, y):
        self._set_child_with_mouse(None, -1, -1)
    #todo:
    def on_mouse_scroll(self, *args):
        pass
    def on_resize(self, *args):
        pass # even when we respond, in this case return None to let window respond too
    pass


class ChildHolder(object): # not yet used?
    "abstract class"
    pass

class SimpleChildHolder(EventDistributorToChildren, ChildHolder): # not yet used?
    def __init__(self):
        EventDistributorToChildren.__init__(self, self._find_child) # kluge?
    def _find_child(self, x, y):
        pass # nim
