#!/usr/bin/python

# Copyright 2005 Nanorex, Inc.  See LICENSE file for details.
# Refer to http://tinyurl.com/8zl86, the 22 Dec discussion about
# rotary motors.

from math import pi, cos, sin
import random
import units
import sys

DEBUG = False

DT = 1.e-16 * units.second
SPRING_STIFFNESS = 10 * units.newton / units.meter

# Sw(x) goes from 0 to 1, use 1-Sw(x) to go from 1 to 0
def Sw(x, a=.5/pi, b=2*pi):
    if x < 0: return 0
    elif x > 1: return 1
    else: return x - a * cos(b * (x - .25))

class Atom:
    def __init__(self, mass, x, y, z):
        self.mass = mass
        self.position = units.Vector(x, y, z)
        self.velocity = units.ZERO_VELOCITY
        self.zeroForce()
    def zeroForce(self):
        self.force = units.ZERO_FORCE
    def __repr__(self):
        pos = self.position
        return "<%s %s>" % (repr(self.mass), repr(self.position))
    def timeStep(self):
        self.position += self.velocity.scale(DT)
        self.velocity += self.force.scale(DT / self.mass)

class Spring:
    def __init__(self, stiffness, atom1, atom2):
        self.stiffness = stiffness
        self.atom1 = atom1
        self.atom2 = atom2
        self.length = (atom1.position - atom2.position).length()
    def timeStep(self):
        x = self.atom1.position - self.atom2.position
        f = x.normalize().scale(self.stiffness * (x.length() - self.length))
        self.atom1.force -= f
        self.atom2.force += f

class RotaryController:
    def __init__(self, atomlist):
        self.atoms = atomlist
        center = units.ZERO_POSITION
        for atm in atomlist:
            center += atm.position
        self.center = center = center.scale(1./len(atomlist))
        # Determine the direction of the axis. If the atoms are all
        # lying in a plane, this should be normal to the plane.
        axis = units.ZERO_POSITION
        extended = atomlist + [ atomlist[0], ]
        for i in range(len(atomlist)):
            u = extended[i].position - center
            v = extended[i+1].position - center
            axis += u.cross(v).scale(1./units.meter)
        self.axis = axis = axis.normalize()
        # at this point, axis is dimensionless and unit-length
        self.anchors = anchors = [ ]
        amoi = 0. * units.MomentOfInertiaUnit
        for atom in atomlist:
            x = atom.position - center
            u = axis.scale(x.dot(axis))
            v = x - u   # component perpendicular to motor axis
            w = axis.cross(v)
            def getAnchor(theta, u=u, v=v, w=w):
                # be able to rotate the anchor around the axis
                theta /= units.radian
                return u + v.scale(cos(theta)) + w.scale(sin(theta))
            anchors.append(getAnchor)
            amoi = atom.mass * v.length() ** 2
        self.atomsMomentOfInertia = amoi
        self.omega = 0. * units.radian / units.second
        self.theta = 0. * units.radian

    def nudgeAtomsTowardTheta(self):
        # this is called during the controller's time step function
        # assume that any interatomic forces have already been computed
        # and are represented in the "force" attribute of each atom
        # calculate positions of each anchor, and spring force to atom
        atoms, anchors, center = self.atoms, self.anchors, self.center
        atomDragTorque = 0. * units.TorqueUnit
        for i in range(len(atoms)):
            atom = atoms[i]
            anchor = anchors[i](self.theta)
            # compute force between atom and anchor
            springForce = (atom.position - anchor).scale(SPRING_STIFFNESS)
            atom.force -= springForce
            r = atom.position - center
            T = r.cross(springForce).scale(units.radian)
            atomDragTorque += self.axis.dot(T)
        return atomDragTorque


