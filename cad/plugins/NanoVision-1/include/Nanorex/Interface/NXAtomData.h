// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ATOM_H
#define NX_ATOM_H

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
    typedef enum { DEF = 0, INV, VDW, LIN, CPK, TUB, NUM_STYLES } RenderStyleID;
    
    NXAtomData() { _type = NXAtomDataType; _rsid = DEF; }
    
    void SetIdx(int idx) { _idx = idx; }
    unsigned int GetIdx() { return _idx; }
    
    void SetRenderStyle(RenderStyleID rsid) { _rsid = rsid; }
    RenderStyleID const& GetRenderStyle(void) const { return _rsid; }
    
    static char const *const GetRenderStyleName(RenderStyleID rsid)
    { return _s_renderStyleNames[rsid]; }
    
private:
    unsigned int _idx;
    RenderStyleID _rsid;
    
    static char const *const _s_renderStyleNames[NUM_STYLES];
};


} // Nanorex::

#endif // NX_ATOM_H
