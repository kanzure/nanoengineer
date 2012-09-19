# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-05-13 Created

TODO: 2008-05-13
This is an initial implementation subjected to heavy revision. Initial purpose
is just to RESIZE given structures (of same type) together. Can be extended
in future but needs refactoring then.
- This class assumes attr currentStruct for the current command and also
  assumes a method currentStruct.getAxisEndPoints! Note that this will be true
  for currentStruct = DnaSegment, CntSegment BUT NOT FOR DnaStrand
  so when we support resizing multiple dnastrands, this must be refactored.
- Created to initially support resizing multiple dna segments. Can be extended
    for other commands such as strand, nanotube resizing.
    This class assumes certain things such as the struct being edited will have
    resize handles. If it is not the case, refactoring is needed to move methods
    such as self.updateAverageEndPoints() to the subclasses.
- Need safety features to make sure that structures provided by the
   list of structures (in self._structList) are of valid structure type (e.g.
   if you are resizing multiple Dnasegments, self._structList must contain
   all instances of DnaSegment only.
"""
from geometry.VQT import V

class EditCommand_StructureList:
    def __init__(self, editCommand, structList = ()):
        self.editCommand = editCommand
        self._structList = []
        self.setStructList(structList = structList)

        #self.end1 , self.end2 are the average endpoints calculated using
        #endpoints of structs within structList.
        self.end1 = None
        self.end2 = None
        #TODO: revise the following.
        #@see self._getAverageEndPoints() where these lists are being used.
        #@see: comments in DnaSegmentList.getAxisEndAtomAtPosition()
        self.endPoints_1 = []
        self.endPoints_2 = []
        self.endPointsDict = {} #unused as of 2008-05-13 (used in some commented
        #out code)
        self.updateAverageEndPoints()


    def parent_node_of_class(self, clas):
        """
        Returns parent node of the class <clas> for the
        'currentStructure' of self's editcommand being edited. If there is no
        currentStructure, it returns the parent node of specified class
        of the 'first structure' in the self._structList.
        """
        if self.editCommand.currentStruct:
            if self.editCommand.currentStruct.killed():
                return None

            return self.editCommand.currentStruct.parent_node_of_class(clas)

        if not self._structList:
            return None

        firstStruct = self._structList[0]

        if firstStruct is None:
            return None

        if firstStruct.killed():
            return None

        return firstStruct.parent_node_of_class(clas)

    def killed(self):
        """
        Always returns False as of 2008-05-16. There is no UI to 'delete'
        this list object. (its internal) This method is implemented just to
        handle the calls in , for example, EditCommand.hasValidStructure()
        @see: MultipleDnaSegment_EditCommand.hasValidStructure()
        """
        return False

    def isEmpty(self):
        """
        Returns True if if the self._sturctList is empty.
        """
        if len(self._structList) == 0:
            return True
        return False

    def updateStructList(self):
        """
        Update the structure list , removing the invalid items in the structure
        @see:MultipleDnaSegmentResize_PropertyManager.model_changed()
        @see: self.getstructList()
        """
        #@TODO: Should this always be called in self.getStructList()??? But that
        #could be SLOW because that method gets called too often by
        #the edit command's graphics mode.
        def func(struct):
            if struct is not None and not struct.killed():
                if not struct.isEmpty():
                    return True

            return False

        new_list = filter( lambda struct:
                      func(struct) ,
                      self._structList )

        if len(new_list) != len(self._structList):
            self._structList = new_list


    def getStructList(self):
        """
        Returns the list of structures being edited together.
        @see: MultipleDnaSegmentResize_graphicsMode._drawHandles()
        """
        #Should we call self.updateStructList() here?? But that could be
        #too slow because this method is called quite often in the
        #graphics mode.draw  of the command
        return self._structList


    def setStructList(self, structList = () ):
        """
        Replaces the list of structures (self._structList)
        with the given one.
        @param structList: List containing the structures to be edited at once
                           This list will replace the existing
                           self._structList
        @type: list
        @see: MultipleSegmentResize_EditCommand.setStructList()
              (calls this method. )
        """
        self._structList = list(structList)
        self.updateAverageEndPoints()

    def addToStructList(self, struct):
        """
        Add the given structure to the list of structures being edited together.
        @param struct: Structure to be added to the self._structList
        """

        if struct is not None and not struct in self._structList:
            self._structList.append(struct)
            self.updateAverageEndPoints()

    def removeFromStructList(self, struct):
        """
        Remove the given structure from the list of structures being edited
        together.
        @param struct: Structure to be removed from the self._structList
        """
        if struct in self._structList:
            self._structList.remove(struct)
            self.updateAverageEndPoints()

    def updateAverageEndPoints(self):
        """
        Update self's average end points.
        """
        #(may need refactoring in future)
        self.end1, self.end2 = self._getAverageEndPoints()

    def _getAverageEndPoints(self):
        """
        Subclasses should override this method. Default implementation assumes an
        attr (method) getAxisEndPoints for structures in
        self._structList
        This is not True for some structures such as DnaStrand.
        """
        endPoint1 = V(0.0, 0.0, 0.0)
        endPoint2 = V(0.0, 0.0, 0.0)

        n1 = 0
        n2 = 0
        self.endPoints_1 = []
        self.endPoints_2 = []
        self.endPointsDict = {}

        for struct in self._structList:
            end1, end2 = struct.getAxisEndPoints()
            if end1 is not None:
                endPoint1 += end1
                self.endPoints_1.append(end1)
            if end2 is not None:
                endPoint2 += end2
                n2 += 1
                self.endPoints_2.append(end2)

        n1 =   len(self.endPoints_1)
        n2 =   len(self.endPoints_2)

        if  n1 > 0:
            endPoint1 /= n1
            self.endPoints_1.append(endPoint1)
            ##self.endPointsDict[endPoint1] = self.endPoints_1

        if n2 > 0:
            endPoint2 /= n2
            self.endPoints_2.append(endPoint2)
            ##self.endPointsDict[endPoint2] = self.endPoints_2
        return (endPoint1, endPoint2)

    def getAxisEndPoints(self):
        """
        @TODO: Revise/ Refactor this. This needs to be implemented in a subclass
        rather than here because not all structures that this class will support
        have an attr getAxisEndPoints. (e.g. DnaStrand).  (although several
        strutures will have this attr)
        """
        currentStruct = self.editCommand.currentStruct
        if  currentStruct and hasattr(currentStruct, 'getAxisEndPoints'):
            return self.editCommand.currentStruct.getAxisEndPoints()


        self.updateAverageEndPoints()
        return (self.end1, self.end2)


    def getProps(self):
        """
        Returns the properties of editCommand's currentStruct. If there is
        no currentStruct, it uses the firstStruct in self._structList
        """
        if self.editCommand.currentStruct:
            return self.editCommand.currentStruct.getProps()

        if not self._structList:
            return ()

        firstStruct = self._structList[0]
        if firstStruct is None:
            return ()

        return firstStruct.getProps()

    def setProps(self, props):
        """
        TODO: expand this method
        """
        pass
