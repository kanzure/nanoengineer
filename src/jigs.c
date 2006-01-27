
#include "simulator.h"

/** kT @ 300K is 4.14 zJ -- RMS V of carbon is 1117 m/s
    or 645 m/s each dimension, or 0.645 pm/fs  */

static double gavss(double v) {
    double v0,v1, rSquared;
    do {
	v0=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	v1=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	rSquared = v0*v0 + v1*v1;
    } while (rSquared>=1.0 || rSquared==0.0);
    return v*v0*sqrt(-2.0*log(rSquared)/rSquared);
}

struct xyz gxyz(double v) {
    struct xyz g;
    g.x=gavss(v);
    g.y=gavss(v);
    g.z=gavss(v);
    return g;
}

void
jigGround(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position, struct xyz *force)
{
    struct xyz foo, bar;
    struct xyz q1;
    int k;
    struct xyz rx;

    vsetc(foo,0.0);
    vsetc(q1,0.0);
    for (k=0; k<jig->num_atoms; k++) { // find center
        vadd(foo,position[jig->atoms[k]->index]);
    }
    vmulc(foo,1.0 / jig->num_atoms);

    for (k=0; k<jig->num_atoms; k++) {
        vsub2(rx,position[jig->atoms[k]->index], foo);
        v2x(bar,rx,force[jig->atoms[k]->index]); // bar = rx cross force[]
        vadd(q1,bar);
    }
    vmulc(q1,deltaTframe);
    vadd(jig->xdata, q1);
    jig->data++;

    for (k=0; k<jig->num_atoms; k++) {
        new_position[jig->atoms[k]->index] = position[jig->atoms[k]->index];
    }
}

/*
 * 5 nanonewtons
 */
#define MAX_FORCE  5000.0

void
jigMotor(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position, struct xyz *force)
{
    int k;
    int a1;
    double omega, mass, fmult, rmax;
    double motorq, dragTorque = 0.0;
    double dtheta, sumRsquared;

    NULLPTR(position);
    NULLPTR(new_position);

    // Avoid problems where speed is zero. This disables motors which
    // rotate no more than once every ~20 minutes.
    if (jig->j.rmotor.speed < 1.0e-3) {
	jig->data = 0.0;
	jig->data2 = 0.0;
	return;
    }

    // compute the average angle through which the atoms have
    // rotated in the last time step
    sumRsquared = 0.0;
    rmax = 0.0;
    for (k = 0, dtheta = 0.0; k < jig->num_atoms; k++) {
	struct xyz r, r_old, p_old;
	double ar, rsq, rlen;
	a1 = jig->atoms[k]->index;
	r_old = jig->j.rmotor.atomSpoke[k];
	// flatten r into the plane perpendicular to the axis
	vsub2(r, position[a1], jig->j.rmotor.center);
	jig->j.rmotor.atomSpoke[k] = r;
	rsq = vdot(r, r);
	rlen = sqrt(rsq);
	if (rmax < rlen)
	    rmax = rlen;
	jig->j.rmotor.atomRadius[k] = rlen;
	sumRsquared += rsq;
	ar = vdot(jig->j.rmotor.axis, r);
	vadd2scale(r, jig->j.rmotor.axis, -ar);
	// p is perpendicular to r - what sign?
	p_old = vx(jig->j.rmotor.axis, r_old);
	dtheta += atan2(vdot(p_old, jig->j.rmotor.atomSpoke[k]),
			vdot(r_old, jig->j.rmotor.atomSpoke[k]));
    }
    dtheta /= jig->num_atoms;

    omega = dtheta / Dt;
    // Bosch model
    motorq = jig->j.rmotor.stall * (1. - omega / jig->j.rmotor.speed);

    fmult = motorq / sumRsquared;
    if (fmult > MAX_FORCE / rmax)
	fmult = MAX_FORCE / rmax;
    if (fmult < -MAX_FORCE / rmax)
	fmult = -MAX_FORCE / rmax;

    /* nudge atoms toward their new places */
    dragTorque = 0.0;
    for (k = 0, dtheta = 0.0; k < jig->num_atoms; k++) {
	double fmag;  // magnitude of force
	struct xyz f;  // direction of force
	struct xyz r;
	double rlen;
	a1 = jig->atoms[k]->index;
	r = jig->j.rmotor.atomSpoke[k];
	f = vx(jig->j.rmotor.axis, r);  // axis is a unit vector, len(f)=rlen
	rlen = jig->j.rmotor.atomRadius[k];
	fmag = fmult * rlen;
	dragTorque += fmag * rlen;
	mass = jig->atoms[k]->type->mass * 1e-27;
	vmulc(f, Dt * Dt * fmag / (mass * rlen));
	vadd(new_position[a1], f);
    }

    // spring to keep atoms at roughly the same
    // distance from the center of the motor - no
    // damper needed because spring only works in the
    // radial direction
    for (k = 0, dtheta = 0.0; k < jig->num_atoms; k++) {
	const double SpringConstant = 20.0;
	struct xyz f;
	a1 = jig->atoms[k]->index;
	// compute a spring force, based on delta-distance
	// start with unit vector in spoke direction
	vmul2c(f, jig->j.rmotor.atomSpoke[k], 1.0 / jig->j.rmotor.atomRadius[k]);
	// multiply by correct force magnitude
	vmulc(f, SpringConstant *
	      (jig->j.rmotor.initialAtomRadius[k] - jig->j.rmotor.atomRadius[k]));
	// Verlet
	mass = jig->atoms[k]->type->mass * 1e-27;
	vmulc(f, Dt * Dt / mass);
	vadd(new_position[a1], f);
    }

    // convert rad/sec to GHz
    jig->data = omega / (2.0e9 * Pi);
    // convert from pN-pm to nN-nm
    jig->data2 = dragTorque / ((1e-9/Dx) * (1e-9/Dx));
}

