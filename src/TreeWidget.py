# Copyright (c) 2004-2005 Nanorex, Inc.  All rights reserved.
"""
TreeWidget.py -- adds event handling and standard event bindings to TreeView.py.

[temporarily owned by Bruce, circa 050107, until further notice]

$Id$

History: modelTree.py was originally written by some combination of
Huaicai, Josh, and Mark. Bruce (Jan 2005) reorganized its interface with
Node and Group and their subclasses (Utility.py and other modules)
and rewrote a lot of the model-tree code (mainly to fix bugs),
and split it into three modules:
- TreeView.py (display and update),
- TreeWidget.py (event handling, and some conventions suitable for
  all our tree widgets, if we define other ones), and
- modelTree.py (customized for showing a "model tree" per se).
"""

from TreeView import * # including class TreeView, and import * from many other modules
from selectMode import selectMolsMode, selectAtomsMode
allButtons = (leftButton|midButton|rightButton) #e should be defined in same file as the buttons

from platform import tupleFromQPoint, fix_plurals

# but platform thinks "# def qpointFromTuple - not needed"; for now, don't argue, just do it here:
def QPointFromTuple((x,y)):
    return QPoint(x,y)

debug_dragstuff = 0 # DO NOT COMMIT with 1. - at least not for the alpha-release version (see below)
    # to enable this at runtime, type the following into the "run py code" menu item's dialog:
    # import TreeWidget@@@TreeWidget.debug_dragstuff = 1

# catch and fix error of my having committed this code with debug_dragstuff set:
import os
if not (os.path.isdir("/Users/bruce") and os.path.isdir("/Huge")):
    # oops, I committed with that set to 1! sorry.
    # (well, since this check is here, i might commit it with 1 a few times, but remove it pre-release)
    debug_dragstuff = 0
if debug_dragstuff:
    print "\n * * * * Running with debug_dragstuff set. \nExpect lots of output if you drag in the model tree!\n"

# For some reason I want this module to be independent of Numeric for now:

def pair_plus((x0,y0),(x1,y1)):
    return x0+x1,y0+y1

def pair_minus((x0,y0),(x1,y1)):
    return x0-x1,y0-y1

# These drag_handler classes might turn out to be generally useful for all kinds
# of Qt widgets, so they might be moved to some other file like widgets.py or a
# new file. But for now, they are specific to being used inside this kind
# of TreeWidget -- they might depend intimately on its being a QListView
# whose items represent Nodes. [bruce 050128]

class drag_handler:
    """Abstract class for objects which handle individual drag events
    of various kinds, such as selection-extenders, selection-rects or lassos,
    and drag-and-drop (where we supplied the QDragObject);
    maybe even drag-and-drop of an externally supplied QDragObject.
    Eventually we'll document a general API that all subclasses must follow.
    At first this is ill-defined since there might be only one subclass.
    """
    def cleanup(self, client):
        "[should be overridden in subclasses]"
        pass
    def one_of_yours_Q( self, event, text): ##e should rename, zap text arg, call earlier in client's dropevent processing
        """Someone just now dropped this text on the client widget (your dragsource),
        using this QDropEvent... is it a drag-and-drop you (client's current drag_handler) initiated?
        [should be overridden in subclasses]
        """
        # this superclass method is only appropriate for handlers
        # of ordinary drags unrelated to drag-and-drop.
        if debug_dragstuff:
            print "that's weird, client should not get a drop at the same time as it's handling an ordinary drag! hmm..."
        return False # for example, false for selection-drags (though also it should never happen then)
    def describe_your_drag_and_drop(self):
        "#doc ... subclasses use this to say moving x items, for drags they started, queried by dragMove for statusbar"
        return "<unknown drag>" # should never be seen
    pass

class drag_and_drop_handler(drag_handler): #e this class could be made 1/2 or 1/3 of its present size!! [050129]
    """Handle an individual drag-and-drop event
    for which we supplied the QDragObject (??).
    Later we might split this into subclasses,
    with one for an externally supplied QDragObject... not sure.
    """
    def __init__(self, client, dragsource, drag_type, nodes, click_event):
        """Be ready to start a drag-and-drop (if subsequent mouse motion, fed to us,
        is large enough), whose dragsource, drag_type ('move' or 'copy') and dragged nodes
        are as specified,
        and whose initial click event was the one given
        (needed for its position, especially to decide when to start a drag).
        """
        self.client = client # for its helper methods... not yet uniformly used, mostly still uses dragsource for this purpose
        self.dragsource = dragsource # for creating the QDragObject (and not for much or anything else, ideally)
        assert client == dragsource # until we clean that up in these methods! ###e
        self.drag_type = drag_type
        self.nodes = nodes
        self.click_event = click_event
        # just storing the QPoint from click_event.globalPos() fails,
        # since the pos coords are garbage when checked later,
        # so store x0,y0 instead:
        x0,y0 = tupleFromQPoint(click_event.globalPos())
        self.click_xy = x0,y0
            # keep it in global coords in case of scrolling...
            # good? at least for checking distance threshhold to start a drag, it is.
        self.started_drag = False
        self.start_drag_dist = QApplication.startDragDistance() # this was 4 for me
        self.describe_drag = "<no drag started>" # should never be seen
        
    def mouseMoveEvent(self, event):
        "this must be called by our client, but only when mousebuttons remain down"
        if self.started_drag:
            # once set, this is never cleared, and if we see it in this event
            # it means (1) this object's useful life is over, (2) we're surprised
            # since mouse motion before mouseUp should be part of the drag and drop-or-not,
            # not an ordinary mouse motion event. Maybe this could happen if two mouse buttons
            # are down and one goes up? Not sure. Anyway, warn developer, then ignore it.
            if debug_dragstuff:
                print "fyi (bug??): drag_and_drop_handler mouseMoveEvent even after started_drag"
                ## (fyi: for debugging, we inlined "old_debugging_junk_not_called_now" here
                ##  but it also had those local vars we now define below)
            return
        # we're still waiting to see if the mouse moves enough to start a drag.
        listview = self.dragsource
        gpos = event.globalPos()
        gx,gy = tupleFromQPoint(gpos)
        x0,y0 = self.click_xy
        d2 = (gx-x0)**2 + (gy-y0)**2
        if d2 >= self.start_drag_dist**2:
            self.started_drag = True # warning: this flag means we decided to start one,
                # but following method sets another flag meaning it *actually* started one,
                # and that flag (not this one) is definitive for whether a dragEnter/drop etc is
                # assumed to have to come from us, vs. from an outside app.
            self.start_a_drag(event)
            if debug_dragstuff:
                print "returned from self.start_a_drag() (after recursive event processing)"
            ###e clear statusbar? btw we ought to do this thru a func, not directly;
            # so it can work with mouse enter/leave from client, to share sbar with other widgets.
            return # do no more in this object -- that drag and drop-or-not is all over
        else:
            # mouse didn't yet move enough to start a drag
            pass
        return
    def old_debugging_junk_not_called_now():
        # (this was in mouseMoveEvent above)
        # (keep around in case useful, esp as prototype for drop-point-highlighting code ###@@@)
        if not debug_dragstuff: return
        # for now, just draw something -- this may or may not run anymore, after we really start a drag... [so far, no.]
        unclipped = True # True works, can draw over the QListView column label and the scrollbar.
            # False draws nothing! [later: was that due to the rect in the event?]
            # So we have to use True for now, though it's "dangerous" in terms of what we might mess up.
            ##e probably better (and not hard) to define our own clipper and clip to that...
            #e we could also put this painter inside the drawing area, would that work better? try it sometime.
        painter = QPainter(listview, unclipped)
        gpos = event.globalPos()
        wpos = listview.mapFromGlobal(gpos)
        x,y=wpos.x(),wpos.y() # this works, scrolled or not, at least with unclipped = True
        listview.drawbluething( painter, (x,y)) # guess: this wants viewport coords (ie those of widget). yes.
        listview.update() #k needed?
        pass
    doing_our_own_drag = False
    def one_of_yours_Q( self, event, text): #e rename, re-spec, etc (see super comment)
        if not self.doing_our_own_drag:
            # note, this doesn't run during a drag of something from another widget (to drop on this one)
            # since this drag_handler won't be active then.
            return drag_handler(self, event, text) # super method, prints warning and rets False
        # ok, someone dropped this text on us, while we were doing our own drag.
        # Guess it must be our drag that got dropped!
##        # But let's do some sanity checks first:
##        self.dragged_text = text # cheat, since we don't have this handy anyway! later look inside dragobj for it??
##        if text != self.dragged_text and (1 or debug_dragstuff):
##            print "drag_and_drop_handler: possible bug: text != self.dragged_text: %r != %r" % (text , self.dragged_text)
##            # but otherwise ignore the error for now -- maybe something turned \n into nothing or so,
##            # and that might be OS-specific so I can't test for it right now... but always print,
##            # so someone testing on another OS will tell me.
        if debug_dragstuff:
            print_compact_stack("fyi: stack in one_of_yours_Q (should be inside start_a_drag): ")
        # ok, good enough for now. Just Do It.
        # The thing is, the client was handling the dragmoves, knows what items or gaps are lighted up
        # and ready to take the dropped nodes (and knows how to decide whether/how they can take them);
        # and it knows how to unhighlight them... so let the client do all that.
        # We'll just give it the info it needs about what we were trying to do.
        # I guess it's simpler to do that as a retval than as another layer of callback!
        #####@@@@@ revise return spec of this method
        # And, if drag_type was a move, then since this was all internal to one widget and nodetree,
        # we'll let it erase or move the original nodes too
        # (ie handle the source of the drag, as well as the target of the drop).
        # And that means that any highlighting of the original nodes should have been set up by it
        # and should now be undone by it. but that's hard since it was this object which decided to
        # do that, and when! So for that, we do need a callback telling it we're starting that drag of those nodes. #####@@@@@
        return (True, self.drag_type, self.nodes)
    
    def describe_your_drag_and_drop(self):
        # kluge 050131:
        return self.describe_drag
        
    def start_a_drag(self, event):
        """Start (and wait for completion of) a drag-and-drop of our nodes,
        using our other parameters from __init__,
        where event is the event which made the caller decide to start the drag
        (typically mouseMove, has globalPos(); not sure if we need it for anything).
           Note that recursive event processing (in self.dragsource's event methods called by Qt)
        occurs during this method. Since self.dragsource passes drag events into here (#e),
        method-recursion could occur in this object too.
        """
        dragobj = self.client.advise_starting_drag_and_get_dragobj( self.drag_type, self.nodes )
        ###@@@ we moved a lot from here into client -- does here even still need self.nodes, for example?
        assert not self.doing_our_own_drag
        self.doing_our_own_drag = True
            # we or our client can examine this flag
            # to guess whether a drag or drop event comes from us
            # or from the outside world (or another widget)
        try:
            self.do_our_own_drag( event, dragobj)
            self.doing_our_own_drag = False
        except:
            self.doing_our_own_drag = False
            print_compact_traceback("exception in do_our_own_drag(): ")
        return
    def do_our_own_drag(self, event, dragobj):
        # the following move/copy distinction needs to be "truthful"
        # to make the icon look right ('+' or not) on the Mac.
        if self.drag_type == 'move': 
            wantdel = dragobj.dragMove() #k guess at method name... seems to work
        else:
            wantdel = dragobj.dragCopy()
            # comments from the same code in canvas-b-3.py, probably apply here too:
            # during this call, we do recursive event processing, including the expected dragEnter event, and moves and drop,
            # plus another *initial* unexpected dragEnter event, different event object. To debug those, print the stack!
            # then our dropevent has an exception (for known reasons).
        # more stuff from canvas example, not reviewed:
        # Then, this prints: wantdel = None, target = source = the figureeditor obj (expected).
        if debug_dragstuff:
            print "dragged text: wantdel = %r, target = %r, dragsource = %r" % (wantdel, dragobj.target(), self.dragsource)
