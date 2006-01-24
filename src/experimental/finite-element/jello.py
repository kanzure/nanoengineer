from Tkinter import *
import random
from math import cos, sin

MASS = 1.0e-7
DT = 1.0e-3
STIFFNESS = 1.0e-5
VISCOSITY = 3.0e-8

class ForceTerm:
    def __init__(self, index1, index2, grid):
        self.index1 = index1
        self.index2 = index2
        self.grid = grid
        #self.previousDiff = (0.0, 0.0)
    def compute(self, forces):
        # get the previous diff
        #Px, Py = self.previousDiff
        # find the current diff
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
        #self.previousDiff = (Dx, Dy)

class FiniteElementGrid:
    def __init__(self, side=3):
        self.tk = tk = Tk()
        self.canvas = canvas = Canvas(tk, width=400, height=400)
        canvas.pack()
        width, height = tk.getint(canvas['width']), \
                        tk.getint(canvas['height'])
        self.width, self.height = width, height
        self.particles = particles = [ ]
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
                wx, wy = ((width / 3.) * (xi + 1),
                          (height / 3.) * (yi + 1))
                particles.append(canvas.create_oval(wx-2, wy-2,
                                                    wx+2, wy+2,
                                                    fill='red'))
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
        tk.update()

    counter = 0

    def equationsOfMotion(self):
        A = 1.0e-5
        n = self.side
        forces = (n * n) * [ (0.0, 0.0) ]
        t = self.simTime
        dt = 0.1
        if t > 0 and t < dt:
            forces[0] = (A, -A)
            forces[n*(n-1)] = (A, A)
        elif t > 2.0 and t < 2.0 + dt:
            forces[-1] = (-A, A)
            forces[n-1] = (-A, -A)
        self.counter += 1
        for ft in self.forceTerms:
            ft.compute(forces)
        self_u, self_uold, self_unew = self.u, self.u_old, self.u_new
        index = 0
        DTM = (DT ** 2) / MASS
        for i in range(n):
            for j in range(n):
                uvec = self_u[index]
                uold = self_uold[index]
                unew = (2*uvec[0] - uold[0], 2*uvec[1] - uold[1])
                fi = forces[index]
                self_unew[index] = (unew[0] + DTM * fi[0],
                                    unew[1] + DTM * fi[1])
                index += 1
        self.simTime += DT

    def updateGraphics(self):
        canvas, particles = self.canvas, self.particles
        self_x, self_u, self_u_new = self.x, self.u, self.u_new
        n = self.side
        xs = self.width / 3.
        ys = self.height / 3.
        index = 0
        for i in range(n):
            for j in range(n):
                unew = self_u_new[index]
                uvec = self_u[index]
                canvas.move(particles[index],
                            xs * (unew[0] - uvec[0]),
                            ys * (unew[1] - uvec[1]))
                index += 1
        self.tk.update()

    def run(self):
        # On each step we do verlet, using u_old and u to compute
        # u_new. Then we move each particle from u to u_new. Then
        # we move u to u_old, and u_new to u.
        while self.simTime < 20:
            for i in range(10):
                self.equationsOfMotion()
                tmp = self.u_old
                self.u_old = self.u
                self.u = self.u_new
                self.u_new = tmp
            self.updateGraphics()

# Main program
def main():
    import sys, string
    h = FiniteElementGrid(6)
    h.run()


# Call main when run as script
if __name__ == '__main__':
    main()
