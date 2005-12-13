// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.

#include "simulator.h"

/* creating atoms, bonds, etc */

/** uses global Nexatom, atom, element, positions, old_positions, Dt, Dx, Boltz, and
    Temperature */
// posn in pm or 1e-12 m
void
makatom(int elem, struct xyz posn) {
    struct xyz foo, v, p;
    double mass, therm;
	
    /* create the data structures */
    atom[Nexatom].elt=elem;
    atom[Nexatom].nbonds=0;
    //atom[Nexatom].part = PartNo;
    //atom[Nexatom].disp = DisplayStyle;
    atom[Nexatom].next = NULL;
    atom[Nexatom].bucket = &Space[0][0][0];
	
    mass=periodicTable[elem].mass * 1e-27;
    atom[Nexatom].massacc= Dt*Dt / mass;
	
    /* set position and initialize thermal velocity */
    Positions[Nexatom]=posn;
    OldPositions[Nexatom]=posn;
    AveragePositions[Nexatom]=posn;
    // assuming the structure is minimized, half of this will 
    // disappear into Pe on average 
    therm = sqrt(2.0*(Boltz*Temperature)/mass)*Dt/Dx;
    v=gxyz(therm);
    vsub(OldPositions[Nexatom],v);
	
    /* thermostat trigger stays high, since slower motions shouldn't
       reach the unstable simulation regions of phase space
       {not currently used}

    therm = sqrt((2.0*Boltz*300.0)/mass)*Dt/Dx;
    atom[Nexatom].vlim=(3*therm)*(3*therm);
    */
	
    TotalKE += Boltz*Temperature*1.5;
    atom[Nexatom].energ = (mass*Dx*Dx)/(Dt*Dt);
	
    /* add contribution to overall mass center, momentum */
    totMass += mass;
	
    vmul2c(foo,posn,mass);
    vadd(Cog,foo);
	
    vmul2c(p,v,mass);
    vadd(P,p);
	
    /*
      v=vdif(positions[Nexatom],old_positions[Nexatom]);
      printf("makatom(%d)  V=%.2f ", Nexatom, vlen(v));
      pv(positions[Nexatom]); pvt(old_positions[Nexatom]);
    */
    Nexatom++;
	
}



/** an actual bond is ordered so it has a positive type,
    e.g. atom[a].elt <= atom[b].elt */
/* file format now guarantees no bond before its atoms */
void
makbond(int a, int b, char ord) {
    int n, t, typ, ta, tb, a1, a2;
    double bl, sbl;

    /*****************************************************************************************************/
    /* Patch to insure that multiple bonds get treated as single bonds until we do the right thing. */
    //ord='1';
    /*****************************************************************************************************/

    /*****************************************************************************************************/
    // patch to pretend that carbomeric bonds are double bonds
    if (ord=='c') {
      ord = '2';
    }
    /*****************************************************************************************************/
    
    DPRINT(D_READER, "making bond %d--%d\n",a,b);
    bond[Nexbon].an1=a;
    bond[Nexbon].an2=b;
    bond[Nexbon].order=ord;
	
    n = Nexbon++;

    a=bond[n].an1;
    b=bond[n].an2;
	
    ta=atom[a].elt;
    tb=atom[b].elt;
    if (tb<ta) {t=a; a=b; b=t; t=ta; ta=tb; tb=t;}
	
    typ=bontyp(bond[n].order,ta,tb);
    bond[n].an1=a;
    bond[n].an2=b;
	
    bond[n].type=getBondStretch(ta, tb, ord);

    a1=bond[n].an1;
    atom[a1].bonds[atom[a1].nbonds++]=n;
    a2=bond[n].an2;
    atom[a2].bonds[atom[a2].nbonds++]=n;

	
    bl = vlen(vdif(Positions[a], Positions[b]));
    sbl = bond[n].type->r0;
    /*
    if (bl> 1.11*sbl || bl<0.89*sbl)
	printf("Strained bond: %2f vs %2f  (%s%d-%s%d)\n",bl,sbl,
		  periodicTable[atom[a].elt].symbol, a, periodicTable[atom[b].elt].symbol, b);
    */
}

