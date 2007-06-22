# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
PropertyManagerMixin.py
@author: Ninad
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

History:
ninad20061215: created this mixin class to provide helper methods in various 
Property managers 
ninad20070206: added many new methods to help prop manager ui generation.

mark 2007-05-17: added the new property manager base class PropMgrBaseClass. [now in its own file]

bruce 2007-06-15: partly cleaned up inheritance (by splitting out PropertyManager_common).

"""

__author__ = "Ninad"

from PyQt4.Qt import *
from PyQt4 import Qt, QtCore, QtGui
from Sponsors import SponsorableMixin
from Utility import geticon, getpixmap
from PropMgr_Constants import *
from debug import print_compact_traceback
import platform
from PropMgrBaseClass import PropertyManager_common

class MessageGroupBox(QGroupBox, PropertyManager_common):
    """Creates a Message group box. 
    This class is used by the following Property Managers
    (which are still not using the PropMgrBaseClass):
    - Build Atoms
    - Build Crystal
    - Extrude
    - Move
    - Movie Player
    - Fuse Chunks
    
    Note: This class is temporary. It will be removed after the
    PropMgrs in this list are converted to the PropMgrBaseClass.
    Mark 2007-06-21
    """
    
    expanded = True # Set to False when groupbox is collapsed.
    
    def __init__(self, parent, title=''):
        
        QGroupBox.__init__(self)
	if parent:
	    self.setParent(parent) #Fixed bug 2465 -- ninad 20070622
	    
        self.setAutoFillBackground(True) 
        self.setPalette(self.getPropMgrGroupBoxPalette())
        self.setStyleSheet(self.getStyleSheet())
        
        # Create vertical box layout
        self.VBoxLayout = QVBoxLayout(self)
        self.VBoxLayout.setMargin(pmMsgGrpBoxMargin)
        self.VBoxLayout.setSpacing(pmMsgGrpBoxSpacing)
        
        # Add title button to GroupBox
        self.titleButton = self.getTitleButton(title, self)
        self.VBoxLayout.addWidget(self.titleButton)
        self.connect(self.titleButton,SIGNAL("clicked()"),
                     self.toggleExpandCollapse)
        
        # Yellow MessageTextEdit
        self.MessageTextEdit = QtGui.QTextEdit(self)
        self.MessageTextEdit.setMaximumHeight(80) # 80 pixels height
        self.MessageTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.VBoxLayout.addWidget(self.MessageTextEdit)

        msg_palette = self.getMessageTextEditPalette()

        self.MessageTextEdit.setPalette(msg_palette)
        self.MessageTextEdit.setReadOnly(True)
        
        # wrapWrapMode seems to be set to QTextOption.WrapAnywhere on MacOS,
        # so let's force it here. Mark 2007-05-22.
        self.MessageTextEdit.setWordWrapMode(QTextOption.WordWrap)
        
        # These two policies very important. Mark 2007-05-22
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self.MessageTextEdit.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self.setWhatsThis("""<b>Messages</b>
            <p>This prompts the user for a requisite operation and/or displays 
            helpful messages to the user.</p>""")
        
        parent.MessageTextEdit = self.MessageTextEdit
	
	self.hide()
        
    def getTitleButton(self, title, parent=None, showExpanded=True): #Ninad 070206
        """ Return the groupbox title pushbutton. The pushbutton is customized 
        such that  it appears as a title bar to the user. If the user clicks on 
        this 'titlebar' it sends appropriate signals to open or close the
        groupboxes   'name = string -- title of the groupbox 
        'showExpanded' = boolean .. NE1 uses a different background 
        image in the button's  Style Sheet depending on the bool. 
        (i.e. if showExpanded = True it uses a opened group image  '^')
        See also: getGroupBoxTitleCheckBox , getGroupBoxButtonStyleSheet  methods
        """
        
        button  = QPushButton(title, parent)
        button.setFlat(False)
        button.setAutoFillBackground(True)

	button.setStyleSheet(self.getTitleButtonStyleSheet(showExpanded))
	button.setPalette(self.getTitleButtonPalette())
	
        #ninad 070221 set a non existant 'Ghost Icon' for this button
        #By setting such an icon, the button text left aligns! 
        #(which what we want :-) )
        #So this might be a bug in Qt4.2.  If we don't use the following kludge, 
        #there is no way to left align the push button text but to subclass it. 
        #(could mean a lot of work for such a minor thing)  So OK for now 
        
        button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
        
        return button
    
    def getTitleButtonStyleSheet(self, showExpanded=True):
        """Returns the style sheet for a groupbox title button (or checkbox).
        If <showExpanded> is True, the style sheet includes an expanded icon.
        If <showExpanded> is False, the style sheet includes a collapsed icon.
        """
        
        # Need to move border color and text color to top (make global constants).
        if showExpanded:        
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
    
    def toggleExpandCollapse(self):
        """Slot method for the title button to expand/collapse the groupbox.
        """
        if self.expanded: # Collapse groupbox by hiding ahe yellow TextEdit.
            # The styleSheet contains the expand/collapse icon.
            styleSheet = self.getTitleButtonStyleSheet(showExpanded = False)
            self.titleButton.setStyleSheet(styleSheet)
            # Why do we have to keep resetting the palette?
            # Does assigning a new styleSheet reset the button's palette?
            # If yes, we should add the button's color to the styleSheet.
            # Mark 2007-05-20
            self.titleButton.setPalette(self.getTitleButtonPalette())
            self.titleButton.setIcon(
                    geticon("ui/actions/Properties Manager/GHOST_ICON"))
            self.MessageTextEdit.hide()
            self.expanded = False 
        else: # Expand groupbox by showing the yellow TextEdit.
            # The styleSheet contains the expand/collapse icon.
            styleSheet = self.getTitleButtonStyleSheet(showExpanded = True)
            self.titleButton.setStyleSheet(styleSheet)
            # Why do we have to keep resetting the palette?
            # Does assigning a new styleSheet reset the button's palette?
            # If yes, we should add the button's color to the styleSheet.
            # Mark 2007-05-20
            self.titleButton.setPalette(self.getTitleButtonPalette())
            self.titleButton.setIcon(
                    geticon("ui/actions/Properties Manager/GHOST_ICON"))
            self.MessageTextEdit.show()
            self.expanded = True
    
    def getStyleSheet(self):
        """Return the style sheet for a groupbox. This sets the following 
        properties only:
         - border style
         - border width
         - border color
         - border radius (on corners)
        The background color for a groupbox is set using getPalette()."""
        
        styleSheet = "QGroupBox {border-style:solid;\
        border-width: 1px;\
        border-color: " + pmGrpBoxBorderColor + ";\
        border-radius: 0px;\
        min-width: 10em; }" 
        
        ## For Groupboxs' Pushbutton : 
        ##Other options not used : font:bold 10px;  
        
        return styleSheet
    
    def insertHtmlMessage(self, text, 
                          minLines=4, maxLines=10, 
                          replace=True):
        """Insert <text> (HTML) into the message groupbox.
        <minLines> - The minimum number of lines (of text) to display in the TextEdit.
        if <minLines>=0 the TextEdit will fit its own height to fit <text>. The
        default height is 4 (lines of text).
        <maxLines> - The maximum number of lines to display in the TextEdit widget.
        <replace> should be set to False if you do not wish
        to replace the current text. It will append <text> instead.

        Shows the message groupbox if it is hidden.
        """
        if replace:
            self.MessageTextEdit.clear()
	    
	if text:
	    self._setHeight(minLines, maxLines)
	    QTextEdit.insertHtml(self.MessageTextEdit, text)
	    self.show()
	else:
	    # Hide the message groupbox if it contains no text.
	    self.hide()
	
    def _setHeight(self, minLines=4, maxLines=8):
        """Set the height just high enough to display
        the current text without a vertical scrollbar.
        <minLines> is the minimum number of lines to
        display, even if the text takes up fewer lines.
        <maxLines> is the maximum number of lines to
        diplay before adding a vertical scrollbar.
        """
        
        if minLines == 0:
            fitToHeight=True
        else:
            fitToHeight=False
        
        # Current width of PropMgrTextEdit widget.
        current_width = self.MessageTextEdit.sizeHint().width()
        
        # Probably including Html tags.
        text = self.MessageTextEdit.toPlainText()
        text_width = self.MessageTextEdit.fontMetrics().width(text)
        
        num_lines = text_width/current_width + 1
            # + 1 may create an extra (empty) line on rare occasions.
                        
        if fitToHeight:
            num_lines = min(num_lines, maxLines)
                
        else:
            num_lines = max(num_lines, minLines)

        #margin = self.fontMetrics().leading() * 2 # leading() returned 0. Mark 2007-05-28
        margin = 10 # Based on trial and error. Maybe it is pm?Spacing=5 (*2)? Mark 2007-05-28
        new_height = num_lines * self.MessageTextEdit.fontMetrics().lineSpacing() + margin
        
        if 0: # Debugging code for me. Mark 2007-05-24
            print "--------------------------------"
            print "Widget name =", self.objectName()
            print "minLines =", minLines
            print "maxLines =", maxLines
            print "num_lines=", num_lines
            print "New height=", new_height
            print "text =", text   
            print "Text width=", text_width
            print "current_width (of PropMgrTextEdit)=", current_width
        
        # Reset height of PropMgrTextEdit.
        self.MessageTextEdit.setMinimumSize(QSize(pmMinWidth * 0.5, new_height))
        self.MessageTextEdit.setMaximumHeight(new_height)
    
    # End of messageGroupBox class. ###################
    
def addBottomSpacer(parent, vlayout, last=False):
    """Adds a vertical spacer to the bottom of <parent>, a group box.
    <vlayout> is the VBoxLayout of the Property Manager.
    <last> - Set to True if <parent> is the last (bottom) groupbox in 
    the Property Manager.
    
    Note: There is a copy of this in every
    """
    if last:
	parent.bottom_spacer = \
	    QtGui.QSpacerItem(10, 0, \
			    QtGui.QSizePolicy.Fixed, \
			    QtGui.QSizePolicy.Expanding)
    else:
	parent.bottom_spacer = \
	    QtGui.QSpacerItem(10, pmGroupBoxSpacing, \
			    QtGui.QSizePolicy.Fixed, \
			    QtGui.QSizePolicy.Fixed)
	
    vlayout.addItem(parent.bottom_spacer)
    
# ==

# Class PropertyManagerMixin is currently [when?] used by:
# - Build > Atoms (depositMode/MMKit)
# - Build > Crystal (cookieCutter)
# - Tools > Extrude (extrudeMode)
# - Tools > Fuse (fuseMode)
# - Tools > Move (modifyMode)
# - Simulator > Play Movie (movieMode)
# - GeneratorBaseClass [not anymore! 070615]
#
# Once all these have been migrated to the new PropMgrBaseClass,
# this class can be removed permanently. Mark 2007-05-25

class PropertyManagerMixin(PropertyManager_common, SponsorableMixin):
    """Mixin class that provides methods common to various property managers (but not to PropMgrBaseClass)"""
        
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
        
        try:
            pmWidget = self.pw.propertyManagerScrollArea.widget()
            pmWidget.update_props_if_needed_before_closing()
        except:
            if platform.atom_debug:
                msg1 = "Last PropMgr doesn't have method updatePropsBeforeClosing."
                msg2 =  " That is OK (for now,only implemented in GeometryGenerators)"
                msg3 = "Ignoring Exception"
                print_compact_traceback(msg1 + msg2 + msg3)
            pass
        
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
            print "Groupbox has no widgets. Clicking on groupbox button has no effect."
        return

    def getMsgGroupBoxPalette(self): # note: not used by anything as of 070615
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
    
    def getGroupBoxTitleButton(self, name, parent = None, bool_expand = True): #Ninad 070206
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
    
    def getGroupBoxButtonStyleSheet(self, bool_expand = True):
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
    
    def getGroupBoxTitleCheckBox(self, name, parent = None, bool_expand = True):#Ninad 070207 # note: used only in MMKitDialog as of 070615
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
       
    def getGroupBoxCheckBoxStyleSheet(self, bool_expand = True): # note: used only in MMKitDialog and MMKit as of 070615
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
        """Hide a groupbox (this is not the same as 'toggle' groupbox)"""
                 
        groupBoxWidget.hide()               
        
        styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = False)            
        groupBoxButton.setStyleSheet(styleSheet)      
        palette = self.getGroupBoxButtonPalette()
        groupBoxButton.setPalette(palette)
        groupBoxButton.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
            
    def showGroupBox(self, groupBoxButton, groupBoxWidget):
        """Show a groupbox (this is not the same as 'toggle' groupbox)"""
        
        if not groupBoxWidget.isVisible():               
            groupBoxWidget.show()               
            
            styleSheet = self.getGroupBoxButtonStyleSheet(bool_expand = True)            
            groupBoxButton.setStyleSheet(styleSheet)      
            palette = self.getGroupBoxButtonPalette()
            groupBoxButton.setPalette(palette)
            groupBoxButton.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))

    pass # end of class PropertyManagerMixin

# end
