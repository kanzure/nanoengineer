/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */

#include "simulator.h"

static char const rcsid[] = "$Id$";

// reads atom positions from an XYZ file into Positions[]
// returns the number of atoms read, or -1 for an error.
struct xyz *
readXYZ(char *filename, int *natoms)
{
  int i;
  float x, y, z;
  char symbol[12];
  struct xyz *positions;

  FILE *f = fopen(filename, "r");
  if (f == NULL) {
    perror(filename);
    return NULL;
  }
  if (fscanf(f, "%d\n", natoms) != 1 || *natoms < 1) {
    fprintf(stderr, "error reading atom count from xyz file: %s\n", filename);
    fclose(f);
    return NULL;
  }
  positions= (struct xyz *)allocate(sizeof(struct xyz) * *natoms);
  fscanf(f, "%*s\n"); // skip the RMS=xxx.xx line
  for (i=0; i<*natoms; i++) {
    if (fscanf(f, "%10s %f %f %f\n", symbol, &x, &y, &z) != 4) {
      fprintf(stderr, "error reading atom %d from %s\n", i, filename);
      fclose(f);
      free(positions);
      return NULL;
    }
    positions[i].x = x;
    positions[i].y = y;
    positions[i].z = z;
  }
  return positions;
}
