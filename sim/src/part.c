// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 

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
static int
defaultParseError(void *stream)
{
    struct part *p;
    
    p = (struct part *)stream;
    ERROR1("Parsing part %s", p->filename);
    done("Failed to parse part %s", p->filename);
    RAISER("Failed to parse part", 0);
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
makePart(char *filename, int (*parseError)(void *), void *stream)
{
    struct part *p;
    struct rigidBody *rb;
    
    p = (struct part *)allocate(sizeof(struct part));
    memset(p, 0, sizeof(struct part));
    p->max_atom_id = -1;
    p->filename = copy_string(filename);
    p->parseError = parseError ? parseError : &defaultParseError;
    p->stream = parseError ? stream : p;

    p->num_rigidBodies = 1 ;
    p->rigidBodies = (struct rigidBody *)accumulator(p->rigidBodies, sizeof(struct rigidBody), 0);
    p->atomTypesUsed = hashtable_new(32);
    rb = &p->rigidBodies[0];
    memset(rb, 0, sizeof(struct rigidBody));
    rb->name = copy_string("$Anchor");

    return p;
}

void
destroyPart(struct part *p)
{
    int i;
    int k;
    struct atom *a;
    struct bond *b;
    struct jig *j;
    struct vanDerWaals *v;
    struct rigidBody *rb;
    
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
        //a->prev and next just point to other atoms
        //a->bonds has pointers into the p->bonds array
        destroyAccumulator(a->bonds);
        a->bonds = NULL;
        free(a);
    }
    destroyAccumulator(p->atoms);
    p->atoms = NULL;
    destroyAccumulator(p->charged_atoms);
    p->charged_atoms = NULL;
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

    if (p->rigid_body_info != NULL) {
        rigid_destroy(p);
        p->rigid_body_info = NULL;
    }
    for (i=0; i<p->num_rigidBodies; i++) {
        rb = &p->rigidBodies[i];
        free(rb->name);
        rb->name = NULL;
        destroyAccumulator(rb->stations);
        rb->stations = NULL;
        for (k=0; k<rb->num_stations; k++) {
            free(rb->stationNames[k]);
        }
        destroyAccumulator(rb->stationNames);
        rb->stationNames = NULL;
        destroyAccumulator(rb->axes);
        rb->axes = NULL;
        for (k=0; k<rb->num_axes; k++) {
            free(rb->axisNames[k]);
        }
        destroyAccumulator(rb->axisNames);
        rb->axisNames = NULL;
        free(rb->attachmentLocations);
        rb->attachmentLocations = NULL;
        free(rb->attachmentAtomIndices);
        rb->attachmentAtomIndices = NULL;
    }
    destroyAccumulator(p->rigidBodies);
    p->rigidBodies = NULL;

    // joint has no separately allocated storage
    destroyAccumulator(p->joints);
    p->joints = NULL;

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
    p->vanDerWaals = NULL;
    
    // nothing in a stretch needs freeing
    destroyAccumulator(p->stretches);
    p->stretches = NULL;

    // nothing in a bend needs freeing
    destroyAccumulator(p->bends);
    p->bends = NULL;

    // nothing in a torsion needs freeing
    if (p->torsions != NULL) {
        free(p->torsions);
        p->torsions = NULL;
    }

    // nothing in a cumuleneTorsion needs freeing
    if (p->cumuleneTorsions != NULL) {
        free(p->cumuleneTorsions);
        p->cumuleneTorsions = NULL;
    }

    // nothing in an outOfPlane needs freeing
    if (p->outOfPlanes != NULL) {
        free(p->outOfPlanes);
        p->outOfPlanes = NULL;
    }

    destroyAccumulator(p->queuedComponents);
    p->queuedComponents = NULL;

    hashtable_destroy(p->atomTypesUsed, NULL);
    free(p);
}

static void
addBondToAtom(struct bond *b, struct atom *a)
{
    a->num_bonds++;
    a->bonds = (struct bond **)accumulator(a->bonds, sizeof(struct bond *) * a->num_bonds, 0);
    a->bonds[a->num_bonds - 1] = b;
}

// return the n'th atom which is bonded to a, or NULL
struct atom *
getBondedAtom(struct atom *a, int n)
{
    struct bond *b;
    
    if (a == NULL || n < 0 || a->num_bonds <= n) {
        return NULL;
    }
    b = a->bonds[n];
    if (b->a1 == a) {
        return b->a2;
    }
    if (b->a2 == a) {
        return b->a1;
    }
    fprintf(stderr, "getBondedAtom(): malformed bond\n");
    return NULL;
}

// Fill in the bend data structure for a bend centered on the given
// atom.  The two bonds that make up the bend are indexed in the
// center atom's bond array.
static void
makeBend(struct part *p, struct atom *a, int bond1, int bond2)
{
    struct bond *b1;
    struct bond *b2;
    struct atom *a1;
    struct atom *a2;
    int dir1;
    int dir2;
    struct bendData *type;
    struct bend *b;

    b1 = a->bonds[bond1];
    b2 = a->bonds[bond2];
    CHECK_VALID_BOND(b1);
    CHECK_VALID_BOND(b2);

    if (b1->a1 == a) {
	a1 = b1->a2;
	dir1 = 1;
    } else if (b1->a2 == a) {
	a1 = b1->a1;
	dir1 = 0;
    } else {
	// print a better error if it ever happens...
	fprintf(stderr, "neither end of bond on center!");
    }
    
    if (b2->a1 == a) {
	a2 = b2->a2;
	dir2 = 1;
    } else if (b2->a2 == a) {
	a2 = b2->a1;
	dir2 = 0;
    } else {
	// print a better error if it ever happens...
	fprintf(stderr, "neither end of bond on center!");
    }
    
    // XXX should just use atomType instead of protons
    type = getBendData(a->type->protons,
                       a->hybridization,
                       a1->type->protons, b1->order,
                       a2->type->protons, b2->order);

    if (type != NULL) {
        p->num_bends++;
        p->bends = (struct bend *)accumulator(p->bends, sizeof(struct bend) * p->num_bends, 0);
        b = &p->bends[p->num_bends - 1];
        b->a1 = a1;
        b->ac = a;
        b->a2 = a2;
        b->b1 = b1;
        b->b2 = b2;
        b->dir1 = dir1;
        b->dir2 = dir2;
        b->bendType = type;
    }
}

static void
createBends(struct part *p, struct atom *a)
{
    int lastBond;
    int i;
    
    lastBond = a->num_bonds - 1;
    for (i=a->num_bonds-2; i>= 0; i--) {
        makeBend(p, a, lastBond, i);
    }
}

static void
addBondToAtoms(struct part *p, struct bond *b)
{
    struct stretch *s;
    
    addBondToAtom(b, b->a1);
    addBondToAtom(b, b->a2);

    // Create a stretch for the bond
    p->num_stretches = p->num_bonds;
    p->stretches = (struct stretch *)accumulator(p->stretches, sizeof(struct stretch) * p->num_stretches, 0);
    s = &(p->stretches[p->num_stretches - 1]);
    // XXX skip stretch if both ends are grounded
    s->a1 = b->a1;
    s->a2 = b->a2;
    s->b = b;
    // XXX really should send struct atomType instead of protons
    s->stretchType = getBondStretch(s->a1->type->protons,
                                    s->a2->type->protons,
                                    b->order);

    // Create a set of bends off of each end of this bond
    createBends(p, b->a1);
    createBends(p, b->a2);
}


// Called to indicate that a parser has finished reading data for this
// part.  Finalizes the data structures and switches to the default
// error handler.
struct part *
endPart(struct part *p)
{
    p->parseError = &defaultParseError;
    p->stream = p;
    p->num_vanDerWaals = p->num_static_vanDerWaals;
    
    // XXX realloc any accumulators
    
    // other routines should:
    // build stretchs, bends, and torsions
    // calculate initial velocities
    
    return p;
}

// This is called for every double bond in the cumulene chain.  On
// either end of the chain, there should be atoms of sp2
// hybridization.  In the middle, all of the atoms are sp.  This
// routine returns non-zero only when called with b as one of the two
// ending bonds, but not the other one.  When it does return non-zero,
// b2 is filled in with the other ending bond, and aa, ab, ay, and az
// are the atoms on either end of the bonds b and b2.  So, atom aa
// will be sp2, as will az, while ab and ay are sp.  The total number
// of double bonds in the chain (including b and b2) is returned in n.
static int
findCumuleneTorsion(struct bond *b,
                    struct bond **b2,
                    struct atom **aa,
                    struct atom **ab,
                    struct atom **ay,
                    struct atom **az,
                    int *n)
{
    int chainLength;
    struct bond *lastBond;
    struct bond *nextBond;
    struct atom *nextAtom;
    
    if (b->a1->hybridization == sp && b->a2->hybridization == sp) {
        return 0; // middle of the chain.
    }
    if (b->a1->hybridization != sp && b->a2->hybridization != sp) {
        return 0; // not a cumulene
    }
    if (b->a1->hybridization == sp) {
        nextAtom = b->a1;
        *aa = b->a2;
        *ab = b->a1;
    } else {
        nextAtom = b->a2;
        *aa = b->a1;
        *ab = b->a2;
    }
    nextBond = lastBond = b;
    chainLength = 1;
    while (nextAtom->hybridization == sp) {
        if (nextAtom->num_bonds != 2) {
            // XXX complain, I thought this thing was supposed to be sp, that means TWO bonds!
            return 0;
        }
        if (nextAtom->bonds[0] == lastBond) {
            nextBond = nextAtom->bonds[1];
        } else {
            nextBond = nextAtom->bonds[0];
        }
        switch (nextBond->order) {
        case '2':
        case 'a':
        case 'g': // we're being lenient here, a and g don't really make sense
            break;
        default:
            return 0; // chain terminated by a non-double bond, no torsions
        }
        if (nextBond->a1 == nextAtom) {
            nextAtom = nextBond->a2;
        } else {
            nextAtom = nextBond->a1;
        }
        lastBond = nextBond;
        chainLength++;
    }
    if ((*aa)->index >= nextAtom->index) {
        return 0; // only pick one end of the chain
    }
    *az = nextAtom;
    *b2 = nextBond;
    *n = chainLength;
    if (nextBond->a1 == nextAtom) {
        *ay = nextBond->a2;
    } else {
        *ay = nextBond->a1;
    }
    return 1;
}

