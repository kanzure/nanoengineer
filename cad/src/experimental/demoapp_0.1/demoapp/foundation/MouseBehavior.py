"""
MouseBehavior.py

$Id$

TODO:

split into other files, one for class Tool*,
one for parse_command (rename to avoid confusion w/ user command package?), etc
"""

from pyglet.event import EVENT_HANDLED

from demoapp.foundation.description_utils import description_maker_for_methods_in_class

DEBUG_TRANSITIONS = False

# ==

class PlaceHolder(object): #refile
    """
    For singleton symbol-like instances which can be found and replaced
    wherever they occur in other values, and are never confused
    with ordinary values.
    """
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return self.name
    pass

CMD_RETVAL = PlaceHolder('CMD_RETVAL')

SAME_STATE = PlaceHolder('SAME_STATE')

# ==

NOOP = 'NOOP' # stub
     # unlike None, this means we stop at this object, never calling lower handlers

def parse_command(command): ### REFACTOR into this returning name, args, parse_tip, and parse_transition
    "return (name, args) for any command"
    #### DECIDE: what actually this is retval? event name???? in pane or model? which coords? (guess: model, model coords)
    # TODO: improve to have more return options, be a first class object -- really an expr (description of what to do)
    if type(command) is tuple:
        name, args = command[0], command[1:]
    elif command is None:
        return None, ()
    else:
        # any command with no args
        name, args = command, ()
    assert isinstance(name, type("")) #e improve
    return name, args

# ==

class Transition(object): # use superclass Description??
    """
    Describe a potential state transition, for use by something
    which might actually do it or might just indicate something
    about it in the UI.

    Note: callers are encouraged to supply these as named arguments for clarity,
    and to always supply them in this order, and to supply all of them
    (except for handled) even when they have their default values.

    @param indicators: tooltip and highlighting indicators, to show the user
                       what would happen if this transition was taken.
    @type indicators: sequence of HighlightGraphics_descriptions objects ###doc more

    @param command: what to do to the model when this transition is taken.
                    Can be None for "no operation".
    @type command: ('command name', *parameters )

    @param next_state: next state to go into, when this transition is taken.
                       Can be SAME_STATE to remain in the same state with the
                       same parameters. Can include CMD_RETVAL when the command
                       return value is needed as a parameter of the new state.
    @type next_state: ( state_class, *parameters)

    @param handled: whether a mouse event resulting in this transition being
                    indicated or taken has been fully handled (true) or needs
                    further handling by background event handlers (false)
    @type handled: boolean
    """
    def __init__(self,
                 indicators = (),
                 command = None,
                 next_state = None,
                 handled = True ):
        self.indicators = indicators
        self.command = command
        self.next_state = next_state
        self.handled = handled and EVENT_HANDLED ## technically: or None
        #e todo: also save file and line of caller, if a debug option is set,
        # and print this in tracebacks when processing this transition
        # (perhaps using a feature to store extra info in frames to be printed then?)
    pass

def parse_transition(transition):
    t = transition
    if t is None:
        return None, None, SAME_STATE, False # guesses, 080616 night
    return t.indicators, t.command, t.next_state, t.handled

def parse_state( state_desc):
    "return class, args"
    # maybe: use parse_description_tuple?
    # maybe optim: replacements at same time (as this or as instantiate_state)?
    if state_desc is None:
        return None, ()
    try:
        return state_desc[0], state_desc[1:]
    except:
        print "following exception was in parse_state(%r):" % (state_desc,)
        raise
    pass

def replace_symbols_in(desc, **replacements): # maybe: grab code from exprs for Symbols, to generalize
    res = desc
    if type(desc) is type(()):
        res = tuple([replace_symbols_in(x, **replacements) for x in desc])
    elif type(desc) is PlaceHolder:
        if desc.name in replacements:
            res = replacements[desc.name]
        pass
    # todo: dicts, lists
    # maybe: if res == desc: return desc
    return res

# ==


class ToolStateBehavior(object):
    #doc; related to MouseBehavior (is name ok? ToolState by itself seemed ambiguous...)
    """
    """
    _cmd_retval = None
    def __init__(self, tool):
        "subclasses typically have more init args"
        self.tool = tool
        self.pane = tool.pane # convenience for subclasses
        self.model = tool.pane.model
        return
    def transition_to(self, next_state):
        if next_state is not SAME_STATE:
            if DEBUG_TRANSITIONS:
                print "%r transto %r" % (self, next_state) ##### DEBUG
            self.tool.transition_to( next_state,
                                     CMD_RETVAL = self._cmd_retval )
            # maybe: might decide tool can grab it from self if needed (passed as an arg)
    pass

# ==

class Tool(object):
    """
    Subclasses are specific tools, not being used.
    Instances of subclases are uses of specific tools in specific panes.
    """
    # per-subclass constants
    _default_state = None
    HighlightGraphics_class = None

    # instance variables
    _current_handlers = None
    _f_HighlightGraphics_instance = None # (could probably be per-class)
    _f_HighlightGraphics_descriptions = None # (could probably be per-class)

    def __init__(self, pane):
        """
        @note: doesn't do self.activate()
        """
        self.pane = pane
        # optim (minor): the following could probably be cached per-class
        if self.HighlightGraphics_class:
            tool = self
            self._f_HighlightGraphics_instance = self.HighlightGraphics_class(tool)
            self._f_HighlightGraphics_descriptions = description_maker_for_methods_in_class( self.HighlightGraphics_class)
        pass
    def activate(self, initial_state = None):
        """
        @note: doesn't deactivate other tools on self.pane
        """
        self.transition_to(initial_state or self._default_state)
        return
    def deactivate(self):
        self.remove_state_handlers()
        return
    def remove_state_handlers(self):
        if self._current_handlers:
            self.pane.remove_handlers(self._current_handlers)
            self._current_handlers = None
        return
    def transition_to(self, next_state, **replacements):
        self.remove_state_handlers()
        next_state = replace_symbols_in( next_state, **replacements )
        new_handlers = self.instantiate_state( next_state)
        self.push_state_handlers( new_handlers)
        # review: would this be better if it could call a new
        # replace_handlers method on EventDispatcher
        # (so as to insert them at the same stack level as before)?
        # not sure whether this ever matters in practice...
        # yes, it does matter -- I tried putting some controls on top
        # of the tool area, but that fails from the start, since the
        # first toolstate ends up on top of them.
        return
    def push_state_handlers(self, new_handlers):
        self.pane.push_handlers(new_handlers)
        self._current_handlers = new_handlers
        return
    def instantiate_state(self, state):
        try:
            assert state, "state must not be %r" % (state,)
            state_class, state_args = parse_state(state)
            assert issubclass( state_class, ToolStateBehavior ), \
                   "%r should be a subclass of ToolStateBehavior" % (state_class,)
            res = state_class( self, *state_args)
            return res
        except:
            print "following exception is in %r.instantiate_state(%r):" % (self, state)
            raise
        pass
    pass


