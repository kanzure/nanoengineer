# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
"""
platform.py -- module for platform-specific code,
especially for such code that needs to be called from various other modules.

Also includes some other code that might conceivably vary by platform,
but mainly is here since it had no better place to live. In fact, by 060106
most of its code is like that, and a lot of it has something to do with messages
or the screen or files, that is, issues having to do with both the UI and the
OS interface.

$Id$

bruce 050913 used env.history in some places, revised open_file_in_editor API.
"""
__author__ = "bruce" # and others

import sys, os, time
from qt import Qt, QDesktopWidget, QRect
from constants import * # e.g. for leftButton

import env

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
    def state(self):
        return self._qt_event.state()
    def stateAfter(self):
        return self._qt_event.stateAfter()
    # Added isAutoRepeat.  Mark 050410
    def isAutoRepeat(self):
        return filter_key( self._qt_event.isAutoRepeat() )
    #e more methods might be needed here
    pass

#e there might be other code mentioning "darwin" which should be
#  moved here... maybe also modifier keys in constants.py...

# Use these names for our modifier keys and for how to get the context menu,
# in messages visible to the user.

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

# helpers for processing modifiers on mouse events
# [moved here from GLPane.py -- bruce 050112]

def fix_event_helper(self, event, when, target = None): #bruce 050913 new API; should merge them, use target, doc this one
    if when == 'press':
        but = event.stateAfter()
    else:
        but = event.state()
    but = fix_buttons_helper(self, but, when)
    return but

def fix_buttons_helper(self, but, when):
    """
    Every mouse event's button and modifier key flags should be
    filtered through this method (actually just a "method helper function").

    Arguments:
    
    - self can be the client object; we use it only for storing state
      between calls, namely, self._fix_buttons_saved_buttons.
      The caller need no longer init that to 0.
      
    - 'but' should be the flags from event.stateAfter() or
      event.state(), whichever ones would have the correct set of
      mousebuttons -- this depends on the type of event; see the
      usage in GLPane for an example.
      
    - 'when' should be 'press', 'move', or 'release', according
      to how this function should treat the buttons and modifier keys --
      it will record them for press, and then maintain the same
      ones (in its return value) for move or release, regardless
      of what the real modifier keys and buttons did.

    Returns: a new version of 'but' which is simpler for client code
    to use correctly (as described below).

    Known bugs [as of 050113]: reportedly prints warnings, and perhaps
    has wrong results, when dialogs intercept some "release" events.
    (Or am I confusing these rumors with ones about key-releases?)
    Should be easy to fix given a repeatable example.
    
    More details: this function does two things:

    1. Store all button and modifier-key flags from a mouse-press,
    and reuse them on the
    subsequent mouse-drag and mouse-release events (but not on
    pure mouse-moves), so the caller can just switch on the flags
    to process the event, and will always call properly paired
    begin/end routines (this matters if the user releases or
    presses a modifier key during the middle of a drag; it's
    common to release a modifier key then).

    2. On the Mac, remap
    Option+leftButton to middleButton, so that the Option key
    (also called the Alt key) simulates the middle mouse button.
    (Note that Qt/Mac, by default, lets Control key simulate
    rightButton and remaps Command key to the same flag we call
    cntlButton; we like this and don't change it here.)
    """
    # [by bruce, 040917 (in GLPane.py). At time of commit,
    # tested only on Mac with one-button mouse.]
    
    allButtons = (leftButton|midButton|rightButton)
    allModKeys = (shiftButton|cntlButton|altButton)
    allFlags = (allButtons|allModKeys)
    _debug = 0 # set this to 1 to see some debugging messages
    if when == 'move' and (but & allButtons):
        when = 'drag'
    assert when in ['move','press','drag','release']

    if not hasattr(self, '_fix_buttons_saved_buttons'):
        self._fix_buttons_saved_buttons = 0
    
    # 1. bugfix: make mod keys during drag and button-release the
    # same as on the initial button-press.  Do the same with mouse
    # buttons, if they change during a single drag (though I hope
    # that will be rare).  Do all this before remapping the
    # modkey/mousebutton combinations in part 2 below!
    
    if when == 'press':
        self._fix_buttons_saved_buttons = but & allFlags
        # we'll reuse this button/modkey state during the same
        # drag and release
        if _debug and self._fix_buttons_saved_buttons != but:
            print "fyi, debug: fix_buttons: some event flags unsaved: %d - %d = 0x%x" % (
                but, self._fix_buttons_saved_buttons, but - self._fix_buttons_saved_buttons)
            # fyi: on Mac I once got 2050 - 2 = 0x800 from this statement;
            # don't know what flag 0x800 means; shouldn't be a problem
    elif when in ['drag','release']:
        if (self._fix_buttons_saved_buttons & allButtons):
            but0 = but
            but &= ~allFlags
            but |= self._fix_buttons_saved_buttons
            # restore the modkeys and mousebuttons from the mousepress
            if _debug and but0 != but:
                print "fyi, debug: fix_buttons rewrote but0 0x%x to but 0x%x" % (but0, but) #works
        else:
            
            # fyi: This case might happen in the following rare
            # and weird situation: - the user presses another
            # mousebutton during a drag, then releases the first
            # one, still in the drag; - Qt responds to this by
            # emitting two mouseReleases in a row, one for each
            # released button.  (I don't know if it does this;
            # testing it requires a 3-button mouse, but the one I
            # own is unreliable.)
            #
            # In that case, this code might make some sense of
            # this, but it's not worth analyzing exactly what it
            # does for now.
            #
            # If Qt instead suppresses the first mouseRelease
            #until all buttons are up (as I hope), this case never
            #happens; instead the above code pretends the same
            #mouse button was down during the entire drag.
            print "warning: Qt gave us two mouseReleases without a mousePress;"
            print " ignoring this if we can, but it might cause bugs"
            pass # don't modify 'but'
    else:
        pass # pure move (no mouse buttons down):
             #  don't revise the event flags
    if when == 'release':
        self._fix_buttons_saved_buttons = 0
    
    # 2. let the Mac's Alt/Option mod key simulate middle mouse button.
    if sys.platform in ['darwin']:
        
