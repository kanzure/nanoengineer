# Copyright (c) 2006 Nanorex, Inc.  All rights reserved.
'''
SurfaceChunks.py -- define a new whole-chunk display mode,
which uses Oleksandr's new code to display a chunk as a surface in the chunk's color.

$Id$

See also CylinderChunks.py for comparison.
'''

__author__ = 'bruce'

import drawer
import geometry
from VQT import * # includes Numeric Python functions, like argmax and argmin
from debug import print_compact_traceback
from displaymodes import ChunkDisplayMode
import env
from constants import ave_colors
from constants import diTrueCPK
from prefs_constants import atomHighlightColor_prefs_key
from qt import QApplication, Qt, QCursor
from HistoryWidget import redmsg, orangemsg, greenmsg

chunkHighlightColor_prefs_key = atomHighlightColor_prefs_key # initial kluge

class Interval: 

    def __init__(self, *args):
        """interval constructor"""
        self.min = 0
        self.max = 0
        if len(args) == 0:
            pass
        if len(args) == 2:
            self.min, self.max = args
    def __str__(self):
        """returns the interval in a textual form"""
        s = ""
        s += "%s " % self.min
        s += "%s " % self.max
        return s
        
    def Empty(self):
        """clear interval"""
        self.min = 1000000   
        self.max = -1000000   

    def Center(self):
        """calculate center"""
        return (self.max + self.min) / 2   
  
    def Extent(self):
        """calculate extent"""
        return (self.max - self.min) / 2   

    def Point(self, u):
        """calculate point"""
        return (1 - u) * self.min + u * self.max  

    def Normalize(self, u):
        """normalization"""
        return (u - self.min) / (self.max - self.min)  

    def Contains(self, p):
        """interval contains point"""
        return p >= self.min and p <= self.max  

    def Enclose(self, p):
        """adjust interval"""
        if (p < self.min): 
            self.min = p;
        if (p > self.max): 
            self.max = p;

class Box: 

    def __init__(self, *args):
        """box constructor"""
        self.x = Interval()
        self.y = Interval()       
        self.z = Interval()      
        if len(args) == 0:
            pass
        if len(args) == 3:
            self.x, self.y, self.z = args
 
    def __str__(self):
        """returns the box in a textual form"""
        s = ""
        s += "%s " % self.x
        s += "%s " % self.y
        s += "%s " % self.z
        return s
        
    def Empty(self):
        """clear box"""
        self.x.Empty()   
        self.y.Empty()  
        self.z.Empty()          

    def Center(self):
        """calculate center"""
        return Triple(self.x.Center(),self.y.Center(),self.z.Center())
    
    def Min(self):
        """calculate min"""
        return Triple(self.x.min,self.y.min,self.z.min)

    def Max(self):
        """calculate max"""
        return Triple(self.x.max,self.y.max,self.z.max)

    def Extent(self):
        """calculate extent"""
        return Triple(self.x.Extent(),self.y.Extent(),self.z.Extent())

    def Contains(self, p):
        """box contains point"""
        return self.x.Contains(p.x) and self.y.Contains(p.y) and self.z.Contains(p.z)  

    def Enclose(self, p):
        """adjust box"""
        self.x.Enclose(p.x)
        self.y.Enclose(p.y)
        self.z.Enclose(p.z)
        
class Triple:

    def __init__(self, *args):
        """vector constructor"""
        self.x = 0
        self.y = 0
        self.z = 0
        if len(args) == 0:
            pass
        if len(args) == 1:
            if isinstance(args[0], types.InstanceType):
                self.x = args[0].x
                self.y = args[0].y
                self.z = args[0].z
            elif isinstance(args[0], types.ListType):
                self.x = args[0][0]
                self.y = args[0][1]
                self.z = args[0][2]
            else:    
                self.x = args[0]
                self.y = args[0]
                self.z = args[0]
        if len(args) == 2:
            self.x = args[1][0] - args[0][0]
            self.y = args[1][1] - args[0][1]
            self.z = args[1][2] - args[0][2]
        if len(args) == 3:
            self.x, self.y, self.z = args 

    def __str__(self):
        """returns the triple in a textual form"""
        s = ""
        s += "%s " % self.x
        s += "%s " % self.y
        s += "%s " % self.z
        return s
        
    def Len2(self):
        """square of vector length"""
        return self.x * self.x + self.y * self.y + self.z * self.z    

    def Len(self):
        """vector length"""
        return math.sqrt(self.Len2())
    
    def Normalize(self):
        """normalizes vector to unit length"""
        length = self.Len();
        self.x /= length
        self.y /= length
        self.z /= length
        return self    

    def Greatest(self):
        """calculate greatest value"""
        if self.x > self.y:
            if self.x > self.z:
                return self.x
            else:
                return self.z
        else:    
            if self.y > self.z:
                return self.y
            else:
                return self.z  

    def __add__( self, rhs ):
        """operator a + b"""
        t = Triple(rhs)
        return Triple(self.x + t.x, self.y + t.y, self.z + t.z)
    
    def __radd__( self, lhs ):
        """operator b + a"""
        t = Triple(lhs)
        t.x += self.x
        t.y += self.y
        t.z += self.z
        return t    

    def __sub__( self, rhs ):
        """operator a - b"""
        t = Triple(rhs)
        return Triple(self.x - t.x, self.y - t.y, self.z - t.z)
    
    def __rsub__( self, lhs ):
        """operator b - a"""
        t = Triple(lhs)
        t.x -= self.x
        t.y -= self.y
        t.z -= self.z
        return t    

    def __mul__( self, rhs ):
        """operator a * b"""
        t = Triple(rhs)
        return Triple(self.x * t.x, self.y * t.y, self.z * t.z)    

    def __rmul__( self, lhs ):
        """operator b * a"""
        t = Triple(lhs)
        t.x *= self.x
        t.y *= self.y
        t.z *= self.z
        return t    

    def __div__( self, rhs ):
        """operator a / b"""
        t = Triple(rhs)
        return Triple(self.x / t.x, self.y / t.y, self.z / t.z)
    
    def __rdiv__( self, lhs ):
        """operator b / a"""
        t = Triple(lhs)
        t.x /= self.x
        t.y /= self.y
        t.z /= self.z
        return t    

    def __mod__( self, rhs ):
        """operator a % b (scalar product)"""
        r = self.x * rhs.x + self.y * rhs.y + self.z * rhs.z
        return r    

    def __neg__( self):
        """operator -a"""
        return Triple(-self.x, -self.y, -self.z)

