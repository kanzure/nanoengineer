UIFILES=MainWindowUI.ui rotaryMotorProp.ui simsetup.ui
PYFILES=MainWindowUI.py rotaryMotorProp.py simsetup.py

atom:	$(PYFILES)

MainWindowUI.py: MainWindowUI.ui
	pyuic MainWindowUI.ui > MainWindowUI.py

rotaryMotorProp.py: rotaryMotorProp.ui
	pyuic rotaryMotorProp.ui > rotaryMotorProp.py

simsetup.py: simsetup.ui
	pyuic simsetup.ui > simsetup.py
