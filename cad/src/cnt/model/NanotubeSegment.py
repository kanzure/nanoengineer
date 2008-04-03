# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NanotubeSegment.py - ... 

@author: Bruce, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
import foundation.env as env

from utilities.debug import print_compact_stack, print_compact_traceback
from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond
from geometry.VQT import V, norm, vlen

from foundation.Group import Group

from utilities.icon_utilities import imagename_to_pixmap
from utilities.Comparison     import same_vals

class NanotubeSegment(Group):
    """
    Model object which represents a Nanotube Segment inside a Nanotube Group.

    Internally, this is just a specialized Group containing a single chunk,
    itself containing all the atoms of a nanotube.
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('NanotubeSegment',)
    
    _nanotubeRise = None
    _endPoint1 = None
    _endPoint2 = None
        # TODO: undo or copy code for those attrs,
        # and updating them when the underlying structure changes.
        # But maybe that won't be needed, if they are replaced
        # by computing them from the atom geometry as needed.
        # [bruce 080227 comment]
        
    autodelete_when_empty = True
        # (but only if current command permits that for this class --
        #  see comment near Group.autodelete_when_empty for more info,
        #  and implems of Command.keep_empty_group)
        
    iconPath = "ui/modeltree/NanotubeSegment.png"
    hide_iconPath = "ui/modeltree/NanotubeSegment-hide.png"
    
    def __init__(self, name, assy, dad, members = (), editCommand = None):
        
        self._nanotubeRise = 3.18 #@      
        Group.__init__(self, 
                       name, 
                       assy, 
                       dad, 
                       members = members, 
                       editCommand = editCommand)
        ###BUG: not all callers pass an editCommand. It would be better
        # to figure out on demand which editCommand would be appropriate.
        # [bruce 080227 comment]
        return
        
    def edit(self):
        """
        Edit this NanotubeSegment. 
        @see: NanotubeSegment_EditCommand
        """
        
        commandSequencer = self.assy.w.commandSequencer       
        
        if commandSequencer.currentCommand.commandName != "NANOTUBE_SEGMENT":
            commandSequencer.userEnterTemporaryCommand('NANOTUBE_SEGMENT')
            
        assert commandSequencer.currentCommand.commandName == 'NANOTUBE_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)
    

    #Following methods are likely to be revised in a fully functional dna data 
    # model. These methods are mainly created to get working many core UI 
    # operations for Rattlesnake.  -- Ninad 2008-02-01
    
    def get_all_content_chunks(self):
        """
        Return all the chunks contained within this NanotubeSegment.
        
        @note: there is only one chunk inside this group.
        """
        all_content_chunk_list = []
        
        for member in self.members:
            if isinstance(member, Chunk):
                all_content_chunk_list.append(member)
        
        return all_content_chunk_list 
    
    def getAxisVector(self):
        """
        Returns the unit axis vector of the segment (vector between two axis 
        end points)
        """
        endPoint1, endPoint2 = self.nanotube.getEndPoints()
        if endPoint1 is not None and endPoint2 is not None:
            return norm(endPoint2 - endPoint1)
        else:
            return V(0, 0, 0)
    
    def setProps(self, props):
        """
        Sets some properties. These will be used while editing the structure. 
        (but if the structure is read from an mmp file, this won't work. As a 
        fall back, it returns some constant values) 
        @see: InsertNanotube_EditCommand.createStructure which calls this method. 
        @see: self.getProps, NanotubeSegment_EditCommand.editStructure        
        """        
        _chirality, _type, _endings, _endPoints = props
        
        _n, _m = _chirality
        _endPoint1, _endPoint2 = _endPoints
        
        from cnt.model.Nanotube import Nanotube
        self.nanotube = Nanotube()
        self.nanotube.setChirality(_n, _m)
        self.nanotube.setType(_type)
        self.nanotube.setEndings(_endings)
        self.nanotube.setEndPoints(_endPoint1, _endPoint2)
        
    def getProps(self):
        """
        Returns nanotube parameters necessary for editing.
        
        @see: NanotubeSegment_EditCommand.editStructure where it is used. 
        @see: NanotubeSegment_PropertyManager.getParameters
        @see: NanotubeSegmentEditCommand._createStructure        
        """
        
        #@ BUG: nanotube does not exist if it wasn't created during the
        # current session (i.e. the nanotube was loaded from an MMP file).
        # Need to save/restore these params in the MMP file. --Mark 2008-04-01.
        props = (self.nanotube.getChirality(),
                 self.nanotube.getType(),
                 self.nanotube.getEndPoints())
        return props
    
    def getNanotubeGroup(self):
        """
        Return the NanotubeGroup we are contained in, or None if we're not
        inside one.
        """
        return self.parent_node_of_class( self.assy.NanotubeGroup)
        
    def isAncestorOf(self, obj):
        """
        Checks whether the object <obj> is contained within the NanotubeSegment
        
        Example: If the object is an Atom, it checks whether the 
        atom's chunk is a member of this NanotubeSegment (chunk.dad is self)
        
        It also considers all the logical contents of the NanotubeSegment to determine
        whetehr self is an ancestor. (returns True even for logical contents)
        
                
        @see: self.get_all_content_chunks()
        @see: NanotubeSegment_GraphicsMode.leftDrag
        
        @Note: when dna data model is fully implemented, the code below that is 
        flaged 'pre-Dna data model' and thus the method should be revised 
        """
        
        #start of POST DNA DATA MODEL IMPLEMENTATION ===========================
        c = None
        if isinstance(obj, Atom):       
            c = obj.molecule                 
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if chunk1 is chunk2:
                c = chunk1
        elif isinstance(obj, Chunk):
            c = obj
        
        if c is not None:
            if c in self.get_all_content_chunks():
                return True        
        #end of POST DNA DATA MODEL IMPLEMENTATION =============================    
        
        #start of PRE- DNA DATA MODEL IMPLEMENTATION ===========================
        
        #NOTE: Need to check if the isinstance checks are acceptable (apparently
        #don't add any import cycle) Also this method needs to be revised 
        #after we completely switch to dna data model. 
        if isinstance(obj, Atom):       
            chunk = obj.molecule                
            if chunk.dad is self:
                return True
            else:
                ladder = getattr(chunk, 'ladder', None)
                if ladder:
                    pass
                
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if (chunk1.dad is self) or (chunk2.dad is self):
                return True               
        elif isinstance(obj, Chunk):
            if obj.dad is self:
                return True
        #end of PRE- DNA DATA MODEL IMPLEMENTATION ===========================
                
        return False
    
    def node_icon(self, display_prefs):        
        del display_prefs # unused
        
        if self.all_content_is_hidden():    
            return imagename_to_pixmap( self.hide_iconPath)
        else:
            return imagename_to_pixmap( self.iconPath)        
                
# end
