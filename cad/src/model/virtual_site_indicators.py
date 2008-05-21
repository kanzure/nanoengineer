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
from utilities.constants import red, orange, yellow, average_value, ave_colors, blue, gray, darkgreen
from graphics.drawing.drawer import drawwirecube, drawline
from geometry.VQT import V, vlen

from model.chunk import Chunk

# ==

class VisualFeedbackJig(Jig):
    """
    A superclass for Jigs for internal or in-MT use
    in implementing visual feedback related to
    ND-1 pattern matching, virtual sites, and struts.
    """

    # Jig or Node API class constants:
    
    copyable_attrs = Jig.copyable_attrs + ('_props', )

    # default values of instance variables

    _props = None
    
    # == Jig or Node API methods

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
            #  that this does, as used in VirtualSiteJig.)
        return
    
    def changed_structure(self, atom):
        # review: should we disable self by user choice??
        # make the site_atom color more gray [in some subclasses]???
        # not unless we confirm it's a change that really matters!
        # (note: this is called at least once during or shortly after
        # construction of the VirtualSiteJig, not sure why.)
        return

    # == other methods

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
        """
        Subclasses can use this to set private attributes
        from self._props and to check for errors in that process.

        Methods in self (this class or subclasses) should call this
        in setProps to check for errors, and before every use
        of private attrs this sets from self._props, to make sure
        they are up to date in case self._props has changed somehow.
        (Though it may be that it can't change once set, in current code.)
        """
        # note: if we didn't want to call this before every use,
        # we'd at least need to call it after copy (in the copy)
        # and in undo_update.
        return
    
    pass # end of class VisualFeedbackJig

# ==

class VirtualSiteJig( VisualFeedbackJig):
    """
    A Jig for internal use (also may appear in the MT for purpose of
    letting self.picked control drawing of extra info, but doesn't
    appear there in present implementation of external code),
    for maintaining the relationship between some atoms which
    define a virtual site (the "parent atoms" or "defining atoms"),
    and an atom which represents the site itself
    (all of which are passed to this jig in its atomlist).
    Keeps the "site atom" positioned in the correct place.
    When picked (or when the site atom's chunk is picked),
    draws an indication of how the site atom position
    came from the parent atom positions.
    """

    # Jig or Node API class constants:
    
    sym = "VirtualSiteJig"

    icon_names = ('border/dna.png', 'border/dna.png') # stubs, not correct
    
    # == Jig or Node API methods, and other methods

    def __init__(self, assy, atomlist):
        """
        """
        assert len(atomlist) >= 2
            # at least one parent atom, exactly one site atom (the last one)
        VisualFeedbackJig.__init__(self, assy, atomlist)
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

    def _update_props(self):
        """
        [overrides superclass method]
        """
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
    
    def moved_atom(self, atom):
        """
        [extends Jig method]
        """
        if atom is not self.site_atom():
            self._update_site_atom_position()
        return

    def _update_site_atom_position(self):
        self.site_atom().setposn( self.site_position() )
    
    pass # end of class VirtualSiteJig

# ==

class VirtualBondJig( VisualFeedbackJig):
    """
    For virtual bonds, including PAM5 FF "struts".
    """
    # Jig or Node API class constants:
    
    sym = "VirtualBondJig"

    icon_names = ('border/dna.png', 'border/dna.png') # stubs, not correct
    
    # == Jig or Node API methods, and other methods

    def __init__(self, assy, atomlist):
        """
        """
        assert len(atomlist) == 2
        VisualFeedbackJig.__init__(self, assy, atomlist)
        return

    def _draw_jig(self, glpane, color, highlighted = False):
        """
        [overrides superclass method]
        """
        del color
        self._update_props()
        if highlighted:
            color = yellow
        elif self.picked:
            color = darkgreen
        else:
            color = self._drawing_color()
        ## if self._should_draw_thicker(): ###k is this right?
        ##     # todo: in this case draw a cyl, with glname, MT highlight behavior, etc...
        if 1: # stub
            posns = [a.posn() for a in self.atoms]
            drawline( color, posns[0], posns[1], width = 2 ) # cylinder?
        return

    def _should_draw_thicker(self): # not yet used
        return self.picked or \
               self.atoms[0].molecule.picked or \
               self.atoms[1].molecule.picked

    def _update_props(self):
        """
        [overrides superclass method]
        """
        props = self._props
        self._ks, self._r0 = props # TODO: use in draw, tooltip
        return

    def _drawing_color(self):
        r0 = self._r0 # pm
        ks = self._ks # N/m
        length_in_Angstroms = vlen( self.atoms[0].posn() - self.atoms[1].posn() )
        length = 100.0 * length_in_Angstroms # in pm == picometers
        frac = 1 - 1 / (0.05 * ks * abs(r0 - length) + 1)
        if length < r0:
            # compressed: blue (gray if not at all, blue if a lot; should use ks somehow to get energy or force...)
            # limit = r0 * 0.5
            #frac = (r0 - length) / (r0 * 0.5) # if > 1, we'll use 1 below
            limit_color = blue
        else:
            # stretched
            # limit = r0 * 1.5
            #frac = (length - r0) / (r0 * 0.5)
            limit_color = red
        neutral_color = gray
        if frac > 1.0:
            frac = 1.0
        color = ave_colors( frac, limit_color, neutral_color )
        return color
        
    pass # end of class VirtualBondJig

# ==

class VirtualSiteChunk(Chunk):
    """
    """
    # someday: custom icon for MT?
    # note: mmp save/reload would not preserve this chunk subclass

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

def make_virtual_site( assy, parent_atoms, site_params, MT_name = None):
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
        jig.name = "%s" % (MT_name,) # not presently user-visible, I think
            # (except maybe in statusbar when self is selobj?)
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
    return site_atom

# ==

def make_virtual_bond( assy, atoms, bond_params, MT_name = None ):
    """
    @return: liat of objects to add to model
    """
    jig = VirtualBondJig( assy, atoms )
    jig.setProps( bond_params)
    # also put them into the model somewhere? not for now. just make it findable/drawable from its atoms. NIM
    ###### PROBLEM: how will two chemical atoms draw one of these?
    # - could put it in the model
    #   - only needed if both atoms are chem, since VirtualSiteChunk could draw it itself
    #     (best implem?: ask each atom's chunk if it has a special property that says it'll draw it)
    # - could add features to Atom.draw
    # - could reimplement it as a Bond subclass (bond order zero??);
    #   but worry about bugs in Bond selobj code in various modes
    needed_in_model = True # STUB -- see above for a better rule!
    if MT_name:
        jig.name = "%s" % (MT_name,)
    res = []
    if needed_in_model:
        res.append(jig)
    return res

# ==

def add_virtual_bond( assy, atoms, bond_params, MT_name = None ):
    """
    @return: None
    """
    nodes = make_virtual_bond( assy, atoms, bond_params, MT_name = MT_name)
    for node in nodes:
        assy.addnode(node) # todo: add them in a better place?
    return

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

