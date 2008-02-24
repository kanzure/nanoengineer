# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
splitting_a_mode.py -- explanation/demo of how to split an old mode, while
maintaining temporary compatibility with non-split methods and subclass modes.

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

This file can be deleted after all NE1 modes have been split.

Status:

I think it's right, but I didn't test it.

"""

# context & basic concepts: not described here.

# terminology: C = Command, GM = GraphicsMode.

# The goal is that for each old mode, we have 5 new classes -- 2 main classes
# (its C and GM parts), and 3 "glue" classes that help initialize it --
# one for C-alone, one for GM-alone, and one for a mixed object that has
# both C and GM parts in one instance.
#
# For example, for basicMode these classes are:
# - basicCommand     (main C class)
# - Command          (C-alone glue class)
# - basicGraphicsMode     (main GM class)
# - GraphicsMode          (GM-alone glue class)
# - basicMode     (mixed C/GM glue class)

# The reason we need this is that each glue class has to inherit different
# superclasses and have different __init__ methods. The main differences are
# in how they set up the "cross reference attributes", command.graphicsMode
# and graphicsMode.command, and in whether a command instance has to create
# a new graphicsMode instance. In a mixed object, the command *is* the
# graphicsMode, so it should not create a new one, and each cross-reference
# attribute should be a property pointing to self. In a used-alone object,
# the __init__ method should set up the cross-reference attribute to point
# to another object, and in the command case, it has to create that object
# as a new instance of self.GraphicsMode_class.

# (One other requirement might be some superclasses just for isinstance tests,
# or to revise isinstance tests in other code, probably to just look for the
# basicCommand or basicGraphicsMode part depending on whether they test the
# "current command" or the "current graphicsMode".)

# The mixed object is only needed for compatibility with non-split subclasses
# and to work around bugs from an incomplete split. When it's no longer needed,
# the mixed glue class can be removed, and the other glue classes can be merged
# into the corresponding main classes, with the simpler names retained.
#
# So when basicMode is no longer needed, we'll delete its file (modes.py),
# and merge basicCommand and Command (retaining the name Command),
# and merge basicGraphicsMode and GraphicsMode (retaining the name
# GraphicsMode). But this can only happen when all subclasses are split, i.e.
# when every mode in NE1 is split.

# ===

# So, here is how this should be done with selectMode.
# After that, we'll show how to do it with its subclass selectMolsMode.

# First define classes which can work in either split C & GM form, or mixed form,
# which have most of the methods for each side. Each one has an init method which
# can call its superclass's init method, but which should not call any of the
# "glue init methods" in the superclass. The init methods should have the same
# arg signature as in their superclass.

# (In real life, these would go into different files, described later.
#  For clarity in this demo, they are all in one file.)

# We do the graphics part first since the command part has to refer to it.
#
# Its superclass, in general, should be another _basicGraphicsMode class.
# (In fully split modes that don't need mixed versions, it can also be the
#  value of command_superclass.GraphicsMode_class where command_superclass
#  is what the corresponding Command class inherits, or it can just be a
#  non-basic GraphicsMode class named directly, which should be the
#  same one used in the command superclass. But for modes with mixed versions,
#  it should just be the basicGraphicsMode version of the superclass
#  GraphicsMode.)

class Select_basicGraphicsMode(basicGraphicsMode):
    def __init__(self, glpane):
        """
        """
        basicGraphicsMode.__init__(self, glpane)
        # Now do whatever might be needed to init the graphicsMode object,
        # or the graphicsMode-related attrs of the mixed object.
        #
        # (Similar comments apply as for Select_basicCommand.__init__, below,
        #  but note that for GraphicsModes, there is no Enter method.
        #  Probably we will need to add something like an Enter_graphicsMode
        #  method to the GraphicsMode API. In the meantime, the command's Enter
        #  method has to initialize the graphicsMode object's attrs (which are
        #  the graphics-related attrs of self, in the mixed case, but are
        #  referred to as self.graphicsMode.attr so this will work in the split
        #  case as well), which is a kluge.)
        return

    # Now put all the methods from the "graphics area half" of the original
    # mode -- anything related to graphics, mouse events, cursors (for use in
    # graphics area), key bindings or context menu (for use in graphics area).

    def Draw(self, args):
        pass
    def someMouseMethod(self, args):
        pass
    def someCursorMethod(self, args):
        pass
    # etc

# The command part should in general inherit a _basicCommand superclass.
# Since selectMode inherited basicMode, we have Select_basicCommand inherit
# basicCommand;
# in comparison (done below), selectMolsMode inherited selectMode, so we'd
# make SelectChunks_basicCommand and inherit Select_basicCommand.

class Select_basicCommand(basicCommand):
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
    
    # Now put all the methods from the "command half" of the original
    # mode -- anything related to its property manager, its settings or
    # state, the model operations it does (unless those are so simple
    # that the mouse event bindings in the _GM half can do them directly
    # and the code is still clean, *and* no command-half subclass needs
    # to override them).

    def Enter(self, args):
        pass
    # etc

    # Every method in the original mode goes into one of these halves,
    # or gets split into two methods (with different names), one for
    # each half. If a method gets split, old code that called it (perhaps
    # in other files) needs to call both split methods, or one of them
    # needs to call the other. This requires some thought in each case
    # when it has to be done.

    pass

# ==

# Now we have to make the 3 glue classes.
# Their __init__ methods and properties can each be copied
# from the pattern used to split basicMode.

# Note that we call a "glue" __init__ method only in the "sub-most class"
# (the class we're actually instantiating); all superclass __init__ methods
# we call are in one of the _basicCommand or _basicGraphicsMode superclasses.

class Select_GraphicsMode( Select_basicGraphicsMode):
    """
    Glue class for GM-alone usage only
    """
    # Imitate the init and property code in GraphicsMode, but don't inherit it.
    # (Remember to replace all the occurrences of its superclass with our own.)
    # (When this is later merged with its superclass, most of this can go away
    #  since we'll then be inheriting GraphicsMode here.)

    # (Or can we inherit GraphicsMode *after* the main superclass, and not have
    #  to do some of this? I don't know. ### find out! [I think I did this in PanLikeMode.]
    #  At least we'd probably still need this __init__ method.
    #  If this pattern works, then in *our* subclasses we'd instead post-inherit
    #  this class, Select_GraphicsMode.)

    
    def __init__(self, command):
        self.command = command
        glpane = self.command.glpane 
        Select_basicGraphicsMode.__init__(self, glpane)
        return
    
    # (the rest would come from GraphicsMode if post-inheriting it worked,
    #  or we could split it out of GraphicsMode as a post-mixin to use there and here)

    def _get_commandSequencer(self):
        return self.command.commandSequencer

    commandSequencer = property(_get_commandSequencer)

    def set_cmdname(self, name):
        self.command.set_cmdname(name)
        return

    def _get_hover_highlighting_enabled(self):
        return self.command.hover_highlighting_enabled

    def _set_hover_highlighting_enabled(self, val):
        self.command.hover_highlighting_enabled = val

    hover_highlighting_enabled = property(_get_hover_highlighting_enabled, _set_hover_highlighting_enabled)

    pass

class Select_Command( Select_basicCommand):
    """
    Glue class for C-alone usage only
    """

    # This is needed so the init code knows what kind of GM to make.
    GraphicsMode_class = Select_GraphicsMode

    # Imitate the init and property code in Command, but don't inherit it.
    # (Remember to replace all the occurrences of its superclass with our own.)
    # (When this is later merged with its superclass, most of this can go away
    #  since we'll then be inheriting Command here.)

    # (Or can we inherit Command *after* the main superclass, and not have
    #  to do some of this? I don't know. ### find out! [I think I did this in PanLikeMode.]
    #  At least we'd probably still need this __init__ method.
    #  If this pattern works, then in *our* subclasses we'd instead post-inherit
    #  this class, Select_Command.)

    def __init__(self, commandSequencer):
        Select_basicCommand.__init__(self, commandSequencer)
        self._create_GraphicsMode()
        self._post_init_modify_GraphicsMode()
        return
    
    # (the rest would come from Command if post-inheriting it worked,
    #  or we could split it out of Command as a post-mixin to use there and here)
    
    def _create_GraphicsMode(self):
        GM_class = self.GraphicsMode_class
        assert issubclass(GM_class, GraphicsMode_API)
        args = [self] 
        kws = {} 
        self.graphicsMode = GM_class(*args, **kws)
        pass

    def _post_init_modify_GraphicsMode(self):
        pass

    pass

class selectMode( Select_basicCommand, Select_basicGraphicsMode, anyMode): # might need more superclasses for isinstance?
    """
    Glue class for mixed C/GM usage only
    """
    # Imitate the init and property code in basicMode, but don't inherit it.
    # (Remember to replace all the occurrences of one of its two main
    #  superclasses with the corresponding one of our own.)
    
    # (When we no longer need the mixed-C/GM case, this class can be discarded.)

    # (Or can we inherit basicMode *after* the main superclasses, and not have
    #  to do some of this? I don't know. ### find out! [I think I did this in PanLikeMode.]
    #  At least we'd still need this __init__ method. )

    def __init__(self, glpane):
        assert GLPANE_IS_COMMAND_SEQUENCER:
        commandSequencer = glpane
        
        Select_basicCommand.__init__(self, commandSequencer)
            # was just basicCommand in original
        
        Select_basicGraphicsMode.__init__(self, glpane)
            # was just basicGraphicsMode in original
        return

    # (the rest would come from basicMode if post-inheriting it worked,
    #  or we could split it out of basicMode as a post-mixin to use there and here)
    
    def __get_command(self):
        return self

    command = property(__get_command)

    def __get_graphicsMode(self):
        return self

    graphicsMode = property(__get_graphicsMode)

    pass

# putting these into the right files:

# in Select_Command we want that class, but first its basic version, Select_basicCommand.

# in Select_GraphicsMode we want that class, but first, Select_basicGraphicsMode.

# and in selectMode.py (same name as original mode) we want class selectMode as above.

# And several imports are needed to make this work, but they should be obvious
# from the NameErrors that come from forgetting them, e.g. of GLPANE_IS_COMMAND_SEQUENCER,
# anyMode, other superclasses.

# ==

# For SelectChunks, we'd make, in 3 files, and following the above pattern,
# but revising all superclass occurrences:

# SelectChunks_Command.py:
# SelectChunks_basicCommand inheriting Select_basicCommand
# SelectChunks_Command inheriting SelectChunks_basicCommand

# SelectChunks_GraphicMode.py
# SelectChunks_basicGraphicsMode inheriting Select_basicGraphicsMode
# SelectChunks_GraphicMode inheriting SelectChunks_basicGraphicsMode

# selectMolsMode.py (same name as old file):
# selectMolsMode, inheriting SelectChunk_basicCommand, SelectChunks_basicGraphicsMode

# ==

# If this all works right, then recombined versions of split/recombined mode classes will
# keep working with no problem at all, and so will their non-split subclasses,
# with no changes at all (except perhaps in isinstance tests).

# Not covered above:
#
# - when you'd need to add more stuff to the glue classes than what is copied/modified from their superclasses
#
# - how to use debug_prefs to test either _Command or mixed classes -- basically,
#   maybe easiest to use a hardcoded assignment instead, to put the _Command class into the GLPane list of modes
#   (I think that's right -- check what's done for PanMode etc to be sure)
#
# - what will still not work in the split case -- uses of one part's method or attr from the other part --
#   easiest fix is to change self.attr to self.command.attr for a command attr used in the GM part,
#   and to change self.attr to self.graphicsMode.attr for a GM attr used in the C part.
#   or you can use a property in a single place in the alone-case glue class.
#   But you have to decide where an attr belongs; it's not always obvious,
#   e.g. hover_highlighting_enabled belongs in C part though it's mainly used in GM part,
#   since C part is what wants to set it in certain circumstances. 
#
# - I think there was something else I forgot.

# ==

# end
