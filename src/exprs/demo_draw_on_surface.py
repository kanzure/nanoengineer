"""
demo_draw_on_surface.py

$Id$

070319 a standalone version of the so-called polyline example in demo_drag.py (testexpr_19g)

experimental, not yet finished or called

See also:
- demo_polyline.py (and the other files it refers to, like demo_ui.py)
- TODO comments below
- our_testexpr at bottom (substitute for demo_ui until it's ready)

"""

from basic import *
from basic import _self, _my, _this

from test import * # get lazy for now

from demo_drag import Vertex, kluge_dragtool_state_prefs_key

from OpenGL.GL import * #e could be relegated to separate drawing code class, if we wanted...

from command_registry import auto_register

# ==


###e plan: make it a demo command file alongside demo_polyline.py.

## Q: needs to run in a highlightable object so self.current_event_mousepoint() is defined -- tho empty space works ok in some manner....
##just not sure where we get a coordsys for that -- maybe just make a Coordsys object then?
##
##we might rather use abs coords even if we're on an object with local ones!!!

#e change class polyline3d to not show the red thing until you're done, and let the red thing be a kid of the polyline3d

#e and maybe to always draw closer to screen, but store coords identical to model object --
# use a displist (not yet defined) for translating closer to user

# also in the command class define a PM... or is that really part of the object defn? or one of each?
# probably the command can override the one for the obj, and say whether to show it also...
# what about an "edit obj" command... doesn't that one's PM come from the obj itself? not necessarily...
# tho we can hope it's created from the obj.


# for the create or edit polyline3d, the only PM need so far is the checkbox for closed.
# (initial value from a pref - maybe changing it also changes the pref, when creating one, but when editing one
#  it connects to the specific one only, not to the pref. So the PMs differ at least in that case.)


# so the making of PM needs to be able to differ, for create vs edit.
# OTOH we might ask model objs for PM fields, and model objs knowing they were being made could give different kinds...
# and have attrs that affected how mod ops to them (done as they are made) are interpreted...
# and if this info is on the object itself, the incomplete obj can be saved, which might be good...

# so let's put code here which asks the incomplete polyline3d for a list of editable fields, and makes a PM for them.
# Can it include the points too? why not? later we'd know to suppress that from the PM unless you open the advanced/complete one...
# or we might decl it like that from the start -- a decl on the attribute in the model object.

# ==


##class polyline_handle(DelegatingInstanceOrExpr):
##    delegate = Draggable(Rect(0.3,green))

###e change super: ModelObject or ModelObject3D or so

###e rename
class polyline3d(InstanceOrExpr): # WARNING [070319]: duplicated code, demo_drag.py and demo_draw_on_surface.py [modified a bit]
    """A graphical object with an extendable (or resettable from outside I guess) list of points,
    and a kid (end1) (supplied, but optional (leaving it out is ###UNTESTED)) that can serve as a drag handle by default.
    (And which also picks up a cmenu from self. (kluge!))
    Also some Options, see the code.
    """
    # Note [070307]: this class will be superceded by class Polyline in demo_polyline.py,
    # and the code that uses it below (eg the add_point call) will be superseded by other code in that file.
    #
    ###BUGS: doesn't set color, depends on luck. end1 is not fully part of it so putting cmenu on it will be hard.
    # could use cmenu to set the options.
    # end1 might be in MT directly and also be our kid (not necessarily wrong, caller needn't add it to MT).
    # when drawing on sphere, long line segs can go inside it and not be seen.
    points = State(list_Expr, []) ###k probably wrong way to say the value should be a list
##    end1arg = Arg(StubType,None)
##    end1 = Instance(eval_Expr( call_Expr(end1arg.copy,)( color = green) ))###HACK - works except color is ignored and orig obscures copy
    end1 = Arg(StubType, None, doc = "KLUGE arg: optional externally supplied drag-handle, also is given our cmenu by direct mod")
    closed = Option(bool, False, doc = "whether to draw it as a closed loop")
    _closed_state = State(bool, closed) ####KLUGE, needs OptionState
    relative = Option(bool, True, doc = "whether to position it relative to the center of self.end1 (if it has one)")
    def _init_instance(self):
        end1 = self.end1
        if end1:
            end1.cmenu_maker = self
    def _C__use_relative(self):
        "compute self._use_relative (whether to use the relative option)"
        if self.relative:
            try:
                center = self.end1.center
                return True
            except:
                #e print?
                return False
        return False
    def _C_origin(self): #070307 renamed this to origin from center
        if self._use_relative:
            return self.end1.center # this can vary!
        return ORIGIN
