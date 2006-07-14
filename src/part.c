/* Copyright (c) 2006 Nanorex, Inc. All rights reserved. */

#include "simulator.h"

#define CHECK_VALID_BOND(b) { \
    NULLPTR(b); NULLPTR((b)->a1); NULLPTR((b)->a2); }

static char const rcsid[] = "$Id$";

// This is the default value for the p->parseError() function.
// p->parseError() is called by routines in this file while a part is
// being constructed.  It generally points to a routine that can emit
// line number and character position information to identify the
// location of the error in the input file.  The stream pointer is
// used to pass that information through to the parser's parseError
// routine.
//
// If the parser does not declare a parseError routine, or after
// endPart() is called to indicate that the parser is no longer
// responsible for errors, this routine will be installed as
// p->parseError().  When that happens, the stream pointer is set to
// the part, allowing us to extract and print the filename where the
// problem was found.
static void
defaultParseError(void *stream)
{
    struct part *p;
    
    p = (struct part *)stream;
    ERROR1("Parsing part %s", p->filename);
    done("Failed to parse part %s", p->filename);
    exit(1); // XXX should throw exception so pyrex doesn't exit cad here
}

// Create a new part.  Pass in a filename (or any other string
// identifying where the data for this part is coming from), and an
// error handler.  The parseError() routine will be called with stream
// as it's only argument if any of the routines in this file detect an
// error before you call endPart().  Pass NULL for both parseError and
// stream to use a default error handler.  The default error handler
// will also be used after a call to endPart() if an error is
// detected.
struct part *
makePart(char *filename, void (*parseError)(void *), void *stream)
{
    struct part *p;
    
    p = (struct part *)allocate(sizeof(struct part));
    memset(p, 0, sizeof(struct part));
    p->max_atom_id = -1;
    p->filename = copy_string(filename);
    p->parseError = parseError ? parseError : &defaultParseError;
    p->stream = parseError ? stream : p;
    return p;
}

void
destroyPart(struct part *p)
{
    int i;
    struct atom *a;
    struct bond *b;
    struct jig *j;
    struct vanDerWaals *v;
    
    if (p == NULL){
        return;
    }
    if (p->filename != NULL) {
        free(p->filename);
        p->filename = NULL;
    }
    // p->stream is handled by caller.  readmmp just keeps the stream
    // in it's stack frame.
    destroyAccumulator(p->atom_id_to_index_plus_one);
    p->atom_id_to_index_plus_one = NULL;
    for (i=0; i<p->num_atoms; i++) {
        a = p->atoms[i];

        //a->type points into periodicTable, don't free
        //a->vdwBucket points into p->vdwHash, allocated as part of part
        //a->prev and next just point to other atoms
        //a->bonds has pointers into the p->bonds array
        free(a->bonds);
        a->bonds = NULL;
        free(a);
    }
    destroyAccumulator(p->atoms);
    p->atoms = NULL;
    destroyAccumulator(p->positions);
    p->positions = NULL;
    destroyAccumulator(p->velocities);
    p->velocities = NULL;

    for (i=0; i<p->num_bonds; i++) {
        b = p->bonds[i];
        // b->a1 and a2 point to already freed atoms
        free(b);
    }
    destroyAccumulator(p->bonds);
    p->bonds = NULL;

    for (i=0; i<p->num_jigs; i++) {
        j = p->jigs[i];
        if (j->name != NULL) {
            free(j->name);
            j->name = NULL;
        }
        free(j->atoms);
        j->atoms = NULL;
        if (j->type == RotaryMotor) {
            if (j->j.rmotor.u != NULL) {
                free(j->j.rmotor.u);
                free(j->j.rmotor.v);
                free(j->j.rmotor.w);
                free(j->j.rmotor.rPrevious);
                j->j.rmotor.u = NULL;
                j->j.rmotor.v = NULL;
                j->j.rmotor.w = NULL;
                j->j.rmotor.rPrevious = NULL;
            }
        }
        free(j);
    }
    destroyAccumulator(p->jigs);
    p->jigs = NULL;

    for (i=0; i<p->num_vanDerWaals; i++) {
        v = p->vanDerWaals[i];
        if (v != NULL) {
            // v->a1 and v->a2 already freed
            // v->parameters still held by vdw hashtable
            free(v);
            p->vanDerWaals[i] = NULL;
        }
    }
    destroyAccumulator(p->vanDerWaals);

    // nothing in a stretch needs freeing
    if (p->stretches != NULL) {
        free(p->stretches);
        p->stretches = NULL;
    }

    // nothing in a bend needs freeing
    if (p->bends != NULL) {
        free(p->bends);
        p->bends = NULL;
    }

    // nothing in a torsion needs freeing
    if (p->torsions != NULL) {
        free(p->torsions);
        p->torsions = NULL;
    }

    // nothing in an outOfPlane needs freeing
    if (p->outOfPlanes != NULL) {
        free(p->outOfPlanes);
        p->outOfPlanes = NULL;
    }
    
    free(p);
}

// Add a bond to the bond list for a single atom.
static void
addBondToAtom(struct part *p, struct bond *b, struct atom *a)
{
    int i;
    
    for (i=0; i<a->num_bonds; i++) {
	if (a->bonds[i] == NULL) {
	    a->bonds[i] = b;
	    return;
	}
    }
    ERROR("Internal error: No slot for bond in atom");
    p->parseError(p->stream);
}

// After creating all of the atoms and bonds, we go back and tell each
// atom which bonds it is a part of.
static void
addBondsToAtoms(struct part *p)
{
    int i;
    struct bond *b;
    struct atom *a;
    
    NULLPTR(p);
    for (i=0; i<p->num_bonds; i++) {
	/*
	 * I've seen a few different bugs with null pointers here. We
	 * should try to get a warning of some kind.
	 */
	b = p->bonds[i];
	CHECK_VALID_BOND(b);
	b->a1->num_bonds++;
	b->a2->num_bonds++;
    }
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
	a->bonds = (struct bond **)allocate(sizeof(struct bond *) * a->num_bonds);
	memset(a->bonds, 0, sizeof(struct bond *) * a->num_bonds);
    }
    for (i=0; i<p->num_bonds; i++) {
	b = p->bonds[i];
	addBondToAtom(p, b, b->a1);
	addBondToAtom(p, b, b->a2);
    }
}

// Called to indicate that a parser has finished reading data for this
// part.  Finalizes the data structures and switches to the default
// error handler.
struct part *
endPart(struct part *p)
{
    int i;
    struct xyz mm1;
    struct xyz totalMomentum;
    struct xyz driftVelocity;
    double totalMass;

    p->parseError = &defaultParseError;
    p->stream = p;
    p->num_vanDerWaals = p->num_static_vanDerWaals;
    
    // XXX realloc any accumulators
    
    addBondsToAtoms(p);

    // force a net momentum of zero
    vsetc(totalMomentum, 0.0);
    totalMass = 0.0;
    for (i=0; i < p->num_atoms; i++) {
	double mass = 1.0 / p->atoms[i]->inverseMass;
	totalMass += mass;
	vmul2c(mm1, p->velocities[i], mass);
	vadd(totalMomentum, mm1);
    }
    vmul2c(driftVelocity, totalMomentum, 1.0 / totalMass);
    for (i=0; i < p->num_atoms; i++) {
	vsub(p->velocities[i], driftVelocity);
    }

    // other routines should:
    // build stretchs, bends, and torsions
    // calculate initial velocities
    
    return p;
}

