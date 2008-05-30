// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

#include "simulator.h"

static char const rcsid[] = "$Id$";

static char *
trace_atomID(struct atom *a)
{
  static char buf[16];
  if (a == NULL) {
    return "x";
  }
  if (a->virtualConstructionAtoms != 0) {
    sprintf(buf, "{%d}", a->atomID);
  } else {
    sprintf(buf, "%d", a->atomID);
  }
  return buf;
}

static void
trace_makeBond(struct patternMatch *match, struct bond *b)
{
  char buf[1024];
  char buf1[64];
  struct bondStretch *stretchType;

  sprintf(buf, "# Pattern makeBond: [%d] %s ", match->sequenceNumber, trace_atomID(b->a1));
  strcat(buf, trace_atomID(b->a2));

  stretchType = getBondStretch(b->a1->type->protons,
                               b->a2->type->protons,
                               b->order);

  sprintf(buf1, " %f %f\n", stretchType->ks, stretchType->r0);
  
  strcat(buf, buf1);
  write_traceline(buf);
}

static void
trace_makeVirtualAtom(struct patternMatch *match, struct atom *a)
{
  char buf[1024];
  char buf1[64];

  sprintf(buf, "# Pattern makeVirtualAtom: [%d] %s %d %d ",
          match->sequenceNumber,
          trace_atomID(a),
          a->virtualConstructionAtoms,
          a->virtualFunction);
  strcat(buf, trace_atomID(a->creationParameters.v.virtual1));
  strcat(buf, " ");
  strcat(buf, trace_atomID(a->creationParameters.v.virtual2));
  strcat(buf, " ");
  strcat(buf, trace_atomID(a->creationParameters.v.virtual3));
  strcat(buf, " ");
  strcat(buf, trace_atomID(a->creationParameters.v.virtual4));
  sprintf(buf1, " %f %f %f\n",
          a->creationParameters.v.virtualA,
          a->creationParameters.v.virtualB,
          a->creationParameters.v.virtualC);
  strcat(buf, buf1);
  write_traceline(buf);
}

static void
trace_setStretchType(struct patternMatch *match, struct stretch *s)
{
  char buf[1024];
  char buf1[64];

  sprintf(buf, "# Pattern setStretchType: [%d] %s ", match->sequenceNumber, trace_atomID(s->a1));
  strcat(buf, trace_atomID(s->a2));
  sprintf(buf1, " %f %f\n", s->stretchType->ks, s->stretchType->r0);
  strcat(buf, buf1);
  write_traceline(buf);
}

static void
trace_makeVanDerWaals(struct patternMatch *match, struct atom *a1, struct atom *a2)
{
  char buf[1024];

  sprintf(buf, "# Pattern makeVanDerWaals: [%d] %s ", match->sequenceNumber, trace_atomID(a1));
  strcat(buf, trace_atomID(a2));
  strcat(buf, "\n");
  write_traceline(buf);
}


static void
pam5_requires_gromacs(struct part *p)
{
  if (GromacsOutputBaseName == NULL) {
    ERROR("PAM5 DNA structures must be minimized with GROMACS");
    p->parseError(p->stream);
  }
}

static void
pam3_requires_gromacs(struct part *p)
{
  if (GromacsOutputBaseName == NULL) {
    ERROR("PAM3 DNA structures with electrostatics must be minimized with GROMACS");
    p->parseError(p->stream);
  }
}

// The three vectors from aAx1 to the other three atoms can be thought
// of as the basis for a coordinate system.  We would like that
// coordinate system to be right handed, and we return true if that is
// the case.  If not, swapping aSa and aSb would form a right hand
// system.
static int
isExpectedTwist(struct part *p,
                struct atom *aAx1,
                struct atom *aAx2,
                struct atom *aSa,
                struct atom *aSb)
{
  struct xyz v0;
  struct xyz v1;
  struct xyz v2;
  struct xyz v3;
  struct xyz v1_x_v2;

  if (aAx1->virtualConstructionAtoms ||
      aAx2->virtualConstructionAtoms ||
      aSa->virtualConstructionAtoms ||
      aSb->virtualConstructionAtoms)
  {
    return 0;
  }
  v0 = p->positions[aAx1->index];
  v1 = p->positions[aAx2->index];
  v2 = p->positions[aSa->index];
  v3 = p->positions[aSb->index];
  vsub(v1, v0);
  vsub(v2, v0);
  vsub(v3, v0);
  v2x(v1_x_v2, v1, v2);
  return vdot(v1_x_v2, v3) > 0.0;
}

