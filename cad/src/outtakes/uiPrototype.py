#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""\
<p>This is an attempt to implement Mark's \"Starting NE-1\" slideshow
ideas. This is just a little prototype, and is meant to be tweaked as
we discuss things and reach a consensus about what kind of UI behavior
we want.</p>

<p>This prototype is done in Qt 4. It will encourage people to change
over, and a Qt 3 prototype would grow useless soon, and I can't
practically maintain both versions.</p>

<h1>Workspaces</h1>

<p>When we start, there are no workspaces up. We can bring up one or
more workspaces by selecting <b>File-&gt;New</b>. (Some day,
<b>File-&gt;Open</b> will also work.)</p>

<p>We probably need a concept of an <i>active</i> workspace, even if it's
only the one that the cursor is above right now. We at least need this to
decide which of the toolbar buttons to gray out.</p>

<h2>Tab widget: model tree, property manager</h2>

<p>Each workspace has its own tabbed area on the left side. There are
two tabs, the model tree and a second tab. The second tab could be a
property manager or any dialog that is appropriate at the moment. The
tabbed area for each workspace works completely independently.</p>

<h1>Command Manager Toolbar</h1>

<p>Until we bring up a workspace, the area for the workspace is empty,
and no command buttons are shown. Once there is at least one
workspace, a bunch of command buttons become available: Features,
Sketch, Build, Dimension, and Simulator.</p>

<p><i>Explain what these do....</i></p>

<p><i>It would make sense to me that usually, a command button will
bring up a dialog in the second tab of the tab widget. Is that
right?</i></p>

 <h1>Menu Bar</h1>

This is the typical menu bar that almost every graphical-interface
program has, starting with \"File\" and \"Edit\"...

<h1>Toolbar Buttons</h1>

