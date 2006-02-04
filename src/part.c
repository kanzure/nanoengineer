
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
    p->filename = filename;
    p->parseError = parseError ? parseError : &defaultParseError;
    p->stream = parseError ? stream : p;
    return p;
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
    a->hybridization = sp3;
    
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

static struct jig *
newJig(struct part *p)
{
    struct jig *j;
    
    p->num_jigs++;
    p->jigs = (struct jig **)accumulator(p->jigs, sizeof(struct jig *) * p->num_jigs, 0);
    j = (struct jig *)allocate(sizeof(struct jig));
    p->jigs[p->num_jigs - 1] = j;
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

// Create a rotary motor jig in this part, given the name of the jig,
// parameters controlling the motor, and the list of atoms to include.
// The motor rotates around the center point, with the plane of
// rotation perpendicular to the direction of the axis vector.
//
// (XXX need good description of behavior of stall and speed)
void
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

    // Example uses 1 nN-nm -> 1e6 pN-pm
    // Example uses 2 GHz -> 12.5664e9 radians/second

    // convert nN-nm to pN-pm
    j->j.rmotor.stall = stall * (1e-9/Dx) * (1e-9/Dx);
    // convert from gigahertz to radians per second
    j->j.rmotor.speed = speed * 2.0e9 * Pi;
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
    
    // Add a flywheel with ten times the moment of inertia of the atoms
    j->j.rmotor.momentOfInertia *= 11.0;
    j->j.rmotor.theta = 0.0;
    j->j.rmotor.omega = 0.0;
}

// Create a linear motor jig in this part, given the name of the jig,
// parameters controlling the motor, and the list of atoms to include.
// Atoms in the jig are constrained to move in the direction given by
// the axis vector.  A constant force can be applied, or they can be
// connected to a spring of the given stiffness.
//
// I don't think center actually matters. -emm
//
// XXX behavior when both force and stiffness specified?
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
    j->j.lmotor.force = force;
    j->j.lmotor.stiffness = stiffness;
    j->j.lmotor.center = *center;
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
	j->j.lmotor.center = vprodc(j->j.lmotor.axis, force / atomListLength);
    } else {
	j->j.lmotor.zeroPosition = x + force / stiffness ;
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
	fprintf(f, "  stall: %f\n", j->j.rmotor.stall);
	fprintf(f, "  speed: %f\n", j->j.rmotor.speed);
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
	fprintf(f, "  center: ");
	printXYZ(f, j->j.lmotor.center);
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
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
