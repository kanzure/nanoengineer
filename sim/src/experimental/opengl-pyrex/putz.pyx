# Copyright 2006 Nanorex, Inc.  See LICENSE file for details. 
import math
import qt
import qtgl
import sys
import random

cdef extern from "futz.c":
    # Does OpenGL compel the use of floats, or are doubles OK?
    void line(float x1, float y1, float z1,
              float x2, float y2, float z2,
              float r, float g, float b)
    void sphere(double x, double y, double z,
                double radius,
                double r, double g, double b)
    void glSetup(int windowWidth, int windowHeight)


class GLPane(qtgl.QGLWidget):
    def __init__(self, master=None, name=None, win=None):
        qtgl.QGLWidget.__init__(self, master, name)
        self.win = win
        self.redrawGL = True
        self.setFocusPolicy(qt.QWidget.StrongFocus)
        glSetup(600, 400)
        print "GLPane constructor ran"
        self.update()
    def update(self):
        line(100 * random.random(), 100 * random.random(), 100 * random.random(),
             100 * random.random(), 100 * random.random(), 100 * random.random(),
             random.random(), random.random(), random.random())
        qtgl.QGLWidget.update(self)
    # use self.update to repaint

class MainWindow(qt.QMainWindow):
    def __init__(self):
        qt.QMainWindow.__init__(self)
        self.setEnabled(1)
        self.setOpaqueMoving(0)
        self.glpane = GLPane(self, "glpane", self)
    def show(self):
        self.glpane.show()
        qt.QMainWindow.show(self)


def main():
    qt.QApplication.setColorSpec(qt.QApplication.CustomColor)
    app = qt.QApplication(sys.argv)
    app.connect(app, qt.SIGNAL("lastWindowClosed()"), app.quit)
    win = MainWindow()
    win.show()
