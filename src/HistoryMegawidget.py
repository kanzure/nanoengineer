# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
'''
HistoryMegawidget.py provides a Qt "megawidget" supporting our history/status area.

For now (circa 040105 and until further notice), this file is owned by Bruce,
and is likely to be extensively revised or reorganized at any time, possibly
along with all code that calls it (e.g. any code that generates status messages).

The history code itself (as opposed to the UI code in the megawidget)
will be split into a separate module when it gets complicated.

Terminology: a "megawidget" is an object, not itself a widget, which controls
one or more widgets so as to act like a single more complex widget. I got the
term from "Python Megawidgets" (which are implemented in Tk rather than Qt).

This file should probably be renamed HistoryWidget.py, since megawidgets are normal.

$Id$
'''
__author__ = "bruce"

from qt import *
import sys, os, time
import platform # for atom_debug

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

class message:
    """Stores one message for a history."""
    #e this will get more complicated (and its existence will be justified)
    # once messages can be html-formatted, include links to what they're about,
    # etc; and it may also gain search or filter methods for the display.
    def __init__(self, text, timestamp_as_seconds = None, serno = None, hist = None):
        self.text = text # plain text for now; should not normally have \n at start or end
        if not timestamp_as_seconds:
            timestamp_as_seconds = time.time() # floating point number
        self.time = timestamp_as_seconds
        if not serno:
            try:
                serno = hist.next_serno()
            except:
                serno = -1
        self.serno = serno
    def timestamp_text(self):
        #e should inherit the method from the display env
        timetuple = time.localtime(self.time)
        return time.asctime(timetuple).split()[3] ###stub; i hope this is hh:mm:ss
    def widget_text_header(self):
        return "%d. [%s] " % (self.serno, self.timestamp_text())
    def widget_text(self):
        return self.widget_text_header() + self.text
    def widget_html(self): ###@@@ experimental. This sort of works... 
        ###e also escape < > and & ? not appropriate when self.text contains html, as it sometimes does!
        # maybe it's best in the long run to just require the source messages to escape these if they need to.
        # if not, we'll need some sort of hueristic to escape them except when part of well-formatted tags.
        return "<span style=\"color:#808080\">%s</span>" % self.widget_text_header() + self.text
    def xml_text(self):
        assert 0, "nim" # same fields as widget text, but in xml, and not affected by display prefs
    pass

class History_QTextEdit(QTextEdit):
    def focusInEvent(self, event):
        ## print "fyi: hte focus in" # debug
        return QTextEdit.focusInEvent(self, event)
    def focusOutEvent(self, event):
        ## print "fyi:   hte focus out" # debug
        return QTextEdit.focusOutEvent(self, event)
    def event(self, event):
        # this is getting called for various events, but of the ones in the QTextEdit, not for any mouse events,
        # but is called for KeyEvents (2 each, presumably one press res T, and one release res F).
        # Could this be a difference in PyQt and Qt? Or, is it because we're outside the scrollview?
        debug = platform.atom_debug and 0
        if debug:
            try:
                after = event.stateAfter()
            except:
                after = "<no stateAfter>" # needed for Wheel events, at least [code copied from GLPane.py]
            print "fyi: hte event %r; stateAfter = %r" % (event, after)
        res = QTextEdit.event(self, event)
        if debug:
            print " (event done, res = %r)" % res
        #e now if it was a paintevent, try painting something else over it... or try implementing the method for catching those...
        #e watch out for being outside the scrollview.
        return res
    def repaint(self, *args):
        print "repaint, %r" % args # this is not being called, even though we're getting PaintEvents above.
        return QTextEdit.repaint(*args)
    pass
    
