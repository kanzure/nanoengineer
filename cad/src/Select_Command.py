# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Select_Command.py 

The 'Command' part of the Select Mode (Select_basicCommand and 
Select_basicGraphicsMode are the two split classes of the old selectMode) 
It provides the command object for its GraphicsMode class. The Command class
defines anything related to the 'command half' of the mode  -- 
For example: 
- Anything related to its current Property Manager, its settings or state
- The model operations the command does (unless those are so simple
  that the mouse event bindings in the _GM half can do them directly
  and the code is still clean, *and* no command-half subclass needs
  to override them).

@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details.


TODO:
- Items mentioned in Select_GraphicsMode.py 
- The Enter method needs to be split into Enter_Command and Enter_GM parts

History:
Ninad & Bruce 2007-12-13: Created new Command and GraphicsMode classes from 
                          the old class selectMode and moved the 
                          Command related methods into this class from 
                          selectMode.py

"""
from Command import basicCommand
from Select_GraphicsMode import Select_GraphicsMode

from GraphicsMode_API import GraphicsMode_API

class Select_basicCommand(basicCommand):
    """    
    The 'Command' part of the Select Mode (Select_basicCommand and 
    Select_basicGraphicsMode are the two split classes of the old selectMode) 
    It provides the command object for its GraphicsMode class. The Command class
    defines anything related to the 'command half' of the mode  -- 
    For example: 
    - Anything related to its current Property Manager, its settings or state
    - The model operations the command does (unless those are so simple
      that the mouse event bindings in the _GM half can do them directly
      and the code is still clean, *and* no command-half subclass needs
      to override them).
    
    @see: splitting_a_mode.py that gives a detailed explanation on how
          this is implemented. 
    @see: B{Select_GraphicsMode}, B{Select_basicGraphicsMode}
    @see: B{Select_Command}, B{selectMode}
    @see: B{SelectChunks_basicCommand}, B{SelectAtoms_basicCommand}
          which inherits this class          
          
    """
    hover_highlighting_enabled = True
    # Set this to False if you want to disable hover highlighting.
    
    def __init__(self, commandSequencer):
        """
        ...
        """
        basicCommand.__init__(self, commandSequencer)
        # Now do whatever might be needed to init the command object,
        # or in the mixed case, the command-related attrs of the mixed object.
        # That might be nothing, since most attrs can just be initialized in
        # Enter, since they should be reinitialized every time we enter the
        # command anyway.
        # (If it's nothing, we probably don't need this method, but it's ok
        #  to have it for clarity, especially if there is more than one
        #  superclass.)
        return
        
    def init_gui(self):
        """
	Handles all the GUI display when entering a command
        Subclasses should override this method
	"""
        pass 
    
    def connect_or_disconnect_signals(self, connect):
        """
	Subclasses should override this method
	"""
        pass
    
    def restore_gui(self):
        """
        Handles all the GUI display when leaving a command
	Subclasses should override this method
	"""
        pass 
    
    def makeMenus(self):
        """
        Overrided in subclasses. Default implementation does nothing
        @see: selectAtoms_Command.makeMenus
        @see: selectChunks_Command.makeMenus         
        """
        pass 


class Select_Command(Select_basicCommand):
            
    # This is needed so the init code knows what kind of GM to make.
    GraphicsMode_class = Select_GraphicsMode
    
    def __init__(self, commandSequencer):
        Select_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        self._post_init_modify_GraphicsMode()
        return
        
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)
        pass

    def _post_init_modify_GraphicsMode(self):
        pass
        
    
