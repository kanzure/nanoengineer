// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "simulator.h"

/* creating atoms, bonds, etc */

/** uses global Nexatom, atom, element, cur, old, Dt, Dx, Boltz, and
    Temperature */
void makatom(int elem, struct xyz posn) {
    struct xyz foo, v, p;
    double mass, therm;
	
    /* create the data structures */
    atom[Nexatom].elt=elem;
    atom[Nexatom].nbonds=0;
    atom[Nexatom].part = PartNo;
    atom[Nexatom].disp = DisplayStyle;
    atom[Nexatom].next = NULL;
    atom[Nexatom].bucket = &Space[0][0][0];
	
    mass=element[elem].mass * 1e-27;
    atom[Nexatom].massacc= Dt*Dt / mass;
	
    /* set position and initialize thermal velocity */
    cur[Nexatom]=posn;
    old[Nexatom]=posn;
    avg[Nexatom]=posn;
    therm = sqrt((2.0*Boltz*Temperature)/mass)*Dt/Dx;
    v=gxyz(therm);
    vsub(old[Nexatom],v);
	
    /* thermostat trigger stays high, since slower motions shouldn't
       reach the unstable simulation regions of phase space
    */
    therm = sqrt((2.0*Boltz*300.0)/mass)*Dt/Dx;
    atom[Nexatom].vlim=(3*therm)*(3*therm);
	
    TotalKE += 2.0*Boltz*Temperature;
    atom[Nexatom].energ = (0.5*mass*Dx*Dx)/(Dt*Dt);
	
    /* add contribution to overall mass center, momentum */
    totMass += mass;
	
    vmul2c(foo,posn,mass);
    vadd(Cog,foo);
	
    vmul2c(p,v,mass);
    vadd(P,p);
	
    /*
      v=vlen(vdif(cur[Nexatom],old[Nexatom]));
      DBGPRINTF("makatom(%d)  V=%.2f ", Nexatom, v);
      pv(cur[Nexatom]); pvt(old[Nexatom]);
    */
    Nexatom++;
	
}



/** an actual bond is ordered so it has a positive type,
    e.g. atom[a].elt <= atom[b].elt */
/* 2 phases -- in first, we don't know if both atoms are there yet */
void makbon0(int a, int b, int ord) {
    int t, typ, ta, tb;
    double bl, sbl;
	
    bond[Nexbon].an1=a;
    bond[Nexbon].an2=b;
    bond[Nexbon].order=ord;
	
    Nexbon++;
}

void makbon1(int n) {
    int a, b, t, typ, ta, tb;
    double bl, sbl;
	
    a=bond[n].an1;
    b=bond[n].an2;
	
    ta=atom[a].elt;
    tb=atom[b].elt;
    if (tb<ta) {t=a; a=b; b=t; t=ta; ta=tb; tb=t;}
	
    typ=bontyp(bond[n].order,ta,tb);
    bond[n].an1=a;
    bond[n].an2=b;
	
    bond[n].type=bstab+findbond(typ);
	
    bl = vlen(vdif(cur[a], cur[b]));
    sbl = bond[n].type->r0;
    if (bl> 1.11*sbl || bl<0.89*sbl)
	DBGPRINTF("Strained bond: %2f vs %2f  (%s%d-%s%d)\n",bl,sbl,
		  element[atom[a].elt].symbol, a, element[atom[b].elt].symbol, b);
}

/** torqs are ordered so the bonds match those in bendata */
void maktorq(int a, int b) {
    int t, tq;
    double theta, th0;
	
    tq = findtorq(bond[a].type->typ,bond[b].type->typ);
    if (bendata[tq].b2typ == bond[a].type->typ
	|| bendata[tq].b2typ == -bond[a].type->typ) {t=a; a=b; b=t;}
	
    torq[Nextorq].b1=bond+a;
    torq[Nextorq].b2=bond+b;
    torq[Nextorq].type = bendata+tq;
	
    if (bond[a].an1==bond[b].an1) {
	torq[Nextorq].dir1=1;
	torq[Nextorq].dir2=1;
	torq[Nextorq].a1=bond[a].an2;
	torq[Nextorq].a2=bond[b].an2;
	torq[Nextorq].ac=bond[a].an1;
    }
    else if (bond[a].an2==bond[b].an1) {
	torq[Nextorq].dir1=0;
	torq[Nextorq].dir2=1;
	torq[Nextorq].a1=bond[a].an1;
	torq[Nextorq].a2=bond[b].an2;
	torq[Nextorq].ac=bond[a].an2;
    }
    else if (bond[a].an1==bond[b].an2) {
	torq[Nextorq].dir1=1;
	torq[Nextorq].dir2=0;
	torq[Nextorq].a1=bond[a].an2;
	torq[Nextorq].a2=bond[b].an1;
	torq[Nextorq].ac=bond[a].an1;
    }
    else {
	torq[Nextorq].dir1=0;
	torq[Nextorq].dir2=0;
	torq[Nextorq].a1=bond[a].an1;
	torq[Nextorq].a2=bond[b].an1;
	torq[Nextorq].ac=bond[a].an2;
    }
	
    theta = vang(vdif(cur[torq[Nextorq].a1],cur[torq[Nextorq].ac]),
		 vdif(cur[torq[Nextorq].a2],cur[torq[Nextorq].ac]));
    th0=torq[Nextorq].type->theta0;
	
    if (theta> 1.25*th0 || theta<0.75*th0)
	DBGPRINTF("Strained torq: %.0f vs %.0f  (%s%d-%s%d-%s%d)\n",
		  (180.0/3.1415)*theta, (180.0/3.1415)*th0,
		  element[atom[torq[Nextorq].a1].elt].symbol, torq[Nextorq].a1,
		  element[atom[torq[Nextorq].ac].elt].symbol, torq[Nextorq].ac,
		  element[atom[torq[Nextorq].a2].elt].symbol, torq[Nextorq].a2);
	
	
	
    Nextorq++;
}

