# Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details.
"""
test_modelTreeGui.py - test code for modelTreeGui.py (non-working)

@author: Will
@version: $Id$
@copyright: 2006-2008 Nanorex, Inc.  See LICENSE file for details.

update, bruce 081215:

This test code has not worked for a long time.
To run it at all (in its old location at the end of modelTreeGui.py),
it's necessary to use ExecSubDir (see comment below for details).

Then, the test_api call below, specifically, has bugs:

- it might reveal a bug in ExecSubDir.py, which fails to modify argv
  to remove itself as an argument and fix argv[0] to the expected value;

- the test_api code fails due to no args to __init__ in api class.

But commenting it out (and running with /ExecSubDir.py modelTree/modelTreeGui.py)
also fails:

  AssertionError: too early to call image_directory()

which is due to a recent new requirement in initializing NE1.

There are other similar recent requirements.
All could be solved, by adding some startup code to be called by all test code,
but since I doubt this test code works even once they are solved (since it wasn't
maintained across major finishings and rewrites of this module), it's not worth
the time for now.

So I will move it into an outtakes file, from which it could be
revived and fixed later if desired. I will not bother to port the
imports from that file. Note that that file may be split into several
smaller ones in the near future.
"""

#### TODO: to figure out imports -- this code used to be at the end of the module modelTreeGui.py ####

# the only ones here are the ones no longer used in the main file after this was removed

from PyQt4.Qt import QMainWindow
from PyQt4.Qt import QGroupBox
from PyQt4.Qt import QApplication
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QHBoxLayout


class TestNode(Node_api):
    # WARNING: this test code has not been rerun or actively maintained
    # since modelTreeGui rewrite circa May 07 (or some time before).
    # And bruce 071025 moved drop_on and drop_on_ok from Node_api
    # to MT_DND_Target_API, but made no attempt to update this test code
    # except by removing those methods from it and Node_api, and wrapping
    # the node they're called on below in the same way as in real code above.
    def __init__(self, name, parent = None, icon = None, icon_hidden = None):
        self.open = False #bruce 070508 added this for api compliance; it's not otherwise used by test code
        self.hidden = False
        self._disabled = False
        self.name = name
        self.icon = icon
        self.icon_hidden = icon_hidden
        class FakeAssembly:
            def update_parts(self):
                pass
        self.assy = FakeAssembly() #bruce 070511 comment: this appears to never be used
        self.parentNode = parent
        if parent is not None:
            parent.members.append(self)
        self.members = [ ]
        self.picked = False
        if DEBUG0: self._verify_api_compliance()
    def showTree(self, indent = 0):
        """
        handy diagnostic
        """
        s = (indent * '\t') + repr(self)
        if self.picked: s += ' PICKED'
        print s
        for ch in self.members:
            ch.showTree(indent + 1)
    # beginning of official API
    def pick(self):
        self.picked = True
    def unpick(self):
        self.picked = False
    def apply2picked(self, func):
        if self.picked:
            func(self)
        for x in self.members:
            x.apply2picked(func)
##    def drop_on_ok(self, drag_type, nodes):
##        import sys, traceback
##        for node in nodes:
##            # don't drop stuff that's already here
##            if node in self.members:
##                traceback.print_stack(file = sys.stdout)
##                print self, nodes, node, self.members
##                print 'node is in children already'
##                return False, 'node is in children already'
##        # We can't drop things on chunks or jigs
##        if self.name.startswith("Chunk"):
##            traceback.print_stack(file = sys.stdout)
##            print self, node, self.members
##            print 'cannot drop on a chunk'
##            return False, 'cannot drop on a chunk'
##        if self.name.startswith("Jig"):
##            traceback.print_stack(file = sys.stdout)
##            print self, node, self.members
##            print 'cannot drop on a jig'
##            return False, 'cannot drop on a jig'
##        return True, None
##    def drop_on(self, drag_type, nodes):
##        previous_parents = { }
##        for node in nodes:
##            if drag_type == 'copy':
##                node = node.clone()
##            previous_parents[node] = node.parentNode
##            self.members.append(node)
##            node.parentNode = self
##            node.unpick()
##        if drag_type == 'move':
##            for node in nodes:
##                previous_parents[node].members.remove(node)
##        return [ ]
    def node_icon(self, display_prefs):
        # read up on display_prefs?
        if self.hidden:
            return self.icon_hidden
        else:
            return self.icon
    def is_disabled(self):
        return self._disabled
    # end of official API
    def clone(self):
        newguy = self.__class__(self.name + "-copy", None, self.icon, self.icon_hidden)
        newguy.hidden = self.hidden
        newguy._disabled = self._disabled
        newguy.members = self.members[:]
        return newguy
    def MT_kids(self, item_prefs = {}):
        return self.members
    def __repr__(self):
        return "<Node \"%s\">" % self.name

class TestClipboardNode(TestNode):
    def __init__(self, name):
        TestNode.__init__(self, name)
        self.iconEmpty = QPixmap("../images/clipboard-empty.png")
        self.iconFull = QPixmap("../images/clipboard-full.png")
        self.iconGray = QPixmap("../images/clipboard-gray.png")
        if DEBUG0: self._verify_api_compliance()

    def node_icon(self, display_prefs):
        if self.hidden:  # is the clipboard ever hidden??
            return self.iconGray
        elif self.members:
            return self.iconFull
        else:
            return self.iconEmpty