// Creates a stretch for each bond in the part.
void
generateStretches(struct part *p)
{
    int i;
    
    p->num_stretches = p->num_bonds;
    p->stretches = (struct stretch *)allocate(sizeof(struct stretch) * p->num_stretches);
    for (i=0; i<p->num_bonds; i++) {
	CHECK_VALID_BOND(p->bonds[i]);
	// XXX skip stretch if both ends are grounded
	p->stretches[i].a1 = p->bonds[i]->a1;
	p->stretches[i].a2 = p->bonds[i]->a2;
	p->stretches[i].b = p->bonds[i];
	// XXX really should send struct atomType instead of protons
	p->stretches[i].stretchType = getBondStretch(p->stretches[i].a1->type->protons,
						     p->stretches[i].a2->type->protons,
						     p->bonds[i]->order);
    }
}

// Fill in the bend data structure for a bend centered on the given
// atom.  The two bonds that make up the bend are indexed in the
// center atom's bond array.
static void
makeBend(struct part *p, int bend_number, struct atom *a, int bond1, int bond2)
{
    struct bend *b;
    
    b = &p->bends[bend_number];
    b->ac = a;
    b->b1 = a->bonds[bond1];
    b->b2 = a->bonds[bond2];

    CHECK_VALID_BOND(b->b1);
    if (b->b1->a1 == a) {
	b->a1 = b->b1->a2;
	b->dir1 = 1;
    } else if (b->b1->a2 == a) {
	b->a1 = b->b1->a1;
	b->dir1 = 0;
    } else {
	// print a better error if it ever happens...
	fprintf(stderr, "neither end of bond on center!");
    }
    
    CHECK_VALID_BOND(b->b2);
    if (b->b2->a1 == a) {
	b->a2 = b->b2->a2;
	b->dir2 = 1;
    } else if (b->b2->a2 == a) {
	b->a2 = b->b2->a1;
	b->dir2 = 0;
    } else {
	// print a better error if it ever happens...
	fprintf(stderr, "neither end of bond on center!");
    }
    
    // XXX should just use atomType instead of protons
    b->bendType = getBendData(a->type->protons,
                              a->hybridization,
			      b->a1->type->protons, b->b1->order,
			      b->a2->type->protons, b->b2->order);
}

// Creates a bend for each pair of adjacent bonds in the part.
void
generateBends(struct part *p)
{
    int i;
    int j;
    int k;
    int bend_index = 0;
    struct atom *a;
    
    // first, count the number of bends
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
	for (j=0; j<a->num_bonds; j++) {
	    for (k=j+1; k<a->num_bonds; k++) {
		p->num_bends++;
	    }
	}
    }
    
    p->bends = (struct bend *)allocate(sizeof(struct bend) * p->num_bends);
    
    // now, fill them in (make sure loop structure is same as above)
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
	for (j=0; j<a->num_bonds; j++) {
	    for (k=j+1; k<a->num_bonds; k++) {
		makeBend(p, bend_index++, a, j, k);
	    }
	}
    }
}

static void
makeTorsion(struct part *p, int index, struct bond *center, struct bond *b1, struct bond *b2)
{
    struct torsion *t = &(p->torsions[index]);

    t->aa = center->a1;
    t->ab = center->a2;
    t->a1 = b1->a1 == t->aa ? b1->a2 : b1->a1;
    t->a2 = b2->a1 == t->ab ? b2->a2 : b2->a1;

    // Barrior to rotation of a simple alkene is about 265 kJ/mol, but
    // can be on the order of 50 kJ/mol for "captodative ethylenes",
    // where the charge density on the carbons involved in the double
    // bond has been significantly altered.
    // [[Advanced Organic Chemistry, Jerry March, Fourth Edition,
    // Chapter 4, p.129.]]
    // A is in aJ/rad^2, but rotational barrior is 2A
    // 2.65e5 J/mol == 4.4e-19 J/bond
    // A = 2.2e-19 or 0.22 aJ
    t->A = 0.22; // XXX need to get actual value from real parameters
}

// Creates a torsion for each triplet of adjacent bonds in the part,
// where the center bond is graphitic, aromatic, or double.
void
generateTorsions(struct part *p)
{
    int i;
    int j;
    int k;
    int torsion_index = 0;
    struct bond *b;
    
    // first, count the number of torsions
    for (i=0; i<p->num_bonds; i++) {
	b = p->bonds[i];
        CHECK_VALID_BOND(b);
        switch (b->order) {
        case 'a':
        case 'g':
        case '2':
            for (j=0; j<b->a1->num_bonds; j++) {
                if (b->a1->bonds[j] != b) {
                    for (k=0; k<b->a2->num_bonds; k++) {
                        if (b->a2->bonds[k] != b) {
                            p->num_torsions++;
                        }
                    }
                }
            }
        default:
            break;
        }
        
    }
    
    p->torsions = (struct torsion *)allocate(sizeof(struct torsion) * p->num_torsions);
    
    // now, fill them in (make sure loop structure is same as above)
    for (i=0; i<p->num_bonds; i++) {
	b = p->bonds[i];
        CHECK_VALID_BOND(b);
        switch (b->order) {
        case 'a':
        case 'g':
        case '2':
            for (j=0; j<b->a1->num_bonds; j++) {
                if (b->a1->bonds[j] != b) {
                    for (k=0; k<b->a2->num_bonds; k++) {
                        if (b->a2->bonds[k] != b) {
                            makeTorsion(p, torsion_index++, b, b->a1->bonds[j], b->a2->bonds[k]);
                        }
                    }
                }
            }
        default:
            break;
        }
        
    }
}

static void
makeOutOfPlane(struct part *p, int index, struct atom *a)
{
    struct outOfPlane *o = &(p->outOfPlanes[index]);
    struct bond *b;
    
    o->ac = a;
    b = a->bonds[0];
    o->a1 = b->a1 == a ? b->a2 : b->a1;
    b = a->bonds[1];
    o->a2 = b->a1 == a ? b->a2 : b->a1;
    b = a->bonds[2];
    o->a3 = b->a1 == a ? b->a2 : b->a1;

    // A is in aJ/pm^2
    o->A = 0.00025380636; // This is for carbon in graphene with deflection less than 0.5 pm.
    //o->A = 0.0005; // XXX need to get actual value from real parameters
}

