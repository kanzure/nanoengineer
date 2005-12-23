#!/usr/bin/python

# Refer to http://tinyurl.com/8zl86, the 22 Dec discussion about
# rotary motors.

from math import pi, cos, sin
import random
import units


DT = 1.e-16 * units.second
SPRING_STIFFNESS = 10 * units.newton / units.meter

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

class BoschMotor:

    def __init__(self, atomlist, torque, gigahertz):
        speed = (2 * pi * 1.e9 * units.AngularVelocityUnit) * gigahertz
        print "target speed", speed
        assert units.TorqueUnit.unitsMatch(torque)
        assert units.AngularVelocityUnit.unitsMatch(speed)
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
        axis = axis.normalize()
        # at this point, axis is dimensionless and unit-length
        self.axis = axis
        atomsMomentOfInertia = 0. * units.MomentOfInertiaUnit
        for atom in atomlist:
            spoke = atom.position - center
            r = spoke.cross(axis).length()
            atomsMomentOfInertia += atom.mass * r**2
        flywheelMomentOfInertia = 10 * atomsMomentOfInertia
        self.momentOfInertia = atomsMomentOfInertia + flywheelMomentOfInertia

        #
        #   There REALLY IS a criterion for numerical stability!
        #
        ratio = (DT * torque) / (self.momentOfInertia * speed)
        #if False:
        if abs(ratio) > 0.3:
            # The C code must also throw an exception or do whatever is
            # the equivalent thing at this point.
            raise Exception, "torque-to-speed ratio is too high"

        self.anchors = anchors = [ ]
        for atom in atomlist:
            x = atom.position - center
            u = axis.scale(x.dot(axis))
            v = x - u
            w = axis.cross(v)
            def getAnchor(theta):
                # be able to rotate the anchor around the axis
                theta /= units.radian
                return u + v.scale(cos(theta)) + w.scale(sin(theta))
            anchors.append(getAnchor)
        self.stallTorque = torque
        self.speed = speed
        self.omega = 0. * units.radian / units.second
        self.theta = 0. * units.radian

    def timeStep(self):
        # assume that any interatomic forces have already been computed
        # and are represented in the "force" attribute of each atom
        # calculate positions of each anchor, and spring force to atom
        atoms, anchors, center = self.atoms, self.anchors, self.center
        atomTorqueOnFlywheel = 0. * units.TorqueUnit
        for i in range(len(atoms)):
            atom = atoms[i]
            anchor = anchors[i](self.theta)
            f = (atom.position - anchor).scale(SPRING_STIFFNESS)
            atom.force -= f
            # use f to compute torque atom applies to flywheel
            r = atom.position - center
            T = r.cross(f).scale(units.radian)
            atomTorqueOnFlywheel += self.axis.dot(T)
        controlTorque = self.torqueFunction()
        self.torque = torque = controlTorque + atomTorqueOnFlywheel

        # iterate equations of motion
        self.theta += DT * self.omega
        self.omega += DT * torque / self.momentOfInertia

    def torqueFunction(self):
        # The Bosch model
        return (1.0 - self.omega / self.speed) * self.stallTorque

class DrexlerSwMotor(BoschMotor):
    def torqueFunction(self):
        def Sw(x):
            if x <= 0:
                return 1.
            elif x >= 1:
                return 0.
            return (.5/pi) * cos(2*pi*(x-.25)) - x + 1
        return self.stallTorque * Sw(self.omega / self.speed)

class ThermostatMotor(BoschMotor):
    def torqueFunction(self):
        if self.omega < self.speed:
            return self.stallTorque
        return 0. * units.TorqueUnit

#Motor = BoschMotor
#Motor = DrexlerSwMotor
Motor = ThermostatMotor

################################################

N = 3
alst = [ ]
for i in range(N):
    a = 3 * units.angstrom
    atm = Atom(12 * units.protonMass,
               (1. - 2. * random.random()) * a,
               (1. - 2. * random.random()) * a,
               0.1 * (1. - 2. * random.random()) * a)
    alst.append(atm)

m = Motor(alst, 1.0e-16 * units.TorqueUnit, 2.0e4)

for i in range(1000):
    for a in alst:
        a.zeroForce()
    m.timeStep()
    for a in alst:
        a.timeStep()
    print m.theta, m.omega, m.torque
    #print "---", alst[0]
