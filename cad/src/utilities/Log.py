# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details.
"""
utilities/Log.py -- utility functions related to message logging

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:

Mark wrote these in HistoryWidget.py.

Bruce added quote_html and graymsg.

EricM moved them into a separate file in 2007.
"""

def greenmsg(text):
    """
    Add the html tags needed to display text in green in the HistoryWidget.
    """
    return "<span style=\"color:#006600\">" + text + "</span>"

def redmsg(text):
    """
    Add the html tags needed to display text in red in the HistoryWidget.
    Used for serious error messages, bug reports, etc.
    """
    return "<span style=\"color:#ff0000\">" + text + "</span>"

def orangemsg(text): # some redmsgs might need replacement with this
    """
    Add the html tags needed to display text in orange in the HistoryWidget.
    Used for warnings, and some info the user always needs to be aware of.
    """
    return "<span style=\"color:#e65900\">" + text + "</span>"

def graymsg(text): #bruce 080201 added this to replace _graymsg
    """
    Add the html tags needed to display text in gray in the HistoryWidget.
    Used for developer/debug messages (should probably not be used unless
    debug_prefs or similar debugging options are set).
    """
    return "<span style=\"color:#808080\">" + text + "</span>"

def _graymsg(text): # remove this when its uses are all converted to graymsg
    """
    This is the old name of graymsg (which it calls), but is now deprecated.
    New code should use graymsg instead.
    """
    return graymsg(text)

# ==

def quote_html(text):
    """
    Encode a few html special characters in text, so that it is safe
    to display in the history widget, and so the special characters
    will look like their original forms.

    @note: if quote_html is used in conjunction with e.g. redmsg,
    it must be used inside it, or it will break the effect of redmsg.
    I.e. use them together like this: redmsg(quote_html(text)).
    """
    for char, string in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')]:
        # note: &amp has to come first
        text = text.replace(char, string)
    return text

# end
