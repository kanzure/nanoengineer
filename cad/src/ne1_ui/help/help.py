# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
help.py - help dialog used for mouse controls and keyboard shortcuts

$Id$

History:

Rewritten by Mark as a minimal help facility for Alpha 6.

bruce 071214 renamed class Help -> Ne1HelpDialog,
so uses are findable by text search. The name HelpDialog
was taken (as the module from which we import Ui_HelpDialog).

TODO:

The module should also be renamed, in case we want to use "help"
in a more general way, e.g. as a package name. [bruce 071214 comment]
"""

__author__ = "Josh"


import os, sys

from PyQt4.Qt import QWidget
from PyQt4.Qt import SIGNAL

from ne1_ui.help.HelpDialog import Ui_HelpDialog
from utilities.icon_utilities import geticon

class Ne1HelpDialog(QWidget, Ui_HelpDialog):
    """
    The Help dialog used for mouse controls and keyboard shortcuts
    """
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)
        self.connect(self.help_tab,SIGNAL("currentChanged(int)"),self.setup_current_page)
        self.connect(self.close_btn,SIGNAL("clicked()"),self.close)

        self.setWindowIcon(geticon('ui/border/MainWindow.png'))

        self._setup_mouse_controls_page()
        self.help_tab.setCurrentIndex(0)

        return

    def showDialog(self, pagenum):
        """
        Display the Help dialog with either the Mouse Controls or Keyboard Shortcuts page
        pagenum is the page number, where:
        0 = Mouse Controls
        1 = Keyboard Shortcuts
        2 = Selection Shortcuts
        """
        self.help_tab.setCurrentIndex(pagenum) # Sends signal to setup_current_page()

        # To make sure the Help dialog is displayed on top, we hide, then show it.
        self.hide() # Mark 2007-06-01
        self.show() # Non-modal
        return

    ###### Private methods ###############################

    def _setup_mouse_controls_page(self):
        """
        Setup the Mouse Controls help page.
        """
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        if sys.platform == 'darwin':
            htmlDoc = os.path.normpath(filePath + '/../doc/mousecontrols-mac.htm')
        else:
            htmlDoc = os.path.normpath(filePath + '/../doc/mousecontrols.htm')

        # Make sure help document exists.  If not, display msg in textbrowser.
        if os.path.exists(htmlDoc):
            self.mouse_controls_textbrowser.setHtml(open(htmlDoc).read())
        else:
            msg =  "Help file " + htmlDoc + " not found."
            self.mouse_controls_textbrowser.setPlainText(msg)

    def _setup_keyboard_shortcuts_page(self):
        """
        Setup the Keyboard Shortcuts help page.
        """
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))

        if sys.platform == 'darwin':
            htmlDoc = os.path.normpath(filePath + '/../doc/keyboardshortcuts-mac.htm')
        else:
            htmlDoc = os.path.normpath(filePath + '/../doc/keyboardshortcuts.htm')

        # Make sure help document exists.  If not, display msg in textbrowser.
        if os.path.exists(htmlDoc):
            self.keyboard_shortcuts_textbrowser.setHtml(open(htmlDoc).read())
        else:
            msg =  "Help file " + htmlDoc + " not found."
            self.keyboard_shortcuts_textbrowser.setPlainText(msg)

    def _setup_selection_shortcuts_page(self):
        """
        Setup the Selection Shortcuts help page.
        """
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))

        if sys.platform == 'darwin':
            htmlDoc = os.path.normpath(filePath + '/../doc/selectionshortcuts-mac.htm')
        else:
            htmlDoc = os.path.normpath(filePath + '/../doc/selectionshortcuts.htm')

        # Make sure help document exists.  If not, display msg in textbrowser.
        if os.path.exists(htmlDoc):
            self.selection_shortcuts_textbrowser.setHtml(open(htmlDoc).read())
        else:
            msg =  "Help file " + htmlDoc + " not found."
            self.selection_shortcuts_textbrowser.setPlainText(msg)

    def setup_current_page(self, currentTabIndex):
        pagenumber = currentTabIndex
        if pagenumber is 0:
            self._setup_mouse_controls_page()
        elif pagenumber is 1:
            self._setup_keyboard_shortcuts_page()
        elif pagenumber is 2:
            self._setup_selection_shortcuts_page()
        else:
            print 'Error: Help page unknown: ', pagenumber
