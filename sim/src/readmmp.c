// Copyright 2005-2007 Nanorex, Inc.  See LICENSE file for details. 

#include <limits.h>
#include "simulator.h"

static char const rcsid[] = "$Id$";

struct mmpStream 
{
  FILE *f;
  char *fileName;
  int lineNumber;
  int charPosition;
};

// should be preceded by a call to ERROR() giving details
static int
mmpParseError(void *stream)
{
  // We cast from void * here so that the part routines can take a
  // generic error handler and user data pointer.
  struct mmpStream *mmp = (struct mmpStream *)stream;
  
  ERROR3("In mmp file %s, line %d, col %d", mmp->fileName, mmp->lineNumber, mmp->charPosition);
  done("Failed to parse mmp file");
  RAISER("Failed to parse mmp file", 0);
}


static char tokenBuffer[256];

// Read the next token from the given stream.  Possible return values
// are:
//
//  NULL    when EOF or an error has been encountered
//  ""      a zero length string for each '\0' (treated as a delimiter)
//  delim   a one char length string for each delimiter encountered
//  token   a string for each sequence of non-delimiter characters
//
// See the switch statement for the list of delimiters.
//
// Any sequence of more than 255 non-delimiter characters is broken
// into tokens every 255 characters.
static char *
readToken(struct mmpStream *mmp, int allowNULL)
{
  char *s = tokenBuffer;
  char c;

  if (feof(mmp->f) || ferror(mmp->f)) {
    if (allowNULL) {
      return NULL;
    } else {
      ERROR("Unexpected EOF");
      mmpParseError(mmp);
      return "EOF";
    }
  }
  while ((*s = fgetc(mmp->f)) != EOF) {
    mmp->charPosition++;
    switch (*s) {
    case ' ':
    case '(':
    case ')':
    case ',':
    case ';':
    case '=':
    case '\r':
    case '\n':
    case '\0':
      if (s == tokenBuffer) {
        if (*s == '\n' || *s == '\r') {
          c = fgetc(mmp->f);
          if (c == '\n' || c == '\r') {
            if (c == *s) {
              ungetc(c, mmp->f);
            }
            *s = '\n';
          } else {
            ungetc(c, mmp->f);
          }
          mmp->lineNumber++;
          mmp->charPosition = 1;
        }
        s++;
      } else {
        ungetc(*s, mmp->f);
        mmp->charPosition--;
      }
      *s = '\0';
      return tokenBuffer;
    default:
      s++;
      if (s >= &tokenBuffer[255]) {
        *s = '\0';
        return tokenBuffer;
      }
    }
  }
  if (s == tokenBuffer) {
    if (allowNULL) {
      return NULL;
    } else {
      ERROR("Unexpected EOF");
      mmpParseError(mmp);
      return "EOF";
    }
  }
  *s = '\0';
  return tokenBuffer;
}

// Skip zero or more whitespace characters (space or tab).  Newline is
// not considered whitespace.  The next token will start with the
// first non-whitespace character found.
static void
consumeWhitespace(struct mmpStream *mmp)
{
  int c;
  
  if (feof(mmp->f) || ferror(mmp->f)) {
    return;
  }
  while ((c = fgetc(mmp->f)) != EOF) {
    mmp->charPosition++;
    switch (c) {
    case ' ':
    case '\t':
      break;
    default:
      ungetc(c, mmp->f);
      mmp->charPosition--;
      return;
    }
  }
}

// Ignores the remainder of this line.
static void
consumeRestOfLine(struct mmpStream *mmp)
{
  char *tok;

  while (1) {
    tok = readToken(mmp, 1);
    if (tok == NULL || *tok == '\n' || *tok == '\r') {
      return;
    }
  }
}

// Complains and dies if the next token is not the expected token.
// Pass in NULL to expect EOF.
static int
expectToken(struct mmpStream *mmp, char *expected)
{
  char *tok;
  int ret;
  
  tok = readToken(mmp, 1);
  if (tok == NULL) {
    ret = expected == NULL;
  } else if (expected == NULL) {
    ret = tok == NULL;
  } else {
    ret = !strcmp(tok, expected);
  }
  if (!ret) {
    ERROR2("expected %s, got %s", expected ? expected : "EOF", tok ? tok : "EOF");
    mmpParseError(mmp);
  }
  return ret;
}