// Creates an outOfPlane for each sp2 atom
void
generateOutOfPlanes(struct part *p)
{
    int i;
    int outOfPlane_index = 0;
    struct atom *a;
    
    // first, count the number of outOfPlanes
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
        switch (a->hybridization) {
        case sp2:
        case sp2_g:
            if (a->num_bonds == 3) {
                p->num_outOfPlanes++;
            }
        default:
            break;
        }
        
    }
    
    p->outOfPlanes = (struct outOfPlane *)allocate(sizeof(struct outOfPlane) * p->num_outOfPlanes);
    
    // now, fill them in (make sure loop structure is same as above)
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
        switch (a->hybridization) {
        case sp2:
        case sp2_g:
            if (a->num_bonds == 3) {
                makeOutOfPlane(p, outOfPlane_index++, a);
            } // else WARNING ???
        default:
            break;
        }
        
    }
}


// Scan the dynamic van der Waals list and mark as invalid any
// interaction involving atom a.
static void
invalidateVanDerWaals(struct part *p, struct atom *a)
{
    int i;
    struct vanDerWaals *vdw;
    
    for (i=p->num_static_vanDerWaals; i<p->num_vanDerWaals; i++) {
	vdw = p->vanDerWaals[i];
	if (vdw && (vdw->a1 == a || vdw->a2 == a)) {
	    p->vanDerWaals[i] = NULL;
	    free(vdw);
	    if (i < p->start_vanDerWaals_free_scan) {
		p->start_vanDerWaals_free_scan = i;
	    }
	}
    }
}

// Find a free slot in the dynamic van der Waals list (either one
// marked invalid above, or a new one appended to the list).  Fill it
// with a new, valid, interaction.
static void
makeDynamicVanDerWaals(struct part *p, struct atom *a1, struct atom *a2)
{
    int i;
    struct vanDerWaals *vdw = NULL;
    
    vdw = (struct vanDerWaals *)allocate(sizeof(struct vanDerWaals));
    
    for (i=p->start_vanDerWaals_free_scan; i<p->num_vanDerWaals; i++) {
	if (!(p->vanDerWaals[i])) {
	    p->vanDerWaals[i] = vdw;
	    p->start_vanDerWaals_free_scan = i + 1;
	    break;
	}
    }
    if (i >= p->num_vanDerWaals) {
	p->num_vanDerWaals++;
	p->vanDerWaals = (struct vanDerWaals **)
	    accumulator(p->vanDerWaals,
			sizeof(struct vanDerWaals *) * p->num_vanDerWaals, 0);
	p->vanDerWaals[p->num_vanDerWaals - 1] = vdw;
	p->start_vanDerWaals_free_scan = p->num_vanDerWaals;
    }
    vdw->a1 = a1;
    vdw->a2 = a2;
    vdw->parameters = getVanDerWaalsTable(a1->type->protons, a2->type->protons);
}

// Are a1 and a2 both bonded to the same atom (or to each other)?
static int
isBondedToSame(struct atom *a1, struct atom *a2)
{
    int i;
    int j;
    struct bond *b1;
    struct bond *b2;
    struct atom *ac;
    
    if (a1 == a2) {
        return 1;
    }
    for (i=0; i<a1->num_bonds; i++) {
	b1 = a1->bonds[i];
	ac = (b1->a1 == a1) ? b1->a2 : b1->a1;
	if (ac == a2) {
	    // bonded to each other
	    return 1;
	}
	for (j=0; j<a2->num_bonds; j++) {
	    b2 = a2->bonds[j];
	    if (ac == ((b2->a1 == a2) ? b2->a2 : b2->a1)) {
		// both bonded to common atom ac
		return 1;
	    }
	}
    }
    return 0;
}

static void
verifyVanDerWaals(struct part *p, struct xyz *positions)
{
    int *seen;
    int i;
    int j;
    int k;
    struct atom *a1, *a2;
    double r1, r2;
    int i1, i2;
    struct xyz p1, p2;
    struct vanDerWaals *vdw;
    double rvdw;
    double distance;
    int found;
    int actual_count;
    int notseen_count;
    
    seen = (int *)allocate(sizeof(int) * p->num_vanDerWaals);
    // wware 060109  python exception handling
    NULLPTR(seen);
    for (i=0; i<p->num_vanDerWaals; i++) {
	seen[i] = 0;
    }
    
    for (j=0; j<p->num_atoms; j++) {
	a1 = p->atoms[j];
	i1 = a1->index;
	r1 = a1->type->vanDerWaalsRadius; // angstroms
	p1 = positions[i1];
	for (k=j+1; k<p->num_atoms; k++) {
	    a2 = p->atoms[k];
	    if (!isBondedToSame(a1, a2)) {
		i2 = a2->index;
		r2 = a2->type->vanDerWaalsRadius; // angstroms
		p2 = positions[i2];
		rvdw = (r1 + r2) * 100.0; // picometers
		distance = vlen(vdif(p1, p2));
		if (distance < rvdw * 1.5) {
		    found = 0;
		    for (i=0; i<p->num_vanDerWaals; i++) {
			vdw = p->vanDerWaals[i];
			if (vdw != NULL) {
			    CHECK_VALID_BOND(vdw);
			    if (vdw->a1 == a1 && vdw->a2 == a2) {
				seen[i] = 1;
				found = 1;
				break;
			    }
			}
		    }
		    if (!found) {
			fprintf(stderr, "missing vdw: a1:");
			printAtomShort(stderr, a1);
			fprintf(stderr, " a2:");
			printAtomShort(stderr, a2);
			fprintf(stderr, " distance: %f rvdw: %f\n", distance, rvdw);
		    }
		}
	    }
	}
    }
    actual_count = 0;
    notseen_count = 0;
    for (i=0; i<p->num_vanDerWaals; i++) {
	vdw = p->vanDerWaals[i];
	if (vdw != NULL) {
	    actual_count++;
	    if (!seen[i]) {
		notseen_count++;
		CHECK_VALID_BOND(vdw);
		p1 = positions[vdw->a1->index];
		p2 = positions[vdw->a2->index];
		distance = vlen(vdif(p1, p2));
		r1 = vdw->a1->type->vanDerWaalsRadius; // angstroms
		r2 = vdw->a2->type->vanDerWaalsRadius; // angstroms
		rvdw = (r1 + r2) * 100.0; // picometers
		if (distance < rvdw * 1.5) {
		    fprintf(stderr, "should have found this one above!!!\n");
		}
		if (distance > rvdw * 1.5 + 866.0) {
		    fprintf(stderr, "unnecessary vdw: a1:");
		    printAtomShort(stderr, vdw->a1);
		    fprintf(stderr, " a2:");
		    printAtomShort(stderr, vdw->a2);
		    fprintf(stderr, " distance: %f rvdw: %f\n", distance, rvdw);
		}
	    }
	}
    }
    //fprintf(stderr, "num_vdw: %d actual_count: %d not_seen: %d\n", p->num_vanDerWaals, actual_count, notseen_count);
    free(seen); // yes, alloca would work here too.
}

// XXX watch for atom vibrating between buckets

