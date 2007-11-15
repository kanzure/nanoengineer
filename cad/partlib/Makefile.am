
install-exec-hook:
	@echo Installing partlib...
	mkdir -p $(pkgdatadir)-$(PACKAGE_VERSION)/partlib
	cp -R * $(pkgdatadir)-$(PACKAGE_VERSION)/partlib/
	ln -s $(pkgdatadir)-$(PACKAGE_VERSION)/partlib $(bindir)/NanoEngineer-$(PACKAGE_VERSION).app/partlib

dist-hook:
	cp -R * $(distdir)/
	rm $(distdir)/Makefile
	rm -rf $(distdir)/.svn
	rm -rf $(distdir)/*/.svn
	rm -rf $(distdir)/*/*/.svn

