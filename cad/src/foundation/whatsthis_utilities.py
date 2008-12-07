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

import os

from utilities.icon_utilities import image_directory 

# more imports below; todo: move them to toplevel

#bruce 051227-29 code for putting hyperlinks into most WhatsThis texts
# (now finished enough for release, though needs testing and perhaps cleanup 
# and documentation)

ENABLE_WHATSTHIS_LINKS = True # also used in an external file

_DEBUG_WHATSTHIS_LINKS = False # DO NOT COMMIT with True # only used in this file

# ===

map_from_id_QAction_to_featurename = {}
    # map from id(QAction) to the featurenames in their whatsthis text
    # [bruce 060121 to help with Undo; renamed, bruce 080509]
    # note: also used in undo_internals.py

def fix_whatsthis_text_and_links(parent):
    #bruce 080509 removed old debug code for bugs 1421 and 1721; other cleanup
    #bruce 060319 renamed this from fix_whatsthis_text_for_mac
    #bruce 060120 revised this as part of fixing bug 1295
    #bruce 051227-29 revised this
    """
    [public]
    Fix tooltips and whatsthis text and objects (for all OSes, not just macs
    as this function once did).

    This function does two things:
    
    1. If the system is a Mac, this replaces all occurrences of 'Ctrl'
    with 'Cmd' in all the tooltip and whatsthis text for all QAction or
    QWidget objects that are children of parent.
    
    2. For all systems, it replaces certain whatsthis text patterns with
    hyperlinks, and adds MyWhatsThis objects to widgets with text modified
    that way (or that might contain hyperlinks) or that are QPopupMenus.

    This should be called after all widgets (and their whatsthis text) 
    in the UI have been created. It's ok, but slow (up to 0.2 seconds per call
    or more), to call it more than once on the main window. If you call it again
    on something else, as of 060319 this would have caused bugs by clearing 
    _objects_and_text_that_need_fixing_later, but that can be easily fixed when
    we need to support repeated calls on smaller widgets. (As of the next day,
    that global list was no longer used, and on 080509 the code to maintain it
    is being removed -- whether repeated calls would still cause any bugs ought
    to be reviewed. I notice that there *are* repeated calls -- the main call
    in ne1_ui/Ui_MainWindow.py is followed immediately by another one on a
    smaller widget. So it's probably ok.)

    Calling this on a single QAction works, but doesn't do enough to fix the
    text again for toolbuttons (and I think menuitems) made by Qt from that
    action (re bug 1421).

    See also refix_whatsthis_text_and_links, which can be called to restore
    tooltips and/or whatsthis text which Qt messed up for some reason, as
    happens when you set tooltips or menutext for Undo and Redo actions
    (bug 1421). (Note that it hardcodes the set of actions which need this.)
    """
    if _DEBUG_WHATSTHIS_LINKS:
        print "running fix_whatsthis_text_and_links"
    from platform_dependent.PlatformDependent import is_macintosh
    mac = is_macintosh()
    if mac or ENABLE_WHATSTHIS_LINKS:
        # fix text in 1 or 2 ways for all QAction objects
        # (which are not widgets)
        # ATTENTION:
        # objList only includes QAction widgets that appear in the Main Menu
        # bar. This is a bug since some widgets only appear in toolbars on the
        # Main Window, but not the main menu bar. --Mark and Tom 2007-12-19 
        objList = filter(lambda x: isinstance(x, QAction), parent.children())
        for obj in objList:
            fix_QAction_whatsthis(obj, mac)            
            continue
        pass
    if ENABLE_WHATSTHIS_LINKS:
        # add MyWhatsThis objects to all widgets that might need them
        # (and also fix their text if it's not fixed already --
        #  needed in case it didn't come from a QAction; maybe that never
        #  happens as of 060120)
        objList = filter(lambda x: isinstance(x, QWidget), parent.children())
            # this includes QMenuBar, QPopupMenu for each main menu and cmenu
            # (I guess), but not menuitems themselves. (No hope of including 
            # dynamic cmenu items, but since we make those, we could set their
            # whatsthis text and process it the same way using separate code 
            # (nim ###@@@).) [bruce 060120] In fact there is no menu item 
            # class in Qt that I can find! You add items as QActions or as 
            # sets of attrs. QActions also don't show up in this list...
        for obj in objList:
            # note: the following code is related to
            # fix_QAction_whatsthis(obj, mac)
            # but differs in several ways
            text = whatsthis_text_for_widget(obj) # could be either "" or None
            if text:
                # in case text doesn't come from a QAction, modify it in the 
                # same ways as above, and store it again or pass it to the
                # MyWhatsThis object; both our mods are ok if they happen 
                # twice -- if some hyperlink contains 'ctrl', so did the text
                # before it got command names converted to links.
                if mac:
                    text = replace_ctrl_with_cmd(text)
                text = turn_featurenames_into_links(text)
                assert text # we'll just feed it to a MyWhatsThis object so we 
                    # don't have to store it here
            else:
                text = None # turn "" into None
            ## ismenu = isinstance(obj, QPopupMenu)
            ismenu = isinstance(obj, QMenu)
            try:
                ismenubar = isinstance(obj, QMenuBar)
            except:
                # usual for non-Macs, I presume
                ismenubar = False
            if text is not None and (ismenu or ismenubar):
                # assume any text (even if not changed here) might contain 
                # hyperlinks, so any widget with text might need a MyWhatsThis 
                # object; the above code (which doesn't bother storing 
                # mac-modified text) also assumes we're doing this
                # [REVIEW: what code creates such an object? Is the above
                #  old comment still accurate? bruce 080509 questions]
                print text
                obj.setWhatsThis(text)
                pass
            continue
    return # from fix_whatsthis_text_and_links

