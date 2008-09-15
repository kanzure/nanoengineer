// Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 

#include "simulator.h"

static char const rcsid[] = "$Id$";

static void
trace_set_amber_type(struct atom *a, char *type, struct patternMatch *match)
{
  char buf[1024];

  sprintf(buf, "# Pattern setType: [%d] %d %s\n", match->sequenceNumber, a->atomID, type);
  write_traceline(buf);
}

static void
set_AMBER_type(struct atom *a, char *type, struct patternMatch *match)
{
  if (TypeFeedback) {
    trace_set_amber_type(a, type, match);
  }
}

static void
amber_match_CT_CA_CZ(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];

  if (a->hybridization == sp3) {
    set_AMBER_type(a, "CT", match);
  } else if (a->hybridization == sp2) {
    set_AMBER_type(a, "CA", match);
  } else if (a->hybridization == sp) {
    set_AMBER_type(a, "CZ", match);
  }
}

static void
amber_match_C_star_(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<5; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[5]];
  if (strcmp(a->type->symbol, "H")) {
    a = p->atoms[match->atomIndices[2]];
    set_AMBER_type(a, "C*", match);
  }
}

static void
amber_match_CB(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<9; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[0]];
  set_AMBER_type(a, "CB", match);
  a = p->atoms[match->atomIndices[4]];
  if (!strcmp(a->type->symbol, "C")) {
    set_AMBER_type(a, "CB", match);
  }
}

static void
amber_match_CC_CR_CV(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<5; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[6]];
  if (strcmp(a->type->symbol, "H")) {
    a = p->atoms[match->atomIndices[0]];
    set_AMBER_type(a, "CC", match);
    a = p->atoms[match->atomIndices[2]];
    set_AMBER_type(a, "CR", match);
    a = p->atoms[match->atomIndices[3]];
    if (a->num_bonds == 2) {
      a = p->atoms[match->atomIndices[4]];
      set_AMBER_type(a, "CV", match);
    }
  }
}

static void
amber_match_C(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];

  if (a->hybridization == sp2) {
    set_AMBER_type(a, "C", match);
  }
}

static void
amber_match_CD(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a1 = p->atoms[match->atomIndices[1]];
  struct atom *a2 = p->atoms[match->atomIndices[2]];

  set_AMBER_type(a1, "CD", match);
  set_AMBER_type(a2, "CD", match);
}

static void
amber_match_CK(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<9; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[2]];
  set_AMBER_type(a, "CK", match);
}

static void
amber_match_CM(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<7; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[7]];
  if (!strcmp(a->type->symbol, "N") || !strcmp(a->type->symbol, "O")) {
    a = p->atoms[match->atomIndices[0]];
    set_AMBER_type(a, "CM", match);
    a = p->atoms[match->atomIndices[1]];
    set_AMBER_type(a, "CM", match);
  }

}

static void
amber_match_CN(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<9; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[1]];
  set_AMBER_type(a, "CN", match);
}

static void
amber_match_CQ(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<9; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[6]];
  set_AMBER_type(a, "CQ", match);
}

static void
amber_match_CW(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<5; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[6]];
  if (strcmp(a->type->symbol, "H")) {
    a = p->atoms[match->atomIndices[1]];
    if (!strcmp(a->type->symbol, "N") || !strcmp(a->type->symbol, "C")) {
      a = p->atoms[match->atomIndices[4]];
      set_AMBER_type(a, "CW", match);
    }
  }
}

static void
amber_match_CY(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];

  set_AMBER_type(a, "CY", match);
}

