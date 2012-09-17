# Copyright 2005 Nanorex, Inc.  See LICENSE file for details.
"""Physical units for calculations

Physical quantities are represented here as dictionaries. One key is
'coefficient', the other keys are metric units like 'm', 'sec', 'kg'.
The value for each dimension key is the power to which that unit is
raised. For instance, the representation for a newton is {'sec': -2,
'kg': 1, 'm': 1, 'coefficient': 1.0}.

When quantities are multiplied or divided, the powers of units are
correctly maintained. If one unit ends up being raised to a zeroth
power, that unit is discarded in the product or ratio. If a result is
dimensionless, just return a float.

There are also some handy units and conversions at the bottom of the
file.
"""

import types

coeff = 'coefficient'
class UnitsMismatch(Exception):
    pass

class Quantity:
    def __init__(self,stuff,units=None):
        if units == None:
            stuff = stuff.copy()
            c = stuff[coeff]
            del stuff[coeff]
            self.stuff = stuff
        else:
            c = 1. * stuff
            self.stuff = units.copy()
        for k in self.stuff.keys():
            if self.stuff[k] == 0:
                del self.stuff[k]
        self.stuff[coeff] = c
    def __repr__(self):
        str = '<%g' % self.stuff[coeff]
        for k in self.stuff.keys():
            if k != coeff:
                str = str + ' ' + k
                if self.stuff[k] != 1:
                    str = str + '^' + `self.stuff[k]`
        return str + '>'
    def __add__(self, other):
        self.testUnitsMatch(other)
        stuff = self.stuff.copy()
        stuff[coeff] += other.stuff[coeff]
        return Quantity(stuff)
    def __neg__(self):
        stuff = self.stuff.copy()
        stuff[coeff] = -stuff[coeff]
        return Quantity(stuff)
    def __sub__(self, other):
        return self + (-other)
    def __cmp__(self, other):
        self.testUnitsMatch(other)
        return cmp(self.stuff[coeff], other.stuff[coeff])
    def __mul__(self, other):
        if type(other) in (types.IntType, types.FloatType, types.ComplexType):
            stuff = self.stuff.copy()
            stuff[coeff] = other * stuff[coeff]
            return Quantity(stuff)
        if not isinstance(other, Quantity):
            raise UnitsMismatch, repr(self) + " * " + repr(other)
        stuff = self.stuff.copy()
        for k in other.stuff.keys():
            if k != coeff:
                if stuff.has_key(k):
                    stuff[k] += other.stuff[k]
                    if abs(stuff[k]) < 1.0e-8:
                        del stuff[k]
                else:
                    stuff[k] = other.stuff[k]
        stuff[coeff] *= other.stuff[coeff]
        if len(stuff.keys()) == 1:
            return stuff[coeff]
        else:
            return Quantity(stuff)
    def __rmul__(self, other):
        return self * other
    def __div__(self, other):
        return self * (other ** -1)
    def __rdiv__(self, other):
        return (self ** -1) * other
    def __pow__(self, z):
        stuff = self.stuff.copy()
        for k in stuff.keys():
            if k != coeff:
                stuff[k] = z * stuff[k]
        stuff[coeff] = stuff[coeff] ** z
        return Quantity(stuff)
    def coefficient(self):
        return self.stuff[coeff]
    def unitsMatch(self, other):
        if not isinstance(other, Quantity):
            return False
        otherkeys = other.stuff.keys()
        for k in self.stuff.keys():
            if k not in otherkeys:
                return False
            if k != coeff and self.stuff[k] != other.stuff[k]:
                return False
        return True
    def testUnitsMatch(self, other):
        if not self.unitsMatch(other):
            raise UnitsMismatch, repr(self) + " mismatch " + repr(other)

# Lotsa good stuff on units and measures at:
# http://aurora.rg.iupui.edu/UCUM/UCUM-tab.html

### Fundamental units
meter = Quantity(1,{'m':1})
kilogram = Quantity(1,{'kg':1})
second = Quantity(1,{'sec':1})
coulomb = Quantity(1,{'C':1})
radian = Quantity(1,{'rad':1})

Kilo = 1.e3
Mega = 1.e6
Giga = 1.e9
Tera = 1.e12
Centi = 1.e-2
Milli = 1.e-3
Micro = 1.e-6
Nano = 1.e-9
Pico = 1.e-12
Femto = 1.e-15
Atto = 1.e-18

### Conveniences and metric prefixes
meter2 = meter * meter
meter3 = meter2 * meter

# don't know the official metric names for these, if such exist
speed = meter / second
acceleration = speed / second
density = kilogram / meter3

liter = Milli * meter3
newton = kilogram * acceleration
joule = newton * meter
watt = joule / second
ampere = coulomb / second
volt = joule / coulomb
ohm = volt / ampere
farad = coulomb / volt
weber = volt * second
tesla = weber / meter2
pascal = newton / meter2
henry = weber / ampere

km = Kilo * meter
cm = Centi * meter
mm = Milli * meter
um = Micro * meter
nm = Nano * meter

gram = Milli * kilogram
mgram = Micro * kilogram
ugram = Nano * kilogram

msec = Milli * second
usec = Micro * second
nsec = Nano * second
psec = Pico * second
fsec = Femto * second

uF = Micro * farad
nF = Nano * farad
pF = Pico * farad

mH = Milli * henry
uH = Micro * henry
nH = Nano * henry

Kohm = Kilo * ohm
Mohm = Mega * ohm

### Some English measures
inch = .0254 * meter
foot = 12 * inch
yard = 3 * foot
furlong = 660 * foot
mile = 5280 * foot

gallon = 3.79 * liter
quart = .25 * gallon
pint = .5 * quart
cup = .5 * pint
fluid_ounce = .125 * cup
tablespoon = .5 * fluid_ounce
teaspoon = tablespoon / 3.

minute = 60 * second
hour = 60 * minute
day = 24 * hour
year = 365.25 * day
# There is some disagreement on years. There are Julian years (this is
# that), Gregorian years (365.2425), and tropical years (365.24219).

angstrom = 1.e-10 * meter

protonMass = 1.672621e-27 * kilogram
MomentOfInertiaUnit = kilogram * meter2
TorqueUnit = radian * newton * meter
AngularVelocityUnit = radian / second

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

ZERO_POSITION = Vector(0. * meter,
                       0. * meter,
                       0. * meter)
ZERO_VELOCITY = Vector(0. * meter / second,
                       0. * meter / second,
                       0. * meter / second)
ZERO_FORCE = Vector(0. * newton,
                    0. * newton,
                    0. * newton)
ZERO_TORQUE = Vector(0. * TorqueUnit,
                     0. * TorqueUnit,
                     0. * TorqueUnit)
