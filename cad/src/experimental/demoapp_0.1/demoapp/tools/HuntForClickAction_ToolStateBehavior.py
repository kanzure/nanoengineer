"""
HuntForClickAction_ToolStateBehavior.py - help subclasses highlight the same
thing they will do, for a mouse click or drag on various objects or spaces

$Id$
"""
# refile into another directory?

from demoapp.foundation.MouseBehavior import parse_command, parse_transition, CMD_RETVAL, ToolStateBehavior

class HuntForClickAction_ToolStateBehavior(ToolStateBehavior): # rename?
    """
    Abstract class for one common kind of ToolStateBehavior,
    for use when the user is moving the mouse around to hunt for
    some action they can do by clicking or dragging. Provides for
    integrated code in the subclasses for what a click on something
    would do, used both for highlighting/tooltips during mouse motion
    and for actually doing it on mouse press.

    @see: other classes for fancier kinds of highlighting behavior
          (e.g. when the user might want to compare several possible
          actions and see highlighting for all of them).

    @see: other classes for similar behavior during a drag
          (tip & highlight for places where mouse *up* has certain effects),
          e.g. HuntForReleaseAction_ToolStateBehavior.
    """
    # instance variables
    _tip_and_highlight_info = None

    def on_mouse_motion(self, x, y, dx, dy):
        # todo: only let this event "count" if we moved far enough? maybe let this be a param within transition??
        button, modifiers = 0, 0 ### GUESS AT TYPE (not checked by current code, either)
            #### FIX: use current ones, not constant 0; get them from modkey press/release;
            # and call the following updater then too; later, worry about multiple buttons pressed at once
        transition = self.on_mouse_press_would_do(x, y, button, modifiers)
        tip, command, next_state, handled = parse_transition( transition)
        self._tip_and_highlight_info = tip
        del command, next_state
        return handled # guess at correct behavior; this lets background handlers highlight things too...
            # could be confusing, but not usually mixed with a real tip from ourselves.
            # (If that did happen, we might need a way to let background tip turn off ours or vice versa,
            #  e.g. a tip priority system for tips near each other.)

    def on_mouse_leave(self, x, y):
        self._tip_and_highlight_info = None
        return None # in case other handlers want to know about this event

    def on_mouse_enter(self, x, y):
        return self.on_mouse_motion(x, y, 0, 0) #semi-guess

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Do whatever self.on_mouse_press_would_do() says to do, for this state.
        """
        transition = self.on_mouse_press_would_do(x, y, button, modifiers)
            # pyglet API issue: if other buttons pressed, do we have enough info??
        tip, command, next_state, handled = parse_transition( transition)
        del tip
        self._tip_and_highlight_info = None # or something to say we're doing it, in case redraws occur during that?
        self._cmd_retval = self._doit(command) # this value is used for CMD_RETVAL
        assert self._cmd_retval or not command, "error: %r returns %r in %r" % \
               (command, self._cmd_retval, self)
            # not ok in general, but will help catch bugs for now ###
        self.transition_to(next_state)
        return handled

    def _doit(self, command): # rename to mention "command"?
        name, args = parse_command(command)
        if not name:
            return
        # note: we don't use dispatch_event for model commands -- for one thing,
        # it discards their return value (after using it for its own purposes).
        retval = getattr(self.model, name)(*args) ### REFACTOR, should be self.model.do_command or so
        assert retval # wrong in general, good for now ###
        return retval

    def on_draw_handle(self): #e rename?
        """
        """
        if self._tip_and_highlight_info:
            self.pane.draw_tip_and_highlight(
                    self._tip_and_highlight_info,
                    self.tool._f_HighlightGraphics_instance )
        return

    pass
