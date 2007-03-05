"""
toolbars.py - OpenGL toolbars, basically serving as "working mockups" for Qt toolbars
(but someday we should be able to turn the same toolbar configuration code
 into actual working Qt toolbars)

$Id$
"""

from basic import *
from basic import _app, _self, _my

import Column
reload_once(Column)
from Column import SimpleRow, SimpleColumn

import Overlay
reload_once(Overlay)
from Overlay import Overlay

import Highlightable
reload_once(Highlightable)
from Highlightable import Highlightable

import TextRect
reload_once(TextRect)
from TextRect import TextRect

import Boxed
reload_once(Boxed)
from Boxed import Boxed

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
    # appearance
    delegate = MapListToExpr( _self.toolbutton_for_toolname,
                              toolnames,
                              KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleRow) )
    def toolbutton_for_toolname(self, toolname):
        assert type(toolname) == type("")
        expr = Boxed(TextRect(toolname)) # stub
        #e is it ok about MapListToExpr that it makes us instantiate this ourselves? Can't it guess a cache index on its own?
        #e related Q: can we make it easier, eg using nim InstanceDict or (working) _CV_ rule?
        instance = self.Instance( expr, "#" + toolname)
        return instance
    pass

# end
