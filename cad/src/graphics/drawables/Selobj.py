# Copyright 2006-2009 Nanorex, Inc.  See LICENSE file for details. 
"""
Selobj.py -- provides class Selobj_API, [### WHICH WILL BE RENAMED, ALONG WITH THIS FILE]
which documents the interface from the GLPane to drawable objects which need
to detect whether the mouse touches them, i.e. mainly for
"hover-highlightable" objects, and from other code to whatever such
objects are stored in glpane.selobj (since they are actually under the
mouse).

@author: Bruce
@version: $Id$
@copyright: 2006-2009 Nanorex, Inc.  See LICENSE file for details.

Current status [bruce 080116]:

This partly formalizes an informal API used by GLPane and some
Commands and GraphicsModes to handle hover-highlightable 
drawable objects, which has optional methods for some optional 
abilities they can have, like a different highlight appearance,
an ability to provide a context menu, or an ability to
provide a DragHandler.

There is unfortunately not yet a single consistent API
for "drawables" in NE1. For example, many classes have
draw or Draw methods, but these can have two or three
different arg signatures in different class hierarchies.

The Selobj_API is not a general "drawable API" but covers
most ways in which a drawable object might interact
with the mouse. As currently constructed it's unideal in 
several ways, e.g. its methods have no consistent naming 
convention, and the semantics for "using the default behavior" 
is often "don't provide the method", which means we can't 
provide a default or stub implementation in class Selobj_API 
itself (effectively an "interface class") or we'd break code. 

And, in reality it's probably at least two APIs mushed
together. And certainly it's unclearly named.

The confusion apparent in the docstring and comments of
Selobj.py (class Selobj_API) reflects all this.

This can and should all be cleaned up, but we're unlikely 
to do much of that before FNANO '08. In the meantime, making
the classes that provide the existing "selobj interface"
say they do so is at least a start, since the set of things
to look at to understand all this is more clearly defined.

To clarify: this commit [080116] does not change any behavior or rename
any methods. It only adds an empty superclass to all existing
classes which use methods from the preexisting informal
"selobj interface", thereby partially formalizing the interface.
(It formalizes which classes provide it, though with no detection of
errors in this, but it does not formalize what methods are part
of it -- the comments in Selobj.py are the most we have in that
direction.)

===

### REVIEW: is that really two different interfaces? The GLPane,
finding the selobj via glname, could ask it to return the value
to actually store in glpane.selobj.
First interface is " an object (drawable) which notices the mouse over it",
second is "an object which handles events for the object
under the mouse"... they might not be in 1-1 correspondence
when we have good support for nested glnames!

sort of like a mouse-sensitive drawable vs a mouse-handling model object...
or a mouse event handler for a model object... or for a drawable (or a
nested chain of them, depending on glname nesting for e.g. stereo, or
repeated identical parts)

Note: a drag-handler (see DragHandler.py) and a "selobj" are often the same
object, but obeying a different API; drag_handlers are return values from
a Selobj_API-interface method (which often returns self).

Implementation note: in the current code, all such objects ask
the GLPane (actually the global env module, but ideally a GL Context
representative) to allocate them a "glname" for use during GL_SELECT drawing,
but this implementation may change or be augmented, both for efficiency and to
work for transparent objects.

Note: most objects which implement this interface don't currently [070913]
inherit class Selobj_API. Since the methods in it needn't be overridden,
most client code tests for their presence, and in some cases runs non-noop
default code if they are not found. This should be revised so that all
implementors inherit this class, and so that the default code is moved
to default methods in this class.

WARNING: Until that revision is done, adding this superclass to existing
objects would break code in the GLPane or in modes, which relies on testing
for the lack of presence of certain methods in this API to decide when
to run its own default code instead of calling those methods. Or at least
it would if this class had any methods defined in it ... maybe we should leave
the methods out, add the superclass, then move the methods and their
client-supplied default code into this class gradually.

The init code which allocates a glname should also be moved into an init
method in this class.

Current classes which should inherit this interface include Atom, Bond, Jig,
and Highlightable, and others which have comments about "selobj interface",
e.g. in Plane and DirectionArrow modules.

All comments about either "selobj interface" or "Drawable API" may relate to
this and should be revised. See also scratch/Drawable.py.

Some documentation about this interface exists in exprs/Highlightable.py and
GLPane.py.

Module classification:

Seems most like graphics_behavior_api, but revisit when it's done.
[bruce 071215]
"""

# possible names for this class:
# - class MouseSensor_interface (in file MouseSensor.py? or MouseSensor_interface.py?)
# - class MouseSensitive -- maybe that grammar (adjective) means _interface can be 
#   implied? not sure.
# And should the methods start with a prefix like MouseSensor_ ?

