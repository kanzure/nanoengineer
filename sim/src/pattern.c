// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

#include "simulator.h"

static char const rcsid[] = "$Id$";

static int debugMatch = 0;

static struct patternMatch *
makeMatch(struct part *part, struct compiledPattern *pattern)
{
  struct patternMatch *match;
  int i;

  match = (struct patternMatch *)allocate(sizeof(struct patternMatch));
  match->patternName = pattern->name;
  match->p = part;
  match->numberOfAtoms = pattern->numberOfAtoms;
  match->atomIndices = (int *)allocate(sizeof(int) * pattern->numberOfAtoms);
  match->introducedAtTraversal =
    (int *)allocate(sizeof(int) * pattern->numberOfAtoms);
  for (i=pattern->numberOfAtoms-1; i>=0; i--) {
    match->atomIndices[i] = -1;
    match->introducedAtTraversal[i] = pattern->numberOfTraversals + 1;
  }
  return match;
}

static void
destroyMatch(struct patternMatch *match)
{
  if (match == NULL) {
    return;
  }
  if (match->atomIndices != NULL) {
    free(match->atomIndices);
    match->atomIndices = NULL;
  }
  if (match->introducedAtTraversal != NULL) {
    free(match->introducedAtTraversal);
    match->introducedAtTraversal = NULL;
  }
  free(match);
}

static void
printMatch(struct patternMatch *match)
{
  int i;
  
  printf("match for pattern %s\n", match->patternName);
  for (i=0; i<match->numberOfAtoms; i++) {
    //printf("pattern index: %d, atomid: %d\n", i, match->atomIndices[i]);
    printAtom(stdout, match->p, match->p->atoms[match->atomIndices[i]]);
  }
}

// debug routine
static void
printMatchStatus(struct patternMatch *match,
                 char *label,
                 int traversalIndex,
                 struct atom *matchedAtom)
{
  int i;
  int index;
  struct atom *atom;

  if (debugMatch == 0) {
    return;
  }
  printf("%s%s[%d]: ", label, match->patternName, traversalIndex);
  for (i=0; i<match->numberOfAtoms; i++) {
    if (match->introducedAtTraversal[i] <= traversalIndex) {
      index = match->atomIndices[i];
      if (index < 0 || index > match->p->num_atoms) {
        printf("{%d}", index);
      } else {
        atom = match->p->atoms[match->atomIndices[i]];
        if (atom == matchedAtom) {
          printf("***");
        }
        printAtomShort(stdout, atom);
      }
      printf("[%d] ", match->introducedAtTraversal[i]);
    }
    else {
      printf("{{%d, %d}} ",
             match->atomIndices[i], match->introducedAtTraversal[i]);
    }
  }
  printf("\n");
}

// This routine erases the state of any matches past the indicated
// point in the iteration through the pattern.  While we are iterating
// through possibilities for atom a (which==1) at the start of each
// loop, we must forget the state of atom b (which==2).
static int
resetMatchForThisTraversal(struct patternMatch *match,
                           int traversalIndex,
                           struct compiledPatternTraversal *traversal,
                           int which)
{
  int i;

  if (which == 1) {
    i = traversal->a->idInPattern;
  } else {
    i = traversal->b->idInPattern;
  }
  if (match->introducedAtTraversal[i] >= traversalIndex) {
    if (debugMatch) {
      printf("reset traversal %d, which %d, atom %d; ",
             traversalIndex, which, i);
    }
    match->atomIndices[i] = -1;
    match->introducedAtTraversal[i] = traversalIndex + 1;
  } else if (debugMatch) {
    printf("did not reset traversal %d, which %d, atom %d; ",
           traversalIndex, which, i);
  }
  if (debugMatch) {
    printMatchStatus(match, "", traversalIndex, NULL);
  }
  return 1;
}

static int
atomIsType(struct atom *a, struct atomType *type) 
{
  struct atomType *atype = a->type;
  
  while (atype != NULL) {
    if (atype == type) {
      return 1;
    }
    atype = atype->parent;
  }
  
  return 0;
}

