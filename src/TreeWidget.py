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

class TreeWidget(TreeView, DebugMenuMixin):
    def __init__(self, parent, win, name = None, columns = ["node tree"]):
        """#doc
        creates all columns but only known to work for one column.
        some code only bothers trying to support one column.
        """
        ###@@@ review all init args & instvars, here vs subclasses
        TreeView.__init__(self, parent, win, name, columns = columns) # stores self.win

        self.setAcceptDrops(True)

        # debug menu and reload command ###e subclasses need to add reload actions too
        self._init_time = time.asctime() # for debugging; do before DebugMenuMixin._init1
        DebugMenuMixin._init1(self) ###e will this be too early re subclass init actions??

        ###@@@ soon obs, if not already:
        self.last_selected_node = None #k what's this for? ###@@@ mainly context menus?
         # actually it has several uses which need to be split:
         # - sometimes records last item user clicked on to select it (but not to unselect).
         # - tells context menu what to be about, if not asked for when over an item. [surely obs]
         # - used by context menu to record the item, if it *is* on an item. (even if it refuses to put up a menu) [surely obs]
         # - used as the "item to drag" in drag and drop (regardless of event posns or selection!). [obs]
            #bruce 050109 renamed this from selectedItem since that's
            # a Qt method in QListView! In theory this might fix bugs...
            # didn't notice any though.

        self.modifier = None ###@@@ soon to be obs

        ###@@@ setCurrentItem might help it process keys... ###@@@ try it... maybe i did and it failed, not sure 050110

        self.setDefaultRenameAction(QListView.Accept)
            # I don't think this has any effect, now that we're depriving
            # QListView of mouse events, but I'm setting it anyway just in case.
            # The "real version of this" is in our own contentsMousePress... method.

        # bruce 050110 moved mt_update below the signal connections
        # [not positive this move is needed or good]
        # [undone anyway when we split into 3 modules, 050120]
        
        # bruce 050112 zapping most signals, we'll handle the events ourself.
        
        # Mark and Huaicai - commented this out -
        # causing a bug for context menu display on windows
        # Fixed with the signal to "rightButtonPressed"
##        if sys.platform != 'win32':
##            self.connect(self, SIGNAL("contextMenuRequested(QListViewItem*, const QPoint&,int)"),
##                         self.menuReq)
##        else:             
##            self.connect(self, SIGNAL("rightButtonPressed(QListViewItem*,const QPoint&,int)"),
##                         self.menuReq)
            
##        self.connect(self, SIGNAL("clicked(QListViewItem *)"), self.select)
##        self.connect(self, SIGNAL("expanded(QListViewItem *)"), self.treeItemExpanded)
##        self.connect(self, SIGNAL("collapsed(QListViewItem *)"), self.treeItemCollapsed)
        self.connect(self, SIGNAL("itemRenamed(QListViewItem*, int, const QString&)"), self.slot_itemRenamed)
