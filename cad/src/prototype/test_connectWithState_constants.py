# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
test_connectWithState_constants.py -- constants for use in
test_connectWithState command and its PM.

This file can be merged into the command class, once it's possible
for the PM code to get these values directly from the staterefs
(an intended improvement).

$Id$

History:

070830 bruce split this out of test_command_PMs.py
"""

# definitions for cylinder height and caps style, stored as preferences values
#
# (Note: in a realistic example, these would be defined using the State macro,
#  just as is done for the other state, below. The only reason they're defined
#  as preference values here is to illustrate how that kind of state can be used
#  interchangeably with State-macro-defined instance variables by connectWithState.)

CYLINDER_HEIGHT_PREFS_KEY = "a9.2 scratch/test_connectWithState_PM/cylinder height"
CYLINDER_HEIGHT_DEFAULT_VALUE = 7.5

CYLINDER_ROUND_CAPS_PREFS_KEY = "a9.2 scratch/test_connectWithState_PM/cylinder round_caps"
CYLINDER_ROUND_CAPS_DEFAULT_VALUE = True

def cylinder_round_caps():
    import foundation.env as env
    return env.prefs.get( CYLINDER_ROUND_CAPS_PREFS_KEY, CYLINDER_ROUND_CAPS_DEFAULT_VALUE)

# The state for cylinder width, cylinder color [nim], and cylinder orientation
# is defined using the State macro in the command object (not in this file).
# It could be referenced by the PM class in this file by:
# - self.command.cylinderWidth
# - self.command.cylinderColor (nim)
# - self.command.cylinderVertical (###NIM)
# but in fact is referenced indirectly using string literals for those attr names.

CYLINDER_VERTICAL_DEFAULT_VALUE = True
CYLINDER_WIDTH_DEFAULT_VALUE = 2.0
    ### REVISE: the default value should come from the stateref, when using the State macro

# end
