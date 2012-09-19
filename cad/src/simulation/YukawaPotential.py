# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details.

"""
YukawaPotential.py

Create an .xvg file suitable for passing as the argument to -table for
mdrun.

@author: Eric M
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

The table consists of 7 columns:

r f f'' g g'' h h''

In other words, three functions evaluated at evenly spaced r values,
and their second derivatives.  For the standard Coulomb and
Lennard-Jones potentials, the functions are:

f(r) = 1/r

g(r) = -1/r^6

h(r) = 1/r^12

This table is read by the GROMACS mdrun process when user specified
potential functions are used.  We use this for the non-bonded
interactions between PAM5 model DNA helices.

"""

# DELTA_R should be 0.002 for a gromacs compiled to use single
# precision floats, and 0.0005 for doubles.
DELTA_R = 0.0005

# values from Physics, Halliday and Resnick, Third Edition, 1978
ELECTRON_CHARGE = 1.6021892e-19       # Coulombs (A s)
VACUUM_PERMITTIVITY = 8.854187818e-12 # Farads/meter (A^2 s^4 kg^-1 m^-3)
BOLTZMANN = 1.380662e-23              # Joules/Kelvin (kg m^2 s^-2 K^-1)
AVOGADRO = 6.022045e23                # particles/mol

PHOSPHATE_DIAMETER = 0.4 # nm

import math

class YukawaPotential(object):
    def __init__(self, simulatorParameters):
        self.rCutoff = simulatorParameters.getYukawaRCutoff()
        self.rSwitch = simulatorParameters.getYukawaRSwitch()
        self.shift = simulatorParameters.getYukawaShift()
        self.charge = simulatorParameters.getYukawaCounterionCharge()
        self.molarity = simulatorParameters.getYukawaCounterionMolarity()
        self.temperature = simulatorParameters.getYukawaTemperatureKelvin()
        self.dielectric = simulatorParameters.getYukawaDielectric()
        self.fudge = simulatorParameters.getYukawaConstantMultiple()

        # Bjerrum length (nm)
        L_B = 1e9 * ELECTRON_CHARGE * ELECTRON_CHARGE / (4.0 * math.pi *
                                                         VACUUM_PERMITTIVITY *
                                                         self.dielectric *
                                                         BOLTZMANN *
                                                         self.temperature)
        # (A^2 s^2) (A^-2 s^-4 kg m^3) (kg^-1 m^-2 s^2 K) K^-1 = m
        # about 0.7nm for default conditions

        # Debye length (nm)
        Lambda_D = 1.0 / math.sqrt(4.0 * math.pi * L_B * self.molarity *
                                   self.charge * self.charge)
        # 1/sqrt(nm / litre) --> nm
        # about 1.2nm for default conditions

        mol_K_per_kJ = 1000 / (AVOGADRO * BOLTZMANN)

        t1 = 1.0 + PHOSPHATE_DIAMETER / (2.0 * Lambda_D)
        E_p_p = self.temperature * L_B / \
                (mol_K_per_kJ * PHOSPHATE_DIAMETER * t1 * t1)

        self.YA = E_p_p * PHOSPHATE_DIAMETER * self.fudge
        self.YB = PHOSPHATE_DIAMETER
        self.YC = Lambda_D

        #print "L_B = %e, Lambda_D = %e" % (L_B, Lambda_D)
        #print "t1 = %e, E_p_p = %e" % (t1, E_p_p)
        #print "mol_K_per_kJ = %e" % mol_K_per_kJ
        #print "YA = %e, YB = %e. YC = %e" % (self.YA, self.YB, self.YC)

        self.YShift = 0.0
        if (self.shift):
            self.YShift = self.yukawa(self.rCutoff)

