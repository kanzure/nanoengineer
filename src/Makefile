UIFILES = $(wildcard *.ui)
MANUAL_EDITED_FILES = ElementSelectorDialog.py
PYFILES0 = $(UIFILES:.ui=.py)

#PYFILES = $(filter-out $(MANUAL_EDITED_FILES), $(PYFILES0))

build : $(PYFILES0) 
$(PYFILES0) : %.py : %.ui
	pyuic $< -o $@ 

clean:
	rm $(PYFILES0)

