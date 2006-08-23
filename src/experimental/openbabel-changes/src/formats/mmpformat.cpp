/**********************************************************************
Copyright (C) 2006 Nanorex, Inc.
 
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
***********************************************************************/

#include "babelconfig.h"
#include "mol.h"
#include "obconversion.h"
#include "obmolecformat.h"
#include <errno.h>

#include <vector>
#include <map>

#include <sstream>

#define UNIMPLEMENTED
#define UNTESTED

static int atom_index = 1;
static int bond_index = 1;

#define ERROR(fmt) fprintf(stderr, "%s:%d ", __FILE__, __LINE__); fprintf(stderr, fmt)
#define ERROR1(fmt,a) fprintf(stderr, "%s:%d ", __FILE__, __LINE__); fprintf(stderr, fmt, a)
#define ERROR2(fmt,a,b) fprintf(stderr, "%s:%d ", __FILE__, __LINE__); fprintf(stderr, fmt, a, b)
#define ERROR3(fmt,a,b,c) fprintf(stderr, "%s:%d ", __FILE__, __LINE__); fprintf(stderr, fmt, a, b, c)

//#define OUCH()  throw
#define OUCH()  fprintf(stderr, "TROUBLE %s %d\n", __FILE__, __LINE__)

using namespace std;
namespace OpenBabel
{

    static char __line[2000], *__p;

    struct MMPinfo
    {
	int lineNumber;
	int charPosition;
    };

    // should be preceded by a call to ERROR() giving details
    static void
    mmpParseError(struct MMPinfo *mmpInfo)
    {
	fprintf(stderr, "MMP file line %d, col %d\n", mmpInfo->lineNumber, mmpInfo->charPosition);
    }

