# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details.
"""
General directory view widget. Based on Qt/PyQt example dirview.py,
with modifications for use in MMKit.

Note: in Qt3 this was used in MMKit.py, but in Qt4 it's not used there.

$Id$

This file contains some code from the Qt/PyQt example dirview.py,
whose copyright notice reads as follows:

**************************************************************************
**
** Copyright (C) 1992-2000 Trolltech AS.  All rights reserved.
** Some corrections by M. Biermaier (http://www.office-m.at)
**
** This file is part of an example program for Qt.  This example
** program may be used, distributed and modified without limitation.
**
***************************************************************************
"""

import sys

from PyQt4.Qt import QTreeWidgetItem
from PyQt4.Qt import QTreeWidget
from PyQt4.Qt import QListView
from PyQt4.Qt import QIcon
from PyQt4.Qt import QPixmap
from PyQt4.Qt import QSize
from PyQt4.Qt import QDir
from PyQt4.Qt import QApplication

from utilities.qt4transition import qt4todo

folder_closed_image =[
    "16 16 9 1",
    "g c #808080",
    "b c #c0c000",
    "e c #c0c0c0",
    "# c #000000",
    "c c #ffff00",
    ". c None",
    "a c #585858",
    "f c #a0a0a4",
    "d c #ffffff",
    "..###...........",
    ".#abc##.........",
    ".#daabc#####....",
    ".#ddeaabbccc#...",
    ".#dedeeabbbba...",
    ".#edeeeeaaaab#..",
    ".#deeeeeeefe#ba.",
    ".#eeeeeeefef#ba.",
    ".#eeeeeefeff#ba.",
    ".#eeeeefefff#ba.",
    ".##geefeffff#ba.",
    "...##gefffff#ba.",
    ".....##fffff#ba.",
    ".......##fff#b##",
    ".........##f#b##",
    "...........####."]

folder_open_image =[
    "16 16 11 1",
    "# c #000000",
    "g c #c0c0c0",
    "e c #303030",
    "a c #ffa858",
    "b c #808080",
    "d c #a0a0a4",
    "f c #585858",
    "c c #ffdca8",
    "h c #dcdcdc",
    "i c #ffffff",
    ". c None",
    "....###.........",
    "....#ab##.......",
    "....#acab####...",
    "###.#acccccca#..",
    "#ddefaaaccccca#.",
    "#bdddbaaaacccab#",
    ".eddddbbaaaacab#",
    ".#bddggdbbaaaab#",
    "..edgdggggbbaab#",
    "..#bgggghghdaab#",
    "...ebhggghicfab#",
    "....#edhhiiidab#",
    "......#egiiicfb#",
    "........#egiibb#",
    "..........#egib#",
    "............#ee#"]

folder_locked_image =[
    "16 16 10 1",
    "h c #808080",
    "b c #ffa858",
    "f c #c0c0c0",
    "e c #c05800",
    "# c #000000",
    "c c #ffdca8",
    ". c None",
    "a c #585858",
    "g c #a0a0a4",
    "d c #ffffff",
    "..#a#...........",
    ".#abc####.......",
    ".#daa#eee#......",
    ".#ddf#e##b#.....",
    ".#dfd#e#bcb##...",
    ".#fdccc#daaab#..",
    ".#dfbbbccgfg#ba.",
    ".#ffb#ebbfgg#ba.",
    ".#ffbbe#bggg#ba.",
    ".#fffbbebggg#ba.",
    ".##hf#ebbggg#ba.",
    "...###e#gggg#ba.",
    ".....#e#gggg#ba.",
    "......###ggg#b##",
    ".........##g#b##",
    "...........####."]

pix_file_image =[
    "16 16 7 1",
    "# c #000000",
    "b c #ffffff",
    "e c #000000",
    "d c #404000",
    "c c #c0c000",
    "a c #ffffc0",
    ". c None",
    "................",
    ".........#......",
    "......#.#a##....",
    ".....#b#bbba##..",
    "....#b#bbbabbb#.",
    "...#b#bba##bb#..",
    "..#b#abb#bb##...",
    ".#a#aab#bbbab##.",
    "#a#aaa#bcbbbbbb#",
    "#ccdc#bcbbcbbb#.",
    ".##c#bcbbcabb#..",
    "...#acbacbbbe...",
    "..#aaaacaba#....",
    "...##aaaaa#.....",
    ".....##aa#......",
    ".......##......."]

