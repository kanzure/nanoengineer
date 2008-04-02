// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_ATOMRENDERDATA_H
#define NX_ATOMRENDERDATA_H

//#include <map>
#include <vector>
#include <string>
//#include "Nanorex/Interface/NXOpenGLMaterial.h"


namespace Nanorex {

/* CLASS: NXAtomRenderData */
/**
 * Information for rendering atoms
 */
class NXAtomRenderData {

private:
    typedef unsigned int uint;
    
public:
    NXAtomRenderData(uint const& the_atomicNum);
    ~NXAtomRenderData() {}
    
    uint const& getAtomicNum(void) const { return atomicNum; }
    
	void setRenderStyleCode(std::string const& code) {
		renderStyleCode = code;
	}
	
	std::string const& getRenderStyleCode(void) const {
		return renderStyleCode;
	}
	
    std::vector<void const*> const& getSupplementalData(void) const
    { return supplementalData; }
    
    void setSupplementalData(std::vector<void const *> const& suppData)
    { supplementalData = suppData; }
    
    void addData(void const *dataPtr)
    { supplementalData.push_back(dataPtr); }
    
protected:
    uint atomicNum;
	std::string renderStyleCode;
    std::vector<void const*> supplementalData;
};


} // Nanorex

#endif // NX_ATOMRENDERDATA_H
