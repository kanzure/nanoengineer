
extern double potentialLippincottMorse(double r, void *p);

extern double gradientLippincottMorse(double r, void *p);

extern void initializeBondStretchInterpolater(struct bondStretch *stretch);

extern double gradientBuckingham(double r, void *p);

extern double potentialBuckingham(double r, void *p);

extern void initializeVanDerWaalsInterpolator(struct vanDerWaalsParameters *vdw, int element1, int element2);

extern void printPotentialAndGradientFunctions(char *name, double initial, double increment, double limit);
