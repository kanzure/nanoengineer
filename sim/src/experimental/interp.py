# Copyright 2005 Nanorex, Inc.  See LICENSE file for details.
"""Usage:

Type 'python interp.py c' to generate C code.

Type 'python interp.py gnuplot' to see graphs of the approximations.

Type 'python interp.py quadratic c' to generate C code for a
quadratic interpolator.
Type 'python interp.py linear c' to generate C code for a
linear interpolator.
'quadratic' and 'linear' also work for the 'gnuplot' mode.
The default behavior is 'quadratic' but the behavioral difference
appears to be negligible.

Type 'python interp.py discontinuity' to investigate any
discontinuities in potential or force near r=r0.

------------------

In order to apply this to each of the types of bond length terms, we
need to call this script with each (Ks, R0, De, Beta) set and use it
to generate a C function for that term. In each case, we should
visually inspect the left-of-r0 and right-of-r0 gnuplot graphs to make
sure they look reasonable (and possibly discuss what 'reasonable'
means here). We will probably want to generate the 'points' list based
on the values of R0 and R1; that can probably be done in some
automated way.

The result would be one or more automatically generated C files that
go into the source code, and the Makefile would generate those files
from text files containing the (Ks, R0, De, Beta) sets.

"""

import os
import sys
from math import exp, log, sqrt

# Use 1 if the input to the interpolator is r.
# Use 2 if the input to the interpolator is r**2.
# The default is 2.
TABLE_INPUT_ORDER = 2

if "quadratic" in sys.argv[1:]:
    TABLE_INPUT_ORDER = 2
if "linear" in sys.argv[1:]:
    TABLE_INPUT_ORDER = 1

name = "Csp3_Csp3"
Ks = 440.0     # newtons per meter
R0 = 152.3     # picometers
De = 0.556     # attojoules
Beta = 1.989   # beta

if "nitrogen" in sys.argv[1:]:
    name = "Nsp3_Nsp3"
    Ks = 560.0
    R0 = 138.1
    De = 0.417
    Beta = 2.592

def lippincottPotential(r):
    return De * (1 - exp(-1e-6 * Ks * R0 * (r - R0) * (r - R0) / (2 * De * r)))

def lippincottDerivative(r):
    if r < 0.001: r = 0.001
    a = 5.0e-7
    b = a * Ks * (r - R0)**2 * R0
    c = 2 * a * Ks * (r - R0) * R0
    return -De * (b / (De * r**2) - c / (De * r)) * exp(-b / (De * r))

def morsePotential(r):
    return De * (1 - exp(-Beta * (r - R0))) ** 2

def morseDerivative(r):
    expFoo = exp(-Beta * (r - R0))
    return 2 * Beta * De * (1 - expFoo) * expFoo

####################################################

# Do the V1-r1 trick for putting a bound on Morse potential.
V1 = 10.0 * De
R1 = R0 - log(sqrt(V1/De) + 1) / Beta
D1 = 2.0 * Beta * De * (1 - exp(-Beta * (R1 - R0))) * exp(-Beta * (R1 - R0))

def boundedMorsePotential(r, oldMorse=morsePotential):
    if r < R1: return D1 * (r - R1) + V1
    else: return oldMorse(r)

def boundedMorseDerivative(r, oldDeriv=morseDerivative):
    if r < R1: return D1
    else: return oldDeriv(r)

morsePotential = boundedMorsePotential
morseDerivative = boundedMorseDerivative

##################################################

# Josh wanted to switch from Morse to Lippincott abruptly.
# This gives a discontinuity in the force, and we might want
# something a little smoother.
if "smooth" in sys.argv[1:]:
    def blend(r):
        "zero for r << R0, one for r >> R0, smooth everywhere"
        width = 1.0e-9 * R0   # needed empirical tinkering
        x = (r - R0) / width
        return 0.5 * (1 + x / sqrt(x**2 + 1))

    def compositePotential(r):
        b = blend(r)
        return (b * lippincottPotential(r) +
                (1 - b) * morsePotential(r))

    def compositeDerivative(r):
        b = blend(r)
        return (b * lippincottDerivative(r) +
                (1 - b) * morseDerivative(r))

else:
    def compositePotential(r):
        if r >= R0: return lippincottPotential(r)
        else: return morsePotential(r)

    def compositeDerivative(r):
        if r >= R0: return lippincottDerivative(r)
        else: return morseDerivative(r)

