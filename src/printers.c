// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "simulator.h"

void pbontyp(FILE *f, struct bsdata *ab) {
    fprintf(f, "Bond between %d / %d of order %d: type %d, length %f, stiffness %f\n table %d, start %f, scale %d\n",
	      ab->a1,ab->a2,ab->ord,ab->typ,ab->r0,ab->ks,
	      ab->table,ab->start,ab->scale);
	
}

void bondump(FILE *f) {		/* gather bond statistics */
    int histo[50][23], totno[50], btyp, i, j, k, n;
    double r, perc, means[50];
    struct bsdata *bt;
	
    for (i=0; i<50; i++) {
	totno[i] = 0;
	means[i] = 0.0;
	for (j=0; j<23; j++)
	    histo[i][j]=0;
    }
	
    for (i=0; i<Nexbon; i++) {
	bt=bond[i].type;
	btyp = bt-bstab;
	totno[btyp]++;
	r=vlen(vdif(positions[bond[i].an1], positions[bond[i].an2]));
	means[btyp] += r;
	perc = (r/bt->r0)*20.0 - 8.5;
	k=(int)perc;
	if (k<0) k=0;
	if (k>22) k=22;
	histo[btyp][k]++;
    }
	
    for (i=0; i<BSTABSIZE; i++) if (totno[i]) {
	fprintf(f, "Bond type %s-%s, %d occurences, mean %.2f pm:\n",
		  element[bstab[i].a1].symbol, element[bstab[i].a2].symbol, totno[i],
		  means[i]/(double)totno[i]);
	for (j=0; j<23; j++) {
	    if ((j-1)%10) fprintf(f, " |");
	    else fprintf(f, "-+");
	    n=(80*histo[i][j])/totno[i];
	    if (histo[i][j] && n==0) fprintf(f, ".");
	    for (k=0; k<n; k++) fprintf(f, "M");
	    fprintf(f, "\n");
	}}
    fprintf(f, "Iteration %d\n",Iteration);
}


void pangben(FILE *f, struct angben *ab) {
    fprintf(f, "Bend between %d / %d: kb=%.2f, th0=%.2f\n",
	   ab->b1typ,ab->b2typ,ab->kb,ab->theta0);

}

void speedump(FILE *f) {		/* gather bond statistics */
    int histo[20], iv, i, j, k, n;
    double v, eng, toteng=0.0;
	
    for (i=0; i<21; i++) {
	histo[i]=0;
    }
	
    for (i=0; i<Nexatom; i++) {
	v=vlen(vdif(old_positions[i],positions[i]));
	eng= atom[i].energ*v*v;
	toteng += eng;
	iv=(int)(eng*1e21);
	if (iv>20) iv=20;
	histo[iv]++;
    }
	
    fprintf(f, "Kinetic energies:\n");
    for (j=0; j<21; j++) {
	if (j%5) fprintf(f, " |");
	else fprintf(f, "-+");
	n=(70*histo[j])/Nexatom;
	if (histo[j] && n==0) fprintf(f, ".");
	for (k=0; k<n; k++) fprintf(f, "M");
	fprintf(f, "\n");
    }
    fprintf(f, "Iteration %d, KE %e --> %e\n",Iteration,TotalKE,FoundKE);
}

void pv(FILE *f, struct xyz foo) {
    fprintf(f, "(%.2f, %.2f, %.2f)",foo.x, foo.y, foo.z);
}
void pvt(FILE *f, struct xyz foo) {
    fprintf(f, "(%.2f, %.2f, %.2f)\n",foo.x, foo.y, foo.z);
}

void pa(FILE *f, int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) fprintf(f, "bad atom number %d\n",i);
    else {
	fprintf(f, "atom %s%d (%d bonds): ", element[atom[i].elt].symbol, i, atom[i].nbonds);
	for (j=0; j<atom[i].nbonds; j++) {
	    b=atom[i].bonds[j];
	    ba=(i==bond[b].an1 ? bond[b].an2 : bond[b].an1);
	    fprintf(f, "[%d/%d]: %s%d, ", b, bond[b].order,
		      element[atom[ba].elt].symbol, ba);
	}
	v=vlen(vdif(positions[i],old_positions[i]));
	fprintf(f, "\n   V=%.2f, mV^2=%.6f, pos=", v,1e-4*v*v/atom[i].massacc);
	pv(f, positions[i]);
        pvt(f, old_positions[i]);
	fprintf(f, "   mass = %f, massacc=%e\n", element[atom[i].elt].mass,
	       atom[i].massacc);
    }
}

