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

    # helper functions
    
    def fix_buttons(self, but, when):
        return fix_buttons_helper(self, but, when)
    
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

    # event processing & selection ###@@@ some obs, or move down...
    
    def select(self, item): ###@@@ soon to be obs, i think, or to be inlined... and some belongs in the subclass.
        
        # bruce comment 041220: this is called when widget signals that
        # user clicked on an item, or on blank part of model tree (confirmed by
        # experiment). Event (with mod keys flags) would be useful...
        # 
        self.dprint("select called")
        
        if item:
            if isinstance(item, PartGroup):
                self.dprint("select returns early since item is the PartGroup") #k (but why can't we select it?)
                return
            if item.object.name == self.assy.name:
                self.dprint("select would have returned early since item.object.name == self.assy.name; but it doesn't now")
                # don't return
        
        self.win.assy.unpickatoms() ####@@@@ belongs in the subclass
        
        if not self.modifier:
            # bruce comment 041220: some bugs are caused by this [i.e. self.modifier - 050124] being wrong,
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
        mode = self.win.glpane.mode
        if not isinstance(mode, selectMode):
            return
        if assy.selatoms and isinstance( mode, selectMolsMode):
            self.win.toolsSelectAtoms() ###k check tool name - this case not needed by treewidget
        elif assy.selmols and isinstance( mode, selectAtomsMode):
            self.win.toolsSelectMolecules()
        else:
            pass # nothing selected -- don't worry about assy.selwhat
        return
        
    def keyPressEvent(self, event): ####@@@@ Delete needs revision, and belongs in the subclass
        key = event.key()
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
##        ###@@@ the rest is soon to be obs
##        elif key == Qt.Key_Control:
##            self.modifier = 'Cntl' ###@@@ soon to be obs
##        elif key == Qt.Key_Shift:
##            self.modifier = 'Shift' ###@@@ soon to be obs
        # bruce 041220: I tried passing other key events to the superclass,
        # QListView.keyPressEvent, but I didn't find any that had any effect
        # (e.g. arrow keys, letters) so I took that out.
        return
        
    def keyReleaseEvent(self, event):
        pass