static void
makeCumuleneTorsion(struct part *p,
                    int index,
                    struct atom *aa,
                    struct atom *ab,
                    struct atom *ay,
                    struct atom *az,
                    int j,
                    int k,
                    int n)
{
    struct cumuleneTorsion *t = &(p->cumuleneTorsions[index]);

    if (aa->bonds[j]->a1 == aa) {
        t->a1 = aa->bonds[j]->a2;
    } else {
        t->a1 = aa->bonds[j]->a1;
    }
    t->aa = aa;
    t->ab = ab;
    t->ay = ay;
    t->az = az;
    if (az->bonds[k]->a1 == az) {
        t->a2 = az->bonds[k]->a2;
    } else {
        t->a2 = az->bonds[k]->a1;
    }
    t->numberOfDoubleBonds = n;
    t->A = 0.22 / ((double)n); // XXX need actual value here
}

static void
makeTorsion(struct part *p, int index, struct bond *center, struct bond *b1, struct bond *b2)
{
    struct torsion *t = &(p->torsions[index]);

    t->aa = center->a1;
    t->ab = center->a2;
    t->a1 = b1->a1 == t->aa ? b1->a2 : b1->a1;
    t->a2 = b2->a1 == t->ab ? b2->a2 : b2->a1;

    // These numbers are based on a torsion around a Carbon-Carbon bond.
    switch (center->order) {
    case '2':
        // Barrier to rotation of a simple alkene is about 265 kJ/mol, but
        // can be on the order of 50 kJ/mol for "captodative ethylenes",
        // where the charge density on the carbons involved in the double
        // bond has been significantly altered.
        // [[Advanced Organic Chemistry, Jerry March, Fourth Edition,
        // Chapter 4, p.129.]]
        // A is in aJ/rad^2, but rotational barrior is 2A
        // 2.65e5 J/mol == 4.4e-19 J/bond
        // A = 2.2e-19 or 0.22 aJ
        t->A = 0.22; // XXX need to get actual value from real parameters
        break;
    case 'a':
    case 'g':
        // Damian has calculated the following for a small graphitic system
        //t->A = 0.37013376;
        t->A = 0.04;
        //t->A = 0.0;
        break;
    default:
        t->A = 0;
    }
}

// Creates a torsion for each triplet of adjacent bonds in the part,
// where the center bond is graphitic, aromatic, or double.  If one
// end of a double bond is an sp atom, we make a cumuleneTorsion
// instead.
static void
generateTorsions(struct part *p)
{
    int i;
    int j;
    int k;
    int torsion_index = 0;
    int cumuleneTorsion_index = 0;
    struct bond *b;
    struct bond *b2;
    struct atom *ct_a;
    struct atom *ct_b;
    struct atom *ct_y;
    struct atom *ct_z;
    int n;
    
    // first, count the number of torsions
    for (i=0; i<p->num_bonds; i++) {
	b = p->bonds[i];
        CHECK_VALID_BOND(b);
        switch (b->order) {
        case 'a':
        case 'g':
        case '2':
            if (b->a1->hybridization == sp || b->a2->hybridization == sp) {
                if (findCumuleneTorsion(b, &b2, &ct_a, &ct_b, &ct_y, &ct_z, &n)) {
                    for (j=0; j<ct_a->num_bonds; j++) {
                        if (ct_a->bonds[j] != b) {
                            for (k=0; k<ct_z->num_bonds; k++) {
                                if (ct_z->bonds[k] != b2) {
                                    p->num_cumuleneTorsions++;
                                }
                            }
                        }
                    }
                }
                break;
            }
            for (j=0; j<b->a1->num_bonds; j++) {
                if (b->a1->bonds[j] != b) {
                    for (k=0; k<b->a2->num_bonds; k++) {
                        if (b->a2->bonds[k] != b) {
                            p->num_torsions++;
                        }
                    }
                }
            }
            break;
        default:
            break;
        }
        
    }
    
    p->torsions = (struct torsion *)allocate(sizeof(struct torsion) * p->num_torsions);
    p->cumuleneTorsions = (struct cumuleneTorsion *)allocate(sizeof(struct cumuleneTorsion) * p->num_cumuleneTorsions);
    
    // now, fill them in (make sure loop structure is same as above)
    for (i=0; i<p->num_bonds; i++) {
	b = p->bonds[i];
        CHECK_VALID_BOND(b);
        switch (b->order) {
        case 'a':
        case 'g':
        case '2':
            if (b->a1->hybridization == sp || b->a2->hybridization == sp) {
                if (findCumuleneTorsion(b, &b2, &ct_a, &ct_b, &ct_y, &ct_z, &n)) {
                    for (j=0; j<ct_a->num_bonds; j++) {
                        if (ct_a->bonds[j] != b) {
                            for (k=0; k<ct_z->num_bonds; k++) {
                                if (ct_z->bonds[k] != b2) {
                                    makeCumuleneTorsion(p, cumuleneTorsion_index++, ct_a, ct_b, ct_y, ct_z, j, k, n);
                                }
                            }
                        }
                    }
                }
                break;
            }
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
    //o->A = 0.0;
    //o->A = 0.0005; // XXX need to get actual value from real parameters
}

// Creates an outOfPlane for each sp2 atom
static void
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

void
initializePart(struct part *p, int needVDW)
{
    if (needVDW) {
        updateVanDerWaals(p, NULL, p->positions); BAIL();
    }
    //generateBends(p); BAIL();
    generateTorsions(p); BAIL();
    generateOutOfPlanes(p); BAIL();
    rigid_init(p);
}

struct bend *
getBend(struct part *p, struct atom *a1, struct atom *ac, struct atom *a2)
{
    struct bend *b;
    int i;
    
    for (i=0; i<p->num_bends; i++) {
        b = &p->bends[i];
        if (b->ac == ac && ((b->a1 == a1 && b->a2 == a2) ||
                            (b->a1 == a2 && b->a2 == a1)))
        {
            return b;
        }
    }
    ERROR3("getBend: no bend between atom ids %d-%d-%d", a1->atomID, ac->atomID, a2->atomID);
    p->parseError(p->stream);
    return NULL;
}

struct bond *
getBond(struct part *p, struct atom *a1, struct atom *a2)
{
    struct bond *b;
    int i;
    
    for (i=0; i<p->num_bonds; i++) {
        b = p->bonds[i];
        if ((b->a1 == a1 && b->a2 == a2) ||
            (b->a1 == a2 && b->a2 == a1))
        {
            return b;
        }
    }
    ERROR2("getBond: no bond between atom ids %d-%d", a1->atomID, a2->atomID);
    p->parseError(p->stream);
    return NULL;
}

struct stretch *
getStretch(struct part *p, struct atom *a1, struct atom *a2)
{
    struct stretch *s;
    int i;
    
    for (i=0; i<p->num_stretches; i++) {
        s = &p->stretches[i];
        if ((s->a1 == a1 && s->a2 == a2) ||
            (s->a1 == a2 && s->a2 == a1))
        {
            return s;
        }
    }
    ERROR2("getStretch: no stretch between atom ids %d-%d", a1->atomID, a2->atomID);
    p->parseError(p->stream);
    return NULL;
}

// use these if the vdw generation code fails to create or destroy an
// interaction when it should, as determined by the verification
// routine.  The grid locations of the two indicated atoms will be
// printed each time, along with indications of when the interaction
// between them is created or destroyed.
//#define TRACK_VDW_PAIR
//#define VDW_FIRST_ATOM_ID 61
//#define VDW_SECOND_ATOM_ID 73

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
#ifdef TRACK_VDW_PAIR
            if (vdw->a1->atomID == VDW_FIRST_ATOM_ID && vdw->a2->atomID == VDW_SECOND_ATOM_ID) {
                fprintf(stderr, "deleting vdw from %d to %d\n", vdw->a1->atomID, vdw->a2->atomID);
            }
#endif
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
    struct vanDerWaalsParameters *parameters;

    parameters = getVanDerWaalsTable(a1->type->protons, a2->type->protons);
    if (parameters == NULL) {
        return;
    }
    
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
    vdw->parameters = parameters;
#ifdef TRACK_VDW_PAIR
    if (a1->atomID == VDW_FIRST_ATOM_ID && a2->atomID == VDW_SECOND_ATOM_ID) {
        fprintf(stderr, "creating vdw from %d to %d\n", a1->atomID, a2->atomID);
    }
#endif
}

// Scan the dynamic electrostatic list and mark as invalid any
// interaction involving atom a.
static void
invalidateElectrostatic(struct part *p, struct atom *a)
{
    int i;
    struct electrostatic *es;
    
    for (i=0; i<p->num_electrostatic; i++) {
	es = p->electrostatic[i];
	if (es && (es->a1 == a || es->a2 == a)) {
	    p->electrostatic[i] = NULL;
	    free(es);
	    if (i < p->start_electrostatic_free_scan) {
		p->start_electrostatic_free_scan = i;
	    }
	}
    }
}

// Find a free slot in the dynamic electrostatic list (either one
// marked invalid above, or a new one appended to the list).  Fill it
// with a new, valid, interaction.
static void
makeDynamicElectrostatic(struct part *p, struct atom *a1, struct atom *a2)
{
    int i;
    struct electrostatic *es = NULL;
    
    es = (struct electrostatic *)allocate(sizeof(struct electrostatic));
    
    for (i=p->start_electrostatic_free_scan; i<p->num_electrostatic; i++) {
	if (!(p->electrostatic[i])) {
	    p->electrostatic[i] = es;
	    p->start_electrostatic_free_scan = i + 1;
	    break;
	}
    }
    if (i >= p->num_electrostatic) {
	p->num_electrostatic++;
	p->electrostatic = (struct electrostatic **)
	    accumulator(p->electrostatic,
			sizeof(struct electrostatic *) * p->num_electrostatic, 0);
	p->electrostatic[p->num_electrostatic - 1] = es;
	p->start_electrostatic_free_scan = p->num_electrostatic;
    }
    es->a1 = a1;
    es->a2 = a2;
    es->parameters = getElectrostaticParameters(a1->type->protons, a2->type->protons);
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
		if (distance < rvdw * VanDerWaalsCutoffFactor) {
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
			testAlert("missing vdw: a1:");
			printAtomShort(stderr, a1);
			testAlert(" a2:");
			printAtomShort(stderr, a2);
			testAlert(" distance: %f rvdw: %f\n", distance, rvdw);
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
		if (distance < rvdw * VanDerWaalsCutoffFactor) {
		    testAlert("should have found this one above!!!\n");
		}
		if (distance > rvdw * VanDerWaalsCutoffFactor + 2079.0) { // was 866.0
		    testAlert("unnecessary vdw: a1:");
		    printAtomShort(stderr, vdw->a1);
		    testAlert(" a2:");
		    printAtomShort(stderr, vdw->a2);
		    testAlert(" distance: %f rvdw: %f\n", distance, rvdw);
		}
	    }
	}
    }
    //testAlert("num_vdw: %d actual_count: %d not_seen: %d\n", p->num_vanDerWaals, actual_count, notseen_count);
    free(seen); // yes, alloca would work here too.
}

