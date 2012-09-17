# Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details.
"""
undo_UI.py - Undo-related main menu commands other than Undo/Redo themselves

@author: bruce
@version: $Id$
@copyright: 2005-2007 Nanorex, Inc.  See LICENSE file for details.

History:

bruce 071025 split this out of undo_manager.py
to rationalize import dependencies

TODO:

- general cleanup, especially of comments

WARNING: most comments have not been not reviewed since this code was moved
out of undo_manager.py [as of 071025], so they may be misleadingly out of
context.
"""

from utilities.debug import print_compact_traceback

import foundation.env as env
from utilities.Log import greenmsg, redmsg, _graymsg

from widgets.widget_helpers import PleaseConfirmMsgBox

# ==

def editMakeCheckpoint(win):
    """
    This is called from MWsemantics.editMakeCheckpoint,
    which is documented as:

      "Slot for making a checkpoint (only available when
       Automatic Checkpointing is disabled)."
    """
    env.history.message( greenmsg("Make Checkpoint"))
    # do it
    try:
        #REVIEW: Should make sure this is correct with or without
        # auto-checkpointing enabled, and leaves that setting unchanged.
        # (This is not urgent, since in present UI it can't be called
        #  except when auto-checkpointing is disabled.)
        um = win.assy.undo_manager
        if um:
            um.make_manual_checkpoint()
            # no msg needed, was emitted above:
            ## env.history.message(greenmsg("Make Checkpoint"))
            pass
        else:
            # this should never happen
            msg = "Make Checkpoint: error, no undo_manager"
            env.history.message(redmsg(msg))
    except:
        print_compact_traceback("exception caught in editMakeCheckpoint: ")
        msg = "Internal error in Make Checkpoint. " \
              "Undo/Redo might be unsafe until a new file is opened."
        env.history.message(redmsg(msg))
            #e that wording assumes we can't open more than one file at a time...
    return

def editClearUndoStack(win):
    """
    This is called from MWsemantics.editClearUndoStack,
    which is documented as:

      "Slot for clearing the Undo Stack.  Requires the user to confirm."
    """
    #bruce 060304, modified from Mark's prototype in MWsemantics

    #e the following message should specify the amount of data to be lost...
    #e and the menu item text also should
    msg = "Please confirm that you want to clear the Undo/Redo Stack.<br>" + \
          _graymsg("(This operation cannot be undone.)")
    confirmed = PleaseConfirmMsgBox( msg)
        # TODO: I bet this needs a "don't show this again" checkbox...
        # with a prefs key...
    if not confirmed:
        env.history.message("Clear Undo Stack: Cancelled.") #k needed??
        return
    # do it
    env.history.message(greenmsg("Clear Undo Stack"))
        # no further message needed if it works, I think
    try:
        ##e Note: the following doesn't actually free storage.
        # [update, 060309 -- i think as of a few days ago it does try to... ##k]
        # Once the UI seems to work, we'll either add that to it,
        # or destroy and remake assy.undo_manager itself before doing this
        # (and make sure destroying it frees storage).
        ##e Make sure this can be called with or without auto-checkpointing
        # enabled, and leaves that setting unchanged. #####@@@@@
        win.assy.clear_undo_stack()
    except:
        print_compact_traceback("exception in clear_undo_stack: ")
        msg = "Internal error in Clear Undo Stack. " \
              "Undo/Redo might be unsafe until a new file is opened."
        env.history.message(redmsg(msg))
            #e that wording assumes we can't open more than one file at a time...
    return

# bugs in editClearUndoStack [some fixed as of 060304 1132p PST, removed now]:
# cosmetic:
# + [worked around in this code, for now] '...' needed in menu text;
# - it ought to have ram estimate in menu text;
# - "don't show again" checkbox might be needed
# - does the dialog (or menu item if it doesn't have one) need a wiki help
#   link?
# - dialog starts out too narrow
# - when Undo is disabled at the point where stack was cleared, maybe text
#   should say it was cleared? "Undo stack cleared (%d.)" ???

# end
