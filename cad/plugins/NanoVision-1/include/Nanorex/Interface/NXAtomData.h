// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ATOMDATA_H
#define NX_ATOMDATA_H

#include <string>
#include <openbabel/generic.h>
#define NXAtomDataType OBGenericDataType::CustomData1
using namespace OpenBabel;

namespace Nanorex {


/* CLASS: NXAtomData */
/**
 * A set of Nanorex-specific data stored in OBAtom objects.
 *
 * @ingroup ChemistryDataModel, NanorexInterface
 */
class NXAtomData : public OBGenericData {
public:
	
	// typedef enum { DEF = 0, INV, VDW, LIN, CPK, TUB, NUM_STYLES } RenderStyleID;
    
	NXAtomData(int atomicNum)
	{ _type = NXAtomDataType; _atomicNum = atomicNum; }
    
	void setAtomicNum(int atomicNum) { _atomicNum = atomicNum; }
	int const& getAtomicNum(void) const { return _atomicNum; }
	
	void setIdx(int idx) { _idx = idx; }
    int getIdx() const { return _idx; }
    
	// void SetRenderStyle(RenderStyleID rsid) { _rsid = rsid; }
	// RenderStyleID const& GetRenderStyle(void) const { return _rsid; }
    
	void setRenderStyleCode(std::string const& renderStyleCode) {
		_renderStyleCode = renderStyleCode;
	}
	std::string const& getRenderStyleCode(void) const {
		return _renderStyleCode;
	}
	
	std::vector<void const*> const& getSupplementalData(void) const
	{ return supplementalData; }
	
	void setSupplementalData(std::vector<void const *> const& suppData)
	{ supplementalData = suppData; }
	
	void addSupplementalData(void const *dataPtr)
	{ supplementalData.push_back(dataPtr); }
	
	// static char const *const GetRenderStyleName(RenderStyleID rsid)
	// { return _s_renderStyleNames[rsid]; }
    
private:
	
	int _atomicNum;
	int _idx;
	std::string _renderStyleCode;
	std::vector<void const*> supplementalData;
	
	// static char const *const _s_renderStyleNames[NUM_STYLES];
};


} // Nanorex::

#endif // NX_ATOM_H
