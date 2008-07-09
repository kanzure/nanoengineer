# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
TemporaryCommand.py -- provides several kinds of TemporaryCommand superclasses
(so far, just TemporaryCommand_Overdrawing, used for Zoom/Pan/Rotate).

@author:    Mark, Bruce
@version:   $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL
"""

from PyQt4.Qt import Qt

from command_support.Command import Command, commonCommand

from command_support.GraphicsMode import GraphicsMode, commonGraphicsMode
import ne1_ui.prefs.Preferences as Preferences

# == useful pieces -- Command

class TemporaryCommand_preMixin(commonCommand):
    """
    A pre-Mixin class for Command subclasses
    which want to act as temporary commands.
    """
    command_can_be_suspended = False #bruce 071011
    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)
    #See Command.anyCommand for detailed explanation of the following flag
    command_has_its_own_gui = False
    pass


# == useful pieces -- GraphicsMode

class ESC_to_exit_GraphicsMode_preMixin(commonGraphicsMode):
    """
    A pre-Mixin class for GraphicsModes which overrides their keyPress method
    to call self.command.Done() when the ESC key is pressed,
    but delegate all other keypresses to the superclass.
    NOTE: The default mode or command will override this implementation 
    (i.e. while in default command which is 'Select chunks', hitting Escape key 
    will not exit that command. This is intentional)
    """
    def keyPress(self, key):
        # ESC - Exit our command.
        if key == Qt.Key_Escape:
            #Escape key to exit should not exit the command if its the 
            #default command (which is select chunks or 'SELECTMOLS') 
            if self.command.commandName != Preferences.default_commandName():
                self.command.Done(exit_using_done_or_cancel_button = False)
        else:
            #bruce 071012 bugfix: add 'else' to prevent letting superclass
            # also handle Key_Escape and do assy.selectNone.
            # I think that was a bug, since you might want to pan or zoom etc
            # in order to increase the selection. Other ways of changing
            # the viewpoint (eg trackball) don't deselect everything.
            super(ESC_to_exit_GraphicsMode_preMixin, self).keyPress(key) # Fixes bug 1172 (F1 key). mark 060321
        return
    pass


class Overdrawing_GraphicsMode_preMixin(commonGraphicsMode):
    """
    A pre-Mixin class for GraphicsModes which overrides their Draw method
    to do the saved prior command's drawing
    (perhaps in addition to their own, if they subclass this
     and further extend its Draw method, or if they do incremental
     OpenGL drawing in event handler methods).

    (If there is no saved prior command, which I think never happens
     given how this is used as of 071012, this just calls super(...).Draw()
     followed by (KLUGE) self.glpane.assy.draw(self.glpane).
     TODO: clean that up. (Standard flag for drawing model??
     Same one as in extrudeMode, maybe other commands.))
    """
    def Draw(self):
        drew = self.commandSequencer.prior_command_Draw(self.command)
            # doing this fixes the bug in which Pan etc doesn't show the right things
            # for Cookie or Extrude modes (e.g. bond-offset spheres in Extrude)
        if not drew:
            # I think this can't happen, since our subclasses always run as a temporary
            # command while suspending another one:
            print "fyi: %s using fallback Draw code (I suspect this can never happen)" % self
            super(Overdrawing_GraphicsMode_preMixin, self).Draw()
            self.glpane.assy.draw(self.glpane)
                # TODO: use flag in super Draw for whether it should do this; see docstring for more info
        return

    pass

# ==

class _TemporaryCommand_Overdrawing_GM( ESC_to_exit_GraphicsMode_preMixin,
                                        Overdrawing_GraphicsMode_preMixin,
                                        GraphicsMode ):
    """
    GraphicsMode component of TemporaryCommand_Overdrawing.

    Note: to inherit this, get it from
    TemporaryCommand_Overdrawing.GraphicsMode_class
    rather than inheriting it directly by name.
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
    GraphicsMode_class = _TemporaryCommand_Overdrawing_GM
    featurename = "Undocumented Temporary Command"
        # (I don't know if this featurename is ever user-visible;
        #  if it is, it's probably wrong -- consider overriding
        #  self.get_featurename() to return the value from the
        #  prior command.
        #  The default implementation returns this constant
        #  or (if it's not overridden in subclasses) something
        #  derived from it. [bruce 071227])
    pass

    
# keep this around for awhile, to show how to set it up when we want the
# same thing while converting larger old modes:
#
### == temporary compatibility code (as is the use of commonXXX in the mixins above)
##
##from modes import basicMode
##
### now combine all the classes used to make TemporaryCommand_Overdrawing and its _GM class:
##
##class basicTemporaryCommand_Overdrawing( TemporaryCommand_preMixin,
##                       ESC_to_exit_GraphicsMode_preMixin,
##                       Overdrawing_GraphicsMode_preMixin,
##                       basicMode ):
##    pass

# end
