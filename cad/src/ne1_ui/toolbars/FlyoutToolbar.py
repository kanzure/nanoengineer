# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Ninad 2008-07-15: Created during an initial  refactoring of class CommandToolbar
Moved the common code out of Ui_CommandToolBar and CommandToolbar into this
class.

TODO:
"""
from foundation.wiki_help import QToolBar_WikiHelp
from PyQt4.Qt import QMenu
from PyQt4.Qt import Qt
from PyQt4.Qt import QPalette
from PyQt4.Qt import QToolButton
from PM.PM_Colors import getPalette
from commandToolbar.CommandToolbar_Constants import cmdTbarCmdAreaBtnColor
from utilities.icon_utilities import geticon

_superclass = QToolBar_WikiHelp

class FlyoutToolBar(QToolBar_WikiHelp):

    def __init__(self, parent):
        _superclass.__init__(self, parent)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.addSeparator()
        self.setAutoFillBackground(True)
        palette = self.getPalette()
        self.setPalette(palette)
        self._setExtensionButtonIcon()

    def clear(self):
        """
        Clear the actions within this toolbar AND also clear the
        submenu of the extension popup indicator ('>>") button of this toolbar.
        NOTE: QToolBar.clear() doesn't automatically clear the latter. (at least
        in Qt4.3) Because of this, there was a problem in fixing bug 2916.
        Apparently, the only way to access an extension button widget of a QToolBar
        is to access its children() and the 3rd button in the list is
        the extension indicator button, whose menu need to be cleared.
        """
        _superclass.clear(self)


        extension_menu = self.getExtensionMenu()

        if extension_menu is not None:
            extension_menu.clear()

    def getPalette(self):
        """
        Return a palette for Command Manager 'Commands area'(flyout toolbar)
        (Palette for Tool Buttons in command toolbar command area)
        """
        return getPalette(None,
                          QPalette.Button,
                          cmdTbarCmdAreaBtnColor
                          )

    def _setExtensionButtonIcon(self):
        """
        Sets the icon for the Flyout Toolbar extension button.
        The PNG image can be 24 (or less) pixels high by 10 pixels wide.
        """
        extension_button = self.getExtensionButton()
        extension_button.setIcon(geticon(
            "ui/actions/Command Toolbar/ExtensionButtonImage.png"))

    def getExtensionButton(self):
        """
        Returns the extension popup indicator toolbutton ">>"
        """

        btn = None
        clist = self.children()

        for c in range(0, len(clist)):
            if isinstance(clist[c], QToolButton):
                btn = clist[c]
                break


        return btn

    def getExtensionMenu(self):
        """
        Return the extension menu i.e. the submenu of the extension popup
        indicator button ">>" (if any)
        """
        toolbtn = self.getExtensionButton()

        if toolbtn is None:
            return None

        menu = None

        # Children of 1st QToolButton (3rd toolbar child) contains a single QMenu
        toolbtn_clist = toolbtn.children()

        if toolbtn_clist:
            extension_menu = toolbtn_clist[0] # The extension menu!
            if isinstance(extension_menu, QMenu):
                menu = extension_menu

        return menu


