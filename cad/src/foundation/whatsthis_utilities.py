# Copyright 2005-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
whatsthis_utilities.py

@author: Bruce
@version: $Id$
@copyright: 2005-2008 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4.Qt import QAction
from PyQt4.Qt import QWidget
from PyQt4.Qt import QMenu
from PyQt4.Qt import QMenuBar

#bruce 051227-29 code for putting hyperlinks into most WhatsThis texts
# (now finished enough for release, though needs testing and perhaps cleanup 
# and documentation)

enable_whatsthis_links = True # also used in an external file

debug_whatsthis_links = False # DO NOT COMMIT with True # only used in this file

debug_refix = False # DO NOT COMMIT with True # also used in an external file

use_debug_refix_cutoff = False # DO NOT COMMIT with True  # only used in this file

debug_refix_cutoff = 24  # only used in this file
# vary this by binary search in a debugger; 
# this value is large enough to not matter

# ===

_actions = {} # map from id(QAction) to the featurenames in their whatsthis
              #text [bruce 060121 to help with Undo]
              # SHOULD RENAME (not private), since used in undo_internals.py

_objects_and_text_that_need_fixing_later = [] ####@@@@ should make this less 
####@@@@fragile re repeated calls of fix_whatsthis_text_and_links

def fix_whatsthis_text_and_links(parent, refix_later = (), debug_cutoff = 0):
    #bruce 060319 renamed this from fix_whatsthis_text_for_mac
    #bruce 051227-29 revised this
    #bruce 060120 revised this as part of fixing bug 1295
    """
    [public]
    Fix whatsthis text and objects (for all OSes, not just macs as it once 
    did). This should be called after all widgets (and their whatsthis text) 
    in the UI have been created. Its ok, but slow (up to 0.2 seconds per call 
    or more), to call it more than once on the main window. If you call it again 
    on something else, as of 060319 this will cause bugs by clearing 
    _objects_and_text_that_need_fixing_later, but that can be easily fixed when
    we need to support repeated calls on smaller widgets. Calling it on a 
    single QAction works, but doesn't do enough to fix the text again for 
    toolbuttons (and I think menuitems) made by Qt from that action
    (re bug 1421). See also refix_whatsthis_text_and_links, which can be called
    to restore whatsthis text which Qt messed up for some reason, as happens 
    when you set tooltips or menutext for Undo and Redo actions (bug 1421).
    This function does two things:
    1. If the system is a Mac, this replaces all occurrences of 'Ctrl' 
    with 'Cmd' in all the whatsthis text for all QAction or QWidget objects 
    that are children of parent.
    2. For all systems, it replaces certain whatsthis text patterns with 
    hyperlinks, and adds MyWhatsThis objects to widgets with text modified that
    way (or that might contain hyperlinks) or that are QPopupMenus.
    """
    if debug_whatsthis_links or debug_refix or use_debug_refix_cutoff:
        print "\nrunning fix_whatsthis_text_and_links\n"
    if 0 and debug_cutoff:
        print "returning immediately (sanity check, bug better be there or"\
              "you're insane)" ####@@@@@ yes, bug is not fixed yet
        return
    from PlatformDependent import is_macintosh
    mac = is_macintosh()
    if mac or enable_whatsthis_links:
        # fix text in 1 or 2 ways for all QAction objects
        #(which are not widgets)
        # ATTENTION:
        # objList only includes QAction widgets that appear in the Main Menu
        # bar. This is a bug since some widgets only appear in toolbars on the
        # Main Window, but not the main menu bar. --Mark and Tom 2007-12-19 
        objList = filter(lambda x: isinstance(x, QAction), parent.children())
        if 0 and debug_cutoff:
            print "returning after query list action" ####@@@@@ bug is not 
            ####fixed yet; the illegal instr crash happens after reload 
            ####whatsthis
            return
        ao = 0 # only matters when debug_cutoff is set
        for obj in objList:
            if debug_cutoff: 
                print "ao %d, obj" % ao, obj
            text = str(obj.whatsThis())
            if mac:
                text = replace_ctrl_with_cmd(text)
                if debug_cutoff and 'Undo' in str(text):
                    print 'undo in', ao, obj, text
            if enable_whatsthis_links:
                text = turn_featurenames_into_links(text, savekey = id(obj), \
                                                    saveplace = _actions )
            obj.setWhatsThis(text)
            ao += 4
            if ao == debug_cutoff:
                break
    if debug_cutoff:
        print "returning when ao got to %d; 1,2,3,4 are for obj 0" % ao 
        # 24 doesn't fix, 25 does. hmm. 
        return
    if debug_cutoff:
        print "returning before widgets" ####@@@@@ bug is fixed by this 
        ####point if we let above loop run to completion
        return
    if enable_whatsthis_links:
        # add MyWhatsThis objects to all widgets that might need them
        # (and also fix their text if it's not fixed already --
        #  needed in case it didn't come from a QAction; maybe that never
        #happens as of 060120)
        objList = filter(lambda x: isinstance(x, QWidget), parent.children())
            # this includes QMenuBar, QPopupMenu for each main menu and cmenu
            #(I guess), but not menuitems themselves. (No hope of including 
            # dynamic cmenu items, but since we make those, we could set their
            #whatsthis text and process it the same way using separate code 
            #(nim ###@@@).) [bruce 060120] In fact there is no menu item 
            #class in Qt that I can find! You add items as QActions or as 
            #sets of attrs. QActions also don't show up in this list...
        global _objects_and_text_that_need_fixing_later
        if _objects_and_text_that_need_fixing_later:
            print "bug warning: _objects_and_text_that_need_fixing_later "\
                  "being remade from scratch; causes bug 1421 if not"\
                  "reviewed"###@@@
        _objects_and_text_that_need_fixing_later = []
        objcount = 0 # only matters when debug_cutoff is set and when code 
                     #above this to use it earlier is removed
        for obj in objList:
            text = whatsthis_text_for_widget(obj) # could be either "" or None
            if text:
                # in case text doesn't come from a QAction, modify it in the 
                #same ways as above, and store it again or pass it to the
                #MyWhatsThis object; both our mods are ok if they happen 
                #twice -- if some hyperlink contains 'ctrl', so did the text
                #before it got command names converted to links.
                if mac:
                    text = replace_ctrl_with_cmd(text)
                text = turn_featurenames_into_links(text)
                assert text # we'll just feed it to a MyWhatsThis object so we 
                #don't have to store it here
            else:
                text = None # turn "" into None
            #ismenu = isinstance(obj, QPopupMenu)
            ismenu = isinstance(obj, QMenu)
            try:
                ismenubar = isinstance(obj, QMenuBar)
            except:
                # usual for non-Macs, I presume
                ismenubar = False
            if text is not None and (ismenu or ismenubar):
                # assume any text (even if not changed here) might contain 
                #hyperlinks, so any widget with text might need a MyWhatsThis 
                #object; the above code (which doesn't bother storing 
                #mac-modified text) also assumes we're doing this
                print text
                obj.setWhatsThis(text)
                #bruce 060319 part of fixing bug 1421
                ts = str(text)
                if "Undo" in ts or "Redo" in ts or obj in refix_later or \
                   ismenu or ismenubar:
                    # hardcoded cases cover ToolButtons whose actions are 
                    #Undo or Redo (or a few others included by accident)
                    _objects_and_text_that_need_fixing_later.append\
                                                            (( obj, text))
                    if debug_refix:
                        if obj in refix_later:
                            print "got from refix_later:", obj 
                            ####@@@@ we got a menu from caller, but editmenu 
                            ####bug 1421 still not fixed!
                        if ismenu:
                            print "ismenu", obj
                        if ismenubar:
                            print "ismenubar", obj
            objcount += 1
            if objcount == debug_cutoff: # debug code for bug 1421
                break
            continue
        if debug_refix or use_debug_refix_cutoff:
            print len(_objects_and_text_that_need_fixing_later), \
                  "_objects_and_text_that_need_fixing_later" ####@@@@ 
            print "debug_cutoff was %d, objcount reached %d" % \
                  (debug_cutoff, objcount) # we did the first objcount objects
            if objcount:
                print "last obj done was", objList[objcount - 1]
    return # from fix_whatsthis_text_and_links