##        self.connect(self, SIGNAL("doubleClicked(QListViewItem*, const QPoint&, int)"), self.maybe_beginrename)

        return # from TreeWidget.__init__

    # event processing
    
    def fix_buttons(self, but, when):
        return fix_buttons_helper(self, but, when)

    # context menus
    
    def makemenu(self, lis):
        return makemenu_helper(self, lis)

    # Slot functions # PROBABLY OBS ###@@@
    def treeItemExpanded(self, item):
        node = item.object
        node.open = True ###@@@ do this differently! in a local cache. or just use the tree item prop itself? why not?
        self.update_item_icon(item) ###@@@ implem special cases for self.tree, self.shelf
        # note: doesn't call mt_update

    def treeItemCollapsed(self, item):
        node = item.object
        node.open = False
        self.update_item_icon(item)
        # note: doesn't call mt_update

    # event processing & selection
    
    def select(self, item): ###@@@ soon to be obs, i think, or to be inlined... and some belongs in the subclass.
        
        # bruce comment 041220: this is called when widget signals that
        # user clicked on an item, or on blank part of model tree (confirmed by
        # experiment). Event (with mod keys flags) would be useful,
        # but is evidently not available (maybe it could be, in some other way?)
        # [addendum, 041227: it might be sufficient to wrap this with a subclass
        #  which defines an "event" method to process all events, making a note
        #  of their flags, then handing it off to the superclass event method. ###@@@]
        # bruce 050110: contentsMouseEvent or something like that...
        self.dprint("select called")
        
        if item:
            ## self.bruce_print_item(item) # debug
            if item.object.name == self.assy.name:
                self.dprint("select returns early since item.object.name == self.assy.name")
                return
        
        self.win.assy.unpickatoms() ####@@@@ belongs in the subclass
        
        if isinstance(self.win.glpane.mode, selectMode) and 0: #######@@@@@@@ see if this 'and 0' helps...
            ####@@@@ guess: this causes a bug by doing the update too early somehow... not sure... why not done again below?
            ####@@@@ win_update should do mt_update which should schedule another repaint... does it think none is needed?
            self.dprint("select is calling toolsSelectMolecules")
            self.win.toolsSelectMolecules()
            self.dprint("select done calling toolsSelectMolecules")
                #e should optim:
                # this calls repaintGL redundantly with win.win_update() [bruce 041220]
        else:        
            self.win.assy.selwhat = 2
        
        if not self.modifier:
            # bruce comment 041220: some bugs are caused by this being wrong,
            # e.g. bug 263 (my comment #3 in there explains the likely cause).
            self.win.assy.unpickparts()
        
        if item: 
            if self.modifier == 'Cntl':
                item.object.unpick()
                self.last_selected_node = None
            else:
                item.object.pick()
                self.last_selected_node = item.object
                ###@@@ why only the one item? [bruce question 041220]

