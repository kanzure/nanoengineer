# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
$Id$
"""

from PyQt4 import QtGui
from foundation.wiki_help import QToolBar_WikiHelp
from debug_prefs import debug_pref, Choice_boolean_False

def setupUi(win, toolbarArea):
    """
    Creates and populates the "Build Structures" toolbar in the main window.

    @param win: NE1's main window object.
    @type  win: U{B{QMainWindow}<http://doc.trolltech.com/4/qmainwindow.html>}
    """
    
    # Create the "Build Structures" toolbar.
    win.buildStructuresToolBar = QToolBar_WikiHelp(win)
    win.buildStructuresToolBar.setEnabled(True)
    win.buildStructuresToolBar.setObjectName("buildStructuresToolBar")
    win.addToolBar(toolbarArea, win.buildStructuresToolBar)
    
    # Populate the "Build Structures" toolbar.
    win.buildStructuresToolBar.addAction(win.toolsDepositAtomAction)
    win.buildStructuresToolBar.addAction(win.buildDnaAction)
    
    #  New CNT Builder or old Nanotube Generator?
    if debug_pref("Use new 'Build > CNT' nanotube builder? (next session)", 
                  Choice_boolean_False, 
                  non_debug = True,
                  prefs_key = "A10 devel/Nanotube generator"):
        # New "Build > CNT", experimental. --Mark 2008-03-10
        win.buildStructuresToolBar.addAction(win.buildCntAction) 
    else:
        # Original "Build > Nanotube"
        win.buildStructuresToolBar.addAction(win.insertNanotubeAction)
    
    win.buildStructuresToolBar.addAction(win.insertGrapheneAction)
    win.buildStructuresToolBar.addAction(win.toolsCookieCutAction)
    
    # This adds the Atom Generator example for developers.
    win.buildStructuresToolBar.addAction(win.insertAtomAction)
    
    # This adds the Peptide Generator (piotr 080304)
    win.buildStructuresToolBar.addAction(win.insertPeptideAction)

def retranslateUi(win):
    """
    Assigns the I{window title} property of the "Build Structures" toolbar.
    
    The window title of the "Build Structures" toolbar will be displayed in the
    popup menu under "View > Toolbars".
    """
    win.buildStructuresToolBar.setWindowTitle(
        QtGui.QApplication.translate(
            "MainWindow", "Build Structures", 
            None, QtGui.QApplication.UnicodeUTF8))
    win.buildStructuresToolBar.setToolTip(
        QtGui.QApplication.translate(
            "MainWindow", "Build Structures Toolbar", 
            None, QtGui.QApplication.UnicodeUTF8))