// Update the dynamic van der Waals list for this part.  Validity is a
// tag to prevent rescanning the same configuration a second time.
void
updateVanDerWaals(struct part *p, void *validity, struct xyz *positions)
{
    int i;
    int x;
    int y;
    int z;
    int ax;
    int ay;
    int az;
    struct atom *a;
    struct atom *a2;
    struct atom **bucket;
    double r;

    // wware 060109  python exception handling
    NULLPTR(p);
    NULLPTR(positions);
    if (validity && p->vanDerWaals_validity == validity) {
	return;
    }
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
	ax = (int)positions[i].x / 250;
	ay = (int)positions[i].y / 250;
	az = (int)positions[i].z / 250;
	bucket = &(p->vdwHash[ax&VDW_HASH][ay&VDW_HASH][az&VDW_HASH]);
	if (a->vdwBucket != bucket) {
	    invalidateVanDerWaals(p, a);
	    // remove a from it's old bucket chain
	    if (a->vdwNext) {
		a->vdwNext->vdwPrev = a->vdwPrev;
	    }
	    if (a->vdwPrev) {
		a->vdwPrev->vdwNext = a->vdwNext;
	    } else if (a->vdwBucket) {
		*(a->vdwBucket) = a->vdwNext;
	    }
	    // and add it to the new one
	    a->vdwBucket = bucket;
	    a->vdwNext = *bucket;
	    a->vdwPrev = NULL;
	    *bucket = a;
	    if (a->vdwNext) {
		a->vdwNext->vdwPrev = a;
	    }
	    for (x=ax-3; x<=ax+3; x++) {
		for (y=ay-3; y<=ay+3; y++) {
		    for (z=az-3; z<=az+3; z++) {
			a2 = p->vdwHash[x&VDW_HASH][y&VDW_HASH][z&VDW_HASH];
			while (a2 != NULL) {
			    if (!isBondedToSame(a, a2)) {
				r = vlen(vdif(positions[i], positions[a2->index]));
				if (r<800.0) {
				    if (i < a2->index) {
					// wware 060109  python exception handling
					makeDynamicVanDerWaals(p, a, a2); BAIL();
				    } else {
					// wware 060109  python exception handling
					makeDynamicVanDerWaals(p, a2, a); BAIL();
				    }
				}
			    }
			    a2 = a2->vdwNext;
			}
		    }
		}
	    }
	}
    }
    p->vanDerWaals_validity = validity;
    if (DEBUG(D_VERIFY_VDW)) { // -D13
	// wware 060109  python exception handling
	verifyVanDerWaals(p, positions); BAIL();
    }
}

// All of space is divided into a cubic grid with each cube being
// GRID_SPACING pm on a side.  Every GRID_OCCUPANCY cubes in each
// direction there is a bucket.  Every GRID_SIZE buckets the grid
// wraps back on itself, so that each bucket stores atoms that are in
// an infinite number of grid cubes, where the cubes are some multiple
// of GRID_SPACING * GRID_OCCUPANCY * GRID_SIZE pm apart.  GRID_SIZE
// must be a power of two, so the index along a particular dimension
// of the bucket array where a particular coordinates is found is
// calculated with: (int(x) * GRID_OCCUPANCY) & (GRID_SIZE-1).
//
// Buckets can overlap.  When deciding if an atom is still in the same
// bucket, a fuzzy match is used, masking off one or more low order
// bits of the bucket array index.  When an atom leaves a bucket
// according to the fuzzy matching, it is placed in a new bucket based
// on the non-fuzzy index into the bucket array.  In this way, an atom
// vibrating less than the bucket overlap distance will remain in the
// same bucket irrespective of it's position with respect to the grid
// while it is vibrating.
//
// The fuzzy match looks like this: moved = (current - previous) *
// GRID_MASK.  GRID_MASK is (GRID_SIZE-1) with one or more low order
// bits zeroed.  It works correctly if the subtraction is done two's
// complement, it may not for one's complement subtraction.  With no
// bits zeroed, there is no overlap.  With one zero, the buckets
// overlap by 50%.  Two zeros = 3/4 overlap.  Three zeros = 7/8
// overlap.  The above are if GRID_OCCUPANCY == 1.  Larger values for
// GRID_OCCUPANCY allow overlaps between zero and 50%.

// Returns an entry in the p->atoms array, given an external atom id
// (as used in an mmp file, for example).
static struct atom *
translateAtomID(struct part *p, int atomID)
{
    int atomIndex;
    
    if (atomID < 0 || atomID > p->max_atom_id) {
	ERROR2("atom ID %d out of range [0, %d]", atomID, p->max_atom_id);
	p->parseError(p->stream);
    }
    atomIndex = p->atom_id_to_index_plus_one[atomID] - 1;
    if (atomIndex < 0) {
	ERROR1("atom ID %d not yet encountered", atomID);
	p->parseError(p->stream);
    }
    return p->atoms[atomIndex];
}

// gavss() and gxyz() are also used by the thermostat jig...

static double
part_gavss(double v)
{
    double v0,v1, rSquared;
    
    do {
	// generate random numbers in the range [-1.0 .. 1.0]
	v0=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	v1=(float)rand()/(float)(RAND_MAX/2) - 1.0;
	rSquared = v0*v0 + v1*v1;
    } while (rSquared>=1.0 || rSquared==0.0);
    // v0 and v1 are uniformly distributed within a unit circle
    // (excluding the origin)
    return v*v0*sqrt(-2.0*log(rSquared)/rSquared);
}

static struct xyz
part_gxyz(double v)
{
    struct xyz g;
    
    g.x=part_gavss(v);
    g.y=part_gavss(v);
    g.z=part_gavss(v);
    return g;
}

