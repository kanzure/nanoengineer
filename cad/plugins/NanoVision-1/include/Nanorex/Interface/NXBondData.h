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

} // namespace Nanorex

#endif // NX_BONDDATA_H