class Surface: 

    def __init__(self):
        """surface constructor"""
       
        self.spheres = []
	self.radiuses = []
        
        self.box = Box()
        self.box.Empty()
                    
    def Predicate(self, p):
        """calculate omega function:
           positive inside molecula,
           equal to zero on the boundary,
           negative outside"""
        om = 0.0
        #  calculate omega for all moleculas 
        for i in range(len(self.spheres)):
            t = p - self.spheres[i] 
            r = self.radiuses[i] 
            s = (r * r - t.x * t.x - t.y * t.y - t.z * t.z) / (r + r)
            if i == 0:
                om = s
            else:
                if om < s: 
                    om = s
        return om     
    
    def SurfaceTriangles(self, trias):
        nt = len(trias)
        n = 2   #  number of iterations
        for i in range(n):
            for j in range(nt):
                pn = []
                t = trias[j]
                for k in range(3):
                    p = Triple(t[k][0],t[k][1],t[k][2])
                    n = Triple(-2 * p.x, -2 * p.y, -2 * p.z)
                    n.Normalize()
                    om = self.Predicate(p)
                    if om < -1.0 : om = -1.0
                    pn.append(p - 0.5 * om * n)
                t0 = (pn[0].x, pn[0].y, pn[0].z)    
                t1 = (pn[1].x, pn[1].y, pn[1].z)    
                t2 = (pn[2].x, pn[2].y, pn[2].z)    
                trias[j] = (t0, t1, t2) 
        return trias        

    def SurfaceNormals(self, trias):
	normals = []
	for t in trias:
            v0 = V(t[1][0] - t[0][0], t[1][1] - t[0][1], t[1][2] - t[0][2])
            v1 = V(t[2][0] - t[0][0], t[2][1] - t[0][1], t[2][2] - t[0][2])
	    n = cross(v0, v1)
	    nt = (n[0], n[1], n[2]) 
	    normals.append((nt, nt, nt))
	return normals    
	
