#include <iostream>
#include <cstring>
#include <fstream>
#include <sstream>
#include <set>
#include <map>
#include <vector>
#include <cassert>
#include <openbabel/mol.h>
#include <Nanorex/Interface/NXMoleculeData.h>
#include "periodic_table.h"
#include "ragelistreamptr.h"

using namespace std;
using namespace OpenBabel;
using namespace Nanorex;

#define CERR(x) cerr << filename << ':' << line << ": " << (x) << endl

%%{
# Ragel fsm
    
    machine mmp_parser;
    
    EOL = '\n' ${/*++line;*/} ;
    EOF = 0xff ;
    
    whole_number = digit+
        >to{intval=0;}
        ${intval = intval*10 + (fc-'0');}
    ; 
    
    integer = ('+'? whole_number ) | ('-' whole_number %{intval=-intval;}) ;
    
    charString = ('_' | alnum) (alnum | [_\-])*
        >to{stringval.clear(); stringval = stringval + fc;}
        ${stringval = stringval + fc; }
    ;
    
    charStringWithSpace = ('_' | alnum) (alnum | [ _\-])*
        >to{stringval.clear(); stringval = stringval + fc;}
        ${stringval = stringval + fc; }
    ;
    
    charStringWithSpace2 = ('_' | alnum) (alnum | [ _\-])*
        >to{stringval2.clear();  stringval2 = stringval2 + fc;}
        ${stringval2 = stringval2 + fc; }
    ;
    
    BLANK_LINE = space* EOL @{++line;}
        %{CERR("skipped blank line");}
    ;
    COMMENT_LINE = space* '#' [^\n]* EOL @{++line;}
        %{CERR("skipped comment");}
    ;
    INCOMPREHENSIBLE_LINE = [^\n]+
        EOL @{++line;}
        %{CERR("skipped incomprehensible");}
    ;

    # Read in atom
    get_atom_id = whole_number %{atomID = intval;} ;
    get_atomic_num = '(' space* whole_number @{atomicNum = intval;} space* ')' ;
    get_coords =
        '('  space*
        (integer % { x=intval;}) space* ',' space*
        (integer % { y=intval;}) space* ',' space*
        (integer % { z=intval;}) space* ')'
        ;
    get_atom_style =
        ( 'def'  %{atomStyle[atomID] = diDEFAULT;} |
          'inv'  %{atomStyle[atomID] = diINVISIBLE;} |
          'vdw'  %{atomStyle[atomID] = diTrueCPK;} |
          'lin'  %{atomStyle[atomID] = diLINES;} |
          'cpk'  %{atomStyle[atomID] = diBALL;} |
          'tub'  %{atomStyle[atomID] = diTUBES;} )
        ;
atom_record :=
        space+
        get_atom_id
        space+
        get_atomic_num
        space+
        get_coords
        space+
        get_atom_style
        space* EOL
        @{
            ++line;
            /*cerr << "after atom, *p = ";
            if(*p=='\n') cerr << "\\n" << endl;
            else cerr << (*p) << endl; */
            if(molPtr != NULL) {
                map<int,OBAtom*>::iterator atomExistsQuery = foundAtomList.find(atomID);
                // guard against duplicates
                // also a hack to protect against Ragel's duplicate parsing when encountering a blank line
                if(atomExistsQuery == foundAtomList.end()) {
                    // atom was not previously encountered, include
                    cerr << filename << ':' << line << ": "
                        << chem::PeriodicTable::GetSymbol(chem::element_t(atomicNum))
                        << " atom with index " << atomID << endl;
                    atomPtr = molPtr->NewAtom();
                    // atomPtr->SetIdx(atomID);
                    NXMoleculeData *atomIDData = new NXMoleculeData;
                    atomIDData->SetIdx(atomID);
                    atomPtr->SetData(atomIDData);
                    atomPtr->SetAtomicNum(atomicNum);
                    atomPtr->SetVector(x,y,z);
                    foundAtomList[atomID] = atomPtr;
                }
            }
            fret;
        }
    ;
    


# Read in bond
    get_bond_order = ('1' %{bond_order=1;} |
                      '2' %{bond_order=2;} |
                      '3' %{bond_order=3;} |
                      'a' %{bond_order=4;} |
                      'g' %{bond_order=5;} |
                      'c' %{bond_order=6;} ) ;
    get_bond_target_atom =
        whole_number
        %{
            int const& targetAtomIdx = intval;
            // cerr << "get_bond_target_atom: " << targetAtomIdx << endl;
            map<int,OBAtom*>::iterator targetAtomExistsQuery = foundAtomList.find(targetAtomIdx);
            if(targetAtomExistsQuery == foundAtomList.end()) {
                ostringstream errMsg;
                errMsg << "**ERROR** attempting to bond to non-existent atomID " << targetAtomIdx;
                CERR(errMsg.str());
            }
            else {
                OBAtom *targetAtomPtr = foundAtomList[targetAtomIdx];
                // guard against duplicates
                // also a hack to protect against Ragel's duplicate parsing when encountering a blank line
                if(molPtr->GetBond(atomPtr, targetAtomPtr) == NULL) {
                    // bond was not previously encountered, include
                    ostringstream msg;
                    msg << "bonding atom #" << atomPtr->GetIdx() << " to atom #" << targetAtomPtr->GetIdx();
                    CERR(msg.str());
                    targetAtomList.push_back(targetAtomPtr);
                }
                else {
                    ostringstream msg;
                    msg << "bond to atom #" << targetAtomIdx << " already exists";
                    CERR(msg.str());
                }
            }
        }
    ;
bond_record :=
#        'bond'
        ( get_bond_order
            %{ /*cerr << "bond_record: *p=" << fc << endl;*/ CERR("clearing targetAtomList"); targetAtomList.clear(); }
        )
        (space+ get_bond_target_atom)+
        space* EOL
#        @{++line;}
        @{
            ++line;
            {
                ostringstream msg;
                msg << bondOrderNameString[bond_order-1] << " bond to " << targetAtomList.size() << " atoms";
                CERR(msg.str());
            }
            if(molPtr != NULL && atomPtr != NULL) {
                vector<OBAtom*>::iterator targetAtomIter;
                for(targetAtomIter  = targetAtomList.begin();
                    targetAtomIter != targetAtomList.end();
                    ++targetAtomIter)
                {
                    bondPtr = molPtr->NewBond();
                    bondPtr->SetBondOrder(bond_order);
                    OBAtom *targetAtomPtr = *targetAtomIter;
                    bondPtr->SetBegin(atomPtr);
                    bondPtr->SetEnd(targetAtomPtr);
                    atomPtr->AddBond(bondPtr);
                    targetAtomPtr->AddBond(bondPtr);
                    // cerr << "bonded atom #" << atomPtr->GetIdx() << " to atom #" << targetAtomPtr->GetIdx() << endl;
                }
            }
            fret;
        }
        ;
    
    

# Read in molecule
    mol_style = ('def' | 'inv' | 'vdw' | 'cpk' | 'lin' | 'tub') ;
#ignore molecule style for now
mol_record := space+ '(' space* charString space* ')' space+ mol_style space* EOL
    @{
        ++line;
        molPtr = createNewMolecule();
        molPtr->SetTitle(stringval.c_str());
        {
            ostringstream msg;
            msg << "molecule " << molPtr->GetTitle();
            CERR(msg.str());
        }
        fret;
     }
     ;

# @todo - spaces allowed in keys and values but there should only be one pair per line?
info_atom_record := ( space+ charStringWithSpace space* '=' space* charStringWithSpace2
                      %{  {
                            ostringstream msg;
                            msg << "atom-property: " << stringval << " = " << stringval2;
                            CERR(msg.str());
                          }
                          applyAtomProperty(atomPtr, stringval, stringval2);
                       }
                     )+
                    space* EOL
                    @{
                        fret;
                    }
                    ;
    
#info_record := space+
#               ( 'atom' @{fcall info_atom_record;} |
#                 'chunk' @{fcall info_chunk_record;} |
#                 'leaf' @{fcall info_leaf_record;} |
#                 'opengroup' @{fcall info_opengroup_record;} |
#               );
    
main := ( space**
          ( 'mol'  @{fcall mol_record;} $(main,10) |
            'atom' @{fcall atom_record;} $(main,10) |
            'bond' @{fcall bond_record;} $(main,10) |
            'info' space+ 'atom' @{++line;fcall info_atom_record;} $(main,10) |
            '#' [^\n]* EOL $(main,10) %{++line; CERR("comment"); } |
            [^\n]+ EOL $(main,1) %{++line; CERR("ignored"); }
          )?
#          EOL @{++line;}
        )*
        $err{success = false;}
        ;
    
}%%


