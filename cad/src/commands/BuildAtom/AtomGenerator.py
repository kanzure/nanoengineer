# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details.
"""
AtomGenerator.py - an example of a structure generator class meant
to be a template for developers.

The AtomGenerator class is an example of how a structure generator is
implemented for NanoEngineer-1.  The key points of interest are the
methods:  __init__, gather_parameters and build_struct.
They all **must always** be overridden when a new structure generator
class is defined.

The class variables cmd and prefix should be changed
to fit the new structure generator's role.

@author: Jeff Birac
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

History:
Jeff 2007-05-30: Based on Will Ware's GrapheneGenerator.py
Mark 2007-07-25: Uses new PM module.
"""

from utilities import debug_flags
import foundation.env as env
from model.chem import Atom
from model.chunk import Chunk
from geometry.VQT import V
from model.elements import PeriodicTable
from utilities.Log import greenmsg

from commands.BuildAtom.AtomGeneratorPropertyManager import AtomGeneratorPropertyManager
from command_support.GeneratorBaseClass import GeneratorBaseClass

def enableAtomGenerator(enable):
    """
    This function enables/disables the Atom Generator command by hiding or
    showing it in the Command Manager toolbar and menu.
    The enabling/disabling is done by the user via the "secret" NE1 debugging
    menu.

    To display the secret debugging menu, hold down Shift+Ctrl+Alt keys
    (or Shift+Cmd+Alt on Mac) and right click over the graphics area.
    Select "debug prefs submenu > Atom Generator example code" and
    set the value to True. The "Atom" option will then appear on the
    "Build" Command Manager toolbar/menu.

    @param enable: If true, the Atom Generator is enabled. Specifically, it
                   will be added to the "Build" Command Manager toolbar and
                   menu.
    @type  enable: bool
    """
    win = env.mainwindow()
    win.insertAtomAction.setVisible(enable)

# AtomGeneratorPropertyManager must come BEFORE GeneratorBaseClass in this list.
class AtomGenerator( AtomGeneratorPropertyManager, GeneratorBaseClass ):
    """
    The Atom Generator class provides the "Build > Atom" command for NE1.
    It is intended to be a simple example of how to add a new NE1 command
    that builds (generates) a new structure using parameters from a
    Property Manager and inserts it into the current part.
    """

    cmd     =  greenmsg("Build Atom: ")
    prefix  =  'Atom'   # used for gensym

    # Generators for DNA, nanotubes and graphene have their MT name generated
    # (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True

    # pass window arg to constructor rather than use a global.
    def __init__( self, win ):
        AtomGeneratorPropertyManager.__init__(self)
        GeneratorBaseClass.__init__(self, win)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters( self ):
        """
        Returns all the parameters from the Atom Generator's
        Property Manager needed to build a new atom (chunk).
        """
        x  =  self.xCoordinateField.value()
        y  =  self.yCoordinateField.value()
        z  =  self.zCoordinateField.value()

        # Get the chemical symbol and atom type.
        outElement, outAtomType  =  \
            self.pmElementChooser.getElementSymbolAndAtomType()

        return ( x, y, z, outElement, outAtomType )

    def build_struct( self, name, parameters, position ):
        """
        Build an Atom (as a chunk) according to the given parameters.

        @param name: The name which should be given to the toplevel Node of the
                     generated structure. The name is also passed in self.name.
        @type  name: str

        @param parameters: The parameter tuple returned from
                           L{gather_parameters()}.
        @type  parameters: tuple

        @param position: Unused. The xyz position is obtained from the
                         I{parameters} tuple.
        @type position:  position

        @return: The new structure, i.e. some flavor of a Node, which
                 has not yet been added to the model.  Its structure
                 should depend only on the values of the passed
                 parameters, since if the user asks to build twice, this
                 method may not be called if the parameterss have not
                 changed.
        @rtype:  Node
        """
        x, y, z, theElement, theAtomType  =  parameters

        # Create new chunk to contain the atom.
        outMolecule  =  Chunk( self.win.assy, self.name )
        theAtom      =  Atom( theElement, V(x, y, z), outMolecule )
        theAtom.set_atomtype( theAtomType )
        theAtom.make_enough_bondpoints()

        return outMolecule