// Add an atom to the part.  ExternalID is the atom number as it
// appears in (for example) an mmp file.  ElementType is the number of
// protons (XXX should really be an atomType).
void
makeAtom(struct part *p, int externalID, int elementType, struct xyz position)
{
    double mass;
    double therm;
    struct atom *a;
    struct xyz velocity;
    struct xyz moment;
    struct xyz momentum;
    
    if (externalID < 0) {
	ERROR1("atom ID %d must be >= 0", externalID);
	p->parseError(p->stream);
    }
    if (externalID > p->max_atom_id) {
	p->max_atom_id = externalID;
	p->atom_id_to_index_plus_one = (int *)accumulator(p->atom_id_to_index_plus_one,
							  sizeof(int) * (p->max_atom_id + 1), 1);
    }
    if (p->atom_id_to_index_plus_one[externalID]) {
	ERROR2("atom ID %d already defined with index %d", externalID, p->atom_id_to_index_plus_one[externalID] - 1);
	p->parseError(p->stream);
    }
    p->atom_id_to_index_plus_one[externalID] = ++(p->num_atoms);
    
    p->atoms = (struct atom **)accumulator(p->atoms, sizeof(struct atom *) * p->num_atoms, 0);
    p->positions = (struct xyz *)accumulator(p->positions, sizeof(struct xyz) * p->num_atoms, 0);
    p->velocities = (struct xyz *)accumulator(p->velocities, sizeof(struct xyz) * p->num_atoms, 0);
    
    a = (struct atom *)allocate(sizeof(struct atom));
    p->atoms[p->num_atoms - 1] = a;
    a->index = p->num_atoms - 1;
    a->atomID = externalID;
    
    vset(p->positions[a->index], position);
    
    if (elementType < 0 || elementType > MAX_ELEMENT) {
	ERROR1("Invalid element type: %d", elementType);
	p->parseError(p->stream);
    }
    a->type = &periodicTable[elementType];
    if (a->type->name == NULL) {
	ERROR1("Unsupported element type: %d", elementType);
	p->parseError(p->stream);
    }
    
    a->isGrounded = 0;
    a->num_bonds = 0;
    a->bonds = NULL;
    a->vdwBucket = NULL;
    a->vdwPrev = NULL;
    a->vdwNext = NULL;
    if (a->type->group == 3) {
        a->hybridization = sp2;
    } else {
        a->hybridization = sp3;
    }
    
    mass = a->type->mass * 1e-27;
    a->inverseMass = Dt * Dt / mass;
    
    // XXX break this out into another routine
    therm = sqrt(2.0 * (Boltz * Temperature) / mass) * Dt / Dx;
    velocity = part_gxyz(therm);
    vset(p->velocities[a->index], velocity);
    
    // we should probably have a separate routine that calculates this
    // based on velocities
    p->totalKineticEnergy += Boltz*Temperature*1.5;
    
    p->totalMass += mass;
    
    vmul2c(moment, position, mass);
    vadd(p->centerOfGravity, moment);
    
    vmul2c(momentum, velocity, mass);
    vadd(p->totalMomentum, momentum);
}

void
setAtomHybridization(struct part *p, int atomID, enum hybridization h)
{
    struct atom *a;
    
    if (atomID < 0 || atomID > p->max_atom_id || p->atom_id_to_index_plus_one[atomID] < 1) {
	ERROR1("setAtomHybridization: atom ID %d not seen yet", atomID);
	p->parseError(p->stream);
    }
    a = p->atoms[p->atom_id_to_index_plus_one[atomID] - 1];
    a->hybridization = h;
}

// Add a new bond to this part.  The atomID's are the external atom
// numbers as found in an mmp file (for example).
void
makeBond(struct part *p, int atomID1, int atomID2, char order)
{
    struct bond *b;
    
    /*********************************************************************/
    // patch to pretend that carbomeric bonds are the same as double bonds
    if (order == 'c') {
	order = '2';
    }
    /*********************************************************************/
    
    p->num_bonds++;
    p->bonds = (struct bond **)accumulator(p->bonds, sizeof(struct bond *) * p->num_bonds, 0);
    b = (struct bond *)allocate(sizeof(struct bond));
    p->bonds[p->num_bonds - 1] = b;
    b->a1 = translateAtomID(p, atomID1);
    b->a2 = translateAtomID(p, atomID2);
    CHECK_VALID_BOND(b);
    // XXX should we reject unknown bond orders here?
    b->order = order;
    b->valid = -1;
}

// Add a static van der Waals interaction between a pair of bonded
// atoms.  Not needed unless you want the vDW on directly bonded
// atoms, as all other vDW interactions will be automatically found.
void
makeVanDerWaals(struct part *p, int atomID1, int atomID2)
{
    struct vanDerWaals *v;
    
    p->num_static_vanDerWaals++;
    p->vanDerWaals = (struct vanDerWaals **)accumulator(p->vanDerWaals, sizeof(struct vanDerWaals *) * p->num_static_vanDerWaals, 0);
    v = (struct vanDerWaals *)allocate(sizeof(struct vanDerWaals));
    p->vanDerWaals[p->num_static_vanDerWaals - 1] = v;
    v->a1 = translateAtomID(p, atomID1);
    v->a2 = translateAtomID(p, atomID2);
    CHECK_VALID_BOND(v);
    v->parameters = getVanDerWaalsTable(v->a1->type->protons, v->a2->type->protons);
}

// Compute Sum(1/2*m*v**2) over all the atoms. This is valid ONLY if
// part->velocities has been updated in dynamicsMovie().
double
calculateKinetic(struct part *p)
{
    struct xyz *velocities = p->velocities;
    double total = 0.0;
    int j;
    for (j=0; j<p->num_atoms; j++) {
	struct atom *a = p->atoms[j];
	double v = vlen(velocities[a->index]);
	// save the factor of 1/2 for later, to keep this loop fast
	total += a->type->mass * v * v;
    }
    // We want energy in attojoules to be consistent with potential energy
    // mass is in units of Dmass kilograms
    // velocity is in picometers per Dt seconds
    // total is in units of 1e-24*(Dmass/Dt^2) joules
    // we want attojoules or 1e-18 joules, so we need to multiply by 1e6*Dt^2/Dmass
    // and we need the factor of 1/2 that we left out of the atom loop
    return 5e5 * (Dt * Dt / Dmass) * total;
}


static struct jig *
newJig(struct part *p)
{
    struct jig *j;
    
    p->num_jigs++;
    p->jigs = (struct jig **)accumulator(p->jigs, sizeof(struct jig *) * p->num_jigs, 0);
    j = (struct jig *)allocate(sizeof(struct jig));
    p->jigs[p->num_jigs - 1] = j;

    j->name = NULL;
    j->num_atoms = 0;
    j->atoms = NULL;
    j->degreesOfFreedom = 0;
    j->coordinateIndex = 0;
    j->data = 0.0;
    j->data2 = 0.0;
    j->xdata.x = 0.0;
    j->xdata.y = 0.0;
    j->xdata.z = 0.0;
    
    return j;
}

// Turn an atomID list into an array of struct atom's inside a jig.
static void
jigAtomList(struct part *p, struct jig *j, int atomListLength, int *atomList)
{
    int i;
    
    j->atoms = (struct atom **)allocate(sizeof(struct atom *) * atomListLength);
    j->num_atoms = atomListLength;
    for (i=0; i<atomListLength; i++) {
	j->atoms[i] = translateAtomID(p, atomList[i]);
    }
}

// Turn a pair of atomID's into an array of struct atom's inside a
// jig.  All atoms between the given ID's (inclusive) are included in
// the jig.
static void
jigAtomRange(struct part *p, struct jig *j, int firstID, int lastID)
{
    int len = lastID < firstID ? 0 : 1 + lastID - firstID;
    int id;
    int i;
    
    j->atoms = (struct atom **)allocate(sizeof(struct atom *) * len);
    j->num_atoms = len;
    for (i=0, id=firstID; id<=lastID; i++, id++) {
	j->atoms[i] = translateAtomID(p, id);
    }
}

