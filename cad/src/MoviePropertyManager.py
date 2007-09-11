# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
MoviePropertyManager.py
@author: Ninad
@version: $Id$
@copyright: 2007 Nanorex, Inc.  All rights reserved.

History:
ninad20070507 : Converted movie dashboard into movie Property manager


"""
__author__  = "Ninad"

from PyQt4 import QtCore, QtGui
from Ui_MoviePropertyManager import Ui_MoviePropertyManager
from PyQt4.Qt import Qt, SIGNAL

class MoviePropertyManager(Ui_MoviePropertyManager):
    """
    The MoviePropertyManager class provides the Property Manager for the
    B{Movie mode}.  The UI is defined in L{Ui_MoviePropertyManager}
    """
    def __init__(self, parentMode):
        """
        Constructor for the B{Movie} property manager.
        
        @param parentMode: The parent mode where this Property Manager is used
        @type  parentMode: L{movieMode} 
        """
        Ui_MoviePropertyManager.__init__(self, parentMode)
        self._addGroupBoxes()           
        self.updateMessage() 
    
    def ok_btn_clicked(self):
        """
        Calls MainWindow.toolsDone to exit the current mode. 
        @attention: this method needs to be renamed. (this should be done in 
        PM_Dialog)
        """
        self.w.toolsDone()
    
    def cancel_btn_clicked(self):
        """
        Calls MainWindow.toolsDone to exit the current mode. 
        @attention: this method needs to be renamed. (this should be done in 
        PM_Dialog)
        """
        self.w.toolsCancel()
    
    def updateMessage(self):
        """
        Updates the message box with an informative message.
        """
        msg = "Use movie control buttons in the Property Manager to play \
        current simulation movie (if it exists). You can also load a previously\
        saved movie for this model using <b>'Open Movie File...'</b> option."
        self.MessageGroupBox.insertHtmlMessage( msg, 
                                                minLines      = 6,
                                                setAsDefault  =  True )