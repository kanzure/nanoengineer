"""
toolbars.py - OpenGL toolbars, basically serving as "working mockups" for Qt toolbars
(but someday we should be able to turn the same toolbar configuration code
 into actual working Qt toolbars)

$Id$
"""

from basic import *
from basic import _app, _self, _my

class Toolbar(DelegatingInstanceOrExpr):
    pass

class MainToolbar(Toolbar): ###e how is the Main one different from any other one??? not in any way I yet thought of...
    # unless its flyout feature is unique...
    #e rename
    """The main toolbar that contains (for example) Features, Build, Sketch, Dimension (tool names passed as an arg),
    with their associated flyout toolbars,
    and maintains the state (passed as a stateref) of what tool/subtool is active.
    """
    # args
    #e an arg for the place in which tool name -> tool code mapping is registered?
    #e the app object in which the tools operate?
    #e the world which they affect?
    toolnames = Arg(list_Expr, doc = "list of names of main tools (name->tool associations must be registered elsewhere")
    toolstack_ref = Arg(StateRef, doc = "external state which should be maintained to show what tool & subtool is active now")
    # formulae
    # appearance - how does demo_MT do it?
    delegate = Stub ## SimpleRow(..) -- use MapListToExpr
    pass

# end


