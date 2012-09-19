# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$
"""

random point in n-dim-simplex, as n+1 vertex weights:

- random point in n-cube
- sort the coords
- replace each one, and a final added 1, by itself minus the prior one.

evidence: each ordering of cube coords corrs to a simplicial region of the cube;
the operation shifts that into a standard posn.

more evidence: the op appears to be volume-preserving (the sort is, the shears are -- those minus prior ones are shears)
and fair
and gets the right ineqs on result
so what else could it be? this might be a proof.

maybe Random(x,y,z) means the above for 3 vertices (of any affine type, incl vector or color or real or complex)?
then Random(0,1) is special case, assuming you know you mean Real not Int...

RandomChoice(green, red) has two values
RandomWeighting(green, red) is the above (point in simplex) (most useful for more vertices)

another poss meaning for RandomWeighting would be spherical - rand point on sphere...
but that's more natural when you do have a sphere or ball as your legal points, not a simplex!
So call that one something else and let it have different args.