static int stack_match_initialized = 0;
static double vDax_p[8];
static double vDax_q[8];
static double vDbx_p[8];
static double vDbx_q[8];
static struct atomType *vDa_type[8];
static struct atomType *vDb_type[8];
static double axis_pq;
static struct atomType *vAh5_type;

static struct bondStretch *stretch_5_Pl_Ss_3;
static struct bondStretch *stretch_5_Ss_Pl_3;
static struct bendData *bend_Gv_Ss_Pl_5;

/*
 The source frame is a rectalinear frame (basis vectors are
 orthonormal).  The origin sits on the central axis of the DNA duplex,
 at the location which would be occupied by an Ax3 pseudo-atom.
 Positive X points towards the Gv5 major groove pseudo atom.  Positive
 Y is orthogonal to X, in the plane of the two Ss5 pseudo atoms, and on
 the side of the Ss5 pseudo atom which is closer to it's brother in the
 neighboring base pair.

 In the neighboring base pair, this frame would be rotated around Z
 (based on the duplex twist), and rotated 180 degrees around X, so the
 Z axes of the neighboring frames are anti-parallel.

 The destination frame is neither orthogonal nor normalized.  The
 origin is at the Gv5 pseudo atom.  The basis vectors will be called P
 and Q.  Each extends from the origin to one of the Ss5 pseudo atoms in
 the same base pair.  P in the negative Y direction, and Q in the
 positive Y direction.

   Q
    \
     \
    y \
    ox O
      /
     /
    /
   P

  or, after translating the origins to be coincident:

   Q
    \  y
     \ |
      \|
       O--x
      /
     /
    /
   P

 x_o is the x shift of the origin
 x_g is the negative of the x coordinate of q
 y_m is the y coordinate of q
 x and y are the source frame coordinates
 *p and *q are the destination frame coordinates
*/
static void
changeBasis(double x_o, double x_g, double y_m, double x, double y, double *p, double *q)
{
  x -= x_o;

  *p = x * -0.5/x_g + y * -0.5/y_m ;
  *q = x * -0.5/x_g + y *  0.5/y_m ;
}

static void
init_stack_match(void)
{
  int i;
  char buf[256];
  char *strutName;
  struct patternParameter *param;
  double r0;
  double ks;
  double x_o;
  double x_g;
  double y_m;
  double vDax;
  double vDay;
  double vDbx;
  double vDby;

  if (stack_match_initialized) {
    return;
  }
  param = getPatternParameter("PAM5:basis-x_o"); BAIL();
  x_o = param->value;
  param = getPatternParameter("PAM5:basis-x_g"); BAIL();
  x_g = param->value;
  param = getPatternParameter("PAM5:basis-y_m"); BAIL();
  y_m = param->value;

  vAh5_type = getAtomTypeByName("vAh5");
  changeBasis(x_o, x_g, y_m, 0.0, 0.0, &axis_pq, &axis_pq);
  
  for (i=0; i<8 && i<numStruts; i++) {
    sprintf(buf, "strut-%d", i+1);
    param = getPatternParameter(buf); BAIL();
    strutName = param->stringValue;
    
    sprintf(buf, "vDa%s", strutName);
    vDa_type[i] = getAtomTypeByName(buf);
    sprintf(buf, "vDb%s", strutName);
    vDb_type[i] = getAtomTypeByName(buf);
    
    sprintf(buf, "PAM5-Stack:vDa%s-x", strutName);
    param = getPatternParameter(buf); BAIL();
    vDax = param->value;
    sprintf(buf, "PAM5-Stack:vDa%s-y", strutName);
    param = getPatternParameter(buf); BAIL();
    vDay = param->value;
    changeBasis(x_o, x_g, y_m, vDax, vDay, &vDax_p[i], &vDax_q[i]);
    sprintf(buf, "PAM5-Stack:vDb%s-x", strutName);
    param = getPatternParameter(buf); BAIL();
    vDbx = param->value;
    sprintf(buf, "PAM5-Stack:vDb%s-y", strutName);
    param = getPatternParameter(buf); BAIL();
    vDby = -param->value;
    changeBasis(x_o, x_g, y_m, vDbx, vDby, &vDbx_p[i], &vDbx_q[i]);
  }
  param = getPatternParameter("PAM5:5-Pl-Ss-3_r0"); BAIL();
  r0 = param->value; // pm
  param = getPatternParameter("PAM5:5-Pl-Ss-3_ks"); BAIL();
  ks = param->value; // N/m
  stretch_5_Pl_Ss_3 = newBondStretch("5-Pl-Ss-3", ks, r0, 1.0, -1.0, -1.0, 9, 1);

  param = getPatternParameter("PAM5:5-Ss-Pl-3_r0"); BAIL();
  r0 = param->value; // pm
  param = getPatternParameter("PAM5:5-Ss-Pl-3_ks"); BAIL();
  ks = param->value; // N/m
  stretch_5_Ss_Pl_3 = newBondStretch("5-Ss-Pl-3", ks, r0, 1.0, -1.0, -1.0, 9, 1);

  bend_Gv_Ss_Pl_5 = newBendData("Gv-Ss-Pl-5", 0.0, 0.0, 9);

  stack_match_initialized = 1;
}

