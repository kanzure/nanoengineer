# Copyright (c) 2004-2006 Nanorex, Inc.  All rights reserved.
'''
HistoryWidget.py provides a Qt "megawidget" supporting our history/status area.

For now (circa 040105 and until further notice), this file is owned by Bruce,
and is likely to be extensively revised or reorganized at any time, possibly
along with all code that calls it (e.g. any code that generates status messages).

The history code itself (as opposed to the UI code in the megawidget)
will be split into a separate module when it gets complicated.

Terminology: a "megawidget" is an object, not itself a widget, which controls
one or more widgets so as to act like a single more complex widget. I got the
term from "Python Megawidgets" (which are implemented in Tk rather than Qt).

This file used to be named HistoryMegawidget.py, but that was unnecessarily
verbose, since megawidgets are normal. This file's rev 1.1 is identical
to HistoryMegawidget.py's rev 1.5 except for this name change, which appears
only in this docstring and the classname (and in a few other files).

$Id$
'''
__author__ = "bruce"

from qt import *
import sys, os, time
import platform # for atom_debug, and more
from debug import DebugMenuMixin, privateMethod
from constants import *
import preferences
import env #bruce 050810


# [formatters by Mark; moved into this file by bruce 050107;
#  at some point these might be renamed based on what kinds of messages
#  or message-fragments to use them for, and/or used automatically by
#  methods in here meant for certain kinds of messages.]

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

# ==

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
        self.hist = hist # mark added this
    def timestamp_text(self):
        #e should inherit the method from the display env
        if env.prefs[historyMsgTimestamp_prefs_key]:
            timetuple = time.localtime(self.time)
            # mark pulled the format string into this method
            return "[%s] " % (time.asctime(timetuple).split()[3]) ###stub; i hope this is hh:mm:ss
        else:
            return ''
    def serial_number_text(self):
        if env.prefs[historyMsgSerialNumber_prefs_key]:
            # mark pulled the format string into this method
            return "%d. " % (self.serno)
        else:
            return ''
    def widget_text_header(self): # mark revised the subrs, so this can now be "".
        return self.serial_number_text() + self.timestamp_text()
    def widget_text(self):
        return self.widget_text_header() + self.text
    def widget_html(self): ###@@@ experimental. This sort of works... 
        ###e also escape < > and & ? not appropriate when self.text contains html, as it sometimes does!
        # maybe it's best in the long run to just require the source messages to escape these if they need to.
        # if not, we'll need some sort of hueristic to escape them except when part of well-formatted tags.
        return _graymsg(self.widget_text_header()) + self.text #e could remove _graymsg when what's inside it is ""
    def xml_text(self):
        assert 0, "nim" # same fields as widget text, but in xml, and not affected by display prefs
    pass

hte_super = QTextEdit # also works (sort of) with QTextBrowser [bruce 050914]
m_super = DebugMenuMixin

class History_QTextEdit(hte_super, m_super):
    def __init__(self, parent):#050304
        hte_super.__init__(self, parent)
        m_super._init1(self) # provides self.debug_event()
    def focusInEvent(self, event):
        ## print "fyi: hte focus in" # debug
        return hte_super.focusInEvent(self, event)
    def focusOutEvent(self, event):
        ## print "fyi:   hte focus out" # debug
        return hte_super.focusOutEvent(self, event)
    def event(self, event):
        # this is getting called for various events, but of the ones in the QTextEdit, not for any mouse events,
        # but is called for KeyEvents (2 each, presumably one press res T, and one release res F).
        # Could this be a difference in PyQt and Qt? Or, is it because we're outside the scrollview?
        # I should try overriding contentsEvent instead... ###e
        debug = platform.atom_debug and 0
        if debug:
            try:
                after = event.stateAfter()
            except:
                after = "<no stateAfter>" # needed for Wheel events, at least [code copied from GLPane.py]
            print "fyi: hte event %r; stateAfter = %r" % (event, after)
        res = hte_super.event(self, event)
        if debug:
            print " (event done, res = %r)" % res
        #e now if it was a paintevent, try painting something else over it... or try implementing the method for catching those...
        #e watch out for being outside the scrollview.
        return res
    def contentsMousePressEvent(self, event):#050304
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            return
        return hte_super.contentsMousePressEvent(self, event)
    def repaint(self, *args):
        print "repaint, %r" % args # this is not being called, even though we're getting PaintEvents above.
        return hte_super.repaint(*args)
    def debug_menu_items(self):
        "[overrides method from m_super (DebugMenuMixin)]"
        usual = m_super.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = [
                ## ("reload modules and remake widget", self._reload_and_remake),
                ## ("(treewidget instance created %s)" % self._init_time, lambda x:None, 'disabled'),
                ## ("history widget debug menu", noop, 'disabled'),
                ]
        ## ours.append(None)
        ours.extend(usual)
        #e more new ones on bottom?
        ## [not yet working:]
        ## ours.append(("last colored text", self._debug_find_last_colored_text))
        return ours
    def _debug_find_last_colored_text(self): #bruce 050509 experiment; not yet working
        "search backwards for the last item of colored text"
        case_sensitive = True
        word_only = False
        forward = False
        lookfor = "<span style=\"color:#" # limit this to error or warning? problem: this even finds "gray" timestamps.
            # that is, it *should* find them, but in fact it doesn't seem to work at all -- it doesn't move the cursor.
            # Could it be that it's not looking in the html, only in the main text? Yes -- it finds this if it's in main text!
            # So I should have it look for something recognizable other than color, maybe "] error" or "] warning". ###e
        # first back up a bit??
        self.find( lookfor, case_sensitive, word_only, forward) # modifies cursor position; could pass and return para/index(??)
    pass # end of class History_QTextEdit
    
