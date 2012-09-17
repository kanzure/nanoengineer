# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
toolbars.py - OpenGL toolbars, basically serving as "working mockups" for Qt toolbars
(but someday we should be able to turn the same toolbar configuration code
 into actual working Qt toolbars)

@author: bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from exprs.Column import SimpleRow

from exprs.Highlightable import Highlightable

from exprs.TextRect import TextRect

from exprs.Boxed import Boxed

from exprs.command_registry import CommandRegistry

from utilities.constants import gray, white, blue, green

from exprs.Exprs import list_Expr, format_Expr
from exprs.If_expr import If
from exprs.iterator_exprs import MapListToExpr, KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.attr_decl_macros import Arg, State
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.ExprsConstants import StubType, StateRef
from exprs.__Symbols__ import _self

class Toolbar(DelegatingInstanceOrExpr):
    pass

Command = StubType # might be a class in other files

class MainCommandToolButton(DelegatingInstanceOrExpr): #e rename?
    "Toolbutton for one of the main tools like Features, Build, Sketch -- class hierarchy subject to revision"
    # args
    toolbar = Arg(Toolbar) # our parent - #e rename parent_toolbar? to distinguish from our flyout_toolbar.
    toolname = Arg(str) #e.g. "Build"
    command = Arg(Command, doc = "the command invoked by pressing this toolbutton (might be transient or long lasting)") ###k type ok?
    subtools = Arg(list_Expr) # list of subtools (for cmenu or flyout), with None as a separator -- or as an ignored missing elt??
        # like menu_spec items?
        # Q: can they contain their own conditions, or just let the list be made using Ifs or filters?
        # A: subtools can contain their own conditions, for being shown, enabled, etc. they are ui elements, not just operations.
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
        on_release_in = _self.on_release_in,
        cmenu_obj = _self ###IMPLEM cmenu_obj option alias or renaming; or call it cmenu_maker??
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
    def cmenu_spec(self, highlightable): ###IMPLEM this simpler cmenu API (if it still seems good)
        return map( self.menuitem_for_subtool, self.subtools ) ###e how can that func tell us to leave out one, or incl a sequence?
    def menuitem_for_subtool(self, subtool):
        # stub, assume not None etc
        return ( subtool.name, subtool.cmd_invoke )
    pass

class MainToolbar(Toolbar): ###e how is the Main one different from any other one??? not in any way I yet thought of...
    # unless its flyout feature is unique... or maybe it has the behavior of deciding what to look like, inside it??
    # Nah, its client needs to provide the spec that, even if MainToolbar then does the work... but if it *can* do the work,
    # that might count... maybe it's just that it has no parent toolbar?
    #e rename
    """The main toolbar that contains (for example) Features, Build, Sketch, Dimension (tool names passed as an arg),
    with their associated flyout toolbars,
    and maintains the state (passed as a stateref) of what tool/subtool is active.
    """
    # args
    registry = Arg( CommandRegistry, doc = "the place in which tool name -> tool code mapping is registered, and in which subtools are found")
    #e the app object in which the tools operate?
    #e the world which they affect?
    toolnames = Arg(list_Expr, doc = "list of names of main tools")
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
        registry = self.registry
        ## expr = Boxed(TextRect(toolname)) # stub
        #e look up commands from registry ### LOGIC BUG: don't we get the toolname/cmd pair from the reg? if so,
        # then at this stage, just look up cmd from a local cache we made of cmds that go with our names for them.
        # But in current code, toolnames were passed in. Nevermind.
        command = registry.command_for_toolname(toolname) ###STUB - at least since retval might be None
            # [also, terms are messed up -- straighten out cmd vs tool, use same for main and sub]
            # [maybe: a command is something you do, and a command is "invoke a tool", ie start it (does not imply finishing it) --
            #  but i don't like that much -- what i look up here is the longlived-thing-maker (toolrun maker),
            #  not a subr that invokes it. otoh what abt toolbuttons that have immediate effect, no longlived thing created?
            #  their presence means i *do* have to look up a command, which when run *might* change toolstack state.]
        subtools = registry.subtools_for_command(command) ###STUB??
        expr = MainCommandToolButton( self, toolname, command, subtools)
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
