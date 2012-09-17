# Copyright 2007 Nanorex, Inc.  See LICENSE file for details.
"""
$Id$

code file on selection or region selection?

idea: a simple semantics for region selection,
if "touches all of the drawn stuff" or "any part of it" is too hard
(which it is, for most things except simple shapes),
is "touches all of (or any of) the object's control points".

it's easy to implement, easy to understand, and (i realize now) insensitive to changes of display prefs.

it could be done efficiently enough to do realtime update of region-selected objects
(if we improved our "region" representation, anyway). We might do per-chunk caching of a 2d-screen-version
of all that chunk's control points, then sort them into cells...

(note: an atom's control point is its center, so it's same behavior as now for atoms.
For other objs we have some simple def of what they are -- can be more than strictly needed to define it, for this purpose...
call it a "selection control point". For simple shapes, sphere cyl cone, we might do the real alg (as if all points were cpoints) --
but only when that shape was itself selectable -- when part of display of some model obj, instead define cpoints for that model obj.)
"""
