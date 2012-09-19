# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details.
"""
SurfaceChunks.py -- define a new whole-chunk display mode,
which uses Oleksandr's new code to display a chunk as a surface in the chunk's color.

@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

See also CylinderChunks.py for comparison.

See renderSurface and drawsurface* in drawer.py for rendering code.

How to demo the pyrex/C code for SurfaceChunks
(which only computes the mesh -- it doesn't draw it):

see cad/src/experimental/oleksandr/README.txt.
"""

from numpy.oldnumeric import sqrt, pi, sin, cos
import types

from PyQt4.Qt import QApplication, Qt, QCursor

import foundation.env as env
from graphics.drawing.CS_draw_primitives import drawsurface
from graphics.drawing.CS_draw_primitives import drawsurface_wireframe
from graphics.drawing.shape_vertices import getSphereTriangles
from geometry.VQT import V, cross
from utilities.Log import greenmsg
from graphics.display_styles.displaymodes import ChunkDisplayMode

from utilities.constants import ave_colors
from utilities.constants import diTrueCPK
from utilities.prefs_constants import atomHighlightColor_prefs_key

_psurface_import_worked = False

#Flag that suppresses the console print that reports failed psurface import.
#The psurface feature (surface chunks display) is not a part of NE1 anymore
#by default (as of before 2008-02-15)
_VERBOSE_IMPORT_ERROR = False

_psurface_import_status_has_been_reported = False

def _report_psurface_import_status(): #bruce 080223; only run if feature is used, by default
    """
    Print whether import psurface succeeded, but only
    the first time this is called per session.
    """
    global _psurface_import_status_has_been_reported
    if not _psurface_import_status_has_been_reported:
        _psurface_import_status_has_been_reported = True
        if not _psurface_import_worked:
            print "psurface not imported, check if it has been built"
            print " (will use slow python version instead)"
        else:
            print "fyi: psurface import succeeded:", psurface
    return

try:
    import psurface
    _psurface_import_worked = True
except ImportError:
    if _VERBOSE_IMPORT_ERROR:
        _report_psurface_import_status()

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
        return sqrt(self.Len2())

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
        """make projection all points onto molecula"""
        self.colors = []
        self.points = []
        self.trias = []
        self.Duplicate(trias)
        self.SurfaceNormals()
        np = len(self.points)
        for j in range(np):
            p = self.points[j]
            pt = Triple(p[0],p[1],p[2])
            n = self.normals[j]
            nt = -Triple(n[0],n[1],n[2])
            nt.Normalize()
            om = self.Predicate(pt)
            if om < -2.0 : om = -2.0
            pn = pt - 0.5 * om * nt
            self.points[j] = (pn.x, pn.y, pn.z)
        return (self.trias, self.points, self.colors)

    def Duplicate(self, trias):
        """delete duplicate points"""
        eps = 0.0000001
        n = len(trias)
        n3 = 3 * n
        ia = []
        for i in range(n3):
            ia.append(i + 1)

        #find and mark duplicate points
        points = []
        for i in range(n):
            t = trias[i]
            points.append(Triple(t[0][0],t[0][1],t[0][2]))
            points.append(Triple(t[1][0],t[1][1],t[1][2]))
            points.append(Triple(t[2][0],t[2][1],t[2][2]))
        nb = 17
        #use bucket for increase speed
        bucket = Bucket(nb,points)
        for i in range(n3):
            p = points[i]
            v = bucket.Array(p)
            for jv in range(len(v)):
                j = v[jv]
                if i == j : continue
                if ia[j] > 0 :
                    pj = points[j]
                    if (p - pj).Len2() < eps :
                        ia[j] = - ia[i]
        #change array for points & normals
        #change index
        for i in range(n3):
            if ia[i] > 0 :
                self.points.append((points[i].x,points[i].y,points[i].z))
                ia[i] = len(self.points)
            else:
                ir = ia[i]
                if ir < 0 : ir = -ir
                ia[i] = ia[ir - 1]
        for i in range(n):
            self.trias.append((ia[3*i]-1,ia[3*i+1]-1,ia[3*i+2]-1))

    def SurfaceNormals(self):
        """calculate surface normals for all points"""
        normals = []
        for i in range(len(self.points)):
            normals.append(V(0.0,0.0,0.0))
        for i in range(len(self.trias)):
            t = self.trias[i]
            p0 = self.points[t[0]]
            p1 = self.points[t[1]]
            p2 = self.points[t[2]]
            v0 = V(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
            v1 = V(p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2])
            n = cross(v0, v1)
            normals[t[0]] += n
            normals[t[1]] += n
            normals[t[2]] += n
        self.normals = []
        for n in normals:
            self.normals.append((n[0],n[1],n[2]))
        return self.normals

    def CalculateTorus(self, a, b, u, v):
        """calculate point on torus"""
        pi2 = 2 * pi
        #transformation function - torus
        cf = cos(pi2*u)
        sf = sin(pi2*u)
        ct = cos(pi2*v)
        st = sin(pi2*v)
        #point on torus
        return Triple((a+b*ct)*cf, (a+b*ct)*sf, b*st)

    def TorusTriangles(self, a, b, n):
        """generate triangles on torus"""
        n6 = int(6*a*n)
        if (n6 == 0): n6 = 6
        n2 = int(6*b*n)
        if (n2 == 0): n2 = 6
        trias = []
        for i in range(n6):
            u0 = i / float(n6)
            u1 = (i +1) / float(n6)
            for j in range(n2):
                v0 = j / float(n2);
                v1 = (j + 1) / float(n2)

                p0 = self.CalculateTorus(a,b,u0,v0)
                p1 = self.CalculateTorus(a,b,u1,v0)
                p2 = self.CalculateTorus(a,b,u1,v1)
                p3 = self.CalculateTorus(a,b,u0,v1)

                t1 = ((p0.x,p0.y,p0.z),(p1.x,p1.y,p1.z),(p2.x,p2.y,p2.z))
                t2 = ((p0.x,p0.y,p0.z),(p2.x,p2.y,p2.z),(p3.x,p3.y,p3.z))

                trias.append(t1)
                trias.append(t2)
        return trias


