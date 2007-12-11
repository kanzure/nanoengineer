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
  // search up type heirarchy once one exists
  return a->type == type;
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
  int ret;

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
  ret = hashtable_get(matchSet, buf1) != NULL;
  if (!ret) {
    hashtable_put(matchSet, buf1, (void *)1);
  }
  return ret;
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
        if (debugMatch) {
          printf("[%d] bond %d checking ", traversalIndex, bondNumber);
          printAtomShort(stdout, atomB);
          printf("\n");
        }
        if (matchSpecificAtom(match, traversal->b, atomB, traversalIndex)) {
          matchOneTraversal(match, pattern, traversalIndex+1);
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
    //printf("pattern index: %d, atomid: %d\n", i, match->atomIndices[i]);
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
  allPatterns[0] = makePattern("DNAring", printMatch, 5, 5, t);
}

void
matchPartToAllPatterns(struct part *part)
{
  double val;
  
  matchPartToPattern(part, allPatterns[0]);
  val = getPatternParameter("PAM5:DNAring:upward_bend_theta0");
  printf("theta0: %f\n", val);
}
