# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
"""
testmode.py -- scratchpad for new code (mainly related to DNA Origami),
OWNED BY BRUCE, not imported by default.

FOR NOW [060716], NO ONE BUT BRUCE SHOULD EDIT THIS FILE IN ANY WAY.
(Unless Ninad needs to edit the Qt4 version.)

$Id$

How to use:   [see also exprs/README.txt, which is more up to date]

  [this symlink is no longer needed as of 061207:]
  make a symlink from ~/Nanorex/Modes/testmode.py to this file, i.e.
  % cd ~/Nanorex/Modes
  % ln -s /.../cad/src/testmode.py .

then find testmode in the debug menu's custom modes submenu. It reloads testdraw.py
on every click on empty space, so new drawing code can be tried by editing that file and clicking.

(It also hides most of your toolbars, but you can get them back using the context menu
on the Qt dock, or by changing to another mode, or customize this feature by editing
the "annoyers" list below to leave out the toolbars you want to have remain.)

WARNING: some of the code in here might not be needed;
conversely, some of it might depend on code or data files bruce has at home.
Much of it depends on the "cad/src/exprs" module, and some of that depends
on the "cad/src/experimental/textures" directory.
"""

__author__ = "bruce"

from modes import *
from debug import print_compact_traceback, register_debug_menu_command
import time, math

from state_utils import copy_val

from selectMode import *
from depositMode import depositMode

annoyers = ['editToolbar', 'fileToolbar', 'helpToolbar', 'modifyToolbar',
            'molecularDispToolbar', 'selectToolbar', 'simToolbar',
            ## 'toolsToolbar', # not sure why this is removed, maybe it no longer exists
            ## 'viewToolbar', # I often want this one
            ## one for modes too -- not sure of its name, but I guess I'll let it keep showing too
            ]

## super = selectAtomsMode
super = depositMode

class testmode(super):
    # class constants
    backgroundColor = 103/256.0, 124/256.0, 53/256.0
    modename = 'TEST'
    default_mode_status_text = "Mode: Test"

    compass_moved_in_from_corner = True # only works when compassPosition == UPPER_RIGHT; should set False in basicMode [revised 070110] 
    ## _check_target_depth_fudge_factor = 0.0001 # same as GLPane, tho it caused a demo_drag bug 070115 -- try lower val sometime ###e
    _check_target_depth_fudge_factor = 0.00001 # this gives us another 10x safety factor in demo_drag [070116]
    standard_glDepthFunc = GL_LEQUAL # overrides default value of GL_LESS from GLPane; tested only re not causing bugs; maybe adopt it generally ##e [070117]
        # note: the bug in drawing the overlay in testexpr_10c when the openclose is highlighted is now fixed both with and without
        # this setting [tested both ways 070117]. The internal code doing what it's supposed to, due to this setting, is not tested.

    _defeat_update_selobj_MMB_specialcase = True # 070224; overridden at runtime in some methods below
    
    ## UNKNOWN_SELOBJ = something... this is actually not set here (necessary for now) but a bit later in exprs/test.py [061218 kluge]

    def render_scene(self, glpane):
        # This is always called, and modifying it would let us revise the entire rendering algorithm however needed.
        # This encompasses almost everything done within a single paintGL call -- even the framebuffer clear!
        # For what it doesn't include, see GLPane.paintGL, which gets to its call of this quickly.
        if 0:
            glpane.render_scene()
        else:
            import testdraw
            try:
                testdraw.render_scene(self, glpane)
            except:
                print_compact_traceback("exception in testdraw.render_scene ignored: ")
        return
    
    def Draw(self):
        import testdraw
        try:
            testdraw.Draw(self, self.o, super)
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.Draw ignored: ")
        return

    def Draw_after_highlighting(self, pickCheckOnly = False): #bruce 050610
        # I'm very suspicious of this pickCheckOnly arg in the API... it's not even acceptable to some modes,
        # it's not clear whether they'll be called with it, it's not documented what it should do,
        # and there seems to be a return value when it's used, but not all methods provide one.
        """Do more drawing, after the main drawing code has completed its highlighting/stenciling for selobj.
        Caller will leave glstate in standard form for Draw. Implems are free to turn off depth buffer read or write.
        Warning: anything implems do to depth or stencil buffers will affect the standard selobj-check in bareMotion.
        """
        ## super.Draw_after_highlighting(self, pickCheckOnly) # let testdraw do this if if wants to
        import testdraw
        try:
            testdraw.Draw_after_highlighting(self, pickCheckOnly, self.o, super)
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.Draw_after_highlighting ignored: ")
        return        

    def reload(self):
        import testdraw
        reload(testdraw)
        
    def leftDown(self, event):
        import testdraw
        try:
            testdraw.leftDown(self, event, self.o, super)
                # note: if super.leftDown and/or gl_update should be called now, this must do it.
                # note: this might reload testdraw (inside self.emptySpaceLeftDown).
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.leftDown ignored: ")

    def emptySpaceLeftDown(self, event):
        self.reload()
        super.emptySpaceLeftDown(self, event) #e does testdraw need to intercept this?

    # let super do these, until we get around to defining them here and letting testdraw intercept them:
