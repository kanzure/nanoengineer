UIFILES = $(wildcard *.ui)
MANUAL_EDITED_FILES = ElementSelectorDialog.py
PYFILES0 = $(UIFILES:.ui=.py)

PYFILES = $(filter-out $(MANUAL_EDITED_FILES), $(PYFILES0))

all : $(PYFILES) 
$(PYFILES) : %.py : %.ui
	pyuic $< -o $@ 


