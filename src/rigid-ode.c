
#include "simulator.h"
#include "rigid-ode.h"
#include <ode/ode.h>

struct ode_info 
{
  dWorldID world;
  dBodyID *bodies;
  
};

void
rigid_ode_init(struct part *p)
{
  int i;
  struct rigidBody *rb;
  struct ode_info *ode;
  dWorldID world;
  dBodyID body;
  dQuaternion q;
  
  if (p->num_rigidBodies < 2) {
    return;
  }
  
  ode = (struct ode_info *)allocate(sizeof(struct ode_info));
  p->rigid_body_info = (void *)ode;
  
  ode->world = world = dWorldCreate();
  ode->bodies = (dBodyID *)allocate((p->num_rigidBodies - 1) * sizeof(dBodyID));
  ode->bodies[0] = 0;
  
  for (i=1; i<p->num_rigidBodies; i++) {
    rb = &p->rigidBodies[i];
    ode->bodies[i] = body = dBodyCreate(world);
    dBodySetPosition(body, (dReal)rb->position.x, (dReal)rb->position.y, (dReal)rb->position.z);

    // XXX check the ordering of these, they're not defined in ode docs.
    q[0] = (dReal)rb->orientation.x;
    q[1] = (dReal)rb->orientation.y;
    q[2] = (dReal)rb->orientation.z;
    q[3] = (dReal)rb->orientation.a;
    dBodySetQuaternion(body, q);
  }
}

void
rigid_ode_destroy(struct part *p)
{
  int i;
  struct ode_info *ode;

  if (p->num_rigidBodies < 2) {
    return;
  }
  
  ode = (struct ode_info *)p->rigid_body_info;
  NULLPTR(ode);
  NULLPTR(ode->bodies);

  for (i=1; i<p->num_rigidBodies; i++) {
    dBodyDestroy(ode->bodies[i]);
  }
  free(ode->bodies);
  ode->bodies = NULL;
  
  dWorldDestroy(ode->world);
  free(ode);
  // XXX we may want to call this somewhere.
  //dCloseODE();
}
