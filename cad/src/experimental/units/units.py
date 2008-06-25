# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
units.py - physical units for calculations

$Id$

When quantities are multiplied or divided, the powers of units are
correctly maintained. If one unit ends up being raised to a zeroth
power, that unit is discarded in the product or ratio. If there are
no units left at all, i.e. the result is dimensionless, just return
a float.

Many physical formulas apply transcendental functions to dimensionless
ratios of quantities. For instance, the voltage across a discharging
capacitor is v0*exp(-t/(R*C)), where t, R, and C have dimensions
(seconds, ohms, and farads), but the ratio is dimensionless. So
returning a float in such cases is a desirable behavior.

There are also some handy units and conversions at the bottom of the
file.
"""

__author__ = "Will" # see README for more info

import types

def isnumber(x):
    if type(x) in (types.IntType, types.FloatType):
        return 1
    return 0

class UnitsMismatch(Exception):
    pass

class Quantity:
    def __init__(self,coeff,units,name=None):
        self.coeff = 1. * coeff
        self.units = units.copy()
        if name != None:
            self.name = name
    def __repr__(self):
        str = '<'
        try:
            str = str + self.name + ' '
        except AttributeError:
            pass
        str = str + '%g' % self.coeff
        for k in self.units.keys():
            str = str + ' ' + k
            if self.units[k] != 1:
                str = str + '^' + repr(self.units[k])
        return str + '>'

    def __abs__(self):
        return Quantity(abs(self.coeff), self.units.copy())

    def __neg__(self):
        return Quantity(-self.coeff, self.units.copy())

    def __cmp__(self,other):
        self.unitsMatch(other)
        return cmp(self.coeff, other.coeff)

    def __add__(self,other):
        self.unitsMatch(other)
        units = self.units.copy()
        return Quantity(self.coeff + other.coeff,
                        units)
    def __sub__(self,other):
        self.unitsMatch(other)
        units = self.units.copy()
        return Quantity(self.coeff - other.coeff,
                        units)
    def __mul__(self,other):
        if isinstance(other, Quantity):
            c = 1. * self.coeff * other.coeff
            u = self.multUnits(other, 1)
            if u.keys() == [ ]:
                return c
            else:
                return Quantity(c, u)
        elif isnumber(other):
            return Quantity(other * self.coeff, self.units)
        else:
            raise RuntimeError
    def __rmul__(self, other):
        return self.__mul__(other)
    def __div__(self,other):
        if isinstance(other, Quantity):
            return self * other.reciprocal()
        return Quantity(self.coeff / other, self.units)
    def __rdiv__(self, other):
        return other * self.reciprocal()
    def __pow__(self, n):
        if n == 0:
            return 1.
        if n < 0:
            return 1. / self.__pow__(-n)
        newcoeff = self.coeff ** n
        newunits = { }
        for k in self.units.keys():
            newunits[k] = self.units[k] * n
        return Quantity(newcoeff, newunits)
    def reciprocal(self):
        a = 1. / self.coeff
        b = self.units.copy()
        for k in b.keys():
            b[k] = -b[k]
        return Quantity(a, b)
    def inTermsOf(self, other):
        ratio = self / other
        if isnumber(ratio):
            str = "%g" % ratio
        else:
            str = repr(ratio)
        return str + " " + other.name + "s"
    def multUnits(self,other,n):
        units1 = self.units.copy()
        units2 = other.units.copy()
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
        otherkeys = other.units.keys()
        for k in self.units.keys():
            if k not in otherkeys:
                raise UnitsMismatch
            if k != "coeff" and self.units[k] != other.units[k]:
                raise UnitsMismatch

# Lotsa good stuff on units and measures at:
# http://aurora.rg.iupui.edu/UCUM/UCUM-tab.html

### Fundamental units
meter = m = Quantity(1,{'m':1},"meter")
kilogram = kg = Quantity(1,{'kg':1},"kilogram")
second = sec = Quantity(1,{'sec':1},"second")
coulomb = C = Quantity(1,{'C':1},"coulomb")
radian = rad = Quantity(1,{'rad':1},"radian")
steradian = srad = Quantity(1,{'sr':1},"steradian")

Deca = 10.0
Hecto = 100.0
Kilo = 1.e3
Mega = 1.e6
Giga = 1.e9
Tera = 1.e12
Peta = 1.e15
Exa = 1.e18
Zetta = 1.e21
Yotta = 1.e24

Deci = 0.1
Centi = 0.01
Milli = 1.e-3
Micro = 1.e-6
Nano = 1.e-9
Pico = 1.e-12
Femto = 1.e-15
Atto = 1.e-18
Zepto = 1.e-21
Yocto = 1.e-24

def _make(unit,name):
    unit.name = name
    return unit

### Conveniences and metric prefixes
squareMeter = _make(meter ** 2, "squareMeter")
cubicMeter = _make(meter ** 3, "cubicMeter")

# don't know the official metric names for these, if such exist
speed = meter / second
acceleration = speed / second
density = kilogram / cubicMeter

liter = L = _make(Milli * cubicMeter, "liter")
newton = N = _make(kilogram * acceleration, "newton")
joule = J = _make(newton * meter, "joule")
watt = W = _make(joule / second, "watt")
ampere = A = _make(coulomb / second, "ampere")
volt = V = _make(joule / coulomb, "volt")
ohm = _make(volt / ampere, "ohm")
farad = F = _make(coulomb / volt, "farad")
weber = Wb = _make(volt * second, "weber")
tesla = T = _make(weber / squareMeter, "tesla")
pascal = P = _make(newton / squareMeter, "pascal")
henry = H = _make(weber / ampere, "henry")

calorie = cal = _make(4.1868 * joule, "calorie")
kilocalorie = kcal = _make(Kilo * calorie, "kcal")

km = _make(Kilo * meter, "km")
cm = _make(Centi * meter, "cm")
mm = _make(Milli * meter, "mm")
um = _make(Micro * meter, "um")
nm = _make(Nano * meter, "nm")

are = _make(100 * squareMeter, "are")
hectare = _make(Hecto * are, "hectare")

gram = g = _make(Milli * kilogram, "gram")
mgram = mg = _make(Micro * kilogram, "mgram")
ugram = ug = _make(Nano * kilogram, "ugram")
metricTon = tonne = _make(Kilo * kilogram, "tonne")

A = _make(ampere, "A")
mA = _make(Milli * ampere, "mA")
uA = _make(Micro * ampere, "uA")
nA = _make(Nano * ampere, "nA")
pA = _make(Pico * ampere, "pA")

msec = _make(Milli * second, "msec")
usec = _make(Micro * second, "usec")
nsec = _make(Nano * second, "nsec")
psec = _make(Pico * second, "psec")
fsec = _make(Femto * second, "fsec")

ksec = _make(Kilo * second, "ksec")
Msec = _make(Mega * second, "Msec")
Gsec = _make(Giga * second, "Gsec")
Tsec = _make(Tera * second, "Tsec")

uF = _make(Micro * farad, "uF")
nF = _make(Nano * farad, "nF")
pF = _make(Pico * farad, "pF")

mH = _make(Milli * henry, "mH")
uH = _make(Micro * henry, "uH")
nH = _make(Nano * henry, "nH")

Kohm = _make(Kilo * ohm, "Kohm")
Mohm = _make(Mega * ohm, "Mohm")

# earthGravity = 9.8 * acceleration

gravitationalConstant = 6.67300e-11 * m**3 * kg**-1 * sec**-2
earthMass = 5.9742e24 * kg
earthRadius = 6378.1 * km
earthGravity = gravitationalConstant * earthMass / earthRadius**2

### Electrostatics
electronCharge = 1.60217733e-19 * coulomb
electrostaticConstant = 8.98755e9 * (N * m**2) / (coulomb**2)

### Time
minute = _make(60 * second, "minute")
hour = _make(60 * minute, "hour")
day = _make(24 * hour, "day")
week = _make(7 * day, "week")
year = _make(365.25 * day, "year")
# There is some disagreement on years. These are Julian years.
# Gregorian years are 365.2425 days, and tropical years are 365.24219
# days.
month = _make(year / 12, "month")
# 28, 29, 30, 31... obviously months must be approximate
decade = _make(10 * year, "decade")
century = _make(100 * year, "century")
millenium = _make(1000 * year, "millenium")

### English measures
inch = _make(.0254 * meter, "inch")
foot = _make(12 * inch, "foot")
yard = _make(3 * foot, "yard")
furlong = _make(660 * foot, "furlong")
mile = _make(5280 * foot, "mile")
squareMile = _make(mile ** 2, "squareMile")
acre = _make(43560 * foot**2, "acre")

MPH = _make(mile / hour, "MPH")
MPS = _make(mile / second, "MPS")

gallon = _make(3.79 * liter, "gallon")
quart = _make(.25 * gallon, "quart")
pint = _make(.5 * quart, "pint")
cup = _make(.5 * pint, "cup")
fluid_ounce = _make(.125 * cup, "fluid_ounce")
tablespoon = _make(.5 * fluid_ounce, "tablespoon")
teaspoon = _make(tablespoon / 3., "teaspoon")

# In the English system, should we express weights in terms of
# masses? Or should we multiply masses by 32 feet/sec^2?
ounce = oz = earthGravity * (28.35 * gram)
pound = lb = 16 * ounce
slug = 14.5939 * kg
stone = 6.3503 * kg

if __name__ == "__main__":

    def test1():
        lists = [ [ "Length",
                    inch,
                    furlong,
                    yard,
                    mile,
                    km
                    ],
                  [ "Area",
                    squareMeter,
                    acre,
                    hectare,
                    squareMile,
                    ],
                  [ "Volume",
                    gallon,
                    pint,
                    liter,
                    fluid_ounce,
                    tablespoon,
                    cubicMeter
                    ],
                  [ "Time",
                    day,
                    week,
                    decade,
                    century,
                    ksec,
                    Msec,
                    Gsec
                    ],
                  [ "Random",
                    newton,
                    volt,
                    ampere
                    ]
                  ]
        for lst in lists:
            print "----- " + lst.pop(0) + " -----"
            for i in range(len(lst)):
                for j in range(len(lst)):
                    if i != j:
                        print "one %s is %s" % (lst[i].name,
                                                lst[i].inTermsOf(lst[j]))
            print

    def test2():
        charge = mA * hour
        time = 1390.0 * second
        print charge / time

    test1()

# end