// Returns true if the indicated atom (id) has not yet appeared in the
// match.  This keeps a pattern from matching the same atom twice.
static int
atomNotUsed(struct patternMatch *match, int traversalIndex, int id)
{
  int trial;
  int i;
  
  trial = match->atomIndices[id];
  for (i=match->numberOfAtoms-1; i>=0; i--) {
    if (i != id &&
        match->introducedAtTraversal[i] <= traversalIndex &&
        match->atomIndices[i] == trial)
    {
      return 0;
    }
  }
  return 1;
}

// Returns the next atom to match at the given position in the
// pattern, or NULL if the possibilities have been exhausted.  If an
// atom was fixed at a previous traversal (earlier in the matching
// process), this routing will return that atom on the first call, and
// NULL on the second call.  That state is kept in callCount.
static struct atom *
matchOneAtom(struct patternMatch *match,
             struct compiledPattern *pattern,
             struct compiledPatternAtom *patternAtom,
             int traversalIndex,
             int *callCount)
{
  int id = patternAtom->idInPattern;
  struct part *p = match->p;
  struct atom *a;
  
  if (match->introducedAtTraversal[id] < traversalIndex) {
    // this atom has been fixed at an earlier traversal
    if ((*callCount)++ == 0) {
      // first call at this level, return fixed atom
      a = match->p->atoms[match->atomIndices[id]];
      if (debugMatch) {
        printMatchStatus(match, "firstfixed: ", traversalIndex, a);
      }
      return a;
    }
    // later call at this level, no more possible matches
    return NULL;
  }
  if (match->introducedAtTraversal[id] > traversalIndex) {
    // haven't matched this atom yet, start search at top
    match->atomIndices[id] = -1;
    match->introducedAtTraversal[id] = traversalIndex;
  }
  while (++(match->atomIndices[id]) < p->num_atoms) {
    if (atomNotUsed(match, traversalIndex, id)) {
      a = p->atoms[match->atomIndices[id]];
      if (atomIsType(a, patternAtom->type)) {
        if (debugMatch) {
          printMatchStatus(match, "searched: ", traversalIndex, a);
        }
        return a;
      }
    }
  }
  return NULL;
}

// Returns true if the specified targetAtom matches at the given point
// in the pattern.  The atom may have been fixed at a previous
// traversal, in which case we must be looking at the same atom.  If
// this is a new atom at this traversal, we fix it here if the type is
// correct.
static int
matchSpecificAtom(struct patternMatch *match,
                  struct compiledPatternAtom *patternAtom,
                  struct atom *targetAtom,
                  int traversalIndex)
{
  int id;
  
  if (atomIsType(targetAtom, patternAtom->type)) {
    id = patternAtom->idInPattern;
    if (match->introducedAtTraversal[id] > traversalIndex) {
      match->atomIndices[id] = targetAtom->index;
      if (atomNotUsed(match, traversalIndex, id)) {
        match->introducedAtTraversal[id] = traversalIndex;
        if (debugMatch) {
          printMatchStatus(match, "specific: ", traversalIndex, targetAtom);
        }
        return 1;
      }
      return 0;
    }
    if (match->atomIndices[id] == targetAtom->index) {
      if (debugMatch) {
        printMatchStatus(match, "fixed specific: ", traversalIndex, targetAtom);
      }
      return 1;
    }
  }
  return 0;
}

static struct hashtable *matchSet = NULL;

static int
integerSortCompare(const void *a, const void *b)
{
  return *(int *)a - *(int *)b;
}

