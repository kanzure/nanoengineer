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

from model.chunk import Chunk

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

    def _draw_jig(self, glpane, color, highlighted = False):
        """
        [overrides superclass method]
        """
        # note: kluge: called directly from a specialized Chunk, not from self.draw!
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

    def _update_props(self):
        ##### TODO: if we want these broken-out attrs, call this after copy or undo, or, before every use of self._props
        props = self._props
        self._function_id = props[0]
        if self._function_id == 1:
            self._x, self._y = props[1:]
        else:
            print "%r.setProps: don't recognize those props" % self, props
        return
    
    def site_position(self):
        ## return average_value( [a.posn() for a in self.parent_atoms()] )
        ##     # STUB, actually use self._function_id and _x and _y, or self._props
        self._update_props()
        if self._function_id == 1 and len(self.parent_atoms()) == 3:
            # the only supported kind so far
            parentID1, parentID2, parentID3 = self.parent_atoms()
            A = self._x
            B = self._y
            #   Multiply the vector (parentID2 - parentID1) * A
            #   Multiply the vector (parentID3 - parentID1) * B
            #   Add the above two vectors to parentID1
            pos1 = parentID1.posn()
            pos2 = parentID2.posn()
            pos3 = parentID3.posn()
            return pos1 + (pos2 - pos1) * A + (pos3 - pos1) * B
        else:
            print "bug: unsupported kind of virtual site:", self._props
            return average_value( [a.posn() for a in self.parent_atoms()] )
        pass
            
    def remove_atom(self, atom, **opts):
        """
        [extends superclass method]
        """
        if getattr(self, '_being_killed', False):
            return # prevent infinite recursion (I hope #k)
        self._being_killed = True # only used in this file as of 080520
        self.kill()
            # Note: should be ok, because in pi_bond_sp_chain,
            # this calls destroy which calls super.destroy which calls kill.
            # (I don't know why that doesn't have the same recursion problem
            #  that this does.)
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

    def changed_structure(self, atom):
        # review: should we disable self by user choice??
        # make the site_atom color more gray???
        # not unless we confirm it's a change that really matters!
        # (this is called at least once during construction of this jig,
        #  not sure why.)
        return
    
    pass # end of class VirtualSiteJig

# ==

class VirtualSiteChunk(Chunk):
    """
    """
    # someday: custom icon for MT?
    # note: mmp save/reload would not preserve this chunk subclass
##    def __init__(self, assy, name = None):
##        Chunk.__init__(self, assy, name)
##        return
##    def _get_hotspot(self): # called by __getattr__
##        # kluge: override superclass method, just so draw always calls overdraw_hotspot
##        for atom in self.atoms.itervalues():
##            if hasattr(atom, '_site_atom_jig'):
##                return atom # which atom we return probably doesn't matter
##                    # possible bug: is returning a non-singlet hotspot ok??
##        return Chunk._get_hotspot(self)
##    def overdraw_hotspot(self, glpane, disp):
##        # kluge; ideally we'd add another draw submethod to class Chunk
##        # and override that instead; can't use _draw_external_bonds
##        # since it's not called if there are no such bonds

    def _draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible):
        Chunk._draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible)
        for atom in self.atoms.itervalues():
            if hasattr(atom, '_site_atom_jig'):
                color = 'not used'
                atom._site_atom_jig._draw_jig(glpane, color) # note: needs to be in abs coords
                ## print "called %r._draw_jig" % atom # works
                pass
            continue
        return
    pass

# ==

def make_virtual_site(assy, parent_atoms, site_params, MT_name = None):
    """
    @return: ( object to assign to site_atom_id, list of nodes to add to MT )
    """
    from model.chem import oneUnbonded
    from model.elements import Vs0
    site_atom = oneUnbonded(Vs0, assy, V(0,0,0), Chunk_class = VirtualSiteChunk)
    jig = VirtualSiteJig(assy, parent_atoms + [site_atom])
    jig.setProps(site_params) # so it knows how to compute site_position
    jig._update_site_atom_position()
    # also put them into the model somewhere? just the chunk. store the jig on the atom...
    ## return [ site_atom.molecule, jig ] # list of nodes for MT ### hmm, could let the jig draw if the atom chunk is picked...
    site_atom._site_atom_jig = jig # used (for drawing the jig) only if this atom is in a VirtualSiteChunk
    # todo: put something useful into the tooltip and the chunk name
    if MT_name:
        site_atom.molecule.name = "%s" % (MT_name,)
    return site_atom, [ site_atom.molecule ]

# ==

def add_virtual_site(assy, parent_atoms, site_params, MT_name = None):
    """
    @return: object to assign to site_atom_id

    @warning: caller must call assy.w.win_update()
    """
    site_atom, nodes = make_virtual_site( assy, parent_atoms, site_params, MT_name = MT_name)
    for node in nodes:
        assy.addnode(node) # todo: add them in a better place?
            # review: redundant with oneUnbonded?
##        if node.part is None:
##            # review: shouldn't addnode do this for us? yes... and it already does!!
##            # (so it's not always necessary to call update_parts)
##            # (otoh, does our need to do it mean we have some other bug,
##            #  like nothing calling assy.changed?)
##            # BUG: somehow this .part gets reset to None at some point...
##            # guess: by the time we killed the atom, we'd already grabbed the atoms to sim... yes.
##            print "bug: addnode failed to set %r.part" % node # should never happen 
##            node.inherit_part(node.dad.part)
    return site_atom

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
        site_atom, nodes = make_virtual_site( assy, parent_atoms, site_params)
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