##        self.dprint("select is calling win_update")
##        self.win.win_update()
##        self.dprint("select done calling win_update, returning")
        ####@@@@ maybe this will help:
        self.update_selection_highlighting()
        return

    def keyPressEvent(self, e): ####@@@@ some belongs in the subclass
        key = e.key()
        import platform
        key = platform.filter_key(key) #bruce 041220 (needed for bug 93)
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
        ###@@@ the rest is soon to be obs
        elif key == Qt.Key_Control:
            self.modifier = 'Cntl' ###@@@ soon to be obs
        elif key == Qt.Key_Shift:
            self.modifier = 'Shift' ###@@@ soon to be obs
        # bruce 041220: I tried passing other key events to the superclass,
        # QListView.keyPressEvent, but I didn't find any that had any effect
        # (e.g. arrow keys, letters) so I took that out.
        return
        
    def keyReleaseEvent(self, key):
        self.modifier = None ###@@@ soon to be obs

    # context menus
    
    def menuReq(self, item, pos, col): ####@@@@ some of this goes here (cmenus in general), maybe some in subclass (specific menus)
        """Context menu items function handler for the Model Tree View
        [interface is compatible with a related QListView signal,
         but it's not called that way as of 050112; col arg is not used;
         pos should be the position to put up the menu, in global coords (event.globalPos).]
        """
        print "menuReq got globalPos(?)",pos.x(), pos.y()
        ##pos = QPoint(5,40) ####@@@@ test - remove it! test shows that upper left corner of menu gets to these abs screen coords.

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
        # behavior? If you use them, it just does selection and ignores the
        # control key (no context menu).)
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
        # it acts like you clicked on no item, for this purpose.
        #
        # [refile?] About the menu position and duration:
        # In all cases, the menu top left corner is roughly at the click pos,
        # and the menu disappears immediately on mouseup, whether or not you
        # choose a command from it.
        #
        # This all seems pretty good, so I will imitate it here. [bruce 050113]

        ###@@@ correct item to be None if we were not really on the item acc'd to above,
        ### or do this in following function according to event position...
        self.selection_click(item, pos) # imitate ordinary sel behavior for one click in this place ###@@@ IMPLEM
        ###@@@ make sure that ignores all mod keys, and updates the sel-state (highlighting) of ALL items (incl far away ones)
        # and returns the actual item to treat this as being about? or the sel-set? or grab that elsewhere now?
        # ALSO, for a single plain click on a selected item, this should not unselect the other items!
        # at least finder doesn't (for sel or starting a drag)
        # and we need it to not do that for this use as well.
        set = self.current_selection_set() # a list of items?? might be a more structured thing someday... and/or made of nodes...
            # but i think it's items for now, since some ops really involve them as items more than as nodes...
            # otoh not all of the selected nodes might have real items in the widget, but all should be in this...
            # otth we can make item proxies for them even if those don't own real tree items at the moment...
            # and probably we should...
            # so it's a list of items for now.
        menu = self.make_cmenu_for_set( set)
        print "arg1 of qmpopup is menu = %r, other arg pos is %r" % (menu,pos)#####@@@@@@
        menu.popup(pos) ##### transform pos #e care about which item to put where (e.g. popup(pos,1))?
        # bruce comment 050110: following mt_update is probably not helping anything ###@@@ try removing it; try exec_loop?
        # since the menu has just been put up -- nothing has yet been chosen from it
        self.dprint("mtree.menuReq just returned from menu.popup, probably with menu there - what events are responded to?")###@@@ find out!
        self.mt_update()
        return

    # selection
    
    def item_is_selected(self, item): ###@@@ might work in superclass but only useful here and might be redefined here
        """Is the given item already selected?
        (Special case: for item == None (legal), return False.)
        """
        if not item:
            return False
        return item.isSelected() #k guess ###@@@stub, not sure this is the right/best/ok place to store this state
    
    def selection_click(self, item, pos):
        ###stub(or maybe actually ok?) - we can't yet trust pos! also not used in place of select yet, just to test cmenus, so ignore mod keys.
        # (which in any case will be passed to us, not found in some attribute on self! since some callers filter them.)
        if self.item_is_selected(item): #### according to what saved state??
            ### only valid if self.selected_items exists and is correct, which is not yet true... so fake it if other code didn't do it right:
            if not hasattr(self, 'selected_items'):
                self.selected_items = [] # or could make it from existing sel state of all items? not yet! first figure out who *should*.
            if item not in self.selected_items:
                self.selected_items = [item] # safer than appending it, i think...
            return # no change! #doc why; see comments in menuReq
        self.selected_items = (item and [item]) or []
        self.set_node_sel_from_selected_items( self.selected_items) ####@@@@ implem... steal some code from select, or split it into this...
        ## old name: self.update_all_selected_state()
        ## name I wrongly recalled: self.update_selection_state()
        self.update_selection_highlighting()
        return

    def current_selection_set(self):
        if not hasattr(self, 'selected_items'):
            self.selected_items = [] # see also comments/samecode just above
        return list(self.selected_items)

    # context menus
    
    def make_cmenu_for_set(self, itemset):
        """Return a context menu (QPopupMenu object #k)
        to show for the given set of (presumably selected) items.
        [Might be overridden by subclasses, but usually it's more convenient
        for them to override make_cmenuspec_for_set instead.]
        """
        spec = self.make_cmenuspec_for_set(itemset)  \
               or self.make_cmenuspec_for_set([])  \
               or [('(empty context menu)',noop,'disabled')]
        return self.makemenu( spec)

    def make_cmenuspec_for_set(self, itemset):
        """#doc
        [subclasses should override this]
        # [see also the term Menu_spec]
        """
        return []

    # renaming of item text

    ###@@@ does any of this belong in the subclass??
    def slot_itemRenamed(self, item, col, text): # [bruce 050114 renamed this from changename]
        "receives the signal saying that the given item has been renamed"
        self.dprint("slot_itemRenamed(%r, %r, %r)" % (item,col,text))
        if col != 0: return
        oldname = self.done_renaming()
        what = (oldname and "%r" % oldname) or "something" # not "node %r"
        del oldname
        # bruce 050119 rewrote/bugfixed the following, including the code by
        # Huaicai & Mark to strip whitespace, reject null name, and update
        # displayed item text if different from whatever ends up as the node's
        # name; moved much of that into Node.try_rename.
        text = str(text) # turn QString into python string
        # use text (not further changed) for comparison with final name
        (ok, newname) = item.object.try_rename(text) #e pass col?
        if ok:
            res = "renamed %s to %r" % (what, newname)
        else:
            res = "can't rename %s to %r" % (what, newname) #e redmsg too?
        if text != newname:
            # (this can happen for multiple reasons, depending on Node.try_rename:
            #  new name refused, whitespace stripped, etc)
            # update the display to reflect the actual new name
            # (might happen later, too, if try_rename invalidated this node;
            #  even so it's good to do it now so user sees it a bit sooner)
            item.setText(col, newname)
        self.win.history.message(" (%s)" % res)
        return # no need for more mtree updating than that, I hope (maybe selection? not sure)

    def done_renaming(self):
        try:
            oldname = self.renaming_this_item.object.name
        except:
            oldname = ""
        self.renaming_this_item = None
        self.win.history.transient_msg("")
        return oldname
    
    def maybe_beginrename(self, item, pos, col):
        "calls the Qt method necessary to start in-place editing of the given item's name."
        self.dprint("maybe_beginrename(%r, %r, %r)"%(item,pos,col))
        if not item: return
        if col != 0: return
        if not item.renameEnabled(col): return ####@@@@ 050119 exper
        istr = str(item.text(0))
        if istr in [self.assy.name, "Clipboard"]: return
        msg = "(renaming %r -- complete this by pressing Return, or cancel it by pressing Escape)" % istr
        self.win.history.transient_msg( msg) # seems to work... [when it was .message with transient_id]
        print msg ###@@@ # this happened even for a Datum plane object for which the rename does not work...
        self.renaming_this_item = item # so we can accept renaming if user clicks elsewhere [untested]
        item.startRename(0)

    # drag and drop (ALL DETAILS ARE WRONG AND OBS ###@@@)
    
    ###@@@ bruce 050110 - this overrides a Qt method, is that intended?? the one we should override is dragObject
    ####@@@@ let's try ths change
