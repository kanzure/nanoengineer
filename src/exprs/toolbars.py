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

class MainCommandToolButton(DelegatingInstanceOrExpr): #e rename?
    "Toolbutton for Features, Build, Sketch -- class hierarchy subject to revision"
    # args
    toolname = Arg(str) #e.g. "Build"
    toolbar = Arg(Toolbar) # our parent
    #e also one for its toolbar, esp if it's a mutually exclusive pressed choice -- and ways to cause related cmd/propmgr to be entered
    # state
    pressed = State(bool, False, doc = "whether this button should appear pressed right now")
    # formulae
    plain_bordercolor =       If(pressed, gray, white)
    highlighted_bordercolor = If(pressed, gray, blue)
    pressed_in_bordercolor =  If(pressed, gray, green) # green = going to do something on_release_in
    pressed_out_bordercolor = If(pressed, gray, white) # white = not going to do anything on_release_out
    # appearance
    delegate = Highlightable(
        plain =       Boxed(TextRect(toolname), bordercolor = plain_bordercolor),
        highlighted = Boxed(TextRect(toolname), bordercolor = highlighted_bordercolor), #e submenu is nim
        pressed_in  = Boxed(TextRect(toolname), bordercolor = pressed_in_bordercolor),
        pressed_out = Boxed(TextRect(toolname), bordercolor = pressed_out_bordercolor),
        sbar_text = format_Expr( "%s (click for flyout [nim]; submenu is nim)", toolname ),
        on_release_in = _self.on_release_in
    )
    # repr? with self.toolname. Need to recall how best to fit in -- repr_info? ##e
    # actions
    def on_release_in(self):
        if not self.pressed:
            print "on_release_in %s" % self.toolname
            self.pressed = True #e for now -- later we might let main toolbar decide if this is ok
            #e incremental redraw to look pressed right away? or let toolbar decide?
            self.toolbar._advise_got_pressed(self)
        else:
            #### WRONG but not yet another way to unpress:
            self.pressed = False
            print "unpressed -- not normal in real life!"###
        return #e stub
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
    delegate = SimpleRow(
        MapListToExpr( _self.toolbutton_for_toolname,                       
                      toolnames,
                      KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleRow) ),
        TextRect("flyout goes here")
     )
    def toolbutton_for_toolname(self, toolname):
        assert type(toolname) == type("")
        ## expr = Boxed(TextRect(toolname)) # stub
        expr = MainCommandToolButton(toolname, self)
        #e is it ok about MapListToExpr that it makes us instantiate this ourselves? Can't it guess a cache index on its own?
        #e related Q: can we make it easier, eg using nim InstanceDict or (working) _CV_ rule?
        instance = self.Instance( expr, "#" + toolname)
        return instance
    def _advise_got_pressed(self, button):
        print "my button %r with toolname %r says it got pressed" % (button, button.toolname)
        ###STUB - do the following:
        #e decide if legal at this time
        #e set it as the next running button
        
        #e unpress other buttons (and finish or cancel their runs if needed) (maybe only if their actions are incompat in parallel??)
        # e.g. something like:
        ## while toolstack_ref.get_value()[-1].is_incompatible_with(something):
        ##    didit = toolstack_ref.get_value()[-1].force_finish(something)
        ##    if not didit:
        ##        # oops, still in some prior command (and what about some we already popped out of? restore them?
        ##        # no, don't pop out yet, unless we want that...)
        
        #e start a new ToolRun of this button's command
        #e put it on the stack we were passed (that way its flyout gets displayed, and its pm gets displayed)
        #e update our flyout and PM if needed (for example, by figuring out what subcommands have been registered with this name)
        #e update other stuff not yet used, like a display/edit style, various filters...
        return
    pass

# end
