# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
drawing_constants.py - constants and helpers for graphics.drawing package

@author: Russ, plus others if the code that belongs here is ever moved here
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details. 

History:

090304 bruce split out of drawing_globals to avoid import cycles

TODO:

some geometric variables (but not display lists!) stored into drawing_globals
by external code (mostly setup_draw) should instead be defined here.
"""

# Common constants and helpers for DrawingSet, TransformControl, et al.

# Russ 080915: Support for lazily updating drawing caches, namely a change
# timestamp.  Rather than recording a time per se, an event counter is used.
NO_EVENT_YET = 0
_event_counter = NO_EVENT_YET
def eventStamp():
    global _event_counter
    _event_counter += 1
    return _event_counter

def eventNow(): # not used
    return _event_counter

# end
