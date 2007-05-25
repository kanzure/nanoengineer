# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PropertyManagerMixin.py
@author: Ninad
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:
ninad20061215: created this mixin class to provide helper methods in various 
Property managers 
ninad20070206: added many new methods to help prop manager ui generation.

mark 2007-05-17: added the new property manager base class PropMgrBaseClass.

"""

__author__ = "Ninad"

from PyQt4.Qt import *
from PyQt4 import Qt, QtCore, QtGui
from Utility import geticon
from PyQt4.QtGui import *
from Sponsors import SponsorableMixin
from qt4transition import lineage
from Utility import geticon, getpixmap
from PropMgr_Constants import *
       
# Currently used by:
# - Build > Atoms (depositMode/MMKit)
# - Build > Crystal (cookieCutter)
# - Tools > Extrude (extrudeMode)
# - Tools > Fuse (fuseMode)
# - Tools > Move (modifyMode)
# - Simulator > Play Movie (movieMode)
# - GeneratorBaseClass
#
# Once all these have been migrated to the new PropMgrBaseClass,
# this class can be removed permanently. Mark 2007-05-25

class PropertyManagerMixin(SponsorableMixin):
    '''Mixin class that provides methods common to various property managers''' 
        
    def openPropertyManager(self, tab):
        #tab = property manager widget
        self.pw = self.w.activePartWindow()         
        self.pw.updatePropertyManagerTab(tab)
        try:
            tab.setSponsor()
        except:
            print "tab has no attribute 'setSponsor()'  ignoring."
        self.pw.featureManager.setCurrentIndex(self.pw.featureManager.indexOf(tab))
     
    def closePropertyManager(self):
        if not self.pw:
            self.pw = self.w.activePartWindow() 
        self.pw.featureManager.setCurrentIndex(0)
        self.pw.featureManager.removeTab(self.pw.featureManager.indexOf(self.pw.propertyManagerScrollArea))            
        if self.pw.propertyManagerTab:
            self.pw.propertyManagerTab = None
            
    def toggle_groupbox(self, button, *things):
        """This is intended to be part of the slot method for clicking on an open/close icon
        of a dialog GroupBox. The arguments should be the button (whose icon will be altered here)
        and the child widgets in the groupbox whose visibility should be toggled.
        """
        if things:
            if things[0].isVisible():
                styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = False)
                button.setStyleSheet(styleSheet)      
                palette = self.getGroupBoxButtonPalette()
                button.setPalette(palette)
                button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for thing in things:
                    thing.hide()
            else:
                styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = True)
                button.setStyleSheet(styleSheet)             
                palette = self.getGroupBoxButtonPalette()
                button.setPalette(palette)
                button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for thing in things:
                    thing.show()
                    
        else:
            print "Groupbox has no widgets. Clicking on groupbox button has no effect"
    
    def getPropertyManagerPalette(self):
        """ Return a palette for the property manager.
        """
        # in future we might want to set different palette colors for prop managers. 
        return self.getPalette(None,
                               QtGui.QPalette.ColorRole(10),
                               pmColor)
    
    def getPropMgrTitleFramePalette(self):
        """ Return a palette for Property Manager title frame. 
        """
        #bgrole(10) is 'Windows'
        return self.getPalette(None,
                               QtGui.QPalette.ColorRole(10),
                               pmTitleFrameColor)
    
    def getPropMgrTitleLabelPalette(self):
        """ Return a palette for Property Manager title label. 
        """
        return self.getPalette(None,
                               QtGui.QPalette.WindowText,
                               pmTitleLabelColor)
    
    def getMsgGroupBoxPalette(self):
        """ Return a palette for Property Manager message groupboxes.
        """
        return self.getPalette(None,
                               QtGui.QPalette.Base,
                               pmMessageTextEditColor)
                               
    def getGroupBoxPalette(self):
        """ Return a palette for Property Manager groupboxes. 
        This distinguishes the groupboxes in a property manager.
        The color is slightly darker than the property manager background.
        """
        #bgrole(10) is 'Windows'
        return self.getPalette(None,
                               QtGui.QPalette.ColorRole(10),
                               pmGrpBoxColor)
    
    def getGroupBoxButtonPalette(self):
        """ Return a palette for the groupbox Title button. 
        """
        return self.getPalette(None,
                               QtGui.QPalette.Button, 
                               pmGrpBoxButtonColor)
    
    def getGroupBoxCheckBoxPalette(self):
        """ Returns the background color for the checkbox of any groupbox 
        in a Property Manager. The color is slightly darker than the 
        background palette of the groupbox.
        """
        palette = self.getPalette(None,
                               QtGui.QPalette.WindowText, 
                               pmCheckBoxTextColor)
        
        return self.getPalette(palette,
                               QtGui.QPalette.Button, 
                               pmCheckBoxButtonColor)
    
    def getPalette(self, palette, obj, color):
        """ Given a palette, Qt object and a color, return a new palette.
        If palette is None, create and return a new palette.
        """
        
        if palette:
            pass # Make sure palette is QPalette.
        else:
            palette = QtGui.QPalette()
            
        palette.setColor(QtGui.QPalette.Active, obj, color)
        palette.setColor(QtGui.QPalette.Inactive, obj, color)
        palette.setColor(QtGui.QPalette.Disabled, obj, color)
        return palette
    
    def getGroupBoxStyleSheet(self):
        """Return the style sheet for a groupbox. Example border style, border 
        width etc. The background color for a  groupbox is set separately"""
        
        styleSheet = "QGroupBox {border-style:solid;\
        border-width: 1px;\
        border-color: " + pmGrpBoxBorderColor + ";\
        border-radius: 0px;\
        min-width: 10em; }"
        
        ## For Groupboxs' Pushbutton : 
        
        ##Other options not used : font:bold 10px;  
        
        return styleSheet
    
    def getGroupBoxTitleButton(self, name, parent =None, bool_expand = True): #Ninad 070206
        """ Return the groupbox title pushbutton. The pushbutton is customized 
        such that  it appears as a title bar to the user. If the user clicks on 
        this 'titlebar' it sends appropriate signals to open or close the
        groupboxes   'name = string -- title of the groupbox 
        'bool_expand' = boolean .. NE1 uses a different background 
        image in the button's  Style Sheet depending on the bool. 
        (i.e. if bool_expand = True it uses a opened group image  '^')
        See also: getGroupBoxTitleCheckBox , getGroupBoxButtonStyleSheet  methods
        """
        
        button  = QtGui.QPushButton(name, parent)
        button.setFlat(False)
        button.setAutoFillBackground(True)
        
        palette = self.getGroupBoxButtonPalette()
        button.setPalette(palette)
        
        styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand)
                
        button.setStyleSheet(styleSheet)        
        #ninad 070221 set a non existant 'Ghost Icon' for this button
        #By setting such an icon, the button text left aligns! 
        #(which what we want :-) )
        #So this might be a bug in Qt4.2.  If we don't use the following kludge, 
        #there is no way to left align the push button text but to subclass it. 
        #(could mean a lot of work for such a minor thing)  So OK for now 
        
        button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
        
        return button    
    
    def getGroupBoxButtonStyleSheet(self, bool_expand =True):
        """ Returns the syle sheet for a groupbox title button (or checkbox)
        of a property manager. Returns a string. 
        bool_expand' = boolean .. NE1 uses a different background image in the 
        button's  Style Sheet depending on the bool. 
        (i.e. if bool_expand = True it uses a opened group image  '^')
        """
        
        # Need to move border color and text color to top (make global constants).
        if bool_expand:        
            styleSheet = "QPushButton {border-style:outset;\
            border-width: 2px;\
            border-color: " + pmGrpBoxButtonBorderColor + ";\
            border-radius:2px;\
            font:bold 12px 'Arial'; \
            color: " + pmGrpBoxButtonTextColor + ";\
            min-width:10em;\
            background-image: url(" + pmGrpBoxExpandedImage + ");\
            background-position: right;\
            background-repeat: no-repeat;\
            }"       
        else:
            
            styleSheet = "QPushButton {border-style:outset;\
            border-width: 2px;\
            border-color: " + pmGrpBoxButtonBorderColor + ";\
            border-radius:2px;\
            font: bold 12px 'Arial'; \
            color: " + pmGrpBoxButtonTextColor + ";\
            min-width:10em;\
            background-image: url(" + pmGrpBoxCollapsedImage + ");\
            background-position: right;\
            background-repeat: no-repeat;\
            }"
            
        return styleSheet
    
    def getGroupBoxTitleCheckBox(self, name, parent =None, bool_expand = True):#Ninad 070207
        """ Return the groupbox title checkbox . The checkbox is customized such that 
        it appears as a title bar to the user. If the user clicks on this 'titlebar' it sends 
        appropriate signals to open or close the groupboxes (and also to check or uncheck the box.)
        'name = string -- title of the groupbox 
        'bool_expand' = boolean .. NE1 uses a different background image in the button's 
        Style Sheet depending on the bool. (i.e. if bool_expand = True it uses a opened group image  '^')      
        See also: getGroupBoxTitleButton method.         
        """
        
        checkbox = QtGui.QCheckBox(name, parent)
        checkbox.setAutoFillBackground(True)
        
        palette = self.getGroupBoxCheckBoxPalette()
        checkbox.setPalette(palette)
        
        styleSheet = self.getGroupBoxCheckBoxStyleSheet(bool_expand)
        checkbox.setStyleSheet(styleSheet)             
        checkbox.setText(name)
        
        return checkbox
    
       
    def getGroupBoxCheckBoxStyleSheet(self, bool_expand =True):
        """ Returns the syle sheet for a groupbox checkbox of a property manager
        Returns a string. 
        bool_expand' = boolean .. NE1 uses a different background image in the button's 
        Style Sheet depending on the bool. (i.e. if bool_expand = True it uses a opened group image  '^')
        """
 
        if bool_expand:        
            styleSheet = "QCheckBox {\
            color: " + pmGrpBoxButtonTextColor + ";\
            font: bold 12px 'Arial';\
            }"
        else:
            styleSheet = "QCheckBox {\
            color: " + pmGrpBoxButtonTextColor + ";\
            font: bold 12px 'Arial';\
            }"    
        # Excluded attributes (has issues)-- 
        ##background-image: url(ui/actions/Properties Manager/Opened_GroupBox.png);\
        ##background-position: right;\
        ##background-repeat: no-repeat;\
        
        return styleSheet
    
    def hideGroupBox(self, groupBoxButton, groupBoxWidget):
        # Hide a groupbox (this is not the same a 'toggle' groupbox)        
                 
        groupBoxWidget.hide()               
        
        styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = False)            
        groupBoxButton.setStyleSheet(styleSheet)      
        palette = self.getGroupBoxButtonPalette()
        groupBoxButton.setPalette(palette)
        groupBoxButton.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
            
    def showGroupBox(self, groupBoxButton, groupBoxWidget):
        # Show a groupbox (this is not the same as 'toggle' groupbox)        
        
        if not groupBoxWidget.isVisible():               
            groupBoxWidget.show()               
            
            styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = True)            
            groupBoxButton.setStyleSheet(styleSheet)      
            palette = self.getGroupBoxButtonPalette()
            groupBoxButton.setPalette(palette)
            groupBoxButton.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
