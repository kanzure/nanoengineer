# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
HistoryMegawidget.py provides a Qt "megawidget" supporting our history/status area.

The history code itself (as opposed to the UI code in the megawidget)
will be split into a separate module when it gets complicated.

Terminology: a "megawidget" is an object, not itself a widget, which controls
one or more widgets so as to act like a single more complex widget. I got the
term from "Python Megawidgets" (which are implemented in Tk rather than Qt).

$Id$
'''
__author__ = "bruce"

from qt import QTextEdit
import sys, os, time

class HistoryMegawidget:
    def __init__(self, parent, line1 = None):
        """###doc this;
        optional arg line1 should be a string, generally not ending in '\n'
        """
        ###stub -- we'll likely turn this widget into a frame with buttons
        self.widget = QTextEdit(parent) # public member, private value (except that it's a Qt widget)
        if line1 == None:
            line1 = time.asctime() #stub
        self._insert(line1) # no '\n'
        import platform
        if platform.atom_debug:
            self.debug_init()
    def debug_init(self):
        try:
            ff = "\"%s\"" % __file__
            our_mtime = os.stat(__file__).st_mtime
            tt = time.asctime(time.localtime(our_mtime))
        except:
            ff = "this module's"
            tt = "<exception discarded>"
        self._print("atom_debug: %s modtime is %s" % (ff,tt))
    def _insert(self, something):
        "Insert some text. We might deprecate this interface!"
        self.widget.insert(something)
    def _print(self, line):
        self._insert("\n")
        self._insert(line)
    def set_status_text(self, text, **options):
        """Compatibility method -- pretend we're a statusbar and this is its "set text" call.
        [The following is not yet implemented as of the initial commit:]
        In reality, make sure the new end of the history looks basically like the given text,
        but use semi-heuristics to decide how to combine this text with previous "status text"
        so that the recorded history is not too full of redundant messages.
        Soon, we might add options to help tune this, or switch to separate methods.
        """
        #e timestamp?
        #e use html for color etc?
        self._print(text.replace('\r','\n'))
            # it looks like '\r' was messing up msgs from Extrude (unconfirmed theory)
        if options:
            msg = "fyi: bug: set_status_text got unsupported options: %r" % options
            print msg
            self._print(msg)
        return
    pass

# end
