# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Drawable.py - shared properties of all drawable objects

$Id$

[not yet used]
"""

from graphics.drawables.Selobj import Selobj_API

class Drawable(Selobj_API):
    """
    Will wrote:
    > To implement my Bauble class, I need to go into every mode where
    > it will be used, and make sure that all this machinery is in
    > place....

    (reviewing the subsequent wiki text as of tonight)

    Not really -- what you are describing is more like it was an
    independent jig than part of what you draw for your main jig.
    Group.addchild, in particular, will mean it shows up in the MT,
    which is not what we want if it's just some other jig's resize
    handle.
    
    Basically, the existing code you are trying to fit into,
    selectMode.jigLeftDown, is not general enough.
    
    Best solution is to make Bauble inherit a new superclass, Drawable
    (if you don't mind me later redefining the API, or us doing that
    together) or BaubleBaseOrWhateverYouCallIt (if you prefer a period
    in which that and Drawable coexist and are related but different),
    and then add this new superclass to the list of things
    SelectAtoms_GraphicsMode treats specially in its event handlers, which is
    now Atom, Bond, Jig.
    
    (If you are willing to let me heavily influence Drawable, as you
    seem to be, you might as well just start defining it in a new
    python source file.)
    
    This Bauble is not selectable and should not need a .picked
    attribute, and should never be permitted in any of those lists of
    selected whatevers in that mode object.
    
    What it needs is an allocated glName (like existing
    not-named-as-such drawables have -- see init code for Atom, Bond,
    Chunk, maybe Jig or some of its subclasses), some methods you'll
    learn about when it tracebacks (like draw_in_abs_coords and maybe
    one for highlight color), and of course a draw method, and a drag
    method, and special cases in lots of the places in SelectAtoms_GraphicsMode
    that now have them for Atom, Bond, Jig -- but these should of
    course be cases for Drawable, not for Bauble. And they might as
    well come first, so if we ever wanted to make something inherit
    from both Drawable and Atom or Bond or Jig, the Drawable API would
    win out in terms of how SelectAtoms_GraphicsMode interacted with it.

    *** __init__ must set self.glname using alloc_my_glselect_name
    [note, this has been revised, bruce 080220; class Atom now sets
     self._glname using assy.alloc_my_glselect_name; glpane has this
     method as well, as of before 080917]
    
    *** Needs a draw_in_abs_coords method
    
    Among the special cases will be for mouse down, mouse drag, mouse
    up. If there is now an object being dragged, or a state variable
    about what kind of thing is being dragged, it needs to fit into
    that (tomorrow I can look and see if that scheme needs cleanup or
    could reasonably be extended as-is).

    *** special cases go in SelectAtoms_GraphicsMode, not here
    
    The code that looks at selobj may also need cases for this, but
    maybe not, if it doesn't need a context menu and doesn't traceback
    without it.

    *** assume I don't need this for now
    
    As for when to draw it, draw it when you draw its owning jig --
    owning jig needs an attr whose value is the bauble (or maybe more
    than one bauble, with an attr which is a dict from bauble-role to
    bauble), and drawing code which (sometimes or always) draws it.

    *** already doing this
    
    As for its position, that might as well be relative to the jig,
    and whatever code now moves or rotates jigs will need to do the
    right thing, and I *hope* that code already calls methods on the
    jig to move it or rotate it, and if so, just override those on
    your jig to do the right thing. If its position and orientation is
    fully relative, that code needn't be modified (if your jig has a
    quat). Warning: someone added quats to motor jigs and others, and
    then (I think) partly or fully abandoned them and didn't clean up the mess,
    so there may be quats that are not modified and/or not honored,
    etc, on some jigs. Either that, or there are partly-redundant quat
    and other attrs, so that the situation with rot methods is confusing.
    And it may be that the move/rotate code (in Move Mode) is not very general
    and will need to be taught to send a nicer method call to Jigs which own Baubles.

    *** motion relative to the jig is a good idea
    
    As for what the Bauble drag method does (when called by the new
    Drawable special case in SelectAtoms_GraphicsMode leftDrag or whatever),
    that is to actually modify its own relative posn in the jig, and
    then do gl_update so that everything (including its parent jig,
    thus itself) gets redrawn, soon after the event is done being
    handled.
    
    The convention for drags is to record the 3d point at which the
    mouse clicked on the Drawable (known from the depth buffer value
    -- the code for clicking on a Jig shows you how to figure this
    out, and the new code for doing this for Drawables also belongs in
    SelectAtoms_GraphicsMode), then interpret mouse motion as being in the
    plane through that point and parallel to the screen, so it's now a
    3d vector, then translate the object by that, then apply whatever
    constraints its position has (e.g. project to a plane it's
    confined to or limit the amount of the drag), but do this in a way
    that lacks history-dependence (this would matter when reaching
    limits). We've never yet had drag-constraints except when dragging
    bondpoints.
    
    Anything not equivalent to that will seem wrong and be a bug.
    
    All the above is for non-selectable non-Node Drawables.
    
    ===========================================================
    
    the current code may assume the glName stack is only 1 deep at
    most, and if you give Bauble a glName of its own, then to obey
    that, the owning Jig needs to not draw it until it pops its own
    main glName, if it has one (which it needs if it can be
    highlighted or dragged as a whole Jig).

    or we could fix the current code to not make that assumption.

    ===

    see also http://www.nanoengineer-1.net/mediawiki/index.php?title=Drawable_objects

    see also class Bauble, and handles.py
    """
    def __init__(self):
        self.glname = self.assy.alloc_my_glselect_name(self) # or self.glpane, or ... #bruce 080917 revised

    def draw_in_abs_coords(self, glpane, color):
        raise Exception, 'abstract method, must be overloaded'
