# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
ops_view.py provides viewSlotsMixin for MWsemantics,
with view slot methods and related helper methods.

$Id$

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

mark 060120 split this out of MWsemantics.py.

'''

from HistoryWidget import greenmsg, redmsg, orangemsg
from constants import *
from VQT import *

import preferences
import env

class viewSlotsMixin: #mark 060120 moved these methods out of class MWsemantics
    "Mixin class to provide view-related methods for class MWsemantics. Has slot methods and their helper methods."
    
    ###################################
    # View Toolbar Slots
    ###################################

    def setViewHome(self):
        """Reset view to Home view"""
        cmd = greenmsg("Current View: ")
        info = 'Home'
        env.history.message(cmd + info)
        self.glpane.setViewHome()

    def setViewFitToWindow(self):
        """ Fit to Window """
        cmd = greenmsg("Fit to Window: ")
        info = ''
        env.history.message(cmd + info)
        self.glpane.setViewFitToWindow()
            
    def setViewHomeToCurrent(self): #bruce 050418 revised docstring, and moved bodies of View methods into GLPane
        """Changes Home view of the model to the current view in the glpane."""
        cmd = greenmsg("Set Home View to Current View: ")
        info = 'Home'
        env.history.message(cmd + info)
        self.glpane.setViewHomeToCurrent()
            
    def setViewRecenter(self):
        """Recenter the view around the origin of modeling space.
        """
        cmd = greenmsg("Recenter View: ")
        info = 'View Recentered'
        env.history.message(cmd + info)
        self.glpane.setViewRecenter()
                
    def zoomTool(self, val):
        """Zoom Tool, allowing the user to specify a rectangular area 
        by holding down the left button and dragging the mouse to zoom 
        into a specific area of the model.
        val = True when Zoom tool button was toggled on, False when it
            it was toggled off.
        """

        # This fixes bug 1081.  mark 060111.
        if not val: # The Zoom button was toggled off.  Return to 'prevMode'.
            self.glpane.mode.Done()
            return
        
        self.save_current_mode_attrs()
        self.glpane.setMode('ZOOM')
        
        # This should be placed in zoomMode.Enter or init_gui, but it always appears 
        # before the green "Entering Mode: Zoom" msg.  So I put it here.  Mark 050130
        env.history.message("You may hit the Esc key to exit Zoom Tool.")

    def panTool(self, val):
        """Pan Tool allows X-Y panning using the left mouse button.
        val = True when Pan tool button was toggled on, False when it
            it was toggled off.
        """
        
        # This fixes bug 1081.  mark 060111.
        if not val: # The Pan button was toggled off.  Return to 'prevMode'.
            self.glpane.mode.Done()
            return
            
        self.save_current_mode_attrs()
        self.glpane.setMode('PAN')
        env.history.message("You may hit the Esc key to exit Pan Tool.")

    def rotateTool(self, val):
        """Rotate Tool allows free rotation using the left mouse button.
        val = True when Rotate tool button was toggled on, False when it
            it was toggled off.
        """
        
        # This fixes bug 1081.  mark 060111.
        if not val: # The Rotate button was toggled off.  Return to 'prevMode'.
            self.glpane.mode.Done()
            return
            
        self.save_current_mode_attrs()
        self.glpane.setMode('ROTATE')
        env.history.message("You may hit the Esc key to exit Rotate Tool.")
        
    def save_current_mode_attrs(self):
        '''Save some current mode attrs before entering Zoom, Pan or Rotate mode.
        '''
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode".
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeDisplay = self.glpane.display  # Added to fix bug 1489. mark 060215.
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient
                
    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.setViewProjection(ORTHOGRAPHIC)

    def setViewPerspec(self):
        self.glpane.setViewProjection(PERSPECTIVE)

    def setViewNormalTo(self): # 
        '''Set view to the normal vector of the plane defined by 3 or more
        selected atoms or a jig's (Motor or RectGadget) axis.
        '''
        cmd = greenmsg("Set View Normal To: ")
        
        chunks = self.assy.selmols
        jigs = self.assy.getSelectedJigs()
        atoms = self.assy.selatoms_list()
        
        if len(chunks) == 1 and len(atoms) == 0:
            # Even though chunks have an axis, it is not necessarily the same
            # axis attr stored in the chunk.  Get the chunks atoms and let
            # compute_heuristic_axis() recompute them.
            atoms = chunks[0].atoms.values()
        elif len(jigs) == 1 and len(atoms) == 0:
            # Warning: RectGadgets have no atoms.  We handle this special case below.
            atoms = jigs[0].atoms 
        elif len(atoms) < 3:
            # There is a problem when allowing only 2 selected atoms. 
            # Changing requirement to 3 atoms fixes bug 1418. mark 060322
            msg = redmsg("Please select some atoms, jigs, and/or chunks, covering at least 3 atoms")
            env.history.message(cmd + msg)
            return
        
        # This check is needed for jigs that have no atoms.  Currently, this 
        # is the case for RectGadgets (ESP Image and Grid Plane) only.
        if len(atoms):
            pos = A( map( lambda a: a.posn(), atoms ) )
            nears = [ self.glpane.out, self.glpane.up ]
            from geometry import compute_heuristic_axis
            axis = compute_heuristic_axis( pos, 'normal', already_centered = False, nears = nears, dflt = None )
        else: # We have a jig with no atoms.
            axis = jigs[0].getaxis() # Get the jig's axis.
            # If axis is pointing into the screen, negate (reverse) axis.
            if dot(axis, self.glpane.lineOfSight) > 0:
                axis = -axis

        if not axis:
            msg = orangemsg( "Warning: Normal axis could not be determined. No change in view." )
            env.history.message(cmd + msg)
            return
        
        # Compute the destination quat (q2).
        q2 = Q(V(0,0,1), axis)
        q2 = q2.conj()
        
        self.glpane.rotateView(q2)
        
        info = 'View set to normal vector of the plane defined by the selected atoms.'
        env.history.message(cmd + info)
        
    def setViewNormalTo_NEW(self):
        '''Set view to the normal vector of the plane defined by 3 or more
        selected atoms or a jig's (Motor or RectGadget) axis.
        '''
        # This implementation has two serious problems:
        #   1. it selects a normal based on the atoms and not the axis of a jig (e.g. a moved rotary motor).
        #   2. doesn't consider selected jigs that have no atoms.
        # Bruce and I will discuss this and determine the best implem.  
        # For A7, I've decide to use the original version. This version will be reinstated in A8
        # after fixing these problems. mark 060322.
        
        cmd = greenmsg("Set View Normal To: ")
        
        atoms = self.assy.getSelectedAtoms()
        
        if len(atoms) < 3:
            # There is a problem when allowing only 2 selected atoms.
            # Changing requirement to 3 atoms fixes bug 1418. mark 060322
            msg = redmsg("Please select some atoms, jigs, and/or chunks, covering at least 3 atoms")
            env.history.message(cmd + msg)
            return
        
        pos = A( map( lambda a: a.posn(), atoms ) ) # build list of atom xyz positions.
        nears = [ self.glpane.out, self.glpane.up ]
        from geometry import compute_heuristic_axis
        axis = compute_heuristic_axis( pos, 'normal', already_centered = False, nears = nears, dflt = None )

        if not axis:
            msg = orangemsg( "Warning: Normal axis could not be determined. No change in view." )
            env.history.message(cmd + msg)
            return
        
        # Compute the destination quat (q2).
        q2 = Q(V(0,0,1), axis)
        q2 = q2.conj()
        
        self.glpane.rotateView(q2)
        
        info = 'View set to normal of the plane defined by the selection.'
        env.history.message(cmd + info)
        
    def setViewParallelTo(self):
        '''Set view parallel to the vector defined by 2 selected atoms.
        '''
        cmd = greenmsg("Set View Parallel To: ")
        
        atoms = self.assy.selatoms_list()
        
        if len(atoms) != 2:
            msg = redmsg("You must select 2 atoms.")
            env.history.message(cmd + msg)
            return
        
        v = norm(atoms[0].posn()-atoms[1].posn())
        
        if vlen(v) < 0.0001: # Atoms are on top of each other.
            info = 'The selected atoms are on top of each other.  No change in view.'
            env.history.message(cmd + info)
            return
        
        # If vec is pointing into the screen, negate (reverse) vec.
        if dot(v, self.glpane.lineOfSight) > 0:
            v = -v
        
        # Compute the destination quat (q2).
        q2 = Q(V(0,0,1), v)
        q2 = q2.conj()
        
        self.glpane.rotateView(q2)
        
        info = 'View set parallel to the vector defined by the 2 selected atoms.'
        env.history.message(cmd + info)
    
    def setViewOpposite(self):
        '''Set view to the opposite of current view. '''
        cmd = greenmsg("Opposite View: ")
        info = 'Current view opposite to the previous view'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), pi))
  
    def setViewPlus90(self): # Added by Mark. 051013.
        '''Increment the current view by 90 degrees around the vertical axis. '''
        cmd = greenmsg("Rotate View +90 : ")
        info = 'View incremented by 90 degrees'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), pi/2))
        
    def setViewMinus90(self): # Added by Mark. 051013.
        '''Decrement the current view by 90 degrees around the vertical axis. '''
        cmd = greenmsg("Rotate View -90 : ")
        info = 'View decremented by 90 degrees'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), -pi/2))

    def setViewBack(self):
        cmd = greenmsg("Back View: ")
        info = 'Current view is Back View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),pi))

    def setViewBottom(self):
        cmd = greenmsg("Bottom View: ")
        info = 'Current view is Bottom View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(1,0,0),-pi/2))

    def setViewFront(self):
        cmd = greenmsg("Front View: ")
        info = 'Current view is Front View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(1,0,0,0))

    def setViewLeft(self):
        cmd = greenmsg("Left View: ")
        info = 'Current view is Left View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),pi/2))

    def setViewRight(self):
        cmd = greenmsg("Right View: ")
        info = 'Current view is Right View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),-pi/2))

    def setViewTop(self):
        cmd = greenmsg("Top View: ")
        info = 'Current view is Top View'
        env.history.message(cmd + info)

        self.glpane.rotateView(Q(V(1,0,0),pi/2))
        
    def saveNamedView(self):
        from Utility import Csys
        csys = Csys(self.assy, None, 
                                self.glpane.scale, 
                                self.glpane.pov, 
                                self.glpane.zoomFactor, 
                                self.glpane.quat)
        part = self.assy.part
        part.ensure_toplevel_group()
        part.topnode.addchild(csys)
        self.mt.mt_update()
        
    def viewRaytraceScene(self):
        'Slot for "View > Raytrace Scene"'
        
        cmd = greenmsg("Raytrace Scene: ")
        
        assy = self.assy
        part = self.assy.part
        glpane = self.glpane
        
        from PovrayScene import PovrayScene
        pvs = PovrayScene(assy, params=(None, glpane.width, glpane.height, 'png'))
        pvs.render_image()
        part.ensure_toplevel_group()
        part.topnode.addchild(pvs)
        self.mt.mt_update()
        
        msg = "POV-Ray rendering complete."
        env.history.message( cmd + msg ) 