// *********************** GENERATED BY RAGEL 6.0 *******************
// ** Do not edit directly. Edit NanorexMMPImportExport.rl instead **
// ******************************************************************

// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "NanorexMMPImportExport.h"
#include <QFileInfo>

#define VERBOSE

#if defined(VERBOSE)
#define CDEBUG(x) DEBUG_MSG(filename, line, x)
inline void DEBUG_MSG(string const& filename, int line, string const& s)
{
    ostringstream msg;
    msg << line << ": " << s;
    NXLOG_INFO(filename, msg.str());
/*    Nanorex::NXLogger* logger = Nanorex::NXLogger::Instance();
    if (logger != 0)
        logger->log(Nanorex::NXLogLevel_Info, filename, msg.str());*/
}
#else
#define CDEBUG(x)
#endif




%%{
# Ragel fsm
    
    machine mmp_parser;
    
    EOL = '\n' ;
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
    
    charStringWithSpace = ('_' | alnum)  (space | '_' | alnum)*
        >to{stringval.clear(); stringval = stringval + fc;}
    ${stringval = stringval + fc; }
    ;
    
    charStringWithSpace2 = ('_' | alnum)  (space | '-' | alnum)*
        >to{stringval2.clear();  stringval2 = stringval2 + fc;}
    ${stringval2 = stringval2 + fc; }
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
        ( 'def'  %{atomStyleID = NXAtomData::DEF;} |
          'inv'  %{atomStyleID = NXAtomData::INV;} |
          'vdw'  %{atomStyleID = NXAtomData::VDW;} |
          'lin'  %{atomStyleID = NXAtomData::LIN;} |
          'cpk'  %{atomStyleID = NXAtomData::CPK;} |
          'tub'  %{atomStyleID = NXAtomData::TUB;} )
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
            if(molPtr != NULL) {
                map<int,OBAtom*>::iterator atomExistsQuery = 
                    foundAtomList.find(atomID);
                // guard against duplicates
                // also a hack to protect against Ragel's duplicate
                // parsing when encountering a blank line
                if(atomExistsQuery == foundAtomList.end()) {
                    // atom was not previously encountered, include
                    ostringstream msg;
                    msg << etab.GetSymbol(atomicNum)
                        << " atom with index " << atomID;
                    CDEBUG(msg.str().c_str());
                    atomPtr = molPtr->NewAtom();
                    NXAtomData *atomIDData = new NXAtomData;
                    atomIDData->SetIdx(atomID);
                    atomIDData->SetRenderStyle(atomStyleID);
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
            map<int,OBAtom*>::iterator targetAtomExistsQuery =
                foundAtomList.find(targetAtomIdx);
            if(targetAtomExistsQuery == foundAtomList.end()) {
                ostringstream errMsg;
                errMsg << "**ERROR** attempting to bond to non-existent atomID "
                       << targetAtomIdx;
                CDEBUG(errMsg.str());
            }
            else {
                OBAtom *targetAtomPtr = foundAtomList[targetAtomIdx];
                // guard against duplicates
                // also a hack to protect against Ragel's duplicate parsing
                // when encountering a blank line
                if(molPtr->GetBond(atomPtr, targetAtomPtr) == NULL) {
                    // bond was not previously encountered, include
                    ostringstream msg;
                    msg << "bonding atom #" << atomPtr->GetIdx() << " to atom #"
                        << targetAtomPtr->GetIdx();
                    CDEBUG(msg.str());
                    targetAtomList.push_back(targetAtomPtr);
                }
                else {
                    ostringstream msg;
                    msg << "bond to atom #" << targetAtomIdx
                        << " already exists";
                    CDEBUG(msg.str());
                }
            }
        }
    ;
bond_record :=
#        'bond'
        ( get_bond_order
          %{ CDEBUG("clearing targetAtomList"); targetAtomList.clear(); }
        )
        (space+ get_bond_target_atom)+
        space* EOL
        @{
            ++line;
            {
                ostringstream msg;
                msg << _s_bondOrderNameString[bond_order-1] << " bond to "
                    << targetAtomList.size() << " atoms";
                CDEBUG(msg.str());
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
                }
            }
            fret;
        }
    ;
    
    
    
# Read in molecule
    mol_style = ('def' | 'inv' | 'vdw' | 'cpk' | 'lin' | 'tub') ;
#ignore molecule style for now
mol_record := space+
              '(' space*  charStringWithSpace  space* ')'
              space+ mol_style space*
              EOL
        @{
            ++line;
            createNewMolecule();
            molPtr->SetTitle(stringval.c_str());
            {
                ostringstream msg;
                msg << "molecule " << molPtr->GetTitle();
                CDEBUG(msg.str());
            }
            fret;
        }
    ;
    
# @todo - spaces allowed in keys and values but there
#         should only be one pair per line?
info_atom_record := ( space+ charStringWithSpace space* '=' space* charStringWithSpace2
                      %{  {
                          ostringstream msg;
                          msg << "atom-property: " << stringval
                              << " = " << stringval2;
                          CDEBUG(msg.str());
                      }
                          applyAtomType(stringval, stringval2);
                      }
                    )+
        space* EOL
        @{
            ++line;
            fret;
        }
    ;
    
group_record := space+ '(' space*  charStringWithSpace  space* ')' space* EOL
        @{
            ++line;
            createNewMoleculeSet();
            {
                ostringstream msg;
                msg << "group " << stringval;
                CDEBUG(msg.str());
            }
            fret;
        }
    ;
    
# ignore everything following 'egroup'
egroup_record := [^\n]* EOL
        @{
            ++line;
            closeMoleculeSet();
            CDEBUG("egroup");
        }
    ;
    
    
main := ( space**
          ( 'group'  @{fcall group_record;} $(main,10) |
            'egroup'  @{fcall egroup_record;} $(main,10) |
            'mol'  @{fcall mol_record;} $(main,10) |
            'atom' @{fcall atom_record;} $(main,10) |
            'bond' @{fcall bond_record;} $(main,10) |
            'info' space+ 'atom' @{++line;fcall info_atom_record;} $(main,10) |
            '#' [^\n]* EOL $(main,10) %{++line; CDEBUG("comment"); } |
            [^\n]+ EOL $(main,1) %{++line; CDEBUG("ignored"); }
          )?
        )*
        $err{success = false;}
    ;
    
}%%