// Parse an integer.  Returns 1 if value was successfully filled in
// with an integer value.  If checkForNewline is true, and a newline
// was encountered instead of an integer the newline is consumed and 0
// is returned.
//
// Any whitespace before and after the integer is consumed.
static int
expectInt(struct mmpStream *mmp, int *value, int checkForNewline)
{
  char *tok;
  char *end;
  long int val;

  consumeWhitespace(mmp);
  tok = readToken(mmp, 1);
  if (value == NULL) {
    ERROR("internal error, value==NULL");
    return mmpParseError(mmp);
  }
  if (tok != NULL) {
    if ((*tok == '\n' || *tok == '\r') && checkForNewline) {
      return 0;
    }
    if (*tok == '\0') {
      ERROR("expected int, got \\0");
      return mmpParseError(mmp);
    }
    errno = 0;
    val = strtol(tok, &end, 0);
    if (errno != 0) {
      ERROR1("integer value out of range: %s", tok);
      return mmpParseError(mmp);
    }
    if (*end != '\0') {
      ERROR1("expected int, got %s", tok);
      return mmpParseError(mmp);
    }
    if (val > INT_MAX || val < INT_MIN) {
      ERROR1("integer value out of range: %s", tok);
      return mmpParseError(mmp);
    }
    *value = val;
    consumeWhitespace(mmp);
    return 1;
  }
  ERROR("expected int, got EOF");
  return mmpParseError(mmp);
}

// Parse a double.  Returns 1 if value was successfully filled in
// with a double value.  If checkForNewline is true, and a newline
// was encountered instead of a double the newline is consumed and 0
// is returned.
//
// Any whitespace before and after the double is consumed.
static int
expectDouble(struct mmpStream *mmp, double *value, int checkForNewline)
{
  char *tok;
  char *end;
  double val;

  consumeWhitespace(mmp);
  tok = readToken(mmp, 1);
  if (value == NULL) {
    ERROR("internal error, value==NULL");
    return mmpParseError(mmp);
  }
  if (tok != NULL) {
    if ((*tok == '\n' || *tok == '\r') && checkForNewline) {
      return 0;
    }
    if (*tok == '\0') {
      ERROR("expected double, got \\0");
      return mmpParseError(mmp);
    }
    errno = 0;
    val = strtod(tok, &end);
    if (errno != 0) {
      ERROR1("double value out of range: %s", tok);
      return mmpParseError(mmp);
    }
    if (*end != '\0') {
      ERROR1("expected double, got %s", tok);
      return mmpParseError(mmp);
    }
    *value = val;
    consumeWhitespace(mmp);
    return 1;
  }
  ERROR("expected double, got EOF");
  return mmpParseError(mmp);
}

// Parses:
//
// ( <double> [, <double>]* )
//
// where each space between the parenthesis can be zero or more
// whitespace characters.  If p is non-null, the doubles are
// stored in successive array elements.
//
// Any whitespace before and after the parenthesis is consumed.
static void
expectNDoubles(struct mmpStream *mmp, int n, double *p)
{
  int i;
  double d;

  consumeWhitespace(mmp);
  expectToken(mmp, "("); BAIL();
  for (i=0; i<n; i++) {
    expectDouble(mmp, &d, 0); BAIL();
    if (i < n-1) {
      expectToken(mmp, ","); BAIL();
    }
    if (p != NULL) {
      p[i] = d;
    }
  }
  consumeWhitespace(mmp); // only needed if n==0
  expectToken(mmp, ")"); BAIL();
  consumeWhitespace(mmp);
}

// Parses:
//
// ( <int>, <int>, <int> )
//
// where each space between the parenthesis can be zero or more
// whitespace characters.  If p is non-null, the three ints are
// multiplied by 0.1 and placed in the x, y, and z fields.
//
// Any whitespace before and after the triple is consumed.
static void
expectXYZInts(struct mmpStream *mmp, struct xyz *p)
{
  int x;
  int y;
  int z;

  consumeWhitespace(mmp);
  expectToken(mmp, "("); BAIL();
  expectInt(mmp, &x, 0); BAIL();
  expectToken(mmp, ","); BAIL();
  expectInt(mmp, &y, 0); BAIL();
  expectToken(mmp, ","); BAIL();
  expectInt(mmp, &z, 0); BAIL();
  expectToken(mmp, ")"); BAIL();
  consumeWhitespace(mmp);

  if (p != NULL) {
    p->x = x * 0.1;
    p->y = y * 0.1;
    p->z = z * 0.1;
  }
}

