
install-exec-hook:
	@echo Installing DNA Generator plugin...
	mkdir -p $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/plugins/DNA
	cp -R * $(DESTDIR)/$(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/plugins/DNA/

dist-hook:
	cp -R * $(distdir)/
	rm $(distdir)/Makefile
	rm -rf `find $(distdir) -name .svn`

