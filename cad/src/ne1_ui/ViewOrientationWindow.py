# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
ViewOrientationWindow.py

@author: Ninad
@version: $Id$
@copyright: 2006-2007 Nanorex, Inc.  See LICENSE file for details.

Module classification: [bruce 080101]

Ideally this might be general and not need to be a singleton,
and be classified into "widgets". For all I know, it already almost is,
but certainly the attr accesses into "win" are not yet that general,
and I can't tell how much else might not be.
So to be safe I'm putting it into ne1_ui, though refactoring
almost all of it into "widgets" would be good to do sometime.
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt, SIGNAL, QMainWindow, QDockWidget

from ne1_ui.Ui_ViewOrientation import Ui_ViewOrientation
from utilities.icon_utilities import geticon

class ViewOrientationWindow(QDockWidget, Ui_ViewOrientation):

    def __init__(self, win):
        QDockWidget.__init__(self, win)
        self.win = win
        #self.setupUi(self.win)
        self.setupUi(self)

        win.standardViewMethodDict = {}
        win.namedViewMethodDict = {}

        self.lastViewList = None

        #Signals
        QtCore.QObject.connect(self.saveNamedViewToolButton,QtCore.SIGNAL("clicked()"), win.saveNamedView)
        QtCore.QObject.connect(self.orientationViewList, SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.changeViewOrientation)
        QtCore.QObject.connect(self.pinOrientationWindowToolButton, SIGNAL("clicked()"), self.changePinIcon)

    def createOrientationViewList(self):
        """
        Create a list of views for the first time.
        It includes all standard views and all named views that exist in the MT.
        """
        #NIY ninad061116
        #Add items as QListWidgetItem ...
        #Defining these as QListWidgetItem facilitates use of itemDoubleClicked Signal) ninad 061115

        win = self.win

        self.addStandardViewItems()

        self.namedViewList = win.getNamedViewList() #Save the last named view list

        for item in self.namedViewList:
            itemNamedView = QtGui.QListWidgetItem(item.name, self.orientationViewList)
            itemNamedView.setIcon(
                geticon("ui/modeltree/csys.png"))
            win.namedViewMethodDict[itemNamedView] = item.change_view

        self.lastViewList = self.namedViewList

    def addStandardViewItems(self):
        """
        Add the standard views to the Orientation Window
        """
        win = self.win

        #The default items
        itemViewNormalTo = QtGui.QListWidgetItem(win.viewNormalToAction.objectName(), self.orientationViewList)
        itemViewNormalTo.setIcon(win.viewNormalToAction.icon())
        win.standardViewMethodDict[itemViewNormalTo] = win.viewNormalTo

        itemViewParallelTo= QtGui.QListWidgetItem(win.viewParallelToAction.objectName(), self.orientationViewList)
        itemViewParallelTo.setIcon(win.viewParallelToAction.icon())
        win.standardViewMethodDict[itemViewParallelTo] = win.viewParallelTo

        itemViewFront = QtGui.QListWidgetItem(win.viewFrontAction.objectName(), self.orientationViewList)
        itemViewFront.setIcon(win.viewFrontAction.icon())
        win.standardViewMethodDict[itemViewFront] = win.viewFront

        itemViewBack = QtGui.QListWidgetItem(win.viewBackAction.objectName(), self.orientationViewList)
        itemViewBack.setIcon(win.viewBackAction.icon())
        win.standardViewMethodDict[itemViewBack] = win.viewBack

        itemViewLeft = QtGui.QListWidgetItem(win.viewLeftAction.objectName(), self.orientationViewList)
        itemViewLeft.setIcon(win.viewLeftAction.icon())
        win.standardViewMethodDict[itemViewLeft] = win.viewLeft

        itemViewRight = QtGui.QListWidgetItem(win.viewRightAction.objectName(), self.orientationViewList)
        itemViewRight.setIcon(win.viewRightAction.icon())
        win.standardViewMethodDict[itemViewRight] = win.viewRight

        itemViewTop = QtGui.QListWidgetItem(win.viewTopAction.objectName(), self.orientationViewList)
        itemViewTop.setIcon(win.viewTopAction.icon())
        win.standardViewMethodDict[itemViewTop] = win.viewTop

        itemViewBottom = QtGui.QListWidgetItem(win.viewBottomAction.objectName(), self.orientationViewList)
        itemViewBottom.setIcon(win.viewBottomAction.icon())
        win.standardViewMethodDict[itemViewBottom] = win.viewBottom

        itemViewIsometric = QtGui.QListWidgetItem(win.viewIsometricAction.objectName(), self.orientationViewList)
        itemViewIsometric.setIcon(win.viewIsometricAction.icon())
        win.standardViewMethodDict[itemViewIsometric] = win.viewIsometric

        itemViewFlipViewVert = QtGui.QListWidgetItem(win.viewFlipViewVertAction.objectName(), self.orientationViewList)
        itemViewFlipViewVert.setIcon(win.viewFlipViewVertAction.icon())
        win.standardViewMethodDict[itemViewFlipViewVert] = win.viewFlipViewVert

        itemViewFlipViewHorz = QtGui.QListWidgetItem(win.viewFlipViewHorzAction.objectName(), self.orientationViewList)
        itemViewFlipViewHorz.setIcon(win.viewFlipViewHorzAction.icon())
        win.standardViewMethodDict[itemViewFlipViewHorz] = win.viewFlipViewHorz

        itemViewRotatePlus90 = QtGui.QListWidgetItem(win.viewRotatePlus90Action.objectName(), self.orientationViewList)
        itemViewRotatePlus90.setIcon(win.viewRotatePlus90Action.icon())
        win.standardViewMethodDict[itemViewRotatePlus90] = win.viewRotatePlus90

        itemViewRotateMinus90 = QtGui.QListWidgetItem(win.viewRotateMinus90Action.objectName(), self.orientationViewList)
        itemViewRotateMinus90.setIcon(win.viewRotateMinus90Action.icon())
        win.standardViewMethodDict[itemViewRotateMinus90] = win.viewRotateMinus90
        return

    def updateOrientationViewList(self, viewList=None):
        """
        Update the orientation view list when a new Saved Named View Node is created
        """
        # ninad 061201: This function is called from inside the mt_update() if the orientation
        # window is visible.

        win = self.win

        self.namedViewList = win.getNamedViewList()

        # check whether the list of view nodes is same as before. If its same, no need to go further.
        if self.namedViewList == self.lastViewList:
            ## print "updateOrientationViewList called but returning as named view nodes haven't changed"
            return

        #start with a clean slate
        #@@@ ninad 061201 It would have been better to update the dictionary with new key value pairs
        #(and removing key-val pairs not in the new list.) There should be a better way to update the
        #self.orientationViewList instead of erasing everything in it.
        #We are passing view nodes name (item.name) to
        # a QListWidgetItem . And this QListWidgetItem object in turn is included in the dictionary.
        # Since, even a huge assembly is unlikely to have a large number of named view nodes, for now I will
        #just use dict.clear() to clear the old dictionary and also self.orientationViewList.clear() to clear all the
        #items in orientationViewList (similar to what MMKit does)...Perhaps the latter implementation
        #should be changed in future

        win.namedViewMethodDict.clear()
        self.orientationViewList.clear()

        self.addStandardViewItems() # Add standard views as the list widget items to the orientation window

        for item in self.namedViewList:
            itemNamedView = QtGui.QListWidgetItem(item.name, self.orientationViewList)
            itemNamedView.setIcon(
                geticon("ui/modeltree/csys.png"))
            win.namedViewMethodDict[itemNamedView] = item.change_view

        self.lastViewList = self.namedViewList

    def changeViewOrientation(self, widgetItemJunk = None): #Ninad 061115
        """
        Change the view when the item in the Orientation view window
        is double clicked
        @param widgetItemJunk: This is the widget item from the
                             itemDoubleClicked signal. It is not used.
                             We just want to know that this event occured
        @type  widgetItemJunk: QWidgetItem or None
        """
        win = self.win

        if win.standardViewMethodDict.has_key(
              self.orientationViewList.currentItem() ):
            viewMethod = win.standardViewMethodDict[self.orientationViewList.currentItem()]
            viewMethod()
        elif win.namedViewMethodDict.has_key(
              self.orientationViewList.currentItem() ):
            viewMethod = win.namedViewMethodDict[self.orientationViewList.currentItem()]
            viewMethod()
        else:
            print "bug while changing the view from Orientation Window."\
                  "Ignoring change view command"
            #@@ ninad 061201 Not sure if it would ever be called.
            #Adding just to be safe.
            return

        #Hide orientation window after changing the view if it is 'unpinned'
        if not self.pinOrientationWindowToolButton.isChecked():
            win.orientationWindow.setVisible(False)
            # REVIEW: should we replace win.orientationWindow by self, which
            # I think is always the same? [bruce 080101 question]

    def changePinIcon(self):
        """
        Change the icon of the Pinned button
        """
        if self.pinOrientationWindowToolButton.isChecked():
            self.pinOrientationWindowToolButton.setIcon(
                geticon("ui/dialogs/pinned.png"))
        else:
            self.pinOrientationWindowToolButton.setIcon(
                geticon("ui/dialogs/unpinned.png"))

    def getLastNamedViewList(self, list):
        self.lastNamedViewList = list
        return self.lastNamedViewList

    def keyReleaseEvent(self, event):
        """
        The keystroke release event handler for the Orientation dialog.

        @param event: The key release event.
        @type  event: U{B{QKeyEvent}<http://doc.trolltech.com/4/qkeyevent.html>}

        @note: This overrides QWidget.keyReleaseEvent().
        """
        key = event.key()
        if key == Qt.Key_Escape:
            # Close the dialog if the user has (pressed and then) released the
            # Esc key.
            self.close()
        else:
            event.ignore() # Important, per the Qt documentation.

    def closeEvent(self, ce):
        """
        When the user closes the dialog by clicking the 'X' button
        on the dialog title bar, uncheck the vieOrientationAction icon
        and close the dialog.
        """
        self.win.viewOrientationAction.setChecked(False)
        ce.accept()

