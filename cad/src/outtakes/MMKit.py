# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
MMKit.py

THIS FILE HAS BEEN DEPRECATED.

SEE NEW IMPLEMETATION IN --
Ui_BuildAtomsPropertyManager.py,
BuildAtomsPropertyManager.py,
Ui_PartLibPropertyManager.py,
PartLibPropertyManager.py,
Ui_PastePropertyManager.py
PastePropertyManager.py


$Id$

History:

Created by Huaicai.

Modified by several developers since then.

ninad 20070716: Code cleanup to make mmkit a propMgr object in deposit mode
instead of being inherited by that mode.


"""

import os, sys

from PyQt4 import QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import QDialog, SIGNAL, QIcon, QVBoxLayout, QStringList, QFileDialog
from PyQt4.Qt import QDir, QTreeView, QTreeWidgetItem, QAbstractItemDelegate, QWhatsThis

from MMKitDialog import Ui_MMKitDialog
from graphics.widgets.ThumbView import MMKitView, ChunkView
from model.elements import PeriodicTable
from utilities.constants import diTUBES
## from model.chem import Atom [not used i think - bruce 071113]
## from model.chunk import Chunk [not used i think - bruce 071113]
from foundation.Utility import imagename_to_icon, geticon
from model.assembly import Assembly
from files.mmp.files_mmp import readmmp
from model.part import Part
import foundation.env as env
from utilities import debug_flags
from utilities.debug import print_compact_traceback
from sponsors.Sponsors import SponsorableMixin
from PropertyManagerMixin import PropertyManagerMixin, pmSetPropMgrIcon, pmSetPropMgrTitle
from PM.PropMgr_Constants import pmMMKitPageMargin
from model.bond_constants import btype_from_v6

# PageId constants for mmkit_tab
AtomsPage = 0
ClipboardPage = 1
LibraryPage = 2

noblegases = ["He", "Ne", "Ar", "Kr"] # Mark 2007-05-31

# debugging flags -- do not commit with True
debug_mmkit_events = False

class MMKit(QDialog,
            Ui_MMKitDialog,
            PropertyManagerMixin,
            SponsorableMixin):
    """
    THIS CLASS HAS BEEN DEPRECATED.
    SEE NEW IMPLEMETATION IN--
    Ui_BuildAtomsPropertyManager.py,
    BuildAtomsPropertyManager.py,
    Ui_PartLibPropertyManager.py,
    PartLibPropertyManager.py,
    Ui_PastePropertyManager.py
    PastePropertyManager.py

    Provide the MMKit PM for Build Atoms mode.
    """
    # <title> - the title that appears in the property manager header.
    title = "Build Atoms"
    # <iconPath> - full path to PNG file that appears in the header.
    iconPath = "ui/actions/Tools/Build Structures/Build Atoms.png"

    bond_id2name =['sp3', 'sp2', 'sp', 'sp2(graphitic)']
    sponsor_keyword = 'Build'

    def __init__(self, parentMode, win):
        QDialog.__init__(self, win, Qt.Dialog)# Qt.WStyle_Customize | Qt.WStyle_Tool | Qt.WStyle_Title | Qt.WStyle_NoBorder)

        self.w = win
        self.o = self.w.glpane

        #@NOTE: As of 20070717, MMKit supports only depositMode as its parent
        #(and perhaps subclasses of depositMode ..but such a class that also
        #uses MMKit is NIY so it is unconfirmed)  -- ninad
        self.parentMode = parentMode

        self.setupUi(self)

        # setupUi() did not add the icon or title. We do that here.
        pmSetPropMgrIcon( self, self.iconPath )
        pmSetPropMgrTitle( self, self.title )

        #self.connect(self.hybrid_btngrp,SIGNAL("buttonClicked(int)"),self.set_hybrid_type)

        self.pw = None # pw = partwindow

        self.connect(self.mmkit_tab,
                     SIGNAL("currentChanged(int)"),
                     self.tabCurrentChanged)

        self.connect(self.chunkListBox,
                     SIGNAL("currentItemChanged(QListWidgetItem*,QListWidgetItem*)"),
                     self.chunkChanged)
        self.connect(self.browseButton,
                     SIGNAL("clicked(bool)"),
                     self.browseDirectories)
        self.connect(self.defaultPartLibButton,
                     SIGNAL("clicked(bool)"),
                     self.useDefaultPartLibDirectory)

        #self.connect(self.elementButtonGroup,SIGNAL("buttonClicked(int)"),self.setElementInfo)

        self.connect(self.thumbView_groupBoxButton, SIGNAL("clicked()"),
                     self.toggle_thumbView_groupBox)
        self.connect(self.bondTool_groupBoxButton , SIGNAL("clicked()"),
                     self.toggle_bondTool_groupBox)
        self.connect(self.MMKitGrpBox_TitleButton, SIGNAL("clicked()"),
                     self.toggle_MMKit_groupBox)
        self.connect(self.filterCB, SIGNAL("stateChanged(int)"),
                     self.toggle_selectionFilter_groupBox)
        self.connect(self.advancedOptions_groupBoxButton, SIGNAL("clicked()"),
                     self.toggle_advancedOptions_groupBox)

        # Make the elements act like a big exclusive radio button.
        self.theElements = QtGui.QButtonGroup()
        self.theElements.setExclusive(True)
        self.theElements.addButton(self.toolButton1, 1)
        self.theElements.addButton(self.toolButton2, 2)
        self.theElements.addButton(self.toolButton6, 6)
        self.theElements.addButton(self.toolButton7, 7)
        self.theElements.addButton(self.toolButton8, 8)
        self.theElements.addButton(self.toolButton10, 10)
        self.theElements.addButton(self.toolButton9, 9)
        self.theElements.addButton(self.toolButton13,13)
        self.theElements.addButton(self.toolButton17,17)
        self.theElements.addButton(self.toolButton5, 5)
        self.theElements.addButton(self.toolButton10_2, 18)
        self.theElements.addButton(self.toolButton15, 15)
        self.theElements.addButton(self.toolButton16, 16)
        self.theElements.addButton(self.toolButton14, 14)
        self.theElements.addButton(self.toolButton33, 33)
        self.theElements.addButton(self.toolButton34, 34)
        self.theElements.addButton(self.toolButton35, 35)
        self.theElements.addButton(self.toolButton32, 32)
        self.theElements.addButton(self.toolButton36, 36)
        self.connect(self.theElements, SIGNAL("buttonPressed(int)"), self.update_dialog)

        self.theHybridizations = QtGui.QButtonGroup()
        self.theHybridizations.setExclusive(True)
        self.theHybridizations.addButton(self.sp3_btn, 0)
        self.theHybridizations.addButton(self.sp2_btn, 1)
        self.theHybridizations.addButton(self.sp_btn, 2)
        self.theHybridizations.addButton(self.graphitic_btn, 3)
        self.connect(self.theHybridizations, SIGNAL("buttonClicked(int)"), self.update_hybrid_btngrp)

        self.connect(self.filterCB,
                        SIGNAL("toggled(bool)"),self.set_selection_filter)


        self.elemTable = PeriodicTable
        self.displayMode = diTUBES
        self.elm = None

        self.newModel = None  ## used to save the selected lib part

        self.flayout = None

        # It looks like we now have correct fixes for bugs 1659 and bug 1824. If so, it would be safe to simply
        # hardware self.icon_tabs to True and simplify code accordingly. But we're not 100% certain, so by leaving
        # it as a debug pref, we can help any users who see those bugs come up again.
        # wware 060420
        #
        # Update, bruce 070328: the False value of this debug_pref is known to fail in the Qt4 version (on Mac anyway),
        # due to AttributeError exceptions for setMargin and setTabLabel,
        # so I'm changing the prefs key for it in order to let Qt3 and Qt4 have independent debug_pref settings,
        # adding a warning in the menu text, and adding a try/except to help in debugging this if anyone ever wants to.
        # (If the bugs Will mentioned go away entirely, we can abandon support for the False value instead of fixing it,
        #  as Will suggested.)
        from utilities.debug_prefs import debug_pref, Choice_boolean_True
        self.icon_tabs = debug_pref("use icons in MMKit tabs? (only True works in Qt4)", Choice_boolean_True,
                                    prefs_key = "A7/mmkit tab icons/Qt4")
            #e Changes to this only take effect in the next session.
            # Ideally we'd add a history message about that, when this is changed.
            # (It's not yet easy to do that in a supported way in debug_pref.) [bruce 060313]

        if not self.icon_tabs:
            # This code is known to fail in Qt4 Mac version, as explained above. [bruce 061222 and 070328]
            try:
                self.mmkit_tab.setMargin ( 0 )
            except:
                print_compact_traceback("ignoring this Qt4-specific exception: ") #bruce 061222
                pass
            self.mmkit_tab.setTabLabel (self.atomsPage, 'Atoms')
            self.mmkit_tab.setTabLabel (self.clipboardPage, 'Clipbd')
            self.mmkit_tab.setTabLabel (self.libraryPage, 'Lib')
        else:
            # Add icons to MMKit's tabs. mark 060223.
            atoms_ic = imagename_to_icon("actions/Properties Manager/MMKit.png")
            self.mmkit_tab.setTabIcon(self.mmkit_tab.indexOf(self.atomsPage), QIcon(atoms_ic))

            self.update_clipboard_page_icon() # Loads proper icon for clibpoard tab. Mark 2007-06-01

            library_ic = imagename_to_icon("actions/Properties Manager/library.png")
            self.mmkit_tab.setTabIcon(self.mmkit_tab.indexOf(self.libraryPage), QIcon(library_ic))

        # Tab tooltips. mark 060326
        self.mmkit_tab.setTabToolTip(self.mmkit_tab.indexOf(self.atomsPage), 'Atoms')
        self.mmkit_tab.setTabToolTip(self.mmkit_tab.indexOf(self.clipboardPage), 'Clipboard')
        self.mmkit_tab.setTabToolTip(self.mmkit_tab.indexOf(self.libraryPage), 'Part Library')

        self._setNewView('MMKitView')

        # Set current element in element button group.


        self.theElements.button(self.w.Element).setChecked(True)

        #self.connect(self., SIGNAL("), )

        self.connect(self.w.hybridComboBox, SIGNAL("activated(int)"), self.hybridChangedOutside)

        self.connect(self.w.hybridComboBox, SIGNAL("activated(const QString&)"), self.change2AtomsPage)
        self.connect(self.w.elemChangeComboBox, SIGNAL("activated(const QString&)"), self.change2AtomsPage)
        self.connect(self.w.pasteComboBox, SIGNAL("activated(const QString&)"), self.change2ClipboardPage)

        #self.connect(self.w.depositAtomDashboard.pasteBtn, SIGNAL("pressed()"), self.change2ClipboardPage)
        self.connect(self.w.depositAtomDashboard.pasteBtn, SIGNAL("stateChanged(int)"), self.pasteBtnStateChanged)
        self.connect(self.w.depositAtomDashboard.depositBtn, SIGNAL("stateChanged(int)"), self.depositBtnStateChanged)

        self.connect(self.dirView, SIGNAL("selectionChanged(QItemSelection *, QItemSelection *)"), self.partChanged)

        self.add_whats_this_text()

        return # from __init__

    # ==

    #bruce 060412 added everything related to __needs_update_xxx, to fix bugs 1726, 1629 and mitigate bug 1677;
    # for more info see the comments where update_clipboard_items is called (in depositMode.py).

    __needs_update_clipboard_items = False
        # (there could be other flags like this for other kinds of updates we might need)


    def show_propMgr(self):
        """
        Show the Build Property Manager.
        """
        #@NOTE: The build property manager files are still refered as MMKit and
        #MMKitDialog. This will change in the near future. -- ninad 20070717

        self.update_dialog(self.parentMode.w.Element)
        self.parentMode.set_selection_filter(False) # disable selection filter
        self.openPropertyManager(self)

        #Following is an old comment, was originally in depositMode.init_gui:
        #Do these before connecting signals or we'll get history msgs.
        #Part of fix for bug 1620. mark 060322
        self.highlightingCB.setChecked(self.parentMode.hover_highlighting_enabled)
        self.waterCB.setChecked(self.parentMode.water_enabled)


    def update_dialog(self, elemNum):
        """Called when the current element has been changed.
           Update non user interactive controls display for current selected
           element: element label info and element graphics info """

        elm = self.elemTable.getElement(elemNum)

        currentIndex = self.mmkit_tab.currentIndex()
        atomPageIndex = self.mmkit_tab.indexOf(self.atomsPage)

        ##if elm == self.elm and self.currentPageOpen(AtomsPage): return
        if elm == self.elm and (currentIndex == atomPageIndex) : return

        ## The following statements are redundant in some situations.
        self.theElements.button(elemNum).setChecked(True)
        self.w.Element = elemNum

        self.color = self.elemTable.getElemColor(elemNum)
        self.elm = self.elemTable.getElement(elemNum)

        self.update_hybrid_btngrp()

        self.elemGLPane.resetView()
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)

        #update the selection filter
        self.update_selection_filter_list()

        # Fix for bug 353, to allow the dialog to be updated with the correct page.  For example,
        # when the user selects Paste from the Edit toolbar/menu, the MMKit should show
        # the Clipboard page and not the Atoms page. Mark 050808
        if self.w.depositState == 'Clipboard':
            self.change2ClipboardPage()
        else:
            self.change2AtomsPage()
        self.tabCurrentChanged()

        self.updateBuildAtomsMessage() # Mark 2007-06-01

    def updateBuildAtomsMessage(self):
        """Updates the message box with an informative message based on the current page
        and current selected atom type.
        """
        msg = ""

        if self.MMKit_groupBox.isVisible():
            pageIndex = self.mmkit_tab.currentIndex()
            page = None

            if pageIndex is 0: # atomsPage
                msg = "Double click in empty space to insert a single " + self.elm.name + " atom. "
                if not self.elm.symbol in noblegases:
                    msg += "Click on an atom's <i>red bondpoint</i> to attach a " + self.elm.name + " atom to it."

            elif pageIndex is 1: # clipboardPage
                pastableItems = self.w.assy.shelf.get_pastable_chunks()
                if pastableItems:
                    msg = "Double click in empty space to insert a copy of the selected clipboard item. \
                    Click on a <i>red bondpoint</i> to attach a copy of the selected clipboard item."
                else:
                    msg = "There are no items on the clipboard."

            elif pageIndex is 2: # libraryPage
                msg = "Double click in empty space to insert a copy of the selected part in the library."

        else: # Bonds Tool is selected (MMKit groupbox is hidden).
            if self.parentMode.cutBondsAction.isChecked():
                msg = "<b> Cut Bonds </b> tool is active. \
                Click on bonds in order to delete them."
                self.MessageGroupBox.insertHtmlMessage(msg)
                return

            if not hasattr(self, 'bondclick_v6'): # Mark 2007-06-01
                return
            if self.bondclick_v6:
                name = btype_from_v6(self.bondclick_v6)
                msg = "Click bonds or bondpoints to make them %s bonds." % name # name is 'single' etc

        # Post message.
        self.MessageGroupBox.insertHtmlMessage(msg)

    #== Atom Selection Filter helper methods

    def set_selection_filter(self, enabled):
        """Slot for Atom Selection Filter checkbox. Prints history message when selection filter is
        enabled/disabled and updates the cursor.
        """

        if enabled != self.w.selection_filter_enabled:
            if enabled:
                env.history.message("Atom Selection Filter enabled.")
            else:
                env.history.message("Atom Selection Filter disabled.")

        self.w.selection_filter_enabled = enabled

        #print "update_selection_filter_list(): self.w.filtered_elements=", self.w.filtered_elements

        ##self.update_selection_filter_list_widget()
        self.update_selection_filter_list()
        self.filterlistLE.setEnabled(enabled)
        self.filterCB.setChecked(enabled)
        self.o.graphicsMode.update_cursor()

    def update_selection_filter_list(self):
        """Adds/removes the element selected in the MMKit to/from Atom Selection Filter
        based on what modifier key is pressed (if any).
        """
        eltnum = self.w.Element

        if self.o.modkeys is None:
            self.w.filtered_elements = []
            self.w.filtered_elements.append(PeriodicTable.getElement(eltnum))
        if self.o.modkeys == 'Shift':
            if not PeriodicTable.getElement(eltnum) in self.w.filtered_elements[:]:
                self.w.filtered_elements.append(PeriodicTable.getElement(eltnum))
        elif self.o.modkeys == 'Control':
            if PeriodicTable.getElement(eltnum) in self.w.filtered_elements[:]:
                self.w.filtered_elements.remove(PeriodicTable.getElement(eltnum))

        self.update_selection_filter_list_widget()

    def update_selection_filter_list_widget(self):
        """Updates the list of elements displayed in the Atom Selection Filter List.
        """
        filtered_syms=''
        for e in self.w.filtered_elements[:]:
            if filtered_syms: filtered_syms += ", "
            filtered_syms += e.symbol
        #self.w.depositAtomDashboard.filterlistLE.setText(filtered_syms)
        self.filterlistLE.setText(filtered_syms)

    def toggle_bondTool_groupBox(self):
        self.toggle_groupbox(self.bondTool_groupBoxButton, self.bondToolWidget)

    def toggle_thumbView_groupBox(self):
        self.toggle_groupbox(self.thumbView_groupBoxButton, self.elementFrame)

    def toggle_MMKit_groupBox(self):
        self.toggle_groupbox(self.MMKitGrpBox_TitleButton, self.mmkit_tab, self.transmuteBtn, self.transmuteCB)

    def toggle_selectionFilter_groupBox(self, state):
        """ Toggles the groupbox item display depending on checked state of the selection filter checkbox """

        #Current state is 'off' or(Qt.Unchecked)

        if state is 0:
            styleSheet = self.getGroupBoxCheckBoxStyleSheet(bool_expand = False)
            self.filterCB.setStyleSheet(styleSheet)

            palette = self.getGroupBoxCheckBoxPalette()
            self.filterCB.setPalette(palette)

            #hide the following widgets when checkbox is unchecked --
            self.selectionFilter_label.hide()
            self.filterlistLE.hide()
        else:
            styleSheet = self.getGroupBoxCheckBoxStyleSheet(bool_expand = True)
            self.filterCB.setStyleSheet(styleSheet)

            palette = self.getGroupBoxCheckBoxPalette()
            self.filterCB.setPalette(palette)

            #hide the following widgets when checkbox is unchecked --
            self.selectionFilter_label.show()
            self.filterlistLE.show()


    def toggle_advancedOptions_groupBox(self):
        self.toggle_groupbox(self.advancedOptions_groupBoxButton, self.autobondCB, self.waterCB, self.highlightingCB)

    #bruce 070615 removed 'def toggle_groupbox', since our mixin superclass PropertyManagerMixin
    # provides an identical-enough version.

    def tabCurrentChanged(self):
        pageIndex = self.mmkit_tab.currentIndex()
        page = None
        if pageIndex is 0: page = self.atomsPage
        elif pageIndex is 1: page = self.clipboardPage
        elif pageIndex is 2: page = self.libraryPage
        self.setup_current_page(page)

    def update_clipboard_items(self):
        self.__needs_update_clipboard_items = True
        self.update() # this makes sure self.event will get called; it might be better to test the flag only in self.repaint, not sure
        return

    def event(self, event): #bruce 060412 debug code, but also checks all self.__needs_update_xxx flags (an essential bugfix)
        if debug_mmkit_events:
            print "debug: MMKit.event got %r, type %r" % (event, event.type())
                # Qt doc for QEvent lists 'enum type' codes; the subclass is also printed by %r

        if self.__needs_update_clipboard_items:
            self.__really_update_clipboard_items()
            self.__needs_update_clipboard_items = False

        res = QDialog.event(self, event)
        if debug_mmkit_events:
            if res is not None:
                print "debug: MMKit.event returns %r" % (res,) # usually True, sometimes False
        # if we return None we get TypeError: invalid result type from MMKit.event()
        return res

    # ==

    def pasteBtnStateChanged(self, state):
        """Slot method. Called when the state of the Paste button of deposit dashboard has been changed. """
        if state == QButton.On:
            self.change2ClipboardPage()


    def depositBtnStateChanged(self, state):
        """Slot method. Called when the state of the Deposit button of deposit dashboard has been changed. """
        if state == QButton.On:
           self.change2AtomsPage()


    def hybridChangedOutside(self, newId):
        """Slot method. Called when user changes element hybridization from the dashboard.
         This method achieves the same effect as user clicked one of the hybridization buttons."""
        self.theElements.button(newId).setChecked(True)
        self.set_hybrid_type(newId)
        self.w.Element = newId

        ## fix bug 868
        self.w.depositAtomDashboard.depositBtn.setChecked(True)


    def change2AtomsPage(self):
        """Slot method called when user changes element/hybrid combobox or
        presses Deposit button from Build mode dashboard.
        """
        if self.mmkit_tab.currentIndex() != AtomsPage:
            self.mmkit_tab.setCurrentIndex(AtomsPage) # Generates signal

    def change2ClipboardPage(self):
        """Slot method called when user changes pastable item combobox or
        presses the Paste button from the Build mode dashboard. """
        if self.mmkit_tab.currentIndex() != ClipboardPage:
            self.mmkit_tab.setCurrentIndex(ClipboardPage) # Generates signal??


    def setElementInfo(self,value):
        """Slot method called when an element button is pressed in the element ButtonGroup.
        """
        self.w.setElement(value)


    def update_hybrid_btngrp(self, buttonIndex = 0):
        """Update the buttons of the current element\'s hybridization types into hybrid_btngrp;
        select the specified one if provided"""
        elem = PeriodicTable.getElement(self.w.Element) # self.w.Element is atomic number

        atypes = elem.atomtypes

        if elem.name == 'Carbon':
            self.setup_C_hybrid_buttons()
        elif elem.name == 'Nitrogen':
            self.setup_N_hybrid_buttons()
        elif elem.name == 'Oxygen':
            self.setup_O_hybrid_buttons()
        elif elem.name == 'Sulfur':
            self.setup_S_hybrid_buttons()
        else:
            self.hide_hybrid_btngrp()
            self.elemGLPane.changeHybridType(None)
            return

        #if len(atypes) > 1:
        # Prequisite: w.hybridComboBox has been updated at this moment.
        b_name = self.bond_id2name[buttonIndex]
        self.elemGLPane.changeHybridType(b_name)
        self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
        self.theHybridizations.button(buttonIndex).setChecked(True)
        self.set_hybrid_type(buttonIndex)
        # Added Atomic Hybrids label. Mark 2007-05-30
        self.atomic_hybrids_label.setText("Atomic Hybrids for " + elem.name + " :")
        self.show_hybrid_btngrp()

    def show_hybrid_btngrp(self): # Mark 2007-06-20
        """Show the hybrid button group and label above it.
        This is a companion method to hide_hybrid_btngrp().
        It includes workarounds for Qt layout issues that crop up
        when hiding/showing the hybrid button groupbox using Qt's
        hide() and show() methods. See bug 2407 for more information.
        """
        if 1:
            self.hybrid_btngrp.show()
        else:
            self.hybrid_btngrp.show()
            self.atomic_hybrids_label.show()

    def hide_hybrid_btngrp(self): # Mark 2007-06-20
        """Hide the hybrid button group and label above it.
        This is a companion method to show_hybrid_btngrp().
        It includes workarounds for Qt layout issues that crop up
        when hiding/showing the hybrid button groupbox using Qt's
        hide() and show() methods. See bug 2407 for more information.
        """
        if 1:
            # This way of hiding confuses the layout manager, so I had
            # do create special spacers and set sizepolicies just to make
            # this work.
            self.hybrid_btngrp.hide()
            # I had to do this instead of use hide() since hide()
            # confuses the layout manager in special situations, like
            # that described in bug 2407. Mark 2007-06-20
            self.atomic_hybrids_label.setText(" ")
        else:
            # Alternate way of hiding. Hide all contents and the QButtonGroupbox
            # border, but there is no way to hide the border.
            self.sp3_btn.hide()
            self.sp2_btn.hide()
            self.sp_btn.hide()
            self.graphitic_btn.hide()
            self.atomic_hybrids_label.hide()

    def setup_C_hybrid_buttons(self):
        """Displays the Carbon hybrid buttons.
        """
        self.theElements.button(self.w.Element).setChecked(True)
        self.sp3_btn.setIcon(imagename_to_icon('modeltree/C_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setIcon(imagename_to_icon('modeltree/C_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.setIcon(imagename_to_icon('modeltree/C_sp.png'))
        self.sp_btn.show()
        self.graphitic_btn.hide()

    def setup_N_hybrid_buttons(self):
        """Displays the Nitrogen hybrid buttons.
        """
        self.sp3_btn.setIcon(imagename_to_icon('modeltree/N_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setIcon(imagename_to_icon('modeltree/N_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.setIcon(imagename_to_icon('modeltree/N_sp.png'))
        self.sp_btn.show()
        self.graphitic_btn.setIcon(imagename_to_icon('modeltree/N_graphitic.png'))
        self.graphitic_btn.show()


    def setup_O_hybrid_buttons(self):
        """Displays the Oxygen hybrid buttons.
        """
        self.sp3_btn.setIcon(imagename_to_icon('modeltree/O_sp3.png'))
        self.sp3_btn.show()
        self.sp2_btn.setIcon(imagename_to_icon('modeltree/O_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.graphitic_btn.hide()


    def setup_S_hybrid_buttons(self):
        """Displays the Sulfur hybrid buttons.
        """
        self.sp3_btn.setIcon(imagename_to_icon('modeltree/O_sp3.png')) # S and O are the same.
        self.sp3_btn.show()
        self.sp2_btn.setIcon(imagename_to_icon('modeltree/O_sp2.png'))
        self.sp2_btn.show()
        self.sp_btn.hide()
        self.graphitic_btn.hide()


    def set_hybrid_type(self, type_id):
        """Slot method. Called when any of the hybrid type buttons was clicked. """
        self.w.hybridComboBox.setCurrentIndex( type_id )

        b_name = self.bond_id2name[type_id]

        #This condition fixs bug 866, also saves time since no need to draw without MMKIt shown
        if self.isVisible():
            self.elemGLPane.changeHybridType(b_name)
            self.elemGLPane.refreshDisplay(self.elm, self.displayMode)


    def setup_current_page(self, page):
        """Slot method that is called whenever a user clicks on the
        'Atoms', 'Clipboard' or 'Library' tab to change to that page.
        """

        #print "setup_current_page: page=", page

        if page == self.atomsPage:  # Atoms page
            self.w.depositState = 'Atoms'
            self.w.update_depositState_buttons()
            self.elemGLPane.resetView()
            self.elemGLPane.refreshDisplay(self.elm, self.displayMode)
            self.browseButton.hide()
            self.defaultPartLibButton.hide()
            self.atomsPageSpacer.changeSize(0,5,
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Minimum)

        elif page == self.clipboardPage: # Clipboard page
            self.w.depositState = 'Clipboard'
            self.w.update_depositState_buttons()
            self.elemGLPane.setDisplay(self.displayMode)
            self._clipboardPageView()
            self.browseButton.hide()
            self.defaultPartLibButton.hide()
            self.atomsPageSpacer.changeSize(0,5,
                QtGui.QSizePolicy.Expanding,
                QtGui.QSizePolicy.Minimum)

        elif page == self.libraryPage: # Library page
            if self.rootDir:
                self.elemGLPane.setDisplay(self.displayMode)
                self._libPageView()
            self.browseButton.show()
            self.defaultPartLibButton.show()
            self.atomsPageSpacer.changeSize(0,5,
                QtGui.QSizePolicy.Minimum,
                QtGui.QSizePolicy.Minimum)

            #Turn off both paste and deposit buttons, so when in library page and user choose 'set hotspot and copy'
            #it will change to paste page, also, when no chunk selected, a history message shows instead of depositing an atom.
            self.w.depositState = 'Library'
            self.w.update_depositState_buttons()
        else:
            print 'Error: MMKit page unknown: ', page

        self.elemGLPane.setFocus()
        self.updateBuildAtomsMessage()

    def chunkChanged(self, item, previous):
        """Slot method. Called when user changed the selected chunk. """

        itemId = self.chunkListBox.row(item)

        if itemId != -1:

            newChunk = self.pastableItems[itemId]

            #self.w.pasteComboBox.setCurrentIndex(itemId)
            #buildModeObj = self.w.commandSequencer._commandTable['DEPOSIT']
            #assert buildModeObj
            #buildModeObj.setPaste()

            ##Compared to the above way, I think this way is better. Modules are more uncoupled.
            self.w.pasteComboBox.setCurrentIndex(itemId) # Fixes bug 1754. mark 060325

            self.elemGLPane.updateModel(newChunk)


    def __really_update_clipboard_items(self): #bruce 060412 renamed this from update_clipboard_items to __really_update_clipboard_items
        """Updates the items in the clipboard\'s listview, if the clipboard is currently shown. """
        if self.currentPageOpen(ClipboardPage): #bruce 060313 added this condition to fix bugs 1631, 1669, and MMKit part of 1627
            self._clipboardPageView() # includes self.update_clipboard_page_icon()
        else:
            self.update_clipboard_page_icon() # do this part of it, even if page not shown
        return

    def partChanged(self, item):
        """Slot method, called when user changed the partlib brower tree"""
        if isinstance(item, self.FileItem):
           self._libPageView(True)
        else:
           self.newModel = None
           self.elemGLPane.updateModel(self.newModel)


    def getPastablePart(self):
        """Public method. Retrieve pastable part and hotspot if current tab page is in libary, otherwise, return None. """
        if self.currentPageOpen(LibraryPage):
            return self.newModel, self.elemGLPane.hotspotAtom
        return None, None

    def currentPageOpen(self, page_id):
        """Returns True if <page_id> is the current page open in the tab widget, where:
            0 = Atoms page
            1 = Clipboard page
            2 = Library page
        """
        pageIndex = self.mmkit_tab.currentIndex()

        if page_id == pageIndex:
            return True
        else:
            return False

    def _libPageView(self, isFile = False):
        item = self.dirView.selectedItem()
        if not isFile and not isinstance(item, self.FileItem):
            self.newModel = None
            self.elemGLPane.updateModel(self.newModel)
            return

        mmpfile = str(item.getFileObj())
        if os.path.isfile(mmpfile):
            #self.newModel = Assembly(self.w, "Assembly 1")
            self.newModel = Assembly(self.w, os.path.normpath(mmpfile)) #ninad060924 to fix bug 1164
            self.newModel.o = self.elemGLPane ## Make it looks "Assembly" used by glpane.
            readmmp(self.newModel, mmpfile)

