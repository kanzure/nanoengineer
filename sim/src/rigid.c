
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#include "simulator.h"
#include "rigid-ode.h"

#ifndef USE_ODE
static void
check_rigid_support(struct part *p)
{
  struct rigidBody *rb;

  if (p->num_rigidBodies < 1) {
    return;
  }
  rb = &p->rigidBodies[0];
  if (p->num_rigidBodies > 1 || rb->num_attachments > 0) {
    ERROR("no rigid body support");
  }
}
#endif

void
rigid_init(struct part *p)
{
#ifdef USE_ODE
  rigid_ode_init(p);
#else
  check_rigid_support(p);
#endif
}

void
rigid_destroy(struct part *p)
{
#ifdef USE_ODE
  rigid_ode_destroy(p);
#else
  check_rigid_support(p);
#endif
}

void
rigid_relative_to_absolute(struct part *p, int bodyIndex, struct xyz relative, struct xyz *absolute)
{
#ifdef USE_ODE
  rigid_ode_relative_to_absolute(p, bodyIndex, relative, absolute);
#else
  ERROR("no rigid body support");
#endif
}

void
rigid_apply_force_relative(struct part *p, int bodyIndex, struct xyz force_location_relative, struct xyz force_direction_absolute)
{
#ifdef USE_ODE
  rigid_ode_apply_force_relative(p, bodyIndex, force_location_relative, force_direction_absolute);
#else
  ERROR("no rigid body support");
#endif
}

void
rigid_forces(struct part *p, struct xyz *positions, struct xyz *forces)
{
  int i;
  int j;
  int atomIndex;
  double f;
  struct rigidBody *rb;
  struct xyz absolute;
  struct xyz delta;
  struct xyz force;

  // XXX also need to compute thermal transfer to body.
  for (i=0; i<p->num_rigidBodies; i++) {
    rb = &p->rigidBodies[i];
    for (j=0; j<rb->num_attachments; j++) {
      rigid_relative_to_absolute(p, i, rb->attachmentLocations[j], &absolute);
      atomIndex = rb->attachmentAtomIndices[j];
      vsub2(delta, positions[atomIndex], absolute);
      f = vdot(delta, delta) * 1; // XXX unit conversion, spring force constant
      vmul2c(force, delta, f);
      vsub(forces[atomIndex], force);
      rigid_apply_force_relative(p, i, rb->attachmentLocations[j], force);
    }
  }
}
