# folder names containing microservices makefiles
microservices=webserver manageusers prescription-analyzer 

stubs: $(microservices)

$(microservices):
	$(MAKE) -C $@ stubs

.PHONY: stubs $(microservices)