###############################################################

if "discontinuity" in sys.argv[1:]:
    # Check for continuity when we switch from Lippincott to Morse
    h = 1.0e-10 * R0
    sys.stderr.write("%f %f\n" %
                     (compositePotential(R0 - h),
                      compositePotential(R0 + h)))
    # 5.1035893951e-08 -5.10296338518e-12 for abrupt switch
    sys.stderr.write("%f %f\n" %
                     (compositeDerivative(R0 - h),
                      compositeDerivative(R0 + h)))
    # -0.000670303668534 6.70118994284e-08 for abrupt switch

    # Alternatively, allowing for round-off error, do asserts
    diff = compositePotential(R0 - h) - compositePotential(R0 + h)
    assert abs(diff) < 1.0e-6 * De  # this one is OK
    diff = compositeDerivative(R0 - h) - compositeDerivative(R0 + h)
    assert abs(diff) < 1.0e-4 * De / R0  # Is this OK?

GNUPLOT_PAUSE = 5

class Gnuplot:
    def __init__(self, enable=True):
        if enable:
            self.outf = open("/tmp/results", "w")
        else:
            self.outf = None
    def add(self, x, *y):
        if self.outf != None:
            if hasattr(self, "graphs"):
                assert len(y) == self.graphs
            else:
                self.graphs = len(y)
            format = "%.16e " + (self.graphs * " %.16e") + "\n"
            self.outf.write(format % ((x,) + y))
    def plot(self):
        if self.outf != None:
            self.outf.close()
            g = os.popen("gnuplot", "w")
            if hasattr(self, "ylimits"):
                cmd = "plot [] [%.16e:%.16e] " % self.ylimits
            else:
                cmd = "plot "
            for i in range(self.graphs):
                cmd += "\"/tmp/results\" using 1:%d with lines" % (i + 2)
                if i < self.graphs - 1:
                    cmd += ","
                cmd += " "
            cmd += "; pause %f\n" % GNUPLOT_PAUSE
            g.write(cmd)
            g.close()
            #os.system("rm -f /tmp/results")

if False:
    gp = Gnuplot()
    r = R0 + 0.0001
    while r < 3 * R0:
        gp.add(r, compositePotential(r))
        r += 0.01
    gp.plot()
    sys.exit(0)

# Does r0 need to be in this list?
points = [
    0,
    0.99 * R1,
    R1,
    0.8 * R1 + 0.2 * R0,
    0.6 * R1 + 0.4 * R0,
    0.4 * R1 + 0.6 * R0,
    0.2 * R1 + 0.8 * R0,
    0.05 * R1 + 0.95 * R0,
    R0,
    R0 * 1.05,
    R0 * 1.2,
    R0 * 1.3,
    R0 * 1.5,
    R0 * 1.8,
    R0 * 2.0,
    R0 * 2.2
    ]
points.sort()  # in case I messed up

if "static_inline" in sys.argv[1:]:
    STATIC_INLINE = "static inline"
else:
    STATIC_INLINE = ""

