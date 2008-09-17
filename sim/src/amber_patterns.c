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

static char *ANY_MAPPING[] = {
  "Ca", "C0",
  "F",  "F",
  "Cl", "Cl",
  "Br", "Br",
  "I",  "I",
  "Na", "IB",
  "Mg", "MG",
  "P",  "P",
  "Cu", "CU",
  "Fe", "FE",
  "Li", "Li",
  "K",  "K",
  "Rb", "Rb",
  "Cs", "Cs",
  "Zn", "Zn",
  NULL, NULL
};

static void
amber_match_ANY(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];
  char *t = a->type->symbol;
  int i;

  i = 0;
  while (ANY_MAPPING[i] != NULL) {
    if (!strcmp(t, ANY_MAPPING[i])) {
      set_AMBER_type(a, ANY_MAPPING[i+1], match);
      return;
    }
    i += 2;
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

static void
amber_match_H_C(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aH = p->atoms[match->atomIndices[0]];
  struct atom *aC = p->atoms[match->atomIndices[1]];
  struct atom *neighbor_atom;
  int i;
  int pos = 0;
  int ewg = 0;
  char *t;
  
  if (aC->hybridization == sp) {
    set_AMBER_type(aH, "HZ", match); // H on sp C
    return;
  }
  for (i=aC->num_bonds-1; i>=0; i--) {
    neighbor_atom = getBondedAtom(aC, i);
    if (neighbor_atom != aH) {
      t = neighbor_atom->type->symbol;
      if (!strcmp(t, "S") || !strcmp(t, "O")) {
        ewg++;
      } else if (!strcmp(t, "N")) {
        if (neighbor_atom->num_bonds > 3) {
          pos++;
        } else {
          ewg++;
        }
      }
    }
  }
  if (pos > 0) {
    set_AMBER_type(aH, "HP", match); // H next to positive N
    return;
  }
  if (aC->hybridization == sp3) {
    if (ewg == 0) {
      set_AMBER_type(aH, "HC", match); // H on sp3, no withdrawing groups
      return;
    }
    if (ewg == 1) {
      set_AMBER_type(aH, "H1", match); // H on sp3, 1 withdrawing group
      return;
    }
    if (ewg == 2) {
      set_AMBER_type(aH, "H2", match); // H on sp3, 2 withdrawing groups
      return;
    }
    set_AMBER_type(aH, "H3", match); // H on sp3, 3 withdrawing groups
    return;
  }
  if (ewg == 0) {
    set_AMBER_type(aH, "HA", match); // H on sp2, no withdrawing groups
    return;
  }
  if (ewg == 1) {
    set_AMBER_type(aH, "H4", match); // H on sp2, 1 withdrawing group
    return;
  }
  set_AMBER_type(aH, "H5", match); // H on sp2, 2 withdrawing groups
}

static void
amber_match_H_N(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aH = p->atoms[match->atomIndices[0]];

  set_AMBER_type(aH, "H", match); // H on N
}

static void
amber_match_H_S(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aH = p->atoms[match->atomIndices[0]];

  set_AMBER_type(aH, "HS", match); // H on S
}

static void
amber_match_H_O(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aH = p->atoms[match->atomIndices[0]];
  struct atom *aO = p->atoms[match->atomIndices[1]];
  struct atom *neighbor_atom;
  
  neighbor_atom = getBondedAtom(aO, 0);
  if (neighbor_atom == aH) {
    neighbor_atom = getBondedAtom(aO, 1);
  }
  if (neighbor_atom && !strcmp(neighbor_atom->type->symbol, "H")) {
    set_AMBER_type(aH, "HW", match); // H in water
  } else {
    set_AMBER_type(aH, "HO", match); // H on O, not water
  }
}

static void
amber_match_N_N2_N3_NT_NY(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];
  struct atom *a2;
  int i;
  
  if (a->hybridization == sp3) {
    if (a->num_bonds == 4) {
      set_AMBER_type(a, "N3", match); // sp3 N with 4 bonds (positive)
    } else {
      set_AMBER_type(a, "NT", match); // sp3 N with 3 bonds
    }
  } else if (a->hybridization == sp2) {
    for (i=a->num_bonds-1; i>=0; i--) {
      a2 = getBondedAtom(a, i);
      if (!strcmp(a2->type->symbol, "C") && a2->hybridization == sp2) {
        set_AMBER_type(a, "N2", match); // sp2 N bonded to sp2 C
        return;
      }
    }
    set_AMBER_type(a, "N", match); // sp2 N
  } else if (a->hybridization == sp) {
    set_AMBER_type(a, "NY", match); // sp N
  }
}

