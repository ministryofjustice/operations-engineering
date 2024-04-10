TOPTARGETS := all clean build 

SUBDIRS := $(wildcard lambdas/*/.)
BASE = $(shell /bin/pwd)

$(TOPTARGETS): $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@ $(MAKECMDGOALS) $(ARGS) BASE="${BASE}"

.PHONY: $(TOPTARGETS) $(SUBDIRS)