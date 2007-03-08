"""
demo_polyline.py

$Id$

see also demo_polygon, polyline in _19g demo_drag, and DragCommand scratch, and free x-y rot code, and demo_ui.py

Is this the command to make one (maybe rename it demo_cmd_polyline.py)
or the data type too, which happens to include the command (this name is good)?

The "demo" is because it's not part of the exprs module per se, but shows how to use it for a specific app.
"""

from basic import *


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
        nim # similar to on_baremotion -- maybe even identical if we decide that's simpler --
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

SketchEntity = ModelObject #e stub

# caps: Polyline or PolyLine? see web search?? just initial cap seems most common.
# note, in UI it might just be a line... OTOH that's not good in geometric prim code terms!

# about removing points from a polyline:
# fyi: http://softsurfer.com/Archive/algorithm_0205/algorithm_0205.htm
# "We will consider several different algorithms for reducing the [set of] points in a polyline
#  to produce a simplified polyline that approximates the original within a specified tolerance.
#  Most of these algorithms work in any dimension..."

from OpenGL.GL import *

class Polyline(SketchEntity): #e rename -- 2D or general?
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
    closed = Option(bool, False, doc = "whether to draw it as a closed loop")
    _closed_state = State(bool, closed) ####KLUGE -- closed and _closed_state should be a single OptionState attr [nim]
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
        nim
    def _C_origin(self): #070307 renamed this to origin from center (in demo_drag.py version); not sure if needed here at all
##        if self._use_relative:
##            return self.end1.center # this can vary!
        return ORIGIN
    def add_point(self, pos, replace = False):
        "add a point at the given 3d position; if replace is True, it replaces the existing last point"
        pos = pos - self.origin ##e be more general -- but should be done by superclass or glue code or by calling transform method...
        if replace:
            self.points = self.points[:-1]#UNTESTED
        self.points = self.points + [pos] ### INEFFICIENT if lots of points, but need to use '+' for now to make sure it's change-tracked
    def draw(self):
        self.draw_lines()
        #e option to also draw dots on the points
        #  [btw they might be draggable -- but that's for an edit-wrapper's draw code
        #   (and it might make draggable points on-demand for speed, and use a highlight method other than glnames... #e)]
        if 0:
            self.draw_points()
        return
    def draw_lines(self):
        "draw our line segments, using our current style attrs [which are nim]"
        ###e WHAT SETS COLOR? see drawline - in practice it's thin and dark gray - probably just luck!
        ###e also want to set width, style... and these ought to be state attrs of self, changeable by cmenu and/or PM, in fact.
        if self._closed_state:
            glBegin(GL_LINE_LOOP)
        else:
            glBegin(GL_LINE_STRIP)#k
##        if self._use_relative:
##            # general case
##            origin = self.origin
####            # also include origin as first point!
####            glVertex3fv(origin)
##            for pos in self.points:
##                glVertex3fv(pos + origin)
##        else:
##            # optim
        for pos in self.points:
            glVertex3fv(pos)
        glEnd()
    def draw_points(self):
        "[nim] draw our points, using our current style attrs"
        for pos in self.points:
            pass ###e draw a dot - how ? same size even if 3d & perspective?? prob ok as approx, even if not the true intent...
            # in that case we'll eventually be using a texture (or pixmap) with alpha so it looks nice!
        return
    def draw_alignment_lines(self):
        "helper method for some interactive drawing wrappers: draw yellow and blue dotted alignment lines for the last segment"
        nim
    def draw_tooltip(self):
        #e does this even belong here? prob not -- let edit wrapper ask for info and do it from the info
        nim
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

    pass
    
    pass

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

    pass

#e more commands for one? cmenu commands? etc

# ==

##e register the types & commands

'''say above: intercept in testmode - baremotion, update_selobj i guess
and some other selobj controls
prob no need to intercept them in selectMode itself
but i am not sure...
i could have said the same about all my other mods to it...
'''

#e also move new incr methods in controls.py to class HL 

#e also say above where we get in and out of opengl xor mode, and grab eg code from cookiemode or zoom or whatever to do that
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
