UIFILES=MainWindowUI.ui rotaryMotorProp.ui simsetup.ui elementSelectorForm.ui LinearMotorProp.ui
PYFILES=MainWindowUI.py RotaryMotorPropDialog.py simsetup.py elementSelectorForm.py LinearMotorPropDialog.py

atom:	$(PYFILES)

MainWindowUI.py: MainWindowUI.ui
	pyuic MainWindowUI.ui > MainWindowUI.py

rotaryMotorPropDialog.py: rotaryMotorProp.ui
	pyuic rotaryMotorProp.ui > RotaryMotorPropDialog.py

simsetup.py: simsetup.ui
	pyuic simsetup.ui > simsetup.py

elementSelectorForm.py: elementSelectorForm.ui
	pyuic elementSelectorForm.ui > elementSelectorForm.py

LinearMotorPropDialog.py: LinearMotorProp.ui
	pyuic LinearMotorProp.ui > LinearMotorPropDialog.py