##    def startDrag(self): 
#        print "MT.startDrag: self.last_selected_node = [",self.last_selected_node,"]"
##        if self.last_selected_node:
##            foo = QDragObject(self)
##            foo.drag()
    def dragObject(self):
        self.dprint("dragObject, last_selected_node is %r" % self.last_selected_node)
        if self.last_selected_node: # Qt doc says "depending on the selected nodes"
            foo = QDragObject(self)
            return foo
            ##foo.drag()

    def dropEvent(self, event):
        above = False
        pnt = event.pos() - QPoint(0,24)
        # mark comments [04-12-10]
        # We need to check where we are dropping the selected item.  We cannot allow it 
        # to be dropped into the Data group.  This is what we are checking for here.
        # mmtop = 5 top nodes * (
        #                treeStepSize (space b/w parent and child nodes = 20 pixels) + 
        #                5 pixels (space b/w nodes ))
        mttop = 5 * (self.treeStepSize() + 5) # Y pos past top 5 nodes of MT (after last datum plane node).
#        print "modelTree.dropEvent: mttop = ",mttop
        if pnt.y() < mttop:
            pnt.setY(mttop) # We dropped above the first chunk (onto datum plane/csys). Mark 041210
            above = True # If we move node, insert it above first node in MT.
        droptarget = self.itemAt(self.contentsToViewport(pnt))
        if droptarget:
            sdaddy = self.last_selected_node.whosurdaddy() # Selected item's daddy (source)
            tdaddy = droptarget.object.whosurdaddy() # Drop target item's daddy (target)
#            print "Source selected item:", self.last_selected_node,", sdaddy: ", sdaddy
#            print "Target drop item:", droptarget.object,", tdaddy: ", tdaddy
            if sdaddy == "Data": return # selected item is in the Data group.  Do nothing.
            if sdaddy == "ROOT": return # selected item is the part or clipboard. Do nothing.    
            if isinstance(droptarget.object, Group): above = True # If drop target is a Group
            self.last_selected_node.moveto(droptarget.object, above)
