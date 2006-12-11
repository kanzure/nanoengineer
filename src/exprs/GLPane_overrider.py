"""
$Id$
"""

from GLPane import * # since this mode might depend on all kinds of imports and constants in that module

from idlelib.Delegator import Delegator

class GLPane_overrider(Delegator, object): # object superclass added for selobj = property(...), unreviewed re Delegator
    """Be a proxy for the GLPane, which replaces some of its methods with our own versions,
    for use only during render_scene.
       Note that this is not a subclass of GLPane,
    but in some ways acts like one, but any method call delegated into GLPane will NOT get back
    to this proxy object when it calls submethods, even if those submethods are defined here.
       When this sets attrs of GLPane that need to be noticed by outside code via GLPane itself,
    this will need to say self.delegate.attr = val
    where the methods of GLPane it was copied from would just say self.attr = val.
    But we don't do this change for gets of those attrs for in comments, to reduce unnecessary diffs.
    """
    ### WARNING: much of this code is duplicated with GLPane.py in cad/src.
    ### sets to fix: if lots, make a property-like thing to delegate an attr to a delegate -- would be generally useful
    ### or make it happen auto? Delegator can't do that, can something else do it?
    # self.selobj - FIXED i.e. sets use self.delegate.selobj
    # self.glselect_dict - ok since modified, never replaced
    # self.need_setup_lighting - FIXED
    # self.wants_gl_update - FIXED
    # self.vdist - FIXED
    # self.glselect_wanted - FIXED
    # self.targetdepth - FIX UNLESS LOCAL - seems ok since local
    # self.current_glselect - FIX UNLESS LOCAL - seems ok since local -- WRONG, external code looks at it! (modes, selectMode)
        # btw, the same code in those files fails to set it here... in fact maybe i'm wrong and it doesn't look at it,
        # but starting now [061208 1032p] Highlightable is going to look at it, so (1) i'll put it in self.delegate,
        # (2) the jig select code in those files might be wrong now, if I ever draw jigs in funny projection matrices
        # (as I surely will someday).
    # self.wX # FIX - seems ok since local
    # self.wY # FIX - seems ok since local
    # self.glselect - ok since obs
    #
    # ok since readonly in rendering code:
    ##    self.compassPosition
    ##    self.quat 
    ##    self.scale
    ##    self.zoomFactor
    ##    self.near
    ##    self.far
    #
    # things returned by __getattr__ should be ok
    # things set by begin_tracking_usage -- hopefully ok since only used in this code, not in the code of GLPane called outside of this

    def _get_selobj(self):
        return self.delegate.selobj
    def _set_selobj(self, val):
        self.delegate.selobj = val
    selobj = property(_get_selobj, _set_selobj) # 061211 954a, see if this fixes highlight-delay bug when overrider is used ####
    
    def render_scene(self):#bruce 061208 split this out so some modes can override it (also removed obsolete trans_feature experiment)
        
        #k not sure whether next things are also needed in the split-out standard_repaint [bruce 050617]

        drawer._glprefs.update() #bruce 051126; kluge: have to do this before lighting *and* inside standard_repaint_0
        
        if self.need_setup_lighting \
          or self._last_glprefs_data_used_by_lights != drawer.glprefs_data_used_by_setup_standard_lights() \
          or debug_pref("always setup_lighting?", Choice_boolean_False):
            #bruce 060415 added debug_pref("always setup_lighting?"), in GLPane and ThumbView [KEEP DFLTS THE SAME!!];
            # using it makes specularity work on my iMac G4,
            # except for brief periods as you move mouse around to change selobj (also observed on G5, but less frequently I think).
            # BTW using this (on G4) has no effect on whether "new wirespheres" is needed to make wirespheres visible.
            #
            # (bruce 051126 added override_light_specular part of condition)
            # I don't know if it matters to avoid calling this every time...
            # in case it's slow, we'll only do it when it might have changed.
            self.delegate.need_setup_lighting = False # set to true again if setLighting is called
            self._setup_lighting()

        self.standard_repaint()
        
        return # from render_scene
    
    def standard_repaint(self): #bruce 050617 split this out; bruce 061208 removed obsolete special_topnode experiment
        """#doc... this trashes both gl matrices! caller must push them both if it needs the current ones.
        this routine sets its own matrixmode but depends on other gl state being standard when entered.
        """
        match_checking_code = self.begin_tracking_usage() #bruce 050806
        try:
            try:
                self.standard_repaint_0()
            except:
                print "exception in standard_repaint_0 (being reraised)"
                    # we're not restoring stack depths here, so this will mess up callers, so we'll reraise;
                    # so the caller will print a traceback, thus we don't need to print one here. [bruce 050806]
                raise
        finally:
            self.delegate.wants_gl_update = True #bruce 050804
            self.end_tracking_usage( match_checking_code, self.wants_gl_update_was_True ) # same invalidator even if exception
        return

    def standard_repaint_0(self):
        drawer._glprefs.update() #bruce 051126 (so prefs changes do gl_update when needed)
            # (kluge: have to do this before lighting *and* inside standard_repaint_0)
        c = self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT )
            #e if stencil clear is expensive, we could optim and only do it when needed [bruce ca. 050615]

        # "Blue Sky" is the only gradient supported in A7.  Mark 05
        if self.backgroundGradient:
            vtColors = (bluesky)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            drawer.drawFullWindow(vtColors)

        aspect = (self.width + 0.0)/(self.height + 0.0)
        vdist = 6.0 * self.scale
        self.delegate.vdist = vdist #bruce 050616 new feature (storing vdist in self), not yet used where it ought to be
        
        self._setup_modelview( vdist)
            #bruce 050608 moved modelview setup here, from just before the mode.Draw call

        # if GL_SELECT pass is needed (for hit test of objects with mouse), do it first.
        ###e note: if any objects moved since they were last rendered, this hit-test will still work (using their new posns),
        # but the later depth comparison (below) might not work right. See comments there for details.
        self.glselect_dict.clear()
            # this will be filled iff we do a gl_select draw,
            # then used only in the same paintGL call to alert some objects they might be the one

        if self.selobj is not None: #bruce 050702 part of fixing bug 716 (and possibly 715-5, though that's untested)
            try:
                # this 'try' might not be needed once the following method is fully implemented,
                # but it's good anyway for robustness
                if not self.mode.selobj_still_ok(self.selobj) or self.selobj_hicolor(self.selobj) is None:
                    #bruce 050822 added the selobj_hicolor test
                    self.set_selobj(None)
            except:
                # bug, but for now, don't disallow this selobj in this case
                # (message would be too verbose except for debug version)
                if platform.atom_debug:
                    print_compact_traceback("atom_debug: exception ignored: ")
                pass
            pass
        
        if self.glselect_wanted:
            ####@@@@ WARNING: The original code for this, here in GLPane, has been duplicated and slightly modified
            # in at least three other places (search for glRenderMode to find them). This is bad; common code
            # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
            # that should be fixed too. [bruce 060721 comment]
            wX, wY, self.targetdepth = self.glselect_wanted # wX,wY is the point to do the hit-test at
                # targetdepth is the depth buffer value to look for at that point, during ordinary drawing phase
                # (could also be used to set up clipping planes to further restrict hit-test, but this isn't yet done)
                # (Warning: targetdepth could in theory be out of date, if more events come between bareMotion
                #  and the one caused by its gl_update, whose paintGL is what's running now, and if those events
                #  move what's drawn. Maybe that could happen with mousewheel events or (someday) with keypresses
                #  having a graphical effect. Ideally we'd count intentional redraws, and disable this picking in that case.)
            self.wX, self.wY = wX,wY
            self.delegate.glselect_wanted = 0
            self.delegate.current_glselect = (wX,wY,3,3) #bruce 050615 for use by nodes which want to set up their own projection matrix
            self._setup_projection( aspect, vdist, glselect = self.current_glselect ) # option makes it use gluPickMatrix
                # replace 3,3 with 1,1? 5,5? not sure whether this will matter... in principle should have no effect except speed
            glSelectBuffer(self.glselectBufferSize)
            glRenderMode(GL_SELECT)
            glInitNames()
            ## glPushName(0) # this would be ignored if not in GL_SELECT mode, so do it after we enter that! [no longer needed]
            ## self.glselect = 1
            glMatrixMode(GL_MODELVIEW)
            try:
                self.mode.Draw() # should perhaps optim by skipping chunks based on bbox... don't know if that would help or hurt
                    # note: this might call some display lists which, when created, registered namestack names,
                    # so we need to still know those names!
            except:
                print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
                glMatrixMode(GL_MODELVIEW)
                self._setup_modelview( vdist) ###k correctness of this is unreviewed! ####@@@@
                # now it's important to continue, at least enough to restore other gl state
            self.delegate.current_glselect = False
            ###e On systems with no stencil buffer, I think we'd also need to draw selobj here in highlighted form
            # (in case that form is bigger than when it's not highlighted), or (easier & faster) just always pretend
            # it passes the hit test and add it to glselect_dict -- and, make sure to give it "first dibs" for being
            # the next selobj. I'll implement some of this now (untested when no stencil buffer) but not yet all. [bruce 050612]
            obj = self.selobj
            if obj is not None:
                self.glselect_dict[id(obj)] = obj
                    ###k unneeded, if the func that looks at this dict always tries selobj first
                    # (except for a kluge near "if self.glselect_dict", commented on below)
            ## self.glselect = 0
            glFlush()
            hit_records = list(glRenderMode(GL_RENDER))
            ## print "%d hits" % len(hit_records)
            for (near,far,names) in hit_records: # see example code, renderpass.py
                ## print "hit record: near,far,names:",near,far,names
                    # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                    # which proves that near/far are too far apart to give actual depth,
                    # in spite of the 1-pixel drawing window (presumably they're vertices
                    # taken from unclipped primitives, not clipped ones).
                if 1:
                    # partial workaround for bug 1527. This can be removed once that bug (in drawer.py)
                    # is properly fixed. This exists in two places -- GLPane.py and modes.py. [bruce 060217]
                    if names and names[-1] == 0:
                        print "%d(g) partial workaround for bug 1527: removing 0 from end of namestack:" % env.redraw_counter, names
                        names = names[:-1]
