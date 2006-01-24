#!/usr/bin/python

"""Use designer-qt3 to tweak cruft.ui. Then run
pyuic cruft.ui > cruft.py
"""

from cruft import *
from qt import *
from qtcanvas import *
import sys
import random
import time

class Crufty(Form1):
    ANIMATION_DELAY = 100   # milliseconds
    def __init__(self,parent = None,name = None,modal = 0,fl = 0):
        Form1.__init__(self,parent,name,modal,fl)
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.timeout)
        self.lastTime = time.time()
        self.timer.start(self.ANIMATION_DELAY)

    def pushButton1_clicked(self):
        self.app.quit()

    def timeout(self):
        self.paintEvent(None)
        self.timer.start(self.ANIMATION_DELAY)

    def paintEvent(self, e):
        p = QPainter()
        size = self.frame1.size()
        w, h = size.width(), size.height()
        p.begin(self.frame1)
        p.eraseRect(0, 0, w, h)
        for i in range(50):
            r = random.random()
            if r < 0.25:
                p.setPen(QPen(Qt.yellow))
            elif r < 0.5:
                p.setPen(QPen(Qt.red))
            elif r < 0.75:
                p.setPen(QPen(Qt.green))
            else:
                p.setPen(QPen(Qt.blue))
            x1 = w * random.random()
            y1 = h * random.random()
            x2 = w * random.random()
            y2 = h * random.random()
            p.drawLine(x1, y1, x2, y2)
        p.flush()
        p.end()

def main():
    app = QApplication(sys.argv)
    cr = Crufty()
    app.setName("howdy")
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    main()
