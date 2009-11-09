
EXTRA_DIST = keyboardshortcuts.htm mousecontrols.htm

install-exec-hook:
	@echo Copying the UI documentation files...
	mkdir -p $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/doc
	cp keyboardshortcuts.htm $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/doc/
	cp mousecontrols.htm $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/doc/

