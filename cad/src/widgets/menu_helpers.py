# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
menu_helpers.py - helpers for creating or modifying Qt menus

@author: Josh, Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Originally by Josh, as part of GLPane.py.

Bruce 050112 moved this code into widgets.py,
later added features including checkmark & Undo support,
split it into more than one function,
and on 080203 moved it into its own file.

At some point Will ported it to Qt4 (while it was in widgets.py).

Module classification: [bruce 080203]

Might have been in utilities except for depending on undo_manager (foundation).
Since its only purpose is to help make or modify menus for use in Qt widgets,
it seems more useful to file it in widgets than in foundation.
(Reusable widgets are in a sense just a certain kind of "ui utility".)
"""

from PyQt4.Qt import QMenu
from PyQt4.Qt import QAction
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QIcon

from utilities import debug_flags

from foundation.undo_manager import wrap_callable_for_undo

# ==

# helper for making popup menus from our own "menu specs" description format,
# consisting of nested lists of text, callables or submenus, options.

def makemenu_helper(widget, menu_spec, menu = None):
    """
    Make and return a reusable or one-time-use (at caller's option)
    popup menu whose structure is specified by menu_spec,
    which is a list of menu item specifiers, each of which is either None
    (for a separator) or a tuple of the form (menu text, callable or submenu,
    option1, option2, ...) with 0 or more options (described below).
       A submenu can be either another menu_spec list, or a QMenu object
    (but in the latter case the menu text is ignored -- maybe it comes
    from that QMenu object somehow -- not sure if this was different in Qt3).
    In either case it is the 2nd menu-item-tuple element, in place of the callable.
       Otherwise the callable must satisfy the python 'callable' predicate,
    and is executed if the menu item is chosen, wrapped inside another function
    which handles Undo checkpointing and Undo-command-name setting.
       The options in a menu item tuple can be zero or more (in any order,
    duplicates allowed) of the following:
    'disabled' -- the menu item should be disabled;
    'checked' -- the menu item will be checked;
    None -- this option is legal but ignored (but the callable must still satisfy
    the python predicate "callable"; constants.noop might be useful for that case).
       The Qt3 version also supported tuple-options consisting of one of the words
    'iconset' and 'whatsThis' followed by an appropriate argument, but those have
    not yet been ported to Qt4 (except possibly for disabled menu items -- UNTESTED).
       Unrecognized options may or may not generate warnings, and are otherwise ignored.
    [###FIX that -- they always ought to print a warning to developers. Note that right
    now they do iff 'disabled' is one of the options and ATOM_DEBUG is set.]
       The 'widget' argument should be the Qt widget
    which is using this function to put up a menu.
       If the menu argument is provided, it should be a QMenu
    to which we'll add items; otherwise we create our own QMenu
    and add items to it.
    """
    from utilities.debug import print_compact_traceback
    import types
    if menu is None:
        menu = QMenu(widget)
        ## menu.show()
        #bruce 070514 removed menu.show() to fix a cosmetic and performance bug
        # (on Mac, possibly on other platforms too; probably unreported)
        # in which the debug menu first appears in screen center, slowly grows
        # to full size while remaining blank, then moves to its final position
        # and looks normal (causing a visual glitch, and a 2-3 second delay
        # in being able to use it). May fix similar issues with other menus.
        # If this causes harm for some menus or platforms, we can adapt it.
    # bruce 040909-16 moved this method from basicMode to GLPane,
    # leaving a delegator for it in basicMode.
    # (bruce was not the original author, but modified it)
    #menu = QMenu( widget)
    for m in menu_spec:
        try: #bruce 050416 added try/except as debug code and for safety
            menutext = m and widget.trUtf8(m[0])
            if m and isinstance(m[1], QMenu): #bruce 041010 added this case
                submenu = m[1]
                #menu.insertItem( menutext, submenu )
                menu.addMenu(submenu)   # how do I get menutext in there?
                    # (similar code might work for QAction case too, not sure)
            elif m and isinstance(m[1], types.ListType): #bruce 041103 added this case
                submenu = QMenu(menutext, menu)
                submenu = makemenu_helper(widget, m[1], submenu) # [this used to call widget.makemenu]
                menu.addMenu(submenu)
            elif m:
                assert callable(m[1]), \
                    "%r[1] needs to be a callable" % (m,) #bruce 041103
                # transform m[1] into a new callable that makes undo checkpoints and provides an undo command-name
                # [bruce 060324 for possible bugs in undo noticing cmenu items, and for the cmdnames]
                func = wrap_callable_for_undo(m[1], cmdname = m[0])
                    # guess about cmdname, but it might be reasonable for A7 as long as we ensure weird characters won't confuse it
                import foundation.changes as changes
                changes.keep_forever(func) # THIS IS BAD (memory leak), but it's not a severe one, so ok for A7 [bruce 060324]
                    # (note: the hard part about removing these when we no longer need them is knowing when to do that
                    #  if the user ends up not selecting anything from the menu. Also, some callers make these
                    #  menus for reuse multiple times, and for them we never want to deallocate func even when some
                    #  menu command gets used. We could solve both of these by making the caller pass a place to keep these
                    #  which it would deallocate someday or which would ensure only one per distinct kind of menu is kept. #e)
                if 'disabled' not in m[2:]:
                    act = QAction(widget)
                    act.setText( menutext)
                    if 'checked' in m[2:]:
                        act.setCheckable(True)
                        act.setChecked(True)
                    menu.addAction(act)
                    widget.connect(act, SIGNAL("activated()"), func)
                else:
                    # disabled case
                    # [why is this case done differently, in this Qt4 port?? -- bruce 070522 question]
                    insert_command_into_menu(menu, menutext, func, options = m[2:], raw_command = True)
            else:
                menu.addSeparator() #bruce 070522 bugfix -- before this, separators were placed lower down or dropped
                    # so as not to come before disabled items, for unknown reasons.
                    # (Speculation: maybe because insertSeparator was used, since addSeparator didn't work or wasn't noticed,
                    #  and since disabled item were added by an older function (also for unknown reasons)?)
                pass
        except Exception, e:
            if isinstance(e, SystemExit):
                raise
            print_compact_traceback("exception in makemenu_helper ignored, for %r:\n" % (m,) )
                #bruce 070522 restored this (was skipped in Qt4 port)
            pass #e could add a fake menu item here as an error message
    return menu # from makemenu_helper

# ==

def insert_command_into_menu(menu, menutext, command, options = (), position = -1, raw_command = False, undo_cmdname = None):
    """
    [This was part of makemenu_helper in the Qt3 version; in Qt4 it's only
     used for the disabled case, presumably for some good reason but not one
     which has been documented. It's also used independently of makemenu_helper.]

    Insert a new item into menu (a QMenu), whose menutext, command, and options are as given,
    with undo_cmdname defaulting to menutext (used only if raw_command is false),
    where options is a list or tuple in the same form as used in "menu_spec" lists
    such as are passed to makemenu_helper (which this function helps implement).
       The caller should have already translated/localized menutext if desired.
       If position is given, insert the new item at that position, otherwise at the end.
    Return the Qt menu item id of the new menu item.
    (I am not sure whether this remains valid if other items are inserted before it. ###k)
       If raw_command is False (default), this function will wrap command with standard logic for nE-1 menu commands
    (presently, wrap_callable_for_undo), and ensure that a python reference to the resulting callable is kept forever.
       If raw_command is True, this function will pass command unchanged into the menu,
    and the caller is responsible for retaining a Python reference to command.
       ###e This might need an argument for the path or function to be used to resolve icon filenames.
    """
    #bruce 060613 split this out of makemenu_helper.
    # Only called for len(options) > 0, though it presumably works
    # just as well for len 0 (try it sometime).
    import types
    from foundation.whatsthis_utilities import turn_featurenames_into_links, ENABLE_WHATSTHIS_LINKS
    if not raw_command:
        command = wrap_callable_for_undo(command, cmdname = undo_cmdname or menutext)
        import foundation.changes as changes
        changes.keep_forever(command)
            # see comments on similar code above about why this is bad in theory, but necessary and ok for now
    iconset = None
    for option in options:
        # some options have to be processed first
        # since they are only usable when the menu item is inserted. [bruce 050614]
        if type(option) is types.TupleType:
            if option[0] == 'iconset':
                # support iconset, pixmap, or pixmap filename [bruce 050614 new feature]
                iconset = option[1]
                if type(iconset) is types.StringType:
                    filename = iconset
                    from utilities.icon_utilities import imagename_to_pixmap
                    iconset = imagename_to_pixmap(filename)
                if isinstance(iconset, QPixmap):
                    # (this is true for imagename_to_pixmap retval)
                    iconset = QIcon(iconset)
    if iconset is not None:
        import foundation.changes as changes
        changes.keep_forever(iconset) #e memory leak; ought to make caller pass a place to keep it, or a unique id of what to keep
        #mitem_id = menu.insertItem( iconset, menutext, -1, position ) #bruce 050614, revised 060613 (added -1, position)
        mitem = menu.addAction( iconset, menutext ) #bruce 050614, revised 060613 (added -1, position)
            # Will this work with checkmark items? Yes, but it replaces the checkmark --
            # instead, the icon looks different for the checked item.
            # For the test case of gamess.png on Mac, the 'checked' item's icon
            # looked like a 3d-depressed button.
            # In the future we can tell the iconset what to display in each case
            # (see QIcon and/or QMenu docs, and helper funcs presently in debug_prefs.py.)
    else:
        # mitem_id = len(menu) -- mitem_id was previously an integer, indexing into the menu
        mitem = menu.addAction(menutext)
    for option in options:
        if option == 'checked':
            mitem.setChecked(True)
        elif option == 'unchecked': #bruce 050614 -- see what this does visually, if anything
            mitem.setChecked(False)
        elif option == 'disabled':
            mitem.setEnabled(False)
        elif type(option) is types.TupleType:
            if option[0] == 'whatsThis':
                text = option[1]
                if ENABLE_WHATSTHIS_LINKS:
                    text = turn_featurenames_into_links(text)
                mitem.setWhatsThis(text)
            elif option[0] == 'iconset':
                pass # this was processed above
            else:
                if debug_flags.atom_debug:
                    print "atom_debug: fyi: don't understand menu_spec option %r", (option,)
            pass
        elif option is None:
            pass # this is explicitly permitted and has no effect
        else:
            if debug_flags.atom_debug:
                print "atom_debug: fyi: don't understand menu_spec option %r", (option,)
        pass
        #e and something to use QMenuData.setShortcut
        #e and something to run whatever func you want on menu and mitem_id
    return mitem # from insert_command_into_menu

# end
