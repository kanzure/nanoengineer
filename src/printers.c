// Copyright (c) 2004 Nanorex, Inc. All Rights Reserved.
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "simulator.h"

void pbontyp(struct bsdata *ab) {
    printf("Bond between %d / %d of order %d: type %d, length %f, stiffness %f\n table %d, start %f, scale %d\n",
	      ab->a1,ab->a2,ab->ord,ab->typ,ab->r0,ab->ks,
	      ab->table,ab->start,ab->scale);
	
}

void bondump() {		/* gather bond statistics */
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
	r=vlen(vdif(cur[bond[i].an1], cur[bond[i].an2]));
	means[btyp] += r;
	perc = (r/bt->r0)*20.0 - 8.5;
	k=(int)perc;
	if (k<0) k=0;
	if (k>22) k=22;
	histo[btyp][k]++;
    }
	
    for (i=0; i<BSTABSIZE; i++) if (totno[i]) {
	printf("Bond type %s-%s, %d occurences, mean %.2f pm:\n",
		  element[bstab[i].a1].symbol, element[bstab[i].a2].symbol, totno[i],
		  means[i]/(double)totno[i]);
	for (j=0; j<23; j++) {
	    if ((j-1)%10) printf(" |");
	    else printf("-+");
	    n=(80*histo[i][j])/totno[i];
	    if (histo[i][j] && n==0) printf(".");
	    for (k=0; k<n; k++) printf("M");
	    printf("\n");
	}}
    printf("Iteration %d\n",Iteration);
}


void pangben(struct angben *ab) {
    printf("Bend between %d / %d: kb=%.2f, th0=%.2f\n",
	   ab->b1typ,ab->b2typ,ab->kb,ab->theta0);

}

void speedump() {		/* gather bond statistics */
    int histo[20], iv, i, j, k, n;
    double v, eng, toteng=0.0;
	
    for (i=0; i<21; i++) {
	histo[i]=0;
    }
	
    for (i=0; i<Nexatom; i++) {
	v=vlen(vdif(old[i],cur[i]));
	eng= atom[i].energ*v*v;
	toteng += eng;
	iv=(int)(eng*1e21);
	if (iv>20) iv=20;
	histo[iv]++;
    }
	
    printf("Kinetic energies:\n");
    for (j=0; j<21; j++) {
	if (j%5) printf(" |");
	else printf("-+");
	n=(70*histo[j])/Nexatom;
	if (histo[j] && n==0) printf(".");
	for (k=0; k<n; k++) printf("M");
	printf("\n");
    }
    printf("Iteration %d, KE %e --> %e\n",Iteration,TotalKE,FoundKE);
}

void pv(struct xyz foo) {
    printf("(%.2f, %.2f, %.2f)",foo.x, foo.y, foo.z);
}
void pvt(struct xyz foo) {
    printf("(%.2f, %.2f, %.2f)\n",foo.x, foo.y, foo.z);
}

void pa(int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) printf("bad atom number %d\n",i);
    else {
	printf("atom %s%d (%d bonds): ", element[atom[i].elt].symbol, i, atom[i].nbonds);
	for (j=0; j<atom[i].nbonds; j++) {
	    b=atom[i].bonds[j];
	    ba=(i==bond[b].an1 ? bond[b].an2 : bond[b].an1);
	    printf("[%d/%d]: %s%d, ", b, bond[b].order,
		      element[atom[ba].elt].symbol, ba);
	}
	v=vlen(vdif(cur[i],old[i]));
	printf("\n   V=%.2f, mV^2=%.6f, pos=", v,1e-4*v*v/atom[i].massacc);
	pv(cur[i]); pvt(old[i]);
	printf("   mass = %f, massacc=%e\n", element[atom[i].elt].mass,
	       atom[i].massacc);
    }
}

void checkatom(int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) printf("bad atom number %d\n",i);
    else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
	printf("bad element in atom %d: %d\n", i, atom[i].elt);
    else if (atom[i].nbonds <0 || atom[i].nbonds >NBONDS)
	printf("bad nbonds in atom %d: %d\n", i, atom[i].nbonds);
    else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
	printf("bad element in atom %d: %d\n", i, atom[i].elt);
    else for (j=0; j<atom[i].nbonds; j++) {
	b=atom[i].bonds[j];
	if (b < 0 || b >= Nexbon)
	    printf("bad bonds number in atom %d: %d\n", i, b);
	else if (i != bond[b].an1 && i != bond[b].an2) {
	    printf("bond %d of atom %d [%d] doesn't point back\n", j, i, b);
	    exit(0);
	}
    }
}

