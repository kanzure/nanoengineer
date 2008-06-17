class MouseBehavior_OBS(object): #### REVIEW: might be no longer used, and/or renamed to ToolStateBehavior
    # REVIEW: how are MouseBehavior and Tool related in a class hierarchy? guess: Tool's a subclass.
    """
    Abstract class for simple mouse behaviors that are temporarily pushed
    as handlers onto a pane (by client code after it creates us).
    The pane is arg 1 of the constructor; the other args depend on the subclass.

    To implement its "exit condition", a subclass instance should call self.done(),
    which removes itself from pane's handlers, from within one or more of its
    event handler methods. It can then return None or EVENT_HANDLED depending
    on whether the exposed handlers should also handle the same event.
    It can even dispatch some other event (or more than one), then return EVENT_HANDLED,
    effectively replacing one event with another.
    """
    ### REVISE subs to call our init method
    def __init__(self, pane):
        "subclasses typically have more init args"
        self.pane = pane
    def done(self):
        self.pane.remove_handlers(self)
    pass

class Tool_OBS(object): ### REVISE super to MouseBehavior...
    # or make this an option of mousebehavior? or "wrap" an MB to be a Tool? YES. THEN IT CAN PUSH multiple handlers when it starts.
    """
    A Tool can act like a toggle button when in a pallette,
    or like a set of event handlers when applied to a pane or widget.

    A tool instance can be abstract, or be active within a specific pane,
    self.pane.
    """
    def __init__(self, pane): #k more args?
        self.pane = pane
    pass


    #e check for CMD_RETVAL in the args... is this just "symbol replacement"? treating arg as "expr for a literal value"?
    assert 0, "nim"
    #### PROBLEM which CMD_RETVAL solves: state needs arg returned when command is run!!!
    # simplest soln: always store cmd retval in a standard attribute...
    # and have a name for that to use in the transition, CMD_RETVAL ### IMPLEM
