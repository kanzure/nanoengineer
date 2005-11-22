
extern double potentialLippincottMorse(double rSquared, void *p);

extern double gradientLippincottMorse(double rSquared, void *p);

extern void initializeBondStretchInterpolater(struct bondStretch *stretch);

extern double gradientBuckingham(double rSquared, void *p);

extern double potentialBuckingham(double rSquared, void *p);

extern void initializeVanDerWaalsInterpolator(struct vanDerWaalsParameters *vdw, int element1, int element2);

extern void printPotentialAndGradientFunctions(char *name, double initial, double increment, double limit);
