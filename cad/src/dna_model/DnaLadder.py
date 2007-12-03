# Copyright 2007 Nanorex, Inc.  See LICENSE file for details. 
"""
DnaLadder.py - ... 

Used internally; may or may not be a Node, though some kinds
of Chunk might own a ladder or "ladder rail".

@author: Bruce
@version: $Id$
@copyright: 2007 Nanorex, Inc.  See LICENSE file for details.

Context:

The PAM atoms in any PAM DNA structure will be internally divided into
"ladders", in which all the bonding strictly follows the pattern

 ... -+-+-+-+-+-+- ... (strand 1)
      | | | | | | 
 ... -+-+-+-+-+-+- ... (axis)
      | | | | | | 
 ... -+-+-+-+-+-+- ... (strand 2; missing if single-stranded)

(with the strand bond directions antiparallel and standardized).

The dna updater will maintain these ladders, updating them
when their structure is changed. So a changed atom in a ladder will
either dissolve or fragment its ladder (or mark it for the updater to
do that when it next runs), and the updater, dealing with all changed
atoms, will scan all the atoms not in valid ladders to make them into
new ladders (merging new ladders end-to-end with old ones, when that's
valid, and whe they don't become too long to be handled efficiently).

A Dna Segment will therefore consist of a series of ladders (a new one
at every point along it where either strand has a nick or crossover,
or at other points to make it not too long). Each "ladder rail"
(one of the three horizontal atom-bond chains in the figure")
will probably be a separate Chunk, though the entire ladder should
have a single display list for efficiency (so its rung bonds are
in a display list) as soon as that's practical to implement.

So the roles for a ladder include:
- guide the dna updater in making new chunks
- have display code and a display list

A ladder will be fully visible to copy and undo (i.e. it will
contain undoable state), but will not be stored in the mmp file.
"""


### REVIEW: should a DnaLadder contain any undoable state?
# (guess: yes... maybe it'll be a Group subclass, for sake of copy & undo?
#  for now, assume just an object (not a Node), and try to fit it into
#  the copy & undo code in some other way... or I might decide it's entirely
#  implicit re them.) If that gets hard, make it a Group. (Where in the internal MT?
#  whereever the chunks would have been, without it.)

class DnaLadder(object):
    """
    """
    def __init__(self, axis_rail):
        self.axis_rail = axis_rail
        self.strand_rails = []
    def add_strand_rail(self, strand_rail):
        ## assert strand_rail.baselength() == self.axis_rail.baselength()# IMPLEM baselength
        self.strand_rails.append(strand_rail)
        return
    def finished(self):
        ## assert len(self.strand_rails) in (1,2)
        # happens in mmkit - leave it as just a print at least until we implem "delete bare atoms" -
        if not ( len(self.strand_rails) in (1,2) ):
            print "error: DnaLadder %r has %d strand_rails " \
                  "(should be 1 or 2)" % (self, len(self.strand_rails))
        for rail in self.strand_rails:
            pass # reverse if nec to fit axis_rail?? or later? @@@
    pass

# end
