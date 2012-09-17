#! /usr/bin/python

import os
import sys
import re
from Numeric import *
from LinearAlgebra import *

nampat = re.compile("([A-Z][a-z]?[+=-][A-Z][a-z]?[+=-][A-Z][a-z]?)\.1\.log")
thetapat = re.compile(" INPUT CARD\> *theta *= *([\d\.-]+)")
engpat = re.compile(" FINAL U-B3LYP ENERGY IS +([\d\.-]+)")
hobond = re.compile("[A-Z+=]+\.")

Hartree = 4.3597482 # attoJoules
Bohr = 0.5291772083 # Angstroms

def fexist(fname):
    try: os.stat(fname)
    except OSError: return False
    return True

def findnext(f,pat):
    while 1:
        card = f.readline()
        if not card: return None
        m = pat.match(card)
        if m: return m

def ending(nam,suf):
    if suf==nam[-len(suf):]: return nam
    else: return nam+suf

def readangle(name):
    b=zeros((0,2),Float)
    for num in "123456789":
        fn='angles/'+name+'.'+num+'.log'
        if not fexist(fn): continue
        f=open(fn)
        theta = 2*(180-float(findnext(f,thetapat).group(1)))*pi/180.0
        try: e = float(findnext(f,engpat).group(1))*Hartree
        except AttributeError:
            # print '# bad energy in',name+'.'+num
            e=0.0
        if e != 0.0: b=concatenate((b,array(((theta,e),))),axis=0)
    return b

# return a function that evals a polynomial
def poly(c):
    def ep(x):
        b=0.0
        for q in c:
            b = q+x*b
        return b
    return ep

# The derivative of a polynomial
def dif(p):
    a=arange(len(p))[::-1]
    return (a*p)[:-1]

def newton(f,df,g):
    fg=f(g)
    while abs(fg)>1e-8:
        dfg=df(g)
        g=g-fg/dfg
        fg=f(g)
    return g

def quadmin(a,fa,b,fb,c,fc):
    num =  (b-a)**2 * (fb-fc) - (b-c)**2 * (fb-fa)
    den =  (b-a)    * (fb-fc) - (b-c)    * (fb-fa)
    if den == 0.0: return b
    return b - num / (2*den)

def golden(f,a,fa,b,fb,c,fc, tol=1e-2):
    if c-a<tol: return quadmin(a,fa,b,fb,c,fc)
    if c-b > b-a:
        new = b+0.38197*(c-b)
        fnew = f(new)
        if fnew < fb: return golden(f, b,fb, new,fnew, c,fc)
        else: return golden(f, a,fa, b,fb, new, fnew)
    else:
        new = a+0.61803*(b-a)
        fnew = f(new)
        if fnew < fb: return golden(f, a, fa, new,fnew, b,fb)
        else: return golden(f, new, fnew, b,fb, c,fc)

def ak(m):

    # find lowest point
    lo=m[0][1]
    ix=0
    for i in range(shape(m)[0]):
        if m[i][1] < lo:
            lo=m[i][1]
            ix=i
    # take it and its neighbors for parabolic interpolation
    a = m[ix-1][0]
    fa= m[ix-1][1]
    b = m[ix][0]
    fb= m[ix][1]
    c = m[ix+1][0]
    fc= m[ix+1][1]

    # the lowest point on the parabola
    th0 = quadmin(a,fa,b,fb,c,fc)

    # its value via Lagrange's formula
    eth0 = (fa*((th0-b)*(th0-c))/((a-b)*(a-c)) +
           fb*((th0-a)*(th0-c))/((b-a)*(b-c)) +
           fc*((th0-a)*(th0-b))/((c-a)*(c-b)))

    # adjust points to min of 0
    m=m-array([0.0,eth0])

    fa= m[ix-1][1]
    fb= m[ix][1]
    fc= m[ix+1][1]

    # stiffness, interpolated between two triples of points
    # this assumes equally spaced abcissas
    num = (b - a)*fc + (a - c)*fb + (c - b)*fa
    den = (b - a)* c**2  + (a**2  - b**2 )*c + a*b**2  - a**2 * b
    Kth1 = 200.0 * num / den

    ob = b
    if th0>b: ix += 1
    else: ix -= 1
    a = m[ix-1][0]
    fa= m[ix-1][1]
    b = m[ix][0]
    fb= m[ix][1]
    c = m[ix+1][0]
    fc= m[ix+1][1]
    num = (b - a)*fc + (a - c)*fb + (c - b)*fa
    den = (b - a)* c**2  + (a**2  - b**2 )*c + a*b**2  - a**2 * b
    Kth2 = 200.0 * num / den

    Kth = Kth1 + (Kth2-Kth1)*(th0-ob)/(b-ob)

    return th0, Kth

for fn in os.listdir('angles'):
    m=nampat.match(fn)
    if not m: continue
    name=m.group(1)
    m=readangle(name)
##     x=m[:,0]
##     xn=1.0
##     a=zeros((shape(m)[0],5),Float)
##     for i in range(5):
##         a[:,4-i]=xn
##         xn=x*xn
##     b=m[:,1]
##     coef, sosr, rank, svs = linear_least_squares(a,b)
##     d2f=poly(dif(dif(coef)))
##     nx = newton(poly(dif(coef)), d2f, 1.5)
##     print name, 'theta0=', nx, 'Ktheta=', d2f(nx)


    # find lowest point
    lo=m[0][1]
    ix=0
    for i in range(shape(m)[0]):
        if m[i][1] < lo:
            lo=m[i][1]
            ix=i

    # take it and its neighbors for parabolic interpolation

    if ix==0: ix=1
    if ix>len(m)-2: ix=len(m)-2

    m2=m[ix-1:ix+2]

    x=m2[:,0]
    xn=1.0
    a=zeros((3,3),Float)

    for i in [2,1,0]:

        a[:,i]=xn

        xn=x*xn
    b=m2[:,1]
    coef, sosr, rank, svs = linear_least_squares(a,b)
    d2f=poly(dif(dif(coef)))
    nx = newton(poly(dif(coef)), d2f, m2[1,0])
    print name, 'theta0=', nx, 'Ktheta=', d2f(nx)
