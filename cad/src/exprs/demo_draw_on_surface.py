# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
demo_draw_on_surface.py

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

070319 a standalone version of the so-called polyline example in demo_drag.py (testexpr_19g)

See also:
- demo_polyline.py (and the other files it refers to, like demo_ui.py)
- TODO comments below
- our_testexpr at bottom (substitute for demo_ui until it's ready)

"""

from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import glBegin
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEnd

from utilities.constants import yellow, purple, red, noop

from widgets.simple_dialogs import grab_text_using_dialog

from exprs.Exprs import list_Expr
from exprs.If_expr import If
from exprs.Column import SimpleColumn, SimpleRow
from exprs.Boxed import Boxed
from exprs.TextRect import TextRect
from exprs.Rect import Rect
from exprs.world import World
from exprs.Highlightable import Highlightable, BackgroundObject
from exprs.Overlay import Overlay
from exprs.controls import checkbox_pref, ActionButton
from exprs.draggable import DraggableObject
from exprs.projection import DrawInCorner
from exprs.Center import Left, Top, Center
from exprs.transforms import Translate
from exprs.iterator_exprs import MapListToExpr, KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr
from exprs.demo_drag import Vertex, kluge_dragtool_state_prefs_key, DZFUZZ
from exprs.command_registry import auto_register
from exprs.instance_helpers import InstanceOrExpr, DelegatingInstanceOrExpr
from exprs.attr_decl_macros import State, Arg, Option, ArgOrOption, Instance
from exprs.ExprsConstants import StubType, Width, Color, Point, PM_CORNER, ORIGIN, DZ
from exprs.widget2d import Stub
from exprs.__Symbols__ import _self, Anything

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
    #e rename? this name means "PG for the command make_<class>"
    ###e who supplies this? the command? i guess so. is it a local class inside it? or at least the value of an attr inside it?
    "contents of property manager group for a polyline3d which is being made"
    ###e needs some args that let it find that polyline3d or the making-command!
##    arg = Arg()
    #e someday be able to automake this from higher-level contents... but returning a widget is always going to be a possibility
    # (see also comments in PM_from_groups about this)
    title = "Polyline Properties" ###e USE ME in PM_from_groups
    delegate = SimpleColumn(
        checkbox_pref( kluge_dragtool_state_prefs_key + "bla2", "closed loop?", dflt = False), # only gets closed when done -- ok??
    )
    pass

class PM_from_groups(DelegatingInstanceOrExpr): ###e refile into demo_ui or so, and call it on [make_polyline3d_PG(somearg)]
    "Make a Property Manager UI from a list of groupbox content widgets (eg columns of field editors) and other info."
    # args
    groups = Arg(list_Expr)
        #e in future these groups need to come with more attrs, like group titles
        # (WAIT, they already do have a title attr which we don't use here!),
        # whether they're closable and if so whether initially closed...
        # and they might include their own Boxed already...
        # the type decl might say we want a list of PropertyGroupBoxes,
        # with autoconversion of ParameterGroups to those...
    message = Option(str, "(PM message goes here)") # this has to be already split into lines, for now; all indentation is stripped
    # formulae
    def _C_use_message(self):
        lines = self.message.split('\n')
        lines = [line.strip() for line in lines]
        lines = filter(None, lines)
        return '\n'.join(lines)
    use_message = _self.use_message
    # appearance
    message_box = Boxed(TextRect(use_message), gap = 0, bordercolor = yellow)
    group_box_column = MapListToExpr(
        KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(Boxed), ###e change to a GroupBox, with a title from the group...
        groups,
        KLUGE_for_passing_expr_classes_as_functions_to_ArgExpr(SimpleColumn)
     )
    delegate = SimpleColumn(
        Left(message_box),
        Left(group_box_column),
     )
    pass

# ==

class PM_Command(DelegatingInstanceOrExpr): #e review name, etc ##e delegating?? ###k hmm, is it a command, or a CommandRun? can those be same class?
    "superclass for commands with their own property managers"
    # default ways to get the PM
    property_manager_groups = () # typically overridden by a subclass
    property_manager_message = _self.__class__.__name__ #e improve, use _C_ if needed # typically overridden by a subclass
    property_manager = Instance( PM_from_groups( _self.property_manager_groups, message = _self.property_manager_message ))
    # find the world -- maybe this belongs in a yet higher Command superclass? ###e
    world = Option(World)
    pass

# ===

class _cmd_DrawOnSurface_BG(Highlightable):
    "[private helper] background drag event bindings for cmd_DrawOnSurface; intended for use inside BackgroundObject()"
    # args [needed for sharing state with something]
    world = Option(World)
    #e code for event handlers during the drag, eg on_drag
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

        self.newnode = newnode
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
        import foundation.env as env #FIX - make this unnecessary
        if isinstance(self.newnode, polyline3d) and env.prefs.get(kluge_dragtool_state_prefs_key + "bla2", False):
            self.newnode._closed_state = True ####KLUGE, I'd rather say .closed but that won't work until I have OptionState
        return
    pass # end of class _cmd_DrawOnSurface_BG

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
    property_manager_message = """
        Sketch a 3D polyline
        on any model surface
        or in free space.
        [Note: model surface
        is NIM for click, but
        works for drag-over.]
    """

        # super should make property_manager from the groups, if we don't make a whole one ourselves [might be already stub-coded]

    # appearance of world while we're active, including code for click/drag event handlers for objects or bg
    #e (someday we might need to separate the bg and the rest, so an outer rendering loop can handle them separately)
    delegate = Overlay(
        _self.world, # draw whatever is in there
            ###BUG: actual objects are not yet drawn in a way that lets them delegate drags to us -- only the BG does that yet.
            # Possible fixes:
            # 1. One is discussed below -- get the objects to delegate their drag event calls to us,
            # also passing self for coordsys, altered behavior, etc. Do this by drawing a wrapped version of them that
            # looks in graphics env for what to do.
            # 2. Another way might be simpler: in testmode.get_obj_under_cursor, which replaces None with our BackgroundObject,
            # also replace *other* objects with it, if they are a kind we wish to draw on or cause to be ignored (except for their
            # pixel depth)! Or, replace them with a wrapped version of themselves, created dynamically... [##k fast enough??]
            # In general a command may well want to be involved in those highlighting decisions, and that's one way.
            # (Though we do have to worry about effects on highlighting, between and within drags.)
        BackgroundObject( _cmd_DrawOnSurface_BG(world = _self.world)),
     )
    pass # end of class cmd_DrawOnSurface

        #####e TODO:   ####@@@@

        # Q: how do we get the things in _self.world to draw in the way we want them to? (style, filtering, highlighting)
        # A: provide them advice on that in our graphics dynenv, which we set up in a wrapper around the above delegation,
        # which is a drawing-interface (graphics interface) delegation. [or see another easier way, in a comment just above]
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
        # [done]

        # Someday: measure the pixel depth to affect this drawing, after drawing the model, but before drawing the
        # "front plane of 2d control widgets",
        # or hover-highlights, or whatever object you're creating based on the depth (eg a polyline3d in this code).
        # Right now it's measured after all drawing, so it's often too near to the user -- especially bad if you wiggle
        # the mouse around in one place and go over what you just drew -- because of our drawing it closer by DZFUZZ
        # (or even storing it closer, as now -- worse in other ways but both are bad in this way).
        #    If you detected what objects owned the pixels, you could leave out the ones
        # you don't want after the fact, interpolating depths for those points -- imperfect, but better than now,
        # and no need for measuring intermediate depths or controlling rendering order. Or, you could ask model objs
        # to compute their ideal depth rather than relying on pixeldepth. When we want to store intrinsic coords rel to them,
        # we'll need related abilities anyway. It'd have ambiguities for surfaces right on the near clipping plane, though,
        # unless you could tell the pixels you touched came from specific objects.

# ===

class TextEditField(DelegatingInstanceOrExpr):
    text = State(str, "(empty)") #e dflt should be an arg, or more to the point, the text should come from a stateref ###DOIT
    label = Option(str, "(field label)")
    dialog_title = Option(str, "(title)")
    dflt_dialog_label = "enter some text; use @@@ for \\n" # a public class attr (for clients to use in longer labels)
    dialog_label = Option(str, dflt_dialog_label)
    delegate = Highlightable(
        SimpleRow(Top(TextRect(label)), Top(TextRect(text))), #e long enough? too long? nlines ok? # Top is for when >1 line in text
        #e highlight form with blue border?
        on_doubleclick = _self.on_doubleclick, # on_press -> on_doubleclick -- probably better
        sbar_text = "double-click to edit textfield",
        #e cmenu binding too?
     )
    def on_doubleclick(self):
        ok, text = grab_text_using_dialog( default = self.text,
                                           title = self.dialog_title,
                                           label = self.dialog_label )
        if ok:
            #e unicode?? (see cad/src MT Node renaming code, or Node.name mmp code, or the Comment Node,
            # for example code that can handle it)
            #e filter through a func about what's acceptable?
            # if it fails, repeat dialog with more specific label?
            # strip whitespace? etc
            # eventually customize all that, for now just do what's most useful right here
            text = text.strip()
            self.text = text # changes state
        else:
            print "cancelled text edit, old text remains: %r" % (self.text,) #e some other place to put a message in the UI?
        return
    pass

# ===

# how short can another command be?
# ... looks like its UI needs to be thought through, or the longest part will be the scratch comments! #e
ColorEdit = TextEditField ###WRONG ARGS
color_ref = label = "stubs"
    ###BTW, StateRefs must not be designed well yet, since I'm always reluctant to use one and/or I forget how.
    # also I need new HL helpers for them, eg to turn one (eg for Color) into another (for text) using state transforms --
    # that latter one needs to be able to reject some sets since they don't meet its conds, noticably by the setting code.
    # (by raising ValueError??)
    # Digr: actually, if user can enter color using text, the state should include the text, not only the color derived from it!!
    # So that helper function might be misguided in this context.

Movable = Stub

class StatefulRect(DelegatingInstanceOrExpr): ###UNFINISHED but works for now
    # args
    rect = ArgOrOption(Movable(Rect), Rect(1,1,yellow), doc = "copy state from a snapshot of this guy's state")
        ###k not sure of Movable; for now, we ignore it and just grab out the state attrs we happen to know about as Rect attrs
    # state (maybe stateargs?)
    width = State(Width, rect.width)
    height = State(Width, rect.height)
    color = State(Color, rect.color)
    # appearance ###k missing the Movable -- does that belong in here, anyway??
    delegate = Rect(width, height, color)
    pass


class _cmd_MakeRect_BG(Highlightable):
    """Background event bindings for dragging out new Rects.
    (Not involved with selecting/moving/editing/resizing rects after they're made,
     even if that happens immediately to a rect this code makes from a single drag.)
    """
    # args [needed for sharing state with something]
    world = Option(World)
    #e something to share state with a control panel in the PM - unless we just use prefs for that

    # The drag event handlers modify the following state and/or derived objects (some documented with their defs):
    # self.rubber_rect = None or a newly made Rect we're dragging out right now
    #  (implemented as a rubberband-object drawable -- NOT a model object -- since it has formulae to our state, not its own state)
    #
    # nim: self.newnode = None or a Model Object version of the Rect we're dragging out now, or last dragged out...
    #  in general this may be redundant with "the selection", if dragging out a rect selects it, or shift-dragging it adds it to sel...
    # note, which of these are change-tracked? the ones used in drawing. that means all of them i guess.

    startpoint = State(Point, None, doc = "mousedown position; one corner of the rect") #e (or its center, for variants of this cmd)
    curpoint = State(Point, None, doc = "last mouse position used for the other corner of the rect")
    making_a_rect_now = State(bool, False, doc = "whether we're making a rect right now, using the current drag")

    # formulae
    whj = curpoint - startpoint # contains dims of current rect; only valid while we're making one, or after it's done before next press
    w = whj[0] ###k what if negative?? evidently we make a neg-width Rect and nothing complains and it draws properly... ###REVIEW
    h = whj[1] # ditto
    color = purple # for now -- will be a pref or PM control for the color to use for new rects
    rubber_rect = Instance( If( making_a_rect_now, Translate(Rect(w,h,color),startpoint)) )
        # this Instance is needed, at least by Highlightable
    # appearance -- note, for superclass Highlightable, this is plain, not delegate, and must be an Instance.
    # This means it's not good to subclass Highlightable rather than delegating to it. (Especially in example code!) ###FIX
    ## delegate = _self.rubber_rect
    plain = _self.rubber_rect

    # code for event handlers during the drag.
    def on_press(self):
        self.startpoint = self.current_event_mousepoint()
        self.making_a_rect_now = False #k probably not needed
            # don't make until we drag!
        self.curpoint = None #k probably not needed, but might help to catch bugs where whj is used when it shouldn't be
        #e change cursor, someday; sooner, change state to name the desired cursor, and display that cursorname in the PM
        return

    def on_drag(self):
        self.curpoint = self.current_event_mousepoint( plane = self.startpoint )
        self.making_a_rect_now = True
        return

    def on_release(self):
        ##e decide whether to really make one... here, assume we do, as long as we started one:
        if self.making_a_rect_now:
            node_expr = DraggableObject(StatefulRect(self.rubber_rect)) #e StatefulMovableRect? StatefulSnapshot(self.rubber_rect)??
                ###k can we just pass the rubber rect and assume StatefulRect can grab its state from it by taking a snapshot??
                ###WRONG for DraggableObject to be here, I think -- it's how we display it -- not sure, at least movability might be here...
                ### the posn is in the rubber_rect since it has Translate... this seems potentially bad/klugy tho...
                # older cmts, related: ... also its state needs to include abs posn...
                # maybe this means, split DraggableObject into event binding part (for this UI) and Movable part (for abs posn state). #k
            self.newnode = self.world.make_and_add( node_expr, type = "Rect")
                ###BUG (understood): type = "Rect" is not affecting sbar_text in DraggableObject. Need to add it in StatefulRect itself.
            self.newnode.motion = self.startpoint ###KLUGE
            self.making_a_rect_now = False # hide the rubber rect now that the real one is there
        else:
            print "fyi: click with no drag did nothing" ##e remove after debug
        return

    pass # end of class _cmd_MakeRect_BG


class make_Rect_PG(PropertyGroup):
    "property group contents for making a Rect"
    # note: classname includes make_Rect rather than MakeRect,
    # since it might not be the *only* PG for cmd_MakeRect, and it might be shared by other commands' PMs.
    # (not sure this is sensible)
    title = "Rect properties"
    delegate = SimpleColumn(
        ColorEdit( color_ref, label ), ##e [could put color name into prefs, for now...]
        #e dimensions? (numeric textfields) co-update with its draggability? yes...
        #e someday: units, gridding, ref plane, ...
     )
    pass

class cmd_MakeRect(PM_Command):
    """#doc
    """
    # name and description
    cmd_name = "MakeRect"
    cmd_desc = "make a screen-aligned rectangle" # in abs coords, with choosable fill color

    # property manager
    property_manager_groups = list_Expr( make_Rect_PG(_self) )
    property_manager_message = """
        Drag out a purple Rect.
    """

    # appearance of world while we're active, including code for click/drag event handlers for objects or bg
    background = Instance( _cmd_MakeRect_BG(world = _self.world) ) #k might not need to be split out, once bugs are fixed
    delegate = Overlay(
        _self.world,
        background, ####e SHOULD NOT BE NEEDED, but doesn't work anyway
        BackgroundObject( background ),
     )
    pass # end of class cmd_MakeRect

# cmd_MakeRect status as of 070326 mon morn:
# - ###TODO: need some visual indication after click, that drag would now make a rect... not sure what it can be... a tiny but toobig one??
#   of course the best one is a cursor... how hard can it be to make a cursor? we have tons of example code for it...
#   and for now, just pick an existing one that looks ok here.
# - kluges about copying state, especially abs position
# - lots of nfrs, esp color
# - don't know why neg widths are working, but my guess is, Rect allows them and doesn't cull when drawing #k; needs cleanup
#
# mainly, i need to integrate all this with demo_ui.py.

# ===

# short term -- until demo_ui.py works,
# make a testexpr which keeps us in the state in which this command is active and its PM is showing.
# But the TODO items above are still needed to make this do anything.

class whatever(DelegatingInstanceOrExpr): ###e rename
    # simulates the env that demo_ui will provide (stub version, evolving to be more like it)
    ui_and_world = Instance(World())#####
    ###e following needs to permit cmd_DrawOnSurface to vary
    # (at least let it also be cmd_MakeRect; use a menu of options? or use one ActionButton per command, since more like a toolbar?)
    # -- but with Instance inside the variation, I think --
    # ie it should be a map from the desired cmd expr to the cmd instance -- or, make a new one each time, so it's a cmdrun...
    # maybe see how demo_ui/toolbar was planning to do it... ###e
    toolbar = SimpleColumn(
        ActionButton( _self.do_cmd_DrawOnSurface, "button: cmd_DrawOnSurface"), #e make the text from the command #e the running one should look pressed
        ActionButton( _self.do_cmd_MakeRect, "button: cmd_MakeRect"),
     ) ###e show it where? above PM for now?
    current_cmdrun = State(Anything, None) # what is actually in here? an Instance of a "command run",   [btw is None needed??]
        # or of a command obj that handles multiple runs (ie a command_runner?)... up to it to not get messed up if that happens
        # (and for now, unfortunately, not remaking it is probably a significant speed optim)
        # (so should we let an outer command handler have the PM and get reused, but an inner CommandRun get remade? why bother?)
    def do_cmd_DrawOnSurface(self): #e which name is better: do_cmd or set_cmd? depends on type of command!
        self._do_cmd( cmd_DrawOnSurface)
    def do_cmd_MakeRect(self):
        self._do_cmd( cmd_MakeRect)
    def _do_cmd( self, cmd):
        "set self.current_cmdrun, etc..."
        # do we make a new one if button pressed when one already running?? yes for now.
        self.current_cmdrun = self.Instance( cmd(world = self.ui_and_world), id(cmd) ) #e cache that expr? index ok? why cache instance?
            #old cmt: #e args? world? new object? does its super handle some? Command vs CommandRun?
    pm = current_cmdrun.property_manager
    corner_stuff = SimpleColumn( toolbar, pm)
    delegate = Overlay(
        current_cmdrun,
        DrawInCorner( corner_stuff, corner = PM_CORNER),
     )
    def _init_instance(self):
        super(whatever, self)._init_instance()
        self.do_cmd_MakeRect() # or at least set some command, preferably a "null" or "default" one
            # note that this resets the current tool state on reload -- not really desirable;
            # how was demo_ui planning to handle that? ###k
    pass

our_testexpr = whatever()

# ==

## __register__ = ['cmd_DrawOnSurface'] #e or could be filter(func, dir()) ... ###e is calling a global function clearer? yes.

auto_register( globals()) #e or list the objects?

# end