class Selobj_API:
    """
    ###doc
    WARNING: API details (method names, arglists) are subject to change.
    """
    ### see list of methods below -- but don't add any method stubs here
    # for now, or some code will break (as explained in module docstring).

    # some *new* api methods can safely be added here:

    def nodes_containing_selobj(self): #bruce 080507
        """
        Return a list (not a tuple) of all nodes that contain self,
        in innermost-to-outermost order if convenient. If self bridges
        multiple leaf nodes (e.g. if self is an external bond), include
        all those leaf nodes (and all their containing nodes) in the result,
        but in that case, the order of nodes within the result is undefined,
        and whether the result might contain some nodes twice is undefined.
        """
        return []
    
    pass

# comment moved from exprs/Highlightable.py, edited here :

# == selobj interface

###e should define a class for the selobj interface; see classes Highlightable and
# _UNKNOWN_SELOBJ_class for an example --

# methods desired by glpane for analyzing hits, responding to them

# - object.glname (?)
#    [note, not really a public attribute; e.g. class Atom made it private
#     and introduced get_glname method on 080220]
# - and the env table for glname to object -- in future that goes to first kind of obj,
#  it returns 2nd kind [note: being moved from env to assy as of bruce 080220]
#   (and does glpane need to remember more than just one selobj it returns??)

# and by mode for passing on events:

# - leftClick
# - make_selobj_cmenu_items

# by glpane for drawing selobj -- not sure how to classify these -- but only done on one
#  object so i think it's on the 2nd interface

# - selobj_still_ok, [glpane asks mode(?), default implem asks selobj]
# - draw_in_abs_coords,
# - highlight_color_for_modkeys
# - mouseover_statusbar_message (used in GLPane.set_selobj)

# other things looked at on a selobj:
# - getInformationString (maybe not on all objects??)
# - killed
# - glname (might be a kluge)
# - part (only on some kinds?)

# see also: _UNKNOWN_SELOBJ_class


# new, 070919 - here are the distinct interfaces...
"""
gl select hit detector - for an object with a glname, which draws inside it - must draw in
a special way

related opengl names: glSelectBuffer, glselect/glname in our own related internal names,
glRenderMode(GL_SELECT)

class GL_SELECT_HitDetector_Mixin

(other kinds of hit detectors - they'd need geometric info in api, but would not need to
draw at all, let alone specially -- except insofar as to record unambiguously when they
did get drawn, ie whether they are really in the scene, and if so under what coordsys that
was (when in display lists). maybe "draw" means "add self to that frame scene tree"?? or
maybe we imitate glselect and repeat the draw in a special way? as my partly done expr
draw reform was trying to do, for its own hit detection to work inside display lists...)

==

ObjectUnderMouse_interface - for anything which can be returned as the object under the
mouse, then queried about what to do, or even about how to draw itself specially (over its
ordinary representation, which may have to be drawn too, being in a display list).

glpane.selobj rename to glpane.objectUnderMouse (someday)

selobj - an object assignable to glpane.selobj - should provide actions in ui for mouse
events over it - highlightable, draggable, ... mouse sensitive - handler of mouse events -
can ask for this obj under mouse -

==

Q: is being overdrawn specially, a different interface than being objectUnderMouse?
evidence: objUnderMouse might say "here are the objects to overdraw specially" and they
might be more than just it. It would call all their drawing code with special flags (look
highlighted in certain way) and in abs coords... latter might be fixed if we reimplemented
how this works as a separate drawing pass, someday.

but note that in current code this object also gets first dibs at providing the next
detected hit using stencil buffer... hmm... what does stencil buffer say about how all
these interfaces have to be related?

###
Can I factor out the related code from the GLPane, while I'm doing this? And fix some bugs
and add required new APIs at same time (fix bugs in highlightable vs displists, add api
for region sel, and for multiple highlighted objects for single obj under mouse)

==

region selection interface - a node which contains region-selectable things and control
points for them
"""


### REVIEW: should check_target_depth_fudge_factor
# be an attribute of each object which can be drawn as selobj, instead of an attr of the mode?
# (as of 070921 it's an optional mode attr, default value supplied by its client, GLPane.)


# outtake??
        ####@@@@ TODO -- rename draw_in_abs_coords and make it imply highlighting so obj knows whether to get bigger
        # (note: having it always draw selatoms bigger, as if highlighted, as it does now, would probably be ok in hit-test,
        #  since false positives in hit test are ok, but this is not used in hit test; and it's probably wrong in depth-test
        #  of glselect_dict objs (where it *is* used), resulting in "premonition of bigger size" when hit test passed... ###bug);
        # make provisions elsewhere for objs "stuck as selobj" even if tests to retain that from stencil are not done
        # (and as optim, turn off stencil drawing then if you think it probably won't be needed after last draw you'll do)



# end
