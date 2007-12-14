# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
selectMolsMode.py 

$Id$


History:



Ninad 2007-02-16:   Split class selectMolsMode out of selectMode.py 
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectMolsMode moving them into
                          their own module [ See SelectChunks_Command.py and 
                          SelectChunks_GraphicsMode.py]
"""

from constants import GLPANE_IS_COMMAND_SEQUENCER

from SelectChunks_Command import SelectChunks_basicCommand
from SelectChunks_GraphicsMode import SelectChunks_basicGraphicsMode


class selectMolsMode(SelectChunks_basicCommand, 
                     SelectChunks_basicGraphicsMode):
    """
    Select Chunks Mode
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
    
    
    def provideParamsForTemporaryMode(self, temporaryModeName):
        """
	NOTE: This needs to be a general API method. There are situations when 
	user enters a temporary mode , does something there and returns back to
	the previous mode he was in. He also needs to send some data from 
	previous mode to the temporary mode .	 
	@see: DnaLineMode
	@see: self.acceptParamsFromTemporaryMode for further comments and 
	      example	
        """	        
        if temporaryModeName == "DNA_LINE_MODE":
            #This is the number of mouse clicks that the temporary mode accepts
            # When this limit is reached, the temporary mode will return to the
            #previous mode.	    
            dnaEditCntl = self.win.dnaEditController
            if dnaEditCntl:
                params = dnaEditCntl.provideParamsForTemporaryMode(
                    temporaryModeName) 
        else:
            #@attention This is an arbitrary number, needs cleanup. 
            mouseClickLimit = 2
            params = (mouseClickLimit)

        return params

    def acceptParamsFromTemporaryMode(self, temporaryModeName, params):
        """
	NOTE: This needs to be a general API method. There are situations when 
	user enters a temporary mode , does something there and returns back to
	the previous mode he was in. He also needs some data that he gathered 
	in that temporary mode so as to use it in the original mode he was 
	working on. Here is a good example: 
	-  User is working in selectMolsMode, Now he enters a temporary mode 
	called DnaLine mode, where, he clicks two points in the 3Dworkspace 
	and expects to create a DNA using the points he clicked as endpoints. 
	Internally, the program returns to the previous mode after two clicks. 
	The temporary mode sends this information to the method defined in 
	the previous mode called acceptParamsFromTemporaryMode and then the
	previous mode (selectMolsMode) can use it further to create a dna 
	@see: DnaLineMode
	@see: self.provideParamsForTemporaryMode
	TODO: 
	- This needs to be a more general method in mode API. 
	- Right now it is used only for creating a DNA line. It is assumed
	 that the DNADuplxEditController is invoked while in selectMolsMode. 
	 If we decide to define a new DnaMode, then this method needs to go 
	 there. 
	 - Even better if the commandSequencer API starts supporting 
	 sommandSequencer.previousCommand (like it does for previous mode) 
	 where, the previousCommand can be an editController or mode, then 
	 it would be good to define this API method in that mode or 
	 editcontroller class  itself. In the above example, this method would 
	 then belong to DnaDuplexEditController. 
	 -- [Ninad 2007-10-25 comment]	
        """

        #Usually params will contain 2 items. But if user abruptly terminates  
        #the temporary mode, this might not be true. So move the chunk by offset
        #only when you have got 2 points!  Ninad 2007-10-16
        if 1:
            if len(params) == 2:	    
                dnaEditController = self.win.dnaEditController
                if dnaEditController:
                    dnaEditController.acceptParamsFromTemporaryMode(params)

    def selectConnectedChunks(self):
        """
	TODO: Not implemented yet. Need to define a method in ops_select to 
	do this
        """        
        pass
    

# ==