# We will instantiate an Interpolator for each bond type.
# Note that the tables used by Interpolators are pretty small,
# typically about 512 bytes (~64 doubles).
class Interpolator:
    def __init__(self, name, func, points):
        self.name = name
        self.intervals = intervals = [ ]
        # Generate a cubic spline for each interpolation interval.
        for u, v in map(None, points[:-1], points[1:]):
            FU, FV = func(u), func(v)
            h = 0.01 # picometers?
            # I know I said we shouldn't do numerical integration,
            # and yet here I am, doing it anyway. Shame on me.
            DU = (func(u + h) - FU) / h
            DV = (func(v + h) - FV) / h
            denom = (u - v)**3
            A = ((-DV - DU) * v + (DV + DU) * u +
                 2 * FV - 2 * FU) / denom
            B = -((-DV - 2 * DU) * v**2  +
                  u * ((DU - DV) * v + 3 * FV - 3 * FU) +
                  3 * FV * v - 3 * FU * v +
                  (2 * DV + DU) * u**2) / denom
            C = (- DU * v**3  +
                 u * ((- 2 * DV - DU) * v**2  + 6 * FV * v - 6 * FU * v) +
                 (DV + 2 * DU) * u**2 * v + DV * u**3) / denom
            D = -(u *(-DU * v**3  - 3 * FU * v**2) +
                  FU * v**3 + u**2 * ((DU - DV) * v**2 + 3 * FV * v) +
                  u**3 * (DV * v - FV)) / denom
            intervals.append((u, A, B, C, D))

    def __call__(self, x):
        def getInterval(x, intervalList):
            # run-time proportional to the log of the length
            # of the interval list
            n = len(intervalList)
            if n < 2:
                return intervalList[0]
            n2 = n / 2
            if x < intervalList[n2][0]:
                return getInterval(x, intervalList[:n2])
            else:
                return getInterval(x, intervalList[n2:])
        # Tree-search the intervals to get coefficients.
        u, A, B, C, D = getInterval(x, self.intervals)
        # Plug coefficients into polynomial.
        return ((A * x + B) * x + C) * x + D

    def c_code(self):
        """Generate C code to efficiently implement this interpolator."""
        def codeChoice(intervalList):
            n = len(intervalList)
            if n < 2:
                return ("A=%.16e;B=%.16e;C=%.16e;D=%.16e;"
                        % intervalList[0][1:])
            n2 = n / 2
            return ("if (x < %.16e) {%s} else {%s}"
                    % (intervalList[n2][0],
                       codeChoice(intervalList[:n2]),
                       codeChoice(intervalList[n2:])))
        return (STATIC_INLINE + " double interpolator_%s(double x) {" % self.name +
                "double A,B,C,D;%s" % codeChoice(self.intervals) +
                "return ((A * x + B) * x + C) * x + D;}")

DISCRETIZE_POINTS = ("discretize" in sys.argv[1:])
NUM_SLOTS = 10000

class EvenOrderInterpolator:
    def __init__(self, name, func, points):
        self.name = name
        self.intervals = intervals = [ ]
        if DISCRETIZE_POINTS:
            self.startPoint = start = 1. * points[0] ** 2
            self.finishPoint = finish = 1. * points[-1] ** 2
            self.xstep = xstep = (finish - start) / NUM_SLOTS
            intpoints = [ ]
            newpoints = [ ]
            for p in points:
                index = int((p**2 - start) / xstep)
                newvalue = (start + index * xstep) ** 0.5
                intpoints.append(index)
                newpoints.append(newvalue)
            points = newpoints
        j = 0
        for u, v in map(None, points[:-1], points[1:]):
            s0 = s2 = s4 = s6 = s8 = 0.0
            P = Q = R = 0.0
            N = 2
            x = 1. * u
            dx = (1. * v - u) / N
            for i in range(N+1):
                y = func(x)
                s0 += dx
                s2 += dx * x**2
                s4 += dx * x**4
                s6 += dx * x**6
                s8 += dx * x**8
                P += dx * y * x**4
                Q += dx * y * x**2
                R += dx * y
                x += dx
            denom = ((s0*s4 - s2**2) * s8 +
                     (s2*s6 - s4**2) * s4 +
                     (s2*s4 - s0*s6) * s6)
            a11 = (s0 * s4 - s2**2) / denom
            a12 = (s2 * s4 - s0 * s6) / denom
            a13 = (s2 * s6 - s4**2) / denom
            a21 = a12
            a22 = (s0 * s8 - s4**2) / denom
            a23 = (s4 * s6 - s2 * s8) / denom
            a31 = a13
            a32 = a23
            a33 = (s4 * s8 - s6**2) / denom

            A = a11 * P + a12 * Q + a13 * R
            B = a21 * P + a22 * Q + a23 * R
            C = a31 * P + a32 * Q + a33 * R

            if DISCRETIZE_POINTS:
                intervals.append((intpoints[j], A, B, C))
            else:
                intervals.append((u**2, A, B, C))
            j += 1

    def __call__(self, xsq):
        def getInterval(xsq, intervalList):
            # run-time proportional to the log of the length
            # of the interval list
            n = len(intervalList)
            if n < 2:
                return intervalList[0]
            n2 = n / 2
            if xsq < intervalList[n2][0]:
                return getInterval(xsq, intervalList[:n2])
            else:
                return getInterval(xsq, intervalList[n2:])
        # Tree-search the intervals to get coefficients.
        if DISCRETIZE_POINTS:
            j = (xsq - self.startPoint) / self.xstep
            u, A, B, C = getInterval(j, self.intervals)
        else:
            u, A, B, C = getInterval(xsq, self.intervals)
        # Plug coefficients into polynomial.
        return (A * xsq + B) * xsq + C

    def c_code(self):
        """Generate C code to efficiently implement this interpolator."""
        def codeChoice(intervalList):
            n = len(intervalList)
            if n < 2:
                return ("return (%.16e * xsq + %.16e) * xsq + %.16e;"
                        % intervalList[0][1:])
            n2 = n / 2
            if DISCRETIZE_POINTS:
                return ("if (j < %d) {%s} else {%s}"
                        % (intervalList[n2][0],
                           codeChoice(intervalList[:n2]),
                           codeChoice(intervalList[n2:])))
            else:
                return ("if (xsq < %.16e) {%s} else {%s}"
                        % (intervalList[n2][0],
                           codeChoice(intervalList[:n2]),
                           codeChoice(intervalList[n2:])))
        if DISCRETIZE_POINTS:
            return (STATIC_INLINE + " double interpolator_%s(double xsq) {\n" % self.name +
                    "int j = (int) (%.16e * (xsq - %.16e));" % (1.0 / self.xstep, self.startPoint) +
                    codeChoice(self.intervals) +
                    "}")
        else:
            return (STATIC_INLINE + " double interpolator_%s(double xsq) {\n" % self.name +
                    codeChoice(self.intervals) +
                    "}")