void checkatom(FILE *f, int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) fprintf(f, "bad atom number %d\n",i);
    else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
	fprintf(f, "bad element in atom %d: %d\n", i, atom[i].elt);
    else if (atom[i].nbonds <0 || atom[i].nbonds >NBONDS)
	fprintf(f, "bad nbonds in atom %d: %d\n", i, atom[i].nbonds);
    else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
	fprintf(f, "bad element in atom %d: %d\n", i, atom[i].elt);
    else for (j=0; j<atom[i].nbonds; j++) {
	b=atom[i].bonds[j];
	if (b < 0 || b >= Nexbon)
	    fprintf(f, "bad bonds number in atom %d: %d\n", i, b);
	else if (i != bond[b].an1 && i != bond[b].an2) {
	    fprintf(f, "bond %d of atom %d [%d] doesn't point back\n", j, i, b);
	    exit(0);
	}
    }
}

void pb(FILE *f, int i) {
    double len;
    struct bsdata *bt;
    int index;
	
    if (i<0 || i>=Nexbon) fprintf(f, "bad bond number %d\n",i);
    else {
	bt = bond[i].type;
	len = vlen(vdif(positions[bond[i].an1],positions[bond[i].an2]));
	fprintf(f, "bond %d[%d] [%s%d(%d)-%s%d(%d)]: length %.1f\n",
		  i, bond[i].order,
		  element[atom[bond[i].an1].elt].symbol, bond[i].an1, atom[bond[i].an1].elt,
		  element[atom[bond[i].an2].elt].symbol, bond[i].an2, atom[bond[i].an2].elt,
		  len);
	index=(int)((len*len)-bt->start)/bt->scale;
	if (index<0 || index>=TABLEN)
	    fprintf(f, "r0=%.1f, index=%d of %d, off table\n",  bt->r0, index, TABLEN);
	else fprintf(f, "r0=%.1f, index=%d of %d, value %f\n", bt->r0, index, TABLEN,
		       bt->table->t1[index] + len*len*bt->table->t2[index]);
    }
}

void printAllBonds(FILE *f) 
{
    int i;
    for (i=0; i<Nexbon; i++) {
        pb(f, i);
    }
}


void pq(FILE *f, int i) {
    struct xyz r1, r2;
    if (i<0 || i>=Nextorq) fprintf(f, "bad torq number %d\n",i);
    else {
	fprintf(f, "torq %s%d-%s%d-%s%d, that's %d-%d=%d-%d\n",
		  element[atom[torq[i].a1].elt].symbol, torq[i].a1,
		  element[atom[torq[i].ac].elt].symbol, torq[i].ac,
		  element[atom[torq[i].a2].elt].symbol, torq[i].a2,
		  (torq[i].dir1 ? torq[i].b1->an2 :  torq[i].b1->an1),
		  (torq[i].dir1 ? torq[i].b1->an1 :  torq[i].b1->an2),
		  (torq[i].dir2 ? torq[i].b2->an1 :  torq[i].b2->an2),
		  (torq[i].dir2 ? torq[i].b2->an2 :  torq[i].b2->an1));
		
	r1=vdif(positions[torq[i].a1],positions[torq[i].ac]);
	r2=vdif(positions[torq[i].a2],positions[torq[i].ac]);
	fprintf(f, "r1= %.1f, r2= %.1f, theta=%.2f (%.0f)\n",
		  vlen(r1), vlen(r2), vang(r1, r2),
		  (180.0/3.1415)*vang(r1, r2));
	fprintf(f, " theta0=%f, Kb=%f, Ks=%f\n",torq[i].theta0, torq[i].kb1,
	       torq[i].kb1/(vlen(r1) * vlen(r2)));
    }
}

void pvdw(FILE *f, struct vdWbuf *buf, int n) {
    fprintf(f, "vdW %s%d-%s%d: vanderTable[%d]\n",
	      element[atom[buf->item[n].a1].elt].symbol, buf->item[n].a1,
	      element[atom[buf->item[n].a2].elt].symbol, buf->item[n].a2,
	      buf->item[n].table - vanderTable);
    fprintf(f, "start; %f, scale %d, b=%f, m=%f\n",
	      sqrt(buf->item[n].table->start), buf->item[n].table->scale,
	      buf->item[n].table->table.t1[0],
	      buf->item[n].table->table.t2[0]);
	
}

