#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
from PyQt4.Qt import *
from PyQt4 import QtCore, QtGui

# Hunt for the icons directory
icons = 'icons'
for i in range(3):
    import os
    if os.path.exists(icons + '/MainWindowUI_image1.png'):
        break
    icons = '../' + icons



partWindowBaseClass = QWidget
# partWindowBaseClass = QGroupBox

class PartWindow(partWindowBaseClass):
    def __init__(self, parent=None):
        partWindowBaseClass.__init__(self)
        self.parent = parent
        self.setWindowTitle("My Part Window")
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        layout = QtGui.QHBoxLayout(self)
        layout.setMargin(0)
        layout.setSpacing(0)

        #########################

        holder = QWidget()
        holder.setMaximumWidth(200)
        sublayout = QVBoxLayout(holder)
        sublayout.setMargin(0)
        sublayout.setSpacing(0)
        layout.addWidget(holder)

        dismissButton = QPushButton()
        dismissButton.setIcon(QIcon(icons + '/GrapheneGeneratorDialog_image3.png'))
        sublayout.addWidget(dismissButton)
        self.connect(dismissButton,SIGNAL("clicked()"),self.dismiss)

        ###

        self.propertyManager = QtGui.QTabWidget()
        self.propertyManager.setCurrentIndex(0)
        self.propertyManager.setMaximumWidth(200)

        self.modelTreeTab = QtGui.QWidget()
        self.propertyManager.addTab(self.modelTreeTab, "Model Tree")
        modelTreeTabLayout = QtGui.QVBoxLayout(self.modelTreeTab)
        modelTreeTabLayout.setMargin(0)
        modelTreeTabLayout.setSpacing(0)

        self.tab2 = QtGui.QWidget()
        self.propertyManager.addTab(self.tab2, "Second tab")

        sublayout.addWidget(self.propertyManager)

        ###

        self.modelTree = QtGui.QTreeWidget()
        self.modelTree.setColumnCount(2)
        self.modelTree.setHeaderLabels(['', 'Thingy'])
        self.populateModelTree()
        modelTreeTabLayout.addWidget(self.modelTree)

        self.glpane = GLPane()
        layout.addWidget(self.glpane)


    def populateModelTree(self):
        abc = QTreeWidgetItem()
        abc.setIcon(0, QIcon(icons + '/NanotubeGeneratorDialog_image1.png'))
        abc.setText(1, 'abc')
        self.modelTree.addTopLevelItem(abc)

        defg = QTreeWidgetItem(abc)
        defg.setIcon(0, QIcon(icons + '/MainWindowUI_image125.png'))
        defg.setText(1, 'defg')

        hi = QTreeWidgetItem(abc)
        hi.setIcon(0, QIcon(icons + '/MainWindowUI_image138.png'))
        hi.setText(1, 'hi')

        jkl = QTreeWidgetItem(defg)
        jkl.setIcon(0, QIcon(icons + '/MainWindowUI_image38.png'))
        jkl.setText(1, 'jkl')
        mno = QTreeWidgetItem(defg)
        mno.setIcon(0, QIcon(icons + '/GrapheneGeneratorDialog_image7.png'))
        mno.setText(1, 'mno')
        pqr = QTreeWidgetItem(defg)
        pqr.setIcon(0, QIcon(icons + '/MainWindowUI_image90.png'))
        pqr.setText(1, 'pqr')

        stu = QTreeWidgetItem(hi)
        stu.setIcon(0, QIcon(icons + '/UserPrefsDialog_image0.png'))
        stu.setText(1, 'stu')
        vwx = QTreeWidgetItem(hi)
        vwx.setIcon(0, QIcon(icons + '/MainWindowUI_image40.png'))
        vwx.setText(1, 'vwx')

    def setRowCol(self, row, col):
        self.row, self.col = row, col

    def dismiss(self):
        self.parent.removePartWindow(self)




########################################################################



class GLPane(QGLWidget):
    def __init__(self, master=None):
        glformat = QGLFormat()
        glformat.setStencil(True)
        QGLWidget.__init__(self, glformat, master)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)


##########################################################################



class GridPosition:
    def __init__(self):
        self.row, self.col = 0, 0
        self.availableSlots = [ ]
        self.takenSlots = { }

    def next(self, widget):
        if len(self.availableSlots) > 0:
            row, col = self.availableSlots.pop(0)
        else:
            row, col = self.row, self.col
            if row == col:
                # when on the diagonal, start a new self.column
                self.row = 0
                self.col = col + 1
            elif row < col:
                # continue moving down the right edge until we're about
                # to hit the diagonal, then start a new bottom self.row
                if row == col - 1:
                    self.row = row + 1
                    self.col = 0
                else:
                    self.row = row + 1
            else:
                # move right along the bottom edge til you hit the diagonal
                self.col = col + 1
        self.takenSlots[widget] = (row, col)
        return row, col

    def removeWidget(self, widget):
        rc = self.takenSlots[widget]
        self.availableSlots.append(rc)
        del self.takenSlots[widget]

