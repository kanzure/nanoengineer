#!/usr/bin/python

# Refer to http://tinyurl.com/8zl86, the 22 Dec discussion about
# rotary motors.

from math import pi, cos, sin
import random
import units

class Vector:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z
    def __repr__(self):
        return "[%s %s %s]" % (repr(self.x), repr(self.y), repr(self.z))
    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)
    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
    def __neg__(self, other):
        return Vector(-self.x, -self.y, -self.z)
    def scale(self, m):
        return Vector(self.x * m, self.y * m, self.z * m)
    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z
    def cross(self, other):
        return Vector(self.y * other.z - self.z * other.y,
                      self.z * other.x - self.x * other.z,
                      self.x * other.y - self.y * other.x)
    def length(self):
        return self.dot(self) ** .5
    def normalize(self):
        return self.scale(1. / self.length())

DT = 1.e-16 * units.second
PROTON_MASS = 1.672621e-27 * units.kilogram
ANGSTROM = 1.e-10 * units.meter
SPRING_STIFFNESS = 10 * units.newton / units.meter
MOMENT_OF_INERTIA_UNIT = units.kilogram * units.meter2
TORQUE_UNIT = units.radian * units.newton * units.meter
ANGULAR_VELOCITY_UNIT = units.radian / units.second

ZERO_POSITION = Vector(0. * units.meter,
                       0. * units.meter,
                       0. * units.meter)
ZERO_VELOCITY = Vector(0. * units.meter / units.second,
                       0. * units.meter / units.second,
                       0. * units.meter / units.second)
ZERO_FORCE = Vector(0. * units.newton,
                    0. * units.newton,
                    0. * units.newton)
ZERO_TORQUE = Vector(0. * TORQUE_UNIT,
                     0. * TORQUE_UNIT,
                     0. * TORQUE_UNIT)

class Atom:
    def __init__(self, mass, x, y, z):
        self.mass = mass
        self.position = Vector(x, y, z)
        self.velocity = ZERO_VELOCITY
        self.zeroForce()
    def zeroForce(self):
        self.force = ZERO_FORCE
    def __repr__(self):
        pos = self.position
        return "<%s %s>" % (repr(self.mass), repr(self.position))
    def timeStep(self):
        self.position += self.velocity.scale(DT)
        self.velocity += self.force.scale(DT / self.mass)

class Motor:

    def __init__(self, atomlist, torque, gigahertz):
        speed = (2 * pi * 1.e9 * ANGULAR_VELOCITY_UNIT) * gigahertz
        print "target speed", speed
        assert TORQUE_UNIT.unitsMatch(torque)
        assert ANGULAR_VELOCITY_UNIT.unitsMatch(speed)
        self.atoms = atomlist
        center = ZERO_POSITION
        for atm in atomlist:
            center += atm.position
        self.center = center = center.scale(1./len(atomlist))
        # Determine the direction of the axis. If the atoms are all
        # lying in a plane, this should be normal to the plane.
        axis = ZERO_POSITION
        extended = atomlist + [ atomlist[0], ]
        for i in range(len(atomlist)):
            u = extended[i].position - center
            v = extended[i+1].position - center
            axis += u.cross(v).scale(1./units.meter)
        axis = axis.normalize()
        # at this point, axis is dimensionless and unit-length
        self.axis = axis
        atomsMomentOfInertia = 0. * MOMENT_OF_INERTIA_UNIT
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
        atomTorqueOnFlywheel = 0. * TORQUE_UNIT
        for i in range(len(atoms)):
            atom = atoms[i]
            anchor = anchors[i](self.theta)
            f = (atom.position - anchor).scale(SPRING_STIFFNESS)
            atom.force -= f
            # use f to compute torque atom applies to flywheel
            r = atom.position - center
            T = r.cross(f).scale(units.radian)
            atomTorqueOnFlywheel += self.axis.dot(T)
        print atomTorqueOnFlywheel
        controlTorque = (1.0 - self.omega / self.speed) * self.stallTorque
        self.torque = torque = controlTorque + atomTorqueOnFlywheel

        # iterate equations of motion
        self.theta += DT * self.omega
        self.omega += DT * torque / self.momentOfInertia

################################################

N = 3
alst = [ ]
for i in range(N):
    a = 3 * ANGSTROM
    atm = Atom(12 * PROTON_MASS,
               (1. - 2. * random.random()) * a,
               (1. - 2. * random.random()) * a,
               0.1 * (1. - 2. * random.random()) * a)
    alst.append(atm)

m = Motor(alst, 1.0e-15 * TORQUE_UNIT, 2.0e4)

for i in range(100):
    for a in alst:
        a.zeroForce()
    m.timeStep()
    for a in alst:
        a.timeStep()
    print m.theta, m.omega, m.torque
    #print "---", alst[0]
