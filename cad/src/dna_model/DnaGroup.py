# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaGroup.py - ... 

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.
"""

from dna_model.Block import Block
#Following import is disabled. See addSegment method for reason.
##from dna_model.DnaSegment import DnaSegment

class DnaGroup(Block):
    """
    Model object which packages together some Dna Segments, Dna Strands,
    and other objects needed to represent all their PAM atoms and markers.

    The contents are not directly visible to the user in the model tree,
    except for Blocks (fyi, this behavior comes from our Block superclass,
    which is a kind of Group).
    
    But internally, most of the contents are Nodes which can be stored
    in mmp files, copied, and undo-scanned in the usual ways.

    Specific kinds of Group member contents include:
    - DnaStrands (optionally inside Blocks)
    - DnaSegments (ditto)
    - Blocks (a kind of Group)
    - DnaAtomMarkers (a kind of Jig, probably always inside an owning
      DnaStrand or DnaSegment)
    - specialized chunks for holding PAM atoms:
      - DnaAxisChunk (undecided whether these will live inside DnaSegments
        they belong to, but probably they will)
      - DnaStrandChunk (undecided whether these will live inside their
        DnaStrands, but probably they will)

    As other attributes:
    - whatever other properties the user needs to assign, which are not
      covered by the member nodes or superclass attributes.
    """
    # example method:
    def get_segments(self):
        """
        Return a list of all our DnaSegment objects.
        """
        return self.get_subnodes_of_class("DnaSegment") # IMPLEM get_subnodes_of_class
    

    def addSegment(self, segment):
        """
        Creates a new segment object for this dnaGroup
        @param segment: The DnaSegment to be added to this DnaGroup object
        @type: B{DnaSegment}  
        """
        #importing DnaSegment created an import cycle which throws error. 
        #So the isinstance check is is disabled for now. -- Here is the error
        ##Traceback (most recent call last):
            ##File "main.py", line 137, in ?
              ##_start_NE1()
            ##File "main.py", line 132, in _start_NE1
              ##startup_script( _main_globals )
            ##File "C:\Atom\cad\src\startup\main_startup.py", line 119, in startup_script
              ##from MWsemantics import MWsemantics
            ##File "C:\Atom\cad\src\MWsemantics.py", line 40, in ?
              ##from GLPane import GLPane
            ##File "C:\Atom\cad\src\GLPane.py", line 122, in ?
              ##from DnaDuplexEditController import DnaDuplexEditController
            ##File "C:\Atom\cad\src\DnaDuplexEditController.py", line 31, in ?
              ##from dna_model.DnaSegment import DnaSegment
            ##File "C:\Atom\cad\src\dna_model\DnaSegment.py", line 10, in ?
              ##from dna_model.DnaStrandOrSegment import DnaStrandOrSegment
            ##File "C:\Atom\cad\src\dna_model\DnaStrandOrSegment.py", line 11, in ?
              ##from dna_model.DnaGroup import DnaGroup
            ##File "C:\Atom\cad\src\dna_model\DnaGroup.py", line 11, in ?
              ##from dna_model.DnaSegment import DnaSegment
          ##ImportError: cannot import name DnaSegment
        
        ##assert isinstance(segment, DnaSegment)
        
        
        self.addchild(segment)

# end
