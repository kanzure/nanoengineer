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
            Should horizontal/vertical snap checks always be done before
            standard axis  snap checks -- guess-- No. The current implementation
            however skips the standard axis snap check if the
            horizontal/vertical snap checks succeed.

"""

from commands.Select.Select_Command import Select_Command
from temporary_commands.LineMode.Line_GraphicsMode import Line_GraphicsMode
from utilities.debug import print_compact_traceback
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

    command_should_resume_prevMode = True
    command_has_its_own_PM = False

    _results_callback = None #bruce 080801



    def setParams(self, params):
        """
        Assign values obtained from the parent mode to the instance variables
        of this command object.
        """
        # REVIEW: I think this is only called from self.command_entered(),
        # and ought to be private or inlined. I revised it to accept a tuple
        # of length 1 rather than an int. If old code had bugs of calling it
        # from the wrong places (which pass tuples of length 5), those are
        # now tracebacks, but before were perhaps silent errors (probably
        # harmless). So if my analysis of possible callers is wrong, this
        # change might cause bugs. [bruce 080801]
        assert len(params) == 1 #bruce 080801
        (self.mouseClickLimit,) = params

    def _f_results_for_caller_and_prepare_for_new_input(self):
        """
        This is called only from GraphicsMode.leftUp()
        Give results for the caller of this request command and then prepare for
        next input (mouse click points) from the user. Note that this is called
        from Line_GraphiceMode.leftUp() only when the mouseClickLimit
        is not specified (i.e. the command is not exited automatically after
        'n' number of mouseclicks)

        @see: Line_GraphiceMode.leftUp()
        @see: RotateAboutPoints_GraphiceMode.leftUp()
        """
        if self._results_callback:
            # note: see comment in command_will_exit version of this code
            params = self._results_for_request_command_caller()
            self._results_callback( params)

        self.mouseClickPoints = []
        self.graphicsMode.resetVariables()


    def _results_for_request_command_caller(self):
        """
        @return: tuple of results to return to whatever "called"
                 self as a "request command"

        [overridden in subclasses]
        @see: Line_Command._f_results_for_caller_and_prepare_for_new_input()
        @see: RotateAboutPoint_Command._results_for_request_command_caller()
        """
        #bruce 080801
        ### REVIEW: make this a Request Command API method??
        return (self.mouseClickPoints,)

    def command_entered(self):
        super(Line_Command, self).command_entered()
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
            # callRequestCommand. Under the current command sequencer
            # API, it's important to
            # call the callback no matter how self is exited (except possibly
            # when self.commandSequencer.exit_is_forced). This code always
            # calls it. [bruce 080904 comment]
            params = self._results_for_request_command_caller()
            self._results_callback( params)

        #clear the list [bruce 080801 revision, not fully analyzed: always do this]
        self.mouseClickPoints = []

        self.graphicsMode.resetVariables()
        return