// Create a ground jig in this part, given the jig name, and the list
// of atoms in the jig.  Atoms in the ground jig will not move.
void
makeGround(struct part *p, char *name, int atomListLength, int *atomList)
{
    int i;
    struct jig *j = newJig(p);
    
    j->type = Ground;
    j->name = name;
    jigAtomList(p, j, atomListLength, atomList);
    for (i=0; i<atomListLength; i++) {
	j->atoms[i]->isGrounded = 1;
    }
}


// Create a thermometer jig in this part, given the jig name, and the
// range of atoms to include in the jig.  The Temperature of the atoms
// in the jig will be reported in the trace file.
void
makeThermometer(struct part *p, char *name, int firstAtomID, int lastAtomID)
{
    struct jig *j = newJig(p);
    
    j->type = Thermometer;
    j->name = name;
    jigAtomRange(p, j, firstAtomID, lastAtomID);
}

// Create an dihedral meter jig in this part, given the jig name, and the
// three atoms to measure.  The dihedral angle between the atoms will be
// reported in the trace file.
void
makeDihedralMeter(struct part *p, char *name, int atomID1, int atomID2, int atomID3, int atomID4)
{
    struct jig *j = newJig(p);
    
    j->type = DihedralMeter;
    j->name = name;
    j->atoms = (struct atom **)allocate(sizeof(struct atom *) * 4);
    j->num_atoms = 4;
    j->atoms[0] = translateAtomID(p, atomID1);
    j->atoms[1] = translateAtomID(p, atomID2);
    j->atoms[2] = translateAtomID(p, atomID3);
    j->atoms[3] = translateAtomID(p, atomID4);
}

// Create an angle meter jig in this part, given the jig name, and the
// three atoms to measure.  The angle between the atoms will be
// reported in the trace file.
void
makeAngleMeter(struct part *p, char *name, int atomID1, int atomID2, int atomID3)
{
    struct jig *j = newJig(p);
    
    j->type = AngleMeter;
    j->name = name;
    j->atoms = (struct atom **)allocate(sizeof(struct atom *) * 3);
    j->num_atoms = 3;
    j->atoms[0] = translateAtomID(p, atomID1);
    j->atoms[1] = translateAtomID(p, atomID2);
    j->atoms[2] = translateAtomID(p, atomID3);
}

// Create a radius jig in this part, given the jig name, and the two
// atoms to measure.  The disance between the atoms will be reported
// in the trace file.
void
makeRadiusMeter(struct part *p, char *name, int atomID1, int atomID2)
{
    struct jig *j = newJig(p);
    
    j->type = RadiusMeter;
    j->name = name;
    j->atoms = (struct atom **)allocate(sizeof(struct atom *) * 2);
    j->num_atoms = 2;
    j->atoms[0] = translateAtomID(p, atomID1);
    j->atoms[1] = translateAtomID(p, atomID2);
}

// Create a thermostat jig in this part, given the name of the jig,
// the set point temperature, and the range of atoms to include.
// Kinetic energy will be added or removed from the given range of
// atoms to maintain the given temperature.
void
makeThermostat(struct part *p, char *name, double temperature, int firstAtomID, int lastAtomID)
{
    struct jig *j = newJig(p);
    
    j->type = Thermostat;
    j->name = name;
    j->j.thermostat.temperature = temperature;
    jigAtomRange(p, j, firstAtomID, lastAtomID);
}

// Empirically it looks like you don't want to go with a smaller
// flywheel than this.
#define MIN_MOMENT  5.0e-20

// Create a rotary motor jig in this part, given the name of the jig,
// parameters controlling the motor, and the list of atoms to include.
// The motor rotates around the center point, with the plane of
// rotation perpendicular to the direction of the axis vector.
//
// (XXX need good description of behavior of stall and speed)
// stall torque is in nN-nm
// speed is in GHz
struct jig *
makeRotaryMotor(struct part *p, char *name,
                double stall, double speed,
                struct xyz *center, struct xyz *axis,
                int atomListLength, int *atomList)
{
    int i, k;
    double mass;
    struct jig *j = newJig(p);
    
    j->type = RotaryMotor;
    j->name = name;
    j->degreesOfFreedom = 1; // the angle the motor has rotated by in radians

    // Example uses 1 nN-nm -> 1e6 pN-pm
    // Example uses 2 GHz -> 12.5664e9 radians/second

    // convert nN-nm to pN-pm (multiply by 1e6)
    // torque's sign is meaningless, force it positive
    j->j.rmotor.stall = fabs(stall) * (1e-9/Dx) * (1e-9/Dx);

    // this will do until we get a separate number in the mmp record
    // minimizeTorque is in aN m (1e-18 N m, or 1e-9 N 1e-9 m, or nN nm)
    j->j.rmotor.minimizeTorque = fabs(stall);
    
    // convert from gigahertz to radians per second
    j->j.rmotor.speed = speed * 2.0e9 * Pi;
    // critical damping gets us up to speed as quickly as possible
    // http://hyperphysics.phy-astr.gsu.edu/hbase/oscda2.html
    j->j.rmotor.dampingCoefficient = 0.7071;
    j->j.rmotor.damping_enabled = 1;
    j->j.rmotor.center = *center;
    j->j.rmotor.axis = uvec(*axis);
    // axis now has a length of one
    jigAtomList(p, j, atomListLength, atomList);
    
    j->j.rmotor.u = (struct xyz *)allocate(sizeof(struct xyz) * atomListLength);
    j->j.rmotor.v = (struct xyz *)allocate(sizeof(struct xyz) * atomListLength);
    j->j.rmotor.w = (struct xyz *)allocate(sizeof(struct xyz) * atomListLength);
    j->j.rmotor.rPrevious = (struct xyz *)allocate(sizeof(struct xyz) * atomListLength);
    j->j.rmotor.momentOfInertia = 0.0;
    for (i = 0; i < j->num_atoms; i++) {
	struct xyz r, v;
	double lenv;
	k = j->atoms[i]->index;
	/* for each atom connected to the motor */
	mass = j->atoms[i]->type->mass * 1e-27;
	
	/* u, v, and w can be used to compute the new anchor position from
	 * theta. The new position is u + v cos(theta) + w sin(theta). u is
	 * parallel to the motor axis, v and w are perpendicular to the axis
	 * and perpendicular to each other and the same length.
	 */
	r = vdif(p->positions[k], j->j.rmotor.center);
	vmul2c(j->j.rmotor.u[i], j->j.rmotor.axis, vdot(r, j->j.rmotor.axis));
	v = r;
	vsub(v, j->j.rmotor.u[i]);
	lenv = vlen(v);
	j->j.rmotor.v[i] = v;
	j->j.rmotor.w[i] = vx(j->j.rmotor.axis, v);
	j->j.rmotor.momentOfInertia += mass * lenv * lenv;
	vsetc(j->j.rmotor.rPrevious[i], 0.0);
    }
    
    // Add a flywheel with many times the moment of inertia of the atoms
    j->j.rmotor.momentOfInertia *= 11.0;
    if (j->j.rmotor.momentOfInertia < MIN_MOMENT)
	j->j.rmotor.momentOfInertia = MIN_MOMENT;
    j->j.rmotor.theta = 0.0;
    j->j.rmotor.omega = 0.0;
    return j;
}

