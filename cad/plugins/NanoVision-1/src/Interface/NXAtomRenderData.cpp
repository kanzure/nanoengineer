// Copyright 2008 Nanorex, Inc.  See LICENSE file for details.

#include "Nanorex/Interface/NXAtomRenderData.h"

#include <openbabel/atom.h>
using namespace OpenBabel;
using namespace std;


namespace Nanorex {

NXAtomRenderData::NXAtomRenderData(unsigned int const& the_atomicNum)
    : atomicNum(the_atomicNum)
{
}

} // Nanorex