static void
amber_match_NC(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a;
  int i;

  for (i=0; i<6; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[0]];
  // We don't check for LP, NA and N* will override
  set_AMBER_type(a, "NC", match); // aromatic 6-ring N w/LP
}

static void
amber_match_NB(struct patternMatch *match)
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
  a = p->atoms[match->atomIndices[0]];
  // We don't check for LP, NA and N* will override
  set_AMBER_type(a, "NB", match); // aromatic 5-ring N w/LP
}

static void
amber_match_NA_N_star_(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *aN = p->atoms[match->atomIndices[0]];
  struct atom *a;
  int i;

  for (i=0; i<match->numberOfAtoms-1; i++) {
    a = p->atoms[match->atomIndices[i]];
    if (a->hybridization != sp2) {
      return;
    }
  }
  a = p->atoms[match->atomIndices[match->numberOfAtoms-1]];
  if (!strcmp(a->type->symbol, "H")) {
    set_AMBER_type(aN, "NA", match); // aromatic ring N with H
  } else {
    set_AMBER_type(aN, "N*", match); // aromatic ring N with R group
  }
}

static void
amber_match_O(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];

  if (a->num_bonds == 1) {
    set_AMBER_type(a, "O", match);
  }
}

static void
amber_match_O2(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a0 = p->atoms[match->atomIndices[0]];
  struct atom *a2 = p->atoms[match->atomIndices[2]];

  if (a0->num_bonds == 1 && a2->num_bonds == 1) {
    set_AMBER_type(a0, "O2", match);
    set_AMBER_type(a2, "O2", match);
  }
}

static void
amber_match_OH_OS_OW(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a0 = p->atoms[match->atomIndices[0]];
  struct atom *a1 = p->atoms[match->atomIndices[1]];
  struct atom *a2 = p->atoms[match->atomIndices[2]];
  int num_H = 0;

  if (!strcmp(a1->type->symbol, "H")) {
    num_H++;
  }
  if (!strcmp(a2->type->symbol, "H")) {
    num_H++;
  }
  if (num_H == 2) {
    set_AMBER_type(a0, "OW", match); // H-O-H
  } else if (num_H == 1) {
    set_AMBER_type(a0, "OH", match); // R-O-H
  } else {
    set_AMBER_type(a0, "OS", match); // R-O-R
  }
}

static void
amber_match_SH(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];

  set_AMBER_type(a, "SH", match);
}

static void
amber_match_S_1(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a = p->atoms[match->atomIndices[0]];

  set_AMBER_type(a, "S", match);
}

static void
amber_match_S_2(struct patternMatch *match)
{
  struct part *p = match->p;
  struct atom *a0 = p->atoms[match->atomIndices[0]];
  struct atom *a1 = p->atoms[match->atomIndices[0]];

  set_AMBER_type(a0, "S", match);
  set_AMBER_type(a1, "S", match);
}