static void *tempBuffer = NULL;

// Names in mmp files are delimited by ()'s.  () are encoded using
// %xx, and so are disallowed from appearing in the encoded form that
// we're reading here.  This reads an arbitrary length name (up to
// half the size of available memory) and returns an allocated copy of
// it.  Individual tokens are read and concatenated together to form
// the resulting name.  A \0 may be included, and will be encoded as
// %00.  The closing parenthesis must occur before a newline or end of
// file.
//
// Any whitespace before and after the name is consumed.
static char *
expectName(struct mmpStream *mmp)
{
  char *tok;
  char *buf;
  int len;
  
  consumeWhitespace(mmp);
  expectToken(mmp, "("); BAILR("");
  len = 0;
  tempBuffer = accumulator(tempBuffer, len + 1, 0);
  buf = (char *)tempBuffer;
  buf[len] = '\0';
  while ((tok = readToken(mmp, 1)) != NULL) {
    if (!strcmp(tok, ")")) {
      consumeWhitespace(mmp);
      return copy_string(buf);
    }
    if (*tok == '\0') {
      tok = "%00";
    }
    if (*tok == '\n' || *tok == '\r') {
      ERROR("reading name, expected ), got newline");
      mmpParseError(mmp);
      return "";
    }
    len += strlen(tok);
    tempBuffer = accumulator(tempBuffer, len + 1, 0);
    buf = (char *)tempBuffer;
    strcat(buf, tok);
  }
  ERROR("reading name, expected ), got EOF");
  mmpParseError(mmp);
  return "";
}

// Parses a list of integers terminated by a newline.  An arbitrary
// number of integers can be parsed, and the accumulator they are
// stored in is placed in listPtr, with the length stored in length.  If
// expectedLength is non-zero, complains and dies if the actual length
// is not expectedLength.  Also complains and dies for zero length
// lists.
static void
expectIntList(struct mmpStream *mmp, int **listPtr, int *length, int expectedLength)
{
  int *buf;
  int index;
  int len;
  int listElement;
  
  len = 0;
  tempBuffer = accumulator(tempBuffer, len, 0);
  buf = (int *)tempBuffer;
  index = 0;
  while (expectInt(mmp, &listElement, 1)) {
    len += sizeof(int);
    tempBuffer = accumulator(tempBuffer, len, 0);
    buf = (int *)tempBuffer;
    buf[index++] = listElement;
  }
  BAIL();
  if (index == 0) {
    ERROR("zero length list of atoms");
    mmpParseError(mmp);
    return;
  }
  if (expectedLength != 0 && expectedLength != index) {
    ERROR2("expected exactly %d atoms, got %d", expectedLength, index);
    mmpParseError(mmp);
    return;
  }
  *length = index;
  *listPtr = buf;
}

#define BAILP() if (EXCEPTION) { destroyPart(p); return NULL; }

