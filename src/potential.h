extern double stretchPotential(struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double rSquared);

extern double stretchGradient(struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double rSquared);

extern double calculatePotential(struct part *p, struct xyz *position);

extern void calculateGradient(struct part *p, struct xyz *position, struct xyz *force);