void
createAMBERPatterns(void)
{
  struct compiledPatternTraversal *t[15];
  struct compiledPatternAtom *a[15];

  a[0] = makePatternAtom(0, "Elt");
  t[0] = makeTraversal(a[0], a[0], '1');
  makePattern("AMBER-ANY", amber_match_ANY, 1, 1, t);

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

  a[0] = makePatternAtom(0, "H");
  a[1] = makePatternAtom(1, "C");
  t[0] = makeTraversal(a[0], a[1], '1');
  makePattern("AMBER-H-C", amber_match_H_C, 2, 1, t);

  a[0] = makePatternAtom(0, "H");
  a[1] = makePatternAtom(1, "N");
  t[0] = makeTraversal(a[0], a[1], '1');
  makePattern("AMBER-H-N", amber_match_H_N, 2, 1, t);

  a[0] = makePatternAtom(0, "H");
  a[1] = makePatternAtom(1, "S");
  t[0] = makeTraversal(a[0], a[1], '1');
  makePattern("AMBER-H-S", amber_match_H_S, 2, 1, t);

  a[0] = makePatternAtom(0, "H");
  a[1] = makePatternAtom(1, "O");
  t[0] = makeTraversal(a[0], a[1], '1');
  makePattern("AMBER-H-O", amber_match_H_O, 2, 1, t);

  a[0] = makePatternAtom(0, "N");
  t[0] = makeTraversal(a[0], a[0], '1');
  makePattern("AMBER-N-N2-N3-NT-NY", amber_match_N_N2_N3_NT_NY, 1, 1, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "Elt"); // N or C
  a[2] = makePatternAtom(2, "Elt");
  a[3] = makePatternAtom(3, "Elt");
  a[4] = makePatternAtom(4, "Elt");
  a[5] = makePatternAtom(5, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[5], "1ag2");
  t[5] = makeTraversal2(a[5], a[0], "1ag2");
  makePattern("AMBER-NC", amber_match_NC, 6, 6, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "Elt"); // N or C
  a[2] = makePatternAtom(2, "Elt");
  a[3] = makePatternAtom(3, "Elt");
  a[4] = makePatternAtom(4, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  makePattern("AMBER-NB", amber_match_NB, 5, 5, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "Elt"); // N or C
  a[2] = makePatternAtom(2, "Elt");
  a[3] = makePatternAtom(3, "Elt");
  a[4] = makePatternAtom(4, "Elt");
  a[5] = makePatternAtom(5, "Elt");
  a[6] = makePatternAtom(6, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[5], "1ag2");
  t[5] = makeTraversal2(a[5], a[0], "1ag2");
  t[6] = makeTraversal(a[0], a[6], '1');
  makePattern("AMBER-NA-N*", amber_match_NA_N_star_, 7, 7, t);

  a[0] = makePatternAtom(0, "N");
  a[1] = makePatternAtom(1, "Elt"); // N or C
  a[2] = makePatternAtom(2, "Elt");
  a[3] = makePatternAtom(3, "Elt");
  a[4] = makePatternAtom(4, "Elt");
  a[5] = makePatternAtom(5, "Elt");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  t[2] = makeTraversal2(a[2], a[3], "1ag2");
  t[3] = makeTraversal2(a[3], a[4], "1ag2");
  t[4] = makeTraversal2(a[4], a[0], "1ag2");
  t[5] = makeTraversal(a[0], a[5], '1');
  makePattern("AMBER-NA-N*", amber_match_NA_N_star_, 6, 6, t);

  a[0] = makePatternAtom(0, "O");
  a[1] = makePatternAtom(1, "C");
  t[0] = makeTraversal(a[0], a[1], '2');
  makePattern("AMBER-O", amber_match_O, 2, 1, t);

  a[0] = makePatternAtom(0, "O");
  a[1] = makePatternAtom(1, "Elt");
  a[2] = makePatternAtom(2, "O");
  t[0] = makeTraversal2(a[0], a[1], "1ag2");
  t[1] = makeTraversal2(a[1], a[2], "1ag2");
  makePattern("AMBER-O2", amber_match_O2, 3, 2, t);

  a[0] = makePatternAtom(0, "O");
  a[1] = makePatternAtom(1, "Elt");
  a[2] = makePatternAtom(2, "Elt");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[0], a[2], '1');
  makePattern("AMBER-OH-OS-OW", amber_match_OH_OS_OW, 3, 2, t);

  a[0] = makePatternAtom(0, "S");
  a[1] = makePatternAtom(1, "H");
  t[0] = makeTraversal(a[0], a[1], '1');
  makePattern("AMBER-SH", amber_match_SH, 2, 1, t);

  a[0] = makePatternAtom(0, "S");
  a[1] = makePatternAtom(1, "C");
  a[2] = makePatternAtom(2, "C");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[0], a[2], '1');
  makePattern("AMBER-S-1", amber_match_S_1, 3, 2, t);

  a[0] = makePatternAtom(0, "S");
  a[1] = makePatternAtom(1, "S");
  a[2] = makePatternAtom(2, "Elt");
  a[3] = makePatternAtom(3, "Elt");
  t[0] = makeTraversal(a[0], a[1], '1');
  t[1] = makeTraversal(a[0], a[2], '1');
  t[2] = makeTraversal(a[1], a[3], '1');
  makePattern("AMBER-S-2", amber_match_S_2, 3, 2, t);
}