#define SKIP_IF_BLANK_OR_COMMENT_LINE(p) { \
    for(; *p != '\0' && isspace(*p); ++p); \
    if(*p == '\0') { cerr << "Skipping blank line" << endl; continue; } \
    if(*p == '#') { cerr << "skipping blank line" << endl; continue; } \
}

%% write data;


class MMPException {};

class MMPParser {
public:
    MMPParser(string const& theFilename);
    ~MMPParser();
    
    bool parse(void);
    void printMolecules(void);
    
private:
    map<int, char const*> atomStyle;
    static char const *const diDEFAULT;
    static char const *const diINVISIBLE;
    static char const *const diTrueCPK;
    static char const *const diLINES;
    static char const *const diBALL;
    static char const *const diTUBES;
    static char const *const bondOrderString;
    static char const *const bondOrderNameString[];
    
    string filename;
    ifstream mmpfile;
    
    // Ragel + parser state variables
    int cs, stack[1000], top;
    int intval, atomicNum, atomID, bond_order;
    int x, y, z;
    int line;
    OBMol *molPtr;
    OBAtom *atomPtr;
    OBBond *bondPtr;
    map<int,OBAtom*> foundAtomList;
    vector<OBAtom*> targetAtomList;
    string stringval, stringval2;
    
    RagelIstreamPtr p, pe, eof;
    
