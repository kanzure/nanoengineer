// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 

#include "simulator.h"

static char const rcsid[] = "$Id$";

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
resetMatchForThisTraversal(struct patternMatch *match, int traversalIndex)
{
  int i;
  
  for (i=match->numberOfAtoms-1; i>=0; i--) {
    if (match->introducedAtTraversal[i] == traversalIndex) {
      match->atomIndices[i] = -1;
    }
  }
}

static int
atomIsType(struct atom *a, struct atomType *type) 
{
  // search up type heirarchy once one exists
  return a->type == type;
}
           
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
      return match->p->atoms[match->atomIndices[id]];
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
    a = p->atoms[match->atomIndices[id]];
    if (atomIsType(a, patternAtom->type)) {
      return a;
    }
  }
  return NULL;
}

static int
matchSpecificAtom(struct patternMatch *match,
                  struct compiledPatternAtom *patternAtom,
                  struct atom *targetAtom,
                  int traversalIndex)
{
  int id;
  
  if (atomIsType(targetAtom, patternAtom->type)) {
    id = patternAtom->idInPattern;
    match->atomIndices[id] = targetAtom->index;
    match->introducedAtTraversal[id] = traversalIndex;
    return 1;
  }
  return 0;
}

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
  struct bond *bond;
  struct compiledPatternTraversal *traversal;
  
  if (traversalIndex >= pattern->numberOfTraversals) {
    // check for duplicate matches here
    pattern->matchFunction(match);
    return;
  }
  resetMatchForThisTraversal(match, traversalIndex);
  traversal = pattern->traversals[traversalIndex];
  while ((atomA = matchOneAtom(match,
                               pattern,
                               traversal->a,
                               traversalIndex,
                               &atomACallCount)) != NULL) {
    if (traversal->a == traversal->b) {
      // introducing new atom, bond order doesn't matter
      matchOneTraversal(match, pattern, traversalIndex+1);
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
          matchOneTraversal(match, pattern, traversalIndex+1);
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
        if (matchSpecificAtom(match, traversal->b, atomB, traversalIndex)) {
          matchOneTraversal(match, pattern, traversalIndex+1);
        }
      }
    }
  }
}


static void
matchPartToPattern(struct part *part, struct compiledPattern *pattern)
{
  struct patternMatch *match;

  match = makeMatch(part, pattern);
  matchOneTraversal(match, pattern, 0);
  destroyMatch(match);
}


static struct atomType *unmatchable = NULL;

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
  unmatchable->symbol[0] = 'e';
  unmatchable->symbol[1] = 'r';
  unmatchable->symbol[2] = 'r';
  unmatchable->symbol[3] = '\0';
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

static void
printMatch(struct patternMatch *match)
{
  int i;
  
  printf("match for pattern %s\n", match->patternName);
  for (i=0; i<match->numberOfAtoms; i++) {
    printf("pattern index: %d, atomid: %d\n", i, match->atomIndices[i]);
    printAtom(stdout, match->p, match->p->atoms[match->atomIndices[i]]);
  }
}

static struct compiledPattern *allPatterns[1];

void
createPatterns(void)
{
  struct compiledPatternTraversal *t[10];
  struct compiledPatternAtom *a[10];
  
  makeUnmatchableType();
  
  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "O");
  a[2] = makePatternAtom(2, "O");
  a[3] = makePatternAtom(3, "H");
  t[0] = makeTraversal(a[0], a[1], '2');
  t[1] = makeTraversal(a[0], a[2], '1');
  t[2] = makeTraversal(a[2], a[3], '1');
  allPatterns[0] = makePattern("COOH", printMatch, 4, 3, t);
}

void
matchPartToAllPatterns(struct part *part)
{
  matchPartToPattern(part, allPatterns[0]);
}