class MaybeFasterEvenOrderInterpolator(EvenOrderInterpolator):
    def c_code(self):
        assert DISCRETIZE_POINTS
        """Generate C code to efficiently implement this interpolator."""
        ccode = "double A[] = {"
        for ivl in self.intervals:
            ccode += "%.16e," % ivl[1]
        ccode += "};\n"
        ccode += "double B[] = {"
        for ivl in self.intervals:
            ccode += "%.16e," % ivl[2]
        ccode += "};\n"
        ccode += "double C[] = {"
        for ivl in self.intervals:
            ccode += "%.16e," % ivl[3]
        ccode += "};\n"
        ccode += "int slots[] = {\n"
        j = 0
        for i in range(NUM_SLOTS):
            ccode += "%d," % j
            if j < len(self.intervals) and i >= self.intervals[j][0]:
                j += 1
        ccode += "};\n"
        ccode += STATIC_INLINE + " double interpolator_%s(double xsq) {\n" % self.name
        ccode += "int j = (int) (%.16e * (xsq - %.16e));\n" % (1.0 / self.xstep, self.startPoint)
        ccode += "j = j[slots];"
        ccode += "return (A[j] * xsq + B[j]) * xsq + C[j];}"
        return ccode


if "sqrt" in sys.argv[1:]:
    points = [1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 8, 10,
              12, 14, 17, 20, 25, 30, 35, 40, 50, 60, 80, 100]
    def myFunction(x):
        return x ** 0.5
    name = "sqrt"
else:
    myFunction = compositeDerivative


if TABLE_INPUT_ORDER == 2:
    interp = EvenOrderInterpolator(name, myFunction, points)
else:
    interp = Interpolator(name, myFunction, points)

def graphRegion(start, finish):
    gp = Gnuplot()
    N = 10000

    rstep = (1.0 * finish - start) / N
    r = 1.0 * start
    errsq = 0.0

    for i in range(N):
        f_real = myFunction(r)
        f_approx = interp(r ** TABLE_INPUT_ORDER)
        errsq += (f_real - f_approx) ** 2
        gp.add(r, f_real, f_approx)
        r += rstep

    sys.stderr.write("Total square error is %g\n" % errsq)
    sys.stderr.write("Mean square error is %g\n"% (errsq / N))
    gp.plot()

if "c" in sys.argv[1:]:
    # crank it thru 'indent' so it's not so ugly
    outf = open("interp_ugly.c", "w")
    outf.write(interp.c_code())
    outf.close()

if "graph" in sys.argv[1:]:
    # Because the Morse potential is so huge, we need
    # to graph Morse and Lippincott separately.

    if "sqrt" in sys.argv[1:]:
        graphRegion(points[0], points[-1])
    else:
        if True:
            GNUPLOT_PAUSE = 10
            #graphRegion(0, R0)
            graphRegion(.5*(R0+R1), R0)
            #graphRegion(R0, points[-1])
        else:
            graphRegion(R1, R0)
            graphRegion(R0, points[-1])
