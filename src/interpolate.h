extern double bender(double rsq);
extern double hooke(double rsq);
extern double lippmor(double rsq);
extern double bucking(double rsq);
extern double square(double x);
extern void initializeBondStretchInterpolater(struct bondStretch *stretch);
extern void testInterpolateBondStretch(int ord, int a1, int a2);
extern void initializeVanDerWaalsInterpolator(struct vdWtab *table, int element1, int element2);
extern void vdWsetup(void);

