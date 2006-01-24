#!/usr/bin/python

"""This is a demonstration of some very simple Qt ideas. Qt is so
complicated that you can't just sit down and write a GUI like you
could in Java or Tkinter. You need to start in Qt Designer.

Use designer-qt3 to tweak cruft.ui. Then run
pyuic cruft.ui > cruft.py    or just    make cruft.py
to produce a class that gets inherited by Crufty.

Qt Designer won't do everything you want. You sometimes need to
manually edit the XML in cruft.ui to accomplish things that it can't
do.


"""

from cruft import *
from qt import *
from qtcanvas import *
import sys
import random
import time

class Crufty(Cruft):

    ANIMATION_DELAY = 30   # milliseconds
    COLOR_CHOICES = (
        QColor(Qt.red), QColor(Qt.yellow),
        QColor(Qt.green), QColor(Qt.blue)
        )

    def __init__(self, parent=None, name=None, modal=0, fl=0):
        Cruft.__init__(self,parent,name,modal,fl)
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
        """Draw a colorful collection of lines and circles.
        """
        p = QPainter()
        size = self.frame1.size()
        w, h = size.width(), size.height()
        p.begin(self.frame1)
        p.eraseRect(0, 0, w, h)
        for i in range(100):
            color = random.choice(self.COLOR_CHOICES)
            p.setPen(QPen(color))
            p.setBrush(QBrush(color))
            x1 = w * random.random()
            y1 = h * random.random()
            if random.random() < 0.5:
                x2 = w * random.random()
                y2 = h * random.random()
                p.drawLine(x1, y1, x2, y2)
            else:
                x2 = 0.05 * w * random.random()
                y2 = x2
                p.drawEllipse(x1, y1, x2, y2)
        p.flush()
        p.end()

def main():
    app = QApplication(sys.argv)
    cr = Crufty()
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    main()