%% # Ragel FSM data

%% write data;


// static data

char const NanorexMMPImportExport::_s_bondOrderString[NUM_BOND_TYPES] = {
 '1', '2', '3', 'a', 'g', 'c'
};

char const
NanorexMMPImportExport::_s_bondOrderNameString[NUM_BOND_TYPES][16] =
{
    "single", "double", "triple", "aromatic", "graphitic", "carbomeric"
};

char const NanorexMMPImportExport::_s_hybridizationName[8][8] = {
    "none", "sp", "sp2", "sp3", "X-hyb4", "X-hyb5", "X-hyb6", "X-hyb7"
};


/* CONSTRUCTOR */
NanorexMMPImportExport::NanorexMMPImportExport()
{
    reset();
}

/* DESTRUCTOR */
NanorexMMPImportExport::~NanorexMMPImportExport()
{
}


/* FUNCTION: reset */
void NanorexMMPImportExport::reset(void)
{
    line = 0;
    atomPtr = NULL;
    bondPtr = NULL;
    foundAtomList.clear();
    targetAtomList.clear();
    molPtr = NULL;
    molSetPtr = NULL;
    while(!molSetPtrStack.empty()) molSetPtrStack.pop();
    
    // initialize the ragel engine
    %% write init;
}


/* FUNCTION: importFromFile */
NXCommandResult*
NanorexMMPImportExport::
importFromFile(NXMoleculeSet *rootMoleculeSetPtr,
               NXDataStoreInfo *dataStoreInfo,
               const std::string& theFilename,
               int /*frameSetId*/, int /*frameIndex*/)
{
    bool success = true;
    NXCommandResult *result = new NXCommandResult();
    result->setResult(NX_CMD_SUCCESS);
    
    ifstream mmpfile(theFilename.c_str(), ios::in);
    if(!mmpfile) {
        populateCommandResult(result,
                              (string("Couldn't open file: ") + theFilename)
                              .c_str());
        success = false;
    }
    else {
        filename = theFilename;
        success = readMMP(mmpfile, rootMoleculeSetPtr);
    }
    
	// Set the meta information about the data store.
	if (success) {
		dataStoreInfo->setIsSingleStructure(true);
	}
    
    return result;
}