void
jigLinearMotor(struct jig *jig, struct xyz *position, struct xyz *new_position, struct xyz *force, double deltaTframe)
{
    int i;
    int a1;
    struct xyz r;
    struct xyz f;
    double ff, x;

    // calculate the average position of all atoms in the motor (r)
    r = vcon(0.0);
    for (i=0;i<jig->num_atoms;i++) {
        /* for each atom connected to the "shaft" */
        r=vsum(r,position[jig->atoms[i]->index]);
    }
    r=vprodc(r, 1.0/jig->num_atoms);

    // x is length of projection of r onto axis (axis is unit vector)
    x=vdot(r,jig->j.lmotor.axis);
    jig->data = x - jig->j.lmotor.motorPosition;

    if (jig->j.lmotor.stiffness == 0.0) {
        vset(f, jig->j.lmotor.center);
    } else {
	// zeroPosition is projection distance of r onto axis for 0 force
	ff = jig->j.lmotor.stiffness * (jig->j.lmotor.zeroPosition - x) / jig->num_atoms;
	f = vprodc(jig->j.lmotor.axis, ff);
    }
    // Calculate the resulting force on each atom, and project it onto
    // the motor axis.  This dissapates lateral force from the system
    // without translating it anywhere else, or reporting it out.
    // XXX report resulting force on linear bearing out to higher level
    for (i=0;i<jig->num_atoms;i++) {
        a1 = jig->atoms[i]->index;
        ff = vdot(vdif(new_position[a1], position[a1]), jig->j.lmotor.axis);
        vadd2(new_position[a1], position[a1], vprodc(jig->j.lmotor.axis, ff));
        ff = vdot(vsum(force[a1], f), jig->j.lmotor.axis) ;
        vmul2c(force[a1], jig->j.lmotor.axis, ff);
    }
}

