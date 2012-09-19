#! /usr/bin/python

from math import *

r0=1
De=1
ks=100
beta = sqrt(ks/(2*De))

def morse(r):
    return De*(1-exp(-sqrt(ks/(2*De))*(r-r0)))**2
def lipp(r):
    return De*(1-exp(-ks*r0*(r-r0)**2/(2*De*r)))
def lippmor(r):
    if r<r0: return morse(r) - De
    else: return lipp(r) - De

def flp(x):
    k1              = 4.55328
    k2              = -8.24688
    k3              = 4.7872
    c               = 4.00777

    return c*(1/(k1*x**2+k2*x+k3)**16-1/(k1*x**2+k2*x+k3)**8)

def fmo(x):
    k1              = 2303.27
    k2              = 1.12845
    k3              = 1.45109
    c               = 59.1548
    k1              = 95.1566
    k2              = 1.3563
    k3              = 0.416429
    c               = 46234.9

    return k1*(c/(k2+x**2)**16-1/(k3+x**2)**8)

def flipmor(r):
    if r<1.03946: return fmo(r)
    else: return flp(r)

for i in range(600):
    x=i*0.001 + .9
    print x, flp(x), fmo(x)
#    print x, lippmor(x)

#    print x, flipmor(x),(flipmor(x+0.001)-flipmor(x-0.001))*1e3

## r<0, quartic
## a               = 2689.48          +/- 12.49        (0.4645%)
## b               = -11027.6         +/- 48.73        (0.4419%)
## c               = 16997.7          +/- 71.21        (0.419%)
## d               = -11670.6         +/- 46.22        (0.396%)
## e               = 3009.98          +/- 11.24        (0.3734%)

## r>0

## a               = 274.58           +/- 6.785        (2.471%)
## b               = -1349            +/- 29.58        (2.193%)
## c               = 2459.39          +/- 48.31        (1.964%)
## d               = -1970.22         +/- 35.02        (1.777%)
## e               = 584.236          +/- 9.506        (1.627%)

## for r>r0, using +/ a[i]/x^i

## a               = 214.69           +/- 1.915        (0.8918%)
## b               = -1092.98         +/- 9.376        (0.8578%)
## c               = 2068.38          +/- 17.13        (0.8281%)
## d               = -1721.46         +/- 13.83        (0.8036%)
## e               = 530.38           +/- 4.168        (0.7859%)
