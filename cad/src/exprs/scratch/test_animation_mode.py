"""
test_animation_mode.py -- scratch code for animation loop, connectWithState, exprs drawing.

@author: Bruce
@version: $Id$

To run this code:

1. shell commands to make a symbolic link
(or you can copy it if you don't want to recommit your edits):

% cd ~/Nanorex/Modes
% ln -s /Nanorex/trunk/cad/src/exprs/scratch/test_animation_mode.py .  # or whatever this file's absolute pathname is

2. rerun NE1 (needed?)

3. debug menu -> custom modes -> test_animation_mode

History: this was mostly written long ago in my spare time,
just for fun. I put it in cvs since it's sometimes useful now
as a testbed.

Bugs:

updated 070831

- Needs fix for exit to remove PM tab, like in test_commands

- Performance is worse in NE1 PyOpenGL than in the PyOpenGL I have on the iMac G5
  (the same thing is true for testmode)

- refers to a missing image file on my desktop

(out of date below this)

test_animation_mode bugs as of 060219 night:
- loop stops; should be checkbox
- arrow keys are not camera relative; they're player-rel but player never turns; really they're world-rel (which is wrong)
- camera never tries to swing behind player
- camera dynamics are not very good (should get there faster, stop sooner, maybe have inertia)
- stuff is not in MT or mmp file
- stuff is not very interesting yet

and a couple more noted on g4:
- antialiasing
- a few more
"""

from widgets.prefs_widgets import Preferences_StateRef, Preferences_StateRef_double, ObjAttr_StateRef
from foundation.changes import Formula

## from test_animation_mode_PM import test_animation_mode_PM
from prototype.test_command_PMs import ExampleCommand1_PM
from PM.PM_GroupBox import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_PushButton import PM_PushButton
from PM.PM_CheckBox import PM_CheckBox

##from modes import *
##from modes import basicMode
from command_support.Command import Command
from command_support.GraphicsMode import GraphicsMode

from utilities.debug import print_compact_traceback, register_debug_menu_command
import time, math

from foundation.state_utils import copy_val

from utilities.constants import green, red, white, pink, black, brown, gray # other colors below
from math import pi
from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.drawers import drawbrick
from graphics.drawing.CS_draw_primitives import drawsphere
from graphics.drawing.CS_draw_primitives import drawcylinder
from OpenGL.GL import GL_LIGHTING, glDisable, glEnable
from geometry.VQT import cross, proj2sphere, V, norm, Q, vlen

from foundation.Utility import Node
import foundation.env as env

DX = V(1,0,0)
DY = V(0,1,0)
DZ = V(0,0,1)

from PyQt4.Qt import Qt, QCursor
# for Qt.Key_Left, etc

shiftButton = Qt.ShiftModifier
controlButton = Qt.ControlModifier

# from experiment, 070813, intel macbook pro
_key_control = 16777250
_key_command = 16777249


# for points of interest in this file, search for:
# - class test_animation_mode

###TODO:

# works in exprs/test.py: Image("/Users/bruce/Desktop/IMG_0560 clouds1.jpg")
# see test_commands.py...

# WARNING: if you have test_animation_mode.py OR test_animation_mode.pyc in cad/src, that one gets imported instead of one in ~/Nanorex/Modes.

# see also test_animation_mode-outtakes.py [lots of obs stuff moved there, 060219]

class Sketch3D_entity: pass
class Sketch3D_Sphere(Sketch3D_entity):
    # see class Sphere in exprs.Rect -- that ought to be enough info for a complete one!
    pass

##from exprs.staterefs import PrefsKey_StateRef
##
##def Preferences_StateRef_double( prefs_key, defaultValue = 0.0): #UNTESTED
##    ### TODO: cache this instance somehow (based on our args), as we IMPLEM the way to make it -- see test_commands for that
##    expr = PrefsKey_StateRef( prefs_key, defaultValue)
##    return find_or_make_expr_instance( expr, cache_key = ('PrefsState', prefs_key), assert_same = (defaultValue,) )
##
##### IMPLEM find_or_make_expr_instance, and make it fast when expr already exists (but do make it check assert_same, for now)



CANNON_HEIGHT_PREFS_KEY = "a9.2 devel/test_animation_mode/cannon height"
CANNON_HEIGHT_DEFAULT_VALUE = 7.5

def cannon_height(): # make a method?? why?
    return env.prefs.get( CANNON_HEIGHT_PREFS_KEY, CANNON_HEIGHT_DEFAULT_VALUE)

def set_cannon_height(val):
    env.prefs[CANNON_HEIGHT_PREFS_KEY] = val

CANNON_OSCILLATES_PREFS_KEY = "a9.2 devel/test_animation_mode/cannon oscillates"
CANNON_OSCILLATES_DEFAULT_VALUE = True

def cannon_oscillates():
    return env.prefs.get( CANNON_OSCILLATES_PREFS_KEY, CANNON_OSCILLATES_DEFAULT_VALUE)

SILLY_TEST = False ####


KLUGE_MANUAL_UPDATE = False # temporary
TESTING_KLUGES = False # temporary

