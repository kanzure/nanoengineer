from qt import *

class modelTree(QListView):
    def __init__(self,parent):
        QListView.__init__(self,parent,"modelTreeView")
        self.addColumn("Model Tree")
        
        self.header().setClickEnabled(0,self.header().count() - 1)
        self.setGeometry(QRect(0,0,131,560))
        self.setSizePolicy(QSizePolicy(0,7,0,244,False))
        self.setResizePolicy(QScrollView.Manual)
        self.setShowSortIndicator(0)