// set initial speed of rotary motor
// initialSpeed in GHz
// rmotor.omega in radians per second
void
setInitialSpeed(struct jig *j, double initialSpeed)
{
    j->j.rmotor.omega = initialSpeed * 2.0e9 * Pi;
    // maybe also set minimizeTorque
}

void
setDampingCoefficient(struct jig *j, double dampingCoefficient)
{
    j->j.rmotor.dampingCoefficient = dampingCoefficient;
}

void
setDampingEnabled(struct jig *j, int dampingEnabled)
{
    j->j.rmotor.damping_enabled = dampingEnabled;
}

// Create a linear motor jig in this part, given the name of the jig,
// parameters controlling the motor, and the list of atoms to include.
// Atoms in the jig are constrained to move in the direction given by
// the axis vector.  A constant force can be applied, or they can be
// connected to a spring of the given stiffness.
//
// Jig output is the change in the averge of the positions of all of
// the atoms in the motor from the input positions.
//
// When stiffness is zero, force is uniformly divided among the atoms.
//
// When stiffness is non-zero, it represents a spring connecting the
// center of the atoms to a point along the motor axis from that
// point.  The force parameter is used to determine where the spring
// is attached.  The spring attachment point is such that the initial
// force on the motor is the force parameter.  The force from the
// spring is always evenly divided among the atoms.
void
makeLinearMotor(struct part *p, char *name,
                double force, double stiffness,
                struct xyz *center, struct xyz *axis,
                int atomListLength, int *atomList)
{
    int i;
    double x;
    struct xyz centerOfAtoms;
    struct jig *j = newJig(p);
    
    j->type = LinearMotor;
    j->name = name;
    // linear motor is not a distinct object which can move on its
    // own, it's just a function of the average location of its atoms,
    // so it has no independant degrees of freedom.
    //j->degreesOfFreedom = 1; // distance motor has moved in pm.
    
    j->j.lmotor.force = force; // in pN
    j->j.lmotor.stiffness = stiffness; // in N/m
    j->j.lmotor.axis = uvec(*axis);
    jigAtomList(p, j, atomListLength, atomList);
    
    centerOfAtoms = vcon(0.0);
    for (i=0; i<atomListLength; i++) {
	centerOfAtoms = vsum(centerOfAtoms, p->positions[j->atoms[i]->index]);
    }
    centerOfAtoms = vprodc(centerOfAtoms, 1.0 / atomListLength);
    
    // x is length of projection of centerOfAtoms onto axis (from
    // origin, not center)
    x = vdot(centerOfAtoms, j->j.lmotor.axis);
    j->j.lmotor.motorPosition = x;
    
    if (stiffness == 0.0) {
	j->j.lmotor.zeroPosition = x;
	j->j.lmotor.constantForce = vprodc(j->j.lmotor.axis, force / atomListLength);
    } else {
	j->j.lmotor.zeroPosition = x + force / stiffness ;
        vsetc(j->j.lmotor.constantForce, 0.0);
    }
}

void
printXYZ(FILE *f, struct xyz p)
{
    fprintf(f, "(%f, %f, %f)", p.x, p.y, p.z);
}

void
printAtomShort(FILE *f, struct atom *a)
{
    fprintf(f, "%s(%d)", a->type->symbol, a->atomID);
}

char
printableBondOrder(struct bond *b)
{
    switch (b->order) {
    case '1':
	return '-' ;
	break;
    case '2':
	return '=' ;
	break;
    case '3':
	return '+' ;
	break;
    case 'a':
	return '@' ;
	break;
    case 'g':
	return '#' ;
	break;
    case 'c':
	return '~' ;
	break;
    default:
	return b->order;
	break;
    }
}

char *
hybridizationString(enum hybridization h)
{
    switch (h) {
    case sp:
        return "sp";
    case sp2:
        return "sp2";
    case sp2_g:
        return "sp2_g";
    case sp3:
        return "sp3";
    case sp3d:
        return "sp3d";
    default:
        return "???";
    }
}

void
printAtom(FILE *f, struct part *p, struct atom *a)
{
    int i;
    struct bond *b;
    
    fprintf(f, " atom ");
    printAtomShort(f, a);
    fprintf(f, ".%s ", hybridizationString(a->hybridization));
    printXYZ(f, p->positions[a->index]);
    for (i=0; i<a->num_bonds; i++) {
	fprintf(f, " ");
	b = a->bonds[i];
	fprintf(f, "%c", printableBondOrder(b));
	CHECK_VALID_BOND(b);
	if (b->a1 == a) {
	    printAtomShort(f, b->a2);
	} else if (b->a2 == a) {
	    printAtomShort(f, b->a1);
	} else {
	    fprintf(f, "!!! improper bond on atom: ");
	    printAtomShort(f, b->a1);
	    printAtomShort(f, b->a2);
	}
    }
    fprintf(f, "\n");
}

void
printBond(FILE *f, struct part *p, struct bond *b)
{
    fprintf(f, " bond ");
    CHECK_VALID_BOND(b);
    printAtomShort(f, b->a1);
    fprintf(f, "%c", printableBondOrder(b));
    printAtomShort(f, b->a2);
    fprintf(f, "\n");
}

char *
printableJigType(struct jig *j)
{
    switch (j->type) {
    case Ground:        return "Ground";
    case Thermometer:   return "Thermometer";
    case DihedralMeter: return "DihedralMeter";
    case AngleMeter:    return "AngleMeter";
    case RadiusMeter:   return "RadiusMeter";
    case Thermostat:    return "Thermostat";
    case RotaryMotor:   return "RotaryMotor";
    case LinearMotor:   return "LinearMotor";
    default:            return "unknown";
    }
}

void
printJig(FILE *f, struct part *p, struct jig *j)
{
    int i;
    
    fprintf(f, " %s jig (%s)", printableJigType(j), j->name);
    for (i=0; i<j->num_atoms; i++) {
	fprintf(f, " ");
	printAtomShort(f, j->atoms[i]);
    }
    fprintf(f, "\n");
    switch (j->type) {
    case Thermostat:
	fprintf(f, "  temperature: %f\n", j->j.thermostat.temperature);
	break;
    case RotaryMotor:
	fprintf(f, "  stall torque: %13.10e pN-pm\n", j->j.rmotor.stall);
	fprintf(f, "  top speed: %13.10e radians per second\n", j->j.rmotor.speed);
	fprintf(f, "  current speed: %13.10e radians per second\n", j->j.rmotor.omega);
	fprintf(f, "  minimize torque: %13.10e pN-pm\n", j->j.rmotor.minimizeTorque * 1e6);
	fprintf(f, "  damping: %13.10e\n", j->j.rmotor.damping_enabled ? j->j.rmotor.dampingCoefficient : 0.0);
	fprintf(f, "  center: ");
	printXYZ(f, j->j.rmotor.center);
	fprintf(f, "\n");
	fprintf(f, "  axis: ");
	printXYZ(f, j->j.rmotor.axis);
	fprintf(f, "\n");
	break;
    case LinearMotor:
	fprintf(f, "  force: %f\n", j->j.lmotor.force);
	fprintf(f, "  stiffness: %f\n", j->j.lmotor.stiffness);
	fprintf(f, "  constantForce: ");
	printXYZ(f, j->j.lmotor.constantForce);
	fprintf(f, "\n");
	fprintf(f, "  axis: ");
	printXYZ(f, j->j.lmotor.axis);
	fprintf(f, "\n");
	break;
    default:
	break;
    }
}

