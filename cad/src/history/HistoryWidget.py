# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
HistoryWidget.py -- provides a Qt "megawidget" supporting our history/status area.

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

TODO:

This file ought to be extensively revised or reorganized, possibly along
with all code that calls it (e.g. any code that generates status messages).

The history code itself (as opposed to the UI code in the megawidget)
should be split into a separate module when it gets complicated.

In fact, it should be split into a few cooperating objects (archive, widget,
file io, storage ops), in separate files. [bruce 080104 comment]

Terminology:

A "megawidget" is an object, not itself a widget, which controls
one or more widgets so as to act like a single more complex widget. I got the
term from "Python Megawidgets" (which are implemented in Tk rather than Qt).
"""

import sys, os, time

from PyQt4 import QtCore
from PyQt4.Qt import Qt
from PyQt4.Qt import QTextEdit, QTextOption

from utilities import debug_flags
from platform_dependent.PlatformDependent import mkdirs_in_filename
from widgets.DebugMenuMixin import DebugMenuMixin
import foundation.env as env

from utilities.prefs_constants import historyMsgTimestamp_prefs_key
from utilities.prefs_constants import historyMsgSerialNumber_prefs_key
from utilities.prefs_constants import historyHeight_prefs_key

from utilities.Log import graymsg, quote_html, greenmsg, redmsg, orangemsg

from platform_dependent.PlatformDependent import fix_plurals

class message:
    """
    Stores one message for a history.
    """
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
        return graymsg(self.widget_text_header()) + self.text #e could remove graymsg when what's inside it is ""
    def xml_text(self):
        assert 0, "nim" # same fields as widget text, but in xml, and not affected by display prefs
    pass

# hte_super = QTextEdit # also works (sort of) with QTextBrowser [bruce 050914]
# Switching to QTextBrowser also removes some misleading things from the HistoryWidget's context
# menu, since a user isn't allowed to put text in it. (E.g. "Insert Unicode control character")
#hte_super = QTextBrowser
hte_super = QTextEdit
m_super = DebugMenuMixin

class History_QTextEdit(hte_super, m_super):
    def __init__(self, parent):#050304
        hte_super.__init__(self, parent)
        m_super._init1(self) # provides self.debug_event() # note: as of 071010 this calls DebugMenuMixin._init1
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
        debug = debug_flags.atom_debug and 0
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
        """
        [overrides method from m_super (DebugMenuMixin)]
        """
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
        """
        search backwards for the last item of colored text
        """
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

# ==

class HistoryWidget:
    # - Someday we're likely to turn this widget into a frame with buttons.
    # - Note that we're assuming there is only one of these per program run --
    # not necessarily one per window, if we someday have more than one window.
    # If we decide more than one window displays the status, sharing one history,
    # we'll have to figure out how to do that at the time.
    def __init__(self, parent, header_line = None, filename = None, mkdirs = 0):
        """
        ###doc this;
        optional arg header_line should be a string, generally not ending in '\n'
        """
        if 1: #bruce 060301 (in two places)
            env.last_history_serno = self.last_serno

        self._deferred_summary_messages = {}
        
        ###### User Preference initialization ##############################
        
        # Get history related settings from prefs db.
        # If they are not found, set default values here.
        # The keys are located in constants.py
        # Mark 050716
        # [revised by bruce 050810; comment above is now no longer up to date]
        
        #ninad 060904 modified this Still a partial implementation of NFR 843
        self.history_height = env.prefs[historyHeight_prefs_key]

        
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
        if debug_flags.atom_debug:
            self._debug_init()
        self._print_msg(file_msg)
        return
    
    def _init_widget(self, parent):
        """
        [private]
        set up self.widget
        """
        self.widget = History_QTextEdit(parent) # public member, private value (except that it's a Qt widget)
        self.widget.setFocusPolicy(QtCore.Qt.ClickFocus) ##e StrongFocus also can be tabbed to, might be better
            # not needed on Mac [bruce], but needed on Windows [mark],
            # to support copy/paste command sequences, etc

        # Partial implem for NFR 843.  Need a method for updating the height of the widget. Mark 050729
        
        # The minimum height of the history widget. This attr is useful
        # if self's widget-owner needs to compute its own minimum height.
        self.minimumHeight = \
            self.widget.fontMetrics().lineSpacing() * \
            self.history_height + 2 # Plus 2 pixels
        self.widget.setMinimumHeight(int(self.minimumHeight))
        # Initialize the variable used in expanding / collapsing 
        # the history widget.
        self._previousWidgetHeight = self.minimumHeight

        self.widget.setWordWrapMode(QTextOption.WordWrap)
        self.widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget.ensureCursorVisible()
        return
    
    def collapseWidget(self):
        """
        Collapse the history widget.
        """
        #Store the earlier history widget height (to be used in 
        # self.expandWidget)
        self._previousWidgetHeight = self.widget.height()
        self.widget.setMaximumHeight(0)
    
    def expandWidget(self):
        """
        Expand the history widget
        """        
        self.widget.setMaximumHeight(self._previousWidgetHeight)
        
    
    file = None
    filename = ""
    def _init_file(self, filename, mkdirs = 0):
        """
        Set up optional file. Call this even if filename is None, so debug code can run.
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
        elif debug_flags.atom_debug:
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
        """
        record initial info useful for debugging
        """
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
        """
        [private method]
        Append some text to the widget and the optional history file.
        The text is not processed except to add newlines as needed.
        We assume the given text does not normally start or end with a newline.
        """
        ## something = str(something) # usually something should already be a string
        if self.file:
            self.file.write(something.encode("utf_8"))
            self.file.write('\n') # file gets \n after each line, not before
            if debug_flags.atom_debug:
                # (we also flush in self.h_update(), whether or not debugging)
                self.file.flush()
        self.widget.append(something) # apparently prepends a newline if needed
        self.widget.ensureCursorVisible()
            #e Someday we need a checkbox or heuristic to turn off this
            # autoscrolling, in case user wants to read or copy something
            # while new status messages keep pouring in.

    # main print method for one message
    
    def _print_msg(self, msg):
        """
        Format and print one message (a string, usually not starting or
        ending with newline). Precede it with a timestamp.
        Most printing should go though this method.
        Client code should call a higher-level method which uses this one.
        [Someday we might also #e:
        - compress redundant messages which would otherwise be too verbose.
        - add html or xml formatting, differently for different kinds of
          messages, as indicated by optional args (not yet designed).
        - when debugging, print info about the call stack at the time the
          message is printed [this is now implemented by a debug_pref, 060720].]
        """
        ###e in debug_stack mode, walk stack and compare to stored stack and print exit of old frames and enter of (some) new ones
        m1 = message(msg, hist = self)
        msg = m1.widget_html() # widget_text() or widget_html()
        self._append(msg) ##e need to pass the message object, since also puts it into the file, but text might be different! ###@@@
        if 0 and debug_flags.atom_debug: # this is redundant with __stderr__ in _append, so we no longer do it.
            print "(history:)", msg
        return

    # helpers for the message objects inside us

    last_serno = 0
    def next_serno(self):
        self.last_serno += 1
        if 1: #bruce 060301 (in two places)
            env.last_history_serno = self.last_serno
        return self.last_serno

    saved_msg = saved_options = saved_transient_id = None
    saved_norepeat_id = None
    
    # the main public method, typically accessed in new code as env.history.message(),
    # or in older code via the MainWindow object (e.g. win.history or w.history or self.history):
    
    def message(self, msg, transient_id = None, repaint = 0, norepeat_id = None, **options):
        """
        Compatibility method -- pretend we're a statusbar and this is its "set text" call.
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
           If color is provided, it should be one of a fixed list of supported colors (see code for details),
        and it's applied after quote_html, and (I hope) only in the widget, not in the statusbar
        (so it should be compatible with transient_id).
        """
        self.emit_all_deferred_summary_messages() # bruce 080130 new feature
            # REVIEW: should this be done here even if not msg?
            # The goals of doing it are to make sure it happens even for
            # commands that end by emitting only that message.
            # The side effect of printing it before transients
            # is probably bad rather than good. A better scheme might be
            # to call this as a side effect of internally ending a command
            # if we have any way to do that (e.g. related to the code that
            # automatically calls undo checkpoints then, or actually inside
            # the calling of some undo checkpoints).
        
        # (quote_html and color are implemented as one of the **options, not directly in this method. [bruce 060126])
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
        from utilities.debug_prefs import debug_pref, Choice_boolean_False
        if debug_pref("print history.message() call stacks?", Choice_boolean_False): #bruce 060720
            from utilities.debug import compact_stack
            options['compact_stack'] = compact_stack(skip_innermost_n = 1)
                # skips compact_stack itself, and this line that calls it
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

    def redmsg(self, msg, **kws): #bruce 080201
        """
        Shorthand for self.message(redmsg(msg), <options>).
        """
        self.message(redmsg(msg), **kws)
        return

    def orangemsg(self, msg, **kws): #bruce 080201
        """
        Shorthand for self.message(orangemsg(msg), <options>).
        """
        self.message(orangemsg(msg), **kws)
        return

    def greenmsg(self, msg, **kws): #bruce 080201
        """
        Shorthand for self.message(greenmsg(msg), <options>).
        """
        self.message(greenmsg(msg), **kws)
        return

    def graymsg(self, msg, **kws): #bruce 080201
        """
        Shorthand for self.message(graymsg(msg), <options>).
        """
        self.message(graymsg(msg), **kws)
        return
    
    # ==
    
    def flush_saved_transients(self):
        """
        make sure a saved-up transient message, if there is one,
        is put into the history now
        """
        self.message(None)
        # [passing None is a private implem -- outsiders should not do this!]

    # ==

    def deferred_summary_message(self, format, count = 1): #bruce 080130
        """
        Store a summary message to be emitted near the end of the current
        operation (in the current implem this is approximated as before
        the next history message of any kind), with '[N]' in the format string
        replaced with the number of calls of this method since the last time
        summary messages were emitted.

        @param format: message format string, containing optional '[N]'.
        @type format:  string (possibly containing HTML if that is compatible
                       with fix_plurals()).
        
        @param count: if provided, pretend we were called that many times,
                      i.e. count up that many occurrences. Default 1.
                      Passing 0 causes this summary message to be printed
                      later even if the total count remains 0.
        @type count:  nonnegative int.
        """
        # todo: message types should be classes, and the formatting using '[N]'
        # and fix_plurals (done elsewhere), as well as metainfo like whether
        # they are errors or warnings or neither, should be done by methods
        # and attrs of those classes. (True for both regular and deferred messages.)
        
        assert count >= 0 # 0 is permitted, but does have an effect
        # other code may also assume count is an int (not e.g. a float)
        self._deferred_summary_messages.setdefault( format, 0)
        self._deferred_summary_messages[ format] += count
        return

    def emit_deferred_summary_message(self, format, even_if_none = False):
        """
        Emit the specified deferred summary message, if any have been recorded
        (or even if not, if the option requests that).
        """
        assert 0, "nim"

    def emit_all_deferred_summary_messages(self):
        """
        Emit all deferred summary messages which have been stored,
        in the sort order of their format strings,
        once each with their counts appropriately inserted.
        Clear the set of stored messages before emitting any messages.
        (If more are added during this call, that's probably a bug,
         but this is not checked for or treated specially.)

        This is called internally before other messages are emitted
        (in the present implem of this deferred summary message scheme),
        and can also be called externally at any time.
        """
        items = self._deferred_summary_messages.items() # (format, count) pairs
        self._deferred_summary_messages = {}
        items.sort() # use format string as sorting key.
            # TODO: use order in which messages first arrived (since last emitted). 
            # possible todo: let message provider specify a different sorting key.
        for format, count in items:
            self._emit_one_summary_message(format, count)
        return

    def _emit_one_summary_message(self, format, count):
        msg = format.replace("[N]", "%s" % count)
            # note: not an error if format doesn't contain "[N]"
        # assume msg contains '(s)' -- could check this instead to avoid debug print
        msg = fix_plurals(msg, between = 3)
            # kluge: if a large between option is generally safe,
            # it ought to be made the default in fix_plurals
            #
            # todo: review for safety in case msg contains HTML (e.g. colors)
            # todo: ideally format would be a class instance which knew warning status, etc,
            # rather than containing html
        self.message( msg)
        return
    
    # ==
    
    def statusbar_msg(self, msg_text, repaint = False):
        """
        Show the message I{msg_text} (which must be plain text and short) in 
        the main window's status bar. This only works for plain text messages,
        not html. If the message is too long, it might make the window become
        too wide, perhaps off the screen! Thus use this with care.
        
        Also, the message might be erased right away by events beyond our 
        control. Thus this is best used only indirectly by self.message with
        transient_id option, and only for messages coming out almost
        continuously for some period, e.g. during a drag.
        
        @param msg_text: The message for the status bar.
        @type  msg_text: string
        
        @param repaint: Forces a repaint of the status bar with the new message.
                        This doesn't work (see Bruce's comments in code).
        @param repaint: boolean
        """
        win = env.mainwindow()
        sbar = win.statusBar()

        if msg_text:
            sbar.showMessage(msg_text)
        else:
            sbar.clearMessage()
        if repaint:
            ## this didn't work, so don't do it until I know why it didn't work:
            ## sbar.repaint()
            ##   #k will this help extrude show its transient msgs upon entry?
            # so do this instead:
            print msg_text
        return
    
    def progress_msg(self, msg_text): # Bug 1343, wware 060310
        win = env.mainwindow()
        statusBar = win.statusBar()
        statusBar.statusMsgLabel.setText(msg_text)
    
    def widget_msg(self, msg, options):
        #e improved timestamp?
        #e use html for color etc? [some callers put this directly in the msg, for now]
        _quote_html = options.pop('quote_html', False) #bruce 060126 new feature, improving on message_no_html interface ##k
        if _quote_html:
            msg = quote_html(msg)
        _color = options.pop('color', None)
        if _color:
            #bruce 060126 new feature; for now only permits 4 fixed color name strings;
            # should someday permit any color name (in any format) or object (of any kind) #e
            funcs = {'green':greenmsg, 'orange':orangemsg, 'red':redmsg, 'gray':graymsg}
            func = funcs[_color] # any colorname not in this dict is an exception (ok for now)
            msg = func(msg)
        _compact_stack = options.pop('compact_stack', "") #bruce 060720
        if _compact_stack:
            msg += graymsg("; history.message() call stack: %s" % quote_html(_compact_stack))
        # any unrecognized options are warned about below
        self._print_msg(msg)
        if options:
            msg2 = "fyi: bug: widget_msg got unsupported options: %r" % options
            print msg2 # too important to only print in the history file --
                # could indicate that not enough info is being saved there
            self._print_msg(msg2)
        return
    
    def debug_print(self, fmt, *args):
        """
        Any code that wants to print debug-only notes, properly timestamped
        and intermixed with other history, and included in the history file,
        can use this method.
        """
        if not debug_flags.atom_debug:
            return
        msg = ("debug: " + fmt) % args
        self._print_msg(msg)

    # inval/update methods
    
    def h_update(self): # bruce 050107 renamed this from 'update'
        """
        (should be called at the end of most user events)
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
