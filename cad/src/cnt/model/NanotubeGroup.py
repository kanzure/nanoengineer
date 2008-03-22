# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
NanotubeGroup.py - ... 

@author: Bruce, Mark
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from dna.model.Block import Block
from model.chunk import Chunk

from utilities.constants import gensym

from utilities.icon_utilities import imagename_to_pixmap

from cnt.updater.nanotube_updater_globals import _f_NanotubeGroup_for_homeless_objects_in_Part

from utilities import debug_flags


# Following import is disabled. See addSegment method for reason.
## from cnt_model.NanotubeSegment import NanotubeSegment

class NanotubeGroup(Block): ### NEEDS REVIEW after recent changes to usage of Block in DnaGroup [bruce 080318 comment]
    """
    Model object which packages together some Cnt Segments, Cnt Strands,
    and other objects needed to represent all their PAM atoms and markers.

    The contents are not directly visible to the user in the model tree,
    except for Blocks (fyi, this behavior comes from our Block superclass,
    which is a kind of Group).
    
    But internally, most of the contents are Nodes which can be stored
    in mmp files, copied, and undo-scanned in the usual ways.

    Specific kinds of Group member contents include:
    - CntStrands (optionally inside Blocks)
    - NanotubeSegments (ditto)
    - Blocks (a kind of Group)
    - CntMarkers (a kind of Jig, probably always inside an owning
      CntStrand or NanotubeSegment)
    - specialized chunks for holding PAM atoms:
      - CntAxisChunk (undecided whether these will live inside NanotubeSegments
        they belong to, but probably they will)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes.
    """
    
    # The iconPath specifies path(string) of an icon that represents the 
    # objects of this class  
    iconPath = "modeltree/CNT.png"    
    hide_iconPath = "modeltree/CNT-hide.png"

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('NanotubeGroup',)
    
    # Open/closed state of the Cnt Group in the Model Tree --
    # default closed. Note: this is ignored by the Model Tree code
    # (since we inherit from Block), but whether it affects any other code
    # (e.g. a PM display widget) is not yet decided.
    open = False
    
    autodelete_when_empty = True
        # (but only if current command permits that for this class --
        #  see comment near Group.autodelete_when_empty for more info,
        #  and implems of Command.keep_empty_group)
    
    def node_icon(self, display_prefs):
        """
        Model Tree node icon for the cnt group node
        @see: Group.all_content_is_hidden() 
        """
        del display_prefs # unused
        
        if self.all_content_is_hidden():    
            return imagename_to_pixmap( self.hide_iconPath)
        else:
            return imagename_to_pixmap( self.iconPath)     

    def make_CntStrandOrSegment_for_marker(self, controlling_marker): # review: wholechain arg needed? @@@
        """
        The given CntMarker is either newly made to control a wholechain,
        or old but newly controlling it; but it has no CntStrandOrSegment.
        
        Make and return a new CntStrand or NanotubeSegment
        (ask marker what class to use)
        inside self (review: inside some Block in self?),
        perhaps making use of info in controlling_marker
        to help decide how to initialize some of its attributes.
        
        (Assume calling code will later move all chunks
        and markers from marker's wholechain into the new CntStrandOrSegment,
        and will store references to it as needed
        into controlling_marker and/or its wholechain,
        so don't do those things here.)
        """
        assert not self.killed(), \
               "self must not be killed in %r.make_CntStrandOrSegment_for_marker" % self
        class1 = controlling_marker.CntStrandOrSegment_class()
        name = gensym(class1.__name__.split('.')[-1]) ###STUB -- should use class constant prefix, ensure unique names
            # todo: sensible name? (if we split a seg, is name related to old seg; if so how?)
        assy = controlling_marker.assy # it's a Jig so it has one
        obj = class1(name, assy, None) # note: these args are for Group.__init__
        self.addchild(obj) # note: this asserts self.assy is not None
            # (but it can't assert not self.killed(), see its comment for why)
        return obj
    
    # Note: some methods below this point are examples or experiments or stubs,
    # and are likely to be revised significantly or replaced.
    # [bruce 080115 comment]
    
    # example method:
    def get_segments(self):
        """
        Return a list of all our NanotubeSegment objects.
        """
        return self.get_topmost_subnodes_of_class(self.assy.NanotubeSegment)

    def addSegment(self, segment):
        """
        Adds a new cnt segment object to self.
        
        @param segment: The NanotubeSegment to be added to this NanotubeGroup object
        @type: B{NanotubeSegment}  
        """
        # importing NanotubeSegment created an import cycle which throws error. 
        # So this isinstance check is disabled for now.
        ## assert isinstance(segment, NanotubeSegment)
        
        self.addchild(segment)
    
    def getProps(self):
        """
	Method to support Cnt editing. see Group.__init__ for 
	a comment
        
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it supply the Cnt Segment list (children) and then add 
        #individual segments when setProps is called??
        # [probably not; see B&N email discussion from when this comment was added]
        if self.editCommand:
            props = ()
            return props

    def setProps(self, props):
        """
	Method  to support Cnt editing. see Group.__init__ for 
	a comment
        THIS IS THE DEFAULT IMPLEMENTATION. TO BE MODIFIED
	"""
        #Should it accept the Cnt Segment list and then add individual segments?
        pass
    
    def edit(self):
        """
        @see: Group.edit()
        """
        commandSequencer = self.assy.w.commandSequencer
        commandSequencer.userEnterCommand('BUILD_NANOTUBE')
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'BUILD_NANOTUBE'
        currentCommand.editStructure(self)
        
    def getAxisChunks(self):
        """
        Returns a list of Axis chunks inside a NanotubeGroup object
        
        @return: A list containing all the axis chunks
                 within self.
        @rtype: list
        """
        #TO BE REVISED. It uses isinstance check for  
        #Chunk and some additional things to find out a list of strands inside
        # a NanotubeGroup -- Ninad 2008-02-02       
        axisChunkList = []
        def filterAxisChunks(node):
            if isinstance(node, Chunk): # and node.isAxisChunk():
                axisChunkList.append(node)    
                
        self.apply2all(filterAxisChunks)
        
        return axisChunkList
    
    def isEmpty(self):
        """
        Returns True if there are no axis or strand chunks as its members 
        (Returns True even when there are empty NanotubeSegment objects inside)
        
        TODO: It doesn't consider other possibilitis such as hairpins . 
        In general it relies on what getAxisChunks and getStrands returns 
        (which in turn use 'Chunk' object to determine these things.)
        This method must be revised in the near future in a fully functional
        cnt data model
        @see: BuildNanotube_EditCommand._finalizeStructure where this test is
        used. 
        """
        #May be for the short term, we can use self.getAtomList()? But that 
        #doesn't ensure if the NanotubeGroup always has atom of type either 
        #'strand' or 'axis' . 
        if len(self.getAxisChunks()) == 0:
            return True
        else:
            return False
    
    def getSelectedSegments(self):
        """
        Returns a list of segments whose all members are selected.        
        @return: A list containing the selected strand objects
                 within self.
        @rtype: list
        """
        #TODO: This is a TEMPORARY KLUDGE  until Cnt model is fully functional. 
        #Must be revised. Basically it returns a list of NanotubeSegments whose 
        #all members are selected. 
        #See BuildNanotube_PropertyManager._currentSelectionParams() where it is used
        #-- Ninad 2008-01-18
        segmentList = self.get_segments()
        
        selectedSegmentList = []    
                                    
        for segment in segmentList:
            
            pickedNodes = []
            unpickedNodes = []
            
            def func(node):
                if isinstance(node, Chunk):
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
        Return a list of all atoms cotained within this NanotubeGroup
        """
        atomList = []
        def func(node):
            if isinstance(node, Chunk):
                atomList.extend(node.atoms.itervalues())
        
        self.apply2all(func)
        return atomList
    
    def draw_highlighted(self, glpane, color):
        """
        Draw the strand and axis chunks as highlighted. (Calls the related 
        methods in the chunk class)
        @param: GLPane object 
        @param color: The highlight color
        @see: Chunk.draw_highlighted()
        @see: SelectChunks_GraphicsMode.draw_highlightedChunk()
        @see: SelectChunks_GraphicsMode._get_objects_to_highlight()
        @see: SelectChunks_GraphicsMode._is_cntGroup_highlighting_enabled()        
        """  
        for c in self.getStrands():
            c.draw_highlighted(glpane, color)
        for c in self.getAxisChunks():
            c.draw_highlighted(glpane, color)
   
 
    pass # end of class NanotubeGroup