// Returns true if the matched set of atoms has already been found
// while matching this pattern.  Keeps symmetric patterns from
// matching more than once on the same set of atoms.  The set of
// matched atoms is canonicalized (by sorting the numerical ids),
// turned into a string, and used as a hashtable key.
static int
checkForDuplicateMatch(struct patternMatch *match)
{
  int i;
  int len;
  int *atomIndices = (int *)allocate(sizeof(int) * match->numberOfAtoms);
  char *buf1;
  char buf2[20];
  int dup;

  for (i=match->numberOfAtoms-1; i>=0; i--) {
    atomIndices[i] = match->atomIndices[i];
  }
  qsort(atomIndices, match->numberOfAtoms, sizeof(int), integerSortCompare);
  len = 0;
  for (i=match->numberOfAtoms-1; i>=0; i--) {
    sprintf(buf2, "%d.", atomIndices[i]);
    len += strlen(buf2);
  }
  buf1 = (char *)allocate(sizeof(char) * (len + 1));
  buf1[0] = '\0';
  for (i=match->numberOfAtoms-1; i>=0; i--) {
    sprintf(buf2, "%d.", atomIndices[i]);
    strcat(buf1, buf2);
  }
  dup = hashtable_get(matchSet, buf1) != NULL;
  if (!dup) {
    hashtable_put(matchSet, buf1, (void *)1);
  }
  return !dup;
}

// Matches one traversal in a compiled pattern.  See
// http://www.nanoengineer-1.net/mediawiki/index.php?title=User:Emessick/Molecular_pattern_matching
// for a description of the algorithm.  Basically, each traversal
// represents an expansion of the set of criteria for matching the
// pattern.  The first traversal establishes a seed, and later
// traversals add to the seed, crystallizing the pattern around it.
// The crystallization only proceeds in the presence of a matching
// target structure.  If the crystal grows to the end of the traversal
// list, the whole pattern matched.
static void
matchOneTraversal(struct patternMatch *match,
                  struct compiledPattern *pattern,
                  int traversalIndex)
{
  struct atom *atomA;
  struct atom *atomB;
  int atomACallCount = 0;
  int atomBCallCount = 0;
  int isBonded;
  int bondNumber;
  int atomsAreTheSame;
  struct bond *bond;
  struct compiledPatternTraversal *traversal;
  
  if (traversalIndex >= pattern->numberOfTraversals) {
    if (debugMatch) {
      printf("found match, checking for duplicate\n");
      printMatch(match);
    }
    if (checkForDuplicateMatch(match)) {
      pattern->matchFunction(match);
    }
    return;
  }
  traversal = pattern->traversals[traversalIndex];
  resetMatchForThisTraversal(match, traversalIndex, traversal, 1);
  if (debugMatch) {
    printf("%s[%d]\n", match->patternName, traversalIndex);
  }
  atomsAreTheSame = traversal->a == traversal->b;
  while ((atomsAreTheSame ||
          resetMatchForThisTraversal(match, traversalIndex, traversal, 2)) &&
         (atomA = matchOneAtom(match,
                               pattern,
                               traversal->a,
                               traversalIndex,
                               &atomACallCount)) != NULL) {
    if (traversal->a == traversal->b) {
      // introducing new atom, bond order doesn't matter
      matchOneTraversal(match, pattern, traversalIndex+1); BAIL();
      continue;
    }
    // build list of atoms bonded to a
    if (traversal->bondOrder == '0') {
      // a must not be bonded to b
      while ((atomB = matchOneAtom(match,
                                   pattern,
                                   traversal->b,
                                   traversalIndex,
                                   &atomBCallCount)) != NULL) {
        isBonded = 0;
        for (bondNumber=atomA->num_bonds-1; bondNumber>=0; bondNumber--) {
          bond = atomA->bonds[bondNumber];
          if ((atomA == bond->a1 && atomB == bond->a2) ||
              (atomA == bond->a2 && atomB == bond->a1))
          {
            isBonded = 1;
            break;
          }
        }
        if (!isBonded) {
          matchOneTraversal(match, pattern, traversalIndex+1); BAIL();
        }
      }
      continue;
    }
    for (bondNumber=atomA->num_bonds-1; bondNumber>=0; bondNumber--) {
      bond = atomA->bonds[bondNumber];
      if (bond->order == traversal->bondOrder) {
        if (atomA == bond->a1) {
          atomB = bond->a2;
        } else {
          atomB = bond->a1;
        }
        if (debugMatch) {
          printf("[%d] bond %d checking ", traversalIndex, bondNumber);
          printAtomShort(stdout, atomB);
          printf("\n");
        }
        if (matchSpecificAtom(match, traversal->b, atomB, traversalIndex)) {
          matchOneTraversal(match, pattern, traversalIndex+1); BAIL();
        }
        resetMatchForThisTraversal(match, traversalIndex, traversal, 2);
      }
    }
  }
}