##                        if names:
##                            print " new last element maps to %r" % env.obj_with_glselect_name.get(names[-1])
                if names:
                    # for now, len is always 0 or 1, i think; if not, best to use only the last element...
                    # tho if we ever support "name/subname paths" we'll probably let first name interpret the remaining ones.
                    ###e in fact, when nodes change projection or viewport for kids, and/or share their kids, they need to
                    # put their own names on the stack, so we'll know how to redraw the kids, or which ones are meant when shared.
                    if platform.atom_debug and len(names) > 1: ###@@@ bruce 060725
                        if len(names) == 2 and names[0] == names[1]:
                            if not env.seen_before("dual-names bug"): # this happens for Atoms, don't know why (colorsorter bug??)
                                print "debug (once-per-session message): why are some glnames duplicated on the namestack?",names
                        else:
                            print "debug fyi: len(names) == %d (names = %r)" % (len(names), names)
                    obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                    if obj is None:
                        print "bug: obj_with_glselect_name returns None for name %r at end of namestack %r" % (names[-1],names)
                    self.glselect_dict[id(obj)] = obj # now these can be rerendered specially, at the end of mode.Draw
            #e maybe we should now sort glselect_dict by "hit priority" (for depth-tiebreaking), or at least put self.selobj first.
            # (or this could be done lower down, where it's used.)
            
        self._setup_projection( aspect, vdist)

        # In the glselect_wanted case, we now know (in glselect_dict) which objects draw any pixels at the mouse position,
        # but not which one is in front (the near/far info from GL_SELECT has too wide a range to tell us that).
        # So we have to get them to tell us their depth at that point (as it was last actually drawn
            ###@@@dothat for bugfix; also selobj first)
        # (and how it compares to the prior measured depth-buffer value there, as passed in glselect_wanted,
        #  if we want to avoid selecting something when it's obscured by non-selectable drawing in front of it).
        if self.glselect_dict:
            # kluge: this is always the case if self.glselect_wanted was set and self.selobj was set,
            # since selobj is always stored in glselect_dict then; if not for that, we might need to reset
            # selobj to None here for empty glselect_dict -- not sure, not fully analyzed. [bruce 050612]
            newpicked = self.preDraw_glselect_dict() # retval is new mouseover object, or None ###k verify
            ###e now tell this obj it's picked (for highlighting), which might affect how the main draw happens.
            # or, just store it so code knows it's there, and (later) overdraw it for highlighting.
            self.set_selobj( newpicked, "newpicked")
            ###e we'll probably need to notify some observers that selobj changed (if in fact it did). ###@@@
            ## env.history.statusbar_msg("%s" % newpicked) -- messed up by depmode "click to do x" msg
        
        # otherwise don't change prior selobj -- we have a separate system to set it back to None when needed
        # (which has to be implemented in the bareMotion routines of client modes -- would self.bareMotion be better? ###@@@ review)
        
        # draw according to mode
        glMatrixMode(GL_MODELVIEW) # this is assumed within Draw methods [bruce 050608 comment]
        self.mode.Draw()

        # highlight selobj if necessary -- we redraw it now (though it was part of
        # what was just drawn above) for two reasons:
        # - it might be in a display list in non-highlighted form (and if so, the above draw used that form);
        # - we need to draw it into the stencil buffer too, so mode.bareMotion can tell when mouse is still over it.
        if self.selobj is not None:
            # draw the selobj as highlighted, and make provisions for fast test
            # (by external code) of mouse still being over it (using stencil buffer)

            # note: if selobj highlight is partly translucent or transparent (neither yet supported),
            # we might need to draw it depth-sorted with other translucent objects
            # (now drawn by some modes using Draw_after_highlighting, not depth-sorted or modularly);
            # but our use of the stencil buffer assumes it's drawn at the end (except for objects which
            # don't obscure it for purposes of highlighting hit-test). This will need to be thought through
            # carefully if there can be several translucent objects (meant to be opaque re hit-tests),
            # and traslucent highlighting. See also the comment about highlight_into_depth, below. [bruce 060724 comment]

            # first gather info needed to know what to do -- highlight color (and whether to draw that at all)
            # and whether object might be bigger when highlighted (affects whether depth write is needed now).
            hicolor = self.selobj_hicolor( self.selobj) #bruce 050822 revised this; ###@@@ should record it from earlier test above
            # if that is None, should we act as if selobj is not still_ok?
            # guess: yes, but related code needs review.
            # I think I've now effectively implemented this separately, next to the still_ok test above.
            # [bruce 050822 comment]
            if hicolor is None:
                if platform.atom_debug:
                    print "atom_debug: probable bug: self.selobj_hicolor( self.selobj) is None for %r" % self.selobj #bruce 050822
            highlight_might_be_bigger = True # True is always ok; someday we might let some objects tell us this can be False

            # color-writing is needed here, iff the mode asked for it, for this selobj.
            highlight_into_color = (hicolor is not None)

            if highlight_into_color:
                # depth-writing is needed here, if highlight might be drawn in front of not-yet-drawn transparent surfaces
                # (like Build mode water surface) -- otherwise they will look like they're in front of some of the highlighting
                # even though they're not. (In principle, the preDraw_glselect_dict call above needs to know whether this depth
                # writing occurred ###doc why. Probably we should store it into the object itself... ###@@@ review, then doit )
                highlight_into_depth = highlight_might_be_bigger
            else:
                highlight_into_depth = False ###@@@ might also need to store 0 into obj...see discussion above

            if not highlight_into_depth:
                glDepthMask(GL_FALSE) # turn off depth writing (but not depth test)
            if not highlight_into_color:
                glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) # don't draw color pixels
                        
            # Note: stencil buffer was cleared earlier in this paintGL call.
            glStencilFunc(GL_ALWAYS, 1, 1)
                # These args make sure stencil test always passes, so color is drawn if we want it to be,
                # and so we can tell whether depth test passes in glStencilOp (even if depth *writing* is disabled ###untested);
                # this also sets reference value of 1 for use by GL_REPLACE.
                # (Args are: func to say when drawing-test passes; ref value; comparison mask.
                #  Warning: Passing -1 for reference value, to get all 1's, does not work -- it makes ref value 0!)
            glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
                # turn on stencil-buffer writing based on depth test
                # (args are: what to do on fail, zfail, zpass (see OpenGL "red book" p. 468))
            glEnable(GL_STENCIL_TEST)
                # this enables both aspects of the test: effect on drawing, and use of stencil op (I think #k);
                # apparently they can't be enabled separately
            ##print glGetIntegerv( GL_STENCIL_REF)
            
            # Now "translate the world" slightly closer to the screen,
            # to ensure depth test passes for appropriate parts of highlight-drawing
            # even if roundoff errors would make it unreliable to just let equal depths pass the test.
            # The amount of translation is a guess (ideally it should be just enough to achieve the mentioned purpose).
            # (Note: In principle, this motion towards the screen needs to be accounted for when testing depths in
            #  preDraw_glselect_dict (and we might want to store it on the object itself as a reliable record of whether
            #  it happened and for which object). In practice, as long as the stencil optim works, this isn't needed,
            #  and it's not yet implemented. This is predicted to result in highlight flickering if no stencil bits are
            #  available. ###e should fix sometime, if that ever happens.)
            
            glMatrixMode(GL_PROJECTION) # prepare to "translate the world"
            glPushMatrix() # could avoid using another matrix-stack-level if necessary, by untranslating when done
            glTranslatef(0.0, 0.0, +0.01) # move the world a bit towards the screen
                # (this works, but someday verify sign is correct in theory #k)
                # [actually it has some visual bugs, esp. in perspective view when off-center,
                #  and it would be better to just use a depth offset, or better still (probably)
                #  to change the depth test to LEQUAL, either just for now, or all the time. bruce 060729 comment]
            glMatrixMode(GL_MODELVIEW) # probably required!
            
            ####@@@@ TODO -- rename draw_in_abs_coords and make it imply highlighting so obj knows whether to get bigger
            # (note: having it always draw selatoms bigger, as if highlighted, as it does now, would probably be ok in hit-test,
            #  since false positives in hit test are ok, but this is not used in hit test; and it's probably wrong in depth-test
            #  of glselect_dict objs (where it *is* used), resulting in "premonition of bigger size" when hit test passed... ###bug);
            # make provisions elsewhere for objs "stuck as selobj" even if tests to retain that from stencil are not done
            # (and as optim, turn off stencil drawing then if you think it probably won't be needed after last draw you'll do)
            
            self.selobj.draw_in_abs_coords(self, hicolor or black) ###@@@ test having color writing disabled here, does stencil still happen??
            
            # restore gl state (but don't do unneeded OpenGL ops in case that speeds it up somehow)
            if not highlight_into_depth:
                glDepthMask(GL_TRUE)
            if not highlight_into_color:
                glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)                
            glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
                # no need to undo glStencilFunc state, I think -- whoever cares will set it up again
                # when they reenable stenciling.
            glDisable(GL_STENCIL_TEST)
            
            glMatrixMode(GL_PROJECTION)
            glPopMatrix()
            glMatrixMode(GL_MODELVIEW) #k maybe not needed

        self.mode.Draw_after_highlighting() # e.g. draws water surface in Build mode
            # note: this is called with the same coordinate system as mode.Draw() [bruce 061208 comment]

        ###@@@ move remaining items back into caller? sometimes yes sometimes no... need to make them more modular... [bruce 050617]
        
        # let parts (other than the main part) draw a text label, to warn
        # the user that the main part is not being shown [bruce 050408]
        try:
            self.part.draw_text_label(self)
        except:
            if platform.atom_debug:
                print_compact_traceback( "atom_debug: exception in self.part.draw_text_label(self): " )
            pass # if it happens at all, it'll happen too often to bother users with an error message
        
        # draw coordinate-orientation arrows at upper right corner of glpane
        if env.prefs[displayCompass_prefs_key]:
            self.drawcompass(aspect) #bruce 050608 moved this here, and rewrote it to behave then

        try:
            # kluge 061208 to let us draw things in the corners, to tide us over until we modularize the rendering alg as a whole
            from basic import reload_once
            import test
            reload_once(test)
            test.after_drawcompass(self, aspect)
        except:
            print_compact_traceback("bug: exception ignored in test.after_drawcompass: ")
        
        #ninad060921 The following draws a dotted origin axis if the correct preferece is checked. 
        #The GL_DEPTH_TEST is disabled while drawing this so that if axis is below a model, 
        #it will just draw it as dotted line (Remember that we are drawing 2 origins superimposed over each other
        #the dotted will be displayed only when the solid origin is obsucured by a model in front of it. 
        if env.prefs[displayOriginAxis_prefs_key]:
            if env.prefs[displayOriginAsSmallAxis_prefs_key]:
                drawer.drawOriginAsSmallAxis(self.scale, (0.0,0.0,0.0), dashEnabled = True)
            else:
                drawer.drawaxes(self.scale, (0.0,0.0,0.0), coloraxes=True, dashEnabled = True)

        glMatrixMode(GL_MODELVIEW) #bruce 050707 precaution in case drawing code outside of paintGL forgets to do this
            # (see discussion in bug 727, which was caused by that)
            # (it might also be good to set mode-specific standard GL state before checking self.redrawGL in paintGL #e)

        return # from standard_repaint_0 (which is the central submethod of paintGL)
    
    def selobj_hicolor(self, obj): #bruce 050822 split this out
        """If obj was to be highlighted as selobj (whether or not it's presently self.selobj),
        what would its highlight color be?
        Or return None if obj should not be allowed as selobj.
        """
        try:
            hicolor = self.mode.selobj_highlight_color( obj) #e should implem noop version in basicMode [or maybe i did]
            # mode can decide whether selobj should be highlighted (return None if not), and if so, in what color
        except:
            if platform.atom_debug:
                print_compact_traceback("atom_debug: selobj_highlight_color exception for %r: " % obj)
            hicolor = None #bruce 050822 changed this from LEDon to None
        return hicolor
    
    def set_selobj(self, selobj, why = "why?"):
        if selobj is not self.selobj:
            if debug_set_selobj:
                print_compact_stack("debug_set_selobj: %r -> %r: " % (self.selobj, selobj))
            #bruce 050702 partly address bug 715-3 (the presently-broken Build mode statusbar messages).
            # Temporary fix, since Build mode's messages are better and should be restored.
            if selobj is not None:
                try:
                    try:
                        #bruce 050806 let selobj control this
                        method = selobj.mouseover_statusbar_message # only defined for atoms, for now
                    except AttributeError:
                        msg = "%s" % (selobj,)
                    else:
                        msg = method()
                except:
                    msg = "<exception in selobj statusbar message code>"
            else:
                msg = " "
            env.history.statusbar_msg(msg)
        self.delegate.selobj = selobj
        #e notify some observers?
        return

    def preDraw_glselect_dict(self): #bruce 050609
        # We need to draw glselect_dict objects separately, so their drawing code runs now rather than in the past
        # (when some display list was being compiled), so they can notice they're in that dict.
        # We also draw them first, so that the nearest one (or one of them, if there's a tie)
        # is sure to update the depth buffer. (Then we clear it so that this drawing doesn't mess up
        # later drawing at the same depth.)
        # (If some mode with special drawing code wants to join this system, it should be refactored
        #  to store special nodes in the model which can be drawn in the standard way.)
        glMatrixMode(GL_MODELVIEW)
        glColorMask(GL_FALSE,GL_FALSE,GL_FALSE,GL_FALSE) # optimization -- don't draw color pixels (depth is all we need)
        newpicked = None # in case of errors, and to record found object
        # here we should sort the objs to check the ones we most want first (esp selobj)...
        #bruce 050702 try sorting this, see if it helps pick bonds rather than invis selatoms -- it seems to help.
        # This removes a bad side effect of today's earlier fix of bug 715-1.
        objects = self.glselect_dict.values()
        items = [] # (order, obj) pairs, for sorting objects
        for obj in objects:
            if obj is self.selobj:
                order = 0
            elif obj.__class__ is Bond:
                order = 1
            else:
                order = 2
            items.append((order, obj))
        items.sort()
        for orderjunk, obj in items:
            try:
                method = obj.draw_in_abs_coords
            except AttributeError:
                print "bug? ignored: %r has no draw_in_abs_coords method" % (obj,)
                print "   items are:", items
            else:
                try:
                    method(self, white) # draw depth info (color doesn't matter since we're not drawing pixels)
                        #bruce 050822 changed black to white in case some draw methods have boolean-test bugs for black (unlikely)
                        ###@@@ in principle, this needs bugfixes; in practice the bugs are tolerable in the short term
                        # (see longer discussion in other comments):
                        # - if no one reaches target depth, or more than one does, be smarter about what to do?
                        # - try current selobj first [this is done, as of 050702],
                        #   or give it priority in comparison - if it passes be sure to pick it
                        # - be sure to draw each obj in same way it was last drawn, esp if highlighted:
                        #    maybe drawn bigger (selatom)
                        #    moved towards screen
                    newpicked = self.check_target_depth( obj)
                        # returns obj or None -- not sure if that should be guaranteed [bruce 050822 comment]
                    if newpicked is not None:
                        break
                except:
                    print_compact_traceback("exception in %r.draw_in_abs_coords ignored: " % (obj,))
        ##e should check depth here to make sure it's near enough but not too near
        # (if too near, it means objects moved, and we should cancel this pick)
        glClear(GL_DEPTH_BUFFER_BIT) # prevent those predraws from messing up the subsequent main draws
        glColorMask(GL_TRUE,GL_TRUE,GL_TRUE,GL_TRUE)
        self.glselect_dict.clear() #k needed? even if not, seems safer this way.
            # do this now to avoid confusing the main draw methods,
            # in case they check this dict to decide whether they're
            # being called by draw_in_abs_coords
            # [which would be deprecated! but would work, not counting display lists.]
        #bruce 050822 new feature: objects which had no highlight color should not be allowed in self.selobj
        # (to make sure they can't be operated on without user intending this),
        # though they should still obscure other objects.
        if newpicked is not None:
            hicolor = self.selobj_hicolor( newpicked)
            if hicolor is None:
                newpicked = None
                # [note: there are one or two other checks of the same thing,
                #  e.g. to cover preexisting selobjs whose hicolor might have changed [bruce 060726 comment]]
        else:
            #bruce 060217 debug code re bug 1527. Not sure only happens on a bug, so using atom_debug.
            # (But I couldn't yet cause this to be printed while testing that bug.)
            #bruce 060224 disabling it since it's happening all the time when hover-highlighting in Build
            # (though I didn't reanalyze my reasons for thinking it might be a bug, so I don't know if it's a real one or not).
            if 0 and platform.atom_debug:
                print "atom_debug: newpicked is None -- bug? items are:", items
        return newpicked # might be None in case of errors (or if selobj_hicolor returns None)

    def check_target_depth(self, candidate): #bruce 050609; tolerance revised 050702
        """[private helper method]
           WARNING: docstring is obsolete -- no newpicked anymore, retval details differ: ###@@@
        Candidate is an object which drew at the mouse position during GL_SELECT drawing mode
        (using the given gl_select name), and which (1) has now noticed this, via its entry in self.glselect_dict
        (which was made when GL_SELECT mode was exited; as of 050609 this is in the same paintGL call as we're in now),
        and (2) has already drawn into the depth buffer during normal rendering (or an earlier rendering pass).
        (It doesn't matter whether it's already drawn into the color buffer when it calls this method.)
           We should read pixels from the depth buffer (after glFlush)
        to check whether it has just reached self.targetdepth at the appropriate point,
        which would mean candidate is the actual newly picked object.
           If so, record this fact and return True, else return False.
        We might quickly return False (checking nothing) if we already returned True in the same pass,
        or we might read pixels anyway for debugging or assertions.
           It's possible to read a depth even nearer than targetdepth, if the drawing passes round
        their coordinates differently (as the use of gluPickMatrix for GL_SELECT is likely to do),
        or if events between the initial targetdepth measurement and this redraw tell any model objects to move.
        Someday we should check for this.
        """
        glFlush()
        wX, wY = self.wX, self.wY
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        newdepth = wZ[0][0]
        targetdepth = self.targetdepth
        ####@@@@ here we could effectively move selobj forwards... warning: worry about scales of coord systems in doing that...
        # due to that issue it is probably be easier to fix this when drawing it, instead
        if newdepth <= targetdepth + 0.0001: # use fudge factor in case of roundoff errors
            # [bruce 050702: 0.000001 was not enough! 0.00003 or more was needed, to properly highlight some bonds
            #  which became too hard to highlight after today's initial fix of bug 715-1.]
            #e could check for newdepth being < targetdepth - 0.002 (error), but best
            # to just let caller do that (NIM), since we would often not catch this error anyway,
            # since we're turning into noop on first success
            # (no choice unless we re-cleared depth buffer now, which btw we could do... #e).
            ## print "target depth reached by",candidate,newdepth , targetdepth
            return candidate
                # caller should not call us again without clearing depth buffer,
                # otherwise we'll keep returning every object even if its true depth is too high
        ## print "target depth NOT reached by",candidate,newdepth , targetdepth
        return None

    def _setup_modelview(self, vdist): #bruce 050608 split this out; 050615 added explanatory comments
        "set up modelview coordinate system"
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glTranslatef( 0.0, 0.0, - vdist)
            # [bruce comment 050615]
            # translate coords for drawing, away from eye (through screen and beyond it) by vdist;
            # this places origin at desired position in eyespace for "center of view" (and for center of trackball rotation).
            
            # bruce 041214 comment: some code assumes vdist is always 6.0 * self.scale
            # (e.g. eyeball computations, see bug 30), thus has bugs for aspect < 1.0.
            # We should have glpane attrs for aspect, w_scale, h_scale, eyeball,
            # clipping planes, etc, like we do now for right, up, etc. ###e

        q = self.quat 
        glRotatef( q.angle*180.0/pi, q.x, q.y, q.z) # rotate those coords by the trackball quat
        glTranslatef( self.pov[0], self.pov[1], self.pov[2]) # and translate them by -cov, to bring cov (center of view) to origin
        return

    def _setup_projection(self, aspect, vdist, glselect = False): #bruce 050608 split this out; 050615 revised docstring
        """Set up standard projection matrix contents using aspect, vdist, and some attributes of self.
        (Warning: leaves matrixmode as GL_PROJECTION.)
        Optional arg glselect should be False (default) or a 4-tuple (to prepare for GL_SELECT picking).
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scale = self.scale * self.zoomFactor #bruce 050608 used this to clarify following code
        near, far = self.near, self.far

        if glselect:
            x,y,w,h = glselect
            gluPickMatrix(
                    x,y,
                    w,h,
                    glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
            )
         
        if self.ortho:
            glOrtho( - scale * aspect, scale * aspect,
                     - scale,          scale,
                       vdist * near, vdist * far )
        else:
            glFrustum( - scale * near * aspect, scale * near * aspect,
                       - scale * near,          scale * near,
                         vdist * near, vdist * far)
        return

    def drawcompass(self, aspect):
        """Draw the "compass" (the perpendicular colored arrows showing orientation of model coordinates)
        in a corner of the GLPane specified by preference variables.
        No longer assumes a specific glMatrixMode, but sets it to GL_MODELVIEW on exit.
        No longer trashes either matrix, but does require enough GL_PROJECTION stack depth
        to do glPushMatrix on it (though the guaranteed depth for that stack is only 2).
        """
        #bruce 050608 improved behavior re GL state requirements and side effects; 050707 revised docstring accordingly.
        #mark 0510230 switched Y and Z colors.  Now X = red, Y = green, Z = blue, standard in all CAD programs.
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity() #k needed?
        
        # Set compass position using glOrtho
        if self.compassPosition == UPPER_RIGHT:
            ### glOrtho(-50*aspect, 5.5*aspect, -50, 5.5,  -5, 500) # Upper Right
            # hack for use in testmode:
            glOrtho(-40*aspect, 15.5*aspect, -50, 5.5,  -5, 500)
        elif self.compassPosition == UPPER_LEFT:
            glOrtho(-5*aspect, 50.5*aspect, -50, 5.5,  -5, 500) # Upper Left
        elif self.compassPosition == LOWER_LEFT:
            glOrtho(-5*aspect, 50.5*aspect, -5, 50.5,  -5, 500) # Lower Left
        else:
            glOrtho(-50*aspect, 5.5*aspect, -5, 50.5,  -5, 500) # Lower Right
        
        q = self.quat
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glEnable(GL_COLOR_MATERIAL)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_CULL_FACE)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # X Arrow (Red)      
        glePolyCone([[-1,0,0], [0,0,0], [4,0,0], [3,0,0], [5,0,0], [6,0,0]],
                    [[0,0,0], [1,0,0], [1,0,0], [.5,0,0], [.5,0,0], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
        
        # Y Arrow (Green) 
        glePolyCone([[0,-1,0], [0,0,0], [0,4,0], [0,3,0], [0,5,0], [0,6,0]],
                    [[0,0,0], [0,.9,0], [0,.9,0], [0,.4,0], [0,.4,0], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
        
        # Z Arrow (Blue)
        glePolyCone([[0,0,-1], [0,0,0], [0,0,4], [0,0,3], [0,0,5], [0,0,6]],
                    [[0,0,0], [0,0,1], [0,0,1], [0,0,.4], [0,0,.4], [0,0,0]],
                    [.3,.3,.3,.75,0,0])
                    
        glEnable(GL_CULL_FACE)
        glDisable(GL_COLOR_MATERIAL)
           
        ##Adding "X, Y, Z" text labels for Axis. By test, the following code will get
        # segmentation fault on Mandrake Linux 10.0 with libqt3-3.2.3-17mdk
        # or other 3.2.* versions, but works with libqt3-3.3.3-26mdk. Huaicai 1/15/05

        if env.prefs[displayCompassLabels_prefs_key]: ###sys.platform in ['darwin', 'win32']:
                glDisable(GL_LIGHTING)
                glDisable(GL_DEPTH_TEST)
                ## glPushMatrix()
                font = QFont( QString("Helvetica"), 12)
                self.qglColor(QColor(200, 75, 75)) # Dark Red
                self.renderText(5.3, 0.0, 0.0, QString("x"), font)
                self.qglColor(QColor(25, 100, 25)) # Dark Green
                self.renderText(0.0, 4.8, 0.0, QString("y"), font)
                self.qglColor(QColor(50, 50, 200)) # Dark Blue
                self.renderText(0.0, 0.0, 5.0, QString("z"), font)
                ## glPopMatrix()
                glEnable(GL_DEPTH_TEST)
                glEnable(GL_LIGHTING)

        #bruce 050707 switched order to leave ending matrixmode in standard state, GL_MODELVIEW
        # (though it doesn't matter for present calling code; see discussion in bug 727)
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()
        return
    
    pass # end of class GLPane_overrider

# end

