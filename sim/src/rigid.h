
// Copyright 2006 Nanorex, Inc.  See LICENSE file for details. 
extern void rigid_init(struct part *p);

extern void rigid_destroy(struct part *p);

extern void rigid_relative_to_absolute(struct part *p, int bodyIndex, struct xyz relative, struct xyz *absolute);

extern void rigid_apply_force_relative(struct part *p, int bodyIndex, struct xyz force_location_relative, struct xyz force_direction_absolute);

extern void rigid_forces(struct part *p, struct xyz *positions, struct xyz *forces);



