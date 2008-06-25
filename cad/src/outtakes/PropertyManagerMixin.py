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

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import QPalette
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QGroupBox
from PyQt4.Qt import QFrame
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QLabel
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QSpacerItem
from PyQt4.Qt import QToolButton
from PyQt4.Qt import QSize
from PyQt4.Qt import QWhatsThis
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QPushButton
from PyQt4.Qt import QTextEdit

from utilities import debug_flags

from utilities.icon_utilities import geticon, getpixmap
from sponsors.Sponsors import SponsorableMixin
from utilities.qt4transition import lineage
from utilities.debug import print_compact_traceback
from PropMgrBaseClass import PropertyManager_common, getPalette
from PM.PropMgr_Constants import pmColor
from PM.PropMgr_Constants import pmAllButtons
from PM.PropMgr_Constants import pmTitleFrameColor
from PM.PropMgr_Constants import pmTitleLabelColor
from PM.PropMgr_Constants import pmMessageTextEditColor
from PM.PropMgr_Constants import pmGrpBoxColor
from PM.PropMgr_Constants import pmGrpBoxButtonColor
from PM.PropMgr_Constants import pmCheckBoxTextColor
from PM.PropMgr_Constants import pmCheckBoxButtonColor
from PM.PropMgr_Constants import pmGrpBoxBorderColor
from PM.PropMgr_Constants import pmGrpBoxButtonBorderColor
from PM.PropMgr_Constants import pmGrpBoxButtonTextColor
from PM.PropMgr_Constants import pmGrpBoxExpandedImage
from PM.PropMgr_Constants import pmGrpBoxCollapsedImage
from PM.PropMgr_Constants import pmGrpBoxVboxLayoutMargin
from PM.PropMgr_Constants import pmGrpBoxVboxLayoutSpacing
from PM.PropMgr_Constants import pmMainVboxLayoutMargin
from PM.PropMgr_Constants import pmMainVboxLayoutSpacing
from PM.PropMgr_Constants import pmHeaderFrameMargin
from PM.PropMgr_Constants import pmHeaderFrameSpacing
from PM.PropMgr_Constants import pmLabelLeftAlignment
from PM.PropMgr_Constants import getHeaderFont
from PM.PropMgr_Constants import pmSponsorFrameMargin
from PM.PropMgr_Constants import pmSponsorFrameSpacing
from PM.PropMgr_Constants import pmTopRowBtnsMargin
from PM.PropMgr_Constants import pmTopRowBtnsSpacing
from PM.PropMgr_Constants import pmDoneButton
from PM.PropMgr_Constants import pmCancelButton
from PM.PropMgr_Constants import pmRestoreDefaultsButton
from PM.PropMgr_Constants import pmPreviewButton
from PM.PropMgr_Constants import pmWhatsThisButton
from PM.PropMgr_Constants import pmMsgGrpBoxMargin
from PM.PropMgr_Constants import pmMsgGrpBoxSpacing
from PM.PropMgr_Constants import pmMinWidth
from PM.PropMgr_Constants import pmGroupBoxSpacing

def pmVBoxLayout(propMgr):
    """Create the master vertical box layout for <propMgr>.
    """
    propMgr.pmVBoxLayout = QtGui.QVBoxLayout(propMgr)
    propMgr.pmVBoxLayout.setMargin(pmMainVboxLayoutMargin)
    propMgr.pmVBoxLayout.setSpacing(pmMainVboxLayoutSpacing)
    propMgr.pmVBoxLayout.setObjectName("pmVBoxLayout")

def pmSetPropMgrTitle(propMgr, title):
    """Set the Property Manager header title to string <title>.
    """
    propMgr.header_label.setText(title)

def pmSetPropMgrIcon(propMgr, png_path):
    """Set the Property Manager icon in the header.
    <png_path> is the relative path to the PNG file.
    """
    propMgr.header_pixmap.setPixmap(getpixmap(png_path))

    #@ self.heading_pixmap = QtGui.QLabel(self.heading_frame)
    #@ self.heading_pixmap.setPixmap(getpixmap('ui/actions/Tools/Build Structures/Atoms.png'))

