# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
platform.py -- module for platform-specific code,
especially for such code that needs to be called from various other modules.

$Id$
"""

import sys
from qt import Qt

def filter_key(key, debug_keys = 0): # bruce 040929 split this out of basicMode.keyPress(), where I'd added it as a mac-specific bugfix.
    """given a Qt keycode key, usually return it unchanged,
       but return a different keycode if that would help fix platform-specific bugs in Qt keycodes
       or in our use of them.
    """
    if sys.platform == 'darwin': #e we'll need to update this, since some mac pythons have a different sys.platform
        ###bruce 040924 temp fix, should be revised once we understand relation to other systems (see my email to josh & ninad):
        if key == 4099: ##k will this 4099 be the same in other macs? other platforms? Does Qt define it anywhere??
            if debug_keys:
                print "fyi: mac bugfix: remapping key %d (actual delete key) to key %d (Qt.Key_Delete)" % (key, Qt.Key_Delete)
            key = Qt.Key_Delete
    return key

#e there might be other code mentioning "darwin" which should be moved here... maybe also modifier keys in constants.py...

# end