// All of space is divided into a cubic grid with each cube being
// GRID_SPACING pm on a side.  Every GRID_OCCUPANCY cubes in each
// direction there is a bucket.  Every GRID_SIZE buckets the grid
// wraps back on itself, so that each bucket stores atoms that are in
// an infinite number of grid cubes, where the cubes are some multiple
// of GRID_SPACING * GRID_OCCUPANCY * GRID_SIZE pm apart.  GRID_SIZE
// must be a power of two, so the index along a particular dimension
// of the bucket array where a particular coordinates is found is
// calculated with: (int(x/GRID_SPACING) * GRID_OCCUPANCY) &
// (GRID_SIZE-1).
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
// The fuzzy match looks like this: moved = (current - previous) &
// GRID_MASK.  GRID_MASK is (GRID_SIZE-1) with one or more low order
// bits zeroed.  It works correctly if the subtraction is done two's
// complement, it may not for one's complement subtraction.  With no
// bits zeroed, there is no overlap.  With one zero, the buckets
// overlap by 50%.  Two zeros = 3/4 overlap.  Three zeros = 7/8
// overlap.  The above are if GRID_OCCUPANCY == 1.  Larger values for
// GRID_OCCUPANCY allow overlaps between zero and 50%.
//
// Current algorithm is written for 50% overlap, so GRID_OCCUPANCY is
// assumed to be 1, simplifing the code.
//
// GRID_FUZZY_BUCKET_WIDTH is the size of a fuzzy bucket in bucket
// units.  For a 50% overlap it has the value 2.