##    def leftDrag(self, event):
##        pass
##
##    def leftUp(self, event):
##        pass
    
    def Enter(self):
        print
        print "entering testmode again", time.asctime()
        self.reload()
        self.assy = self.w.assy
        self.o.pov = V(0,0,0)
        self.o.quat = Q(1,0,0,0)

        res = super.Enter(self)
        if 1:
            # new 070103; needs reload??
            import testdraw
            testdraw.end_of_Enter(self.o)
        return res

    def init_gui(self): #050528; revised 070123
        ## self.w.modifyToolbar.hide()
        self.hidethese = hidethese = []
        win = self.w
        for tbname in annoyers:
            try:
                try:
                    tb = getattr(win, tbname)
                except AttributeError: # someone might rename one of them
                    import __main__
                    if __main__.USING_Qt3: # most of them are not defined in Qt4 so don't bother printing this then [bruce 070123]
                        print "testmode: fyi: toolbar missing: %s" % tbname # someone might rename one of them
                else:
                    if tb.isVisible(): # someone might make one not visible by default
                        tb.hide()
                        hidethese.append(tb) # only if hiding it was needed and claims it worked
            except:
                # bug
                print_compact_traceback("bug in hiding toolbar %r in testmode init_gui: " % tbname)
            continue
        return

    def restore_gui(self): #050528
        ## self.w.modifyToolbar.show()
        for tb in self.hidethese:
            tb.show()


    # middle* event methods, defined here to permit "New motion UI" to be prototyped in testmode [bruce 070224].
    #
    # Notes: there are 12 "middle" methods in all (4 key combos, and Down Drag Up),
    # tho for left & right buttons there are only 9 (since there is no ShiftCntl combo).
    #   That doesn't bother selectMode since it ignores the ShiftCntl part of the methodname,
    # channelling them all together and later using glpane.modkeys to sort them out
    # (which does define a separate state for 'Shift+Control').
    #   But for capturing these middle
    # methods (i.e. Alt/Option button) for the "New motion UI", it's tougher -- we want to use
    # selectMode's ability to count a tiny drag as not a drag, to dispatch on selobj type
    # (Atom, Bond, Jig, DragHandler), and maybe more, so we need to turn these into left methods here,
    # but we need to add something like glpane.altkey to not forget they were really middle,
    # and then we need to modify selectMode to not think they are really left if this would mess it up
    # (which may only matter for Atom Bond Jig being visible in testmode) -- only for DragHandler would
    # it pass the event inside (and then we'd detect glpane.altkey inside Highlightable).
    #   Either that, or we could actually implement the "New motion UI" directly inside selectMode,
    # for all objects.
    #   Either way, we need extensive mods to selectMode, but that's just been split into new files
    # in Qt4 branch but not Qt3 branch, so it might be better to not do that now, either splitting it
    # in Qt3 the same way, or holding off until Qt4 is standard.
    #   I guess there is one simpler way: ignore the issue of Atom Bond Jig being visible in testmode
    # (the bug will be that middle clicks on them act like left clicks) -- just turn middle into left,
    # don't tell selectMode, and worry only about the empty space or DragHandler cases. We can also
    # forget the ShiftCntl part at the same time. Ok, I'll try it! (It required a minor change in
    # selectMode, to notice a new attr _defeat_update_selobj_MMB_specialcase defined above.)
    #   It was simpler before I added the debug_pref to turn it off! 3 distinct methods before, all 12 needed now.

    def _update_MMB_policy(self):
        "[private helper for middle* methods]"
        capture_MMB = debug_pref("testmode capture MMB", Choice_boolean_False, prefs_key = "A9 devel/testmode/testmode capture MMB")
        self._capture_MMB = self._defeat_update_selobj_MMB_specialcase = capture_MMB
        return

    def _middle_anything(self, event, methodname):
        "[private helper for middle* methods]"
        # glpane = self.o
        # print "%s: glpane.button = %r" % (methodname, glpane.button,)
            # 'MMB' for Down and Drag, None for Up, in singlet middleClick; when it's None,
            # Highlightable will just have to remember it from the middleDown or middleDrag [and now it does]
        self._update_MMB_policy()
        if self._capture_MMB:
            if methodname.endswith('Down'):
                super.leftDown(self, event) # don't go through self.leftDown for now -- it's only used for reload, gl_update, etc
            elif methodname.endswith('Drag'):
                super.leftDrag(self, event)
            elif methodname.endswith('Up'):
                super.leftUp(self, event)
            else:
                assert 0, "bad methodname %r" % (methodname,)
        else:
            method = getattr(super, methodname)
            method(self, event)
        return
        
    def middleDown(self, event):
        self._middle_anything( event, 'middleDown')
    def middleShiftDown(self, event):
        self._middle_anything( event, 'middleShiftDown')
    def middleCntlDown(self, event):
        self._middle_anything( event, 'middleCntlDown')
    def middleShiftCntlDown(self, event):
        self._middle_anything( event, 'middleShiftCntlDown')
        
    def middleDrag(self, event):
        self._middle_anything( event, 'middleDrag')
    def middleShiftDrag(self, event):
        self._middle_anything( event, 'middleShiftDrag')
    def middleCntlDrag(self, event):
        self._middle_anything( event, 'middleCntlDrag')
    def middleShiftCntlDrag(self, event):
        self._middle_anything( event, 'middleShiftCntlDrag')
        
    def middleUp(self, event):
        self._middle_anything( event, 'middleUp')
    def middleShiftUp(self, event):
        self._middle_anything( event, 'middleShiftUp')
    def middleCntlUp(self, event):
        self._middle_anything( event, 'middleCntlUp')
    def middleShiftCntlUp(self, event):
        self._middle_anything( event, 'middleShiftCntlUp')


    def keyPressEvent(self, event):
        try:
            ascii = event.ascii()
        except:
            # event.ascii() reportedly doesn't work in Qt4 [bruce 070122]
            ascii = -1
        try:
            key = event.key()
        except:
            # no one reported a problem with this, but we might as well be paranoid about it [bruce 070122]
            key = -1
        if ascii == ' ': # doesn't work
            self._please_exit_loop = True
        elif key == 32:
            self._please_exit_loop = True
        else:
            super.keyPressEvent(self, event) #060429 try to get ',' and '.' binding #bruce 070122 basicMode->super
        return
    
    def keyReleaseEvent(self, event):
        super.keyReleaseEvent(self, event) #bruce 070122 new feature (probably fixes some bugs), and basicMode->super

    def makeMenus(self):
        super.makeMenus(self) # this makes standard items for selobj if it's atom or bond or Highlightable, and a few more:
        ## print "menu_spec is", self.Menu_spec # note, it may differ depending on selobj
            ## menu_spec is:
            ##[('Enable Jig Selection', <bound method testmode.toggleJigSelection...>, 'checked'),
            ## None,
            ## ('Change Background Color...', <bound method MWsemantics.dispBGColor...>)]
##        self.Menu_spec.extend( [
##            ('loop', self.myloop),
##         ] )
        return
    
    _please_exit_loop = False
    _in_loop = False
    _loop_start_time = 0

    pass # end of class testmode

# end
