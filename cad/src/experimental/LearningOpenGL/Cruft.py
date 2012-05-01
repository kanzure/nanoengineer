#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
>... anything I'm doing wrong?

Not overriding QGLWidget's necessary methods that draw things,
paintGL, resizeGL, maybe an init method. GLPane shows the way,
so does the smaller ThumbView.

But it's easier and more relevant to NE1 to forget about learning (for now)
to make your own GL context aka QGLWidget, and just use NE1's,
like we did to demo brad's code in selectMode.py,
where if some debug flag is set,
we replace mode.Draw with his own drawing code.

I doubt you need to override anything higher up than mode.Draw,
but if you do, you can add debug flags to GLPane to call your own code
instead of what it now does inside paintGL. Or patch into it at runtime,
like this:

# in your test code
glpane = assy.w.glpane

def mypaintGL(): bla

glpane.paintGL = mypaintGL # this does *not* get the GLPane (self) as arg 1
# but it gets whatever other args paintGL usually gets
"""


import CruftDialog
from qt import *
from qtcanvas import *
from qtgl import *
from OpenGL.GL import *
import numpy
import sys
import random
import time
import foo

class MyGLWidget(QGLWidget):
    def __init__(self, parent, name, shareWidget=None):
        """  """
        if shareWidget:
            self.shareWidget = shareWidget #bruce 051212
            format = shareWidget.format()
            QGLWidget.__init__(self, format, parent, name, shareWidget)
            if not self.isSharing():
                print "Request of display list sharing is failed."
                return
        else:  
            QGLWidget.__init__(self, parent, name)  
        
        # point of view, and half-height of window in Angstroms
        self.pov = Numeric.array((0.0, 0.0, 0.0))
        self.scale = 10.0
        #self.quat = Q(1, 0, 0, 0)

        self.selectedObj = None
        
        # clipping planes, as percentage of distance from the eye
        self.near = 0.66
        self.far = 2.0  
        # start in perspective mode
        self.ortho = False #True
        self.initialised = False
        self.backgroundColor = (0.5, 0.5, 0.5)  # gray
    
    def initializeGL(self):
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        return
    
    def resetView(self):
        '''Subclass can override this method with different <scale>, so call this version in the overridden
           version. '''
        self.pov = Numeric.array((0.0, 0.0, 0.0))
        #self.quat = Q(1, 0, 0, 0)
        
    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
           
        glViewport(0, 0, self.width, self.height)
        
        if not self.initialised:
            self.initialised = True


    def _setup_projection(self, glselect = False): #bruce 050608 split this out; 050615 revised docstring
        """Set up standard projection matrix contents using aspect, vdist, and some attributes of self.
        (Warning: leaves matrixmode as GL_PROJECTION.)
        Optional arg glselect should be False (default) or a 4-tuple (to prepare for GL_SELECT picking).
        """
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        scale = self.scale #bruce 050608 used this to clarify following code
        near, far = self.near, self.far

        if glselect:
            x,y,w,h = glselect
            gluPickMatrix(
                    x,y,
                    w,h,
                    glGetIntegerv( GL_VIEWPORT ) #k is this arg needed? it might be the default...
            )
         
        if self.ortho:
            glOrtho( - scale * self.aspect, scale * self.aspect,
                     - scale,          scale,
                       self.vdist * near, self.vdist * far )
        else:
            glFrustum( - scale * near * self.aspect, scale * near * self.aspect,
                       - scale * near,          scale * near,
                         self.vdist * near, self.vdist * far)
        return
    
    
    def paintGL(self):        
        """Called by QtGL when redrawing is needed.
            For every redraw, color & depth butter are cleared, view projection are reset, view location & orientation are also reset. 
        """
        if not self.initialised: return

        c = self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.aspect = (self.width + 0.0)/(self.height + 0.0)
        self.vdist = 6.0 * self.scale
        self._setup_projection()
        
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()    
        glTranslatef(0.0, 0.0, -self.vdist)
       
        #q = self.quat
        
        #glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glTranslatef(self.pov[0], self.pov[1], self.pov[2])
        
        #self.drawModel()
        foo.foo()




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
        foo.init()
        glformat = QGLFormat()
        glformat.setStencil(True)
        # self.qglwidget = QGLWidget(glformat, self.frame1, "glpane")
        self.qglwidget = MyGLWidget(glformat, self.frame1)
        self.qglwidget.resizeGL(400, 400)

    def pushButton1_clicked(self):
        self.app.quit()

    def __paintEvent(self, e):
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