##        self.modifier = None ###@@@ soon to be obs

    # context menus ###@@@ move this down
    
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
        self.selection_click(item, pos, col, permit_drag = False) 
        
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

    # selection - move this down ####@@@@ also make it work
    
    def item_is_selected(self, item): ###@@@ might work in superclass but only useful here and might be redefined here
        """Is the given item already selected?
        (Special case: for item == None (legal), return False.)
        """
        if not item:
            return False
        return item.isSelected() #k guess ###@@@stub, not sure this is the right/best/ok place to store this state
    
    def selection_click(self, item, pos, col, modkeys = 0, permit_drag = True):
        """Perform the ordinary selection-modifying behavior for one click in this place
        (i.e. at position pos ###k what coords??, on the given item (might be None), in column col [ignored now]).
        Assume the modifier keys for this click were as given in modkeys, for purposes of selection or drag(??) semantics.
        We immediately modify the set of selected items -- changing the selection state of their Nodes (node.picked),
        updating tree-item highlighting (but not anything else in the application -- those will be updated when Qt resumes
         event processing after we return from handling this click ###@@@ so we need to inval the glpane to make that work!
         until then, it won't update til... when? the next paintGL call. hmm. I guess we just have to fix this now.).
    
        If permit_drag is True (the default), this click might become the start of a drag of the same set of items it
        causes to be selected; but this routine only sets some instance variables to help a mouse move method decide whether
        to do that.
        
        #doc elsewhere: for a single plain click on a selected item, this should not unselect the other items!
        # at least finder doesn't (for sel or starting a drag)
        # and we need it to not do that for this use as well.
        """
        
        ### this is not used in place of select yet, just to test cmenus...
        # (which in any case will be passed to us, not found in some attribute on self! since some callers filter them.)

        #e first filter item and pos so that positions too far to left or right don't count as being on item. NIM.
        # one case of this is clicks on the open/close togging icon. Not sure if they ever get here, though,
        # in fact, caller might do this filtering. We'll see.
        
        if item and item.object.picked: ###@@@ does this depend on modkeys?? ###@@@ do stuff to set up for drag, too
            return # no change! #doc why; see comments in menuReq

        #e now perform sel logic... using item none or not, and modkeys... update .picked and item highlighting. ####@@@@
        ####@@@@ implem... steal some code from select, or split it into this...
        # stub: just toggle it for this one item. wait, above behavior defeats this... too tired, do this tomorrow.
        if item:
            node = item.object
            if node.picked:
                node.unpick() # won't happen yet...
            else:
                node.pick()
        self.update_selection_highlighting()
        self.win.glpane.update() ####k will this work already, just making it call paintGL? or must we inval something too??
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
        """Calls the Qt method necessary to start in-place editing of the given item's name.
        Meant to be called as an event-response; presently called for double-click on the name. ###@@@ not yet exactly then
        """
        self.dprint("maybe_beginrename(%r, %r, %r)"%(item,pos,col))
        if not item: return
        if col != 0: return
        if not item.renameEnabled(col): return ####@@@@ 050119 exper; should be enough to stop renaming of Clipboard ###test
        istr = str(item.text(0))
        ## now done by rename disabled in their node subclasses: ###@@@ test
        ## if istr in [self.assy.name, "Clipboard"]: return
        msg = "(renaming %r -- complete this by pressing Return, or cancel it by pressing Escape)" % istr
        self.win.history.transient_msg( msg)
            # this happened even for a Datum plane object for which the rename does not work... does it still? ###@@@
            # bug: that message doesn't go away if user cancels the rename.
        self.renaming_this_item = item # so we can accept renaming if user clicks outside the editfield for the name
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
# bruce 050121 removing all these obs special cases, even tho not yet replaced with revised ones,
# since these entire routines are all wrong and will be totally replaced.
##            sdaddy = self.last_selected_node.whosurdaddy() # Selected item's daddy (source)
##            tdaddy = droptarget.object.whosurdaddy() # Drop target item's daddy (target)
###            print "Source selected item:", self.last_selected_node,", sdaddy: ", sdaddy
###            print "Target drop item:", droptarget.object,", tdaddy: ", tdaddy
##            if sdaddy == "Data": return # selected item is in the Data group.  Do nothing.
##            if sdaddy == "ROOT": return # selected item is the part or clipboard. Do nothing.    
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

    #####@@@@@ main event handlers - move up
    
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

    def contentsMouseDoubleClickEvent(self, event):
        return self.contentsMousePressEvent(event, dblclick = 1) # fine for open/close; until we need it to edit names

    renaming_this_item = None
    def contentsMousePressEvent(self, event, dblclick = 0):
        "[called by Qt, or by our own contentsMouseDoubleClickEvent]"
        
        # figure out position and item of click (before doing any side effects)
        #e this might be split into a separate routine if it's useful during drag
        
        cpos = event.pos() # this is in contents coords;
            # y=1 is just under column label (which does not scroll with content)
        vpos = self.contentsToViewport(cpos)
        item = self.itemAt(vpos)
        
        # before anything else (except above -- in case this scrolls for some reason),
        # let this click finish an in-place renaming, if there was one.
        if self.renaming_this_item:
            self.renaming_this_item.okRename(0) # 0 is column # this ends up calling slot_itemRenamed
                # could this scroll the view? I doubt it, but if so,
                # it's good that we figured out cpos,vpos,item before that.
            self.done_renaming()
                # redundant with slot function, but i'm not sure that always runs or gets that far

        # now figure out what part of the item (if any) we clicked on,
        # setting 'part' to a constant string describing which part, or None.

        # (someday: if we clicked too far to left or right of visible part of item,
        #  set item = part = None; or we might have new 'part' values
        #  for those positions. #e)

        part = None
        ## clicked_on_text = clicked_on_icon = clicked_on_openclose = False
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
##               self.presspos.setX(event.pos().x())
##               self.presspos.setY(event.pos().y())
##               self.mousePressed = True
            # our version of dirview example's code:
            isdecorated = 1 # should conform to self.rootIsDecorated()
            header = self.header()
            special_x = header.sectionPos( header.mapToIndex( 0 ))
                # where is this x? by experiment it's always 0 for us. must be left edge of column 0.
                # btw, Qt C++ eg uses mapToActual but there's no such attr when tried here.
            extra = self.treeStepSize() * (item.depth() + isdecorated) + self.itemMargin()
            ## special_x_2 = header.sectionPos( header.mapToActual( 0 )) # no such attr
##            print "for that item: special x pos = %r, treestep = %r, depth %r, margin %r" % (
##                                        special_x, self.treeStepSize(), item.depth(), self.itemMargin() )
            greater_by = vpos.x() - (special_x + extra) # this tells whether we hit the left edge of the icon, for a very big icon.