class test_animation_mode_PM(ExampleCommand1_PM):
    """
    [does not use GBC; at least Done & Cancel should work]
    """
    title = "test_animation_mode PM"
    def _addGroupBoxes(self):
        """Add the groupboxes for this Property Manager."""
        self.pmGroupBox1 = \
            PM_GroupBox( self, 
                         title           =  "test_animation_mode globals",
                         )
        self._loadGroupBox1(self.pmGroupBox1)
        self.pmGroupBox2 = \
            PM_GroupBox( self, 
                         title           =  "commands",
                         )
        self._loadGroupBox2(self.pmGroupBox2)
        return

    _sMaxCannonHeight = 20
    
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets into groupbox 1 (passed as pmGroupBox)
        """
##        elementComboBoxItems  =  self._sElementSymbolList
##        self.elementComboBox  =  \
##            PM_ComboBox( pmGroupBox,
##                         label         =  "Elements :",
##                         choices       =  elementComboBoxItems,
##                         index         =  0,
##                         setAsDefault  =  True,
##                         spanWidth     =  False )

        ### change to a control for cannon height, dflt 7.5.
        # have to figure out what state that is, how to share it and track it.
        # use expr state to store it?? change class cannon into an expr?
        # but then when we adjust this does it affect all cannons or only a current one? either is possibly desirable...
        # and if both can work, it means cannon instances have formulas for their height,
        # some referring to default from class or maker...
        
        self.cannonHeightSpinbox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "cannon height:", #e try ending that label with " :" rather than ":", too
                              value         =  CANNON_HEIGHT_DEFAULT_VALUE,
                              # guess: default value or initial value (guess they can't be distinguished -- bug -- yes, doc confirms)
                              setAsDefault  =  True,
                              minimum       =  3,
                              maximum       =  self._sMaxCannonHeight,
                              singleStep    =  0.25,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )
        ### REVIEW: when we make the connection, where does the initial value come from if they differ?
        # best guess answer: PM_spec above specifies default value within PM (if any); existing state specifies current value.
        self.cannonHeightSpinbox.connectWithState(
            Preferences_StateRef_double( CANNON_HEIGHT_PREFS_KEY, CANNON_HEIGHT_DEFAULT_VALUE )
            )
        
        self.cannonWidthSpinbox  =  \
            PM_DoubleSpinBox( pmGroupBox,
                              label         =  "cannon width:",
                              value         =  2.0,
                              setAsDefault  =  True,
                              minimum       =  0.1,
                              maximum       =  15.0,
                              singleStep    =  0.1,
                              decimals      =  self._sCoordinateDecimals,
                              suffix        =  ' ' + self._sCoordinateUnits )
        self.cannonWidthSpinbox.connectWithState(
            ObjAttr_StateRef( self.commandrun, 'cannonWidth') # first real test of ObjAttr_StateRef.
                # test results: pm change -> tracked state change (mode attr), with redraw being triggered: works.
                # other direction (mode change to cannonWidth, in cmd_Start -> pm change) -- fails! ###BUG
                # note: the prefs state also was not tested in that direction! now it is, in fire command, and it works,
                # but this, also tested there, still fails. ... What could be different in these two cases?
            # Is there an API mismatch in the lval we get for this, with get_value not doing usage tracking?
            )
        
        self.cannonOscillatesCheckbox = \
            PM_CheckBox(pmGroupBox,
                        text       = 'oscillate cannon during loop' , 
                        ## value = CANNON_OSCILLATES_DEFAULT_VALUE ### BUG: not working as default value for restore defaults
                        # in fact, worse bug -- TypeError: __init__() got an unexpected keyword argument 'value'
                        )
        self.cannonOscillatesCheckbox.setDefaultValue(CANNON_OSCILLATES_DEFAULT_VALUE) #bruce extension to its API
        self.cannonOscillatesCheckbox.connectWithState( ### UNTESTED in direction mode->PM, tho i think code is tested in user prefs
            Preferences_StateRef( CANNON_OSCILLATES_PREFS_KEY, CANNON_OSCILLATES_DEFAULT_VALUE ) )
        return

    def _loadGroupBox2(self, pmGroupBox):
        self.startButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "Start",
                           spanWidth = False ) ###BUG: button spans PM width, in spite of this setting
        self.startButton.setAction( self.cmd_Start, cmdname = "Start")
        
        self.stopButton = \
            PM_PushButton( pmGroupBox,
                           label     = "",
                           text      = "Stop",
                           spanWidth = False )
        self.stopButton.setAction( self.cmd_Stop, cmdname = "Stop")

        #e also let in_loop be shown, or control whether they're disabled... note it can be changed by external effects
        # so we need to track it and control their disabled state, using a formula that gets checked sufficiently often...
        # connect the expr or formula for self.commandrun._in_loop to the update function...

        ## whenever_state_changes( ObjAttr_StateRef( self.commandrun, '_in_loop'), self.update_GroupBox2 ) ###IMPLEM 2 things

        ## or just do this?? call_often(update_GroupBox2) -- a few times per sec, and explicit calls on the buttons... seems worse...

        if not KLUGE_MANUAL_UPDATE:
            self._keepme = Formula( self.update_GroupBox2, self.update_GroupBox2 ) ### hmm.....
        
        return

    def update_GroupBox2(self, junk = None):
        in_loop = self.commandrun._in_loop ### or should this be passed in?? probably a better habit is if it's not...
            # note we can't track it from running this, since that attr is not directly usage tracked.
            # maybe we should change it so it is? then just call this once and say "call whenever what it used changes"...
            ##### TODO / REVIEW
        self.startButton.setEnabled( not in_loop) ### TODO: make something like setEnabledFormula for this... pass it a function??
        self.stopButton.setEnabled( in_loop)
        return

    def update_after_Draw(self):
        ### WARNINGS:
        # 1. this is called *during* Draw (not strictly after all drawing), so if this method
        # uses any state that tracks usage, that is treated as affecting the graphics area,
        # and changes to it trigger redraw, whether or not redraw is needed (except insofar
        # as it's "needed" in order to call this routine).
        # 2. given when it's called, this routine can do true updates (recomputes and displays)
        # or "Qt updates" (invals of Qt widgets), but must not do invals of NE1 tracked state.
        if KLUGE_MANUAL_UPDATE:
            self.update_GroupBox2()
        
    def cmd_Start(self):
        self.commandrun.cmd_Start()
        if KLUGE_MANUAL_UPDATE:
            self.update_GroupBox2()

    def cmd_Stop(self):
        self.commandrun.cmd_Stop()
        if KLUGE_MANUAL_UPDATE:
            self.update_GroupBox2()
            ###BUG: KLUGE_MANUAL_UPDATE doesn't cover stops inside test_animation_mode object itself! restart impossible then.
            # Workaround (untested): adjust cannon height or use arrow key -- should trigger redraw.
        
    def _addWhatsThisText(self):
        """
        What's This text for some of the widgets in the Property Manager
        """
        self.cannonHeightSpinbox.setWhatsThis("cannon height")
        return
    pass # test_animation_mode_PM


'''
File "/Nanorex/Working/cad/src/platform.py", line 92, in ascii
  return filter_key( self._qt_event.ascii() ) #k (does filter_key matter here?)
AttributeError: ascii
'''
#unfixed bug in arrow key bindings -- due to event.ascii ### BUG: not available in Qt4 [070811]

keynames = {}
for keyname in filter(lambda s: s.startswith('Key'), dir(Qt)):
    keynames[getattr(Qt, keyname)] = keyname

def keyname(key):#070812
    try:
        return keynames[keyname]
    except KeyError:
        return "<key %r>" % (key,)
    pass

pink1 = (0.8, 0.4, 0.4)
yellow = (0.8, 0.7, 0.0)
yellow2 = (0.8, 0.7, 0.2)
ygreen = (0.4, 0.85, 0.1)
blue = (0.0, 0.2, 0.9)
orange = (1.0, 0.35, 0.05)
orange = (1.0, 0.3, 0.00)
pumpkin = (0.9, 0.4, 0.0)
purple = (0.7, 0.0, 0.7) #060218 bugfix

def light(color, whiteness = 0.25):
    return mix(color, white, whiteness)

def mix(color1, color2, amount2):
    amount2 = V(amount2, amount2, amount2) #e optional?
    amount1 = V(1, 1, 1) - amount2
    return color1 * amount1 + color2 * amount2

lgreen = light(green)
lblue = light(blue)
lred = light(red)

colorkeys = dict(R = light(red),
                 G = light(green),
                 B = light(blue),
                 P = light(purple),
                 W = light(black, 0.8),
                 K = light(black),
                 Y = yellow,
                 O = orange,
            )

# and these, once we move them there:

####@@@@ assume Node inherits _S_State_Mixin
### that and other _S_ mixins can define writemmp, which classes can override if they want to use trad methods,
# calling utils in it to write info if desired (worry - don't Groups do that for them in some cases??),
# or they can not define it or tell it to call that mixin version, and then it just uses decls.
# also we can support binary mmp from them, as well as undo of course.
# undo policy decls can override what you'd guess from state decls. ###refile this

S_DATA = 'S_DATA'
# S_DATA, S_CHILD, S_CHILDREN, S_PARENT, S_PARENTS, S_REF, S_REFS, S_CACHE, S_JUNK, S_OWNED_BY, ...

class _S_Data_Mixin: pass #e stub #e refile in state_utils

class _S_ImmutableData_Mixin(_S_Data_Mixin):
    """
    For efficiency, inheritors of this mixin promise that all their declared data
    is immutable, so it can be shared by all copies, and so they themselves can be
    copied as themselves. (Most of them deepcopy the data passed into them, to protect
    themselves from callers who might pass shared data.)
    """
    def _s_deepcopy(self, copyfunc): ##k API
        #e maybe someday we'll inherit this from (say) _S_ImmutableData_Mixin
        return self
    def _s_copy_for_shallow_mod(self): #e likely to be renamed, maybe ...private_mod
        """
        Private method for main class -- copy self, sharing data,
        in anticipation that the copy will be privately modified
        and then returned as a new immutable data object.
        """
        assert 0, "nim" #e but should be easily done using _s_initargs, or perhaps the set of _s_attr decls
    pass

# see also comments about _s_initargs API, below

# ==

def do_what_MainWindowUI_should_do(win):
    pass

##_superclass = selectAtomsMode # this works too [050528]
##_superclass = basicMode
_superclass = Command
# see also _superclass_GM

# new stuff 060218

# local copy for debugging & customization, original by josh in VQT.py
class myTrackball:
    """
    A trackball object. The current transformation matrix
    can be retrieved using the "matrix" attribute.
    """
    def __init__(self, wide, high):
        """
        Create a Trackball object.
        "size" is the radius of the inner trackball
        sphere.
        """
        self.w2=wide/2.0
        self.h2=high/2.0
        self.scale = 1.1 / min(wide/2.0, high/2.0)
        self.quat = Q(1,0,0,0)
        self.oldmouse = None

    def rescale(self, wide, high):
        self.w2=wide/2.0
        self.h2=high/2.0
        self.scale = 1.1 / min(wide/2.0, high/2.0)

    def start(self, px, py):
        self.oldmouse=proj2sphere((px-self.w2)*self.scale,
                                  (self.h2-py)*self.scale)

    def update(self, px, py, uq=None):
        newmouse = proj2sphere((px-self.w2)*self.scale,
                               (self.h2-py)*self.scale)
        if self.oldmouse and not uq:
            quat = Q(self.oldmouse, newmouse)
        elif self.oldmouse and uq:
            quat =  uq + Q(self.oldmouse, newmouse) - uq
        else:
            quat = Q(1,0,0,0)
        self.oldmouse = newmouse
        ## print "trackball quat would rotate V(0,0,1) to",quat.rot(V(0,0,1))
        showquat("trackball quat", quat, where = V(-3,0,0))
        
        ## drawline(white, self.origin, endpoint)
        return quat
    pass

def hacktrack(glpane):
    print "hacking trackball, permanently"
    glpane.trackball = myTrackball(10, 10)
    glpane.trackball.rescale(glpane.width, glpane.height)

quats_to_show = {}

def showquat(label, quat, where = V(0,0,0)):
    quats_to_show[label] = (Q(quat), + where)

def draw_debug_quats(glpane):
    for quat, where in quats_to_show.values():
        drawquat(glpane, quat, where)

def drawquat(glpane, quat, where):
    # not yet good enough: need to correct for screensize and scale, put it in fixed place/size on screen.
    # more importantly, what I *need* to show is accumulation of several small quats... not sure how.
    # or maybe, the *history* of this one? as it is, latest value might be "0" and so i don't see the transient one.
    oldquat = glpane.quat
    newquat = oldquat + quat
    def trans(screenpos):
        return glpane.pov + oldquat.unrot(screenpos)
    # show how the x,y,z axes would be moved.
    p0 = trans(where)
    for vec, color in [ (V(1,0,0), red), (V(0,1,0), green), (V(0,0,1), blue) ]:
        vecnow = oldquat.rot(vec)
        vecthen = newquat.rot(vec)
        p1 = trans(where + vecnow)
        p2 = trans(where + vecthen)
        drawline(color, p0, p1)
        drawline(color, p1, p2)
    return

# i want a trackball which is constrained to keep the Y axis in the up/out plane.
# this cmd works, but interface is a pain... at least needs button, but really needs to be a trackball option for this mode.
# well, it can be, since we intercept the trackballing events!
def novertigo_cmd(widget):
    glpane = widget
    novertigo(glpane)
    return

def novertigo(glpane):
    """
    Rotate the view so that the Y axis V(0,1,0) points up, plus maybe a bit in or out.
    """
    xjunk, y, z = Y = glpane.quat.rot(V(0,1,0))
    # we'll use a projection of this into the y,z plane, but fix it to be within our range; note, y,z could be (0,0)
    k = 2 # determines max angle from vertical
    ## print "Y =",Y
    ## printvec("Y",Y)
    if y < k * abs(z):
        y = k * abs(z)
    if y == 0 and z == 0:
        y, z = 1, 0
    proj = norm(V(0, y, z))
    ##printvec("proj",proj)
    ## print proj
    # proj is where we want Y to be
    incrquat = Q(Y, proj)
    showquat("incrquat",incrquat, V(3,0,0))
    glpane.quat += incrquat
##    q2 = glpane.quat + Q(Y, proj)
##    glpane.snapToView(q2, glpane.scale, glpane.pov, glpane.zoomFactor)
    return

def printvec(label, vec):
    print label, "(%03f, %03f, %03f)" % (vec[0], vec[1], vec[2]) # why does it print with 6 digits? Y (-0.003402, 0.696759, 0.717297)

register_debug_menu_command("novertigo", novertigo_cmd) # will only work in glpane debug menu


def hack_standard_repaint_0(glpane, prefunc):
    """
    replace glpane.standard_repaint_0 with one which calls prefunc
    and then calls the class version of standard_repaint_0
    """
    def imposter(glpane = glpane, prefunc = prefunc):
        prefunc()
        glpane.__class__.standard_repaint_0(glpane)
        return
    glpane.standard_repaint_0 = imposter
    return

# ==

class CyberTextNode(Node):
    """
    Hold some text which can be edited and displayed, and a few properties to control when/where/how to display it.
    Also try to let it exist in cyberspace, i.e. when it's changed, store it there, and when we're reshown, reload it from there.
    For initial test, cyberspace means a file whose basename we contain and whose dirname is hardcoded.
    Or a prefs db entry, or something like that.
    - Hmm... how does user make one? Mt cmenu.
    - How does user edit text? Ideally, select node, then text is shown in editable text field.
    This field is only there when something has text to edit (not nec. us).
    Optional cool feature: if multiple nodes selected, show all of them (editably) in that text field (longer, scrollable).
    - Where do we put that text field? Better make one... no good place at the moment.
    Do we have *any* code to grab for that?
    - history widget
    - debug text edit
    - glpane text, with our own key bindings for editing -- sounds harder, not sure it really is (need focus to follow selected node)
    Related nE-1 desired features:
    - edit props for any node, in a pane added below it in MT when it's selected -- this is almost identical to what we want here
    - text-containing node, for notes, or display in 3dview -- also almost identical
    - the cyberspace part is the only weird part
    So, what to do?
    - have a text widget at MT bottom, hide/show on demand
    - be able to tie it to edit any textual lvalue; some owner takes it over by providing that lval's API, later releases it,
      and new owners can also kick out old ones
    - this node, when selected, takes it over unless it's locked, or always if some cmenu command is used or if it's unlocked
    - this locking is controlled by a cmenu on the text widget, or a checkbox, or equivalent
    
    """

# see Macintosh HD:Nanorex:code, work notes:060401 code snippets
# QTextEdit(win.mt)

def find_or_make_textpane(win):
    try:
        return win.__textpane
    except:
        pass
    try:
        vs = win.vsplitter2
    except:
        return None
    # make it only once
    te = QTextEdit(vs) #e use subclass with key bindings; maybe put it in a 1-pixel frame
    vs.setSizes([vs.height() - 100, 100]) #k assumes our new widget is only the 2nd shown thing of two things (1st being win.mt)
    te.show()
    win.__textpane = te
    return te

'''
set mtree_in_a_vsplitter in MWsemantics (edit it before startup) (debug_pref?)
from __main__ import foo as win
import test_animation_mode
print test_animation_mode.find_or_make_textpane(win)
'''

# ==

class DebugNode(Node):
    def __init__(self, stuff, name = None):
        assy = env.mainwindow().assy #k wrongheaded??
        Node.__init__(self, assy, name)
        self.stuff = stuff # exprs for what to draw (list of objects)
    _s_attr_stuff = S_DATA
    def draw(self, glpane, dispdef):
        if self.picked: # only draw when picked! (good?)
            draw_stuff(self.stuff, glpane)
    def writemmp(self, mapping):
        """
        Write this Node to an mmp file, as controlled by mapping,
        which should be an instance of writemmp_mapping.
        """
        line = "# nim: mmp record for %r" % self.__class__.__name__
        mapping.write(line + '\n')
        # no warning; this happens all the time as we make undo checkpoints
        return
    def __CM_upgrade_my_code(self): # experiment
        """
        replace self with an updated version using the latest code, for self *and* self's data!
        """
        name = self.__class__.__name__
        print "name is",name # "DebugNode"
        print self.__class__.__module__ # "test_animation_mode"
        #e rest is nim; like copy_val but treats instances differently, maps them through an upgrader
    pass

def draw_stuff(stuff, glpane):
    if type(stuff) in (type(()), type([])):
        for thing in stuff:
            draw_stuff(thing, glpane)
    else:
        try:
            stuff.draw(glpane)
        except:
            print_compact_traceback("draw_stuff skipping %r: " % (stuff,))
    return

# ==

class DrawableStuff(_S_Data_Mixin):
    def __init__(self, *args, **kws):
        self.args = copy_val(args)
        self.kws = copy_val(kws)
        self.process_args()
    _s_attr_args = S_DATA
    _s_attr_kws = S_DATA
    def _s_initargs(self):
        #####k API -- in this case we're providing full info,
        # but didn't the _um_ version get to leave out some attrs, and instead handle them with diffs?? ###@@@
        # we want to keep it simple, but we know there are some objects that require that approach...
        # maybe let them define a *different* method and leave this one undefined?? or have a different retval format for that case??
        return self.args, self.kws
    def process_args(self):
        # callers can add arg asserts if they want; we guarantee __init__ will call this, so it can store args in attrs,
        # which _S_Data_Mixin will effectively treat as S_CACHE by default
        pass
    pass

class makeline(DrawableStuff):
    def process_args(self):
        self.color, self.pos1, self.pos2 = self.args[0:3]
    def draw(self, glpane):
        drawline(self.color, self.pos1, self.pos2)
    pass

class makedot(DrawableStuff):
    def process_args(self):
        self.color, self.pos = self.args[0:2]
    def draw(self, glpane):
        #e stub, need to choose radius based on pixel size, and make a circle not sphere
        detailLevel = 2
        radius = 0.1 ### total stub and guess
        drawsphere(self.color, self.pos, radius, detailLevel)
        pass #####@@@@@
    pass

class makevecs(DrawableStuff):
    def process_args(self):
        self.origin, self.vecs, self.colors = self.args[0:3]
        self.vecs_colors = zip(self.vecs, self.colors)
    def draw(self, glpane):
        for vec, color in self.vecs_colors:
            drawline(color, self.origin, self.origin + vec)
        return
    pass

# ==

class attrholder:
    def __init__(self, **options):
        self.__dict__.update(options)
    pass

DEFAULT_DIRECTIONS = attrholder(away = - DZ, towards = DZ, up = DY, down = - DY, left = - DX, right = DX)
    # maybe attrnames should differ?

def interpret_arrow_key( key, space = None): ###TODO: pass space if nec.
    """
    return None for a non-3d-arrow-key, or a direction vector for one, taken from space or DEFAULT_DIRECTIONS
    """
    if not space:
        space = DEFAULT_DIRECTIONS
    if key == Qt.Key_Up: # 4115:# up means in = lineofsight = away from user
        return space.away
    elif key == Qt.Key_Down: # 4117: # down means out = towards user
        return space.towards
    elif key == Qt.Key_Left: # 4114: # left, right mean themselves
        return space.left
    elif key == Qt.Key_Right: # 4116:
        return space.right
    elif key == Qt.Key_PageUp: # 4118: # pageup means up
        return space.up
    elif key == Qt.Key_PageDown: # 4119: # pagedown means down
        return space.down
    return None

# ==

class shelvable_graphic:
    # some default state attrs (kluge, should be in a graphical subclass)
    pos = V(0,0,0)
    dir = V(1,0,0)
    size = V(1,1,1)
    color = pink1
    dead = False # set self.dead to True in instances, to cause destroy() and culling on next redraw
        # ok to set it during a command (then it prevents redraw of self) or during redraw (culls upon return); see guy.draw for implem
    def __init__(self, space, dict1 = {}):
        self.__dict__.update(dict1) # do first so we don't overwrite the following ones
        self.space = space # note: this is the mode, a test_animation_mode instance [assume it is a Command, not a GraphicsMode]
        self.glpane = space.glpane
        self.stuff = {} # kids, i guess [need a way of removing old ones]
        self.creation_time = space.simtime
    def changed(self):#050116 [long after shelvable_graphic stub created; note that it never worked yet]
        global_changed[self] = self ###k does self count as a legit key, or not?
    def save(self, storage, key):
        storage[key] = self.state()
    def state(self):
        res = {}
        for k in self.__dict__.keys(): # not dir(self), that includes class methods...
            if not (k.startswith('_') or k in ['space','stuff']): ###@@@ see also "snaps.py" which I started writing...
                #k don't exclude stuff... need pickle methods to turn objs into refs to them or their snapshot then.
                res[k] = self.__dict__[k]
        return res
    def contents(self):
        """
        other objs whose state is sometimes considered part of ours, but not in self.state()
        """
        return self.stuff.values()
    def load(self, storage, key):
        """
        change our state to match what's in the storage
        """
        stored = storage[key]
        self.__dict__.update(stored) # dangerous!
    def destroy(self):
        ## print "destroying", self # works
        pass
    def move(self, vec):
        self.pos = self.pos + vec
    pass # pickleable, mainly

##class brick(shelvable_graphic): # this is not right yet
##    "a brick, in standard orientation, std size, brighter if keyfocus is on it; has specified shelf-key for state"
##    def draw(self, pos = V(0,0,0), dir = V(1,0,0), size = V(1,1,1), color = pink1):
##        # drawbrick(pink1, self.origin + V(2.5, 0, 0), self.right, 2.0, 4.0, 6.0) - uses current GL context (that's ok)
##        drawbrick(color, pos, dir, size[0], size[1], size[2])
##    pass

class wireguy(shelvable_graphic): # used for square tiles in the "racetrack"
    moves = False # to change this, let it be in the dict arg when we create this
    def draw(self, glpane):
        ## drawwirecube(self.color, self.pos, 1.02 / 2.0)# no place for self.dir; last number is not what i hoped...
        pos = self.pos
        if self.moves:
            pos = pos + DY * (self.space.simtime - self.creation_time) # 070813  [071010 glpane .mode -> self.space == a Command]
        drawbrick( self.color, pos - V(0, 0.6, 0), self.dir, 1.0, 1.0, 0.05) ## 0.98, 0.98, 0.05)
    pass

TOOFAR = 100 # some things disappear when this far away -- to test this, use 6 so things disappear within sight -- works

CANNONBALL_SPEED = 21
BIRD_SPEED = 11 # not yet used

class cannonball(shelvable_graphic):
    motion = V(0,0,0) # caller may want to use CANNONBALL_SPEED when setting this
    
    position = None
    velocity = None
    last_update_time = None
    acceleration = -10 * DY * 3
    def update_incr(self):
        if self.last_update_time is None:
            self.last_update_time = self.creation_time
        if self.position is None:
            self.position = V(0,0,0) + self.pos ###k
        if self.velocity is None:
            self.velocity = V(0,0,0) + self.motion ###k
        now = self.space.simtime
        delta_time = now - self.last_update_time
        # if too large, do the following in several steps, or use a quadratic formula
        self.position += (delta_time * self.velocity)
        self.velocity += (delta_time * self.acceleration)
        self.last_update_time = now
        ## print "dt = %r, so set position = %r, velocity %r" % (delta_time, self.position, self.velocity)
        return
    def draw(self, glpane):
        self.update_incr() # now self.position should be correct; self.pos is starting position
##        age = (self.space.simtime - self.creation_time)
##        displacement = self.motion * age
        displacement = self.position - self.pos
        if vlen(displacement) > TOOFAR:
            self.dead = True # causes delayed destroy/cull
        else:
            pos = self.position
            drawsphere( blue, pos, 1, 2)
        return
    pass

class cannon(shelvable_graphic): # one of these is self.cannon in test_animation_mode; created with mode = that mode

    direction = norm(DY - DX) #070821
    
    def basepos(self):
        mode = self.space
        ## pos = mode.origin
        pos = self.pos # changed by .move()
        return pos + V(mode.brickpos, 0, 0) - DY * 9
    
    def draw(self): # needs glpane arg if ever occurs in object list
        mode = self.space # note: uses mode.brickpos for position, updated separately -- should bring that in here

        ## drawwirecube(purple, mode.origin, 5.0)
        ## drawwirecube(gray, mode.origin, 6.5)
        ## if 0: drawbrick(yellow, mode.origin, mode.right, 2.0, 4.0, 6.0)

        basepos = self.basepos()
        drawbrick(pink1, basepos + 1.0 * self.direction, mode.right, 2.0, 2.0, 1.0) # wrong orientation
        detailLevel = 2
        drawsphere(red, basepos + 2.5 * self.direction, 2, detailLevel) ###@@@
        radius = mode.cannonWidth / 2.0 # note: this is usage-tracked!
        drawcylinder(lgreen,
                     basepos + 2.5 * self.direction,
                     basepos + cannon_height() * self.direction,
                     radius, True)
        # with red, its lighting is pretty poor; pink1 looks nice

    def fire(self): # bound to command key
        toppos = self.basepos() + cannon_height() * self.direction
            # note: cannon_height() is usage tracked, but needn't be in this context, but that needs to be ok without any reason
            # to mention it here, since the same issue affects all usage tracked variables used in commands.
        new = cannonball(self.space, dict(pos = toppos, motion = self.direction * CANNONBALL_SPEED))
        self.space.appendnew(new)
        if SILLY_TEST:
            self.grow_cannon()
        return
    
    def grow_cannon(self):
        set_cannon_height(cannon_height()+1) # test of whether pm gets updated -- it does!
        self.space.cannonWidth += 0.5 # ditto - in this case it doesn't! bug [fixed now]
        
    pass # class cannon

class guy(shelvable_graphic):
    """
    a combo of object list and a specific thing ###FIX
    """
    def draw(self, glpane):
        # this main guy is the one that needs to be transparent, so you can see what's he's making under him!
        # and, the thing he might make also needs to be transparent but there. and, a key should put it down for you... and unput it.
        # and, remove any other stuff in same pos!
        pos = self.pos ## + self.space.now # 070813 experiment -- works [since then, glpane .mode -> self.space, but i don't want to move this guy (the 3d cursor)
        drawbrick(self.color, pos, self.dir, 1, 1, 1) ## 2.0, 4.0, 6.0) # uses current GL context
        glDisable(GL_LIGHTING)
        drawbrick(gray, pos * V(1,0,1) - V(0, 6, 0), self.dir, 1, 1, 0.02) # brick dims for this dir are x, inout, z
        glEnable(GL_LIGHTING)
        drawline(light(black, 0.2), pos, pos * V(1,0,1) - V(0, 6, 0))
        #e and a line between them
        deads = []
        for thing in self.stuff.itervalues():
            #e move to superclass? ... well, they need to notice our shadow hitting them! be transparent? fog?
            # i bet transparent is not super hard to do... note that for cubes (or any convex solids)
            # it's easy to know back to front order...
            if thing.dead:
                # (thing.dead was set during a command -- don't draw it)
                deads.append(thing)
            else:
                thing.draw(glpane) # arg?
                if thing.dead: # (thing.dead was set during draw method itself, which may or may not have returned early)
                    deads.append(thing)
        for thing in deads:
            thing.destroy()
            del self.stuff[id(thing)]
        return
    def keyPressEvent(self, event):
        key = event.key()
        ## asc = event.ascii()  ### BUG: not available in Qt4 [070811]
        ## but = event.stateAfter()  ### BUG: not available in Qt4 [070811]
        ## but = event.state()  ### BUG: not available in Qt4 [070811]
        but = -1
        
        self.shift = but & shiftButton # not set correctly at the moment; used to control whether to makeonehere
        self.control = but & controlButton # not yet used
        try:
            chrkey = chr(key)
        except:
            chrkey = None
        ##print key, asc, but, chrkey
        if key == Qt.Key_Return: # 4100: # Return
            key = ord('\n')
            ## asc = key
##        if key == ord('\n') or 32 <= key <= 126:
##            # use asc, so 'a' vs 'A' is correct
##            self.text = str_insert(self.text, self.curpos, chr(asc))
##            self.curpos += 1
##            ## didn't work: return 1 ###@@@ incrkluge test; not correct btw!
##        elif key == 'rdel': # names like that are stubs
##            self.text = self.text[:self.curpos] + self.text[self.curpos+1:]
##        elif key in [4099, 'del']: # Delete on Mac; unable to bind the "del" key!
##            self.text = self.text[:self.curpos-1] + self.text[self.curpos:]
##            self.curpos -= 1
        ## print "data:", asc, key, chrkey, self.colorkeys # asc = 114, key = 82, chr(key) = 'R'

        arrowdir = interpret_arrow_key(key)
        
        if chrkey in colorkeys:
            self.color = colorkeys[chrkey]
        ### 060402 new arrow keys [not done., disabled]
##        elif key == 4114:
##            # left
##            self.space.o.left
        # end of 060402 new arrow keys
        #e also arrow keys... should these be model relative as here?
        # [this is in class guy, but would make more sense in class test_animation_mode]
        elif arrowdir is not None:
            if not self.space._in_loop:
                self.move( arrowdir)
            else:
                self.space.cannon.move( arrowdir)
        elif chrkey == ',': # '<'
            self.space.rotleft(0.05) # far away stuff goes left, that much of 360deg ... around what center?
        elif chrkey == '.': # '>'
            self.space.rotleft(-0.05) ###@@@ subr is wrong at the moment
        else:
            print "test_animation_mode received key:", keyname(event.key()) ## "(%r)" % event.key()
        self.save()
    def save(self):
        pass # save the state! just store our dict at a key... but turn values from objs to refs... ask the objs for those. ###@@@
    def move(self, delta):
        """
        overrides superclass move; compatible but does more
        """
        if self.shift:
            self.makeonehere() # should be in the space, not the guy itself! ###@@@
        self.lastmotion = delta
        # this is superclass.move: ###FIX, call it
        pos = self.pos = self.pos + delta
        ##print "new pos and proj", pos, pos * V(1,0,1) - V(0,6,0)
        # caller does redraw, no need to tell it to here
    def makeonehere(self):
        d1 = dict(self.__dict__)
        if self.space._in_loop: ## FIX: could simplify since self.space == mode [did it now, glpane .mode -> space]
            ## d1['moves'] = True # sets new.moves = True
            d1['motion'] = DY * 3 # new.motion
            new = cannonball(self.space, d1)
        else:
            new = wireguy(self.space, d1) # note: it inherits copies of all our attributes! such as pos, color.
        #e remove any existing stuff in the same place! let's store them in a dict by place, not this list... ###@@@
        self.space.appendnew(new)
        ## self.stuff.append(new)
    pass # end of class guy

# ==

'editToolbar', 'fileToolbar', 'helpToolbar',
'modifyToolbar', 'molecularDispToolbar',

annoyers = [##'editToolbar', 'fileToolbar', 'helpToolbar', 'modifyToolbar',
            ##'molecularDispToolbar', 'selectToolbar', 'simToolbar',
            ## 'toolsToolbar',
            ##'viewToolbar',
    ] # all have been renamed in Qt4


# code copied from test_commands.py:
# these imports are not needed in a minimal example like ExampleCommand2;
# to make that clear, we put them down here instead of at the top of the file
from graphics.drawing.CS_draw_primitives import drawline
from utilities.constants import red, green
##from exprs.ExprsConstants import PIXELS
from exprs.images import Image
##from exprs.Overlay import Overlay
from exprs.instance_helpers import get_glpane_InstanceHolder
from exprs.Rect import Rect # needed for Image size option and/or for testing
from exprs.Boxed import Boxed
from exprs.draggable import DraggablyBoxed
from exprs.instance_helpers import InstanceMacro
from exprs.attr_decl_macros import State

from exprs.TextRect import TextRect#k
class TextState(InstanceMacro):#e rename?
    text = State(str, "initial text", doc = "text")#k
    _value = TextRect(text) #k value #e need size?s
    pass

# ==============================================================================

## _superclass_GM = _superclass.GraphicsMode_class # wrong, this is None now
_superclass_GM = GraphicsMode
print "_superclass = %r, _superclass_GM = %r" % (_superclass, _superclass_GM)####

class test_animation_mode_GM( _superclass_GM ):
    
    def leftDown(self, event):
        pass

    def leftDrag(self, event):
        pass
    
    def leftUp(self, event):
        pass

    def middleDrag(self, event):
        glpane = self.glpane
##        q1 = Q(glpane.quat)
        _superclass_GM.middleDrag(self, event)
        self.command.modelstate += 1
##        q2 = Q(glpane.quat)
        novertigo(glpane)
##        q3 = Q(glpane.quat)
##        print "nv", q1, q2, q3
        return

    def pre_repaint(self):
        """
        This is called early enough in paintGL to have a chance
        (unlike Draw) to update the point of view.
        """
        if self.isCurrentGraphicsMode() and self.command._in_loop:
            ## self.glpane.quat += Q(V(0,0,1), norm(V(0, 0.01, 0.99)))
            ## now = time.time() - self._loop_start_time
            now = self.command.simtime
            self.now = now # not used??
            if cannon_oscillates():
                self.command.brickpos = 2.5 + 0.7 * math.sin(now * 2 * pi)
            else:
                self.command.brickpos = 2.5
            self.set_cov()
        return

    def set_cov(self):#060218... doesn't yet work very well. need to check if 6*self.glpane.scale is correct...
            # not that i know what would fail if not.
        return ######
        try:
            space = self.command # since this method is in the GraphicsMode
            glpane = self.glpane
            cov = - glpane.pov # center of view, ie what camera is looking at
            guy_offset = space.guy.pos - cov
            # camera wants to rotate, but can't do this super-quickly, and it might have inertia, not sure...
            # kluge, test: set cov to some fraction of the distance
            newcov = + cov
            newcov += guy_offset * 0.2
            # now figure out new pos of camera (maintains distance), then new angle... what is old pos of camera?
            eyeball = (glpane.quat).unrot(V(0, 0, 6 * glpane.scale)) - glpane.pov # code copied from selectMode; the 6 might be wrong
                # took out - from -glpane.quat since it looks wrong... this drastically improved it, still not perfect.
                # but it turned out that was wrong! There was some other bug (what was it? I forget).
                # And th - was needed. I prefer to put in unrot instead.
            _debug_oldeye = + eyeball
            desireddist = 6*glpane.scale
            nowdist = vlen(eyeball - newcov) #k not used? should it be?
            # now move it partway towards guy... what about elevation? should we track its shadow instead?
            # ignore for now and see what happens? or just use fixed ratio?
            desired_elev = 2 * glpane.scale ## guess
            desired_h_dist = math.sqrt( desireddist * desireddist - desired_elev * desired_elev)
##            print "desireddist = %s, desired_elev = %s, desired_h_dist = %s" % (desireddist, desired_elev, desired_h_dist)
            # figure out coords for use in setting camera position from this
            dx, dy, dz = eyeball - newcov
            # x, z is a ratio to maintain
            eyedir = norm(V(dx, 0, dz)) * desired_h_dist # dir on ground only
            eyedir += desired_elev * V(0,1,0)
            # eyedir is ideal position rel to newcov, but eyeball should only move partway towards it... perfect this later (inertia?)
            eyeball += ((eyedir + newcov) - eyeball) * 0.2
            # now we know where eyeball is... it should look towards newcov... so real cov is partly there
            realcov = eyeball + norm(newcov - eyeball) * desireddist
##            print "desired-eyeball to desired-cov dist is", vlen(eyeball - realcov)
            # the quat is one which would look from eyeball to realcov, but keeping y in that vertical plane.
            # hmm... wish I could just use gluLookAt.
            #   Q(x, y, z) where x, y, and z are three orthonormal vectors
            #   is the quaternion that rotates the standard axes into that reference frame.
            # Standard axes: eyeball from cov is positive z...
            wantz = norm(eyeball - realcov)
            Y = V(0,1,0)
            wantx = norm(cross(Y, wantz))
            wanty = cross(wantz, wantx)
##            ## print "w", wantx, wanty, wantz
            realquat = - Q(wantx, wanty, wantz) # added '-' since should be correct...
##            print "X_AXIS =? realquat.rot(wantx)", realquat.rot(wantx)
##            print "Y_AXIS =? realquat.rot(wanty)", realquat.rot(wanty)
##            print "Z_AXIS =? realquat.rot(wantz)", realquat.rot(wantz)
            glpane.pov = - realcov
            glpane.quat = realquat ###@@@ see if - helps... makes elev 0 and makes it unstable eventually... but should be correct!
            #e store attrs for debug drawing
    # DON'T ZAP THIS, it might be very useful for improving the camera follower algorithm
##            # want to show (maybe elsewhere in diff coords): old eyeball, old guy, new guy, new place to lookat,
##            # new eyeball, actual cov... and some lines between them, blobs at them, etc; and store this for later back/fwd browsing
##            # (hmm, use ericm's little movie format? or smth similar, with back/fwd buttons for replay, or node per frame in MT,
##            #  visible when selected)
##            oldeye = _debug_oldeye
##            oldcov = cov
##            newguy = + space.guy.pos
##            guylookat = + newcov
##            debug_stuff = [makeline(white, oldeye, oldcov), makeline(gray, oldcov, newguy), makedot(gray, guylookat),
##                           makeline(orange, oldeye, eyeball), makedot(green, eyeball),
##                           makedot(blue, realcov),
##                           makevecs(realcov, [wantx, wanty, wantz], [red, green, blue]),
##                                ]
##            dn = DebugNode(debug_stuff, name = "debug%d" % env.redraw_counter)
##            space.placenode(dn) #e maybe ought to put them in a group, one per loop? not sure, might be more inconvenient than useful.
##            print "tried to set eyeball to be at", eyeball, "and cov at", realcov
##            apparenteyeball = (glpane.quat).unrot(V(0, 0, 6*glpane.scale)) - glpane.pov ### will unrot fix it? yes!
##            print "recomputed eyeball from formula is", apparenteyeball, "and also", realcov + glpane.out * desireddist
##            # 2nd formula says we got it right. first formula must be wrong (also in earlier use above).
##            # if we assume that glpane.eyeball() is nonsense (too early for gluUnProject??)
##            # then the data makes sense. Could the selectMode formula source have been right all along? #####@@@@@
        except:
            print_compact_traceback("math error: ")
            space.cmd_Stop()
            pass
        return

    def Draw(self):
##        ##print "test_animation_mode.Draw"

        glpane = self.glpane

##        # can we use smth lke mousepoints to print model coords of eyeball?
##        print "glpane says eyeball is now at", glpane.eyeball(), "and cov at", - glpane.pov, " ." ####@@@@
        ## basicMode.Draw(self)
        _superclass_GM.Draw(self)
        origin = self.command.origin
        endpoint = origin + self.command.right * 10.0
        drawline(white, origin, endpoint)

        self.command.cannon.draw()

        glpane.assy.draw(glpane)
        ## thing.draw(glpane, endpoint)
        self.command.guy.draw(glpane)
        ## draw_debug_quats(glpane)
        self.command._expr_instance.draw() #070813 - works, but resizer highlight doesn't work, didn't investigate why not ###BUG

        if self.command.propMgr:
            self.command.propMgr.update_after_Draw()
        return

    def keyPressEvent(self, event):
        ## ascii = event.ascii() ### BUG: not available in Qt4 [070811]
        key = event.key()
##        if ascii == ' ': # doesn't work
##            self.cmd_Stop()
        if key == 32 or key == ord('S'): # note: 32 doesn't work, gets caught at some earlier stage and makes an orientation window
                ### note: ord('s') does not work... 83 is presumably the ascii code of 'S', not 's'
            self.command.cmd_Stop()
        ## if not self.what_has_our_focus: # can this be a single floor tile? or only the entire floor?
            # note that the focus is like the "character" in a game...camera should follow it through 3d space...
            # and it might have a dir, not just be an object... it might be a guy *near* the object.
            # so this var might be "what's near our guy" or "what's under our guy".
            # yeah, i'm sure it should be a guy (who might be over empty space, might move continuously).
            # otoh, this guy might have a finger poiinting at a thing, which is what gets our key events!
            # so we feed key to him, he feeds it out his feet or finger.
            # why not do "depmode" but with a guy walking around the mol? ... but how to draw the guy? not easy!
            # the keyfocus concept is that it's invisible, or a highlight state of the thing near it! or a simple line...
        elif key == _key_command or key == ord('F'): # F repeats, command doesn't
            self.command.cannon.fire()
        elif key == ord('G'):
            self.command.cannon.grow_cannon() # useful for testing PM update
        else:
            self.command.guy.keyPressEvent(event) ## wrong anyway : or thing.keyPressEvent(event)
            
        ## self.incrkluge = thing.keyPressEvent(event)
        self.redraw()
    
    def keyReleaseEvent(self, event):
        pass ## thing.keyReleaseEvent(event)

    def redraw(self):
        #e could be optimized if nothing but typing, and no DEL, occurred!
        self.command.modelstate += 1
        ##bruce 050528 zapped this: self.glpane.paintGL() - do it this newer way now:
        self.glpane.gl_update()

    def update_cursor_for_no_MB(self):
        """
        [part of GraphicsMode subclass API]
        """
        self.o.setCursor(QCursor(Qt.ArrowCursor))

    pass # end of class test_animation_mode_GM

# ========

from exprs.ExprsMeta import ExprsMeta
from exprs.StatePlace import StatePlace
from exprs.instance_helpers import IorE_guest_mixin

class test_animation_mode(_superclass, IorE_guest_mixin): # list of supers might need object if it doesn't have IorE_guest_mixin; see also __init__
    __metaclass__ = ExprsMeta # this seems to cause no harm.
        # Will it let us define State in here (if we generalize the implem)??
        # probably not just yet, but we'll try it and see what errors we get.
    transient_state = StatePlace('transient') # see if this makes State work... it's not enough --
        # it is a formula with a compute method, and Exprs.py:273 asserts self._e_is_instance before
        # proceeding with that. I predict self would need a lot of IorE to work here...
    _e_is_instance = True # I predict this just gets to another exception... if it's even correct --
        # it might be wrong to say it in the class itself!!! anyway it didn't complain about that
        # but i was right, it then asked for _i_env_ipath_for_formula_at_index...
        # so there is a set of things we need, to be able to support formulae like that one for transient_state,
        # and i bet IorE is mostly that set of things, but also with support for things we don't need or even want,
        # like child instances, call == customize, etc.
        #
        # So there are different ways to go: ### DECIDE:
        # - revise State to work without transient_state [probably desirable in the long run, anyway]
        # - make a more standalone way of defining transient_state
        # - split IorE into the part we want here and the rest (the part we want here might be a post-mixin)
        # - revise IorE to be safe to inherit here (as a post-mixin I guess), ie make it ask us what __call__ should do.
        #
        # Let's see what happens if we just inherit IorE. maybe it already works due to _e_is_instance,
        # and if not, maybe I can override __call__ or remove __call__ alone from what I inherit.

    # class constants needed by mode API
    backgroundColor = 103/256.0, 124/256.0, 53/256.0
    commandName = 'TEST_ANIMATION'
    featurename = "Prototype: Example Animation Mode"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING

    # other class constants
    PM_class = test_animation_mode_PM

    GraphicsMode_class = test_animation_mode_GM

    # tracked state (specially defined instance variables)
    # (none yet, but we want to put _in_loop here, at least)
    # can we say: _in_loop = State(boolean, False) ?
    # Or would that overload State too much, or use a too-generic word? ###REVIEW

    ## _in_loop = False ###TODO: unset this when we're suspended due to some temp commands -- but not all??
    _in_loop = State(bool, False)
    cannonWidth = State(float, 2.0) ## add , _e_debug = True to see debug prints about some accesses to this state
    
    # initial values of instance variables
    now = 0.0 #070813 [still used? maybe simtime has replaced it?]
    brickpos = 2.5
    # in _superclass anyMode: propMgr = None

    _please_exit_loop = False
    _loop_start_time = 0
    simtime = 0.0 # this is a constant between loops, and grows with real time during loops. only changed in cmd_Start. never reset.

    def __init__(self, glpane):
        """
        create an expr instance, to draw in addition to the model
        """
        # code copied from test_commands.py
        super(test_animation_mode, self).__init__(glpane) # that only calls some mode's init method, not IorE.__init__,
            # so (for now) call that separately
        IorE_guest_mixin.__init__(self, glpane)
        if 0:
            # expr from test_commands - works except for resizer highlighting
            ## expr1 = Rect(4, 1, green)
            expr1 = TextState()
            expr2 = DraggablyBoxed(expr1, resizable = True)
                ###BUG: resizing is projecting mouseray in the wrong way, when plane is tilted!
                # I vaguely recall that the Boxed resizable option was only coded for use in 2D widgets,
                # whereas some other constrained drag code is correct for 3D but not yet directly usable in Boxed.
                # So this is just an example interactive expr, not the best way to do resizing in 3D. (Though it could be fixed.)
            expr = expr2
        if 0:
            expr = Rect() # works
        if 1:
            expr = Image("/Users/bruce/Desktop/IMG_0560 clouds g5 2.jpg", size = Rect(), two_sided = True)
        
        # note: this code is similar to _expr_instance_for_imagename in confirmation_corner.py
        ih = get_glpane_InstanceHolder(glpane)
        index = (id(self),) # WARNING: needs to be unique, we're sharing this InstanceHolder with everything else in NE1
        self._expr_instance = ih.Instance( expr, index, skip_expr_compare = True)

        ## in Draw: add         self._expr_instance.draw()

        if TESTING_KLUGES:
            self.clear_command_state() ###### FOR TESTING
            print "clear_command_state in init, testing kluge"####

        return

    def clear_command_state(self):
        """
        (part of command API)
        """
        self.cmd_Stop()
        if TESTING_KLUGES:
            print "KLUGE FOR TESTING: set cannonWidth in cmd_Stop"
            self.cannonWidth = 2.0########### DOES IT FIX THE BUG? THEN ZAP.
        ## this line seems to mess up the reload of test_animation_mode when i reenter it when in itself:
        ## super(test_animation_mode, self).clear_command_state()
        return
    
    def Enter(self):
        print
        print "entering test_animation_mode again", time.asctime()
##        self.assy = self.w.assy # [AttributeError: can't set attribute -- property?]
        hacktrack(self.glpane)
        hack_standard_repaint_0(self.glpane, self.graphicsMode.pre_repaint)
            # KLUGE -- this ought to be part of an Enter_GraphicsMode method...
            # there was something like that in one of those Pan/Rotate/Zoom classes too...
            # need to find those and decide when to call a method like that.
        self.glpane.pov = V(0, 0, 0)
        self.glpane.quat = Q(1,0,0,0) + Q(V(1,0,0),10.0 * pi/180)
        print "self.glpane.scale =", self.glpane.scale # 10 -- or 10.0?
        self.glpane.scale = 20.0 #### 070813 # note: using 20 (int not float) may have caused AssertionError:
            ## in GLPane.py 3473 in typecheckViewArgs
            ## assert isinstance(s2, float)
        
        print "self.glpane.scale changed to", self.glpane.scale
        self.right = V(1,0,0) ## self.glpane.right
        self.up = V(0,1,0)
        self.left = - self.right
        self.down = - self.up
        self.away = V(0,0,-1)
        self.towards = - self.away
        self.origin = - self.glpane.pov ###k replace with V(0,0,0)
        self.guy = guy(self)
        self.cannon = cannon(self)
        
        ##self.glbufstates = [0, 0] # 0 = unknown, number = last drawn model state number
        self.modelstate = 1
        # set perspective view -- no need, just do it in user prefs
        return _superclass.Enter(self)
    
    def init_gui(self): #050528
        ## self.w.modifyToolbar.hide()
        self.hidethese = hidethese = []
        for tbname in annoyers:
            try:
                tb = getattr(self.w, tbname)
                if tb.isVisible(): # someone might make one not visible by default
                    tb.hide()
                    hidethese.append(tb) # only if hiding it was needed and claims it worked
            except:
                print_compact_traceback("hmm %s: " % tbname) # someone might rename one of them

        win = self.win
        self.propMgr = self.PM_class(win, commandrun = self)
        self.propMgr.show()

    def restore_gui(self): #050528
        ## self.w.modifyToolbar.show()
        for tb in self.hidethese:
            tb.show()

        self.propMgr.hide()

# not used now, but keep (was used to append DebugNodes):
##    def placenode(self, node):
##        "place newly made node somewhere in the MT"
##        # modified from Part.place_new_jig
##        part = self.assy.part
##        part.ensure_toplevel_group()
##        part.topnode.addchild(node) # order? later ones come below earlier ones, which is good.
##        self.w.mt.mt_update()
##        return

    def appendnew(self, new): ##FIX: stores object list (really a dict) in self.guy
        stuff = self.guy.stuff
        ## stuff.append(new) # it's a list
        stuff[id(new)] = new # it's a dict
        ## print "appendnew: %d things" % len(stuff) # test culling of old things -- works
        return

    def rotleft(self, amount):
        """
        [#doc is in caller]
        """
        # from Q doc: Q(V(x,y,z), theta) is what you probably want.
        #060218 bugfix: left -> down
        self.glpane.quat += Q(self.down, amount * 2 * pi) # does something, but not yet what i want. need to transform to my model...###@@@
        ## self.redraw() - do in caller
        
    def makeMenus(self):
        _superclass.makeMenus(self)
        self.Menu_spec = [
            ('loop', self.cmd_Start),
         ]
        return

    def cmd_Start(self): # renamed from myloop
        # WARNING: this does not return until the loop stops; it does recursive event processing
        # (including going into temporary subcommand modes, or even going entirely into other modes)
        # while it runs. If we wish some subcommands to suspect the simtime updates and redraws this
        # does, they should somehow set a flag here which affects this loop, since they have no
        # direct way to exit this loop immediately.
        if SILLY_TEST:
            self.cannonWidth = 5.0 - self.cannonWidth # test whether pm gets updated -- it doesn't (bug)
        if self._in_loop:
            print "cmd_Start: already in loop, ignoring"
            #e future: increase the time remaining
            return
        print "cmd_Start: starting loop"
        glpane = self.glpane
        starttime = self._loop_start_time = time.time()
        start_simtime = self.simtime
        safety_timeout = 600.0 # 10 minutes -- not really needed as long as 's' works to stop the loop
        self._please_exit_loop = False
        self._in_loop = True
        # if the menu stays up all this time, we'll have to instead set a flag to make this happen later, or so...
        # anyway, it doesn't.
        min_frame_time = 0.1 ### 0.02
        while not self._please_exit_loop and time.time() < starttime + safety_timeout:
            ## glpane.quat += Q(glpane.up, glpane.out) # works
            self.simtime = start_simtime + (time.time() - starttime)
            glpane.gl_update_duration()
                # This processes events (including keypresses etc, which mode should record),
                # and then does a redraw (which should update the state vars first),
                # times the redraw (and the other event processing) in glpane._repaint_start_time, glpane._repaint_end_time,
                # and sets glpane._repaint_duration =  max(MIN_REPAINT_TIME, duration), where MIN_REPAINT_TIME = 0.01.
                #
                # If any of those events exit this mode, that will happen right away, but our clear_command_state method
                # will run cmd_Stop so that this loop will exit ASAP. To make this exit faster,
                # we also test _please_exit_loop just below. (REVIEW: do we need to set such a flag to be tested
                # inside gl_update_duration itself??)
            if not self._please_exit_loop: #### TODO: also test whether app is exiting, in this and every other internal event loop
                duration = glpane._repaint_end_time - glpane._repaint_start_time
                # this is actual duration of state-update-calcs and redraw. if too fast, slow down!
                if duration < min_frame_time:
                    time.sleep(min_frame_time - duration)
            continue
        ## self.simtime = start_simtime + (time.time() - starttime) -- no, might cause glitch on next redraw
        self._in_loop = False
        return

    def cmd_Stop(self):
        if self._in_loop:
            print "cmd_Stop: exiting loop"
            self._please_exit_loop = True
        else:
            print "cmd_Stop: not in loop, ignoring" #e show this msg in PM somewhere?
        return

    pass # end of class test_animation_mode

# DebugNode

# end
