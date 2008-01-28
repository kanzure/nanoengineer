# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaSegment_EditCommand provides a way to edit an existing DnaSegment. 

To edit a segment, first enter BuildDna_EditCommand (accessed using Build> Dna) 
then, select an axis chunk of an existing DnaSegment  within the DnaGroup you
are editing. When you select the axis chunk, it enters DnaSegment_Editcommand
and shows the prperty manager with its widgets showing the properties of 
selected segment. 

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2008-01-18: Created

TODO: 
DnaSegment_editCommand doesn't retain , for instance, crossovers. This can be 
fixed after dna_data model is fully implemented

"""

from EditCommand import EditCommand 

from dna_model.DnaSegment import DnaSegment
from DnaSegment_GraphicsMode import DnaSegment_GraphicsMode


from utilities.Log  import redmsg
from VQT            import V, Veq
from DnaDuplex      import B_Dna_PAM3
from DnaDuplex      import B_Dna_PAM5

from GeneratorBaseClass import  PluginBug, UserError


from constants import gensym

from Dna_Constants import getDuplexLength
from test_connectWithState import State_preMixin

#see. self._create_or_update_handles for the info about the debug flag below
#Never commit with this flag enabled
DEBUG_DRAW_HANDLES_USING_EXPRS_MODULE = 0  

class DnaSegment_EditCommand(State_preMixin, EditCommand):
    cmd              =  'Dna Segment'
    sponsor_keyword  =  'DNA'
    prefix           =  'Segment '   # used for gensym
    cmdname          = "DNA_SEGMENT"
    commandName       = 'DNA_SEGMENT'
    featurename       = 'Edit Dna Segment'
    
   
    command_should_resume_prevMode = True
    command_has_its_own_gui = True
    command_can_be_suspended = False
    
    # Generators for DNA, nanotubes and graphene have their MT name 
    # generated (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 
    
    #Graphics Mode 
    GraphicsMode_class = DnaSegment_GraphicsMode
    
    #required by DnaLine_GM
    mouseClickPoints = []
    
    
    #This is set to BuildDna_EditCommand.flyoutToolbar (as of 2008-01-14, 
    #it only uses 
    flyoutToolbar = None
       
    _parentDnaGroup = None
    
    
    
    
    
    def __init__(self, commandSequencer, struct = None):
        """
        Constructor for DnaDuplex_EditCommand
        """     
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct
        
        #####################
        #Graphics handles for editing the structure . 
        #Not implemented as of 2008-01-25. 
        self.handles = []        
        self.endHandle1 = None 
        self.endHandle2 = None
        
        #Junk instance variable cylinderWidth. ONLY used for experimental work 
        #in drawing a handle (when debuug flag: 
        #DEBUG_DRAW_HANDLES_USING_EXPRS_MODULE is ON. )
        #see: self._create_or_update_handles for more infor
        self.cylinderWidth    = 10.0
    
        ############################
        
    
    def init_gui(self):
        """
        Initialize gui. 
        """
        #Note that DnaSegment_EditCommand only act as an edit command for an 
        #existing structure. The call to self.propMgr.show() is done only during
        #the call to self.editStructure ..i .e. only after self.struct is 
        #updated. This is done because of the following reason:
        # - self.init_gui is called immediately after entering the command. 
        # - self.init_gui in turn, initialized propMgr object and may also 
        #  show the property manager. The self.propMgr.show routine calls 
        #  an update widget method just before the show. This update method 
        #  updates the widgets based on the parameters from the existing 
        #  structure of the command (self.editCommand.struct)
        #  Although, it checks whether this structure exists, the editCommand
        #  could still have a self.struct attr from a previous run. (Note that 
        #  EditCommand API was written before the command sequencer API and 
        #  it has some loose ends like this. ) -- Ninad 2008-01-22
        self.create_and_or_show_PM_if_wanted(showPropMgr = False)
    
               
    def editStructure(self, struct = None):
        EditCommand.editStructure(self, struct)        
        if self.struct:
            #@@@TEMPORARY CODE            
            assert isinstance(self.struct, DnaSegment)
            #When the structure (segment) is finalized (afterthe  modifications),
            #it will be added to the original DnaGroup to which it belonged 
            #before we began editing (modifying) it. 
            self._parentDnaGroup = self.struct.get_DnaGroup() 
            if DEBUG_DRAW_HANDLES_USING_EXPRS_MODULE:
                self._create_or_update_handles()
  
    def _create_or_update_handles(self):
        """
        EXPERIMENTAL METHOD. this will be called only when the flag 
        DEBUG_DRAW_HANDLES_USING_EXPRS_MODULE is turned on.
        Creates handles or updates handle position if the handles are 
        already defined. This doesn't work as of 2008-01-28. The intention is 
        to just try using exprs module to create a handle. Once that works, 
        this routine will be heavily revised.
        @see: self.editStructure
        @see: DnaSegment_GraphicsMode._drawHandles()
        """
        endPoint1, endPoint2 = self.struct.getAxisEndPoints()       
        
        from constants import white
        
        from VQT import norm
        from drawer import drawcylinder, drawsphere
        
        from exprs.ExprsMeta import ExprsMeta
        from exprs.instance_helpers import IorE_guest_mixin
        from exprs.attr_decl_macros import Instance, State
        
        from exprs.__Symbols__ import _self
        from exprs.Exprs import call_Expr ## , tuple_Expr ### TODO: USE tuple_Expr
        from exprs.Center import Center
        
        from exprs.Rect import Rect # used to make our drag handle appearance
        
        from exprs.DraggableHandle import DraggableHandle_AlongLine
        from exprs.If_expr import If_expr
        
        from prefs_widgets import ObjAttr_StateRef
        
        from exprs.Rect import Sphere
        from exprs.ExprsConstants import ORIGIN, DX, DZ
        from exprs.draggable import DraggableObject
        from exprs.dna_ribbon_view import Cylinder
        
        ##aHandle = DraggableObject(Cylinder((ORIGIN,ORIGIN+DX),1,white))

        #aHandle = Instance( DraggableHandle_AlongLine(
            #appearance = Center(Rect(0.5, 0.5, white)),             
            #origin = endPoint1,             
            #direction = norm(endPoint1 - endPoint2),            
            #sbar_text = "", 
            #range = (0.1, 10)
                          #))
                
        self.aHandle = self.Instance( DraggableHandle_AlongLine(
            appearance = Sphere(2.0, white ),     
            height_ref = call_Expr( ObjAttr_StateRef, _self, 'cylinderWidth'), 
            origin = endPoint1,             
            direction = norm(endPoint1 - endPoint2),            
            sbar_text = "",
            ), 
            index = id(self)
        )
        self.handles.append(self.aHandle)
           
    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr
        propMgr = self.win.createDnaSegmentPropMgr_if_needed(self)
        return propMgr
    
    def _gatherParameters(self):
        """
        Return the parameters from the property manager UI.

        @return: All the parameters (get those from the property manager):
                 - numberOfBases
                 - dnaForm
                 - basesPerTurn
                 - endPoint1
                 - endPoint2
        @rtype:  tuple
        """     
        return self.propMgr.getParameters()
    
    def _createStructure(self):
        """
        Creates and returns the structure (in this case a L{Group} object that 
        contains the DNA strand and axis chunks. 
        @return : group containing that contains the DNA strand and axis chunks.
        @rtype: L{Group}  
        @note: This needs to return a DNA object once that model is implemented        
        """

        params = self._gatherParameters()

        # No error checking in build_struct, do all your error
        # checking in gather_parameters
        numberOfBases, \
                     dnaForm, \
                     dnaModel, \
                     basesPerTurn, \
                     endPoint1, \
                     endPoint2 = params
        
        #If user enters the number of basepairs and hits preview i.e. endPoint1
        #and endPoint2 are not entered by the user and thus have default value 
        #of V(0, 0, 0), then enter the endPoint1 as V(0, 0, 0) and compute
        #endPoint2 using the duplex length. 
        #Do not use '==' equality check on vectors! its a bug. Use same_vals 
        # or Veq instead. 
        if Veq(endPoint1 , endPoint2) and Veq(endPoint1, V(0, 0, 0)):
            endPoint2 = endPoint1 + \
                      self.win.glpane.right*getDuplexLength('B-DNA', 
                                                            numberOfBases)
            

        if numberOfBases < 1:
            msg = redmsg("Cannot to preview/insert a DNA duplex with 0 bases.")
            self.propMgr.updateMessage(msg)
            self.dna = None # Fixes bug 2530. Mark 2007-09-02
            return None

        if dnaForm == 'B-DNA':
            if dnaModel == 'PAM-3':
                dna = B_Dna_PAM3()
            elif dnaModel == 'PAM-5':
                dna = B_Dna_PAM5()
            else:
                print "bug: unknown dnaModel type: ", dnaModel
        else:
            raise PluginBug("Unsupported DNA Form: " + dnaForm)

        self.dna  =  dna  # needed for done msg

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
        
               
        # Create the model tree group node. 
        # Make sure that the 'topnode'  of this part is a Group (under which the
        # DNa group will be placed), if the topnode is not a group, make it a
        # a 'Group' (applicable to Clipboard parts).See part.py
        # --Part.ensure_toplevel_group method. This is an important line
        # and it fixes bug 2585
        self.win.assy.part.ensure_toplevel_group()
        if 1:
            dnaSegment = DnaSegment(self.name, 
                         self.win.assy,
                         self.win.assy.part.topnode,
                         editCommand = self  )
        try:
            # Make the DNA duplex. <dnaGroup> will contain three chunks:
            #  - Strand1
            #  - Strand2
            #  - Axis
            dna.make(dnaSegment, 
                     numberOfBases, 
                     basesPerTurn, 
                     endPoint1,
                     endPoint2)
        

            return dnaSegment

        except (PluginBug, UserError):
            # Why do we need UserError here? Mark 2007-08-28
            dnaSegment.kill()
            raise PluginBug("Internal error while trying to create DNA duplex.")

    
    def _modifyStructure(self, params):
        """
        Modify the structure based on the parameters specified. 
        Overrides EditCommand._modifystructure. This method removes the old 
        structure and creates a new one using self._createStructure. This 
        was needed for the structures like this (Dna, Nanotube etc) . .
        See more comments in the method.
        """    
        assert self.struct
        # parameters have changed, update existing structure
        self._revertNumber()

        # self.name needed for done message
        if self.create_name_from_prefix:
            # create a new name
            name = self.name = gensym(self.prefix) # (in _build_struct)
            self._gensym_data_for_reusing_name = (self.prefix, name)
        else:
            # use externally created name
            self._gensym_data_for_reusing_name = None
                # (can't reuse name in this case -- not sure what prefix it was
                #  made with)
            name = self.name
            
        #@NOTE: Unlike editcommands such as Plane_EditCommand, this 
        #editCommand actually removes the structure and creates a new one 
        #when its modified. We don't yet know if the DNA object model 
        # will solve this problem. (i.e. reusing the object and just modifying
        #its attributes.  Till that time, we'll continue to use 
        #what the old GeneratorBaseClass use to do ..i.e. remove the item and 
        # create a new one  -- Ninad 2007-10-24
        
        self._removeStructure()
        
        self.previousParams = params

        self.struct = self._createStructure()
        #Now append the new structure in self._segmentList (this list of 
        #segments
        #will be provided to the previous command (BuildDna_EditCommand)
        #TODO: Should self._createStructure does the job of appending the 
        #structure 
        #to the list of segments? This fixes bug 2599 
        #(see also BuildDna_PropertyManager.Ok 
        
        if self._parentDnaGroup is not None:
            #Should this be an assertion? (assert self._parentDnaGroup is not 
            #None. For now lets just print a warning if parentDnaGroup is None 
            self._parentDnaGroup.addSegment(self.struct)
            
        return 
