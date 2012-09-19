# drawing primitives (renamed from some taken from soundspace.py); inefficient

from pyglet.gl import *

import math

# ==

def drawdisc2d(r, x, y, slices=20, start=0, end=2*math.pi):
    "use after glColor3f; filled"
    d = (end - start) / (slices - 1)
    s = start
    points = [(x, y)] + [(x + r * math.cos(a*d+s), y + r * math.sin(a*d+s)) \
                         for a in range(slices)]
    points = ((GLfloat * 2) * len(points))(*points)
    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, points)
    glDrawArrays(GL_TRIANGLE_FAN, 0, len(points))
    glPopClientAttrib()

def drawcircle2d(r, x, y, slices=20):
    "use after glColor3f; not filled"
    d = 2 * math.pi / slices
    points = [(x + r * math.cos(a*d), y + r * math.sin(a*d)) \
                         for a in range(slices)]
    points = ((GLfloat * 2) * len(points))(*points)
    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, points)
    glDrawArrays(GL_LINE_LOOP, 0, len(points))
    glPopClientAttrib()

def drawline2d(color, p1, p2): # modified from drawcircle2d
    glColor3f(*color)
    points = [(p1[0], p1[1]), (p2[0], p2[1])] # the inner things have to be tuples for this to work, it seems
    points = ((GLfloat * 2) * len(points))(*points)
    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointer(2, GL_FLOAT, 0, points)
    glDrawArrays(GL_LINE_LOOP, 0, len(points))
    glPopClientAttrib()

