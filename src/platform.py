# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
platform.py -- module for platform-specific code,
especially for such code that needs to be called from various other modules.

Also includes some other code that might conceivably vary by platform,
but mainly is here since it had no better place to live.

$Id$
"""

import sys, os, time
from qt import Qt

# file utilities

def mkdirs_in_filename(filename):
    """Make all directories needed for the directory part of this filename,
    if nothing exists there. Never make the filename itself (even if it's
    intended to be a directory, which we have no way of knowing anyway).
    If something other than a directory exists at one of the dirs we might
    otherwise make, we don't change it, which will probably lead to errors
    in this function or in the caller, which is fine.
    """
    dir, file = os.path.split(filename)
    if not os.path.exists(dir):
        mkdirs_in_filename(dir)
        os.mkdir(dir)
    return

# event code

def is_macintosh():
    #e we might need to update this, since I suspect some mac pythons
    # have a different value for sys.platform
    return sys.platform in ['darwin']

def filter_key(key, debug_keys = 0):
    """given a Qt keycode key, usually return it unchanged,
       but return a different keycode if that would help fix platform-specific bugs in Qt keycodes
       or in our use of them.
    """
    # bruce 040929 split this out of basicMode.keyPress(), where I'd added it
    # as a mac-specific bugfix.
    if is_macintosh():
        # Help fix Qt's Mac-specific Delete key bug, bug 93.
        ###bruce 040924 temp fix, should be revised once we understand relation to other systems (see my email to josh & ninad):
        if key == 4099: ##k will this 4099 be the same in other macs? other platforms? Does Qt define it anywhere??
            if debug_keys:
                print "fyi: mac bugfix: remapping key %d (actual delete key) to key %d (Qt.Key_Delete)" % (key, Qt.Key_Delete)
            key = Qt.Key_Delete
    return key

def atom_event(qt_event):
    """Return our own event object in place of (or wrapping) the given Qt event.
    Fix bugs in Qt events, and someday provide new features to help in history-tracking.
    So far [041220] this only handles key events, and does no more than fix the Mac-specific
    bug in the Delete key (bug 93).
    """
    return atomEvent(qt_event)

class atomEvent:
    "our own event type. API should be non-qt-specific."
    def __init__(self, qt_event):
        self._qt_event = qt_event # private
    def key(self):
        return filter_key( self._qt_event.key() )
    def ascii(self):
        return filter_key( self._qt_event.ascii() )
    #e more methods might be needed here
    pass

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


# code which contains hardcoded filenames in the user's homedir, etc
# (moved into this module from MWsemantics.py by bruce 050104,
#  since not specific to one window, might be needed before main window init,
#  and the directory names might become platform-specific.)

_tmpFilePath = None

def find_or_make_Nanorex_prefs_directory():
    """
    Find or make the directory ~/Nanorex, in which we will store
    preferences, temporary files, etc.
    If it doesn't exist and can't be made, try using /tmp.
    [#e Future: for Windows that backup dir should be something other than /tmp.
     And for all OSes, we should use a more conventional place to store prefs
     if there is one (certainly there is on Mac).]
    """
    global _tmpFilePath
    if _tmpFilePath:
        return _tmpFilePath # already chosen, always return the same one
    _tmpFilePath = _find_or_make_prefsdir_0()
    assert _tmpFilePath
    return _tmpFilePath

def _find_or_make_prefsdir_0():
    """private helper function for find_or_make_Nanorex_prefs_directory"""
    
    #Create the temporary file directory if not exist [by huaicai ~041201]
    # bruce 041202 comments about future changes to this code:
    # - we'll probably rename this, sometime before Alpha goes out,
    #   since its purpose will become more user-visible and general.
    # - it might be good to create a README file in the directory
    #   when we create it. And maybe to tell the user we created it,
    #   in a dialog.
    # - If creating it fails, we might want to create it in /tmp
    #   (or wherever some python function says is a good temp dir)
    #   rather than leaving an ususable path in tmpFilePath. This
    #   could affect someone giving a demo on a strange machine!
    # - If it exists already, we might want to test that it's a
    #   directory and is writable. If we someday routinely create
    #   a new file in it for each session, that will be a good-
    #   enough test.
    tmpFilePath = os.path.normpath(os.path.expanduser("~/Nanorex/"))
    if not os.path.exists(tmpFilePath):
        from debug import print_compact_traceback
        try:
            os.mkdir(tmpFilePath)
        except:
            #bruce 041202 fixed minor bug in next line; removed return statement
            print_compact_traceback("exception in creating temporary directory: \"%s\"" % tmpFilePath)
            #bruce 050104 new feature [needs to be made portable so it works on Windows ###@@@]
            os_tempdir = "/tmp"
            print "warning: using \"%s\" for temporary directory, since \"%s\" didn't work" % (os_tempdir, tmpFilePath)
            tmpFilePath = os_tempdir
    #e now we should create or update a README file in there [bruce 050104]
    return tmpFilePath

def make_history_filename():
    """[private method for history init code]
    Return a suitable name for a new history file (not an existing filename).
    The filename contains the current time, so should be called once per history
    (probably once per process), not once per window when we have more than one.
    This filename could also someday be used as a "process name", valid forever,
    but relative to the local filesystem.
    """
    prefsdir = find_or_make_Nanorex_prefs_directory()
    tried_already = None
    while 1:
        histfile = os.path.join( prefsdir, "Histories", "h%s.txt" % time.strftime("%Y%m%d-%H%M%S") )
            # e.g. ~/Nanorex/Histories/h20050104-160000.txt
        if not os.path.exists(histfile):
            if histfile == tried_already:
                # this is ok, but is so unlikely that it might indicate a bug, so report it
                print "fyi: using history file \"%s\" after all; someone removed it!" % histfile
            return histfile # caller should print this at some point
        # Another process which wants to use the same kind of history filename
        # (in the same Nanorex-specific prefs directory) must have started less
        # than one second before! Wait for this to be untrue. Print something,
        # in case this gets into an infloop from some sort of bug. This is rare
        # enough that it doesn't matter much what we print -- hardly anyone
        # should see it.
        if histfile != tried_already:
            print "fyi: history file \"%s\" already exists; will try again shortly..." % histfile
        tried_already = histfile # prevent printing another msg about the same filename
        time.sleep(0.35)
        continue
    pass

# When we start, figure out whether user wants to enable general debugging code
# which turns on extra internal error checking (perhaps slowing down the code).
# There is no need to document this, since it is intended for developers familiar
# with the python code.
# I put this into platform.py in case the way of initializing it is platform-specific.
# If we think of a more sensible place to put this, we can move it. [bruce 041103]

try:
    atom_debug # don't disturb it if already set (e.g. by .atom-debug-rc)
except:
    try:
        atom_debug = os.environ['ATOM_DEBUG'] # as a string; suggest "1" or "0"
    except:
        atom_debug = 0
    try:
        atom_debug = int(atom_debug)
    except:
        pass
    atom_debug = not not atom_debug
if atom_debug:
    print "fyi: user has requested ATOM_DEBUG feature; extra debugging code enabled; might be slower"

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
        elif word.endswith("(s)") or word.endswith("(s),"):
            # (that condition is a kluge, should be generalized [bruce 041217])
            suflen = ( word.endswith("(s),") and 1) or 0 # klugier and klugier
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
                if suflen:
                    words[i], suffix = words[i][:-suflen], words[i][-suflen:]
                else:
                    suffix = ""
                if num == "1":
                    words[i] = words[i][:-3] + suffix
                else:
                    words[i] = words[i][:-3] + "s" + suffix
            else:
                # error, but no change to words[i]
                print "fyi, cosmetic bug: fix_plurals(%r) found no number close enough to affect %r" % (text,word)
            numpos = -1 # don't permit "2 dog(s) cat(s)" -> "2 dogs cats"
    if not count:
        print """fyi, possible cosmetic bug: fix_plurals(%r) got text with no "(s)", has no effect""" % (text,)
    return " ".join(words)

# == test code

if __name__ == "__main__":
    msg = 'Dehydrogenate: removed 4 atom(s) from 1 molecule(s) (1 selected molecule(s) had no hydrogens)'
    msg2 = 'Dehydrogenate: removed 4 atoms from 1 molecule (1 selected molecule had no hydrogens)'
    assert fix_plurals(msg) == msg2
    print "test done"

# end