/** torqs are ordered so the bonds match those in bendata */
void
maktorq(int center, int a, int b)
{
  // center is index into atom[]
  // a and b are indexes into bond[]
  int element_center;
  int element_1;
  int element_2;
  
  element_center = atom[center].elt;
  torq[Nextorq].ac = center;

  if (bond[a].an1 == center) {
    element_1 = atom[bond[a].an2].elt;
    torq[Nextorq].dir1=1;
    torq[Nextorq].a1=bond[a].an2;
  } else if (bond[a].an2 == center) {
    element_1 = atom[bond[a].an1].elt;
    torq[Nextorq].dir1=0;
    torq[Nextorq].a1=bond[a].an1;
  } else {
    // print a better error if it ever happens...
    fprintf(stderr, "neither end of bond on center!");
  }

  if (bond[b].an1 == center) {
    element_2 = atom[bond[b].an2].elt;
    torq[Nextorq].dir2=1;
    torq[Nextorq].a2=bond[b].an2;
  } else if (bond[b].an2 == center) {
    element_2 = atom[bond[b].an1].elt;
    torq[Nextorq].dir2=0;
    torq[Nextorq].a2=bond[b].an1;
  } else {
    // print a better error if it ever happens...
    fprintf(stderr, "neither end of bond on center!");
  }
	
  torq[Nextorq].b1=bond+a;
  torq[Nextorq].b2=bond+b;
  torq[Nextorq].type = getBendData(element_center,
                                   element_1, bond[a].order,
                                   element_2, bond[b].order);
	
  Nextorq++;
}

/** make a vdw in one go, in calc loop */
void makvdw(int a1, int a2) {
    struct vdWbuf *newbuf;
    int i, j;
	
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
    Nexvanbuf->item[Nexvanbuf->fill].table = getVanDerWaalsTable(i, j);
	
    Nexvanbuf->fill++;
}


int
makcon(int typ, struct MOT *mot, int n, int *atnos) {
    int i;
	
    Constraint[Nexcon].type = typ;
    Constraint[Nexcon].natoms=n;
    Constraint[Nexcon].motor=mot;
    Constraint[Nexcon].atoms = (int *)allocate(n * sizeof(int));
    for (i=0; i<n; i++) Constraint[Nexcon].atoms[i]=atnos[i];
    return Nexcon++;
}

/** input torque in nN*nm,  speed in gigahertz
    store in pN*pm, rad/Dt
*/

struct MOT *
makmot(double stall, double speed, struct xyz vec1,  struct xyz vec2)
{
    int i;
	
    Motor[Nexmot].center=vec1;
    Motor[Nexmot].axis=uvec(vec2);
    Motor[Nexmot].stall=stall*(1e-9/Dx)*(1e-9/Dx);
    Motor[Nexmot].speed=speed*1e9*2.0*Pi* Dt;
	
    return Motor+Nexmot++;
}

void
makmot2(int i) {
    struct MOT *mot;
    struct xyz r, q, vrmax;
    int j, *atlis;
    double x, mass, rmax=0.0, mominert=0.0;
	
    if (Constraint[i].type != CODEmotor) return;
	
    atlis = Constraint[i].atoms;
    mot = Constraint[i].motor;
	
    for (j=0;j<Constraint[i].natoms;j++) {
	/* for each atom connected to the "shaft" */
	mass = periodicTable[atom[atlis[j]].elt].mass * 1e-27;
		
	/* find its projection onto the rotation vector */
	r=vdif(Positions[atlis[j]],mot->center);
	x=vdot(r,mot->axis);
	vmul2c(q,mot->axis,x);
	vadd2(mot->atocent[j],q,mot->center);
		
	/* and orthogonal distance */
	r=vdif(Positions[atlis[j]],mot->atocent[j]);
	mot->ator[j] = r;
	mot->radius[j]=vlen(r);
	if (mot->radius[j] > rmax) vrmax=r;
		
	mominert += mot->radius[j]*mass;
    }
    // mot->moment = (Dt*Dt)/mominert;
    // give the motor a flywheel w/ Tc about a picosecond
    mot->moment = (Dt*Dt)/(mot->stall*1e8*1e-27/(1e-9/Dx));
    DPRINT(D_READER, "moment %e\n", mot->moment);
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
    if (mot->speed==0.0) mot->theta = mot->atang[0];
}

