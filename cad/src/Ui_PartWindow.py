# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Ui_PartWindow.py provides the part window class.

$Id$

To do:
- Move HistoryWidget to be inside a QDockWidget,
or reconfigure splitter such that the history widget spans the full width
of the part window.
- Remove unused methods.
- Fix window title(s) when MDI is enabled.

History: 

- PartWindow and GridPosition classes moved here from MWSemantics.py.
  Mark 2007-06-27
"""

from PyQt4.Qt import Qt, QWidget, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt4.Qt import QTabWidget, QScrollArea, QSizePolicy
from GLPane import GLPane
from PropMgr_Constants import pmDefaultWidth, pmMaxWidth, pmMinWidth
from icon_utilities import geticon
from modelTree import modelTree
from qt4transition import qt4warnDestruction, qt4todo
import platform, env, os
from PlatformDependent import make_history_filename
from PM.PM_Utilities import printSizePolicy, printSizeHints
from PM.PM_Colors  import   getPalette
from debug import print_compact_traceback #bruce 070627 bugfix

from prefs_constants import captionFullPath_prefs_key

class _leftChannelTabWidget(QTabWidget): #bruce 070829 made this subclass re bug 2522
    def KLUGE_setGLPane(self, glpane):
        self._glpane = glpane
        return
    def removeTab(self, index):
        res = QTabWidget.removeTab(self, index)
            # note: AFAIK, res is always None
        if index != -1: # -1 happens!
            glpane = self._glpane
            glpane.gl_update_confcorner() # fix bug 2522 (try 2)
        return res
    pass

class Ui_PartWindow(QWidget):
    """
    Provides a "part window" composed of the model tree/property manager (tabs)
    on the left (referred to as the "left channel") and the glpane
    (with a history widget below) on the right. A resizable splitter 
    separates the left channel and the 3D graphics area.
    
    @note: I will be heavily modifying this file. Please tell me if you intend
    to work on this file. Mark 2007-12-31.
    """
    widgets = [] # For debugging purposes.

    def __init__(self, assy, parent):
        """
        Constructor for the part window.
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.assy = assy
        self.setWindowIcon(geticon("ui/border/Part.png"))
        self.updateWindowTitle()
        
        #Used in expanding or collapsing the Model Tree/ PM area
        self._previous_leftChannelWidgetWidth = pmDefaultWidth

        # The main layout for the part window is an HBoxLayout <pwHBoxLayout>.
        pwHBoxLayout = QHBoxLayout(self)
        pwHBoxLayout.setMargin(3) # Makes a difference; I like 3. -- Mark
        pwHBoxLayout.setSpacing(0)

        # ################################################################
        # <pwHSplitter> is the "main splitter" bw the MT/PropMgr and the 
        # glpane with the following children:
        # - <leftChannelWidget> (QWidget)
        # - <pwVSplitter> (QSplitter)

        self.pwHSplitter = pwHSplitter = QSplitter(Qt.Horizontal)
        pwHSplitter.setObjectName("main splitter")
        pwHSplitter.setHandleWidth(3) # The splitter handle is 3 pixels wide.
        pwHBoxLayout.addWidget(pwHSplitter)

        # ##################################################################
        # <leftChannelWidget> - the container of all widgets left of the 
        # main splitter:
        # - <leftChannelTabWidget> (QTabWidget), with children:
        #    - <modelTreeTab> (QWidget)
        #    - <propertyManagerScrollArea> (QScrollArea), with the child:
        #       - <propertyManagerTab> (QWidget)

        self.leftChannelWidget = leftChannelWidget = QWidget(parent)
        leftChannelWidget.setObjectName("leftChannelWidget")
        leftChannelWidget.setMinimumWidth(pmMinWidth)
        leftChannelWidget.setMaximumWidth(pmMaxWidth)
        leftChannelWidget.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Fixed),
                        QSizePolicy.Policy(QSizePolicy.Expanding)))

        # This layout will contain only the leftChannelTabWidget (done below).
        leftChannelVBoxLayout = QVBoxLayout(leftChannelWidget)
        leftChannelVBoxLayout.setMargin(0)
        leftChannelVBoxLayout.setSpacing(0)

        pwHSplitter.addWidget(leftChannelWidget)

        # Makes it so leftChannelWidget is not collapsible.
        pwHSplitter.setCollapsible (0, False)

        # Left Channel Tab Widget - a QTabWidget that contains the MT and PropMgr.
        # I'll rename this later since this isn't a good name. It is also
        # used in other files. --Mark
        #
        # Note [bruce 070829]: to fix bug 2522 I need to intercept
        # self.leftChannelTabWidget.removeTab, so I made it a subclass of QTabWidget.
        # It needs to know the GLPane, but that's not created yet, so we set
        # it later using KLUGE_setGLPane (below).
        self.leftChannelTabWidget = _leftChannelTabWidget() 
           # _leftChannelTabWidget subclasses QTabWidget
           # NOTE: No parent supplied. Could this be the source of the
           # minor vsplitter resizing problem I was trying to resolve a few
           # months ago?  Try supplying a parent later. Mark 2008-01-01
        self.leftChannelTabWidget.setObjectName("leftChannelTabWidget")
        self.leftChannelTabWidget.setCurrentIndex(0)
        self.leftChannelTabWidget.setAutoFillBackground(True)

        # Create the model tree "tab" widget. It will contain the MT GUI widget.
        # Set the tab icon, too.
        self.modelTreeTab = QWidget()
        self.modelTreeTab.setObjectName("modelTreeTab")
        self.leftChannelTabWidget.addTab(self.modelTreeTab,
                                   geticon("ui/modeltree/Model_Tree"), "") 

        modelTreeTabLayout = QVBoxLayout(self.modelTreeTab)
        modelTreeTabLayout.setMargin(0)
        modelTreeTabLayout.setSpacing(0)

        # Create the model tree (GUI) and add it to the tab layout.
        self.modelTree = modelTree(self.modelTreeTab, parent)
        self.modelTree.modelTreeGui.setObjectName("modelTreeGui")
        modelTreeTabLayout.addWidget(self.modelTree.modelTreeGui)

        # Create the property manager "tab" widget. It will contain the PropMgr
        # scroll area, which will contain the property manager and all its 
        # widgets.
        self.propertyManagerTab = QWidget()
        self.propertyManagerTab.setObjectName("propertyManagerTab")

        self.propertyManagerScrollArea = QScrollArea(self.leftChannelTabWidget)
        self.propertyManagerScrollArea.setObjectName("propertyManagerScrollArea")
        self.propertyManagerScrollArea.setWidget(self.propertyManagerTab)
        self.propertyManagerScrollArea.setWidgetResizable(True) 
        # Eureka! 
        # setWidgetResizable(True) will resize the Property Manager (and its contents)
        # correctly when the scrollbar appears/disappears. It even accounts correctly for 
        # collapsed/expanded groupboxes! Mark 2007-05-29

        # Add the property manager scroll area as a "tabbed" widget. 
        # Set the tab icon, too.
        self.leftChannelTabWidget.addTab(self.propertyManagerScrollArea, 
                                   geticon("ui/modeltree/Property_Manager"), "")

        # Finally, add the "leftChannelTabWidget" to the left channel layout.
        leftChannelVBoxLayout.addWidget(self.leftChannelTabWidget)

        # ##################################################################
        # <pwVSplitter> - a splitter comprising of all widgets to the right
        # of the main splitter with children:
        # - <glpane> (GLPane)
        # - <history_object> (HistoryWidget)

        self.pwVSplitter = pwVSplitter = QSplitter(Qt.Vertical, pwHSplitter)
        pwVSplitter.setObjectName("pwVSplitter")

        # Create the glpane and make it a child of the (vertical) splitter.
        self.glpane = GLPane(assy, self, 'glpane name', parent)
        self.leftChannelTabWidget.KLUGE_setGLPane(self.glpane) # help fix bug 2522 [bruce 070829]
        qt4warnDestruction(self.glpane, 'GLPane of PartWindow')
        pwVSplitter.addWidget(self.glpane)

        from HistoryWidget import HistoryWidget

        histfile = make_history_filename() #@@@ ninad 061213 This is likely a new bug for multipane concept 
        #as each file in a session will have its own history widget
        qt4todo('histfile = make_history_filename()')

        #bruce 050913 renamed self.history to self.history_object, and deprecated direct access
        # to self.history; code should use env.history to emit messages, self.history_widget
        # to see the history widget, or self.history_object to see its owning object per se
        # rather than as a place to emit messages (this is rarely needed).
        self.history_object = HistoryWidget(self, filename = histfile, mkdirs = 1)
            # this is not a Qt widget, but its owner;
            # use self.history_widget for Qt calls that need the widget itself.
        self.history_widget = self.history_object.widget
        self.history_widget.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Ignored)

            #bruce 050913, in case future code splits history widget (as main window subwidget)
            # from history message recipient (the global object env.history).

        env.history = self.history_object #bruce 050727, revised 050913

        pwVSplitter.addWidget(self.history_widget)

        pwHSplitter.addWidget(pwVSplitter)

        if 0: #@ Debugging code related to bug 2424. Mark 2007-06-27.
            self.widgets.append(self.pwHSplitter)
            self.widgets.append(leftChannelWidget)
            self.widgets.append(self.leftChannelTabWidget)
            self.widgets.append(self.modelTreeTab)
            self.widgets.append(self.modelTree.modelTreeGui)
            self.widgets.append(self.propertyManagerScrollArea)
            self.widgets.append(self.propertyManagerTab)
            self.widgets.append(self.pwVSplitter)

            print "PartWindow.__init__() ======================================"
            self.printSizeInfo()

            # The following call to the QSplitter.sizes() function returns zero for 
            # the width of the glpane. I consider this "our bug". It should be looked
            # into at later time. Mark 2007-06-27.
            print "MAIN HSPLITTER SIZES: ", pwHSplitter.sizes()
        
    def updateWindowTitle(self, changed = False): #by mark; bruce 050810 revised this in several ways, fixed bug 785
        """
        Update the window title (caption) at the top of the of the part window. 
        Example:  "partname.mmp"
        
        This implements the standard way most applications indicate that a
        document has unsaved changes. On Mac OS X the close button will have
        a modified look; on other platforms the window title will have
        an '*' (asterisk).
        
        @param changed: If True, the document has unsaved changes.
        @type  changed: boolean
        
        @see: U{B{windowTitle}<http://doc.trolltech.com/4/qwidget.html#windowTitle-prop>},
              U{B{windowModified}<http://doc.trolltech.com/4/qwidget.html#windowModified-prop>}
        """
        caption_fullpath = env.prefs[captionFullPath_prefs_key]

        try:
            # self.assy.filename is always an empty string, even after a
            # file has been opened with a complete name. Need to ask Bruce 
            # about this problem, resulting in a bug (i.e. the window title
            # is always "Untitled". Mark 2008-01-02.
            junk, basename = os.path.split(self.assy.filename)
            assert basename # it's normal for this to fail, when there is no file yet

            if caption_fullpath:
                partname = os.path.normpath(self.assy.filename) #fixed bug 453-1 ninad060721
            else:
                partname = basename

        except:
            partname = 'Untitled'

        # If you're wondering about the "[*]" placeholder below, see:
        # http://doc.trolltech.com/4/qwidget.html#windowModified-prop
        self.setWindowTitle(self.trUtf8(partname + '[*]'))
        self.setWindowModified(changed)
        return
    
    def collapseLeftChanneWidget(self):
        """
        Collapse the left channel widget.
	"""
        self._previous_leftChannelWidgetWidth = self.leftChannelWidget.width()
        self.leftChannelWidget.setFixedWidth(0)
        self.pwHSplitter.setMaximumWidth(self.leftChannelWidget.width())

    def expandLeftChanneWidget(self):
        """
        Expand the let channel widget.
        
        @see: L{MWsemantics._showFullScreenCommonCode()} for an example 
        showing how it is used.
	"""
        if self._previous_leftChannelWidgetWidth == 0:
            self._previous_leftChannelWidgetWidth = pmDefaultWidth
        self.leftChannelWidget.setMaximumWidth(
            self._previous_leftChannelWidgetWidth)  
        self.pwHSplitter.setMaximumWidth(self.leftChannelWidget.width())

    def collapseHistoryWidget(self):
        """
        Collapse the history widget area. 
	"""
        self.history_object.collapseWidget()	

    def expandHistoryWidget(self):
        """
        Expand the history widget area
	"""
        self.history_object.expandWidget()	

    def printSizeInfo(self):
        """
        Used to print the sizeHints and sizePolicy of left channel widgets.
	I'm using this to help resolve bug 2424:
	"Allow resizing of splitter between Property Manager and Graphics window."
	-- Mark
	"""
        for widget in self.widgets:
            printSizePolicy(widget)
            #printSizeHints(widget)
            #print "\n"

    def setRowCol(self, row, col):
        self.row, self.col = row, col

    def updatePropertyManagerTab(self, tab): #Ninad 061207
        "Update the Properties Manager tab with 'tab' "

        self.parent.glpane.gl_update_confcorner() #bruce 070627, since PM affects confcorner appearance

        if self.propertyManagerScrollArea.widget():
            #The following is necessary to get rid of those C object deleted errors (and the resulting bugs)
            lastwidgetobject = self.propertyManagerScrollArea.takeWidget() 
            if lastwidgetobject:
                #bruce 071018 revised this code; see my comment on same code in PM_Dialog
                try:
                    lastwidgetobject.update_props_if_needed_before_closing
                except AttributeError:
                    if 1 or platform.atom_debug:
                        msg1 = "Last PropMgr %r doesn't have method" % lastwidgetobject
                        msg2 =" update_props_if_needed_before_closing. That's"
                        msg3 = " OK (for now, only implemented for Plane PM). "
                        msg4 = "Ignoring Exception"
                        print_compact_traceback(msg1 + msg2 + msg3 + msg4)
                else:
                    lastwidgetobject.update_props_if_needed_before_closing()

            lastwidgetobject.hide() # @ ninad 061212 perhaps hiding the widget is not needed

        self.leftChannelTabWidget.removeTab(self.leftChannelTabWidget.indexOf(self.propertyManagerScrollArea))

        #Set the PropertyManager tab scroll area to the appropriate widget .at
        self.propertyManagerScrollArea.setWidget(tab)

        self.leftChannelTabWidget.addTab(self.propertyManagerScrollArea, 
                                   geticon("ui/modeltree/Property_Manager"), "")

        self.leftChannelTabWidget.setCurrentIndex(self.leftChannelTabWidget.indexOf(self.propertyManagerScrollArea))

    def KLUGE_current_PropertyManager(self): #bruce 070627; revised 070829 as part of fixing bug 2523
        """
        Return the current Property Manager widget (whether or not its tab is
        chosen, but only if it has a tab), or None if there is not one.
           WARNING: This method's existence (not only its implementation) is a kluge,
        since the right way to access that would be by asking the "command sequencer";
        but that's not yet implemented, so this is the best we can do for now.
        Also, it would be better to get the top command and talk to it, not its PM
        (a QWidget). Also, whatever calls this will be making assumptions about that PM
        which are really only the command's business. So in short, every call of this is
        in need of cleanup once we have a working "command sequencer". (That's true of many
        things related to PMs, not only this method.)
           WARNING: The return values are (presumably) widgets, but they can also be mode objects
        and generator objects, due to excessive use of multiple inheritance in the current PM code.
        So be careful what you do with them -- they might have lots of extra methods/attrs,
        and setting your own attrs in them might mess things up.
        """
        res = self.propertyManagerScrollArea.widget()
        if not hasattr(res, 'done_btn'):
            # not sure what widget this is otherwise, but it is a widget
            # (not None) for the default mode, at least on startup, so just
            # return None in this case
            return None
        # Sometimes this PM remains present from a prior command, even when
        # there is no longer a tab for the PM. As part of fixing bug 2523
        # we have to avoid returning it in that case. How we do that is a kluge,
        # but hopefully this entire kluge function can be dispensed with soon.
        # This change also fixes bug 2522 on the Mac (but not on Windows --
        # for that, we needed to intercept removeTab in separate code above).
        index = self.leftChannelTabWidget.indexOf(self.propertyManagerScrollArea)
        if index == -1:
            return None
        # Due to bugs in other code, sometimes the PM tab is left in place,
        # though the PM itself is hidden. To avoid finding the PM in that case,
        # also check whether it's hidden. This will fix the CC part of a new bug
        # just reported by Keith in email (when hitting Ok in DNA Gen).
        if res.isHidden():
            return None
        return res

    def dismiss(self):
        self.parent.removePartWindow(self)

class GridPosition_DEPRECATED:
    """
    Provides a grid layout object for the support of an multiple document
    interface (MDI) in NE1. It is not currently used since MDI is not
    supported yet.
    
    @deprecated: We will be using Qt's QWorkspace class to support MDI.
    Mark 2008-01-01.
    """
    def __init__(self):
        self.row, self.col = 0, 0
        self.availableSlots = [ ]
        self.takenSlots = { }

    def next(self, widget):
        if len(self.availableSlots) > 0:
            row, col = self.availableSlots.pop(0)
        else:
            row, col = self.row, self.col
            if row == col:
                # when on the diagonal, start a new self.column
                self.row = 0
                self.col = col + 1
            elif row < col:
                # continue moving down the right edge until we're about
                # to hit the diagonal, then start a new bottom self.row
                if row == col - 1:
                    self.row = row + 1
                    self.col = 0
                else:
                    self.row = row + 1
            else:
                # move right along the bottom edge til you hit the diagonal
                self.col = col + 1
        self.takenSlots[widget] = (row, col)
        return row, col

    def removeWidget(self, widget):
        rc = self.takenSlots[widget]
        self.availableSlots.append(rc)
        del self.takenSlots[widget]