<p>That's the kind of stuff we already have in NE-1. Those are applicable
in many situations, though in practice some will be grayed out, depending
on which workspace is active.</p>"""

from PyQt4 import QtCore, QtGui
from PyQt4.Qt import QWidget
from PyQt4.Qt import QGLWidget
from PyQt4.Qt import QDialog
from PyQt4.Qt import QMainWindow
from PyQt4.Qt import QSizePolicy
from PyQt4.Qt import QIcon
from PyQt4.Qt import QGLFormat
from PyQt4.Qt import QVBoxLayout
from PyQt4.Qt import QTextEdit
from PyQt4.Qt import QTextOption
from PyQt4.Qt import QPushButton
from PyQt4.Qt import SIGNAL
from PyQt4.Qt import QTimer
from PyQt4.Qt import QHBoxLayout
from PyQt4.Qt import QGridLayout

import modelTree.modelTreeGui as modelTreeGui

# Hunt for the icons directory
icons = 'icons'
for i in range(3):
    import os
    if os.path.exists(icons + '/MainWindowUI_image1.png'):
        break
    icons = '../' + icons

class PartWindow(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self)
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

        ###

        self.featureManager = QtGui.QTabWidget()
        self.featureManager.setCurrentIndex(0)
        self.featureManager.setMaximumWidth(200)

        self.modelTreeTab = QtGui.QWidget()
        self.featureManager.addTab(self.modelTreeTab, "Model Tree")
        modelTreeTabLayout = QtGui.QVBoxLayout(self.modelTreeTab)
        modelTreeTabLayout.setMargin(0)
        modelTreeTabLayout.setSpacing(0)

        self.propertyManagerTab = QtGui.QWidget()
        self.featureManager.addTab(self.propertyManagerTab, "Property Manager")

        sublayout.addWidget(self.featureManager)

        ###

        self.modelTree = modelTreeGui.TestWrapper()
        self.modelTree.addIconButton(QIcon(icons + '/GrapheneGeneratorDialog_image3.png'),
                                     self.dismiss)
        modelTreeTabLayout.addWidget(self.modelTree)

        self.glpane = GLPane()
        layout.addWidget(self.glpane)

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

class AboutWindow(QDialog):
    def __init__(self, html, width=600, timeout=None):
        QDialog.__init__(self)
        self.setMinimumWidth(width)
        self.setObjectName("About NanoEngineer-1")
        TextEditLayout = QVBoxLayout(self)
        TextEditLayout.setSpacing(0)
        TextEditLayout.setMargin(0)
        self.text_edit = QTextEdit(self)
        self.text_edit.setHtml(html)
        self.text_edit.setReadOnly(True)
        self.text_edit.setWordWrapMode(QTextOption.WordWrap)
        TextEditLayout.addWidget(self.text_edit)
        self.quit_button = QPushButton("OK")
        TextEditLayout.addWidget(self.quit_button)
        self.connect(self.quit_button, SIGNAL("clicked()"), self.close)
        if timeout is not None:
            self.qt = QTimer()
            self.qt.setInterval(1000*timeout)
            self.qt.start()
            self.connect(self.qt, SIGNAL("timeout()"), self.close)
        self.show()
        self.exec_()

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

        ################################################

        self.menubar = self.menuBar()
        # Any menu action makes the status bar message disappear

        fileMenu = QtGui.QMenu(self.menubar)
        fileMenu.setTitle("File")
        self.menubar.addAction(fileMenu.menuAction())

        newAction = QtGui.QAction("New", self)
        newAction.setIcon(QtGui.QtIcon(icons + '/GroupPropDialog_image0.png'))
        fileMenu.addAction(newAction)
        openAction = QtGui.QAction("Open", self)
        openAction.setIcon(QtGui.QtIcon(icons + "/MainWindowUI_image1"))
        fileMenu.addAction(openAction)
        saveAction = QtGui.QAction("Save", self)
        saveAction.setIcon(QtGui.QtIcon(icons + "/MainWindowUI_image2"))
        fileMenu.addAction(saveAction)

        self.connect(newAction,SIGNAL("activated()"),self.fileNew)
        self.connect(openAction,SIGNAL("activated()"),self.fileOpen)
        self.connect(saveAction,SIGNAL("activated()"),self.fileSave)

        for otherMenuName in ('Edit', 'View', 'Display', 'Select', 'Modify', 'NanoHive-1'):
            otherMenu = QtGui.QMenu(self.menubar)
            otherMenu.setTitle(otherMenuName)
            self.menubar.addAction(otherMenu.menuAction())

        helpMenu = QtGui.QMenu(self.menubar)
        helpMenu.setTitle("Help")
        self.menubar.addAction(helpMenu.menuAction())

        aboutAction = QtGui.QAction("About", self)
        aboutAction.setIcon(QtGui.QtIcon(icons + '/MainWindowUI_image0.png'))
        helpMenu.addAction(aboutAction)

        self.connect(aboutAction,SIGNAL("activated()"),self.helpAbout)

        ##############################################

        self.setMenuBar(self.menubar)

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
        self.connect(pb,SIGNAL("clicked()"),self.fileNew)
        lilo.addWidget(pb)
        for x in "1 2 4 5 6 7 8 18 42 10 43 150 93 94 97 137".split():
            pb = QPushButton(self.littleIcons)
            pb.setIcon(QIcon(icons + '/MainWindowUI_image' + x + '.png'))
            lilo.addWidget(pb)
        layout.addWidget(self.littleIcons)

        layout.addWidget(middlewidget)

        self.layout = QGridLayout(middlewidget)
        self.layout.setMargin(0)
        self.layout.setSpacing(2)
        self.gridPosition = GridPosition()
        self.numParts = 0

        self.show()
        explainWindow = AboutWindow("Select <b>Help-&gt;About</b>"
                                    " for instructions...",
                                    200, 3)

    def removePartWindow(self, pw):
        self.layout.removeWidget(pw)
        self.gridPosition.removeWidget(pw)
        self.numParts -= 1
        if self.numParts == 0:
            self.bigButtons.hide()

    def fileNew(self):
        if self.numParts == 0:
            self.bigButtons.show()
        self.numParts += 1
        pw = PartWindow(self)
        row, col = self.gridPosition.next(pw)
        self.layout.addWidget(pw, row, col)

    def fileOpen(self):
        print "Let's pretend we're opening a file"

    def fileSave(self):
        print "Let's pretend we're saving a file"

    def helpAbout(self):
        AboutWindow(__doc__)

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()

    sys.exit(app.exec_())