##            target = dragobj.target()
##            # what is target? not mtree or its viewport... (as far as pyqt knows, assuming that's the hex address i see in repr)
##            widget1 = target
##            try:
##                while widget1:
##                    print "target or a parent:",widget1
##                    # use QObject methods:
##                    print "  .className() = %r" % widget1.className()
##                    print "  .name() = %r" % widget1.name()
##                    widget1 = widget1.parent()
##                    if not widget1:
##                        print "  has no parent!"
##                    what_we_got_from_that = '''
##dragged text: wantdel = True, target = <constants.qt.QWidget object at 0x36e7b70>, dragsource = <modelTree.modelTree object at 0xd0de240>
##target or a parent: <constants.qt.QWidget object at 0x36e7b70>
##  .className() = 'QWidget'
##  .name() = 'qt_viewport'
##target or a parent: <modelTree.modelTree object at 0xd0de240>
##  .className() = 'modelTree'
##  .name() = 'modelTreeView'
##target or a parent: <constants.qt.QSplitter object at 0x36975d0>
##  .className() = 'QSplitter'
##  .name() = 'ContentsWindow'
##target or a parent: <constants.qt.QSplitter object at 0x3697660>
##  .className() = 'QSplitter'
##  .name() = 'vContentsWindow'
##target or a parent: <MWsemantics.MWsemantics object at 0x4c45a0>
##  .className() = 'MWsemantics'
##  .name() = 'nanoENGINEER-1'
##  has no parent!
##'''
##            except:
##                print_compact_traceback("oops: ")
                
        # dropped on model tree (tho it does not accept it): target == dragsource == <modelTree.modelTree object at 0xce2d120>
        # dropped on glpane: target == None. dropped on external app Terminal: target == None.
        # dropped on the HistoryWidget (which does accept it and the text gets into it):
        #   target = <constants.qt.QWidget object at 0xd4c39f0>
        # (PyQt doesn't realize its true class, I guess... but who knows which obj it is anyway)
        # always wantdel = None, always same dragsource, and always no more mouseMove events but one mouseRelease event.
        # ... but things are different after I told the viewport (not just the widget) to accept drops (and dropping on mtree):
        # target = <constants.qt.QWidget object at 0xd4c3f30>, dragsource = <modelTree.modelTree object at 0xce2de10>
        # (guess: this widget is the content widget inside the scrollview; should find out sometime)
        # and better, the icon during the drag is showing the little square-framed +-sign for "copy"!
        # (which means I need to tell the truth about "copy" vs "move" to the QDragObject. I guess that'll work out ok.)

        ###e delete dragobj? i think python refder does that and it might not be needed anyway
        
        return # from do_our_own_drag
    
    def mouseReleaseEvent(self, event):
        # this seems to be normal, whether or not we did our own drag.
        if debug_dragstuff:
            print "drag_and_drop_handler.mouseReleaseEvent, self.started_drag = %r" % self.started_drag
        pass
    def cleanup(self, client = None): ###@@@ call this from above
        "we're done; reset whatever we set outside this object, remove reference cycles, etc"
        assert self.client == None or self.client == client
        self.dragsource = self.client = None
        #e clean statusbar; dragobj if stored here
    pass # end of class drag_and_drop_handler
        

# main widget class

class TreeWidget(TreeView, DebugMenuMixin):
    def __init__(self, parent, win, name = None, columns = ["node tree"], size = (200, 560)):
        """#doc
        creates all columns but only known to work for one column.
        most of its code only bothers trying to support one column.
        """
        self.debug_dragstuff = debug_dragstuff # so TreeView.py can see it [KLUGE! clean up sometime.]
        ###@@@ review all init args & instvars, here vs subclasses
        TreeView.__init__(self, parent, win, name, columns = columns, size = size) # stores self.win

        #e maybe subclass should tell us whether to do this...
        # of the following, old mtree had first only, canvas example has 2nd only, dirview example has both. [050128]