##    center = _self.origin #k might not be needed -- guessing it's not, 070307
    def add_point(self, pos):
        "add a point at the given 3d position"
        pos = pos - self.origin
        self.points = self.points + [pos] ### INEFFICIENT, but need to use '+' for now to make sure it's change-tracked
    def draw(self):
        ###k is it wrong to draw both a kid and some opengl stuff?? not really, just suboptimal if opengl stuff takes long (re rendering.py)
        self.drawkid(self.end1) # end1 node
        if self._closed_state:
            glBegin(GL_LINE_LOOP) # note: nothing sets color. see drawline for how.
                # in practice it's thin and dark gray - just by luck.
        else:
            glBegin(GL_LINE_STRIP)
        if self._use_relative:
            # general case - but also include origin (end1.center) as first point!
            origin = self.origin
            glVertex3fv(origin)
            for pos in self.points:
                glVertex3fv(pos + origin)
        else:
            # optim - but not equivalent since don't include origin!
            for pos in self.points:
                glVertex3fv(pos)
        glEnd()
        #e option to also draw dots on the points [useful if we're made differently, one click per point; and they might be draggable #e]
        return
    def make_selobj_cmenu_items(self, menu_spec, highlightable):
        """Add self-specific context menu items to <menu_spec> list when self is the selobj (or its delegate(?)... ###doc better).
        Only works if this obj (self) gets passed to Highlightable's cmenu_maker option (which DraggableObject(self) will do).
        [For more examples, see this method as implemented in chem.py, jigs*.py in cad/src.]
        """
        menu_spec.extend([
            ("polyline3d", noop, 'disabled'), # or 'checked' or 'unchecked'; item = None for separator; submenu possible
        ])

    pass # end of class polyline3d

# ==

PropertyGroup = DelegatingInstanceOrExpr

class make_polyline3d_PG(PropertyGroup):###e call me ###e revise -- not clear it should refer to a pref
    ###e who supplies this? the command? i guess so. is it a local class inside it? or at least the value of an attr inside it?
    "contents of property manager group for a polyline3d which is being made"
    ###e needs some args that let it find that polyline3d or the making-command!
##    arg = Arg()
    #e someday be able to automake this from higher-level contents... but returning a widget is always going to be a possibility
    delegate = SimpleColumn(
        checkbox_pref( kluge_dragtool_state_prefs_key + "bla2", "closed?", dflt = False),
    )
    title = "Polyline Properties" ###USE ME
    pass

class PM_from_groups(DelegatingInstanceOrExpr): ###e refile into demo_ui or so, and call it on [make_polyline3d_PG(somearg)]
    groups = Arg(list_Expr)
    delegate = MapListToExpr(
        KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(Boxed), ###e change to a GroupBox, with a title from the group...
        groups,
        KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn)
     )
    pass

# ==

class PM_Command(DelegatingInstanceOrExpr): #e review name, etc ##e delegating?? ###k hmm, is it a command, or a CommandRun? can those be same class?
    "superclass for commands with their own property managers"
    # default ways to get the PM
    property_manager_groups = () # typically overridden by a subclass
    property_manager = Instance( PM_from_groups( _self.property_manager_groups ))
    # find the world -- maybe this belongs in a yet higher Command superclass? ###e
    world = Option(World)
    pass

