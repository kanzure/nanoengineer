#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "simulator.h"

void pbontyp(struct bsdata *ab) {
    DBGPRINTF("Bond between %d / %d of order %d: type %d, length %f, stiffness %f\n table %d, start %f, scale %d\n",
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
	DBGPRINTF("Bond type %s-%s, %d occurences, mean %.2f pm:\n",
		  element[bstab[i].a1].symbol, element[bstab[i].a2].symbol, totno[i],
		  means[i]/(double)totno[i]);
	for (j=0; j<23; j++) {
	    if ((j-1)%10) DBGPRINTF(" |");
	    else DBGPRINTF("-+");
	    n=(80*histo[i][j])/totno[i];
	    if (histo[i][j] && n==0) DBGPRINTF(".");
	    for (k=0; k<n; k++) DBGPRINTF("M");
	    DBGPRINTF("\n");
	}}
    DBGPRINTF("Iteration %d\n",Iteration);
}


void pangben(struct angben *ab) {
    DBGPRINTF("Bend between %d / %d: kb=%.2f, th0=%.2f\n\
 --Table[%d]: %.0f by %d:  -->%.2f/%.4f,  -->%.2f/%.4f\n",
	      ab->b1typ,ab->b2typ,ab->kb,ab->theta0,
	      TABLEN,ab->start,ab->scale,
	      ab->tab1->t1[0],ab->tab1->t2[0],
	      ab->tab2->t1[0],ab->tab2->t2[0]);
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
    DBGPRINTF("(%.2f, %.2f, %.2f)",foo.x, foo.y, foo.z);
}
void pvt(struct xyz foo) {
    DBGPRINTF("(%.2f, %.2f, %.2f)\n",foo.x, foo.y, foo.z);
}

void pa(int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) DBGPRINTF("bad atom number %d\n",i);
    else {
	DBGPRINTF("atom %s%d (%d bonds): ", element[atom[i].elt].symbol, i, atom[i].nbonds);
	for (j=0; j<atom[i].nbonds; j++) {
	    b=atom[i].bonds[j];
	    ba=(i==bond[b].an1 ? bond[b].an2 : bond[b].an1);
	    DBGPRINTF("[%d/%d]: %s%d, ", b, bond[b].order,
		      element[atom[ba].elt].symbol, ba);
	}
	v=vlen(vdif(cur[i],old[i]));
	DBGPRINTF("\n   V=%.2f, mV^2=%.6f, pos=", v,1e-4*v*v/atom[i].massacc);
	pv(cur[i]); pvt(old[i]);
	DBGPRINTF("   massacc=%e\n",atom[i].massacc);
    }
}

void checkatom(int i) {
    int j, b, ba;
    double v;
	
    if (i<0 || i>=Nexatom) DBGPRINTF("bad atom number %d\n",i);
    else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
	DBGPRINTF("bad element in atom %d: %d\n", i, atom[i].elt);
    else if (atom[i].nbonds <0 || atom[i].nbonds >NBONDS)
	DBGPRINTF("bad nbonds in atom %d: %d\n", i, atom[i].nbonds);
    else if (atom[i].elt < 0 || atom[i].elt >= NUMELTS)
	DBGPRINTF("bad element in atom %d: %d\n", i, atom[i].elt);
    else for (j=0; j<atom[i].nbonds; j++) {
	b=atom[i].bonds[j];
	if (b < 0 || b >= Nexbon)
	    DBGPRINTF("bad bonds number in atom %d: %d\n", i, b);
	else if (i != bond[b].an1 && i != bond[b].an2) {
	    DBGPRINTF("bond %d of atom %d [%d] doesn't point back\n", j, i, b);
	    exit(0);
	}
    }
}

void pb(int i) {
    double len;
    struct bsdata *bt;
    int index;
	
    if (i<0 || i>=Nexbon) DBGPRINTF("bad bond number %d\n",i);
    else {
	bt = bond[i].type;
	len = vlen(vdif(cur[bond[i].an1],cur[bond[i].an2]));
	DBGPRINTF("bond %d[%d] [%s%d(%d)-%s%d(%d)]: length %.1f\n",
		  i, bond[i].order,
		  element[atom[bond[i].an1].elt].symbol, bond[i].an1, atom[bond[i].an1].elt,
		  element[atom[bond[i].an1].elt].symbol, bond[i].an2, atom[bond[i].an2].elt,
		  len);
	index=(int)((len*len)-bt->start)/bt->scale;
	if (index<0 || index>=TABLEN)
	    DBGPRINTF("r0=%.1f, index=%d of %d, off table\n",  bt->r0, index, TABLEN);
	else DBGPRINTF("r0=%.1f, index=%d of %d, value %f\n", bt->r0, index, TABLEN,
		       bt->table->t1[index] + len*len*bt->table->t2[index]);
    }
}