void
printVanDerWaals(FILE *f, struct part *p, struct vanDerWaals *v)
{
    double len;
    double potential;
    double gradient;
    struct xyz p1;
    struct xyz p2;
    
    if (v != NULL) {
	fprintf(f, " vanDerWaals ");
	CHECK_VALID_BOND(v);
	printAtomShort(f, v->a1);
	fprintf(f, " ");
	printAtomShort(f, v->a2);
	
	p1 = p->positions[v->a1->index];
	p2 = p->positions[v->a2->index];
	vsub(p1, p2);
	len = vlen(p1);
	
	
	potential = vanDerWaalsPotential(NULL, NULL, v->parameters, len);
	gradient = vanDerWaalsGradient(NULL, NULL, v->parameters, len);
	fprintf(f, " r: %f r0: %f, V: %f, dV: %f\n", len, v->parameters->rvdW, potential, gradient);
    }
}

void
printStretch(FILE *f, struct part *p, struct stretch *s)
{
    double len;
    double potential;
    double gradient;
    struct xyz p1;
    struct xyz p2;
    
    CHECK_VALID_BOND(s);
    fprintf(f, " stretch ");
    printAtomShort(f, s->a1);
    fprintf(f, ", ");
    printAtomShort(f, s->a2);
    fprintf(f, ":  %s ", s->stretchType->bondName);
    
    p1 = p->positions[s->a1->index];
    p2 = p->positions[s->a2->index];
    vsub(p1, p2);
    len = vlen(p1);
    
    potential = stretchPotential(NULL, NULL, s->stretchType, len);
    gradient = stretchGradient(NULL, NULL, s->stretchType, len);
    fprintf(f, "r: %f r0: %f, V: %f, dV: %f\n", len, s->stretchType->r0, potential, gradient);
}

void
printBend(FILE *f, struct part *p, struct bend *b)
{
    double invlen;
    double costheta;
    double theta;
    double dTheta;
    double potential;
    //double z;
    struct xyz p1;
    struct xyz pc;
    struct xyz p2;
    
    CHECK_VALID_BOND(b);
    fprintf(f, " bend ");
    printAtomShort(f, b->a1);
    fprintf(f, ", ");
    printAtomShort(f, b->ac);
    fprintf(f, ", ");
    printAtomShort(f, b->a2);
    fprintf(f, ":  %s ", b->bendType->bendName);
    
    p1 = p->positions[b->a1->index];
    pc = p->positions[b->ac->index];
    p2 = p->positions[b->a2->index];
    
    vsub(p1, pc);
    invlen = 1.0 / vlen(p1);
    vmulc(p1, invlen); // p1 is now unit vector from ac to a1
    
    vsub(p2, pc);
    invlen = 1.0 / vlen(p2);
    vmulc(p2, invlen); // p2 is now unit vector from ac to a2
    
    costheta = vdot(p1, p2);
    theta = acos(costheta);
    fprintf(f, "theta: %f ", theta * 180.0 / Pi);
    
#if 0
    z = vlen(vsum(p1, p2)); // z is length of cord between where bonds intersect unit sphere
    
#define ACOS_POLY_A -0.0820599
#define ACOS_POLY_B  0.142376
#define ACOS_POLY_C -0.137239
#define ACOS_POLY_D -0.969476
    
    // this is the equivalent of theta=arccos(z);
    theta = Pi + z * (ACOS_POLY_D +
		      z * (ACOS_POLY_C +
			   z * (ACOS_POLY_B +
				z *  ACOS_POLY_A   )));
    
    fprintf(f, "polytheta: %f ", theta * 180.0 / Pi);
#endif
    
    dTheta = (theta - b->bendType->theta0);
    potential = 1e-6 * 0.5 * dTheta * dTheta * b->bendType->kb;
    
    fprintf(f, "theta0: %f dTheta: %f, V: %f\n", b->bendType->theta0 * 180.0 / Pi, dTheta * 180.0 / Pi, potential);
}

void
printTorsion(FILE *f, struct part *p, struct torsion *t)
{
    NULLPTR(t);
    NULLPTR(t->a1);
    NULLPTR(t->aa);
    NULLPTR(t->ab);
    NULLPTR(t->a2);
    fprintf(f, " torsion ");
    printAtomShort(f, t->a1);
    fprintf(f, " - ");
    printAtomShort(f, t->aa);
    fprintf(f, " = ");
    printAtomShort(f, t->ab);
    fprintf(f, " - ");
    printAtomShort(f, t->a2);
    fprintf(f, "\n");
}

void
printOutOfPlane(FILE *f, struct part *p, struct outOfPlane *o)
{
    NULLPTR(o);
    NULLPTR(o->ac);
    NULLPTR(o->a1);
    NULLPTR(o->a2);
    NULLPTR(o->a3);
    fprintf(f, " outOfPlane ");
    printAtomShort(f, o->ac);
    fprintf(f, " - (");
    printAtomShort(f, o->a1);
    fprintf(f, ", ");
    printAtomShort(f, o->a2);
    fprintf(f, ", ");
    printAtomShort(f, o->a3);
    fprintf(f, ")\n");
}

void
printPart(FILE *f, struct part *p)
{
    int i;
    
    fprintf(f, "part loaded from file %s\n", p->filename);
    for (i=0; i<p->num_atoms; i++) {
	printAtom(f, p, p->atoms[i]);
    }
    for (i=0; i<p->num_bonds; i++) {
	printBond(f, p, p->bonds[i]);
    }
    for (i=0; i<p->num_jigs; i++) {
	printJig(f, p, p->jigs[i]);
    }
    for (i=0; i<p->num_vanDerWaals; i++) {
	printVanDerWaals(f, p, p->vanDerWaals[i]);
    }
    for (i=0; i<p->num_stretches; i++) {
	printStretch(f, p, &p->stretches[i]);
    }
    for (i=0; i<p->num_bends; i++) {
	printBend(f, p, &p->bends[i]);
    }
    for (i=0; i<p->num_torsions; i++) {
	printTorsion(f, p, &p->torsions[i]);
    }
    for (i=0; i<p->num_outOfPlanes; i++) {
	printOutOfPlane(f, p, &p->outOfPlanes[i]);
    }
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
