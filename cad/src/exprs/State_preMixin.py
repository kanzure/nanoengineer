# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.
"""
State_preMixin.py - help classes define change-tracked attributes using the State macro

@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

080910 bruce split this out of test_connectWithState.py, since it's
been used in real code for some time
"""

from exprs.ExprsMeta import ExprsMeta
from exprs.IorE_guest_mixin import IorE_guest_mixin

class State_preMixin( IorE_guest_mixin):
    # TODO: refile (alongside IorE_guest_mixin ? in its own file?), once cleaned up & bugfixed --
    # note, as of 080128 or so, this is used in real code.
    """
    Use this as the *first* superclass (thus the _preMixin in the name)
    in order to permit use of the State macro in the class assignments
    which set up instance variable defaults in a given class.
    The glpane (*not* the commandSequencer!) must be passed as the
    first argument to __init__.
    """
    # the following are needed for now in order to use the State macro,
    # along with the IorE_guest_mixin superclass; this may be cleaned up:
    __metaclass__ = ExprsMeta
    _e_is_instance = True ### REVIEW: can the superclass define this, since to work as a noninstance you need a special subclass?
    _e_has_args = True # not needed -- only purpose is to remove "w/o a" from repr(self)

    def __init__(self, glpane, *args, **kws):
        DEBUG_INIT = False # if True, enables some debug prints in console
        if DEBUG_INIT:
            print "State_preMixin.__init__", glpane, args, kws
        IorE_guest_mixin.__init__(self, glpane)

        # REVIEW: should callers do the following, not us?
        if DEBUG_INIT:
            print " State_preMixin.__init__ will call", super(State_preMixin, self).__init__
                ## <bound method test_connectWithState.__init__ of <test_connectWithState#4789(i w/o a)>>

            # note: the following debug output suggests that this would cause
            # infinite recursion, but something prevents it from happening at all
            # (it seems likely that no call at all is happening, but this is not yet
            #  fully tested -- maybe something different is called from what's printed)
            #
            ##debug fyi: starting DnaSegment_EditCommand.__init__
            ##State_preMixin.__init__ <GLPane 0> () {}
            ## State_preMixin.__init__ will call <bound method DnaSegment_EditCommand.__init__ of <DnaSegment_EditCommand#6986(i)>>
            ## State_preMixin.__init__ returned from calling <bound method DnaSegment_EditCommand.__init__ of <DnaSegment_EditCommand#6987(i)>>
            ##debug fyi: inside DnaSegment_EditCommand.__init__, returned from State_preMixin.__init__

        super(State_preMixin, self).__init__(glpane, *args, **kws)
            # this is not calling ExampleCommand.__init__ as I hoped it would. I don't know why. ###BUG
            # (but is it calling anything? i forget. clarify!)
        if DEBUG_INIT:
            print " State_preMixin.__init__ returned from calling", super(State_preMixin, self).__init__
    pass

# end
