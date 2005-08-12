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
        1 = Keyboard Shortcuts'''
        
        if pagenum == 0:
            self._setup_mouse_controls_page()
        elif pagenum == 1:
            self._setup_keyboard_shortcuts_page()
        else:
            print "Error: unknown page."
            return
            
        self.help_tab.setCurrentPage(pagenum) 
        self.show() # Non-modal
        return

    ###### Private methods ###############################
    
    def _setup_mouse_controls_page(self):
        ''' Setup the Mouse Controls help page.
        '''
        text = "<b>Mouse Controls</b>"\
        "<p>"\
        "Left Button does something according to mode, see below"\
        "<p>"\
        "Middle Button : Rotate View"\
        "<p>"\
        "Middle Button+Shift : Pan View"\
        "<p>"\
        "Middle Button+Cntl/Cmd : Zoom View (vertical mouse motion) / Turn (horizontal mouse motion)"\
        "<p>"\
        "Mouse Wheel : Zoom, half-speed with Shift, double-speed with Cntl/Cmd"\
        "<p>"\
        "Right Button : Context Menu"\
        "<p>"\
        "<b>Build Mode:</b><br>"\
        "Left-Click deposits an atom or chunk from the clipboard in empty space or bonds it to an open bond.<br>"\
        "Left-Drag on an atom moves the molecule.<br>"\
        "Shift+Left-Drag moves atoms or open bonds.<br>"\
        "Cntl+Left-Click deletes a highlighted atom.<br>"

        #self.mouse_controls_textbrowser.setText(text)

        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        htmlDoc = os.path.normpath(filePath + '/../doc/mousecontrols.htm')
        self.mouse_controls_textbrowser.setSource(htmlDoc)

        
    def _setup_keyboard_shortcuts_page(self):
        ''' Setup the Keyboard Shortcuts help page.
        '''
        #text = "Keyboard Shortcuts"
        #self.keyboard_shortcuts_textbrowser.setText(text)
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        htmlDoc = os.path.normpath(filePath + '/../doc/keyboardaccelerators.htm')
        self.keyboard_shortcuts_textbrowser.setSource(htmlDoc)

        
    def setup_current_page(self, pagename):
        if pagename == 'Mouse Controls':
            self._setup_mouse_controls_page()
        elif pagename == 'Keyboard Shortcuts':
            self._setup_keyboard_shortcuts_page()
        else:
            print 'Error: Preferences page unknown: ', pagename