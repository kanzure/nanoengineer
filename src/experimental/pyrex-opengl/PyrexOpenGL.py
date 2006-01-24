#!/usr/bin/python

from PyrexOpenGLGui import *
from qt import *
from qtgl import QGLWidget, QGLFormat
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import quux
import sys
import random
import time

USE_OPENGL = True

class MyGLWidget(QGLWidget):

    def __init__(self, master=None, name=None, win=None):
        self.win = win
        QGLWidget.__init__(self, QGLFormat(), master, name)

    def gl_update(self):
        self.update()

    def paintGL(self):
        quux.test()
        self.drawSquares()

    def drawSquares(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glColor3f(1.0, 1.0, 1.0)
        glOrtho(-1.0, 1.0,
                -1.0, 1.0,
                -1.0, 1.0) 
        glBegin(GL_POLYGON)
        glVertex2f(-0.5, -0.5)
        glVertex2f(-0.5, 0.5)
        glVertex2f(0.5, 0.5)
        glVertex2f(0.5, -0.5)
        glEnd()
        glFlush()



class PyrexOpenGL(PyrexOpenGLGui):

    ANIMATION_DELAY = 1000   # milliseconds
    COLOR_CHOICES = (
        QColor(Qt.red), QColor(Qt.yellow),
        QColor(Qt.green), QColor(Qt.blue)
        )

    def __init__(self, parent=None, name=None, modal=0, fl=0):
        PyrexOpenGLGui.__init__(self,parent,name,modal,fl)
        if USE_OPENGL:
            self.glthing = MyGLWidget(self.frame1, "glthing", self)
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
        if USE_OPENGL:
            self.glthing.update()
        else:
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
            p.end()

def main():
    app = QApplication(sys.argv)
    cr = PyrexOpenGL()
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    main()
