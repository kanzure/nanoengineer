# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
An example of a structure generator class meant 
to be a template for developers.

The AtomGenerator class is an example of how structure generator is
implemented for NanoEngineer-1.  The key points of interest are the 
methods:  __init__, gatherParameter and buildStruct.  
They all **must always** be overriden when a new structure generator 
class is defined.

The class variables cmd, prefix and sponsor_keyword should be changed 
to fit the new structure generator's role.

@author: Jeff Birac
@copyright: Copyright (c) 2007 Nanorex, Inc.  All rights reserved.
@version: 0.1

AtomGenerator.py

$Id$

History:
Jeff 2007-05-30: Based on Will Ware's GrapheneGenerator.py
"""

__author__ = "Jeff"

import platform, env
from chem import molecule, Atom
from VQT import V
import string
from elements import PeriodicTable
from HistoryWidget import greenmsg

from PyQt4.Qt import QDialog
from AtomGeneratorDialog import AtomPropertyManager
from GeneratorBaseClass import GeneratorBaseClass

def enableAtomGenerator(enable):
    """Enables/disables the Atom Generator by hiding or showing it.
    This is normally done by the user via the debugging menu.
    <enable> - boolean, where:
      True = show Atom Generator button/menu item
      False = hide Atom Generator button/menu item
    """
    win = env.mainwindow()
    win.insertAtomAction.setVisible(enable)

# AtomPropertyManager must come BEFORE GeneratorBaseClass in this list.
class AtomGenerator( QDialog, AtomPropertyManager, GeneratorBaseClass ):
    """The Atom Generator class.
    """

    cmd     =  greenmsg("Build Atom: ")
    prefix  =  'Atom-'   # used for gensym

    # Generators for DNA, nanotubes and graphene have their MT name generated 
    # (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix  =  True 

    # We now support multiple keywords 
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword  =  'Atom'

    # pass window arg to constructor rather than use a global.
    def __init__( self, win ):
        QDialog.__init__(self, win)
        AtomPropertyManager.__init__(self)
        GeneratorBaseClass.__init__(self, win)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters( self ):
        """Return a tuple of all the parameters from the Property Manager.
        """
        x  =  self.xCoordinateField.value()
        y  =  self.yCoordinateField.value()
        z  =  self.zCoordinateField.value()
        
        # Get the chemical symbol.
        outElement  =  str(self.elementComboBox.currentText())

        return ( x, y, z, outElement )

    def build_struct( self, inName, inParams, inPosition ):
        """Build an Atom (as a chunk) according to the given parameters.
        """
        x, y, z, theElement  =  inParams

        # Create new molecule (chunk) to contain the atom.
        outMolecule  =  molecule( self.win.assy, self.name )
        theAtom      =  Atom( theElement, V(x, y, z), outMolecule)
        theAtom.make_enough_bondpoints()

        return outMolecule
