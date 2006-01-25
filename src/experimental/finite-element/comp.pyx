cdef extern from "comphelp.c":
    setup(computronium, int n)
    internalForces(double stiffness, double viscosityOverDt, double dtm)
    verletMomentum()
    applyForces(forces, double dtm)

def _setup(computronium, n):
    setup(computronium, n)

def _internalForces(stiffness, viscOverDt, dtm):
    internalForces(stiffness, viscOverDt, dtm)

def _verletMomentum():
    verletMomentum()

def _applyForces(forces, dtm):
    applyForces(forces, dtm)