### please try adding your platform here, and tell me whether it
### breaks anything... see below.
        
        # As of 040916 this hasn't been tested on other platforms,
        # so I used sys.platform to limit it to the Mac.  Note
        # that sys.platform is 'darwin' for my MacPython 2.3 and
        # Fink python 2.3 installs, but might be 'mac' or
        # 'macintosh' or so for some other Macintosh Pythons. When
        # we find out, we should add those to the above list.  As
        # for non-Mac platforms, what I think this code would do
        # (if they were added to the above list) is either
        # nothing, or remap some other modifier key (different
        # than Shift or Control) to middleButton.  If it does the
        # latter, maybe we'll decide that's good (for users with
        # less than 3 mouse buttons) and document it.
        
        # -- bruce 040916-17
        
        if (but & altButton) and (but & leftButton):
            but = but - altButton - leftButton + midButton
    return but

# ===

# Finding or making special directories and files (e.g. in user's homedir):

# code which contains hardcoded filenames in the user's homedir, etc
# (moved into this module from MWsemantics.py by bruce 050104,
#  since not specific to one window, might be needed before main window init,
#  and the directory names might become platform-specific.)

_tmpFilePath = None

def find_or_make_Nanorex_directory():
    """
    Find or make the directory ~/Nanorex, in which we will store
    important subdirectories such as Preferences, temporary files, etc.
    If it doesn't exist and can't be made, try using /tmp.
    [#e Future: for Windows that backup dir should be something other than /tmp.
     And for all OSes, we should use a more conventional place to store prefs
     if there is one (certainly there is on Mac).]
    """
    global _tmpFilePath
    if _tmpFilePath:
        return _tmpFilePath # already chosen, always return the same one
    _tmpFilePath = _find_or_make_nanorex_dir_0()
    assert _tmpFilePath
    return _tmpFilePath

def _find_or_make_nanorex_dir_0():
    """private helper function for find_or_make_Nanorex_directory"""
    
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

def path_of_Nanorex_subdir(subdir): #bruce 060614
    """Return the full pathname which should be used for the given ~/Nanorex subdirectory,
    without checking whether it exists.
       WARNING: as a kluge, the current implem may create ~/Nanorex itself.
    This might be necessary (rather than a kluge) if the name can only be determined by creating it
    (as the current code for creating it assumes, but whose true status is unknown).
    """
    nanorex = find_or_make_Nanorex_directory()
    nanorex_subdir = os.path.join(nanorex, subdir)
    return nanorex_subdir
    
