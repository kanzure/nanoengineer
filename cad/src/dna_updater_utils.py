# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
dna_updater_utils.py -- utilities for dna_updater.py

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

def replace_atom_class(assy, atom, newclass, *atomdicts): #e refile??
    """
    Change atom's class to newclass.

    This might be done by directly replacing atom.__class__,
    or by making a new Atom instance (identical except for __class__)
    and replacing atom with newatom in the rest of the model (assy)
    and in all transient state that might point to atom (accessible
    via assy). If any atomdicts are passed, they are assumed to be
    atom.key -> atom dicts in which atom should be also replaced with
    newatom (at the same key, since it will be given the same .key).

    @param assy: the model in which atom resides.
    @type assy: Assembly.

    @param atom: a real atom or bondpoint of any subclass of Atom.
    @type atom: Atom.

    @param newclass: any subclass of Atom.
    @type newclass: class

    @param atomdicts: zero or more dicts which map atm.key to atm
                      and in which atom should be replaced with
                      newatom if necessary.
    @type atomdicts:  zero or more dictionaries.
    
    @return: None. (If newatom is needed, caller should get it
                   from one of the atomdicts.)
    """
    # The present implem works by directly resetting atom.__class__,
    # since this works in Python (though I'm not sure how officially
    # it's supported) and is much simpler and faster than the alternative.
    #
    # (This is not a kluge, except to the extent that it might not be
    # officially supported. It's a well-defined concept (assuming the
    # classes are written to be compatible), is officially supported
    # in some languages, and does exactly what we want.)
    #
    # If resetting __class__ ever stops working, we'll have to implement
    # this function in a much harder way: make a new Atom of the desired
    # class, and then replace atom with newatom everywhere it occurs,
    # both in the model and in all transient state -- in bonds, jigs,
    # chunks (including hotspot), part.selatoms, glpane.selobj/.selatom,
    # and any other state I'm forgetting or that gets added to the code.
    # (But I think we could get away without also replacing it in undo diffs
    # or the glname allocator, since the old atom won't have had a chance
    # to get into undo diffs by the time the dna_updater runs, or to get
    # drawn (so its glname won't matter yet).)
    # 
    # See outtakes/Atom_replace_class.py for unfinished code which does
    # some of that work, and a more detailed comment about what would have
    # to be done, also covering analogous replacements for Bond and Chunk.
    
    atom.__class__ = newclass
    return

def replace_bond_class(assy, bond, newclass, *bonddicts): #e refile??
    """
    Like replace_atom_class, except for Bonds.
    The bonddicts map id(bond) -> bond.
    """
    bond.__class__ = newclass
    return

# end