# What we did in Qt 3:
##         #self.newModel = Assembly(self.w, "Assembly 1")
##         self.newModel = Assembly(self.w, os.path.normpath(mmpfile)) #ninad060924 to fix bug 1164

##         self.newModel.o = self.elemGLPane ## Make it looks "Assembly" used by glpane.
##         readmmp(self.newModel, mmpfile)

##         # The following is absolute nonsense, and is part of what's breaking the fix of bug 2028,
##         # so it needs to be revised, to give this assy a standard structure.
##         # We'll have to find some other way to draw the hotspot singlet
##         # (e.g. a reasonable, straightforward way). So we did -- MMKitView.always_draw_hotspot is True.
##         # [bruce 060627]

## ##        # Move all stuff under assembly.tree into assy.shelf. This is needed to draw hotspot singlet
## ##        def addChild(child):
## ##            self.newModel.shelf.addchild(child)
## ##
## ##        # Remove existing clipboard items from the libary part before adopting childern from 'tree'.
## ##        self.newModel.shelf.members = []
## ##        self.newModel.tree.apply2all(addChild)
## ##
## ##        self.newModel.shelf.prior_part = None
## ##        self.newModel.part = Part(self.newModel, self.newModel.shelf)

##         if 1: #bruce 060627

            self.newModel.update_parts() #k not sure if needed after readmmp)
            self.newModel.checkparts()
            if self.newModel.shelf.members:
                if debug_flags.atom_debug:
                    print "debug warning: library part %r contains clipboard items" % mmpfile
                    # we'll see if this is common
                    # happens for e.g. nanokids/nanoKid-C39H42O2.mmp
                for m in self.newModel.shelf.members[:]:
                    m.kill() #k guess about a correct way to handle them
                self.newModel.update_parts() #k probably not needed
                self.newModel.checkparts() #k probably not needed
        else:
            self.newModel = None

        self.elemGLPane.updateModel(self.newModel)


    def _clipboardPageView(self):
        """Updates the clipboard page. """
        if not self.currentPageOpen(ClipboardPage):
            # (old code permitted this to be false below in 'if len(list):',
            #  but failed to check for it in the 'else' clause,
            #  thus causing bug 1627 [I think], now fixed in our caller)
            print "bug: _clipboardPageView called when not self.currentPageOpen(ClipboardPage)" #bruce 060313
            return

        self.pastableItems = self.w.assy.shelf.get_pastable_chunks()
        self.chunkListBox.clear()
        for item in self.pastableItems:
            self.chunkListBox.addItem(item.name)

        newModel = None
        if len(self.pastableItems):
            i = self.w.pasteComboBox.currentIndex()
            if i < 0:
                i = self.w.pasteComboBox.count() - 1
            # Make sure the clipboard page is open before calling selSelected(), because
            # setSelected() causes the clipboard page to be displayed when we don't want it to
            # be displayed (i.e. pressing Control+C to copy something to the clipboard).
            self.chunkListBox.setCurrentItem(self.chunkListBox.item(i))
            # bruce 060313 question: why don't we now have to pass the selected chunk to
            # self.elemGLPane.updateModel? ###@@@
            newModel = self.pastableItems[i]
        self.elemGLPane.updateModel(newModel)
        self.update_clipboard_page_icon()


    def update_clipboard_page_icon(self):
        """Updates the Clipboard page (tab) icon with a full or empty clipboard icon
        based on whether there is anything on the clipboard (pasteables).
        """
        if not self.icon_tabs:
            # Work around for bug 1659. mark 060310 [revised by bruce 060313]
            return

        if self.w.assy.shelf.get_pastable_chunks():
            clipboard_ic = imagename_to_icon("actions/Properties Manager/clipboard-full.png")
        else:
            clipboard_ic = imagename_to_icon("actions/Properties Manager/clipboard-empty.png")

        self.mmkit_tab.setTabIcon(self.mmkit_tab.indexOf(self.clipboardPage), QIcon(clipboard_ic))

    class DirView(QTreeView):
        def __init__(self, mmkit, parent):
            QTreeView.__init__(self, parent)

            self.setEnabled(True)
            self.model = QtGui.QDirModel(['*.mmp', '*.MMP'], # name filters
                                         QDir.AllEntries|QDir.AllDirs|QDir.NoDotAndDotDot, # filters
                                         QDir.Name # sort order
                                         )
                # explanation of filters (from Qt 4.2 doc for QDirModel):
                # - QDir.AllEntries = list files, dirs, drives, symlinks.
                # - QDir.AllDirs = include dirs regardless of other filters [guess: needed to ignore the name filters for dirs]
                # - QDir.NoDotAndDotDot = don't include '.' and '..' dirs
                #
                # about dirnames of "CVS":
                # The docs don't mention any way to filter the dirnames using a callback,
                # or any choices besides "filter them same as filenames" or "don't filter them".
                # So there is no documented way to filter out the "CVS" subdirectories like we did in Qt3
                # (short of subclassing this and overriding some methods,
                #  but the docs don't make it obvious how to do that correctly).
                # Fortunately, autoBuild.py removes them from the partlib copy in built releases.
                #
                # Other QDirModel methods we might want to use:
                # QDirModel.refresh, to update its state from the filesystem (but see the docs --
                #  they imply we might have to pass the model's root pathname to that method,
                #  even if it hasn't changed, but they're not entirely clear on that).
                #
                # [bruce 070502 comments]

            self.path = None
            self.mmkit = mmkit
            self.setModel(self.model)
            self.setWindowTitle(self.tr("Dir View"))

            self.setItemsExpandable(True)
            self.setAlternatingRowColors(True)
            self.setColumnWidth(0, 200)
            for i in range(2,4):
                self.setColumnWidth(i, 4)

            self.show()

        #Ninad 070326 reimplementing mouseReleaseEvent and resizeEvent
        #for DirView Class (which is a subclass of QTreeView)
        #The old code reimplemented 'event' class which handles *all* events.
        #There was a bad bug which didn't send an event when the widget is resized
        # and then the seletcion is changed. In NE1Qt3 this wasn't a problem because
        #it only had one column. Now that we have multiple columns
        #(which are needed to show the horizontal scrollbar.
        # While using Library page only resize event or mouse release events
        #by the user should update the thumbview.
        #The Qt documentation also suggests reimplementing subevents instead of the main
        #event handler method (event())
        def mouseReleaseEvent(self, evt):
            """ Reimplementation of mouseReleaseEvent method of QTreeView"""
            if self.selectedItem() is not None:
                    self.mmkit._libPageView()
            return QTreeView.mouseReleaseEvent(self, evt)

        def resizeEvent(self, evt):
            """ Reimplementation of resizeEvent method of QTreeView"""
            if self.selectedItem() is not None:
                    self.mmkit._libPageView()
            return QTreeView.resizeEvent(self, evt)


        #Following method (event() ) is not reimplemented anymore. Instead, the subevent handlers are
        #reimplemented (see above)  -- ninad 070326
        """
        def event(self, evt):
            if evt.type() == evt.Timer:
                # This is the event we get when the library selection changes, so if there has
                # been a library selection, update the library page's GLPane. But this can also
                # happen without a selection; in that case don't erase the atom page's display.
                if self.selectedItem() is not None:
                    self.mmkit._libPageView()
            return QTreeView.event(self, evt)"""

        def setRootPath(self, path):
            self.path = path
            self.setRootIndex(self.model.index(path))

        def selectedItem(self):
            indexes = self.selectedIndexes()
            if not indexes:
                return None
            index = indexes[0]
            if not index.isValid():
                return None

            return self.FileItem(str(self.model.filePath(index)))

    class FileItem:
        def __init__(self, path):
            self.path = path
            dummy, self.filename = os.path.split(path)
        def name(self):
            return self.filename
        def getFileObj(self):
            return self.path
    DirView.FileItem = FileItem

    def _setNewView(self, viewClassName):
        # Put the GL widget inside the frame
        if not self.flayout:
            self.flayout = QVBoxLayout(self.elementFrame)
            self.flayout.setMargin(1)
            self.flayout.setSpacing(1)
        else:
            if self.elemGLPane:
                self.flayout.removeChild(self.elemGLPane)
                self.elemGLPane = None

        if viewClassName == 'ChunkView':
            # We never come here! How odd.
            self.elemGLPane = ChunkView(self.elementFrame, "chunk glPane", self.w.glpane)
        elif viewClassName == 'MMKitView':
            self.elemGLPane = MMKitView(self.elementFrame, "MMKitView glPane", self.w.glpane)

        self.flayout.addWidget(self.elemGLPane,1)


        #ninad 070326. Note that self.DirView inherits QTreeView.
        #It has got nothing to do with the experimental class DirView in file Dirview.py
        self.dirView = self.DirView(self, self.libraryPage)
        self.dirView.setSortingEnabled(False) #bruce 070521 changed True to False -- fixes "reverse order" bug on my Mac
        ##self.dirView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

        libraryPageLayout = QVBoxLayout(self.libraryPage)
        libraryPageLayout.setMargin(pmMMKitPageMargin) # Was 4. Mark 2007-05-30
        libraryPageLayout.setSpacing(2)
        libraryPageLayout.addWidget(self.dirView)


        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        libDir = os.path.normpath(filePath + '/../partlib')

        self.libPathKey = '/nanorex/nE-1/libraryPath'
        libDir = env.prefs.get(self.libPathKey, libDir)

        if os.path.isdir(libDir):
            self.rootDir = libDir
            self.dirView.setRootPath(libDir)
        else:
            self.rootDir = None
            from history.HistoryWidget import redmsg
            env.history.message(redmsg("The part library directory: %s doesn't exist." %libDir))

    def browseDirectories(self):
       """Slot method for the browse button of library page. """
       # Determine what directory to open.
       if self.w.assy.filename:
           odir = os.path.dirname(self.w.assy.filename)
       else:
           from utilities.prefs_constants import workingDirectory_prefs_key
           odir = env.prefs[workingDirectory_prefs_key]

       fdir = QFileDialog.getExistingDirectory(self, "Choose library directory", odir)
       libDir = str(fdir)
       if libDir and os.path.isdir(libDir):
           env.prefs[self.libPathKey] = libDir
           self.dirView.setRootPath(libDir)
           #Refresh GL-thumbView display
           self.newModel = None
           self.elemGLPane.updateModel(self.newModel)

    def useDefaultPartLibDirectory(self):
        """ Slot method that to reset the part lib directory path to default"""
        from history.HistoryWidget import redmsg

        #ninad070503 : A future enhancement would be a preference to have
        # a user defined 'default dir path' for the
        #part lib location.

        # set libDir to the standard partlib path
        filePath = os.path.dirname(os.path.abspath(sys.argv[0]))
        libDir = os.path.normpath(filePath + '/../partlib')

        if libDir and os.path.isdir(libDir):
            if self.dirView.path == libDir:
                msg1 = "Current directory path for the partlib is the default path."
                msg2 = " Current path not changed"
                env.history.message(redmsg(msg1 + msg2))
                return
            env.prefs[self.libPathKey] = libDir
            self.dirView.setRootPath(libDir)
            #Refresh GL-thumbView display
            self.newModel = None
            self.elemGLPane.updateModel(self.newModel)
        else:
            msg1 = "The default patlib directory %s doesn't exist."%libDir
            msg2 = "Current path not changed"
            env.history.message(redmsg(msg1 + msg2))


    def closeEvent(self, e):
        """This event handler receives all MMKit close events.  In other words,
        when this dialog's close() slot gets called, this gets called with event 'e'.
        """
        self.hide()

        # If the 'Library' page is open, change it to 'Atoms'.  Mark 051212.
        if self.currentPageOpen(LibraryPage):
            self.setup_current_page(self.atomsPage)


