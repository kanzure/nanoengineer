import sys, string
from qt import *
from os import *

TRUE  = 1
FALSE = 0

fileopen = [
'    16    13        5            1',
'. c #040404',
'# c #808304',
'a c None',
'b c #f3f704',
'c c #f3f7f3',
'aaaaaaaaa...aaaa',
'aaaaaaaa.aaa.a.a',
'aaaaaaaaaaaaa..a',
'a...aaaaaaaa...a',
'.bcb.......aaaaa',
'.cbcbcbcbc.aaaaa',
'.bcbcbcbcb.aaaaa',
'.cbcb...........',
'.bcb.#########.a',
'.cb.#########.aa',
'.b.#########.aaa',
'..#########.aaaa',
'...........aaaaa'
]

filenew = [
'16 16 3 1',
'       c None',
'.      c #000000000000',
'X      c #FFFFFFFFFFFF',
'                ',
'   ......       ',
'   .XXX.X.      ',
'   .XXX.XX.     ',
'   .XXX.XXX.    ',
'   .XXX.....    ',
'   .XXXXXXX.    ',
'   .XXXXXXX.    ',
'   .XXXXXXX.    ',
'   .XXXXXXX.    ',
'   .XXXXXXX.    ',
'   .XXXXXXX.    ',
'   .XXXXXXX.    ',
'   .........    ',
'                ',
'                '
]

back = [
'16 16 5 1',
'# c #000000',
'a c #ffffff',
'c c #808080',
'b c #c0c0c0',
'. c None',
'................',
'.......#........',
'......##........',
'.....#a#........',
'....#aa########.',
'...#aabaaaaaaa#.',
'..#aabbbbbbbbb#.',
'...#abbbbbbbbb#.',
'...c#ab########.',
'....c#a#ccccccc.',
'.....c##c.......',
'......c#c.......',
'.......cc.......',
'........c.......',
'................',
'......................']

forward = [
'16 16 5 1',
'# c #000000',
'a c #ffffff',
'c c #808080',
'b c #c0c0c0',
'. c None',
'................',
'................',
'.........#......',
'.........##.....',
'.........#a#....',
'..########aa#...',
'..#aaaaaaabaa#..',
'..#bbbbbbbbbaa#.',
'..#bbbbbbbbba#..',
'..########ba#c..',
'..ccccccc#a#c...',
'........c##c....',
'........c#c.....',
'........cc......',
'........c.......',
'................',
'................']

homes = [
'16 16 4 1',
'# c #000000',
'a c #ffffff',
'b c #c0c0c0',
'. c None',
'........... ....',
'   ....##.......',
'..#...####......',
'..#..#aabb#.....',
'..#.#aaaabb#....',
'..##aaaaaabb#...',
'..#aaaaaaaabb#..',
'.#aaaaaaaaabbb#.',
'###aaaaaaaabb###',
'..#aaaaaaaabb#..',
'..#aaa###aabb#..',
'..#aaa#.#aabb#..',
'..#aaa#.#aabb#..',
'..#aaa#.#aabb#..',
'..#aaa#.#aabb#..',
'..#####.######..',
'................']
mainicon_data = [
"22 22 47 1",
"t c #0065a3",
"z c #0065a4",
"H c #0166a4",
"s c #0266a5",
"C c #0367a5",
"u c #0568a5",
"D c #0568a6",
"L c #0568a7",
"y c #0669a7",
"r c #0769a7",
"v c #0c6ca8",
"G c #0e6da9",
"n c #0f6ea9",
"# c #120906",
"J c #126faa",
"l c #1370aa",
"m c #1470ab",
"K c #1772ab",
"I c #2077ae",
"O c #2278af",
"N c #257aaf",
"B c #297cb0",
"b c #359103",
"k c #3784b5",
"R c #3a86b5",
"o c #3c87b6",
"c c #469903",
"d c #4f9e03",
"e c #5aa403",
"f c #61a702",
"q c #68a0c2",
"g c #68ab01",
"E c #6ea3c4",
"a c #70af00",
"Q c #71a5c5",
"S c #75a7c6",
"M c #87b1cb",
"x c #93b8cf",
"w c #96bacf",
"j c #a3c1d3",
"p c #b0c8d7",
"i c #bdd0da",
"P c #bdd0db",
"F c #bed1db",
"h c #c2d3dc",
"A c #cdd9df",
". c #ffffff",
".....................#",
".....................#",
".aaaaaaaaaaaaaaaaaaa.#",
"..b...aaaaaaaaa......#",
"..c...aaaaaaaaa......#",
"..d...aaaaaaaaa......#",
"..e...aaaaaaaaa......#",
"..f...aaaaaaaaa......#",
"..g......hih.........#",
"..g....jklmnop.......#",
"..g...qrstttuvw......#",
"..g..xyztttttzlA.....#",
".....BCtttttttDE.....#",
"....FGttttttttHI.....#",
"....iJttttttttzK.....#",
"....hGztttttttzB.....#",
".....outttttttLM.....#",
".....pvztttttHN......#",
"......wlDHzHyOP......#",
".......AQRoRS........#",
".....................#",
"######################"
]

