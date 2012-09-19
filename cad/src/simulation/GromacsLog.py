# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

"""
GromacsLog.py

Parse the .log file output of the GROMACS mdrun program, specifically
during conjugate gradients minimization.  Note the energy values for
various components as they change, and report their final values.

@author: Eric M
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.

GROMACS is not very computer friendly about its output formats.  In
this case, table headings and values appear on alternate lines, and
which ones are included varies from run to run.

Sample output:

Configuring nonbonded kernels...
Testing ia32 SSE2 support... present.


           Step           Time         Lambda
              0        0.00000        0.00000

   Energies (kJ/mol)
           Bond  Harmonic Pot.          LJ-14     Coulomb-14        LJ (SR)
    1.67136e+01    3.91076e+01    6.14294e-01    0.00000e+00    4.51586e+01
   Coulomb (SR)      Potential    Kinetic En.   Total Energy    Temperature
    0.00000e+00    1.01594e+02    0.00000e+00    1.01594e+02    0.00000e+00
 Pressure (bar)
    0.00000e+00

   F-max             =  1.11581e+01 on atom 237
   F-Norm            =  7.33720e+01

           Step           Time         Lambda
              0        0.00000        0.00000

   Energies (kJ/mol)
           Bond  Harmonic Pot.          LJ-14     Coulomb-14        LJ (SR)
    1.65284e+01    3.88862e+01    6.14476e-01    0.00000e+00    4.51403e+01
   Coulomb (SR)      Potential    Kinetic En.   Total Energy    Temperature
    0.00000e+00    1.01169e+02    0.00000e+00    1.01169e+02    0.00000e+00
 Pressure (bar)
    0.00000e+00



           Step           Time         Lambda
              0        0.00000        0.00000

   Energies (kJ/mol)
           Bond  Harmonic Pot.        LJ (SR)   Coulomb (SR)      Potential
    1.96551e+00    1.16216e+00    0.00000e+00    0.00000e+00    3.12768e+00
    Kinetic En.   Total Energy    Temperature Pressure (bar)
    0.00000e+00    3.12768e+00    0.00000e+00    0.00000e+00



"""

import foundation.env as env
from utilities.Log import quote_html, orangemsg

AVOGADRO = 6.022045e23                # particles/mol

class GromacsLog(object):
    def __init__(self):
        self.state = 0
        self._resetColumns()

    def addLine(self, line):
        columns = line.split()

        if (len(columns) == 3 and
            columns[0] == 'Step' and
            columns[1] == 'Time' and
            columns[2] == 'Lambda'):

            self._resetColumns()
            self.state = 1
            return
        if (self.state == 1 and len(columns) == 3):
            self.step = columns[0]
            self.state = 2
            return
        if (self.state == 2 and len(columns) == 0):
            self.state = 3
            return
        if (self.state == 3 and len(columns) == 2 and columns[0] == 'Energies'):
            self.state = 4
            return
        if (self.state == 4):
            if (len(columns) > 0):
                self.state = 5
                self.column_headers = self._extractColumns(line.rstrip())
                return
            else:
                self._emitColumns()
                self.state = 0
                return
        if (self.state == 5):
            if (len(columns) == len(self.column_headers)):
                self._addColumns(self.column_headers, columns)
                self.state = 4
                return
            else:
                self.state = 0 # this never happens
                return

# Stepsize too small, or no change in energy.
# Converged to machine precision,
# but not to the requested precision Fmax < 0.006022
#
# Polak-Ribiere Conjugate Gradients did not converge to Fmax < 0.006022 in 100001 steps.

        if (line.find("converge") >= 0 and line.find("Fmax") >= 0):
            env.history.message("Energy (Bond, Strut, Nonbonded): (%f, %f, %f) zJ" %
                                (self.getBondEnergy(),
                                 self.getHarmonicEnergy(),
                                 self.getNonbondedEnergy()))
            env.history.message("Total Energy %f zJ" % self.getTotalEnergy())
            if (line.find("machine") >= 0 or line.find("did not") >= 0):
                env.history.message(orangemsg(quote_html(line.rstrip())))
            else:
                env.history.message(quote_html(line.rstrip()))
            return

    def _extractColumns(self, line):
        columns = []
        while (len(line) >= 15):
            col = line[:15]
            line = line[15:]
            columns.append(col.strip())
        return columns

    def _resetColumns(self):
        self._values = {}
        self.step = "-"

    def _addColumns(self, headers, values):
        for i in range(len(headers)):
            key = headers[i]
            value = values[i]
            self._values[key] = value

    def _emitColumns(self):
        result = "%s: (%f + %f + %f) = %f zJ" % (self.step,
                                                 self.getBondEnergy(),
                                                 self.getHarmonicEnergy(),
                                                 self.getNonbondedEnergy(),
                                                 self.getTotalEnergy())
        env.history.statusbar_msg(result)

    def kJ_per_mol_to_zJ(self, kJ_per_mol):
        joules = kJ_per_mol * 1000.0 / AVOGADRO
        return joules * 1e21

    def _getSingleEnergy(self, key):
        if (self._values.has_key(key)):
            try:
                value = float(self._values[key])
            except:
                print "_getSingleEnergy(): malformed value for %s: '%s'" % (key, self._values[key])
                value = 0.0
            return self.kJ_per_mol_to_zJ(value)
        return 0.0

    def getBondEnergy(self):
        return self._getSingleEnergy("Bond") + self._getSingleEnergy("Morse") + self._getSingleEnergy("Angle")

    def getHarmonicEnergy(self):
        return self._getSingleEnergy("Harmonic Pot.")

    def getNonbondedEnergy(self):
        return self._getSingleEnergy("LJ-14") + self._getSingleEnergy("LJ (SR)") + self._getSingleEnergy("Buck.ham (SR)")

    def getTotalEnergy(self):
        return self._getSingleEnergy("Total Energy")