static void
pam5_basepair_match(struct patternMatch *match)
{
  struct atom *aS1 = match->p->atoms[match->atomIndices[1]];
  struct atom *aS2 = match->p->atoms[match->atomIndices[2]];
  struct bond *bond;

  pam5_requires_gromacs(match->p); BAIL();
  init_stack_match(); BAIL();
  bond = makeBond(match->p, aS1, aS2, '1');
  queueBond(match->p, bond);
  trace_makeBond(match, bond);
  //printMatch(match);
}

static void
pam5_stack_match(struct patternMatch *match)
{
  struct atom *aGv1 = match->p->atoms[match->atomIndices[0]];
  struct atom *aGv2 = match->p->atoms[match->atomIndices[1]];
  struct atom *aS1a = match->p->atoms[match->atomIndices[2]];
  struct atom *aS1b = match->p->atoms[match->atomIndices[3]];
  struct atom *aS2a = match->p->atoms[match->atomIndices[4]];
  struct atom *aS2b = match->p->atoms[match->atomIndices[5]];
  struct atom *vA;
  struct atom *vB;
  struct bond *bond;
  int i;
  
  pam5_requires_gromacs(match->p); BAIL();
  init_stack_match(); BAIL();
  
  // S1a    S2b
  //  |      |
  // Gv1----Gv2
  //  |      |
  // S1b    S2a
  if (!isExpectedTwist(match->p, aGv1, aGv2, aS1a, aS1b)) {
    aS1a = match->p->atoms[match->atomIndices[3]];
    aS1b = match->p->atoms[match->atomIndices[2]];
  }
  if (!isExpectedTwist(match->p, aGv2, aGv1, aS2a, aS2b)) {
    aS2a = match->p->atoms[match->atomIndices[5]];
    aS2b = match->p->atoms[match->atomIndices[4]];
  }
  // Atoms are now in canonical orientations.  The twist is such that
  // the S1a-S2a distance is greater than the S1b-S2b distance in
  // BDNA.
  for (i=0; i<8 && i < numStruts; i++) {
    vA = makeVirtualAtom(vDa_type[i], sp3, 3, 1,
                         aGv1, aS1a, aS1b, NULL,
                         vDax_p[i], vDax_q[i], 0.0);
    vB = makeVirtualAtom(vDb_type[i], sp3, 3, 1,
                         aGv2, aS2a, aS2b, NULL,
                         vDbx_p[i], vDbx_q[i], 0.0);
    bond = makeBond(match->p, vA, vB, '1');
    queueAtom(match->p, vA);
    trace_makeVirtualAtom(match, vA);
    queueAtom(match->p, vB);
    trace_makeVirtualAtom(match, vB);
    queueBond(match->p, bond);
    trace_makeBond(match, bond);
  }
  //printMatch(match);
}

