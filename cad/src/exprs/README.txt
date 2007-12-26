cad/src/exprs/README.txt

 Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
# $Id$

This exprs package is an experimental module (working, but incomplete, and in need
of optimization and refactoring) to support a higher-level programming
style for creating patterns of cooperating objects described by
expression-like data (also called "exprs").

So far [071219], it is only used in NE1 for drawing textured images, but it has
working examples of various kinds of interactive graphical behaviors
(many of which are more complex than what is so far available in NE1),
so it might also be used to help implement graphical handles and the
like (e.g. for rotating a helix around a curved axis).

Farther in the future, it could help with implementing various kinds
of "relations" between model objects, with reconfigurable UI elements,
and ultimately with many other things. (Or we might refactor it so
that the parts that would most help with those things, e.g. its
integrated first-class formulae and change-tracked attributes, were
more readily available to other classes. This has been done
experimentally in test_connectWithState.)

It is listed just above graphics in the package ordering, because most of
its example exprs involve graphics and need to import graphics code.
Ideally it would be refactored into (at least) a graphics.exprs
module, a geometry.exprs module, and a lower-level "foundational"
exprs module that could go into foundation or (if changes.py went with
it) utilities.

General features:
* instantiate expression-like descriptions of patterns of cooperating objects ("exprs")
* easily customize those descriptions as a way of configuring the objects they'd create
* the descriptions are first-class data objects, permitting (when implemented)
saving them in files, applying replacement rules, etc.

Specific support for:
* integrated change-tracked attributes, defined by formula or method, or as mutable state 
** nim: state of declared types
** nim: arguments and options meeting declared interfaces
* toplevel formulae as exprs

====

Older notes, partly obsolete:


Note: this directory cad/src/exprs will someday become a python package in NE1,
but for now, it's still experimental, is never loaded by default, and perhaps not all its
source files have been committed.

For info on how to try it out, see file header of cad/src/testmode.py,
or (more complete) the "How to run a numbered test" section below.

Its files mostly don't yet have proper file headers or copyright info. 
(They are all copyright Nanorex, Inc, same as the code in cad/src/*.py files.)

Regarding developer changes in cvs, all files in this package are entirely "owned" by Bruce
until further notice. 

See also PLAN and BUGS in this directory.

-- Bruce, 061011 & 061023 & 061208

===

Note about Qt4 [as of 070110]:

I do all my interactive graphics work in the Qt3 (MAIN) branch. It's been
ported into the Qt4 branch on 12/15/06. It only required one or two trivial
changes to work there (since it has no interaction with Qt). (I think it had a
reference to a main window toolbar attribute name that was removed 
in the Qt4 branch, and it needed a change in GLPane due to dynamic tooltips
not working right.) Those changes are in the Qt4 branch, not yet ported back
to the MAIN branch.

===

Guide to the files involved in the interactive graphics subsystem,
and to my current work on them [bruce 070110]:

(all filenames relative to cad/src)

The ordinary NE1 files I often work on for this project are:

- changes.py   change tracking system (already used in several ways in NE1)

- GLPane.py    3d graphics Qt widget (same as in NE1)

The files only used by the new interactive graphics subsystem are these:

(I change these multiple times per day and never send checkin mail about them)

- testmode.py  an NE1 mode for testing this system, accessed at bottom of debug menu

- testdraw.py  the outermost drawing/reloading code; interface from testmode to exprs subdirectory

- experimental/textures subdirectory (test images and icons)

- exprs subdirectory

  - exprs/test.py  main entry point, list of test cases with status comments, widgets for corners

===

Developer Notes:

- automatic reload:

Modifying source files and clicking in empty space often automatically reloads the
modified source files. This sometimes fails (i.e. causes bugs after reload), since a few 
source files are not set up for reload in this way (especially Exprs and ExprsMeta), 
and it only works if you also modify test.py and all files that import from the modified 
files (due to some nim features in the reload system). It also only happens at all if
ATOM_DEBUG is set in the debug menu. It's worth the trouble, because when it works it
saves lots of time compared to restarting NE1 and reentering testmode every time you
make a trivial change to test.py or some other file you're testing.

When automatic reload "fails" (that is, happens but causes bugs),
the usual result is a lot of exceptions (printed to console)
mentioning things about super(obj), or something not being an instance of OpExpr,
or a few others. The solution is to restart NE1 and reenter testmode.

Note that some preferences set by checkboxes, and some debug_prefs, are not persistent.

- ###e should describe testexpr and testbed

- ###e should describe GLPane_overrider

===

How to run a numbered test (e.g. testexpr_18):

- find the line in exprs/test.py which looks like 

  testexpr = testexpr_19d 

(or testexpr = testexpr_nnn for some other _nnn)

(this line is near the first occurrence of "@@@@")

- change it to (for example)

  testexpr = testexpr_18

(with no indentation in the file)
(spelling note: testexpr, not testexprs)

- either enter testmode, or if you were already in it, click on empty space.

- wait a few seconds for the new test to be drawn. The console prints should
include something like "remaking main instance" and something about which
testexpr_nnn it probably is.

There is a nearby line, enable_testbed = True (or False), which can also be
edited, and which controls whether useful extra stuff (not part of the
specific testexpr) is displayed along with it, in some of the corners.

There is also a nearby long comment with an ordered summary of some of the
most interesting tests.

==

Hints about interacting with some of the tests:

- They will redraw faster if you turn on the debug_pref

  "GLPane: skip redraws requested only by Qt?"

  (It's a big speedup of the use of popup menus over the GLPane,
   and of a few other things, at least on Mac, during which every change 
   to the popup menu causes a redraw of the GLPane if this is not set to True,
   due to conservative behavior by Qt. This is untested on other platforms,
   and it could be that on some of them, Qt is right to do these extra redraws,
   and without them there may be drawing bugs.)
  
  (This speedup and debug_pref is not specific to testmode, but can be tried
   with any NE1 mode.)

- The redrawing is sometimes slow, and this especially affects interacting
with checkboxes or other choice-widgets drawn by this code in the GLPane, or
clicking on the gray rectangle in testexpr_19g. In general, before clicking
on some control in the GLPane, mouse over it and then wait for its statusbar
message to appear; after clicking on it, expect to wait a few seconds to see
the change (even to see a checkmark in a checkbox). In some cases, due to
bugs, you may also need to move the mouse off the control to see the
expected change in its own appearance. (For example, this happens with the
disabled state of the "clear button" in testexpr_19g.)

[end]
