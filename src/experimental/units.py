'''mks.py - physical units for calculations

Physical quantities are represented here as dictionaries. One key
is 'coefficient', the other keys are metric units like 'm', 'sec',
'kg'. The value for each dimension key is the power to which that unit
is raised. For instance, force is in newtons, (kg m/sec^2), so the
representation for a newton is {'sec': -2, 'kg': 1, 'm': 1,
'coefficient': 1.0}.

When quantities are multiplied or divided, the powers of units are
correctly maintained. If one unit ends up being raised to a zeroth
power, that unit is discarded in the product or ratio. If there are
no units left at all, i.e. the result is dimensionless, just return
a float.

Many physical formulas apply transcendental functions to dimensionless
ratios of quantities. For instance, the voltage across a discharging
capacitor is exp(-t/(R*C)), where t, R, and C have dimensions
(seconds, ohms, and farads), but the ratio is dimensionless. So
returning a float in such cases is a desirable behavior.

There are also some handy units and conversions at the bottom of the
file.'''

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
    def __add__(self,other):
	self.testUnitsMatch(other)
	units = self.stuff.copy()
	del units[coeff]
	return Quantity(self.stuff[coeff] + other.stuff[coeff],
			units)
    def __sub__(self,other):
	self.testUnitsMatch(other)
	units = self.stuff.copy()
	del units[coeff]
	return Quantity(self.stuff[coeff] - other.stuff[coeff],
			units)
    def __mul__(self,other):
        if type(other) in (types.IntType, types.FloatType, types.ComplexType):
            stuff = self.stuff.copy()
            stuff[coeff] = other * stuff[coeff]
            return Quantity(stuff)
        if not isinstance(other, Quantity):
            raise UnitsMismatch, repr(self) + " * " + repr(other)
	c = 1. * self.stuff[coeff] * other.stuff[coeff]
	u = self.multUnits(other, 1)
	if u.keys() == [ ]:
	    return c
	else:
	    return Quantity(c, u)
    def __rmul__(self,other):
	a = self.stuff.copy()
	a[coeff] = other * a[coeff]
	return Quantity(a)
    def __div__(self,other):
	try:
	    c = 1. * self.stuff[coeff] / other.stuff[coeff]
	    u = self.multUnits(other, -1)
	except AttributeError:
	    c = 1. * self.stuff[coeff] / other
	    u = self.stuff.copy()
	    del u[coeff]
	if u.keys() == [ ]:
	    return c
	else:
	    return Quantity(c, u)
    def __rdiv__(self,other):
	a = self.stuff.copy()
	b = other / a[coeff]
	del a[coeff]
	for k in a.keys():
	    a[k] = -a[k]
	return Quantity(b, a)
    def __pow__(self, z):
        stuff = self.stuff.copy()
        for k in stuff.keys():
            if k != coeff:
                stuff[k] = z * stuff[k]
        stuff[coeff] = stuff[coeff] ** z
        return Quantity(stuff)
    def multUnits(self,other,n):
	units1 = self.stuff.copy()
	units2 = other.stuff.copy()
	del units1[coeff]
	del units2[coeff]
	for k in units1.keys():
	    if k in units2.keys():
		units1[k] = units1[k] + n * units2[k]
	for k in units2.keys():
	    if k not in units1.keys():
		units1[k] = n * units2[k]
	for k in units1.keys():
	    if units1[k] == 0:
		del units1[k]
	return units1
    def unitsMatch(self,other):
        if not isinstance(other, Quantity):
            return False
	otherkeys = other.stuff.keys()
	for k in self.stuff.keys():
	    if k not in otherkeys:
		return False
	    if k != coeff and self.stuff[k] != other.stuff[k]:
		return False
        return True
    def testUnitsMatch(self,other):
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
