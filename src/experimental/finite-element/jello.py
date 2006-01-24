#!/usr/bin/python

from jelloGui import *
from qt import *
from qtcanvas import *
import sys
import random
import time
import Numeric
from math import cos, sin

MASS = 1.0e-7
DT = 1.0e-3
STIFFNESS = 1.0e-5
VISCOSITY = 1.0e-7

class ForceTerm:
    def __init__(self, index1, index2, grid):
        self.index1 = index1
        self.index2 = index2
        self.grid = grid
    def compute(self, forces):
        i1, i2 = self.index1, self.index2
        g = self.grid
        u1, u2 = g.u[i1], g.u[i2]
        o1, o2 = g.u_old[i1], g.u_old[i2]
        Dx, Dy = u2[0] - u1[0], u2[1] - u1[1]
        Px, Py = o2[0] - o1[0], o2[1] - o1[1]
        fx = STIFFNESS * Dx + VISCOSITY * (Dx - Px) / DT
        fy = STIFFNESS * Dy + VISCOSITY * (Dy - Py) / DT
        f1x, f1y = forces[i1]
        f2x, f2y = forces[i2]
        forces[i1] = (f1x + fx, f1y + fy)
        forces[i2] = (f2x - fx, f2y - fy)

class Jello(JelloGui):

    ANIMATION_DELAY = 20   # milliseconds
    COLOR_CHOICES = (
        QColor(Qt.red), QColor(Qt.yellow),
        QColor(Qt.green), QColor(Qt.blue)
        )

    def __init__(self, side=5):
        JelloGui.__init__(self, parent=None, name=None, modal=0, fl=0)
        size = self.frame1.size()
        self.width, self.height = size.width(), size.height()
        self.forceTerms = [ ]

        self.side = side
        self.u_old = [ ]  # displacement
        self.u_new = [ ]  # displacement
        self.u = u = [ ]  # displacement
        self.x = x = [ ]  # nominal positions
        for i in range(side):
            for j in range(side):
                xi, yi = 1. * i / side, 1. * j / side
                self.u_old.append((0., 0.))
                self.u_new.append((0., 0.))
                u.append((0., 0.))
                x.append((xi, yi))
        # set up the force terms
        for i in range(side):
            for j in range(side - 1):
                index1 = i * side + j
                index2 = i * side + j + 1
                self.forceTerms.append(ForceTerm(index1, index2, self))
        for i in range(side - 1):
            for j in range(side):
                index1 = i * side + j
                index2 = (i + 1) * side + j
                self.forceTerms.append(ForceTerm(index1, index2, self))
        self.simTime = 0.0

        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.timeout)
        self.lastTime = time.time()
        self.timer.start(self.ANIMATION_DELAY)



    def pushButton1_clicked(self):
        self.app.quit()

    def timeout(self):
        self.oneFrame()
        self.timer.start(self.ANIMATION_DELAY)

    def oneFrame(self):
        # On each step we do verlet, using u_old and u to compute
        # u_new. Then we move each particle from u to u_new. Then
        # we move u to u_old, and u_new to u.
        for i in range(1):
            self.equationsOfMotion()
            tmp = self.u_old
            self.u_old = self.u
            self.u = self.u_new
            self.u_new = tmp
        self.paintEvent(None)

    def paintEvent(self, e):
        """Draw a colorful collection of lines and circles.
        """
        p = QPainter()
        n, w, h = self.side, self.width, self.height
        self_x, self_u = self.x, self.u
        p.begin(self.frame1)
        p.eraseRect(0, 0, w, h)
        p.setPen(QPen(Qt.black))
        p.setBrush(QBrush(Qt.blue))
        w3, h3 = w / 3, h / 3
        index = 0
        for i in range(n):
            for j in range(n):
                xvec = self_x[index]
                uvec = self_u[index]
                #x = w3 * (xvec[0] + uvec[0] + 1)
                x = h3 * (xvec[0] + uvec[0] + 1)
                y = h3 * (xvec[1] + uvec[1] + 1)
                p.drawEllipse(x, y, w/50, w/50)
                index += 1
        p.flush()
        p.end()

    def equationsOfMotion(self):
        A = 3.0e-6
        n = self.side
        t = self.simTime
        self.simTime += DT
        DTM = (DT ** 2) / MASS
        # zero the forces
        forces = (n * n) * [ (0.0, 0.0) ]
        # apply external forces
        forceTime = 0.1
        if t > 0 and t < forceTime:
            forces[0] = (A, -A)
            forces[n*(n-1)] = (A, A)
        elif t > 2.0 and t < 2.0 + forceTime:
            forces[-1] = (-A, A)
            forces[n-1] = (-A, -A)
            pass
        # compute internal forces  (opportunity for speed-up)
        for ft in self.forceTerms:
            ft.compute(forces)
        self_u, self_uold, self_unew = self.u, self.u_old, self.u_new
        # iterate Verlet   (opportunity for speed-up)
        index = 0
        for i in range(n):
            for j in range(n):
                uvec = self_u[index]
                uold = self_uold[index]
                unew = (2*uvec[0] - uold[0], 2*uvec[1] - uold[1])
                fi = forces[index]
                self_unew[index] = (unew[0] + DTM * fi[0],
                                    unew[1] + DTM * fi[1])
                index += 1

def main():
    app = QApplication(sys.argv)
    cr = Jello(4)
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    main()
