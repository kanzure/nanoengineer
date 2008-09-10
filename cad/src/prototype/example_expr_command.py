# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
example_expr_command.py -- example of how to use an interactive graphics
expr in a command (unfinished, so partly scratch code); command and PM
are each variants of ExampleCommand1's command and PM classes
 
@author: Bruce
@version: $Id$
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.

History:

070830 bruce split this out of test_commands.py and test_command_PMs.py,
in which it was called ExampleCommand2E
"""

# == PM class

from prototype.test_command_PMs import ExampleCommand1_PM

from PM.PM_LineEdit      import PM_LineEdit
from PM.PM_GroupBox      import PM_GroupBox

_superclass_PM = ExampleCommand1_PM

class ExampleCommand2E_PM( ExampleCommand1_PM ):
    # NOTE: used to use ExampleCommand2_PM which uses GBC; UNTESTED with this superclass [bruce 080910]
    """
    Property Manager for Example Command 2E
    """
    title = "Example Command 2E"
    prefix = "Thing2E" # for names created by GBC
    
    def _addGroupBoxes(self):
        """
        Add group boxes to this Property Manager.
        """
        _superclass_PM._addGroupBoxes(self)
        
        self.pmGroupBox2 = PM_GroupBox( self, title =  "group box 2" )
        self._loadGroupBox2(self.pmGroupBox2)
        
        return
    
    def _loadGroupBox2(self, groupbox):
        """
        Load widgets into group box 2.
        """
        self.someLineEdit  =  \
            PM_LineEdit( groupbox,
                         label        = "Text:",
                         text         = "initial text (pm)",
                         setAsDefault = True,
                         spanWidth    = False )
        ### TODO: self.someLineEdit.connectWithState( ... some text state ...)
        # and then connect the TextState text to the same state
        # (or just use that state? no, it needs an address outside that complicated expr)
        return

    pass

# == command class

# these imports are not needed in a minimal example like ExampleCommand1:

from graphics.drawing.CS_draw_primitives import drawline
from utilities.constants import red
from geometry.VQT import V
from exprs.instance_helpers import get_glpane_InstanceHolder
from exprs.draggable import DraggablyBoxed

from exprs.instance_helpers import InstanceMacro
from exprs.attr_decl_macros import State
from exprs.TextRect import TextRect

class TextState(InstanceMacro): # rename?
    text = State(str, "initial text", doc = "text")
    _value = TextRect(text) # need size?
    pass

from prototype.test_commands import ExampleCommand1 # NOTE: was ExampleCommand2, this revision UNTESTED [bruce 080910]


##from commands.SelectAtoms.SelectAtoms_Command import SelectAtoms_Command # used indirectly via ExampleCommand1
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode



##class ExampleCommand2E_GM( ExampleCommand1.GraphicsMode_class): #bruce 071014 split out _GM class; works, except highlighting
class ExampleCommand2E_GM(SelectAtoms_GraphicsMode):
    def Draw(self):
        """
        Do some custom drawing (in the model's abs coordsys) after drawing the model.
        """
        #print "start ExampleCommand2E Draw"
        glpane = self.glpane
        super(ExampleCommand2E_GM, self).Draw()
        drawline(red, V(1,0,1), V(1,1,1), width = 2)
        self.command._expr_instance.draw()
        #print "end ExampleCommand2E Draw"
    pass

##class ExampleCommand2E_GM_KLUGED( ExampleCommand1.GraphicsMode_class,
##                            SelectAtoms_Command #### KLUGE, will it work? trying to use it just for its GM aspects...
##                           ): #bruce 071014 split out _GM class
##    # status, 071022: works except for highlighting (tho it looked like it did something on mouseover;
##    #  i forget if this eg had a good HL color change on that resizer), and on drag on that resizer i got
##    #  a region selection rubberband lasso/window. Until now it also had an exception in leftUp then,
##    ## AttributeError: 'ExampleCommand2E_GM_KLUGED' object has no attribute 'ignore_next_leftUp_event'
##    ##  [GLPane.py:1845] [selectAtomsMode.py:494]
##    # but setting this in __init__ works around that (see comment there).
#@ATTENTION:
#UPDATE 2008-08-22: Above comment is obsolete since SelectAtomsMode class has 
#been deprecated . This commented out code needs to be revised if its ever used.
#[-- Ninad comment]
##    
##    command = None # defeat the property in selectAtomsMode #k needed?
##    
##    def __init__(self, command):
##        ExampleCommand1.GraphicsMode_class.__init__(self, command) # includes self.command = command
##        SelectAtoms_Command.__init__(self, self.glpane) ##k??
##        self.ignore_next_leftUp_event = True
##            # kluge, since we didn't run the GM part of SelectAtoms_Command.Enter,
##            # which normally does this.
##        return
##
##    def Draw(self):
##        """
##        Do some custom drawing (in the model's abs coordsys) after drawing the model.
##        """
##        glpane = self.glpane
##        super(ExampleCommand2E_GM_KLUGED, self).Draw()
##        drawline(red, V(1,0,1), V(1,1,1), width = 2)
##        self.command._expr_instance.draw()
##    pass

##KLUGE_USE_SELATOMS_AS_GM = True ####
##
##if KLUGE_USE_SELATOMS_AS_GM:
##    ExampleCommand2E_GM = ExampleCommand2E_GM_KLUGED ##### improve

class ExampleCommand2E( ExampleCommand1, object):
    """
    Add things not needed in a minimal example, to try them out.
    (Uses a PM which is the same as ExampleCommand1 except for title.)
    """
    # Note: object superclass is only needed to permit super(ExampleCommand2E, self) to work.
    # object superclass should not come first, or it overrides __new__
    # (maybe could fix using def __init__ -- not tried, since object coming last works ok)

    commandName = 'ExampleCommand2E-commandName'
    PM_class = ExampleCommand2E_PM
    featurename = "Prototype: ExampleCommand2E"

    GraphicsMode_class = ExampleCommand2E_GM

    def __init__(self, commandSequencer):
        """
        create an expr instance, to draw in addition to the model
        """
        super(ExampleCommand2E, self).__init__(commandSequencer)
        glpane = commandSequencer.assy.glpane
        expr1 = TextState()
        expr2 = DraggablyBoxed(expr1, resizable = True)
            ###BUG: resizing is projecting mouseray in the wrong way, when plane is tilted!
            # I vaguely recall that the Boxed resizable option was only coded for use in 2D widgets,
            # whereas some other constrained drag code is correct for 3D but not yet directly usable in Boxed.
            # So this is just an example interactive expr, not the best way to do resizing in 3D. (Though it could be fixed.)

        # note: this code is similar to _expr_instance_for_imagename in confirmation_corner.py
        ih = get_glpane_InstanceHolder(glpane)
        expr = expr2
        index = (id(self),) # WARNING: needs to be unique, we're sharing this InstanceHolder with everything else in NE1
        self._expr_instance = ih.Instance( expr, index, skip_expr_compare = True)

        return
    
    pass # end of class ExampleCommand2E

# end
