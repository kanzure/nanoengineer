# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
handles.py - graphical handles used in Extrude Mode.

Deprecated for new code, since they don't use the Selobj_API
used by most handle-like things.

@author: Bruce
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

TODO:

Needs cleanup.
"""

from numpy.oldnumeric import sqrt

from geometry.VQT import V
from geometry.VQT import vlen
from geometry.VQT import norm
from geometry.VQT import orthodist
from graphics.drawing.CS_draw_primitives import drawsphere
from utilities.constants import ave_colors
from utilities.constants import magenta
from utilities.constants import blue

class handleWithHandleSet:
    """
    used to wrap handles returned  a handleset, so they can use its methods
    """
    def __init__(self, handle, handleset, copy_id = None): 
        self.handle = handle
        self.handleset = handleset
        self.copy_id = copy_id
    def click(self): #e now leftDown, but later, "button press" leftUp
        self.handleset.click_handle( self.handle, self.copy_id)
    def move(self, motion):
        self.handleset.move_handle( self.handle, self.copy_id, motion )
    def __repr__(self):
        return "handleWithHandleSet( %r, %r, %r)" % (self.handle, self.handleset, self.copy_id)
    def __str__(self):
        return self.handleset.str_handle( self.handle, self.copy_id)
    def leftDown_status_msg(self):
        return self.handleset.leftDown_status_msg( self.handle, self.copy_id)
    pass

class HandleSet:
    """
    maintain a set of spheres, able to be intersected with a ray, or a 3d point
    """
    color = (0.5,0.5,0.5) # default color (gray50)
    radius_multiplier = 1.0 # this might be patched to some other value by our owner;
     # should affect all internal computations using radii, but not returned radii inside handle tuples ####NIM
    def __init__(self):
        self.origin = V(0,0,0) # changed  this only by certain subclasses, in practice
        self.handles = [] # list of (pos,radius,info) tuples
        # handlpos and maxradius are not used now, but might be used later to optimize this.
        self.handlpos = [] # list of their pos's (compare to singlpos in class Chunk (_recompute_singlpos))
        self.maxradius = 0.01 # not true, but best if it's always positive, I think
    #e to optimize, we might want a "compile" method which caches Array versions of these lists
    def addHandle(self, pos, radius, info):
        """
        add a handle of the given position, radius, and info,
        and return its index, unique in this Set
        """
        self.handles.append((pos,radius,info))
        self.handlpos.append(pos)
        if radius > self.maxradius:
            self.maxradius = radius
        return len(self.handles) # index of new handle #e needed?
    def compile(self): #e unused??
        pass #e cache Array versions of some of our lists
    def move(self, offset):
        self.origin = self.origin + offset
        ## warning: this would be wrong (due to destructive mod of a vector): self.origin += motion
    def draw(self, glpane, offset = V(0,0,0), color = None, info = {}): # this code is copied/modified into a subclass, sorry
        """
        draw our spheres (in practice we'll need to extend this for different sets...)
        """
##        self.radius_multiplier = 1.0 # this might be changed by certain subclass's process_optional_info method
##        self.process_optional_info(info) # might reset instvars that affect following code... (kluge?)
        color = color or self.color
        ##detailLevel = 0 # just an icosahedron
        detailLevel = 1 # easier to click on this way
        ##radius = 0.33 # the one we store might be too large? no, i guess it's ok.
        #e (i might prefer an octahedron, or a miniature-convex-hull-of-extrude-unit)
        offset = offset + self.origin
        radius_multiplier = self.radius_multiplier
        color = tuple(color) + (1.0,) ## experiment 050218: alpha factor #bruce 051230 moved outside of loop to fix bug 1250
        for (pos,radius,info) in self.handles:
            drawsphere(color, pos + offset, radius * radius_multiplier, detailLevel)
##    def process_optional_info(self, info):
##        "some subclasses should override this to let info affect draw method"
##        pass
    def findHandles_containing(self, point):
        """
        return a list of all the handles (in arbitrary order)
        which (as balls) contain the given 3d point
        """
        res = []
        for (pos,radius,info) in self.handles: #e revise this code if we cluster them, esp with bigger radius
            if vlen(point - pos) <= radius * self.radius_multiplier:
                res.append((pos,radius,info))
        return res
##    def findHandles_near(self, point, radius = None):
##        """return a list (in arbitrary order) of pairs (dist, handle) for all the handles
##           which are near the given point (within the given radius (default very large###e???),
##           *or* within their own sphere-radius). #### WRONG CODE
##        """
##        assert 0
    def findHandles_exact(self, p1, p2, cutoff = 0.0, backs_ok = 1, offset = V(0,0,0)):
        """
        @return: a list of (dist, handle) pairs, in arbitrary order, which
        includes, for each handle (spherical surface) hit by the ray  p1
        thru p2, its front-surface intersection with the ray, unless that has
        dist < cutoff and backs_ok, in which case include its back-surface
        intersection (unless *that* has dist < cutoff).
        """
        #e For now, just be simple, don't worry about speed.
        # Someday we can preprocess self.handlpos using Numeric functions,
        # like in nearSinglets and/or findSinglets
        # (I have untested prototype code for this in extrude-outs.py).
        hh = self.handles
        res = []
        v = norm(p2-p1)
        # is this modifying the vector in-place, causing a bug?? 
        ## offset += self.origin # treat our handles' pos as relative to this
        # I don't know, but one of the three instances of += was doing this!!!
        # probably i was resetting the atom or mol pos....
        offset = offset + self.origin # treat our handles' pos as relative to this
        radius_multiplier = self.radius_multiplier
        for (pos,radius,info) in hh:
            ## bug in this? pos += offset
            pos = pos + offset
            radius *= radius_multiplier
            dist, wid = orthodist(p1, v, pos)
            if radius >= wid: # the ray hits the sphere
                delta = sqrt(radius*radius - wid*wid)
                front = dist - delta # depth  p1 of front surface of sphere, where it's hit
                if front >= cutoff:
                    res.append((front,(pos,radius,info)))
                elif backs_ok:
                    back = dist + delta
                    if back >= cutoff:
                        res.append((back,(pos,radius,info)))
        return res
    def frontDistHandle(self, p1, p2, cutoff = 0.0, backs_ok = 1, offset = V(0,0,0), copy_id = None):
        """
        @return: None, or the frontmost (dist, handle) pair, as computed by
        findHandles_exact; but turn the handle into a pyobj for convenience of
        caller.
        """
        # check: i don't know if retval needs self.radius_multiplier...
        # review: will we need to let caller know whether it was the front or
        # back surface we hit? or even the exact position on the sphere? if
        # so, add more data to the returned pair.
        dhdh = self.findHandles_exact(p1, p2, cutoff, backs_ok, offset = offset)
        if not dhdh: return None
        dhdh.sort()
        (dist, handle0) = dhdh[0]
        handle = self.wrap_handle(handle0, copy_id)
        return (dist, handle)
    def wrap_handle(self, handle, copy_id):
        (pos,radius,info) = handle # check format
        return handleWithHandleSet( handle, self, copy_id = copy_id)
    def click_handle( self, handle, copy_id):
        "click one of our own handles; subclasses should override this"
        pass
    def move_handle( self, handle, copy_id, motion):
        "move one of our own handles (e.g. when it's dragged); subclasses should override this"
        pass
    def str_handle( self, handle, copy_id):
        "subclasses are encouraged to override this so it looks good in messages to the user"
        (pos,radius,info) = handle
        return "<handle pos=%r, radius=%3f, info=%r, in copy %r of %r>" % (pos,radius,info,copy_id,self)
    def leftDown_status_msg( self, handle, copy_id):
        "subclasses should override this"
        return ""
    def handle_setpos( self, ind, newpos):
        "patch our arrays to change pos of just one handle"
        (pos,radius,info) = self.handles[ind]
        pos = newpos
        self.handles[ind] = (pos,radius,info)
        self.handlpos[ind] = pos #e might fail if we ever make self.compile() do something
        pass
    pass

class draggableHandle_HandleSet(HandleSet):
    "a handleset, with behavior to let you drag the entire thing, and something else too" # used for "purple center"...
    def __init__(self, color = magenta, motion_callback = None, statusmsg = "draggable handle"):
        self.color = color
        self.motion_callback = motion_callback
        self.statusmsg = statusmsg
        HandleSet.__init__(self)
    def move_handle( self, handle, copy_id, motion):
        self.move(motion)
        if self.motion_callback:
            self.motion_callback(motion)
        return
    def leftDown_status_msg( self, handle, copy_id):
        return self.statusmsg
    pass

class repunitHandleSet(HandleSet): #e this really belongs in extrudeMode.py, not in this file
    "a handleset for an extrudeable unit, which lets copy_id specify which repunit is meant"
    def __init__(self, *args, **kws):
        self.target = kws.pop('target') # must be specified; the extrudeMode object we're helping to control
        HandleSet.__init__(self, *args, **kws)
    def move_handle( self, handle, copy_id, motion):
        self.target.drag_repunit(copy_id, motion)
    def hset_name(self, copy_id): #e move this name code to the hset itself
        if copy_id: 
            name = "repeat unit #%d" % copy_id
        else:
            name = "base unit"
        return name
    def str_handle( self, handle, copy_id):
        name = self.hset_name(copy_id)
        (pos,radius,info) = handle
        return "atom at pos=%r in %s" % (pos,name)
    def leftDown_status_msg( self, handle, copy_id):
        name = self.hset_name(copy_id)
        if copy_id:
            return "%s (can be dragged to change the offset)" % name
        else:
            return name # + " (can be dragged to move the entire model -- not implemented)"
        pass
    pass


class niceoffsetsHandleSet(HandleSet): #e this really belongs in extrudeMode.py, not in this file
    "a handleset for holding the set of nice offsets"
    #e in future, we can show things on mouseover, perhaps like:
    # mouseover of nice_offset handle will light up its two singlets;
    # mouseover of a singlet will light up the applicable other singlets
    # and nice_offset handles; etc.
    special_pos = V(0,0,0)
    special_color = blue
    def __init__(self, *args, **kws):
        self.target = kws.pop('target') # must be specified; the extrudeMode object we're helping to control
        HandleSet.__init__(self, *args, **kws)
    def leftDown_status_msg( self, handle, copy_id):
        (pos,radius,info) = handle
        i1,i2 = info
        # this text is meant for the present situation, where we jump on mousedown;
        # better behavior would be buttonlike (jump on mouseup, iff still over handle),
        # and the text should be adjusted when we implement that #e
        return "overlapped bondpoints base#%d and rep#%d" % (i1,i2)
    def click_handle( self, handle, copy_id):
        self.target.click_nice_offset_handle(handle)
##    def process_optional_info(self, info):
##        bond_tolerance = info.get('bond_tolerance',1.0)
##        self.radius_multiplier = bond_tolerance # affects draw() method
    def draw(self, glpane, offset = V(0,0,0), color = None, info = {}): # modified copy of superclass draw method
        "draw our spheres (in practice we'll need to extend this for different sets...)"
##        self.radius_multiplier = 1.0 # this might be changed by certain subclass's process_optional_info method
##        self.process_optional_info(info) # might reset instvars that affect following code... (kluge?)
        color = color or self.color
        ##detailLevel = 0 # just an icosahedron
        detailLevel = 1 # easier to click on this way
        ##radius = 0.33 # the one we store might be too large? no, i guess it's ok.
        #e (i might prefer an octahedron, or a miniature-convex-hull-of-extrude-unit)
        offset = offset + self.origin
        radius_multiplier = self.radius_multiplier
        special_pos = self.special_pos # patched in ###nim?
        special_pos = special_pos + offset #k?? or just self.origin??
        special_color = self.special_color # default is used
##        count = 0
        for (pos,radius,info) in self.handles:
            radius *= radius_multiplier
            pos = pos + offset
            dist = vlen(special_pos - pos)
            if dist <= radius:
                color2 = ave_colors( 1.0 - dist/radius, special_color, color )
##                count += 1
            else:
                color2 = color
            ## experiment 050218: add alpha factor to color
            color2 = tuple(color2) + (0.25,)
            drawsphere(color2, pos, radius, detailLevel)
##        self.color2_count = count # kluge, probably not used since should equal nbonds
        return
    pass


# we'll use the atoms of the mols
# and a sep set or two
# of special ones
# and singlet-pair spheres (maybe variabe size)

# ok to only use spheres for now
# if the api could permit changing that

# we don't want to force every stored handle to be an object!

# ..

# each handleset can compute, for one of its handles:
# what to do on mouseover
#  change their color
#  give them a status message
#  (change cursor?)
# what to do if you click, drag, mouseup (click - like button) (true button down/off/up behavior would be good)
# what to do for a long drag




# just these kinds for now:
# rep unit atoms
# base unit atoms
# magenta
# white

# end