folderClosedIcon = 0
folderLockedIcon = 0
folderOpenIcon = 0
fileIcon = 0

qt4todo("""The QListView, QListViewItem, QCheckListItem, and
QListViewItemIterator classes have been renamed Q3ListView,
Q3ListViewItem, Q3CheckListItem, and Q3ListViewItemIterator, and have
been moved to the Qt3Support library. New Qt applications should use
one of the following four classes instead: QTreeView or QTreeWidget
for tree-like structures; QListWidget or the new QListView class for
one-dimensional lists.

See Model/View Programming for an overview of the new item view
classes.
http://doc.trolltech.com/4.0/model-view-programming.html

Examples involving QTreeWidgetItem:
Qt-4.1.4/examples/network/torrent/mainwindow.cpp
Qt-4.1.4/examples/tools/plugandpaint/plugindialog.cpp
--> Qt-4.1.4/examples/tools/settingseditor/settingstree.cpp <--
Qt-4.1.4/examples/xml/dombookmarks/xbeltree.cpp
Qt-4.1.4/examples/xml/saxbookmarks/xbelgenerator.cpp
Qt-4.1.4/examples/xml/saxbookmarks/xbelhandler.cpp""")

class FileItem(QTreeWidgetItem):
    def __init__(self, parent, fio, name=None):
        QTreeWidgetItem.__init__(self)
        parent.addChild(self)
        if name is not None:
            self.setText(1, name)

        self.f = name
        self.fileObj = fio

    def getFileObj(self):
        return self.fileObj

    def text(self, column):
        if column == 0:
            return self.f

    #def setup(self):
    #    self.setExpandable(1)
    #    QTreeWidgetItem.setup(self)


class Directory(QTreeWidgetItem):

    def __init__(self, parent, name=None):
        QTreeWidgetItem.__init__(self)

        self.filterList = ('mmp', 'MMP')

        if isinstance(parent, QListView):
            self.p = None
            if name:
                self.f = name
            else:
                self.f = '/'
        else:
            self.p = parent
            self.f = name

        self.readable = QDir( self.fullName() ).isReadable()

        if  not self.readable :
            self.setIcon(0, folderLockedIcon)
        else:
            self.setIcon(0, folderClosedIcon)
        if name is not None:
            self.setText(1, name)
        if isinstance(parent, QTreeWidget):
            parent.addTopLevelItem(self)
        else:
            parent.addChild(self)


    def setOpen(self, o):
        if  o:
            self.setIcon(0, folderOpenIcon)
        else:
            self.setIcon(0, folderClosedIcon)

        if o and not self.childCount():
            s = self.fullName()
            thisDir = QDir(s)
            if not thisDir.isReadable():
                self.readable = 0
                return

            files = thisDir.entryInfoList()
            if files:
                for f in files:
                    # f is a QFileInfo
                    # f.fileName is '.' or '..' or 'bearings' or...
                    fileName = str(f.fileName())
                    if fileName == '.' or fileName == '..':
                        continue
                    elif f.isSymLink():
                        d = QTreeWidgetItem(self, fileName)#, 'Symbolic Link')
                        d.setIcon(0, fileIcon)
                    elif f.isDir():
                        if fileName == 'CVS':
                            #bruce 060319 skip CVS directories, so developers see same set of directories as end-users
                            # (implements NFR I recently reported)
                            # WARNING: this is only legitimate for some applications of this module.
                            # For now that's ok (we only use it in MMKit). Later this feature should be turned on
                            # by an optional argument to __init__, and generalized to a list of files to not show
                            # or to a filter function.
                            continue
                        d = Directory(self, fileName)
                    else:
                        if f.isFile():
                            s = 'File'
                        else:
                            s = 'Special'
                        if not fileName[-3:] in self.filterList:
                            continue
                        d = FileItem(self, f.absFilePath(), fileName)
                        d.setIcon(0, fileIcon)

        qt4todo('QTreeWidgetItem.setOpen(self, o)')


    def setup(self):
        self.setExpandable(1)
        QTreeWidgetItem.setup(self)


    def fullName(self):
        if self.p:
            if not hasattr(self.p, 'fullName'):
                qt4todo('Make the parent a Directory instead of a DirView')
                s = self.f
            else:
                s = self.p.fullName() + self.f
        else:
            s = self.f

        if not s.endswith('/'):
            s += '/'
        return s


    def text(self, column):
        if column == 0:
            return self.f
        ##elif self.readable:
        ##    return 'Directory'
        ##else:
        ##    return 'Unreadable Directory'

    def setFilter(self, filterList):
        '''This is used to filter out file display in the QListView.
           @param filterList is a list of file tyes like '.mmp' or '.MMP' etc. '''
        self.filterList = filterList