class SurfaceChunks(ChunkDisplayMode):
    "example chunk display mode, which draws the chunk as a surface, aligned to the chunk's axes, of the chunk's color"
    mmp_code = 'srf' # this must be a unique 3-letter code, distinct from the values in constants.dispNames or in other display modes
    disp_label = 'SurfaceChunks' # label for statusbar fields, menu text, etc
    icon_name = "displaySurface.png"
    hide_icon_name = "displaySurface-hide.png"
    featurename = "Set Display Surface" #mark 060611
    cmdname = greenmsg("Set Display Surface: ") # Mark 060621.
    ##e also should define icon as an icon object or filename, either in class or in each instance
    ##e also should define a featurename for wiki help
    def drawchunk(self, glpane, chunk, memo, highlighted):
        """Draw chunk in glpane in the whole-chunk display mode represented by this ChunkDisplayMode subclass.
        Assume we're already in chunk's local coordinate system
        (i.e. do all drawing using atom coordinates in chunk.basepos, not chunk.atpos).
           If highlighted is true, draw it in hover-highlighted form (but note that it may have
        already been drawn in unhighlighted form in the same frame, so normally the highlighted form should
        augment or obscure the unhighlighted form).
           Draw it as unselected, whether or not chunk.picked is true. See also self.drawchunk_selection_frame.
        (The reason that's a separate method is to permit future drawing optimizations when a chunk is selected
        or deselected but does not otherwise change in appearance or position.)
           If this drawing requires info about chunk which it is useful to precompute (as an optimization),
        that info should be computed by our compute_memo method and will be passed as the memo argument
        (whose format and content is whatever self.compute_memo returns). That info must not depend on
        the highlighted variable or on whether the chunk is selected.
	"""
        if not chunk.atoms:
            return
        pos, radius, color, tm, nm = memo
        if highlighted:
            color = ave_colors(0.5, color, env.prefs[chunkHighlightColor_prefs_key]) #e should the caller compute this somehow?
	# THIS IS WHERE OLEKSANDR SHOULD CALL HIS NEW CODE TO RENDER THE SURFACE (NOT CYLINDER).
	#   But if this requires time-consuming computations which depend on atom positions (etc) but not on point of view,
	# those should be done in compute_memo, not here, and their results will be passed here in the memo argument.
	# (This method drawchunk will not be called on every frame, but it will usually be called much more often than compute_memo.)
	#   For example, memo might contain a Pyrex object pointer to a C object representing some sort of mesh,
	# which can be rendered quickly by calling a Pyrex method on it.
        drawer.drawsurface(color, pos, radius, tm, nm)
        return
    def drawchunk_selection_frame(self, glpane, chunk, selection_frame_color, memo, highlighted):
        """Given the same arguments as drawchunk, plus selection_frame_color, draw the chunk's selection frame.
        (Drawing the chunk itself as well would not cause drawing errors
         but would presumably be a highly undesirable slowdown, especially if redrawing
         after selection and deselection is optimized to not have to redraw the chunk at all.)
           Note: in the initial implementation of the code that calls this method,
        the highlighted argument might be false whether or not we're actually hover-highlighted.
        And if that's fixed, then just as for drawchunk, we might be called twice when we're highlighted,
        once with highlighted = False and then later with highlighted = True.
        """
        if not chunk.atoms:
            return
        pos, radius, color, tm, nm = memo
        color = selection_frame_color
        # make it a little bigger than the sphere itself
        alittle = 0.01
        # THIS IS WHERE OLEKSANDR SHOULD RENDER A "SELECTED" SURFACE, OR (PREFERABLY) A SELECTION WIREFRAME
        # around an already-rendered surface.
        # (For a selected chunk, both this and drawchunk will be called -- not necessarily in that order.)
        drawer.drawsurface_wireframe(color, pos, radius + alittle, tm, nm)
	return
    def compute_memo(self, chunk):
        """If drawing chunk in this display mode can be optimized by precomputing some info from chunk's appearance,
        compute that info and return it.
           If this computation requires preference values, access them as env.prefs[key],
        and that will cause the memo to be removed (invalidated) when that preference value is changed by the user.
           This computation is assumed to also depend on, and only on, chunk's appearance in ordinary display modes
        (i.e. it's invalidated whenever havelist is). There is not yet any way to change that,
        so bugs will occur if any ordinarily invisible chunk info affects this rendering,
        and potential optimizations will not be done if any ordinarily visible info is not visible in this rendering.
        These can be fixed if necessary by having the real work done within class Chunk's _recompute_ rules,
        with this function or drawchunk just accessing the result of that (and sometimes causing its recomputation),
        and with whatever invalidation is needed being added to appropriate setter methods of class Chunk.
        If the real work can depend on more than chunk's ordinary appearance can, the access would need to be in drawchunk;
        otherwise it could be in drawchunk or in this method compute_memo.
        """
        # for this example, we'll turn the chunk axes into a cylinder.
        # Since chunk.axis is not always one of the vectors chunk.evecs (actually chunk.poly_evals_evecs_axis[2]),
        # it's best to just use the axis and center, then recompute a bounding cylinder.
        if not chunk.atoms:
            return None
	
	# Put up hourglass cursor to indicate we are busy. Restore the cursor below. Mark 060621.
	QApplication.setOverrideCursor( QCursor(Qt.WaitCursor) )
	env.history.message(self.cmdname + "Computing surface. Please wait...") # Mark 060621.
	env.history.h_update() # Update history widget with last message. # Mark 060623.
	
        center = chunk.center
        points = chunk.atpos - center        
        bcenter = chunk.abs_to_base(center)
        rad = 0.0
	s = Surface()
	margin = 0
	for a in chunk.atoms.values():
	    dispjunk, ra = a.howdraw(diTrueCPK)
	    if ra > margin : margin = ra
	    s.radiuses.append(ra)
        for p in points:
            pt = Triple(p[0], p[1], p[2])
	    s.spheres.append(pt)
            r = p[0]**2+p[1]**2+p[2]**2
            if r > rad: rad = r
        rad = sqrt(rad)
        radius = rad + margin
	for i in range(len(points)):
	    s.spheres[i] /= radius
	    s.radiuses[i] /= radius
	color = chunk.color
        if color is None:
            color = V(0.5,0.5,0.5)
	#  create surface 
	level = 3
	if rad > 6 : level = 4
	ts =drawer.getSphereTriangles(level)
	tm = s.SurfaceTriangles(ts)
	nm = s.SurfaceNormals(tm)
	
	QApplication.restoreOverrideCursor() # Restore the cursor. Mark 060621.
	env.history.message(self.cmdname + "Done.") # Mark 060621.
	
        return (bcenter, radius, color, tm, nm)
    
    pass # end of class SurfaceChunks

ChunkDisplayMode.register_display_mode_class(SurfaceChunks)

# end
