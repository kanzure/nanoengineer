PYFILES=MainWindowUI.py ElementSelectorUI.py SimulatorUI.py GroundPropUI.py LinearMotorPropUI.py RotaryMotorPropUI.py

atom:	$(PYFILES)

MainWindowUI.py: MainWindowUI.ui
	pyuic MainWindowUI.ui > MainWindowUI.py

ElementSelectorUI.py: ElementSelectorUI.ui
	pyuic ElementSelectorUI.ui > ElementSelectorUI.py

SimulatorUI.py: SimulatorUI.ui
	pyuic SimulatorUI.ui > SimulatorUI.py

# Jig Property Dialogs

GroundPropUI.py: GroundPropUI.ui
	pyuic GroundPropUI.ui > GroundPropUI.py

LinearMotorPropUI.py: LinearMotorPropUI.ui
	pyuic LinearMotorPropUI.ui > LinearMotorPropUI.py

RotaryMotorPropUI.py: RotaryMotorPropUI.ui
	pyuic RotaryMotorPropUI.ui > RotaryMotorPropUI.py

clean:
	rm $(PYFILES)
