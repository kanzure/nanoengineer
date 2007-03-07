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

# caps: Polyline or PolyLine? see web search?? note, in UI it might just be a line... OTOH that's not good in geometric prim code terms!

class Polyline(SketchEntity): #e rename both (2D or not?) [(see especially class polyline in demo_drag)]
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

# say above: intercerpt in testmode - bafemotion, update selobj i guess
and some other sleobj controls
prob no need to intrercept them in seletMOde itself
but i am not sure..
i could have said same about all my other mods to it...

#e also move new incr methods to HL from controls

#e also say above where we get in and out of xor mod and grab eg code from cookieor wgatever
#btw is it used now for incr edrawing in selmode itself, for region sel , and if not why not?
#is region el itself a cmd of this form -- even though the std editmode might get into it?
#adv of xor mode in that case - ok if you didn't have a premade screen image aorund

really do review class polyline soo, anf old demo_poygon too esp for its Command suers, and command scratc file too

# end
