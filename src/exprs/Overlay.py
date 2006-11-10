"""
Overlay.py

$Id$
"""

##NIM

class Overlay(DelegatingWidgetExpr):
    "Overlay has the size of its first arg, but draws all its args in the same place, with the same origin."
    def draw(self):
        for a in self.args[::-1]:
            #e We'd like this to work properly for little filled polys drawn over big ones.
            # We might need something like z translation or depth offset or "decal mode"(??) or a different depth test.
            # Different depth test would be best, but roundoff error might make it wrong...
            # This is definitely needed for overdrawing like that to work, but it's low priority for now.
            # Callers can kluge it using Closer, though that's imperfect in perspective mode (or when viewpoint is rotated).
            # But for now, let's just try drawing in the wrong order and see if that helps... yep!
            if a is None:
                continue # even for first arg -- but that being None would fail in other ways, since it'd be our delegate
            a.draw() #e try/except
    pass # Overlay

#e see also FilledSquare
