# Copyright 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""
simple_dialogs.py - simple dialogs, collected here for convenience.

TODO: merge some of them into one function.

@author: Bruce, based on code by others
@version: $Id$
@copyright: 2004-2009 Nanorex, Inc.  See LICENSE file for details.
"""

from PyQt4.Qt import QInputDialog, QLineEdit, QDialog
from utilities.icon_utilities import geticon

def grab_text_using_dialog( default = "",
                            title = "title",
                            label = "label",
                            iconPath  = "ui/border/MainWindow.png"):
    """
    Get some text from the user by putting up a dialog with the
    supplied title, label, and default text. Return (ok, text)
    as described below.

    Replace @@@ with \n in the returned text (and convert it to a Python
    string). If it contains unicode characters, raise UnicodeEncodeError.

    @return: the 2-tuple (ok, text), which is (True, text) if we succeed,
             or (False, None) if the user cancels.
    """
    # TODO: add an option to allow this to accept unicode,
    # and do something better if that's not provided and unicode is entered
    # (right now it just raises a UnicodeEncodeError).

    # modified from _set_test_from_dialog( ),
    # which was modified from debug_runpycode_from_a_dialog,
    # which does the "run py code" debug menu command

    # Qt4 version [070329; similar code in an exprs-module file]

    inputDialog = QDialog() # No parent
    inputDialog.setWindowIcon(geticon(iconPath))

    text, ok = QInputDialog.getText(inputDialog, title, label,
                                    QLineEdit.Normal, default)
        # note: parent arg is needed in Qt4, not in Qt3

    if ok:
        # fyi: type(text) == <class '__main__.qt.QString'>
        text = str(text)
        text = text.replace("@@@",'\n')
    else:
        pass # print "grab_text_using_dialog: cancelled"
    return ok, text

# ==

# TODO: merge the features of the following grab_text_line_using_dialog
# with the above grab_text_using_dialog by adding options to distinguish
# them, and rewrite all calls to use the above grab_text_using_dialog.
# Also improve it to permit unicode.

def grab_text_line_using_dialog( default = "",
                                 title = "title",
                                 label = "label",
                                 iconPath  = "ui/border/MainWindow.png"): #bruce 070531
    """
    Use a dialog to get one line of text from the user, with given default
    (initial) value, dialog window title, and label text inside the dialog.
    If successful, return (True, text);
    if not, return (False, "Reason why not").
    Returned text is a python string (not unicode).
    """
    # WARNING: several routines contain very similar code.
    # We should combine them into one (see comment before this function).
    # This function was modified from grab_text_line_using_dialog() (above)
    # which was modified from _set_test_from_dialog(),
    # which was modified from debug_runpycode_from_a_dialog(),
    # which does the "run py code" debug menu command.

    inputDialog = QDialog() # No parent
    inputDialog.setWindowIcon(geticon(iconPath))

    text, ok = QInputDialog.getText(inputDialog, title, label,
                                    QLineEdit.Normal, default)
        # note: parent arg needed only in Qt4
    if not ok:
        reason = "Cancelled"
    if ok:
        try:
            # fyi: type(text) == <class '__main__.qt.QString'>
            text = str(text) ###BUG: won't work for unicode
        except:
            ok = False
            reason = "Unicode is not yet supported"
        ## text = text.replace("@@@",'\n')
    if ok:
        return True, text
    else:
        return False, reason
    pass

# end