##        self.setAcceptDrops(True) #k apparently not needed; removed 050129 late,
        ## do we still have duplicate-enter bug since then?? ####k ####@@@@
        self.viewport().setAcceptDrops(True)
            #####@@@@@@ btw trying only this one for first time, same as 1st time with this one at all and with scroll signal
        # btw see "dragAutoScroll" property in QScrollView docs. dflt true. that's why we have to accept drops on viewport.

        if debug_dragstuff:
            print "self, and our viewport:",self,self.viewport()

        # debug menu and reload command ###e subclasses need to add reload actions too
        self._init_time = time.asctime() # for debugging; do before DebugMenuMixin._init1
        DebugMenuMixin._init1(self) ###e will this be too early re subclass init actions??

        self.setDefaultRenameAction(QListView.Accept)
            # I don't think this has any effect, now that we're depriving
            # QListView of mouse events, but I'm setting it anyway just in case.
            # The "real version of this" is in our own contentsMousePress... method.
        
        # bruce 050112 zapping most signals, we'll handle the events ourself.
        
        self.connect(self, SIGNAL("itemRenamed(QListViewItem*, int, const QString&)"), self.slot_itemRenamed)

        self.connect(self, SIGNAL("contentsMoving(int, int)"), self.slot_contentsMoving)

        return # from TreeWidget.__init__

    # helper functions
    
    def fix_buttons(self, but, when):
        return fix_buttons_helper(self, but, when)
    
    def makemenu(self, lis):
        return makemenu_helper(self, lis)    

    # mouse event handlers (except for drag & drop, those are farther below)

    # helper variable for knowing if you might be inside an external-source drag, not now in the widget...
    # might need revision to store more than just the last single event of all types together... #####@@@@@ revise, use [050201]
    last_event_type = "none" #k or imitate some other one?
    
    def contentsMouseDoubleClickEvent(self, event):
        "[called by Qt]"
        return self.contentsMousePressEvent(event, dblclick = 1)

    renaming_this_item = None

    def contentsMousePressEvent(self, event, dblclick = 0):
        "[called by Qt, or by our own contentsMouseDoubleClickEvent]"
        self.last_event_type = "press"
        
        # figure out position and item of click (before doing any side effects)
        #e this might be split into a separate routine if it's useful during drag
        
        cpos = event.pos() # this is in contents coords;
            # y=1 is just under column label (which does not scroll with content)
        vpos = self.contentsToViewport(cpos)
        item = self.itemAt(vpos)
        
        # before anything else (except above -- in case this scrolls for some reason),
        # let this click finish an in-place renaming, if there was one.
        # [050131, added protection against item being deleted during renaming]
        self.click_elsewhere_finishes_renaming()

        # now figure out what part of the item (if any) we clicked on,
        # setting 'part' to a constant string describing which part, or None.

        # (someday: if we clicked too far to left or right of visible part of item,
        #  set item = part = None; or we might have new 'part' values
        #  for those positions. #e)

        part = None
        if item:
            # where in the item did we click? relevant Qt things:
            # QListViewItem::width - width of text in col k (without cropping)
            # ... see also PyQt example code, examples3/dirview.py, search for rootIsDecorated
            # Note: if we click to right of col0, we never get here, since item is already None.
            rootIsDecorated = 1
                # more generally: 0 or 1 depending on self.rootIsDecorated()
            header = self.header()
            col0_left_x = header.sectionPos( header.mapToIndex( 0 ))
                # where is this x? by experiment it's always 0 for us. must be left edge of column 0.
                # btw, Qt C++ eg uses mapToActual but there's no such attr when tried here.
            indent = self.treeStepSize() * (item.depth() + rootIsDecorated) + self.itemMargin()
            x_past_openclose = vpos.x() - (col0_left_x + indent)
                # this tells whether we hit the left edge of the icon
                # (by when it's positive), for a very big icon.
            if x_past_openclose > 22: # this cutoff seems ok now; depends on our icon sizes
                part = 'text'
                #e incorrect if we're to the right of the visible text;
                # Qt docs show how to check text width to find out; should use that
                # (also we're not checking for still being in column 0, just assuming that)
            elif x_past_openclose > 2: # this cutoff seems ok (tho it's a bit subjective)
                part = 'icon'
            elif (x_past_openclose > -15) and self.item_isOpenable(item):
                # warning: item.isExpandable() is wrong here; see item_isOpenable docstring
                # this cutoff seems ok; depends on desired size of "click area" around openclose
                part = 'openclose'
            elif vpos.x() >= col0_left_x:
                part = 'left'
            else:
                part = item = None # to the left of column 0 (not currently possible I think)
            pass
        else:
            col0_left_x = x_past_openclose = -1000 # debug kluge
        
        # If this click's data differs from the prior one, this event shouldn't
        # be counted as a double click. Or the same, if too much time passed since prior click,
        # which would mean Qt erred and called this a double click even though its first click
        # went to a different widget (I don't know if Qt can make that mistake).
        # ###e nim feature... and low pri, since Qt seems reasonably conservative
        # about what it calls a double click. ###@@@

        ###e probably store some things here too, in case we'll decide later to start a drag.

        self.clicked( event, vpos, item, part, dblclick)

        self.update_select_mode() # change user-visible mode to selectMolsMode iff necessary
        
        return # from contentsMousePressedEvent

    drag_handler = None # this can be set by selection_click()
    def contentsMouseMoveEvent(self, event): # note: does not yet use or need fix_buttons
        "[overrides QListView method]"
        self.last_event_type = "move"
        # This method might be needed, to prevent QListView's version of it from messing us up,
        # even if it had no body. Anyway, now it does have one.
        # Note that it is not called by Qt for a dragMoveEvent,
        # but it's involved in drag and drop since it decides whether we should start one.
        # WARNING: if it does start one, its subr might not return until that entire drag and drop
        # is finished! There will be recursive event processing during that time.
        if self.drag_handler:
            # this should only be true when some button is down in the event!
            # but in case of weirdness in sequence of events we get from Qt,
            # let's check this ourselves!
            if event.state() & allButtons: # if any mouse button is pressed
                self.drag_handler.mouseMoveEvent( event) #k worry about coords?
        pass
    
    def contentsMouseReleaseEvent(self, event): # note: does not yet use or need fix_buttons
        "[overrides QListView method]"
        self.last_event_type = "release"
        # This method might be needed, to prevent QListView version of it from messing us up,
        # even if it does nothing.
        # (At least, without it, QListView emits its "clicked" signal.)
        # (Many comments for contentsMouseMoveEvent apply to this method as well.)
        if self.drag_handler:
            self.drag_handler.mouseReleaseEvent( event) #k worry about coords?
            self.drag_handler.cleanup(self) # redundant but that's ok ###k
                # (if it already cleaned up, it doesn't know self, and might need to someday, so we pass it in)
            self.drag_handler = None
        pass

    def enterEvent(self, event): ####e #####@@@@@ should this (and Leave) call our drag_handler??
        "[should be called by Qt when mouse enters this widget]"
        self.last_event_type = "enter"
        # [Qt doc says this method is on QWidget; there doesn't seem to be a "contentsEnterEvent".]
        # erase any statusbar messages that might be left over from other widgets
        # (eg advice from Build mode in glpane)
        ###e [should replace it with "our current sbar text", not " " --
        # see comment near a call of history.transient_msg]
        self.statusbar_msg(" ") # bruce 050126; works

    def statusbar_msg(self, msg):
        #e should store the current one for this widget, to share sbar with other widgets;
        # or better, the method we're calling should do that for all widgets (or their parts) in a uniform way
        self.win.history.transient_msg( msg)

    # external update methods
    
    def update_select_mode(self): #bruce 050124; this should become a mode-specific method and be used more generally.
        """This should be called at the end of event handlers which might have
        changed the current internal selection mode (atoms vs chunks),
        to resolve disagreements between that and the visible selection mode
        iff it's one of the Select modes. If the current mode is not one of
        Select Atoms or Select Chunks, this routine has no effect.
           If possible, we leave the visible mode the same (even changing assy.selwhat
        to fit, if nothing is actually selected). But if forced to, by what is
        currently selected, then we change the visible selection mode to fit
        what is actually selected.
        """
        #e should optim: this can call repaintGL redundantly
        # with win.win_update() [bruce 041220; is this still true? 050124]
        # [later: is that a typo meaning paintGL? which is now called gl_update,
        #  and soon will be ok to call redundantly? 050127]
        mode = self.win.glpane.mode
        if not isinstance(mode, selectMode):
            return
        assy = self.assy
        if assy.selatoms and isinstance( mode, selectMolsMode):
            self.win.toolsSelectAtoms() ###k check tool name - this case not needed by treewidget
        elif assy.selmols and isinstance( mode, selectAtomsMode):
            self.win.toolsSelectMolecules()
        else:
            pass # nothing selected -- don't worry about assy.selwhat
        return

    def update_glpane(self):
        self.win.glpane.update()
        ####k will this work already, just making it call paintGL in the next event loop?
        # or must we inval something too??
        # [new comment, 050127:] it seems to work... needs a bit more testing,
        # then can be moved into GLPane as the new implem of gl_update.
    
    # command bindings for clicks on various parts of tree items
    # are hardcoded in the 'clicked' method:
    
    def clicked( self, event, vpos, item, part, dblclick):
        """Called on every mousedown (regardless of mouse buttons / modifier keys).
        Event is the Qt event (not yet passed through fix_buttons).
        vpos is its position in viewport coordinates.
        item is None or a QListViewItem.
        If item, then part is one of ... #doc; otherwise it's None.
        dblclick says whether this should count as a double click
        (note that for some bindings we'll implement, this won't matter).
        (Note that even if dblclick can be determined directly from event,
        caller might have its own opinion, which is what we use, so the flag
        would need to be separately passed anyway.)
        """

        # handle debug menu; canonicalize buttons and modifier keys.
        
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            return
        but = event.stateAfter()
        but = self.fix_buttons(but, 'press')

        # figure out modifier (not stored, just used here & passed to subrs)
        # (option/alt key (mac) aka midButton (other platforms) is used separately below)
        if (but & (shiftButton|cntlButton)) == (shiftButton|cntlButton):
            modifier = 'ShiftCntl'
        elif but & shiftButton:
            modifier = 'Shift'
        elif but & cntlButton:
            modifier = 'Cntl'
        else:
            modifier = None

        # Now check for various user commands, performing the first one that applies,
        # and doing whatever inval or update is needed within the tree widget itself,
        # but not necessarily all needed external updates (some of these are done
        # by our caller).
        
        # handle context menu request.
        
        if but & rightButton:  # regardless of other modifier keys (unlike Mac - change this?)
            # This means we want a context menu, for the given item
            # (regardless of which part of it we clicked on (even openclose or left)!),
            # or for a set of selected items which it's part of
            # (this is detected in following subr), or for no item if item == None.
            # The menu (and the selection-modifying behavior before we put it up) can ignore dblclick.
            # 050126: let's pass it the modifier keys too (more clearly ok for shift
            # than for control, but try both for now).
            pos = event.globalPos()
            self.menuReq( item, pos, modifier) # does all needed updates ###k even in glpane?
            return

        # after this point, treat clicks to left of open/close icon as if on no item.
        # (would it be better to treat them as on open/close, or have a special cmenu
        #  about the parent items, letting you close any of those? ##e)
        if part == 'left':
            part = item = None
        
        # handle open/close toggling. (ignores modifier keys, mouse buttons, dblclick)
        if part == 'openclose':
            # this can only happen for a non-leaf item!
            self.toggle_open(item) # does all needed inval/update/repaint
            return

        # handle in-place editing of the item text, on double-click
        
        #e (someday this might be extended to edit a variant of the text,
        #   if some of it is a fixed label or addendum... to implem that,
        #   just call item.setText first, within the subroutine.)

        if dblclick and part == 'text' and not modifier: # but midButton will also do this, for now
            # presumably the first click selected this item... does this matter?? #k
            # BTW it would not be true if this was a Control-double-click! This is not allowed now.
            # If we wanted to be paranoid, we'd return unless the modkeys and button
            # were identical with the saved prior click... #e
            col = 0
            return self.maybe_beginrename( item, vpos, col)

        # what's left?
        # - selection.
        # - drag-starting, whether for d&d or (saved for later #e) a selection range or rect.
        # - hover behaviors (tooltip with help info or longer name; cmenu) (saved for later. #e)
        #####@@@@ need code to save event info for drag-starting

        # handle selection-click, and/or start of a drag
        # (we can't in general distinguish these until more events come)

