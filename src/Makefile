PYFILES=MainWindowUI.py ElementSelectorDialog.py SimSetupDialog.py GroundPropDialog.py LinearMotorPropDialog.py RotaryMotorPropDialog.py

atom:	$(PYFILES)

MainWindowUI.py: MainWindowUI.ui
	pyuic MainWindowUI.ui > MainWindowUI.py

ElementSelectorDialog.py: ElementSelectorDialog.ui
	pyuic ElementSelectorDialog.ui > ElementSelectorDialog.py

SimSetupDialog.py: SimSetupDialog.ui
	pyuic SimSetupDialog.ui > SimSetupDialog.py

# Jig Property Dialogs

GroundPropDialog.py: GroundPropDialog.ui
	pyuic GroundPropDialog.ui > GroundPropDialog.py

LinearMotorPropDialog.py: LinearMotorPropDialog.ui
	pyuic LinearMotorPropDialog.ui > LinearMotorPropDialog.py

RotaryMotorPropDialog.py: RotaryMotorPropDialog.ui
	pyuic RotaryMotorPropDialog.ui > RotaryMotorPropDialog.py

clean:
	rm $(PYFILES)