# MAIN_WINDOW_SIZE = (1024, 768)
MAIN_WINDOW_SIZE = (800, 600)

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("My Main Window")
        self.setMinimumWidth(MAIN_WINDOW_SIZE[0])
        self.setMinimumHeight(MAIN_WINDOW_SIZE[1])

        self.statusbar = QtGui.QStatusBar(self)
        self.statusbar.showMessage("Status message")
        self.setStatusBar(self.statusbar)

        self.menubar = self.menuBar()
        # Any menu action makes the status bar message disappear

        fileMenu = QtGui.QMenu(self.menubar)
        fileMenu.setTitle("File")
        self.menubar.addAction(fileMenu.menuAction())

        newAction = QtGui.QAction("New", self)
        newAction.setIcon(QtGui.QIcon(icons + '/GroupPropDialog_image0.png'))
        fileMenu.addAction(newAction)
        openAction = QtGui.QAction("Open", self)
        openAction.setIcon(QtGui.QIcon(icons + "/MainWindowUI_image1"))
        fileMenu.addAction(openAction)
        saveAction = QtGui.QAction("Save", self)
        saveAction.setIcon(QtGui.QIcon(icons + "/MainWindowUI_image2"))
        fileMenu.addAction(saveAction)

        for otherMenuName in ('Edit', 'View', 'Display', 'Select', 'Modify', 'NanoHive-1', 'Help'):
            otherMenu = QtGui.QMenu(self.menubar)
            otherMenu.setTitle(otherMenuName)
            self.menubar.addAction(otherMenu.menuAction())

        self.setMenuBar(self.menubar)

        self.connect(newAction,SIGNAL("activated()"),self.newFile)
        self.connect(openAction,SIGNAL("activated()"),self.openFile)
        self.connect(saveAction,SIGNAL("activated()"),self.saveFile)

        centralwidget = QWidget()
        self.setCentralWidget(centralwidget)
        layout = QVBoxLayout(centralwidget)
        layout.setMargin(0)
        layout.setSpacing(0)
        middlewidget = QWidget()

        self.bigButtons = QWidget()
        bblo = QHBoxLayout(self.bigButtons)
        bblo.setMargin(0)
        bblo.setSpacing(0)
        self.bigButtons.setMinimumHeight(50)
        self.bigButtons.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        for name in ('Features', 'Sketch', 'Build', 'Dimension', 'Simulator'):
            btn = QPushButton(self.bigButtons)
            btn.setMaximumWidth(80)
            btn.setMinimumHeight(50)
            btn.setText(name)
            self.bigButtons.layout().addWidget(btn)
        self.bigButtons.hide()
        layout.addWidget(self.bigButtons)

        self.littleIcons = QWidget()
        self.littleIcons.setMinimumHeight(30)
        self.littleIcons.setMaximumHeight(30)
        lilo = QHBoxLayout(self.littleIcons)
        lilo.setMargin(0)
        lilo.setSpacing(0)
        pb = QPushButton(self.littleIcons)
        pb.setIcon(QIcon(icons + '/GroupPropDialog_image0.png'))
        self.connect(pb,SIGNAL("clicked()"),self.newFile)
        lilo.addWidget(pb)
        for x in "1 2 4 5 6 7 8 18 42 10 43 150 93 94 97 137".split():
            pb = QPushButton(self.littleIcons)
            pb.setIcon(QIcon(icons + '/MainWindowUI_image' + x + '.png'))
            lilo.addWidget(pb)
        layout.addWidget(self.littleIcons)

        layout.addWidget(middlewidget)

        self.layout = QGridLayout(middlewidget)
        self.layout.setMargin(0)
        self.layout.setSpacing(0)
        self.gridPosition = GridPosition()
        self.numParts = 0

    def removePartWindow(self, pw):
        self.layout.removeWidget(pw)
        self.gridPosition.removeWidget(pw)
        self.numParts -= 1
        if self.numParts == 0:
            self.bigButtons.hide()

    def newFile(self):
        if self.numParts == 0:
            self.bigButtons.show()
        self.numParts += 1
        pw = PartWindow(self)
        row, col = self.gridPosition.next(pw)
        self.layout.addWidget(pw, row, col)

    def openFile(self):
        print "Let's pretend we're opening a file"

    def saveFile(self):
        print "Let's pretend we're saving a file"

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
