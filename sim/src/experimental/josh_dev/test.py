
# Copyright 2005 Nanorex, Inc.  See LICENSE file for details.
from bondage import *
e,p,b = readmmp('ethane.mmp')
bondsetup(b)

dt=1e-16

massacc=array([dt*dt/elmass[x] for x in e])

n=p+massacc*force(p)

x= os.times()
## print 'running...',
## for i in xrange(100000):
##     o=p
##     p=n
##     n=2*p-o+massacc*force(p)

## print os.times()[0]-x[0]