def pmAddHeader(propMgr):
    """Creates the Property Manager header, which contains
    a pixmap and white text label.
    """

    # Heading frame (dark gray), which contains
    # a pixmap and (white) heading text.
    propMgr.header_frame = QFrame(propMgr)
    propMgr.header_frame.setFrameShape(QFrame.NoFrame)
    propMgr.header_frame.setFrameShadow(QFrame.Plain)

    header_frame_palette = propMgr.getPropMgrTitleFramePalette()
    propMgr.header_frame.setPalette(header_frame_palette)
    propMgr.header_frame.setAutoFillBackground(True)

    # HBox layout for heading frame, containing the pixmap
    # and label (title).
    HeaderFrameHLayout = QHBoxLayout(propMgr.header_frame)
    HeaderFrameHLayout.setMargin(pmHeaderFrameMargin) # 2 pixels around edges.
    HeaderFrameHLayout.setSpacing(pmHeaderFrameSpacing) # 5 pixel between pixmap and label.

    # PropMgr icon. Set image by calling setPropMgrIcon() at any time.
    propMgr.header_pixmap = QLabel(propMgr.header_frame)
    propMgr.header_pixmap.setSizePolicy(
        QSizePolicy(QSizePolicy.Policy(QSizePolicy.Fixed),
                          QSizePolicy.Policy(QSizePolicy.Fixed)))

    propMgr.header_pixmap.setScaledContents(True)

    HeaderFrameHLayout.addWidget(propMgr.header_pixmap)

    # PropMgr title label
    propMgr.header_label = QLabel(propMgr.header_frame)
    header_label_palette = propMgr.getPropMgrTitleLabelPalette()
    propMgr.header_label.setPalette(header_label_palette)
    propMgr.header_label.setAlignment(pmLabelLeftAlignment)

    # PropMgr heading font (for label).
    propMgr.header_label.setFont(getHeaderFont())
    HeaderFrameHLayout.addWidget(propMgr.header_label)

    propMgr.pmVBoxLayout.addWidget(propMgr.header_frame)

def pmAddSponsorButton(propMgr):
    """Creates the sponsor button for <propMgr>.
    """
    propMgr.sponsor_frame = QtGui.QFrame(propMgr)
    propMgr.sponsor_frame.setFrameShape(QtGui.QFrame.NoFrame)
    propMgr.sponsor_frame.setFrameShadow(QtGui.QFrame.Plain)
    propMgr.sponsor_frame.setObjectName("sponsor_frame")

    propMgr.gridlayout_sponsor = QtGui.QGridLayout(propMgr.sponsor_frame)
    propMgr.gridlayout_sponsor.setMargin(pmSponsorFrameMargin)
    propMgr.gridlayout_sponsor.setSpacing(pmSponsorFrameSpacing)

    propMgr.sponsor_btn = QtGui.QPushButton(propMgr.sponsor_frame)
    propMgr.sponsor_btn.setAutoDefault(False)
    propMgr.sponsor_btn.setFlat(True)
    propMgr.sponsor_btn.setObjectName("sponsor_btn")
    propMgr.gridlayout_sponsor.addWidget(propMgr.sponsor_btn,0,0,1,1)

    propMgr.connect(propMgr.sponsor_btn,
                    SIGNAL("clicked()"),
                    propMgr.sponsor_btn_clicked)

    propMgr.pmVBoxLayout.addWidget(propMgr.sponsor_frame)