##        if dblclick:
##            # Too likely this 2nd click was a mistake -- let the first click handle
##            # it alone. (This only matters for Control-click, which toggles selection,
##            # once the feature of discarding dblclick flag when item/part
##            # changed is implemented.)
##            return

        # after this point, double click acts just like two single clicks
        # (since dblclick flag is ignored).
        
        # if buttons are not what we expect, return now (thus avoiding bad effects
        # from some possible bugs in the above code)
        if (but & allButtons) not in [leftButton, midButton]:
            # (note, this is after fix_buttons, so on Mac this means click or option-click)
            return

        drag_should_copy = but & midButton # standard for Mac; don't know about others
        drag_type = (drag_should_copy and 'copy') or 'move'

        self.selection_click( item, # might be None
                              modifier = modifier,
                              ## group_select_kids = (part == 'icon'), ##k ok? could we use dblclick to mean this??
                              group_select_kids = True, # bruce 050126 after email discussion with Josh
                              permit_drag_type = drag_type,
                              event = event )
            # note: the same selection_click method, called differently,
            # also determines the selection for context menus.
            # It does all needed invals/updates except for update_select_mode.
        
        return # from clicked

    # context menu requests (the menu items themselves are defined by our subclass)
    
    def menuReq(self, item, pos, modifier):
        """Context menu items function handler for the Model Tree View
        [interface is mostly compatible with a related QListView signal,
         but it's no longer called that way; col arg was not used and is now removed;
         pos should be the position to put up the menu, in global coords (event.globalPos).]
        """
        # First, what items should this context menu be about?
        #
        # Here's what the Mac (OS 10.2) Finder does:
        #
        # (btw, for the mac, context menus are asked for by control-click,
        #  vs. right-click on other platforms -- here I'll say context-click:)
        #
        # - If you context-click on a selected item, the menu is about
        # the set of (one or more) selected items, which does not change.
        #
        # - If you context-click on another item, the selection changes to
        # include just the item you clicked on (and you can see that in
        # the selection highlighting), and the menu is about *that* item.
        #
        # - If you click on no item, you get a menu for the window as a whole
        # (whether or not items were selected; if any were, they are unselected).
        #
        # Furthermore, when the menu is about a set of more than one items,
        # the text of its entries makes this clear.
        #
        # (What about other modifier keys which normally modify selection
        # behavior? If you use them, the Mac just does selection and ignores the
        # control key (no context menu). I decided [050126] to instead let them
        # affect selection as normal, then put up the cmenu on the result --
        # especially for Shift, but even for Control which can remove the clicked-
        # on item. (Motivation: for shift, I found myself trying to use it this way,
        # to extend a selection before getting the cmenu, and failing.)
        #
        # Note that this implies: the visible selection always shows you what
        # set of items the context menu is about and will operate on; it's easy
        # to make the menu be about the existing selection, or about no items,
        # or (usually) about any existing single item; the only harder case for
        # the user is when you want a menu about one item, and it and others are
        # selected, in which case, you just click somewhere (to unselect all)
        # and then context-click on the desired item; if instead you don't notice
        # that any other items are selected, you'll notice your mistake when you
        # see the text of the menu entries.
        #
        # BTW, if you click on an "open/close icon" (or to the left of an item),
        # it acts like you clicked on no item, for this purpose. (As of 050124
        # our caller behaves differently in this case too, on purpose I guess...)
        #
        # [refile?] About the menu position and duration:
        # In all cases, the menu top left corner is roughly at the click pos,
        # and the menu disappears immediately on mouseup, whether or not you
        # choose a command from it. [That last part is nim since I don't yet
        # know how to make it happen.]
        #
        # This all seems pretty good, so I will imitate it here. [bruce 050113]

        #e correct item to be None if we were not really on the item acc'd to above?
        # no, let the caller do that, if it needs to be done.
        
        self.selection_click( item, modifier = modifier, group_select_kids = True, permit_drag_type = None)
            # this does all needed invals/updates except update_select_mode
            # bruce 050126: group_select_kids changed to True after discussion with Josh...
            # the same principle applies to context menu ops as to everything else.
            # Also, changed modifier from None to the one passed in.

        nodeset = self.topmost_selected_nodes()
            # topmost_selected_nodes is "more efficient" than selected_nodes,
            # and [050126] equivalent to it now that we're enforcing "selected group
            # implies selected members", assuming the command are coded to operate on
            # all members of groups (when that makes sense).
        menu = self.make_cmenu_for_set( nodeset)
        
        menu.exec_loop(pos) # was menu.popup before 050126
            #e should we care about which item to put where (e.g. popup(pos,1))?
        
        # the menu commands will do their own updates within this widget (and to glpane),
        # but we used exec_loop (which does not return until the menu command has run)
        # so we can do necessary external updates here. (We might later have to change back
        # to menu.popup so we can make the menu go away on mouseup, and then put this update
        # into the menu commands. #e)
        self.update_select_mode() #k is this done redundantly by our caller? if not, move it there?

        return # from menuReq
    
    def make_cmenu_for_set(self, nodeset):
        """Return a context menu (QPopupMenu object #k)
        to show for the given set of (presumably selected) items.
        [Might be overridden by subclasses, but usually it's more convenient
        and better for them to override make_cmenuspec_for_set instead.]
        """
        spec = self.make_cmenuspec_for_set(nodeset)  \
               or self.make_cmenuspec_for_set([])  \
               or [('(empty context menu)',noop,'disabled')]
        return self.makemenu( spec)

    def make_cmenuspec_for_set(self, nodeset):
        """Return a Menu_spec list (of a format suitable for makemenu_helper)
        for a context menu suitable for nodeset, a list of 0 or more selected nodes
        (which includes only the topmost selected nodes, i.e. it includes no
        children of selected nodes even if they are selected).
           Subclasses should override this to provide an actual menu spec.
        The subclass implementation can directly examine the selection status of nodes
        below those in nodeset, if desired, and can assume every node in nodeset is picked,
        and every node not in it or under something in it is not picked.
        [all subclasses should override this]
        """
        return []


    # sets of selected items or nodes
    
    #e [do we also want versions with node arguments, which search only in subtrees?
    #   if so, those should just be (or call) Node methods.]
    
    def selected_nodes(self):
        "return a list of all currently selected nodes (perhaps including both groups and some of their members)"
        # For now, it's ok if this is slow, since it's only used to help make a context menu.
        # (Later we might need a fast version, for each subtree,
        #  so the same info will have to be kept incrementally in the nodes. #e)
        # (We can also imagine wanting these structured as a tree, e.g. for copying... #e)
        res = []
        def func(x):
            if x.picked:
                res.append(x)
        for node in self.topnodes:
            node.apply2all(func)
        return res

    def topmost_selected_nodes(self): #e might be needed by some context menus... how should the makers ask for it?
        "return a list of all selected nodes as seen by apply2picked, i.e. without looking inside selected Groups"
        res = []
        def func(x):
            res.append(x)
        for node in self.topnodes:
            node.apply2picked(func)
        return res

    
    # selection logic

    def pick( self, item, group_select_kids = True ):
        "select the given item (actually the node or group it shows)"
        if group_select_kids:
            item.object.pick()
        else:
            item.object.pick_top()
            # as of 050131, this is: illegal (since it violates an invariant),
            # incorrectly implemented (since it doesn't do leaf-specific pick funcs,
            # though this could probably be easily fixed just as I'll fix unpick_top),
            # and never called (since group_select_kids is always True).
        return

    def unpick( self, item, group_select_kids = True ):
        "deselect the given item (actually the node or group it shows)"
        if group_select_kids:
            item.object.unpick()
        else:
            item.object.unpick_top()
        return

    def unpick_all(self):
        for node in self.topnodes:
            node.unpick()
        
    def selection_click(self, item, _guard_ = 67548, \
                        group_select_kids = True, modifier = None, permit_drag_type = None, event = None):
        """Perform the ordinary selection-modifying behavior for one click on this item (might be None).
        Assume the modifier keys for this click were as given in modifier, for purposes of selection or drag(??) semantics.
        We immediately modify the set of selected items -- changing the selection state of their Nodes (node.picked),
        updating tree-item highlighting (but not anything else in the application -- those will be updated when Qt resumes
         event processing after we return from handling this click ###@@@ so we need to inval the glpane to make that work!
         until then, it won't update til... when? the next paintGL call. hmm. I guess we just have to fix this now.).
    
        If permit_drag_type is not None, this click might become the start of a drag of the same set of items it
        causes to be selected; but this routine only sets some instance variables to help a mouse move method decide whether
        to do that. The value of permit_drag_type should be 'move' or 'copy' according to which type of drag should be done
        if it's done within this widget. (If the drop occurs outside this widget, ... #doc)
        
        #doc elsewhere: for a single plain click on a selected item, this should not unselect the other items!
        # at least finder doesn't (for sel or starting a drag)
        # and we need it to not do that for this use as well.
        """
        assert _guard_ == 67548, "you passed too many positional arguments to this function!"
        
        ###@@@ maybe some of this (or its callers) belongs in the subclass?
        
        # Note: the following behavior uses Shift and Control sort of like the
        # GLPane (and original modelTree) do, but in some ways imitates the Mac
        # and/or the QListView behavior; in general the Mac behavior is probably
        # better (IMHO) and maybe we should imitate it more. (For example, I'm
        # very skeptical of the goodness of applying pick or unpick to entire
        # subtrees as the default behavior; for now I refrained from changing
        # that, but added a new mod-key-pair ShiftCntl to permit defeating it.)
        # [bruce 050124]

        #e This needs some way to warn the user of what happens in subtrees
        # they can't see (when nodes are openable but closed, or even just with
        # their kids scrolled out of sight). Probably best is to always show
        # sel state of kids in some manner, right inside each Group's item. #e

        # warning: in future the pick and unpick methods we're calling here
        # might call incremental updaters back in this module or treeview!

        # [bruce 050128 adding drag & drop support]
        if self.drag_handler:
            if debug_dragstuff:
                print "should never happen: selection_click finds old drag_handler to dispose of"
            try:
                self.drag_handler.cleanup(self)
            except:
                print_compact_traceback("self.drag_handler.cleanup(self): ")
            pass
        self.drag_handler = None # might be set to an appropriate drag_handler below
        