def find_or_make_Nanorex_subdir(subdir, make = True): #bruce 060614 added make arg; revised implem (so subdir can be >1 level deep)
    """Find or make a given subdirectory under ~/Nanorex/. It's allowed to be more than one level deep, using '/' separator.
    (This assumes '/' is an acceptable file separator on all platforms. I think it is, but haven't fully verified it. [bruce 060614])
    (If make = False, never make it; return None if it's not there.)
    Return the full path of the Nanorex subdirectory, whether it already exists or was made here.
    """
    subdir = path_of_Nanorex_subdir(subdir)

    errorcode, path_or_errortext = find_or_make_any_directory(subdir, make = make)
    if errorcode:
        if make:
            # this should not normally happen, since ~/Nanorex should be writable, but it's possible in theory
            print "bug: should not normally happen:", path_or_errortext
        return None
    return path_or_errortext

def find_or_make_partfiles_subdir(assy): # Mark 060612.
    """Find or make the "part files" subdirectory next to the current assy (MMP file).
    Returns the full path of the "part files" directory whether it already exists or was made here.
    """
    
    #&&& Need to worry about the situation when the user hasn't saved the MMP file (i.e. Untitled).
    #&&& Talk to Bruce about this. Mark 060612.
    path_wo_ext, ext = os.path.splitext(assy.filename)
    partfiles_dir = path_wo_ext + " Files"
    
    if os.path.isdir(partfiles_dir):
        return 0, partfiles_dir
    elif os.path.exists(partfiles_dir):
        return 1, "%s exists, but it is not a directory" % partfiles_dir
    else:
        try:
            os.mkdir(partfiles_dir)
        except:
            return 1, "find_or_make_partfiles(): Cannot create directory %s" % partfiles_dir

    return 0, partfiles_dir

def find_or_make_any_directory(dirname, make = True, make_higher_dirs = True): #bruce 060614
    """Find or make the given directory, making containing directories as needed unless make_higher_dirs is false.
    (If make is false, don't make it, only find it.)
    Make sure it's really a directory.
    For any error, return (1, errortext); on success return (0, full_path_of_dir).
    In other words, return (errorcode, path_or_errortext).
    """
    ###e once this works, redefine some other functions in terms of it, here and in callers of functions here.
    dirname = os.path.abspath(os.path.normpath(dirname)) #k might be redundant, in wrong order, etc
    if os.path.isdir(dirname):
        return 0, dirname
    if os.path.exists(dirname):
        return 1, "[%s] exists but is not a directory" % (dirname,)
    # not there
    if not make:
        return 1, "[%s] does not exist" % (dirname,)
    # try to make it; first make sure parent is there, only making it if make_higher_dirs is true.
    parent, basedir = os.path.split(dirname)
    if not parent or parent == dirname:
        # be sure to avoid infinite recursion; parent == dirname can happen for "/",
        # though presumably that never gets here since isdir is true for it, so this might never be reached.
        return 1, "[%s] does not exist" % (dirname,)
    assert basedir
    assert parent
    errorcode, path = find_or_make_any_directory(parent, make = make_higher_dirs, make_higher_dirs = make_higher_dirs)
    if errorcode:
        return errorcode, path # path is the errortext
    # now try to make the dir in question; this could fail for a variety of reasons
    # (like the parent not being writable, bad chars in basedir, disk being full...)
    try:
        os.mkdir(dirname)
    except:
        return 1, "can't create directory [%s]" % (dirname, ) ###e should grab exception text to say why not
    if not os.path.isdir(dirname):
        return 1, "bug: [%s] is not a directory, even though mkdir said it made it" % (dirname, ) # should never happen
    return 0, dirname

    
_histfile = None
_histfile_timestamp_string = None
    #bruce 060614 kluge -- record this for use in creating other per-session unique directory names
    # To clean this up, we should create this filename, and the file itself,
    # earlier in startup_funcs, and be 100% sure it's unique (include pid, use O_EXCL, or test in some manner).

def make_history_filename():
    """[private method for history init code]
    Return a suitable name for a new history file (not an existing filename).
    Note: this does not actually create the file! It's assumed the caller will do that immediately
    (and we don't provide perfect protection against two callers doing this at the same time).
       The filename contains the current time, so this should be called once per history
    (probably once per process), not once per window when we have more than one.
    This filename could also someday be used as a "process name", valid forever,
    but relative to the local filesystem.
    """
    prefsdir = find_or_make_Nanorex_directory()
    tried_already = None
    while 1:
        timestamp_string = time.strftime("%Y%m%d-%H%M%S")
        histfile = os.path.join( prefsdir, "Histories", "h%s.txt" % timestamp_string )
            # e.g. ~/Nanorex/Histories/h20050104-160000.txt
        if not os.path.exists(histfile):
            if histfile == tried_already:
                # this is ok, but is so unlikely that it might indicate a bug, so report it
                print "fyi: using history file \"%s\" after all; someone removed it!" % histfile
            if "kluge":
                global _histfile, _histfile_timestamp_string
                _histfile = histfile
                _histfile_timestamp_string = timestamp_string # this lacks the 'h' and the '.txt'
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