static void
pam5_basepair_handle_match(struct patternMatch *match)
{
  struct atom *aAh = match->p->atoms[match->atomIndices[0]];
  struct atom *aGv = match->p->atoms[match->atomIndices[1]];
  struct atom *aS1 = match->p->atoms[match->atomIndices[2]];
  struct atom *aS2 = match->p->atoms[match->atomIndices[3]];
  struct atom *vA;
  struct bond *bond;
  
  pam5_requires_gromacs(match->p); BAIL();
  init_stack_match(); BAIL();
  
  // S1
  //  |
  // Gv----Ah
  //  |
  // S2
  if (aAh->isGrounded) {
    vA = makeVirtualAtom(vAh5_type, sp3, 3, 1,
                         aGv, aS1, aS2, NULL,
                         axis_pq, axis_pq, 0.0);
    
    bond = makeBond(match->p, vA, aAh, '1');
    queueAtom(match->p, vA);
    trace_makeVirtualAtom(match, vA);
    queueBond(match->p, bond);
    trace_makeBond(match, bond);
  }
  //printMatch(match);
}

// Sets the phosphate-sugar bond type differently based on the bond
// direction.  This allows the phosphate to be closer to one sugar
// than the other, based on the strand direction.
static void
pam5_phosphate_sugar_match(struct patternMatch *match) 
{
  struct part *p = match->p;
  struct atom *aPl = p->atoms[match->atomIndices[0]];
  struct atom *aSs = p->atoms[match->atomIndices[1]];
  struct bond *b = getBond(p, aPl, aSs); BAIL();
  struct stretch *s = getStretch(p, aPl, aSs); BAIL();
  int reverse;

  pam5_requires_gromacs(match->p); BAIL();
  init_stack_match(); BAIL();

  switch (b->direction) {
  case 'F':
    reverse = (b->a1 == aSs);
    break;
  case 'R':
    reverse = (b->a1 == aPl);
    break;
  default:
    ERROR2("pam5_phosphate_sugar_match: bond between ids %d and %d has no direction", aPl->atomID, aSs->atomID);
    p->parseError(p->stream);
    return;
  }
  s->stretchType = reverse ? stretch_5_Ss_Pl_3 : stretch_5_Pl_Ss_3 ;
  trace_setStretchType(match, s);
  //printMatch(match);
}

// Creates the Pl-Pl interaction, which replaces the Pl-Ss-Pl bend
// term.
static void
pam5_phosphate_phosphate_match(struct patternMatch *match) 
{
  struct part *p = match->p;
  struct atom *aPl1 = p->atoms[match->atomIndices[0]];
  struct atom *aPl2 = p->atoms[match->atomIndices[2]];
  struct bond *bond;
  
  pam5_requires_gromacs(p); BAIL();

  bond = makeBond(p, aPl1, aPl2, '1');
  queueBond(p, bond);
  trace_makeBond(match, bond);
  //printMatch(match);
}

// Creates the Gv-Pl interaction, which replaces the Gv-Ss-Pl bend
// term.  Only do this on the 5' side.
static void
pam5_groove_phosphate_match(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aGv = p->atoms[match->atomIndices[0]];
  struct atom *aSs = p->atoms[match->atomIndices[1]];
  struct atom *aPl = p->atoms[match->atomIndices[2]];
  struct bond *b = getBond(p, aPl, aSs); BAIL();
  struct bond *bond;
  struct bend *bend;
  int reverse;
  char order;

  pam5_requires_gromacs(p); BAIL();

  switch (b->direction) {
  case 'F':
    reverse = (b->a1 == aSs);
    break;
  case 'R':
    reverse = (b->a1 == aPl);
    break;
  default:
    ERROR2("pam5_phosphate_sugar_match: bond between ids %d and %d has no direction", aPl->atomID, aSs->atomID);
    p->parseError(p->stream);
    return;
  }

  if (reverse) {
    order = '2';
  } else {
    order = '1';
    bend = getBend(p, aGv, aSs, aPl);
    bend->bendType = bend_Gv_Ss_Pl_5;
  }
  
  bond = makeBond(p, aPl, aGv, order);
  queueBond(p, bond);
  trace_makeBond(match, bond);
  //printMatch(match);
}