/** input force in pN,  stiffness in N/m
    internal units are pN and pm, so no translation necessary
*/

struct MOT *
maklmot(double force, double stiff, struct xyz vec1,  struct xyz vec2)
{
    int i;
	
    Motor[Nexmot].axis=uvec(vec2);
    Motor[Nexmot].stall=force;
    Motor[Nexmot].speed=stiff;
	
    return Motor+Nexmot++;
}

void
maklmot2(int i) {
    struct MOT *mot;
    struct xyz r, q, vrmax;
    int j, *atlis;
    double x, c;
	
    if (Constraint[i].type != CODElmotor) return;
	
    atlis = Constraint[i].atoms;
    mot = Constraint[i].motor;

    // r is average shaft-atom position

    r = vcon(0.0);
	
    for (j=0;j<Constraint[i].natoms;j++) 
      /* for each atom connected to the "shaft" */
      r=vsum(r,Positions[atlis[j]]);
    
    r=vprodc(r, 1.0/Constraint[i].natoms);

    // x is length of projection of r onto axis
    x=vdot(r,mot->axis);
    // save it -- the initial position
    mot->theta = x;

    // note .stall is force and .speed is stiffness
    // .theta0 will be projection dist of r onto axis for 0 force
    if (mot->speed == 0.0) {
      mot->theta0 = x;
    } else {
      mot->theta0 = x + mot->stall/mot->speed;
    }

    // if constant force, just use this force vector
    if (mot->speed == 0.0) 
      mot->center = vprodc(mot->axis,mot->stall/Constraint[i].natoms);
    

}

static int readname(char *buf, char **ret) {

  char b1[128];
  int j;
  sscanf(buf, "(%[^)])%n", b1, &j);
  DPRINT(D_READER, "got name (%s)\n", b1);
  *ret = malloc(strlen(b1)+1);
  strcpy(*ret, b1);
  return j;

}

static int readshaft(char *buf, int *iv, int *atnotab) {

  int i, j;
	
  DPRINT(D_READER, "from <%s> ", buf);
  j=sscanf(buf, "%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d%d",
	   iv, iv+1, iv+2, iv+3, iv+4, iv+5, iv+6, iv+7, iv+8, iv+9,
	   iv+10, iv+11, iv+12, iv+13, iv+14, iv+15, iv+16, iv+17,
	   iv+18, iv+19, iv+20, iv+21, iv+22, iv+23, iv+24, iv+25,
	   iv+26, iv+27, iv+28, iv+29);
  DPRINT(D_READER, "got shaft of %d atoms\n",j);
  for (i=0; i<j; i++) iv[i]=atnotab[iv[i]];
  return j;
}


/** file reading */