# Switching function to smoothly reduce a function to zero.
# Transition begins when r == start, below which the value is 1.  The
# value smoothly changes to 0 by the time r == end, after which it
# remains 0.
#
# Potential functions are multiplied by the switching function S:
#
#          (r/start - 1)^4
# S = (1 - ----------------- ) ^4
#          (end/start - 1)^4
#
# in the range start < r < end.

        self.switch_len = self.rCutoff - self.rSwitch
        self.switch_len_4 = self.switch_len * self.switch_len * self.switch_len * self.switch_len

        self.switch_d_1 = ((self.rCutoff / self.rSwitch) - 1)
        self.switch_d_2 = -16.0 / (self.switch_d_1 * self.switch_d_1 * self.switch_d_1 * self.switch_d_1 * self.rSwitch)
        self.switch_d2_1 = (self.rCutoff / self.rSwitch) - 1
        self.switch_d2_1_4 = self.switch_d2_1 * self.switch_d2_1 * self.switch_d2_1 * self.switch_d2_1
        self.switch_d2_1_8 = self.switch_d2_1_4 * self.switch_d2_1_4
        self.switch_d2_1_8_start_2 = self.switch_d2_1_8 * self.rSwitch * self.rSwitch

        if (self.switch_len <= 0.0):
            self.func = self.yukawa
            self.d2_func = self.d2_yukawa
        else:
            self.func = self.switch_yukawa
            self.d2_func = self.d2_switch_yukawa

    def writeToFile(self, pathName):
        tableFile = open(pathName, 'w')
        r = 0.0
        # We go to 2 * self.rCutoff because GROMACS reuses the mdp
        # option table-extension (how far past self.rCutoff we need to
        # extend the table) as the length of the 1-4 interaction
        # table.  Since we want 1-4 interactions to go to self.rCutoff
        # as well, we need table-extension to be self.rCutoff, which
        # results in the normal table being 2 * self.rCutoff.  Silly,
        # really.
        while (r < 2 * self.rCutoff + (DELTA_R / 2.0)):
            print >>tableFile, \
                  "%8.4f %13.6e %13.6e %13.6e %13.6e %13.6e %13.6e" % (r,
                                                                       self.r_1(r),
                                                                       self.d2_r_1(r),
                                                                       self.func(r),
                                                                       self.d2_func(r),
                                                                       0,
                                                                       0)
            r += DELTA_R
        tableFile.close()

    def r_1(self, r):
        if (r < 0.04):
            return 0.0
        return 1.0 / r

    def d2_r_1(self, r):
        if (r < 0.04):
            return 0.0
        return 2.0 / (r * r * r)

    def r_6(self, r):
        if (r < 0.04):
            return 0.0
        return -1.0 / (r * r * r * r * r * r)

    def d2_r_6(self, r):
        if (r < 0.04):
            return 0.0
        return -42.0 / (r * r * r * r * r * r * r * r)

    def r_12(self, r):
        if (r < 0.04):
            return 0.0
        return 1.0 / (r * r * r * r * r * r * r * r * r * r * r * r)

    def d2_r_12(self, r):
        if (r < 0.04):
            return 0.0
        return 156.0 / (r * r * r * r * r * r * r * r * r * r * r * r * r * r)


    def yukawa(self, r):
        if (r < 0.04):
            return self.yukawa(0.04) + 0.04 - r ;
        return (self.YA / r) * math.exp(-(r - self.YB) / self.YC) - self.YShift

    def d_yukawa(self, r):
        if (r < 0.04):
            return 0.0
        return self.YA * math.exp(-(r - self.YB) / self.YC) * (-1.0/(r * r) - 1.0/(self.YC * r))

    def d2_yukawa(self, r):
        if (r < 0.04):
            return 0.0
        return self.YA * math.exp(-(r - self.YB) / self.YC) * (2.0/(self.YC * r * r) + 1.0/(self.YC * self.YC * r) + 2.0/(r * r * r))


    def switch(self, r):
        if (r <= self.rSwitch):
            return 1.0
        if (r >= self.rCutoff):
            return 0.0

        rDiff = r - self.rSwitch
        S1 = ((rDiff * rDiff * rDiff * rDiff) / self.switch_len_4) - 1
        return S1 * S1 * S1 * S1

    def d_switch(self, r):
        if (r <= self.rSwitch):
            return 0.0
        if (r >= self.rCutoff):
            return 0.0

        t1 = r - self.rSwitch
        t1_4 = t1 * t1 * t1 * t1
        t2 = 1 - t1_4 / self.switch_len_4
        t3 = (r / self.rSwitch) - 1
        t4 = t2 * t2 * t2 * t3 * t3 * t3
        return self.switch_d_2 * t4

    def d2_switch(self, r):
        if (r <= self.rSwitch):
            return 0.0
        if (r >= self.rCutoff):
            return 0.0

        t1 = r - self.rSwitch
        t1_4 = t1 * t1 * t1 * t1
        t2 = t1_4 / self.switch_len_4

        t3 = (r / self.rSwitch) - 1
        t3_2 = t3 * t3
        t3_4 = t3_2 * t3_2

        return (48 * (-(1 - t2) * self.switch_d2_1_4 + 4 * t3_4) * (t2 - 1) * (t2 - 1) * t3_2) / self.switch_d2_1_8_start_2

    def switch_yukawa(self, r):
        return self.switch(r) * self.yukawa(r)

    def d2_switch_yukawa(self, r):
        return self.d2_switch(r) * self.yukawa(r) + 2.0 * self.d_switch(r) * self.d_yukawa(r) + self.switch(r) * self.d2_yukawa(r)
