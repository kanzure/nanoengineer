
class unused_methods_in_class_MT_View: #removed from it, bruce 081216
    def repaint_some_nodes_NOT_YET_USED(self, nodes): #bruce 080507 experimental, for cross-highlighting; maybe not used; rename?
        """
        For each node in nodes, repaint that node, if it was painted the last
        time we repainted self as a whole. (If it wasn't, it might not be an
        error, if it was due to that node being inside a closed group, or to
        a future optim for nodes not visible due to scrolling, or if we're being
        called on a new node before it got painted here the first time; so we
        print no warning unless debug flags are set.)

        Optimization for non-visible nodes (outside scrollarea viewport) is
        permitted, but not implemented as of 080507.

        @warning: this can only legally be called during a paintEvent on self.
                  Otherwise it doesn't paint (but causes no harm, I think)
                  and Qt prints errors to the console. THE INITIAL IMPLEM IN
                  THE CALLERS IGNORES THIS ISSUE AND THEREFORE DOESN'T YET WORK.
                  See code comments for likely fix.
        """
        # See docstring comment about the caller implem not yet working.
        # The fix will probably be for the outer-class methods to queue up the
        # nodes to repaint incrementally, and do the necessary update calls
        # so that a paintEvent can occur, and set enough new flags to make it
        # incremental, so its main effect will just be to call this method.
        # The danger is that other update calls (not via our modelTreeGui's mt_update method)
        # are coming from Qt and need to be non-incremental. (Don't know, should find out.)
        # So an initial fix might just ignore the "incremental" issue
        # except for deferring the mt_update effects themselves
        # (but I'm not sure if those effects are legal inside paintEvent!).
        
        if not self._painted:
            # called too early; not an error
            return
        # (Possible optim: it will often happen that none of the passed nodes
        #  have stored positions. We could check for this first and not bother
        #  to set up the painter in that case. I'm guessing this is not needed.)
        painter = QtGui.QPainter()
        painter.begin(self)
        try:
            for node in nodes:
                where = self._painted.get(node) # (x, y) or None
                if where:
                    print "mt debug fyi: repainting %r" % (node,) #### remove when works
                    x, y = where
                    _paintnode(node, painter, x, y, self.palette_widget,
                               option_holder = self)
                else:
                    print "mt debug fyi: NOT repainting %r" % (node,) #### remove when works
                continue
        finally:
            painter.end()
        return



    # WARNING: the following methods duplicate some of the code in
    # _our_QItemDelegate in the other MT implem, far above [now removed].
    # Also, they are mostly not yet used (still true, 070612). They might be
    # used to help make in-place node-label-edit work again.
    
    def createEditor(self, node):
        """
        Create and return a QLineEdit child widget to serve as an editor for the given node; initialize its text.
        """
        parent = self
        qle = QLineEdit(parent)
        self.setEditorData(qle, node)
        return qle

    def setEditorData(self, lineEdit, node):
        """
        copy the editable data from node to lineEdit
        """
        value = node.name
        lineEdit.setText(value)
        return

    def setModelData(self, lineEdit, node):
        """
        copy the editable data from lineEdit to node (if permitted); display a statusbar message about the result
        """
        # Note: try_rename checks node.rename_enabled()
        # BUG: try_rename doesn't handle unicode (though it seems to handle some non-ascii chars somehow)
        # Note: see similar code in a method in another class in this file.
        oldname = node.name
        ok, text = node.try_rename( lineEdit.text() )
        # if ok, text is the new text, perhaps modified;
        # if not ok, text is an error message
        if ok:
            msg = "Renamed node [%s] to [%s]" % (oldname, text) ##e need quote_html??
            self.statusbar_message(msg)
            ## self.modeltreegui.mt_update() #e might be redundant with caller; if so, might be a speed hit
        else:
            msg = "Can't rename node [%s]: %s" % (oldname, text) # text is reason why not
            self.statusbar_message(msg)
        return

    def updateEditorGeometry(self, editor, option, index):
        rect = option.rect
        rect.setX(rect.x() + _ICONSIZE[0])
        qfm = QFontMetrics(editor.font())
        width = qfm.width(editor.text()) + 10
        width = min(width, rect.width() - _ICONSIZE[0])
##        parent = self.parent()
        parent = self
        width = min(width, parent.width() - 50 - rect.x())
        rect.setWidth(width)
        editor.setGeometry(rect)
        return