class DirView(QTreeWidget):
    def __init__(self, parent=None, name=None):
        QTreeWidget.__init__(self, parent)
        global folderClosedIcon, folderLockedIcon, folderOpenIcon, fileIcon

        folderClosedIcon = QIcon(QPixmap(folder_closed_image))
        folderLockedIcon = QIcon(QPixmap(folder_locked_image))
        folderOpenIcon = QIcon(QPixmap(folder_open_image))
        fileIcon = QIcon(QPixmap(pix_file_image))

        self.setHeaderLabels(["", "Name"])
        #self.addColumn("Name", 150) # added 150. mark 060303. [bruce then changed 'width=150' to '150' to avoid exception]
            # Calling addColumn() here causes DirView to change size after its parent (MMKit) is shown.
            # I've not been successful figuring out how to control the height of the DirView (QTreeWidget)
            # after adding this column. See comments in MWsemantics._findGoodLocation() for more
            # information about how I compensate for this. Mark 060222.
        #self.setGeometry(QRect(7,-1,191,150))
        self.setMinimumSize(QSize(160,150))
            # Trying to force height to be 150, but addColumn() overrides this.  To see the problem,
            # simply comment out addColumn() above and enter Build mode. mark 060222.
        #self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.sizePolicy().hasHeightForWidth()))
        qt4todo('self.setTreeStepSize(20)')
        qt4todo('self.setColumnWidth(0, 150)') # Force the column width to 150 again. Fixes bug 1613. mark 060303.
            # The only time you'll see bug 1613 is when your partlib path is very long.
            # The column width is set by the width of the partlib path.
            # If you have a short path (i.e. /atom/cad/partlib), you wouldn't notice this bug.
            # A fresh Windows install has its partlib in C:\Program Files\NanoEngineer-1 vx.x.x Alpha\partlib.
            # This was causing the MMKit to be very wide on Windows by default on startup.

        #self.connect(self, SIGNAL("selectionChanged(QTreeWidgetItem *)"), self.partChanged)

    def partChanged(self, item):
        if isinstance(item, FileItem):
            fi = item.getFileObj()
            print "The selected file is: ", str(fi)



########################################################################
# Test code
# Here is the example we find in PyQt-x11-gpl-4.0.1/examples/itemviews/dirview.py

if __name__ == '__main__':
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)

    model = QtGui.QDirModel(['*.mmp', '*.MMP'], QDir.AllEntries|QDir.AllDirs, QDir.Name)
    tree = QtGui.QTreeView()
    tree.setModel(model)
    tree.setRootIndex(model.index('../partlib'))

    tree.setWindowTitle(tree.tr("Dir View"))
    tree.resize(250, 480)
    tree.show()
    for i in range(1,4):
        tree.hideColumn(i)

    sys.exit(app.exec_())


if False and __name__ == '__main__':
    a = QApplication(sys.argv)
    if 1:
        mw = DirView()
        a.setMainWidget(mw)
        mw.setCaption('PyQt Example - Directory Browser')
        mw.resize(400, 400)
        #mw.setSelectionMode(QTreeWidget.Extended)
        root = Directory(mw)#, '/huaicai')
        root.setOpen(1)
        mw.show()
        a.exec_()

    else:
        roots = QDir("/download")
        fiList = roots.entryInfoList()
        for drv in fiList:
            print "The file path is: ", str(drv.absFilePath())
        a.exec_()

# end