// Housekeeping that has to happen around the recursive
// matchOneTraversal() routine.
static void
matchPartToPattern(struct part *part, struct compiledPattern *pattern)
{
  struct patternMatch *match;

  match = makeMatch(part, pattern);
  matchSet = hashtable_new(64);
  matchOneTraversal(match, pattern, 0);
  destroyMatch(match);
  hashtable_destroy(matchSet, NULL);
  matchSet = NULL;
  BAIL();
  addQueuedComponents(part);
}


static struct atomType *unmatchable = NULL;

// Creates an atomType which cannot represent any atoms.  Used only if
// a pattern references an unknown type.  In that case, the pattern
// can never match.
static void
makeUnmatchableType(void)
{
  if (unmatchable != NULL) {
    return;
  }
  unmatchable = (struct atomType *)allocate(sizeof(struct atomType));
  unmatchable->protons = -1;
  unmatchable->group = -1;
  unmatchable->period = -1;
  unmatchable->name = "error";
  unmatchable->symbol = "error";
  unmatchable->mass = -1;
  unmatchable->vanDerWaalsRadius = -1;
  unmatchable->e_vanDerWaals = -1;
  unmatchable->n_bonds = -1;
  unmatchable->covalentRadius = -1;
  unmatchable->charge = 0;
  unmatchable->refCount = 1;
}


static struct compiledPatternAtom *
makePatternAtom(int id, char *type)
{
  struct compiledPatternAtom *a;
  struct atomType *t = getAtomTypeByName(type);
  if (t == NULL) {
    fprintf(stderr, "unknown atom type: %s\n", type);
    t = unmatchable;
  }
  a = (struct compiledPatternAtom *)
    allocate(sizeof(struct compiledPatternAtom));
  a->type = t;
  a->idInPattern = id;
  return a;
}

static struct compiledPatternTraversal *
makeTraversal(struct compiledPatternAtom *a,
              struct compiledPatternAtom *b,
              char bondOrder)
{
  struct compiledPatternTraversal *t;

  t = (struct compiledPatternTraversal *)
    allocate(sizeof(struct compiledPatternTraversal));
  t->a = a;
  t->b = b;
  t->bondOrder = bondOrder;
  return t;
}

static struct compiledPattern *
makePattern(char *name,
            void (*matchFunction)(struct patternMatch *match),
            int numAtoms,
            int numTraversals,
            struct compiledPatternTraversal **traversals)
{
  int i;
  struct compiledPattern *pat;

  pat = (struct compiledPattern *)allocate(sizeof(struct compiledPattern));
  pat->name = name;
  pat->matchFunction = matchFunction;
  pat->numberOfAtoms = numAtoms;
  pat->numberOfTraversals = numTraversals;
  pat->traversals = (struct compiledPatternTraversal **)
    allocate(sizeof(struct compiledPatternTraversal *) * numTraversals);
  for (i=0; i<numTraversals; i++) {
    pat->traversals[i] = traversals[i];
  }
  return pat;
}

