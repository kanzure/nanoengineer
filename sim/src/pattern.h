// Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
#ifndef PATTERN_H_INCLUDED
#define PATTERN_H_INCLUDED

#define RCSID_PATTERN_H  "$Id$"

struct compiledPatternAtom
{
  struct atomType *type;
  int idInPattern;
};

struct compiledPatternTraversal
{
  struct compiledPatternAtom *a;
  struct compiledPatternAtom *b;
  char bondOrder;
};

struct patternMatch 
{
  struct part *p;
  char *patternName;
  int numberOfAtoms;
  int *atomIndices;
  int *introducedAtTraversal;
};

struct compiledPattern
{
  char *name;
  void (*matchFunction)(struct patternMatch *match);
  int numberOfAtoms;
  int numberOfTraversals;
  struct compiledPatternTraversal **traversals;
};

extern int atomIsType(struct atom *a, struct atomType *type);

extern struct compiledPatternAtom *makePatternAtom(int id, char *type);

extern struct compiledPatternTraversal *makeTraversal(struct compiledPatternAtom *a, struct compiledPatternAtom *b, char bondOrder);

extern void makePattern(char *name, void (*matchFunction)(struct patternMatch *match), int numAtoms, int numTraversals, struct compiledPatternTraversal **traversals);

extern void matchPartToAllPatterns(struct part *part);

extern void createPatterns(void);

#endif