##        # store info about this click for subsequent mouseMoveEvents, so they can
##        # decide whether to start a drag of some kind (for extending a selection, drag & drop, etc).
##        #e not clear if it's cleaner to decide that right here, or when this info is used;
##        # someday this self.drag_info object might be a drag_handler with its own event methods;
##        # we'd then decide on its class here, so try to decide now.
##        if item and not modifier:
##            # subsequent mouseMoves might start a drag and drop.
##            self.drag_info = drag_and_drop_handler( 
##        self.drag_info = attrholder()
##        self.drag_info.permit_drag_type = permit_drag_type # whether or not it's None
        
        ###DOC - some comments below are WRONG, they're from before group_select_kids option was honored ####@@@@

        if modifier == 'ShiftCntl': # bruce 050124 new behavior [or use Option key? #e]
            # toggle the sel state of the clicked item ONLY (no effect on members);
            # noop if no item.
            if item:
                if item.object.picked:
                    self.unpick( item, group_select_kids = group_select_kids)
                else:
                    self.pick( item, group_select_kids = group_select_kids)
        elif modifier == 'Cntl':
            # unselect the clicked item (and all its members); noop if no item.
            if item:
                self.unpick( item, group_select_kids = group_select_kids)
        elif modifier == 'Shift':
            # Mac would select a range... but I will just add to the selection,
            # for now (this item and all its members); noop for no item.
            ##e in future: create a drag_selection_handler, which behaves differently
            # depending on modifiers (since we'll also do it for Cntl
            # and maybe even for ShiftCntl) and on whether item is None.
            if item:
                # whether or not item.object.picked -- this matters
                # for groups with not all picked contents!
                self.pick( item, group_select_kids = group_select_kids)
        else:
            # no modifier (among shift and control anyway)...
            if item:
                if item.object.picked:
                    # must be noop when item already picked, in case we're
                    # starting a drag of multiple items
                    pass
                else:
                    # deselect all items except this one
                    self.unpick_all()
                        ###e should this only be done within the "current space",
                        # imitating separate focus for PartGroup subtrees?
                        # same Q for how far group_select_kids (ie Group.pick) descends?
                        # Not sure.
                    self.pick( item, group_select_kids = group_select_kids)
                # this click might later turn out to be starting a drag
                # of the now-selected items:
                if permit_drag_type:
                    self.drag_handler = self.drag_and_drop_handler( permit_drag_type, self.topmost_selected_nodes(), event)
                    # that method will create an object to handle the drag, pass it self,
                    # tell it how to callback to self in some ways when it starts the drag
            else:
                # no item
                self.unpick_all()
        # that should do it!
        
        ##e only sometimes do the following? have our own inval flags for these?
        ## do in subsets? do first on items changed above?
        ## [latter might be needed soon, for speed of visual feedback]
        self.update_selection_highlighting()
        self.update_glpane()

        return # from selection_click


    # selection dragging methods [#e not yet implemented] would go here

    
    # drag and drop event handlers and helpers
    # (some might be relevant whether the dragsource is self or something external)

    def drag_and_drop_handler( self, permit_drag_type, nodes, click_event):
        "this instance's way of constructing a drag_and_drop_handler with itself as dragsource"
        listview = self
        dragsource = listview
        client = listview
        return drag_and_drop_handler( client, dragsource, permit_drag_type, nodes, click_event)
            # in the current imperfect API, this handler knows about the next few special methods
            # in this object, and knows that "client" is this object, so it can call them.
            # (except that internally it might still sometimes use dragsource when it should use client,
            # since those are always the same for now.) [050129]

    def get_pixmap_for_dragging_nodes(self, drag_type, nodes):
        ####@@@@ call this from advise_starting_drag_and_get_dragobj (not from handler )
        
        #e [also put the drag-text-making code in another method near here? or even the dragobj maker?
        # or even the decision of what to do when the motion is large enough (ie let drag_handler role be only to notice that,
        # not to do whatever should be done at that point? as if its role was to filter our events into higher level ones
        # where one of them would be enoughMotionToStartADragEvent?] ###e yes, lots of cleanup is possible here...
        """Our current drag_handler can call this to ask us for a nice-looking pixmap
        representing this drag_type of these nodes,
        to put into its QDragObject as a custom pixmap.
        If we're not yet sure how to make one, we can just return None.
        """
        return None

    current_drag_type = None
    current_drag_nodes = []
    def advise_starting_drag_and_get_dragobj(self, drag_type, nodes):
        """Our current drag_handler can call this to advise us
        that it started a drag of given type on given nodes,
        and that we should highlight the original nodes to indicate this,
        and that if we get any drop-related events (e.g. dragEnter, dragMove, dragLeave)
        that we should also highlight the possible drop points
        (assuming the potential drop is this drag it started).
            Also it wants a QDragObject from us, so we have to make one and return it!
        (It will then start the drag on it in the right way... unless we decide
        to move that code from it to here, as well. #e)
        """
        #####@@@@@ moved from caller (next 2 paras), works here yet?
        
        # make up some text to be dragged in case the custom pixmap doesn't work or is nim
        ## text = "x\n%s %d item(s)" % ... # this results in appearance (w/o custom pixmap) of "x move 5 items..."
        dragobj_text = "%s %d item(s)" % (drag_type, len(nodes)) # e.g. "copy 5 item(s)"
        dragobj_text = fix_plurals(dragobj_text) # e.g. "copy 5 items" or "move 1 item" -- no "ing" to keep it as short as possible
        ## works but not very useful: for node in self.nodes: dragobj_text += "\n  %s" % node.name
        ####@@@@ use the above to verify nodes are in the right order! and might be more useful for history or sbar...

        # make the dragobj [move sbar code above this? also add a history greenmsg? ###e]
        dragsource = self
        dragobj = QTextDrag( dragobj_text, dragsource)
            # \n and \r were each turned to \n, \n\r gave two \ns - even in "od -c"; as processed through Terminal
        pixmap = self.get_pixmap_for_dragging_nodes(drag_type, nodes) #e make this work! now it returns None.
        if pixmap:
            dragobj.setPixmap(pixmap)

        # store data to advise potential drop-points about what might drop on them
        # (in case it affects their highlighting, motion, acceptance of drop...)
        self.current_drag_type = drag_type
        self.current_drag_nodes = nodes
        #####@@@@@ do the highlighting of original items...
        # btw should the sbar be done from here as well? probably yes.
        # stub for all of that:
        ing_dict = { "move":"moving", "copy":"copying" }
        whatting = ing_dict[ drag_type] # moving or copying?
        sbar_text = fix_plurals( "%s %d item(s)" % (whatting, len(nodes)) ) # not quite the same as the text for the QDragObject
        desc = sbar_text + " [not yet implemented]"
        # now everything we do with desc is wrong, needs revision, but might work for now [050131]:
        # stuff it into drag_handler (kluge, bad boundary) for use when we ask it this during update_drop_point_highlighting: 
        self.drag_handler.describe_drag = desc
        # early warning to the statusbar: probably ok, tho will normally be overwritten soon (with itself)
        self.statusbar_msg( desc + " <this suffix should not be seen>" ) ###e remove suffix when flickers
        if debug_dragstuff and "what you want" == "something that looks really silly and annoying":
            # also use whatting in a transient node prefix, see below
            for node in nodes:
                item = self.nodeItem(node)
                    #e rename? I wrongly guessed it was called self.item_for_node(node)
                col = 0
                item.setText( col, "%s: %s" % (whatting, node.name))
                item.repaint() #e in the non-stub code we'll probably repaint it
                    # in a different way so it looks dim, italic, colored, or whatever --
                    # for copy, not much or at all different (esp if it still looks selected, that should be enough)
                    #   (so if this stub code gets released, change it to not bother doing this at all for copy) #####@@@@@
                    # but for move, these original nodes should look "almost missing" but with names still readable
                    # (whereas this prefix makes them less readable since more likely truncated by the right edge of the widget)
                    # (but this is at least useful for debugging, i hope! unless it itself has to be too much debugged....)
        return dragobj
    
    def advise_ended_drag(self):#####@@@@@ call this
        "we call this ourselves - it does not do the operation on the nodes, but it resets variables" 
        ###e should it also undo any highlighting of original nodes?
        # or let caller do it? or just let next update do it? not sure...
        self.current_drag_type = None
        self.current_drag_nodes = []
        return

    # About tracking the position of a drag from outside (contentsDragEnter/Move/Leave/Drop):
    # we don't track a pos from dragEnter since we're not sure it supplies one and since
    # the "duplicate Enter bug" worries me. We track the pos from contentsDragMove, given
    # in contents coords, but only valid at the then-current contents position
    # (and until the next dragMove or dragLeave). When it comes we have to record
    # what it was and what the contents position was. And we track changing contents
    # positions, reported separately during a scroll (most importantly, during an
    # autoscroll done by Qt during the drag event). All these events call a common
    # updater for drop-point highlighting, update_drop_point_highlighting, which combines
    # all this recorded info to know where to highlight (and remembers where it drew last
    # time so it can un-highlight). It should only be called during a drag, and it can ask
    # the listview what item is under various points near the drag-point.

    # This is the last reported scroll position (topleft contents pos which is visible
    # according to scrolling), reported by the contentsMoving signal.
    last_scrollpos = (0,0)

    # This is the last *reported* dragMoveEvent position, as a pair (x,y) in contents coords,
    # or None when there's been a dragLeave since then, or (equivalently) if scrolling occurred
    # (presumably autoscrolling during a drag) and we're disabling drops during scrolling.
    last_dragMove_cpos = None

    # And this is the value of scrollpos at the same time we set self.last_dragMove_cpos.
    # (Its value when last_dragMove_cpos is None is undefined, i.e. should not be cared about.)
    last_dragMove_scrollpos = (0,0)

    # And this is the last "ok flag" for a drag enter or move event, set False by a dragLeave;
    # not sure if this is needed, but maybe it's anded with whether last_dragMove_cpos is set... #doc
    last_dragMove_ok = False
    
    def contentsDragEnterEvent(self, event):
        self.last_event_type = "dragenter"
        # warning: for unknown reasons, this is sometimes called twice when i'd expect it to be called once.
##        if debug_dragstuff:
##            print_compact_stack("contentsDragEnterEvent stack (fyi): ")
        ok = QTextDrag.canDecode(event) # this code is duplicated elsewhere
        event.accept(ok)
        self.last_dragMove_ok = ok
        # the Qt docs warn that actually looking at the text might be slow (requires talking to the external app
        # if it came from one), so using the text to find out whether the source is external would not be a good idea.
        # For a dragMoveEvent, it subclasses DropEvent and thus might have a "source" we can look at... don't know.
##        if debug_dragstuff:
##            print "enter: ok = %r" % ok
        #e maybe do same highlighting as dragmove... but not for now,
        # since we have that dup-enter bug that the canvas had
        return

    def dragEnterEvent(self,event):
        self.last_event_type = "dragenter" #k ok to do this here and for contentsDragEnter both??
        if debug_dragstuff:
            print "dragEnterEvent happened too! SHOULD NOT HAPPEN" # unless we are not accepting drops on the viewport

    # To highlight the correct items/gaps under potential drop-points during drag and drop,
    # we need to be told when autoscrolling occurs, since Qt neglects to send us new dragMove events
    # when the global cursor position doesn't change, even though the position within the contents
    # does change due to Qt's own autoscrolling!
##    do_update_drop_point_highlighting_in_next_viewportPaintEvent = False
    def slot_contentsMoving(self, x, y):
        """[Called by the Qt signal whose doc says:
        "This signal is emitted just before the contents are moved
         to position (x, y)." But this wording is misleading --
        it's actually the position of the topleft visible part of the
        contents (in contents coords), as determined by the scrollbars.
        """
        ## want one of these?? self.last_event_type = "slot_contentsMoving"
        self.last_scrollpos = (x,y)
        
        # Now, in case we're in a drag (after a dragMove), reset the drag position
        # to None, just as a dragLeave would do, so as to disable a drop
        # (and drop-point highlighting) during autoscrolling. (Note that any
        # scrolling during a drag must be autoscrolling -- user is not touching
        # scrollbar, and tree structure should not be changing.)
        #   For commentary about why this is a feature not a bug,
        # even though it was motivated by the difficulty of doing the drop-point
        # highlighting properly during autoscroll (and for the details of that
        # difficulty and ideas for solving it), see removed comments in this method
        # dated 050130 (in rev 1.21 in cvs).
        
        # The following code is similar in dragLeave and Drop and slot_contentsMoving,
        # not sure if identical:
        self.last_dragMove_ok = False # not needed right now, but might matter
            # after the next dragEnter but before the next dragMove
        self.last_dragMove_cpos = None
        # The following statusbar_msg suffix is the only way users are told
        # why the drop-point highlighting disappeared, or what to do about it.
        # It must be short but clear!
        self.drop_disabled_because = "drop disabled by autoscroll, until mouse moves" #k still too long??
        self.update_drop_point_highlighting()
        return
    
    def contentsDragMoveEvent(self, event):
        self.last_event_type = "dragmove"
        # we can re-accept it (they suggest letting this depend on event.pos())...
        # don't know if we need to, but all their doc examples do... so we will.
        ok = QTextDrag.canDecode(event) # this code is duplicated elsewhere
        event.accept(ok)
            # note: using an "empty rect" arg did not cause "continuous dragMove events"
            # like the Qt docs promised it would... for details, see comments near here
            # in cvs rev. 1.19 [committed 050129] of this file. (Maybe some dragMove
            # events were coming but not contentDragMove? I doubt it but who knows.)
        self.last_dragMove_ok = ok
        ## gpos = event.globalPos() # AttributeError: globalPos
        pos = event.pos()