def pmAddTopRowButtons(propMgr, showFlags=pmAllButtons):
    """Creates the OK, Cancel, Preview, and What's This
    buttons row at the top of the Property Manager <propMgr>.
    <showFlags> is an enum that can be used to show only certain
    Property Manager buttons, where:

    pmDoneButton = 1
    pmCancelButton = 2
    pmRestoreDefaultsButton = 4
    pmPreviewButton = 8
    pmWhatsThisButton = 16
    pmAllButtons = 31

    These flags are defined in PropMgr_Constants.py.

    This subroutine is used by the following Property Managers
    (which are still not using the PropMgrBaseClass):
    - Build Atoms
    - Build Crystal
    - Extrude
    - Move
    - Movie Player
    - Fuse Chunks

    Note: This subrouting is temporary. It will be removed after the
    PropMgrs in this list are converted to the PropMgrBaseClass.
    Mark 2007-06-24
    """
    # The Top Buttons Row includes the following widgets:
    #
    # - propMgr.pmTopRowBtns (Hbox Layout containing everything:)
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
    propMgr.pmTopRowBtns = QHBoxLayout()

    # Horizontal spacer
    HSpacer = QSpacerItem(1, 1,
                        QSizePolicy.Expanding,
                        QSizePolicy.Minimum)

    # Frame containing all the buttons.
    propMgr.TopRowBtnsFrame = QFrame()

    propMgr.TopRowBtnsFrame.setFrameShape(QFrame.NoFrame)
    propMgr.TopRowBtnsFrame.setFrameShadow(QFrame.Plain)

    # Create Hbox layout for main frame.
    TopRowBtnsHLayout = QHBoxLayout(propMgr.TopRowBtnsFrame)
    TopRowBtnsHLayout.setMargin(pmTopRowBtnsMargin)
    TopRowBtnsHLayout.setSpacing(pmTopRowBtnsSpacing)

    TopRowBtnsHLayout.addItem(HSpacer)

    # Set button type.
    buttonType = QToolButton
    # May want to use QToolButton.setAutoRaise(1) below. Mark 2007-05-29

    # OK (Done) button.
    propMgr.done_btn = buttonType(propMgr.TopRowBtnsFrame)
    propMgr.done_btn.setIcon(
        geticon("ui/actions/Properties Manager/Done.png"))
    propMgr.done_btn.setIconSize(QSize(22,22))
    propMgr.connect(propMgr.done_btn,
                   SIGNAL("clicked()"),
                   propMgr.ok_btn_clicked)
    propMgr.done_btn.setToolTip("Done")

    TopRowBtnsHLayout.addWidget(propMgr.done_btn)

    # Cancel (Abort) button.
    propMgr.abort_btn = buttonType(propMgr.TopRowBtnsFrame)
    propMgr.abort_btn.setIcon(
        geticon("ui/actions/Properties Manager/Abort.png"))
    propMgr.abort_btn.setIconSize(QSize(22,22))
    propMgr.connect(propMgr.abort_btn,
                   SIGNAL("clicked()"),
                   propMgr.abort_btn_clicked)
    propMgr.abort_btn.setToolTip("Cancel")

    TopRowBtnsHLayout.addWidget(propMgr.abort_btn)

    # Restore Defaults button.
    propMgr.restore_defaults_btn = buttonType(propMgr.TopRowBtnsFrame)
    propMgr.restore_defaults_btn.setIcon(
        geticon("ui/actions/Properties Manager/Restore.png"))
    propMgr.restore_defaults_btn.setIconSize(QSize(22,22))
    propMgr.connect(propMgr.restore_defaults_btn,
                   SIGNAL("clicked()"),
                   propMgr.restore_defaults_btn_clicked)
    propMgr.restore_defaults_btn.setToolTip("Restore Defaults")
    TopRowBtnsHLayout.addWidget(propMgr.restore_defaults_btn)

    # Preview (glasses) button.
    propMgr.preview_btn = buttonType(propMgr.TopRowBtnsFrame)
    propMgr.preview_btn.setIcon(
        geticon("ui/actions/Properties Manager/Preview.png"))
    propMgr.preview_btn.setIconSize(QSize(22,22))
    propMgr.connect(propMgr.preview_btn,
                   SIGNAL("clicked()"),
                   propMgr.preview_btn_clicked)
    propMgr.preview_btn.setToolTip("Preview")

    TopRowBtnsHLayout.addWidget(propMgr.preview_btn)

    # What's This (?) button.
    propMgr.whatsthis_btn = buttonType(propMgr.TopRowBtnsFrame)
    propMgr.whatsthis_btn.setIcon(
        geticon("ui/actions/Properties Manager/WhatsThis.png"))
    propMgr.whatsthis_btn.setIconSize(QSize(22,22))
    propMgr.connect(propMgr.whatsthis_btn,
                   SIGNAL("clicked()"),
                   QWhatsThis.enterWhatsThisMode)
    propMgr.whatsthis_btn.setToolTip("What\'s This Help")

    TopRowBtnsHLayout.addWidget(propMgr.whatsthis_btn)

    TopRowBtnsHLayout.addItem(HSpacer)

    # Create Button Row
    propMgr.pmTopRowBtns.addWidget(propMgr.TopRowBtnsFrame)

    propMgr.pmVBoxLayout.addLayout(propMgr.pmTopRowBtns)

    # Add What's This for buttons.

    propMgr.done_btn.setWhatsThis("""<b>Done</b>
        <p><img source=\"ui/actions/Properties Manager/Done.png\"><br>
        Completes and/or exits the current command.</p>""")

    propMgr.abort_btn.setWhatsThis("""<b>Cancel</b>
        <p><img source=\"ui/actions/Properties Manager/Abort.png\"><br>
        Cancels the current command.</p>""")

    propMgr.restore_defaults_btn.setWhatsThis("""<b>Restore Defaults</b>
        <p><img source=\"ui/actions/Properties Manager/Restore.png\"><br>
        Restores the defaut values of the Property Manager.</p>""")

    propMgr.preview_btn.setWhatsThis("""<b>Preview</b>
        <p><img source=\"ui/actions/Properties Manager/Preview.png\"><br>
        Preview the structure based on current Property Manager settings.</p>""")

    propMgr.whatsthis_btn.setWhatsThis("""<b>What's This</b>
        <p><img source=\"ui/actions/Properties Manager/WhatsThis.png\"><br>
        Click this option to invoke a small question mark that is attached to the mouse pointer,
        then click on an object which you would like more information about.
        A pop-up box appears with information about the object you selected.</p>""")

    # Hide the buttons that shouldn't be displayed base on <showFlags>.

    if not showFlags & pmDoneButton:
        propMgr.done_btn.hide()
    if not showFlags & pmCancelButton:
        propMgr.abort_btn.hide()
    if not showFlags & pmRestoreDefaultsButton:
        propMgr.restore_defaults_btn.hide()
    if not showFlags & pmPreviewButton:
        propMgr.preview_btn.hide()
    if not showFlags & pmWhatsThisButton:
        propMgr.whatsthis_btn.hide()

    return