static void
pam5_crossover_match(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aP5 = p->atoms[match->atomIndices[5]];
  struct atom *aP7 = p->atoms[match->atomIndices[7]];
  struct atom *aP8 = p->atoms[match->atomIndices[8]];
  struct atom *aP10 = p->atoms[match->atomIndices[10]];

  // P7    P5    P2    P8    P10
  //   \  /  \  /  \  /  \  /
  //    S6    S1    S3    S9
  //          |     |
  //          G0 xx G4
  //
  // Note that since groove G0 is not bonded to G4, they are in
  // different duplexes, which is what makes this a crossover.  Since
  // we've created direct bonds between neighboring phosphates, the
  // only non-bonded interaction which is not automatically excluded
  // is P7-P10.  We want to add P7-P8, P5-P10, and P5-P8.

  makeVanDerWaals(p, aP7->atomID, aP8->atomID);
  trace_makeVanDerWaals(match, aP7, aP8);
  makeVanDerWaals(p, aP5->atomID, aP10->atomID);
  trace_makeVanDerWaals(match, aP5, aP10);
  makeVanDerWaals(p, aP5->atomID, aP8->atomID);
  trace_makeVanDerWaals(match, aP5, aP8);
  //printMatch(match);
}

static void
pam5_full_crossover_match(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aP3 = p->atoms[match->atomIndices[3]];
  struct atom *aP8 = p->atoms[match->atomIndices[8]];
  struct bond *bond;

  //  G0--G1
  //  |   |
  //  S9  S2
  //  |   |
  //  P8  P3
  //  |   |
  //  S7  S4
  //  |   |
  //  G6--G5
  
  bond = makeBond(p, aP3, aP8, '2');
  queueBond(p, bond);
  trace_makeBond(match, bond);
  //printMatch(match);
}

static void
pam3_crossover_match(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aS1 = p->atoms[match->atomIndices[1]];
  struct atom *aS2 = p->atoms[match->atomIndices[2]];
  struct atom *aS4 = p->atoms[match->atomIndices[4]];
  struct atom *aS5 = p->atoms[match->atomIndices[5]];
  struct atom *aS6 = p->atoms[match->atomIndices[6]];
  struct atom *aS7 = p->atoms[match->atomIndices[7]];

  // S5--S4--S1--S2--S6--S7
  //         |   |
  //         A0xxA3
  //
  // Note that since Axis Z0 is not bonded to A3, they are in
  // different duplexes, which is what makes this a crossover.  Since
  // there are direct bonds between neighboring sugars, the only
  // non-bonded interactions which are not automatically excluded are
  // S4-S7 and S5-S6.  We want to add S1-S7, S2-S5, and S4-S6.

  if (EnableElectrostatic) {
    makeVanDerWaals(p, aS1->atomID, aS7->atomID);
    trace_makeVanDerWaals(match, aS1, aS7);
    makeVanDerWaals(p, aS2->atomID, aS5->atomID);
    trace_makeVanDerWaals(match, aS2, aS5);
    makeVanDerWaals(p, aS4->atomID, aS6->atomID);
    trace_makeVanDerWaals(match, aS4, aS6);
  }
}

static void
pam3_any_match(struct patternMatch *match)
{
  if (EnableElectrostatic) {
    pam3_requires_gromacs(match->p);
  }
}

