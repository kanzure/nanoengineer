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
mark 2007-05-25: Added PropMgrPushButton
mark 2007-05-28: Added PropMgrLineEdit, PropMgrCheckBox and PropMgrListWidget
ninad 2007-06-03: Added PropMgrToolButton
ninad 2007-06-05: Added PropMgrRadioButton
bruce 2007-06-15: partly cleaned up inheritance.

"""

__author__ = "Mark"

# Mark's To Do List (by order of priority): updated 2007-06-21
# - Add new "parentPropMgr" attr for all widget classes. (important)
# - Support horizontal resizing using splitter (A9.1 backlog item)
# - Finish support for Restore Defaults:
#    - PropMgrComboBox.setItems() and PropMgrComboBox.setCurrentIndex()
#    - PropMgrComboBox.setText()
# - Add color theme user pref in Preferences dialog. (minor)
# - Set title button color via style sheet (see getTitleButtonStyleSheet)
# - "range" attr (str) that can be included in What's This text. (minor)
# - override setObjectName() in PropMgrWidgetMixin class to create
#   standard names.
# - Add important PropMgr widget classes:
#   - PropMgrMMKit (needed by BuildAtomsPropertyManager, a future PropMgr)
#   - PropMgrColorChooser
#   - PropMgrLabel
#   - PropMgrGroupAction (needed by PlanePropertyManager)

import os

from PyQt4 import QtCore

from PyQt4.Qt import Qt
from PyQt4.Qt import QGroupBox
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QDoubleSpinBox
from PyQt4.Qt import QSpinBox
from PyQt4.Qt import QComboBox
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QLineEdit
from PyQt4.Qt import QCheckBox
from PyQt4.Qt import QListWidget
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QPalette
from PyQt4.Qt import QFrame
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QLabel
from PyQt4.Qt import QWidget
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QGridLayout
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QSize
from PyQt4.Qt import QRadioButton
from PyQt4.Qt import QTextCursor

from utilities import debug_flags

from utilities.icon_utilities import geticon, getpixmap
from utilities.debug import print_compact_traceback

from PM.PropMgr_Constants import pmColor
from PM.PropMgr_Constants import pmTitleFrameColor
from PM.PropMgr_Constants import pmTitleLabelColor
from PM.PropMgr_Constants import pmMinWidth
from PM.PropMgr_Constants import pmDefaultWidth
from PM.PropMgr_Constants import pmLabelRightAlignment
from PM.PropMgr_Constants import pmLabelLeftAlignment
from PM.PropMgr_Constants import pmMainVboxLayoutMargin
from PM.PropMgr_Constants import pmMainVboxLayoutSpacing
from PM.PropMgr_Constants import pmHeaderFrameMargin
from PM.PropMgr_Constants import pmHeaderFrameSpacing
from PM.PropMgr_Constants import getHeaderFont
from PM.PropMgr_Constants import pmSponsorFrameMargin
from PM.PropMgr_Constants import pmSponsorFrameSpacing
from PM.PropMgr_Constants import pmTopRowBtnsMargin
from PM.PropMgr_Constants import pmTopRowBtnsSpacing
from PM.PropMgr_Constants import pmGroupBoxSpacing
from PM.PropMgr_Constants import pmGrpBoxVboxLayoutMargin
from PM.PropMgr_Constants import pmGrpBoxVboxLayoutSpacing
from PM.PropMgr_Constants import pmGridLayoutMargin
from PM.PropMgr_Constants import pmGridLayoutSpacing
from PM.PropMgr_Constants import pmGrpBoxButtonColor
from PM.PropMgr_Constants import pmGrpBoxButtonBorderColor
from PM.PropMgr_Constants import pmGrpBoxButtonTextColor
from PM.PropMgr_Constants import pmGrpBoxExpandedImage
from PM.PropMgr_Constants import pmGrpBoxCollapsedImage
from PM.PropMgr_Constants import pmGrpBoxGridLayoutMargin
from PM.PropMgr_Constants import pmGrpBoxGridLayoutSpacing
from PM.PropMgr_Constants import pmGrpBoxColor
from PM.PropMgr_Constants import pmGrpBoxBorderColor
from PM.PropMgr_Constants import pmMsgGrpBoxMargin
from PM.PropMgr_Constants import pmMsgGrpBoxSpacing
from PM.PropMgr_Constants import pmMessageTextEditColor
from PM.PropMgr_Constants import pmDoneButton
from PM.PropMgr_Constants import pmCancelButton
from PM.PropMgr_Constants import pmRestoreDefaultsButton
from PM.PropMgr_Constants import pmPreviewButton
from PM.PropMgr_Constants import pmWhatsThisButton

# Special Qt debugging functions written by Mark. 2007-05-24 ############

def getSizePolicyName(sizepolicy):
    """Returns the formal name of <sizepolicy>, a QSizePolicy.
    FYI:
    QSizePolicy.GrowFlag   = 1
    QSizePolicy.ExpandFlag = 2
    QSizePolicy.ShrinkFlag = 4
    QSizePolicy.IgnoreFlag = 8
    """
    assert isinstance(sizepolicy, QSizePolicy)

    if sizepolicy == QSizePolicy.Fixed:
        name = "SizePolicy.Fixed"
    if sizepolicy == QSizePolicy.GrowFlag:
        name = "SizePolicy.Minimum"
    if sizepolicy == QSizePolicy.ShrinkFlag:
        name = "SizePolicy.Maximum"
    if sizepolicy == (QSizePolicy.GrowFlag | QSizePolicy.ShrinkFlag):
        name = "SizePolicy.Preferred"
    if sizepolicy == (QSizePolicy.GrowFlag | QSizePolicy.ShrinkFlag |QSizePolicy.ExpandFlag):
        name = "SizePolicy.Expanding"
    if sizepolicy == (QSizePolicy.GrowFlag | QSizePolicy.ExpandFlag):
        name = "SizePolicy.MinimumExpanding"
    if sizepolicy == (QSizePolicy.ShrinkFlag | QSizePolicy.GrowFlag | QSizePolicy.IgnoreFlag):
        name = "SizePolicy.Ignored"
    return name

def printSizePolicy(widget):
    """Special method for debugging Qt sizePolicies.
    Prints the horizontal and vertical policy of <widget>.
    """
    sizePolicy = widget.sizePolicy()
    print "-----------------------------------"
    print "Widget name =", widget.objectName()
    print "Horizontal SizePolicy =", getSizePolicyName(sizePolicy.horizontalPolicy())
    print "Vertical SizePolicy =",   getSizePolicyName(sizePolicy.verticalPolicy()
    )
def printSizeHints(widget):
    """Special method for debugging Qt size hints.
    Prints the minimumSizeHint (width and height)
    and the sizeHint (width and height) of <widget>.
    """
    print "-----------------------------------"
    print "Widget name =", widget.objectName()
    print "Current Width, Height =", widget.width(), widget.height()
    minSize = widget.minimumSizeHint()
    print "Min Width, Height =", minSize.width(), minSize.height()
    sizeHint = widget.sizeHint()
    print "SizeHint Width, Height =", sizeHint.width(), sizeHint.height()

# PropMgr helper functions ##########################################

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
        labelAlignment = pmLabelRightAlignment

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
            labelAlignment = pmLabelLeftAlignment

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

class PropertyManager_common: #bruce 070615 split this out of class PropertyManagerMixin
    """Methods common to PropertyManagerMixin and PropMgrBaseClass.
    """
    def getPropertyManagerPalette(self):
        """ Return a palette for the property manager.
        """
        # in future we might want to set different palette colors for prop managers.
        return self.getPalette(None,
                               QPalette.ColorRole(10),
                               pmColor)

    def getPropMgrTitleFramePalette(self): # note: used only by PropMgrBaseClass as of 070615
        """ Return a palette for Property Manager title frame.
        """
        #bgrole(10) is 'Windows'
        return self.getPalette(None,
                               QPalette.ColorRole(10),
                               pmTitleFrameColor)

    def getPropMgrTitleLabelPalette(self): # note: used only by PropMgrBaseClass as of 070615
        """ Return a palette for Property Manager title label.
        """
        return self.getPalette(None,
                               QPalette.WindowText,
                               pmTitleLabelColor)

    def getPropMgrGroupBoxPalette(self): # note: used only by MessageGroupBox as of 070621
        """ Return a palette for Property Manager groupbox.
        """
        return self.getPalette(None,
                               QPalette.ColorRole(10),
                               pmGrpBoxColor)

    def getTitleButtonPalette(self): # note: used only by MessageGroupBox as of 070621
        """ Return a palette for a GroupBox title button.
        """
        return self.getPalette(None,
                               QPalette.Button,
                               pmGrpBoxButtonColor)


    def getMessageTextEditPalette(self): # note: used only by MessageGroupBox as of 070621
        """ Return a palette for a MessageGroupBox TextEdit (yellow).
        """
        return self.getPalette(None,
                               QPalette.Base,
                               pmMessageTextEditColor)


    def getPalette(self, palette, obj, color): #k maybe only used by methods in this class (not sure) [bruce 070615]
        """ Given a palette, Qt object [actually a ColorRole] and a color, return a new palette.
        If palette is None, create and return a new palette.
        """
        #bruce 070615 replaced with call to another (preexisting) function which has same name and identical code.
        return getPalette(palette, obj, color)

    ###e move more methods here?

    pass # end of class PropertyManager_common

# ==

class PropMgrBaseClass(PropertyManager_common): #bruce 070615 inherit PropertyManager_common, so GBC doesn't need to for our sake
    """Property Manager base class.
    [To make a PM class from this mixin-superclass, subclass it to customize
    the widget set and add behavior, and inherit QDialog (before this class).
    You must also provide certain methods provided by GeneratorBaseClass
    (either by inheriting it -- not sure if superclass order matters for that --
     or by defining them yourself), including ok_btn_clicked and several others,
     including at least some defined by SponsorableMixin (open_sponsor_homepage, setSponsor).
     This set of requirements may be cleaned up.]
    [Note: Technically, this is not a "base class" but a "mixin class".]
    """

    widgets = [] # All widgets in the PropMgr dialog
    num_groupboxes = 0 # Number of groupboxes in PropMgr.
    lastGroupBox = None # The last groupbox in this PropMgr
                        # (i.e. the most recent GroupBox added).
    pmHeightComputed = False # See show() for explaination.

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

        if 0: # For me. Mark 2007-05-17.
            self.debugSizePolicy()

        # Keep this around; it might be useful.
        # I may want to use it now that I understand it.
        # Mark 2007-05-17.
        #QMetaObject.connectSlotsByName(self)

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

        if 1: # Print the current sizePolicies.
            printSizePolicy(self)
            printSizePolicy(self.MessageGroupBox)
            printSizePolicy(self.MessageTextEdit)

    def show(self):
        """Show the Property Manager.
        """
        self.setSponsor()
        if not self.pw or self:
            self.pw = self.win.activePartWindow()       #@@@ ninad061206
            self.pw.updatePropertyManagerTab(self) # Redundant code. Fix after A9. Mark 2007-06-01
            self.pw.featureManager.setCurrentIndex(self.pw.featureManager.indexOf(self))
        else:
            self.pw.updatePropertyManagerTab(self)
            self.pw.featureManager.setCurrentIndex(self.pw.featureManager.indexOf(self))

        if not self.pmHeightComputed:
            # This fixes a bug (discovered by Ninad) in which the
            # user *reenters* the PropMgr, and the PropMgr has a
            # collapsed groupbox. When the user expands the collapsed groupbox,
            # widgets are "crushed" in all expanded groupboxes. Mark 2007-05-24
            self.fitContents() # pmHeightComputed set to True in fitContents().

        # Show the default message whenever we open the Property Manager.
        self.MessageGroupBox.MessageTextEdit.restoreDefault()

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
            printSizeHints(self)

        pmWidth = pmDefaultWidth - (4 * 2)
        pmHeight = self.sizeHint().height()
        self.pmHeightComputed = True # See show() for explanation.

        self.resize(pmWidth, pmHeight)

        # Save this. May need it when we support resizing via splitter.
        #self.resize(QSize(
        #    QRect(0,0,pmWidth,pmHeight).size()).
        #    expandedTo(self.minimumSizeHint()))

        if 0:
            print "PropMgr.fitContents(): Width, Height =", self.width(), self.height()

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

        # PropMgr title label
        self.header_label = QLabel(self.header_frame)
        header_label_palette = self.getPropMgrTitleLabelPalette()
        self.header_label.setPalette(header_label_palette)
        self.header_label.setAlignment(pmLabelLeftAlignment)

        # PropMgr heading font (for label).
        self.header_label.setFont(getHeaderFont())
        HeaderFrameHLayout.addWidget(self.header_label)

        self.VBoxLayout.addWidget(self.header_frame)

    def setPropMgrTitle(self, title):
        """Set the Property Manager header title to string <title>.
        """
        self.header_label.setText(title)

    def setPropMgrIcon(self, png_path):
        """Set the Property Manager icon in the header.
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

        button_whatsthis_widget = self.sponsor_btn
            #bruce 070615 bugfix -- put tooltip & whatsthis on self.sponsor_btn, not self.
            # [self.sponsor_frame might be another possible place to put them.]

        button_whatsthis_widget.setWhatsThis("""<b>Sponsor Button</b>
            <p>When clicked, this sponsor logo will display a short
            description about a NanoEngineer-1 sponsor. This can
            be an official sponsor or credit given to a contributor
            that has helped code part or all of this command.
            A link is provided in the description to learn more
            about this sponsor.</p>""")

        button_whatsthis_widget.setToolTip("NanoEngineer-1 Sponsor Button")

        return

    def addTopRowBtns(self, showFlags=None):
        """Creates the OK, Cancel, Preview, and What's This
        buttons row at the top of the Pmgr.
        """
        # The Top Buttons Row includes the following widgets:
        #
        # - self.pmTopRowBtns (Hbox Layout containing everything:)
        #
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
        # This QHBoxLayout is (probably) not necessary. Try using just the frame for
        # the foundation. I think it should work. Mark 2007-05-30

        # Horizontal spacer
        HSpacer = QSpacerItem(1, 1,
                                QSizePolicy.Expanding,
                                QSizePolicy.Minimum)

        # Frame containing all the buttons.
        self.TopRowBtnsFrame = QFrame()

        self.TopRowBtnsFrame.setFrameShape(QFrame.NoFrame)
        self.TopRowBtnsFrame.setFrameShadow(QFrame.Plain)

        # Create Hbox layout for main frame.
        TopRowBtnsHLayout = QHBoxLayout(self.TopRowBtnsFrame)
        TopRowBtnsHLayout.setMargin(pmTopRowBtnsMargin)
        TopRowBtnsHLayout.setSpacing(pmTopRowBtnsSpacing)

        TopRowBtnsHLayout.addItem(HSpacer)

        # Set button type.
        if 1: # Mark 2007-05-30
            # Needs to be QToolButton for MacOS. Fine for Windows, too.
            buttonType = QToolButton
            # May want to use QToolButton.setAutoRaise(1) below. Mark 2007-05-29
        else:
            buttonType = QPushButton # Do not use.

        # OK (Done) button.
        self.done_btn = buttonType(self.TopRowBtnsFrame)
        self.done_btn.setIcon(
            geticon("ui/actions/Properties Manager/Done.png"))
        self.done_btn.setIconSize(QSize(22,22))
        self.connect(self.done_btn,SIGNAL("clicked()"),
                     self.ok_btn_clicked)
        self.done_btn.setToolTip("Done")

        TopRowBtnsHLayout.addWidget(self.done_btn)

        # Cancel (Abort) button.
        self.abort_btn = buttonType(self.TopRowBtnsFrame)
        self.abort_btn.setIcon(
            geticon("ui/actions/Properties Manager/Abort.png"))
        self.abort_btn.setIconSize(QSize(22,22))
        self.connect(self.abort_btn,SIGNAL("clicked()"),
                     self.abort_btn_clicked)
        self.abort_btn.setToolTip("Cancel")

        TopRowBtnsHLayout.addWidget(self.abort_btn)

        # Restore Defaults button.
        self.restore_defaults_btn = buttonType(self.TopRowBtnsFrame)
        self.restore_defaults_btn.setIcon(
            geticon("ui/actions/Properties Manager/Restore.png"))
        self.restore_defaults_btn.setIconSize(QSize(22,22))
        self.connect(self.restore_defaults_btn,SIGNAL("clicked()"),
                     self.restore_defaults_btn_clicked)
        self.restore_defaults_btn.setToolTip("Restore Defaults")
        TopRowBtnsHLayout.addWidget(self.restore_defaults_btn)

        # Preview (glasses) button.
        self.preview_btn = buttonType(self.TopRowBtnsFrame)
        self.preview_btn.setIcon(
            geticon("ui/actions/Properties Manager/Preview.png"))
        self.preview_btn.setIconSize(QSize(22,22))
        self.connect(self.preview_btn,SIGNAL("clicked()"),
                     self.preview_btn_clicked)
        self.preview_btn.setToolTip("Preview")

        TopRowBtnsHLayout.addWidget(self.preview_btn)

        # What's This (?) button.
        self.whatsthis_btn = buttonType(self.TopRowBtnsFrame)
        self.whatsthis_btn.setIcon(
            geticon("ui/actions/Properties Manager/WhatsThis.png"))
        self.whatsthis_btn.setIconSize(QSize(22,22))
        self.connect(self.whatsthis_btn,SIGNAL("clicked()"),
                     self.enter_WhatsThisMode)
        self.whatsthis_btn.setToolTip("What\'s This Help")

        TopRowBtnsHLayout.addWidget(self.whatsthis_btn)

        TopRowBtnsHLayout.addItem(HSpacer)

        # Create Button Row
        self.pmTopRowBtns.addWidget(self.TopRowBtnsFrame)

        self.VBoxLayout.addLayout(self.pmTopRowBtns)

        # Add What's This for buttons.

        self.done_btn.setWhatsThis("""<b>Done</b>
            <p><img source=\"ui/actions/Properties Manager/Done.png\"><br>
            Completes and/or exits the current command.</p>""")

        self.abort_btn.setWhatsThis("""<b>Cancel</b>
            <p><img source=\"ui/actions/Properties Manager/Abort.png\"><br>
            Cancels the current command.</p>""")

        self.restore_defaults_btn.setWhatsThis("""<b>Restore Defaults</b>
            <p><img source=\"ui/actions/Properties Manager/Restore.png\"><br>
            Restores the defaut values of the Property Manager.</p>""")

        self.preview_btn.setWhatsThis("""<b>Preview</b>
            <p><img source=\"ui/actions/Properties Manager/Preview.png\"><br>
            Preview the structure based on current Property Manager settings.</p>""")

        self.whatsthis_btn.setWhatsThis("""<b>What's This</b>
            <p><img source=\"ui/actions/Properties Manager/WhatsThis.png\"><br>
            Click this option to invoke a small question mark that is attached to the mouse pointer,
            then click on an object which you would like more information about.
            A pop-up box appears with information about the object you selected.</p>""")

        return

    def hideTopRowButtons(self, pmButtonFlags=None):
        """Hide one or more top row buttons using <pmButtonFlags>.
        Button flags not set will cause the button to be shown
        if currently hidden.

        The button flags are:
            pmDoneButton = 1
            pmCancelButton = 2
            pmRestoreDefaultsButton = 4
            pmPreviewButton = 8
            pmWhatsThisButton = 16
            pmAllButtons = 31

        These flags are defined in PropMgr_Constants.py.
        """

        if pmButtonFlags & pmDoneButton: self.done_btn.hide()
        else: self.done_btn.show()

        if pmButtonFlags & pmCancelButton: self.abort_btn.hide()
        else: self.abort_btn.show()

        if pmButtonFlags & pmRestoreDefaultsButton:
            self.restore_defaults_btn.hide()
        else: self.restore_defaults_btn.show()

        if pmButtonFlags & pmPreviewButton: self.preview_btn.hide()
        else: self.preview_btn.show()

        if pmButtonFlags & pmWhatsThisButton: self.whatsthis_btn.hide()
        else: self.whatsthis_btn.show()

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

    def addWidgetAndLabelToParent(self, parent, label, spanWidth):
        """Add this widget and its label to <parent>.
        <label> is the text for this widget's label. If <label> is
        empty, no label will be added.
        If <spanWidth> (boolean) is True, the widget (and its label)
        will span the entire width of <parent> (a groupbox).
        """

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

        parent.GridLayout.addWidget(self,
                                    widgetRow, widgetColumn,
                                    1, widgetSpanCols)
        parent.widgets.append(self)

        parent.num_rows += incRows


    def hide(self):
        """Hide this widget and its label. If hidden, the widget
        will not be displayed when its groupbox is expanded.
        Call show() to unhide this widget (and its label).
        """
        self.hidden = True
        QWidget.hide(self) # Hide self.
        if self.labelWidget:# Hide self's label if it has one.
            self.labelWidget.hide()

        if isinstance(self, PropMgrGroupBox):
            # Change the spacer height to zero to "hide" it unless
            # self is the last GroupBox in the Property Manager.
            # if not self.parent.lastGroupBox is self and \
            if self.VSpacerWidget:
                self.VSpacerWidget.changeSize(10, 0)

    def show(self):
        """Show this widget and its label.
        """
        self.hidden = False
        QWidget.show(self) # Show self.
        if self.labelWidget:# Show self's label if it has one.
            self.labelWidget.show()

        if isinstance(self, PropMgrGroupBox):
            # Reset the height of the VSpacerWidget, if this groupbox has one.
            if self.VSpacerWidget:
                self.VSpacerWidget.changeSize(10, self.VSpacerWidget.defaultHeight)

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

    def restoreDefault(self):
        """Restores the default value this widget.

        Note: Need to disconnect and reconnect wigdets to slots.
        """

        if 0: # Debugging. Mark 2007-05-25
            if self.setAsDefault:
                print "Restoring default for ", self.objectName()

        if isinstance(self, PropMgrGroupBox):
            for widget in self.widgets:
                widget.restoreDefault()

        if isinstance(self, PropMgrTextEdit):
            if self.setAsDefault:
                self.insertHtml(self.defaultText,
                                setAsDefault = True,
                                replace = True)

        if isinstance(self, PropMgrDoubleSpinBox):
            if self.setAsDefault:
                self.setValue(self.defaultValue)

        if isinstance(self, PropMgrSpinBox):
            if self.setAsDefault:
                self.setValue(self.defaultValue)

        if isinstance(self, PropMgrComboBox):
            if self.setAsDefault:
                self.clear()
                for choice in self.defaultChoices:
                    self.addItem(choice)
                self.setCurrentIndex(self.defaultIdx)

        if isinstance(self, PropMgrPushButton):
            if self.setAsDefault:
                self.setText(self.defaultText)

        if isinstance(self, PropMgrLineEdit):
            if self.setAsDefault:
                self.setText(self.defaultText)

        if isinstance(self, PropMgrCheckBox):
            if self.setAsDefault:
                self.setCheckState(self.defaultState)

        if isinstance(self, PropMgrListWidget):
            if self.setAsDefault:
                self.insertItems(0, self.defaultItems)
                self.setCurrentRow(self.defaultRow)
                '''
                self.clear()
                for choice in self.defaultChoices:
                    self.addItem(choice)
                self.setCurrentRow(self.defaultRow)
                '''