_tempfiles_dir = None # this is assigned if and only if we ever create that dir, so we can move it when we quit. (Not a kluge.)
_tempfiles_dir_has_moved = False

def tempfiles_dir(make = True): #bruce 060614
    """Return (and by default, make if necessary) the pathname of the subdir for this process's temporary files.
    If make is false and this dir is not there, return None rather than its intended name.
       [All temporary files created by this process should go into the subdir we return,
    and upon normal exit it should be moved to a different location or name that marks it as "Old",
    e.g. from ~/Nanorex/TemporaryFiles into ~/Nanorex/OldTempFiles,
    and subsequent nE-1 startups should consider deleting it if it's both marked as old
    (meaning nE-1 didn't crash and can't be still running)
    and is too old in modtime of any file, or recorded quit-time
    (eg modtime of a logfile that records the quit). But all that is NIM as of 060614.]
    """
    #bruce 060614; current implem is a kluge, but should be ok in practice
    # unless you start more than one nE-1 process in one second, and furthermore they
    # happen to both think they own the same history file name (unlikely but possible)
    if _tempfiles_dir_has_moved:
        print "bug: _tempfiles_dir_has_moved but we're calling tempfiles_dir after that; _tempfiles_dir == %r" % (_tempfiles_dir,)
    assert _histfile_timestamp_string, "too early to call tempfiles_dir"
    global _tempfiles_dir
    if _tempfiles_dir:
        return _tempfiles_dir
    _tempfiles_dir = find_or_make_Nanorex_subdir("TemporaryFiles/t%s" % _histfile_timestamp_string, make = make )
    # that might be None if make is false, but that's ok since it already was None if we got this far
    # [don't reset _tempfiles_dir_has_moved to mitigate the bug of calling this when it's already set,
    #  since the newly made dir might have the same name as the moved one so we don't want to try moving it again]
    return _tempfiles_dir

def move_tempfiles_dir_when_quitting(): #bruce 060614 ###@@@ need to call this when nE-1 quits
    """If tempfiles_dir actually created a directory during this session,
    move it to where old ones belong. (Also reset variables so that if some bug makes someone
    call tempfiles_dir again, it will complain, but then return the moved directory
    rather than a now-invalid pathname.)
    """
    global _tempfiles_dir, _tempfiles_dir_has_moved
    if _tempfiles_dir_has_moved:
        print "bug: _tempfiles_dir_has_moved but we're calling move_tempfiles_dir_when_quitting again" #e print_compact_stack
        return
    _tempfiles_dir_has_moved = True # even if not _tempfiles_dir
    if not _tempfiles_dir:
        return
    if not os.path.isdir(_tempfiles_dir):
        print "bug: can't find _tempfiles_dir %r which we supposedly made earlier this session" % (_tempfiles_dir,)
        return
    assert _histfile_timestamp_string
    movetodir = find_or_make_Nanorex_subdir("OldTempFiles")
    moveto = os.path.join( movetodir, os.path.basename(_tempfiles_dir))
    assert _tempfiles_dir != moveto
    os.rename(_tempfiles_dir, moveto)
    _tempfiles_dir = moveto
    return

# ===

# atom_debug variable:

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

# ===

# user-message helpers:

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

def hhmmss_str(secs):
    """Given the number of seconds, return the elapsed time as a string in hh:mm:ss format"""
    # [bruce 050415 comment: this is sometimes called from external code
    #  after the progressbar is hidden and our launch method has returned.]
    # bruce 050415 revising this to use pure int computations (so bugs from
    #  numeric roundoff can't occur) and to fix a bug when hours > 0 (commented below).
    secs = int(secs)
    hours = int(secs/3600) # use int divisor, not float
    # (btw, the int() wrapper has no effect until python int '/' operator changes to produce nonints)
    minutes = int(secs/60 - hours*60)
    seconds = int(secs - minutes*60 - hours*3600) #bruce 050415 fix bug 439: also subtract hours
    if hours:
        return '%02d:%02d:%02d' % (hours, minutes, seconds)
    else:
        return '%02d:%02d' % (minutes, seconds)

