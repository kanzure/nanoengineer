# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
@author:    Ninad
@version:   $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL


History:
Split this out of LineMode.py (and deprecated that class)

TODOs:
- Refactor/ expand snap code. Should all the snapping code be in its own module?
- Need to discuss and derive various snap rules 
  Examples: If 'theta_snap' between dragged line and the  two reference enties 
            is the same, then the snap should use the entity with shortest  
            distance
            Should horizontal/vertical snap checkes always be done before 
            standard axis  snap checks -- guess-- No. The current implementation
            however skips the standard axis snap check if the 
            horizontal/vertical snap checks succeed.           

"""

from commands.Select.Select_Command import Select_Command
from temporary_commands.LineMode.Line_GraphicsMode import Line_GraphicsMode
from utilities.GlobalPreferences import USE_COMMAND_STACK


# == Command part

class Line_Command(Select_Command): 
    """
    Encapsulates the Line_Command tool functionality.
    """
    # class constants

    commandName = 'Line_Command'
    featurename = "Line Command"
        # (I don't know if this featurename is ever user-visible;
        #  if it is, it's probably wrong -- consider overriding
        #  self.get_featurename() to return the value from the
        #  prior command, if this is used as a temporary command.
        #  The default implementation returns this constant
        #  or (if it's not overridden in subclasses) something
        #  derived from it. [bruce 071227])
    from utilities.constants import CL_REQUEST
    command_level = CL_REQUEST

    GraphicsMode_class = Line_GraphicsMode

    # Initial value for the instance variable. (Note that although it is assigned 
    # an empty tuple, later it is assigned a list.) Empty tuple is just for 
    # the safer implementation than an empty list. Also, it is not 'None' 
    # because in Line_GraphicsMode.bareMotion, it does a check using
    # len(mouseClickPoints)
    mouseClickPoints = ()

    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_PM = False

    _results_callback = None #bruce 080801
    
    

    def setParams(self, params):
        """
        Assign values obtained from the parent mode to the instance variables
        of this command object. 
        """
        # REVIEW: I think this is only called from self.init_gui,
        # and ought to be private or inlined. I revised it to accept a tuple
        # of length 1 rather than an int. If old code had bugs of calling it
        # from the wrong places (which pass tuples of length 5), those are
        # now tracebacks, but before were perhaps silent errors (probably
        # harmless). So if my analysis of possible callers is wrong, this
        # change might cause bugs. [bruce 080801]
        assert len(params) == 1 #bruce 080801
        (self.mouseClickLimit,) = params


    def _results_for_request_command_caller(self):
        """
        @return: tuple of results to return to whatever "called"
                 self as a "request command"

        [overridden in subclasses]
        """
        #bruce 080801 split this out of restore_gui
        ### REVIEW: make this a Request Command API method??
        return (self.mouseClickPoints,)


    #START New Command API methods. (used when USE_COMMAND_STACK is True)======
    def command_entered(self):
        super(Line_Command, self).command_entered()
        self._command_enter_effects()

    def _command_enter_effects(self):
        """
	common code for Enter and command_entered
	"""
        #@TODO: merge into command_entered when USE_COMMAND_STACK is 
        # always true and Enter is removed
        #clear the list (for safety) which may still have old data in it
        self.mouseClickPoints = []
        self.glpane.gl_update()

        params, results_callback = self._args_and_callback_for_request_command()
        if params is not None:
            self.setParams(params)
            self._results_callback = results_callback
            # otherwise we were not called as a request command;
            # method above prints something in that case, for now ###
        else:
            # maybe: set default params?
            self._results_callback = None
            
            
    def command_will_exit(self):
        super(Line_Command, self).command_will_exit()
        if self._results_callback:
            # note: _results_callback comes from an argument to
            # callRequestCommand.
            params = self._results_for_request_command_caller()
            self._results_callback( params)

        #clear the list [bruce 080801 revision, not fully analyzed: always do this]
        self.mouseClickPoints = []

        self.graphicsMode.resetVariables()
        return  
    

    #END New Command API methods ===============================================
    
    
    #START - OLD command api methods init_gui, restore_gui =====================
    if not USE_COMMAND_STACK:

        def init_gui(self):
            """
            Initialize GUI for this mode 
            """
            #clear the list (for safety) which may still have old data in it
            self.mouseClickPoints = []
            self.glpane.gl_update()
    
            params, results_callback = self._args_and_callback_for_request_command()
            if params is not None:
                self.setParams(params)
                self._results_callback = results_callback
                # otherwise we were not called as a request command;
                # method above prints something in that case, for now ###
            else:
                # maybe: set default params?
                self._results_callback = None
            return   
    
    
        def restore_gui(self):
            """
            Restore the GUI 
            """
            if self._results_callback:
                # note: _results_callback comes from an argument to
                # callRequestCommand.
                params = self._results_for_request_command_caller()
                self._results_callback( params)
    
            #clear the list [bruce 080801 revision, not fully analyzed: always do this]
            self.mouseClickPoints = []
    
            self.graphicsMode.resetVariables()
            return
        
    #END - OLD command api methods init_gui, restore_gui =======================