##        if debug_dragstuff:
##            print "drag move pos:",tupleFromQPoint(pos) # this is in contents area coords. it autoscrolls but is not resent then!
        self.last_dragMove_cpos = tupleFromQPoint(pos)
        self.last_dragMove_scrollpos = self.last_scrollpos
        self.update_drop_point_highlighting() # call whether or not self.last_dragMove_ok in case it just changed to False somehow
        return
        
    def contentsDragLeaveEvent(self, event):
        self.last_event_type = "dragleave"
##        if debug_dragstuff:
##            print "contentsDragLeaveEvent, event == %r" % event
        # the following code is similar in dragLeave and Drop and slot_contentsMoving,
        # not sure if identical
        self.last_dragMove_ok = False # not needed right now, but might matter
            # after the next dragEnter but before the next dragMove
        self.last_dragMove_cpos = None
        self.drop_disabled_because = "(drop outside model tree is not supported)" # maybe no need for text like this? ##e
        self.update_drop_point_highlighting()
        return
    
    def dragLeaveEvent(self, event):
        self.last_event_type = "dragleave" ###k ok here too?
        if debug_dragstuff:
            print "dragLeaveEvent, event == %r, SHOULD NOT HAPPEN" % event
        #e remove highlighting from dragmove

    true_dragMove_cpos = None
    drop_disabled_because = ""
    
    def update_drop_point_highlighting(self, undo_only = False):
        #k undo_only might not be needed once a clipping issue is solved -- see call that uses/used it, comments near it
        """###OBS - some of this is wrong since we no longer use viewportPaintEvent as much -- 050131.
           Maintain highlighting of possible drop points, which should exist whenever
        self.last_dragMove_cpos and self.last_dragMove_ok, based on a drag position
        determined by several last_xxx variables as explained in a comment near them.
        Do new highlighting and undo old highlighting, by direct drawing and/or
        invalidation (QWidget.update).
           Note that some of the same drawing also needs
        to be done by our custom viewportPaintEvent on top of whatever our superclass
        would draw, even if we draw in the same place here -- this routine's drawing
        works for things already visible, viewportPaintEvent's for things uncovered
        by scrolling, and we're not always sure which is which, nor would it be practical
        to fully divide the work even if we were.
           So, this routine records what drawing needs to happen (of the "do" type, not
        the "undo" type), and calls a common routine to do it, also called by
        viewportPaintEvent if its rect might overlap that drawing (which is always
        small in vertical extent, since near the drop point -- at least for now).
           But for "undo" drawing it's different... I guess viewportPaintEvent needn't do
        any "undo drawing" since what its super method draws is "fully undone" already.
           Oh, one more thing -- the "original nodes" also look different (during a move),
        and this is "do" drawing which changes less often, is done even when the dragged
        point is outside the widget, and has a large vertical extent -- so don't do it
        in this routine! It too needs doing when it happens and in viewportPaintEvent,
        and undoing when that happens (but not in viewportPaintEvent), but is done by some
        other routine. ####@@@@ write it!
           If in the future we highlight all inactive drop points as well as the one active
        one, that too (the inactive ones) would be done separately for the same reasons.
        """
        assert not undo_only
        undo_true_dragMove_cpos = self.true_dragMove_cpos # undo whatever was done for this pos
            # that only works if we're sure the items have not moved,
            # otherwise we'd need to record not just this position
            # but whatever drawing we did due to it; should be ok for now
        if self.last_dragMove_cpos and self.last_dragMove_ok:
            # some drop-point highlighting is wanted; figure out where.
            # if we felt like importing Numeric (and even VQT) we could do something like this:
            ## correction = self.last_scrollpos - self.last_dragMove_scrollpos
            ## self.true_dragMove_cpos = self.last_dragMove_cpos + correction
            # but instead:
            correction = pair_minus( self.last_scrollpos, self.last_dragMove_scrollpos )
            self.true_dragMove_cpos = pair_plus( self.last_dragMove_cpos, correction )
            substatus = "" # use "" since flicker on/off is better than flicker between two texts!
##            if debug_dragstuff:
##                print "correction = %d - %d = %d; true = lastmovecpos %d + correction = %d" % (
##                    self.last_scrollpos[1], self.last_dragMove_scrollpos[1], correction[1],
##                    self.last_dragMove_cpos[1], self.true_dragMove_cpos[1] )
        else:
            self.true_dragMove_cpos = None
            ####@@@@ the following is only valid if a dragLeave (I think) was the last event we had in the app! (or so)
            # now, this shows up even for a "copy" event which moves the scrollbar! #####@@@@@
            # use self.last_event_type somehow (revise it so we can)#####@@@@@
            substatus = " -- " + self.drop_disabled_because
                # substatus is independent of whether drag is initiated in this widget
        # now figure out where the drag came from and what it means, to mention in statsubar
        if self.drag_handler:
            # if this exists, then it should be the source... or this message will report that bug
            desc = self.drag_handler.describe_your_drag_and_drop()
        else:
            desc = "drag from outside tree widget" #e subclass should supply widget description
        self.statusbar_msg( desc + substatus )

        # now it's time to figure out where we are, if anywhere, and what drop points we would hit

        listview = self
        cpos = self.true_dragMove_cpos # None or a tuple
        if cpos:
            x,y = cpos
            ## not needed: item = self.itemAtCposXY(x,y) # item you might want to drop on directly, or None
            # How to detect the mouse pointing at a gap:
            # a gap lies between (the rows of) adjacent items-or-None (but never both None);
            # the items touch so the gap (as a mouse-target) overlaps each one by some amount;
            # if we imagine it extends y_up into top item and y_down into bottom item,
            # then it can be looked for by letting mouse drag around a dual-point AFM :-)
            # whose points are that much down and up (in reverse order) from its own position...
            # that is, look for a top item y_down above your pos, and for a bottom one y_up below your pos.
            # Usually y_down == y_up, but that's no excuse to fail to reverse them in this code!
            # In fact, to support hysteresis and/or mouse-hotspot-corrections
            # we might make them vary a bit, per gap,
            # and then they'll differ when looked for above and below one item -- different gaps...
            # BTW, the item found above tells us (mostly) what two gaps to look for...
            # not if it's None, though...
            #    For now, to simplify this, just look a fixed amount up or down,
            # and see one item in both places (then drop onto that item, regardless of x I think? not sure)
            # or see two items-or-Nones (only bottom one can be None, since we leave no empty space at top --
            # not true, the top point could look above the top item, but we don't permit a drop there).
            # Then you want to drop between them; x position determines desired depth (closest icon-column-
            # centerline of permissible drop-depths), can be as left as either item (above or below gap)
            # or as right as either item or as hypothetical children of top item if that one is openable.
            # (No ambiguity if that matches depth of bottom item! And useful for becoming top child of closed
            # items, since drop directly on item makes you bottom child. Sbar message should say where you'd drop. ###e)

            # Find the items-or-Nones above and below the gap (if same, you're over that item, not a gap):
            ###e should change from hardcoded constants below... sorry, the deadline approaches...
            top = self.itemAtCposXY(x,y-3) #e these constants will probably need subjective adjustment, maybe hysteresis
            bottom = self.itemAtCposXY(x,y+3)
            return #####@@@@@
            if top == bottom:
                if top:
                    # dropping inside item top
                    where = "dropping inside item %r" % top.object.name
                else:
                    # dropping into empty space
                    where = "dropping into empty space"
            elif not top:
                # too high to drop (it's above all items, at least for now with no big gaps in the display)
                where = "too high, above highest item %r" % bottom.object.name
            else:
                # dropping into the gap between items top (not None) and bottom (maybe None);
                # use x position to figure out desired depth
                where = "somewhere in gap between items %r and %r..." % (top.object.name, bottom.object.name)
                dtop = self.itemDepth(top) # in units of integers not pixels?? or floats but where 1.0 is the level-change in x?
                    # or ints but where the level-change is known to us??
                dbottom = self.itemDepth(bottom)
                dmouse = self.itemDepthForCposX(x) # depth of the mouse itself (float, 1.0 means "size of one level")
                mindepth = min(dtop, dbottom) # leftmost possible drop-point (larger depths are innermore ie to the right)
                maxdepth = max(dtop, bottom) # rightmost, not yet counting "new child of top"
                maybe_new_child_of_top = False # change below
                if 0 and self.isItemOpenable(top): #### 0 in case attrname is wrong, i need to commit now #####@@@@@ where i am is here
                    maybe_new_child_of_top = True ### 050201 433pm
                    dtop_child = dtop + 1
                    if dtop_child > xxx: pass ####
                pass ####@@@@@ stubbly here...

        listview.itemAt
        ###

        # now undo old drawing and do new drawing. #####@@@@@
        
        if not debug_dragstuff: return  #e remove soon, when next stuff is not a stub
        
        ###stub for debugging: draw white to undo and blue to do, of a symbol just showing where this point is.
        # always undo first, in case there's an overlap! (might never happen once we're doing real highlighting, not sure)
        # for real highlighting some of it will be redrawing of items in different ways, instead of new drawing.
        painter = QPainter(self.viewport(), True) # this might not end up drawing in enough places... draws in viewport coords; False###e
        # fyi: the following method knows about true_dragMove_cpos perhaps being None, draws nothing in that case
        self.draw_stubsymbol_at_cpos_in_viewport(painter, undo_true_dragMove_cpos, color = Qt.white, blot = 1) #e should use backgroundcolor from a palette
        if not undo_only:
            self.draw_stubsymbol_at_cpos_in_viewport(painter, self.true_dragMove_cpos, color = Qt.blue) #e should use highlight color from a palette

    def itemDepth(self,item):
        return 2.0 #stub #####@@@@@
    def itemAtCposXY(self, x, y):
        ####WRONG, does not check for too far to left or right, on openclose, etc...
        ### USE AS STUB but then split out the code from contentsMousePress
        # and use that instead of direct itemAt. #####@@@@@
        #e also, for DND or seldrag we might want both the item-row and whether we're really in it... for now, assume not...
        # but worry about where user will point mouse for gaps if i draw an arrow to the left of the items pointing to them,
        # or a circle just outside the icon level...
        vpos = self.contentsToViewport(QPoint(x,y)) # or QPointFromTuple((x,y)) #k or i bet QPoint could be left out entirely
        return self.itemAt(vpos) # might be None
    
    def draw_stubsymbol_at_cpos_in_viewport(self, painter, cpos, color = Qt.red, blot = False):
        if cpos == None:
            # warning: other code in this file just says "if cpos",
            # so if we switch to Numeric, watch out for (0,0) being false!
            return
        cx,cy = cpos
        dx,dy = self.last_scrollpos
        x = cx - dx
        y = cy - dy
