# Copyright 2007-2009 Nanorex, Inc.  See LICENSE file for details.
"""
TemporaryCommand.py -- provides several kinds of TemporaryCommand superclasses
(so far, just TemporaryCommand_Overdrawing, used for Zoom/Pan/Rotate).

@author:    Mark, Bruce
@version:   $Id$
@copyright: 2007-2009 Nanorex, Inc.  See LICENSE file for details.
@license:   GPL
"""

from PyQt4.Qt import Qt

from command_support.Command import Command, commonCommand

from command_support.GraphicsMode import GraphicsMode, commonGraphicsMode

# == useful pieces -- Command

class TemporaryCommand_preMixin(commonCommand):
    """
    A pre-Mixin class for Command subclasses
    which want to act as temporary commands.
    """
    command_should_resume_prevMode = True #bruce 071011, to be revised (replaces need for customized Done method)
    #See Command.anyCommand for detailed explanation of the following flag
    command_has_its_own_PM = False
    pass


# == useful pieces -- GraphicsMode

class ESC_to_exit_GraphicsMode_preMixin(commonGraphicsMode):
    """
    A pre-mixin class for GraphicsModes which overrides their keyPress method
    to call self.command.command_Done() when the ESC key is pressed
    if self.command.should_exit_when_ESC_key_pressed() returns true,
    or to call assy.selectNone otherwise,
    but which delegates all other keypresses to the superclass.
    """
    def keyPress(self, key):
        # ESC - Exit our command, if it permits exit due to ESC key.
        if key == Qt.Key_Escape:
            if self.command.should_exit_when_ESC_key_pressed():
                self.command.command_Done()
            else:
                self.glpane.assy.selectNone()
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
    A pre-mixin class for GraphicsModes which want to override their
    Draw_* methods to do the parent command's drawing
    (perhaps in addition to their own, if they subclass this
     and further extend its Draw_* methods, or if they do incremental
     OpenGL drawing in event handler methods).

    (If there is no parent command, which I think never happens
     given how this is used as of 071012, this will raise an exception
     when any of its Draw_* methods are called.)

    @see: related class Delegating_GraphicsMode
    """
    #bruce 090310 revised this
    def Draw_preparation(self):
        self.parentGraphicsMode.Draw_preparation()
    
    def Draw_axes(self):
        self.parentGraphicsMode.Draw_axes()
    
    def Draw_model(self):
        self.parentGraphicsMode.Draw_model()
    
    def Draw_other(self):
        # doing this fixes the bug in which Pan etc doesn't show the right things
        # for BuildCrystal or Extrude modes (e.g. bond-offset spheres in Extrude)
        self.parentGraphicsMode.Draw_other()
    
    def Draw_after_highlighting(self, pickCheckOnly = False):
        #bruce 090310 new feature (or bugfix) -- delegate this too
        self.parentGraphicsMode.Draw_after_highlighting(pickCheckOnly = pickCheckOnly)

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
    of the saved parentCommand.
    
    In other respects, inherits behavior from Command
    and GraphicsMode.
    """
    GraphicsMode_class = _TemporaryCommand_Overdrawing_GM
    __abstract_command_class = True
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
