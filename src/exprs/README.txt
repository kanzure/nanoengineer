cad/src/exprs/README.txt

# $Id$

Note: this directory cad/src/exprs will someday become a python package in NE1,
but for now, it's still experimental, is never loaded by default, and perhaps not all its
source files have been committed.

For info on how to try it out, see file header of cad/src/testmode.py.

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


Notes:

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

[end]