/** make a vdw in one go, in calc loop */
void makvdw(int a1, int a2) {
    struct vdWbuf *newbuf;
    int nx, i, j;
	
    if (Nexvanbuf->fill >= VANBUFSIZ) {
	if (Nexvanbuf->next) {
	    Nexvanbuf = Nexvanbuf->next;
	    Nexvanbuf->fill = 0;
	}
	else {
	    newbuf=malloc(sizeof(struct vdWbuf));
	    Nexvanbuf->next = newbuf;
	    Nexvanbuf = newbuf;
	    Nexvanbuf->fill = 0;
	    Nexvanbuf->next = NULL;
	}
    }
	
    Nexvanbuf->item[Nexvanbuf->fill].a1 = a1;
    Nexvanbuf->item[Nexvanbuf->fill].a2 = a2;
	
    i = min(atom[a1].elt,atom[a2].elt);
    j = max(atom[a2].elt,atom[a2].elt);
    nx = i*(NUMELTS+1) - i*(i+1)/2 + j-i;
    Nexvanbuf->item[Nexvanbuf->fill].table = vanderTable+nx;
	
    Nexvanbuf->fill++;
}

int Count = 0;

void findnobo(int a1) {
    int a2, ix, iy, iz, i, j, k;
    struct A *p;
    double r;
	
    ix= (int)cur[a1].x / 250 + 4;
    iy= (int)cur[a1].y / 250 + 4;
    iz= (int)cur[a1].z / 250 + 4;
	
    for (i=ix-7; i<ix; i++)
	for (j=iy-7; j<iy; j++)
	    for (k=iz-7; k<iz; k++)
		for (p=Space[i&SPMASK][j&SPMASK][k&SPMASK]; p; p=p->next) {
		    a2 = p-atom;
		    if (a2>a1 && atom[a1].part != atom[a2].part) {
			r=vlen(vdif(cur[a1],cur[a2]));
			if (r<800.0) {
			    makvdw(a1, a2);
			    Count++;
			}
		    }
		}
}

/** same as stretch bonds, 2 phases */
void makvander0(int a1, int a2) {
    struct vdWbuf *newbuf;
    int nx, i, j;
	
    if (Nexvanbuf->fill >= VANBUFSIZ) {
	if (Nexvanbuf->next) {
	    Nexvanbuf = Nexvanbuf->next;
	    Nexvanbuf->fill = 0;
	}
	else {
	    newbuf=malloc(sizeof(struct vdWbuf));
	    Nexvanbuf->next = newbuf;
	    Nexvanbuf = newbuf;
	    Nexvanbuf->fill = 0;
	    Nexvanbuf->next = NULL;
	}
    }
	
    Nexvanbuf->item[Nexvanbuf->fill].a1 = a1;
    Nexvanbuf->item[Nexvanbuf->fill].a2 = a2;
	
    /*
      DBGPRINTF("making(0) vdW %d/%d: atoms %d-%d\n",
      Nexvanbuf-&vanderRoot, Nexvanbuf->fill, a1, a2);
    */
	
    Nexvanbuf->fill++;
}