# End of PropMgrWidgetMixin ############################

class PropMgrGroupBox(QGroupBox, PropMgrWidgetMixin):
    """Group Box class for Property Manager group boxes.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    labelWidget = None # Needed for PropMgrWidgetMixin class (might use to hold title).
    expanded = True # Set to False when groupbox is collapsed.
    widgets = [] # All widgets in the groupbox (except the title button).
    num_rows = 0 # Number of rows in this groupbox.
    num_groupboxes = 0 # Number of groupboxes in this groupbox.
    lastGroupBox = None # The last groupbox in this GroupBox
                        # (i.e. the most recent GroupBox added).
    setAsDefault = True # If set to False, no widgets in this groupbox will be
                        # reset to their default value when the Restore Defaults
                        # button is clicked, regardless thier own <setAsDefault> value.

    def __init__(self, parent, title='', titleButton=False, setAsDefault=True):
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
        <setAsDefault> - if False, no widgets in this groupbox will have thier
                        default values restored when the Restore Defaults
                        button is clicked, regardless thier own <setAsDefault> value.
        """

        QGroupBox.__init__(self)

        self.parent = parent
        parent.num_groupboxes += 1
        num_groupboxes = 0

        self.setObjectName(parent.objectName() +
                           "/pmGroupBox" +
                           str(parent.num_groupboxes))

        self.setAsDefault = setAsDefault

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

        # Fixes the height of the groupbox. Very important. Mark 2007-05-29
        self.setSizePolicy(
            QSizePolicy(QSizePolicy.Policy(QSizePolicy.Preferred),
                        QSizePolicy.Policy(QSizePolicy.Fixed)))

        self.addBottomSpacer()

    def addBottomSpacer(self):
        """Add a vertical spacer below this groupbox <self>.
        Assume <self> is going to be the last groupbox in this PropMgr, so set
        its spacer's vertical sizePolicy to MinimumExpanding. We then set the
        vertical sizePolicy of the last groupbox's spacer to Fixed and set its
        height to pmGroupBoxSpacing.
        """
        # Spacers are only added to groupboxes in the PropMgr, not
        # nested groupboxes.
        if not isinstance(self.parent, PropMgrBaseClass):
            self.VSpacerWidget = None
            return

        if self.parent.lastGroupBox:
            # lastGroupBox is no longer the last one. <self> will be the
            # lastGroupBox, so we must change the VSpacerWidget height
            # and sizePolicy of lastGroupBox to be a fixed
            # spacer between it and <self>.
            defaultHeight = pmGroupBoxSpacing
            self.parent.lastGroupBox.VSpacerWidget.changeSize(
                10, defaultHeight,
                QSizePolicy.Fixed,
                QSizePolicy.Fixed)
            self.parent.lastGroupBox.VSpacerWidget.defaultHeight = defaultHeight

        # Add a 1 pixel high, MinimumExpanding VSpacer below this GroupBox.
        # This keeps the PropMgr layout squeezed together as groupboxes
        # are expanded, collapsed, hidden and shown again.
        defaultHeight = 1
        self.VSpacerWidget = QSpacerItem(10, defaultHeight,
                                        QSizePolicy.Fixed,
                                        QSizePolicy.MinimumExpanding)

        self.VSpacerWidget.defaultHeight = defaultHeight

        self.parent.VBoxLayout.addItem(self.VSpacerWidget)

        # This groupbox is now the last one in the PropMgr.
        self.parent.lastGroupBox = self

    def setTitle(self, title):
        """Sets the groupbox title to <title>.
        This overrides QGroupBox's setTitle() method.
        """
        # Create QLabel widget.
        self.labelWidget = QLabel()
        labelAlignment = pmLabelLeftAlignment
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

