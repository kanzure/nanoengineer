# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
demo_ui.py - try out a more CAD-like UI organization

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from exprs.toolbars import MainToolbar

from exprs.command_registry import find_or_make_global_command_registry

from utilities.constants import pink
from utilities.prefs_constants import UPPER_LEFT, UPPER_RIGHT

from exprs.Exprs import list_Expr
from exprs.If_expr import If
from exprs.widget2d import Stub
from exprs.Rect import Rect
from exprs.TextRect import TextRect
from exprs.world import World
from exprs.Overlay import Overlay
from exprs.Column import SimpleColumn, SimpleRow
from exprs.projection import DrawInCorner
from exprs.Center import Top
from exprs.attr_decl_macros import State, Instance
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.__Symbols__ import _self

from exprs.demo_MT import MT_try2

testexpr_34 = Rect(0.7,0.3,pink) # just to make sure the imports from here are working -- replace it with a real test when we have one

# ToolRuns #e rename-- or maybe those classes will be derived from Tool classes somehow

class ToolRun(DelegatingInstanceOrExpr): # what is the super? it has several distinct parts we draw, but when do we draw "the whole thing" -- when editing one???
    property_manager = None ### has to be None! not Spacer(0) ## None -- one of these Spacers might be needed;
        # guess1: Overlay/Row arg is not None but its delegate is!
        # guess2: bug in DrawInCorner(None)
        # guess3: Top(propmgr)
    graphics_area_topright_buttons = None ## Spacer(0) ## None
    pass

class DefaultToolRun(ToolRun):
    """An internal pseudo-ToolRun that is always active, and controls the property manager display
    and other things normally controlled by the active tool or subtool when they exist (eg Done/Cancel buttons in graphics area).
    In general it just sets them to invisible stubs.
    """
    pass


# term/ui guesses until i learn otherwise:
# - Tool is the classname of the thing whose tool button you hit to get into,
#   and which has its own prop mgr or inherits one from a parent tool
#   - A Tool Instance sits there whether or not the tool is active; it can supply things like a prefs pane, tool button, etc;
#     typically there's one long-lived instance for each Command eg Sketch or sub-command eg Line
# - each time a Tool is activated it produces a new ToolRun...
# - there is a stack of currently active toolruns, each one the parent of the next
#   (usual depth one or two, plus an outer constant one with no prop mgr, user-invisible)

from exprs.debug_exprs import DebugPrintAttrs ###e move up, or into basic; rename to more memorable name (maybe just Debug?) (add DebugDraw?)


#e set up a Sketch tool, which has a main button with a Sketch PM and for now has all the Sketch Entities we know about,
# and later can be told to have a specific subset of them (if they are found) and an "other" item for access to more (incl custom ones).

Tool = Stub
class SketchTool(Tool): #e move to demo_sketch?
    "#doc"
    # it has a main command or PM
    # - default PM for subcommands without their own PM
    # - PM you see if you select a sketch for editing
    # - it might have some parts of this PM available when adding a specific element to the sketch, too
    # - in general, a PM has a bunch of possible groups, but each one has a condition for being shown.
    #   and some of them exist on more than one PM. So a PM is an expr made of PMGroup exprs...
    #   we could make one from a list of field names & types, but in general it's not made that way.

    # and an ability to host subcommands
    # - it makes a new Sketch for them if necessary;
    # - or like any command, since it needs a Sketch, maybe one is selected when it's entered;
    #   but unlike some args, if none is selected user is not prompted for one - but is prompted for a ref plane or surface;
    #   this is because Sketch has an Arg(RefPlaneOrSurface)... or special code to look for Args it doesn't have from the UI...
    #   sort of like an Arg default expr, but not really the same thing. And maybe it's on a StateArg.
    #   (If it's entered via Insert Line, this ref plane prompting happens too (V4d p15), even though PM title is Insert Line... hmm.
    #    I can see some sense in that. All PMs have a message area; conditions determine whether it's active,
    #    and if it is, it acts like a subcommand of its own, since the click effect depends on its being there, I think.)
    #
    #   And maybe this special code is not on a Sketch modelobj, but on the MakeSketch command. And maybe SketchTool == MakeSketch?
    #   But don't you get into it if you select an existing sketch in the right way?
    #   It's a "tool for making, editing, inspecting sketches" which contains a lot of commands and other things.
    #   You might get into it in various ways, eg a cmenu item on a sketch's MT node or on a visible sketch element.
    #   SketchTool seems right.
    #
    # and a way to filter available commands to find subcommands to put on its flyout toolbar as subtools
    # which means it has a flyout toolbar, btw; and more fundamentally it has the list of items on it (since it has cmenu of those too)

    pass