/*
static struct bendData *pam5_Ax_Ax_Ss_low = NULL;
static struct bendData *pam5_Ax_Ax_Ss_high = NULL;

static void
pam5_ring_match(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aA1 = p->atoms[match->atomIndices[0]];
  struct atom *aA2 = p->atoms[match->atomIndices[1]];
  struct atom *aS2 = p->atoms[match->atomIndices[2]];
  struct atom *aP  = p->atoms[match->atomIndices[3]];
  struct atom *aS1 = p->atoms[match->atomIndices[4]];
  struct atom *aE;
  struct bond *b = getBond(p, aP, aS1);
  struct atom *t;
  struct bend *bend1;
  struct bend *bend2;
  int reverse = 0;

  BAIL();
  if (match->numberOfAtoms == 6) {
    aE = p->atoms[match->atomIndices[5]];
  }
  // here is the layout we're looking for:
  //
  //  aS2->aP->aS1
  //   |        |
  //  aA2------aA1 (- - - Ae)
  //
  // reverse means the bond directions are flipped from that layout

  switch (b->direction) {
  case 'F':
    reverse = (b->a1 == aS1);
    break;
  case 'R':
    reverse = (b->a1 == aP);
    break;
  default:
    ERROR2("pam5_ring_match: bond between ids %d and %d has no direction", aP->atomID, aS1->atomID);
    p->parseError(p->stream);
    return;
  }
  if (match->numberOfAtoms == 5) {
    if (reverse) {
      t = aA1;
      aA1 = aA2;
      aA2 = t;
      t = aS1;
      aS1 = aS2;
      aS2 = t;
    }
    bend1 = getBend(p, aA2, aA1, aS1); BAIL();
    bend2 = getBend(p, aA1, aA2, aS2); BAIL();
    bend1->bendType = pam5_Ax_Ax_Ss_low;
    bend2->bendType = pam5_Ax_Ax_Ss_high;
  } else {
    bend1 = getBend(p, aE, aA1, aS1); BAIL();
    bend1->bendType = reverse ? pam5_Ax_Ax_Ss_high : pam5_Ax_Ax_Ss_low;
  }
  //printMatch(match);
}
*/

