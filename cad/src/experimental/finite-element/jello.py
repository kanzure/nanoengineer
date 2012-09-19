#!/usr/bin/python

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
from jelloGui import *
import sys
import random
import time
import types
import string
from math import cos, sin, sqrt

PROFILING = True
if PROFILING:
    import hotshot, hotshot.stats

GOT_PYREX = False
try:
    import comp
    GOT_PYREX = True
except ImportError:
    pass

N = 4

# milliseconds
ANIMATION_DELAY = 50

"""I think this is the correct way to
scale stiffness and viscosity.
"""
RADIUS = 15 / N**.5
MASS = 3.0e-6 / N**2
DT = 3.0e-3
STIFFNESS = 1.0e-8 * N
VISCOSITY = 3.0e-9 * N
DTM = (DT ** 2) / MASS
TIME_STEP = 0.2
MAXTIME = 1.0e20

A = 3.0e-8

def addvec(u, v):
    return (u[0] + v[0], u[1] + v[1])
def subvec(u, v):
    return (u[0] - v[0], u[1] - v[1])
def scalevec(u, k):
    return (u[0] * k, u[1] * k)

# Keep the old, current and new versions of u
# in here, along with x.
class Computronium:
    def __init__(self, owner):
        self.owner = owner
        self.u = u = N**2 * [ (0.0, 0.0) ]
        self.u_old = N**2 * [ (0.0, 0.0) ]
        self.u_new = N**2 * [ (0.0, 0.0) ]
        self.x = x = [ ]  # nominal positions
        for i in range(N):
            for j in range(N):
                x.append((1. * j / N,
                          1. * i / N))
        self.forceTerms = [ ]
        # set up the force terms
        for i in range(N):
            for j in range(N - 1):
                self.forceTerms.append((i * N + j,
                                        i * N + j + 1))
        for i in range(N - 1):
            for j in range(N):
                self.forceTerms.append((i * N + j,
                                        (i + 1) * N + j))
        self.simTime = 0.0

    def internalForces(self):
        forces = self.zeroForces()
        u, o = self.u, self.u_old
        for i1, i2 in self.forceTerms:
            D = subvec(u[i2], u[i1]) # relative displacement
            P = subvec(o[i2], o[i1]) # previous relative displacement
            f = addvec(scalevec(D, STIFFNESS),
                       scalevec(subvec(D, P), VISCOSITY / DT))
            forces[i1] = addvec(forces[i1], f)
            forces[i2] = subvec(forces[i2], f)
        self.applyForces(forces)

    def verletMomentum(self):
        self_u, self_uold, self_unew = self.u, self.u_old, self.u_new
        for i in range(N**2):
                self_unew[i] = subvec(scalevec(self_u[i], 2),
                                      self_uold[i])

    def applyForces(self, f):
        self_unew = self.u_new
        index = 0
        for i in range(N**2):
            unew = self_unew[i]
            fi = f[i]
            self_unew[i] = (unew[0] + DTM * fi[0],
                            unew[1] + DTM * fi[1])

    def zeroForces(self):
        return N**2 * [ (0.0, 0.0) ]

    def draw(self, cb, h, w):
        # x is nominal position
        # u is displacement
        p = [ ]
        a = 0.6
        b = .5 * (1 - a)
        for i in range(N**2):
            xvec = self.x[i]
            uvec = self.u[i]
            cb(h * (a * (xvec[0] + uvec[0]) + b),
               w * (a * (xvec[1] + uvec[1]) + b))

    def rotate(self):
        tmp = self.u_old
        self.u_old = self.u
        self.u = self.u_new
        self.u_new = tmp


if GOT_PYREX:
    # Keep the old, current and new versions of u
    # in here, along with x.
    class ComputroniumWithPyrex(Computronium):
        def __init__(self, owner):
            self.owner = owner
            comp._setup(N)

        def internalForces(self):
            comp._internalForces(STIFFNESS, VISCOSITY/DT, DTM)

        def verletMomentum(self):
            comp._verletMomentum()

        def applyForces(self, f):
            comp._applyForces(f, DTM)

        def draw(self, cb, h, w):
            return comp._draw(cb, h, w)

        def rotate(self):
            return comp._rotate()

    Computronium = ComputroniumWithPyrex


class Jello(JelloGui):

    COLOR_CHOICES = (
        QColor(Qt.red), QColor(Qt.yellow),
        QColor(Qt.green), QColor(Qt.blue)
        )

    def __init__(self):
        JelloGui.__init__(self, parent=None, name=None, modal=0, fl=0)
        size = self.frame1.size()
        self.width, self.height = size.width(), size.height()
        self.comp = Computronium(self)

        self.simTime = 0.0

        self.timer = QTimer(self)
        self.connect(self.timer, SIGNAL('timeout()'), self.timeout)
        self.lastTime = time.time()
        self.timer.start(ANIMATION_DELAY)

        self.push = self.comp.zeroForces()
        for i in range(N/2):
            f = A * (.5*N - i) / (.5*N)
            self.push[i] = (-f, f)
            self.push[N*N-1 - i] = (f, -f)
        self.painter = QPainter()

    def pushButton1_clicked(self):
        self.quit()

    def quit(self):
        self.app.quit()

    def timeout(self):
        try:
            self.oneFrame()
        except AssertionError, e:
            import traceback
            traceback.print_exc()
            self.quit()
        if self.simTime > MAXTIME:
            self.app.quit()

    def oneFrame(self):
        # On each step we do verlet, using u_old and u to compute
        # u_new. Then we move each particle from u to u_new. Then
        # we move u to u_old, and u_new to u.
        for i in range(int(TIME_STEP / DT)):
            self.equationsOfMotion()
        self.paintEvent(None)

    def paintEvent(self, e):
        p = self.painter
        w, h = self.width, self.height
        p.begin(self.frame1)
        p.eraseRect(0, 0, w, h)
        p.setPen(QPen(Qt.black))
        p.setBrush(QBrush(Qt.blue))
        def draw(x, y, de=p.drawEllipse, r=RADIUS):
            de(x, y, r, r)
        #self.comp.draw(draw, w, h)
        self.comp.draw(draw, h, h)
        p.end()

    def equationsOfMotion(self):
        comp = self.comp
        t = self.simTime
        self.simTime += DT
        pushTime = 1.0
        comp.verletMomentum()
        comp.internalForces()
        if t < pushTime:
            comp.applyForces(self.push)
        comp.rotate()

def main(n, maxTime=1.0e20):
    global N, RADIUS, MAXTIME
    N = n
    RADIUS = 15 / n**.5
    MAXTIME = maxTime
    app = QApplication(sys.argv)
    cr = Jello()
    cr.app = app
    app.setMainWidget(cr)
    cr.show()
    cr.update()
    app.exec_loop()

if __name__ == "__main__":
    if PROFILING:
        prof = hotshot.Profile("jello.prof")
        def m():
            main(4, maxTime=30.0)
        prof.runcall(m)
        prof.close()
        print 'Profiling run is finished, figuring out stats'
        stats = hotshot.stats.load("jello.prof")
        stats.strip_dirs()
        stats.sort_stats('time', 'calls')
        stats.print_stats(20)
        sys.exit(0)
    try:
        n = string.atoi(sys.argv[1])
    except:
        n = 10
    main(n)