class Bucket:

    def __init__(self, n, points):
        """bucket constructor"""
        self.n = n
        self.nn = n * n
        self.nnn = self.nn * n
        self.a = []
        for i in range(self.nnn):
            self.a.append([])
        count = 0
        for p in points:
            self.a[self.Index(p)].append(count)
            count += 1

    def Index(self, p):
        """calculate index in bucket for point p"""
        i = (int)(self.n * (p.x + 1) / 2)
        if i >= self.n : i = self.n - 1
        j = (int)(self.n * (p.y + 1) / 2)
        if j >= self.n : j = self.n - 1
        k = (int)(self.n * (p.z + 1) / 2)
        if k >= self.n : k = self.n - 1
        return i * self.nn + j * self.n + k

    def Array(self, p):
        """get array from bucket for point p"""
        return self.a[self.Index(p)]


class SurfaceChunks(ChunkDisplayMode):
    """
    example chunk display mode, which draws the chunk as a surface,
    aligned to the chunk's axes, of the chunk's color
    """
    # mmp_code must be a unique 3-letter code, distinct from the values in 
    # constants.dispNames or in other display modes
    mmp_code = 'srf' 
    disp_label = 'SurfaceChunks' # label for statusbar fields, menu text, etc
    icon_name = "modeltree/displaySurface.png"
    hide_icon_name = "modeltree/displaySurface-hide.png"
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
        drawsurface(color, pos, radius, tm, nm)
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
        drawsurface_wireframe(color, pos, radius + alittle, tm, nm)
        return
    def drawchunk_realtime(self, glpane, chunk, highlighted=False):
        """
        Draws the chunk style that may depend on a current view.
        piotr 080320
        """
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

        _report_psurface_import_status() # prints only once per session

        if _psurface_import_worked: # cpp surface stuff
            center = chunk.center
            bcenter = chunk.abs_to_base(center)
            rad = 0.0
            margin = 0
            radiuses = []
            spheres = []
            atoms = []
            coltypes = []
            for a in chunk.atoms.values():
                col = a.drawing_color()
                ii = 0
                for ic in range(len(coltypes)):
                    ct = coltypes[ic]
                    if ct == col:
                        break;
                    ii += 1
                if ii >= len(coltypes):
                    coltypes.append(col);
                atoms.append(ii)
                dispjunk, ra = a.howdraw(diTrueCPK)
                if ra > margin : margin = ra
                radiuses.append(ra)
                p = a.posn() - center
                spheres.append(p)
                r = p[0]**2+p[1]**2+p[2]**2
                if r > rad: rad = r
            rad = sqrt(rad)
            radius = rad + margin
            cspheres = []
            from utilities.debug_prefs import debug_pref, Choice_boolean_True
            use_colors = debug_pref("surface: use colors?", Choice_boolean_True) #bruce 060927 (old code had 0 for use_colors)
            for i in range(len(spheres)):
                st = spheres[i] / radius
                rt = radiuses[i] / radius
                # cspheres.append((st[0],st[1],st[2],rt,use_colors))
                cspheres.append((st[0],st[1],st[2],rt,atoms[i]))
            #cspheres.append((-0.3,0,0,0.3,1))
            #cspheres.append((0.3,0,0,0.3,2))
            color = chunk.drawing_color()
            if color is None:
                color = V(0.5,0.5,0.5)
            #  create surface
            level = 3
            if rad > 6 : level = 4
            ps = psurface
            # 0 - sphere triangles
            # 1 - torus rectangles
            # 2 - omega rectangles
            method = 2
            ((em,pm,am), nm) = ps.CreateSurface(cspheres, level, method)
            cm = []
            if True: # True for color
                for i in range(len(am)):
                    cm.append(coltypes[am[i]])
            else:
                for i in range(len(am)):
                    cm.append((0.5,0.5,0.5))
            tm = (em,pm,cm)
        else : # python surface stuff
            center = chunk.center
            bcenter = chunk.abs_to_base(center)
            rad = 0.0
            s = Surface()
            margin = 0
            for a in chunk.atoms.values():
                dispjunk, ra = a.howdraw(diTrueCPK)
                if ra > margin : margin = ra
                s.radiuses.append(ra)
                p = a.posn() - center
                s.spheres.append(Triple(p[0], p[1], p[2]))
                r = p[0]**2+p[1]**2+p[2]**2
                if r > rad: rad = r
            rad = sqrt(rad)
            radius = rad + margin
            for i in range(len(s.spheres)):
                s.spheres[i] /= radius
                s.radiuses[i] /= radius
            color = chunk.drawing_color()
            if color is None:
                color = V(0.5,0.5,0.5)
            #  create surface
            level = 3
            if rad > 6 : level = 4
            ts = getSphereTriangles(level)
            #ts = s.TorusTriangles(0.7, 0.3, 20)
            tm = s.SurfaceTriangles(ts)
            nm = s.SurfaceNormals()

        QApplication.restoreOverrideCursor() # Restore the cursor. Mark 060621.
        env.history.message(self.cmdname + "Done.") # Mark 060621.

        return (bcenter, radius, color, tm, nm)

    pass # end of class SurfaceChunks

ChunkDisplayMode.register_display_mode_class(SurfaceChunks)

# end
