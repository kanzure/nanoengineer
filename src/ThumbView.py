# Copyright (c) 2004 Nanorex, Inc.  All rights reserved.
'''
ThumbView.py

$Id$
'''

from qtgl import *
from OpenGL.GL import *
from VQT import *
import drawer


class ThumbView(QGLWidget):
    """A simple version of OpenGL widget, which can be used to show a simple thumb view of models when loading models or color changing. The display list sharing between 2 QGLWidgets seems to cause the water surface opaque problems(not completely sure), so don't use sharing temporarily, we'll investigate further.---Huaicai
    """ 
    def __init__(self, parent, name, shareWidget):
        """  """
        if shareWidget:
            QGLWidget.__init__(self, parent, name, shareWidget)
            #if not self.isSharing():
            #    print "Request of display list sharing is failed."
            #    return
        else:  QGLWidget.__init__(self, parent, name)  
        
        # point of view, and half-height of window in Angstroms
        self.pov = V(0.0, 0.0, 0.0)
        self.scale = 10.0
        self.quat = Q(1, 0, 0, 0)

        # clipping planes, as percentage of distance from the eye
        self.near = 0.66
        self.far = 2.0  
        # start in perspective mode
        self.ortho = False #True
        self.initialised = False

        
    def initializeGL(self):
        """set up lighting in the model, which is the same as that in GLPane, so we can reproduce the same shading affect.
        """
        glEnable(GL_NORMALIZE)
        glLightfv(GL_LIGHT0, GL_POSITION, (-50, 70, 30, 0))
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.3, 0.3, 0.3, 1.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (0.8, 0.8, 0.8, 1.0))
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightfv(GL_LIGHT1, GL_POSITION, (-20, 20, 20, 0))
        glLightfv(GL_LIGHT1, GL_AMBIENT, (0.4, 0.4, 0.4, 1.0))
        glLightfv(GL_LIGHT1, GL_DIFFUSE, (0.4, 0.4, 0.4, 1.0))
        glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, 1.0)
        glLightfv(GL_LIGHT2, GL_POSITION, (0, 0, 100, 0))
        glLightfv(GL_LIGHT2, GL_AMBIENT, (1.0, 1.0, 1.0, 1.0))
        glLightfv(GL_LIGHT2, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
        glLightf(GL_LIGHT2, GL_CONSTANT_ATTENUATION, 1.0)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glDisable(GL_LIGHT2)
        glShadeModel(GL_SMOOTH)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        self.backgroundColor = (0.7, 0.66, 0.73)#(216/255.0, 213/255.0, 159/255.0)
        #if not self.isSharing():
        drawer.setup()  
        
    def resizeGL(self, width, height):
        """Called by QtGL when the drawing window is resized.
        """
        self.width = width
        self.height = height
           
        glViewport(0, 0, self.width, self.height)
           
        if not self.initialised:
            self.initialised = True
 
    def paintGL(self):        
        """Called by QtGL when redrawing is needed.
            For every redraw, color & depth butter are cleared, view projection are reset, view location & orientation are also reset. 
        """
        if not self.initialised: return
        
        c=self.backgroundColor
        glClearColor(c[0], c[1], c[2], 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()

        aspect = (self.width + 0.0)/(self.height + 0.0)
       
        vdist = 6.0 * self.scale
                
        if self.ortho:
            glOrtho(-self.scale*aspect, self.scale*aspect, -self.scale, self.scale, vdist*self.near, vdist*self.far)
        else:
            glFrustum(-self.scale*aspect*self.near, self.scale*aspect*self.near, -self.scale*self.near, self.scale*self.near, vdist*self.near, vdist*self.far)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()    
        glTranslatef(0.0, 0.0, - vdist)
       
        q = self.quat
        
        glRotatef(q.angle*180.0/pi, q.x, q.y, q.z)
        glTranslatef(self.pov[0], self.pov[1], self.pov[2])
        
        self.drawModel()
   
        
    def drawModel(self):
        """This is abstract method of drawing models, subclass should overwrite it with concrete model drawing statements """        
        pass
        
   