class HistoryWidget:
    # - Someday we're likely to turn this widget into a frame with buttons.
    # - Note that we're assuming there is only one of these per program run --
    # not necessarily one per window, if we someday have more than one window.
    # If we decide more than one window displays the status, sharing one history,
    # we'll have to figure out how to do that at the time.
    def __init__(self, parent, header_line = None, filename = None, mkdirs = 0):
        """###doc this;
        optional arg header_line should be a string, generally not ending in '\n'
        """
        
        ###### User Preference initialization ##############################
        
        # Get history related settings from prefs db.
        # If they are not found, set default values here.
        # The keys are located in constants.py
        # Mark 050716
        # [revised by bruce 050810; comment above is now no longer up to date]
                
        self.history_height = env.prefs.get(historyHeight_prefs_key, 4)
        
        ###### End of User Preference initialization ########################## 
        
        if header_line == None:
            ## header_line_1 = "(running from [%s])" % os.path.dirname(os.path.abspath(sys.argv[0])) #bruce 050516
            ## header_line_2 = "session history, started at: %s" % time.asctime() #stub
            ## header_line = header_line_1 + '<br>' + header_line_2 # <br> is now tested and works [bruce 050516]
            timestr = time.asctime() # do this first
            path = os.path.dirname(os.path.abspath(sys.argv[0])) #bruce 050516 added "running from" path to this message
                # (if this proves to be too long, we can shorten it or make it only come out when atom_debug is set)
            header_line = "session history (running from %s), started at: %s" % (path, timestr) #stub
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

        # Partial implem for NFR 843.  Need a method for updating the height of the widget. Mark 050729
        h = self.widget.fontMetrics().lineSpacing() * self.history_height + 2 # Plus 2 pixels
        self.widget.setGeometry(QRect(0,0,100,h))
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
                    platform.mkdirs_in_filename(filename)
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
        privateMethod()
        ## something = str(something) # usually something should already be a string
        if self.file:
            self.file.write(something)
            self.file.write('\n') # file gets \n after each line, not before
            if platform.atom_debug:
                # (we also flush in self.h_update(), whether or not debugging)
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

    saved_msg = saved_options = saved_transient_id = None
    saved_norepeat_id = None
    
    # the main public method, typically accessed in new code as env.history.message(),
    # or in older code via the MainWindow object (e.g. win.history or w.history or self.history):
    
    def message(self, msg, transient_id = None, repaint = 0, norepeat_id = None, **options):
        """Compatibility method -- pretend we're a statusbar and this is its "set text" call.
        [The following is not yet implemented as of the initial commit:]
        In reality, make sure the new end of the history looks basically like the given text,
        but use semi-heuristics to decide how to combine this text with previous "status text"
        so that the recorded history is not too full of redundant messages.
        Soon, we might add options to help tune this, or switch to separate methods.
        [Some of these features might be in _print_msg rather than in this method directly.]
           If transient_id is supplied, then for successive messages for which it's the same,
        put them all in the conventional statusbar, but only print the last one into the widget.
        (This can only be done when the next message comes. To permit this to be forced to occur
        by client code, a msg of None or "" is permitted and ignored. [#e also clear statusbar then?])
           When transient_id is supplied, repaint = 1 tries to repaint the statusbar after modifying it.
        Presently this doesn't yet work, so it prints the msg instead, to be sure it's seen.
        This option should be used during a long computation containing no Qt event processing.
        (Which should ideally never be allowed to occur, but that's a separate issue.)
           If norepeat_id is supplied (assumed not to co-occur with transient_id),
        print the first message normally (out of several in a row with the same norepeat_id)
        but discard the others.
           If quote_html is True, replace the html-active chars '<', '>', '&' in msg
        with forms that will print as themselves. Note that this is not compatible with text
        returned by functions such as greenmsg; for that, you have to use quote_html(text) on appropriate
        portions of the message text. See also message_no_html.
           When quote_html is combined with transient_id, (I hope) it only affects the
        message printed to the history widget, not to the statusbar.
        """
        # (quote_html is implemented as one of the **options, not directly in this method. [bruce 060126])
        # first emit a saved_up message, if necessary
        if self.saved_transient_id and self.saved_transient_id != transient_id:
            self.widget_msg( self.saved_msg, self.saved_options)
            self.saved_msg = self.saved_options = self.saved_transient_id = None # just an optim
            self.statusbar_msg("") # no longer show it in true statusbar
                # (this might clear someone else's message from there; no way to avoid this
                #  that I know of; not too bad, since lots of events beyond our control do it too)
        
        # "call env.in_op() from code that runs soon after missing env.begin_op() calls" [bruce 050908]
        # (##fix: we do this after the saved-up message, but that's cheating,
        #  since non-missing begin_ops need some other way to handle that,
        #  namely, saving up a message object, which grabs some current-op info
        #  when created rather than when printed.)
        env.in_op('(history message)') # note, this is also called for transient_id messages which get initially put into sbar...
            # is it ok if env.in_op recursively calls this method, self.message??
            # I think so, at least if subcall doesn't use transient_id option. ##k [bruce 050909]
            
        # never save or emit a null msg (whether or not it came with a transient_id)
        if not msg:
            return
        # now handle the present msg: save (and show transiently) or emit
        if transient_id:
            self.statusbar_msg(msg, repaint = repaint) # (no html allowed in msg!)
            # (Actually we should make a message object now, so the timestamp is
            # made when the message was generated (not when emitted, if that's delayed),
            # and then show its plain text version transiently (including a text
            # timestamp), and save the same message object for later addition to the
            # widget and file. Should be straightforward, but I'll commit it separately
            # since it requires message objects to be created higher up, and
            # ideally passed lower down, than they are now. ###@@@)
            self.saved_msg = msg
            self.saved_options = options
            self.saved_transient_id = transient_id
        else:
            if norepeat_id and norepeat_id == self.saved_norepeat_id:
                return
            self.saved_norepeat_id = norepeat_id # whether supplied or None
            self.widget_msg( msg, options)
        return

    def message_no_html(self, msg, **kws): #bruce 050727; revised 060126 (should now be more correct when combined with transient_id)
        ## msg = quote_html(msg)
        ## self.message( msg, **kws)
        opts = dict(quote_html = True) # different default than message, but still permit explicit caller option to override
        opts.update(kws)
        return self.message( msg, **opts)
    
    def flush_saved_transients(self):
        """make sure a saved-up transient message, if there is one,
        is put into the history now
        """
        self.message(None)
        # [passing None is a private implem -- outsiders should not do this!]
    
    def statusbar_msg(self, msg_text, repaint = 0): #bruce 050914 renamed transient_msg => statusbar_msg
        """Show the message (which must be plain text and short) in Qt's main status bar.
        This only works for plain text messages, not html.
        If the message is too long, it might make the window become too wide, perhaps off the screen!
        Thus use this with care.
        Also, the message might be erased right away by events beyond our control.
        Thus this is best used only indirectly by self.message with transient_id option,
        and only for messages coming out almost continuously for some period, e.g. during a drag.
        """
        # This implem is a kluge, to handle some even worse kluges presently in MWsemantics;
        # those will be cleaned up soon (I hope) and then this can be too.
        # Kluge or not, it should probably just call a method in MWsemantics... for now it's here.
        win = self.widget.topLevelWidget()
            # ... use an init option instead? for win, or the sbar itself...
        # work around the kluge in MWsemantics [not anymore! bruce 050107] ###@@@ redoc
        if 0:
            orig_sb_method = win.__class__.statusBar 
            sbar = orig_sb_method(win)
        else:
            # what we'd do without that kluge
            sbar = win.statusBar()
        # now we can emit the message
        if msg_text:
            sbar.message(msg_text)
        else:
            sbar.clear()
        if repaint:
            ## this didn't work, so don't do it until I know why it didn't work:
            ## sbar.repaint()
            ##   #k will this help extrude show its transient msgs upon entry?
            # so do this instead:
            print msg_text
        return
    
    def widget_msg(self, msg, options):
        #e improved timestamp?
        #e use html for color etc? [some callers put this directly in the msg, for now]
        _quote_html = options.pop('quote_html', False) #bruce 060126 new feature, improving on message_no_html interface ##k
        if _quote_html:
            msg = quote_html(msg)
        # any other options are warned about below
        self._print_msg(msg)
        if options:
            msg2 = "fyi: bug: widget_msg got unsupported options: %r" % options
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
    
    def h_update(self): # bruce 050107 renamed this from 'update'
        """(should be called at the end of most user events)
        [no longer named update, since that conflicts with QWidget.update --
         technically this doesn't matter since we are not a QWidget subclass,
         but even so it's good to avoid this confusion.]
        """
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
    
    def h_update_experimental_dont_call_me(self):
        self.widget.update()
            # http://doc.trolltech.com/3.3/qwidget.html#update
        ###@@@ try calling this from win.win_update to see if that fixes the repaint bugs after leaving extrude!
            ### it was not enough. guess: it is not updated because it does not have the focus...
            # so try an explicit repaint call.
        self.widget.repaint()
        # also not enough. what's up with it?? did it not yet get passed correct geometry info? does repaint need a rect?
        # ###@@@
    
    pass # end of class HistoryWidget

# end