void filred(char *filnam) {
	
    FILE *file;
    char buf[256];
    char ord;
    int i, j, n, m, b, c, lastatom;
    double stall, speed, force, stiff;
    struct xyz vec1,vec2;
    int a1, a2, ie, ix, iy, iz, ix1, iy1, iz1, iv[NJATOMS];
    int firstatom=1, offset;
    int atnum, atnotab[2*NATOMS];
    struct vdWbuf *nvb;
    char nambuf[128],nambuf2[128], *strg, *junk;
    int colr[3];
	
    file=fopen(filnam,"r");
    if (file==NULL) {
      perror(filnam);
      exit(1);
    }
	
    while (fgets(buf,255,file)) {
	/* atom number (element) (posx, posy, posz) */
	/* position vectors are integral 0.1pm */
	if (0==strncasecmp("atom",buf,4)) {
	    sscanf(buf+4, "%d (%d) (%d,%d,%d", &atnum, &ie, &ix, &iy, &iz);

            DPRINT(D_READER, "in filred: %s %d (%d) (%d,%d,%d) \n","atom",
                   lastatom,ie, ix, iy, iz );
	    
	    // hack: change singlets to hydrogen
	    // if (ie == 0) ie=1;

	    atnotab[atnum]=Nexatom;
	    lastatom = Nexatom;
			
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    makatom(ie,vec1);
	}


	/* bondO atno atno atno ... (where O is order) */
	else if (0==strncasecmp("bond",buf,4)) {
	  DPRINT(D_READER, "%s\n",buf);
          ord = buf[4];
	  j=readshaft(buf+5, iv, atnotab);
	  DPRINT(D_READER, "j=%d\n",j);
	  for (i=0; i<j; i++) makbond(lastatom, iv[i], ord);
	}
		
	/* [vander]Waals atno atno atno ... (for atoms on same part) */
	else if (0==strncasecmp("waals",buf,5)) {
			
	    j=readshaft(buf+5, iv, atnotab);
			
	    for (i=0; i<j; i++) makvdw(lastatom,iv[i]);
	}
		
	/* constraints */
	/* welded to space: */
	// ground (<name>) <atoms>
	// accept "anchor" as synonym for "ground" wware 051213
	else if (0==strncasecmp("ground",buf,6) ||
		 0==strncasecmp("anchor",buf,6)) {
	  j=readname(buf+7,&strg);
	  i=readname(buf+7+j+1, &junk);
	  j=readshaft(buf+7+j+i+1, iv, atnotab);
	  i=makcon(CODEground, NULL, j, iv);
	  Constraint[i].name = strg;
	}
	
	// thermometer
	// thermo (name) (r, g, b) <atom1> <atom2>
	else if (0==strncasecmp("thermo",buf,6)) {
	  i=readname(buf+7,&strg);
	  sscanf(buf+7+i, " (%[0-9, ]) %n", nambuf, &j);

	  j=readshaft(buf+7+i+j, iv, atnotab);

	  DPRINT(D_READER, "got thermometer (%s) @%d\n", strg, j);
	  DPRINT(D_READER, "got shaft of %d atoms\n",j);

	  i=makcon(CODEtemp, NULL, j, iv);
	  Constraint[i].name = strg;
	}

	// angle meter
	// angle (name) <atoms>
	else if (0==strncasecmp("angle",buf,5)) {

	  j=readname(buf+6,&strg);
	  DPRINT(D_READER, "got angle meter (%s) @%d\n", strg, j);
	  j=readshaft(buf+6+j, iv, atnotab);
	  i=makcon(CODEangle, NULL, j, iv);
	  Constraint[i].name = strg;
	}

	// radius meter
	// radius (name) <atoms>
	else if (0==strncasecmp("radius",buf,6)) {

	  j=readname(buf+7,&strg);
	  DPRINT(D_READER, "got radius meter (%s) @%d\n", strg, j);
	  j=readshaft(buf+7+j, iv, atnotab);
	  i=makcon(CODEradius, NULL, j, iv);
	  Constraint[i].name = strg;
	}

	// Langevin thermostat
	// stat (name) (r, g, b) (temp) atom1 atom2
	else if (0==strncasecmp("stat",buf,4)) {
	  i=readname(buf+5,&strg);
	  sscanf(buf+5+i, " (%[0-9, ]) (%d)%n", nambuf, &ix, &j);
	  DPRINT(D_READER, "%s%sgot stat (%s) %d @%d\n", buf+5+i, buf+5+i+j, strg, ix, j);
	  j=readshaft(buf+5+i+j, iv, atnotab);
	  i=makcon(CODEstat, NULL, j, iv);
	  Constraint[i].temp = ix;
	  Constraint[i].name = strg;
	}

	// motor
	/* rmotor (name) (r,g,b) <torque> <speed> (<center>) (<axis>) */
	/* torque in nN*nm  speed in gigahertz */
	else if (0==strncasecmp("rmotor",buf,6)) {
	    j=readname(buf+7,&strg);
	    sscanf(buf+j+7, " (%[0-9, ]) %lf %lf (%d, %d, %d) (%d, %d, %d",
		   nambuf, &stall, &speed, &ix, &iy, &iz, &ix1, &iy1, &iz1);
	    DPRINT(D_READER, "%s\ngot motor (%s)  %lf %lf (%d, %d, %d) (%d, %d, %d) \n",
                   buf,strg,stall,speed, ix, iy, iz, ix1, iy1, iz1);
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) {
              fprintf(stderr, "motor needs a shaft: %d\n", j);
            } else {
	      j=readshaft(buf+5, iv, atnotab);

	      i=makcon(CODEmotor, makmot(stall, speed, vec1, vec2), j, iv);
	      makmot2(i);
	    }
	    Constraint[i].name = strg;
	}

	// bearing 
	/* bearing (name) (r,g,b) (<center>) (<axis>) */
	else if (0==strncasecmp("bearing",buf,7)) {
	  for (i=2,j=8;i;j++) if (buf[j]==')') i--;
	    sscanf(buf+j+1, " (%d, %d, %d) (%d, %d, %d",
		    &ix, &iy, &iz, &ix1, &iy1, &iz1);
	    DPRINT(D_READER, "%s\ngot bearing (%d)  (%d, %d, %d) (%d, %d, %d) \n",
		   buf,j, ix, iy, iz, ix1, iy1, iz1);	
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) {
              fprintf(stderr, "bearing needs a shaft: %d\n", j);
            } else {
	      j=readshaft(buf+5, iv, atnotab);

	      i=makcon(CODEbearing, makmot(stall, speed, vec1, vec2), j, iv);
	      makmot2(i);
              Constraint[i].name = strg;
	    }
	}
		
	// linear motor
	/* lmotor (name) (r,g,b) <force> <stiff> (<center>) (<axis>) */
	else if (0==strncasecmp("lmotor",buf,6)) {
	    j=readname(buf+7,&strg);
	    sscanf(buf+j+7, " (%[0-9, ]) %lf %lf (%d, %d, %d) (%d, %d, %d",
		   nambuf, &force, &stiff, &ix, &iy, &iz, &ix1, &iy1, &iz1);
	    printf( "%s\ngot motor (%s)  %lf %lf (%d, %d, %d) (%d, %d, %d) \n",
                   buf,strg,force,stiff, ix, iy, iz, ix1, iy1, iz1);
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) {
              fprintf(stderr, "lmotor needs a shaft\n");
            } else {
	      j=readshaft(buf+5, iv, atnotab);
	      i=makcon(CODElmotor, maklmot(force, stiff, vec1, vec2), j, iv);
	      maklmot2(i);
              Constraint[i].name = strg;
	    }
	}
		
	// spring
	/* spring <stiffness>, (<center1>) (<center2>) */
	else if (0==strncasecmp("spring",buf,6)) {
	  for (i=2,j=7;i;j++) if (buf[j]==')') i--;
	  sscanf(buf+5, " (%d, %d, %d) %lf, %lf, (%d, %d, %d) (%d, %d, %d",
		   nambuf, colr, colr+1, colr+2,
		   &stall, &speed, &ix, &iy, &iz, &ix1, &iy1, &iz1);
			
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) {
              fprintf(stderr, "spring needs a shaft\n");
            } else {
	      j=readshaft(buf+5, iv, atnotab);
	      i=makcon(CODEspring, makmot(stall, speed, vec1, vec2), j, iv);
	      makmot2(i);
	    }
	}
		
	// slider
	/* slider (<center>) (<axis>) */
	/* torque in nN*nm  speed in gigahertz */
	else if (0==strncasecmp("slider",buf,6)) {
	  for (i=2,j=7;i;j++) if (buf[j]==')') i--;
	  sscanf(buf+5, " (%d, %d, %d) %lf, %lf, (%d, %d, %d) (%d, %d, %d",
		   nambuf, colr, colr+1, colr+2,
		   &stall, &speed, &ix, &iy, &iz, &ix1, &iy1, &iz1);
			
	    vec1.x=(double)ix *0.1;
	    vec1.y=(double)iy *0.1;
	    vec1.z=(double)iz *0.1;
	    vec2.x=(double)ix1 *0.1;
	    vec2.y=(double)iy1 *0.1;
	    vec2.z=(double)iz1 *0.1;
	    fgets(buf,127,file);
	    if (strncasecmp("shaft",buf,5)) {
              fprintf(stderr, "slider needs a shaft\n");
            } else {
	      j=readshaft(buf+5, iv, atnotab);
	      i=makcon(CODEslider, makmot(stall, speed, vec1, vec2), j, iv);
	      makmot2(i);
	    }
	}
    
	// kelvin <temperature>
	else if (0==strncasecmp("kelvin",buf,6)) {
	    sscanf(buf+6, "%d", &ix);
	    // Temperature = (double)ix;
	    // printf("Temperature set to %f\n",Temperature);
	}
		
	else if (0==strncasecmp("end",buf,3)) {
	  break;
	}
		
	DPRINT(D_READER, "??? %s\n", buf);
		
    }
    fclose(file);
	

    /* got all the static vdW bonds we'll see */
    Dynobuf = Nexvanbuf;
    Dynoix = Nexvanbuf->fill;
	

    /*
      for (i=0; i<Nexatom; i++) pa(i);
      for (i=0; i<Nexbon; i++) pb(i);
    */
	
    /* create bending bonds */
    for (i=0; i<Nexatom; i++) {
      for (m=0; m<atom[i].nbonds-1; m++) {
	    for (n=m+1; n<atom[i].nbonds; n++) {
          checkatom(stderr, i); // move outside of m loop?
          maktorq(i, atom[i].bonds[m], atom[i].bonds[n]);
	    }
      }
    }
	
    /* find bounding box */
	
    vset(vec1, Positions[0]);
    vset(vec2, Positions[0]);
	
    for (i=1; i<Nexatom; i++) {
	vmin(vec1,Positions[i]);
	vmax(vec2,Positions[i]);
    }
    vadd2(Center, vec1, vec2);
    vmulc(Center, 0.5);
	
    vset(Bbox[0], vsum(vec1, vcon(-100.0)));
    vset(Bbox[1], vsum(vec2, vcon(100.0)));

    // center of gravity
    vmulc(Cog,1.0/totMass);

    // total velocity
    
    vmul2c(vec1,P,1.0/totMass);
    for (i=1; i<Nexatom; i++) {
	vadd(OldPositions[i],vec1);
    }
    
	
}

// reads atom positions from an XYZ file into Positions[]
// returns the number of atoms read, or -1 for an error.
struct xyz *
readXYZ(char *filename, int *natoms)
{
  int i;
  float x, y, z;
  char symbol[12];
  struct xyz *positions;

  FILE *f = fopen(filename, "r");
  if (f == NULL) {
    perror(filename);
    return NULL;
  }
  if (fscanf(f, "%d\n", natoms) != 1 || *natoms < 1 || *natoms > NATOMS) {
    fprintf(stderr, "error reading atom count from xyz file: %s\n", filename);
    fclose(f);
    return NULL;
  }
  positions= (struct xyz *)allocate(sizeof(struct xyz) * *natoms);
  fscanf(f, "%*s\n"); // skip the RMS=xxx.xx line
  for (i=0; i<*natoms; i++) {
    if (fscanf(f, "%10s %f %f %f\n", symbol, &x, &y, &z) != 4) {
      fprintf(stderr, "error reading atom %d from %s\n", i, filename);
      fclose(f);
      free(positions);
      return NULL;
    }
    positions[i].x = x;
    positions[i].y = y;
    positions[i].z = z;
  }
  return positions;
}