class HistoryMegawidget:
    # - Someday we're likely to turn this widget into a frame with buttons.
    # - Note that we're assuming there is only one of these per program run --
    # not necessarily one per window, if we someday have more than one window.
    # If we decide more than one window displays the status, sharing one history,
    # we'll have to figure out how to do that at the time.
    def __init__(self, parent, header_line = None, filename = None, mkdirs = 0):
        """###doc this;
        optional arg header_line should be a string, generally not ending in '\n'
        """
        if header_line == None:
            header_line = "session history, started at: %s" % time.asctime() #stub
        self._init_widget(parent)
        file_msg = self._init_file(filename, mkdirs = mkdirs)
        self._append(header_line) # appends to both widget and file
        # most output should pass through self._print_msg, not just self._append
        if platform.atom_debug:
            self._debug_init()
        self._print_msg(file_msg)
        return
    
    def _init_widget(self, parent):
        "[private] set up self.widget"
        self.widget = History_QTextEdit(parent) # public member, private value (except that it's a Qt widget)
        self.widget.setFocusPolicy(QWidget.ClickFocus) ##e StrongFocus also can be tabbed to, might be better
            # not needed on Mac [bruce], but needed on Windows [mark],
            # to support copy/paste command sequences, etc
        return
    
    file = None
    filename = ""
    def _init_file(self, filename, mkdirs = 0):
        """Set up optional file. Call this even if filename is None, so debug code can run.
        Don't output a history message naming the file -- but return one,
        so caller can do that later if it wants to.
        """
        if filename:
            # user wants history saved; save it or print it.
            try:
                if mkdirs: # this is optional, for safety
                    mkdirs_in_filename(filename)
                ff = open(filename, "a")
            except:
                print "bug warning: couldn't make history file %r; printing to sys.__stderr__ instead" % filename
                self.filename = "sys.__stderr__"
                self.file = sys.__stderr__
            else:
                self.filename = filename
                self.file = ff
        elif platform.atom_debug:
            # developer wants it saved, but program thinks user doesn't
            print "atom_debug: printing history to sys.__stderr__"
            self.filename = "sys.__stderr__"
            self.file = sys.__stderr__
        else:
            pass
        # make sure print output says what's happening, one way or another
        if self.file: # even if it's __stderr__
            self.file.write("# nanorex history file, format version 050104\n")
            self.file.flush()
            file_msg = "(saving history in file \"%s\")" % self.filename
        else:
            file_msg = "(history is not being saved in any file)"
        print file_msg #e remove this soon
        return file_msg
    
    def _debug_init(self):
        "record initial info useful for debugging"
        # record modtime of this module
        try:
            ff = "\"%s\"" % __file__
            our_mtime = os.stat(__file__).st_mtime
            tt = time.asctime(time.localtime(our_mtime))
        except:
            ff = "this module's"
            tt = "<exception discarded>"
        self._print_msg("atom_debug: %s modtime is %s" % (ff,tt))
    
    def _append(self, something): ###e perhaps split into append_text, append_html, and append_msg
        """[private method] Append some text to the widget and the optional history file.
        The text is not processed except to add newlines as needed.
        We assume the given text does not normally start or end with a newline.
        """
        ## something = str(something) # usually something should already be a string
        if self.file:
            self.file.write(something)
            self.file.write('\n') # file gets \n after each line, not before
            if platform.atom_debug:
                # (we also flush in self.update(), whether or not debugging)
                self.file.flush()
        self.widget.append(something) # apparently prepends a newline if needed
        self.widget.scrollToBottom()
            #e Someday we need a checkbox or heuristic to turn off this
            # autoscrolling, in case user wants to read or copy something
            # while new status messages keep pouring in.

    # main print method for one message
    
    def _print_msg(self, msg):
        """Format and print one message (a string, usually not starting or
        ending with newline). Precede it with a timestamp.
        Most printing should go though this method.
        Client code should call a higher-level method which uses this one.
        [Someday we might also #e:
        - compress redundant messages which would otherwise be too verbose.
        - add html or xml formatting, differently for different kinds of
          messages, as indicated by optional args (not yet designed).
        - when debugging, print info about the call stack at the time the
          message is printed.]
        """
        ###e in debug_stack mode, walk stack and compare to stored stack and print exit of old frames and enter of (some) new ones
        m1 = message(msg, hist = self)
        msg = m1.widget_html() # widget_text() or widget_html()
        self._append(msg) ##e need to pass the message object, since also puts it into the file, but text might be different! ###@@@
        if 0 and platform.atom_debug: # this is redundant with __stderr__ in _append, so we no longer do it.
            print "(history:)", msg
        return

    # helpers for the message objects inside us

    last_serno = 0
    def next_serno(self):
        self.last_serno += 1
        return self.last_serno
    
    # public methods:
    
    def set_status_text(self, msg, **options):
        """Compatibility method -- pretend we're a statusbar and this is its "set text" call.
        [The following is not yet implemented as of the initial commit:]
        In reality, make sure the new end of the history looks basically like the given text,
        but use semi-heuristics to decide how to combine this text with previous "status text"
        so that the recorded history is not too full of redundant messages.
        Soon, we might add options to help tune this, or switch to separate methods.
        [Some of these features might be in _print_msg rather than in this method directly.]
        """
        #e improved timestamp?
        #e use html for color etc?
        self._print_msg(msg)
        if options:
            msg2 = "fyi: bug: set_status_text got unsupported options: %r" % options
            print msg2 # too important to only print in the history file --
                # could indicate that not enough info is being saved there
            self._print_msg(msg2)
        return
    
    def debug_print(self, fmt, **args):
        """Any code that wants to print debug-only notes, properly timestamped
        and intermixed with other history, and included in the history file,
        can use this method."""
        if not platform.atom_debug:
            return
        msg = ("atom_debug: " + fmt) % args
        self._print_msg(msg)

    # inval/update methods
    
    def update(self):
        """(should be called at the end of most user events)"""
        if self.file:
            self.file.flush()
            #k is this too slow, e.g. for bareMotion or keystrokes?
            # if so, don't call it for those, or make it check whether it's needed.
            #k is this often enough, in case of bugs? Maybe not,
            # so we also flush every msg when atom_debug (in another method).
        # nothing for widget is yet needed here, since changes to QTextEdit cause it to be
        # invalidated and later updated (repainted) by internal Qt code,
        # using a separate update event coming after other Qt events are processed,
        # but maybe something will be needed later. [bruce 041228]
        return
    
    def update_experimental_dont_call_me(self):
        self.widget.update()
            # http://doc.trolltech.com/3.3/qwidget.html#update
        ###@@@ try calling this from win.update to see if that fixes the repaint bugs after leaving extrude!
            ### it was not enough. guess: it is not updated because it does not have the focus...
            # so try an explicit repaint call.
        self.widget.repaint()
        # also not enough. what's up with it?? did it not yet get passed correct geometry info? does repaint need a rect?
        # ###@@@
    
    pass # end of class HistoryMegawidget

# end
