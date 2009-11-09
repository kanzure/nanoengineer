
all:
if RUN_FREEZEPYTHON
	@echo Freezing NanoEngineer-1...
		$(FREEZEPYTHON) --install-dir dist --target-name=NanoEngineer-1 \
			--include-modules sip,dbhash main.py
else
	@echo Byte-compiling NanoEngineer-1...
	python -c "import compileall; compileall.compile_dir('.')"

endif

install-exec-hook:
	mkdir -p $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program

if RUN_FREEZEPYTHON
	@echo Installing the frozen NanoEngineer-1...
	cp -r dist/* $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/
	echo '#!/bin/sh' > $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION)
	echo $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/NanoEngineer-1 >> $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION)
else
	@echo Installing byte-compiled NanoEngineer-1...
	cp *.pyc $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/
	cp -r analysis $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r cnt $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r commandSequencer $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r commandToolbar $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r command_support $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r commands $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r dna $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r exprs $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r files $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r foundation $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r geometry $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r graphics $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r history $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r model $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r modelTree $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r model_updater $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r ne1_startup $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r ne1_ui $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r operations $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r outtakes $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r platform_dependent $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r PM $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r processes $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r protein $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r prototype $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r scratch $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r simulation $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r sponsors $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r temporary_commands $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r tests $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r tools $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r utilities $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	cp -r widgets $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program
	echo '#!/bin/sh' > $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION)
	echo PYTHONPATH=$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program python $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/main.pyc >> $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION)
endif
	chmod 755 $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION)
	pushd $(DESTDIR)/$(bindir) && rm -f NanoEngineer-1
	pushd $(DESTDIR)/$(bindir) && ln -s NanoEngineer-$(PACKAGE_VERSION) NanoEngineer-1
#	rm -f $(DESTDIR)/$(bindir)/NanoEngineer-1
#	ln -s $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION) $(DESTDIR)/$(bindir)/NanoEngineer-1

	@echo Copying the GAMESS helper script...
#	mkdir -p $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/bin
#	cp rungms $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/bin/

	@echo Copying images...
	mkdir -p $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/src
	cp -R ui $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/src/

	@echo Copying ReadMe.html...
	mkdir -p $(DESTDIR)/$(pkgdatadir)-$(PACKAGE_VERSION)
	cp ReadMe.html $(DESTDIR)/$(pkgdatadir)-$(PACKAGE_VERSION)/

EXTRA_DIST = ReadMe.html rungms

dist-hook:
	cp -R *.py $(distdir)/
	cp -R exprs $(distdir)/
	cp -R PM $(distdir)/
	mkdir -p $(distdir)/ui/actions
	cp -R ui/actions/Edit $(distdir)/ui/actions/
	cp -R ui/actions/File $(distdir)/ui/actions/
	cp -R ui/actions/Help $(distdir)/ui/actions/
	cp -R ui/actions/Insert $(distdir)/ui/actions/
	cp -R ui/actions/Properties\ Manager $(distdir)/ui/actions/
	cp -R ui/actions/Simulation $(distdir)/ui/actions/
	cp -R ui/actions/Toolbars $(distdir)/ui/actions/
	cp -R ui/actions/Tools $(distdir)/ui/actions/
	cp -R ui/actions/View $(distdir)/ui/actions/
	cp -R ui/border $(distdir)/ui/
	cp -R ui/confcorner $(distdir)/ui/
	cp -R ui/cursors $(distdir)/ui/
	cp -R ui/dialogs $(distdir)/ui/
	cp -R ui/exprs $(distdir)/ui/
	cp -R ui/images $(distdir)/ui/
	cp -R ui/modeltree $(distdir)/ui/
	rm -rf `find $(distdir) -name .svn`
	rm -rf $(distdir)/*/.svn
	rm -rf $(distdir)/*/*/.svn
	rm -rf $(distdir)/*/*/*/.svn
	rm -rf $(distdir)/*/*/*/*/.svn

