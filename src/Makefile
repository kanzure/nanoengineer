UI_DIR = ../GUI

UIFILES=MainWindowUI.ui rotaryMotorProp.ui LinearMotorProp.ui simsetup.ui elementSelectorForm.ui
PYFILES=MainWindowUI.py RotaryMotorPropDialog.py LinearMotorPropDialog.py simsetup.py elementSelectorForm.py

atom:	$(PYFILES)

MainWindowUI.py: $(UI_DIR)/MainWindowUI.ui
	pyuic $(UI_DIR)/MainWindowUI.ui > MainWindowUI.py

RotaryMotorPropDialog.py: $(UI_DIR)/rotaryMotorProp.ui
	pyuic $(UI_DIR)/rotaryMotorProp.ui > RotaryMotorPropDialog.py

LinearMotorPropDialog.py: $(UI_DIR)/LinearMotorProp.ui
	pyuic $(UI_DIR)/LinearMotorProp.ui > LinearMotorPropDialog.py

simsetup.py: $(UI_DIR)/simsetup.ui
	pyuic $(UI_DIR)/simsetup.ui > simsetup.py

elementSelectorForm.py: $(UI_DIR)/elementSelectorForm.ui
	pyuic $(UI_DIR)/elementSelectorForm.ui > elementSelectorForm.py
