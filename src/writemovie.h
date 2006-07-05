/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */
#ifndef WRITEMOVIE_H_INCLUDED
#define WRITEMOVIE_H_INCLUDED

#define RCSID_WRITEMOVIE_H  "$Id$"

extern void initializeDeltaBuffers(struct part *part);

extern void writeOutputHeader(FILE *f, struct part *part);

extern void writeOutputTrailer(FILE *f, struct part *part, int frameNumber);

extern void writeSimpleAtomPosition(struct part *part, struct xyz *positions, int i);

extern void writeSimplePositionMarker(struct xyz *position, float radius, float r, float g, float b);

extern void writeSimpleForceVector(struct xyz *positions, int i, struct xyz *force, int color, double scale);

extern void writeSimpleForceVectorOffset(struct xyz *positions, int i, struct xyz *force, int color, double scale, struct xyz offset);

extern void writeSimpleStressVector(struct xyz *positions, int a1, int a2, int ac, double stress, double min, double max);

extern void writeSimpleMovieFrame(struct part *part, struct xyz *positions, struct xyz *forces, const char *format, ...);

extern void writeDynamicsMovieFrame(FILE *f, int n, struct part *part, struct xyz *pos, int last_frame);

extern int writeMinimizeMovieFrame(FILE *f, struct part *part, int final, struct xyz *pos, double rms, double max_force, int frameNumber, int last_frame, char *callLocation, char *message, double potential);

#endif
