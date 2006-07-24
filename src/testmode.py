# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
testmode.py -- scratchpad for new code, OWNED BY BRUCE, not imported by default.

FOR NOW [060716], NO ONE BUT BRUCE SHOULD EDIT THIS FILE IN ANY WAY.

$Id$

How to use: make a symlink from ~/Nanorex/Modes/testmode.py to this file, i.e.

  % cd ~/Nanorex/Modes
  % ln -s /.../cad/src/testmode.py .

then find testmode in debug menu's custom modes submenu. It reloads testdraw.py
on every click, so new drawing code can be tried by editing that file and clicking.

(It also hides all your toolbars, but you can get them back using the context menu
on the Qt dock, or customize this feature by editing the "annoyers" list below.)

WARNING: some of the code in here might not be needed;
conversely, some of it might depend on code or data files bruce has at home.
'''

__author__ = "bruce"

from modes import *
from debug import print_compact_traceback, register_debug_menu_command
import time, math

from state_utils import copy_val

from selectMode import *

annoyers = ['editToolbar', 'fileToolbar', 'helpToolbar', 'modifyToolbar',
            'molecularDispToolbar', 'selectToolbar', 'simToolbar',
            ## 'toolsToolbar', # not sure why this is removed, maybe it no longer exists
            ## 'viewToolbar', # I often want this one
            ## one for modes too -- not sure of its name, but I guess I'll let it keep showing too
            ]

super = selectAtomsMode

class testmode(super):
    # class constants
    backgroundColor = 103/256.0, 124/256.0, 53/256.0
    modename = 'TEST'
    default_mode_status_text = "Mode: Test"

    def Draw(self):
        ## print "testmode draw"
        # initial purpose: test new drawing primitives, defined in testdraw.py, frequently edited
        ## did reload here, until 060723 late
        import testdraw
        try:
            testdraw.drawtest(self.o)
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.drawtest ignored: ")
        return

    def reload(self):
        import testdraw
        reload(testdraw)
        
    def leftDown(self, event):
        self.reload() # did this in Draw, not here & Enter, until 060723 late
        import testdraw
        try:
            testdraw.leftDown(self.o, event)
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.leftDown ignored: ")
        self.o.gl_update() # cause another call of self.Draw() [###e actually it might be better to let testdraw.leftDown decide on this]

    def leftDrag(self, event):
        pass

    def leftUp(self, event):
        pass

    
    def Enter(self):
        print
        print "entering testmode again", time.asctime()
        self.reload()
        self.assy = self.w.assy
##        hacktrack(self.o)
##        hack_standard_repaint_0(self.o, self.pre_repaint)
        self.o.pov = V(0,0,0)
        self.o.quat = Q(1,0,0,0) + Q(V(1,0,0),10.0 * pi/180)
        self.right = V(1,0,0) ## self.o.right
        self.up = V(0,1,0)
        self.left = - self.right
        self.down = - self.up
        self.away = V(0,0,-1)
        self.towards = - self.away
        self.origin = - self.o.pov ###k replace with V(0,0,0)
##        self.guy = guy(self)
        ##self.glbufstates = [0,0] # 0 = unknown, number = last drawn model state number
        self.modelstate = 1
        # set perspective view -- no need, just do it in user prefs
        return super.Enter(self)

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

    def restore_gui(self): #050528
        ## self.w.modifyToolbar.show()
        for tb in self.hidethese:
            tb.show()

    def middleDrag(self, event):
        glpane = self.o
##        q1 = Q(glpane.quat)
        super.middleDrag(self, event)
        self.modelstate += 1
##        q2 = Q(glpane.quat)
        ## novertigo(glpane)
##        q3 = Q(glpane.quat)
##        print "nv",q1,q2,q3
        return

##    brickpos = 2.5
##    def Draw(self):
####        # can we use smth lke mousepoints to print model coords of eyeball?
####        print "glpane says eyeball is now at", self.o.eyeball(), "and cov at", - self.o.pov, " ." ####@@@@
##        basicMode.Draw(self)
##        self.endpoint = endpoint = self.origin + self.right * 10.0
##        drawline(white, self.origin, endpoint)
##        ## drawwirecube(purple, self.origin, 5.0)
##        ## drawwirecube(gray, self.origin, 6.5)
##        if 0: drawbrick(yellow, self.origin, self.right, 2.0,4.0,6.0)
##        drawbrick(pink1, self.origin + V(self.brickpos,0,0), self.right, 2.0,4.0,6.0)
##        # with red, its lighting is pretty poor; pink1 looks nice
##        self.o.assy.draw(self.o)
##        ## thing.draw(self.o, endpoint)
##        self.guy.draw(self.o)
##        ## draw_debug_quats(self.o)
    
    def keyPressEvent(self,event):
        ascii = event.ascii()
        key = event.key()
        if ascii == ' ': # doesn't work
            self._please_exit_loop = True
        elif key == 32:
            self._please_exit_loop = True
        else:
            basicMode.keyPressEvent(self,event) #060429 try to get ',' and '.' binding
        return
    
    def keyReleaseEvent(self,event):
        pass ## thing.keyReleaseEvent(event)

    def makeMenus(self):
        super.makeMenus(self)
        self.Menu_spec = [
##            ('loop', self.myloop),
         ]

    _please_exit_loop = False
    _in_loop = False
    _loop_start_time = 0

    pass # end of class testmode

# end
