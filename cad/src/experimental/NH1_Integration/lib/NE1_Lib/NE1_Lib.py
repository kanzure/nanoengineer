
# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
NE1 core-library-related API.
"""


class NE1_Lib:
    """
    Core NE1 methods (to support the NH1 wizard.) This API is just to give an
    idea - still needs to be thought through.

    The premise of the getXxxUI() methods is that NE1 shall provide a set of
    common UI for things for consistency, ie, so that the user only needs to
    learn one widget for model tree node selection, and the same widget for
    node selection is used everywhere.
    """


    def getConstraintsSelectorUI(self):
        """
        Returns the UI for selecting constraints.
        """
        pass


    def getMeasurementsSelectorUI(self):
        """
        Returns the UI for selecting measurements.
        """
        pass


    def getAtomSetSelectorUI(self):
        """
        Returns the UI for selecting atom set nodes from the model tree.
        """
        pass


    def detectUnMinized(self):
        """
        Detects and reports whether there are un-minimized structures in any of
        the simulation input files.
        """
        pass


    def checkJigSanity(self):
        """
        Checks whether there are any unreasonable jig parameters in the
        simulation.
        """
        pass


    def detectUnusedJigs(self):
        """
        Detects and reports whether there are any unused jigs in the input MMP
        files.
        """
        pass


    def detectReactionPoints(self):
        """
        Detects and reports reaction points found in the structures in the
        input files.
        """
        pass


    def checkSpinMultiplicity(self):
        """
        Reports on spin mulitiplicity.
        """
        pass
