# Copyright 2008 Nanorex, Inc.  See LICENSE file for details.
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
2008-05-21 - 2008-06-01 Created and further refactored and modified
@See: ListWidgetItems_Command_Mixin,
      ListWidgetItems_GraphicsMode_Mixin
      ListWidgetItems_PM_Mixin,
      CrossoverSite_Marker
      MakeCrossovers_GraphicsMode


TODO  2008-06-01 :
- See class CrossoverSite_Marker for details
- more Documentation
"""

from exprs.If_expr import If_expr
from exprs.instance_helpers import DelegatingInstanceOrExpr
from exprs.Arrow           import Arrow
from exprs.ExprsConstants   import ORIGIN
from exprs.Highlightable    import Highlightable

from exprs.attr_decl_macros import Instance, Option, Arg
from exprs.ExprsConstants import Point
from utilities.constants import black, banana, copper, silver
from exprs.Set import Action
from exprs.__Symbols__ import _self
from exprs.attr_decl_macros import State
from exprs.__Symbols__ import Anything
from exprs.dna_ribbon_view import Cylinder
from exprs.ExprsConstants import Vector
from exprs.Overlay          import Overlay
from exprs.Exprs import call_Expr

class MakeCrossovers_Handle(DelegatingInstanceOrExpr):

    should_draw = State(bool, True)
    radius = 0.8

    point1 = Arg(Point)
    point2 = Arg(Point)

    scale = Arg(float)

    crossoverSite_marker =  Option(
        Action,
        doc = 'The CrossoverSite Marker class which instantiates this handle')

    #Command object specified as an 'Option' during instantiation of the class
    #see DnaSegment_EditCommand class definition.
    command =  Option(Action,
                      doc = 'The Command which instantiates this handle')



    crossoverPairs = Option(tuple, ())


    #Stateusbar text. Variable needs to be renamed in superclass.
    sbar_text = Option(str,
                       "Click on the handle to create this crossover",
                       doc = "Statusbar text on mouseover")


    delegate = If_expr(_self.should_draw,
                       Highlightable(
                           Overlay (
                               Cylinder((call_Expr(_self.crossoverPairs[0].posn),
                                         call_Expr(_self.crossoverPairs[3].posn)),
                                             radius = radius,
                                             color = silver),

                               Cylinder((call_Expr(_self.crossoverPairs[1].posn),
                                         call_Expr(_self.crossoverPairs[2].posn)),
                                             radius = radius,
                                             color = silver)),

                           Overlay (
                               Cylinder((call_Expr(_self.crossoverPairs[0].posn),
                                         call_Expr(_self.crossoverPairs[3].posn)),
                                             radius = radius,
                                             color = banana),

                               Cylinder((call_Expr(_self.crossoverPairs[1].posn),
                                         call_Expr(_self.crossoverPairs[2].posn)),
                                             radius = radius,
                                             color = banana)),

                           on_press = _self.on_press,
                           on_release = _self.on_release,
                           sbar_text = sbar_text
                           ))

    ##delegate = If_expr(_self.should_draw,
                       ##Highlightable(Cylinder((point1, point2),
                                              ##radius = radius,
                                              ##color = silver),
                                     ##Cylinder((point1, point2),
                                              ##radius = radius,
                                              ##color = banana),
                                     ##on_press = _self.on_press,
                                     ##on_release = _self.on_release))


    ##delegate = \
        ##If_expr(
            ##_self.should_draw,
            ##Highlightable(Arrow(
                ##color = silver,
                ##arrowBasePoint = point1,
                ####tailPoint = norm(vector)*1.0,
                ##tailPoint = point2,
                ##radius = radius,
                ##scale = scale),

                ##Arrow(
                ##color = banana,
                ##arrowBasePoint =  point1,
                ####tailPoint = norm(vector)*1.0,
                ##tailPoint =  point2,
                ##radius = radius,
                ##scale = scale),
                ##on_press = _self.on_press,
                ##on_release = _self.on_release ) ) #

    def hasValidParamsForDrawing(self):
        """
        Overridden in subclasses. Default implementation returns True
        if this object (the highlightable) can be drawn without any known
        issues
        @see: DnaStrand_ResizeHandle.hasValidParamsForDrawing for more notes.
        """
        ##self.should_draw = True
        return self.should_draw

    def on_press(self):
        pass

    def on_release(self):
        self.command.makeCrossover(self.crossoverPairs)
        self.crossoverSite_marker.removeHandle(self)

