#ifndef JIGS_H_INCLUDED
#define JIGS_H_INCLUDED

#define RCSID_JIGS_H  "$Id$"

extern struct xyz gxyz(double v);

extern void jigMotorPreforce(struct jig *jig, struct xyz *position, struct xyz *force, double deltaTframe);

extern void jigGround(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position, struct xyz *force);

extern void jigMotor(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position, struct xyz *force);

extern void jigLinearMotor(struct jig *jig, struct xyz *position, struct xyz *new_position, struct xyz *force, double deltaTframe);

extern void jigThermometer(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position);

extern void jigThermostat(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position);

extern double angleBetween(struct xyz xyz1, struct xyz xyz2);

extern void jigDihedral(struct jig *jig, struct xyz *new_position);

extern void jigAngle(struct jig *jig, struct xyz *new_position);

extern void jigRadius(struct jig *jig, struct xyz *new_position);

#endif
