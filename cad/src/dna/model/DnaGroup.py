# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
DnaGroup.py - ...

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from foundation.Group import Group

from utilities.constants import gensym

from utilities.icon_utilities import imagename_to_pixmap

from dna.updater.dna_updater_globals import _f_DnaGroup_for_homeless_objects_in_Part

from utilities import debug_flags

from utilities.debug import print_compact_stack


class DnaGroup(Group):
    """
    Model object which packages together some Dna Segments, Dna Strands,
    and other objects needed to represent all their PAM atoms and markers.

    Specific kinds of Group member contents include:
    - DnaStrands (optionally inside Groups)
    - DnaSegments (ditto)
    - Groups (someday might be called Blocks when they occur in this context;
       note that class Block is deprecated and should not be used for these)
    - DnaMarkers (a kind of Jig, always inside an owning
      DnaStrand or DnaSegment)
    - specialized chunks for holding PAM atoms:
      - DnaAxisChunk (these live inside the DnaSegments they belong to)
      - DnaStrandChunk (these live inside their DnaStrands)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes. [nim?]
    """

    # The iconPath specifies path(string) of an icon that represents the
    # objects of this class
    iconPath = "modeltree/DNA.png"
    hide_iconPath = "modeltree/DNA-hide.png"

    # This should be a tuple of classifications that appear in
    # files_mmp._GROUP_CLASSIFICATIONS, most general first.
    # See comment in class Group for more info. [bruce 080115]
    _mmp_group_classifications = ('DnaGroup',)

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
        Model Tree node icon for the dna group node
        @see: Group.all_content_is_hidden()
        """
        del display_prefs # unused

        if self.all_content_is_hidden():
            return imagename_to_pixmap( self.hide_iconPath)
        else:
            return imagename_to_pixmap( self.iconPath)


    def make_DnaStrandOrSegment_for_marker(self, controlling_marker): # review: wholechain arg needed? @@@
        """
        The given DnaMarker is either newly made to control a wholechain,
        or old but newly controlling it; but it has no DnaStrandOrSegment.

        Make and return a new DnaStrand or DnaSegment
        (ask marker what class to use)
        inside self (review: inside some Group inside self?),
        perhaps making use of info in controlling_marker
        to help decide how to initialize some of its attributes.

        (Assume calling code will later move all chunks
        and markers from marker's wholechain into the new DnaStrandOrSegment,
        and will store references to it as needed
        into controlling_marker and/or its wholechain,
        so don't do those things here.)
        """
        assert not self.killed(), \
               "self must not be killed in %r.make_DnaStrandOrSegment_for_marker" % self
        class1 = controlling_marker.DnaStrandOrSegment_class()
        name = gensym(class1.__name__.split('.')[-1], self.assy)
            ###STUB -- should use class constant prefix
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
        Return a list of all our DnaSegment objects.
        """
        return self.get_topmost_subnodes_of_class(self.assy.DnaSegment)

    def addSegment(self, segment):
        """
        Adds a new segment object for this dnaGroup.

        @param segment: The DnaSegment to be added to this DnaGroup object
        @type: B{DnaSegment}
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
        commandSequencer.userEnterCommand('BUILD_DNA', always_update = True)
        currentCommand = commandSequencer.currentCommand
        assert currentCommand.commandName == 'BUILD_DNA'
        currentCommand.editStructure(self)

    def getDnaSequence(self, format = 'CSV'):
        """
        Return the complete Dna sequence information string (i.e. all strand
        sequences) in the specified format.

        @return: The Dna sequence string
        @rtype: string

        """
        if format == 'CSV':#comma separated values.
            separator = ','
        dnaSequenceString = ''
        strandList = self.getStrands()

        for strand in strandList:
            dnaSequenceString = dnaSequenceString + strand.name + separator
            strandSequenceString = str(strand.getStrandSequence())
            if strandSequenceString:
                strandSequenceString = strandSequenceString.upper()
                dnaSequenceString = dnaSequenceString + strandSequenceString

            dnaSequenceString = dnaSequenceString + "\n"

        return dnaSequenceString


    def getStrands(self):
        """
        Returns a list of strands inside a DnaGroup object

        @return: A list containing all the strand objects
                 within self.
        @rtype: list

        @see: B{BuildDna_PropertyManager.updateStrandListWidget()}
        @see: B{BuildDna_PropertyManager._currentSelectionParams}
        """

        #TO BE REVISED. As of 2008-01-17, it uses isinstance check for
        #Chunk and some additional things to find out a list of strands inside
        # a DnaGroup -- Ninad 2008-01-17

        if self.assy is None:
            #This is to avoid possible bugs if group gets deleted. But print
            #traceback so that we know about this bug. This could happen due to
            #insufficient command sequencer stack. Temporary fix for bug 2699
            print_compact_stack("bug: self.assy is None for DnaGroup %s."%self)
            return ()

        strandList = []

        def filterStrands(node):
            if isinstance(node, self.assy.DnaStrand) and not node.isEmpty():
                strandList.append(node)
            elif isinstance(node, self.assy.Chunk) and node.isStrandChunk():
                if node.parent_node_of_class(self.assy.DnaStrand) is None:
                    strandList.append(node)

        self.apply2all(filterStrands)

        return strandList

    def getAxisChunks(self):
        """
        Returns a list of Axis chunks inside a DnaGroup object

        @return: A list containing all the axis chunks
                 within self.
        @rtype: list
        """
        if self.assy is None:
            #This is to avoid possible bugs if group gets deleted. But print
            #traceback so that we know about this bug. This could happen due to
            #insufficient command sequencer stack. Temporary fix for bug 2699
            print_compact_stack("bug: self.assy is None for DnaGroup %s."%self)
            return ()

        #TO BE REVISED. It uses isinstance check for
        #Chunk and some additional things to find out a list of strands inside
        # a DnaGroup -- Ninad 2008-02-02

        axisChunkList = []
        def filterAxisChunks(node):
            if isinstance(node, self.assy.Chunk) and node.isAxisChunk():
                axisChunkList.append(node)

        self.apply2all(filterAxisChunks)

        return axisChunkList

    def isEmpty(self):
        """
        Returns True if there are no axis or strand chunks as its members
        (Returns True even when there are empty DnaSegment objects inside)

        TODO: It doesn't consider other possibilitis such as hairpins .
        In general it relies on what getAxisChunks and getStrands returns
        (which in turn use 'Chunk' object to determine these things.)
        This method must be revised in the near future in a fully functional
        dna data model
        @see: BuildDna_EditCommand._finalizeStructure where this test is used.
        """
        #May be for the short term, we can use self.getAtomList()? But that
        #doesn't ensure if the DnaGroup always has atom of type either
        #'strand' or 'axis' .
        if len(self.getStrands()) == 0 and len(self.getAxisChunks()) == 0:
            return True
        else:
            return False


    def getSelectedStrands(self):
        """
        Returns a list of selected strands of the DnaGroup
        @return: A list containing the selected strand objects
                 within self.
        @rtype: list
        """
        selectedStrandList = []
        for strand in self.getStrands():
            if strand.picked:
                selectedStrandList.append(strand)

        return selectedStrandList

    def getSelectedSegments(self):
        """
        Returns a list of segments whose all members are selected.
        @return: A list containing the selected strand objects
                 within self.
        @rtype: list
        """
        #TODO: This is a TEMPORARY KLUDGE  until Dna model is fully functional.
        #Must be revised. Basically it returns a list of DnaSegments whose
        #all members are selected.
        #See BuildDna_PropertyManager._currentSelectionParams() where it is used
        #-- Ninad 2008-01-18
        segmentList = self.get_segments()

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
        Return a list of all atoms cotained within this DnaGroup
        """
        atomList = []
        def func(node):
            if isinstance(node, self.assy.Chunk):
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
        """
        for c in self.getStrands():
            c.draw_highlighted(glpane, color)
        for c in self.getAxisChunks():
            c.draw_highlighted(glpane, color)


    pass # end of class DnaGroup

# ==

def find_or_make_DnaGroup_for_homeless_object(node):
    """
    All DNA objects found outside of a DnaGroup during one run of the dna updater
    in one Part should be put into one new DnaGroup at the end of that Part.
    This is a fallback, since it only happens if we didn't sanitize DnaGroups
    when reading a file, or due to bugs in Dna-related user ops,
    or a user running an ordinary op on DNA that our UI is supposed to disallow.
    So don't worry much about prettiness, just correctness,
    though don't gratuitously discard info.

    The hard part is "during one run of the dna updater". We'll let it make a
    global dict from Part to this DnaGroup, and discard it after every run
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
        res = _f_DnaGroup_for_homeless_objects_in_Part[part]
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
            print "\nBUG: _f_DnaGroup_for_homeless_objects_in_Part[%r] " \
                  "found %r which is killed -- discarding it" % \
                  (part, res)
            res = None
    if not res:
        res = _make_DnaGroup_for_homeless_objects_in_Part(part)
        _f_DnaGroup_for_homeless_objects_in_Part[part] = res
    return res

def _make_DnaGroup_for_homeless_objects_in_Part(part):
    # not needed, done in addnode: part.ensure_toplevel_group()
    assy = part.assy #k
    name = gensym("DnaGroup", assy) #bruce 080407 remove "fallback", pass assy
    dad = None
    dnaGroup = DnaGroup(name, assy, dad) # same args as for Group.__init__
    part.addnode(dnaGroup)
    if debug_flags.DEBUG_DNA_UPDATER:
        print "dna_updater: made new dnaGroup %r" % dnaGroup, \
              "(bug or unfixed mmp file)"
    return dnaGroup

# end