// Note that this must be called AFTER simulation parameters (like Dt)
// have been set.  makeAtom() uses Dt to set inverseMass for each
// atom.
struct part *
readMMP(char *filename)
{
  struct part *p;
  struct mmpStream thisMMPStream, *mmp;
  char *tok;
  char bondOrder;
  char *name, *fontname, *junk;
  char *bodyName1;
  char *bodyName2;
  char *stationName1;
  char *stationName2;
  char *axisName1;
  char *axisName2;
  int fontsize;
  int elementType;
  int previousAtomID = -1; // ID of atom just defined, so we can back-reference to it in later lines
  struct jig *previousRotaryMotor = NULL; // for back-reference of info line setting initial_speed
  double initialSpeed;
  double dampingCoefficient;
  int dampingEnabled;
  double stall;
  double speed;
  double force;
  double stiffness;
  double temperature;
  double mass;
  double inertiaTensor[6];
  double quat[4];
  struct quaternion orientation;
  struct xyz position;
  struct xyz center;
  struct xyz axis;
  int atomListLength;
  int *atomList;
  int atomID; // atom number in mmp file
  int atomID2;
  int atomID3;
  int atomID4;
  int bondDirection;
  char *baseSequence;

  mmp = &thisMMPStream;
  mmp->fileName = filename;
  mmp->lineNumber = 1;
  mmp->charPosition = 1;
  mmp->f = fopen(filename, "r");
  if (mmp->f == NULL) {
    ERROR_ERRNO1("Could not open %s", mmp->fileName);
    mmp->lineNumber = 0;
    mmp->charPosition = 0;
    mmpParseError(mmp);
    return NULL;
  }

  p = makePart(filename, &mmpParseError, mmp);

  while ((tok = readToken(mmp, 1)) != NULL) {

    // atom atomNumber (element) (posx, posy, posz)
    // Identifies a new atom with the given element type and position.
    // Position vectors are integers with units of 0.1pm.
    if (!strcmp(tok, "atom")) {
      expectInt(mmp, &atomID, 0); BAILP();
      expectToken(mmp, "("); BAILP();
      expectInt(mmp, &elementType, 0); BAILP();
      expectToken(mmp, ")"); BAILP();
      expectXYZInts(mmp, &position); BAILP();
      consumeRestOfLine(mmp);
          
      // hack: change singlets to hydrogen
      if (elementType == 0) {
        elementType=1;
      }
      previousAtomID = atomID;

      // at this point, position is in pm (expectXYZInts converts)
      addAtom(p, makeAtom(p, atomID, elementType, position)); BAILP();
    }

    // after an atom:
    //  info atom atomtype = sp2
    // after an rmotor:
    //  info leaf initial_speed = 20.0
    else if (!strcmp(tok, "info")) {
      consumeWhitespace(mmp);
      tok = readToken(mmp, 0);
      if (!strcmp(tok, "atom")) {
        consumeWhitespace(mmp);
        tok = readToken(mmp, 0);
        if (!strcmp(tok, "atomtype")) {
          enum hybridization hybridization = sp3;
          
          consumeWhitespace(mmp);
          expectToken(mmp, "="); BAILP();
          consumeWhitespace(mmp);
          tok = readToken(mmp, 0);

          if (!strcmp(tok, "sp3d")) {
            hybridization = sp3d;
          } else if (!strcmp(tok, "sp3")) {
            hybridization = sp3;
          } else if (!strcmp(tok, "sp2(graphitic)")) {
            hybridization = sp2_g;
          } else if (!strcmp(tok, "sp2")) {
            hybridization = sp2;
          } else if (!strcmp(tok, "sp")) {
            hybridization = sp;
          } else {
            ERROR1("unknown hybridization: %s", tok);
            mmpParseError(mmp);
            BAILP();
          }

          consumeRestOfLine(mmp);

          setAtomHybridization(p, previousAtomID, hybridization); BAILP();
        }
      } else if (!strcmp(tok, "leaf")) {
        consumeWhitespace(mmp);
        tok = readToken(mmp, 0);
        if (!strcmp(tok, "initial_speed")) {
          consumeWhitespace(mmp);
          expectToken(mmp, "="); BAILP();
          expectDouble(mmp, &initialSpeed, 0); BAILP();
          consumeRestOfLine(mmp);

          if (previousRotaryMotor == NULL) {
            ERROR("setting initial_speed without previous rotary motor");
            mmpParseError(mmp);
            BAILP();
          }
          setInitialSpeed(previousRotaryMotor, initialSpeed);
        } else if (!strcmp(tok, "damping_coefficient")) {
          consumeWhitespace(mmp);
          expectToken(mmp, "="); BAILP();
          expectDouble(mmp, &dampingCoefficient, 0); BAILP();
          consumeRestOfLine(mmp);

          if (previousRotaryMotor == NULL) {
            ERROR("setting damping_coefficient without previous rotary motor");
            mmpParseError(mmp);
            BAILP();
          }
          setDampingCoefficient(previousRotaryMotor, dampingCoefficient);
        } else if (!strcmp(tok, "dampers_enabled")) {
          // info leaf dampers_enabled = False
          consumeWhitespace(mmp);
          expectToken(mmp, "="); BAILP();
          consumeWhitespace(mmp);
          tok = readToken(mmp, 0);
          dampingEnabled = strcmp(tok, "False") ? 1 : 0;
          consumeRestOfLine(mmp);

          if (previousRotaryMotor == NULL) {
            ERROR("setting dampers_enabled without previous rotary motor");
            mmpParseError(mmp);
            BAILP();
          }
          setDampingEnabled(previousRotaryMotor, dampingEnabled);
        }
      }
    }
  
    // bondO atno atno atno ...
    // Indicates bonds of order O between previous atom and listed
    // atoms.
    else if (!strncmp(tok, "bond", 4) && strlen(tok) == 5) {
      bondOrder = tok[4];
      // XXX should we accept zero length bond list?
      // XXX should we reject unknown bond orders?
      while (expectInt(mmp, &atomID, 1)) {
        addBond(p, makeBondFromIDs(p, previousAtomID, atomID, bondOrder));
        BAILP();
      }
    }

    // bond_direction atno atno
    // Indicates bond has direction from first to second atom
    else if (!strncmp(tok, "bond_direction", 14)) {
      expectInt(mmp, &atomID, 0);
      expectInt(mmp, &atomID2, 0);
      consumeRestOfLine(mmp);
      setBondDirection(p, atomID, atomID2); BAILP();
    }

    // bond_chain atno atno
    // Create a sequence of bonds between consecutive pairs of atoms
    // in given range.
    else if (!strcmp(tok, "bond_chain")) {
      expectInt(mmp, &atomID, 0);
      expectInt(mmp, &atomID2, 0);
      consumeRestOfLine(mmp);
      createBondChain(p, atomID, atomID2, 0, NULL); BAILP();
    }

    // directional_bond_chain atno atno direction [sequence]
    // Create a sequence of bonds between consecutive pairs of atoms
    // in given range.  Set their directions, and optionally apply DNA
    // sequence info to any PAM sugar atoms in the chain.
    else if (!strcmp(tok, "directional_bond_chain")) {
      expectInt(mmp, &atomID, 0);
      expectInt(mmp, &atomID2, 0);
      expectInt(mmp, &bondDirection, 0);
      baseSequence = readToken(mmp, 0);
      if (*baseSequence == '\n') {
        baseSequence = NULL;
      } else {
        consumeRestOfLine(mmp);
      }
      createBondChain(p, atomID, atomID2, bondDirection, baseSequence); BAILP();
    }

    // dna_rung_bonds atno atno atno atno
    // Create bonds between two sequences of atoms.
    else if (!strcmp(tok, "dna_rung_bonds")) {
      expectInt(mmp, &atomID, 0);
      expectInt(mmp, &atomID2, 0);
      expectInt(mmp, &atomID3, 0);
      expectInt(mmp, &atomID4, 0);
      consumeRestOfLine(mmp);
      createRungBonds(p, atomID, atomID2, atomID3, atomID4); BAILP();
    }
		
    // waals atno atno atno ...
    // Asks for van der Waals interactions between previous atom and
    // listed atoms.  Only needed if the given atoms are bonded.
    else if (!strcmp(tok, "waals")) {
      // XXX should we accept zero length vdw list?
      while (expectInt(mmp, &atomID, 1)) {
        makeVanDerWaals(p, previousAtomID, atomID); BAILP();
      }
      consumeRestOfLine(mmp);
    }
		
    // ground (<name>) (r, g, b) <atoms>
    // accept "anchor" as synonym for "ground" wware 051213
    else if (!strcmp(tok, "ground") ||
	     !strcmp(tok, "anchor")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      makeGround(p, name, atomListLength, atomList); BAILP();
    }
	
    // thermo (name) (r, g, b) <atom1> <atom2>
    // thermometer for atoms in range [atom1..atom2]
    else if (!strcmp(tok, "thermo")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectIntList(mmp, &atomList, &atomListLength, 3); BAILP(); // only interested in first two
      makeThermometer(p, name, atomList[0], atomList[1]); BAILP();
    }

    // mdihedral (name) (Fontname) <fontsize> <atom1> <atom2> <atom3> <atom4>
    // dihedral meter
    else if (!strcmp(tok, "mdihedral")) {
      name = expectName(mmp); BAILP();
      junk = expectName(mmp); BAILP(); // center of jig
      fontname = expectName(mmp); BAILP();
      free(junk);
      free(fontname);
      expectInt(mmp, &fontsize, 0); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 4); BAILP();
      makeDihedralMeter(p, name, atomList[0], atomList[1],
			atomList[2], atomList[3]); BAILP();
    }

    // mangle (name) (Fontname) <fontsize> <atom1> <atom2> <atom3>
    // angle meter
    else if (!strcmp(tok, "mangle")) {
      name = expectName(mmp); BAILP();
      junk = expectName(mmp); BAILP(); // center of jig
      fontname = expectName(mmp); BAILP();
      free(junk);
      free(fontname);
      expectInt(mmp, &fontsize, 0); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 3); BAILP();
      makeAngleMeter(p, name, atomList[0], atomList[1], atomList[2]); BAILP();
    }

    // mdistance (name) (Fontname) <fontsize> <atom1> <atom2>
    // radius meter
    else if (!strcmp(tok, "mdistance")) {
      name = expectName(mmp); BAILP();
      junk = expectName(mmp); BAILP(); // center of jig
      fontname = expectName(mmp); BAILP();
      free(junk);
      free(fontname);
      expectInt(mmp, &fontsize, 0); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 2); BAILP();
      makeRadiusMeter(p, name, atomList[0], atomList[1]); BAILP();
    }

    // stat (name) (r, g, b) (temp) <atom1> <atom2>
    // Langevin thermostat for atoms in range [atom1..atom2]
    else if (!strcmp(tok, "stat")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectToken(mmp, "("); BAILP();
      expectDouble(mmp, &temperature, 0); BAILP();
      expectToken(mmp, ")"); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 3); BAILP(); // only interested in first two
      makeThermostat(p, name, temperature, atomList[0], atomList[1]); BAILP();
    }

    // rmotor (name) (r,g,b) <torque> <speed> (<center>) (<axis>)
    // shaft atom...
    // rotary motor
    // stall torque in nN*nm
    // speed in gigahertz
    else if (!strcmp(tok, "rmotor")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectDouble(mmp, &stall, 0); BAILP();
      expectDouble(mmp, &speed, 0); BAILP();
      expectXYZInts(mmp, &center); BAILP();
      expectXYZInts(mmp, &axis); BAILP();
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft"); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      previousRotaryMotor = makeRotaryMotor(p, name, stall, speed, &center, &axis, atomListLength, atomList); BAILP();
    }

    /* lmotor (name) (r,g,b) <force> <stiff> (<center>) (<axis>) */
    // shaft atom...
    // linear motor
    // force in pN
    // stiffness in N/m
    else if (0==strcmp(tok, "lmotor")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectDouble(mmp, &force, 0); BAILP();
      expectDouble(mmp, &stiffness, 0); BAILP();
      expectXYZInts(mmp, &center); BAILP();
      expectXYZInts(mmp, &axis); BAILP();
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft"); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      makeLinearMotor(p, name, force, stiffness, &center, &axis, atomListLength, atomList); BAILP();
    }
		
    else if (!strncmp(tok, "end", 3)) {
      break;
    }

    // rigidBody (bodyName) (<position 3vector>) (<orientation quaternion>) <mass> (<inertia matrix 6 elements>)
    else if (0==strcmp(tok, "rigidBody")) {
      bodyName1 = expectName(mmp); BAILP();
      expectXYZInts(mmp, &center); BAILP(); // position
      expectNDoubles(mmp, 4, quat); BAILP(); // quaternion, orientation
      orientation.x = quat[0];
      orientation.y = quat[1];
      orientation.z = quat[2];
      orientation.a = quat[3];
      expectDouble(mmp, &mass, 0); BAILP();
      expectNDoubles(mmp, 6, inertiaTensor); BAILP(); // inertia matrix
      consumeRestOfLine(mmp);
      makeRigidBody(p, bodyName1, mass, inertiaTensor, center, orientation); BAILP();
    }

    // stationPoint (bodyName) (stationName) (<position 3vector>)
    else if (0==strcmp(tok, "stationPoint")) {
      bodyName1 = expectName(mmp); BAILP();
      stationName1 = expectName(mmp); BAILP();
      expectXYZInts(mmp, &center); BAILP();
      makeStationPoint(p, bodyName1, stationName1, center); BAILP();
      free(bodyName1);
    }

    // bodyAxis (bodyName) (axisName) (<axis 3vector>)
    else if (0==strcmp(tok, "bodyAxis")) {
      bodyName1 = expectName(mmp); BAILP();
      axisName1 = expectName(mmp); BAILP();
      expectXYZInts(mmp, &center); BAILP();
      makeBodyAxis(p, bodyName1, axisName1, center); BAILP();
      free(bodyName1);
    }

    // attachAtoms (bodyName) atomset...
    else if (0==strcmp(tok, "attachAtoms")) {
      bodyName1 = expectName(mmp); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      makeAtomAttachments(p, bodyName1, atomListLength, atomList); BAILP();
      free(bodyName1);
    }
    
    else if (0==strcmp(tok, "joint")) {
      consumeWhitespace(mmp);
      tok = readToken(mmp, 0);
      // joint Ball (bodyName1) (stationName1) (bodyName2) (stationName2)
      if (0==strcmp(tok, "Ball")) {
        bodyName1 = expectName(mmp); BAILP();
        stationName1 = expectName(mmp); BAILP();
        bodyName2 = expectName(mmp); BAILP();
        stationName2 = expectName(mmp); BAILP();
        consumeRestOfLine(mmp);
        makeBallJoint(p, bodyName1, stationName1, bodyName2, stationName2); BAILP();
        free(bodyName1);
        free(stationName1);
        free(bodyName2);
        free(stationName2);
      }
      // joint Hinge (bodyName1) (stationName1) (axisName1) (bodyName2) (stationName2) (axisName2)
      else if (0==strcmp(tok, "Hinge")) {
        bodyName1 = expectName(mmp); BAILP();
        stationName1 = expectName(mmp); BAILP();
        axisName1 = expectName(mmp); BAILP();
        bodyName2 = expectName(mmp); BAILP();
        stationName2 = expectName(mmp); BAILP();
        axisName2 = expectName(mmp); BAILP();
        consumeRestOfLine(mmp);
        makeHingeJoint(p, bodyName1, stationName1, axisName1, bodyName2, stationName2, axisName2); BAILP();
        free(bodyName1);
        free(stationName1);
        free(axisName1);
        free(bodyName2);
        free(stationName2);
        free(axisName2);
      }
      // joint Slider (bodyName1) (axisName1) (bodyName2) (axisName2)
      else if (0==strcmp(tok, "Slider")) {
        bodyName1 = expectName(mmp); BAILP();
        axisName1 = expectName(mmp); BAILP();
        bodyName2 = expectName(mmp); BAILP();
        axisName2 = expectName(mmp); BAILP();
        consumeRestOfLine(mmp);
        makeSliderJoint(p, bodyName1, axisName1, bodyName2, axisName2); BAILP();
        free(bodyName1);
        free(axisName1);
        free(bodyName2);
        free(axisName2);
      }

      else {
        ERROR1("Unrecognized joint type: %s", tok);
        mmpParseError(mmp);
        BAILP();
      }
    }
    
