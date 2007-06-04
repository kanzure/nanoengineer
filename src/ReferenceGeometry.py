# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
@author: Ninad,
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@version: $Id$

History:
ninad 20070521 : Created

ninad 20070701: Implemented DragHandler and selobj interface for the 
class Handles. (and for ReferenceGeoemtry which is a superclass of Plane)

ninad 20070704: Changed the superclass from Node to Jig based on a discussion 
with Bruce. This allows us to use code for jig selection deletion in some select 
modes. (note that it continues to use drag handler, selobj interfaces.). 
This might CHANGE in future.  After making jig a superclass of ReferenceGeometry
some methods in this file have become overdefined. This needs cleanup
"""

#@NOTE:This file is subjected to major changes.

#@TODO: Ninad20070604 :
#- Needs documentation and code cleanup / organization post Alpha-9.
#--Examples: code not reused -- It uses and modifies methods in 
#GeneratorBaseClass instead of inheriting it. Better to make changes in 
#GeneratorBase class. -- see another note in this file for reason why I did 
#this for A9.
#-After making jig a superclass of ReferenceGeometry
#some methods in this file have become overdefined. This needs cleanup.

__author__ = "Ninad"


from Utility import Node
from constants import darkgreen, orange, yellow, white
from constants import gensym
from Utility import imagename_to_pixmap
import env
import platform
from DragHandler import DragHandler_API
from jigs import Jig


class ReferenceGeometry(Jig, DragHandler_API):
    ''' Superclass for various reference geometries. 
    Example or reference geometries: Plane, Point, Line'''
    
    sym = "Geometry" # affects name-making code in __init__
    pickcolor = darkgreen 
    mmp_record_name = "#" # if not redefined, this means it's just a comment in an mmp file
    featurename = "" 
    #color = normcolor = (0.5, 0.5, 0.5)
    color = normcolor = orange

    atoms = []
    points = None
    handles = None
    
    copyable_attrs = Node.copyable_attrs + ('pickcolor', 'normcolor', 'color')
        
    def __init__(self, win):  
        self.win = win
        #Node.__init__(self, win.assy, gensym("%s-" % self.sym))        
        Jig.__init__(self, win.assy, self.atoms)        
        self.glname = env.alloc_my_glselect_name( self) 
        self.glpane = self.assy.o
        
        self.pw = None
        self.modePropertyManager = None
        self.struct = None
        self.previousParams = None
        self.existingStructForEditing = False
        self.old_props = None
        
    
    def needs_atoms_to_survive(self): 
        '''Overrided method inherited from Jig. This is used to tell 
        if the jig can be copied even it doesn't have atoms.'''
        return False
                        
    def _draw(self, glpane, dispdef):
        self._draw_geometry(glpane, self.color)        
    
    def _draw_geometry(self,glpane, color, highlighted =False):
        ''' The main code that draws the geometry. 
        Subclasses should override this method.'''
        pass
            
    def draw(self, glpane):
        try:
            glPushName(self.glname)
            self._draw(glpane, dispdef)
        except:
            glPopName()
            print_compact_traceback("ignoring exception when drawing Plane %r: " % self)
        else:
            glPopName()
                
    def draw_in_abs_coords(self, glpane, color):
        '''Draws the reference geometry with highlighting.'''       
        self._draw_geometry(glpane, color, highlighted = True)   
                   
    def node_icon(self, display_prefs):
        '''A subclasse should override this if it needs to 
        choose its icons differently'''
        return imagename_to_pixmap( self.icon_names[self.hidden] )
    
    def pick(self): 
        """Select the reference geometry"""
        if not self.picked: 
            Node.pick(self)
            self.normcolor = self.color
            self.color = self.pickcolor
        return

    def unpick(self):
        """Unselect the reference geometry"""
        if self.picked:
            Node.unpick(self) 
            self.color = self.normcolor # see also a copy method which has to use the same statement to compensate for this kluge

    def rot(self, quat):
        pass
    
    ##===============copy methods ==================###
    def copy_full_in_mapping(self, mapping): #bruce 070430 revised to honor mapping.assy
        clas = self.__class__
        new = clas(mapping.assy.w, []) # don't pass any atoms yet (maybe not all of them are yet copied)
            # [Note: as of about 050526, passing atomlist of [] is permitted for motors, but they assert it's [].
            #  Before that, they didn't even accept the arg.]
        # Now, how to copy all the desired state? We could wait til fixup stage, then use mmp write/read methods!
        # But I'd rather do this cleanly and have the mmp methods use these, instead...
        # by declaring copyable attrs, or so.
        new._orig = self
        new._mapping = mapping
        return new
    
    ###============== selobj interface ===============###
     
    #Methods for selobj interface  . Note that draw_in_abs_coords method is 
    #already defined above. All of the following is NIY  -- Ninad 20070522
    
    def leftClick(self, point, event, mode):       
        mode.geometryLeftDown(self, event)
        mode.update_selobj(event)
        return self
                    
    def mouseover_statusbar_message(self):
        return str(self.name)
        
    def highlight_color_for_modkeys(self, modkeys):
        return yellow
    
    # copying Bruce's code from class Highligtable with some mods.Need to see        
    # if sleobj_still_ok method is needed. OK for now --Ninad 20070601        
    def selobj_still_ok(self):
        res = self.__class__ is ReferenceGeometry 
        if res:
            our_selobj = self
            glname = self.glname
            owner = env.obj_with_glselect_name.get(glname, None)
            if owner is not our_selobj:
                res = False
                # owner might be None, in theory, but is probably a replacement of self at same ipath
                # do debug prints
                print "%r no longer owns glname %r, instead %r does" % (self, glname, owner) # [perhaps never seen as of 061121]
                our_ipath = self.ipath
                owner_ipath = getattr(owner, 'ipath', '<missing>')
                if our_ipath != owner_ipath:
                    # [perhaps never seen as of 061121]
                    print "WARNING: ipath for that glname also changed, from %r to %r" % (our_ipath, owner_ipath)
                pass
            pass
            # MORE IS PROBABLY NEEDED HERE: that check above is about whether this selobj got replaced locally;
            # the comments in the calling code are about whether it's no longer being drawn in the current frame;
            # I think both issues are valid and need addressing in this code or it'll probably cause bugs. [061120 comment] ###BUG
        import env
        if not res and env.debug():
            print "debug: selobj_still_ok is false for %r" % self ###@@@
        return res # I forgot this line, and it took me a couple hours to debug that problem! Ugh.
            # Caller now prints a warning if it's None. 
    
    ###=========== Drag Handler interface =============###
    def handles_updates(self): #k guessing this one might be needed
        return True
            
    def DraggedOn(self, event, mode):        
        mode.geometryLeftDrag(self, event)
        mode.update_selobj(event)
        return
    
    def ReleasedOn(self, selobj, event, mode): 
        pass
  
    ##======common methods for Property Managers=====###
    #@NOTE: This copies some methods from GeneratorBaseClass
    #first I intended to inherit ReferenceGeometry from that class but 
    #had weired problems in importing it. Something to do with 
    #QPaindevice/ QApplication /QPixmap. NE1 didn't start de to that error
    #Therefore, implemented and modified the following methods. OK for Alpha9 
    #and maybe later -- Ninad 20070703
    
    def abort_btn_clicked(self):
        self.cancel_btn_clicked()
        pass
    def restore_defaults_btn_clicked(self):
        pass
    
    def enter_WhatsThisMode(self):
        pass
    
    def ok_btn_clicked(self):
        'Slot for the OK button'
        if platform.atom_debug: print 'ok button clicked'
                    
        self._ok_or_preview(doneMsg=True)   
        self.accept() #bruce 060621
        self.struct = None
        self.closePropertyManager() 
        # the following reopens the property manager of the mode after 
        #when the PM of the reference geometry is closed. -- Ninad 20070103
        
        if self.win.assy.o.mode.modename in \
           ['DEPOSIT', 'MODIFY', 'FUSE', 'MOVIE']:
            self.modePropertyManager = self.win.assy.o.mode
        if self.modePropertyManager:
            self.openPropertyManager(self.modePropertyManager)
        return
    
    def cancel_btn_clicked(self):
        'Slot for the Cancel button'
        if platform.atom_debug: print 'cancel button clicked'
        self.win.assy.current_command_info(cmdname = self.cmdname + " (Cancel)")
           
        if self.existingStructForEditing: 
            if self.old_props:
                self.setProps(self.old_props)
                self.glpane.gl_update() 
                
        else:
            self.remove_struct()            
        self._revert_number()
        self.reject() 
        self.closePropertyManager()
        
        if self.win.assy.o.mode.modename in \
           ['DEPOSIT', 'MODIFY', 'FUSE', 'MOVIE']:
            self.modePropertyManager = self.win.assy.o.mode
            
        if self.modePropertyManager:
            self.openPropertyManager(self.modePropertyManager)
        return
    
    def preview_btn_clicked(self):
        if platform.atom_debug: print 'preview button clicked'
        self._ok_or_preview(previewing=True)
    
    
    def _ok_or_preview(self, doneMsg=False, previewing=False):
        self.win.assy.current_command_info(cmdname = self.cmdname) 
        self._build_struct(previewing=previewing)
        if doneMsg:
            env.history.message(self.cmd + self.done_msg())
        
        self.win.win_update()
    
    def _build_struct(self, previewing=False):
        if platform.atom_debug:
            print '_build_struct'
            
        params = self.gather_parameters()
        
        if self.struct == None:
            if platform.atom_debug:
                print 'no old structure, we are making a new structure'
        elif params != self.previousParams:
            if platform.atom_debug:
                print 'parameters have changed, update existing structure'
            self._revert_number()
            # fall through, using old name
        else:
            if platform.atom_debug:
                print 'old structure, parameters same as previous, do nothing'
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
        self.win.assy.place_new_geometry(self.struct)                
                
    def _revert_number(self):
        import Utility
        if hasattr(self, '_Gno'):
            Gno = self._Gno
        if hasattr(self, '_ViewNum'):
            Utility.ViewNum = self._ViewNum
    
    def remove_struct(self):
        if platform.atom_debug: print 'Should we remove an existing structure?'
        if self.struct != None:
            if platform.atom_debug: print 'Yes, remove it'
            self.struct.kill()
            self.struct = None
            self.win.win_update() # includes mt_update
        else:
            if platform.atom_debug: print 'No structure to remove'
    
    def done_msg(self):
        '''Tell what message to print when the geometry has been
        built. This may be overloaded in the specific generator.
        '''
        return "%s created." % self.name
    