# ==

# code for determining screen size (different for Mac due to menubar)

#e (I should also pull in some more related code from atom.py...)

def screen_pos_size(): ###e this copies code in atom.py -- atom.py should call this
    """Return (x,y),(w,h), where the main screen area
    (not including menubar, for Mac) is in a rect of size w,h,
    topleft at x,y. Note that x,y is 0,0 except for Mac.
    Current implementation guesses Mac menubar size since it doesn't
    know how to measure it.
    """
    # Create desktop widget to obtain screen resolution
    dtop = QDesktopWidget()
    screensize = QRect (dtop.screenGeometry (0))
    
    if is_macintosh():
        # menubar_height = 44 was measured (approximately) on an iMac G5 20 inch
        # screen; I don't know if it's the same on all Macs (or whether it can
        # vary with OS or user settings). (Is there any way of getting this info
        # from Qt? #e)
        menubar_height = 44
    else:
        menubar_height = 0
    
    screen_w = screensize.width()
    screen_h = screensize.height() # of which menubar_height is in use at the top

    x,y = 0,0
    w,h = screen_w, screen_h
    
    y += menubar_height
    h -= menubar_height

    return (x,y), (w,h)

# ==

# main window layout save/restore
# [not sure in which file this belongs -- not really this one]
# and other code related to main window size [which does belong here]

def fullkey(keyprefix, *subkeys): #e this func belongs in preferences.py
    res = keyprefix
    for subkey in subkeys:
        res += "/" + subkey
    return res

def size_pos_keys( keyprefix):
    return fullkey(keyprefix, "geometry", "size"), fullkey(keyprefix, "geometry", "pos")

def tupleFromQPoint(qpoint):
    return qpoint.x(), qpoint.y()

def tupleFromQSize(qsize):
    return qsize.width(), qsize.height()

# def qpointFromTuple - not needed

def get_window_pos_size(win):
    size = tupleFromQSize( win.size())
    pos = tupleFromQPoint( win.pos())
    return pos, size

def save_window_pos_size( win, keyprefix): #bruce 050913 removed histmessage arg
    """Save the size and position of the given main window, win,
    in the preferences database, using keys based on the given keyprefix,
    which caller ought to reserve for geometry aspects of the main window.
    (#e Someday, maybe save more aspects like dock layout and splitter bar positions??)
    """
##    from preferences import prefs_context
##    prefs = prefs_context()
    ksize, kpos = size_pos_keys( keyprefix)
    pos, size = get_window_pos_size(win)
    changes = { ksize: size, kpos: pos }
    env.prefs.update( changes) # use update so it only opens/closes dbfile once
    env.history.message("saved window position %r and size %r" % (pos,size))
    return

def load_window_pos_size( win, keyprefix, defaults = None, screen = None): #bruce 050913 removed histmessage arg; 060517 revised
    """Load the last-saved size and position of the given main window, win,
    from the preferences database, using keys based on the given keyprefix,
    which caller ought to reserve for geometry aspects of the main window.
    (If no prefs have been stored, return reasonable or given defaults.)
       Then set win's actual position and size (using supplied defaults, and
    limited by supplied screen size, both given as ((pos_x,pos_y),(size_x,size_y)).
    (#e Someday, maybe restore more aspects like dock layout and splitter bar positions??)
    """
    if screen is None:
        screen = screen_pos_size()
    ((x0,y0),(w,h)) = screen
    x1 = x0 + w
    y1 = y0 + h

    pos, size = get_prefs_for_window_pos_size( win, keyprefix, defaults)
    # now use pos and size, within limits set by screen
    px,py = pos
    sx,sy = size
    if sx > w: sx = w
    if sy > h: sy = h
    if px < x0: px = x0
    if py < y0: py = y0
    if px > x1 - sx: px = x1 - sx
    if py > y1 - sy: py = y1 - sy
    env.history.message("restoring last-saved window position %r and size %r" % ((px,py),(sx,sy)))
    win.resize(sx,sy)
    win.move(px,py)
    return

