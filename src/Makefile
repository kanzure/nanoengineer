
# $Id$

CFLAGS=-g -Wall -I/usr/include/python2.4

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

pyclean:
	rm -f $(PYFILES0) *.pyc *~

clean:
	rm -f *.pyc *~ *.o *.so atombase.c

abt: atombase.so atombasetests.py
	python atombasetests.py

atombase.c: atombasehelp.c atombase.pyx
	pyrexc atombase.pyx

atombase.so: atombase.o
	gcc -shared -o atombase.so atombase.o $(LDFLAGS)
