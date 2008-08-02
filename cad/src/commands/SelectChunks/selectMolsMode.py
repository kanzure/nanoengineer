# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
selectMolsMode.py

@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Ninad 2007-02-16:   Split class selectMolsMode out of selectMode.py
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from
                          the old class selectMolsMode moving them into
                          their own module [ See SelectChunks_Command.py and
                          SelectChunks_GraphicsMode.py]
"""

from utilities.constants import GLPANE_IS_COMMAND_SEQUENCER
from utilities.debug import print_compact_stack

from commands.SelectChunks.SelectChunks_Command import SelectChunks_basicCommand
from commands.SelectChunks.SelectChunks_GraphicsMode import SelectChunks_basicGraphicsMode


class selectMolsMode(SelectChunks_basicCommand,
                     SelectChunks_basicGraphicsMode):
    """
    Select Chunks Mode (compatibility version for unsplit modes; deprecated)
    """
    def __init__(self, glpane):
        assert GLPANE_IS_COMMAND_SEQUENCER

        commandSequencer = glpane

        SelectChunks_basicCommand.__init__(self, commandSequencer)
            # was just basicCommand in original

        SelectChunks_basicGraphicsMode.__init__(self, glpane)
            # was just basicGraphicsMode in original
        return

    # (the rest would come from basicMode if post-inheriting it worked,
    #  or we could split it out of basicMode as a post-mixin to use there and
    #  here)

    def __get_command(self):
        return self

    command = property(__get_command)

    def __get_graphicsMode(self):
        return self

    graphicsMode = property(__get_graphicsMode)

##    def provideParamsForTemporaryMode(self, temporaryModeName = None):
##        """
##        NOTE: This needs to be a general API method. There are situations when
##        user enters a temporary mode , does something there and returns back to
##        the previous mode he was in. User also needs to send some data from
##        previous mode to the temporary mode .
##        @see: DnaLineMode
##        @see: self.acceptParamsFromTemporaryMode for further comments and
##              example
##        """
##        print_compact_stack( "selectMolsMode.provideParamsForTemporaryMode should no longer be called: ") #bruce 080801
##        mouseClickLimit = 2
##        params = (mouseClickLimit,)
##        return params

##    def acceptParamsFromTemporaryMode(self, temporaryModeName, params):
##        """
##        NOTE: This needs to be a general API method. There are situations when
##        user enters a temporary mode , does something there and returns back to
##        the previous mode he was in. He also needs some data that he gathered
##        in that temporary mode so as to use it in the original mode he was
##        working on. Here is a good example:
##        -  User is working in selectMolsMode, Now he enters a temporary mode
##        called DnaLine mode, where, he clicks two points in the 3Dworkspace
##        and expects to create a DNA using the points he clicked as endpoints.
##        Internally, the program returns to the previous mode after two clicks.
##        The temporary mode sends this information to the method defined in
##        the previous mode called acceptParamsFromTemporaryMode and then the
##        previous mode (selectMolsMode) can use it further to create a dna
##        @see: DnaLineMode, B{BuildDna_EditCommand}, B{DnaDuplex_Command}
##        @see: self.provideParamsForTemporaryMode
##        TODO:
##        - This needs to be a more general method in Command API.
##
##        """
##        pass

    pass # end of class

# end
