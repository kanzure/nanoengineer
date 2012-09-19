# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:

TODO:
- See items in EditCommand_StructureList
"""

from utilities.Comparison import same_vals
from command_support.EditCommand_StructureList import EditCommand_StructureList

_superclass = EditCommand_StructureList

class DnaSegmentList(EditCommand_StructureList):
    """
    DnaSegmentList class provides an object that acts as a self.struct object
    for MultipleDnaSegmentResize_EditCommand. It maintains an internal list
    of structures (self._structList) which it loops through while resizing
    multiple segments at once.
    """


    def getBasesPerTurn(self):
        """
        Returns the bases per turn for the currentStucture
        of self's editcommand.
        """
        assert self.editCommand.currentStruct
        return self.editCommand.currentStruct.getBasesPerTurn()

    def getDuplexRise(self):
        """
        Returns the duplex rise for the currentStucture
        of self's editcommand.
        """
        if self.editCommand.currentStruct:
            return self.editCommand.currentStruct.getDuplexRise()

        if not self._structList:
            return 3.18

        firstSegment = self._structList[0]
        return firstSegment.getDuplexRise()

    def getNumberOfBasePairs(self):
        """
        Returns the number of bae pairs (basepairs) per turn for the
        currentStucture of self's editcommand.
        """
        if self.editCommand.currentStruct:
            return self.editCommand.currentStruct.getNumberOfBasePairs()

        if not self._structList:
            return 0

        firstSegment = self._structList[0]
        return firstSegment.getNumberOfBasePairs()


    def getAxisEndAtomAtPosition(self, position):
        """
        Returns the axis end atom of the 'currentStruct' of self's editCommand,
        at the given position.
        Example:
        If there are 4 Dnasegments being resized at the same time, the two
        resize handles will be at the average end positions. When you resize
        these segments using , for example , the right handle, it loops through
        the individual segments to resize those. While doing these, it needs to
        know the resize end axis atom. How to get that information? In
        self.updateAverageEndPoints() (which is called earlier), we create
        two lists for each end. Example: all end1 points are in
        self.endPoint_1_list (including their average end point which is
        self.end1) . So in this routine, we determine which of the list to
        use based on <position> (which is  either of the average end points
        i.e. self.end1 or self.end2) and then check which of the endPoints
        of the editCommand's currentStruct lies in this list.

        @TODO: This method will be SLOW if there are large number of structures
        being edited at once (i.e. large self._structList) . Needs revision.
        Needs revision.
        We can't use a dictionary because dict.key cant be a Vector object
        (example dict[key] != ([1.0, 2.0, 3.0])) see the disabled code that
        tried to use has_key of dict. Need to come up with a better search
        algorithm.
        """

        new_position = None

        for end in (self.end1, self.end2):
            if same_vals(position, end):

                if same_vals(end, self.end1):
                    lst = self.endPoints_1
                else:
                    lst = self.endPoints_2

                for e in self.editCommand.currentStruct.getAxisEndPoints():
                    for pos in lst:
                        if same_vals(pos, e):
                            new_position = e
                            break
                        if new_position is not None:
                            break
                    ##if e in lst:
                        ##new_position = e
                        ##break

        ##if self.endPointsDict.has_key(position):
            ##for end in self.editCommand.currentStruct.getAxisEndPoints():
                ##if end in self.endPointsDict[position]:
                    ##new_position = end
                    ##break

        if new_position is not None:
            return self.editCommand.currentStruct.getAxisEndAtomAtPosition(
                new_position)

        return None

    def is_PAM3_DnaSegment(self):
        """
        Returns True if all segments in self._structList are PAM3 dna segments
        @see: DnaSegment.is_PAM3_DnaSegment()
        """
        if not self._structList:
            return False

        for segment in self._structList:
            if not segment.is_PAM3_DnaSegment():
                return False

        return True

    def getOtherAxisEndAtom(self, atom_at_one_end):
        """
        Returns the axis atom at the other end of the DnaSegment
        The DnaSegment object being 'currentStruct' of self's editCommand.
        """
        return self.editCommand.currentStruct.getOtherAxisEndAtom(
            atom_at_one_end)

    def getAxisEndAtoms(self):
        """
        Returns the axis end atoms of the DnaSegment. The DnaSegment object
        being 'currentStruct' of self's editCommand.
        """
        if self.editCommand.currentStruct:
            return self.editCommand.currentStruct.getAxisEndAtoms()

        if not self._structList:
            return None, None

        #If there is no 'currentStruct' of self's editcommand, just return
        #the axis end atoms of the first segment in the list as a fall back.
        #(Caller should be careful in specifying currentStruct attr )
        firstSegment = self._structList[0]
        return firstSegment.getAxisEndAtoms()
