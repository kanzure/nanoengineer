// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#ifndef NX_BONDDATA_H
#define NX_BONDDATA_H

namespace Nanorex {

enum BondType {
	SINGLE_BOND = 0,
		DOUBLE_BOND,
		TRIPLE_BOND,
		AROMATIC_BOND,
		CARBOMERIC_BOND,
		GRAPHITIC_BOND,
		NUM_BOND_TYPES
};


/* CLASS: NXBondData */
/**
 * Information related to bonds
 */
class NXBondData {
public:
	NXBondData(BondType const& the_order,
	           double const& the_length)
		: order(the_order), length(the_length)
	{
	}
	~NXBondData() {}
	
    /// Bond order: 1=single, 2=double, 3=triple, 4=aromatic
	BondType const& getOrder(void) const { return order; }
	
    /// Length
	double const& getLength(void) const { return length; }
	
    /// Custom supplemental data
	std::vector<void const*> const& getSupplementalData(void) const
	{ return supplementalData; }
	
	void setSupplementalData(std::vector<void const*> const& suppData)
	{ supplementalData = suppData; }
	
	void addSupplementalData(void const *const dataPtr)
	{ supplementalData.push_back(dataPtr); }
	
protected:
	BondType order;
	double length;
	std::vector<void const*> supplementalData;
};



} // namespace Nanorex

#endif // NX_BONDDATA_H