void makvander1(struct vdWbuf *buf, int n) {
	
    int nx, i, j, a1, a2;
	
	
    a1=buf->item[n].a1;
    a2=buf->item[n].a2;
	
    i = min(atom[a1].elt,atom[a2].elt);
    j = max(atom[a2].elt,atom[a2].elt);
    nx = i*(NUMELTS+1) - i*(i+1)/2 + j-i;
    buf->item[n].table = vanderTable+nx;
	
    /*
      DBGPRINTF("making(1) vdW %d/%d: atoms %d-%d\n",
      buf-&vanderRoot, n, buf->item[n].a1, buf->item[n].a2);
    */
}

int makcon(int typ, struct MOT *mot, int n, int *atnos) {
    int i;
	
    Constraint[Nexcon].type = typ;
    Constraint[Nexcon].natoms=n;
    Constraint[Nexcon].motor=mot;
    for (i=0; i<n; i++) Constraint[Nexcon].atoms[i]=atnos[i];
    return Nexcon++;
}

/** input torque in nN*nm,  speed in gigahertz
    store in pN*pm, rad/Dt
*/

struct MOT * makmot(double stall, double speed,
		    struct xyz vec1,  struct xyz vec2) {
    int i;
	
    Motor[Nexmot].center=vec1;
    Motor[Nexmot].axis=uvec(vec2);
    Motor[Nexmot].stall=stall*(1e-9/Dx)*(1e-9/Dx);
    Motor[Nexmot].speed=speed*1e9*2.0*Pi* Dt;
	
    return Motor+Nexmot++;
}

void makmot2(int i) {
    struct MOT *mot;
    struct xyz r, q, vrmax;
    int j, *atlis;
    double x, mass, rmax=0.0, mominert=0.0;
	
    if (Constraint[i].type != 1) return;
	
    atlis = Constraint[i].atoms;
    mot = Constraint[i].motor;
    mot->axis = uvec(mot->axis);
	
    for (j=0;j<Constraint[i].natoms;j++) {
	/* for each atom connected to the "shaft" */
	mass = element[atom[atlis[j]].elt].mass * 1e-27;
		
	/* find its projection onto the rotation vector */
	r=vdif(cur[atlis[j]],mot->center);
	x=vdot(r,mot->axis);
	vmul2c(q,mot->axis,x);
	vadd2(mot->atocent[j],q,mot->center);
		
	/* and orthogonal distance */
	r=vdif(cur[atlis[j]],mot->atocent[j]);
	mot->ator[j] = r;
	mot->radius[j]=vlen(r);
	if (mot->radius[j] > rmax) vrmax=r;
		
	mominert += mot->radius[j]*mass;
    }
    mot->moment = (Dt*Dt)/mominert;
    mot->theta = 0.0;
    mot->theta0 = 0.0;
	
    /* set up coordinate system for rotations */
    mot->roty = uvec(vrmax);
    mot->rotz = vx(mot->axis, mot->roty);
    /* the idea is that an atom at (radius, atang) can be rotated theta
       by putting it at radius*(roty*cos(nt)+rotz*sin(nt))
       where nt is theta + atang
    */
    for (j=0;j<Constraint[i].natoms;j++) { /* now find the angles */
	r=uvec(mot->ator[j]);
	mot->atang[j] = atan2(vdot(r,mot->rotz),vdot(r,mot->roty));
    }
}

/** file reading */