class AssistantWindow(QMainWindow):
    def __init__(self,home_,_path,parent=None,name=None,fl=0):
        QMainWindow.__init__(self,parent,name,fl)
#        QMainWindow.__init__(self,parent,name,Qt.WDestructiveClose)
        
#class AssistantWindow(QMainWindow):
#    def __init__(self,parent = None,name = None,fl = 0):
#        QMainWindow.__init__(self,parent,name,fl)
        if name == None:
            self.setName("Help")
            
        self.pathCombo = 0
        self.history = []
        self.bookmarks = []
        self.mHistory = {}
        self.mBookmarks = {}
        self.readHistory()
        self.readBookmarks()
        
        self.mainicon = QPixmap(mainicon_data)
        self.setIcon(self.mainicon)

        self.browser = QTextBrowser(self)

        self.browser.mimeSourceFactory().setFilePath(_path)
        self.browser.setFrameStyle(QFrame.Panel|QFrame.Sunken)
        self.connect(self.browser,SIGNAL('sourceChanged(const QString&)'),self.slotSourceChanged)

        self.setCentralWidget(self.browser)

        if home_ != '':
            self.browser.setSource(home_)

        self.connect(self.browser,SIGNAL('highlighted(const QString&)'),self.statusBar(),SLOT('message(const QString&)'))

        self.resize(1000,650)
        self.setCaption('nanoENGINEER-1 Assistant')

        file = QPopupMenu(self)
        newIcon = QIconSet(QPixmap(filenew))
        file.insertItem(newIcon,'&New Window',self.slotNewWindow,Qt.CTRL+Qt.Key_N)
        openIcon = QIconSet(QPixmap(fileopen))
        file.insertItem(openIcon,'&Open File',self.slotOpenFile,Qt.CTRL+Qt.Key_O)
        file.insertItem('&Print',self.slotPrint,Qt.CTRL+Qt.Key_P)
        file.insertSeparator()
        file.insertItem('&Close',self,SLOT('close()'),Qt.CTRL+Qt.Key_Q)
        file.insertItem('E&xit',qApp,SLOT('closeAllWindows()'),Qt.CTRL+Qt.Key_X)

        backIcon = QIconSet(QPixmap(back))
        forwardIcon = QIconSet(QPixmap(forward))
        homeIcon = QIconSet(QPixmap(homes))

        go = QPopupMenu(self)

        self.backwardId = go.insertItem(backIcon,'&Backward',self.browser,SLOT('backward()'),Qt.CTRL+Qt.Key_Left)
        self.forwardId = go.insertItem(forwardIcon,'&Forward',self.browser,SLOT('forward()'),Qt.CTRL+Qt.Key_Right)
        go.insertItem(homeIcon,'&Home',self.browser,SLOT('home()'))

        help = QPopupMenu(self)
        help.insertItem('&About',self.slotAbout)
        help.insertItem('About &Qt',self.slotAboutQt)

        self.hist = QPopupMenu(self)
        for it in self.history:
            self.mHistory[self.hist.insertItem(it)] = it
        self.connect(self.hist,SIGNAL('activated(int)'),self.slotHistChosen)

        self.bookm = QPopupMenu(self)
        self.bookm.insertItem('Add Bookmark',self.slotAddBookmark)
        self.bookm.insertSeparator()

        for it2 in self.bookmarks:
            self.mBookmarks[self.bookm.insertItem(it2)] = it2
        self.connect(self.bookm,SIGNAL('activated(int)'),self.slotBookmChosen)

        self.menuBar().insertItem('&File',file)
        self.menuBar().insertItem('&Go',go)
        self.menuBar().insertItem('History',self.hist)
        self.menuBar().insertItem('Bookmarks',self.bookm)
        self.menuBar().insertSeparator()
        self.menuBar().insertItem('&Help',help)

        self.menuBar().setItemEnabled(self.forwardId,FALSE)
        self.menuBar().setItemEnabled(self.backwardId,FALSE)

        self.connect(self.browser,SIGNAL('backwardAvailable(bool)'),self.setBackwardAvailable)
        self.connect(self.browser,SIGNAL('forwardAvailable(bool)'),self.setForwardAvailable)

        toolbar = QToolBar(self)

        button = QToolButton(backIcon,'Backward','',self.browser,SLOT('backward()'),toolbar)
        self.connect(self.browser,SIGNAL('backwardAvailable(bool)'),button,SLOT('setEnabled(bool)'))
        button.setEnabled(FALSE)
        button = QToolButton(forwardIcon,'Forward','',self.browser,SLOT('forward()'),toolbar)
        self.connect(self.browser,SIGNAL('forwardAvailable(bool)'),button,SLOT('setEnabled(bool)'))
        button.setEnabled(FALSE)
        button = QToolButton(homeIcon,'Home','',self.browser,SLOT('home()'),toolbar)

        toolbar.addSeparator()

        self.pathCombo = QComboBox(TRUE,toolbar)
        self.connect(self.pathCombo,SIGNAL('activated(const QString&)'),self.slotPathSelected)
        toolbar.setStretchableWidget(self.pathCombo)
        self.setRightJustification(TRUE)
        self.setDockEnabled(Qt.DockLeft,FALSE)
        self.setDockEnabled(Qt.DockRight,FALSE)

        self.pathCombo.insertItem(home_)
        self.browser.setFocus()

    def setBackwardAvailable(self,b):
        self.menuBar().setItemEnabled(self.backwardId,b)

    def setForwardAvailable(self,b):
        self.menuBar().setItemEnabled(self.forwardId,b)

    def slotSourceChanged(self,url):
        if self.browser.documentTitle().isNull():
            self.setCaption('nanoENGINEER-1 Assistant' + url)
        else:
            self.setCaption('nanoENGINEER-1 Assistant - ' + str(self.browser.documentTitle()))

        if not url.isEmpty()and self.pathCombo:
            exists = FALSE
            for i in range(self.pathCombo.count()):
                if str(self.pathCombo.text(i)) == str(url):
                    exists = TRUE
                    break
            if exists == FALSE:
                self.pathCombo.insertItem(url,0)
                self.pathCombo.setCurrentItem(0)
                self.mHistory[self.hist.insertItem(url)] = str(url)
            else:
                self.pathCombo.setCurrentItem(i)

    def __del__(self):
        history = self.mHistory
        f = QFile(str(QDir.currentDirPath()) + '/.history')
        f.open(IO_WriteOnly)
        for it in history.keys():
            f.writeBlock(history[it] + '\n')
        f.close()

        bookmarks = self.mBookmarks
        f2 = QFile(str(QDir.currentDirPath()) + '/.bookmarks')
        f2.open(IO_WriteOnly)
        for it in bookmarks.keys():
            f2.writeBlock(bookmarks[it] + '\n')
        f2.close()


    def slotAbout(self):
        QMessageBox.about(self,'HelpViewer Example','''
                        <p>This example implements a simple HTML help viewer
                        using PyQt's rich text capabilities</p>
                        <p>It's just about 100 lines of Python code, so don't expect too much :-)</p>''')

    def slotAboutQt(self):
        QMessageBox.aboutQt(self,'QBrowser')

    def slotOpenFile(self):
        fn = QFileDialog.getOpenFileName('','',self)
        if not fn.isEmpty():
            self.browser.setSource(fn)

    def slotNewWindow(self):
        self.w = AssistantWindow(self.browser.source(),QStringList('qbrowser'))
        self.w.show()

    def slotPrint(self):
        printer = QPrinter()
        printer.setFullPage(TRUE)
        if printer.setup(self):
            p = QPainter(printer)
            metrics = QPaintDeviceMetrics(p.device())
            dpix = metrics.logicalDpiX()
            dpiy = metrics.logicalDpiY()
            margin = 72
            body = QRect(margin*dpix/72,margin*dpiy/72,metrics.width()-margin*dpix/72*2,metrics.height()-margin*dpiy/72*2)
            richText = QSimpleRichText(self.browser.text(),QFont(),self.browser.context(),self.browser.styleSheet(),self.browser.mimeSourceFactory(),body.height())
            richText.setWidth(p,body.width())
            view = QRect(body)
            page = 1
            while TRUE:
                richText.draw(p,body.left(),body.top(),view,self.colorGroup())
                view.moveBy(0,body.height())
                p.translate(0,-body.height())
                p.drawText(view.right()-p.fontMetrics().width(str(page)),view.bottom()+p.fontMetrics().ascent()+5,str(page))
                if view.top() >= richText.height():
                    break
                printer.newPage()
                page = page + 1
            p.end()

    def slotPathSelected(self,_path):
        _path = str(_path)
        self.browser.setSource(_path)
        for i in self.mHistory.keys():
            if self.mHistory[i] == _path:
                self.mHistory[self.hist.insertItem(_path)] = _path

    def readHistory(self):
        if QFile.exists(str(QDir.currentDirPath()) + '/.history'):
            f = QFile(str(QDir.currentDirPath()) + '/.history')
            f.open(IO_ReadOnly)
            while not f.atEnd():
                s = QString()
                f.readLine(s,10000)
                s = str(s)
                self.history.append(str(s[:-1]))
            f.close()

    def readBookmarks(self):
        if QFile.exists(str(QDir.currentDirPath()) + '/.bookmarks'):
            f = QFile(str(QDir.currentDirPath()) + '/.bookmarks')
            f.open(IO_ReadOnly)
            while not f.atEnd():
                s = QString()
                f.readLine(s,10000)
                s = str(s)
                self.bookmarks.append(str(s[:-1]))
            f.close()

    def slotHistChosen(self,i):
        for it in self.mHistory.keys():
            if str(it) == str(i):
                self.browser.setSource(self.mHistory[it])

    def slotBookmChosen(self,i):
        for it in self.mBookmarks.keys():
            if str(it) == str(i):
                self.browser.setSource(self.mBookmarks[it])

    def slotAddBookmark(self):
        self.mBookmarks[self.bookm.insertItem(self.caption())] = str(self.browser.context())

if __name__=='__main__':
    QApplication.setColorSpec(QApplication.CustomColor)
    app=QApplication(sys.argv)

    nedirenv = environ['NE1DIR']
    if nedirenv != None:
        home = nedirenv + '/cad/doc/html/index.html'

#    foo = AssistantWindow()
    foo = AssistantWindow(home,QStringList('.'),None,'help viewer')
    if QApplication.desktop().width() > 1000 and QApplication.desktop().height() > 650:
        foo.show()
    else:
        foo.showMaximized()

    QObject.connect(app,SIGNAL('lastWindowClosed()'),app,SLOT('quit()'))

    app.exec_loop()