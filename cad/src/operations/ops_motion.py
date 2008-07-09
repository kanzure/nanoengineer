# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
ops_motion.py -- various ways of moving or spatially distorting
selected atoms or chunks (and someday, attached jigs).
These operations don't create or destroy atoms or bonds.

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 050507 made this by collecting appropriate methods from class Part.
"""

from utilities.Log import greenmsg, redmsg
from platform_dependent.PlatformDependent import fix_plurals
from geometry.VQT import V, norm, Q, vlen, orthodist
import foundation.env as env
from math import pi
from utilities.debug import print_compact_traceback

from model.chunk import Chunk
from model.jigs import Jig
from model.jigs_motors import Motor
from analysis.ESP.ESPImage import ESPImage
from foundation.Group import Group


class ops_motion_Mixin:
    """
    Mixin class for providing these methods to class Part
    """
    ###@@@ move/rot should be extended to apply to jigs too (and fit into some naming convention)
    
    def movesel(self, offset):
        """
        move selected chunks and jigs in space
        """
        movables = self.getSelectedMovables()
        
        self.translateSpecifiedMovables(offset, movables = movables)
        
    
    def translateSpecifiedMovables(self, offset, movables =()):
        """
        Translate the specified movables.
        @param movables: a list of movables (default value is empty tuple)
        @type movables: list 
        """        
        for m in movables:
            self.changed() 
            m.move(offset)    
  
    def rotsel(self, quat):
        """
        Rotate selected chunks/jigs in space. [Huaicai 8/30/05: Fixed the problem of each rotating
        around its own center, they will now rotate around their common center]
        """                   
        movables = self.getSelectedMovables()
        self.rotateSpecifiedMovables(quat, movables = movables)        
        return
    
    def rotateSpecifiedMovables(self, quat, movables =(), commonCenter = None):
        """
        Rotate the movables specified in the 'movables' list. 
        (Rotated as a unit)
        @param quat: Quaternion for the rotation. 
        @param movables: A list of movables. These movables will be 
                rotated around a common axis
        @type movables: list
        
        """
        numMovables = len(movables)
        
        if commonCenter is None:            
            # Find the common center of all selected chunks to fix bug 594 
            #--Huaicai 8/30/05
            comCenter = V(0.0, 0.0, 0.0)
            if numMovables:
                for m in movables: 
                    comCenter += m.center                      
                comCenter /= numMovables
           
        else:
            comCenter = commonCenter
     
        # Move the selected chunks    
        for m in movables:
            self.changed() #Not sure if this can be combined into one call
            # Get the moving offset because of the rotation around each 
            # movable's own center
            rotOff = quat.rot(m.center - comCenter)  
            rotOff = comCenter - m.center + rotOff 
            m.move(rotOff) 
            m.rot(quat) 
                    
    
    def Stretch(self):
        """
        stretch a Chunk
        """
        mc = env.begin_op("Stretch")
        try:
            cmd = greenmsg("Stretch: ")
            
            if not self.selmols:
                msg =  redmsg("No selected chunks to stretch")
                env.history.message(cmd + msg)
            else:
                self.changed()
                for m in self.selmols:
                    m.stretch(1.1)
                self.o.gl_update()
                
                # Added history message.  Mark 050413.
                info = fix_plurals( "Stretched %d chunk(s)" % len(self.selmols))
                env.history.message( cmd + info)
        finally:
            env.end_op(mc)
        return
    
    def Invert(self):
        """
        Invert the atoms of the selected chunk(s) around the chunk centers
        """
        mc = env.begin_op("Invert")
        cmd = greenmsg("Invert: ")
        
        if not self.selmols:
            msg = redmsg("No selected chunks to invert")
            env.history.message(cmd + msg)
            return
        self.changed()
        for m in self.selmols:
            m.stretch(-1.0)
        self.o.gl_update()
        
        info = fix_plurals( "Inverted %d chunk(s)" % len(self.selmols))
        env.history.message( cmd + info)
        env.end_op(mc) #e try/finally?
    
    def Mirror(self):
        """
        Mirror the selected chunk(s) about a selected grid plane.
        """
        cmd = greenmsg("Mirror: ")
        #ninad060814 this is necessary to fix a bug. Otherwise program will 
        #crash if you try to mirror when the top node of the part 
        #(main part of clipboard) is selected
        
        if self.topnode.picked:
            self.topnode.unpick_top()                                                  
        
        self.mirrorJigs = self.getQualifiedMirrorJigs()
               
        jigCounter = len(self.mirrorJigs)        
                        
        if jigCounter < 1:
            msg1 = "No mirror plane selected."
            msg2 = " Please select a Reference Plane or a Grid Plane first."
            msg = redmsg(msg1+msg2)
            instr1 = "(If it doesn't exist, create it using"
            instr2 = "<b>Insert > Reference Geometry menu </b> )"
            instruction = instr1 + instr2
            env.history.message(cmd + msg  + instruction)
            return 
        elif jigCounter >1:
            msg = redmsg("More than one plane selected. Please select only one plane and try again")
            env.history.message(cmd + msg ) 
            return 
        
        for j in self.mirrorJigs:
            j.unpick()
            
        copiedObject = self.o.assy.part.copy_sel_in_same_part()
        
        # ninad060812 Get the axis vector of the Grid Plane. Then you need to 
        #rotate the inverted chunk by pi around this axis vector
        self.mirrorAxis = self.mirrorJigs[0].getaxis()  
        
        if isinstance(copiedObject, Chunk):
            copiedObject.name = copiedObject.name + "-Mirror"
            self._mirrorChunk(copiedObject)            
            return        
        elif isinstance(copiedObject, Group):
            copiedObject.name = "Mirrored Items"
            def mirrorChild(obj):
                if isinstance(obj, Chunk):
                    self._mirrorChunk(obj)
                elif isinstance(obj, Jig):
                    self._mirrorJig(obj)
                                                           
            copiedObject.apply2all(mirrorChild)
        return                        
                
    def _mirrorChunk(self, chunkToMirror):
        """
        Converts the given chunk into its own mirror. 
        
        @param chunkToMirror: The chunk that needs to be converted into its own
               mirror chunk. 
        @type  chunkToMirror: instance of class Chunk
        @see:  self.Mirror
        """
        m = chunkToMirror
        # ninad060813 Following gives an orthogonal distance between the 
        #chunk center and mirror plane.
        self.mirrorDistance, self.wid = orthodist(m.center, 
                                                  self.mirrorAxis, 
                                                  self.mirrorJigs[0].center) 
        # @@@@ ninad060813 This moves the mirror chunk on the other side of 
        # the mirror plane. It surely moves the chunk along the axis of the 
        # mirror plane but I am still unsure if this *always* moves the 
        # chunk on the other side of the mirror. 
        #Probably the 'orthodist' function has helped me here?? 
        m.move(2*(self.mirrorDistance)*self.mirrorAxis)
        
        m.stretch(-1.0)
        m.rot(Q(self.mirrorAxis, pi))
        return
                
    def _mirrorJig(self, jigToMirror):
        """
        Converts the given jig into its own mirror. If the jig is a motor, 
        it also reverses its direction.
        @param jigToMirror: The jig that needs to be converted into its own
               mirror jig. 
        @type  jigToMirror: instance of class Jig
        @see:  self.Mirror
        """
        j = jigToMirror
        # ninad060813 This gives an orthogonal distance between the chunk 
        # center and mirror plane.
        
        #Fixed bug 2503. 
        if not (isinstance(j, Motor) or isinstance(j, ESPImage)):
            return
        
        self.mirrorDistance, self.wid = orthodist(j.center, self.mirrorAxis, 
                                                  self.mirrorJigs[0].center)         
        j.move(2*(self.mirrorDistance)*self.mirrorAxis)
        
        j.rot(Q(self.mirrorAxis, pi))
        
        #Reverse the direction of Linear and Rotary motor for correct 
        #mirror operation
        if isinstance(j, Motor):
            j.reverse_direction()
        return
            
    def getQualifiedMirrorJigs(self):
        """
        Returns a list of objects that can be used as a   
        reference in Mirror Feature. (referece plane and grid planes are valid 
        objects). Only the first object in this list is used for mirror. 
        See Mirror method for details
        """
        
        jigs = self.assy.getSelectedJigs()
        mirrorJigs = []

        for j in jigs:
            if j.mmp_record_name is "gridplane" or j.mmp_record_name is "plane":
                mirrorJigs.append(j)
                
        return mirrorJigs
    
    def align_NEW(self):
        """
        Align the axes of the selected movables to the axis of the movable
        that is placed at the highest order in the Model Tree
        """
        #@@This is not called yet.
        #method *always* uses the MT order to align chunks or jigs   
        #This supports jigs (including reference planes) but it has following
        #bug -- It always uses the selected movable that is placed highest
        #in the Model Tree, as the reference axis for alignment. (Instead 
        #it should align to the 'first selected movable' 
        #(this doesn't happen (or very rarely happens) in old align method where
        #'selmols' is used.) 

        cmd = greenmsg("Align to Common Axis: ")
        
        movables = self.assy.getSelectedMovables()
        for m in movables:
            print "movable =", m.name
        numMovables = len(movables)
        if len(movables) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            env.history.message(cmd + msg)
            return
        self.changed()
        try:
            firstAxis = movables[0].getaxis()
            for m in movables[1:]:             
                m.rot(Q(m.getaxis(),firstAxis))                
            self.o.gl_update()
        except:
            print_compact_traceback ("bug: selected movable object doesn't have an \
            axis")
            msg = redmsg("bug: selected movable object doesn't have an axis")
            env.history.message(cmd + msg)
            return
        self.o.gl_update()
        
        info = fix_plurals( "Aligned %d item(s)" % (len(movables) - 1) ) \
            + " to axis of %s" % movables[0].name
        env.history.message( cmd + info)
        return
    
    def align(self):
        """
        
        """
        cmd = greenmsg("Align to Common Axis: ")     
 
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            env.history.message(cmd + msg)
            return
        self.changed() #bruce 050131 bugfix or precaution
        #ax = V(0,0,0)
        #for m in self.selmols:
        #    ax += m.getaxis()
        #ax = norm(ax)
        ax = self.selmols[0].getaxis() # Axis of first selected chunk
        for m in self.selmols[1:]:
            m.rot(Q(m.getaxis(),ax))
        self.o.gl_update()
        
        info = fix_plurals( "Aligned %d chunk(s)" % (len(self.selmols) - 1) ) \
            + " to chunk %s" % self.selmols[0].name
        env.history.message( cmd + info)
    
    #Ninad 060904 The following is not called from UI. Need to see if this is useful to the user. 
    def alignPerpendicularToPlane(self):
        """
        Aligns the axes of selected jigs or chunks perpendicular to a reference plane
        """
        cmd = greenmsg("Align to Plane:")
        
        referencePlaneList = self.getQualifiedReferencePlanes()
        jigCounter = len(referencePlaneList) 
        
        self.changed()
        
        if jigCounter:
            referencePlane = referencePlaneList[0] #ninad060904 If more than 1 ref planes are selected, it selectes the first in the order in the mmp file
        
            
        if jigCounter < 1:
            msg = redmsg("Please select a plane first.")
            instruction = "  (If it doesn't exist, create one using <b>Insert > Reference Geometry</b> menu )"
            env.history.message(cmd + msg  + instruction)
            return 

        movables = self.assy.getSelectedMovables()
        numMovables = len(movables)
        #print len(movables)
        
        if numMovables >1:
            for obj in movables:
                if obj is referencePlane:
                    pass
                refAxis = referencePlane.getaxis()
                obj.rot(Q(obj.getaxis(),refAxis))
                self.o.gl_update()
        else:
            msg = redmsg("No chunks or movable jigs selected to align perpendicular to the reference plane.")
            env.history.message(cmd + msg  + instruction)
            return 
            
                 
    def getQualifiedReferencePlanes(self, jigs): #Ninad 060904
        """
        Returns a list of jigs that can be used a  reference plane in align to plane feature.
        """
        referencePlaneList = []
        for j in jigs:
            if j.mmp_record_name is "gridplane":
                referencePlaneList += [j]
        return referencePlaneList 
        
    def alignmove(self):
        
        cmd = greenmsg("Move to Axis: ")
        
        if len(self.selmols) < 2:
            msg = redmsg("Need two or more selected chunks to align")
            env.history.message(cmd + msg)
            return
        self.changed()
        #ax = V(0,0,0)
        #for m in self.selmols:
        #    ax += m.getaxis()
        #ax = norm(ax)
        ax = self.selmols[0].getaxis() # Axis of first selected chunk
        ctr = self.selmols[0].center # Center of first selected chunk
        for m in self.selmols[1:]:
            m.rot(Q(m.getaxis(),ax))
            m.move(ctr-m.center) # offset
        
        self.o.gl_update()
        
        info = fix_plurals( "Aligned %d chunk(s)" % (len(self.selmols) - 1) ) \
            + " to chunk %s" % self.selmols[0].name
        env.history.message( cmd + info)
        
    pass # end of class ops_motion_Mixin

# end
