// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ATOMRENDERDATA_H
#define NX_ATOMRENDERDATA_H

//#include <map>
#include <vector>
//#include "Nanorex/Interface/NXOpenGLMaterial.h"


namespace Nanorex {

/* CLASS: NXAtomRenderData */
/**
 * Information for rendering atoms
 */
class NXAtomRenderData {
    /// @todo shouldn't explicitly depend on OpenGL because various engines use it
private:
    typedef unsigned int uint;
    
public:
    NXAtomRenderData(uint const& the_atomicNum);
                     // NXOpenGLMaterial const& defCol = NXOpenGLMaterial(),
                     // void const *const suppData = NULL);
    ~NXAtomRenderData() {}
    
    uint const& getAtomicNum(void) const { return atomicNum; }
    
    // NXOpenGLMaterial const& getDefaultMaterial(void) const { return defaultMaterial; }
    
    std::vector<void const*> const& getSupplementalData(void) const
    { return supplementalData; }
    
    void setSupplementalData(std::vector<void const *> const& suppData)
    { supplementalData = suppData; }
    
    void addData(void const *dataPtr)
    { supplementalData.push_back(dataPtr); }
    
protected:
    uint atomicNum;
    // NXOpenGLMaterial defaultMaterial;
    std::vector<void const*> supplementalData;
};


} // Nanorex

#endif // NX_ATOMRENDERDATA_H
