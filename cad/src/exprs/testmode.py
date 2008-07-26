# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
testmode.py -- Command/GraphicsMode for testing graphical exprs
(implemented in the exprs module).

@author: Bruce
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

How to use:

  [see also exprs/README.txt, which is more up to date]

  [this symlink is no longer needed as of 061207:]
  make a symlink from ~/Nanorex/Modes/testmode.py to this file, i.e.
  % cd ~/Nanorex/Modes
  % ln -s /.../cad/src/exprs/testmode.py .

then find testmode in the debug menu's custom modes submenu. It reloads testdraw.py
on every click on empty space, so new drawing code can be tried by editing that file and clicking.

(It also hides most of your toolbars, but you can get them back using the context menu
on the Qt dock, or by changing to another mode, or customize this feature by editing
the "annoyers" list below to leave out the toolbars you want to have remain.)

WARNING: some of the code in here might not be needed;
conversely, some of it might depend on code or data files bruce has at home.
Much of it depends on the "cad/src/exprs" module, and some of that used to depend
on the "cad/src/experimental/textures" directory. As of 070604 that's being changed
to depend on a new subdirectory of cad/src/ui named exprs (so it will be supported
in built releases).
"""

import time

from geometry.VQT import V, Q
from commands.BuildAtoms.depositMode import depositMode

from utilities.debug import print_compact_traceback
from utilities.debug_prefs import Choice_boolean_True
from utilities.debug_prefs import Choice_boolean_False
from utilities.debug_prefs import debug_pref


annoyers = ['editToolbar', 'fileToolbar', 'helpToolbar', 'modifyToolbar',
            'molecularDispToolbar', 'selectToolbar', 'simToolbar',
            ## 'toolsToolbar', # not sure why this is removed, maybe it no longer exists
            ## 'viewToolbar', # I often want this one
            ## one for modes too -- not sure of its name, but I guess I'll let it keep showing too
            ]

## superclass = selectAtomsMode
superclass = depositMode

class testmode(superclass):
    # class constants -- some each for Command and GraphicsMode, once we split into those

    # for Command
    
    commandName = 'TEST'
    featurename = "Test Command: Exprs Package"
    from utilities.constants import CL_ENVIRONMENT_PROVIDING
    command_level = CL_ENVIRONMENT_PROVIDING

    # for GraphicsMode

    ## check_target_depth_fudge_factor = 0.0001 # same as GLPane, tho it caused a demo_drag bug 070115 -- try lower val sometime ###e
    check_target_depth_fudge_factor = 0.00001 # this gives us another 10x safety factor in demo_drag [070116]

    # unclassified (Command vs GraphicsMode)
    
    backgroundColor = 103/256.0, 124/256.0, 53/256.0

    compass_moved_in_from_corner = True # only works when compassPosition == UPPER_RIGHT; should set False in basicMode [revised 070110] 

    _defeat_update_selobj_MMB_specialcase = True # 070224; overridden at runtime in some methods below
    
    ## UNKNOWN_SELOBJ = something... this is actually not set here (necessary for now) but a bit later in exprs/test.py [061218 kluge]

##    # work around some of our superclass depositMode's dependence on having its particular PM
##    # [now taken care of in depositMode itself]
##    
##    def pastable_element(self): # bruce 070921
##        "[overrides superclass method]"
##        ## return self.propMgr.elementChooser.getElement()
##        from elements import Carbon
##        return Carbon

    # ==
    
    def render_scene(self, glpane):
        # This is always called, and modifying it would let us revise the entire rendering algorithm however needed.
        # This encompasses almost everything done within a single paintGL call -- even the framebuffer clear!
        # For what it doesn't include, see GLPane.paintGL, which gets to its call of this quickly.
        if 0:
            glpane.render_scene()
        else:
            import exprs.testdraw as testdraw
            try:
                testdraw.render_scene(self, glpane)
            except:
                print_compact_traceback("exception in testdraw.render_scene ignored: ")
        return
    
    def Draw(self):
        self.command._background_object = None
            # a _background_object is only active for event handlers when it was set
            # during the most recent call of testdraw.Draw
        import exprs.testdraw as testdraw
        try:
            testdraw.Draw(self, self.o, superclass)
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
        ## superclass.Draw_after_highlighting(self, pickCheckOnly) # let testdraw do this if if wants to
        import exprs.testdraw as testdraw
        try:
            testdraw.Draw_after_highlighting(self, pickCheckOnly, self.o, superclass)
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.Draw_after_highlighting ignored: ")
        return        

    def reload(self):
        import exprs.testdraw as testdraw
        #bruce 070611 bugfix for release builds: add try/except
        try:
            reload(testdraw)
        except ImportError:
            pass # print "testdraw reload ImportError, ignoring"
        return
        
    def leftDown(self, event):
        import exprs.testdraw as testdraw
        try:
            testdraw.leftDown(self, event, self.o, superclass)
                # note: if superclass.leftDown and/or gl_update should be called now, this must do it.
                # note: this might reload testdraw (inside self.emptySpaceLeftDown).
        except:
            #e history message?
            print_compact_traceback("exception in testdraw.leftDown ignored: ")

    def leftDouble(self, event):
        # Note: added to testmode 070324. (See also selectMode.dragHandlerLeftDouble, which is never called --
        # either it's obsolete, or this should be merged into selectMode.leftDouble and it should call that
        # and let that do the rest of what this does now.)
        #
        # Some issues:
        # - depositMode version deposits when in empty space; ours must not do that if there's a background object
        #   (unless that object says to, somehow), but should otherwise.
        # - depositMode version sets "self.graphicsMode.ignore_next_leftUp_event = True # Fixes bug 1467",
        #   which I guess we should always set (even if not depositing) -- not sure. In theory, bg object should decide.
        #   Also in theory, good code would never need this, since leftUp would only do things its leftDown asked it to do.
        #   Guess: depositMode.leftUp doesn't follow that principle, and this flag works around that flaw by
        #   "turning off an assumption about what leftDown did".
        #   (For example (speculation), that it reset certain variables left over from prior drag??)
        self.graphicsMode.ignore_next_leftUp_event = True
            # I'm guessing this is always necessary, though I'm not sure.
            # Note that it will prevent the call of drag_handler.ReleasedOn -- this seems desirable,
            # since the press method (leftClick) was not called either, for the 2nd click of a double click --
            # and it's also the same behavior as before we added this implem of leftDouble.
            # However, minor ###BUG: the superclasses only reset it in leftUp -- if they were more cautious
            # they'd also do so in leftDown, in case of a missing (or buggily overidden) leftUp call.
            # (Or GLPane would, so not every mode class has to. Or it'd just call leftDoubleUp or so.)
        if self.drag_handler is not None:
            print "fyi: testmode passing leftDouble to drag_handler = %r" % (self.drag_handler,) ####
            # This works: it's a highlightable or a _background_object if we double-clicked on one,
            # and otherwise false (presumably None).
            # So when it's there, let's pass this event to it for handling, and not to the superclass.
            # (Note: most of the DragHandler interface is implemented in selectMode (see also DragHandler.py),
            #  but this new method in it ('leftDouble') is implemented only in testmode.)
            method = getattr( self.drag_handler, 'leftDouble', None)
            if method is not None:
                method(event, self) #e protect from exceptions?
        else:
            print "fyi: testmode passing leftDouble to superclass (since no drag_handler)" ####
            superclass.leftDouble(self, event)
        return

    _background_object = None #070322 new feature: can be set during self.Draw to something to handle clicks on background
        # Note: this is stored in the Command instance, but usually accessed
        # from the GraphicsMode instance using .command._background_object.
        # [bruce 071010]
    
    def get_obj_under_cursor(self, event): #070322 [assume part of GraphicsMode even though not in all subclasses of that]
        "this is called in *some cases* by various mode event handler methods to find out what object the cursor is over"
        # The kinds of calls of this method (whose interface assumptions we need to be sensitive to):
        # - depositMode.singletLeftUp indirectly calls it and checks whether the return value is an instance of Atom,
        #   handling it specially if so.
        # - similarly, selectMode.atomLeftUp can indirectly call it and check whether it returns a non-singlet instance of Atom.
        # - its main call is in selectMode.leftDown to decide (based on the kind of object returned -- None, or anything which
        #   hasattr 'leftClick', or being an instance of Atom or Bond or Jig)
        #   which kind of more specialized leftDown method to call.
        # Note that this method is only called for leftDown or leftUp, never during a drag or baremotion,
        # so its speed is not all-important. That means it might be fast enough, even if it creates new Instances
        # (of exprs module classes) on each call.
        #    WARNING: overriding this method doesn't override the lower-level determination of glpane.selobj,
        # which is also used directly by mode event-handling methods in a similar way as they use this method,
        # and is used in GLPane to determine hover-highlighting behavior (both between and within drags -- in fact,
        #  there is not yet a good-enough way for hover-highlighting behavior to be different during a drag).
        # For some purposes, overriding the determination of selobj in GLPane would be more useful and more flexible
        # than overriding this method; to affect highlighting behavior, it would be essential. [070323 comment]
        res = superclass.get_obj_under_cursor(self, event)
        #e here is where we might let some other mode attr replace or wrap objects in specified classes. [070323 comment]
        if res is None:
            res = self.command._background_object # usually None, sometimes set during draw to something else [070322]
            if res is not None:
                if not hasattr(res, 'leftClick'):
                    print "bug: testmode._background_object %r has no leftClick, will be ineffective" % (res,)
        return res
    
    def emptySpaceLeftDown(self, event):
        #e note: if we override self.get_obj_under_cursor(event) to return a bg object rather than None,
        # i.e. if something sets self.command._background_object to something other than None,
        # then this won't be called by selectMode.leftDown.
        emptySpace_reload = debug_pref("testmode: reload on empty space leftDown?",
                                       Choice_boolean_True,
                                       prefs_key = "A9 devel/testmode/reload on empty space leftDown" ) #070312, also in exprs/test.py
        if emptySpace_reload:
            self.reload()
        superclass.emptySpaceLeftDown(self, event) #e does testdraw need to intercept this? no... instead we override get_obj_under_cursor

    # let superclass do these -- no need to define them here and let testdraw intercept them:
##    def leftDrag(self, event):
##        pass
##
##    def leftUp(self, event):
##        pass
    
    def Enter(self):
        print
        print "entering testmode again", time.asctime()
        self.reload()
##        self.assy = self.w.assy # [now done by basicCommand]
        self.o.pov = V(0,0,0)
        self.o.quat = Q(1,0,0,0)

        res = superclass.Enter(self)
        if 1:
            # new 070103; needs reload??
            import exprs.testdraw as testdraw
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
                    ## import __main__
                    if 0: ## __main__.USING_Qt3: # most of them are not defined in Qt4 so don't bother printing this then [bruce 070123]
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
    # (Atom, Bond, Jig, DragHandler_API), and maybe more, so we need to turn these into left methods here,
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
                superclass.leftDown(self, event) # don't go through self.leftDown for now -- it's only used for reload, gl_update, etc
            elif methodname.endswith('Drag'):
                superclass.leftDrag(self, event)
            elif methodname.endswith('Up'):
                superclass.leftUp(self, event)
            else:
                assert 0, "bad methodname %r" % (methodname,)
        else:
            method = getattr(superclass, methodname)
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
            key = event.key()
        except:
            # no one reported a problem with this, but we might as well be paranoid about it [bruce 070122]
            key = -1
        if key == 32:
            self._please_exit_loop = True
        else:
            superclass.keyPressEvent(self, event) #060429 try to get ',' and '.' binding #bruce 070122 basicMode->superclass
        return
    
    def keyReleaseEvent(self, event):
        superclass.keyReleaseEvent(self, event) #bruce 070122 new feature (probably fixes some bugs), and basicMode->superclass

    def makeMenus(self):
        ### WARNING: this copies and slightly modifies selectMode.makeMenus (not those of our superclass, depositMode!);
        # with slightly more work, we could instead just decide when to call the superclass one here
        # vs. when not to, rather than duplicating the menu items it produces.
        # But we can't do that for now, since we want to ditch its general items
        # whenever there is a selobj which defines make_selobj_cmenu_items,
        # even when we add atom-specific ones it also hardcodes,
        # and later we may also decide to not ditch them if the selobj's make_selobj_cmenu_items returns nothing.
        # DANGER: if this copied code got changed for Qt4, we're introducing a Qt4 porting problem into testmode.
        # [bruce 070228]
    
        selatom, selobj = self.update_selatom_and_selobj( None)

        # not doing:
        ## superclass.makeMenus(self) # this makes standard items for selobj if it's atom or bond or Highlightable, and a few more
        
        self.Menu_spec = []

        ditch_generic = False #bruce 070228
        
        # Local minimize [now called Adjust Atoms in history/Undo, Adjust <what> here and in selectMode -- mark & bruce 060705]
        # WARNING: This code is duplicated in depositMode.makeMenus(). mark 060314.
        if selatom is not None and not selatom.is_singlet() and self.w.simSetupAction.isEnabled():
            # see comments in depositMode version
            self.Menu_spec.append(( 'Adjust atom %s' % selatom, lambda e1 = None, a = selatom: self.localmin(a,0) ))
            self.Menu_spec.append(( 'Adjust 1 layer', lambda e1 = None, a = selatom: self.localmin(a,1) ))
            self.Menu_spec.append(( 'Adjust 2 layers', lambda e1 = None, a = selatom: self.localmin(a,2) ))
            ditch_generic = True #bruce 070228
            
        # selobj-specific menu items. [revised by bruce 060405; for more info see the same code in depositMode]
        if selobj is not None and hasattr(selobj, 'make_selobj_cmenu_items'):
            try:
                selobj.make_selobj_cmenu_items(self.Menu_spec)
                ditch_generic = True #bruce 070228
            except:
                print_compact_traceback("bug: exception (ignored) in make_selobj_cmenu_items for %r: " % selobj)

        if not ditch_generic: #bruce 070228 added this cond; ###BUG: we still have a "Web help: test mode" added by something!
        
            # separator and other mode menu items.
            if self.Menu_spec:
                self.Menu_spec.append(None)
            
            # Enable/Disable Jig Selection.
            # This is duplicated in depositMode.makeMenus() and selectMolsMode.makeMenus().
            if self.o.jigSelectionEnabled:
                self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'checked')])
            else:
                self.Menu_spec.extend( [('Enable Jig Selection',  self.toggleJigSelection, 'unchecked')])
                
            self.Menu_spec.extend( [
                # mark 060303. added the following:
                None,
                ('Edit Color Scheme...', self.w.colorSchemeCommand),
                ])
            pass

##        self.Menu_spec.extend( [
##            ('loop', self.myloop),
##         ] )
        
        return # from makeMenus

    # probably unused, but mentioned in real code, and might be added back (related to self.myloop):
    _please_exit_loop = False
    _in_loop = False
    _loop_start_time = 0

    pass # end of class testmode

# end
