# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
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
        
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient

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
            
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient

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
            
        # we never want these modes (ZOOM, PAN, ROTATE) to be assigned to "prevMode". 
        if self.glpane.mode.modename not in ['ZOOM', 'PAN', 'ROTATE']:
            self.glpane.prevMode = self.glpane.mode.modename
            self.glpane.prevModeColor = self.glpane.mode.backgroundColor
            self.glpane.prevModeGradient = self.glpane.mode.backgroundGradient

        self.glpane.setMode('ROTATE')
        env.history.message("You may hit the Esc key to exit Rotate Tool.")
                
    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.setViewProjection(ORTHOGRAPHIC)

    def setViewPerspec(self):
        self.glpane.setViewProjection(PERSPECTIVE)

    def setViewNormalTo(self):
        '''Set view to the normal vector of the plane defined by 3 or more
        selected atoms or a jig's (Motor or RectGadget) axis.
        '''
        cmd = greenmsg("Orient View Normal To: ")
        
        atoms = self.assy.selatoms_list()
        jigs = self.assy.getSelectedJigs()
        
        if len(jigs) == 1 and len(atoms) == 0:
            axis = jigs[0].getaxis()
        elif len(atoms) >= 3:
            pos = A( map( lambda a: a.posn(), atoms ) )
            from geometry import compute_heuristic_axis
            axis = compute_heuristic_axis( pos, 'normal' )
        else:
            msg = redmsg("Please select at least 3 atoms or a jig.")
            env.history.message(cmd + msg)
            return

        if not axis:
            msg = orangemsg( "Warning: Normal axis cannot be determined. No change in view." )
            env.history.message(cmd + msg)
            return

        # If axis is pointing into the screen, negate (reverse) axis.
        if dot(axis, self.glpane.lineOfSight) > 0:
            axis = -axis
        
        # Compute the destination quat (q2).
        q2 = Q(V(0,0,1), axis)
        q2 = q2.conj()
        
        self.glpane.rotateView(q2)
        
        info = 'View set to normal vector of the plane defined by the selected atoms.'
        env.history.message(cmd + info)

# This should be moved somewhere else.  
# Someday when we have a selection class, this would be a nice method for it.
# Talk to Bruce.  Mark 060118.
    def getaxis(self, atoms):
        '''Returns the 'center' axis. atoms is a list of 3 or more atoms used to compute the 
        center axis.
        '''
        if len(atoms) < 3:
            return V(0,0,0) # Caller beware.
        
        # This code was copied from Motor.recompute_center_axis().  Mark 060118.
        pos=A(map((lambda a: a.posn()), atoms))
        center=sum(pos)/len(pos)
        relpos=pos-center
        guess = map(cross, relpos[:-1], relpos[1:])
        axis=sum(guess)
        return axis
        
    def setViewParallelTo(self):
        '''Set view parallel to the vector defined by 2 selected atoms.
        '''
        cmd = greenmsg("Orient View Parallel To: ")
        
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
        
    def pointing_into_screen(self, v):
        '''Debugging method.  Returns true if vector v points into the screen.
        '''
        # Author - Mark.  060118.
        # Keep this around.  I found it useful to understand this test.
        
        los = self.assy.o.lineOfSight
        
        if 1: 
            print "-----------------------"
            print "v= %.2f %.2f %.2f" % (float(v[0]), float(v[1]), float(v[2]))
            print "los= %.2f %.2f %.2f" % (float(los[0]), float(los[1]), float(los[2]))
            if dot(v, los) < 0:
                print "Vector v is pointing out of the screen."
            else:
                print "Vector v is pointing into the screen."
        
        if dot(v, los) < 0:
            return False
        else:
            return True

    
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