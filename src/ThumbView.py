# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
ThumbView.py

$Id$
'''

from qtgl import *
from OpenGL.GL import *
from OpenGL.GLU import *
from VQT import *
import drawer
from constants import *
from assembly import assembly 
import env

# debugging flags -- do not commit with True
debug_thumbview = False

class ThumbView(QGLWidget):
    """A simple version of OpenGL widget, which can be used to show a simple thumb view of models when loading models or color changing. 
    General rules for multiple QGLWidget uses: make sure the rendering context is current. 
    Remember makeCurrent() will be called implicitly before any ininializeGL, resizeGL, paintGL virtual functions call. Ideally, this class should coordinate with class GLPane in some ways.
    """
    shareWidget = None #bruce 051212
    always_draw_hotspot = False #bruce 060627
    def __init__(self, parent, name, shareWidget):
        """  """
        if shareWidget:
            self.shareWidget = shareWidget #bruce 051212
            format = shareWidget.format()
            QGLWidget.__init__(self, format, parent, name, shareWidget)
            if not self.isSharing():
                print "Request of display list sharing is failed."
                return
        else:  
            QGLWidget.__init__(self, parent, name)  
        
        # point of view, and half-height of window in Angstroms
        self.pov = V(0.0, 0.0, 0.0)
        self.scale = 10.0
        self.quat = Q(1, 0, 0, 0)
        self.trackball = Trackball(10,10)
        self.picking = 0

        self.glselectBufferSize = 500  
        self.selectedObj = None
        
        #This enables the mouse bareMotion() event
        self.setMouseTracking(True)
        
        # clipping planes, as percentage of distance from the eye
        self.near = 0.66
        self.far = 2.0  
        # start in perspective mode
        self.ortho = False #True
        self.initialised = False
        
        # default color and gradient values.
        self.backgroundColor = gray
        self.backgroundGradient = 1 # SkyBlue

    
    def drawModel(self):
        """This is an abstract method of drawing models, subclass should overwrite it with concrete model drawing statements """        
        pass
    
    def drawSelected(self, obj):
        '''Draw the selected object. Subclass need to override it'''
        pass
    
    def _setup_lighting(self): # as of bruce 060415, this is mostly duplicated between GLPane (has comments) and ThumbView ###@@@
        """[private method]
        Set up lighting in the model.
        [Called from both initializeGL and paintGL.]
        """
        glEnable(GL_NORMALIZE)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        #bruce 060415 moved following from ThumbView.initializeGL to this split-out method...
        #bruce 051212 revised lighting code to share prefs and common code with GLPane
        # (to fix bug 1200 and mitigate bugs 475 and 1158;
        #  fully fixing those would require updating lighting in all ThumbView widgets
        #  whenever lighting prefs change, including making .update calls on them,
        #  and is not planned for near future since it's easy enough to close & reopen them)
        try:
            lights = self.shareWidget._lights #bruce 060415 shareWidget --> self.shareWidget; presumably always failed before that
                ####@@@@ will this fix some bugs about common lighting prefs??
        except:
            lights = drawer._default_lights
        
        drawer.setup_standard_lights( lights)
        return
    
    def initializeGL(self):
        self._setup_lighting()

        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if not self.isSharing():
            drawer.setup()  
        return
    
    def resetView(self):
        '''Subclass can override this method with different <scale>, so call this version in the overridden
           version. '''
        self.pov = V(0.0, 0.0, 0.0)
        self.quat = Q(1, 0, 0, 0)
        
    def setBackgroundColor(self, color, gradient):
        '''Set the background  to 'color' or 'gradient' (Sky Blue).
        '''
        self.backgroundColor = color
        
        # Ninad and I discussed this and decided that the background should always be set to skyblue.
        # This issue has to do with Build mode's water surface introducing inconsistencies 
        # with the thumbview background color whenever Build mode's bg color is solid.
        # Change to "if 0:" to have the thubview background match the current mode background.
        # This fixes bug 1229.  Mark 060116
        if 1:
            self.backgroundGradient = 1 
        else:
            self.backgroundGradient = gradient
                
    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
           
        glViewport(0, 0, self.width, self.height)
        
        self.trackball.rescale(width, height)
        
        if not self.initialised:
            self.initialised = True


    def _setup_projection(self, glselect = False): #bruce 050608 split this out; 050615 revised docstring
        """Set up standard projection matrix contents using aspect, vdist, and some attributes of self.
        (Warning: leaves matrixmode as GL_PROJECTION.)
        Optional arg glselect should be False (default) or a 4-tuple (to prepare for GL_SELECT picking).
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scale = self.scale #bruce 050608 used this to clarify following code
        near, far = self.near, self.far

        if glselect:
            x,y,w,h = glselect
            gluPickMatrix(
                    x,y,
                    w,h,
                    glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
            )
         
        if self.ortho:
            glOrtho( - scale * self.aspect, scale * self.aspect,
                     - scale,          scale,
                       self.vdist * near, self.vdist * far )
        else:
            glFrustum( - scale * near * self.aspect, scale * near * self.aspect,
                       - scale * near,          scale * near,
                         self.vdist * near, self.vdist * far)
        return
    
    
    def paintGL(self):        
        """Called by QtGL when redrawing is needed.
            For every redraw, color & depth butter are cleared, view projection are reset, view location & orientation are also reset. 
        """
        if not self.initialised: return

        from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False
        if debug_pref("always setup_lighting?", Choice_boolean_False):
            #bruce 060415 added debug_pref("always setup_lighting?"), in GLPane and ThumbView [KEEP DFLTS THE SAME!!];
            # see comments in GLPane
            self._setup_lighting() #bruce 060415 added this call
        
        c=self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        if self.backgroundGradient:
            vtColors = (bluesky) # "Blue Sky" gradient
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            drawer.drawFullWindow(vtColors)
        
        self.aspect = (self.width + 0.0)/(self.height + 0.0)
        self.vdist = 6.0 * self.scale
        self._setup_projection()
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()    
        glTranslatef(0.0, 0.0, -self.vdist)
       
        q = self.quat
        
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glTranslatef(self.pov[0], self.pov[1], self.pov[2])
        
        self.drawModel()
   
    
    def __getattr__(self, name): # in class ThumbView
        if name == 'lineOfSight':
            return self.quat.unrot(V(0,0,-1))
        elif name == 'right':
            return self.quat.unrot(V(1,0,0))
        elif name == 'left':
            return self.quat.unrot(V(-1,0,0))
        elif name == 'up':
            return self.quat.unrot(V(0,1,0))
        elif name == 'down':
            return self.quat.unrot(V(0,-1,0))
        elif name == 'out':
            return self.quat.unrot(V(0,0,1))
        else:
            raise AttributeError, 'ThumbView has no "%s"' % name #bruce 060209 revised text
    
        
   
    def mousePressEvent(self, event):
        """Dispatches mouse press events depending on shift and
        control key state.
        """
        ## Huaicai 2/25/05. This is to fix item 2 of bug 400: make this rendering context
        ## as current, otherwise, the first event will get wrong coordinates
        self.makeCurrent()
        
        but = event.stateAfter()
        #print "Button pressed: ", but

        if 1:
            #bruce 060328 kluge fix of undo part of bug 1775 (overkill, but should be ok) (part 1 of 2)
            import undo_manager
            main_assy = env.mainwindow().assy
            self.__begin_retval = undo_manager.external_begin_cmd_checkpoint(main_assy, cmdname = "(mmkit)")
        
        if but & leftButton:
            if but & shiftButton:
                pass#self.mode.leftShiftDown(event)
            elif but & cntlButton:
                pass#self.mode.leftCntlDown(event)
            else:
                self.leftDown(event)

        if but & midButton:
            if but & shiftButton:
                pass#self.mode.middleShiftDown(event)
            elif but & cntlButton:
                pass#self.mode.middleCntlDown(event)
            else:
                self.middleDown(event)

        if but & rightButton:
            if but & shiftButton:
                pass#self.mode.rightShiftDown(event)
            elif but & cntlButton:
                pass#self.mode.rightCntlDown(event)
            else:
                pass#self.rightDown(event)         

    __begin_retval = None
    
    def mouseReleaseEvent(self, event):
        """Only used to detect the end of a freehand selection curve.
        """
        but = event.state()
        
        #print "Button released: ", but
        
        if but & leftButton:
            if but & shiftButton:
                pass#self.leftShiftUp(event)
            elif but & cntlButton:
                pass#self.leftCntlUp(event)
            else:
                self.leftUp(event)

        if but & midButton:
            if but & shiftButton:
                pass#self.mode.middleShiftUp(event)
            elif but & cntlButton:
                pass#self.mode.middleCntlUp(event)
            else:
                self.middleUp(event)

        if but & rightButton:
            if but & shiftButton:
                 pass#self.rightShiftUp(event)
            elif but & cntlButton:
                pass#self.rightCntlUp(event)
            else:
                pass#self.rightUp(event)

        if 1:
            #bruce 060328 kluge fix of undo part of bug 1775 (part 2 of 2)
            import undo_manager
            main_assy = env.mainwindow().assy
            undo_manager.external_end_cmd_checkpoint(main_assy, self.__begin_retval)

        return

    def mouseMoveEvent(self, event):
        """Dispatches mouse motion events depending on shift and
        control key state.
        """
        ##self.debug_event(event, 'mouseMoveEvent')
        but = event.state()
        
        if but & leftButton:
            if but & shiftButton:
                pass#self.leftShiftDrag(event)
            elif but & cntlButton:
                pass#self.leftCntlDrag(event)
            else:
                pass#self.leftDrag(event)

        elif but & midButton:
            if but & shiftButton:
                pass#self.middleShiftDrag(event)
            elif but & cntlButton:
                pass#self.middleCntlDrag(event)
            else:
                self.middleDrag(event)

        elif but & rightButton:
            if but & shiftButton:
                pass#self.rightShiftDrag(event)
            elif but & cntlButton:
                pass#self.rightCntlDrag(event)
            else:
                pass#self.rightDrag(event)

        else:
            #Huaicai: To fix bugs related to multiple rendering contexts existed in our application.
            # See comments in mousePressEvent() for more detail.
            self.makeCurrent()
            
            self.bareMotion(event)


    def wheelEvent(self, event):
        but = event.state()
        
        dScale = 1.0/1200.0
        if but & shiftButton: dScale *= 0.5
        if but & cntlButton: dScale *= 2.0
        self.scale *= 1.0 + dScale * event.delta()

        ##: The scale variable needs to set a limit, otherwise, it will set self.near = self.far = 0.0
        ##  because of machine precision, which will cause OpenGL Error. Huaicai 10/18/04
        self.updateGL()


    def bareMotion(self, event):
        wX = event.pos().x()
        wY = self.height - event.pos().y()
        
        if self.selectedObj is not None:
            stencilbit = glReadPixelsi(wX, wY, 1, 1, GL_STENCIL_INDEX)[0][0]
            if stencilbit: # If it's the same highlighting object, no disply change needed.
                return   
        
        self.updateGL()
        
        self.selectedObj = self.select(wX, wY)
        self.highlightSelected(self.selectedObj)
   
        
    def leftDown(self, event):
        pass


    def leftUp(self, event):
        pass

    
    def middleDown(self, event):
        pos = event.pos()
        self.trackball.start(pos.x(), pos.y())
        self.picking = 1
        

    def middleDrag(self, event):
        if not self.picking: return
        
        pos = event.pos()
        q = self.trackball.update(pos.x(), pos.y())
        self.quat += q
        self.updateGL()
    
    
    def middleUp(self, event):
        self.picking = 0
        
        
    def select(self, wX, wY):
        """Use the OpenGL picking/selection to select any object. Return the selected object, 
           otherwise, return None. Restore projection and model/view matrices before returning.
        """
        ####@@@@ WARNING: The original code for this, in GLPane, has been duplicated and slightly modified
        # in at least three other places (search for glRenderMode to find them). This is bad; common code
        # should be used. Furthermore, I suspect it's sometimes needlessly called more than once per frame;
        # that should be fixed too. [bruce 060721 comment]
        wZ = glReadPixelsf(wX, wY, 1, 1, GL_DEPTH_COMPONENT)
        gz = wZ[0][0]
        
        if gz >= GL_FAR_Z: ##Empty space was clicked
            return None
        
        pxyz = A(gluUnProject(wX, wY, gz))
        pn = self.out
        pxyz -= 0.0002*pn
        dp = - dot(pxyz, pn)
        
        #Save projection matrix before it's changed.
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        
        current_glselect = (wX,wY,1,1) 
        self._setup_projection(glselect = current_glselect) 
        
        glSelectBuffer(self.glselectBufferSize)
        glRenderMode(GL_SELECT)
        glInitNames()
        glMatrixMode(GL_MODELVIEW)
        # Save model view matrix before it's changed.
        glPushMatrix()
        try:
            glClipPlane(GL_CLIP_PLANE0, (pn[0], pn[1], pn[2], dp))
            glEnable(GL_CLIP_PLANE0)
            self.drawModel()
            glDisable(GL_CLIP_PLANE0)
        except:
            print_compact_traceback("exception in mode.Draw() during GL_SELECT; ignored; restoring modelview matrix: ")
            glPopMatrix()
            glRenderMode(GL_RENDER)
            return None
        else:
            # Restore model/view matrix
            glPopMatrix()
        
        #Restore project matrix and set matrix mode to Model/View
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        
        glFlush()
        
        hit_records = list(glRenderMode(GL_RENDER))
        if platform.atom_debug and 0:
            print "%d hits" % len(hit_records)
        for (near,far,names) in hit_records: # see example code, renderpass.py
            if platform.atom_debug and 0:
                print "hit record: near,far,names:",near,far,names
                # e.g. hit record: near,far,names: 1439181696 1453030144 (1638426L,)
                # which proves that near/far are too far apart to give actual depth,
                # in spite of the 1-pixel drawing window (presumably they're vertices
                # taken from unclipped primitives, not clipped ones).
            if names:
                obj = env.obj_with_glselect_name.get(names[-1]) #k should always return an obj
                return obj 
        return None # from ThumbView.select


    def highlightSelected(self, obj):
        '''Hight the selected object <obj>. In the mean time, we do stencil test to 
           update stencil buffer, so it can be used to quickly test if pick is still
           on the same <obj> as last test. '''
        
        if not obj: return
        if not isinstance(obj, atom) or (obj.element is not Singlet): return

        self._preHighlight()
        
        self.drawSelected(obj)
            
        self._endHightlight()
        
        glFlush()
        self.swapBuffers()


    def _preHighlight(self):
        '''Before highlight, clear stencil buffer, depth writing and some stencil test settings. '''       
        self.makeCurrent()
        glClear(GL_STENCIL_BUFFER_BIT)
        
        glDepthMask(GL_FALSE) # turn off depth writing (but not depth test)
        #glDisable(GL_DEPTH_TEST)
        glStencilFunc(GL_ALWAYS, 1, 1)
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE)
        glEnable(GL_STENCIL_TEST)
        
        glMatrixMode(GL_PROJECTION) # prepare to "translate the world"
        glPushMatrix() # could avoid using another matrix-stack-level if necessary, by untranslating when done
        glTranslatef(0.0, 0.0, +0.01) # move the world a bit towards the screen
            # (this works, but someday verify sign is correct in theory #k)
        glMatrixMode(GL_MODELVIEW) 
   
        
    def _endHightlight(self):
        '''Turn on depth writing, disable stencil test '''
        glDepthMask(GL_TRUE)
        #glEnable(GL_DEPTH_TEST)
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)
        glDisable(GL_STENCIL_TEST)
        
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)

    def saveLastView(self): #bruce 060627 for compatibility with GLPane (for sake of assy.update_parts)
        pass

    def forget_part(self, part): #bruce 060627 for compatibility with GLPane (for sake of chunk.kill)
        pass

    pass # end of class ThumbView
    
# ==

from chem import atom, Singlet
from chunk import molecule

class ElementView(ThumbView):
    """Element graphical display """    
    def __init__(self, parent, name, shareWidget = None):
        ThumbView.__init__(self, parent, name, shareWidget)
        self.scale = 2.0#5.0 ## the possible largest rvdw of all elements
        self.pos = V(0.0, 0.0, 0.0)
        self.mol = None
        
        ## Dummy attributes. A kludge, just try to make other code
        ##  think it looks like a glpane object.
        self.displayMode = 0  
        self.selatom = None
    
    def resetView(self, scale = 2.0):
        '''Reset current view'''
        ThumbView.resetView(self)
        self.scale = scale
        
    def drawModel(self):
        """The method for element drawing """
        if self.mol:
           self.mol.draw(self, None)

    def refreshDisplay(self, elm, dispMode = diTrueCPK):
        """Display the new element or the same element but new display mode"""   
        self.makeCurrent()
        self.mol = self.constructModel(elm, self.pos, dispMode) 
        self.updateGL()
    
    def updateColorDisplay(self, elm, dispMode = diTrueCPK):
        """Display the new element or the same element but new display mode"""   
        self.makeCurrent()
        self.mol = self.constructModel(elm, self.pos, dispMode) 
        self.updateGL()
    
    
    def constructModel(self, elm, pos, dispMode):
        """This is to try to repeat what 'oneUnbonded()' function does,
        but hope to remove some stuff not needed here.
        The main purpose is to build the geometry model for element display. 
        <Param> elm: An object of class Elem
        <Param> dispMode: the display mode of the atom--(int)
        <Return>: the molecule which contains the geometry model.
        """
        class DummyAssy:
            """dummy assemby class"""
            drawLevel = 2
            
        if 0:#1:
            assy = DummyAssy()
        else:
            from assembly import assembly 
            assy = assembly(None)
            assy.o = self
                
        mol = molecule(assy, 'dummy') 
        atm = atom(elm.symbol, pos, mol)
        atm.display = dispMode
        ## bruce 050510 comment: this is approximately how you should change the atom type (e.g. to sp2) for this new atom:
        ## atm.set_atomtype_but_dont_revise_singlets('sp2')
        ## see also atm.element.atomtypes -> a list of available atomtype objects for that element
        ## (which can be passed to set_atomtype_but_dont_revise_singlets)
        atm.make_singlets_when_no_bonds()
        return mol
    
    def drawSelected(self, obj):
        '''Override the parent version. Specific drawing code for the object. '''
        if isinstance(obj, atom) and (obj.element is Singlet):
            obj.draw_in_abs_coords(self, env.prefs[bondpointHighlightColor_prefs_key])

    pass # end of class ElementView

class MMKitView(ThumbView):
    '''Currently used as the GLWidget for the graphical display and manipulation for element/clipboard/part.
       Initial attempt was to subclass this for each of above type models, but find trouble to dynamically
       change the GLWidget when changing tab page. '''

    always_draw_hotspot = True
        #bruce 060627 to help with bug 2028
        # (replaces a horribe kluge in old code which broke a fix to that bug)

    def __init__(self, parent, name, shareWidget = None):
        ThumbView.__init__(self, parent, name, shareWidget)
        self.scale = 2.0
        self.pos = V(0.0, 0.0, 0.0)
        self.model = None
        
        ## Dummy attributes. A kludge, just try to make other code
        ##  think it looks like a glpane object.
        self.displayMode = 0  
        self.selatom = None
        self.special_topnode = None

        self.hotspotAtom = None #The current hotspot singlet for the part
        self.lastHotspotChunk = None # The previous chunk of the hotspot for the part
        
        hybrid_type_name = None
        elementMode = True  #Used to differentiate elment page versus clipboard/part page
    
        
    def drawModel(self):
        """The method for element drawing """
        if debug_thumbview:
            print "debug: MMKitView.drawModel, model is %r" % (self.model,) #bruce 060412
        if self.model:
           if isinstance(self.model, molecule):
               self.model.draw(self, None)
           else: ## assembly
               self.model.draw(self)

   
    def refreshDisplay(self, elm, dispMode = diTrueCPK):
        """Display the new element or the same element but new display mode"""   
        self.makeCurrent()
        self.model = self.constructModel(elm, self.pos, dispMode)
        self.updateGL()
        

    def changeHybridType(self, name):
        self.hybrid_type_name = name
    
    
    def resetView(self):
        '''Reset current view'''
        ThumbView.resetView(self)
        self.scale = 2.0
    
    
    def drawSelected(self, obj):
        '''Override the parent version. Specific drawing code for the object. '''
        if isinstance(obj, atom) and (obj.element is Singlet):
            obj.draw_in_abs_coords(self, env.prefs[bondpointHighlightColor_prefs_key])

            
    def constructModel(self, elm, pos, dispMode):
        """This is to try to repeat what 'oneUnbonded()' function does,
        but hope to remove some stuff not needed here.
        The main purpose is to build the geometry model for element display. 
        <Param> elm: An object of class Elem
        <Param> dispMode: the display mode of the atom--(int)
        <Return>: the molecule which contains the geometry model.
        """
        class DummyAssy:
            """dummy assemby class"""
            drawLevel = 2
            
        if 0:#1:
            assy = DummyAssy()
        else:
            assy = assembly(None)
            assy.o = self
                
        mol = molecule(assy, 'dummy') 
        atm = atom(elm.symbol, pos, mol)
        atm.display = dispMode
        ## bruce 050510 comment: this is approximately how you should change the atom type (e.g. to sp2) for this new atom:
        if self.hybrid_type_name:
            atm.set_atomtype_but_dont_revise_singlets(self.hybrid_type_name)
        ## see also atm.element.atomtypes -> a list of available atomtype objects for that element
        ## (which can be passed to set_atomtype_but_dont_revise_singlets)
        atm.make_singlets_when_no_bonds()
        
        self.elementMode = True
        
        return mol
    

    def leftDown(self, event):
        '''When in clipboard mode, set hotspot if a Singlet is highlighted. '''
        if self.elementMode: return
        
        obj = self.selectedObj
        if isinstance(obj, atom) and (obj.element is Singlet):
            mol = obj.molecule
            if not mol is self.lastHotspotChunk:
                if self.lastHotspotChunk: # Unset previous hotspot [bruce 060629 fix bug 1974 -- only if in same part]
                    if mol.part is self.lastHotspotChunk.part and mol.part is not None:
                        # Old and new hotspot chunks are in same part. Unset old hotspot,
                        # so as to encourage there to be only one per Part.
                        #   This should happen when you try to make more than one hotspot in one
                        # library part or clipboard item, using the MMKit to make both.
                        #   It might make more sense for more general code in Part to prevent
                        # more than one hotspot per part... but we have never decided whether
                        # that would be a good feature. (I have long suspected that hotspots
                        # should be replaced by some sort of jig, to give more control....)
                        #   I don't know if this case can ever happen as of now, since multichunk
                        # clipboard items aren't shown in MMKit -- whether it can happen now
                        # depends on whether any multichunk library parts have bondpoints on
                        # more than one chunk. [bruce 060629]
                        if env.debug() and self.lastHotspotChunk.hotspot: #bruce 060629 re bug 1974
                            print "debug: unsetting hotspot of %r (was %r)" % \
                                  (self.lastHotspotChunk, self.lastHotspotChunk.hotspot)
                        self.lastHotspotChunk.set_hotspot(None)
                    else:
                        # Don't unset hotspot in this case (doing so was causing bug 1974).
                        if env.debug() and self.lastHotspotChunk.hotspot:
                            print "debug: NOT unsetting hotspot of %r" % (self.lastHotspotChunk, )
                        pass
                self.lastHotspotChunk = mol
                    # [as of 060629, the only purpose of this is to permit the above code to unset it in some cases]
                       
            mol.set_hotspot(obj)

            if 1:
                #bruce 060328 fix gl_update part of bug 1775 (the code looks like that was a bug forever, don't know for sure)
                main_glpane = env.mainwindow().glpane
                if mol.part is main_glpane.part:
                    main_glpane.gl_update()
            
            self.hotspotAtom = obj
            self.updateGL()


    def updateModel(self, newObj):
        '''Set new chunk or assembly for display'''
        if debug_thumbview:
            print "debug: MMKitView.updateModel, __main__._newObj = %r" % (newObj,) #bruce 060412
            import __main__
            __main__._newObj = newObj
        self.model = newObj

        #Reset hotspot related stuff for a new assembly
        if isinstance(newObj, assembly):
            self.hotspotAtom = None
            self.lastHotspotChunk = None
        
        self._fitInWindow()
        self.elementMode = False
        self.updateGL()
    
    
    def setDisplay(self, mode):
        self.displayMode = mode
    
    
    def _fitInWindow(self):
        if not self.model: return
        
        self.quat = Q(1, 0, 0, 0)
        
        if isinstance(self.model, molecule):
            self.model._recompute_bbox()
            bbox = self.model.bbox
        else: ## assembly
            part = self.model.part
            bbox = part.bbox
        
        self.scale = bbox.scale() 
        aspect = float(self.width) / self.height
        if aspect < 1.0:
           self.scale /= aspect
        center = bbox.center()
        self.pov = V(-center[0], -center[1], -center[2])

    pass # end of class MMKitView
    
class ChunkView(ThumbView):
    """Chunk display.""" # Currently this is not used. [still true 060328 due to setup code in MMKit -- bruce comment]
    def __init__(self, parent, name, shareWidget = None):
        ThumbView.__init__(self, parent, name, shareWidget)
        #self.scale = 3.0#5.0 ## the possible largest rvdw of all elements
        self.quat = Q(1, 0, 0, 0)
        self.pos = V(0.0, 0.0, 0.0)
        self.mol = None
        
        ## Dummy attributes. A kludge, just try to make other code
        ##  think it looks like a glpane object.
        self.displayMode = 0  
    
    def resetView(self):
        '''Reset current view'''
        ThumbView.resetView(self)
        self.scale = 10.0
        
    def drawModel(self):
        """The method for element drawing """
        if self.mol:
           self.mol.draw(self, None)

    def updateModel(self, newChunk):
        '''Set new chunk for display'''
        self.mol = newChunk
        self.resetView()
        self.updateGL()
    
    def drawSelected(self, obj):
        '''Override the parent version. Specific drawing code for the object. '''
        if isinstance(obj, atom) and (obj.element is Singlet):
            obj.draw_in_abs_coords(self, env.prefs[bondpointHighlightColor_prefs_key])

    pass # end of class ChunkView

# end