#            if sdaddy != tdaddy: 
#                if sdaddy == "Clipboard" or droptarget.object.name == "Clipboard": 
#                    self.win.win_update() # Selected item moved to/from clipboard. Update both MT and GLpane.
#                    return
#            self.mt_update() # Update MT only
            self.win.win_update()

    def dragMoveEvent(self, event):
        event.accept()

    
    def glpane_eg_mousePressEvent(self, event): ###@@@ zap this when done -- just an example to look at.
        """Dispatches mouse press events depending on shift and
        control key state.
        """
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            return
        but = event.stateAfter()
        but = self.fix_buttons(but, 'press')
        
        #print "Button pressed: ", but
        
        if but & leftButton:
            if but & shiftButton:
                self.mode.leftShiftDown(event)
            elif but & cntlButton:
                self.mode.leftCntlDown(event)
            else:
                self.mode.leftDown(event)

        if but & midButton:
            if but & shiftButton:
                self.mode.middleShiftDown(event)
            elif but & cntlButton:
                self.mode.middleCntlDown(event)
            else:
                self.mode.middleDown(event)

        if but & rightButton:
            if but & shiftButton:
                self.mode.rightShiftDown(event)
            elif but & cntlButton:
                self.mode.rightCntlDown(event)
            else:
                self.mode.rightDown(event)         

    def contentsMouseDoubleClickEvent(self, e):
        self.dprint("dblclick %r, pretending it's another regular click for now" % e)
        return self.contentsMousePressEvent(e, dblclick = 1) # fine for open/close; until we need it to edit names
        pass ####@@@@ ok for now?

    renaming_this_item = None
    def contentsMousePressEvent(self, e, dblclick = 0):
        "[called by Qt, or by other event methods of our own]"
        cpos = e.pos() # Qt doc, and test, agree this is in contents coords;
            # y=1 is just under the "listview label".
            # btw that label does not scroll! (good.)
            # i once thought it did, maybe because it was so often messed up by redraw bugs.
##        self.dprinttime()
##        print "cpos from event:",cpos.x(),cpos.y()    
        vpos = self.contentsToViewport(cpos)
##        print "vpos:",vpos.x(),vpos.y() # this is correct - y==1 is just under label, whether or not scrolled. same as cpos if not.
##        #k does it work right re label at top? or needs -24 like drop code has? seems to work right and not need that (so far).
        item = self.itemAt(vpos)
        
        # first, let this click finish an in-place renaming, if there was one.
        if self.renaming_this_item:
            self.renaming_this_item.okRename(0) # 0 is column # this ends up calling slot_itemRenamed
                # could this scroll the view? I doubt it, but if so,
                # it's good that we figured out cpos,vpos,item before that.
            self.done_renaming()
                # redundant with slot function, but i'm not sure that always runs or gets that far

        try:
            name = item.object.name
        except:
            name = "?" # for item None or a bug
        print "%sclick on item %r (%s)" % (dblclick and "double" or "",item,name)

        if item:
            # where in the item did we click?
            # relevant Qt things:
            # QListViewItem::width - width of text in col k (without cropping)
            # ... and some example code for a directory browser (available in PyQt too... examples3/dirview.py)
##            ## here is the code from dirview.py:
##            # if the user clicked into the root decoration of the item, don't try to start a drag!
##            if self.rootIsDecorated(): isdecorated = 1
##            else : isdecorated = 0
##            #bruce 050120 observes that there's a misplaced ')' in the next line. compare to Qt version of this.
##            if p.x() > self.header().sectionPos( self.header().mapToIndex( 0 )) + self.treeStepSize() * ( i.depth() + isdecorated + self.itemMargin() or
##               p.x() < self.header().sectionPos( self.header().mapToIndex( 0 ) ) ) : ### to left of this column
##               self.presspos.setX(e.pos().x())
##               self.presspos.setY(e.pos().y())
##               self.mousePressed = True
            # our version of dirview example's code:
            isdecorated = 1 # should conform to self.rootIsDecorated()
            header = self.header()
            special_x = header.sectionPos( header.mapToIndex( 0 )) # where is this x? by experiment it's always 0 for us. must be left edge of column 0.
                # btw, Qt C++ eg uses mapToActual but there's no such attr when tried here.
            extra = self.treeStepSize() * (item.depth() + isdecorated) + self.itemMargin()
            ## special_x_2 = header.sectionPos( header.mapToActual( 0 )) # no such attr
