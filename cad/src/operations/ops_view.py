# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_view.py provides viewSlotsMixin for MWsemantics,
with view slot methods and related helper methods.

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details. 

Note: most other ops_*.py files provide mixin classes for Part,
not for MWsemantics like this one.

History:

mark 060120 split this out of MWsemantics.py.
"""

import math
from Numeric import dot
from geometry.geometryUtilities import compute_heuristic_axis
import foundation.env as env
from geometry.VQT import V, Q, A, norm, vlen
from utilities.Log import greenmsg, redmsg, orangemsg
from utilities.prefs_constants import ORTHOGRAPHIC
from utilities.prefs_constants import PERSPECTIVE
from model.NamedView import NamedView
from model.PovrayScene import PovrayScene

class viewSlotsMixin:
    """
    Mixin class to provide view-related methods for class MWsemantics.
    Has slot methods and their helper methods.
    """
    def setViewHome(self):
        """
        Reset view to Home view
        """
        cmd = greenmsg("Current View: ")
        info = 'Home'
        env.history.message(cmd + info)
        self.glpane.setViewHome()

    def setViewFullScreen(self, val):
        """
        Full screen mode. (maximize the glpane real estate by hiding/ collapsing
        other widgets. (only Menu bar and the glpane are shown)
        The widgets hidden or collapsed include: 
         - MainWindow Title bar
         - Command Manager, 
         - All toolbars, 
         - ModelTree/PM area,
         - History Widget,
         - Statusbar         

        @param val: The state of the QAction (checked or uncheced) If True, it 
                    will show the main window full screen , otherwise show it 
                    with its regular size
        @type val: boolean
        @see: MWsemantics.showSemiFullScreen, MWsemantics.showNormal
        @see: self.setViewSemiFullScreen
        """
        if val:
            self.showFullScreen()
        else:
            self.showNormal()

    def setViewSemiFullScreen(self, val):
        """
        Semi-Full Screen mode. (maximize the glpane real estate by hiding/ collapsing
        other widgets. This is different than the 'Full Screen mode' as it hides
        or collapses only the following widgets -- 
         - MainWindow Title bar
         - ModelTree/PM area,
         - History Widget,
         - Statusbar         

        @param val: The state of the QAction (checked or uncheced) If True, it 
                    will show the main window full screen , otherwise show it 
                    with its regular size
        @type val: boolean
        @see: MWsemantics.showSemiFullScreen, MWsemantics.showNormal
        @see: self.setViewFullScreen
        """

        if val:
            self.showSemiFullScreen()
        else:
            self.showNormal()

    def setViewFitToWindow(self):
        """
        Fit to Window
        """
        cmd = greenmsg("Fit to Window: ")
        info = ''
        env.history.message(cmd + info)
        self.glpane.setViewFitToWindow()

    def setViewZoomToSelection(self):
        """
        Zoom to selection (Implemented for only selected jigs and chunks
        """
        cmd = greenmsg("Zoom To Selection:")
        info = ''
        env.history.message(cmd + info)
        self.glpane.setViewZoomToSelection()

    def setViewHomeToCurrent(self):
        """
        Changes Home view of the model to the current view in the glpane.
        """
        cmd = greenmsg("Set Home View to Current View: ")
        info = 'Home'
        env.history.message(cmd + info)
        self.glpane.setViewHomeToCurrent()

    def setViewRecenter(self):
        """
        Recenter the view around the origin of modeling space.
        """
        cmd = greenmsg("Recenter View: ")
        info = 'View Recentered'
        env.history.message(cmd + info)
        self.glpane.setViewRecenter()

    def zoomToArea(self, val):
        """
        Zoom to Area Tool, allowing the user to specify a rectangular area 
        by holding down the left button and dragging the mouse to zoom 
        into a specific area of the model.
        val = True when Zoom tool button was toggled on, False when it
        was toggled off.
        """
        self._zoomPanRotateTool(val, 'ZOOMTOAREA', "Zoom to Area Tool")

    def zoomInOut(self, val):
        """
        Basic Zoom for zooming in and/or out. 

        Zoom out as the user pushes the mouse away (cursor moves up). 
        Zoom in as the user pulls the mouse closer (cursor moves down).

        @param val: True when Zoom in/out button is toggled on, False when it
                    is toggled off.
        @type  val: boolean
        """
        self._zoomPanRotateTool(val, 'ZOOMINOUT', "Zoom In/Out Tool")

    def panTool(self, val):
        """
        Pan Tool allows X-Y panning using the left mouse button.
        val = True when Pan tool button was toggled on, False when it
        was toggled off.
        """
        self._zoomPanRotateTool(val, 'PAN', "Pan Tool")


    def rotateTool(self, val):
        """
        Rotate Tool allows free rotation using the left mouse button.
        val = True when Rotate tool button was toggled on, False when it
        was toggled off.
        """
        self._zoomPanRotateTool(val, 'ROTATE', "Rotate Tool")

    def _zoomPanRotateTool(self, val, commandName, user_mode_name):
        """
        Common code for Zoom, Pan, and Rotate tools.
        """
        commandSequencer = self.commandSequencer

        ## modes_we_are_called_for = ['ZOOM', 'PAN', 'ROTATE']

        # Note: some logic in here was revised by bruce 070814, especially
        # for the case when entering one of these temporary modes needs to
        # autoexit another one. This has allowed these tools to work properly
        # during Extrude Mode (and presumably other commands with internal state).
        # But all this logic should be replaced by something more principled
        # and general, using the Command Sequencer, when we have that.

        # This fixes bug 1081.  mark 060111.
        if not val:
            # The Zoom/Pan/Rotate button was toggled off. We are presumably
            # in the associated temporary command, and the user wants us to
            # exit it. Do so and return to parent command.
            command = commandSequencer.currentCommand

            ## if command.commandName in modes_we_are_called_for:
            if command.commandName == commandName:
                #bruce 071011 change, an educated guess, may increase prints, may cause bugs ### TEST
                # we're now in the command being turned off, as expected.
                if commandSequencer._f_command_stack_is_locked:
                    # this is normal when the command is exiting on its own
                    # and changes the state of its action programmatically.
                    # In this case, redundant exit causes bugs, so skip it.
                    # It might be better to avoid sending the signal when
                    # programmatically changing the action state.
                    # See similar code and comment in Move_Command.py.
                    # [bruce 080829]
                    ## print "DEBUG fyi: _zoomPanRotateTool skipping Done of %r since command stack locked" % commandName
                    ##     # remove when works, or soon after
                    pass               
                else:
                    #Exit this temporary command.
                    command.command_Done()
            else:
                if command is not commandSequencer.nullmode:
                    # bruce 071009 add condition to fix bug 2512
                    # (though the cause remains only guessed at)
                    print "bug: _zoomPanRotateTool sees unexpected current command: %r" % (command,)
                # Note: This can happen on nullMode after certain other exceptions occur.
                # [In fact, it seems to happen whenever we exit zoom/pan/rotate normally...
                #  that is now bug 2512, and its cause is not known, but it might relate
                #  to the comment above from 070814 (guess). [bruce 070831 comment]]
                # Don't run Done in this case.
                pass
            pass
        else:
            # The Zoom/Pan/Rotate button was toggled on.

            commandSequencer.userEnterCommand(commandName, always_update = True)
                #bruce 071011, encapsulating the code that was here before

            # Emit a help message on entering the new temporary command. Ideally this
            # should be done in its Enter or init_gui methods, but that made it
            # appear before the green "Entering Mode: Zoom" msg. So I put it here.
            # [Mark 050130; comment paraphrased by bruce 070814]
            # TODO: do this in a new postEnter command-specific method which is called
            # late enough to have the desired effect (later: such as command_entered,
            # after the ongoing command stack refactoring).
            env.history.message("You may hit the Esc key to exit %s." % user_mode_name)
                ###REVIEW: put this in statusbar instead?
        return

    # GLPane.ortho is checked in GLPane.paintGL
    def setViewOrtho(self):
        self.glpane.setViewProjection(ORTHOGRAPHIC)

    def setViewPerspec(self):
        self.glpane.setViewProjection(PERSPECTIVE)

    def stereoSettings(self):        
        self.enterStereoPropertiesCommand()

    def viewNormalTo(self): # 
        """
        Set view to the normal vector of the plane defined by 3 or more
        selected atoms or a jig's (Motor or RectGadget) axis.
        """
        cmd = greenmsg("Set View Normal To: ")

        chunks = self.assy.selmols
        jigs = self.assy.getSelectedJigs()
        atoms = self.assy.selatoms_list()

        #following fixes bug 1748 ninad 061003. 
        if len(chunks) > 0 and len(atoms) == 0:
            # Even though chunks have an axis, it is not necessarily the same
            # axis attr stored in the chunk.  Get the chunks atoms and let
            # compute_heuristic_axis() recompute them.
            for c in range(len(chunks)):
                atoms += chunks[c].atoms.values()
        elif len(jigs) == 1 and len(atoms) == 0:
            # Warning: RectGadgets have no atoms.  We handle this special case below.
            atoms = jigs[0].atoms 
        elif len(atoms) < 3:
            # There is a problem when allowing only 2 selected atoms. 
            # Changing requirement to 3 atoms fixes bug 1418. mark 060322
            msg = redmsg("Please select some atoms, jigs, and/or chunks, covering at least 3 atoms")
            print "ops_view.py len(atoms) = ", len(atoms)
            env.history.message(cmd + msg)
            return

        # This check is needed for jigs that have no atoms.  Currently, this 
        # is the case for RectGadgets (ESP Image and Grid Plane) only.
        if len(atoms):
            pos = A( map( lambda a: a.posn(), atoms ) )
            nears = [ self.glpane.out, self.glpane.up ]
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

    def viewNormalTo_NEW(self):
        """
        Set view to the normal vector of the plane defined by 3 or more
        selected atoms or a jig's (Motor or RectGadget) axis.
        """
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

    def viewParallelTo(self):
        """
        Set view parallel to the vector defined by 2 selected atoms.
        """
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

    def viewRotate180(self):
        """
        Set view to the opposite of current view.
        """
        cmd = greenmsg("Opposite View: ")
        info = 'Current view opposite to the previous view'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), math.pi))

    def viewRotatePlus90(self): # Added by Mark. 051013.
        """
        Increment the current view by 90 degrees around the vertical axis.
        """
        cmd = greenmsg("Rotate View +90 : ")
        info = 'View incremented by 90 degrees'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), math.pi/2))

    def viewRotateMinus90(self): # Added by Mark. 051013.
        """
        Decrement the current view by 90 degrees around the vertical axis.
        """
        cmd = greenmsg("Rotate View -90 : ")
        info = 'View decremented by 90 degrees'
        env.history.message(cmd + info)
        self.glpane.rotateView(self.glpane.quat + Q(V(0,1,0), -math.pi/2))

    def viewBack(self):
        cmd = greenmsg("Back View: ")
        info = 'Current view is Back View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),math.pi))

    def viewBottom(self):
        cmd = greenmsg("Bottom View: ")
        info = 'Current view is Bottom View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(1,0,0),-math.pi/2))

    def viewFront(self):
        cmd = greenmsg("Front View: ")
        info = 'Current view is Front View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(1,0,0,0))

    def viewLeft(self):
        cmd = greenmsg("Left View: ")
        info = 'Current view is Left View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),math.pi/2))

    def viewRight(self):
        cmd = greenmsg("Right View: ")
        info = 'Current view is Right View'
        env.history.message(cmd + info)
        self.glpane.rotateView(Q(V(0,1,0),-math.pi/2))

    def viewTop(self):
        cmd = greenmsg("Top View: ")
        info = 'Current view is Top View'
        env.history.message(cmd + info)

        self.glpane.rotateView(Q(V(1,0,0),math.pi/2))

    def viewIsometric(self):
        """
        This sets the view to isometric. For isometric view, it needs
        rotation around the vertical axis by pi/4 *followed* by rotation
        around horizontal axis by asin(tan(pi/6) - ninad060810
        """
        # This is not yet called from the MainWindow. Need UI for this.
        # Also need code review -ninad060810
        cmd = greenmsg("Isometric View: ")
        info = 'Current view is Isometric View'
        env.history.message(cmd + info)
        self.quatX = Q(V(1,0,0), math.asin(math.tan(math.pi/6)))
        self.quatY = Q(V(0,1,0), -math.pi/4)
        self.glpane.rotateView(self.quatY+self.quatX)
            # If you put quatX first, it won't give isometric view ninad060810

    def saveNamedView(self):
        csys = NamedView(self.assy, None, 
                         self.glpane.scale, 
                         self.glpane.pov, 
                         self.glpane.zoomFactor, 
                         self.glpane.quat)
        self.assy.addnode(csys)

        self.mt.mt_update()
        return

    def getNamedViewList(self):
        """
        Returns a list of all the named view nodes in the MT inside a part.
        """
        namedViewList = [] # Hold the result list

        def function(node):
            if isinstance(node, NamedView):
                namedViewList.append(node)
            return
        # Append all NamedView nodes to the namedview list
        self.assy.part.topnode.apply2all(function)

        return namedViewList

    def showStandardViewsMenu(self):
        """
        When Standard Views button is activated, show its QMenu
        """
        # By default, nothing happens if you click on the 
        # toolbutton with submenus. The menus are displayed only when you click
        # on the small downward arrow of the tool button.
        # Therefore the following slot is added. ninad 070109

        if self.standardViewsMenu.isVisible():
            self.standardViewsMenu.hide()
        else:
            self.standardViews_btn.showMenu()

    def viewQuteMol(self):
        """
        Slot for 'View > QuteMolX'. Opens the QuteMolX Property Manager.

        @note: The QuteMolX PM will not open if there are no atoms in the part.
        """    
        cmd = greenmsg("QuteMolX : ")

        if self.assy.molecules:
            self.enterQuteMolCommand()
        else:
            msg = orangemsg("No atoms in the current part.")
            env.history.message(cmd + msg)

    def viewRaytraceScene(self):
        """
        Slot for 'View > POV-Ray'.
        Raytraces the current scene. This version does not add a POV-Ray Scene
        node to the model tree. This is preferred since it allows the user to
        preview POV-Ray renderings without having to save the current part
        and/or delete unwanted nodes from the model tree. If the user wants to
        add the node to the model tree, the user must use
        'Insert > POV-Ray Scene'.
        """
        assy = self.assy
        glpane = self.glpane

        #pov = PovrayScene(assy, None, params = (glpane.width, glpane.height, 'png')) #bruce 060620 revised this
        pov = PovrayScene(assy, None)
        pov.raytrace_scene(tmpscene=True) # this emits whatever history messages are needed [bruce 060710 comment]

##    def viewRaytraceScene_ORIG(self):
##        """
##        Slot for 'View > Raytrace Scene'.
##        Raytraces the current scene. This version adds a POV-Ray Scene node to the model tree.
##        """
##        cmd = greenmsg("Raytrace Scene: ")
##        
##        assy = self.assy
##        glpane = self.glpane
##        
##        pov = PovrayScene(assy, None, params = (glpane.width, glpane.height, 'png')) #bruce 060620 revised this
##        #bruce 060620 comment: I doubt it's correct to render the image before adding the node,
##        # in case rendering it takes a long time. Also, if the rendering is aborted, the node
##        # should perhaps not be added (or should be removed if it was already added,
##        # or should be changed to indicate that the rendering was aborted).
##        errorcode, errortext = pov.raytrace_scene() # [note: as of long before 060710 the return value no longer fits this pattern] 
##        if errorcode:
##            env.history.message( cmd + redmsg(errortext) )
##            return
##        assy.addnode(pov)
##        self.mt.mt_update()
##        
##        msg = "POV-Ray rendering complete."
##        env.history.message( cmd + msg ) 

    pass # end of class viewSlotsMixin

# end