void filred(char *filnam) {
	
    FILE *file;
    char buf[256];
    int i, j, n, m, b, c, ord, lastatom;
    double stall, speed;
    struct xyz vec1,vec2;
    int a1, a2, ie, ix, iy, iz, ix1, iy1, iz1, iv[25];
    int firstatom=1, offset;
    int atnum, atnotab[2*NATOMS];
    struct vdWbuf *nvb;
    char nambuf[128];
    int colr[3];
	
    file=fopen(filnam,"r");
	
	
    while (fgets(buf,127,file)) {
	/* atom number (element) (posx, posy, posz) */
	/* position vectors are integral 0.1pm */
	if (0==strncasecmp("atom",buf,4)) {
	    sscanf(buf+4, "%d (%d) (%d,%d,%d", &atnum, &ie, &ix, &iy, &iz);
	    /*
	      DBGPRINTF("in filred: %s %d (%d) (%d,%d,%d) \n","atom",
	      lastatom,ie, ix, iy, iz );
	    */
	    
	    // hack: change singlets to hydrogen
	    if (ie == 0) ie=1;

	    atnotab[atnum]=Nexatom;
	    lastatom = Nexatom;
			
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    makatom(ie,vec1);
	}


	/* bondO atno atno atno ... (where O is order) */
	else if (0==strncasecmp("bond",buf,4)) {
			
	    j=sscanf(buf+4, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
		     &ord, iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
		     iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17,
		     iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
			
	    for (i=0; i<j-1; i++) makbon0(lastatom, atnotab[iv[i]], ord);
	}
		
	/* [vander]Waals atno atno atno ... (for atoms on same part) */
	else if (0==strncasecmp("waals",buf,5)) {
			
	    j=sscanf(buf+5, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
		     iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
		     iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17,
		     iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
			
	    for (i=0; i<j; i++) makvander0(lastatom,atnotab[iv[i]]);
	}
		
	/* constraints */
	/* welded to space: */
	else if (0==strncasecmp("ground",buf,6)) {
	    j=sscanf(buf+6, "(%s) (%d, %d, %d)%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
		     nambuf, colr, colr+1, colr+2,
		     iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
		     iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17,
		     iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
	    for (i=0; i<j; i++) atnotab[iv[i]];
	    makcon(0, NULL, j, iv);
	}
		
	/* rmotor (name) (r,g,b) <torque> <speed> (<center>) (<axis>) */
	/* torque in nN*nm  speed in gigahertz */
	else if (0==strncasecmp("rmotor",buf,6)) {
	    sscanf(buf+5, "(%s) (%d, %d, %d)%lf %lf (%d, %d, %d) (%d, %d, %d",
		   nambuf, colr, colr+1, colr+2,
		   &stall, &speed, &ix, &iy, &iz, &ix1, &iy1, &iz1);
			
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) DBGPRINTF("motor needs a shaft\n");
	    else {
		j=sscanf(buf+5, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
			 iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
			 iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17,
			 iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
		for (i=0; i<j; i++) atnotab[iv[i]];
		i=makcon(1, makmot(stall, speed, vec1, vec2), j, iv);
	    }
	}
		
	/* lmotor <torque>, <speed>, (<center>) (<axis>) */
	/* torque in nN*nm  speed in gigahertz */
	else if (0==strncasecmp("lmotor",buf,6)) {
	    sscanf(buf+5, "(%s) (%d, %d, %d)%lf, %lf, (%d, %d, %d) (%d, %d, %d",
		   nambuf, colr, colr+1, colr+2,
		   &stall, &speed, &ix, &iy, &iz, &ix1, &iy1, &iz1);
			
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) DBGPRINTF("motor needs a shaft\n");
	    else {
		j=sscanf(buf+5, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
			 iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
			 iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17,
			 iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24);
		for (i=0; i<j; i++) atnotab[iv[i]];
		i=makcon(1, makmot(stall, speed, vec1, vec2), j, iv);
	    }
	}
		
	/* mol [nil|bns|vdw] */
	else if (0==strncasecmp("mol ",buf,4)) {
	    PartNo++;
	}
		
	
	else if (0==strncasecmp("kelvin",buf,6)) {
	    sscanf(buf+6, "%d", &ix);
	    Temperature = (double)ix;
	    DBGPRINTF("Temperature set to %f\n",Temperature);
	}
		
	else if (0==strncasecmp("end",buf,3)) break;
		
	else DBGPRINTF("??? %s\n", buf);
		
    }
    fclose(file);
	
	
    /* fill in new atoms, fixup backward bonds */
	
    for (i=0; i<Nexbon; i++) {
	makbon1(i);
	a1=bond[i].an1;
	atom[a1].bonds[atom[a1].nbonds++]=i;
	a2=bond[i].an2;
	atom[a2].bonds[atom[a2].nbonds++]=i;
    }
	
    /* got all the static vdW bonds we'll see */
    Dynobuf = Nexvanbuf;
    Dynoix = Nexvanbuf->fill;
	
    /* fill in new atoms for vanderwaals pointers */
    for (nvb=&vanderRoot; nvb; nvb=nvb->next)
	for (j=0; j<nvb->fill; j++) makvander1(nvb, j);
	
    /*
      for (i=0; i<Nexatom; i++) pa(i);
      for (i=0; i<Nexbon; i++) pb(i);
    */
	
    /* create bending bonds */
    for (i=0; i<Nexatom; i++) {
	for (m=0; m<atom[i].nbonds-1; m++) {
	    for (n=m+1; n<atom[i].nbonds; n++) {
		checkatom(i);
		maktorq(atom[i].bonds[m], atom[i].bonds[n]);
	    }
	}
    }
	
    for (i=0; i<Nexcon; i++) makmot2(i); /* fixup motors */
	
    /* find bounding box */
	
    vset(vec1, cur[0]);
    vset(vec2, cur[0]);
	
    for (i=1; i<Nexatom; i++) {
	vmin(vec1,cur[i]);
	vmax(vec2,cur[i]);
    }
    vadd2(Center, vec1, vec2);
    vmulc(Center, 0.5);
	
    vset(Bbox[0], vsum(vec1, vcon(-100.0)));
    vset(Bbox[1], vsum(vec2, vcon(100.0)));
	
}
