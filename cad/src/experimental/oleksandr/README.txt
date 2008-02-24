README.txt in cad/src/experimental/oleksandr
for psurface module, used by SurfaceChunks chunk display style

# $Id$ 

Copyright 2006-2008 Nanorex, Inc.  See LICENSE file for details. 

===

How to compile:

cd into this directory

% make

On Mac this should produce psurface.so. 

Copy or symlink this into some directory on your Python path when NE1 is run,
e.g. cad/src. 

Then run NE1, make a chunk, select it,
and use the debug menu -> other command "SetDisplay(SurfaceChunks)".

(It may be necessary to have set the debug_pref 'enable SurfaceChunks next session?'.)

This will print one of two things, depending on whether "import psurface" succeeded
(when it ran once at NE1 startup):

            print "psurface not imported, check if it has been built"
            print " (will use slow python version instead)"
        else:
            print "fyi: psurface import succeeded:", psurface

