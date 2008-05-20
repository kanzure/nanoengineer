# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""
virtual_site_indicators.py - graphical indicators related to virtual sites
(as used in the current GROMACS implementation of the PAM5 force field);
presently used only to visualize such sites for debugging,
not as part of their implementation for minimize.

@author: Bruce
@version: $Id$
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
"""

from model.jigs import Jig
from utilities.constants import red, orange, yellow, average_value
from graphics.drawing.drawer import drawwirecube, drawline
from geometry.VQT import V

_superclass = Jig

class VirtualSiteJig(Jig): # rename file, non caps? virtual_site_indicators.py?
    """
    A Jig for internal use (also may appear in the MT for purpose of
    letting self.picked control drawing of extra info),
    for maintaining the relationship between some atoms which
    define a virtual site (the "parent atoms" or "defining atoms"),
    and an atom which represents the site itself
    (all of which are passed to this jig in its atomlist).
    Keeps the "site atom" positioned in the correct place.
    When picked, draws an indication of how the site atom position
    came from the parent atom positions.
    """

    # Jig or Node API class constants:
    
    sym = "VirtualSiteJig"

    icon_names = ('border/dna.png', 'border/dna.png') # stubs, not correct
    
    copyable_attrs = _superclass.copyable_attrs + ('_props', )

    # default values of instance variables

    _props = None
    
    # == Jig or Node API methods, and other methods

    def __init__(self, assy, atomlist):
        """
        """
        assert len(atomlist) >= 2
            # at least one parent atom, exactly one site atom (the last one)
        _superclass.__init__(self, assy, atomlist)
        return

    def site_atom(self):
        return self.atoms[-1]

    def parent_atoms(self):
        return self.atoms[:-1]

    def _draw_jig(self, glpane, color, highlighted = False): ### BUG: nothing calls this. maybe use chunk subclass to call it?? 
        """
        [overrides superclass method]
        """
        if self._should_draw():
            sitepos = self.site_position() # or, should we assume the atom pos is up to date? yes, use that. ### FIX
            colors = [red, orange, yellow]
            for a in self.parent_atoms():
                chunk = a.molecule
                dispdef = chunk.get_dispdef(glpane)
                disp, rad = a.howdraw(dispdef)
                if self.picked:
                    rad *= 1.01
                color = colors[0]
                drawwirecube(color, a.posn(), rad) # useful??
                drawline( color, a.posn(), sitepos)
                # draw each atom in a different color (at least if there are no more than 3)
                colors = colors[1:] + [color]
                continue
        return

    def _should_draw(self):
        return self.picked or self.site_atom().molecule.picked
            # so self needn't appear in MT if that chunk does

    def setProps(self, props):
        """
        Set the parameters which define the virtual site position
        as a function of the parent atom positions, and other properties.

        @param props: the new property values, in a certain order (see code)
        @type  props: tuple
        """
        self._props = props
        self._update_props()
        return

    def _update_props(self): ##### TODO: if we want these broken-out attrs, call this after copy or undo, or, before every use of self._props
        props = self._props
        self._function_id = props[0]
        if self._function_id == 1:
            self._x, self._y = props[1:]
        else:
            print "%r.setProps: don't recognize those props" % self, props
        return
    
    def site_position(self):
        return average_value( [a.posn() for a in self.parent_atoms()] ) # STUB, actually use self._function_id and _x and _y, or self._props

    def remove_atom(self, atom, **opts):
        """
        [extends superclass method]
        """
        self.kill()
            # note: should be ok, because in pi_bond_sp_chain,
            # this calls destroy which calls super.destroy which calls kill
        return

    def moved_atom(self, atom):
        """
        [extends superclass method]
        """
        if atom is not self.site_atom():
            self._update_site_atom_position()
        return

    def _update_site_atom_position(self):
        self.site_atom().setposn( self.site_position() )

    def changed_structure(self):
        pass ### disable self by user choice?? make the site_atom color more gray???
    
    pass

def make_virtual_site(assy, parent_atoms, site_params):
    """
    @return: list of nodes to add to MT
    """
    from model.chem import oneUnbonded
    from model.elements import Ss3 as Vs0 ### STUB
    site_atom = oneUnbonded(Vs0, assy, V(0,0,0))
    jig = VirtualSiteJig(assy, parent_atoms + [site_atom])
    jig.setProps(site_params) # so it knows how to compute site_position
    jig._update_site_atom_position()
    # also put them into the model somewhere? just the chunk. store the jig on the atom...
    ## return [ site_atom.molecule, jig ] # list of nodes for MT ### hmm, could let the jig draw if the atom chunk is picked...
    site_atom._site_atom_jig = jig ###
    return [ site_atom.molecule ] # list of nodes to be added to MT by caller

# == test code

from utilities.debug import register_debug_menu_command

def virtual_site_from_selatoms_command(glpane):
    assy = glpane.assy
    atoms = assy.selatoms.values() # arbitrary order, nevermind
    if len(atoms) != 3:
        errormsg = "select exactly 3 atoms to make a test virtual site"
        env.history.redmsg( errormsg)
        pass
    else:
        parent_atoms = list(atoms)
        site_params = ( 1, 0.5, 0.5 ) # stub
        nodes = make_virtual_site( assy, parent_atoms, site_params)
        for node in nodes:
            assy.addnode(node)
        pass
    assy.w.win_update()
    return

def initialize():
    """
    [called during startup]
    """
    register_debug_menu_command( "Test: virtual site from selatoms",
                                 virtual_site_from_selatoms_command )
    return

# end