# End of PropMgrGroupBox ############################

class PropMgrMessageGroupBox(PropMgrGroupBox):
    '''Message GroupBox class'''

    expanded = True # Set to False when groupbox is collapsed.
    widgets = [] # All widgets in the groupbox (except the title button).
    num_rows = 0 # Number of rows in the groupbox.
    num_grouboxes = 0 # Number of groupboxes in this msg groupbox.

    def __init__(self, parent, title):
        """Constructor for PropMgr group box.
        <parent> is the PropMgr dialog (of type PropMgrBaseClass)
        <title> is the label used on the the title button
        """
        PropMgrGroupBox.__init__(self, parent, title, titleButton=True)

        parent.num_groupboxes += 1
        num_groupboxes = 0

        self.setObjectName(parent.objectName() +
                           "/pmMessageGroupBox" +
                           str(parent.num_groupboxes))

        self.widgets = [] # All widgets in the groupbox (except the title button).

        self.VBoxLayout.setMargin(pmMsgGrpBoxMargin)
        self.VBoxLayout.setSpacing(pmMsgGrpBoxSpacing)

        self.GridLayout.setMargin(0)
        self.GridLayout.setSpacing(0)

        self.MessageTextEdit = PropMgrTextEdit(self, label='', spanWidth=True)

        # wrapWrapMode seems to be set to QTextOption.WrapAnywhere on MacOS,
        # so let's force it here. Mark 2007-05-22.
        self.MessageTextEdit.setWordWrapMode(QTextOption.WordWrap)

        parent.MessageTextEdit = self.MessageTextEdit

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

        # Hide until insertHtmlMessage() loads a message.
        self.hide()

    def insertHtmlMessage(self, text, setAsDefault=False,
                          minLines=4, maxLines=10,
                          replace=True):
        """Insert <text> (HTML) into the Prop Mgr's message groupbox.
        <minLines> - The minimum number of lines (of text) to display in the TextEdit.
        if <minLines>=0 the TextEdit will fit its own height to fit <text>. The
        default height is 4 (lines of text).
        <maxLines> - The maximum number of lines to display in the TextEdit widget.
        <replace> should be set to False if you do not wish
        to replace the current text. It will append <text> instead.

        Shows the message groupbox if it is hidden.
        """
        self.MessageTextEdit.insertHtml(text, setAsDefault,
                                        minLines=minLines, maxLines=maxLines,
                                        replace=True)
        self.show()

