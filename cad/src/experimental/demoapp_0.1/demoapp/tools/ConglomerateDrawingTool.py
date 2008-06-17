"""
ConglomerateDrawingTool.py - shows user good positions for adding new items
(or subassemblies) to "conglomerates" (of objects with lots of attachment and
shape restrictions). Makes it easy to add or move items to nice positions.

$Id$

How it works:

hit test is expanded to cover all nearby objects, and possible modkey settings.
Resulting actions (potential command objects) are sorted/filtered for relevance
and non-excessive-overlap, and drawn to indicate how good they are and how close
the mouse is to picking each one (better affects color, closer means less transparent,
"the one we'd do" has plateau of opacity and special color or appearance, maybe a halo).

requires better hit tests, fast overlap detection in both model space (for what's
possible) and window space (for what's not confusing to show together or mousehit
unambiguously), first-class potential command objects that know various ways
to highlight themselves depending on ui prefs etc (e.g. different tooltip-contrib
if modkeys for this are current or not)...

in future, when objects are slightly flexible, also benefits from constrained motion
understandings (SimBody?), and closeness of fit when overlap prevents exact fit.

"""

# refile:
# tip should be able to be more explicit: click to ...
# and might cover alternatives
# "click here to ...
# or anywhere to ...;
# shift-click to ...
# "
