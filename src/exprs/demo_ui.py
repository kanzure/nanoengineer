"""
demo_ui.py - try out a more CAD-like UI organization

$Id$
"""

from basic import *
from basic import _app, _self, _my

import test
from test import reload_once
reload_once(test) # not sure this is needed if we're only imported from test.py
from test import * # shortcut, since we were moved out of test.py

import toolbars
reload_once(toolbars)
from toolbars import MainToolbar

import command_registry
reload_once(command_registry)
from command_registry import auto_register, find_or_make_global_command_registry, CommandRegistry

# [this first part was written in test.py, thus the globalvar naming scheme.]

# 070228:
# How can we get the functions of both _19i and _30i in one integrated setup?
# Well, can we just display both their control panels (world_uis) in a column??
# yes [works more or less], but they need to share the same World! Right now they each make their own.
# Also, they have different ideas of how to display their world -- both draw it unchanged,
# but one of them draws a background too (for sketching on)... we might change that later
# (for sketching on model objs instead), but for now, we'll switch between them (so leave them as
# separate testexprs) but let each one show the same world differently.
# We'll also want to move each of their tool_maker functions inside their world_ui instances.
# And then we'll want the different possibly-drawn stuff (propmgr, mt, flyout tools, 3d, etc)
# to be in the world_ui in different std attrs, and to wrap them in a general app-ui object.
# And later that app-ui will just be the app object with a self-contained world_ui switcher and draw method.

# Here's the "both panels" version (half-works but not useful -- both panels are on the same world_ui, only one does much):
testexpr_34ix1 = eval_Expr( call_Expr( lambda world_ui:
                                     Overlay( world_ui,
                                              DrawInCorner( SimpleColumn(
                                                  Boxed( eval_Expr( call_Expr( dna_ribbon_view_toolcorner_expr_maker, world_ui ))),
                                                  Boxed( eval_Expr( call_Expr( demo_drag_toolcorner_expr_maker, world_ui.world ))),
                                               )),
                                              DrawInCorner( MT_try2(getattr_Expr(world_ui, 'world')), WORLD_MT_CORNER ),
                                             ),
                                     call_Expr( _app.Instance, testexpr_30b, "#34bi") ### needs to combine cmds in two kinds of world,
                                         # or add a cmd to make a thing to draw marks on like the bg object in _19haux
                                         # (and for that matter the make dna cyl has something to do with an origami construct
                                         #  in a raster pattern)
                                         # (how would all this fit into a user story like mark's recent ones?)
                                     ))

# Here instead are variants of _19i and _30i which use a shared world, but keep their outside function-made tool_makers.

class _world_ui_user(DelegatingInstanceOrExpr): #e refile if accepted #e rename #e merge with app object?? not sure.
    "display the graphics area, property manager pane, and MT, given instructions on making it in an eclectic form (#fix soon)"
    world = Arg(World)
    world_ui_expr = ArgExpr(Anything) # an expr that needs the world as an option named 'world'
    tool_maker = Arg(Anything) # a function from world_ui to the prop mgr
    # formulae
    world_ui = Instance( world_ui_expr(world = world)() ) #k not sure this will work, or ought to -- might want ._e_customize or ._e_supply_args
        # btw this Instance is not strictly needed, but is what we want in spirit
    delegate = Overlay( world_ui, # this is the 3d graphics area, as seen via the given world_ui
                        DrawInCorner( Boxed(
                            eval_Expr( call_Expr( tool_maker, world_ui )) )), # prop mgr (but lower right at the moment (default corner))
                        DrawInCorner( MT_try2( ###e OPTIM: this object ought to be shared ###k Q: maybe it already is, if our ipath is?
                            world_ui.world ## getattr_Expr(world_ui, 'world')
                            ), WORLD_MT_CORNER ), # mt (upper left)  ##e probably should revise arg order to DrawInCorner(corner, thing)
                       )
    pass

testexpr_19jaux = GraphDrawDemo_FixedToolOnArg1(
    # note: testexpr_11q1b is an Image of a file that's only on bruce's mac, but on other macs it should turn into a default image
    Overlay( testexpr_11q1b(size = Rect(10)), SimpleRow(Sphere(2),Sphere(1),Sphere(0.5),Sphere(0.25)) ),
 )

def _19j_tool_maker(world_ui):
    return demo_drag_toolcorner_expr_maker(world_ui.world)

testexpr_19j = eval_Expr( call_Expr( lambda world:
                                     _world_ui_user( world,
                                                     testexpr_19jaux, # needs to receive an option for the world [coded now]
                                                     _19j_tool_maker,
                                      ),
                                     call_Expr( _app.Instance, World(), "#shared world") # the shared world (assuming _app is)
                                    ))
testexpr_30j = eval_Expr( call_Expr( lambda world:
                                     _world_ui_user( world,
                                                     World_dna_holder, # needs to receive an option for the world [coded now]
                                                     dna_ribbon_view_toolcorner_expr_maker,
                                      ),
                                     call_Expr( _app.Instance, World(), "#shared world") # the shared world
                                    ))

# update, 070302 morn:
# The problem is, those don't work yet. They need two NFRs/bugfixes in the underlying code, before they can work:
# - make possible the customization of an ArgExpr (in this case, world_ui_expr, in the expr world_ui_expr(world = world)() ),
#   by pushing a wrapping lexenv_ipath_Expr (which it needs, since it came from outer to inner lexenv) inside it
#   (making a modified/simplified copy, and also caching this as a "forward value" from the original expr)
#   to its contained arg/opt exprs from prior customizations (stored in _e_args and _e_kws),
#   not forgetting to pick up the lexenv mods _i_grabarg would do using .env_for_args (which come in between),
#   also so that further customization exprs *don't* end up (incorrectly) inside that originally-wrapping lexenv_ipath_Expr.
#   (This also requires worrying about how to deal with ipath in this, and some other issues discussed in a non-cvs notesfile.)
# - permit a bare Expr subclass (e.g. World_dna_holder in the eg above) to be passed in as a customizable ArgExpr.
#   This is probably not really needed for now, since we can probably work around it by customizing them first with a fake option.
#
# I worked out (partly on paper, 070301 late) the requirements & coding plans for "customization of an ArgExpr" -- the best way is to
# split obj.env into .lexenv and .env, with .env coming from instantiation (and differing depending on its layer, eg for graphical
# vs model objs, or being present more than once if we have partial instantiation (unlikely)), and being what i usually call dynenv
# though it's not really that if that would mean something in the usual dynenv during a method call,
# and with .lexenv being settable even on some pure exprs (as soon as their owning lexical environment is an Instance),
# and in particular getting set as soon as a lexenv wrapper gets pushed in -- but when a copy is made for further customization,
# getting removed from there and pushed further in (but modified by lexenv_for_args, to pick up grabarg's planned env for args)
# around the stored arg exprs. The new arg exprs added by customization don't have that env wrapper, of course, which is the point.

# But it might be better to defer that plan for now and just rework the above in the way I planned to anyway.
# So let's try that here.

# (TBC)

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

from debug_exprs import DebugPrintAttrs ###e move up, or into basic; rename to more memorable name (maybe just Debug?) (add DebugDraw?)


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
    # In the meantime -- if I could kluge Instance and State to take an option to control this (like index = vv.reload_counter)
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
        # stuff in the corners
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

'''somehow encode the contents:
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
'''
# end
