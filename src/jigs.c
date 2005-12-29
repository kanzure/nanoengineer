
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
jigMotorPreforce(struct jig *jig, struct xyz *position, struct xyz *force, double deltaTframe)
{
    int n;
    struct xyz rx;
    int k;
    double ff;
    int a1;
    double theta;
    struct xyz f;

    if (jig->j.rmotor.speed==0.0) { // just add torque to force

        // set the center of torque each time to the average position
        // of the atoms in the motor
        n=jig->num_atoms;
        vsetc(rx, 0.0);
        for (k=0; k<n; k++) {
            vadd(rx,position[jig->atoms[k]->index]);
        }
        vmulc(rx,1.0/(double)n);
        jig->j.rmotor.center = rx;

        ff = 1e-3 * jig->j.rmotor.stall / n;
        for (k=0; k<n; k++) {
            a1 = jig->atoms[k]->index;
            rx = vdif(position[a1], jig->j.rmotor.center);
            f  = vprodc(vx(jig->j.rmotor.axis, uvec(rx)),ff/vlen(rx));
			    
            //fprintf(stderr, "applying torque %f to %d: other force %f\n",
            //       vlen(f), a1, vlen(force[a1]));

            vadd(force[a1],f);
        }
        // data for printing speed trace
        jig->data2 = jig->j.rmotor.stall; // torque

        rx=uvec(vdif(position[jig->atoms[0]->index], jig->j.rmotor.center));
			
        theta = atan2(vdot(rx, jig->j.rmotor.axisZ), vdot(rx, jig->j.rmotor.axisY));
        /* update the motor's position */
        if (theta>Pi) {
            jig->j.rmotor.theta0 = jig->j.rmotor.theta-2.0*Pi;
            jig->j.rmotor.theta = theta-2.0*Pi;
        }
        else {
            jig->j.rmotor.theta0 = jig->j.rmotor.theta;
            jig->j.rmotor.theta = theta;
        }
        theta = jig->j.rmotor.theta - jig->j.rmotor.theta0;

        jig->data += theta * deltaTframe;
    }
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

void
jigMotor(struct jig *jig, double deltaTframe, struct xyz *position, struct xyz *new_position, struct xyz *force)
{
    double sum_torque;
    int k;
    int a1;
    struct xyz rx;
    struct xyz f;
    double ff;
    double omega, omega0;
    double motorq;
    double theta;
    double stall;
    double z;
    struct xyz v1, v2;

    if (jig->j.rmotor.speed != 0.0) {
        sum_torque = 0.0;
					
        /* input torque due to forces on each atom */
        for (k=0; k<jig->num_atoms; k++) {
            a1 = jig->atoms[k]->index;
            rx = vdif(position[a1],jig->j.rmotor.atomCenterOfRotation[k]);
            f = vx(rx,force[a1]);
            ff = vdot(f, jig->j.rmotor.axis);
            sum_torque += ff;
        }
		    
        //fprintf(stderr, "*** input torque %f\n", sum_torque);

#define FUDGE_FACTOR  2.0e6
	omega0 = FUDGE_FACTOR * (2.0e9 * Pi) * jig->j.rmotor.speed;
        omega = (jig->j.rmotor.theta - jig->j.rmotor.theta0) / Dt;
        motorq = 0.1 * (omega0 - omega);
	// treat stall torque as a _maximum_ torque
	stall = FUDGE_FACTOR * abs(jig->j.rmotor.stall);
	if (motorq < -stall) motorq = -stall;
	if (motorq > stall) motorq = stall;

        omega += motorq + sum_torque * Dt;
        theta = jig->j.rmotor.theta + omega * Dt;

        /* put atoms in their new places */
        for (k=0; k<jig->num_atoms; k++) {
            a1 = jig->atoms[k]->index;
            z = theta + jig->j.rmotor.atomAngle[k];
            vmul2c(v1, jig->j.rmotor.axisY, jig->j.rmotor.atomRadius[k] * cos(z));
            vmul2c(v2, jig->j.rmotor.axisZ, jig->j.rmotor.atomRadius[k] * sin(z));
            vadd2(new_position[a1], v1, v2);
            vadd(new_position[a1], jig->j.rmotor.atomCenterOfRotation[k]);
        }
					
        /* update the motor's position */
        if (theta>Pi) {
            jig->j.rmotor.theta0 = jig->j.rmotor.theta-2.0*Pi;
            jig->j.rmotor.theta = theta-2.0*Pi;
        }
        else {
            jig->j.rmotor.theta0 = jig->j.rmotor.theta;
            jig->j.rmotor.theta = theta;
        }
        // data for printing speed trace
        jig->data += omega * deltaTframe;
        jig->data2 += (motorq) * deltaTframe;
    }
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
