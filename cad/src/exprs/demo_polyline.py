# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
demo_polyline.py -- demo file for Polyline datatype (too unsophisticated for real life) and related commands

$Id$

The "demo" in the filename indicates that this is not part of the exprs module per se,
but shows how to use it for a specific app. For use in our real app, lots of this will
be moved into new files and made more sophisticated (relative coords, relations, better editing, etc).

See also:
- demo_polygon.py,
- class polyline in testexpr_19g demo_drag.py
- (superseded by demo_draw_on_surface.py once that works),
- DragCommand scratch,
- free x-y rot code in draggable.py,
- demo_ui.py (which is supposed to be able to provide access to these commands).

"""

from exprs.command_registry import auto_register

from OpenGL.GL import GL_LIGHTING
from OpenGL.GL import glDisable
from OpenGL.GL import glColor3fv
from OpenGL.GL import glLineStipple
from OpenGL.GL import GL_LINE_STIPPLE
from OpenGL.GL import glEnable
from OpenGL.GL import glLineWidth
from OpenGL.GL import GL_LINE_LOOP
from OpenGL.GL import glBegin
from OpenGL.GL import GL_LINE_STRIP
from OpenGL.GL import glVertex3fv
from OpenGL.GL import glEnd

from utilities.constants import blue, noop

from exprs.Exprs import list_Expr, call_Expr
from exprs.instance_helpers import DelegatingInstanceOrExpr, ModelObject
from exprs.attr_decl_macros import State, Option, Arg
from exprs.ExprsConstants import StubType, ORIGIN

class CommandWithItsOwnEditMode( DelegatingInstanceOrExpr): #e rename! and inherit from Command or MouseCommand or so...
    "#doc"
    #e rename evidence -- this is not the command, it's the edit mode for the command, right?
    # in fact, maybe it's only the redraw code for that -- an even more specialized fragment of it.

    # note that the API inside this is pretty much an entire "edit mode" since it handles time, motion, maybe its own selobj alg, etc;
    # the first few methods I'm writing don't even depend on any other aspect of this.
    
    # note 2: maybe we want to deleg to an obj that does side effects from events, and let this do redraw --
    # rather than subclassing to that obj.

    # declare interface and give default methods/attrs for it

    # note: using xor mode is not obligatory, and someday we'll often use a better-looking method
    # (saved color and maybe depth image), and the xor mode look can be guessed from the more general
    # incremental look -- but classes that want xor-mode-specific drawing can define these anyway...

    def draw(self):
        """[subclass can override this if desired]"""
        self.draw_background()
        self.draw_incrementally_over_fixed_background()
        return

    def draw_background(self):
        """[subclass is encouraged to define this]
        #doc
        WARNING: subclass implem should avoid having its drawing effects change
        (in fact, should avoid using any usage tracked variable which changes)
        during mouse drags or baremotions which are supposed to update the screen quickly.
           That's because, if the state used by this does change, we'll need to redraw the background.
        [At least once we're smart enough to *know* we need to! But before we're smart enough to only redraw some of it.]
        """
        pass

    def draw_incrementally_over_fixed_background(self):
        """[subclass should define this, unless it needs no drawing beyond
        what's done in draw_background, or unless it overrides draw method itself]
        #doc
        """
        pass
    
    def draw_incrementally_for_xor_mode(self):
        """Draw our current graphics-area appearance (or undraw it -- we neither know nor care which)
        for use in xor-mode incremental drawing.
           Subclass implems can assume that the caller has set up the dynamic drawing env
        so that drawing primitives we call can find out that we're doing xor-mode incremental drawing
        and alter their color choices appropriately (since they probably know best how to do that). [###nim]
           They can also assume the caller will do whatever updating (e.g. swapbuffers) is needed, at the end.
           That means most subclasses can use the default method,
        which just calls self.draw_incrementally_over_fixed_background().
        """
        self.draw_incrementally_over_fixed_background()

    def do_baremotion_effects(self):
        """[subclass should define this, if baremotion can have any effects]
        Do whatever state changes are needed as a result of baremotion while we're active.
           WARNING: if any state changes that affect draw_incrementally_for_xor_mode are done
        outside of this method, xor-mode undrawing might not match drawing,
        and bad graphics appearance bugs will result.
        """
        return

    using_xor_mode_now = False # per-instance transient variable; let's hope no code reload can occur while it's True! #k
    using_background_incremental_drawing_now = False # ditto

    # see also some notes about a "better xor mode object" (not in cvs) [070325]
    
    def on_baremotion(self): #e args? grab from env? yes, submethod does that, not us.
        ### CALL ME - needs new interface... note, is API same for in motion or drag??
        #e optim: be able to change state, usage track, then *redraw using old state* if drawing effects got invalled.
        # too hard to do now vs its important (which is not high, since we assume the drawing we do here is fast).
        if self.using_xor_mode_now:
            # note: at this point we better make sure no state changes used by draw_incrementally_for_xor_mode have been done yet!
            self.draw_incrementally_for_xor_mode()
            # change state (based on mouse motion now being reported to us, selobj detection done now (NOT using glselect I hope), etc
            self.do_baremotion_effects()
            self.draw_incrementally_for_xor_mode()
        elif self.using_background_incremental_drawing_now:
            self.do_baremotion_effects()
            self.draw_incrementally_over_fixed_background()
        else:
            self.draw() ###k
        return

    def on_time_passing(self):
        "#doc [only needed if time-dependent animation needs doing; that might include delayed tooltip popups, fadeouts...]"
        assert 0 # nim # similar to on_baremotion -- maybe even identical if we decide that's simpler --
        # it probably is, since time passes during mouse motion too!
        pass
    
    #e ditto for other events - press, drag, release -- hmm, we don't want 5 complicated methods, better refactor this! ####

    pass

# ==

class ClickClickCommand( CommandWithItsOwnEditMode): #e rename!
    """Abstract class for a command in which repeated clicks build up one visible object, until terminated in some manner
    (e.g. by clicking in a final or illegal place, or using the escape key, or somehow invoking some other command).
    """
    # do subclasses provide just the clicking behavior, and interactive display, or also a PM or its data?
    # guess: not the PM -- let that be provided separately, even if it often goes along with a subclass,
    # and even if the subclass tells the UI env that a PM for that cmd and showing a specific target obj
    # would be good to show right now. The env can find one, or make one from knowing the target obj type if necessary...
    ###e note: this does NOT yet handle anything related to scripting or undo, like all commands someday must do --
    # tho hopefully when it does, almost no code changes will be needed in its specific subclasses.

    # declare interface and give default methods/attrs for it

    #e the 4 or 5 user event methods, i guess; things related to patterns of UI activity as command goes thru its phases
    
    pass

# ==

###e def the polyline model obj datatype



class SketchEntity( ModelObject):#e stub
    "abstract class for model objects which are Sketch Entities."
    
    #e what is special about a Sketch Entity, vs any old model object?
    # [the answers are what we want to encode in this class...]
    
    # - it is classified topically as a Sketch Entity:
    #   - by default, in a UI, commands for making one should appear in a "sketch entity toolbar".
    
    _e_model_object_topic = "Sketch Entity"
        # tells default UI where to put a command for making/editing one of these, a display style for one, etc
        ###e this attr name is a stub:
        # - it needs a prefix to say it's a decl about the class (or about an expr customized from a subclass of the class, I think)
        # - it needs to be more specific than just "topic" -- it's a topic about what?
        #   about the kind of model object this makes. But don't rely on superclass to tell you that,
        #   since topic is an attrname in an interface more general than just for model objects, i think.
        #   Also, if something delegates to this, it should only override this attr if it really wants to,
        #   not if it has some other kind of topic. So saying "model object topic" might be enough.
        #   - But maybe say kind rather than topic, since topic is something you can have more than one of??
        # Possible names:
        # _e_model_object_class - no, that would sound like it was the specific subclass name e.g. Polyline,
        #   even if the official name for that is different, e.g. using _type.
        #   Also _e_ has disadvantages.
        #   I wonder if this kind of decl (in some general sense) needs its own new prefix (not _i_ or _e_).
    
    # - maybe it needs to belong to a Sketch:
    #   - when making one, find or make a Sketch to contain it in a standard way
    #   - maybe a make-command for one can only run inside a sketch-making commandrun
    #     (which supplies the sketch, making it as needed).
    #   
    pass

# caps: Polyline or PolyLine? see web search?? just initial cap seems most common.
# note, in UI it might just be a line... OTOH that's not good in geometric prim code terms!

# about removing points from a polyline:
# fyi: http://softsurfer.com/Archive/algorithm_0205/algorithm_0205.htm
# "We will consider several different algorithms for reducing the [set of] points in a polyline
#  to produce a simplified polyline that approximates the original within a specified tolerance.
#  Most of these algorithms work in any dimension..."

class Polyline(SketchEntity): #e rename -- 2D or general? [see also class polyline3d in demo_draw_on_surface.py]
    #e assume SketchEntity super handles whatever relativity is needed? (even add_point coord transform??)
    # more comments on relativity at end of file

    # modified from: class polyline(InstanceOrExpr) in demo_drag.py, and some code therein that uses it (eg the add_point call)

    """A graphical model object with an extendable (or resettable from outside I guess) list of points.
    (Q: Does it also consider that some of them are draggable control points and some are not??
    Guess: not this class -- some other one might. This one considers all points to be equivalent independent state.)
       Also might have some Options, see the code -- or those might belong in wrapper objects for various display/edit modes.
    """
    ###BUGS: doesn't set color, depends on luck. 
    # could use cmenu to set the options.
    # end1 might be in MT directly and also be our kid (not necessarily wrong, caller needn't add it to MT).
    # when drawing on sphere, long line segs can go inside it and not be seen.
    points = State(list_Expr, []) ###k probably wrong way to say the value should be a list
##    end1arg = Arg(StubType,None)
##    end1 = Instance(eval_Expr( call_Expr(end1arg.copy,)( color = green) ))###HACK - works except color is ignored and orig obscures copy
##    end1 = Arg(StubType, None, doc = "KLUGE arg: optional externally supplied drag-handle, also is given our cmenu by direct mod")
    # these style settings ought to be State attrs of self, changeable by cmenu and/or PM, as well as by construction (less important).
    closed = Option(bool, False, doc = "whether to draw it as a closed loop")
    _closed_state = State(bool, closed) ####KLUGE -- closed and _closed_state should be a single OptionState attr [nim]
    linecolor = blue ###KLUGE -- we want it to be a StateOption
        ###e name this linecolor or color?? even if linecolor, also accept color and use it for default??
        # guess: I favor color for use as public option (but might like both to be there) and linecolor for use internally.
    linewidth = 2 ###KLUGE -- we want it to be a StateOption
    dashed = False ###KLUGE -- we want it to be a StateOption
##    relative = Option(bool, True, doc = "whether to position it relative to the center of self.end1 (if it has one)")
##    def _init_instance(self):
##        end1 = self.end1
##        if end1:
##            end1.cmenu_maker = self
##    def _C__use_relative(self):
##        "compute self._use_relative (whether to use the relative option)"
##        if self.relative:
##            try:
##                center = self.end1.center
##                return True
##            except:
##                #e print?
##                return False
##        return False
    def _C_center(self):
        #e how do we define the center? center of bbox??
        #e is the center of rotation necessarily the same? (guess: yes -- what *else* would center mean, or be needed for?)
        # (if so, it ought to approximate the center of a minimal bounding circle -- ie its own bradius not be much larger than needed)
##        if self._use_relative:
##            return self.end1.center # this can vary!
##        return ORIGIN
        assert 0 # nim
    def _C_origin(self): #070307 renamed this to origin from center (in demo_drag.py version); not sure if needed here at all
##        if self._use_relative:
##            return self.end1.center # this can vary!
        return ORIGIN
    def add_point(self, pos, replace = False):
        """add a point at the given 3d position pos; if replace is True, it replaces the existing last point.
        If pos is None, then no point is added, and the last one is removed if replace is true.
        """
        if replace:
            self.points = self.points[:-1]#UNTESTED
        if pos is not None:
            pos = pos - self.origin ##e be more general -- but should be done by superclass or glue code or by calling transform method...
            self.points = self.points + [pos] ### INEFFICIENT if lots of points, but need to use '+' for now to make sure it's change-tracked
        return
    def make_selobj_cmenu_items(self, menu_spec, highlightable):
        """Add self-specific context menu items to <menu_spec> list when self is the selobj (or its delegate(?)... ###doc better).
        Only works if this obj (self) gets passed to Highlightable's cmenu_maker option (which DraggableObject(self) will do).
        [For more examples, see this method as implemented in chem.py, jigs*.py in cad/src.]
        """
        menu_spec.extend([
            ("Polyline", noop, 'disabled'), # or 'checked' or 'unchecked'; item = None for separator; submenu possible

##            ("show potential crossovers", self._cmd_show_potential_crossovers), #e disable if none (or all are already shown or real)
##
##            ("change length", [
##                ("left extend by 1 base", lambda self = self, left = 1, right = 0: self.extend(left, right)),
##                ("left shrink by 1 base", lambda self = self, left = -1, right = 0: self.extend(left, right)),
##                ("right extend by 1 base", lambda self = self, left = 0, right = 1: self.extend(left, right)),
##                ("right shrink by 1 base", lambda self = self, left = 0, right = -1: self.extend(left, right)),
##                ("both extend by 1 base", lambda self = self, left = 1, right = 1: self.extend(left, right)),
##                ("both shrink by 1 base", lambda self = self, left = -1, right = -1: self.extend(left, right)),
##             ] ),
        ])
    pass # end of class Polyline

Drawable = DelegatingInstanceOrExpr #stub; might replace Widget if it becomes real; but Widget is not delegating -- what's up there?
#e also we might put in the delegate = Arg in here,
# plus maybe another arg for the layer... otoh, if that's .env, it gets here specially
# as an implicit make arg, not as an Arg!

class Polyline_draw_helpers( Drawable):
    # The idea is that we delegate to a Polyline, and it keeps all ModelObject state & methods & has superclass for that,
    # but this class can wrap it for purpose of drawing it, and variants or subclasses of this class
    # can wrap it for drawing it in other styles or edit modes (varying display or behavior),
    # and a bundling class that can delegate diff attrs to diff delegs is possible but not yet known if needed.
    #
    # As for our own superclass, it would be based on the interface we're defining support for,
    # but which our delegate doesn't support, or for which we want to ignore whatever support it provides
    # (since that will happen -- anything our superclass defines will not be delegated).
    #
    # NOT YET KNOWN:
    # - naming convention for classes like this
    # - how they are registered as contributing to how to pull a Polyline into a view (and whether to let name do that automatically)
    # - do we have to say we have delegate = Arg(), or is that known from our superclass?
    # - if it's known, can we add more Options (or Args) of our own?
    # - is there also a standard arg for the layer we're in? (BTW if so, is this somehow related to self.env, or taking its place?)
    # - does the layer the new obj is instantiated into remove all need for specifying layers in State decls, and splitting ipath??
    delegate = Arg(Polyline)
    def draw(self):
        self.draw_lines()
        #e option to also draw dots on the points
        #  [btw they might be draggable -- but that's for an edit-wrapper's draw code
        #   (and it might make draggable points on-demand for speed, and use a highlight method other than glnames... #e)]
        if 0:
            self.draw_points()
        return
    def draw_lines(self):
        "draw our line segments, using our current style attrs [which are partly nim]"
        # find variables which determine our GL state
        color = self.fix_color(self.linecolor)
        dashEnabled = self.dashed
        width = self.linewidth
        
        # set temporary GL state (code copied from drawer.drawline)
        glDisable(GL_LIGHTING)
        glColor3fv(color)
        if dashEnabled: 
            glLineStipple(1, 0xAAAA)
            glEnable(GL_LINE_STIPPLE)
        if width != 1:
            glLineWidth(width)
        # draw the lines
        if self._closed_state:
            glBegin(GL_LINE_LOOP)
        else:
            glBegin(GL_LINE_STRIP)
        for pos in self.points:
            glVertex3fv(pos) # [note from old code: could be pos + origin if that can matter]
        glEnd()
        # restore default GL state [some of this might be moved up to callers]
        if width != 1:
            glLineWidth(1.0) 
        if dashEnabled: 
            glDisable(GL_LINE_STIPPLE)
        glEnable(GL_LIGHTING)
        return
    def draw_points(self):
        "[nim] draw our points, using our current style attrs"
        for pos in self.points:
            pass ###e draw a dot - how ? same size even if 3d & perspective?? prob ok as approx, even if not the true intent...
            # in that case we'll eventually be using a texture (or pixmap) with alpha so it looks nice!
        return
    def draw_alignment_lines(self):
        "helper method for some interactive drawing wrappers: draw yellow and blue dotted alignment lines for the last segment"
        assert 0 # nim
    def draw_tooltip(self):
        #e does this even belong here? prob not -- let edit wrapper ask for info and do it from the info
        assert 0 # nim
    pass # end of class xxx

class _draggable_polyline_point(DelegatingInstanceOrExpr): # experimental 070308
    pass


def draggable_polyline_point(polyline):
    "return a func of a point" ##E oops! the point needs to know its index in the polyline! (and the polyline itself.)
    # it seems we don't want a pos like polyline.points has now, but a Point object for the polyline to give us!
    # e.g. polyline.point_objects, where each knows parent, has state, setting its state changes the parent state...
    return lambda point: 'bla'

OverlayList = StubType ## Overlay #stub
map_Expr = StubType

class dragverts_Polyline(DelegatingInstanceOrExpr): # experimental 070308
    polyline = Arg(Polyline)
    func = call_Expr( draggable_polyline_point, polyline)
    delegate = OverlayList( polyline,  ##e make Overlay itself able to take a list arg mixed with a nonlist arg? Like Column?
                            map_Expr( func, polyline.points ) ) ### .points can be what we need, if .point_posns is what this used to be
    pass ###stub

#e type-inspecting/browsing/searching defs?

#e PM defs? how indep of commands are these, btw? general UI Q: given existing one, can you edit it with mouse
# much like you are allowed to make one? If so, in general, how does that affect the code here --
# do we pass an optional existing polyline to the so-called cmd_MakePolyline (so it starts off as if it's already making it)?
# but the mouse would be in the wrong place... unless we only did that when user clicked right on the end-node in it!
# instead do they click on any control vertex and we call this with the polyline and the control vertex both?
# but that (drag an existing control point) is probably a different command, anyway. see also demo_polygon for a related one.

# ==

class cmd_MakePolyline(ClickClickCommand): ##e review naming convention (and interface scope);
    # this cmd_ in the name might imply more, like bundling in a PM too -- or maybe that's ok but optional...
    # and OTOH since it's really the edit mode for that cmd, it may say editmode_MakePolyline or so instead. ##e

    # note: the superclass knows about this kind of drawing... and xor mode (just one kind of drawing it can do, of several)...
    # we just provide the state change methods and draw helper methods like draw_incrementally_for_xor_mode

    # args (?)
    #e the model
    #  - how to make things to add to it -- current config, parent for new objs, etc
    #  - what to show within it, when we draw
    #e the UI
    #e etc
    
    # state
    polyline = None # the polyline we're making/editing, if any
        ##e use State()?? or is this really just a ref to a model obj, or a proposed one
        # (created as a real obj, but not nec. in the MT or cur config yet)?
        # But either way, the polyline itself, or its attrs, or both (whatever can change as we run) do need to be usage tracked. ###e
        
    #e attrs for whether we're rubberbanding it right now, and data if we are (see especially class polyline in demo_drag re this)
    
    # appearance in graphics area
    def draw_background(self):
        "[implements abstract class method]"
        #e this could include fixed parts of the line, if they are numerous; that probably doesn't matter for now
        pass

    def draw_incrementally_over_fixed_background(self):
        """[implements abstract class method]"""
        #e don't draw if end posn is illegal! (as noticed from a formula on some self-state which we assume is set properly)
        # but do draw the selobj-highlighting for anything that needs it during this op!!!
        self.polyline.draw()
        #e also draw the yellow and blue alignment lines, if present
        return

    #e actions for building it -- grab them from class polyline in demo_drag.py

    pass # end of class cmd_MakePolyline

#e more commands for one? cmenu commands? etc

# ==

##e register the types & commands [stub]


##this_module_registry = registry() #e that should also register this registry with a more global one!
##
####class _x: pass # used only for _x.__module__ in following call [e.g. 'exprs.demo_polyline']
##
##auto_register( this_module_registry, globals()) ## , _x.__module__ )

auto_register( globals()) ###e this function needs a more explicit name -- and passing the specific classnames would be better

# ==

'''say above: intercept in testmode - baremotion, update_selobj i guess
and some other selobj controls
prob no need to intercept them in selectMode itself
but i am not sure...
i could have said the same about all my other mods to it...
'''

#e also move new incr methods in controls.py to class HL 

#e also say above where we get in and out of opengl xor mode, and grab eg code from BuildCrystal_Command or zoom or whatever to do that
# (as helper methods in the superclass, or a mixin just for xormode drawing, which could define a swapbuffers method too)

# btw is xormode used now for incr drawing in selmode itself, for region sel -- and if not why not?
# is region sel itself able to be a cmd of this form -- even though the std editmode might get into it as its emptySpaceLeftDown?
# btw, an advantage of xor mode in that case - it's ok if you didn't have a premade screen image around.

'''really do review class polyline soon, and old demo_polygon too, esp for its Command supers, and command_scratch file too.

an eg issue that came up in class polyline:
we need to know what the sketch entity coords are rel to. If it's both draggable, and in/on a ref plane or surface,
then it might be two-level-relative... tho the relativity for Draggable is probably best thought of as transient.

ui discussion: the initial editmode lets you click to add segments, or Undo to un-add them i think (ie to undo the last click
 but not get out of being in the rubberband line mode),
but there is also some way to drag verts or edges or add new control points or remove old ones...
but how is that controlled -- a toolset in the PM? yet another level of flyout toolbar? PM tools seem preferable...

code structure discussion: class polyline is one thing, and an editable view of it another,
and they are different! The editable view is made by mapping the polyline elements into drawables with bindings,
which differ depending on editmode and tool... tho for just making it (not fancier editing) this might not be needed.
'''

# end
