# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
command_levels.py - utilities for interpreting and using command_level values

SCRATCH FILE, might be moved, split, etc ###

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""



##        # then based on args, decide what to ask new current command to do --
##        # maybe _command_do_exit_if_ok, or _command_do_enter_if_ok (on an instance I guess??), or just reset
##        nim
        

# fixed_parent command levels:
from utilities.constants import CL_DEFAULT_MODE
from utilities.constants import CL_ENVIRONMENT_PROVIDING
from utilities.constants import CL_MISC_TOPLEVEL # like subcommand of default mode, I think ###
from utilities.constants import CL_SUBCOMMAND

# nestable (or partly nestable) command levels:
from utilities.constants import CL_EDIT_GENERIC
from utilities.constants import CL_EXTERNAL_ACTION
from utilities.constants import CL_GLOBAL_PROPERTIES
from utilities.constants import CL_VIEW_CHANGE

from utilities.constants import CL_REQUEST ##### BUG: not yet used below

# level constants not allowed for actual commands:
from utilities.constants import CL_ABSTRACT # for abstract command classes
    # (warning if instantiated directly)
from utilities.constants import CL_UNUSED # for command classes thought to be presently unused
    # (warning if instantiated directly, or (if practical) if a subclass is
    #  instantiated)

_USE_COMMAND_PARENT = '_USE_COMMAND_PARENT'

# set up rules for fixed-parent command levels

_ALLOWED_PARENT_LEVELS = {
    CL_DEFAULT_MODE: (), # no parent is acceptable!
    CL_ENVIRONMENT_PROVIDING: _USE_COMMAND_PARENT,
        # the specific command_parent (typically None) is acceptable, no other! not just a level... ######
    CL_MISC_TOPLEVEL: (CL_DEFAULT_MODE,),
    CL_SUBCOMMAND: _USE_COMMAND_PARENT,
 } # note: modified below

# add rules for nestable levels

_apl = _ALLOWED_PARENT_LEVELS # make following mods more readable

_apl[ CL_EDIT_GENERIC ] = \
    (CL_ENVIRONMENT_PROVIDING, CL_DEFAULT_MODE) # "partly nestable"

_apl[ CL_EXTERNAL_ACTION ] = \
    (CL_EDIT_GENERIC, CL_SUBCOMMAND, CL_MISC_TOPLEVEL,
     CL_ENVIRONMENT_PROVIDING, CL_DEFAULT_MODE) # "fully nestable"

_apl[ CL_GLOBAL_PROPERTIES ] = \
    (CL_EXTERNAL_ACTION,) + _apl[ CL_EXTERNAL_ACTION ]

_apl[ CL_VIEW_CHANGE ] = \
    (CL_GLOBAL_PROPERTIES,) + _apl[ CL_GLOBAL_PROPERTIES ]


LEGAL_COMMAND_LEVELS = _ALLOWED_PARENT_LEVELS.keys()


def allowed_parent( want, parent ): # in CommandSequencer
    """
    User wants to enter command class (or instance) <want>
    and current command is <parent>.
    
    (If we enter <want> directly, <parent> will become the parent command.)

    Decide whether <parent> is an acceptable parent command for <want>
    (return a boolean). ### any other retvals besides yes and no? maybe, more info about what to do to get to <want>?
    (we really mean parent or grandparent or ...)

    Assume we already determined we're not *already* in the desired command. ###
    """

    # the info we will use:

    want.command_level
    want.command_parent

    parent.command_level
    parent.command_parent

    
    #### deal with illegal levels -- can we do this in the command description,
    # and always grab the description for use here (probably in the caller)?

    
    allowed_parent_levels = _ALLOWED_PARENT_LEVELS[ want.command_level ]

    if allowed_parent_levels == _USE_COMMAND_PARENT:
        # just check whether parent is the desired parent, or is a parent of that ... ### really part of a higher alg in caller? and/or a new command class method?
        nim ###

    # <want> is nestable, or a fixed parent command that doesn't care about
    # its command_parent field.
    
    # (Note: this scheme would not be sufficient for a command which is
    # "nestable under any subcommand of a given environment-providing command,
    #  but not under other kinds of subcommands".)
    
    return parent.command_level in allowed_parent_levels