class TestNe1Model(Ne1Model_api):
    def __init__(self):
        self.untitledNode = TestNode("Untitled", None,
                                     QPixmap("../images/part.png"))
        self.clipboardNode = TestClipboardNode("Clipboard")
        if DEBUG0: self._verify_api_compliance()

    def get_topnodes(self):
        return [self.untitledNode, self.clipboardNode]

    def make_cmenuspec_for_set(self, nodeset, optflag):
        for node in nodeset:
            def thunk(str):
                def _thunk(str=str):
                    print str
                return _thunk
            if isinstance(node, TestNode):
                disableTuple = ('Disable', lambda node=node: self.cm_disable(node))
                if node.name.startswith("Chunk"):
                    disableTuple += ('disabled',)

                return [('Copy', lambda node=node: self.cm_copy(node)),
                        ('Cut', lambda node=node: self.cm_cut(node)),
                        ('Hide', lambda node=node: self.cm_hide(node)),
                        disableTuple,
                        None,
                        ('Delete', lambda node=node: self.cm_delete(node))]
            else:
                return [('A', thunk('A')),
                        ('B', thunk('B')),
                        None,
                        ('C', thunk('C'), 'disabled'),
                        ('D', thunk('D'))]
        return [ ]

    def complete_context_menu_action(self):
        # unpick all nodes
        for x in self.get_topnodes():
            x.apply2picked(lambda node: node.unpick())
        self.view.mt_update()

    def cm_copy(self, node):
        nodelist = self.view.topmost_selected_nodes()
        if node not in nodelist:
            nodelist.append(node)
        Node_as_MT_DND_Target(self.clipboardNode).drop_on('copy', nodelist)
        self.complete_context_menu_action()

    def cm_cut(self, node):
        nodelist = self.view.topmost_selected_nodes()
        if node not in nodelist:
            nodelist.append(node)
        Node_as_MT_DND_Target(self.clipboardNode).drop_on('move', nodelist)
        self.complete_context_menu_action()

    def cm_disable(self, node):
        node._disabled = not node._disabled
        self.complete_context_menu_action()

    def cm_hide(self, node):
        node.hidden = not node.hidden
        self.complete_context_menu_action()

    def cm_delete(self, node):
        node.parentNode.members.remove(node)
        self.complete_context_menu_action()

class TestGLPane:
    def gl_update(self):
        print "GLPane update"
class TestMainWindow:
    def __init__(self):
        self.glpane = TestGLPane()
        self.orientationWindow = None

class TestWrapper(QGroupBox):

    def __init__(self):
        QGroupBox.__init__(self)

        self.ne1model = ne1model = TestNe1Model()

        self.view = view = ModelTreeGui(TestMainWindow(), "Model tree", ne1model, self)
        view.mt_update()
        self.chunkNum = 2
        self.gbox = QGroupBox()
        vl = QVBoxLayout(self)
        vl.setSpacing(0)
        vl.setMargin(0)
        vl.addWidget(self.view)
        self.buttonLayout = hl = QHBoxLayout()
        hl.setSpacing(0)
        hl.setMargin(0)
        vl.addLayout(hl)
        self.buttonNum = 1
        for func in (self.addmol, self.addjig, self.selected):
            self.addButton(func)

    def addButton(self, func):
        button = QPushButton(func.__doc__)
        setattr(self, "button%d" % self.buttonNum, button)
        self.buttonNum += 1
        self.buttonLayout.addWidget(button)
        self.connect(button, SIGNAL('clicked()'), func)

    def addIconButton(self, icon, func):
        button = QPushButton()
        button.setIcon(icon)
        setattr(self, "button%d" % self.buttonNum, button)
        self.buttonNum += 1
        self.buttonLayout.addWidget(button)
        self.connect(button, SIGNAL('clicked()'), func)

    def addsomething(self, what):
        if what == "Chunk":
            icon = QPixmap('../images/moldefault.png')
            icon_h = QPixmap('../images/moldefault-hide.png')
        else:
            icon = QPixmap('../images/measuredistance.png')
            icon_h = QPixmap('../images/measuredistance-hide.png')
        chunk = TestNode("%s-%d" % (what, self.chunkNum),
                         self.ne1model.untitledNode, icon, icon_h)

        self.chunkNum += 1
        self.view.mt_update()

    def addmol(self):
        """
        Chunk
        """
        # This is equivalent to Part.addmol() in part.py
        self.addsomething("Chunk")

    def addjig(self):
        """
        Jig
        """
        self.addsomething("Jig")

    def selected(self):
        """
        Selected
        """
        print self.view.topmost_selected_nodes()

# ===

def test_api():
    # Test API compliance. If we remove all the functionality, pushing buttons shouldn't raise any
    # exceptions.
    global ModelTreeGui
##    global _our_QItemDelegate, _QtTreeModel
    ModelTreeGui = ModelTreeGui_api # in test code
##    del _our_QItemDelegate, _QtTreeModel

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.wrapper = TestWrapper()
        self.setCentralWidget(self.wrapper)
        self.resize(200, 300)
        self.wrapper.show()

if __name__ == "__main__":
    # To run this test code:
    # % cd cad/src
    # then
    # % ./ExecSubDir.py modelTree/modelTreeGui.py
    # --or--
    # % python ExecSubDir.py modelTree/modelTreeGui.py
    import sys
    if len(sys.argv) > 1:
        test_api()
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())

# end
