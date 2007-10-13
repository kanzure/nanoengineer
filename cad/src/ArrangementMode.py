# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.

"""
ArrangementMode.py -- 

TODO: rename to TemporaryCommand_Overdrawing.py or so

@author:    Mark and Bruce
@copyright: Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
@version:   $Id$
@license:   GPL
"""

    # TODO: this module needs renaming, since it has nothing to do
    # with "arrangements" of anything. What it's about is something like
    # a "view-change temporary command with no PM". We should see which of
    # those qualities it's specific to, when choosing a new name. Note that
    # if we split it into Command and GraphicsMode parts, each part might
    # be specific to different things, i.e. one might be more widely
    # reusable than the other. So they might not have precisely corresponding
    # names, since the name should reflect what it can be used for.
    # [bruce 071010]


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
    pass

# keep this around for awhile, to show how to set it up when we want the
# same thing while converting larger old modes:
#
### == temporary compatibility code (as is the use of commonXXX in the mixins above)
##
##from modes import basicMode
##
##class ArrangementMode( TemporaryCommand_preMixin,
##                       ESC_to_exit_GraphicsMode_preMixin,
##                       Overdrawing_GraphicsMode_preMixin,
##                       basicMode ):
##    pass
                       
# end