void pb(int i) {
    double len;
    struct bsdata *bt;
    int index;
	
    if (i<0 || i>=Nexbon) printf("bad bond number %d\n",i);
    else {
	bt = bond[i].type;
	len = vlen(vdif(cur[bond[i].an1],cur[bond[i].an2]));
	printf("bond %d[%d] [%s%d(%d)-%s%d(%d)]: length %.1f\n",
		  i, bond[i].order,
		  element[atom[bond[i].an1].elt].symbol, bond[i].an1, atom[bond[i].an1].elt,
		  element[atom[bond[i].an1].elt].symbol, bond[i].an2, atom[bond[i].an2].elt,
		  len);
	index=(int)((len*len)-bt->start)/bt->scale;
	if (index<0 || index>=TABLEN)
	    printf("r0=%.1f, index=%d of %d, off table\n",  bt->r0, index, TABLEN);
	else printf("r0=%.1f, index=%d of %d, value %f\n", bt->r0, index, TABLEN,
		       bt->table->t1[index] + len*len*bt->table->t2[index]);
    }
}

void pq(int i) {
    struct xyz r1, r2;
    if (i<0 || i>=Nextorq) printf("bad torq number %d\n",i);
    else {
	printf("torq %s%d-%s%d-%s%d, that's %d-%d=%d-%d\n",
		  element[atom[torq[i].a1].elt].symbol, torq[i].a1,
		  element[atom[torq[i].ac].elt].symbol, torq[i].ac,
		  element[atom[torq[i].a2].elt].symbol, torq[i].a2,
		  (torq[i].dir1 ? torq[i].b1->an2 :  torq[i].b1->an1),
		  (torq[i].dir1 ? torq[i].b1->an1 :  torq[i].b1->an2),
		  (torq[i].dir2 ? torq[i].b2->an1 :  torq[i].b2->an2),
		  (torq[i].dir2 ? torq[i].b2->an2 :  torq[i].b2->an1));
		
	r1=vdif(cur[torq[i].a1],cur[torq[i].ac]);
	r2=vdif(cur[torq[i].a2],cur[torq[i].ac]);
	printf("r1= %.1f, r2= %.1f, theta=%.2f (%.0f)",
		  vlen(r1), vlen(r2), vang(r1, r2),
		  (180.0/3.1415)*vang(r1, r2));
	printf(" theta0=%f, Kb=%f\n",torq[i].type->theta0,
	       torq[i].type->kb);
    }
}

void pvdw(struct vdWbuf *buf, int n) {
    printf("vdW %s%d-%s%d: vanderTable[%d]\n",
	      element[atom[buf->item[n].a1].elt].symbol, buf->item[n].a1,
	      element[atom[buf->item[n].a2].elt].symbol, buf->item[n].a2,
	      buf->item[n].table - vanderTable);
    printf("start; %f, scale %d, b=%f, m=%f\n",
	      sqrt(buf->item[n].table->start), buf->item[n].table->scale,
	      buf->item[n].table->table.t1[0],
	      buf->item[n].table->table.t2[0]);
	
}

void pcon(int i) {
    struct MOT *mot;
    int j;
	
    if (i<0 || i>=Nexcon) {
	printf("Bad constraint number %d\n",i);
	return;
    }
    printf("Constraint %d: ",i);
    if (Constraint[i].type == CODEground) {
	printf("Ground:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODEtemp) {
	printf("Thermometer %s:\n atoms ",Constraint[i].name);
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODEstat) {
	printf("Thermostat %s (%f):\n atoms ",
	       Constraint[i].name,Constraint[i].data);
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODEbearing) {
	printf("Bearing:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODElmotor) {
	printf("Linear motor:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODEspring) {
	printf("Spring:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODEslider) {
	printf("Slider:\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    printf("%d ",Constraint[i].atoms[j]);
	printf("\n");
    }
    else if (Constraint[i].type == CODEmotor) {
	mot = Constraint[i].motor;
	printf("motor; stall torque %.2e, unloaded speed %.2e\n center ",
		  mot->stall, mot->speed);
	pv(mot->center);
	printf(" axis ");
	pvt(mot->axis);
		
	printf(" rot basis ");
	pv(mot->roty); pv(mot->rotz);
	printf(" angles %.0f, %.0f, %.0f\n",
		  180.0*vang(mot->axis,mot->roty)/Pi,
		  180.0*vang(mot->rotz,mot->roty)/Pi,
		  180.0*vang(mot->axis,mot->rotz)/Pi);
		
	for (j=0;j<Constraint[i].natoms;j++) {
	    printf(" atom %d radius %.1f angle %.2f\n   center ",
		      Constraint[i].atoms[j], mot->radius[j], mot->atang[j]);
	    pv(mot->atocent[j]);
	    printf(" posn "); pvt(mot->ator[j]);
	}
	printf(" Theta=%.2f, theta0=%.2f, moment factor =%e\n",
		  mot->theta, mot->theta0, mot->moment);
    }
}


void headcon(FILE *f) {
    struct MOT *mot;
    int i, j;

    fprintf(f, "#");

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
    fprintf(f, "\n#");

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

    for (i=0; i<Nexcon; i++) {
        switch (Constraint[i].type) {
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
	case CODEangle:  
	case CODEradius: 
	    fprintf(f, "%8.2f",Constraint[i].data);
	    Constraint[i].data = 0.0;
	    break;
	case CODEmotor:  
	    fprintf(f, "%8.4f%8.4f",Constraint[i].data,
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