#if 0
    // XXX it looks like there isn't any code to implement this behavior
    // bearing 
    /* bearing (name) (r,g,b) (<center>) (<axis>) */
    else if (0==strcasecmp(tok, "bearing")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectXYZInts(mmp, &center); BAILP();
      expectXYZInts(mmp, &axis); BAILP();
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft"); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      makeBearing(p, name, &center, &axis, atomListLength, atomList); BAILP();
    }
		
    // spring
    /* spring <stiffness>, (<center1>) (<center2>) */
    else if (0==strcasecmp(tok, "spring")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectInt(mmp, &stiffness, 0); BAILP();
      expectXYZInts(mmp, &position); BAILP();
      expectXYZInts(mmp, &position2); BAILP();
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft"); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      makeSpring(p, name, stiffness, &position, &position2, atomListLength, atomList); BAILP();
    }
		
    // slider
    /* slider (<center>) (<axis>) */
    /* torque in nN*nm  speed in gigahertz */
    else if (0==strcasecmp(tok, "slider")) {
      name = expectName(mmp); BAILP();
      expectXYZInts(mmp, NULL); BAILP(); // ignore (rgb) triplet
      expectXYZInts(mmp, &center); BAILP();
      expectXYZInts(mmp, &axis); BAILP();
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft"); BAILP();
      expectIntList(mmp, &atomList, &atomListLength, 0); BAILP();
      makeSlider(p, name, &center, &axis, atomListLength, atomList); BAILP();
    }
    
    // kelvin <temperature>
    else if (0==strcasecmp(tok, "kelvin")) {
      consumeRestOfLine(mmp);
      // Temperature = (double)ix;
      // printf("Temperature set to %f\n",Temperature);
    }
#endif

    else if (tok[0] == '\r' || tok[0] == '\n') {
      // blank line, or second char of \r\n combo
      ;
    } else {
      DPRINT1(D_READER, "??? %s\n", tok);
      consumeRestOfLine(mmp);
    }
  }
  fclose(mmp->f);
  destroyAccumulator(tempBuffer);
  tempBuffer = NULL;

  return endPart(p);
}