def fix_QAction_whatsthis(obj, mac):
    """
    Modify the Qt whatsthis and tooltip text assigned to obj
    (which should be a QAction; not sure if that's required)
    based on the mac flag (an argument) and on the global flag
    ENABLE_WHATSTHIS_LINKS.

    Also save info into the global map_from_id_QAction_to_featurename.
    """
    # fyi: only used in this file, as of 080509
    text = str(obj.whatsThis())
    tooltip = str(obj.toolTip())
    if mac:
        text = replace_ctrl_with_cmd(text)
        tooltip = replace_ctrl_with_cmd(tooltip)
    if ENABLE_WHATSTHIS_LINKS:
        text = turn_featurenames_into_links( text,
                   savekey = id(obj),
                   saveplace = map_from_id_QAction_to_featurename
                )
    obj.setWhatsThis(text)
    obj.setToolTip(tooltip)
    return

def refix_whatsthis_text_and_links( ): #bruce 060319 part of fixing bug 1421
    """
    [public]
    """
    import foundation.env as env
    win = env.mainwindow()
    from platform_dependent.PlatformDependent import is_macintosh
    mac = is_macintosh()
    fix_QAction_whatsthis(win.editUndoAction, mac)
    fix_QAction_whatsthis(win.editRedoAction, mac)
    return

def replace_ctrl_with_cmd(text):
    # by Mark; might modify too much for text which uses Ctrl in unexpected ways
    # (e.g. as part of longer words, or in any non-modifier-key usage)
    """
    Replace all occurrences of Ctrl with Cmd in the given string.
    """
    text = text.replace('Ctrl', 'Cmd')
    text = text.replace('ctrl', 'cmd')
    return text

def whatsthis_text_for_widget(widget): #bruce 060120 split this out of other code
    """
    Return a Python string containing the WhatsThis text for 
    widget (perhaps ""), or None if we can't find that.
    """
    try:
        ## original_text = widget.whatsThis() # never works for 
        ##     # widgets (though it would work for QActions)
        text = str(widget.whatsThis()) 
        #exception; don't know if it can be a QString
    except:
        # this happens for a lot of QObjects (don't know what they are), e.g.
        # for <constants.qt.QObject object at 0xb96b750>
        return None
    else:
        return str( text or "" )
            # note: the 'or ""' above is in case we got None (probably never 
            #  needed, but might as well be safe)
            # note: the str() (in case of QString) might not be needed; 
            # during debug it seemed this was already a Python string
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
    #bruce 051229; revised/renamed 060120; save args 060121; img tags 081205
    """
    [public]
    Given some nonempty whatsthis text, return identical or modified text 
    (e.g. containing a web help URL).
    If savekey and saveplace are passed, and if the text contains a 
    featurename, set saveplace[savekey] to that featurename.
    """
    # make all img source pathnames absolute, if they are not already.
    # [bruce 081205 per mark]
    # POSSIBLE BUGS: the current implementation will fail if the pathnames
    # contain characters that don't encode themselves when parsed
    # (by Qt) in this HTML-tag-attribute context -- at least true
    # for '"' and r'\' (fortunately rare in pathnames), perhaps for
    # other chars. This could probably be fixed by encoding them somehow.
    # I also don't know whether unicode characters will be permitted.
    # If not, this might be fixable by encoding them and/or by replacing
    # this approach with one in which we supply a callback to Qt for
    # interpreting these relative pathnames when they're needed.
    # (Does Qt call that callback an "icon factory"??)
    # WARNING: if these are real bugs, they'll prevent NE1 from starting
    # when it's installed under certain pathnames.
    # [bruce 081206 comments]
    PAT1 = "<img source=\"ui/"
    if PAT1 in text:
        ui_dir = os.path.join( os.path.normpath( image_directory() ), "ui" )
            ### TODO: use the named constant for "ui" here
            # (but not elsewhere in this function)
        # replace "ui" with ui_dir in all occurrences of PAT1 in text
        PAT2 = PAT1.replace("ui/", ui_dir + '/')
        text = text.replace(PAT1, PAT2)
        pass
        
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
            # separated by ' '; could use split, isalpha (or so) ###@@@
            if _DEBUG_WHATSTHIS_LINKS:
                if featurename != name:
                    print "web help name for %r: %r" % (name, featurename,)
                else:
                    print "web help name: %r" % (featurename,)
            if saveplace is not None:
                saveplace[savekey] = featurename
            link = "Feature:" + featurename.replace(' ','_')
                # maybe we can't let ' ' remain in it, otherwise replacement 
                # not needed since will be done later anyway
            ## from wiki_help import wiki_prefix
            ## text = "<a href=\"%s%s\">%s</a>" % \
            ## (wiki_prefix(), link, name) + rest
            text = "<a href=\"%s\">%s</a>" % (link, name) + rest
            return text
    return text

# end
