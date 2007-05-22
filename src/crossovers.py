# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
crossovers.py -- support for DNA crossovers, modelled at various levels

$Id$
"""
__author__ = "bruce"

from constants import noop

def crossover_menu_spec(atom, selatoms):
    """Make a crossover-related menu_spec list for the two atoms in the
    selatoms dict (atom.key -> atom), both Pl, for use in atom's context menu
    (which must be one of the atoms in selatoms). If no menu commands are needed,
    return [] (a valid empty menu_spec) or None.
       Should be reasonably fast, but needn't be super-fast -- called once
    whenever we construct a context menu for exactly two selected Pl atoms.
    """
    assert len(selatoms) == 2
    atoms = selatoms.values()
    assert atom in atoms
    for a1 in atoms:
        assert a1.element.symbol == 'Pl'

    
    return [("crossover stub", noop, 'disabled'),
            ("crossover stub 2", noop,)
           ] ###STUB for testing

# end