    vector<OBMol*> moleculeSet;

    OBMol* createNewMolecule(void);
    void printMolecule(OBMol *molPtr);
    
    void applyAtomProperty(OBAtom *atomPtr,
                           string const& keyStr,
                           string const& valueStr);
};

char const *const MMPParser::diDEFAULT("def");
char const *const MMPParser::diINVISIBLE("inv");
char const *const MMPParser::diTrueCPK("vdw");
char const *const MMPParser::diLINES("lin");
char const *const MMPParser::diBALL("cpk");
char const *const MMPParser::diTUBES("tub");

char const *const MMPParser::bondOrderString("123agc");
char const *const MMPParser::bondOrderNameString[] = {
    "single", "double", "triple", "aromatic", "graphitic", "carbomeric"
};

void MMPParser::applyAtomProperty(OBAtom *atomPtr,
                                  string const& keyStr,
                                  string const& valueStr)
{
    if(molPtr != NULL && atomPtr != NULL) {
        if(keyStr == "atomtype") { // hybridization info
            if(valueStr == "sp") atomPtr->SetHyb(1);
            else if(valueStr == "sp2") atomPtr->SetHyb(2);
            else if(valueStr == "sp2_g") atomPtr->SetHyb(2);
            else if(valueStr == "sp3") atomPtr->SetHyb(3);
            else if(valueStr == "sp3d") atomPtr->SetHyb(3);
            // else ignore
        }
    }
}

MMPParser::MMPParser(string const& theFilename)
{
    filename = theFilename;
    mmpfile.open(filename.c_str(), std::ios::in);
    if(!mmpfile) {
        cerr << "Cannot open " << filename << " for input" << endl;
        throw MMPException();
    }
    
    p = RagelIstreamPtr(mmpfile);
    pe = RagelIstreamPtr(mmpfile, 0, ios::end);
    eof = pe;
    
    line = 0;
    
    molPtr = NULL;
    atomPtr = NULL;
    bondPtr = NULL;
    foundAtomList.clear();
    targetAtomList.clear();
    moleculeSet.clear();

    %% write init;
}

MMPParser::~MMPParser()
{
    vector<OBMol*>::iterator molIter;
    for(molIter = moleculeSet.begin(); molIter != moleculeSet.end(); ++molIter) {
        molPtr = *molIter;
        delete molPtr;
    }
}