class cmd_DrawOnSurface(PM_Command):
    """A command for creating a new object, a 3d polyline, by drawing it over any visible surface
    (but the resulting object is in absolute model coords, in this version).
       To use the command, some UI invokes it, one-time or as a mode, and an object of this class gets
    created and stored in some global place; then the next mousedown (on_press) on a tool-sensitive object
    of a kind this command's mousedown filter thinks it's applicable to (perhaps including empty space,
     though it's unclear which object that corresponds to -- but that doesn't concern this command)
    calls a method in this command for creating and returning an object to handle the drag (which can be self
    or some other recycled object, I suppose -- much like how Highlightable returns itself as the DragHandler, I guess).
       The drag event calls turn into the new object, and something in the end tells the outer stuff whether the
    new object gets really added or discarded (but it's probably present in the set of model objects from the start,
    even if it's only provisional -- outer code can decide if it shows up in the MT in that case, and if so, in what way).
    """
    # class constants, presumed to be part of a "registerable command API"
    # name and description
    cmd_name = "DrawOnSurface"
    cmd_desc = "draw 3D polyline over surface"
    cmd_desc_long = "draw a dense 3D polyline over a 3D surface, following its contours"
    
    #e categorization info, so a UI-builder knows where to include this command, how to classify it for browsing --
    # this includes what it needs to run, what it creates or modifies

    #e info about when this command can sensibly be offered, about what kind of command it is in terms of event-capturing
    # (one drag, many drags, uses selection, etc)...

    #e for when the command is "active":

    #e a display style (or mod of one?) to use -- filter what is shown, how its shown --
    # or maybe it's one of a family of commands that use the same display style -- then it needs to specify an interface
    # that it expects drawables to follow, while it's in effect -- and some overlying system has to decide whether to make
    # a new instance of a model-view and in what style... or maybe this command inserts itself into a tree of commands
    # and a higher node in the tree (a family of commands, maybe a main command of which this is a subcommand)
    # supplies the display style (incl filter) for all its subcommands...
    # ... ultimately this ensures that the drawables know enough for this command
    # to know how to highlight them, select them (if that can occur while it's active), which ones to operate on
    # (so it supplies its own selobj or glname filter)...

    # a property manager

    ## property_manager_groups = [make_polyline3d_PG] # functions to apply to an arg (which arg? ####), or exprheads, to get PM groups
        ##### why not just say make_polyline3d_PG(_self)???
    property_manager_groups = list_Expr( make_polyline3d_PG(_self) )

        # super should make property_manager from the groups, if we don't make a whole one ourselves [might be already stub-coded]
    
    ###e code for event handlers to initiate the drag

    delegate = _self.world # draw whatever is in there

        #####e TODO:   ####@@@@
    
        # Q: how do we get the things in _self.world to draw in the way we want them to? (style, filtering, highlighting)
        # A: provide them advice on that in our graphics dynenv, which we set up in a wrapper around the above delegation,
        # which is a drawing-interface (graphics interface) delegation.
        #
        # Q: when they get activated, how do they send events to us?
        # A: put ourself (as CommandRun with event interface they expect, e.g. on_press) into some dynenv var they can find.
        #
        # So I need a wrapper sort of like DraggableObject but different, and a scheme for World to draw things
        # with the right wrapper around them, and the right set of things, based on what the current command/mode favors.
        # WAIT -- should World do that at all? Maybe it just holds the objs and lets the mode map them into drawables?
        # Yes, that sounds better.
        #
        # For empty space events, when I draw the model through my filter, also draw BackgroundObject(thing to handle them).

    #e code for event handlers during the drag, eg on_drag -- in this class or (better) in another one (DragBehavior-like)
    def on_press(self):
        point = self.current_event_mousepoint()
        newpos = point + DZ * DZFUZZ # kluge: move it slightly closer so we can see it in spite of bg
            ###e needs more principled fix -- not yet sure what that should be -- is it to *draw* closer? (in a perp dir from surface)
            #e or just to create spheres (or anything else with thickness in Z) instead? (that should not always be required)

            ###BUG: DZ is not always the right direction!
            #e maybe scrap it here, and instead change class polyline3d to always draw itself closer to the screen
            # than its stored coords, but store coords identical to those of the underlying model object --
            # use a globally available displist (nim) for translating closer to the user -- hmm, that has to be different
            # for each rotational environment you might be inside! So only the graphical env knows its name...
        
        node_expr = Vertex(newpos, Center(Rect(0.2,0.2, red )))
        
        newnode = self.world.make_and_add( node_expr, type = "Vertex") #070206 added type = "Vertex"
            ###e may want to make, but not add... let it be a kid of the polyline3d
            
        self.newnode = newnode ###KLUGE that we store it directly in self; might work tho; we store it only for use by on_drag_bg
        return
    
    def on_drag(self):
        point = self.current_event_mousepoint()
        lastnode = self.newnode # btw nothing clears this on mouseup, so in theory it could be left from a prior drag

        newpos = point + DZ * DZFUZZ

        # inside a drawable, this is where we'd let the current tool decide what to do,
        # but in this polyline3d-making command we already know what to do:

        if not lastnode:
            print "bug: no self.newnode!!!"
        else:
            if not isinstance(lastnode, polyline3d):
                lastnode = self.newnode = self.world.make_and_add( polyline3d(lastnode), type = "polyline3d" )
                    ###e should we make and add this polyline3d, but get world to put it inside DraggableObject or so?
            lastnode.add_point(newpos)

        return

    def on_release(self):#070223 new hack
        import env #FIX - make this unnecessary
        if isinstance(self.newnode, polyline3d) and env.prefs.get(kluge_dragtool_state_prefs_key + "bla2", False):
            self.newnode._closed_state = True ####KLUGE, I'd rather say .closed but that won't work until I have OptionState
        return
    
    pass # end of class cmd_DrawOnSurface

# ==

# short term -- until demo_ui.py works,
# make a testexpr which keeps us in the state in which this command is active and its PM is showing.
# But the TODO items above are still needed to make this do anything.

class whatever(DelegatingInstanceOrExpr): # simulates the env that demo_ui will provide (stub version)
    ui_and_world = Instance(World())#####
    thisguy = Instance(cmd_DrawOnSurface(world = ui_and_world)) #e args? world? new object? does its super handle some? Command vs CommandRun?
    pm = SimpleColumn(TextRect("PM for DrawOnSurface"),
                      thisguy.property_manager )
    delegate = Overlay(
        thisguy,
        DrawInCorner(pm, corner = LOWER_RIGHT),
     )
    pass

our_testexpr = whatever() 

# ==

## __register__ = ['cmd_DrawOnSurface'] #e or could be filter(func, dir()) ... ###e is calling a global function clearer? yes.

auto_register( globals()) #e or list the objects?

# end
