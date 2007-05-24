# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
PropMgrBaseClass.py
@author: Mark
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  All rights reserved.

History:

mark 2007-05-20: Split PropMgrBaseClass out of PropertyManagerMixin into
                 this file.
mark 2007-05-23: New PropMgrBaseClass with support for the following PropMgr 
                 widget classes:
                 - PropMgrGroupBox (subclass of Qt's QGroupBox widget)
                 - PropMgrComboBox (subclass of Qt's QComboBox widget)
                 - PropMgrDoubleSpinBox (subclass of Qt's QDoubleSpinBox widget)
                 - PropMgrSpinBox (subclass of Qt's QSpinBox widget)
                 - PropMgrTextEdit (subclass of Qt's QTextEdit widget)

"""

__author__ = "Mark"

# Mark's To Do List (by order of priority):
#
# - Add PropMgrPushButton class (needed by DNAGeneratorDialog)
# - Migrate DNAGenerator and DNAGeneratorDialog.
# - Clean up PropertyManagerMixin.py
# - Compute message box size using FontMetrics (important)
# - getWidgetGridLayoutParms() => addWidgetLabel()
# - Support resizing (pmWidth range 200-400)
# - Test PropMgr layout/resizing on a 1024 x 768 monitor.
# - Make fitContents() "smarter". See docstring.
# - Resize width of PropMgr automatically when scrollbar appears to make
#   extra room for it.
# - Ask Bruce how he would move restoreDefault() into PropMgrWidgetMixin
#   class.
# - Standard names for all widgets. (minor)
# - Add color theme user pref in Preferences dialog. (nice to have)
# - Set title button color via style sheet (see getTitleButtonStyleSheet)
# - Create TopRowButtns class with attrs and methods to hide/show 
#   buttons. (minor)
# - add setObjectName("name") to all widgets.
# - "range" attr (str) that can be included in What's This text.

from PyQt4.Qt import *
from PyQt4 import QtCore
from Utility import geticon
from Sponsors import SponsorableMixin
#from qt4transition import lineage # OK to remove? Mark 2007-05-22
from debug_prefs import debug_pref, Choice_boolean_True, Choice_boolean_False, Choice
from Utility import geticon, getpixmap
from PropMgr_Constants import *
from widgets import double_fixup
import os, sys

def getPropMgrImagePath(imageName):
    """Returns the relative path to the icon/image file <imageName>.
    """
    return os.path.join (pmImagePath + imageName)

COLOR_THEME = "Gray"

_colortheme_Choice = Choice(["Gray", "Blue"], default_value = COLOR_THEME)

COLOR_THEME_prefs_key = "A9/Color Theme"

def set_Color_Theme_from_pref():
    global COLOR_THEME
    COLOR_THEME = debug_pref("Color Theme (next session)",
                                       _colortheme_Choice,
                                       non_debug = True,
                                       prefs_key = COLOR_THEME_prefs_key)
    return

set_Color_Theme_from_pref()

# Standard colors for all themes.
pmColor = QColor(230, 231, 230) # Should get this from the main window (parent).
pmGrpBoxColor = QColor(201,203,223)
pmMessageTextEditColor = QColor(255,255,100) # Yellow msg box (QTextEdit widget).
    
if COLOR_THEME == "Gray":

    # Dark Gray Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(120,120,120)
    pmTitleLabelColor = QColor(255,255,255)
    pmGrpBoxButtonColor = QColor(172,173,190)
    pmCheckBoxTextColor = QColor(0,0,255) # used in MMKit
    pmCheckBoxButtonColor = QColor(172,173,190)
    
    
    # Property Manager stylesheet colors (uses HTML Color Codes)
    #@ To do: I intend to add a method for each (like those above) 
    # that returns a palette. Mark 2007-05-17.
    pmGrpBoxBorderColor = "#444F51"
    pmGrpBoxButtonBorderColor = "#939089"
    pmGrpBoxButtonTextColor = "#282821" # Same as pmCheckBoxTextColor

    # Locations of expanded and collapsed title button images.
    pmGrpBoxExpandedImage = getPropMgrImagePath("GroupBox_Opened_Gray.png")
    pmGrpBoxCollapsedImage = getPropMgrImagePath("GroupBox_Closed_Gray.png")

else: # Blue Color Theme
    
    # Colors for Property Manager widgets.
    pmTitleFrameColor = QColor(120,120,120) # I like (50,90,230). mark
    pmTitleLabelColor = QColor(255,255,255)
    pmGrpBoxButtonColor = QColor(172,173,190)
    pmCheckBoxTextColor = QColor(0,0,255)
    pmCheckBoxButtonColor = QColor(172,173,190)
    pmMessageTextEditColor = QColor(255,255,100)

    # Property Manager stylesheet colors (uses HTML Color Codes)
    pmGrpBoxBorderColor = "blue"
    pmGrpBoxButtonBorderColor = "gray"
    pmGrpBoxButtonTextColor = "blue"

    # Locations of groupbox opened and closed images.
    pmGrpBoxExpandedImage = getPropMgrImagePath("GroupBox_Opened_Blue.png")
    pmGrpBoxCollapsedImage = getPropMgrImagePath("GroupBox_Closed_Blue.png")
    
def getPalette(palette, obj, color):
    """ Given a palette, Qt object and a color, return a new palette.
    If palette is None, create and return a new palette.
    """
    if palette:
        pass # Make sure palette is QPalette.
    else:
        palette = QPalette()
            
    palette.setColor(QPalette.Active, obj, color)
    palette.setColor(QPalette.Inactive, obj, color)
    palette.setColor(QPalette.Disabled, obj, color)
    
    return palette

def getWidgetGridLayoutParms(label, row, spanWidth):
    """PropMgr widget GridLayout helper function. 
    Given <label>, <row> and <spanWitdth>, this function returns
    all the parameters needed to place the widget (and its label)
    in the caller's groupbox GridLayout.
    """
    
    if not spanWidth: 
        # This widget and its label are on the same row
        labelRow = row
        labelColumn = 0
        labelSpanCols = 1
        labelAlignment = Qt.AlignRight | \
                         Qt.AlignTrailing | \
                         Qt.AlignVCenter # Label is right justified.
            
        widgetRow = row
        widgetColumn = 1
        widgetSpanCols = 1
        incRows = 1
        
    else: # This widget spans the full width of the groupbox
        if label: # The label and widget are on separate rows.
                
            # Set the label's row, column and alignment.
            labelRow = row
            labelColumn = 0
            labelSpanCols = 2
            labelAlignment = Qt.AlignLeft | \
                           Qt.AlignLeading | \
                           Qt.AlignVCenter # Label is left justified.
                
            # Set this widget's row and column attrs.
            widgetRow = row + 1 # Widget is below the label.
            widgetColumn = 0
            widgetSpanCols = 2
            incRows = 2
        else:  # No label. Just the widget.
            labelRow = labelColumn = labelSpanCols = labelAlignment = 0
            # Set this widget's row and column attrs.
            widgetRow = row
            widgetColumn = 0
            widgetSpanCols = 2
            incRows = 1
            
    return widgetRow, widgetColumn, widgetSpanCols, incRows, \
           labelRow, labelColumn, labelSpanCols, labelAlignment

# End of getWidgetGridLayoutParms ####################################

class PropMgrBaseClass:
    '''Property Manager base class'''
    
    widgets = [] # All widgets in the PropMgr dialog (
    #groupboxes = [] # All groupboxes in the PropMgr, except the message groupbox.
    
    def __init__(self, name):
        
        self.setObjectName(name)
        self.widgets = [] # All widgets in the groupbox (except the title button).
        
        # Main pallete for PropMgr.
        propmgr_palette = self.getPropertyManagerPalette()
        self.setPalette(propmgr_palette)
        
        # Main vertical layout for PropMgr.
        self.VBoxLayout = QVBoxLayout(self)
        self.VBoxLayout.setMargin(pmMainVboxLayoutMargin)
        self.VBoxLayout.setSpacing(pmMainVboxLayoutSpacing)

        # PropMgr's Header.
        self.addHeader()
        self.addSponsorButton()
        self.addTopRowBtns() # Create top buttons row
        self.MessageGroupBox = PropMgrMessageGroupBox(self, "Message")
        
        self.debugSizePolicy() # For me. Mark 2007-05-17.
        
        # Keep this around; it might be useful.
        # I may want to use it now that I understand it.
        # Mark 2007-05-17.
        #QtCore.QMetaObject.connectSlotsByName(self)
    
    def show(self):
        """Show the Graphene Sheet Property Manager.
        """
        self.setSponsor()
        if not self.pw or self:            
            self.pw = self.win.activePartWindow()       #@@@ ninad061206  
            self.pw.updatePropertyManagerTab(self)
            self.pw.featureManager.setCurrentIndex(self.pw.featureManager.indexOf(self))
        else:
            self.pw.updatePropertyManagerTab(self)
            self.pw.featureManager.setCurrentIndex(self.pw.featureManager.indexOf(self))
        self.fitContents()
            
    def fitContents(self):
        """Sets the final width and height of the PropMgr based on the
        current contents. It should be called after all the widgets
        have been added to this PropMgr.
        
        The important thing this does is set the height of the PropMgr
        after it is loaded with all its GroupBoxes (and their widgets).
        Since this PropMgr dialog is sitting in a ScrollArea, we want
        the scrollbar to appear only when it should. This is determined
        by our height, so we must make sure it is always accurate.
        
        Note: This should be called anytime the height changes. 
        Examples:
        - hiding/showing a widget
        - expanding/collapsing a groupbox
        - resizing a widget based on contents (i.e. a TextEdit).
        
        To do: I need to try deleting the bottom spacer, compute 
        pmHeight and adding the spacer back to address expanding/
        collapsing groupboxes.
            
        Ask Bruce how to do this. Mark 2007-05-23
        """
        if 0: # Let's see what minimumSizeHint and sizeHint say.
            minSize = self.minimumSizeHint()
            print "Min Width, Height =", \
                  minSize.width(), \
                  minSize.height()
        
            sizeHint = self.sizeHint()
            print "SizeHint Width, Height =", \
                  sizeHint.width(), \
                  sizeHint.height()
        
        # The width of propmgr is 230 - (4 x 2) = 222 pixels on Windows.
        pmWidth = 230 - (4 * 2) # 230 should be global/constant
        pmHeight = self.sizeHint().height()
        
        self.resize(pmWidth, pmHeight)
        
        # Save this. May need it when we support resizing via splitter.
        #self.resize(QtCore.QSize(
        #    QtCore.QRect(0,0,pmWidth,pmHeight).size()).
        #    expandedTo(self.minimumSizeHint()))
        
        if 0:
            print "PropMgr Width, Height =", self.width(), self.height()
    
    # On the verge of insanity, then I wrote this.... Mark 2007-05-22
    def debugSizePolicy(self): 
        """Special method for debugging sizePolicy.
        Without this, I couldn't figure out how to make groupboxes
        (and their widgets) behave themselves when collapsing and
        expanding them. I needed to experiment with different sizePolicies,
        especially TextEdits and GroupBoxes, to get everything working
        just right. Their layouts can be slippery. Mark 2007-05-22
        """
        
        if 0: # Override PropMgr sizePolicy.
            self.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Minimum)))
        
        if 0: # Override MessageGroupBox sizePolicy.
            self.MessageGroupBox.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        if 0: # Override MessageTextEdit sizePolicy.
            self.MessageTextEdit.setSizePolicy(
                QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                            QSizePolicy.Policy(QSizePolicy.Fixed)))

        if 0: # Print the current sizePolicies.
            self.printSizePolicy(self)
            self.printSizePolicy(self.MessageGroupBox)
            self.printSizePolicy(self.MessageTextEdit)
    
    def printSizePolicy(self, widget):
        """Special method for debugging sizePolicy.
        Prints the horizontal and vertical policy of <widget>.
        """
        sizePolicy = widget.sizePolicy()
        print "-----------------------------------"
        print "Widget name =", self.objectName(), "-", widget.objectName()
        print "Horizontal SizePolicy =", sizePolicy.horizontalPolicy()
        print "Vertical SizePolicy =", sizePolicy.verticalPolicy()
        
    def addHeader(self):
        """Creates the Property Manager header, which contains
        a pixmap and white text label.
        """
        
        # Heading frame (dark gray), which contains 
        # a pixmap and (white) heading text.
        self.header_frame = QFrame(self)
        self.header_frame.setFrameShape(QFrame.NoFrame)
        self.header_frame.setFrameShadow(QFrame.Plain)
        
        header_frame_palette = self.getPropMgrTitleFramePalette()
        self.header_frame.setPalette(header_frame_palette)
        self.header_frame.setAutoFillBackground(True)

        # HBox layout for heading frame, containing the pixmap
        # and label (title).
        HeaderFrameHLayout = QHBoxLayout(self.header_frame)
        HeaderFrameHLayout.setMargin(pmHeaderFrameMargin) # 2 pixels around edges.
        HeaderFrameHLayout.setSpacing(pmHeaderFrameSpacing) # 5 pixel between pixmap and label.

        # PropMgr icon. Set image by calling setPropMgrIcon() at any time.
        self.header_pixmap = QLabel(self.header_frame)
        self.header_pixmap.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Fixed),
                              QSizePolicy.Policy(QSizePolicy.Fixed)))
            
        self.header_pixmap.setScaledContents(True)
        
        HeaderFrameHLayout.addWidget(self.header_pixmap)
        
        # PropMgr title label (DNA)
        self.header_label = QLabel(self.header_frame)
        header_label_palette = self.getPropMgrTitleLabelPalette()
        self.header_label.setPalette(header_label_palette)

        # PropMgr heading font (for label).
        font = QFont(self.header_label.font())
        font.setFamily("Sans Serif")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(False)
        font.setUnderline(False)
        font.setStrikeOut(False)
        font.setBold(True)
        self.header_label.setFont(font)
        
        HeaderFrameHLayout.addWidget(self.header_label)
        
        self.VBoxLayout.addWidget(self.header_frame)
        
    def setPropMgrTitle(self, title):
        """Set the Propery Manager header title to string <title>.
        """
        self.header_label.setText(title)
        
    def setPropMgrIcon(self, png_path):
        """Set the Propery Manager icon in the header.
        <png_path> is the relative path to the PNG file.
        """
        self.header_pixmap.setPixmap(getpixmap(png_path))
        
    
    def addSponsorButton(self):
        """Creates the Property Manager sponsor button, which contains
        a QPushButton inside of a QGridLayout inside of a QFrame.
        The sponsor logo image is not loaded here.
        """
        
        # Sponsor button (inside a frame)
        self.sponsor_frame = QFrame(self)
        self.sponsor_frame.setFrameShape(QFrame.NoFrame)
        self.sponsor_frame.setFrameShadow(QFrame.Plain)

        SponsorFrameGrid = QGridLayout(self.sponsor_frame)
        SponsorFrameGrid.setMargin(pmSponsorFrameMargin)
        SponsorFrameGrid.setSpacing(pmSponsorFrameSpacing) # Has no effect.

        self.sponsor_btn = QPushButton(self.sponsor_frame)
        self.sponsor_btn.setAutoDefault(False)
        self.sponsor_btn.setFlat(True)
        self.connect(self.sponsor_btn,SIGNAL("clicked()"),
                     self.open_sponsor_homepage)
        
        SponsorFrameGrid.addWidget(self.sponsor_btn,0,0,1,1)
        
        self.VBoxLayout.addWidget(self.sponsor_frame)
        
        return

    def addTopRowBtns(self, showFlags=None):
        """Creates the OK, Cancel, Preview, and What's This 
        buttons row at the top of the Pmgr.
        """
        #@ To do: Turn into a class with attrs and methods to hide/show buttons.
        #
        # The Top Buttons Row includes the following widgets:
        #
        # - self.pmTopRowBtns (Hbox Layout containing everything:)
        #   - left spacer (10x10)
        #   - frame
        #     - hbox layout "frameHboxLO" (margin=2, spacing=2)
        #     - Done (OK) button
        #     - Abort (Cancel) button
        #     - Restore Defaults button
        #     - Preview button
        #     - What's This button
        #   - right spacer (10x10)
        
        
        # Main "button group" widget (but it is not a QButtonGroup).
        self.pmTopRowBtns = QHBoxLayout()
        
        # Left and right spacers
        leftSpacer = QSpacerItem(10, 10, 
                                       QSizePolicy.Expanding, 
                                       QSizePolicy.Minimum)
        rightSpacer = QSpacerItem(10, 10, 
                                        QSizePolicy.Expanding,
                                        QSizePolicy.Minimum)
        
        # Frame containing all the buttons.
        self.TopRowBtnsFrame = QFrame()
                
        self.TopRowBtnsFrame.setFrameShape(QFrame.StyledPanel)
        self.TopRowBtnsFrame.setFrameShadow(QFrame.Raised)
        
        # Create Hbox layout for main frame.
        TopRowBtnsHLayout = QHBoxLayout(self.TopRowBtnsFrame)
        TopRowBtnsHLayout.setMargin(pmTopRowBtnsMargin)
        TopRowBtnsHLayout.setSpacing(pmTopRowBtnsSpacing)
        
        # OK (Done) button.
        self.done_btn = QPushButton(self.TopRowBtnsFrame)
        self.done_btn.setIcon(
            geticon("ui/actions/Properties Manager/Done.png"))
        self.connect(self.done_btn,SIGNAL("clicked()"),
                     self.ok_btn_clicked)
        self.done_btn.setToolTip("Done")
        
        TopRowBtnsHLayout.addWidget(self.done_btn)
        
        # Cancel (Abort) button.
        self.abort_btn = QPushButton(self.TopRowBtnsFrame)
        self.abort_btn.setIcon(
            geticon("ui/actions/Properties Manager/Abort.png"))
        self.connect(self.abort_btn,SIGNAL("clicked()"),
                     self.abort_btn_clicked)
        self.abort_btn.setToolTip("Cancel")
        
        TopRowBtnsHLayout.addWidget(self.abort_btn)
        
        # Restore Defaults button.
        self.restore_defaults_btn = QPushButton(self.TopRowBtnsFrame)
        self.restore_defaults_btn.setIcon(
            geticon("ui/actions/Properties Manager/Restore.png"))
        self.connect(self.restore_defaults_btn,SIGNAL("clicked()"),
                     self.restore_defaults_btn_clicked)
        self.restore_defaults_btn.setToolTip("Restore Defaults")
        TopRowBtnsHLayout.addWidget(self.restore_defaults_btn)
        
        # Preview (glasses) button.
        self.preview_btn = QPushButton(self.TopRowBtnsFrame)
        self.preview_btn.setIcon(
            geticon("ui/actions/Properties Manager/Preview.png"))
        self.connect(self.preview_btn,SIGNAL("clicked()"),
                     self.preview_btn_clicked)
        self.preview_btn.setToolTip("Preview")
        
        TopRowBtnsHLayout.addWidget(self.preview_btn)        
        
        # What's This (?) button.
        self.whatsthis_btn = QPushButton(self.TopRowBtnsFrame)
        self.whatsthis_btn.setIcon(
            geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.connect(self.whatsthis_btn,SIGNAL("clicked()"),
                     self.enter_WhatsThisMode)
        self.whatsthis_btn.setToolTip("What\'s This Help")
        
        TopRowBtnsHLayout.addWidget(self.whatsthis_btn)
        
        # Create Button Row
        self.pmTopRowBtns.addItem(leftSpacer)
        self.pmTopRowBtns.addWidget(self.TopRowBtnsFrame)
        self.pmTopRowBtns.addItem(rightSpacer)
        
        self.VBoxLayout.addLayout(self.pmTopRowBtns)
        
        return

    def hideTopRowButtons(self, hideFlags=None):
        """Hide one or more top row buttons using <hideFlags>.
        Hide button flags not set will cause the button to be shown,
        if currently hidden.
        
        The hide button flags are:
            pmShowAllButtons = 0
            pmHideDoneButton = 1
            pmHideCancelButton = 2
            pmHideRestoreDefaultsButton = 4
            pmHidePreviewButton = 8
            pmHideWhatsThisButton = 16
            pmHideAllButtons = 31
            
        These flags are defined in PropMgr_Constants.py.
        """
        
        if hideFlags & pmHideDoneButton: self.done_btn.hide()
        else: self.done_btn.show()
            
        if hideFlags & pmHideCancelButton: self.abort_btn.hide()
        else: self.abort_btn.show()
            
        if hideFlags & pmHideRestoreDefaultsButton: 
            self.restore_defaults_btn.hide()
        else: self.restore_defaults_btn.show()
            
        if hideFlags & pmHidePreviewButton: self.preview_btn.hide()
        else: self.preview_btn.show()
            
        if hideFlags & pmHideWhatsThisButton: self.whatsthis_btn.hide()
        else: self.whatsthis_btn.show()
        
    def addGroupBoxSpacer(self):
        """Add vertical groupbox spacer. 
        """
        groupbox_spacer = QSpacerItem(10,pmGroupBoxSpacing,
                                           QSizePolicy.Fixed,
                                           QSizePolicy.Fixed)
        
        self.VBoxLayout.addItem(groupbox_spacer) # Add spacer
    
    def addBottomSpacer(self):
        """Add spacer at the very bottom of the PropMgr. 
        It is needed to assist proper collasping/expanding of groupboxes.
        """
        spacer_height = 1
        bottom_spacer = QSpacerItem(10, spacer_height,
                                    QSizePolicy.Minimum,
                                    QSizePolicy.MinimumExpanding)
        
        self.VBoxLayout.addItem(bottom_spacer) # Add spacer to bottom
        
    def restore_defaults_btn_clicked(self):
        """Slot for "Restore Defaults" button in the Property Manager.
        """        
        for widget in self.widgets:
            if isinstance(widget, PropMgrGroupBox):
                widget.restoreDefault()
                
# End of PropMgrBaseClass ############################

class PropMgrWidgetMixin:
    """Property Manager Widget Mixin class.
    """
    
    def hide(self):
        """Hide this widget and its label. If hidden, the widget
        will not be displayed when its groupbox is expanded.
        Call show() to unhide this widget (and its label).
        """
        self.hidden = True
        QWidget.hide(self) # Hide self.
        if self.labelWidget:# Hide self's label if it has one.
            self.labelWidget.hide() 
            
    def show(self):
        """Show this widget and its label.
        """
        self.hidden = False
        QWidget.show(self) # Show self.
        if self.labelWidget:# Show self's label if it has one.
            self.labelWidget.show() 
        
    def collapse(self):
        """Hides this widget (and its label) when the groupbox is collapsed.
        """
        QWidget.hide(self) # Hide self.
        if self.labelWidget:# Hide self's label if it has one.
            self.labelWidget.hide() 
        
    def expand(self):
        """Shows this widget (and its label) when the groupbox is expanded,
        unless this widget is hidden (via its hidden attr).
        """
        if self.hidden: return
        QWidget.show(self) # Show self.
        if self.labelWidget:# Show self's label if it has one.
            self.labelWidget.show()
            
# End of PropMgrWidgetMixin ############################
       
class PropMgrGroupBox(QGroupBox, PropMgrWidgetMixin):
    """Group Box class for Property Manager group boxes.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    labelWidget = None # Needed for PropMgrWidgetMixin class (might use to hold title).
    expanded = True # Set to False when groupbox is collapsed.
    widgets = [] # All widgets in the groupbox (except the title button).
    num_rows = 0 # Number of rows in the groupbox.

    def __init__(self, parent, title='', titleButton=False):
        """
        Appends a QGroupBox widget to <parent>, a property manager groupbox.
        
        Arguments:
        
        <parent> - the main property manager dialog (PropMgrBaseClass).
        <title> - the GroupBox title text.
        <titleButton> - if True, a titleButton is added to the top of the
                        GroupBox with the label <title>. The titleButton is
                        used to collapse and expand the GroupBox.
                        if False, no titleButton is added. <title> will be
                        used as the GroupBox title and the GroupBox will
                        not be collapsable/expandable.
        """
        
        QGroupBox.__init__(self)
        self.parent = parent
        
        # Calling addWidget() here is important. If done at the end,
        # the title button does not get assigned its palette for some 
        # unknown reason. Mark 2007-05-20.
        parent.VBoxLayout.addWidget(self) # Add self to PropMgr's VBoxLayout
        
        self.widgets = [] # All widgets in the groupbox (except the title button).
        parent.widgets.append(self)
        
        self.setAutoFillBackground(True) 
        self.setPalette(self.getPalette())
        self.setStyleSheet(self.getStyleSheet())
        
        # Create vertical box layout
        self.VBoxLayout = QVBoxLayout(self)
        self.VBoxLayout.setMargin(pmGrpBoxVboxLayoutMargin)
        self.VBoxLayout.setSpacing(pmGrpBoxVboxLayoutSpacing)
        
        # Create grid layout
        self.GridLayout = QGridLayout()
        self.GridLayout.setMargin(pmGridLayoutMargin)
        self.GridLayout.setSpacing(pmGridLayoutSpacing)
        
        # Insert grid layout in its own VBoxLayout
        self.VBoxLayout.addLayout(self.GridLayout)
        
        if titleButton: # Add title button to GroupBox
            self.titleButton = self.getTitleButton(title, self)
            self.VBoxLayout.insertWidget(0, self.titleButton)
            self.connect(self.titleButton,SIGNAL("clicked()"),
                     self.toggleExpandCollapse)
        else:
            self.setTitle(title)
    
    def setTitle(self, title):
        """Sets the groupbox title to <title>.
        This overrides QGroupBox's setTitle() method.
        """
        # Create QLabel widget.
        self.labelWidget = QLabel()
        labelAlignment = Qt.AlignLeft | \
                           Qt.AlignLeading | \
                           Qt.AlignVCenter # Title is left justified.
        self.labelWidget.setAlignment(labelAlignment)
        self.labelWidget.setText(title)
        self.VBoxLayout.insertWidget(0, self.labelWidget)

    # Title Button Methods #####################################
    
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
        
        self.titleButtonPalette = self.getTitleButtonPalette()
        button.setPalette(self.titleButtonPalette)
        
        #ninad 070221 set a non existant 'Ghost Icon' for this button
        #By setting such an icon, the button text left aligns! 
        #(which what we want :-) )
        #So this might be a bug in Qt4.2.  If we don't use the following kludge, 
        #there is no way to left align the push button text but to subclass it. 
        #(could mean a lot of work for such a minor thing)  So OK for now 
        
        button.setIcon(geticon("ui/actions/Properties Manager/GHOST_ICON"))
        
        return button
    
    def getTitleButtonPalette(self):
        """ Return a palette for a GroupBox title button. 
        """
        return getPalette(None, QPalette.Button, pmGrpBoxButtonColor)
    
    
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
        if self.widgets:
            if self.expanded: # Collapse groupbox by hiding all widgets in groupbox.
                self.GridLayout.setMargin(0)
                self.GridLayout.setSpacing(0)
                # The styleSheet contains the expand/collapse.
                styleSheet = self.getTitleButtonStyleSheet(showExpanded = False)
                self.titleButton.setStyleSheet(styleSheet)
                # Why do we have to keep resetting the palette?
                # Does assigning a new styleSheet reset the button's palette?
                # If yes, we should add the button's color to the styleSheet.
                # Mark 2007-05-20
                self.titleButton.setPalette(self.getTitleButtonPalette())
                self.titleButton.setIcon(
                    geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for widget in self.widgets:
                    widget.collapse()
                self.expanded = False 
            else: # Expand groupbox by showing all widgets in groupbox.
                if isinstance(self, PropMgrMessageGroupBox):
                    # If we don't do this, we get a small space b/w the 
                    # title button and the MessageTextEdit widget.
                    # Extra code unnecessary, but more readable. 
                    # Mark 2007-05-21
                    self.GridLayout.setMargin(0)
                    self.GridLayout.setSpacing(0)
                else:
                    self.GridLayout.setMargin(pmGrpBoxGridLayoutMargin)
                    self.GridLayout.setSpacing(pmGrpBoxGridLayoutSpacing)
                # The styleSheet contains the expand/collapse.
                styleSheet = self.getTitleButtonStyleSheet(showExpanded = True)
                self.titleButton.setStyleSheet(styleSheet)
                # Why do we have to keep resetting the palette?
                # Does assigning a new styleSheet reset the button's palette?
                # If yes, we should add the button's color to the styleSheet.
                # Mark 2007-05-20
                self.titleButton.setPalette(self.getTitleButtonPalette())
                self.titleButton.setIcon(
                    geticon("ui/actions/Properties Manager/GHOST_ICON"))
                for widget in self.widgets:
                    widget.expand()
                self.expanded = True
            
            # This doesn't work because the bottom spacer in the layout expands
            # when a groupbox is collapsed. When I have time, I'll modify fitContents()
            # to address this by deleting the bottom spacer, computing height and adding
            # it again. I'm optimistic that this will work.
            # Mark 2007-05-23
            #self.parent.fitContents()
                
        else:
            print "Groupbox has no widgets. Clicking on groupbox button has no effect"
    
    # GroupBox palette and stylesheet methods. ##############################3
        
    def getPalette(self):
        """ Return a palette for this groupbox. 
        The color should be slightly darker (or lighter) than the property manager background.
        """
        #bgrole(10) is 'Windows'
        return getPalette(None, QPalette.ColorRole(10), pmGrpBoxColor)
    
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
    
    def restoreDefault(self):
        """Restores the default value for all widgets in this groupbox.
        """
        for widget in self.widgets:
            widget.restoreDefault()

# End of PropMgrGroupBox ############################

class PropMgrMessageGroupBox(PropMgrGroupBox):
    '''Message GroupBox class'''

    expanded = True # Set to False when groupbox is collapsed.
    widgets = [] # All widgets in the groupbox (except the title button).
    num_rows = 0 # Number of rows in the groupbox.
    
    def __init__(self, parent, title):
        """Constructor for PropMgr group box.
        <parent> is the PropMgr dialog (of type PropMgrBaseClass)
        <title> is the label used on the the title button
        """
        PropMgrGroupBox.__init__(self, parent, title, titleButton=True)
        self.setObjectName("MessageGroupBox")
        
        self.widgets = [] # All widgets in the groupbox (except the title button).
        
        self.VBoxLayout.setMargin(pmMsgGrpBoxMargin)
        self.VBoxLayout.setSpacing(pmMsgGrpBoxSpacing)
        
        self.GridLayout.setMargin(0)
        self.GridLayout.setSpacing(0)
        
        self.MessageTextEdit = PropMgrTextEdit(self, label='', spanWidth=True)
        
        parent.MessageTextEdit = self.MessageTextEdit
        
        # These two policies very important. Mark 2007-05-22
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        self.MessageTextEdit.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))
        
        # Hide until insertHtmlMessage() loads a message.
        self.hide()
        
    def insertHtmlMessage(self, text, setAsDefault=False):
        """Insert <text> (HTML) into the Prop Mgr's message groupbox.
        Show the message groupbox.
        """
        self.MessageTextEdit.insertHtml(text, setAsDefault)
        self.show()
        
# End of PropMgrMessageGroupBox ############################

class PropMgrTextEdit(QTextEdit, PropMgrWidgetMixin):
    """PropMgr TextEdit class, for groupboxes (PropMgrGroupBox) only.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to True if "Restore Defaults" should 
    # reset this widget's text to defaultText.
    setAsDefault = False
    defaultText = '' # Default text
    
    def __init__(self, parent, label='', spanWidth=False):
        """
        Appends a QTextEdit widget to <parent>, a property manager groupbox.
        The QTextEdit is empty (has no text) by default. Use insertHtml() 
        to insert HTML text into the TextEdit.
        
        Arguments:
        
        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left (or above) of the TextEdit.
        <spanWidth> - if True, the TextEdit and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the TextEdit (unless the label is empty) left justified.
        """
        
        if 0: # Debugging code
            print "QTextEdit.__init__():"
            print "  label=", label
            print "  spanWidth=",spanWidth
        
        if not parent:
            return
        
        QTextEdit.__init__(self)
        
        # Temporary kludge for A9 prerelease. Mark 2007-05-22
        # The problem: I cannot figure out how to set props such
        #   that the textedit height will auto-adjust to fit the 
        #   contents.
        if sys.platform == 'darwin': 
            self.setMinimumSize(40,80) #@ Compute using FontMetrics.
            self.setMaximumSize(300,80)
        else:
            self.setMinimumSize(40,50) #@ Compute using FontMetrics.
            self.setMaximumSize(300,50)
        
        # wrapWrapMode seems to be set to QTextOption.WrapAnywhere on MacOS,
        # so let's force it here. Mark 2007-05-22.
        self.setWordWrapMode(QTextOption.WordWrap)
        
        # Curious to see what this is on MacOS. Mark 2007-05-23
        #print "PropMgrTextEdit.wordWrapMode=", self.wordWrapMode()
        
        # A function that returns all the widget and label layout params.
        widgetRow, widgetColumn, widgetSpanCols, incRows, \
        labelRow, labelColumn, labelSpanCols, labelAlignment = \
        getWidgetGridLayoutParms(label, parent.num_rows, spanWidth)
        
        if label:
            # Create QLabel widget.
            self.labelWidget = QLabel()
            self.labelWidget.setAlignment(labelAlignment)
            self.labelWidget.setText(label)
            parent.GridLayout.addWidget(self.labelWidget,
                                        labelRow, 0,
                                        1, labelSpanCols)
        else:
            self.labelWidget = None
        
        if isinstance(parent, PropMgrMessageGroupBox):
            # Add to parent's VBoxLayout if <parent> is a MessageGroupBox.
            parent.VBoxLayout.addWidget(self)
            self.setPalette(self.getMessageTextEditPalette())
            self.setReadOnly(True)
            self.setObjectName("MessageTextEdit")
        else:
            # Add to parent's GridLayout (default).
            parent.GridLayout.addWidget(self,
                                        widgetRow, widgetColumn,
                                        1, widgetSpanCols)
        parent.widgets.append(self)
        
        parent.num_rows += incRows
        
    def insertHtml(self, text, setAsDefault=False):
        """Insert <text> (HTML) into the Prop Mgr's message groupbox.
        """
        if setAsDefault:
            self.defaultText = text
            self.setAsDefault = True
    
        QTextEdit.insertHtml(self, text)
        
    def getMessageTextEditPalette(self):
        """ Returns a (yellow) palette a message TextEdit.
        """
        return getPalette(None,
                          QPalette.Base,
                          pmMessageTextEditColor)
        
    def restoreDefault(self):
        """Restores the default value for this widget.
        Does nothing if the attr "setAsDefault" is False.
        """
        if self.setAsDefault:
            self.insertHtml(self.defaultText, True)

# End of PropMgrTextEdit ############################

class PropMgrDoubleSpinBox(QDoubleSpinBox, PropMgrWidgetMixin):
    """PropMgr SpinBox class, for groupboxes (PropMgrGroupBox) only.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not 
    # reset this widget's value to val.
    setAsDefault = True
    defaultValue = 0 # Default value of spinbox
    
    def __init__(self, parent, label='', 
                 val=0, setAsDefault=True,
                 min=0, max=99,
                 singleStep=1.0, decimals=1, 
                 suffix='',
                 spanWidth=False):
        """
        Appends a QDoubleSpinBox widget to <parent>, a property manager groupbox.
        
        Arguments:
        
        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left (or above) of the SpinBox.
        <val> - initial value of SpinBox.
        <setAsDefault> - if True, will restore <val>
                         when the "Restore Defaults" button is clicked.
        <min> - minimum value in the SpinBox.
        <max> - maximum value in the SpinBox.
        <decimals> - precision of SpinBox.
        <singleStep> - increment/decrement value when user uses arrows.
        <suffix> - suffix.
        <spanWidth> - if True, the SpinBox and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the SpinBox (unless the label is empty) left justified.
        """
        
        if 0: # Debugging code
            print "PropMgrSpinBox.__init__():"
            print "  label=", label
            print "  val =", val
            print "  setAsDefault =", setAsDefault
            print "  min =", min
            print "  max =", max
            print "  singleStep =", singleStep
            print "  decimals =", decimals
            print "  suffix =", suffix
            print "  spanWidth =", spanWidth
        
        if not parent:
            return
        
        QDoubleSpinBox.__init__(self)
        
        # A function that returns all the widget and label layout params.
        widgetRow, widgetColumn, widgetSpanCols, incRows, \
        labelRow, labelColumn, labelSpanCols, labelAlignment = \
        getWidgetGridLayoutParms(label, parent.num_rows, spanWidth)
        
        if label:
            # Create QLabel widget.
            self.labelWidget = QLabel()
            self.labelWidget.setAlignment(labelAlignment)
            self.labelWidget.setText(label)
            parent.GridLayout.addWidget(self.labelWidget,
                                        labelRow, 0,
                                        1, labelSpanCols)
        else:
            self.labelWidget = None
        
        # Set QDoubleSpinBox min, max, singleStep, decimals, then val
        self.setRange(min, max)
        self.setSingleStep(singleStep)
        self.setDecimals(decimals)
        self.setValue(val) # This must come after setDecimals().
        
        # Set default value
        self.defaultValue=val
        self.setAsDefault = setAsDefault
        
        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)
        
        parent.GridLayout.addWidget(self,
                                    widgetRow, widgetColumn,
                                    1, widgetSpanCols)
        parent.widgets.append(self)
        
        parent.num_rows += incRows
        
    def restoreDefault(self):
        """Restores the default value for this widget.
        Does nothing if the attr "setAsDefault" is False.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)

# End of PropMgrDoubleSpinBox ############################

class PropMgrSpinBox(QSpinBox, PropMgrWidgetMixin):
    """PropMgr SpinBox class, for groupboxes (PropMgrGroupBox) only.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not 
    # reset this widget's value to val.
    setAsDefault = True
    defaultValue = 0 # Default value of spinbox
    
    def __init__(self, parent, label='', 
                 val=0, setAsDefault=True,
                 min=0, max=99,
                 suffix='',
                 spanWidth=False):
        """
        Appends a QSpinBox widget to <parent>, a property manager groupbox.
        
        Arguments:
        
        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left of (or above) the SpinBox.
        <val> - initial value of SpinBox.
        <setAsDefault> - if True, will restore <val>
                         when the "Restore Defaults" button is clicked.
        <min> - minimum value in the SpinBox.
        <max> - maximum value in the SpinBox.
        <suffix> - suffix.
        <spanWidth> - if True, the SpinBox and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the SpinBox (unless the label is empty) left justified.
        """
        
        if 0: # Debugging code
            print "PropMgrSpinBox.__init__():"
            print "  label=", label
            print "  val =", val
            print "  setAsDefault =", setAsDefault
            print "  min =", min
            print "  max =", max
            print "  suffix =", suffix
            print "  spanWidth =", spanWidth
        
        if not parent:
            return
        
        QSpinBox.__init__(self)
        
        # A function that returns all the widget and label layout params.
        widgetRow, widgetColumn, widgetSpanCols, incRows, \
        labelRow, labelColumn, labelSpanCols, labelAlignment = \
        getWidgetGridLayoutParms(label, parent.num_rows, spanWidth)
        
        if label:
            # Create QLabel widget.
            self.labelWidget = QLabel()
            self.labelWidget.setAlignment(labelAlignment)
            self.labelWidget.setText(label)
            parent.GridLayout.addWidget(self.labelWidget,
                                        labelRow, 0,
                                        1, labelSpanCols)
        else:
            self.labelWidget = None
        
        # Set QSpinBox min, max and initial value
        self.setRange(min, max)
        self.setValue(val)
        
        # Set default value
        self.defaultValue=val
        self.setAsDefault = setAsDefault
        
        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)
        
        parent.GridLayout.addWidget(self,
                                    widgetRow, widgetColumn,
                                    1, widgetSpanCols)
        parent.widgets.append(self)
        
        parent.num_rows += incRows
        
    def restoreDefault(self):
        """Restores the default value for this widget.
        Does nothing if the attr "setAsDefault" is False.
        """
        if self.setAsDefault:
            self.setValue(self.defaultValue)

# End of PropMgrSpinBox ############################

class PropMgrComboBox(QComboBox, PropMgrWidgetMixin):
    """PropMgr ComboBox class.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not 
    # reset this widget's choice index to idx.
    setAsDefault = True
    # <defaultIdx> - default index when "Restore Default" is clicked
    defaultIdx = 0
    
    def __init__(self, parent, label='', 
                 choices=[], idx=0, setAsDefault=True,
                 spanWidth=False):
        """
        Appends a QComboBox widget to <parent>, a property manager groupbox.
        
        Arguments:
        
        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left of (or above) the ComboBox.
        <choices> - list of choices (strings) in the ComboBox.
        <idx> - initial index (choice) of combobox. (0=first item)
        <setAsDefault> - if True, will restore <idx> as the current index
                         when the "Restore Defaults" button is clicked.
        <spanWidth> - if True, the ComboBox and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the ComboBox (unless the label is empty) left justified.
        """
        
        if 0: # Debugging code
            print "PropMgrComboBox.__init__():"
            print "  label=",label
            print "  choices =", choices
            print "  idx =", idx
            print "  setAsDefault =", setAsDefault
            print "  spanWidth =", spanWidth
        
        if not parent:
            return
        
        QComboBox.__init__(self)
        
        # A function that returns all the widget and label layout params.
        widgetRow, widgetColumn, widgetSpanCols, incRows, \
        labelRow, labelColumn, labelSpanCols, labelAlignment = \
        getWidgetGridLayoutParms(label, parent.num_rows, spanWidth)
        
        if label:
            # Create QLabel widget.
            self.labelWidget = QLabel()
            self.labelWidget.setAlignment(labelAlignment)
            self.labelWidget.setText(label)
            parent.GridLayout.addWidget(self.labelWidget,
                                        labelRow, 0,
                                        1, labelSpanCols)
        else:
            self.labelWidget = None
        
        # Load QComboBox widget choices and set initial choice (index).
        for i in range(len(choices)):
            self.addItem(choices[i])
        self.setCurrentIndex(idx)
        
        # Set default index
        self.defaultIdx=idx
        self.setAsDefault = setAsDefault
        
        parent.GridLayout.addWidget(self,
                                    widgetRow, widgetColumn,
                                    1, widgetSpanCols)
        parent.widgets.append(self)
        
        parent.num_rows += incRows
    
    def restoreDefault(self):
        """Restores the default choice index for this widget.
        Does nothing if the attr "setAsDefault" is False.
        """
        if self.setAsDefault:
            self.setCurrentIndex(self.defaultIdx)

# End of PropMgrComboBox ############################
