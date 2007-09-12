# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

def greenmsg(text):
    """Add the tags needed to display text in green in the HistoryWidget"""
    return "<span style=\"color:#006600\">" + text + "</span>"
    
def redmsg(text):
    """Add the tags needed to display text in red in the HistoryWidget"""
    return "<span style=\"color:#ff0000\">" + text + "</span>"
    
def orangemsg(text): #bruce 050412; for warnings less severe than errors; some redmsgs might need replacement with this
    """Add the tags needed to display text in orange in the HistoryWidget"""
    return "<span style=\"color:#e65900\">" + text + "</span>"

# (this one, by bruce, is only meant for internal use)
def _graymsg(text):
    return "<span style=\"color:#808080\">" + text + "</span>"

# ==

def quote_html(text): #bruce 050727
    for char, string in [('&', '&amp;'), ('<', '&lt;'), ('>', '&gt;')]: # &amp has to come first
        text = text.replace(char, string)
    return text
