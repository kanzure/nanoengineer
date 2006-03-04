# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
"""
General directory view widget. Based on Qt example dirview. 

$Id$
"""

import sys
from qt import *

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

class FileItem(QListViewItem):
    def __init__(self, parent, fio, name=None):
        apply(QListViewItem.__init__, (self, parent))#, name))
        
        self.f = name
        self.fileObj = fio
    
    def getFileObj(self):
        return self.fileObj
    
    def text(self, column):
        if column == 0:
            return self.f
    
    #def setup(self):
    #    self.setExpandable(1)
    #    QListViewItem.setup(self)
        

class Directory(QListViewItem):
    
    def __init__(self, parent, name=None):
        apply(QListViewItem.__init__,(self,parent, name))
        
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
            self.setPixmap(0, folderLockedIcon )
        else:
            self.setPixmap(0, folderClosedIcon )

        

    def setOpen(self, o):
        if  o: 
            self.setPixmap(0, folderOpenIcon )
        else:
            self.setPixmap(0, folderClosedIcon )

        if o and not self.childCount():
            s = self.fullName()
            thisDir = QDir(s)
            if not thisDir.isReadable():
                self.readable = 0
                return

            files = thisDir.entryInfoList()
            if files:
                for f in files:
                    fileName = str(f.fileName())
                    if fileName == '.' or fileName == '..':
                        continue
                    elif f.isSymLink():
                        d = QListViewItem(self, fileName)#, 'Symbolic Link')
                        d.setPixmap(0, fileIcon)
                    elif f.isDir():
                        d = Directory(self, fileName)
                    else:
                        if f.isFile():
                            s = 'File'
                        else:
                            s = 'Special'
                        if not fileName[-3:] in self.filterList: continue
                        d = FileItem(self, f.absFilePath(), fileName)
                        d.setPixmap(0, fileIcon)
    
        QListViewItem.setOpen(self, o)


    def setup(self):
        self.setExpandable(1)
        QListViewItem.setup(self)


    def fullName(self):
        if self.p:
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

class DirView(QListView):
    def __init__(self, parent=None, name=None):
        QListView.__init__(self, parent, name) 
        global folderClosedIcon, folderLockedIcon, folderOpenIcon, fileIcon

        folderClosedIcon = QPixmap(folder_closed_image)
        folderLockedIcon = QPixmap(folder_locked_image)
        folderOpenIcon = QPixmap(folder_open_image)
        fileIcon = QPixmap(pix_file_image)

        self.addColumn("Name", 150) # May fix bug 1613. mark 060303. [bruce then changed 'width=150' to '150' to avoid exception]
            # Calling addColumn() here causes DirView to change size after its parent (MMKit) is shown.
            # I've not been successful figuring out how to control the height of the DirView (QListView) 
            # after adding this column. See comments in MWsemantics._findGoodLocation() for more 
            # information about how I compensate for this. Mark 060222.
        #self.setGeometry(QRect(7,-1,191,150))
        self.setMinimumSize(QSize(160,150)) 
            # Trying to force height to be 150, but addColumn() overrides this.  To see the problem,
            # simply comment out addColumn() above and enter Build mode. mark 060222.
        #self.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding,QSizePolicy.MinimumExpanding,0,0,self.sizePolicy().hasHeightForWidth()))
        self.setTreeStepSize(20)
        self.setColumnWidth(0, 150) # Force the column width to 150 again. May fix bug 1613. mark 060303.
        
        #self.connect(self, SIGNAL("selectionChanged(QListViewItem *)"), self.partChanged)
        
    def partChanged(self, item):
        if isinstance(item, FileItem):
            fi = item.getFileObj()
            print "The selected file is: ", str(fi)
    
    
    
# Test code
if __name__ == '__main__':
    a = QApplication(sys.argv)
    if 1:
        mw = DirView()
        a.setMainWidget(mw)
        mw.setCaption('PyQt Example - Directory Browser')
        mw.resize(400, 400)
        #mw.setSelectionMode(QListView.Extended)
        root = Directory(mw)#, '/huaicai')
        root.setOpen(1)
        mw.show()
        a.exec_loop()
    
    else:
        roots = QDir("/download")
        fiList = roots.entryInfoList()
        for drv in fiList:
            print "The file path is: ", str(drv.absFilePath())
        a.exec_loop()