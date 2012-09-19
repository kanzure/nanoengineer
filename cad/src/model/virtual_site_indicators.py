# Copyright 2008-2009 Nanorex, Inc.  See LICENSE file for details.
"""
virtual_site_indicators.py - graphical indicators related to virtual sites
(as used in the current GROMACS implementation of the PAM5 force field);
presently used only to visualize such sites for debugging,
not as part of their implementation for minimize.

@author: Bruce
@version: $Id$
@copyright: 2008-2009 Nanorex, Inc.  See LICENSE file for details.
"""

import foundation.env as env


from utilities.prefs_constants import hoverHighlightingColor_prefs_key
from utilities.prefs_constants import selectionColor_prefs_key

from utilities.constants import red, orange, yellow, average_value, ave_colors, blue, gray

from utilities.Log import quote_html

from geometry.VQT import V, vlen


from graphics.drawing.drawers import drawwirecube

from graphics.drawing.CS_draw_primitives import drawline
from graphics.drawing.CS_draw_primitives import drawcylinder

from graphics.drawing.patterned_drawing import isPatternedDrawing
from graphics.drawing.patterned_drawing import startPatternedDrawing
from graphics.drawing.patterned_drawing import endPatternedDrawing


from model.chunk import Chunk

from model.jigs import Jig

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

    def _any_atom_is_hidden(self):
        """
        """
        for atom in self.atoms:
            if atom.is_hidden():
                return True
        return False

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

    def _getToolTipInfo(self): # VirtualSiteJig
        # untested, since some ###BUG prevents this from being shown
        """
        Return a string for display in self's Dynamic Tool tip.

        (Appears when user highlights this jig's drawing,
         but unrelated to tooltip on our site_atom itself.)

        [overridden from class Jig]
        """
        self._update_props() # doesn't yet matter in this method
        msg = "%s: %s" % (self.sym, quote_html(self.name)) + \
              "<br><font color=\"#0000FF\">" \
              "%s</font>" % (self._props,)
        return msg

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
        # note: this is not about whether to draw the site_atom
        # (which is done by a different object),
        # but about whether to draw connections from it to its parent atoms.
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

    def _getToolTipInfo(self): # VirtualBondJig
        """
        Return a string for display in self's Dynamic Tool tip.

        [overridden from class Jig]
        """
        self._update_props()
        ks = self._ks # N/m
        r0 = self._r0 # pm
        length = self._getLength() # pm
        force = ks * (length - r0) # pN
        msg = "%s: %s" % (self.sym, quote_html(self.name)) + \
              "<br><font color=\"#0000FF\">" \
              "ks = %f N/m<br>" \
              "r0 = %f pm<br>" \
              "len = %f pm<br>" \
              "len/r0 = %f<br>" \
              "force = %f pN</font>" % (ks, r0, length, length/r0, force)
        return msg

    def _draw_jig(self, glpane, color, highlighted = False):
        """
        [overrides superclass method]
        """
        del color
        self._update_props()
        if not self._should_draw():
            return

        drawrad = 0.1
        posns = [a.posn() for a in self.atoms]
        normcolor = self._drawing_color()

        # russ 080530: Support for patterned highlighting drawing modes.
        selected = self.picked
        patterned = isPatternedDrawing(select = selected, highlight = highlighted)
        if patterned:
            # Patterned selection drawing needs the normal drawing first.
            drawcylinder( normcolor, posns[0], posns[1], drawrad)
            startPatternedDrawing(select = selected, highlight = highlighted)
            pass
        # Draw solid color, or overlay pattern in highlight or selection color.
        drawcylinder(
            (highlighted and env.prefs[hoverHighlightingColor_prefs_key] or
             selected and env.prefs[selectionColor_prefs_key] or
             normcolor), posns[0], posns[1], drawrad)
        if patterned:
            # Reset from patterned drawing mode.
            endPatternedDrawing(select = selected, highlight = highlighted)
            pass
        return

    def _should_draw(self):
        return not self._any_atom_is_hidden() #080520 new feature

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

    def _getLength(self):
        length_in_Angstroms = vlen( self.atoms[0].posn() - self.atoms[1].posn() )
        length = 100.0 * length_in_Angstroms # in pm == picometers
        return length

    def _drawing_color(self):
        r0 = self._r0 # pm
        ks = self._ks # N/m
        length = self._getLength() # pm
        frac = 1 - 1 / (0.08 * ks * abs(r0 - length) + 1)
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
        ## neutral_color = gray
        neutral_color = (0.8, 0.8, 0.8) # "very light gray"
        if frac > 1.0:
            frac = 1.0
        color = ave_colors( frac, limit_color, neutral_color )
        return color

    pass # end of class VirtualBondJig

# ==

class VirtualSiteChunkDrawer( Chunk._drawer_class ): #bruce 090212 split this out (###UNTESTED)
    def _draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible):
        Chunk._drawer_class._draw_outside_local_coords(self, glpane, disp, drawLevel, is_chunk_visible)
        for atom in self._chunk.atoms.itervalues():
            if hasattr(atom, '_site_atom_jig'):
                color = 'not used'
                atom._site_atom_jig._draw_jig(glpane, color) # note: needs to be in abs coords
                ## print "called %r._draw_jig" % atom # works
                pass
            continue
        return
    pass

class VirtualSiteChunk(Chunk):
    """
    A chunk that (initially) has only a virtual site atom, and represents it in the MT.
    This atom will also have a VirtualSiteJig (and be its site_atom),
    which cooperates with us in some sense, and which we can find
    via that atom.

    Nothing prevents a user from merging several of these chunks
    into one. Its jig-drawing code will still work then.

    Nothing prevents merging it into a regular chunk, but doing that
    would break that code (i.e. stop drawing the VirtualSiteJigs),
    so users shouldn't do that.
    """
    # someday: custom icon for MT?
    # note: mmp save/reload would not preserve this chunk subclass

    # maybe someday: hide our atom if some or all of our parent atoms
    # are hidden. Do this by self.hidden = True so it's noticed by
    # any VirtualBondJigs on our atom. Not simple, since it needs to be
    # done before drawing, not during it, since it's a model change
    # (doing that during drawing can cause bugs); but hidden state
    # can't yet be subscribed to. Maybe an update_parts hook could do it?
    # Not sure if even that would be safe (in terms of changing the model
    # then), though I guess it probably is since updaters change it quite a bit.
    # Anyway, for now, this feature is not needed.

    _drawer_class = VirtualSiteChunkDrawer
    pass

# ==

def make_virtual_site( assy, parent_atoms, site_params, MT_name = None):
    """
    @return: ( object to assign to site_atom_id, list of nodes to add to MT )
    """
    from model.elements import Vs0
    site_atom = assy.make_Atom_and_bondpoints(Vs0, V(0,0,0), Chunk_class = VirtualSiteChunk)
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
            # review: redundant with make_Atom_and_bondpoints?
    return site_atom

# ==

def make_virtual_bond( assy, atoms, bond_params, MT_name = None ):
    """
    @return: liat of objects to add to model
    """
    jig = VirtualBondJig( assy, atoms )
    jig.setProps( bond_params)
    # also put them into the model somewhere? not for now. just make it findable/drawable from its atoms. NIM
    #### PROBLEM: how will two chemical atoms draw one of these?
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

