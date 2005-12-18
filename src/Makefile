
# $Id$

UIFILES = $(wildcard *.ui)
##MANUAL_EDITED_FILES = ElementSelectorDialog.py
PYFILES0 = $(UIFILES:.ui=.py)

##PYFILES = $(filter-out $(MANUAL_EDITED_FILES), $(PYFILES0))

# bruce 051202 added this target
all : 
	echo "Nothing is remade by default -- use one of the explicit make targets."

# bruce 051202 added this target
extensions: 
	python setup.py build_ext --inplace

pyx: extensions

build : $(PYFILES0) 
$(PYFILES0) : %.py : %.ui
	pyuic $< -o $@ 

clean:
	rm -f $(PYFILES0) *.pyc *~