void
createPam5Patterns(void)
{
  struct compiledPatternTraversal *t[15];
  struct compiledPatternAtom *a[15];

  if (VanDerWaalsCutoffRadius < 0.0) {
    // this indicates that the model has no pam5 atoms
    return;
  }
  stack_match_initialized = 0;

  a[0] = makePatternAtom(0, "P5G");
  a[1] = makePatternAtom(1, "P5S");
  a[2] = makePatternAtom(2, "P5S");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[0], a[2], '1');
  makePattern("PAM5-basepair", pam5_basepair_match, 3, 2, t);

  a[0] = makePatternAtom(0, "P5G");
  a[1] = makePatternAtom(1, "P5G");
  a[2] = makePatternAtom(2, "P5S");
  a[3] = makePatternAtom(3, "P5S");
  a[4] = makePatternAtom(4, "P5S");
  a[5] = makePatternAtom(5, "P5S");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[0], a[2], '1');
  t[2] = makeTraversal(a[0], a[3], '1');
  t[3] = makeTraversal(a[1], a[4], '1');
  t[4] = makeTraversal(a[1], a[5], '1');
  makePattern("PAM5-stack", pam5_stack_match, 6, 5, t);

  a[0] = makePatternAtom(0, "P5P");
  a[1] = makePatternAtom(1, "P5S");
  t[0] = makeTraversal(a[0], a[1], '1');
  makePattern("PAM5-phosphate-sugar", pam5_phosphate_sugar_match, 2, 1, t);

  a[0] = makePatternAtom(0, "P5P");
  a[1] = makePatternAtom(1, "P5S");
  a[2] = makePatternAtom(2, "P5P");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  makePattern("PAM5-phosphate-phosphate", pam5_phosphate_phosphate_match, 3, 2, t);

  a[0] = makePatternAtom(0, "P5G");
  a[1] = makePatternAtom(1, "P5S");
  a[2] = makePatternAtom(2, "P5P");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  makePattern("PAM5-groove-phosphate", pam5_groove_phosphate_match, 3, 2, t);

  a[0] = makePatternAtom(0, "P5G");
  a[1] = makePatternAtom(1, "P5S");
  a[2] = makePatternAtom(2, "P5P");
  a[3] = makePatternAtom(3, "P5S");
  a[4] = makePatternAtom(4, "P5G");
  a[5] = makePatternAtom(5, "P5P");
  a[6] = makePatternAtom(6, "P5S");
  a[7] = makePatternAtom(7, "P5P");
  a[8] = makePatternAtom(8, "P5P");
  a[9] = makePatternAtom(9, "P5S");
  a[10] = makePatternAtom(10, "P5P");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  t[2] = makeTraversal(a[2], a[3], '1');
  t[3] = makeTraversal(a[3], a[4], '1');
  t[4] = makeTraversal(a[4], a[0], '0');
  t[5] = makeTraversal(a[1], a[5], '1');
  t[6] = makeTraversal(a[5], a[6], '1');
  t[7] = makeTraversal(a[6], a[7], '1');
  t[8] = makeTraversal(a[3], a[8], '1');
  t[9] = makeTraversal(a[8], a[9], '1');
  t[10] = makeTraversal(a[9], a[10], '1');
  makePattern("PAM5-crossover", pam5_crossover_match, 11, 11, t);

  a[0] = makePatternAtom(0, "P5G");
  a[1] = makePatternAtom(1, "P5G");
  a[2] = makePatternAtom(2, "P5S");
  a[3] = makePatternAtom(3, "P5P");
  a[4] = makePatternAtom(4, "P5S");
  a[5] = makePatternAtom(5, "P5G");
  a[6] = makePatternAtom(6, "P5G");
  a[7] = makePatternAtom(7, "P5S");
  a[8] = makePatternAtom(8, "P5P");
  a[9] = makePatternAtom(9, "P5S");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  t[2] = makeTraversal(a[2], a[3], '1');
  t[3] = makeTraversal(a[3], a[4], '1');
  t[4] = makeTraversal(a[4], a[5], '1');
  t[5] = makeTraversal(a[5], a[6], '1');
  t[6] = makeTraversal(a[6], a[7], '1');
  t[7] = makeTraversal(a[7], a[8], '1');
  t[8] = makeTraversal(a[8], a[9], '1');
  t[9] = makeTraversal(a[9], a[0], '1');
  makePattern("PAM5-full-crossover", pam5_full_crossover_match, 10, 10, t);

  a[0] = makePatternAtom(0, "Ah5");
  a[1] = makePatternAtom(1, "P5G");
  a[2] = makePatternAtom(2, "P5S");
  a[3] = makePatternAtom(3, "P5S");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  t[2] = makeTraversal(a[1], a[3], '1');
  makePattern("PAM5-basepair-handle", pam5_basepair_handle_match, 4, 3, t);

  a[0] = makePatternAtom(0, "PAM3");
  t[0] = makeTraversal(a[0], a[0], '?'); // how to match a bare atom
  makePattern("PAM3-any", pam3_any_match, 1, 1, t);
  
  a[0] = makePatternAtom(0, "Ax3");
  a[1] = makePatternAtom(1, "Ss3");
  a[2] = makePatternAtom(2, "Ss3");
  a[3] = makePatternAtom(3, "Ax3");
  a[4] = makePatternAtom(4, "Ss3");
  a[5] = makePatternAtom(5, "Ss3");
  a[6] = makePatternAtom(6, "Ss3");
  a[7] = makePatternAtom(7, "Ss3");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  t[2] = makeTraversal(a[2], a[3], '1');
  t[3] = makeTraversal(a[3], a[0], '0');
  t[4] = makeTraversal(a[1], a[4], '1');
  t[5] = makeTraversal(a[4], a[5], '1');
  t[6] = makeTraversal(a[2], a[6], '1');
  t[7] = makeTraversal(a[6], a[7], '1');
  makePattern("PAM3-crossover", pam3_crossover_match, 8, 8, t);
}