void pcon(FILE *f, int i) {
    struct MOT *mot;
    int j;
	
    if (i<0 || i>=Nexcon) {
	fprintf(f, "Bad constraint number %d\n",i);
	return;
    }
    fprintf(f, "Constraint %d: ",i);

    switch (Constraint[i].type) {
	case CODEground: 
	fprintf(f, "Ground:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEtemp:
	fprintf(f, "Thermometer %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEstat:
	fprintf(f, "Thermostat %s (%f):\n atoms ",
	       Constraint[i].name,Constraint[i].data);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEbearing:
	fprintf(f, "Bearing:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODElmotor:
	fprintf(f, "Linear motor:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEspring:
	fprintf(f, "Spring:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEslider:
	fprintf(f, "Slider:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEmotor:
	mot = Constraint[i].motor;
	fprintf(f, "motor; stall torque %.2e, unloaded speed %.2e\n center ",
		  mot->stall, mot->speed);
	pv(f, mot->center);
	fprintf(f, " axis ");
	pvt(f, mot->axis);
		
	fprintf(f, " rot basis ");
	pv(f, mot->roty);
        pv(f, mot->rotz);
	fprintf(f, " angles %.0f, %.0f, %.0f\n",
		  180.0*vang(mot->axis,mot->roty)/Pi,
		  180.0*vang(mot->rotz,mot->roty)/Pi,
		  180.0*vang(mot->axis,mot->rotz)/Pi);
		
	for (j=0;j<Constraint[i].natoms;j++) {
	    fprintf(f, " atom %d radius %.1f angle %.2f\n   center ",
		      Constraint[i].atoms[j], mot->radius[j], mot->atang[j]);
	    pv(f, mot->atocent[j]);
	    fprintf(f, " posn ");
            pvt(f, mot->ator[j]);
	}
	fprintf(f, " Theta=%.2f, theta0=%.2f, moment factor =%e\n",
		  mot->theta, mot->theta0, mot->moment);
	break;
    case CODEangle:   
	fprintf(f, "Angle meter %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    case CODEradius:  
	fprintf(f, "radius measure %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    fprintf(f, "%d ",Constraint[i].atoms[j]);
	fprintf(f, "\n");
	break;
    }
}

void printargs(FILE *f, int argc, char **argv)
{
    int i;
    
    fprintf(f, "# simulator trace output\n");
    fprintf(f, "# program arguments:\n");
    fprintf(f, "# ");
    for (i=0; i<argc; i++) {
        fprintf(f, "%s ", argv[i]);
    }
    fprintf(f, "\n#\n");
}


void headcon(FILE *f) {
    struct MOT *mot;
    int i, j;

    fprintf(f, "#     Time ");

    for (i=0; i<Nexcon; i++) {

	Constraint[i].data=0.0;
	vsetc(Constraint[i].xdata,0.0);

        switch (Constraint[i].type) {
	case CODEground:  fprintf(f, "Ground  "); break;
	case CODEtemp:    fprintf(f, "T.meter "); break;
	case CODEstat:    fprintf(f, "T.stat  "); break;
	case CODEbearing: fprintf(f, "Bearing "); break;
	case CODElmotor:  fprintf(f, "Lmotor  "); break;
	case CODEspring:  fprintf(f, "Spring  "); break;
	case CODEslider:  fprintf(f, "Slider  "); break;
	case CODEmotor:   fprintf(f, "sped Motor torq ");
	    Constraint[i].temp=0.0;
	    break;
	case CODEangle:   fprintf(f, "Angle   "); break;
	case CODEradius:  fprintf(f, "Radius  "); break;
	}
    }
    fprintf(f, "\n#  picosec ");

    for (i=0; i<Nexcon; i++) {
	fprintf(f, "%-8.8s",Constraint[i].name);
	if (Constraint[i].type==CODEmotor)
	    fprintf(f, "        ");
    }

    fprintf(f, "\n#\n");

}


void tracon(FILE *f) {
    struct MOT *mot;
    double x;
    int i, j;

    fprintf(f, "%10.4f ", Iteration * Dt / PICOSEC);
    
    for (i=0; i<Nexcon; i++) {
        switch (Constraint[i].type) {
	case CODEangle:  
	    fprintf(f, "%8.5f",Constraint[i].data);
	    break;
	case CODEground: 
	    x=vlen(Constraint[i].xdata)/1e4;
	    fprintf(f, "%8.2f",x/Constraint[i].data);
	    Constraint[i].data=0.0;
	    vsetc(Constraint[i].xdata,0.0);
	    break;
	case CODEtemp:   
	case CODEstat:   
	case CODEbearing:
	case CODElmotor: 
	case CODEspring: 
	case CODEslider: 
	case CODEradius: 
	    fprintf(f, "%8.2f",Constraint[i].data);
	    Constraint[i].data = 0.0;
	    break;
	case CODEmotor:  
	    fprintf(f, "%8.3f%8.3f",Constraint[i].data/(Dt*2e9*Pi),
		    Constraint[i].temp/((1e-9/Dx)*(1e-9/Dx)));
	    Constraint[i].data = 0.0;
	    Constraint[i].temp = 0.0;
	    break;
	}
    }
    fprintf(f, "\n"); // each snapshot is one line
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
