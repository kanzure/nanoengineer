# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PeptideSegment.py - ... 

WARNING: this class is reportedly not used and will soon be moved to outtakes.

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

from foundation.LeafLikeGroup import LeafLikeGroup

_superclass = LeafLikeGroup

class PeptideSegment(LeafLikeGroup):
    """
    Model object which represents a Peptide Segment inside a Peptide Group.

    Internally, this is just a specialized Group containing a single chunk,
    itself containing all the atoms of a Peptide.
    """

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('PeptideSegment',)
    
    Peptide = None
    
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
        
    iconPath = "ui/modeltree/PeptideSegment.png"
    hide_iconPath = "ui/modeltree/PeptideSegment-hide.png"
    
    def writemmp_other_info_opengroup(self, mapping): #bruce 080507 refactoring
        """
        """
        #bruce 080507 refactoring (split this out of Group.writemmp)
        # (I think the following condition is always true, but I didn't
        #  prove this just now, so I left in the test for now.)
        encoded_classifications = self._encoded_classifications()
        if encoded_classifications == "PeptideSegment":
            # This is a Peptide segment, so write the parameters into an info
            # record so we can read and restore them in the next session. 
            # --Mark 2008-04-12
            assert self.Peptide
            mapping.write("info opengroup Peptide-parameters = %d, %d, %s, %s\n" \
                          % (self.Peptide.getChiralityN(),
                             self.Peptide.getChiralityM(),
                             self.Peptide.getType(),
                             self.Peptide.getEndings()))
            pass
        return

    def readmmp_info_opengroup_setitem( self, key, val, interp ):
        """
        [extends superclass method]
        """
        #bruce 080507 refactoring (split this out of the superclass method)
        if key == ['Peptide-parameters']:
            # val includes all the parameters, separated by commas.
            n, m, type, endings = val.split(",")
            self.n = int(n)
            self.m = int(m)
            self.type = type.lstrip()
            self.endings = endings.lstrip()
            # Create the Peptide.
            from cnt.model.Peptide import Peptide
            self.Peptide = Peptide() # Returns a 5x5 CNT.
            self.Peptide.setChirality(self.n, self.m)
            self.Peptide.setType(self.type)
            self.Peptide.setEndings(self.endings)
            # The endpoints are recomputed every time it is edited.
        else:
            _superclass.readmmp_info_opengroup_setitem( self, key, val, interp)
        return
    
    def edit(self):
        """
        Edit this PeptideSegment. 
        @see: PeptideSegment_EditCommand
        """
        
        commandSequencer = self.assy.w.commandSequencer       
        
        commandSequencer.userEnterCommand('Peptide_SEGMENT')
        assert commandSequencer.currentCommand.commandName == 'Peptide_SEGMENT'
        commandSequencer.currentCommand.editStructure(self)
        
    def getAxisVector(self, atomAtVectorOrigin = None):
        """
        Returns the unit axis vector of the segment (vector between two axis 
        end points)
        """
        # REVIEW: use common code for this method? [bruce 081217 comment]
        endPoint1, endPoint2 = self.Peptide.getEndPoints()
                
        if endPoint1 is None or endPoint2 is None:
            return V(0, 0, 0)
        
        #@see: RotateAboutAPoint command. The following code is disabled 
        #as it has bugs (not debugged but could be in 
        #self.Peptide.getEndPoints). So, rotate about a point won't work for 
        #rotating a Peptide. -- Ninad 2008-05-13
      
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
        @see: InsertPeptide_EditCommand.createStructure which calls this method. 
        @see: self.getProps, PeptideSegment_EditCommand.editStructure        
        """
        (_n, _m), _type, _endings, (_endPoint1, _endPoint2) = props
        
        from cnt.model.Peptide import Peptide
        self.Peptide = Peptide()
        self.Peptide.setChirality(_n, _m)
        self.Peptide.setType(_type)
        self.Peptide.setEndings(_endings)
        self.Peptide.setEndPoints(_endPoint1, _endPoint2)
        
    def getProps(self):
        """
        Returns Peptide parameters necessary for editing.
        
        @see: PeptideSegment_EditCommand.editStructure where it is used. 
        @see: PeptideSegment_PropertyManager.getParameters
        @see: PeptideSegmentEditCommand._createStructure        
        """
        # Recompute the endpoints in case this Peptide was read from
        # MMP file (which means this Peptide doesn't have endpoint 
        # parameters yet). 
        self.Peptide.computeEndPointsFromChunk(self.members[0])
        
        return self.Peptide.getParameters()
        
    def getPeptideGroup(self):
        """
        Return the PeptideGroup we are contained in, or None if we're not
        inside one.
        """
        return self.parent_node_of_class( self.assy.PeptideGroup)
    
    def isAncestorOf(self, obj):
        """
        Checks whether the object <obj> is contained within the PeptideSegment
        
        Example: If the object is an Atom, it checks whether the 
        atom's chunk is a member of this PeptideSegment (chunk.dad is self)
        
        It also considers all the logical contents of the PeptideSegment to determine
        whether self is an ancestor. (returns True even for logical contents)
        
        @see: self.get_all_content_chunks()
        @see: PeptideSegment_GraphicsMode.leftDrag
        """
        # see my comments in the NanotubeSegment version [bruce 081217]
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
        
    pass # end of class PeptideSegment
                
# end
