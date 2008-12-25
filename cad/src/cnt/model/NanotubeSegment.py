# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NanotubeSegment.py - ... 

@author: Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

Note: related to DnaStrandOrSegment, from which it was copied and modified.
"""

import foundation.env as env

from utilities.debug import print_compact_stack, print_compact_traceback
from model.chunk import Chunk
from model.chem import Atom
from model.bonds import Bond
from geometry.VQT import V, norm, vlen

from utilities.icon_utilities import imagename_to_pixmap
from utilities.Comparison     import same_vals

def getAllNanotubeSegmentsInPart(assy):
    """
    @return: a list of all NanotubeSegments in the part.
    """        
    selNanotubeSegmentList = []
    def addSelectedNanotubeSegment(obj, ntSegmentList = selNanotubeSegmentList):
        if isinstance(obj, NanotubeSegment):
            ntSegmentList += [obj]
        return
    assy.part.topnode.apply2all(addSelectedNanotubeSegment)
    return selNanotubeSegmentList


from foundation.LeafLikeGroup import LeafLikeGroup

_superclass = LeafLikeGroup

class NanotubeSegment(LeafLikeGroup):
    """
    Model object which represents a Nanotube Segment inside a Nanotube Group.

    Internally, this is just a specialized Group containing a single chunk,
    itself containing all the atoms of a nanotube.
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('NanotubeSegment',)
    
    nanotube = None
    
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
    
    # This partially fixes bug 2914. Copying now works, but the following
    # "warning" is printed to stdout:
    # ****************** needs _copyOfObject: <cnt.model.Nanotube.Nanotube instance at 0x164FC030>
    # I'm guessing this means that we need to override abstract method 
    # _copyOfObject() of DataMixin, but I'd like to discuss this with Bruce first.
    # I also have confirmed that there is still a bug when editing the 
    # copied nanotube (it will automatically move from the clipboard
    # to the part after it is resized).
    # Mark 2008-07-09.
    copyable_attrs = _superclass.copyable_attrs + ('nanotube',)
    
    def writemmp_other_info_opengroup(self, mapping): #bruce 080507 refactoring
        """
        """
        #bruce 080507 refactoring (split this out of Group.writemmp)
        # (I think the following condition is always true, but I didn't
        #  prove this just now, so I left in the test for now.)
        encoded_classifications = self._encoded_classifications()
        if encoded_classifications == "NanotubeSegment":
            # This is a nanotube segment, so write the parameters into an info
            # record so we can read and restore them in the next session. 
            # --Mark 2008-04-12
            assert self.nanotube
            mapping.write("info opengroup nanotube-parameters = %d, %d, %s, %s\n" \
                          % (self.nanotube.getChiralityN(),
                             self.nanotube.getChiralityM(),
                             self.nanotube.getType(),
                             self.nanotube.getEndings()))
            pass
        return

    def readmmp_info_opengroup_setitem( self, key, val, interp ):
        """
        [extends superclass method]
        """
        #bruce 080507 refactoring (split this out of the superclass method)
        if key == ['nanotube-parameters']:
            # val includes all the parameters, separated by commas.
            n, m, type, endings = val.split(",")
            self.n = int(n)
            self.m = int(m)
            self.type = type.lstrip()
            self.endings = endings.lstrip()
            # Create the nanotube.
            from cnt.model.Nanotube import Nanotube
            self.nanotube = Nanotube() # Returns a 5x5 CNT.
            self.nanotube.setChirality(self.n, self.m)
            self.nanotube.setType(self.type)
            self.nanotube.setEndings(self.endings)
            # The endpoints are recomputed every time it is edited.
        else:
            _superclass.readmmp_info_opengroup_setitem( self, key, val, interp)
        return
    
    def edit(self):
        """
        Edit this NanotubeSegment. 
        @see: NanotubeSegment_EditCommand
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('NANOTUBE_SEGMENT')
        assert commandSequencer.currentCommand.commandName == 'NANOTUBE_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)
        return

    def getAxisVector(self, atomAtVectorOrigin = None):
        """
        Returns the unit axis vector of the segment (vector between two axis 
        end points)
        """
        # REVIEW: use common code for this method? [bruce 081217 comment]
        endPoint1, endPoint2 = self.nanotube.getEndPoints()
                
        if endPoint1 is None or endPoint2 is None:
            return V(0, 0, 0)
        
        #@see: RotateAboutAPoint command. The following code is disabled 
        #as it has bugs (not debugged but could be in 
        #self.nanotube.getEndPoints). So, rotate about a point won't work for 
        #rotating a nanotube. -- Ninad 2008-05-13
      
        ##if atomAtVectorOrigin is not None:
            ###If atomAtVectorOrigin is specified, we will return a vector that
            ###starts at this atom and ends at endPoint1 or endPoint2 . 
            ###Which endPoint to choose will be dicided by the distance between
            ###atomAtVectorOrigin and the respective endPoints. (will choose the 
            ###frthest endPoint
            ##origin = atomAtVectorOrigin.posn()
            ##if vlen(endPoint2 - origin ) > vlen(endPoint1 - origin):
                ##return norm(endPoint2 - endPoint1)
            ##else:
                ##return norm(endPoint1 - endPoint2)
        
        return norm(endPoint2 - endPoint1)
    
    def setProps(self, props):
        """
        Sets some properties. These will be used while editing the structure. 
        (but if the structure is read from an mmp file, this won't work. As a 
        fall back, it returns some constant values) 
        @see: InsertNanotube_EditCommand.createStructure which calls this method. 
        @see: self.getProps, NanotubeSegment_EditCommand.editStructure        
        """
        (_n, _m), _type, _endings, (_endPoint1, _endPoint2) = props
        
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
        # Recompute the endpoints in case this nanotube was read from
        # MMP file (which means this nanotube doesn't have endpoint 
        # parameters yet). 
        self.nanotube.computeEndPointsFromChunk(self.members[0])
        
        return self.nanotube.getParameters()
        
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
        whether self is an ancestor. (returns True even for logical contents)
        
        @see: self.get_all_content_chunks() (inherited from LeafLikeGroup)
        @see: NanotubeSegment_GraphicsMode.leftDrag
        """
        # TODO: this needs cleanup (it looks like it's made of two alternative
        # implems, one after the other), generalization (to use some centrally
        # defined notion of logical contents), and optimization. Also, if it
        # is still defined in more than one class, common code should be used.
        # [bruce 080507/081217 comment]
        
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
                # review: could optimize by (c.dad is self), at least in this class
                # [bruce 081217 comment]
                return True        
        
        #NOTE: Need to check if the isinstance checks are acceptable (apparently
        #don't add any import cycle) 
        if isinstance(obj, Atom):       
            chunk = obj.molecule
            if chunk.dad is self:
                return True
            else:
                return False
        elif isinstance(obj, Bond):
            chunk1 = obj.atom1.molecule
            chunk2 = obj.atom1.molecule            
            if (chunk1.dad is self) or (chunk2.dad is self):
                return True               
        elif isinstance(obj, Chunk):
            if obj.dad is self:
                return True
        return False
    
    def node_icon(self, display_prefs):
        # REVIEW: use common code for this method? [bruce 081217 comment]
        del display_prefs
        
        if self.all_content_is_hidden():
            return imagename_to_pixmap( self.hide_iconPath)
        else:
            return imagename_to_pixmap( self.iconPath)
    
    def permit_as_member(self, node, pre_updaters = True, **opts):
        """
        [friend method for enforce_permitted_members_in_groups and subroutines]

        Does self permit node as a direct member,
        when called from enforce_permitted_members_in_groups with
        the same options as we are passed?

        @rtype: boolean

        [extends superclass method]
        """
        # this method was copied from DnaStrandOrSegment and edited for this class
        if not LeafLikeGroup.permit_as_member(self, node, pre_updaters, **opts):
            # reject if superclass would reject [bruce 081217]
            return False
        del opts
        assy = self.assy
        res = isinstance( node, assy.Chunk) #@ NEEDS SOMETHING MORE.
        return res
    pass # end of class NanotubeSegment
                
# end