# End of PropMgrMessageGroupBox ############################

class PropMgrTextEdit(QTextEdit, PropMgrWidgetMixin, PropertyManager_common):
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
        self.setObjectName(parent.objectName() +
                           "/pmTextEdit" +
                           str(parent.num_rows))

        self._setHeight() # Default height is 4 lines high.

        # Needed for Intel MacOS. Otherwise, the horizontal scrollbar
        # is displayed in the MessageGroupBox. Mark 2007-05-24.
        # Shouldn't be needed with _setHeight().
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        if isinstance(parent, PropMgrMessageGroupBox):
            # Add to parent's VBoxLayout if <parent> is a MessageGroupBox.
            parent.VBoxLayout.addWidget(self)
            # We should be calling the propmgr's getMessageTextEditPalette() method,
            # but that will take some extra work which I will do soon. Mark 2007-06-21
            self.setPalette(self.getMessageTextEditPalette())
            self.setReadOnly(True)
            self.setObjectName("MessageTextEdit")
            self.labelWidget = None # Never has one. Mark 2007-05-31
            parent.widgets.append(self)
            parent.num_rows += 1
        else:
            self.addWidgetAndLabelToParent(parent, label, spanWidth)

    def insertHtml(self, text, setAsDefault=False,
                   minLines=4, maxLines=6,
                   replace=True):
        """Insert <text> (HTML) into the Prop Mgr's message groupbox.
        <minLines> is the minimum number of lines to
        display, even if the text takes up fewer lines. The default
        number of lines is 4.
        <maxLines> is the maximum number of lines to
        diplay before adding a vertical scrollbar.
        <replace> should be set to False if you do not wish
        to replace the current text. It will append <text> instead.
        """
        if setAsDefault:
            self.defaultText = text
            self.setAsDefault = True

        if replace:
            # Replace the text by selecting effectively all text and
            # insert the new text 'over' it (overwrite). :jbirac: 20070629
            cursor  =  self.textCursor()
            cursor.setPosition( 0,
                                QTextCursor.MoveAnchor )
            cursor.setPosition( len(self.toPlainText()),
                                QTextCursor.KeepAnchor )
            self.setTextCursor( cursor )

        QTextEdit.insertHtml(self, text)

        if replace:
            # Restore the previous cursor position/selection and mode.
            cursor.setPosition( len(self.toPlainText()),
                                QTextCursor.MoveAnchor )
            self.setTextCursor( cursor )

        self._setHeight(minLines, maxLines)


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
        current_width = self.sizeHint().width()

        # Probably including Html tags.
        text = self.toPlainText()
        text_width = self.fontMetrics().width(text)

        num_lines = text_width/current_width + 1
            # + 1 may create an extra (empty) line on rare occasions.

        if fitToHeight:
            num_lines = min(num_lines, maxLines)

        else:
            num_lines = max(num_lines, minLines)

        #margin = self.fontMetrics().leading() * 2 # leading() returned 0. Mark 2007-05-28
        margin = 10 # Based on trial and error. Maybe it is pm?Spacing=5 (*2)? Mark 2007-05-28
        new_height = num_lines * self.fontMetrics().lineSpacing() + margin

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
        self.setMinimumSize(QSize(pmMinWidth * 0.5, new_height))
        self.setMaximumHeight(new_height)

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

        self.setObjectName(parent.objectName() +
                           "/pmDoubleSpinBox" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Set QDoubleSpinBox min, max, singleStep, decimals, then val
        self.setRange(min, max)
        self.setSingleStep(singleStep)
        self.setDecimals(decimals)

        self.setValue(val) # This must come after setDecimals().

        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

    def setValue(self, val, setAsDefault=True):
        """Set value of widget to <val>. If <setAsDefault> is True,
        <val> becomes the default value for this widget so that
        "Restore Defaults" will reset this widget to <val>.
        """
        if setAsDefault:
            self.setAsDefault=True
            self.defaultValue=val
        QDoubleSpinBox.setValue(self, val)

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

        self.setObjectName(parent.objectName() +
                           "/pmSpinBox" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Set QSpinBox min, max and initial value
        self.setRange(min, max)
        self.setValue(val)

        # Set default value
        self.defaultValue=val
        self.setAsDefault = setAsDefault

        # Add suffix if supplied.
        if suffix:
            self.setSuffix(suffix)

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

    def setValue(self, val, setAsDefault=True):
        """Set value of widget to <val>. If <setAsDefault> is True,
        <val> becomes the default value for this widget so that
        "Restore Defaults" will reset this widget to <val>.
        """
        if setAsDefault:
            self.setAsDefault=True
            self.defaultValue=val
        QSpinBox.setValue(self, val)

# End of PropMgrSpinBox ############################

class PropMgrComboBox(QComboBox, PropMgrWidgetMixin):
    """PropMgr ComboBox class.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's choice index to idx.
    setAsDefault = True
    # <defaultIdx> - default index when "Restore Defaults" is clicked
    defaultIdx = 0
    # <defaultChoices> - default choices when "Restore Defaults" is clicked.
    defaultChoices = []

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

        self.setObjectName(parent.objectName() +
                           "/pmComboBox" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Load QComboBox widget choices and set initial choice (index).
        for choice in choices:
            self.addItem(choice)
        self.setCurrentIndex(idx)

        # Set default index
        self.defaultIdx=idx
        self.defaultChoices=choices
        self.setAsDefault = setAsDefault

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

# End of PropMgrComboBox ############################

class PropMgrPushButton(QPushButton, PropMgrWidgetMixin):
    """PropMgr PushButton class.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's text.
    setAsDefault = True
    # <defaultText> - default text when "Restore Default" is clicked
    defaultText = ""

    def __init__(self, parent, label='',
                 text='', setAsDefault=True,
                 spanWidth=False):
        """
        Appends a QPushButton widget to <parent>, a property manager groupbox.

        Arguments:

        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left of (or above) the PushButton.
        <text> - text displayed on the PushButton.
        <setAsDefault> - if True, will restore <text> as the PushButton's text
                         when the "Restore Defaults" button is clicked.
        <spanWidth> - if True, the PushButton and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the ComboBox (unless the label is empty) left justified.
        """

        if 0: # Debugging code
            print "PropMgrPushButton.__init__():"
            print "  label=",label
            print "  text =", text
            print "  setAsDefault =", setAsDefault
            print "  spanWidth =", spanWidth

        if not parent:
            return

        QPushButton.__init__(self)

        self.setObjectName(parent.objectName() +
                           "/pmPushButton" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Set text
        self.setText(text)

        # Set default text
        self.defaultText=text
        self.setAsDefault = setAsDefault

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

# End of PropMgrPushButton ############################

class PropMgrLineEdit(QLineEdit, PropMgrWidgetMixin):
    """PropMgr LineEdit class, for groupboxes (PropMgrGroupBox) only.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's value to val.
    setAsDefault = True
    defaultText = "" # Default value of lineedit

    def __init__(self, parent, label='',
                 text='', setAsDefault=True,
                 spanWidth=False):
        """
        Appends a QLineEdit widget to <parent>, a property manager groupbox.

        Arguments:

        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left of (or above) the widget.
        <text> - initial value of LineEdit widget.
        <setAsDefault> - if True, will restore <val>
                         when the "Restore Defaults" button is clicked.
        <spanWidth> - if True, the widget and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the SpinBox (unless the label is empty) left justified.
        """

        if 0: # Debugging code
            print "PropMgrLineEdit.__init__():"
            print "  label=", label
            print "  text =", text
            print "  setAsDefault =", setAsDefaultfix
            print "  spanWidth =", spanWidth

        if not parent:
            return

        QLineEdit.__init__(self)

        self.setObjectName(parent.objectName() +
                           "/pmLineEdit" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Set QLineEdit text
        self.setText(text)

        # Set default value
        self.defaultText=text
        self.setAsDefault = setAsDefault

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

# End of PropMgrLineEdit ############################

class PropMgrCheckBox(QCheckBox, PropMgrWidgetMixin):
    """PropMgr CheckBox class, for groupboxes (PropMgrGroupBox) only.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's value to val.
    setAsDefault = True
    defaultState = QtCore.Qt.Unchecked  # Default state of CheckBox. Qt.Checked is checked.

    def __init__(self, parent, label='',
                 isChecked=False, setAsDefault=True,
                 spanWidth=False, checkBoxText =''):
        """
        Appends a QCheckBox widget to <parent>, a property manager groupbox.

        Arguments:

        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left of (or above) the widget.
        <isChecked> - can be True, False, or one of the Qt ToggleStates
                      True = checked
                      False = unchecked
        <setAsDefault> - if True, will restore <val>
                         when the "Restore Defaults" button is clicked.
        <spanWidth> - if True, the widget and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the widget (unless the label is empty) left justified.
        <checkBoxText> - Text for the checkbox itself. It always appears on the
                         right hand side of the checkbox
        """

        if 0: # Debugging code
            print "PropMgrCheckBox.__init__():"
            print "  label=", label
            print "  state =", state
            print "  setAsDefault =", setAsDefaultfix
            print "  spanWidth =", spanWidth

        if not parent:
            return

        QCheckBox.__init__(self)

        self.setObjectName(parent.objectName() +
                           "/pmCheckBox" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        self.setCheckState(isChecked, setAsDefault)
        self.setText(checkBoxText)
        self.addWidgetAndLabelToParent(parent, label, spanWidth)

    def setCheckState(self, state, setAsDefault=True):
        """Set state of widget to <state>. If <setAsDefault> is True,
        <state> becomes the default state for this widget so that
        "Restore Defaults" will reset this widget to <state>.
        <state> can be True, False, or one of the Qt ToggleStates
        True = checked
        False = unchecked
        """

        # Set <state> to the appropriate Qt.ToggleState if True or False.
        if state is True:  state = Qt.Checked
        if state is False: state = Qt.Unchecked

        if setAsDefault:
            self.setAsDefault=setAsDefault
            self.defaultState=state

        QCheckBox.setCheckState(self, state)

# End of PropMgrCheckBox ############################

class PropMgrListWidget(QListWidget, PropMgrWidgetMixin):
    """PropMgr ListWidget class, for groupboxes (PropMgrGroupBox) only.
    """
        # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's choice index to idx.
    setAsDefault = True
    # <defaultRow> - default row when "Restore Defaults" is clicked
    defaultRow = 0
    # <defaultItems> - list of items when "Restore Defaults" is clicked.
    defaultItems = []

    def __init__(self, parent, label='',
                 items=[], row=0, setAsDefault=True,
                 numRows=6, spanWidth=False):
        """
        Appends a QListWidget widget to <parent>, a property manager groupbox.

        Arguments:

        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears to the left of (or above) the ComboBox.
        <items> - list of items (strings) to be inserted in the widget.
        <row> - current row. (0=first item)
        <setAsDefault> - if True, will restore <idx> as the current index
                         when the "Restore Defaults" button is clicked.
        <numRows> - the number of rows to display. If <items> is
                 greater than <numRows>, a scrollbar will be displayed.
        <spanWidth> - if True, the widget and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the widget (unless the label is empty) left justified.
        """

        if 0: # Debugging code
            print "PropMgrListWidget.__init__():"
            print "  label=",label
            print "  items =", items
            print "  row =",row
            print "  setAsDefault =", setAsDefault
            print "  numRows =",numRows
            print "  spanWidth =", spanWidth

        if not parent:
            return

        QListWidget.__init__(self)

        self.setObjectName(parent.objectName() +
                           "/pmListWidget" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Load QComboBox widget choices and set initial choice (index).
        #for choice in choices:
        #    self.addItem(choice)

        self.insertItems(0, items, setAsDefault)
        self.setCurrentRow(row, setAsDefault)

        # Need setChoices() method
        #self.defaultChoices=choices

        # Set height
        margin = self.fontMetrics().leading() * 2 # Mark 2007-05-28
        height = numRows * self.fontMetrics().lineSpacing() + margin
        self.setMaximumHeight(height)

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

    def insertItems(self, row, items, setAsDefault=True):
        """Insert items of widget starting at <row>.
        If <setAsDefault> is True, <items> become the default list of
        items for this widget. "Restore Defaults" will reset
        the list of items to <items>.

        Note: <items> will always replace the list of current items
        in the widget. <row> is ignored. This is considered a bug. Mark 2007-06-04
        """

        if row <> 0:
            msg = "PropMgrListWidget.insertItems(): <row> must be zero. See docstring for details:"
            print_compact_traceback(msg)
            return

        if setAsDefault:
            self.setAsDefault = setAsDefault
            self.defaultItems=items

        self.clear()
        QListWidget.insertItems(self, row, items)

    def setCurrentRow(self, row, setAsDefault=True):
        """Set current row of widget to <row>. If <setAsDefault> is True,
        <row> becomes the default row for this widget so that
        "Restore Defaults" will reset this widget to <row>.
        """
        if setAsDefault:
            self.setAsDefault = setAsDefault
            self.defaultRow=row
        QListWidget.setCurrentRow(self, row)

# End of PropMgrListWidget ############################

class PropMgrToolButton(QToolButton, PropMgrWidgetMixin):
    """PropMgr ToolButton class.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's text.
    setAsDefault = True
    # <defaultText> - default text when "Restore Default" is clicked
    defaultText = ""

    def __init__(self, parent, label='',
                 labelPlacement = 'left',
                 icon = None,
                 toolButtonStyle= 'iconOnly',
                 text='',
                 setAsDefault=True,
                 spanWidth=False):
        """
        Appends a QToolButton widget to <parent>, a property manager groupbox.

        Arguments:

        <parent> - a property manager groupbox (PropMgrGroupBox).
        <label> - label that appears at a position specified by <labelPlacement>
        relative to the Toolbutton
        <labelPlacement> - Placement of the <label> relative to ToolButton.
        (left, right, top, bottom) --- NOT IMPLEMENTED YET
        <icon> icon for the toolbutton
        <toolButtonStyle> NOT IMPLEMENTED YET
        <text> - text displayed on the ToolButton.
        <setAsDefault> - if True, will restore <text> as the ToolButton's text
                         when the "Restore Defaults" button is clicked.
        <spanWidth> - if True, the ToolButton and its label will span the width
                      of its groupbox. Its label will appear directly above
                      the ComboBox (unless the label is empty) left justified.
        """

        if not parent:
            return

        QToolButton.__init__(self)

        self.setObjectName(parent.objectName() +
                           "/pmToolButton" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        # Set text
        self.setText(text)

        # Set default text
        self.defaultText=text
        self.setAsDefault = setAsDefault

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

# End of PropMgrToolButton ############################

class PropMgrRadioButton(QRadioButton, PropMgrWidgetMixin):
    """PropMgr RadioButton class.
    """
    # Set to True to always hide this widget, even when groupbox is expanded.
    hidden = False
    # Set setAsDefault to False if "Restore Defaults" should not
    # reset this widget's text.
    setAsDefault = True
    # <defaultText> - default text when "Restore Default" is clicked
    defaultText = ""

    def __init__(self, parent,
                 text='',
                 setAsDefault=True,
                 spanWidth=True):
        """
        Appends a QRadioButton widget to <parent>, a property manager groupbox.

        Arguments:

        <parent> - a property manager groupbox (PropMgrGroupBox).
        <text> - text displayed on the RadioButton.
        <setAsDefault> - if True, will restore <text> as the RadioButton's text
                         when the "Restore Defaults" button is clicked.
        <spanWidth> - if True, the RadioButton will span the width
                      of its groupbox.
        """

        if not parent:
            return

        QRadioButton.__init__(self)

        label = ''
        self.setObjectName(parent.objectName()+
                           "/pmRadioButton" +
                           str(parent.num_groupboxes) +
                           "/'" + label + "'")

        self.setText(text)
        # Set default text
        self.defaultText=text
        self.setAsDefault = setAsDefault

        self.setCheckable(True)

        self.addWidgetAndLabelToParent(parent, label, spanWidth)

# End of PropMgrRadioButton ############################