# ==

def find_or_make_NanotubeGroup_for_homeless_object(node):
    """
    All CNT objects found outside of a NanotubeGroup during one run of the cnt updater
    in one Part should be put into one new NanotubeGroup at the end of that Part.
    This is a fallback, since it only happens if we didn't sanitize NanotubeGroups
    when reading a file, or due to bugs in Cnt-related user ops,
    or a user running an ordinary op on CNT that our UI is supposed to disallow.
    So don't worry much about prettiness, just correctness,
    though don't gratuitously discard info.

    The hard part is "during one run of the cnt updater". We'll let it make a
    global dict from Part to this NanotubeGroup, and discard it after every run
    (so no need for this dict to be weak-keyed).

    If we have to guess the Part, we'll use the node's assy's current Part
    (but complain, since this probably indicates a bug).
    """
    part = node.part or node.assy.part
    assert part
    if not node.part:
        print "likely bug: %r in %r has no .part" % \
              (node, node.assy)
    try:
        res = _f_NanotubeGroup_for_homeless_objects_in_Part[part]
    except KeyError:
        res = None
    if res:
        # found one -- make sure it's still ok
        # maybe: also make sure it's still in the same part, assy, etc.
        # (not urgent, now that this only lasts for one run of the updater)
        if res.killed():
            # discard it, after complaining [bruce 080218 bugfix for when this
            # got killed by user; works, but now should never happen due to the
            # better fix of calling clear_updater_run_globals() at start and end
            # of every updater run]
            print "\nBUG: _f_NanotubeGroup_for_homeless_objects_in_Part[%r] " \
                  "found %r which is killed -- discarding it" % \
                  (part, res)
            res = None
    if not res:
        res = _make_NanotubeGroup_for_homeless_objects_in_Part(part)
        _f_NanotubeGroup_for_homeless_objects_in_Part[part] = res
    return res

def _make_NanotubeGroup_for_homeless_objects_in_Part(part):
    # not needed, done in addnode: part.ensure_toplevel_group()
    name = gensym("fallback NanotubeGroup")
    assy = part.assy #k
    dad = None
    cntGroup = NanotubeGroup(name, assy, dad) # same args as for Group.__init__
    part.addnode(cntGroup)
    if debug_flags.DEBUG_CNT_UPDATER:
        print "cnt_updater: made new cntGroup %r" % cntGroup, \
              "(bug or unfixed mmp file)"
    return cntGroup
    
# end