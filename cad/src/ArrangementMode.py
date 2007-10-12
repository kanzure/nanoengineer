# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
ArrangementMode.py -- 

TODO: rename to TemporaryCommand_Overdrawing.py or so

@author:    Mark and Bruce
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

from PyQt4.Qt import Qt

from Command import Command, basicCommand, commonCommand

from GraphicsMode import GraphicsMode, basicGraphicsMode, commonGraphicsMode


# == useful pieces -- Command

class TemporaryCommand_preMixin(commonCommand):
    """
    A pre-Mixin class for Command subclasses
    which want to act as temporary commands.
    """
    command_can_be_suspended = False #bruce 071011
    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)
    pass


# == useful pieces -- GraphicsMode

class ESC_to_exit_GraphicsMode_preMixin(commonGraphicsMode):
    """
    A pre-Mixin class for GraphicsModes which overrides their keyPress method
    to call self.command.Done() when the ESC key is pressed,
    but delegate all other keypresses to the superclass.
    """
    def keyPress(self, key):
        # ESC - Exit our command.
        if key == Qt.Key_Escape:
            self.command.Done()
        else:
            #bruce 071012 bugfix: add 'else' to prevent letting superclass
            # also handle Key_Escape and do assy.selectNone.
            # I think that was a bug, since you might want to pan or zoom etc
            # in order to increase the selection. Other ways of changing
            # the viewpoint (eg trackball) don't deselect everything.
            super(TemporaryOverdrawing_GraphicsMode, self).keyPress(key) # Fixes bug 1172 (F1 key). mark 060321
                ### REVIEW correct use of super
        return
    pass


class Overdrawing_GraphicsMode_preMixin(commonGraphicsMode):
    """
    A pre-Mixin class for GraphicsModes which overrides their Draw method
    to do the saved prior command's drawing
    (perhaps in addition to their own, if they subclass this
     and further extend its Draw method, or if they do incremental
     OpenGL drawing in event handler methods).

##    If there is no saved prior command, this just calls GraphicsMode.Draw
##    (regardless of the other superclasses in the mixin).
##    TODO (probably): have it call super(...).Draw in an appropriate way.
    
    KLUGE: THEN IT ALSO CALLS self.glpane.assy.draw(self.glpane).
    TODO: clean that up. (Standard flag for drawing model??
     Same one as in extrudeMode, maybe other commands.)
    """
    def Draw(self): 
        # bruce 070813 revised this to use prevMode
        # TODO soon: move this into a new method in the command sequencer, Draw_by_prior_command or so;
        # have it return whether it called a draw method or not (so we know whether to call our fallback drawing code)
        
        glpane = self.glpane # really this is the command sequencer
        prevMode = glpane.prevMode # really a Command object of some kind -- TODO, rename to _savedCommand or so
        if prevMode is not None:
            # doing this fixes bug in which Zoom etc doesn't show the right things for cookie or
            # extrude modes
            assert not prevMode.is_null
            prevMode.graphicsMode.Draw()
            # WARNING/TODO: this assumes there is at most one saved command
            # which should be drawn. If this changes, we'll need to replace
            # .prevMode with a deeper command stack in the Command Sequencer
            # which provides a way to draw whatever each suspended command
            # thinks it needs to; or we'll need to arrange for prevMode
            # to *be* that stack, delegating Draw to each stack element in turn.
            # Either way, it might be clearest to just call a new CommandSequencer
            # method to "draw the stuff from all the saved commands".
            # Most of the code around this comment would become part of that method.
            # [bruce 071011]
        else:    
            ## GraphicsMode.Draw(self)
            # try this instead:
            super(Overdrawing_GraphicsMode_preMixin, self).Draw()
                ### REVIEW correct use of super
            self.glpane.assy.draw(self.glpane) # TODO: use flag in super Draw; see docstring for more info
        return

    pass

# ==

class TemporaryCommand_Overdrawing_GM( ESC_to_exit_GraphicsMode_preMixin,
                                       Overdrawing_GraphicsMode_preMixin,
                                       GraphicsMode ):
    """
    GraphicsMode component of TemporaryCommand_Overdrawing
    """
    pass

class TemporaryCommand_Overdrawing( TemporaryCommand_preMixin,
                                    Command):
    """
    Common superclass for temporary view-change commands
    such as the Pan, Rotate, and Zoom tools.

    Provides the declarations that make a command temporary,
    a binding from the Escape key to the Done method,
    and a Draw method which delegates to the Draw method
    of the saved prior command (commandSequencer.prevMode).
    Otherwise inherits directly from Command, and its
    GraphicsMode component from GraphicsMode.
    """
    GraphicsMode_class = TemporaryCommand_Overdrawing_GM
    pass

# == temporary compatibility code (as is the use of commonXXX in the mixins above)

from modes import basicMode

class ArrangementMode( TemporaryCommand_preMixin,
                       ESC_to_exit_GraphicsMode_preMixin,
                       Overdrawing_GraphicsMode_preMixin,
                       basicMode ):
    pass
                       
# end
