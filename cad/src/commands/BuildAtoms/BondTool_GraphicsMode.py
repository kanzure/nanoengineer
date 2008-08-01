from commands.BuildAtoms.BuildAtoms_GraphicsMode import BuildAtoms_GraphicsMode
##from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode
from model.bond_constants import V_SINGLE
from utilities.prefs_constants import buildModeHighlightingEnabled_prefs_key
import foundation.env as env

_superclass =  BuildAtoms_GraphicsMode
class BondTool_GraphicsMode(BuildAtoms_GraphicsMode):   
    """
    """    
    def Enter_GraphicsMode(self):
        _superclass.Enter_GraphicsMode(self)
        self.setBond(self.command.getBondType(), True)
        
    def bondLeftUp(self, b, event): 
        # was bondClicked(). mark 060220. 
        #[WARNING: docstring appears to be out of date -- bruce 060702]
        """
        Bond <b> was clicked, so select or unselect its atoms or delete bond <b> 
        based on the current modkey.
        - If no modkey is pressed, clear the selection and pick <b>\'s two atoms.
        - If Shift is pressed, pick <b>\'s two atoms, adding them to the 
          current selection.
        - If Ctrl is pressed,  unpick <b>\'s two atoms, removing them from the 
          current selection.
        - If Shift+Control (Delete) is pressed, delete bond <b>.
        <event> is a LMB release event.
        """
        
        if self.o.modkeys is None:
            self.bond_change_type(b, allow_remake_bondpoints = True)
            self.o.gl_update()
            return
            
        _superclass.bondLeftUp(self, b, event)

        if self.o.modkeys is None:           
            if self.command.isBondsToolActive():                        
            #Following fixes bug 2425 (implements single click bond deletion 
            #in Build Atoms. -- ninad 20070626
                if self.command.isDeleteBondsToolActive():
                    self.bondDelete(event)
                    #@ self.o.gl_update() # Not necessary since win_update()
                                          # is called in bondDelete(). 
                                          # Mark 2007-10-19
                    return                
                self.bond_change_type(b, allow_remake_bondpoints = True)
                self.o.gl_update()
                return        
        _superclass.bondLeftUp(self, b, event)
                
    ##def _get_hover_highlighting_enabled(self):
        ##print "### in _get_hover_highlighting_enabled"
        ##parent_command = self.commandSequencer.prevMode
        ##if parent_command:
            ##print "***parent_command = ", parent_command
            ##return parent_command.graphicsMode._get_hover_highlighting_enabled
        ###fallback --         
        ##return self.command.hover_highlighting_enabled

    ##def _set_hover_highlighting_enabled(self, val):
        ##print "### in _set_hover_highlighting_enabled"
        ##parent_command = self.commandSequencer.prevMode
        ##if parent_command:
            ##print "***parent_command = ", parent_command
            ##parent_command.graphicsMode._set_hover_highlighting_enabled(val)
            ##return
        ###fallback -- 
        ##self.command.hover_highlighting_enabled = val
        
    ##def _get_hover_highlighting_enabled(self):
        
        ##return env.prefs[buildModeHighlightingEnabled_prefs_key]

    ##def _set_hover_highlighting_enabled(self, val):        
        ##self.command.hover_highlighting_enabled = val
        
    ##hover_highlighting_enabled = property(_get_hover_highlighting_enabled, 
                                          ##_set_hover_highlighting_enabled)    
    pass


class DeleteBondTool_GraphicsMode(BuildAtoms_GraphicsMode):    
    
                
    def bondLeftUp(self, b, event):
        if self.o.modkeys is None:
            self.bondDelete(event)
            #@ self.o.gl_update() # Not necessary since win_update()
            # is called in bondDelete(). 
            # Mark 2007-10-19
            return                
                    
        _superclass.bondLeftUp(self, b, event)