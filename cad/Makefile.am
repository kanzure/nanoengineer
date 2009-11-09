
SUBDIRS = src doc partlib plugins

install-exec-hook:
	@echo Installing license files...
#	cp -R Licenses $(pkgdatadir)-$(PACKAGE_VERSION)/

dist-hook:
	mkdir $(distdir)/Licenses
	cp src/LICENSE $(distdir)/Licenses/
	cp licenses-common/NanoKids_Attribution $(distdir)/Licenses/