##            print "for that item: special x pos = %r, treestep = %r, depth %r, margin %r" % (
##                                        special_x, self.treeStepSize(), item.depth(), self.itemMargin() )
            greater_by = vpos.x() - (special_x + extra) # this tells whether we hit the left edge of the icon, for a very big icon.
            if greater_by > 0:
                print "to right of decoration by",greater_by # i think to right by 3 or 2 should count as on decoration...
            else:
                print "not to right",greater_by

        
        if dblclick and item: ####@@@@ and if click in correct place!
            col = 0
            return self.maybe_beginrename(item,vpos,col) ####@@@@ vpos coords?? ####@@@@ see if this works... 050114
            # itworks, but the only way to get out of it is ret, esc, or another rename...
            # how do we make other events work for that? qt doc for QListViewItem gives no clue.
            # maybe check it out for EditField?? Or make my own renamer? read rename in QListView doc?

        ###@@@ copying this in part from glpane_eg_mousePressEvent:   NEED DebugMenuMixin, fix_buttons
        event = e
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            return
        but = event.stateAfter()
        but = self.fix_buttons(but, 'press')
        
        if but & rightButton:
            # context menu
            # kluge for now - be compat with old code
            #####e set self.modifier - probably not yet used by menuReq, anyway
            # def menuReq(self, item, pos, col) - col not used, ends with mt_update, no retval
            pos = event.globalPos() # coords??
            col = -333
            self.menuReq( item, pos, col)
            return

        if not item:
            # kluge: try to use old code, see how much it can handle
            ## self.modifier = None # for now
            self.select(item) ###@@@
            return

        try:
            node = item.object
            leaf = not node.openable()
        except:
            print_compact_traceback("bug:")
            return
        
        if leaf:
            # kluge: try to use old code, see how much it can handle
            ## self.modifier = None # for now
            self.select(item) ###@@@
            return
        
        # not leaf -- for now, do this no matter where we click on it!
        self.toggle_open(item) # does all needed inval/update/repaint
        
        return # from contentsMousePressedEvent

    def contentsMouseMoveEvent(self, e):
        pass
    
    def contentsMouseReleaseEvent(self, e):
        pass # without this, QListView calls its "clicked" signal

    ## dragObject

    def debug_menu_items(self):
        "overrides method from DebugMenuMixin"
        super = DebugMenuMixin
        usual = super.debug_menu_items(self)
            # list of (text, callable) pairs, None for separator
        ours = [
                ("reload TreeWidget.py", self._reload_TreeWidget),
                ("reload modelTree.py", self._reload_modelTree), ###@@@ mnove to subclass?
                ("(treewidget instance created %s)" % self._init_time, lambda x:None, 'disabled'),
                ]
        ours.append(None)
        ours.extend(usual)
        return ours

    def _reload_this_module(self): ####@@@@ revise for my having split the modules, maybe move some to subclass...
        """reload this module, and replace the existing tree widget
        with a new one made from the new module"""
        # for now we might just plop the new one over the existing one! hope that works.
        print "\n_reload_this_module (modelTree.py I assume)"
        import modelTree
        reload(modelTree)
        from modelTree import modelTree
        # figure out where we are
        splitter = self.parent()
        print "splitter:",splitter # QSplitter
        win = self.win
        # imitate MWsemantics.py: Create the model tree widget
        win.mt = win.modelTreeView = modelTree(splitter, win)
        win.modelTreeView.setMinimumSize(0, 0)
        # at this point the new widget is probably to the right of the glpane! hmm...
        splitter.moveToFirst(win.mt)
        # (do we also need to show it? and hide this one? can't hurt. might not work for childwidgets?)
        win.mt.show()
        self.hide()
        print "done reloading... I guess"
        win.history.message( "reloaded model tree, init time %s" % win.mt._init_time)
        return

    _reload_TreeWidget = _reload_modelTree = _reload_this_module ####@@@@

    pass # end of class TreeWidget

# end