##            if greater_by > 0:
##                print "to right of decoration by",greater_by # i think to right by 3 or 2 should count as on decoration...
##            else:
##                print "not to right",greater_by
            if greater_by > 22: #e probably need to adjust this cutoff
                part = 'text'
                #e incorrect if we're to the right of the visible text;
                # Qt docs show how to check text width to find out; should use that
                # (also we're not checking for still being in column 0, just assuming that)
            if greater_by > 2: #e might need to adjust this cutoff (btw it's a bit subjective)
                part = 'icon'
            elif greater_by > -12: ###e surely need to adjust this
                part = 'openclose'
                print "change so openclose can only happen for an expandable item" ####@@@@
            elif vpos.x() >= special_x:
                part = 'left'
            else:
                part = item = None # to the left of column 0 (not currently possible I think)
            pass
        
        # If this click's data differs from the prior one, this event shouldn't
        # be counted as a double click. Or the same, if too much time passed since prior click,
        # which would mean Qt erred and called this a double click even though its first click
        # went to a different widget (I don't know if Qt can make that mistake).
        # ###e nim feature...

        ####@@@@

        # now what? figure out what to actually do. use bindings set up by subclass. use separate routine... ####@@@@
        # probably store some things here too, in case we'll decide later to start a drag.
        # subr might say whether that's permitted or reset what we store here. ####e ###@@@

        self.clicked( event, vpos, item, part, dblclick)   ###e see also selection_click... ###@@@

        self.update_select_mode() # change mode to selectMolsMode iff necessary
        
        return # from contentsMousePressedEvent

    def clicked( self, event, vpos, item, part, dblclick):
        """Called on every mousedown (regardless of mouse buttons / modifier keys).
        Event is the Qt event (not yet passed through fix_buttons).
        vpos is its position in viewport coordinates.
        item is None or a QListViewItem.
        If item, then part is one of ... #doc; otherwise it's None.
        dblclick says whether this should count as a double click
        (note that for some bindings we'll implement, this won't matter).
        """

        # handle debug menu; canonicalize buttons and modifier keys.
        
        if self.debug_event(event, 'mousePressEvent', permit_debug_menu_popup = 1):
            return
        but = event.stateAfter()
        but = self.fix_buttons(but, 'press')

        # now we check for various user commands, handling the first one that applies
        # and returning from this method (having done any needed inval/update which is
        # within the tree widget itself, but not some external updates done by our caller).
        
        # handle context menu request.
        
        if but & rightButton:
            # context menu -- regardless of part of item (if any) we clicked on (even openclose or left)!
            # Also when no item. Ignores modifier keys and dblclick.
            # [kluge for now - be compat with old code
            #####e set self.modifier - probably not yet used by menuReq, anyway
            # def menuReq(self, item, pos, col) - col not used, ends with mt_update, no retval]
            pos = event.globalPos() # coords??
            col = -333
            self.menuReq( item, pos, col)
            return

        # after this point, treat clicks to left of open/close icon as if on no item.
        # (would it be better to treat them as on open/close, or have a special cmenu
        #  about the parent items, letting you close any of those? ##e)
        if part == 'left':
            part = item = None
        
        # handle open/close toggling. (ignores modifier keys, mouse buttons, dblclick)
        if part == 'openclose':
            # this can only happen for a non-leaf item!
            self.toggle_open(item) # does all needed inval/update/repaint ####@@@@ is this finished?
            return

        # handle in-place editing of the item text, on double-click
        
        #e (someday this might be extended to edit a variant of the text,
        #   if some of it is a fixed label or addendum... to implem that,
        #   just call item.setText first, within the subroutine.)

        # (for now, this is done for middle click too, and it ignores modifier keys)
        if dblclick and part = 'text':
            # presumably the first click selected this item... does this matter?? #k
            # BTW it would not be true if this was a Control-double-click!
            # If we wanted to be paranoid, we'd return unless the modkeys and button
            # were identical with the saved prior click (and were null)... #e do that now? ###@@@
            col = 0
            return self.maybe_beginrename( item, vpos, col)

        # what's left?
        # - selection.
        # - drag-starting, whether for d&d or (saved for later #e) a selection range or rect.
        # - hover behaviors (tooltip, cmenu) (saved for later. #e)
        #####@@@@ need code to save event info for drag-starting ###@@@ merge with selection_click, elsewhere

        # selection-click, and/or start of a drag
        # (we can't in general distinguish these until more events come)

        if dblclick:
            # Too likely this 2nd click was a mistake -- let the first click handle
            # it alone. (This only matters for Control-click, which toggles selection,
            # once the feature of discarding dblclick flag when item/part
            # changed is implemented.)
            return

        if (but & allButtons) != leftButton:
            # ignore middle button, and ignore certain bugs in the above code
            return

        # kluge: set self.modifier for compatibility with old code
        if but & shiftButton:
            self.modifier = 'Shift'
        elif but & cntlButton:
            self.modifier = 'Cntl'
        else:
            self.modifier = None
        
        # kluge: try to use old code, see how much it can handle
        ####@@@@ some or all of its behavior might belong in a subclass -- not sure
            
        self.select(item) ###@@@
        
        return # from clicked

    def contentsMouseMoveEvent(self, event):
        "[overrides QListView method]"
        # This method might be needed, to prevent QListView from messing us up.
        pass
    
    def contentsMouseReleaseEvent(self, event):
        "[overrides QListView method]"
        # This method might be needed, to prevent QListView from messing us up.
        # (At least, without it, QListView emits its "clicked" signal.)
        pass 

    # debug menu items

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

