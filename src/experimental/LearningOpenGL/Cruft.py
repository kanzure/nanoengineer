#!/usr/bin/python

import CruftDialog
from qt import *
from qtcanvas import *
from qtgl import *
import OpenGL
import sys
import random
import time
import foo

class Cruft(CruftDialog.CruftDialog):

    ANIMATION_DELAY = 50   # milliseconds
    COLOR_CHOICES = (
        # Wonder Bread builds strong bodies twelve ways.
        # Oh wait, now these are the eBay colors.
        QColor(Qt.red), QColor(Qt.yellow),
        QColor(Qt.green), QColor(Qt.blue)
        )

    def __init__(self, parent=None, name=None, modal=0, fl=0):
        CruftDialog.CruftDialog.__init__(self,parent,name,modal,fl)
        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.timeout)
        self.lastTime = time.time()
        self.timer.start(self.ANIMATION_DELAY)
        glformat = QGLFormat()
        glformat.setStencil(True)
        self.qglwidget = QGLWidget(glformat, self.frame1, "glpane")
        # Try to get some control over rectangle size and shape?
        #self.qglwidget.initializeOverlayGL()
        #self.qglwidget.resizeOverlayGL(200, 200)
        foo.init()

    def pushButton1_clicked(self):
        self.app.quit()

    def timeout(self):
        self.paintEvent(None)
        self.timer.start(self.ANIMATION_DELAY)

    def paintEvent(self, e):
        """Draw a colorful collection of lines and circles.
        """
        foo.foo()
        if False:
            print 'paintEvent',
            sys.stdout.flush()
        if False:
            # Here is how to draw stuff using PyQt
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
    cr = Cruft()
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    main()