/* FUNCTION: readMMP */
bool NanorexMMPImportExport::readMMP(istream& instream,
                                     NXMoleculeSet *rootMoleculeSetPtr)
{
    reset();
    
    p = RagelIstreamPtr(instream);
    pe = RagelIstreamPtr(instream, 0, ios::end);
    eof = pe;
    
    molSetPtr = rootMoleculeSetPtr;
    molSetPtrStack.push(molSetPtr);
    
    /// @todo handle first 'group' statement and molSetPtrStack initialization
    
    // Ragel parser implementation
    bool success = true;
    %% write exec;
    
    // End-of-parsing sanity checks
    if(molSetPtrStack.size() != 1) {
        NXLOG_WARNING("NanorexMMPImportExport",
                      "At least one group has no matching egroup statement");
    }
    return success;
}


/* FUNCTION: createNewMoleculeSet */
void NanorexMMPImportExport::createNewMoleculeSet(void)
{
    if(molSetPtr != NULL) {
        NXMoleculeSet *newMolSetPtr = new NXMoleculeSet;
        molSetPtr->addChild(newMolSetPtr);
        molSetPtrStack.push(newMolSetPtr);
        molSetPtr = newMolSetPtr;
    }
}


/* FUNCTION: closeMoleculeSet */
void NanorexMMPImportExport::closeMoleculeSet(void)
{
    molSetPtrStack.pop();
    molSetPtr = (molSetPtrStack.size() == 0) ? NULL : molSetPtrStack.top();
}


/* FUNCTION: createNewMolecule */
inline void NanorexMMPImportExport::createNewMolecule(void)
{ 
    atomPtr = NULL;
    bondPtr = NULL;
    molPtr = NULL;
    molPtr = molSetPtr->newMolecule();
}


