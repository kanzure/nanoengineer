
#SUBDIRS = sim
SUBDIRS = cad sim

deb-dist: dist
	tar xzf NanoEngineer-$(PACKAGE_VERSION).tar.gz
	cp -r debian NanoEngineer-$(PACKAGE_VERSION)/
	(cd NanoEngineer-$(PACKAGE_VERSION) && debuild --no-tgz-check -us -uc) \
		|| exit 1
	rm -rf NanoEngineer-$(PACKAGE_VERSION)

