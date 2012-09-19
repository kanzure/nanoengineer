$Id$

class ControlPoint:
    """
    abstract class for any kind of control point for use inside another object like a polyline;
    subclasses can include ones on a reference object
    # note: obs name: PointOnReferenceObject
    """
    pass

class PolylineSegment:
    """
    abstract class for any kind of polyline segment
    """
    pass


class ModelObject: pass # rename Model3D_Component or so?


class Polyline(ModelObject):
    """
    A version of a polyline model object type based on a graph,
    with control points able to be on different ref objects;
    this class provides the data type and necessary low-level operations;
    it does NOT provide drawing and editing-UI code --
    when those are needed they must be provided by associated classes.
    """
    # each one has a graph of control points and segments
    # which have to have types that meet some APIs for them
    # (which depend only on our own code, since it uses those APIs)
    # (but note that if methods are added to this class that might add to the list of required APIs for the parts!)

    controlPointType = ControlPoint ### REVIEW: capitalize attr name?
        # note: this is the data type, not the UI, so we have the
        # most general type we can; a typical UI would encourage or require
        # the creation of points of some more specific type;
        # if so, that's declared in that UI code.

    segmentType = PolylineSegment

    _graph = Instance( Graph( vertexType = controlPointType,
                              edgeType = segmentType ) )
        # Q. is Instance required?
        # Note: this declaration implicitly says that this member is part of our data
        # (to be inspected, saved, copied, etc)...
        # Q. but what about the private name? does it indicate we'd rather save it
        # in terms of the separate accessors with public names??

    controlPoints = _graph.vertices

    segments = _graph.edges

    ## addControlPoint = _graph.addVertex #e or is it better to require use of controlPoints as a dict, adding or extending?
        # not necessarily... e.g. this method would require that the point was not already there.
        # OTOH we can use it as a set instead and make sure the set.add method requires that... ###k

        # the price of not doing this is having to alias tons of method names...

    # but these aliases seem useful
    addControlPoint = controlPoints.add
    addSegment = segments.add

    pass

class Polyline_drawer(Drawer):
    """
    a view of a polyline for the purpose of drawing it
    """

    delegate = Arg(Polyline, doc = "the Polyline we draw")
        ###e rename to self.polyline? but we do need to delegate to it for convenience.

    def draw(self):
        ### IMPLEM self.drawer as something to draw objects in their usual way,
        # subject to usual env rules for that (drawing styles and filters);
        # drawset can have optims for drawing a large set;
        # maybe we'll pass options about their role in us,
        # for it to use when looking up display styles.
        #
        # OR it can just be self, if this doesn't cause confusion due to delegation
        # by hiding parts of self.delegate. Hmm... should we declare what attrs to delegate?
        self.drawer.drawset( self.controlPoints )
        self.drawer.drawset( self.segments )
        return

    pass


def Polyline_UI_helper: #k super? should provide helper methods for this kind of component
        # (one which adds data editing ops for use by a graphical UI)
    """
    methods for editing polylines for use by a graphical UI
    """
    data = Arg(Polyline, doc = "the Polyline we help to edit") #e rename to self.polyline?

    def addControlPoint(self, pointType): #k not sure if we need this, but it's like addSegment below...
        # note that it takes the type, not the object! because we know it's new...
        # but it's not really a type, it's a description, since it has all the data as well. ### RENAME the arg!
        ## point = pointType() ###k ?? no, the container needs to make it, from the description... or is it an expr with code? HMM #####
        point = self.data.makeControlPoint(pointType)
            # note: this implem is generic for things that can instantiate descriptions,
            # except for knowing to call makeControlPoint rather than make...
            # which differs from make in having defaults suitable for self.data.ControlPointType
        self.data.addControlPoint(point)

    def addSegment(self, fromPoint, toPoint, segmentType):
            # note: this is sort of like self.make(segmentType(fromPoint, toPoint))
            # if we imagine that those descriptions (in the arg) carried enough info
            # for us to know their roles in self.
        """
        Add a new segment of type Line from fromPoint to point toPoint,
        each of which might be either an existing Point object in self
        or a description of a new one we should create
        (e.g. as coords and ref object or frame).
        """
        ## fromPoint = self.canonicalizePoint(fromPoint)
            #e rename: find or make? this adds the points if needed. # Note re choosing the name:
            # it is a purely UI method -- the only reason to not know, here, if it's an existing or new point,
            # is that we had user mouse position data, then we saw if user was hovering over an existing point,
            # and if so passed that point, else the mouse position.
            # (So should the caller turn the posn into a new point, for clarity?
            #  maybe only the caller knows the point type, whether that's ok given what's near, etc?
            #  YES, make caller do that, thus we comment this out.)
        ## toPoint = self.canonicalizePoint(toPoint)
        line = segmentType(fromPoint, toPoint)
            ###k? old code said self.Line... self.Line is a type and constructor for whatever we use as a line...
            # but does this method care whether the points are in the same ref object? no, it does not require that.
        self.data.addSegment(line) # the more fundamental method; so self.data is our polyline data, not self! ###k
        return
    def

# now bring in code from:
# - my polyline drawing eg code -- it can add lines or sketched curves
#   for the latter, add the angle cond from squeak --
#   or is that part of separate UI class for a stroke? yes, it is... in this code
#   just say: collect a stroke from the drag, give me the points to be drawing
#   (if we want to optim, give me the permanent and tentative ones seply, and give permanent ones incrly)
#   (so my stroke-drawing code can optim for a stroke being built up, by making a displist tree...)

# - my scratch code for drawing this with its construction lines, in xor mode

# - if i like this way of splitting up classes, then split the file and make separate files

# conclusions:
# - yes, do it like this, keep this (at least as scratch to make clean & real)
#   - want separate classes
#   - want formulae
#   - want types
# - maybe it's more like a sketch than a line... as you added sketch elements, they might share one set of control points,
#   and those might be kept by the sketch in per-ref-object sets for efficiency.
#   so one sketch element (entity) might then refer to or own various sketch primitives including points and segments.
#   So this object here is really more like the sketch itself.
#   (But do sketches share points between them? No -- if you want that, promote those points to ReferencePoints outside the sketch.)
# - note we'll have folding paths, etc, in future, related to this code
#   - note they're like sketches in being able to have disconected pieces, other things in them, etc
#   - and fancier -- tags on the elements, etc
#   - they'd make good use of using generic helper objects but with more specific implem and UI classes for those obj's components.
#     (eg a graph but of a specific kind of points)

