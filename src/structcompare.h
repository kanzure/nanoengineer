#ifndef STRUCTCOMPARE_H_INCLUDED
#define STRUCTCOMPARE_H_INCLUDED

extern int doStructureCompare(struct sim_context *ctx,
			      int numberOfAtoms,
                              struct xyz *basePositions,
                              struct xyz *initialPositions,
                              int iterLimit,
                              double deviationLimit,
                              double maxDeltaLimit,
                              double maxScale);

#endif
