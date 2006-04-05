# Copyright (c) 2005-2006 Nanorex, Inc.  All rights reserved.
'''
LightingTool.py

$Id$
'''
__author__ = "Mark"

from LightingToolDialog import *

class LightingTool(LightingToolDialog):
    def __init__(self, glpane):
        LightingToolDialog.__init__(self)
        self.glpane = glpane
        if self.setup(): return
        self.exec_loop()

    def setup(self):
        """ Setup sliders and checkboxes. Return true on error (not yet possible).
        """
        self.lights = self.glpane.getLighting()
#        print "Lights = ", self.lights
        
        self.light1CB.setChecked(self.lights[0][2])
        self.ambLight1SL.setValue(int (self.lights[0][0] * 100))
        self.ambLight1LCD.display(self.lights[0][0])
        self.diffuseLight1SL.setValue(int (self.lights[0][1] * 100))
        self.diffuseLight1LCD.display(self.lights[0][1])
        
        self.light2CB.setChecked(self.lights[1][2])
        self.ambLight2SL.setValue(int (self.lights[1][0] * 100))
        self.ambLight2LCD.display(self.lights[1][0])
        self.diffuseLight2SL.setValue(int (self.lights[1][1] * 100))
        self.diffuseLight2LCD.display(self.lights[1][1])
        
        self.light3CB.setChecked(self.lights[2][2])
        self.ambLight3SL.setValue(int (self.lights[2][0] * 100))
        self.ambLight3LCD.display(self.lights[2][0])
        self.diffuseLight3SL.setValue(int (self.lights[2][1] * 100))
        self.diffuseLight3LCD.display(self.lights[2][1])
        
    def valueChangedAmbient1(self, val):
        self.ambLight1LCD.display(val * .01)
        self.setLights()

    def valueChangedDiffuse1(self, val):
        self.diffuseLight1LCD.display(val * .01)
        self.setLights()
        
    def valueChangedAmbient2(self, val):
        self.ambLight2LCD.display(val * .01)
        self.setLights()

    def valueChangedDiffuse2(self, val):
        self.diffuseLight2LCD.display(val * .01)
        self.setLights()

    def valueChangedAmbient3(self, val):
        self.ambLight3LCD.display(val * .01)
        self.setLights()

    def valueChangedDiffuse3(self, val):
        self.diffuseLight3LCD.display(val * .01)
        self.setLights()

    def setLights(self): # [bruce question: is this also called directly when checkboxes are changed?]
        
        light1 = [self.ambLight1SL.value() * .01, \
                self.diffuseLight1SL.value() * .01, \
                self.light1CB.isChecked()]
        light2 = [self.ambLight2SL.value() * .01, \
                self.diffuseLight2SL.value() * .01, \
                self.light2CB.isChecked()]
        light3 = [self.ambLight3SL.value() * .01, \
                self.diffuseLight3SL.value() * .01,
                self.light3CB.isChecked()]
                
        self.glpane.setLighting([light1, light2, light3])

    def restore(self): # bruce 050311 addition, not yet tested or used ###@@@
        "implement a button for Use Defaults or Restore Default Values, if one is added to the UI"
        self.glpane.restoreDefaultLighting() # set default lighting in glpane
        save_lights = self.lights # save original lights, in case of Cancel after this restore
        self.setup() # set sliders to the restored values; also does unwanted set of self.lights
        self.lights = save_lights # fix that unwanted set
        return
    
    #################
    # Save Button
    #################
    def accept(self):
        self.glpane.saveLighting() # save current lighting to preferences database
        QDialog.accept(self)
        
    #################
    # Cancel Button
    #################
    def reject(self):
        self.glpane.setLighting(self.lights) # restore lighting from when dialog was entered
        QDialog.reject(self)
