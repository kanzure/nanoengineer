# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
PeptideGroup.py - ... 

@author: Bruce, Mark
@version: $Id: PeptideGroup.py 12414 2008-04-09 05:22:11Z marksims $
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from foundation.Group import Group

from utilities.constants import gensym

from utilities.icon_utilities import imagename_to_pixmap

from utilities import debug_flags

from utilities.debug import print_compact_stack


class PeptideGroup(Group):
    """
    Model object which packages together some Dna Segments, Dna Strands,
    and other objects needed to represent all their PAM atoms and markers.

    Specific kinds of Group member contents include:
    - PeptideSegments (optionally inside Groups)
    - Groups (someday might be called Blocks when they occur in this context;
       note that class Block is deprecated and should not be used for these)
    - DnaMarkers (a kind of Jig, always inside an owning PeptideSegment)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes. [nim?]
    """
    
    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('PeptideGroup',)
    
    # Open/closed state of the Dna Group in the Model Tree --
    # default closed.
    # OBSOLETE COMMENT: Note: this is ignored by the Model Tree code
    # (since we inherit from Block), but whether it affects any other code
    # (e.g. a PM display widget) is not yet decided.
    open = False
    
    autodelete_when_empty = True
        # (but only if current command permits that for this class --
        #  see comment near Group.autodelete_when_empty for more info,
        #  and implems of Command.keep_empty_group)
    
    def node_icon(self, display_prefs):
        """
        Model Tree node icon for the Peptide group node
        @see: Group.all_content_is_hidden() 
        """        
        open = display_prefs.get('open', False)
        if open:
            if self.all_content_is_hidden():    
                return imagename_to_pixmap("modeltree/PeptideGroup-expanded-hide.png")
            else:
                return imagename_to_pixmap("modeltree/PeptideGroup-expanded.png")
        else:
            if self.all_content_is_hidden():    
                return imagename_to_pixmap("modeltree/PeptideGroup-collapsed-hide.png")
            else:
                return imagename_to_pixmap("modeltree/PeptideGroup-collapsed.png")
    
    # Note: some methods below this point are examples or experiments or stubs,
    # and are likely to be revised significantly or replaced.
    # [bruce 080115 comment]
    
    # example method:
    def getSegments(self):
        """
        Return a list of all our PeptideSegment objects.
        """
        return self.get_topmost_subnodes_of_class(self.assy.PeptideSegment)
    
    def isEmpty(self):
        """
        Returns True if there are no Peptide chunks as its members 
        (Returns True even when there are empty PeptideSegment objects inside)
        
        @see: BuildPeptide_EditCommand._finalizeStructure where this test is used. 
        """
        #May be for the short term, we can use self.getAtomList()? But that 
        #doesn't ensure if the DnaGroup always has atom of type either 
        #'strand' or 'axis' . 
        if len(self.getSegments()) == 0:
            return True
        else:
            return False

    def addSegment(self, segment):
        """
        Adds a new segment object for this dnaGroup.
        
        @param segment: The PeptideSegment to be added to this PeptideGroup object
        @type: B{PeptideSegment}  
        """       
        self.addchild(segment)
    
    def getProps(self):
        """
	Method to support Dna duplex editing. see Group.__init__ for 
	a comment
        
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it supply the Dna Segment list (children) and then add 
        #individual segments when setProps is called??
        # [probably not; see B&N email discussion from when this comment was added]
        if self.editCommand:
            props = ()
            return props

    def setProps(self, props):
        """
	Method  to support Dna duplex editing. see Group.__init__ for 
	a comment
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it accept the Dna Segment list and then add individual segments?
        pass
    
    def edit(self):
        """
        @see: Group.edit()
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('BUILD_Peptide', always_update = True)
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'BUILD_Peptide'
        currentCommand.editStructure(self)
    
    
    def getSelectedSegments(self):
        """
        Returns a list of segments whose all members are selected.        
        @return: A list containing the selected strand objects
                 within self.
        @rtype: list
        """
        #TODO: This is a TEMPORARY KLUDGE  until Dna model is fully functional. 
        #Must be revised. Basically it returns a list of PeptideSegments whose 
        #all members are selected. 
        #See BuildDna_PropertyManager._currentSelectionParams() where it is used
        #-- Ninad 2008-01-18
        segmentList = self.getSegments()
        
        selectedSegmentList = []    
                                    
        for segment in segmentList:
            
            pickedNodes = []
            unpickedNodes = []
            
            def func(node):
                if isinstance(node, self.assy.Chunk):
                    if not node.picked:
                        unpickedNodes.append(node)
                    else:
                        pickedNodes.append(node)   
                        
            segment.apply2all(func)
            
            if len(unpickedNodes) == 0 and pickedNodes:
                selectedSegmentList.append(segment)  
                
        return selectedSegmentList
    
    def getAtomList(self):
        """
        Return a list of all atoms contained within this PeptideGroup
        """
        atomList = []
        def func(node):
            if isinstance(node, self.assy.Chunk):
                atomList.extend(node.atoms.itervalues())
        
        self.apply2all(func)
        return atomList
    
    def draw_highlighted(self, glpane, color):
        """
        Draw the Peptide segment chunks as highlighted. (Calls the related 
        methods in the chunk class)
        @param: GLPane object 
        @param color: The highlight color
        @see: Chunk.draw_highlighted()
        @see: SelectChunks_GraphicsMode.draw_highlightedChunk()
        @see: SelectChunks_GraphicsMode._get_objects_to_highlight()
        @see: SelectChunks_GraphicsMode._is_dnaGroup_highlighting_enabled()   #@     
        """  
        for c in self.getSegments():
            c.draw_highlighted(glpane, color)
            
    pass # end of class PeptideGroup

# ==

