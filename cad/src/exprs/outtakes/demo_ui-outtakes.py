# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id
"""

outtakes file

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
