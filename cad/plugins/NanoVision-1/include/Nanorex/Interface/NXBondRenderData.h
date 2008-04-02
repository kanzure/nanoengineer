// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BONDRENDERDATA_H
#define NX_BONDRENDERDATA_H

#include <vector>


namespace Nanorex {


/* CLASS: NXBondRenderData */
/**
 * Information for rendering bonds
 */
class NXBondRenderData {
public:
    NXBondRenderData(int const& the_order,
                     double const& the_length);
    ~NXBondRenderData() {}
    
    /// Bond order: 1=single, 2=double, 3=triple, 5=aromatic
    int const& getOrder(void) const { return order; }
    
    /// Length
    double const& getLength(void) const { return length; }
    
    /// Custom supplemental data
    std::vector<void const*> const& getSupplementalData(void) const
    { return supplementalData; }
    
    void setSupplementalData(std::vector<void const*> const& suppData)
    { supplementalData = suppData; }
    
    void addData(void const *const dataPtr)
    { supplementalData.push_back(dataPtr); }
    
protected:
    int order;
    double length;
    std::vector<void const*> supplementalData;
};


} // Nanorex

#endif // NX_BONDRENDERDATA_H
