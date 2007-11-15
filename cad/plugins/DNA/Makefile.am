
install-exec-hook:
	@echo Installing DNA Generator plugin...
	mkdir -p $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/plugins/DNA
	cp -R * $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/plugins/DNA/

dist-hook:
	cp -R * $(distdir)/
	rm $(distdir)/Makefile
	rm -rf `find $(distdir) -name .svn`

