# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
command_levels.py - utilities for interpreting and using command_level values,
including the rules for how commands can nest on the command stack

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

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

from utilities.constants import CL_REQUEST

# level constants not allowed for actual commands:
from utilities.constants import CL_ABSTRACT # for abstract command classes
    # (warning if instantiated directly)
from utilities.constants import CL_UNUSED # for command classes thought to be presently unused
    # (warning if instantiated directly, or (if practical) if a subclass is
    #  instantiated)

from utilities.constants import DEFAULT_COMMAND

# ==

# set up rules for fixed-parent command levels

_USE_COMMAND_PARENT = '_USE_COMMAND_PARENT' # marks a fixed-parent command

_ALLOWED_PARENT_LEVELS = {
    CL_DEFAULT_MODE: (), # no parent is acceptable!
    CL_ENVIRONMENT_PROVIDING: _USE_COMMAND_PARENT,
        # this means only the specified command_parent is acceptable, no other!
        # (or the default command, if none is specified.)
        # So it needs special case code, since it's not just
        # a level like the others.
    CL_MISC_TOPLEVEL: (CL_DEFAULT_MODE,),
    CL_SUBCOMMAND: _USE_COMMAND_PARENT,
 } # note: this dict is modified below

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

# request command rule is added last, since it refers to all keys added so far:
_apl[ CL_REQUEST ] = tuple( [CL_REQUEST] + _apl.keys() ) # not sorted, should be ok


# public constants constructed from the above private ones

LEGAL_COMMAND_LEVELS = _ALLOWED_PARENT_LEVELS.keys()

FIXED_PARENT_LEVELS = [level
                       for level in LEGAL_COMMAND_LEVELS
                       if _apl[level] == _USE_COMMAND_PARENT]

_IGNORE_FLYOUT_LEVELS = (
        CL_VIEW_CHANGE,
        CL_REQUEST,
        CL_ABSTRACT,
        CL_UNUSED,
 )

AFFECTS_FLYOUT_LEVELS = filter( lambda level: level not in _IGNORE_FLYOUT_LEVELS,
                                LEGAL_COMMAND_LEVELS )

def allowed_parent( want, parent ): #bruce 080815
    """
    Assume that the user wants to enter command class (or instance) <want>,
    and current command class (or instance) is <parent>,
    and that the caller already knows we're not *already* in the desired
    command.

    (Note that this means that if we immediately entered <want>,
     its parent command would be <parent>, whether or not that's
     acceptable.)

    @return: whether <parent> is a suitable parent
             or grandparent (etc) command for <want>.
    @rtype: boolean

    If we return True, it means the caller shouldn't exit
    any commands, though it may need to enter some before
    entering <want>.

    If we return False, it means the caller does need to exit <parent>,
    then call us again to decide what to do.
    """
    # future: will we need any other retvals besides yes and no?
    # maybe, more info about what to do to get to <want>?

    # make sure the info we will use is present:

    want.command_level
    want.command_parent

    parent.command_level
    parent.command_parent
    parent.commandName

    # if want.command_level is illegal, the following will fail (KeyError)
    # (we should check this earlier, in the "command description"
    #  (i.e. FeatureDescriptor) #todo)
    # (we might revise the caller to pass the FeatureDescriptor here,
    #  in place of what's now used for want and parent, namely,
    #  actual command instances)

    allowed_parent_levels = _ALLOWED_PARENT_LEVELS[ want.command_level ]

    if allowed_parent_levels == _USE_COMMAND_PARENT:

        # want is a fixed-parent command

        # just check whether parent is the desired parent, or is a parent of that ...
        ### really part of a higher alg in caller? and/or a new command class method?
        allowed_parent_names = [ want.command_parent or DEFAULT_COMMAND ]
        allowed_parent_names += [ DEFAULT_COMMAND ] # don't bother to remove duplicates
        # WARNING: THIS ASSUMES AT MOST ONE LEVEL OF REQUIRED PARENTS

        res = parent.commandName in allowed_parent_names

    else:

        # <want> is nestable
        # (or a fixed parent command that doesn't care about
        #  its command_parent field? I don't think that's possible.)

        # (Note: this scheme would not be sufficient for a command which is
        # "nestable under any subcommand of a given environment-providing command,
        #  but not under other kinds of subcommands".)

        res = parent.command_level in allowed_parent_levels

    return res

# end

