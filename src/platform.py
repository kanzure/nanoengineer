# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
platform.py -- module for platform-specific code,
especially for such code that needs to be called from various other modules.

$Id$
"""

import sys
from qt import Qt

def is_macintosh():
    #e we might need to update this, since I suspect some mac pythons
    # have a different value for sys.platform
    return sys.platform in ['darwin']

def filter_key(key, debug_keys = 0): # bruce 040929 split this out of basicMode.keyPress(), where I'd added it as a mac-specific bugfix.
    """given a Qt keycode key, usually return it unchanged,
       but return a different keycode if that would help fix platform-specific bugs in Qt keycodes
       or in our use of them.
    """
    if is_macintosh():
        ###bruce 040924 temp fix, should be revised once we understand relation to other systems (see my email to josh & ninad):
        if key == 4099: ##k will this 4099 be the same in other macs? other platforms? Does Qt define it anywhere??
            if debug_keys:
                print "fyi: mac bugfix: remapping key %d (actual delete key) to key %d (Qt.Key_Delete)" % (key, Qt.Key_Delete)
            key = Qt.Key_Delete
    return key

#e there might be other code mentioning "darwin" which should be moved here... maybe also modifier keys in constants.py...

# Use these names for our modifier keys and for how to get the context menu, in messages visible to the user.

def shift_name():
    "name of Shift modifier key"
    return "Shift"

def control_name():
    "name of Control modifier key"
    if is_macintosh():
        return "Command"
    else:
        return "Control"
    pass

def context_menu_prefix():
    """what to say instead of "context" in the phrase "context menu" """
    if is_macintosh():
        return "Control"
    else:
        return "Right" #k I think
    pass

def middle_button_prefix():
    """what to say instead of "middle" as a prefix for press or click,
    for middle mouse button actions
    """
    if is_macintosh():
        return "Option" # name of Option/Alt modifier key
    else:
        return "Middle" # refers to middle mouse button
    pass

# here are some functions involving user messages, which don't really belong in
# this file, but there is not yet a better place for them. [bruce 041018]

def fix_plurals(text, between = 1):
    """fix plurals in text (a message for the user) by changing:
      1 thing(s) -> 1 thing
      2 thing(s) -> 2 things
    permitting at most 'between' extra words in between,
    e.g. by default
      2 green thing(s) -> 2 green things.
    #"""
    words = text.split(" ")
    numpos = -1
    count = 0
    for word,i in zip(words,range(len(words))):
        if word and word[-1].isdigit():
            # if word ends with a digit, call it a number (e.g. "(1" )
            numpos = i
        elif word.endswith("(s)"):
            count += 1
            if numpos >= 0 and (i-numpos) <= (between+1): # not too far back
                # fix word for whether number is 1
                nw = words[numpos]
                assert nw and nw[-1].isdigit()
                # consider only the adjacent digits at the end
                num = ""
                for cc in nw:
                    num += cc
                    if not cc.isdigit():
                        num = ""
                if num == "1":
                    words[i] = words[i][:-3]
                else:
                    words[i] = words[i][:-3] + "s"
            else:
                # error, but no change to words[i]
                print "fyi, cosmetic bug: fix_plurals(%r) found no number close enough to affect %r" % (text,word)
            numpos = -1 # don't permit "2 dog(s) cat(s)" -> "2 dogs cats"
    if not count:
        print """fyi, possible cosmetic bug: fix_plurals(%r) got text with no "(s)", has no effect""" % (text,)
    return " ".join(words)

# end

if __name__ == "__main__":
    print fix_plurals('Dehydrogenate: removed 4 atom(s) from 1 molecule(s) (1 selected molecule(s) had no hydrogens)')
    
'''
    fyi, cosmetic bug: fix_plurals('Dehydrogenate: removed 4 atom(s) from 1 molecule(s) (1 selected molecule(s) had no hydrogens)') found no number close enough to affect 'molecule(s)'
'''