inline OBMol* MMPParser::createNewMolecule(void)
{ 
    // foundAtomList.clear();
    atomPtr = NULL;
    bondPtr = NULL;
    OBMol *newMolPtr = new OBMol;
    moleculeSet.push_back(newMolPtr);
    return newMolPtr;
}


bool MMPParser::parse()
{
    bool success = true;
    %% write exec;
    return success;
}


void MMPParser::printMolecule(OBMol *molPtr)
{
    set<int> prevAtomIdx;
    set<int> prevBondIdx;
    
    cout << "Molecule (" << molPtr->GetTitle() << ')' << endl;
    
    OBAtomIterator atomIter;
    for(atomPtr = molPtr->BeginAtom(atomIter);
        atomPtr != NULL;
        atomPtr = molPtr->NextAtom(atomIter))
    {
        // int const atomID = atomPtr->GetIdx();
        NXMoleculeData *atomIDData = static_cast<NXMoleculeData*>(atomPtr->GetData(NXMoleculeDataType));
        int atomID = atomIDData->GetIdx();
        map<int,char const*>::const_iterator atomStyleIter = atomStyle.find(atomID);
        assert(atomStyleIter != atomStyle.end());
        char const *const atomStyleString = atomStyleIter->second;
        cout << "atom " << atomID << " (" << atomPtr->GetAtomicNum() << ") "
            << '(' << atomPtr->x() << ',' << atomPtr->y() << ',' << atomPtr->z() << ')'
            << ' ' << atomStyleString << endl;
        
        char const *hybridizationString[8] = {
            "none", "sp", "sp2", "sp3", "X-hyb4", "X-hyb5", "X-hyb6", "X-hyb7"
        };
        if(atomPtr->GetHyb() != 0)
            cout << "info atom atomtype = " << hybridizationString[atomPtr->GetHyb()] << endl;
        
        OBBondIterator bondIter;
        vector<int> bondCategories[6];
        for(bondPtr = atomPtr->BeginBond(bondIter);
            bondPtr != NULL;
            bondPtr = atomPtr->NextBond(bondIter))
        {
            OBAtom *nbrAtomPtr = bondPtr->GetNbrAtom(atomPtr);
            if(prevAtomIdx.find(nbrAtomPtr->GetIdx()) != prevAtomIdx.end()) {
                int bondOrder = bondPtr->GetBondOrder();
                bondCategories[bondOrder-1].push_back(nbrAtomPtr->GetIdx());
                prevBondIdx.insert(bondPtr->GetIdx());
            }
        }
        
        for(int i=0; i<6; ++i) {
                int J = bondCategories[i].size();
                if(J > 0) {
                    cout << "bond" << bondOrderString[i];
                    for(int j=0; j<J; ++j)
                         cout << ' ' << bondCategories[i][j];
                    cout  << endl;
            }
        }
        
        prevAtomIdx.insert(atomID);
    }
    
    cerr << "# atoms check ";
    if(molPtr->NumAtoms() == prevAtomIdx.size())
        cerr << "PASS ("  << molPtr->NumAtoms() << ')' << endl;
    else
        cerr << "FAIL: " << molPtr->NumAtoms() << " != " << prevAtomIdx.size()<< endl;
    
    cerr << "# bonds check ";
    if(molPtr->NumBonds() == prevBondIdx.size())
        cerr << "PASS (" << molPtr->NumBonds() << ')' << endl;
    else
        cerr << "FAIL: " << molPtr->NumBonds() << " != " << prevBondIdx.size()<< endl;
        
    cout << endl;
}


void MMPParser::printMolecules(void)
{
    vector<OBMol*>::iterator molIter;
    for(molIter = moleculeSet.begin();
        molIter != moleculeSet.end();
        ++molIter)
    {
        printMolecule(*molIter);
    }
}


int main(int argc, char *argv[])
{
    if(argc != 2) {
        cerr << "usage: mmp-parser <filename>" << endl;
        return 1;
    }
    MMPParser mmpParser(argv[1]);
    bool parsed = mmpParser.parse();
    if(parsed) mmpParser.printMolecules();
    return 0;
}