static void
pam5_requires_gromacs(struct part *p)
{
  if (GromacsOutputBaseName == NULL) {
    ERROR("PAM5 DNA structures must be minimized with GROMACS");
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

static void
init_stack_match(void)
{
  int i;
  char buf[256];
  struct patternParameter *param;

  if (stack_match_initialized) {
    return;
  }
  for (i=0; i<8; i++) {
    sprintf(buf, "vDa%d", i+1);
    vDa_type[i] = getAtomTypeByName(buf);
    sprintf(buf, "vDb%d", i+1);
    vDb_type[i] = getAtomTypeByName(buf);

    sprintf(buf, "PAM5-Stack:vDa%d-p", i+1);
    param = getPatternParameter(buf); BAIL();
    vDax_p[i] = param->value;
    sprintf(buf, "PAM5-Stack:vDa%d-q", i+1);
    param = getPatternParameter(buf); BAIL();
    vDax_q[i] = param->value;
    sprintf(buf, "PAM5-Stack:vDb%d-p", i+1);
    param = getPatternParameter(buf); BAIL();
    vDbx_p[i] = param->value;
    sprintf(buf, "PAM5-Stack:vDb%d-q", i+1);
    param = getPatternParameter(buf); BAIL();
    vDbx_q[i] = param->value;
  }
  stack_match_initialized = 1;
}

static void
pam5_basepair_match(struct patternMatch *match)
{
  struct atom *aS1 = match->p->atoms[match->atomIndices[1]];
  struct atom *aS2 = match->p->atoms[match->atomIndices[2]];
  struct bond *bond;

  pam5_requires_gromacs(match->p); BAIL();
  bond = makeBond(match->p, aS1, aS2, '1');
  queueBond(match->p, bond);
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
  init_stack_match();
  
  // S1a    S2a
  //  |      |
  // Gv1----Gv2
  //  |      |
  // S1b    S2b
  if (!isExpectedTwist(match->p, aGv1, aGv2, aS1a, aS1b)) {
    aS1a = match->p->atoms[match->atomIndices[3]];
    aS1b = match->p->atoms[match->atomIndices[2]];
  }
  if (!isExpectedTwist(match->p, aGv2, aGv1, aS2a, aS2b)) {
    aS2a = match->p->atoms[match->atomIndices[5]];
    aS2b = match->p->atoms[match->atomIndices[4]];
  }
  // atoms are now in canonical orientations
  for (i=0; i<8; i++) {
    vA = makeVirtualAtom(vDa_type[i], sp3, 3, 1,
                         aGv1, aS1a, aS1b, NULL,
                         vDax_p[i], vDax_q[i], 0.0);
    vB = makeVirtualAtom(vDb_type[i], sp3, 3, 1,
                         aGv2, aS2a, aS2b, NULL,
                         vDbx_p[i], vDbx_q[i], 0.0);
    bond = makeBond(match->p, vA, vB, '1');
    queueAtom(match->p, vA);
    queueAtom(match->p, vB);
    queueBond(match->p, bond);
  }
}

#define NUM_PATTERNS 2
static struct compiledPattern *allPatterns[NUM_PATTERNS];

void
createPatterns(void)
{
  //double ktheta;
  //double theta0;
  struct compiledPatternTraversal *t[10];
  struct compiledPatternAtom *a[10];
  //struct patternParameter *param;
  
  makeUnmatchableType();

  /*
  a[0] = makePatternAtom(0, "Ax5");
  a[1] = makePatternAtom(1, "Ax5");
  a[2] = makePatternAtom(2, "Ss5");
  a[3] = makePatternAtom(3, "Pl5");
  a[4] = makePatternAtom(4, "Ss5");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[1], a[2], '1');
  t[2] = makeTraversal(a[2], a[3], '1');
  t[3] = makeTraversal(a[3], a[4], '1');
  t[4] = makeTraversal(a[4], a[0], '1');
  allPatterns[0] = makePattern("PAM5-ring", pam5_ring_match, 5, 5, t);

  a[0] = makePatternAtom(0, "Ax5");
  a[1] = makePatternAtom(1, "Ax5");
  a[2] = makePatternAtom(2, "Ss5");
  a[3] = makePatternAtom(3, "Pl5");
  a[4] = makePatternAtom(4, "Ss5");
  a[5] = makePatternAtom(5, "Ae5");
  t[0] = makeTraversal(a[5], a[0], '1');
  t[1] = makeTraversal(a[0], a[1], '1');
  t[2] = makeTraversal(a[1], a[2], '1');
  t[3] = makeTraversal(a[2], a[3], '1');
  t[4] = makeTraversal(a[3], a[4], '1');
  t[5] = makeTraversal(a[4], a[0], '1');
  allPatterns[1] = makePattern("PAM5-ring-end", pam5_ring_match, 6, 6, t);
  */
  
  a[0] = makePatternAtom(0, "P5G");
  a[1] = makePatternAtom(1, "P5S");
  a[2] = makePatternAtom(2, "P5S");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[0], a[2], '1');
  allPatterns[0] = makePattern("PAM5-basepair", pam5_basepair_match, 3, 2, t);

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
  allPatterns[1] = makePattern("PAM5-stack", pam5_stack_match, 6, 5, t);
  
  /*
  param = getPatternParameter("PAM5:Ax-Ax-Ss_low_ktheta"); BAIL();
  ktheta = param->value * 1e6;
  param = getPatternParameter("PAM5:Ax-Ax-Ss_low_theta0"); BAIL();
  theta0 = param->value * param->angleUnits;
  pam5_Ax_Ax_Ss_low = newBendData("Ax-Ax-Ss_low", ktheta, theta0, 9);

  param = getPatternParameter("PAM5:Ax-Ax-Ss_high_ktheta"); BAIL();
  ktheta = param->value * 1e6;
  param = getPatternParameter("PAM5:Ax-Ax-Ss_high_theta0"); BAIL();
  theta0 = param->value * param->angleUnits;
  pam5_Ax_Ax_Ss_high = newBendData("Ax-Ax-Ss_high", ktheta, theta0, 9);
  */
}

void
matchPartToAllPatterns(struct part *part)
{
  int i;

  for (i=0; i<NUM_PATTERNS; i++) {
    matchPartToPattern(part, allPatterns[i]); BAIL();
  }
}
