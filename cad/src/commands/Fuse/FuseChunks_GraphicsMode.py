# Copyright 2004-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
FuseChunks_GraphicsMode.py

@author: Mark
@version: $Id$
@copyright: 2004-2008 Nanorex, Inc.  See LICENSE file for details.

History:
Originally by Mark as class 'fuseChunksMode'.
Ninad 2008-01-25: Split Command and GraphicsMode classes
                  out of class fuseChunksMode. The command class can be 
                  found in FuseChunks_Command.py
"""
from graphics.drawing.CS_draw_primitives import drawline
from graphics.behaviors.shape import get_selCurve_color

from utilities.constants import green
from utilities.constants import magenta
from utilities.constants import blue
from utilities.constants import darkred

from commands.Move.Move_GraphicsMode import Move_GraphicsMode
from commands.Translate.TranslateChunks_GraphicsMode import TranslateChunks_GraphicsMode
from commands.Rotate.RotateChunks_GraphicsMode import RotateChunks_GraphicsMode

class _FuseChunks_GraphicsMode_preMixin:
    # REVIEW: this should probably inherit from Move_GraphicsMode,
    # since it often calls its methods as if they were superclass methods.
    # [bruce comment 080722]
    """
    The pre- Mixin class for various graphics modes that will be used for the
    FuseChunks_Command. This should strictly be a pre-Mixin class. 
    The intention is to override some methods of Move_GraphicsMode , 
    such as 'Draw' and use them in the graphics modes of FuseChunks_Command. 
    
    The Move_GraphicsMode also has two subclasses TranslateChunks_GraphicsMode
    and RotateChunks_GraphicsMode. Even in FuseChunks mode (command), we 
    need to use these two modes , at the same time we also need to override
    the Draw methods etc so that the 3D workspce shows things like fusable atoms 
    and bonds. To achieve this, we have made this special Mixin class to define
    Draw methods etc. Then, the class FuseChunks_GraphicsMode inherits this 
    first and then the Move_GraphicsMode. (so that, for example 
    self.Draw in that class  actually uses the method defined in this mixin 
    class instead of Move_GraphicsMode.Draw.) 
    
    We are doing similar thing in classes such as --
    Translate_in_FuseChunks_GraphicsMode where the it uses Draw related methods 
    from this class and special drag related methods form 
    TranslateChunks_GraphicsMode
    
    @see: B{TranslateChunks_GraphicsMode} 
    @see: B{Translate_in_FuseChunks_GraphicsMode} 
    @see: B{RotateChunks_GraphicsMode}
    @see: B{Rotate_in_FuseChunks_GraphicsMode} 
    @see: Move_GraphicsMode
    @see: FuseChunks_Command
    """
    recompute_fusables = True
        # 'recompute_fusables' is used to optimize redraws by skipping the 
        # recomputing of fusables
        # (bondable pairs or overlapping atoms). When set to False, Draw() will
        # not recompute fusables 
        # before repainting the GLPane. When False, 'recompute_fusables' is 
        # reset to True in Draw(), 
        # so it is the responsibility of the caller to Draw() (i.e. win_update()
        # or gl_update()) to reset it to False before each redraw if desired.
        #For more info, see comments in Draw().
    
    something_was_picked = False
        # 'something_was_picked' is a special boolean flag needed by Draw() 
        # to determine when 
        # the state has changed from something selected to nothing selected.  
        # It is used to 
        # properly update the tolerance label in the Property Manager
        # when all chunks are unselected.
    
    def Enter_GraphicsMode(self):
        Move_GraphicsMode.Enter_GraphicsMode(self)
        self.recompute_fusables = True	
        return
    
    def Draw(self):
        """
        Draw bondable pairs or overlapping atoms.
        """
        if self.o.is_animating or self.o.button == 'MMB':
            # Don't need to recompute fusables if we are animating between views 
            # or zooming, panning or rotating with the MMB.
            self.recompute_fusables = False

        # 'recompute_fusables' is set to False when the bondable pairs or 
        # overlapping atoms don't need to be recomputed.
        # Scenerios when 'recompute_fusables' is set to False:
        #   1. animating between views. Done above, boolean attr 
        #      'self.o.is_animating' is checked.
        #   2. zooming, panning and rotating with MMB. Done above, 
        #      check if self.o.button == 'MMB'
        #   3. Zooming with mouse wheel, done in self.Wheel().
        # If 'recompute_fusables' is False here, it is immediately reset to 
        # True below. mark 060405
        if self.recompute_fusables:
            # This is important and needed in case there is nothing selected.  
            # I mention this because it looks redundant since is the first thing
            # done in find_bondable_pairs(). 
            self.command.bondable_pairs = []
            self.command.ways_of_bonding = {}
            self.command.overlapping_atoms = []

            if self.o.assy.selmols: 
                # Recompute fusables. This can be very expensive, especially 
                # with large parts.
                self.command.find_fusables() 
                if not self.something_was_picked: 
                    self.something_was_picked = True
            else:
                # Nothing is selected, so there can be no fusables.
                # Check if we need to update the slider tolerance label.
                # This fixed bug 502-14.  Mark 050407
                if self.something_was_picked:
                    self.command.reset_tolerance_label()
                    self.something_was_picked = False # Reset flag
        else:
            self.recompute_fusables = True

        Move_GraphicsMode.Draw(self)

        if self.command.bondable_pairs:
            self.draw_bondable_pairs()

        elif self.command.overlapping_atoms:
            self.draw_overlapping_atoms()

        return
    
    def draw_bondable_pairs(self):
        """
        Draws bondable pairs of singlets and the bond lines between them. 
        Singlets in the selected chunk(s) are colored green.
        Singlets in the unselected chunk(s) are colored blue.
        Singlets with more than one way to bond are colored magenta.
        """
        # Color of bond lines --
        bondline_color = get_selCurve_color(0,self.o.backgroundColor) 
        for s1,s2 in self.command.bondable_pairs:
            color = (self.command.ways_of_bonding[s1.key] > 1) and magenta or green
            s1.overdraw_with_special_color(color)
            color = (self.command.ways_of_bonding[s2.key] > 1) and magenta or blue
            s2.overdraw_with_special_color(color)
            # Draw bond lines between singlets --
            drawline(bondline_color, s1.posn(), s2.posn()) 
    

    def draw_overlapping_atoms(self):
        """
        Draws overlapping atoms. 
        Atoms in the selected chunk(s) are colored green.
        Atoms in the unselected chunk(s) that will be deleted are colored 
        darkred.
        """
        for a1,a2 in self.command.overlapping_atoms:
            # a1 atoms are the selected chunk atoms
            a1.overdraw_with_special_color(green) # NFR/bug 945. Mark 051029.
            # a2 atoms are the unselected chunk(s) atoms
            a2.overdraw_with_special_color(darkred)
    
    def leftDouble(self, event):
        # This keeps us from leaving Fuse Chunks mode, 
        #as is the case in Move Chunks mode.
        pass

    def Wheel(self, event):
        """
        Mouse wheel event handler.  This overrides Move_GraphicsMode.Wheel() to 
        optimize redraws by setting 'recompute_fusables' to False so that Draw()
        will not recompute fusables while zooming in/out.
        """
        Move_GraphicsMode.Wheel(self, event)
        self.recompute_fusables = False

    pass # end of class _FuseChunks_GraphicsMode_preMixin

           
class FuseChunks_GraphicsMode(_FuseChunks_GraphicsMode_preMixin, 
                              Move_GraphicsMode):
    """
    The default Graphics mode for the FuseChunks_Command
    @see: _FuseChunks_GraphicsMode_preMixin for comments on multiple inheritance
    @see: B{FuseChunks_Command} where it is used as a default graphics mode 
         class
    @see: B{FuseChunks_Command._createGraphicsMode} 
    """    
    pass

class Translate_in_FuseChunks_GraphicsMode(_FuseChunks_GraphicsMode_preMixin,
                                           TranslateChunks_GraphicsMode):
    """
    When the translate groupbox of the FuseChunks Command  property manager is 
    active, the graphics mode for the command will be 
    Translate_in_FuseChunks_GraphicsMode. 
    @see: _FuseChunks_GraphicsMode_preMixin for comments on multiple inheritance
    @see: B{FuseChunks_Command._createGraphicsMode} 
    """
    pass

class Rotate_in_FuseChunks_GraphicsMode(_FuseChunks_GraphicsMode_preMixin,
                                        RotateChunks_GraphicsMode):
    """
    When the translate groupbox of the FuseChunks Command  property manager is 
    active, the graphics mode for the command will be 
    Rotate_in_FuseChunks_GraphicsMode. 
    @see: _FuseChunks_GraphicsMode_preMixin for comments on multiple inheritance
    @see: B{FuseChunks_Command._createGraphicsMode} 
    """
    pass

# end