def get_prefs_for_window_pos_size( win, keyprefix, defaults = None):
    """Load and return the last-saved size and position of the given main window, win,
    from the preferences database, using keys based on the given keyprefix,
    which caller ought to reserve for geometry aspects of the main window.
    (If no prefs have been stored, return reasonable or given defaults.)
    """
    #bruce 060517 split this out of load_window_pos_size
    if defaults is None:
        defaults = get_window_pos_size(win)
    dpos, dsize = defaults
    px,py = dpos # check correctness of args, even if not used later
    sx,sy = dsize
    import preferences
    prefs = preferences.prefs_context()
    ksize, kpos = size_pos_keys( keyprefix)
    pos = prefs.get(kpos, dpos)
    size = prefs.get(ksize, dsize)
    return pos, size

def open_file_in_editor(file, hflag = True): #bruce 050913 revised this
    """Opens a file in a standard text editor.
    Error messages go to console and (unless hflag is false) to env.history.
    """
    #bruce 050913 replaced history arg with hflag = True, since all callers passed env.history to history arg.
    file = os.path.normpath(file)
    
    if hflag:
        from HistoryWidget import redmsg
    
    if not os.path.exists(file):
        msg = "File does not exist: " + file
        print msg
        if hflag:
            env.history.message(redmsg(msg))
        return
        
    editor_and_args = get_text_editor()
        # a list of editor name and 0 or more required initial arguments [bruce 050704 revised API]
    editor = editor_and_args[0]
    initial_args = list( editor_and_args[1:] )
        
    if os.path.exists(editor):
        args = [editor] + initial_args + [file]
        if atom_debug:
            print  "editor = ",editor
            print  "Spawnv args are %r" % (args,)

        try: #bruce 050704
            from debug import print_compact_traceback
        except:
            def noop(*args): pass
            print_compact_traceback = noop
        try:
            # Spawn the editor.
            kid = os.spawnv(os.P_NOWAIT, editor, args)
        except: # We had an exception.
            print_compact_traceback("Exception in editor; continuing: ")
            msg = "Cannot open file " + file + ".  Trouble spawning editor " + editor
            print msg
            if hflag:
                env.history.message(redmsg(msg))
    else:
        msg = "Cannot open file " + file + ".  Editor " + editor + " not found."
        if hflag:
            env.history.message(redmsg(msg))
    return
            
def get_text_editor(): #bruce 050704 revised API
    """Returns a list of the name and required initial shell-command-line arguments (if any) of a text editor for this platform.
    The editor can be caused to open a file by launching it using these args plus the filename.
    """
    args = [] # might be modified below
    if sys.platform == 'win32': # Windows
        editor = "C:/WINDOWS/notepad.exe"
    elif sys.platform == 'darwin': # MacOSX
        editor = "/usr/bin/open"
        args = ['-e']
        # /usr/bin/open needs -e argument to force treatment of file as text file.
    else: # Linux
        editor = "/usr/bin/kwrite"
    return [editor] + args

def get_rootdir():
    """Returns the root directory for this platform.
    """
    if sys.platform == 'win32': # Windows
        rootdir = "C:/"
    else: # Linux and MacOS
        rootdir = "/"
    
    return rootdir

def get_gms_name():
    '''Returns either GAMESS (Linux or MacOS) or PC GAMESS (Windows). 
    '''
    if sys.platform == 'win32': # Windows
        gms_name = "PC GAMESS"
    else: # Linux and MacOS
        gms_name =  "GAMESS"
    
    return gms_name

def find_pyrexc():
    import Pyrex
    if sys.platform == 'darwin':
        x = os.path.dirname(Pyrex.__file__).split('/')
        return '/'.join(x[:-4] + ['bin', 'pyrexc'])
    elif sys.platform == 'linux2':
        if os.path.exists('/usr/bin/pyrexc'):
            return '/usr/bin/pyrexc'
        if os.path.exists('/usr/local/bin/pyrexc'):
            return '/usr/local/bin/pyrexc'
        raise Exception('cannot find pyrexc')
    else:
        # windows
        return 'python c:/Python' + sys.version[:3] + '/Scripts/pyrexc.py'

# ==

#bruce 051201 moved wiki help code from here to new file wiki_help.py

# == test code

if __name__ == "__main__":
    msg = 'Dehydrogenate: removed 4 atom(s) from 1 molecule(s) (1 selected molecule(s) had no hydrogens)'
    msg2 = 'Dehydrogenate: removed 4 atoms from 1 molecule (1 selected molecule had no hydrogens)'
    assert fix_plurals(msg) == msg2
    print "test done"

# end
