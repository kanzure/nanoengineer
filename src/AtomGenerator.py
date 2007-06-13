# Copyright 2006-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
AtomGenerator.py

$Id$

History:
Jeff 2007-05-30: Based on Will Ware's GrapheneGenerator.py
"""

__author__ = "Jeff"

import platform
#from math import atan2, sin, cos, pi
#import assembly, chem, bonds, Utility
from chem import molecule, Atom
from VQT import V
import string
from elements import PeriodicTable
from HistoryWidget import greenmsg

from PyQt4.Qt import QDialog
from AtomGeneratorDialog import AtomPropMgr
from GeneratorBaseClass import GeneratorBaseClass

# AtomPropMgr must come BEFORE GeneratorBaseClass in this list.
class AtomGenerator( QDialog, AtomPropMgr, GeneratorBaseClass ):
    """The Atom Generator class.
    """

    cmd = greenmsg("Build Atom: ")
    prefix = 'Atom-'   # used for gensym

    # Generators for DNA, nanotubes and graphene have their MT name generated 
    # (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = True 
    # We now support multiple keywords 
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword = 'Atom'

    # pass window arg to constructor rather than use a global.
    def __init__( self, win ):
        QDialog.__init__(self, win)
        AtomPropMgr.__init__(self)
        GeneratorBaseClass.__init__(self, win)

    ###################################################
    # How to build this kind of structure, along with
    # any necessary helper functions

    def gather_parameters( self ):
        """Return all the parameters from the Property Manager.
        """
        x  =  self.xCoordinateField.value()
        y  =  self.yCoordinateField.value()
        z  =  self.zCoordinateField.value()
        element = str(self.elementComboBox.currentText()) # chemical symbol
        
        return ( x, y, z, element )

    def build_struct( self, name, params, position ):
        """Build an Atom (as a chunk) from the 
           parameters in the Property Manager.
        """
        x, y, z, element  =  params
        
        mol = molecule(self.win.assy, name)
        atm = Atom(element, V(x, y, z), mol)
        atm.make_enough_bondpoints()

        return mol

