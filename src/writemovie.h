
extern void writeOutputHeader(FILE *f, struct part *part);

extern void writeOutputTrailer(FILE *f, struct part *part, int frameNumber);

extern void snapshot(FILE *f, int n, struct part *part, struct xyz *pos);

extern int minshot(FILE *f, struct part *part, int final, struct xyz *pos, double rms, double hifsq, int frameNumber, char *callLocation);
