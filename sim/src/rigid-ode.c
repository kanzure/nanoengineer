
// Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
#include "simulator.h"
#include "rigid-ode.h"

#ifdef USE_ODE

#include <ode/ode.h>

// There is a sphere centered on a station point on body1, whose
// radius is the square root of this value (in pm).  The corrosponding
// station point on body2 must be inside that sphere.
#define STATION_TOLERANCE 0.04

// similar for axes
#define AXIS_TOLERANCE 0.04

struct ode_info 
{
  dWorldID world;
  dBodyID *bodies;
  dJointID *joints;
};

static void
findStationPoint(struct part *p,
                 int jointNumber,
                 char *jointType,
                 int body1index,
                 int body2index,
                 dBodyID body1,
                 dBodyID body2,
                 int station1index,
                 int station2index,
                 dVector3 station1)
{
  struct xyz s1;
  struct xyz s2;
  dVector3 station2;
  dReal deltax;
  dReal deltay;
  dReal deltaz;

  s1 = p->rigidBodies[body1index].stations[station1index];
  s2 = p->rigidBodies[body2index].stations[station2index];
  dBodyGetRelPointPos(body1, (dReal)s1.x, (dReal)s1.y, (dReal)s1.z, station1);
  dBodyGetRelPointPos(body2, (dReal)s2.x, (dReal)s2.y, (dReal)s2.z, station2);
  deltax = station1[0] - station2[0];
  deltay = station1[1] - station2[1];
  deltaz = station1[2] - station2[2];
  if (deltax * deltax + deltay * deltay + deltaz * deltaz > STATION_TOLERANCE) {
    ERROR5("joint %d, a %s, StationPoint mismatch: (%f, %f, %f)", jointNumber, jointType, deltax, deltay, deltaz);
    dBodyGetPosRelPoint(body2, station1[0], station1[1], station1[2], station2);
    ERROR3("StationPoint on body2 would be (%f, %f, %f) to match body1", station2[0], station2[1], station2[2]);
    p->parseError(p->stream);
  }
}

static void
findAxis(struct part *p,
         int jointNumber,
         char *jointType,
         int body1index,
         int body2index,
         dBodyID body1,
         dBodyID body2,
         int axis1index,
         int axis2index,
         dVector3 axis1)
{
  struct xyz a1;
  struct xyz a2;
  dVector3 axis2;
  dReal deltax;
  dReal deltay;
  dReal deltaz;

  a1 = p->rigidBodies[body1index].axes[axis1index];
  a2 = p->rigidBodies[body2index].axes[axis2index];
  dBodyVectorToWorld(body1, (dReal)a1.x, (dReal)a1.y, (dReal)a1.z, axis1);
  dBodyVectorToWorld(body2, (dReal)a2.x, (dReal)a2.y, (dReal)a2.z, axis2);
  deltax = axis1[0] - axis2[0];
  deltay = axis1[1] - axis2[1];
  deltaz = axis1[2] - axis2[2];
  if (deltax * deltax + deltay * deltay + deltaz * deltaz > AXIS_TOLERANCE) {
    ERROR5("joint %d, a %s, Axis mismatch: (%f, %f, %f)", jointNumber, jointType, deltax, deltay, deltaz);
    dBodyVectorFromWorld(body2, axis1[0], axis1[1], axis1[2], axis2);
    ERROR3("AxisPoint on body2 would be (%f, %f, %f) to match body1", axis2[0], axis2[1], axis2[2]);
    p->parseError(p->stream);
  }
}


void
rigid_ode_init(struct part *p)
{
  int i;
  int k;
  struct xyz attachAtomLocation;
  struct rigidBody *rb;
  struct joint *j;
  struct ode_info *ode;
  dWorldID world;
  dBodyID body;
  dJointID joint;
  dQuaternion q;
  int b1;
  int b2;
  dBodyID body1;
  dBodyID body2;
  dVector3 station1;
  dVector3 axis1;
  
  if (p->num_rigidBodies < 2) {
    return;
  }
  
  ode = (struct ode_info *)allocate(sizeof(struct ode_info));
  p->rigid_body_info = (void *)ode;
  
  ode->world = world = dWorldCreate();
  ode->bodies = (dBodyID *)allocate((p->num_rigidBodies) * sizeof(dBodyID));
  ode->bodies[0] = 0;
  ode->joints = (dJointID *)allocate((p->num_joints) * sizeof(dJointID));
  
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
    for (k=0; k<rb->num_attachments; k++) {
      attachAtomLocation = p->positions[rb->attachmentAtomIndices[k]];
      dBodyGetPosRelPoint(body,
                          (dReal)attachAtomLocation.x,
                          (dReal)attachAtomLocation.y,
                          (dReal)attachAtomLocation.z,
                          station1);
      rb->attachmentLocations[k].x = (double)station1[0];
      rb->attachmentLocations[k].y = (double)station1[1];
      rb->attachmentLocations[k].z = (double)station1[2];
    }
  }

  for (i=0; i<p->num_joints; i++) {
    j = &p->joints[i];
    b1 = j->rigidBody1;
    b2 = j->rigidBody2;
    body1 = ode->bodies[b1];
    body2 = ode->bodies[b2];
    switch (j->type) {
    case JointBall:
      ode->joints[i] = joint = dJointCreateBall(world, 0);
      dJointAttach(joint, body1, body2);
      findStationPoint(p, i, "Ball", b1, b2, body1, body2, j->station1_1, j->station2_1, station1);
      dJointSetBallAnchor(joint, station1[0], station1[1], station1[2]);
      break;
    case JointHinge:
      ode->joints[i] = joint = dJointCreateHinge(world, 0);
      dJointAttach(joint, body1, body2);
      findStationPoint(p, i, "Hinge", b1, b2, body1, body2, j->station1_1, j->station2_1, station1);
      dJointSetHingeAnchor(joint, station1[0], station1[1], station1[2]);
      findAxis(p, i, "Hinge", b1, b2, body1, body2, j->axis1_1, j->axis2_1, axis1);
      dJointSetHingeAxis(joint, axis1[0], axis1[1], axis1[2]);
      break;
    case JointSlider:
      ode->joints[i] = joint = dJointCreateSlider(world, 0);
      dJointAttach(joint, body1, body2);
      findAxis(p, i, "Slider", b1, b2, body1, body2, j->axis1_1, j->axis2_1, axis1);
      dJointSetSliderAxis(joint, axis1[0], axis1[1], axis1[2]);
      break;
    default:
      ERROR1("unknown joint type for joint %d", i);
      p->parseError(p->stream);
    }
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

  for (i=0; i<p->num_joints; i++) {
    dJointDestroy(ode->joints[i]);
  }
  free(ode->joints);
  ode->joints = NULL;
  
  dWorldDestroy(ode->world);
  free(ode);
  // XXX we may want to call this somewhere.
  //dCloseODE();
}

void
rigid_ode_relative_to_absolute(struct part *p, int bodyIndex, struct xyz relative, struct xyz *absolute)
{
  ERROR("rigid_ode_relative_to_absolute not implemented");
}

void
rigid_ode_apply_force_relative(struct part *p, int bodyIndex, struct xyz force_location_relative, struct xyz force_direction_absolute)
{
  ERROR("rigid_ode_apply_force_relative not implemented");
}

#endif
