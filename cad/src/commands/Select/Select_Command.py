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
from command_support.Command import basicCommand
from commands.Select.Select_GraphicsMode import Select_GraphicsMode

from command_support.GraphicsMode_API import GraphicsMode_API

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

    @see: cad/doc/splitting_a_mode.py that gives a detailed explanation on how
          this is implemented.
    @see: B{Select_GraphicsMode}, B{Select_basicGraphicsMode}
    @see: B{Select_Command}, B{selectMode}
    @see: B{SelectChunks_basicCommand}, B{SelectAtoms_basicCommand}
          which inherits this class

    """
    # class constants
    
    from utilities.constants import CL_ABSTRACT
    command_level = CL_ABSTRACT

    
    # Don't highlight singlets. (This attribute is set to True in
    # SelectAtoms_Command)
    highlight_singlets = False

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
        @see: self._makeEditContextMenu()
        @see: SelectChunks_EditCommand.makeMenus()
        """
        pass
    
    def _makeEditContextMenus(self):
        """
        Subclasses can call this method inside self.makeMenus() if they need 
        context menu items for editing selected components such as Nanotube, 
        DnaStrand , DnaSegments.
        
        Creates a context menu items to edit a selected component. 
        If more than one type of components are selected, the edit options
        are not added. Example: if a DnaStrand is selected, this method will
        add a context menu 'Edit selected DnaStrand'. But if, along with 
        DnaStrand, a DnaSegment is selected, it won't show options to edit 
        the dna strand or dna segment.     
        
        @see: SelectChunks_EditCommand.makeMenus()
        @see: se;f.makeMenus() 
        """
        selectedDnaSegments = self.win.assy.getSelectedDnaSegments()
        selectedDnaStrands = self.win.assy.getSelectedDnaStrands() 
        selectedNanotubes = self.win.assy.getSelectedNanotubeSegments()
        
        
        numOfSegments = len(selectedDnaSegments)
        numOfStrands = len(selectedDnaStrands)
        numOfNanotubes = len(selectedNanotubes)
        
                
        #If both DnaSegments and DnaStrands are selected, we will not show 
        #context menu for editing the selected entities i.e. Edit DnaSegment..
        #AND "Edit DnaStrands..". This is based on a discussion with Mark. This 
        #can be easily changed if we decide that way  -- Ninad 2008-07-10
        count = 0
        for num in (numOfSegments, numOfStrands, numOfNanotubes): 
           
            if num > 0:
                count += 1
            
            if count > 1:
                return 
                        
        if numOfSegments or numOfStrands:
            self._makeDnaContextMenus()
        
        if numOfNanotubes:
            self._makeNanotubeContextMenus()
            
        return
               
    
    def _makeDnaContextMenus(self):
        """
        Make Dna specific context menu that allows editing a *selected* 
        DnaStrand or DnaSegment.
        @see: self._makeEditContextMenu() which calls this method
        """
        contextMenuList = []
        selectedDnaSegments = self.win.assy.getSelectedDnaSegments()
        selectedDnaStrands = self.win.assy.getSelectedDnaStrands()
        
        #If both DnaSegments and DnaStrands are selected, we will not show 
        #context menu for editing the selected entities i.e. Edit DnaSegment.. AND
        #"Edit DnaStrands..". This is based on a discussion with Mark. This 
        #can be easily changed if we decide that way  -- Ninad 2008-07-10
        if not selectedDnaStrands:     
            if len(selectedDnaSegments) == 1:
                segment = selectedDnaSegments[0]
                item = (("Edit Selected DnaSegment..."), 
                            segment.edit)
                contextMenuList.append(item)
                contextMenuList.append(None) #adds a separator 
                
            if len(selectedDnaSegments) > 1:
                item = (("Resize Selected DnaSegments "\
                         "(%d)..."%len(selectedDnaSegments)), 
                        self.win.resizeSelectedDnaSegments)
                contextMenuList.append(item)
                contextMenuList.append(None)
            
        if not selectedDnaSegments:
            if len(selectedDnaStrands) == 1:
                strand = selectedDnaStrands[0]
                item = (("Edit Selected DnaStrand..."), 
                            strand.edit)
                contextMenuList.append(item)

        self.Menu_spec.extend(contextMenuList)        
                
        return
    
    def _makeNanotubeContextMenus(self):
        """
        Make Nanotube specific context menu that allows editing a *selected* 
        Nanotube
        @see: self._makeEditContextMenu() which calls this method
        """
        contextMenuList = []
        selectedNanotubes = self.win.assy.getSelectedNanotubeSegments()
        if len(selectedNanotubes) == 1:
            nanotube = selectedNanotubes[0]
            item = (("Edit Selected Nanotube..."), 
                        nanotube.edit)
            contextMenuList.append(item)
            
        self.Menu_spec.extend(contextMenuList)
            
        return 


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


