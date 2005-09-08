
#include <limits.h>
#include "simulator.h"

static int lineNumber;
static int charPosition;
static char *mmpFileName;
static char tokenBuffer[256];

static void
die()
{
  doneExit(1, tracef, "Failed to parse mmp file");
}

// should be followed by a call to ERROR() giving details
static void
mmpParseError()
{
  ERROR("Parsing mmp file %s, line %d, col %d", mmpFileName, lineNumber, charPosition);
}


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
readToken(FILE *f)
{
  char *s = tokenBuffer;

  if (feof(f) || ferror(f)) {
    return NULL;
  }
  while ((*s = fgetc(f)) != EOF) {
    charPosition++;
    switch (*s) {
    case ' ':
    case '(':
    case ')':
    case ',':
    case ';':
    case '=':
    case '\n':
    case '\0':
      if (s == tokenBuffer) {
        if (*s == '\n') {
          lineNumber++;
          charPosition = 1;
        }
        s++;
      } else {
        ungetc(*s, f);
        charPosition--;
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
consumeWhitespace(FILE *f)
{
  int c;
  
  if (feof(f) || ferror(f)) {
    return;
  }
  while ((c = fgetc(f)) != EOF) {
    charPosition++;
    switch (c) {
    case ' ':
    case '\t':
      break;
    default:
      ungetc(c, f);
      charPosition--;
      return;
    }
  }
}

// Ignores the remainder of this line.
static void
consumeRestOfLine(FILE *f)
{
  char *tok;

  while (1) {
    tok = readToken(f);
    if (tok == NULL || *tok == '\n') {
      return;
    }
  }
}

// Complains and dies if the next token is not the expected token.
// Pass in NULL to expect EOF.
static int
expectToken(FILE *f, char *expected)
{
  char *tok;
  int ret;
  
  tok = readToken(f);
  if (tok == NULL) {
    ret = expected == NULL;
  } else if (expected == NULL) {
    ret = tok == NULL;
  } else {
    ret = !strcmp(tok, expected);
  }
  if (!ret) {
    mmpParseError();
    ERROR("expected %s, got %s", expected ? expected : "EOF", tok ? tok : "EOF");
    die();
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
expectInt(FILE *f, int *value, int checkForNewline)
{
  char *tok;
  char *end;
  long int val;

  consumeWhitespace(f);
  tok = readToken(f);
  if (value == NULL) {
    ERROR("internal error, value==NULL");
    die();
  }
  if (tok != NULL) {
    if (*tok == '\n' && checkForNewline) {
      return 0;
    }
    if (*tok == '\0') {
      mmpParseError();
      ERROR("expected int, got \\0");
      die();
    }
    errno = 0;
    val = strtol(tok, &end, 0);
    if (errno != 0) {
      mmpParseError();
      ERROR("integer value out of range: %s", tok);
      die();
    }
    if (*end != '\0') {
      mmpParseError();
      ERROR("expected int, got %s", tok);
      die();
    }
    if (val > INT_MAX || val < INT_MIN) {
      mmpParseError();
      ERROR("integer value out of range: %s", tok);
      die();
    }
    *value = val;
    consumeWhitespace(f);
    return 1;
  }
  mmpParseError();
  ERROR("expected int, got EOF");
  die();
}

// Parse a double.  Returns 1 if value was successfully filled in
// with a double value.  If checkForNewline is true, and a newline
// was encountered instead of a double the newline is consumed and 0
// is returned.
//
// Any whitespace before and after the double is consumed.
static int
expectDouble(FILE *f, double *value, int checkForNewline)
{
  char *tok;
  char *end;
  double val;

  consumeWhitespace(f);
  tok = readToken(f);
  if (value == NULL) {
    ERROR("internal error, value==NULL");
    die();
  }
  if (tok != NULL) {
    if (*tok == '\n' && checkForNewline) {
      return 0;
    }
    if (*tok == '\0') {
      mmpParseError();
      ERROR("expected double, got \\0");
      die();
    }
    errno = 0;
    val = strtod(tok, &end);
    if (errno != 0) {
      mmpParseError();
      ERROR("double value out of range: %s", tok);
      die();
    }
    if (*end != '\0') {
      mmpParseError();
      ERROR("expected double, got %s", tok);
      die();
    }
    *value = val;
    consumeWhitespace(f);
    return 1;
  }
  mmpParseError();
  ERROR("expected double, got EOF");
  die();
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
expectXYZInts(FILE *f, struct xyz *p)
{
  int x;
  int y;
  int z;

  consumeWhitespace(f);
  expectToken(f, "(");
  expectInt(f, &x, 0);
  expectToken(f, ",");
  expectInt(f, &y, 0);
  expectToken(f, ",");
  expectInt(f, &z, 0);
  expectToken(f, ")");
  consumeWhitespace(f);

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
expectName(FILE *f)
{
  char *tok;
  char *buf;
  int len;
  
  consumeWhitespace(f);
  expectToken(f, "(");
  len = 0;
  tempBuffer = accumulator(tempBuffer, len + 1, 0);
  buf = (char *)tempBuffer;
  buf[len] = '\0';
  while ((tok = readToken(f)) != NULL) {
    if (!strcmp(tok, ")")) {
      consumeWhitespace(f);
      return copy_string(buf);
    }
    if (*tok == '\0') {
      tok = "%00";
    }
    if (*tok == '\n') {
      mmpParseError();
      ERROR("reading name, expected ), got newline");
      die();
    }
    len += strlen(tok);
    tempBuffer = accumulator(tempBuffer, len + 1, 0);
    buf = (char *)tempBuffer;
    strcat(buf, tok);
  }
  mmpParseError();
  ERROR("reading name, expected ), got EOF");
  die();
}

// Parses a list of integers terminated by a newline.  An arbitrary
// number of integers can be parsed, and the freshly allocated result
// is stored in listPtr, with the length stored in length.  If
// expectedLength is non-zero, complains and dies if the actual length
// is not expectedLength.  Also complains and dies for zero length
// lists.
static void
expectIntList(FILE *f, int **listPtr, int *length, int expectedLength)
{
  int *buf;
  int index;
  int len;
  int listElement;
  
  len = 0;
  tempBuffer = accumulator(tempBuffer, len, 0);
  buf = (int *)tempBuffer;
  index = 0;
  while (expectInt(f, &listElement, 1)) {
    len += sizeof(int);
    tempBuffer = accumulator(tempBuffer, len, 0);
    buf = (int *)tempBuffer;
    buf[index++] = listElement;
  }
  if (index == 0) {
    mmpParseError();
    ERROR("zero length list of atoms");
    die();
  }
  if (expectedLength != 0 && expectedLength != index) {
    mmpParseError();
    ERROR("expected exactly %d atoms, got %d", expectedLength, index);
    die();
  }
  *length = index;
  *listPtr = (int *)copy_memory(buf, len);
}

// Translates atom numbers (as stored and referenced in mmp files)
// into atom indexes, which are sequential numbers allocated as the
// atoms appear in an mmp file.
static void
translateAtomNumbers(int atomListLength, int *atomList,
                     int *atomNumberList, int maxAtomNumber)
{
  int i;
  int atomIndex;
  
  for (i=0; i<atomListLength; i++) {
    if (atomList[i] < 0 || atomList[i] > maxAtomNumber) {
      mmpParseError();
      ERROR("atom number %d out of range [0, %d]", atomList[i], maxAtomNumber);
      die();
    }
    atomIndex = atomNumberList[atomList[i]] - 1;
    if (atomIndex < 0) {
      mmpParseError();
      ERROR("atom number %d not yet encountered", atomList[i]);
      die();
    }
    atomList[i] = atomIndex;
  }
}

static int
translateAtomNumber(int atomNumber, int *atomNumberList, int maxAtomNumber)
{
  int atomIndex;
  
  if (atomNumber < 0 || atomNumber > maxAtomNumber) {
    mmpParseError();
    ERROR("atom number %d out of range [0, %d]", atomNumber, maxAtomNumber);
    die();
  }
  atomIndex = atomNumberList[atomNumber] - 1;
  if (atomIndex < 0) {
    mmpParseError();
    ERROR("atom number %d not yet encountered", atomNumber);
    die();
  }
  return atomIndex;
}


void
readMMP(char *filename)
{
  FILE *f;
  char *tok;
  char bondOrder;
  int i;
  int m;
  int n;
  char *name;
  int element;
  int lastatom; // index of atom just defined, so we can back-reference to it in later lines
  double stall, speed, force, stiff;
  double temperature;
  struct xyz vec1, vec2;
  int atomListLength;
  int *atomList;
  int atomNumber; // identifier in mmp file
  int *atomNumberList = NULL; // translates atom numbers (read from mmp file) into indexes into atom array
  int maxAtomNumber = -1;
    
  f = fopen(filename, "r");
  if (f == NULL) {
    perror(filename);
    exit(1);
  }
  mmpFileName = filename;
  lineNumber = 1;
  charPosition = 1;

  while ((tok = readToken(f)) != NULL) {

    // atom atomNumber (element) (posx, posy, posz)
    // Identifies a new atom with the given element type and position.
    // Position vectors are integers with units of 0.1pm.
    if (!strcmp(tok, "atom")) {
      expectInt(f, &atomNumber, 0);
      expectToken(f, "(");
      expectInt(f, &element, 0);
      expectToken(f, ")");
      expectXYZInts(f, &vec1);
      consumeRestOfLine(f);
          
      // hack: change singlets to hydrogen
      // if (element == 0) element=1;

      if (atomNumber > maxAtomNumber) {
        maxAtomNumber = atomNumber;
        atomNumberList = (int *)accumulator(atomNumberList, (maxAtomNumber+1)*sizeof(int), 1);
      }
      // add one so that the automatic zeroing of the accumulator produces invalid entries
      atomNumberList[atomNumber]=Nexatom+1;
      lastatom = Nexatom;
			
      makatom(element, vec1);
    }

    // bondO atno atno atno ...
    // Indicates bonds of order O between previous atom and listed
    // atoms.
    else if (!strncmp(tok, "bond", 4)) {
      bondOrder = tok[4];
      // XXX should we accept zero length bond list?
      // XXX should we reject unknown bond orders?
      while (expectInt(f, &atomNumber, 1)) {
        makbond(lastatom, translateAtomNumber(atomNumber, atomNumberList, maxAtomNumber), bondOrder);
      }
    }
		
    // waals atno atno atno ...
    // Asks for van Der Waals interactions between previous atom and
    // listed atoms.  Only needed if the given atoms are bonded.
    else if (!strcmp(tok, "waals")) {
      // XXX should we accept zero length vdw list?
      while (expectInt(f, &atomNumber, 1)) {
        makvdw(lastatom, translateAtomNumber(atomNumber, atomNumberList, maxAtomNumber));
      }
    }
		
    // ground (<name>) (r, g, b) <atoms>
    else if (!strcmp(tok, "ground")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectIntList(f, &atomList, &atomListLength, 0);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEground, NULL, atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      Constraint[i].name = name;
    }
	
    // thermo (name) (r, g, b) <atom1> <atom2>
    // thermometer for atoms in range [atom1..atom2]
    else if (!strcmp(tok, "thermo")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectIntList(f, &atomList, &atomListLength, 3); // only interested in first two
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEtemp, NULL, atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      Constraint[i].name = name;
    }

    // angle (name) <atom1> <atom2> <atom3>
    // angle meter
    else if (!strcmp(tok, "angle")) {
      name = expectName(f);
      expectIntList(f, &atomList, &atomListLength, 3);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEangle, NULL, atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      Constraint[i].name = name;
    }

    // radius (name) <atom1> <atom2>
    // radius meter
    else if (!strcmp(tok, "radius")) {
      name = expectName(f);
      expectIntList(f, &atomList, &atomListLength, 2);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEradius, NULL, atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      Constraint[i].name = name;
    }

    // stat (name) (r, g, b) (temp) <atom1> <atom2>
    // Langevin thermostat for atoms in range [atom1..atom2]
    else if (!strcmp(tok, "stat")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectToken(f, "(");
      expectDouble(f, &temperature, 0);
      expectToken(f, ")");
      expectIntList(f, &atomList, &atomListLength, 3); // only interested in first two
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEstat, NULL, atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      Constraint[i].temp = temperature;
      Constraint[i].name = name;
    }

    // rmotor (name) (r,g,b) <torque> <speed> (<center>) (<axis>)
    // shaft atom...
    // rotary motor
    // torque in nN*nm  speed in gigahertz */
    else if (!strcmp(tok, "rmotor")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectDouble(f, &stall, 0);
      expectDouble(f, &speed, 0);
      expectXYZInts(f, &vec1);
      expectXYZInts(f, &vec2);
      consumeRestOfLine(f);
      expectToken(f, "shaft");
      expectIntList(f, &atomList, &atomListLength, 0);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEmotor, makmot(stall, speed, vec1, vec2), atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      makmot2(i);
      Constraint[i].name = name;
    }

    /* lmotor (name) (r,g,b) <force> <stiff> (<center>) (<axis>) */
    // shaft atom...
    // linear motor
    else if (0==strcasecmp(tok, "lmotor")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectDouble(f, &force, 0);
      expectDouble(f, &stiff, 0);
      expectXYZInts(f, &vec1);
      expectXYZInts(f, &vec2);
      consumeRestOfLine(f);
      expectToken(f, "shaft");
      expectIntList(f, &atomList, &atomListLength, 0);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODElmotor, maklmot(force, stiff, vec1, vec2), atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      maklmot2(i);
      Constraint[i].name = name;
    }
		
    else if (!strcmp(tok, "end")) {
      consumeRestOfLine(f);
      break;
    }

#if 0
    // XXX it looks like there isn't any code to implement this behavior
    // bearing 
    /* bearing (name) (r,g,b) (<center>) (<axis>) */
    else if (0==strcasecmp(tok, "bearing")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectXYZInts(f, &vec1);
      expectXYZInts(f, &vec2);
      consumeRestOfLine(f);
      expectToken(f, "shaft");
      expectIntList(f, &atomList, &atomListLength, 0);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEbearing, makmot(0.0, 0.0, vec1, vec2), atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      makmot2(i);
      Constraint[i].name = name;
    }
		
    // spring
    /* spring <stiffness>, (<center1>) (<center2>) */
    else if (0==strcasecmp(tok, "spring")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectInt(f, &stall, 0);
      expectInt(f, &speed, 0);
      expectXYZInts(f, &vec1);
      expectXYZInts(f, &vec2);
      consumeRestOfLine(f);
      expectToken(f, "shaft");
      expectIntList(f, &atomList, &atomListLength, 0);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEspring, makmot(stall, speed, vec1, vec2), atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      makmot2(i);
      Constraint[i].name = name;
    }
		
    // slider
    /* slider (<center>) (<axis>) */
    /* torque in nN*nm  speed in gigahertz */
    else if (0==strcasecmp(tok, "slider")) {
      name = expectName(f);
      expectXYZInts(f, NULL); // ignore (rgb) triplet
      expectInt(f, &stall, 0);
      expectInt(f, &speed, 0);
      expectXYZInts(f, &vec1);
      expectXYZInts(f, &vec2);
      consumeRestOfLine(f);
      expectToken(f, "shaft");
      expectIntList(f, &atomList, &atomListLength, 0);
      translateAtomNumbers(atomListLength, atomList, atomNumberList, maxAtomNumber);
      i=makcon(CODEslider, makmot(stall, speed, vec1, vec2), atomListLength, atomList);
      // note, current makcon allocates and copies, so we free
      free(atomList);
      makmot2(i);
      Constraint[i].name = name;
    }
    
    // kelvin <temperature>
    else if (0==strcasecmp(tok, "kelvin")) {
      consumeRestOfLine(f);
      // Temperature = (double)ix;
      // printf("Temperature set to %f\n",Temperature);
    }
#endif

    else {
      DPRINT(D_READER, "??? %s\n", tok);
      consumeRestOfLine(f);
    }
  }
  fclose(f);

  /* got all the static vdW bonds we'll see */
  Dynobuf = Nexvanbuf;
  Dynoix = Nexvanbuf->fill;
	
  /* create bending bonds */
  for (i=0; i<Nexatom; i++) {
    for (m=0; m<atom[i].nbonds-1; m++) {
      for (n=m+1; n<atom[i].nbonds; n++) {
        checkatom(stderr, i); // move outside of m loop?
        maktorq(i, atom[i].bonds[m], atom[i].bonds[n]);
      }
    }
  }

  // total velocity
  vmul2c(vec1,P,1.0/totMass);
  for (i=1; i<Nexatom; i++) {
    vadd(OldPositions[i],vec1);
  }
}
