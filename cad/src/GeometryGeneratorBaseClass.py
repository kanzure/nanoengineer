# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

"""
$Id$

#####=============TEMPORARY GeometryGeneratorBaseClass=========###

#@TODO: This is a temporary class for Alpha9.x, Alpha10 It should be modified
#or deleted during post A9 development (when we revise GeneratorBaseClass)
#This is very much like GeneratorBaseClass but has a few modifications
#for use in PlaneGenerator.  At present, only PlaneGenerator inherits this
#class. -- Ninad 2007-06-06

History:
ninad 20070606: Originally Created this as a temporary work for Alpha9,
                In Alpha9 this class is inherited by PlaneGenerator class. 
                It is still being used because of some missing functionality 
                in GeneratorBaseClass. 
ninad 2007-09-11: Created this file. (split this class out of 
                 ReferenceGeometry.py

"""

import env
import platform

from debug import print_compact_traceback

from constants import darkgreen, orange, yellow

from OpenGL.GL import glPushName
from OpenGL.GL import glPopName

from Utility import Node
from jigs    import Jig

from DragHandler   import DragHandler_API
from HistoryWidget import greenmsg

from state_utils import same_vals


class GeometryGeneratorBaseClass:
    """
    Geometry Generator base class . This is a temporary class for Alpha9. 
    It should be modified   or deleted during post A9 development 
    (when we revise GeneratorBaseClass)  This is very much like 
    GeneratorBaseClass but has a few modifications
    for use in PlaneGenerator.  At present, PlaneGenerator inherits this.
    """
    # see definition details in GeneratorBaseClass
    cmd      =  "" 
    cmdname  =  "" 

    ##======common methods for Property Managers=====###
    #@NOTE: This copies some methods from GeneratorBaseClass
    #first I intended to inherit ReferenceGeometry from that class but 
    #had weired problems in importing it. Something to do with 
    #QPaindevice/ QApplication /QPixmap. NE1 didn't start de to that error
    #Therefore, implemented and modified the following methods. OK for Alpha9 
    #and maybe later -- Ninad 20070603
    
     # pass window arg to constructor rather than use a global, wware 051103
    def __init__(self, win):
        """
        Constructor for the class GeometryGeneratorBaseClass.        
        """
        self.win = win
        # pw = part window. 
        # Its subclasses will create their partwindow objects 
        # (and destroy them after Done) -- @@ not be a good idea if we have
        # multiple partwindow support? (i.e. when win object is replaced(?) by 
        # partwindow object for each partwindow).  But this works fine.
        # ..same guess -- because opening multiple windows is not supported
        # When we begin supporting that, lots of things will change and this 
        # might be one of them .--- ninad 20070613
        self.pw                   =  None
        self.modePropertyManager  =  None
        self.struct               =  None
        self.previousParams       =  None
        self.old_props            =  None
        self.existingStructForEditing  =  False
        
        if 1:
            #bruce 060616 added the following kluge to make sure both cmdname 
            #and cmd are set properly.
            if not self.cmdname and not self.cmd:
                self.cmdname = "Generate something"
            if self.cmd and not self.cmdname:
                # deprecated but common, as of 060616
                self.cmdname = self.cmd # fallback
                try:
                    cmdname = self.cmd.split('>')[1]
                    cmdname = cmdname.split('<')[0]
                    cmdname = cmdname.split(':')[0]
                    self.cmdname = cmdname
                except:
                    if platform.atom_debug:
                        print "fyi: %r guessed wrong \
                        about format of self.cmd == %r" % (self, self.cmd,)
                    
            elif self.cmdname and not self.cmd:
                # this is intended to be the usual situation, but isn't yet, 
                #as of 060616
                self.cmd = greenmsg(self.cmdname + ": ")
        return
    
    def abort_btn_clicked(self):
        """
        Slot for Abort button
        """
        self.cancel_btn_clicked()
        
    def restore_defaults_btn_clicked(self):
        """
        Slot for Restore defaults button
        """
        pass
    
    def enter_WhatsThisMode(self):
        """
        Show what's this text
        """
        pass
    
    def ok_btn_clicked(self):
        """
        Slot for the OK button
        """
        if platform.atom_debug: print 'ok button clicked'
                    
        self._ok_or_preview(doneMsg = True)   
        self.accept() #bruce 060621
        self.struct = None
        self.close() # Close the property manager.
        
        # The following reopens the property manager of the mode after 
        # when the PM of the reference geometry is closed. -- Ninad 20070603 
        # Note: the value of self.modePropertyManager can be None
        # @see: anyMode.propMgr
        self.modePropertyManager = self.win.assy.o.mode.propMgr
                
        if self.modePropertyManager:
            #@self.openPropertyManager(self.modePropertyManager)
            # (re)open the PM of the current command (i.e. "Build > Atoms").
            self.open(self.modePropertyManager)
        return
    
    def cancel_btn_clicked(self):
        """
        Slot for the Cancel button.
        """
        if platform.atom_debug: print 'cancel button clicked'
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
           
        if self.existingStructForEditing: 
            if self.old_props:
                self.geometry.setProps(self.old_props)
                self.geometry.glpane.gl_update() 
                
        else:
            self.remove_struct()            
        self._revert_number()
        self.reject() 
        self.close() # Closes the property manager.
        
        # The following reopens the property manager of the command after
        # the PM of the reference geometry generator (i.e. Plane) is closed.
        # Note: the value of self.modePropertyManager can be None.
        # See anyMode.propMgr
        self.modePropertyManager = self.win.assy.o.mode.propMgr
            
        if self.modePropertyManager:
            #@self.openPropertyManager(self.modePropertyManager)
            # (re)open the PM of the current command (i.e. "Build > Atoms").
            self.open(self.modePropertyManager)
        return
    
    def preview_btn_clicked(self):
        """
        Slot for the Preview button.
        """
        if platform.atom_debug: print 'preview button clicked'
        self._ok_or_preview(previewing = True)
    
    def _ok_or_preview(self, doneMsg = False, previewing = False):
        """
        Things to do when done or Preview button in PM are clicked
        (Need documentation)
        """
        self.win.assy.current_command_info(cmdname = self.cmdname) 
        self._build_struct(previewing = previewing)
        if doneMsg:
            env.history.message(self.cmd + self.done_msg())
        
        self.win.win_update()
    
    def _build_struct(self, previewing = False):
        """
        Build structure
        (need documentation)
        """
        if platform.atom_debug:
            print '_build_struct'
            
        params = self.gather_parameters()
        
        if self.struct is None:
            if platform.atom_debug:
                print 'no old structure, we are making a new structure'
        elif not same_vals( params, self.previousParams):
            if platform.atom_debug:
                print 'parameters have changed, update existing structure'
            self._revert_number()
            # fall through, using old name
        else:
            if platform.atom_debug:
                print 'old structure, parameters same as previous, do nothing'
            if not previewing:
                self.struct.updateCosmeticProps()
            return

        name = self.name
        if platform.atom_debug:
            print "Used existing name =", name
        
        if previewing:
            env.history.message(self.cmd + "Previewing " + name)
        else:
            env.history.message(self.cmd + "Creating " + name)
        self.remove_struct()
        self.previousParams = params
        if platform.atom_debug: print 'build a new structure'
        self.struct = self.build_struct(name, params)
        if not previewing:
            self.struct.updateCosmeticProps()
        self.win.assy.place_new_geometry(self.struct)  
        #@ following not needed?? - ninad 20070606
        self.win.assy.changed()
        self.win.win_update()
                    
    def _revert_number(self):
        """
        need documentation 
        """
        #bruce 070603: removing the Gno part of revert_number, 
        #since it won't work properly with the new gensym.
        # If we still need this side effect, we'll have to implement it
        #differently.Note that the only other reference to _Gno is a few lines 
        #below, where it's set in _build_struct (also removed now).
        ##        import chem
        ##        if hasattr(self, '_Gno'):
        ##            chem.Gno = self._Gno
        import Utility
        if hasattr(self, '_ViewNum'):
            Utility.ViewNum = self._ViewNum
    
    def remove_struct(self):
        """
        Delete the old structure generated during preview if user modifies 
        some parameters or hits cancel
        """
        if platform.atom_debug: print 'Should we remove an existing structure?'
        if self.struct != None:
            if platform.atom_debug: print 'Yes, remove it'
            self.struct.kill()
            self.struct = None
            self.win.win_update() # includes mt_update
        else:
            if platform.atom_debug: print 'No structure to remove'
    
    def done_msg(self):
        """
        Returns the done message. This may be overloaded in the specific 
        generator.
        """
        return "%s created." % self.name
 