#bruce 070615 commented out the following since I think it's obsolete:
# (evidence: no other mentions of 'polish' or 'move_to_best_location' in our code,
#  and MMKit is no longer a movable dialog)
##    num_polish = 0
##
##    def polish(self):
##        """This slot is called after a widget has been fully created and before it is shown the very first time.
##        Polishing is useful for final initialization which depends on having an instantiated widget.
##        This is something a constructor cannot guarantee since the initialization of the subclasses might not be finished.
##        After this function, the widget has a proper font and palette and QApplication.polish() has been called.
##        Remember to call QDialog's implementation when reimplementing this function.
##        """
##        QDialog.polish(self) # call QDialog's polish() implementation
##        self.num_polish += 1
##        #&print "num_polish =", self.num_polish
##        if self.num_polish < 2:
##            # polish() is called twice; not sure why.
##            # Call move_to_best_location() only after the second polish signal since
##            # get_location() can only get self.frameGeometry() after that.
##            return
##        self.move_to_best_location(True)


    def show(self):
        """MMKit\'s show slot.
        """
        #QDialog.show(self)
        #&print "MMKit.move: setting mainwindow to active window"
        #Show it in Property Manager Tab ninad061207
        if not self.pw or self:
            self.pw = self.w.activePartWindow()       #@@@ ninad061206
            self.pw.updatePropertyManagerTab(self)
            self.setSponsor()

        else:
            if not self.pw:
                self.pw = self.w.activePartWindow()
            self.pw.updatePropertyManagerTab(self)


        self.w.activateWindow() # Fixes bug 1503.  mark 060216.
            # Required to give the keyboard input focus back to self (MainWindow).

    def add_whats_this_text(self):
        """What's This text for some of the widgets in the Build > Atoms Property Manager.
        Many are still missing.
        """

        self.elementFrame.setWhatsThis("""<b>Preview Window</b>
        <p>This displays the active object. It can be inserted by double
        clicking in the 3D graphics area.</p>
        <p>Left click on a red bondpoint to make it a green <i>hotspot</i>
        (clipboard and library parts only). The hotspot indicates which
        bondpoint should be used to bond the current object when selecting
        a bondpoint in the model.</p>
        <p><u>Mouse Commands Supported</u><br>
        Left - Select hotspot (clipboard and library parts only)<br>
        Middle - Rotate view<br> \
        Wheel - Zoom in/out \
        </p>""")

        self.MMKit_groupBox.setWhatsThis("""<b>Molecular Modeling Kit</b>
        <p>A tabular widget for selecting atom types or other structures to insert
        into the model.</p>
        <p><b>Atoms Tab</b> - A select group of atom types options from the periodic
        table of elements.</p>
        <p><b>Clipboard Tab</b> - the list of objects copied on the clipboard (using
        the Copy command).</p>
        <p><b>Library Tab</b> - Accesses the NE1 Part Library. There are hundreds of
        structures to choose from.</p>""")

        self.transmuteBtn.setWhatsThis("""<b>Transmute Atoms</b>
        <p>When clicked, transmutes selected atoms to the current type displayed
        in the Preview window.</p>""")

        self.transmuteCB.setWhatsThis("""<b>Force to keep bonds</b>
        <p>When checked, all bonds remain in place when atoms are transmuted,
        even if this will result in unrealistic (chemical) bonds.</p>""")

        self.selectionFilter_groupBox.setWhatsThis("""<b>Atoms Selection Filter</b>
        <p>When activated, only atoms listed can be selected.</p>""")

        self.advancedOptions_groupBox.setWhatsThis("""<b>Advanced Options</b>
        <p><b>Autobond</b> - when checked, the atom being inserted or attached to another
        atom will autobond to other bondpoints of other candidate atoms automatically.</p>
        <p><b>Highlighting</b> - Turns on/off hover highlighting.</p>
        <p><b>Water</b>- Adds a tranparent plane normal to the screen through 0,0,0. Anything
        behind the water plane can not be selected.</p>""")

        self.transmuteAtomsAction.setWhatsThis("""<b>Transmute Atoms</b>
        <p>When clicked, transmutes selected atoms to the current type displayed
        in the Preview window.</p>""")

    pass # end of class MMKit

# end
