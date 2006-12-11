
#include "simulator.h"
#include "rigid-ode.h"

#define USE_ODE

void
rigid_init(struct part *p)
{
#ifdef USE_ODE
  rigid_ode_init(p);
#else
  if (p->num_rigidBodies > 0) {
    ERROR("no rigid body support");
  }
#endif
}

void
rigid_destroy(struct part *p)
{
#ifdef USE_ODE
  rigid_ode_destroy(p);
#else
  if (p->num_rigidBodies > 0) {
    ERROR("no rigid body support");
  }
#endif
}
