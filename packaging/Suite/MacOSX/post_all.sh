#!/bin/sh
OUTFIL=/tmp/scriptvars_all
echo "SPATH=$0" > $OUTFIL
echo "PPATH=$1" >> $OUTFIL
echo "TARGETLOC=$2" >> $OUTFIL
echo "TARGETVOL=$3" >> $OUTFIL
env >> $OUTFIL