def fix_QAction_whatsthis(obj, mac):
    """
    [only used in this file]
    """
    text = str(obj.whatsThis())
    if mac:
        text = replace_ctrl_with_cmd(text)
    if enable_whatsthis_links:
        text = turn_featurenames_into_links\
             (text, savekey = id(obj), saveplace = _actions )
    obj.setWhatsThis(text)
    return

def refix_whatsthis_text_and_links( ): #bruce 060319 part of fixing bug 1421
    """
    [public]
    """
##    if use_debug_refix_cutoff:
##        # debug code for bug 1421
##        print "\nuse_debug_refix_cutoff is true"
##        import env
##        win = env.mainwindow()
##        fix_whatsthis_text_and_links( win, refix_later = (win.editMenu,), 
##        debug_cutoff = debug_refix_cutoff )
##        return
    import foundation.env as env
    win = env.mainwindow()
    from PlatformDependent import is_macintosh
    mac = is_macintosh()
    fix_QAction_whatsthis(win.editUndoAction, mac)
    fix_QAction_whatsthis(win.editRedoAction, mac)
    if use_debug_refix_cutoff:
        print "returning from refix_whatsthis_text_and_links "\
              "w/o using laterones"
#bruce 060320 zapping this for bug 1721 (leaving it in was an oversight, 
#though I didn't know it'd cause any bug)
##    for obj, text in _objects_and_text_that_need_fixing_later:
##        give_widget_MyWhatsThis_and_text( obj, text)
    return

