# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
Ui_CommandToolbar.py - UI and hardcoded content for the Command Toolbar

@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.


Module classification: [bruce 071228]

At present, this hardcodes the set of main toolbuttons
('Build', 'Tools', etc) and at least some of the specific list
of subcommands under each one.

So clearly it belongs in ne1_ui, even though it ought to be
refactored into that part (the specific contents of NE1's
CommandToolbar, in ne1_ui) and a more general part (probably
for a toplevel 'CommandToolbar' package) which could set up any similar
toolbutton hierarchy, given a specification for its content and
ordering (or leave some of that to be added later by external calls --
it may do some of that now, but I can't tell from the code or comments).

(After this future refactoring, the general part, either a QWidget subclass
like now, or owning one, would construct the toolbutton hierarchy
semi-automatically from a known set of command modules, either specified to it
as a constructor argument or passed to a later setup method (all at once or
incrementally).)

Accordingly, due to the hardcoded UI layout and contents,
this is classified into ne1_ui for now, though its subclass is not
(see comments there).


History:

ninad 070125: created this file, moved and modified relevant code from
CommandManager to this file.

mark 20071226: renamed from Ui_CommandManager to Ui_CommandToolbar.

TODO: Code cleanup planned for Alpha 10 (lower priority) -- Ninad 2007-09-11

"""

from PyQt4    import QtGui
from PyQt4.Qt import QWidget
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QButtonGroup
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QSize
from PyQt4.Qt import Qt
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QString
from PyQt4.Qt import QPalette

from utilities.icon_utilities import geticon
from foundation.whatsthis_utilities import fix_QAction_whatsthis
from foundation.wiki_help import QToolBar_WikiHelp
from commandToolbar.CommandToolbar_Constants import cmdTbarCntrlAreaBtnColor
from commandToolbar.CommandToolbar_Constants import cmdTbarSubCntrlAreaBtnColor
from commandToolbar.CommandToolbar_Constants import cmdTbarCmdAreaBtnColor

from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForCommandToolbarBuildButton
from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForCommandToolbarToolsButton
from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForCommandToolbarMoveButton
from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForCommandToolbarSimulationButton
from ne1_ui.WhatsThisText_for_CommandToolbars import whatsThisTextForCommandToolbarInsertButton

from PM.PM_Colors import getPalette

from ne1_ui.toolbars.FlyoutToolbar import FlyoutToolBar

#debug flag for bug 2633 (in Qt4.3 all control area buttons collapse into a
#single button. The following flag, if True, sets the controlarea as a
#QWidget instead of a QToolbar. As of 2008-02-20, we are not using any of the
#QToolbar features to make the control area a Qtoolbar. (In future we will
#use some features such as adding new actions to the toolbar or autohiding
#actions/ items that don't fit the specified width (accessible via '>>'
#indicator). The command toolbar code is likely to be revised post FNANO08
#that time, this can be cleaned up further. Till then, the default
#implementation will use controlarea as a QWidget object instead of QToolbar
DEFINE_CONTROL_AREA_AS_A_QWIDGET = True

class Ui_CommandToolbar( QWidget ):
    """
    This provides most of the User Interface for the command toolbar
    called in CommandToolbar class.
    """
    def __init__(self, win):
        """
        Constructor for class Ui_CommandToolbar.

        @param win: Mainwindow object
        @type  win: L{MWsemantics}
        """
        QWidget.__init__(self)

        self.win = win

    def setupUi(self):
        """
        Setup the UI for the command toolbar.
        """
        #ninad 070123 : It's important to set the Vertical size policy of the
        # cmd toolbar widget. otherwise the flyout QToolbar messes up the
        #layout (makes the command toolbar twice as big)
        #I have set the vertical policy as fixed. Works fine. There are some
        # MainWindow resizing problems for but those are not due to this
        #size policy AFAIK
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout_cmdtoolbar = QHBoxLayout(self)
        layout_cmdtoolbar.setMargin(2)
        layout_cmdtoolbar.setSpacing(2)

        #See comment at the top for details about this flag
        if DEFINE_CONTROL_AREA_AS_A_QWIDGET:
            self.cmdToolbarControlArea = QWidget(self)
        else:
            self.cmdToolbarControlArea = QToolBar_WikiHelp(self)

        self.cmdToolbarControlArea.setAutoFillBackground(True)

        self.ctrlAreaPalette = self.getCmdMgrCtrlAreaPalette()
        self.cmdToolbarControlArea.setPalette(self.ctrlAreaPalette)

        self.cmdToolbarControlArea.setMinimumHeight(62)
        self.cmdToolbarControlArea.setMinimumWidth(380)
        self.cmdToolbarControlArea.setSizePolicy(QSizePolicy.Fixed,
                                                 QSizePolicy.Fixed)

        #See comment at the top for details about this flag
        if DEFINE_CONTROL_AREA_AS_A_QWIDGET:
            layout_controlArea = QHBoxLayout(self.cmdToolbarControlArea)
            layout_controlArea.setMargin(0)
            layout_controlArea.setSpacing(0)

        self.cmdButtonGroup = QButtonGroup()
        btn_index = 0

        for name in ('Build', 'Insert', 'Tools', 'Move', 'Simulation'):
            btn = QToolButton(self.cmdToolbarControlArea)
            btn.setObjectName(name)
            btn.setMinimumWidth(75)
            btn.setMaximumWidth(75)
            btn.setMinimumHeight(62)
            btn.setAutoRaise(True)
            btn.setCheckable(True)
            btn.setAutoExclusive(True)
            iconpath = "ui/actions/Command Toolbar/ControlArea/" + name + ".png"
            btn.setIcon(geticon(iconpath))
            btn.setIconSize(QSize(22, 22))
            btn.setText(name)
            btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            btn.setPalette(self.ctrlAreaPalette)
            self.cmdButtonGroup.addButton(btn, btn_index)
            btn_index += 1
            #See comment at the top for details about this flag
            if DEFINE_CONTROL_AREA_AS_A_QWIDGET:
                layout_controlArea.addWidget(btn)
            else:
                self.cmdToolbarControlArea.layout().addWidget(btn)
                #following has issues. so not adding widget directly to the
                #toolbar. (instead adding it in its layout)-- ninad 070124
                ##self.cmdToolbarControlArea.addWidget(btn)

        layout_cmdtoolbar.addWidget(self.cmdToolbarControlArea)

        #Flyout Toolbar in the command toolbar
        self.flyoutToolBar = FlyoutToolBar(self)

        layout_cmdtoolbar.addWidget(self.flyoutToolBar)

        #ninad 070116: Define a spacer item. It will have the exact geometry
        # as that of the flyout toolbar. it is added to the command toolbar
        # layout only when the Flyout Toolbar is hidden. It is required
        # to keep the 'Control Area' widget fixed in its place (otherwise,
        #after hiding the flyout toolbar, the layout adjusts the position of
        #remaining widget items)

        self.spacerItem = QSpacerItem(0,
                                      0,
                                      QtGui.QSizePolicy.Expanding,
                                      QtGui.QSizePolicy.Minimum)
        self.spacerItem.setGeometry = self.flyoutToolBar.geometry()

        for btn in self.cmdButtonGroup.buttons():
            if str(btn.objectName()) == 'Build':
                btn.setMenu(self.win.buildStructuresMenu)
                btn.setPopupMode(QToolButton.MenuButtonPopup)
                btn.setToolTip("Build Commands")
                whatsThisTextForCommandToolbarBuildButton(btn)
            if str(btn.objectName()) == 'Insert':
                btn.setMenu(self.win.insertMenu)
                btn.setPopupMode(QToolButton.MenuButtonPopup)
                btn.setToolTip("Insert Commands")
                whatsThisTextForCommandToolbarInsertButton(btn)
            if str(btn.objectName()) == 'Tools':
                #fyi: cmd stands for 'command toolbar' - ninad070406
                self.win.cmdToolsMenu = QtGui.QMenu(self.win)
                self.win.cmdToolsMenu.addAction(self.win.toolsExtrudeAction)
                self.win.cmdToolsMenu.addAction(self.win.toolsFuseChunksAction)
                self.win.cmdToolsMenu.addSeparator()
                self.win.cmdToolsMenu.addAction(self.win.modifyMergeAction)
                self.win.cmdToolsMenu.addAction(self.win.modifyMirrorAction)
                self.win.cmdToolsMenu.addAction(self.win.modifyInvertAction)
                self.win.cmdToolsMenu.addAction(self.win.modifyStretchAction)
                btn.setMenu(self.win.cmdToolsMenu)
                btn.setPopupMode(QToolButton.MenuButtonPopup)
                btn.setToolTip("Tools")
                whatsThisTextForCommandToolbarToolsButton(btn)
            if str(btn.objectName()) == 'Move':
                self.win.moveMenu = QtGui.QMenu(self.win)
                self.win.moveMenu.addAction(self.win.toolsMoveMoleculeAction)
                self.win.moveMenu.addAction(self.win.rotateComponentsAction)
                self.win.moveMenu.addSeparator()
                self.win.moveMenu.addAction(
                    self.win.modifyAlignCommonAxisAction)
                ##self.win.moveMenu.addAction(\
                ##    self.win.modifyCenterCommonAxisAction)
                btn.setMenu(self.win.moveMenu)
                btn.setPopupMode(QToolButton.MenuButtonPopup)
                btn.setToolTip("Move Commands")
                whatsThisTextForCommandToolbarMoveButton(btn)
            if str(btn.objectName()) == 'Dimension':
                btn.setMenu(self.win.dimensionsMenu)
                btn.setPopupMode(QToolButton.MenuButtonPopup)
                btn.setToolTip("Dimensioning Commands")
            if str(btn.objectName()) == 'Simulation':
                btn.setMenu(self.win.simulationMenu)
                btn.setPopupMode(QToolButton.MenuButtonPopup)
                btn.setToolTip("Simulation Commands")
                whatsThisTextForCommandToolbarSimulationButton(btn)

            # Convert all "img" tags in the button's "What's This" text
            # into abs paths (from their original rel paths).
            # Partially fixes bug 2943. --mark 2008-12-07
            # [bruce 081209 revised this -- removed mac = False]
            fix_QAction_whatsthis(btn)
        return

    def truncateText(self, text, length = 12, truncateSymbol = '...'):
        """
        Truncates the tooltip text with the given truncation symbol
        (three dots) in the case
        """

        #ninad 070201 This is a temporary fix. Ideally it should show the whole
        #text in the  toolbutton. But there are some layout / size policy
        #problems because of which the toolbar height increases after you print
        #tooltip text on two or more lines. (undesirable effect)

        if not text:
            print "no text to truncate. Returning"
            return

        truncatedLength  = length - len(truncateSymbol)

        if len(text) > length:
            return text[:truncatedLength] + truncateSymbol
        else:
            return text



    def wrapToolButtonText(self, text):
        """
        Add a newline character at the end of each word in the toolbutton text
        """
        #ninad 070126 QToolButton lacks this method. This is not really a
        #'word wrap' but OK for now.

        #@@@ ninad 070126. Not calling this method as it is creating an annoying
        #resizing problem in the Command toolbar layout. Possible solution is
        #to add a spacer item in a vbox layout to the command toolbar layout

        stringlist = text.split(" ", QString.SkipEmptyParts)
        text2 = QString()
        if len(stringlist) > 1:
            for l in stringlist:
                text2.append(l)
                text2.append("\n")
            return text2

        return None

    ##==================================================================##
    #color palettes (UI stuff) for different command toolbar areas

    def getCmdMgrCtrlAreaPalette(self):
        """ Return a palette for Command Manager control area
        (Palette for Tool Buttons in command toolbar control area)
        """
        #See comment at the top for details about this flag
        if DEFINE_CONTROL_AREA_AS_A_QWIDGET:
            return getPalette(None,
                              QPalette.Window,
                              cmdTbarCntrlAreaBtnColor
                              )
        else:
            return getPalette(None,
                              QPalette.Button,
                              cmdTbarCntrlAreaBtnColor
                              )


    def getCmdMgrSubCtrlAreaPalette(self):
        """ Return a palette for Command Manager sub control area
        (Palette for Tool Buttons in command toolbar sub control area)
        """
        #Define the color role. Make sure to apply color to QPalette.Button
        #instead of QPalette.Window as it is a QToolBar. - ninad 20070619

        return getPalette(None,
                          QPalette.Button,
                          cmdTbarSubCntrlAreaBtnColor
                          )

    def getCmdMgrCommandAreaPalette(self):
        """ Return a palette for Command Manager 'Commands area'(flyout toolbar)
        (Palette for Tool Buttons in command toolbar command area)
        """
        return self.flyoutToolBar.getPalette()
