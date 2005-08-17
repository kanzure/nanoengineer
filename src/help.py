# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
$Id$

History:

Rewritten by Mark as a mininal help facility for Alpha 6.

"""

__author__ = "Josh"


from qt import *
from HelpDialog import HelpDialog
import os, sys

class Help(HelpDialog):
    '''The Help dialog used for mouse controls and keyboard shortcuts
    '''
       
    def __init__(self):
        HelpDialog.__init__(self)
        return
    
    def showDialog(self, pagenum):
        '''Display the Help dialog with either the Mouse Controls or Keyboard Shortcuts page
        pagenum is the page number, where:
        0 = Mouse Controls
        1 = Keyboard Shortcuts
        '''
        self.help_tab.setCurrentPage(pagenum) # Sends signal to setup_current_page()
        self.show() # Non-modal 
        return

    ###### Private methods ###############################
    
    def _setup_mouse_controls_page(self):
        ''' Setup the Mouse Controls help page.
        '''
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        if sys.platform == 'darwin':
            htmlDoc = os.path.normpath(filePath + '/../doc/mousecontrols-mac.htm')
        else:
            htmlDoc = os.path.normpath(filePath + '/../doc/mousecontrols.htm')
        
        # Make sure help document exists.  If not, display msg in textbrowser.
        if os.path.exists(htmlDoc):
            self.mouse_controls_textbrowser.setSource(htmlDoc)
        else:
            msg =  "Help file " + htmlDoc + " not found."
            self.mouse_controls_textbrowser.setText(msg)

    def _setup_keyboard_shortcuts_page(self):
        ''' Setup the Keyboard Shortcuts help page.
        '''
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        
        if sys.platform == 'darwin':
            htmlDoc = os.path.normpath(filePath + '/../doc/keyboardshortcuts-mac.htm')
        else:
            htmlDoc = os.path.normpath(filePath + '/../doc/keyboardshortcuts.htm')
        
        # Make sure help document exists.  If not, display msg in textbrowser.
        if os.path.exists(htmlDoc):
            self.keyboard_shortcuts_textbrowser.setSource(htmlDoc)
        else:
            msg =  "Help file " + htmlDoc + " not found."
            self.keyboard_shortcuts_textbrowser.setText(msg)
        
    def setup_current_page(self, pagename):
        if pagename == 'Mouse Controls':
            self._setup_mouse_controls_page()
        elif pagename == 'Keyboard Shortcuts':
            self._setup_keyboard_shortcuts_page()
        else:
            print 'Error: Preferences page unknown: ', pagename