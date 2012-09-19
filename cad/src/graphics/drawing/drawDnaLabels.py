# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-08-14 created.
Originally created in BreakOrJoinstrands_GraphicsMode. Moved into its own
module as its a general helper function used by many GraphicsModes

TODO:
- allow prefs_keys as an argument for draw_dnaBaseNumberLabels
- refactor. some code (sub def func in draw_dnaBaseNumberLabels)
  may better be in a dna/model class?
"""
import foundation.env as env
from PyQt4.Qt import QFont, QString

from utilities.prefs_constants import dnaBaseNumberLabelColor_prefs_key
from utilities.prefs_constants import dnaBaseNumberingOrder_prefs_key
from utilities.prefs_constants import dnaBaseNumberLabelChoice_prefs_key


def _correct_baseatom_order_for_dnaStrand(strand, baseatoms):
    """
    See a TODO comment in this method body.
    @see: _draw_dnaBaseNumberLabels()

    """
    #@TODO: REVISE this. Its only called from _draw_dnaBaseNumberLabels()
    #See if this method should be a moved to DnaStrand class and
    #some portion of the ._draw_dnaBaseNumberLabels() that returns
    #baseatoms to class DnaStrandOrSegment. Issue with this refactoring:
    #there is a method in DnaStrand class that returns baseatoms in bond
    #direction. May be it needs to be revised/ replaced with
    #wholechain.get_all_base_atoms_in_order()
    #-- Ninad 2008-08-06
    numberingOrder = env.prefs[dnaBaseNumberingOrder_prefs_key]
    five_prime_end = strand.get_five_prime_end_base_atom()
    if five_prime_end:
        if numberingOrder == 0:
            if not five_prime_end is baseatoms[0]:
                baseatoms.reverse()
        elif numberingOrder == 1:
            if five_prime_end is baseatoms[0]:
                baseatoms.reverse()
    return baseatoms


def draw_dnaBaseNumberLabels(glpane):
    """
    Draw the DNA basee number labels.

    baseNumLabelChoice:(obtained from command class)
    0 =  None
    1 = Strands and Segments
    2 =  Strands Only
    3 =  Segments Only

    @see: _correct_baseatom_order_for_dnaStrand()
    @see: BuildDna_GraphicsMode._drawLabels()
    """

    win = glpane.win

    baseNumLabelChoice = env.prefs[dnaBaseNumberLabelChoice_prefs_key]

    if glpane.scale > 65.0:
        fontSize = 9
    else:
        fontSize = 12

    if baseNumLabelChoice == 0:
        return


    segments = win.assy.part.get_topmost_subnodes_of_class(win.assy.DnaSegment)
    strands =  win.assy.part.get_topmost_subnodes_of_class(win.assy.DnaStrand)

    font = QFont( QString("Helvetica"), fontSize)
    textColor = env.prefs[dnaBaseNumberLabelColor_prefs_key]
    # WARNING: Anything smaller than 9 pt on Mac OS X results in
    # un-rendered text.


    def func(strandOrSegmentList):
        for strandOrSegment in strandOrSegmentList:
            #Don't draw the labels if the strand or segment is hidden
            if strandOrSegment.all_content_is_hidden():
                continue
            whole_chain = strandOrSegment.get_wholechain()
            if whole_chain is None:
                continue
            baseatoms = whole_chain.get_all_baseatoms_in_order()

            if isinstance(strandOrSegment, win.assy.DnaStrand):
                baseatoms = _correct_baseatom_order_for_dnaStrand(
                    strandOrSegment,
                    baseatoms)

            i = 1
            for atm in baseatoms:
                text = "%d" %(i)
                highlighting_radius = atm.highlighting_radius()
                if highlighting_radius < 1.2:
                    highlighting_radius = 4.0
                pos = atm.posn() + (0.03+ highlighting_radius)*glpane.out ##+ (glpane.right + glpane.up)

                glpane.renderTextAtPosition(pos,
                                            text,
                                            textColor = textColor,
                                            textFont = font)

                i += 1

    if baseNumLabelChoice in (1, 2):
        func(strands)
    if baseNumLabelChoice in (1, 3):
        func(segments)


