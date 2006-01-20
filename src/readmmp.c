
#include <limits.h>
#include "simulator.h"

struct mmpStream 
{
  FILE *f;
  char *fileName;
  int lineNumber;
  int charPosition;
};

// should be preceded by a call to ERROR() giving details
static void
mmpParseError(void *stream)
{
  // We cast from void * here so that the part routines can take a
  // generic error handler and user data pointer.
  struct mmpStream *mmp = (struct mmpStream *)stream;
  
  ERROR3("In mmp file %s, line %d, col %d", mmp->fileName, mmp->lineNumber, mmp->charPosition);
  done("Failed to parse mmp file");
  exit(1); // XXX should throw exception
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
readToken(struct mmpStream *mmp)
{
  char *s = tokenBuffer;

  if (feof(mmp->f) || ferror(mmp->f)) {
    return NULL;
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
        // XXX line numbering is off by a factor of 2 for files with
        // \r\n line termination
        if (*s == '\n' || *s == '\r') {
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
    return NULL;
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
    tok = readToken(mmp);
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
  
  tok = readToken(mmp);
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
  tok = readToken(mmp);
  if (value == NULL) {
    ERROR("internal error, value==NULL");
    mmpParseError(mmp);
  }
  if (tok != NULL) {
    if ((*tok == '\n' || *tok == '\r') && checkForNewline) {
      return 0;
    }
    if (*tok == '\0') {
      ERROR("expected int, got \\0");
      mmpParseError(mmp);
    }
    errno = 0;
    val = strtol(tok, &end, 0);
    if (errno != 0) {
      ERROR1("integer value out of range: %s", tok);
      mmpParseError(mmp);
    }
    if (*end != '\0') {
      ERROR1("expected int, got %s", tok);
      mmpParseError(mmp);
    }
    if (val > INT_MAX || val < INT_MIN) {
      ERROR1("integer value out of range: %s", tok);
      mmpParseError(mmp);
    }
    *value = val;
    consumeWhitespace(mmp);
    return 1;
  }
  ERROR("expected int, got EOF");
  mmpParseError(mmp);
  return 0; // not reached
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
  tok = readToken(mmp);
  if (value == NULL) {
    ERROR("internal error, value==NULL");
    mmpParseError(mmp);
  }
  if (tok != NULL) {
    if ((*tok == '\n' || *tok == '\r') && checkForNewline) {
      return 0;
    }
    if (*tok == '\0') {
      ERROR("expected double, got \\0");
      mmpParseError(mmp);
    }
    errno = 0;
    val = strtod(tok, &end);
    if (errno != 0) {
      ERROR1("double value out of range: %s", tok);
      mmpParseError(mmp);
    }
    if (*end != '\0') {
      ERROR1("expected double, got %s", tok);
      mmpParseError(mmp);
    }
    *value = val;
    consumeWhitespace(mmp);
    return 1;
  }
  ERROR("expected double, got EOF");
  mmpParseError(mmp);
  return 0; // not reached
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
  expectToken(mmp, "(");
  expectInt(mmp, &x, 0);
  expectToken(mmp, ",");
  expectInt(mmp, &y, 0);
  expectToken(mmp, ",");
  expectInt(mmp, &z, 0);
  expectToken(mmp, ")");
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
  expectToken(mmp, "(");
  len = 0;
  tempBuffer = accumulator(tempBuffer, len + 1, 0);
  buf = (char *)tempBuffer;
  buf[len] = '\0';
  while ((tok = readToken(mmp)) != NULL) {
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
    }
    len += strlen(tok);
    tempBuffer = accumulator(tempBuffer, len + 1, 0);
    buf = (char *)tempBuffer;
    strcat(buf, tok);
  }
  ERROR("reading name, expected ), got EOF");
  mmpParseError(mmp);
  return ""; // not reached
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
  if (index == 0) {
    ERROR("zero length list of atoms");
    mmpParseError(mmp);
  }
  if (expectedLength != 0 && expectedLength != index) {
    ERROR2("expected exactly %d atoms, got %d", expectedLength, index);
    mmpParseError(mmp);
  }
  *length = index;
  *listPtr = buf;
}


struct part *
readMMP(char *filename)
{
  struct part *p;
  struct mmpStream thisMMPStream, *mmp;
  char *tok;
  char bondOrder;
  char *name, *fontname, *junk;
  int fontsize;
  int elementType;
  int previousAtomID = -1; // ID of atom just defined, so we can back-reference to it in later lines
  double stall;
  double speed;
  double force;
  double stiffness;
  double temperature;
  struct xyz position;
  struct xyz center;
  struct xyz axis;
  int atomListLength;
  int *atomList;
  int atomID; // atom number in mmp file

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
  }

  p = makePart(filename, &mmpParseError, mmp);

  while ((tok = readToken(mmp)) != NULL) {

    // atom atomNumber (element) (posx, posy, posz)
    // Identifies a new atom with the given element type and position.
    // Position vectors are integers with units of 0.1pm.
    if (!strcmp(tok, "atom")) {
      expectInt(mmp, &atomID, 0);
      expectToken(mmp, "(");
      expectInt(mmp, &elementType, 0);
      expectToken(mmp, ")");
      expectXYZInts(mmp, &position);
      consumeRestOfLine(mmp);
          
      // hack: change singlets to hydrogen
      // if (elementType == 0) elementType=1;
      previousAtomID = atomID;
			
      makeAtom(p, atomID, elementType, position);
    }
    
    // info atom atomtype = sp2
    else if (!strcmp(tok, "info")) {
      consumeWhitespace(mmp);
      tok = readToken(mmp);
      if (!strcmp(tok, "atom")) {
        consumeWhitespace(mmp);
        tok = readToken(mmp);
        if (!strcmp(tok, "atomtype")) {
          enum hybridization hybridization;
          
          consumeWhitespace(mmp);
          expectToken(mmp, "=");
          consumeWhitespace(mmp);
          tok = readToken(mmp);

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
          }

          consumeRestOfLine(mmp);

          setAtomHybridization(p, previousAtomID, hybridization);
        }
      }
    }

    // bondO atno atno atno ...
    // Indicates bonds of order O between previous atom and listed
    // atoms.
    else if (!strncmp(tok, "bond", 4)) {
      bondOrder = tok[4];
      // XXX should we accept zero length bond list?
      // XXX should we reject unknown bond orders?
      while (expectInt(mmp, &atomID, 1)) {
        makeBond(p, previousAtomID, atomID, bondOrder);
      }
    }
		
    // waals atno atno atno ...
    // Asks for van der Waals interactions between previous atom and
    // listed atoms.  Only needed if the given atoms are bonded.
    else if (!strcmp(tok, "waals")) {
      // XXX should we accept zero length vdw list?
      while (expectInt(mmp, &atomID, 1)) {
        makeVanDerWaals(p, previousAtomID, atomID);
      }
    }
		
    // ground (<name>) (r, g, b) <atoms>
    // accept "anchor" as synonym for "ground" wware 051213
    else if (!strcmp(tok, "ground") ||
	     !strcmp(tok, "anchor")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectIntList(mmp, &atomList, &atomListLength, 0);
      makeGround(p, name, atomListLength, atomList);
    }
	
    // thermo (name) (r, g, b) <atom1> <atom2>
    // thermometer for atoms in range [atom1..atom2]
    else if (!strcmp(tok, "thermo")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectIntList(mmp, &atomList, &atomListLength, 3); // only interested in first two
      makeThermometer(p, name, atomList[0], atomList[1]);
    }

    // mdihedral (name) (Fontname) <fontsize> <atom1> <atom2> <atom3> <atom4>
    // dihedral meter
    else if (!strcmp(tok, "mdihedral")) {
      name = expectName(mmp);
      junk = expectName(mmp); // center of jig
      fontname = expectName(mmp);
      expectInt(mmp, &fontsize, 0);
      expectIntList(mmp, &atomList, &atomListLength, 4);
      makeDihedralMeter(p, name, atomList[0], atomList[1],
			atomList[2], atomList[3]);
    }

    // mangle (name) (Fontname) <fontsize> <atom1> <atom2> <atom3>
    // angle meter
    else if (!strcmp(tok, "mangle")) {
      name = expectName(mmp);
      junk = expectName(mmp); // center of jig
      fontname = expectName(mmp);
      expectInt(mmp, &fontsize, 0);
      expectIntList(mmp, &atomList, &atomListLength, 3);
      makeAngleMeter(p, name, atomList[0], atomList[1], atomList[2]);
    }

    // mdistance (name) (Fontname) <fontsize> <atom1> <atom2>
    // radius meter
    else if (!strcmp(tok, "mdistance")) {
      name = expectName(mmp);
      junk = expectName(mmp); // center of jig
      fontname = expectName(mmp);
      expectInt(mmp, &fontsize, 0);
      expectIntList(mmp, &atomList, &atomListLength, 2);
      makeRadiusMeter(p, name, atomList[0], atomList[1]);
    }

    // stat (name) (r, g, b) (temp) <atom1> <atom2>
    // Langevin thermostat for atoms in range [atom1..atom2]
    else if (!strcmp(tok, "stat")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectToken(mmp, "(");
      expectDouble(mmp, &temperature, 0);
      expectToken(mmp, ")");
      expectIntList(mmp, &atomList, &atomListLength, 3); // only interested in first two
      makeThermostat(p, name, temperature, atomList[0], atomList[1]);
    }

    // rmotor (name) (r,g,b) <torque> <speed> (<center>) (<axis>)
    // shaft atom...
    // rotary motor
    // torque in nN*nm  speed in gigahertz */
    else if (!strcmp(tok, "rmotor")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectDouble(mmp, &stall, 0);
      expectDouble(mmp, &speed, 0);
      expectXYZInts(mmp, &center);
      expectXYZInts(mmp, &axis);
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft");
      expectIntList(mmp, &atomList, &atomListLength, 0);
      makeRotaryMotor(p, name, stall, speed, &center, &axis, atomListLength, atomList);
    }

    /* lmotor (name) (r,g,b) <force> <stiff> (<center>) (<axis>) */
    // shaft atom...
    // linear motor
    else if (0==strcmp(tok, "lmotor")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectDouble(mmp, &force, 0);
      expectDouble(mmp, &stiffness, 0);
      expectXYZInts(mmp, &center);
      expectXYZInts(mmp, &axis);
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft");
      expectIntList(mmp, &atomList, &atomListLength, 0);
      makeLinearMotor(p, name, force, stiffness, &center, &axis, atomListLength, atomList);
    }
		
    else if (!strcmp(tok, "end")) {
      consumeRestOfLine(mmp);
      break;
    }

#if 0
    // XXX it looks like there isn't any code to implement this behavior
    // bearing 
    /* bearing (name) (r,g,b) (<center>) (<axis>) */
    else if (0==strcasecmp(tok, "bearing")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectXYZInts(mmp, &center);
      expectXYZInts(mmp, &axis);
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft");
      expectIntList(mmp, &atomList, &atomListLength, 0);
      makeBearing(p, name, &center, &axis, atomListLength, atomList);
    }
		
    // spring
    /* spring <stiffness>, (<center1>) (<center2>) */
    else if (0==strcasecmp(tok, "spring")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectInt(mmp, &stiffness, 0);
      expectXYZInts(mmp, &position);
      expectXYZInts(mmp, &position2);
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft");
      expectIntList(mmp, &atomList, &atomListLength, 0);
      makeSpring(p, name, stiffness, &position, &position2, atomListLength, atomList);
    }
		
    // slider
    /* slider (<center>) (<axis>) */
    /* torque in nN*nm  speed in gigahertz */
    else if (0==strcasecmp(tok, "slider")) {
      name = expectName(mmp);
      expectXYZInts(mmp, NULL); // ignore (rgb) triplet
      expectXYZInts(mmp, &center);
      expectXYZInts(mmp, &axis);
      consumeRestOfLine(mmp);
      expectToken(mmp, "shaft");
      expectIntList(mmp, &atomList, &atomListLength, 0);
      makeSlider(p, name, &center, &axis, atomListLength, atomList);
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

  return endPart(p);
}