class BoschMotor(RotaryController):

    def __init__(self, atomlist, torque, gigahertz):
        RotaryController.__init__(self, atomlist)
        speed = (2 * pi * 1.e9 * units.AngularVelocityUnit) * gigahertz
        if DEBUG: print "target speed", speed
        assert units.TorqueUnit.unitsMatch(torque)
        assert units.AngularVelocityUnit.unitsMatch(speed)
        self.stallTorque = torque
        self.speed = speed

        amoi = self.atomsMomentOfInertia
        flywheelMomentOfInertia = 10 * amoi
        self.momentOfInertia = amoi + flywheelMomentOfInertia

        #
        #   There REALLY IS a criterion for numerical stability!
        #
        ratio = (DT * torque) / (self.momentOfInertia * speed)
        #if False:
        if abs(ratio) > 0.3:
            # The C code must also throw an exception or do whatever is
            # the equivalent thing at this point.
            raise Exception, "torque-to-speed ratio is too high"

    def timeStep(self):
        # assume that any interatomic forces have already been computed
        # and are represented in the "force" attribute of each atom
        # calculate positions of each anchor, and spring force to atom
        atomDragTorque = self.nudgeAtomsTowardTheta()
        controlTorque = self.torqueFunction()
        self.torque = torque = controlTorque + atomDragTorque

        # iterate equations of motion
        self.theta += DT * self.omega
        self.omega += DT * torque / self.momentOfInertia

    def torqueFunction(self):
        # The Bosch model
        return (1.0 - self.omega / self.speed) * self.stallTorque

class ThermostatMotor(BoschMotor):
    def torqueFunction(self):
        # bang-bang control
        if self.omega < self.speed:
            return self.stallTorque
        else:
            return -self.stallTorque

class RotarySpeedController(RotaryController):
    def __init__(self, atomlist, rampupTime, gigahertz):
        RotaryController.__init__(self, atomlist)
        speed = (2 * pi * 1.e9 * units.AngularVelocityUnit) * gigahertz
        if DEBUG: print "target speed", speed
        assert units.second.unitsMatch(rampupTime)
        assert units.AngularVelocityUnit.unitsMatch(speed)
        self.time = 0. * units.second
        self.rampupTime = rampupTime
        self.speed = speed

    def timeStep(self):
        self.nudgeAtomsTowardTheta()
        # iterate equations of motion
        self.theta += DT * self.omega
        self.omega = self.speed * Sw(self.time / self.rampupTime)
        self.time += DT

################################################

N = 6
alst = [ ]
for i in range(N):
    def rand():
        #return 0.1 * (1. - 2. * random.random())
        return 0.
    a = 3 * units.angstrom
    x = a * (rand() + cos(2 * pi * i / N))
    y = a * (rand() + sin(2 * pi * i / N))
    z = a * rand()
    atm = Atom(12 * units.protonMass, x, y, z)
    alst.append(atm)

springs = [ ]
extended = alst + [ alst[0], ]
for i in range(N):
    atom1 = extended[i]
    atom2 = extended[i+1]
    stiffness = 400 * units.newton / units.meter
    springs.append(Spring(stiffness, atom1, atom2))

type = "S"
ghz = 2000

if type == "B":
    Motor = BoschMotor
    m = Motor(alst, 1.0e-16 * units.TorqueUnit, ghz)
elif type == "T":
    Motor = ThermostatMotor
    m = Motor(alst, 1.0e-16 * units.TorqueUnit, ghz)
elif type == "S":
    Motor = RotarySpeedController
    m = Motor(alst, 10000 * DT, ghz)

yyy = open("yyy", "w")
zzz = open("zzz", "w")

for i in range(10000):
    for a in alst:
        a.zeroForce()
    for s in springs:
        s.timeStep()
    m.timeStep()
    for a in alst:
        a.timeStep()
    if (i % 100) == 0:
        #print m.theta, m.omega, alst[0]
        p = alst[0].position
        yyy.write("%g %g\n" % (p.x.coefficient(), p.y.coefficient()))
        p = alst[N/2].position
        zzz.write("%g %g\n" % (p.x.coefficient(), p.y.coefficient()))

yyy.close()
zzz.close()

print "Gnuplot command:   plot \"yyy\" with lines, \"zzz\" with lines"
