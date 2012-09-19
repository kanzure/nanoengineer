# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Fond3D.py - a vector-drawing OpenGL font.

The font is a vector-drawing thing. The entries in the font are
integer coordinates. The drawing space is 5x7.

$Id$

History:

wware 060324 - created

bruce 071030 - split Font3D out of dimensions module (since used in drawer.py)
"""

__author__ = "Will"

import types
import Numeric
from Numeric import dot

from OpenGL.GL import glVertex

from geometry.VQT import cross
from graphics.drawing.CS_draw_primitives import drawline # import cycle

_font = {
    ' ': ( ),
    'A': (((0, 0),
           (0, 4),
           (1, 6),
           (3, 6),
           (4, 4),
           (4, 0)),
          ((0, 3),
           (4, 3))),
    'B': (((0, 6),
           (3, 6),
           (4, 5),
           (4, 4),
           (3, 3),
           (1, 3)),
          ((3, 3),
           (4, 2),
           (4, 1),
           (3, 0),
           (0, 0)),
          ((1, 6),
           (1, 0))),
    'C': ((4, 5),
          (3, 6),
          (1, 6),
          (0, 5),
          (0, 1),
          (1, 0),
          (3, 0),
          (4, 1)),
    'D': (((0, 6),
           (3, 6),
           (4, 5),
           (4, 1),
           (3, 0),
           (0, 0)),
          ((1, 6),
           (1, 0))),
    'E': (((4, 6),
           (0, 6),
           (0, 0),
           (4, 0)),
          ((0, 3),
           (3, 3))),
    'F': (((4, 6),
           (0, 6),
           (0, 0)),
          ((0, 3),
           (3, 3))),
    'G': ((4, 5),
          (3, 6),
          (1, 6),
          (0, 5),
          (0, 1),
          (1, 0),
          (3, 0),
          (4, 1),
          (4, 3),
          (2, 3)),
    'H': (((0, 6),
           (0, 0)),
          ((4, 6),
           (4, 0)),
          ((0, 3),
           (4, 3))),
    'I': (((1, 6),
           (3, 6)),
          ((1, 0),
           (3, 0)),
          ((2, 6),
           (2, 0))),
    'J': (((3, 6),
           (3, 1),
           (2, 0),
           (1, 0),
           (0, 1),
           (0, 2)),
          ((2, 6),
           (4, 6))),
    'K': (((0, 0),
           (0, 6)),
          ((0, 2),
           (4, 6)),
          ((2, 4),
           (4, 0))),
    'L': ((0, 6),
          (0, 0),
          (4, 0)),
    'M': ((0, 0),
          (0, 6),
          (2, 2),
          (4, 6),
          (4, 0)),
    'N': ((0, 0),
          (0, 6),
          (4, 0),
          (4, 6)),
    'O': ((4, 5),
          (3, 6),
          (1, 6),
          (0, 5),
          (0, 1),
          (1, 0),
          (3, 0),
          (4, 1),
          (4, 5)),
    'P': ((0, 3),
          (3, 3),
          (4, 4),
          (4, 5),
          (3, 6),
          (0, 6),
          (0, 0)),
    'Q': (((4, 5),
           (3, 6),
           (1, 6),
           (0, 5),
           (0, 1),
           (1, 0),
           (3, 0),
           (4, 1),
           (4, 5)),
          ((2, 2),
           (4, 0))),
    'R': (((0, 3),
           (3, 3),
           (4, 4),
           (4, 5),
           (3, 6),
           (0, 6),
           (0, 0)),
          ((2, 3),
           (4, 0))),
    'S': ((4, 5),
          (3, 6),
          (1, 6),
          (0, 5),
          (0, 4),
          (1, 3),
          (3, 3),
          (4, 2),
          (4, 1),
          (3, 0),
          (1, 0),
          (0, 1)),
    'T': (((0, 6),
           (4, 6)),
          ((2, 6),
           (2, 0))),
    'U': ((0, 6),
          (0, 1),
          (1, 0),
          (3, 0),
          (4, 1),
          (4, 6)),
    'V': ((0, 6),
          (2, 0),
          (4, 6)),
    'W': ((0, 6),
          (1, 0),
          (2, 4),
          (3, 0),
          (4, 6)),
    'X': (((0, 0),
           (4, 6)),
          ((0, 6),
           (4, 0))),
    'Y': (((0, 6),
           (2, 3),
           (4, 6)),
          ((2, 3),
           (2, 0))),
    'Z': ((0, 6),
          (4, 6),
          (0, 0),
          (4, 0)),
    # do we need lowercase? not yet
    '.': ((2, 0),
          (3, 0),
          (3, 1),
          (2, 1),
          (2, 0)),
    '/': ((0, 0),
          (3, 6)),
    '#': (((1, 0),
           (2, 6)),
          ((2, 0),
           (3, 6)),
          ((0, 4),
           (4, 4)),
          ((0, 2),
           (4, 2))),
    '+': (((0, 3),
           (4, 3)),
          ((2, 5),
           (2, 1))),
    '-': ((0, 3),
          (4, 3)),
    '*': (((0, 3),
           (4, 3)),
          ((1, 1),
           (3, 5)),
          ((1, 5),
           (3, 1))),
    # Still need: ~ ` ! @ $ % ^ & ( ) _ = [ ] { } ; : ' " | < > , ?
    '0': (((0, 6),
           (4, 0)),
          ((1, 0),
           (0, 1),
           (0, 5),
           (1, 6),
           (3, 6),
           (4, 5),
           (4, 1),
           (3, 0),
           (1, 0))),
    '1': ((1, 0),
          (3, 0),
          (2, 0),
          (2, 6),
          (1, 5)),
    '2': ((0, 5),
          (1, 6),
          (3, 6),
          (4, 5),
          (4, 3),
          (0, 1),
          (0, 0),
          (4, 0)),
    '3': ((0, 5),
          (1, 6),
          (3, 6),
          (4, 5),
          (4, 4),
          (3, 3),
          (1, 3),
          (3, 3),
          (4, 2),
          (4, 1),
          (3, 0),
          (1, 0),
          (0, 1)),
    '4': ((1, 6),
          (0, 3),
          (4, 3),
          (4, 6),
          (4, 0)),
    '5': ((4, 6),
          (0, 6),
          (0, 3),
          (3, 3),
          (4, 2),
          (4, 1),
          (3, 0),
          (0, 0)),
    '6': ((3, 6),
          (0, 4),
          (0, 1),
          (1, 0),
          (3, 0),
          (4, 1),
          (4, 2),
          (3, 3),
          (1, 3),
          (0, 2)),
    '7': ((0, 6),
          (4, 6),
          (2, 0)),
    '8': ((1, 3),
          (0, 4),
          (0, 5),
          (1, 6),
          (3, 6),
          (4, 5),
          (4, 4),
          (3, 3),
          (1, 3),
          (0, 2),
          (0, 1),
          (1, 0),
          (3, 0),
          (4, 1),
          (4, 2),
          (3, 3)),
    '9': ((1, 0),
          (4, 3),
          (4, 5),
          (3, 6),
          (1, 6),
          (0, 5),
          (0, 4),
          (1, 3),
          (3, 3),
          (4, 4)),
    }

WIDTH = 5
HEIGHT = 7
SCALE = 0.08
    # TODO: WIDTH, HEIGHT should be Font3D attributes;
    # right now, they are public, used in dimensions.py.
    # [bruce 071030 comment]

class Font3D:

    def __init__(self, xpos=0, ypos=0, right=None, up=None,
                 rot90=False, glBegin=False):

        self.glBegin = glBegin
        if right is not None and up is not None:
            # The out-of-screen direction for text should always agree with
            # the "real" out-of-screen direction.
            self.outOfScreen = cross(right, up)

            if rot90:
                self.xflip = xflip = right[1] < 0.0
            else:
                self.xflip = xflip = right[0] < 0.0

            xgap = WIDTH
            halfheight = 0.5 * HEIGHT

            if xflip:
                xgap *= -SCALE
                def fx(x): return SCALE * (WIDTH - 1 - x)
            else:
                xgap *= SCALE
                def fx(x): return SCALE * x

            if rot90:
                ypos += xgap
                xpos -= halfheight * SCALE
                def tfm(x, y, yoff1, yflip):
                    if yflip:
                        y1 = SCALE * (HEIGHT - 1 - y)
                    else:
                        y1 = SCALE * y
                    return Numeric.array((xpos + yoff1 + y1, ypos + fx(x), 0.0))
            else:
                xpos += xgap
                ypos -= halfheight * SCALE
                def tfm(x, y, yoff1, yflip):
                    if yflip:
                        y1 = SCALE * (HEIGHT - 1 - y)
                    else:
                        y1 = SCALE * y
                    return Numeric.array((xpos + fx(x), ypos + yoff1 + y1, 0.0))
            self.tfm = tfm

    def drawString(self, str, yoff=1.0, color=None, tfm=None,
                   _font_X=_font['X']):
        n = len(str)
        if not self.glBegin:
            assert color is not None
        if hasattr(self, 'tfm'):
            assert tfm is None
            if self.xflip:
                def fi(i): return i - (n + 1)
            else:
                def fi(i): return i
            # figure out what the yflip should be
            p0 = self.tfm(0, 0, yoff, False)
            textOutOfScreen = cross(self.tfm(1, 0, yoff, False) - p0,
                                    self.tfm(0, 1, yoff, False) - p0)
            yflip = dot(textOutOfScreen, self.outOfScreen) < 0.0
            def tfmgen(i):
                def tfm2(x, y):
                    return self.tfm(x + (WIDTH+1) * fi(i), y, yoff, yflip)
                return tfm2
        else:
            assert tfm is not None
            def tfmgen(i):
                def tfm2(x, y):
                    return tfm(x + i * (WIDTH+1), y)
                return tfm2
        for i in range(n):
            # A pen-stroke is a tuple of 2D vectors with integer
            # coordinates. Each character is represented as a stroke,
            # or a tuple of strokes e.g. '+' or 'X' or '#'.
            def drawSequence(seq, tfm=tfmgen(i)):
                if len(seq) == 0:
                    return  # a space character has an empty sequence
                if type(seq[0][0]) is not types.IntType:
                    # handle multi-stroke characters
                    for x in seq:
                        drawSequence(x)
                    return
                seq = map(lambda tpl: apply(tfm,tpl), seq)
                for i in range(len(seq) - 1):
                    pos1, pos2 = seq[i], seq[i+1]
                    if self.glBegin:
                        # This is what we do for grid planes, where "somebody"
                        # is drawGPGrid in drawers.py.
                        # Somebody has already taken care of glBegin(GL_LINES).
                        # TODO: explain this in docstring.
                        glVertex(pos1[0], pos1[1], pos1[2])
                        glVertex(pos2[0], pos2[1], pos2[2])
                        # Somebody has already taken care of glEnd().
                    else:
                        # This is what we do for dimensions.
                        drawline(color, seq[i], seq[i+1])
            drawSequence(_font.get(str[i], _font_X))
        return
    pass

# end
