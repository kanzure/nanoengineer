#ifndef POTENTIAL_H_INCLUDED
#define POTENTIAL_H_INCLUDED

extern double stretchPotential(struct sim_context *ctx, struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double rSquared);

extern double stretchGradient(struct sim_context *ctx, struct part *p, struct stretch *stretch, struct bondStretch *stretchType, double rSquared);

extern double vanDerWaalsPotential(struct sim_context *ctx, struct part *p, struct vanDerWaals *vdw, struct vanDerWaalsParameters *parameters, double rSquared);

extern double vanDerWaalsGradient(struct sim_context *ctx, struct part *p, struct vanDerWaals *vdw, struct vanDerWaalsParameters *parameters, double rSquared);

extern double calculatePotential(struct sim_context *ctx, struct part *p, struct xyz *position);

extern void calculateGradient(struct sim_context *ctx, struct part *p, struct xyz *position, struct xyz *force);

#endif
