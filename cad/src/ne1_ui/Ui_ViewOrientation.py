# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import Qt
from PyQt4.Qt import QRect
from utilities.icon_utilities import geticon

class Ui_ViewOrientation:

    def setupUi(self, orientationWidget):

        win = self.win
        MainWindow = self.win

        # Set the default width and height.
        _width = 150
        _height = 280
        _maxWidth = 400 # 400 should be more than enough. --mark

        # "View > Orientation" Dock Widget
        orientationWidget.setEnabled(True)
        orientationWidget.setFloating(True)
        orientationWidget.setVisible(False)
        orientationWidget.setWindowTitle("Orientation" )
        orientationWidget.setWindowIcon(
            geticon("ui/actions/View/Modify/Orientation.png"))
        orientationWidget.setGeometry(QRect(0, 0, _width, _height))
        orientationWidget.setMaximumWidth(400)

        x = max(0, win.geometry().x())
        y = max(0, win.geometry().y())

        orientationWidget.move(x, y)

        self.orientationWindowContents = QtGui.QWidget(orientationWidget)

        gridlayout = QtGui.QGridLayout(self.orientationWindowContents)

        gridlayout.setMargin(4)
        gridlayout.setSpacing(4)

        hboxlayout = QtGui.QHBoxLayout()
        hboxlayout.setMargin(0)
        hboxlayout.setSpacing(6)

        self.pinOrientationWindowToolButton = QtGui.QToolButton(self.orientationWindowContents)
        self.pinOrientationWindowToolButton.setCheckable(True)

        self.pinOrientationWindowToolButton.setIcon(
            geticon("ui/dialogs/unpinned.png"))
        hboxlayout.addWidget(self.pinOrientationWindowToolButton)

        self.saveNamedViewToolButton = QtGui.QToolButton(self.orientationWindowContents)
        self.saveNamedViewToolButton.setIcon(
            geticon("ui/actions/View/Modify/Save_Named_View.png"))  #@@ ninad 061115 dir path will be modified
        hboxlayout.addWidget(self.saveNamedViewToolButton)
        gridlayout.addLayout(hboxlayout, 0, 0, 1, 1)

        self.orientationViewList = QtGui.QListWidget(orientationWidget)
        self.orientationViewList.setFlow(QtGui.QListWidget.TopToBottom)
        self.orientationViewList.setWindowIcon(
            geticon("ui/actions/View/Modify/Orientation.png"))

        gridlayout.addWidget(self.orientationViewList, 1, 0, 1, 1)

        orientationWidget.setWidget(self.orientationWindowContents)

        MainWindow.addDockWidget(Qt.BottomDockWidgetArea, orientationWidget)