def replace_ctrl_with_cmd(text):
    # by mark; might modify too much for text which uses Ctrl in unexpected ways
    # (e.g. as part of longer words, or in any non-modifier-key usage)
    """
    Replace all occurrences of Ctrl with Cmd in the given string.
    """
    text = text.replace('Ctrl', 'Cmd')
    text = text.replace('ctrl', 'cmd')
    return text

def whatsthis_text_for_widget(widget): #bruce 060120 split 
    """
    Return a Python string containing the WhatsThis text for 
    widget (perhaps ""), or None if we can't find that.
    """
    #this out of other code
    try:
        ## original_text = widget.whatsThis() # never works for 
        ##widgets (though it would work for QActions)
        text = str(widget.whatsThis()) 
        #exception; don't know if it can be a QString
    except:
        # this happens for a lot of QObjects (don't know what they are), e.g. 
        #for <constants.qt.QObject object at 0xb96b750>
        return None
    else:
        return str( text or "" )
            #note: the 'or ""' above is in case we got None (probably never 
            #needed, but might as well be safe)
            #note: the str() (in case of QString) might not be needed; 
            #during debug it seemed this was already a Python string
    pass

def debracket(text, left, right): #bruce 051229 ##e refile this?
    """
    If text contains (literal substrings) left followed eventually by
    right (without another occurrence of left),return the triple 
    (before, between, after)
    where before + left + between + right + after == text.
    Otherwise return None.
    """
    splitleft = text.split(left, 1)
    if len(splitleft) < 2: 
        return None # len should never be more than 2
    before, t2 = splitleft
    splitright = t2.split(right, 1)
    if len(splitright) < 2: 
        return None
    between, after = splitright
    assert before + left + between + right + after == text
    if left in between: 
        return None # not sure we found the correct 'right' in this case
    return (before, between, after)

def turn_featurenames_into_links(text, savekey = None, saveplace = None): 
    #bruce 051229; revised and renamed 060120; save args 060121
    """
    [public]
    Given some nonempty whatsthis text, return identical or modified text 
    (e.g. containing a web help URL).
    If savekey and saveplace are passed, and if the text contains a 
    featurename, set saveplace[savekey] to that featurename.
    """
    # look for words between <u><b> and </b></u> to replace with a web help link
    if text.startswith("<u><b>"): # require this at start, not just somewhere
                                  # like debracket would
        split1 = debracket(text, "<u><b>", "</b></u>")
        if split1:
            junk, name, rest = split1
            featurename = name # might be changed below
            if "[[Feature:" in rest: # it's an optim to test this first, 
                #since usually false 
                #Extract feature name to use in the link, when this differs 
                #from name shown in WhatsThis text; this name is usually given 
                #in an HTML comment but we use it w/o modifying the text 
                #whether or not it's in one.
                # We use it in the link but not in the displayed WhatsThis text.
                split2 = debracket(rest, "[[Feature:", "]]")
                if not split2:
                    print "syntax error in Feature: link for WhatsThis text \
                    for %r" % name
                    return text
                junk, featurename, junk2 = split2
            #e should verify featurename is one or more capitalized words 
            #sep by ' '; could use split, isalpha (or so) ###@@@
            if debug_whatsthis_links:
                if featurename != name:
                    print "web help name for %r: %r" % (name, featurename,)
                else:
                    print "web help name: %r" % (featurename,)
            if saveplace is not None:
                saveplace[savekey] = featurename
            link = "Feature:" + featurename.replace(' ','_')
                # maybe we can't let ' ' remain in it, otherwise replacement 
                #not needed since will be done later anyway
            #from wiki_help import wiki_prefix
            #text = "<a href=\"%s%s\">%s</a>" % 
            #(wiki_prefix(), link, name) + rest
            text = "<a href=\"%s\">%s</a>" % (link, name) + rest
            return text
    return text

# end
