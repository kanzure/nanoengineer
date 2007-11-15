
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
	mkdir -p $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program

if RUN_FREEZEPYTHON
	@echo Installing the frozen NanoEngineer-1...
	cp -r dist/* $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/
	echo '#!/bin/sh' > $(bindir)/NanoEngineer-$(PACKAGE_VERSION)
	echo $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/NanoEngineer-1 >> $(bindir)/NanoEngineer-$(PACKAGE_VERSION)
else
	@echo Installing byte-compiled NanoEngineer-1...
	cp *.pyc $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/
	mkdir -p $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/exprs
	cp exprs/*.pyc $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/exprs/
	mkdir -p $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/PM
	cp PM/*.pyc $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/PM/
	echo '#!/bin/sh' > $(bindir)/NanoEngineer-$(PACKAGE_VERSION)
	echo python $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/program/main.pyc >> $(bindir)/NanoEngineer-$(PACKAGE_VERSION)
endif
	chmod 755 $(bindir)/NanoEngineer-$(PACKAGE_VERSION)
	pushd $(bindir) && rm -f NanoEngineer-1
	pushd $(bindir) && ln -s NanoEngineer-$(PACKAGE_VERSION) NanoEngineer-1
#	rm -f $(bindir)/NanoEngineer-1
#	ln -s $(bindir)/NanoEngineer-$(PACKAGE_VERSION) $(bindir)/NanoEngineer-1

	@echo Copying the GAMESS helper script...
	mkdir -p $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/bin
	cp rungms $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/bin/

	@echo Copying images...
	mkdir -p $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/src
	cp -R ui $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/src/

	@echo Copying ReadMe.html...
	mkdir -p $(pkgdatadir)-$(PACKAGE_VERSION)
	cp ReadMe.html $(pkgdatadir)-$(PACKAGE_VERSION)/

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

