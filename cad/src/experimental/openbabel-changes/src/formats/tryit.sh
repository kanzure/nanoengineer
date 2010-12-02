#!/bin/sh

# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
# This is a script for quickly testing changes to mmpformat.cpp on a Linux box.
# (For the moment, Will's Linux box in particular.)

BASE=/home/wware/polosims/cad/partlib
# SRCFILE=${BASE}/bearings/SmallBearing.mmp
# SRCFILE=${BASE}/fullerenes/graphene-inductor.mmp
# SRCFILE=${BASE}/pumps/PumpRotor.mmp
# SRCFILE=${BASE}/fullerenes/C78.mmp
# SRCFILE=${BASE}/nanocars/nanocar.mmp
SRCFILE=/home/wware/bdna.c3d1

EXT=mdl

make || exit 1
/usr/bin/install -c .libs/mmpformat.so /usr/local/lib/openbabel/mmpformat.so || exit 1
/usr/bin/install -c .libs/mmpformat.lai /usr/local/lib/openbabel/mmpformat.la || exit 1
/usr/bin/install -c .libs/mmpformat.a /usr/local/lib/openbabel/mmpformat.a || exit 1
babel ${SRCFILE} ~/foo.${EXT} || exit 1
babel ~/foo.${EXT} ~/foo.mmp || exit 1
(cd ~/polosims/cad/src; ATOM_DEBUG=1 ./atom.py --initial-file ~/foo.mmp)