    enum hybridization {
	sp,
	sp2,
	sp2_g, // graphitic
	sp3,
	sp3d
    };

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
    readToken(istream& mmp, struct MMPinfo *mmpInfo)
    {
	char *s = tokenBuffer;

	if (mmp.eof() || mmp.bad()) {
	    return NULL;
	}
	while (!mmp.eof()) {
	    mmp.get((char &)s[0]);
	    mmpInfo->charPosition++;
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
			mmpInfo->lineNumber++;
			mmpInfo->charPosition = 1;
		    }
		    s++;
		} else {
		    mmp.unget();
		    mmpInfo->charPosition--;
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
    consumeWhitespace(istream& mmp, struct MMPinfo *mmpInfo)
    {
	char c;

	if (mmp.eof() || mmp.bad()) {
	    return;
	}
	while (!mmp.eof()) {
	    mmp.get(c);
	    mmpInfo->charPosition++;
	    switch (c) {
	    case ' ':
	    case '\t':
		break;
	    default:
		mmp.unget();
		mmpInfo->charPosition--;
		return;
	    }
	}
    }

    // Ignores the remainder of this line.
    static void
    consumeRestOfLine(istream& mmp, struct MMPinfo *mmpInfo)
    {
	char *tok;

	while (1) {
	    tok = readToken(mmp, mmpInfo);
	    if (tok == NULL || *tok == '\n' || *tok == '\r') {
		return;
	    }
	}
    }

    // Complains and dies if the next token is not the expected token.
    // Pass in NULL to expect EOF.
    static int
    expectToken(istream& mmp, struct MMPinfo *mmpInfo, char *expected)
    {
	char *tok;
	int ret;

	tok = readToken(mmp, mmpInfo);
	if (tok == NULL) {
	    ret = expected == NULL;
	} else if (expected == NULL) {
	    ret = tok == NULL;
	} else {
	    ret = !strcmp(tok, expected);
	}
	if (!ret) {
	    ERROR2("expected \"%s\", got \"%s\"\n", expected ? expected : "EOF", tok ? tok : "EOF");
	    mmpParseError(mmpInfo);
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
    expectInt(istream& mmp, struct MMPinfo *mmpInfo, int *value, int checkForNewline)
    {
	char *tok;
	char *end;
	long int val;

	consumeWhitespace(mmp, mmpInfo);
	tok = readToken(mmp, mmpInfo);
	if (value == NULL) {
	    ERROR("internal error, value==NULL");
	    mmpParseError(mmpInfo);
	}
	if (tok != NULL) {
	    if ((*tok == '\n' || *tok == '\r') && checkForNewline) {
		return 0;
	    }
	    if (*tok == '\0') {
		ERROR("expected int, got \\0\n");
		mmpParseError(mmpInfo);
	    }
	    errno = 0;
	    val = strtol(tok, &end, 0);
	    if (errno != 0) {
		ERROR1("integer value out of range: \"%s\"\n", tok);
		mmpParseError(mmpInfo);
	    }
	    if (*end != '\0') {
		ERROR1("expected int, got \"%s\"\n", tok);
		mmpParseError(mmpInfo);
	    }
	    if (val > INT_MAX || val < INT_MIN) {
		ERROR1("integer value out of range: \"%s\"\n", tok);
		mmpParseError(mmpInfo);
	    }
	    *value = val;
	    consumeWhitespace(mmp, mmpInfo);
	    return 1;
	}
	ERROR("expected int, got EOF\n");
	mmpParseError(mmpInfo);
	return 0; // not reached
    }

    // Parse a double.  Returns 1 if value was successfully filled in
    // with a double value.  If checkForNewline is true, and a newline
    // was encountered instead of a double the newline is consumed and 0
    // is returned.
    //
    // Any whitespace before and after the double is consumed.
    static int
    expectDouble(istream& mmp, struct MMPinfo *mmpInfo, double *value, int checkForNewline)
    {
	char *tok;
	char *end;
	double val;

	consumeWhitespace(mmp, mmpInfo);
	tok = readToken(mmp, mmpInfo);
	if (value == NULL) {
	    ERROR("internal error, value==NULL");
	    mmpParseError(mmpInfo);
	}
	if (tok != NULL) {
	    if ((*tok == '\n' || *tok == '\r') && checkForNewline) {
		return 0;
	    }
	    if (*tok == '\0') {
		ERROR("expected double, got \\0");
		mmpParseError(mmpInfo);
	    }
	    errno = 0;
	    val = strtod(tok, &end);
	    if (errno != 0) {
		ERROR1("double value out of range: %s", tok);
		mmpParseError(mmpInfo);
	    }
	    if (*end != '\0') {
		ERROR1("expected double, got %s", tok);
		mmpParseError(mmpInfo);
	    }
	    *value = val;
	    consumeWhitespace(mmp, mmpInfo);
	    return 1;
	}
	ERROR("expected double, got EOF");
	mmpParseError(mmpInfo);
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
    static vector3
    expectXYZInts(istream& mmp, struct MMPinfo *mmpInfo)
    {
	int x;
	int y;
	int z;

	consumeWhitespace(mmp, mmpInfo);
	expectToken(mmp, mmpInfo, "(");
	expectInt(mmp, mmpInfo, &x, 0);
	expectToken(mmp, mmpInfo, ",");
	expectInt(mmp, mmpInfo, &y, 0);
	expectToken(mmp, mmpInfo, ",");
	expectInt(mmp, mmpInfo, &z, 0);
	expectToken(mmp, mmpInfo, ")");
	consumeWhitespace(mmp, mmpInfo);
	return vector3(x * 0.001, y * 0.001, z * 0.001);
    }

    static char tempBuffer[1000];

    char *
    copy_string(char *s)
    {
	int n = strlen(s)+1;
	char *ret = (char *)malloc(n);
	if (ret == NULL) {
	    fprintf(stderr, "Out of memory\n");
	    exit(1);
	}
	return strcpy(ret, s);
    }

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
    expectName(istream& mmp, struct MMPinfo *mmpInfo)
    {
	char *tok;
	char *buf;
	int len;

	consumeWhitespace(mmp, mmpInfo);
	expectToken(mmp, mmpInfo, "(");
	len = 0;
	buf = (char *)tempBuffer;
	buf[len] = '\0';
	while ((tok = readToken(mmp, mmpInfo)) != NULL) {
	    if (!strcmp(tok, ")")) {
		consumeWhitespace(mmp, mmpInfo);
		return copy_string(buf);
	    }
	    if (*tok == '\0') {
		tok = "%00";
	    }
	    if (*tok == '\n' || *tok == '\r') {
		ERROR("reading name, expected ), got newline");
		mmpParseError(mmpInfo);
	    }
	    len += strlen(tok);
	    buf = (char *)tempBuffer;
	    strcat(buf, tok);
	}
	ERROR("reading name, expected ), got EOF");
	mmpParseError(mmpInfo);
	return ""; // not reached
    }

    // Parses a list of integers terminated by a newline.  An arbitrary
    // number of integers can be parsed, and the accumulator they are
    // stored in is placed in listPtr, with the length stored in length.  If
    // expectedLength is non-zero, complains and dies if the actual length
    // is not expectedLength.  Also complains and dies for zero length
    // lists.
    static void
    expectIntList(istream& mmp, struct MMPinfo *mmpInfo, int **listPtr, int *length, int expectedLength)
    {
	int *buf;
	int index;
	int len;
	int listElement;

	len = 0;
	buf = (int *)tempBuffer;
	index = 0;
	while (expectInt(mmp, mmpInfo, &listElement, 1)) {
	    len += sizeof(int);
	    buf = (int *)tempBuffer;
	    buf[index++] = listElement;
	}
	if (index == 0) {
	    ERROR("zero length list of atoms");
	    mmpParseError(mmpInfo);
	}
	if (expectedLength != 0 && expectedLength != index) {
	    ERROR2("expected exactly %d atoms, got %d", expectedLength, index);
	    mmpParseError(mmpInfo);
	}
	*length = index;
	*listPtr = buf;
    }

    static void
    makeAtom(OBMol& mol, int atomID, int elementType, vector3 v, OBResidue *res)
    {
	OBAtom atom;
	atom.SetVector(v);
	atom.SetAtomicNum(elementType);
	if (res != NULL)
	    atom.SetResidue(res);
	mol.AddAtom(atom);
    }

    static void
    setAtomHybridization(OBMol& mol, int previousAtomID, enum hybridization hybridization)
    {
	OBAtom *atom = mol.GetAtom(previousAtomID);
	switch (hybridization) {
	case sp:
	    atom->SetHyb(1);
	    break;
	case sp2:
	    atom->SetHyb(2);
	    break;
	case sp2_g:
	    atom->SetHyb(2);  UNTESTED;
	    break;
	case sp3:
	    atom->SetHyb(3);
	    break;
	case sp3d:
	    atom->SetHyb(3);  UNTESTED;
	    break;
	default:
	    OUCH();
	    break;
	}
    }

    static void
    makeBond(OBMol& mol, int previousAtomID, int atomID, char bondOrder)
    {
	OBBond bnd;
	OBAtom *atom1, *atom2;
	atom1 = mol.GetAtom(previousAtomID);
	atom2 = mol.GetAtom(atomID);
	if (atom1 == NULL || atom2 == NULL) {
	    // This will happen whenever there are bondpoints in an MMP file
	    // so it's not a big deal.
	    return;
	}

	bnd.Set(bond_index++, atom1, atom2, 1, 0);

	switch (bondOrder) {
	case '1':
	    bnd.SetBO(1);
	    break;
	case '2':
	    bnd.SetBO(2);
	    break;
	case '3':
	    bnd.SetBO(3);
	    break;
	case 'a':  // aromatic, Open Babel handles this
	case 'g':  // graphitic -> same as aromatic??
	case 'c':  // carbomeric -> same as aromatic??
	    bnd.SetBO(5);
	    break;
	default:
	    UNIMPLEMENTED;  // ? ? ? ?
	    OUCH();
	    break;
	}

	mol.AddBond(bnd);
    }

    static void
    makeVanDerWaals(OBMol& p, int previousAtomID, int atomID)
    {
	// I really don't think we need anything here.
    }

    static void
    readMMP(OBMol& mol, istream& mmp)
    {
	//struct part *p;
	//struct mmpStream thisMMPStream, *mmp;
	char *tok;
	static char group_name[200];
	//int group_num = 0;  // If we get groups, we only want the first one. Ignore "View Data" group.
	char bondOrder;
	int elementType;
	int previousAtomID = -1; // ID of atom just defined, so we can back-reference to it in later lines
	vector3 position;
	vector3 center;
	vector3 axis;
	int atomID;
	struct MMPinfo mmpInfo;
	OBResidue *residue = NULL;
	int resnum = 1;
	int atoms_in_this_group = 0;  // we want the first NON-EMPTY group

	mmpInfo.lineNumber = 1;
	mmpInfo.charPosition = 1;
	group_name[0] = '\0';

	while ((tok = readToken(mmp, &mmpInfo)) != NULL) {

#if 0
	    fprintf(stderr, "TOKEN: \"%s\"\n", tok);
#endif

	    // atom atomNumber (element) (posx, posy, posz)
	    // Identifies a new atom with the given element type and position.
	    // Position vectors are integers with units of 0.1pm.
	    if (!strcmp(tok, "atom")) {
		expectInt(mmp, &mmpInfo, &atomID, 0);
		expectToken(mmp, &mmpInfo, "(");
		expectInt(mmp, &mmpInfo, &elementType, 0);
		expectToken(mmp, &mmpInfo, ")");
		position = expectXYZInts(mmp, &mmpInfo);
		if (elementType != 0) {
		    // hack: change singlets to hydrogen
		    // if (elementType == 0) elementType=1;
		    previousAtomID = atomID;
		    makeAtom(mol, atomID, elementType, position, residue);
		}
		atoms_in_this_group++;
		consumeRestOfLine(mmp, &mmpInfo);
	    }

	    // after an atom:
	    //  info atom atomtype = sp2
	    // after an rmotor:
	    //  info leaf initial_speed = 20.0
	    else if (!strcmp(tok, "info")) {
		consumeWhitespace(mmp, &mmpInfo);
		tok = readToken(mmp, &mmpInfo);
		if (!strcmp(tok, "atom")) {
		    consumeWhitespace(mmp, &mmpInfo);
		    tok = readToken(mmp, &mmpInfo);
		    if (!strcmp(tok, "atomtype")) {
			enum hybridization hybridization = sp3;
			
			consumeWhitespace(mmp, &mmpInfo);
			expectToken(mmp, &mmpInfo, "=");
			consumeWhitespace(mmp, &mmpInfo);
			tok = readToken(mmp, &mmpInfo);
			
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
			    mmpParseError(&mmpInfo);
			}
			setAtomHybridization(mol, previousAtomID, hybridization);
		    }
		}
		consumeRestOfLine(mmp, &mmpInfo);
	    }
	    else if (!strncmp(tok, "bond", 4)) {
		bondOrder = tok[4];
		while (expectInt(mmp, &mmpInfo, &atomID, 1)) {
		    makeBond(mol, previousAtomID, atomID, bondOrder);
		}
	    }
	    else if (!strcmp(tok, "mol")) {
		char *name = expectName(mmp, &mmpInfo);
		residue = new OBResidue();
		residue->SetName(name);
		residue->SetNum(resnum++);
		mol.AddResidue(*residue);
		consumeRestOfLine(mmp, &mmpInfo);
	    }
	    else if (!strcmp(tok, "group")) {
		strcpy(group_name, expectName(mmp, &mmpInfo));
		consumeRestOfLine(mmp, &mmpInfo);
		atoms_in_this_group = 0;
	    }
	    else if (!strcmp(tok, "egroup")) {
		consumeRestOfLine(mmp, &mmpInfo);
		if (atoms_in_this_group > 0) {
		    // got a non-empty group, read remains and bail
		    while ((tok = readToken(mmp, &mmpInfo)) != NULL);
		    return;
		}
	    }

	    else if (!strcmp(tok, "end")) {
		consumeRestOfLine(mmp, &mmpInfo);
		return;
	    }
	    else if (tok[0] == '\r' || tok[0] == '\n') {
		// blank line, or second char of \r\n combo
		;
	    } else {
		consumeRestOfLine(mmp, &mmpInfo);
	    }
	}
    }



    class MMPFormat : public OBMoleculeFormat
    {
    public:
	//Register this format type ID
	MMPFormat()
	{
	    OBConversion::RegisterFormat("mmp",this, "chemical/x-mmp");
	    OBConversion::RegisterFormat("ent",this, "chemical/x-mmp");
	}

	virtual const char* Description() //required
	{
	    return
		"Molecular Machine Part format\n \
       Read Options e.g. -as\n\
        s  Output single bonds only\n\
        b  Disable bonding entirely\n\n";
	}

	virtual const char* SpecificationURL()
	{
	    return "http://www.nanoengineer-1.net";
	}

	virtual const char* GetMIMEType()
	{ return "chemical/x-mmp"; };

	//Flags() can return be any the following combined by | or be omitted if none apply
	// NOTREADABLE  READONEONLY  NOTWRITABLE  WRITEONEONLY
	virtual unsigned int Flags()
	{
	    return READONEONLY;
	};

	//*** This section identical for most OBMol conversions ***
	////////////////////////////////////////////////////
	/// The "API" interface functions
	virtual bool ReadMolecule(OBBase* pOb, OBConversion* pConv);
	virtual bool WriteMolecule(OBBase* pOb, OBConversion* pConv);

    };
    //***

    //Make an instance of the format class
    MMPFormat theMMPFormat;

    static char buffer[BUFF_SIZE];

    /////////////////////////////////////////////////////////////////
    bool MMPFormat::ReadMolecule(OBBase* pOb, OBConversion* pConv)
    {

	OBMol* pmol = dynamic_cast<OBMol*>(pOb);
	if(pmol==NULL)
	    return false;

	//Define some references so we can use the old parameter names
	istream &ifs = *pConv->GetInStream();
	OBMol &mol = *pmol;
	const char* title = pConv->GetTitle();

	int chainNum = 1;
	OBBitVec bs;

	mol.SetTitle(title);

	mol.BeginModify();


	readMMP(mol, ifs);

	// these two should be unnecessary for a MMP file, unless it's broken
	mol.ConnectTheDots();
	mol.PerceiveBondOrders();

	// clean out remaining blank lines
	while(ifs.peek() != EOF && ifs.good() &&
	      (ifs.peek() == '\n' || ifs.peek() == '\r'))
	    ifs.getline(buffer,BUFF_SIZE);

	mol.EndModify();

	mol.SetAtomTypesPerceived();
	atomtyper.AssignImplicitValence(mol);

	if (!mol.NumAtoms())
	    return(false);
	return(true);
    }

    /*
     * Open Babel's OBResidue corresponds to NE-1's chunk.
     */

    //////////////////////////////////////////////////////////////////////////////
    bool MMPFormat::WriteMolecule(OBBase* pOb, OBConversion* pConv)
    {
	extern void _mmp_write_atoms(OBMol& mol, ostream &ofs, int resnum);
	OBMol* pmol = dynamic_cast<OBMol*>(pOb);
	if(pmol==NULL)
	    return false;

	//Define some references so we can use the old parameter names
	ostream &ofs = *pConv->GetOutStream();
	OBMol &mol = *pmol;

	unsigned int i;
	char buffer[BUFF_SIZE];
	char group_name[200];
	int resnum = 1;
	int residueIndex, previousResidueIndex = -1;

	snprintf(buffer, BUFF_SIZE, "mmpformat 050920 required; 060421 preferred");
	ofs << buffer << endl;
	//snprintf(buffer, BUFF_SIZE, "# Generated by OpenBabel %s", BABEL_VERSION);
	//ofs << buffer << endl;
	snprintf(buffer, BUFF_SIZE, "kelvin 300");
	ofs << buffer << endl;

	// Let's set up a coordinate system so the nasty warning goes away.
	ofs << "group (View Data)" << endl;
	ofs << "info opengroup open = True" << endl;
	ofs << "csys (HomeView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)" << endl;
	ofs << "csys (LastView) (1.000000, 0.000000, 0.000000, 0.000000) (10.000000) (0.000000, 0.000000, 0.000000) (1.000000)" << endl;
	ofs << "egroup (View Data)" << endl;

	if (strlen(mol.GetTitle()) > 0) {
	    const char *p = mol.GetTitle();
	    std::string fn = p;
	    int pos = fn.find_last_of("\\/");
	    if (pos != string::npos) p += pos + 1;
	    strncpy(group_name, p, 199);
	    char *dot = strrchr(group_name, '.');
	    if (dot != NULL)
		*dot = '\0';
	} else {
	    snprintf(group_name, 200, "Babel-generated file");
	}
	snprintf(buffer, BUFF_SIZE, "group (%s)", group_name);
	ofs << buffer << endl;
	snprintf(buffer, BUFF_SIZE, "info opengroup open = True");
	ofs << buffer << endl;

	if (mol.NumResidues() > 0) {
	    OBResidue *residue;
	    vector<OBResidue*>::iterator r;
	    for (residue = mol.BeginResidue(r); residue; residue = mol.NextResidue(r)) {
		residueIndex = residue->GetIdx();
		if (residueIndex != previousResidueIndex) {
		    previousResidueIndex = residueIndex;
		    snprintf(buffer, BUFF_SIZE, "mol (Chunk %d)", residueIndex);
		    ofs << buffer << endl;
		}
		_mmp_write_atoms(mol, ofs, residueIndex);
	    }
	} else {
	    snprintf(buffer, BUFF_SIZE, "mol (Chunk 1)");
	    ofs << buffer << endl;
	    _mmp_write_atoms(mol, ofs, -1);
	}

	snprintf(buffer, BUFF_SIZE, "egroup (%s)", group_name);
	ofs << buffer << endl;

	ofs << "group (Clipboard)" << endl;
	ofs << "info opengroup open = True" << endl;
	ofs << "egroup (Clipboard)" << endl;
	
	ofs << "end molecular machine part" << endl;
	return(true);
    }

    void _mmp_write_atoms(OBMol& mol, ostream &ofs, int resnum)
    {
	for (int i = 1; i <= mol.NumAtoms(); i ++) {
	    OBAtom *atom = mol.GetAtom(i);
	    if (resnum == -1 || (atom->GetResidue() != NULL && atom->GetResidue()->GetIdx() == resnum)) {
		snprintf(buffer, BUFF_SIZE, "atom %d (%d) (%d, %d, %d) def",
			 atom->GetIdx(), atom->GetAtomicNum(),
			 (int) (1000.0 * atom->GetX()),
			 (int) (1000.0 * atom->GetY()),
			 (int) (1000.0 * atom->GetZ()));
		ofs << buffer << endl;
		// Now the bonds
		vector<OBEdgeBase*>::iterator j;
		for (int bondOrder = 1; bondOrder <= 5; bondOrder++) {
		    int bondsOfThisOrder = 0;
		    OBBond *bond;
		    for (bond = atom->BeginBond(j); bond; bond = atom->NextBond(j)) {
			if (bond->GetBO() == bondOrder) {
			    OBAtom *atom2 = bond->GetNbrAtom(atom);
			    if (atom2->GetIdx() < atom->GetIdx())
				bondsOfThisOrder++;
			}
		    }
		    if (bondsOfThisOrder > 0) {
			UNTESTED; // test for aromatic, graphitic, carbomeric bonds
			static char bondchars[] = " 123agc";
			snprintf(buffer, BUFF_SIZE, "bond%c", bondchars[bondOrder]);
			ofs << buffer;
			for (bond = atom->BeginBond(j); bond; bond = atom->NextBond(j)) {
			    if (bond->GetBO() == bondOrder) {
				OBAtom *atom2 = bond->GetNbrAtom(atom);
				if (atom2->GetIdx() < atom->GetIdx()) {
				    snprintf(buffer, BUFF_SIZE, " %d", atom2->GetIdx());
				    ofs << buffer;
				}
			    }
			}
			ofs << endl;
		    }
		}
	    }
	}
    }
} //namespace OpenBabel