void pq(int i) {
    struct xyz r1, r2;
    if (i<0 || i>=Nextorq) DBGPRINTF("bad torq number %d\n",i);
    else {
	DBGPRINTF("torq %s%d-%s%d-%s%d, that's %d-%d=%d-%d\n",
		  element[atom[torq[i].a1].elt].symbol, torq[i].a1,
		  element[atom[torq[i].ac].elt].symbol, torq[i].ac,
		  element[atom[torq[i].a2].elt].symbol, torq[i].a2,
		  (torq[i].dir1 ? torq[i].b1->an2 :  torq[i].b1->an1),
		  (torq[i].dir1 ? torq[i].b1->an1 :  torq[i].b1->an2),
		  (torq[i].dir2 ? torq[i].b2->an1 :  torq[i].b2->an2),
		  (torq[i].dir2 ? torq[i].b2->an2 :  torq[i].b2->an1));
		
	r1=vdif(cur[torq[i].a1],cur[torq[i].ac]);
	r2=vdif(cur[torq[i].a2],cur[torq[i].ac]);
	DBGPRINTF("r1= %.1f, r2= %.1f, theta=%.2f (%.0f)\n",
		  vlen(r1), vlen(r2), vang(r1, r2),
		  (180.0/3.1415)*vang(r1, r2));
    }
}

void pvdw(struct vdWbuf *buf, int n) {
    DBGPRINTF("vdW %s%d-%s%d: vanderTable[%d]\n",
	      element[atom[buf->item[n].a1].elt].symbol, buf->item[n].a1,
	      element[atom[buf->item[n].a2].elt].symbol, buf->item[n].a2,
	      buf->item[n].table - vanderTable);
    DBGPRINTF("start; %f, scale %d, b=%f, m=%f\n",
	      sqrt(buf->item[n].table->start), buf->item[n].table->scale,
	      buf->item[n].table->table.t1[0],
	      buf->item[n].table->table.t2[0]);
	
}

void pcon(int i) {
    struct MOT *mot;
    int j;
	
    if (i<0 || i>=Nexcon) {
	DBGPRINTF("Bad constraint number %d\n",i);
	return;
    }
    DBGPRINTF("Constraint %d: ",i);
    if (Constraint[i].type == 0) {
	DBGPRINTF("Space weld\n atoms ");
	for (j=0;j<Constraint[i].natoms;j++)
	    DBGPRINTF("%d ",Constraint[i].atoms[j]);
	DBGPRINTF("\n");
    }
    else if (Constraint[i].type == 1) {
	mot = Constraint[i].motor;
	DBGPRINTF("motor; stall torque %.2e, unloaded speed %.2e\n center ",
		  mot->stall, mot->speed);
	pv(mot->center);
	DBGPRINTF(" axis ");
	pvt(mot->axis);
		
	DBGPRINTF(" rot basis ");
	pv(mot->roty); pv(mot->rotz);
	DBGPRINTF(" angles %.0f, %.0f, %.0f\n",
		  180.0*vang(mot->axis,mot->roty)/Pi,
		  180.0*vang(mot->rotz,mot->roty)/Pi,
		  180.0*vang(mot->axis,mot->rotz)/Pi);
		
	for (j=0;j<Constraint[i].natoms;j++) {
	    DBGPRINTF(" atom %d radius %.1f angle %.2f\n   center ",
		      Constraint[i].atoms[j], mot->radius[j], mot->atang[j]);
	    pv(mot->atocent[j]);
	    DBGPRINTF(" posn "); pvt(mot->ator[j]);
	}
	DBGPRINTF(" Theta=%.2f, theta0=%.2f, moment factor =%e\n",
		  mot->theta, mot->theta0, mot->moment);
    }
}