void
jigThermometer(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position)
{
    double z;
    double ff;
    int a1;
    int k;
    struct xyz f;

    z = deltaTframe / (3 * jig->num_atoms);
    ff=0.0;
    for (k=0; k<jig->num_atoms; k++) {
	a1 = jig->atoms[k]->index;
	f = vdif(position[a1],new_position[a1]);
	ff += vdot(f, f) * jig->atoms[k]->type->mass;
    }
    ff *= Dx*Dx/(Dt*Dt) * 1e-27 / Boltz;
    jig->data += ff*z;
}

// Langevin thermostat
void
jigThermostat(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position)
{
    double z;
    double ke;
    int a1;
    int k;
    double therm;
    struct xyz v1;
    struct xyz v2;
    double ff;
    double mass;

    z = deltaTframe / (3 * jig->num_atoms);
    ke=0.0;

    for (k=0; k<jig->num_atoms; k++) {
	a1 = jig->atoms[k]->index;
	mass = jig->atoms[k]->type->mass;
	therm = sqrt((Boltz*jig->j.thermostat.temperature)/
		     (mass * 1e-27))*Dt/Dx;
        v1 = vdif(new_position[a1],position[a1]);
        ff = vdot(v1, v1) * mass;

        vmulc(v1,1.0-Gamma);
        v2= gxyz(G1*therm);
        vadd(v1, v2);
        vadd2(new_position[a1],position[a1],v1);

        // add up the energy
        ke += vdot(v1, v1) * mass - ff;

    }
    ke *= 0.5 * Dx*Dx/(Dt*Dt) * 1e-27 * 1e18;
    jig->data += ke;
}

double
angleBetween(struct xyz xyz1, struct xyz xyz2)
{
    double Lsq1, Lsq2, L1, L2, dprod;
    Lsq1 = vdot(xyz1, xyz1);
    if (Lsq1 < 1.0e-10)
	return 0.0;
    Lsq2 = vdot(xyz2, xyz2);
    if (Lsq2 < 1.0e-10)
	return 0.0;
    L1 = sqrt(Lsq1);
    L2 = sqrt(Lsq2);
    dprod = vdot(xyz1, xyz2) / sqrt(Lsq1 * Lsq2);
    if (dprod >= 1.0)
	return 0.0;
    if (dprod <= -1.0)
	return 180.0;
    return (180.0 / Pi) * acos(dprod);
}


void
jigDihedral(struct jig *jig, struct xyz *new_position)
{
    struct xyz wx;
    struct xyz xy;
    struct xyz yx;
    struct xyz zy;
    struct xyz u, v;

    // better have 4 atoms exactly
    vsub2(wx,new_position[jig->atoms[0]->index],
          new_position[jig->atoms[1]->index]);
    vsub2(yx,new_position[jig->atoms[2]->index],
          new_position[jig->atoms[1]->index]);
    vsub2(xy,new_position[jig->atoms[1]->index],
          new_position[jig->atoms[2]->index]);
    vsub2(zy,new_position[jig->atoms[3]->index],
          new_position[jig->atoms[2]->index]);
    // vx = cross product
    u = vx(wx, yx);
    v = vx(xy, zy);
    if (vdot(zy, u) < 0) {
	jig->data = -angleBetween(u, v);
    } else {
	jig->data = angleBetween(u, v);
    }
}


void
jigAngle(struct jig *jig, struct xyz *new_position)
{
    struct xyz v1;
    struct xyz v2;

    // better have 3 atoms exactly
    vsub2(v1,new_position[jig->atoms[0]->index],
          new_position[jig->atoms[1]->index]);
    vsub2(v2,new_position[jig->atoms[2]->index],
          new_position[jig->atoms[1]->index]);
    // jig->data = acos(vdot(v1,v2)/(vlen(v1)*vlen(v2)));
    jig->data = angleBetween(v1, v2);
}


void
jigRadius(struct jig *jig, struct xyz *new_position)
{
    struct xyz v1;

    // better have 2 atoms exactly
    vsub2(v1,new_position[jig->atoms[0]->index],
          new_position[jig->atoms[1]->index]);

    jig->data = vlen(v1);
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