void
createAMBERPatterns(void)
{
  struct compiledPatternTraversal *t[15];
  struct compiledPatternAtom *a[15];

  a[0] = makePatternAtom(0, "C");
  t[0] = makeTraversal(a[0], a[0], '1');
  makePattern("AMBER-CT-CA-CZ", amber_match_CT_CA_CZ, 1, 1, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "C");
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "C");
  a[4] = makePatternAtom(4, "C");
  a[5] = makePatternAtom(5, "Elt"); // not H
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal(a[2], a[5], '1');
  makePattern("AMBER-C*", amber_match_C_star_, 6, 6, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "Elt");
  a[2] = makePatternAtom(2, "Elt");
  a[3] = makePatternAtom(3, "Elt");
  a[4] = makePatternAtom(4, "Elt");
  a[5] = makePatternAtom(5, "Elt");
  a[6] = makePatternAtom(6, "Elt");
  a[7] = makePatternAtom(7, "Elt");
  a[8] = makePatternAtom(8, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal2(a[0], a[5], "1ag2");
  t[6] = makeTraversal2(a[5], a[6], "1ag2");
  t[7] = makeTraversal2(a[6], a[7], "1ag2");
  t[8] = makeTraversal2(a[7], a[8], "1ag2");
  t[9] = makeTraversal2(a[8], a[4], "1ag2");
  makePattern("AMBER-CB", amber_match_CB, 9, 10, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "N");
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "N");
  a[4] = makePatternAtom(4, "C");
  a[5] = makePatternAtom(5, "H");
  a[6] = makePatternAtom(6, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal(a[4], a[5], '1');
  t[6] = makeTraversal(a[0], a[6], '1');
  makePattern("AMBER-CC-CR-CV", amber_match_CC_CR_CV, 7, 7, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "O");
  a[2] = makePatternAtom(2, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "ag2");
  t[1] = makeTraversal2(a[0], a[2], "1ag");
  makePattern("AMBER-C", amber_match_C, 3, 2, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "C");
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "C");
  t[0] = makeTraversal(a[0], a[1], '2');
  t[1] = makeTraversal(a[1], a[2], '1');
  t[2] = makeTraversal(a[2], a[3], '2');
  makePattern("AMBER-CD", amber_match_CD, 4, 3, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "N");
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "N");
  a[4] = makePatternAtom(4, "C");
  a[5] = makePatternAtom(5, "N");
  a[6] = makePatternAtom(6, "C");
  a[7] = makePatternAtom(7, "N");
  a[8] = makePatternAtom(8, "C");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal2(a[0], a[5], "1ag2");
  t[6] = makeTraversal2(a[5], a[6], "1ag2");
  t[7] = makeTraversal2(a[6], a[7], "1ag2");
  t[8] = makeTraversal2(a[7], a[8], "1ag2");
  t[9] = makeTraversal2(a[8], a[4], "1ag2");
  makePattern("AMBER-CK", amber_match_CK, 9, 10, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "C");
  a[2] = makePatternAtom(2, "N");
  a[3] = makePatternAtom(3, "C");
  a[4] = makePatternAtom(4, "N");
  a[5] = makePatternAtom(5, "C");
  a[6] = makePatternAtom(6, "O");
  a[7] = makePatternAtom(7, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[5], "1ag2");
  t[5] = makeTraversal2(a[5], a[0], "1ag2");
  t[6] = makeTraversal2(a[3], a[6], "ag2");
  t[7] = makeTraversal2(a[5], a[7], "1ag2");
  makePattern("AMBER-CM", amber_match_CM, 8, 8, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "C");
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "C");
  a[4] = makePatternAtom(4, "C");
  a[5] = makePatternAtom(5, "C");
  a[6] = makePatternAtom(6, "C");
  a[7] = makePatternAtom(7, "C");
  a[8] = makePatternAtom(8, "C");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal2(a[1], a[5], "1ag2");
  t[6] = makeTraversal2(a[5], a[6], "1ag2");
  t[7] = makeTraversal2(a[6], a[7], "1ag2");
  t[8] = makeTraversal2(a[7], a[8], "1ag2");
  t[9] = makeTraversal2(a[8], a[2], "1ag2");
  makePattern("AMBER-CN", amber_match_CN, 9, 10, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "C");
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "N");
  a[4] = makePatternAtom(4, "C");
  a[5] = makePatternAtom(5, "N");
  a[6] = makePatternAtom(6, "C");
  a[7] = makePatternAtom(7, "N");
  a[8] = makePatternAtom(8, "C");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal2(a[1], a[5], "1ag2");
  t[6] = makeTraversal2(a[5], a[6], "1ag2");
  t[7] = makeTraversal2(a[6], a[7], "1ag2");
  t[8] = makeTraversal2(a[7], a[8], "1ag2");
  t[9] = makeTraversal2(a[8], a[2], "1ag2");
  makePattern("AMBER-CQ", amber_match_CQ, 9, 10, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "Elt"); // N or C
  a[2] = makePatternAtom(2, "C");
  a[3] = makePatternAtom(3, "N");
  a[4] = makePatternAtom(4, "C");
  a[5] = makePatternAtom(5, "H");
  a[6] = makePatternAtom(6, "Elt"); // not H
  a[7] = makePatternAtom(7, "H");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal(a[4], a[5], '1');
  t[6] = makeTraversal(a[0], a[6], '1');
  t[7] = makeTraversal(a[3], a[7], '1');
  makePattern("AMBER-CW", amber_match_CW, 8, 8, t);

  a[0] = makePatternAtom(0, "C");
  a[1] = makePatternAtom(1, "N");
  t[0] = makeTraversal(a[0], a[1], '3');
  makePattern("AMBER-CY", amber_match_CY, 2, 1, t);
}
