# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
Animate.py [just notes so far]

$Id$

"""


"""
Animate   [some thoughts, 061121]

on_press = Animate(args)

an Action which creates a temporary time-based formula... for interpolational-setting of the side effects listed,
or explicit formula for setting external vars to, or.... [arg syntax unexplored, need some simple desired egs first, see below]

redraws measure time since start, decide what to draw (based on time), whether to gl_update after draw (whether we didn't reach the end)

(but the actual setting of a specific time comes at the start of the redraw, as late as possible, so motion looks as accurate as poss)

(an indep setting gives max frame rate to permit, but for now, max possible will be what we want, very likely)

(measurement is in real time, not counting time we're suspended in some way, eg user pause button, not in the app, etc)

(we also want buttons to stop all anims, and to skip to end of all anims)


other Actions:

- Set(lval, newval) [see controls.py for a prototype, 061130, which takes a stateref rather than an lval as arg1 -- might be wrong]

- Action(callable) # or just a bare callable?

- give commands by their highlevel names

see also scratch6.py, about behaviors & user events & binding actions to them


simple desired egs:
- interpolate any given attr-change in a gradual way
  - (over a given or standard (user pref) time duration)
  - (with the interpolation method a property of the attr itself -- as if a fancier form of __setattr__, __setattr_animated__)
    [implem: does it actually temporarily set it to a formula? might be most efficient, if not all such attrs are always needed!!]
- pass constants to formulas in an animated range - ie when specifying rotation of a newly made thing,
  say it starts x, anims to y, rests at y (ie real value for saving in files is y)
  - ambiguity - for using in other computations, use final or animating value? if final, we have to know (declare) which other comps
    are for drawing and which are not. hmm.

motivations:
- in a lot of user actions in UIs, it'd be easier to understand if the change occurred gradually.
  (and we want this to be easy to express)
- might be useful for inputs to interactive physics, too. (ie it's a form of programmed control path)
- might even be useful for inputs to non-interactive physics -- this lets you preview the path interactively as you devel it,
  but the same path can be passed to a sim which will use it as input, even if sim itself is not realtime in speed and/or interaction.
- production of movies -- e.g. part of a "key-frame animator".

Note that in some egs, the animated actions effectively need to be first-class savable objects. (key-frame anim, sim path control)
In those, the start time is somehow programmed, not "literally the time of giving the command" as in the user-action animation app.

"""

from basic import * # includes Action

class Animate(Action):
    ...

# end for now