class main_ui_layout(DelegatingInstanceOrExpr):
    #e rename? is it not only the ui, but the entire app? (selection, files, etc)
    #e merge in the App obj from test.py, and the _recent_tests system in some form?

    # args (none yet)

    # internal state - permanent
    ###e note: when we reload and remake this instance, we'd prefer it if the world state stayed unchanged (as i presume it does)
    # but if the default_tool instance and toolstack state got remade. The lack of the latter has been confusing me
    # since changes to ui code aren't working. I think this is a difference between a ui and operations layer (should change)
    # vs model data layer (should not change even tho the op methods on it can change). So when I can put these things into layers
    # (not only State, but even Instance or attrs within them) and make those sensitive to reload, that will help.
    # In the meantime -- if I could kluge Instance and State to take an option to control this
    # (like index = exprs_globals.reload_counter)
    # it might help.... #####TRYIT SOMETIME, and BE CAREFUL UNTIL I DO.
    world = Instance(World())
    default_tool = Instance(DefaultToolRun())

    # internal state - varying
    toolstack = State(list_Expr, [default_tool]) # always has at least one tool on it; a stack of Instances not exprs
        # maybe the better term for this is something like command & subcommand
    current_tool = toolstack[-1] # last tool on the stack is current; exiting it will pop the stack (Instance not expr)
        ##e (add a type-assertion (as opposed to type-coercion) primitive, so I can say "this is an Instance" in the code?)
        # NOTE: this is not strictly speaking a tool, but ONE RUN of a tool. That might be important enough to rename it for,
        # to ToolRun or maybe ActiveTool or RunningTool or ToolInUse or ToolBeingUsed...
        # [but note, obj might remain around on history or in Undo stack, even when no longer being used],
        # since we also have to deal with Tools in the sense of Tool Run Producers, eg toolbuttons. ###e

    # parts of the appearance
    registry = find_or_make_global_command_registry() ## None ###STUB, will fail --
        ## AttributeError: 'NoneType' object has no attribute 'command_for_toolname'
    toolstack_ref = None ###STUB
    toolbar = Instance( MainToolbar( registry, ["Features", "Build", "Sketch"], toolstack_ref ) ) #e arg order?
        ###e args/opts for what tools to show -- maybe their cmdnames & it loads them from elsewhere
        #e add row of tool buttons, and flyout toolbar; use ChoiceRow?? the things should probably look pressed...
        # they might need cmenus (find out what the deal is with the cmenus i see in the ui mockup - related to flyouts?
        #    yes, it's like this: main tools have cmenus with subtools, and if you pick one, main tool and its subtool both look pressed
        # I'll need new specialized controls.py classes for these; new super Control for all kinds of controls?? (not sure why...)
    propmgr = SimpleColumn(
        TextRect("(property manager)"), #e possibly to become a tab control tab
        DebugPrintAttrs(current_tool.property_manager) # must be None if we don't want one visible; otherwise an Instance
        ###BUG: DebugPrintAttrs shows that it's a spacer -- I guess IorE turns None into one when it instantiates? Make it a false one??
     )
    mt = SimpleColumn(
        TextRect("(model tree)"), #e possibly to become a tab control tab, but only when we're in the left channel
        MT_try2(world) #e rename to  "Feature Manager" ??
        ##e soon, MT should be not on whole world but on model or cur. part, a specific obj in the world
     )
    graphics_area = _self.world
        ##e ditto for what we show here, except it might not be the exact same object, and it will really be shown in a way
        # that depends on both the current display style and the current tool (command & subcommand)
    graphics_area_topright_buttons = current_tool.graphics_area_topright_buttons
    # overall appearance
    delegate = Overlay(
        # stuff in the corners -- note, these don't use the corner constants for standalone tests like PM_CORNER
        DrawInCorner(corner = UPPER_LEFT)(
            SimpleColumn(
                toolbar,
                #e add tab control
                SimpleRow(
                    If( current_tool.property_manager, Top(propmgr), None), #k None?? prob ok now, see demo_MT comment 070302 ###k
                    Top(mt)), #e actually we'd then put a splitter & glpane-like-thing...
                #e anything just below the propmgr?
         )),
        DrawInCorner(corner = UPPER_RIGHT)( ##e of graphics area, not entire screen...
            graphics_area_topright_buttons ### WRONG, these should go under the main toolbar area on the right
                # (but we don't yet have any 2dwidgets which expand to fill the available space, except DrawInCorner of entire screen)
                # (this won't matter once the toolbar is done entirely in Qt, so we don't need to correct it for now)
         ),
        #e other corners? "... an area (view) on the right side
        # of the main window for accessing the part library, on-line documentation, etc"
        # the main graphics area
            #e [this too ought to go under the toolbar and to the right of the propmgr, but that can wait until they're fully in Qt]
        graphics_area
     )
    pass

testexpr_34a = main_ui_layout()

"""
somehow encode the contents:
Features: ?

Build:
Molecule
DNA
DNA Origami
Carbon Nanotube [hmm, what about B-N, and graphene sheet]
Heterojunction [hmm, doesn't say of what]

Sketch:
(Dimension)
(On surface)
Line
"""
# end