// Update the dynamic van der Waals list for this part.  Validity is a
// tag to prevent rescanning the same configuration a second time.
void
updateVanDerWaals(struct part *p, void *validity, struct xyz *positions)
{
    int i;
    int ax;
    int ay;
    int az;
    int ax2;
    int ay2;
    int az2;
    struct atom *a;
    struct atom *a2;
    struct atom *aNext;
    struct atom *aPrev;
    struct atom **bucket;
    double r;
    double rSquared;
    double actualR;
    double r_maxVdw;
    double r_maxElectrostatic;
    double coulombK;
    struct xyz dr;
    double drSquared;
    int dx;
    int dy;
    int dz;
    double deltax;
    double deltay;
    double deltaz;
    double deltaXSquared;
    double deltaYSquared;
    double deltaZSquared;
    int signx;
    int signy;
    int signz;

    // wware 060109  python exception handling
    NULLPTR(p);
    if (validity && p->vanDerWaals_validity == validity) {
	return;
    }
    if (p->num_atoms <= 0) {
        return;
    }
    NULLPTR(positions);
    for (i=0; i<p->num_atoms; i++) {
	a = p->atoms[i];
        if (a->type->vanDerWaalsRadius <= 0.0) {
            continue;
        }
	ax = (int)(positions[i].x / GRID_SPACING);
	ay = (int)(positions[i].y / GRID_SPACING);
	az = (int)(positions[i].z / GRID_SPACING);

#ifdef TRACK_VDW_PAIR
        if (a->atomID == VDW_FIRST_ATOM_ID || a->atomID == VDW_SECOND_ATOM_ID) {
            fprintf(stderr, "%d (%d, %d, %d) Iteration %d\n", a->atomID, ax, ay, az, Iteration);
        }
#endif
	if (a->vdwBucketInvalid ||
            (ax - a->vdwBucketIndexX) & GRID_MASK_FUZZY ||
            (ay - a->vdwBucketIndexY) & GRID_MASK_FUZZY ||
            (az - a->vdwBucketIndexZ) & GRID_MASK_FUZZY) {

	    invalidateVanDerWaals(p, a);
            invalidateElectrostatic(p, a);
	    // remove a from it's old bucket chain
	    if (a->vdwNext) {
		a->vdwNext->vdwPrev = a->vdwPrev;
	    }
	    if (a->vdwPrev) {
		a->vdwPrev->vdwNext = a->vdwNext;
	    } else {
                bucket = &(p->vdwHash[a->vdwBucketIndexX][a->vdwBucketIndexY][a->vdwBucketIndexZ]);
                if (*bucket == a) {
                    *bucket = a->vdwNext;
                }
	    }
	    // and add it to the new one
            a->vdwBucketIndexX = ax & GRID_MASK;
            a->vdwBucketIndexY = ay & GRID_MASK;
            a->vdwBucketIndexZ = az & GRID_MASK;
            a->vdwBucketInvalid = 0;
            bucket = &(p->vdwHash[a->vdwBucketIndexX][a->vdwBucketIndexY][a->vdwBucketIndexZ]);

            // If a is charged, we put it on the front of the list, otherwise
            // we search for the first non-charged atom and insert it there.
            // This maintains the invariant that charged atoms preceed non
            // charged atoms.
            if (a->isCharged) {
                a->vdwNext = *bucket;
                a->vdwPrev = NULL;
                *bucket = a;
                if (a->vdwNext) {
                    a->vdwNext->vdwPrev = a;
                }
            } else {
                aNext = *bucket;
                aPrev = NULL;
                while (aNext != NULL && aNext->isCharged) {
                    aPrev = aNext;
                    aNext = aNext->vdwNext;
                }
                // At this point, aNext is the first non-charged atom
                // and aPrev is the last charged atom.  Either or both
                // may be NULL.
                a->vdwNext = aNext;
                a->vdwPrev = aPrev;
                if (aPrev == NULL) {
                    *bucket = a;
                } else {
                    aPrev->vdwNext = a;
                }
                if (aNext != NULL) {
                    aNext->vdwPrev = a;
                }
            }
            
            r_maxVdw = (a->type->vanDerWaalsRadius * 100.0 + p->maxVanDerWaalsRadius) * VanDerWaalsCutoffFactor;
            r = r_maxVdw;
            if (EnableElectrostatic && a->isCharged) {
                coulombK = COULOMB * a->type->charge * p->maxParticleCharge / DielectricConstant;
                r_maxElectrostatic = fabs(coulombK) / MinElectrostaticSensitivity;
                if (r_maxElectrostatic > r) {
                    r = r_maxElectrostatic;
                }
            }

            rSquared = r * r;
            dx = 0;
            while (1) {
                // deltax is the minimum distance along the x axis
                // between the fuzzy edges of the two buckets we're
                // looking at.  Both atoms can move within their
                // respective fuzzy buckets and will never get closer
                // than this along the x axis.  If the fuzzy buckets
                // overlap, or share an edge, the distance is zero.
                deltax = (dx-GRID_FUZZY_BUCKET_WIDTH > 0 ? dx-GRID_FUZZY_BUCKET_WIDTH : 0) * GRID_SPACING;
                if (deltax > r) {
                    break;
                }
                deltaXSquared = deltax * deltax;
                for (signx=-1; signx<=1; signx+=2) {
                    if (signx > 0 || dx > 0) {
                        ax2 = ax + dx * signx;
                        
                        dy = 0;
                        while (1) {
                            deltay = (dy-GRID_FUZZY_BUCKET_WIDTH > 0 ? dy-GRID_FUZZY_BUCKET_WIDTH : 0) * GRID_SPACING;
                            deltaYSquared = deltay * deltay;
                            if (deltaXSquared + deltaYSquared > rSquared) {
                                break;
                            }
                            for (signy=-1; signy<=1; signy+=2) {
                                if (signy > 0 || dy > 0) {
                                    ay2 = ay + dy * signy;

                                    dz = 0;
                                    while (1) {
                                        deltaz = (dz-GRID_FUZZY_BUCKET_WIDTH > 0 ? dz-GRID_FUZZY_BUCKET_WIDTH : 0) * GRID_SPACING;
                                        deltaZSquared = deltaz * deltaz;
                                        if (deltaXSquared +
                                            deltaYSquared +
                                            deltaZSquared > rSquared) {
                                            break;
                                        }
                                        for (signz=-1; signz<=1; signz+=2) {
                                            if (signz > 0 || dz > 0) {
                                                az2 = az + dz * signz;
                                                // We hit this point in the code once for each bucket
                                                // that could contain an atom of any type which is
                                                // within the maximum vdw cutoff radius.

                                                a2 = p->vdwHash[ax2&GRID_MASK][ay2&GRID_MASK][az2&GRID_MASK];
                                                for (; a2 != NULL; a2=a2->vdwNext) {
                                                    if (isBondedToSame(a, a2)) {
                                                        continue;
                                                    }
                                                    if (a->type->vanDerWaalsRadius > 0.0 &&
                                                        a2->type->vanDerWaalsRadius > 0.0) {
                                                        // At this point, we know the types of both
                                                        // atoms, so we can eliminate buckets which
                                                        // might be in range for some atom types,
                                                        // but not for this one.
                                                        actualR = (a->type->vanDerWaalsRadius * 100.0 +
                                                                   a2->type->vanDerWaalsRadius * 100.0)
                                                            * VanDerWaalsCutoffFactor;
                                                        if (deltaXSquared +
                                                            deltaYSquared +
                                                            deltaZSquared > (actualR * actualR)) {
                                                            continue;
                                                        }
                                                        // Now we check to see if the two atoms are
                                                        // actually within the same wrapping of the
                                                        // grid.  Just because they're in nearby
                                                        // buckets, it doesn't mean that they are
                                                        // actually near each other.  This check is
                                                        // very coarse, because we've already
                                                        // eliminated intermediate distances.
                                                        dr = vdif(positions[i], positions[a2->index]);
                                                        drSquared = vdot(dr, dr);
                                                        if (drSquared < GRID_WRAP_COMPARE * GRID_WRAP_COMPARE) {
                                                            // We insure that all vdw's are created
                                                            // with the first atom of lower index
                                                            // than the second.
                                                            if (i < a2->index) {
                                                                makeDynamicVanDerWaals(p, a, a2); BAIL();
                                                            } else {
                                                                makeDynamicVanDerWaals(p, a2, a); BAIL();
                                                            }
                                                        }
                                                    }
                                                    if (EnableElectrostatic && a->isCharged && a2->isCharged) {
                                                        coulombK = COULOMB * a->type->charge * a2->type->charge /
                                                            DielectricConstant;
                                                        actualR = fabs(coulombK) / MinElectrostaticSensitivity;
                                                        if (deltaXSquared +
                                                            deltaYSquared +
                                                            deltaZSquared > (actualR * actualR)) {
                                                            continue;
                                                        }
                                                        dr = vdif(positions[i], positions[a2->index]);
                                                        drSquared = vdot(dr, dr);
                                                        if (drSquared < GRID_WRAP_COMPARE * GRID_WRAP_COMPARE) {
                                                            if (i < a2->index) {
                                                                makeDynamicElectrostatic(p, a, a2); BAIL();
                                                            } else {
                                                                makeDynamicElectrostatic(p, a2, a); BAIL();
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                        dz++;
                                    }
                                }
                            }
                            dy++;
                        }
                    }
                }
                dx++;
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
        return NULL;
    }
    atomIndex = p->atom_id_to_index_plus_one[atomID] - 1;
    if (atomIndex < 0) {
	ERROR1("atom ID %d not yet encountered", atomID);
	p->parseError(p->stream);
        return NULL;
    }
    return p->atoms[atomIndex];
}

// gaussianDistribution() and gxyz() are also used by the thermostat jig...

// generate a random number with a gaussian distribution
//
// see Knuth, Vol 2, 3.4.1.C
static double
gaussianDistribution(double mean, double stddev)
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
    return mean + stddev * v0 * sqrt(-2.0 * log(rSquared) / rSquared);
}

// Generates a gaussian distributed random velocity for a range of
// atoms, scaled by 1/sqrt(mass).  The result array must be
// preallocated by the caller.
static void
generateRandomVelocities(struct part *p, struct xyz *velocity, int firstAtom, int lastAtom)
{
    int i;
    double stddev;
    
    for (i=firstAtom; i<=lastAtom; i++) {
        stddev = sqrt(2.0 * Boltz * Temperature / (p->atoms[i]->mass * 1e-27)) * Dt / Dx;
        velocity[i].x = gaussianDistribution(0.0, stddev);
        velocity[i].y = gaussianDistribution(0.0, stddev);
        velocity[i].z = gaussianDistribution(0.0, stddev);
    }
}

// Find the center of mass of a range of atoms in the part.
static struct xyz
findCenterOfMass(struct part *p, struct xyz *position, int firstAtom, int lastAtom)
{
    struct xyz com;
    struct xyz a;
    double mass;
    double totalMass = 0.0;
    int i;

    vsetc(com, 0.0);
    for (i=firstAtom; i<=lastAtom; i++) {
        mass = p->atoms[i]->mass;
        vmul2c(a, position[i], mass);
        vadd(com, a);
        totalMass += mass;
    }
    if (fabs(totalMass) > 1e-20) {
        vmulc(com, 1.0/totalMass);
    }
    return com;
}

static double
findTotalMass(struct part *p, int firstAtom, int lastAtom)
{
    double mass = 0.0;
    int i;

    for (i=firstAtom; i<=lastAtom; i++) {
        mass += p->atoms[i]->mass;
    }
    return mass;
}

static struct xyz
findAngularMomentum(struct part *p, struct xyz center, struct xyz *position, struct xyz *velocity, int firstAtom, int lastAtom)
{
    int i;
    struct xyz total_angular_momentum;
    struct xyz ap;
    struct xyz r;
    double mass;
    
    vsetc(total_angular_momentum, 0.0);
    for (i=firstAtom; i<=lastAtom; i++) {
        mass = p->atoms[i]->mass;
        vsub2(r, position[i], center);
        v2x(ap, r, velocity[i]);         // ap = r x (velocity * mass)
        vmulc(ap, mass);
        vadd(total_angular_momentum, ap);
    }
    return total_angular_momentum;
}

static struct xyz
findLinearMomentum(struct part *p, struct xyz *velocity, int firstAtom, int lastAtom)
{
    int i;
    struct xyz total_momentum;
    struct xyz momentum;
    double mass;
    
    vsetc(total_momentum, 0.0);
    for (i=firstAtom; i<=lastAtom; i++) {
        mass = p->atoms[i]->mass;
        vmul2c(momentum, velocity[i], mass);
        vadd(total_momentum, momentum);
    }
    return total_momentum;
}

static double
findMomentOfInertiaTensorComponent(struct part *p,
                                   struct xyz *position,
                                   struct xyz com,
                                   int axis1,
                                   int axis2,
                                   int firstAtom,
                                   int lastAtom)
{
    int i;
    struct xyza *com_a = (struct xyza *)(&com);
    struct xyza *position_a = (struct xyza *)position;
    double delta_axis1;
    double delta_axis2;
    double mass;
    double ret = 0.0;
    
    if (axis1 == axis2) {
        // I_xx = sum(m * (y^2 + z^2))
        axis1 = (axis1 + 1) % 3;
        axis2 = (axis2 + 2) % 3;
        for (i=firstAtom; i<=lastAtom; i++) {
            mass = p->atoms[i]->mass;
            delta_axis1 = position_a[i].a[axis1] - com_a->a[axis1];
            delta_axis2 = position_a[i].a[axis2] - com_a->a[axis2];
            ret += mass * (delta_axis1 * delta_axis1 + delta_axis2 * delta_axis2);
        }
    } else {
        // I_xy = -sum(m * x * y)
        for (i=firstAtom; i<=lastAtom; i++) {
            mass = p->atoms[i]->mass;
            delta_axis1 = position_a[i].a[axis1] - com_a->a[axis1];
            delta_axis2 = position_a[i].a[axis2] - com_a->a[axis2];
            ret -= mass * delta_axis1 * delta_axis2;
        }
    }
    return ret;
}


static void
findMomentOfInertiaTensor(struct part *p,
                          struct xyz *position,
                          struct xyz com,
                          double *inertia_tensor,
                          int firstAtom,
                          int lastAtom)
{
    inertia_tensor[0] = findMomentOfInertiaTensorComponent(p, position, com, 0, 0, firstAtom, lastAtom); // xx
    inertia_tensor[1] = findMomentOfInertiaTensorComponent(p, position, com, 0, 1, firstAtom, lastAtom); // xy
    inertia_tensor[2] = findMomentOfInertiaTensorComponent(p, position, com, 0, 2, firstAtom, lastAtom); // xz

    inertia_tensor[3] = inertia_tensor[1]; // yx = xy
    inertia_tensor[4] = findMomentOfInertiaTensorComponent(p, position, com, 1, 1, firstAtom, lastAtom); // yy
    inertia_tensor[5] = findMomentOfInertiaTensorComponent(p, position, com, 1, 2, firstAtom, lastAtom); // yz

    inertia_tensor[6] = inertia_tensor[2]; // zx = xz
    inertia_tensor[7] = inertia_tensor[5]; // zy = yz
    inertia_tensor[8] = findMomentOfInertiaTensorComponent(p, position, com, 2, 2, firstAtom, lastAtom); // zz
}

static void
addAngularVelocity(struct xyz center,
                   struct xyz dav,
                   struct xyz *position,
                   struct xyz *velocity,
                   int firstAtom,
                   int lastAtom)
{
    int i;
    struct xyz r;
    struct xyz davxr;
        
    for (i=firstAtom; i<=lastAtom; i++) {
        vsub2(r, position[i], center);
        v2x(davxr, dav, r);
        vadd(velocity[i], davxr);
    }
}

static void
addLinearVelocity(struct xyz dv,
                  struct xyz *velocity,
                  int firstAtom,
                  int lastAtom)
{
    int i;
    
    for (i=firstAtom; i<=lastAtom; i++) {
        vadd(velocity[i], dv);
    }
}

#if 0
static void
printPositionVelocity(struct xyz *position, struct xyz *velocity, int firstAtom, int lastAtom)
{
    int i;
    
    for (i=firstAtom; i<=lastAtom; i++) {
        printf("%d: (%7.3f, %7.3f, %7.3f) (%7.3f, %7.3f, %7.3f)\n",
               i,
               position[i].x,
               position[i].y,
               position[i].z,
               velocity[i].x,
               velocity[i].y,
               velocity[i].z);
    }
    printf("\n");
}

static void
printMomenta(struct part *p, struct xyz *position, struct xyz *velocity, int firstAtom, int lastAtom)
{
    struct xyz com;
    struct xyz total_linear_momentum;
    struct xyz total_angular_momentum;
    
    com = findCenterOfMass(p, position, firstAtom, lastAtom);
    printf("center of mass: (%f, %f, %f)\n", com.x, com.y, com.z);
    total_linear_momentum = findLinearMomentum(p, velocity, firstAtom, lastAtom);
    printf("total_linear_momentum: (%f, %f, %f)\n", total_linear_momentum.x, total_linear_momentum.y, total_linear_momentum.z);

    total_angular_momentum = findAngularMomentum(p, com, position, velocity, firstAtom, lastAtom);
    printf("total_angular_momentum: (%f, %f, %f)\n", total_angular_momentum.x, total_angular_momentum.y, total_angular_momentum.z);
    printPositionVelocity(position, velocity, firstAtom, lastAtom);
}
#endif

// Alter the given velocities for a range of atoms to remove any
// translational motion, and any rotation around their center of mass.
static void
neutralizeMomentum(struct part *p, struct xyz *position, struct xyz *velocity, int firstAtom, int lastAtom)
{
    struct xyz total_linear_momentum;
    struct xyz total_angular_momentum;
    struct xyz com;
    struct xyz dv;
    struct xyz dav;
    double inverseTotalMass;
    double momentOfInertiaTensor[9];
    double momentOfInertiaTensorInverse[9];

    com = findCenterOfMass(p, position, firstAtom, lastAtom);
    inverseTotalMass = 1.0 / findTotalMass(p, firstAtom, lastAtom);

    total_angular_momentum = findAngularMomentum(p, com, position, velocity, firstAtom, lastAtom);
    findMomentOfInertiaTensor(p, position, com, momentOfInertiaTensor, firstAtom, lastAtom);
    if (matrixInvert3(momentOfInertiaTensorInverse, momentOfInertiaTensor)) {
        matrixTransform(&dav, momentOfInertiaTensorInverse, &total_angular_momentum);
        vmulc(dav, -1.0);
        addAngularVelocity(com, dav, position, velocity, firstAtom, lastAtom);
    }

    total_linear_momentum = findLinearMomentum(p, velocity, firstAtom, lastAtom);
    vmul2c(dv, total_linear_momentum, -inverseTotalMass);
    addLinearVelocity(dv, velocity, firstAtom, lastAtom);
}

// Change the given velocities of a range of atoms so that their
// kinetic energies are scaled by the given factor.
static void
scaleKinetic(struct xyz *velocity, double factor, int firstAtom, int lastAtom)
{
    int i;
    double velocity_factor = sqrt(factor);

    // ke_old = m v_old^2 / 2
    // ke_new = m v_new^2 / 2 = factor ke_old = factor (m v_old^2 / 2)
    // m v_new^2 = factor m v_old^2
    // v_new^2 = factor v_old^2
    // v_new = sqrt(factor) v_old
    
    for (i=firstAtom; i<=lastAtom; i++) {
        vmulc(velocity[i], velocity_factor);
    }
}

void
setThermalVelocities(struct part *p, double temperature)
{
    int firstAtom = 0;
    int lastAtom = p->num_atoms-1;
    int dof; // degrees of freedom
    int i = 0;
    double initial_temp;

    if (p->num_atoms == 1 || temperature < 1e-8) {
        return;
    }
    // probably should be 3N-6, but the thermometer doesn't know that
    // the linear and angular momentum have been cancelled.
    dof = 3 * p->num_atoms;
    if (dof < 1) {
        dof = 1;
    }

    initial_temp = 0.0;
    while (fabs(initial_temp) < 1e-8) {
        generateRandomVelocities(p, p->velocities, firstAtom, lastAtom);
        neutralizeMomentum(p, p->positions, p->velocities, firstAtom, lastAtom);

        // kinetic = 3 k T / 2
        // T = kinetic 2 / 3 k
        // calculateKinetic() returns aJ (1e-18 J), so we get Kelvins:

        initial_temp = calculateKinetic(p) * 2.0 * 1e-18 / (Boltz * ((double)dof));
        if (++i > 10) {
            ERROR("unable to set initial temperature");
            return;
        }
    }

    // We scale to get to twice the target temperature, because we're
    // assuming the part has been minimized, and the energy will be
    // divided between kinetic and potential energy.
    scaleKinetic(p->velocities, 2.0 * temperature / initial_temp, firstAtom, lastAtom);
}

struct atom *
makeVirtualAtom(struct atomType *type,
                enum hybridization hybridization,
                char constructionAtoms,
                char function,
                struct atom *atom1,
                struct atom *atom2,
                struct atom *atom3,
                struct atom *atom4,
                double parameterA,
                double parameterB,
                double parameterC)
{
    struct atom *a;
    
    a = (struct atom *)allocate(sizeof(struct atom));
    memset(a, 0, sizeof(struct atom));

    a->type = type;
    a->hybridization = hybridization;
    a->virtualConstructionAtoms = constructionAtoms;
    a->virtualFunction = function;
    a->creationParameters.v.virtual1 = atom1;
    a->creationParameters.v.virtual2 = atom2;
    a->creationParameters.v.virtual3 = atom3;
    a->creationParameters.v.virtual4 = atom4;
    a->creationParameters.v.virtualA = parameterA;
    a->creationParameters.v.virtualB = parameterB;
    a->creationParameters.v.virtualC = parameterC;
    
    a->vdwBucketInvalid = 1;

    return a;
}

void
addVirtualAtom(struct part *p, struct atom *a)
{
    double vdwRadius;

    if (a == NULL) {
        return;
    }
    p->num_generated_atoms++;
    p->generated_atoms = (struct atom **)accumulator(p->generated_atoms,
                                                     sizeof(struct atom *) *
                                                     p->num_generated_atoms,
                                                     0);
    p->generated_atoms[p->num_generated_atoms - 1] = a;
    a->index = p->num_generated_atoms - 1;
    a->isGenerated = 1;
    
    hashtable_put(p->atomTypesUsed, a->type->symbol, a->type);

    vdwRadius = a->type->vanDerWaalsRadius * 100.0; // convert from angstroms to pm
    if (vdwRadius > p->maxVanDerWaalsRadius) {
        p->maxVanDerWaalsRadius = vdwRadius;
    }
}

// Create an atom, but don't add it to the part.  ExternalID is the
// atom number as it appears in (for example) an mmp file.
// ElementType is the number of protons (XXX should really be an
// atomType).
// position is in pm.
struct atom *
makeAtom(struct part *p, int externalID, int elementType, struct xyz position)
{
    double mass;
    struct atom *a;
    
    if (externalID < 0) {
	ERROR1("atom ID %d must be >= 0", externalID);
	p->parseError(p->stream);
        return NULL;
    }
    if (!isAtomTypeValid(elementType)) {
	ERROR1("Invalid element type: %d", elementType);
	p->parseError(p->stream);
        return NULL;
    }
    
    a = (struct atom *)allocate(sizeof(struct atom));
    memset(a, 0, sizeof(struct atom));
    a->atomID = externalID;
    a->type = getAtomTypeByIndex(elementType);
    a->vdwBucketInvalid = 1;
    
    if (a->type->group == 3) {
        a->hybridization = sp2;
    } else {
        a->hybridization = sp3;
    }

    if (a->type->charge != 0.0) {
        a->isCharged = 1;
    }
    
    mass = a->type->mass * 1e-27;
    a->mass = a->type->mass;
    a->inverseMass = Dt * Dt / mass;
    a->creationParameters.r.initialPosition = position;
    
    return a;
}

// Add a real atom to the part at the given position.
void
addAtom(struct part *p, struct atom *a)
{
    double vdwRadius;
    double absCharge;

    if (a == NULL) {
        return;
    }
    if (a->atomID > p->max_atom_id) {
	p->max_atom_id = a->atomID;
	p->atom_id_to_index_plus_one = (int *)accumulator(p->atom_id_to_index_plus_one,
							  sizeof(int) * (p->max_atom_id + 1), 1);
    }
    if (p->atom_id_to_index_plus_one[a->atomID]) {
	ERROR2("atom ID %d already defined with index %d", a->atomID, p->atom_id_to_index_plus_one[a->atomID] - 1);
	p->parseError(p->stream);
        return;
    }
    p->atom_id_to_index_plus_one[a->atomID] = ++(p->num_atoms);
    
    p->atoms = (struct atom **)accumulator(p->atoms, sizeof(struct atom *) * p->num_atoms, 0);
    p->positions = (struct xyz *)accumulator(p->positions, sizeof(struct xyz) * p->num_atoms, 0);
    p->velocities = (struct xyz *)accumulator(p->velocities, sizeof(struct xyz) * p->num_atoms, 0);
    p->atoms[p->num_atoms - 1] = a;
    a->index = p->num_atoms - 1;
    
    vset(p->positions[a->index], a->creationParameters.r.initialPosition);
    vsetc(p->velocities[a->index], 0.0);
    hashtable_put(p->atomTypesUsed, a->type->symbol, a->type);
    absCharge = fabs(a->type->charge);
    if (absCharge > p->maxParticleCharge) {
        p->maxParticleCharge = absCharge;
    }

    if (a->isCharged) {
        p->num_charged_atoms++;
        p->charged_atoms = (struct atom **)accumulator(p->charged_atoms, sizeof(struct atom *) * p->num_charged_atoms, 0);
        p->charged_atoms[p->num_charged_atoms - 1] = a;
    }

    vdwRadius = a->type->vanDerWaalsRadius * 100.0; // convert from angstroms to pm
    if (vdwRadius > p->maxVanDerWaalsRadius) {
        p->maxVanDerWaalsRadius = vdwRadius;
    }
}

void
setAtomHybridization(struct part *p, int atomID, enum hybridization h)
{
    struct atom *a;
    
    if (atomID < 0 || atomID > p->max_atom_id || p->atom_id_to_index_plus_one[atomID] < 1) {
	ERROR1("setAtomHybridization: atom ID %d not seen yet", atomID);
	p->parseError(p->stream);
        return;
    }
    a = p->atoms[p->atom_id_to_index_plus_one[atomID] - 1];
    a->hybridization = h;
}

// Create a new bond, but don't add it to the part.  The atomID's are
// the external atom numbers as found in an mmp file (for example).
struct bond *
makeBond(struct part *p, struct atom *a1, struct atom *a2, char order)
{
    struct bond *b;
    
    /*********************************************************************/
    // patch to pretend that carbomeric bonds are the same as double bonds
    if (order == 'c') {
	order = '2';
    }
    /*********************************************************************/
    
    b = (struct bond *)allocate(sizeof(struct bond));
    b->a1 = a1;
    b->a2 = a2;
    // XXX should we reject unknown bond orders here?
    b->order = order;
    b->direction = '?';
    b->valid = -1;
    return b;
}

struct bond *
makeBondFromIDs(struct part *p, int atomID1, int atomID2, char order)
{
    struct atom *a1;
    struct atom *a2;
    
    a1 = translateAtomID(p, atomID1); BAILR(NULL);
    a2 = translateAtomID(p, atomID2); BAILR(NULL);
    return makeBond(p, a1, a2, order);
}

void
addBond(struct part *p, struct bond *b)
{
    if (b == NULL) {
        return;
    }
    p->num_bonds++;
    p->bonds = (struct bond **)accumulator(p->bonds, sizeof(struct bond *) * p->num_bonds, 0);
    p->bonds[p->num_bonds - 1] = b;
    addBondToAtoms(p, b);
}

void
setBondDirection(struct part *p, int atomID1, int atomID2)
{
    struct atom *a1 = translateAtomID(p, atomID1); BAIL();
    struct atom *a2 = translateAtomID(p, atomID2); BAIL();
    struct bond *b;
    int i;
    
    for (i=p->num_bonds-1; i>=0; i--) {
        b = p->bonds[i];
        if (b->a1 == a1 && b->a2 == a2) {
            b->direction = 'F';
            return;
        }
        if (b->a1 == a2 && b->a2 == a1) {
            b->direction = 'R';
            return;
        }
    }
    ERROR2("setBondDirection: no bond between atom ids %d and %d", atomID1, atomID2);
    p->parseError(p->stream);
    return;
}

void
createBondChain(struct part *p, int atomID1, int atomID2, int bondDirection, char *baseSequence) 
{
    int previous;
    int current;
    
    printf("createBondChain(%d, %d, %d, '%s')\n", atomID1, atomID2, bondDirection, baseSequence);
    previous = atomID1;
    for (current=atomID1+1; current<=atomID2; previous=current, current++) {
        addBond(p, makeBondFromIDs(p, previous, current, '1')); BAIL();
        if (bondDirection < 0) {
            setBondDirection(p, current, previous);
        } else if (bondDirection > 0) {
            setBondDirection(p, previous, current);
        }
        BAIL();
    }
    // XXX set atom bases based on baseSequence
}

static struct atomType *typeSinglet = NULL;
static struct atomType *typePAMPhosphate = NULL;

static int
atomIDisOKforRungBond(struct part *p, int atomID)
{
    struct atom *a;
    
    if (typeSinglet == NULL) {
        typeSinglet = getAtomTypeByName("Singlet");
    }
    if (typePAMPhosphate == NULL) {
        typePAMPhosphate = getAtomTypeByName("P5P");
    }
    a = translateAtomID(p, atomID); BAILR(0);
    if (atomIsType(a, typeSinglet) || atomIsType(a, typePAMPhosphate)) {
        return 0;
    }
    return 1;
}


static int
nextRungBondID(struct part *p, int currentID, int lastID)
{
    // bondpoints and phosphates are not acceptable
    while (currentID <= lastID && !atomIDisOKforRungBond(p, currentID)) {
        BAILR(-1);
        currentID++;
    }
    if (currentID <= lastID) {
        return currentID;
    }
    return -1;
}

void
createRungBonds(struct part *p, int atomID1start, int atomID1end, int atomID2start, int atomID2end)
{
    int oneID;
    int twoID;
    
    printf("createRungBonds(%d, %d, %d, %d)\n", atomID1start, atomID1end, atomID2start, atomID2end);
    oneID = nextRungBondID(p, atomID1start, atomID1end);
    twoID = nextRungBondID(p, atomID2start, atomID2end);
    while (oneID >= 0 && twoID >= 0) {
        addBond(p, makeBondFromIDs(p, oneID, twoID, '1')); BAIL();
        oneID = nextRungBondID(p, oneID+1, atomID1end); BAIL();
        twoID = nextRungBondID(p, twoID+1, atomID2end); BAIL();
    }
    // XXX warn if oneID or twoID is >= 0?
}

static void
queueComponent(struct part *p, enum componentType type, void *component)
{
    struct queueablePartComponent *c;
    
    p->num_queued_components++;
    p->queuedComponents = (struct queueablePartComponent *)accumulator(p->queuedComponents, sizeof(struct queueablePartComponent) * p->num_queued_components, 0);
    c = &(p->queuedComponents[p->num_queued_components - 1]);

    c->type = type;
    c->component.any = component;
}

void
queueAtom(struct part *p, struct atom *a)
{
    a->atomID = (p->max_atom_id++) + 1 ;
    queueComponent(p, componentAtom, (void *)a);
}

void
queueBond(struct part *p, struct bond *b)
{
    queueComponent(p, componentBond, (void *)b);
}

void
addQueuedComponents(struct part *p)
{
    struct queueablePartComponent *c;
    int i;

    for (i=0; i<p->num_queued_components; i++) {
        c = &(p->queuedComponents[i]);
        switch (c->type) {
        case componentAtom:
            if (c->component.a->virtualConstructionAtoms != 0) {
                addVirtualAtom(p, c->component.a);
            } else {
                addAtom(p, c->component.a);
            }
            break;
        case componentBond:
            addBond(p, c->component.b);
            break;
        }
    }
    p->num_queued_components = 0;
    destroyAccumulator(p->queuedComponents);
    p->queuedComponents = NULL;
}

// Add a static van der Waals interaction between a pair of bonded
// atoms.  Not needed unless you want the vDW on directly bonded
// atoms, as all other vDW interactions will be automatically found.
void
makeVanDerWaals(struct part *p, int atomID1, int atomID2)
{
    struct vanDerWaals *v;
    struct vanDerWaalsParameters *parameters;
    struct atom *a1;
    struct atom *a2;
    
    a1 = translateAtomID(p, atomID1); BAIL();
    a2 = translateAtomID(p, atomID2); BAIL();
    parameters = getVanDerWaalsTable(a1->type->protons, a2->type->protons);
    if (parameters == NULL) {
        return;
    }
    p->num_static_vanDerWaals++;
    p->vanDerWaals = (struct vanDerWaals **)accumulator(p->vanDerWaals, sizeof(struct vanDerWaals *) * p->num_static_vanDerWaals, 0);
    v = (struct vanDerWaals *)allocate(sizeof(struct vanDerWaals));
    p->vanDerWaals[p->num_static_vanDerWaals - 1] = v;
    v->a1 = a1;
    v->a2 = a2;
    CHECK_VALID_BOND(v);
    v->parameters = parameters;
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
        // v in pm/Dt
	double v = vlen(velocities[a->index]);
        // mass in yg (1e-24 g)
	// save the factor of 1/2 for later, to keep this loop fast
	total += a->mass * v * v;
    }
    // We want energy in attojoules to be consistent with potential energy
    // mass is in units of Dmass kilograms (Dmass = 1e-27, for mass in yg)
    // velocity is in Dx meters per Dt seconds
    // total is in units of (Dmass Dx^2/Dt^2) joules
    // we want attojoules or 1e-18 joules, so we need to multiply by 1e18
    // and we need the factor of 1/2 that we left out of the atom loop
    return total * 0.5 * 1e18 * Dmass * Dx * Dx / (Dt * Dt);
}

// XXX we could turn this into a hashtable if we need the speed
// because of lots of bodies.
static int
findRigidBodyByName(struct part *p, char *name)
{
    int i;
    
    for (i=0; i<p->num_rigidBodies; i++) {
        if (!strcmp(name, p->rigidBodies[i].name)) {
            return i;
        }
    }
    return -1;
}

static int
findStationPointByName(struct part *p, int rigidBodyIndex, char *stationName)
{
    int i;
    struct rigidBody *rb = &p->rigidBodies[rigidBodyIndex];

    for (i=0; i<rb->num_stations; i++) {
        if (!strcmp(stationName, rb->stationNames[i])) {
            return i;
        }
    }
    return -1;
}

static int
findAxisByName(struct part *p, int rigidBodyIndex, char *axisName)
{
    int i;
    struct rigidBody *rb = &p->rigidBodies[rigidBodyIndex];

    for (i=0; i<rb->num_axes; i++) {
        if (!strcmp(axisName, rb->axisNames[i])) {
            return i;
        }
    }
    return -1;
}


void
makeRigidBody(struct part *p, char *name, double mass, double *inertiaTensor, struct xyz position, struct quaternion orientation)
{
    struct rigidBody *rb;
    int i;

    if (findRigidBodyByName(p, name) >= 0) {
        ERROR1("duplicate rigidBody declaration: %s", name);
        p->parseError(p->stream);
        return;
    }
    
    p->num_rigidBodies++;
    p->rigidBodies = (struct rigidBody *)accumulator(p->rigidBodies, p->num_rigidBodies * sizeof(struct rigidBody), 0);
    rb = &p->rigidBodies[p->num_rigidBodies - 1];
    rb->name = name;
    rb->num_stations = 0;
    rb->stations = NULL;
    rb->stationNames = NULL;
    rb->num_axes = 0;
    rb->axes = NULL;
    rb->axisNames = NULL;
    rb->num_attachments = 0;
    rb->attachmentLocations = NULL;
    rb->attachmentAtomIndices = NULL;
    for (i=0; i<6; i++) {
        rb->inertiaTensor[i] = inertiaTensor[i];
    }
    rb->mass = mass;
    rb->position = position;
    vsetc(rb->velocity, 0.0);
    rb->orientation = orientation;
    vsetc(rb->rotation, 0.0);
}

void
makeStationPoint(struct part *p, char *bodyName, char *stationName, struct xyz position)
{
    int i;
    struct rigidBody *rb;

    i = findRigidBodyByName(p, bodyName);
    if (i < 0) {
        ERROR1("rigidBody named (%s) not found", bodyName);
        p->parseError(p->stream);
        return;
    }
    
    rb = &p->rigidBodies[i];
    if (findStationPointByName(p, i, stationName) >= 0) {
        ERROR2("duplicate stationName: %s on rigidBody: %s", stationName, bodyName);
        p->parseError(p->stream);
        return;
    }
    
    rb->num_stations++;
    rb->stations = (struct xyz *)accumulator(rb->stations, rb->num_stations * sizeof (struct xyz), 0);
    rb->stationNames = (char **)accumulator(rb->stationNames, rb->num_stations * sizeof (char *), 0);
    rb->stations[rb->num_stations-1] = position;
    rb->stationNames[rb->num_stations-1] = stationName;
    return;
}

void
makeBodyAxis(struct part *p, char *bodyName, char *axisName, struct xyz orientation)
{
    int i;
    struct rigidBody *rb;

    i = findRigidBodyByName(p, bodyName);
    if (i < 0) {
        ERROR1("rigidBody named (%s) not found", bodyName);
        p->parseError(p->stream);
        return;
    }
    
    rb = &p->rigidBodies[i];
    if (findAxisByName(p, i, axisName) >= 0) {
        ERROR2("duplicate axisName: %s on rigidBody: %s", axisName, bodyName);
        p->parseError(p->stream);
        return;
    }
    
    rb->num_axes++;
    rb->axes = (struct xyz *)accumulator(rb->axes, rb->num_axes * sizeof (struct xyz), 0);
    rb->axisNames = (char **)accumulator(rb->axisNames, rb->num_axes * sizeof (char *), 0);
    rb->axes[rb->num_axes-1] = orientation;
    rb->axisNames[rb->num_axes-1] = axisName;
}

void
makeAtomAttachments(struct part *p, char *bodyName, int atomListLength, int *atomList)
{
    int i;
    int j;
    struct rigidBody *rb;
    struct atom *a;

    i = findRigidBodyByName(p, bodyName);
    if (i < 0) {
        ERROR1("rigidBody named (%s) not found", bodyName);
        p->parseError(p->stream);
        return;
    }
    
    rb = &p->rigidBodies[i];
    if (rb->num_attachments != 0) {
        ERROR1("more than one attachAtoms for body %s", bodyName);
        p->parseError(p->stream);
        return;
    }
    rb->num_attachments = atomListLength;
    rb->attachmentLocations = (struct xyz *)allocate(atomListLength * sizeof(struct xyz));
    rb->attachmentAtomIndices = (int *)allocate(atomListLength * sizeof(int));
    for (j=0; j<atomListLength; j++) {
	a = translateAtomID(p, atomList[j]); BAIL();
        vsetc(rb->attachmentLocations[j], 0.0);
        rb->attachmentAtomIndices[j] = a->index;
    }
}

static struct joint *
newJoint(struct part *p)
{
    struct joint *j;
    
    p->num_joints++;
    p->joints = (struct joint *)accumulator(p->joints, p->num_joints * sizeof (struct joint), 0);
    j = &p->joints[p->num_joints-1];

    j->rigidBody1 = -1;
    j->rigidBody2 = -1;
    j->station1_1 = -1;
    j->station2_1 = -1;
    j->axis1_1 = -1;
    j->axis2_1 = -1;

    return j;
}

static int
requireRigidBody(struct part *p, char *name)
{
    int i = findRigidBodyByName(p, name);
    if (i < 0) {
        ERROR1("no rigid body named %s", name);
        p->parseError(p->stream);
        return 0;
    }
    return i;
}

static int
requireStationPoint(struct part *p, char *bodyName, char *stationName)
{
    int i = findRigidBodyByName(p, bodyName);
    int j;
    
    if (i < 0) {
        ERROR1("no rigid body named %s", bodyName);
        p->parseError(p->stream);
        return 0;
    }
    j = findStationPointByName(p, i, stationName);
    if (j < 0) {
        ERROR2("no station named %s in rigid body %s", stationName, bodyName);
        p->parseError(p->stream);
        return 0;
    }
    return j;
}

static int
requireAxis(struct part *p, char *bodyName, char *axisName)
{
    int i = findRigidBodyByName(p, bodyName);
    int j;
    
    if (i < 0) {
        ERROR1("no rigid body named %s", bodyName);
        p->parseError(p->stream);
        return 0;
    }
    j = findAxisByName(p, i, axisName);
    if (j < 0) {
        ERROR2("no axis named %s in rigid body %s", axisName, bodyName);
        p->parseError(p->stream);
        return 0;
    }
    return j;
}

void
makeBallJoint(struct part *p, char *bodyName1, char *stationName1, char *bodyName2, char *stationName2)
{
    struct joint *j = newJoint(p);

    j->type = JointBall;
    j->rigidBody1 = requireRigidBody(p, bodyName1); BAIL();
    j->station1_1 = requireStationPoint(p, bodyName1, stationName1); BAIL();
    j->rigidBody2 = requireRigidBody(p, bodyName2); BAIL();
    j->station2_1 = requireStationPoint(p, bodyName2, stationName2); BAIL();
}

void
makeHingeJoint(struct part *p, char *bodyName1, char *stationName1, char *axisName1, char *bodyName2, char *stationName2, char *axisName2)
{
    struct joint *j = newJoint(p);

    j->type = JointHinge;
    j->rigidBody1 = requireRigidBody(p, bodyName1); BAIL();
    j->station1_1 = requireStationPoint(p, bodyName1, stationName1); BAIL();
    j->axis1_1 = requireAxis(p, bodyName1, axisName1); BAIL();
    j->rigidBody2 = requireRigidBody(p, bodyName2); BAIL();
    j->station2_1 = requireStationPoint(p, bodyName2, stationName2); BAIL();
    j->axis2_1 = requireAxis(p, bodyName2, axisName2); BAIL();
}

void
makeSliderJoint(struct part *p, char *bodyName1, char *axisName1, char *bodyName2, char *axisName2)
{
    struct joint *j = newJoint(p);

    j->type = JointSlider;
    j->rigidBody1 = requireRigidBody(p, bodyName1); BAIL();
    j->axis1_1 = requireAxis(p, bodyName1, axisName1); BAIL();
    j->rigidBody2 = requireRigidBody(p, bodyName2); BAIL();
    j->axis2_1 = requireAxis(p, bodyName2, axisName2); BAIL();
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
	j->atoms[i] = translateAtomID(p, atomList[i]); BAIL();
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
	j->atoms[i] = translateAtomID(p, id); BAIL();
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
    jigAtomList(p, j, atomListLength, atomList); BAIL();
    for (i=0; i<atomListLength; i++) {
	j->atoms[i]->isGrounded = 1;
        // The following lines test energy conservation of systems
        // with grounds.  Do a dynamics run without these lines,
        // saving the result.  Then comment these lines in and rerun
        // the dynamics run.  Make sure the computed velocities at the
        // beginning of the run are identical.  It's simplest to just
        // do the run at 0 K.  Start with a slightly strained
        // structure to get some motion.  The results should be
        // identical between the two runs.

        //j->atoms[i]->mass *= 100.0;
        //j->atoms[i]->inverseMass = Dt * Dt / (j->atoms[i]->mass * 1e-27);
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
    j->atoms[0] = translateAtomID(p, atomID1); BAIL();
    j->atoms[1] = translateAtomID(p, atomID2); BAIL();
    j->atoms[2] = translateAtomID(p, atomID3); BAIL();
    j->atoms[3] = translateAtomID(p, atomID4); BAIL();
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
    j->atoms[0] = translateAtomID(p, atomID1); BAIL();
    j->atoms[1] = translateAtomID(p, atomID2); BAIL();
    j->atoms[2] = translateAtomID(p, atomID3); BAIL();
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
    j->atoms[0] = translateAtomID(p, atomID1); BAIL();
    j->atoms[1] = translateAtomID(p, atomID2); BAIL();
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
    jigAtomList(p, j, atomListLength, atomList); BAILR(NULL);
    
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
	mass = j->atoms[i]->mass * 1e-27;
	
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
    jigAtomList(p, j, atomListLength, atomList); BAIL();
    
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
printQuaternion(FILE *f, struct quaternion q)
{
    fprintf(f, "(%f i, %f j, %f k, %f)", q.x, q.y, q.z, q.a);
}

void
printInertiaTensor(FILE *f, double *t)
{
    fprintf(f, "/ %14.7e %14.7e %14.7e \\\n", t[0], t[1], t[2]);
    fprintf(f, "| %14s %14.7e %14.7e |\n", "", t[3], t[4]);
    fprintf(f, "\\ %14s %14s %14.7e /\n", "", "", t[5]);
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
    if (b->direction != '?') {
        fprintf(f, " %c", b->direction);
    }
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

static void
printJointType(FILE *f, enum jointType type)
{
    switch (type) {
    case JointBall:
        fprintf(f, "Ball");
        break;
    case JointHinge:
        fprintf(f, "Hinge");
        break;
    case JointSlider:
        fprintf(f, "Slider");
        break;
    default:
        fprintf(f, "*Unknown*");
        break;
    }
}

void
printJoint(FILE *f, struct part *p, struct joint *j)
{
    printJointType(f, j->type);
    fprintf(f, " joint between (%s) and (%s)\n", p->rigidBodies[j->rigidBody1].name, p->rigidBodies[j->rigidBody2].name);
}

void
printRigidBody(FILE *f, struct part *p, struct rigidBody *rb)
{
    int i;
    
    fprintf(f, " rigidBody (%s)\n", rb->name);
    fprintf(f, "  position: ");
    printXYZ(f, rb->position);
    fprintf(f, "\n  orientation: ");
    printQuaternion(f, rb->orientation);
    fprintf(f, "\n  mass: %f\n  inertiaTensor:\n", rb->mass);
    printInertiaTensor(f, rb->inertiaTensor);
    if (rb->num_stations > 0) {
        fprintf(f, "  stations:\n");
        for (i=0; i<rb->num_stations; i++) {
            fprintf(f, "   (%s) ", rb->stationNames[i]);
            printXYZ(f, rb->stations[i]);
            fprintf(f, "\n");
        }
    }
    if (rb->num_axes > 0) {
        fprintf(f, "  axes:\n");
        for (i=0; i<rb->num_axes; i++) {
            fprintf(f, "   (%s) ", rb->axisNames[i]);
            printXYZ(f, rb->axes[i]);
            fprintf(f, "\n");
        }
    }
    if (rb->num_attachments > 0) {
        fprintf(f, "  attached atoms:  ");
        for (i=0; i<rb->num_attachments; i++) {
            printAtomShort(f, p->atoms[rb->attachmentAtomIndices[i]]);
            fprintf(f, " ");
        }
        fprintf(f, "\n");
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
printElectrostatic(FILE *f, struct part *p, struct electrostatic *es)
{
    double len;
    double potential;
    double gradient;
    struct xyz p1;
    struct xyz p2;
    
    if (es != NULL) {
	fprintf(f, " electrostatic ");
	CHECK_VALID_BOND(es);
	printAtomShort(f, es->a1);
	fprintf(f, " ");
	printAtomShort(f, es->a2);
	
	p1 = p->positions[es->a1->index];
	p2 = p->positions[es->a2->index];
	vsub(p1, p2);
	len = vlen(p1);
	
	
	potential = electrostaticPotential(NULL, NULL, es->parameters, len);
	gradient = electrostaticGradient(NULL, NULL, es->parameters, len);
	fprintf(f, " r: %f k: %f, V: %f, dV: %f\n", len, es->parameters->k, potential, gradient);
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
printCumuleneTorsion(FILE *f, struct part *p, struct cumuleneTorsion *t)
{
    NULLPTR(t);
    NULLPTR(t->a1);
    NULLPTR(t->aa);
    NULLPTR(t->ab);
    NULLPTR(t->ay);
    NULLPTR(t->az);
    NULLPTR(t->a2);
    fprintf(f, " cumuleneTorsion ");
    printAtomShort(f, t->a1);
    fprintf(f, " - ");
    printAtomShort(f, t->aa);
    fprintf(f, " = ");
    printAtomShort(f, t->ab);
    fprintf(f, " ... ");
    printAtomShort(f, t->ay);
    fprintf(f, " = ");
    printAtomShort(f, t->az);
    fprintf(f, " - ");
    printAtomShort(f, t->a2);
    fprintf(f, " chain length %d double bonds\n", t->numberOfDoubleBonds);
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

static FILE *whereToPrintHashtableEntries = NULL;

static void
printAtomtypeHashtableEntry(char *symbol, void *value)
{
    struct atomType *at = (struct atomType *)value;

    if (at != NULL) {
        fprintf(whereToPrintHashtableEntries, "   %s(%s)\n", at->name, at->symbol);
    }
}


void
printPart(FILE *f, struct part *p)
{
    int i;
    
    fprintf(f, "part loaded from file %s\n", p->filename);
    whereToPrintHashtableEntries = f;
    fprintf(f, "atomTypes used:\n");
    hashtable_iterate(p->atomTypesUsed, printAtomtypeHashtableEntry);
    for (i=0; i<p->num_atoms; i++) {
	printAtom(f, p, p->atoms[i]);
    }
    for (i=0; i<p->num_bonds; i++) {
	printBond(f, p, p->bonds[i]);
    }
    for (i=0; i<p->num_jigs; i++) {
	printJig(f, p, p->jigs[i]);
    }
    for (i=0; i<p->num_rigidBodies; i++) {
	printRigidBody(f, p, &p->rigidBodies[i]);
    }
    for (i=0; i<p->num_vanDerWaals; i++) {
	printVanDerWaals(f, p, p->vanDerWaals[i]);
    }
    for (i=0; i<p->num_electrostatic; i++) {
	printElectrostatic(f, p, p->electrostatic[i]);
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
    for (i=0; i<p->num_cumuleneTorsions; i++) {
	printCumuleneTorsion(f, p, &p->cumuleneTorsions[i]);
    }
    for (i=0; i<p->num_outOfPlanes; i++) {
	printOutOfPlane(f, p, &p->outOfPlanes[i]);
    }
    for (i=0; i<p->num_joints; i++) {
        printJoint(f, p, &p->joints[i]);
    }
}

/*
 * Local Variables:
 * c-basic-offset: 4
 * tab-width: 8
 * End:
 */
