# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
cdef extern from "comphelp.c":
    setup(int n)
    internalForces(double stiffness, double viscosityOverDt, double dtm)
    verletMomentum()
    applyForces(forces, double dtm)
    draw(drawCallback, int w, int h)
    rotate()

def _setup(n):
    setup(n)

def _internalForces(stiffness, viscOverDt, dtm):
    internalForces(stiffness, viscOverDt, dtm)

def _verletMomentum():
    verletMomentum()

def _applyForces(forces, dtm):
    applyForces(forces, dtm)

def _draw(cb, w, h):
    return draw(cb, w, h)

def _rotate():
    return rotate()