/* FUNCTION: applyAtomType */
void NanorexMMPImportExport::applyAtomType(string const& keyStr,
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




/* FUNCTION: exportToFile */
NXCommandResult*
NanorexMMPImportExport::
exportToFile(NXMoleculeSet *molSetPtr,
             NXDataStoreInfo */*dataStoreInfo*/,
             const std::string& theFilename,
             int /*frameSetId*/, int /*frameIndex*/)
{
    NXCommandResult *result = new NXCommandResult();
    result->setResult(NX_CMD_SUCCESS);
    
    ofstream mmpfile(theFilename.c_str(), ios::out);
    if(!mmpfile) {
        populateCommandResult(result,
                              (string("Couldn't open file: ") + theFilename)
                              .c_str());
    }
    else {
        PrintMoleculeSet(mmpfile, molSetPtr);
        mmpfile.close();
    }
    return result;
}


/* FUNCTION: GetAtomID */
/* static */
int NanorexMMPImportExport::GetAtomID(OBAtom *atomPtr)
{
    NXAtomData *atomIDData = 
        static_cast<NXAtomData*>(atomPtr->GetData(NXAtomDataType));
    int atomID = atomIDData->GetIdx();
    return atomID;
}


/* FUNCTION: GetAtomRenderStyleName */
/* static */
char const *const NanorexMMPImportExport::GetAtomRenderStyleName(OBAtom *atomPtr)
{
    NXAtomData *atomDataPtr =
        static_cast<NXAtomData*>(atomPtr->GetData(NXAtomDataType));
    NXAtomData::RenderStyleID atomStyleID = atomDataPtr->GetRenderStyle();
    char const *const atomRenderStyle =
        NXAtomData::GetRenderStyleName(atomStyleID);
    return atomRenderStyle;
}


/* FUNCTION: PrintMolecule */
/* static */
void NanorexMMPImportExport::PrintMolecule(ostream& o,
                                           OBMol *const molPtr)
{
    set<int> prevAtomIdx;
    set<int> prevBondIdx; /// @todo - replace with simple bond count
    
    o << "mol (" << molPtr->GetTitle() << ')' << endl;
    
    OBAtomIterator atomIter;
    OBAtom *atomPtr = NULL;
    // For each atom ...
    for(atomPtr = molPtr->BeginAtom(atomIter);
        atomPtr != NULL;
        atomPtr = molPtr->NextAtom(atomIter))
    {
        // ... write the 'atom' line ...
        int atomID = GetAtomID(atomPtr);
        o << "atom " << atomID << " (" << atomPtr->GetAtomicNum() << ") " << '('
          << atomPtr->x() << ',' << atomPtr->y() << ',' << atomPtr->z()
          << ") " << GetAtomRenderStyleName(atomPtr) << endl;
        
        if(atomPtr->GetHyb() != 0) {
            o << "info atom atomtype = "
              << _s_hybridizationName[atomPtr->GetHyb()] << endl;
        }
        
        // ... write the 'bond' lines for this atom ...
        // ... first sort bonds by type ...
        OBBondIterator bondIter;
        OBBond *bondPtr = NULL;
        vector<int> bondCategories[6];
        for(bondPtr = atomPtr->BeginBond(bondIter);
            bondPtr != NULL;
            bondPtr = atomPtr->NextBond(bondIter))
        {
            // write bond statement only if target atom was previously written
            OBAtom *nbrAtomPtr = bondPtr->GetNbrAtom(atomPtr);
            int nbrAtomID = GetAtomID(nbrAtomPtr);
            if(prevAtomIdx.find(nbrAtomID) != prevAtomIdx.end()) {
                int bondOrder = bondPtr->GetBondOrder();
                bondCategories[bondOrder-1].push_back(nbrAtomID);
                // record bond for sanity check at end
                prevBondIdx.insert(bondPtr->GetIdx());
            }
        }
        
        // ... write the bonds, one line per type ...
        for(int i=0; i<6; ++i) {
            int J = bondCategories[i].size();
            if(J > 0) {
                o << "bond" << _s_bondOrderString[i];
                for(int j=0; j<J; ++j)
                    o << ' ' << bondCategories[i][j];
                o  << endl;
            }
        }
        
        // record atom as 'previously written'
        prevAtomIdx.insert(atomID);
    }
    
    // debug diagnostics
    ostringstream debugMsg;
    debugMsg << "# atoms check ";
    if(molPtr->NumAtoms() == prevAtomIdx.size())
        debugMsg << "PASS ("  << molPtr->NumAtoms() << ')' << endl;
    else
        debugMsg << "FAIL: "
                 << molPtr->NumAtoms() << " != " << prevAtomIdx.size()<< endl;
    
    debugMsg << "# bonds check ";
    if(molPtr->NumBonds() == prevBondIdx.size())
        debugMsg << "PASS (" << molPtr->NumBonds() << ')' << endl;
    else
        debugMsg << "FAIL: "
                 << molPtr->NumBonds() << " != " << prevBondIdx.size()<< endl;
    
    debugMsg.flush();
    NXLOG_DEBUG("NanorexMMPImportExport::PrintMoleculeSet",
                debugMsg.str().c_str());
}


/* FUNCTION: PrintMoleculeSet */
/* static */
void NanorexMMPImportExport::PrintMoleculeSet(ostream& o,
                                              NXMoleculeSet *const molSetPtr)
{
    // Iterate over all child molecules
    OBMolIterator molIter;
    for(molIter = molSetPtr->moleculesBegin();
        molIter != molSetPtr->moleculesEnd();
        ++molIter)
    {
        PrintMolecule(o, *molIter);
    }
    
    // Iterate over all child molecule sets
    NXMoleculeSetIterator molSetIter;
    for(molSetIter = molSetPtr->childrenBegin();
        molSetIter != molSetPtr->childrenEnd();
        ++molSetIter)
    {
        PrintMoleculeSet(o, *molSetIter);
    }
}


/* FUNCTION: populateCommandResult */
void
NanorexMMPImportExport::populateCommandResult (NXCommandResult* result,
                                               const string& message)
{
    result->setResult(NX_PLUGIN_REPORTS_ERROR);
    vector<QString> resultVector;
    resultVector.push_back("OpenBabelImportExport");
    resultVector.push_back(message.c_str());
    result->setParamVector(resultVector);
}

Q_EXPORT_PLUGIN2 (NanorexMMPImportExport, NanorexMMPImportExport)