##        if debug_dragstuff:
##            print "drawing (white or blue or ...) at vpos:",x,y
        if not blot:
            self.drawbluething( painter, (x,y), color)
        else:
            # blotbluething doesn't work, so just be quick and dirty here:
##            for i in [-1,0,+1]:
##                for j in [-1,0,1]:
##                    self.drawbluething( painter, (x+i,y+j), color)
            self.drawbluething( painter, (x,y), color) #050130 9:33pm #####@@@@@
        return

    # this debug func overrides the one in TreeView so I can extend it here
    def drawbluething(self, painter, pos = (0,0), color = Qt.blue): # bruce 050110 taken from my local canvas_b2.py
        "[for debugging] draw a recognizable symbol in the given QPainter, at given position, of given color"
        p = painter # caller should have called begin on the widget, assuming that works
        p.setPen(QPen(color, 3)) # 3 is pen thickness
        w,h = 100,9 # bbox rect size of what we draw (i think)
        x,y = pos # topleft of what we draw
        p.drawEllipse(x,y,h,h)
        fudge_up = 1 # 1 for h = 9, 2 for h = 10
        p.drawLine(x+h, y+h/2 - fudge_up, x+w, y+h/2 - fudge_up)

##    def blotbluething(self, painter, pos = (0,0), color = Qt.white): ###k this doesn't work, why?
##        "[for debugging] blot out what drawbluething drew, with 1 pixel margin as well"
##        p = painter # caller should have called begin on the widget, assuming that works
##        p.setPen(QPen(color, 6)) # 6 is pen thickness, at least half of 11, our height in the end, below
##        w,h = 100,9 # bbox rect size of what we draw (i think)
##        w += 1 # correct bug in above
##        w += 2; h += 2 # margin
##        x,y = pos # topleft of what we draw
##        x -= 1; y -= 1 # margin
##        p.drawRect(x,y,h,h)

    def viewportPaintEvent(self, event):
        "[overrides TreeView.viewportPaintEvent]"
##        if debug_dragstuff:
##            print "TreeWidget.viewportPaintEvent"
        super = TreeView # the class, not the module
        res = super.viewportPaintEvent(self, event)
        cpos = self.true_dragMove_cpos
        if cpos and debug_dragstuff:
            painter = QPainter(self.viewport(), True)
            self.draw_stubsymbol_at_cpos_in_viewport(painter, cpos, color = Qt.green) # i think we're depending on clip to event.rect()
                # should use highlightcolor; for debug use diff color than when drawn in the other place that can draw this
            if debug_dragstuff:
                print "drew in green"
##        if self.do_update_drop_point_highlighting_in_next_viewportPaintEvent: ###@@@ 050130
##            self.do_update_drop_point_highlighting_in_next_viewportPaintEvent = False
##            self.update_drop_point_highlighting()
        return res
    
        #e change highlighting/indicating of possible drop points (gaps or items) (e.g. darken icons of items)
        #e should we also change whether we accept the drop or not based on where it is? [i think not. surely not for alpha.]
        # - do we want to?
        # - does it affect the icon appearance? if so will this mislead users into thinking entire widget refuses?
        # - does it work, semantically?
        # ...also is it possible to actually examine the text being offered, to decide whether to accept it?
        # (that way we can tell if it's from inside or outside this app. this would not be needed for alpha.)
        
        # [later solved that: get a contentsMoving signal.]
        # so i'd better use the advice above about returning the empty rect!
##        # following is not right, we want to try doing this inside the contents.
##        listview = self
##        wpos = listview.mapFromGlobal(gpos)

    def junk_copied_from_above():
        unclipped = True # True works, can draw over the QListView column label and the scrollbar. False draws nothing!
            # So we have to use True for now, though it's "dangerous" in terms of what we might mess up.
            ##e probably better (and not hard) to define our own clipper and clip to that...
            #e we could also put this painter inside the drawing area, would that work better? try it sometime.
        painter = QPainter(listview, unclipped)
        gpos = event.globalPos()
        wpos = listview.mapFromGlobal(gpos)
        x,y=wpos.x(),wpos.y() # this works, scrolled or not, at least with unclipped = True
        listview.drawbluething( painter, (x,y)) # guess: this wants viewport coords (ie those of widget). yes.
        listview.update() #k needed?
        
    def contentsDropEvent(self, event):
        self.last_event_type = "drop"
        if debug_dragstuff:
            print "contentsDropEvent, event == %r" % event

        # should we disable the drag_handler, or rely on mouseRelease to do that? ###e ####@@@@
        
        # We might be inside autoscroll, with drop-point highlighting disabled...
        # detectable by self.last_dragMove_cpos == None. In that case we should
        # refuse the drop. Ideally we'd report what the drop would have been into...
        # not for now since computing that is nim even for an accepted drop! ###e revisit
        
        disabled = (self.last_dragMove_cpos == None) # used more than once below

        # the following code is similar in dragLeave and Drop, not sure if identical
        self.last_dragMove_ok = False # not needed right now, but might matter
            # after the next dragEnter but before the next dragMove
        self.last_dragMove_cpos = None
        if disabled:
            self.drop_disabled_because = "drop ignored since in autoscroll" # will be zapped by redmsg anyway
        else:
            self.drop_disabled_because = "<bug if you see this>" # only shows up when disabled... clean this up!
                #####@@@@@ this comes out when you click and scroll, e.g. if copy in cmenu extends contents height... not in any drag
        self.update_drop_point_highlighting()

        if disabled:
            self.redmsg( "drop refused due to autoscrolling (and no subsequent mouse motion) -- too dangerous.")
            event.ignore()
            return
        
        oktext = QTextDrag.canDecode(event)
            #e in future even this part (choice of dropped data type to look for)
            # should be delegated to the current drag_handler if it recognizes it
        if oktext:
            if debug_dragstuff:
                print "accepting text"
            str1 = QString() # see dropsite.py in examples3
            res = QTextDrag.decode(event, str1)
            text = str(str1)
            if debug_dragstuff:
                print "got this res and text: %r, %r" % (res,text) # guess: from finder it will be filename [was url i think]
            event.accept(True)
            # up to this point (accepting dropped text) we'll behave the same whether or not it was *our* dropped object.
            # (except for the highlighting done by DragMove, which ideally would distinguish that according to which items
            #  want to accept drops from inside vs outside this widget. But that distinction can be post-Alpha.)
            # Now that we accepted the drop, to handle it properly we do need to know whether it was ours.
            # If it was ours, it was created by a presently active drag_handler
            # (which should be still inside its start_a_drag method), so if we have one, just ask it.
            # (Someday we might think it's wise to do this earlier so it had a chance to reject the drop.)
            if self.drag_handler:
                messed_up_retval = self.drag_handler.one_of_yours_Q( event, text) # False, or a tuple of useful data #e revise!
                if messed_up_retval:
                    # return "true" whether or not it accepts the drag! (once it has that choice) (i mean return "recognized"
                    # not just "accepted". it could return (recognized, type, nodes) with type==None meaning rejected.
                    # when it always does that we can change the call to immediately assign the reval to the tuple, if we want.
                    recognized_Q, drag_type, nodes = messed_up_retval
                    # but for now we can only handle the following:
                    assert recognized_Q == True
                    if debug_dragstuff:
                        # because recognized_Q:
                        print "our drag handler recognized this drop as one it had generated"
                        if drag_type:
                            print "our drag handler accepted this drop"
                    assert drag_type in ['copy','move'] # for now it can't reject it; to do that it would return None
                        # (sorry for the mess, the deadline approaches)
                    # and nodes is a list of 1 or more nodes, and it's been our job to highlight the originals specially too,
                    # which means we already knew this list of nodes
                    assert nodes == nodes #e i mean the ones we already knew about
                    # and (unlike some other comments' claims nearby)
                    # it's our job to now do the operation.
                    if debug_dragstuff:
                        print "NOT IMPLEMENTED: do the op on these dragged nodes:",nodes
                        self.redmsg("NIM: do the op %r on %d nodes, first/last names %r, %r" % (
                            drag_type, len(nodes), nodes[0].name, nodes[-1].name ))
##                    do the op
##                    } #####@@@@@@
                    ### OBS WRONG COMMENT:
                    # not only that, it did all the work needed by it (since it, more than us, knew what it all meant...);
                    # and it even did all the updates in this widget, required by whatever it did to our state --
                    # even though some highlighting is set up here but should be undone by it? not sure about that yet!
                    # (maybe we do the graphics and it does the semantics... but the changes need to be coordinated)
                    # in other words the interaction between this and the handler is not clear -- they are like parts of one object
                    # and maybe it's even a bit weird to separate them... we'll see. Anyway, sounds like we're done.
                    return
                pass
            # well, that guy didn't want it (or didn't exist) so it's our problem. That means the drop is from another app.
            # (or another widget in this app.)
            # someday we'll handle these and that will be very useful...
            # for now just acknowledge that we got this data and what it contained
            # (in a way which might sometimes be marginally useful, and seems non-harmful unless
            #  someone drops way too much text onto us, which they can easily avoid doing.)
            if len(text) > 250:
                text = text[:250] + "..."
            self.win.history.message("fyi: accepted (but ignoring) this dropped text from outside this widget: %r" % text)
        else:
            # drop was not able to provide us with text -- can't possibly be one of ours
            if self.drag_handler and self.drag_handler.doing_our_own_drag:
                errmsg = "likely bug warning: dropped object should have been ours but provided no text; ignored"
                self.redmsg(errmsg) #e redmsg
            event.accept(False)
            self.redmsg("fyi (nim feature): refused dropped object which could not provide text")
        self.statusbar_msg(" ") # probably a good idea -- not sure!
        return # from overly-long method contentsDropEvent

    def redmsg(self, errmsg): #e someday this might come from the subclass #e refile this method near statusbar_msg
        "put an error message into the History"
        from HistoryWidget import redmsg
        self.win.history.message( redmsg(errmsg))
        self.statusbar_msg(" ") # probably a good idea -- not sure!
        return
    
    
    # key event handlers
    
    def keyPressEvent(self, event): ####@@@@ Delete might need revision, and belongs in the subclass
        key = event.key()
        import platform
        key = platform.filter_key(key) #bruce 041220 (needed for bug 93)
        ####@@@@ as of 050126 this delete binding doesn't seem to work:
        if key == Qt.Key_Delete: ####@@@@ belongs in the subclass
            # bruce 041220: this fixes bug 93 (Delete on Mac) when the model
            # tree has the focus; the fix for other cases is in separate code.
            # Note that the Del key (and the Delete key on non-Mac platforms)
            # never makes it to this keyPressEvent method, but is handled at
            # some earlier stage by the widget, and in a different way;
            # probably this happens because it's a menu item accelerator.
            # The Del key (or the Delete menu item) always directly runs
            # MWsemantics.killDo, regardless of focus.
            self.win.killDo()
            ## part of killDo: self.win.win_update()
        # bruce 041220: I tried passing other key events to the superclass,
        # QListView.keyPressEvent, but I didn't find any that had any effect
        # (e.g. arrow keys, letters) so I took that out.
        return


    # in-place editing of item text

    renaming_this_item = None
    
    def maybe_beginrename(self, item, pos, col):
        """Calls the Qt method necessary to start in-place editing of the given item's name.
        Meant to be called as an event-response; presently called for double-click on the name.
        """
        self.dprint("maybe_beginrename(%r, %r, %r)"%(item,pos,col))
        if not item: return
        # Given the event bindings that call this as of 050128,
        # the first click of the double-click that gets here selects the item
        # (including its members, if it's a group); this might be bad (esp. if
        # it's left selected at the end), but
        # changing it requires updates (to mtree and glpane) we're not doing now,
        # whether we change it before or after the rename,
        # and during the rename it might be useful to see what you're renaming
        # in the glpane too (and glpane redraw might be slow).
        # So I think we'll only unpick when the renaming is done;
        # if it's cancelled, we currently never notice this, so we have no place
        # to unpick; that's ok for now. [bruce 050128]
