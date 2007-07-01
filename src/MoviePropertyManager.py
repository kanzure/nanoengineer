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
from PropertyManagerMixin import PropertyManagerMixin, pmSetPropMgrIcon, pmSetPropMgrTitle
from PyQt4.Qt import Qt, SIGNAL
from Utility import geticon

class MoviePropertyManager(QtGui.QWidget, 
                          PropertyManagerMixin, 
                          Ui_MoviePropertyManager):
    
    # The title(s) that appears in the property manager header.
    title = "Play Movie"
    # The full path to PNG file(s) that appears in the header.
    iconPath = "ui/actions/Simulation/Play_Movie.png"
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        self.setupUi(self)
        
        self.lastCheckedRotateAction = None 
        self.lastCheckedTranslateAction = None
        
        # Update the title and icon for "Translate" (the default move mode).
	pmSetPropMgrIcon( self, self.iconPath )
	pmSetPropMgrTitle( self, self.title )
                
        #connect slots        
        self.connect(self.movieOptions_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_movieOptionsGroupBox)
        
        self.connect(self.movieControls_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_movieControlsGroupBox)  
        
        self.connect(self.movieFiles_groupBoxButton, 
                     SIGNAL("clicked()"),
                     self.toggle_movieFilesGroupBox)  
        
    def toggle_movieOptionsGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other 
       groupbox
       Example: If user clicks on Movie groupbox button, it will toggle the 
       display of the groupbox """
        
        self.toggle_groupbox(self.movieOptions_groupBoxButton, 
                             self.movieOptionsGroupBox_widgetHolder) 
        
    def toggle_movieControlsGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other 
       groupbox
       Example: If user clicks on Movie groupbox button, it will toggle the 
       display of the groupbox """
                
        self.toggle_groupbox(self.movieControls_groupBoxButton, 
                             self.movieControlsGroupBox_widgetHolder) 
        
    def toggle_movieFilesGroupBox(self):
        """ Toggles the item display in the parent groupbox of the button and 
       hides the other groupbox also disconnecting the actions in the other 
       groupbox
       Example: If user clicks on Movie groupbox button, it will toggle the 
       display of the groupbox """
        
        self.toggle_groupbox(self.movieFiles_groupBoxButton, 
                             self.movieFilesGroupBox_widgetHolder) 