class pmMessageGroupBox(QGroupBox, PropertyManager_common):
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
    defaultText = ""
    # The default text that is displayed whenever the Property Manager is displayed.
    setAsDefault = True
    # Checked to determine if <defaultText> should be restored whenever the
    # Property Manager is displayed.

    def __init__(self,
                 parent,
                 title = ''):

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

    def insertHtmlMessage(self, text, setAsDefault=True,
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
        if setAsDefault:
            self.defaultText = text
            self.setAsDefault = True

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

def pmAddBottomSpacer(parent, vlayout, last=False):
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
#
# - Build > Atoms (depositMode/MMKit)
# - Build > Crystal (cookieCutter)
# - Tools > Extrude (extrudeMode)
# - Tools > Fuse (fuseMode)
# - Tools > Move (modifyMode)
# - Simulator > Play Movie (movieMode)
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
            if debug_flags.atom_debug:
                msg1 = "Last PropMgr doesn't have method updatePropsBeforeClosing."
                msg2 =  " That is OK (for now, only implemented in GeometryGenerators)"
                msg3 = "Ignoring Exception: "
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

    def getGroupBoxTitleCheckBox(self, name, parent = None, bool_expand = True):#Ninad 070207
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

    def getGroupBoxCheckBoxStyleSheet(self, bool_expand = True):
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

    def ok_btn_clicked(self):
        self.w.toolsDone()
        pass

    def abort_btn_clicked(self):
        self.w.toolsCancel()
        pass

    def restore_defaults_btn_clicked(self):
        pass

    def preview_btn_clicked(self):
        pass

    pass # end of class PropertyManagerMixin

# end