##        item.object.unpick() #bruce 050128 precautionary change -- undo the picking done by the first click of the double-click
##        ###e probably need to update the display too? not sure. ####@@@@
##        if item.object.picked: print "didn't wpork!"######@@@@@@
##        else: print "did work!"
        if col != 0: return
        if not item.renameEnabled(col):
            self.statusbar_msg("renaming %r is not allowed" % item.object.name) #k will this last too long?
            return
        istr = str(item.text(0))
        msg = "(renaming %r; complete by <Return> or click; cancel by <Escape>)" % istr # text, not html!
        self.statusbar_msg( msg)
            # this happened even for a Datum plane object for which the rename does not work... does it still? ###@@@
        ###@@@ some minor bugs about that statusbar message: [050126]
        # - it needs to reappear in enterEvent rather than having " " appear then
        # - it needs to go away after user cancels the rename
        #   (can some focus-related event or state tell us when?)
        # + [fixed:] it could be shortened; also it fails to mention "accept by click elsewhere"
        #   and wrongly hints this would not work
        # - its text (like some of our method names) assumes the item text is something's name,
        #   but only our subclass (or maybe even only the node) knows what the item text actually represents!
        self.renaming_this_item = item # so we can accept renaming if user clicks outside the editfield for the name
        item.startRename(0)

    ###@@@ does any of this belong in the subclass??
    def slot_itemRenamed(self, item, col, text): # [bruce 050114 renamed this from changename]
        "receives the signal from QListView saying that the given item has been renamed"
        self.dprint("slot_itemRenamed(%r, %r, %r)" % (item,col,text))
        if col != 0: return
        oldname = self.done_renaming()
        if oldname != item.object.name: #bruce 050128 #e clean all this up, see comments below
            if platform.atom_debug:
                print "atom_debug: bug, fyi: oldname != item.object.name: %r, %r" % (oldname, item.object.name)
        what = (oldname and "%r" % oldname) or "something" # not "node %r"
        ## del oldname
        # bruce 050119 rewrote/bugfixed the following, including the code by
        # Huaicai & Mark to strip whitespace, reject null name, and update
        # displayed item text if different from whatever ends up as the node's
        # name; moved much of that into Node.try_rename.
        text_now_displayed = str(text) # turn QString into python string
        del text
        # use text_now_displayed (not further changed) for comparison with final name that should be displayed
        (ok, newname) = item.object.try_rename(text_now_displayed) #e pass col?
        if ok:
            res = "renamed %s to %r" % (what, newname)
            if newname != item.object.name: #bruce 050128
                if platform.atom_debug:
                    print "atom_debug: bug, fyi: newname != item.object.name: %r, %r" % (newname, item.object.name)
        else:
            reason = newname
            del newname
            ## newname = oldname # since newname should be what we want to show in the node now!
            ##      # [bruce 050128 to fix new bug mentioned by Ninad and in the catchall bug report]
            res = "can't rename %s to \"%s\": %s" % (what, text_now_displayed, reason) #e redmsg too?
            ##e not sure this is legal (it's a func but maybe not a method): res = self.win.history.redmsg(res)
        newname = item.object.name # better to just get it from here -- shouldn't even return it from try_rename! #e
        if text_now_displayed != newname:
            # (this can happen for multiple reasons, depending on Node.try_rename:
            #  new name refused, whitespace stripped, etc)
            # update the display to reflect the actual new name
            # (might happen later, too, if try_rename invalidated this node;
            #  even so it's good to do it now so user sees it a bit sooner)
            item.setText(col, newname)
        self.win.history.message( res)
        #obs: # no need for more mtree updating than that, I hope (maybe selection? not sure)
        #bruce 050128 precautionary change -- undo the picking done by the
        # first click of the double-click that started the renaming
        item.object.unpick()
        self.win.win_update()
        return 

    def click_elsewhere_finishes_renaming(self):
        "[private] let this click finish an in-place renaming, if there was one."
        # [050131, added protection against item being deleted during renaming -- I hope this fixes bug 363]
        if self.renaming_this_item:
            try:
                self.renaming_this_item.okRename(0) # 0 is column # this ends up calling slot_itemRenamed
                    # could this scroll the view? I doubt it, but if so,
                    # it's good that we figured out cpos,vpos,item before that.
            except:
                # various errors are possible, including (I guess)
                # "RuntimeError: underlying C/C++ object has been deleted"
                # if user deletes that object from the glpane or a toolbutton during the rename [050131 comment]
                pass
            self.done_renaming()
                # redundant with slot function, but i'm not sure that always runs or gets that far
        self.renaming_this_item = None # redundant with done_renaming()... last minute alpha precaution
        return

    def done_renaming(self):
        "call this when renaming is done (and if possible when it's cancelled, tho I don't yet know how)"
        try:
            oldname = self.renaming_this_item.object.name
        except:
            # various errors are possible, including (I guess)
            # "RuntimeError: underlying C/C++ object has been deleted"
            # if user deletes that object from the glpane or a toolbutton during the rename [050131 comment]
            oldname = ""
        self.renaming_this_item = None
        self.statusbar_msg("")
        return oldname

    # debug menu items

    def debug_menu_items(self):
        "overrides method from DebugMenuMixin"
        super = DebugMenuMixin
        usual = super.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = [
                ("reload modules and remake widget", self._reload_and_remake),
                ("(treewidget instance created %s)" % self._init_time, lambda x:None, 'disabled'),
                ("call win_update()", self._call_win_update),
                ("call mt_update()", self._call_mt_update),
                ]
        ours.append(None)
        ours.extend(usual)
        return ours

    def _call_win_update(self):
        self.win.win_update()

    def _call_mt_update(self):
        self.mt_update()
        
    def _reload_and_remake(self):  ###e needs rewriting to let subclass help with the details...
        """reload all necessary modules (not just this one), and replace the existing tree widget
        (an instance of some subclass of this class)
        with a new one made using the reloaded modules
        """
        # for now we might just plop the new one over the existing one! hope that works.
        print "_reload_this_module... i mean all needed modules for the tree widget, and remake it..."

        width = self.width() #050128
        height = self.height()

        # figure out which modules to reload. The ones of the classes...
        print "finding modules we should reload, innermost first:"
        class1 = self.__class__
        bases = class1.__bases__ # base classes (tuple), not including class1 - this is not the superclass list!
        # there is some method to get supers, but for now let's be quick and simple
        classes = [class1]
        while bases: # loop on class1 and bases; we've already included class1 in our list
            from TreeView import TreeView
            if class1 == TreeView:
                break # beyond that we get things whose modules print as:
                      # constants (lots of times), sip, and __builtin__
            super = bases[0] # ignore mixins, if any
            classes.append(super)
            class1 = super
            bases = class1.__bases__
        modulenames = map( lambda c: c.__module__, classes ) # __module__ is misnamed, it's only a module name
        modules = map( lambda n: sys.modules[n], modulenames )
        print "module names:", modulenames
        print "reloading all these %d modules, outermost first" % len(modules)
        modules.reverse()
        for mod in modules:
            print "reloading",mod
            reload(mod)
        print "now remaking the model tree widget" #e should let subclass give us these details...
        from modelTree import modelTree
        # figure out where we are
        splitter = self.parent() # QSplitter
        sizes = splitter.sizes() # e.g. [207, 633]
        # record the current scroll position so it can later be set to something similar
        scrollpos = self.viewportToContents(0,0)
        win = self.win
        # imitate MWsemantics.py: Create the model tree widget
        win.mt = win.modelTreeView = modelTree(splitter, win, size = (width,height))
        x, y = scrollpos
        win.mt.setContentsPos( x, y) # do this twice; this first time probably doesn't help
        # at this point the new widget is probably to the right of the glpane! hmm...
        splitter.moveToFirst(win.mt)
        win.mt.show()
        self.hide()
        splitter.moveToLast(self)
        # looking at splitter.sizes() at various times,
        # they make no sense, but if the move ops work, then the kids are newmt, glpane, junk.
        wantsizes = [width, sum(sizes) - width]
        while len(wantsizes) < len(sizes):
            wantsizes.append(0)
        splitter.setSizes(sizes) ###e this will also help us extend what's stored by save/load window layout.
        print "splitter-child sizes after setSizes",splitter.sizes()
        splitter.updateGeometry()
        splitter.update()
        win.mt.setContentsPos( x, y) # do this 3 times ... doesn't help avoid a "flicker to no scrollbar state"
            # but i bet setting the contents height initially would help! try it sometime. ###e
        qApp.processEvents() # might be needed before setContentPos in order to make it work
        win.mt.setContentsPos( x, y) # do this 3 times - was not enough to do it before updateGeometry above
##        win.mt.show()
##        self.hide()
        print "done reloading... I guess"
        win.history.message( "reloaded model tree, init time %s" % win.mt._init_time)
        return

    pass # end of class TreeWidget

# end

