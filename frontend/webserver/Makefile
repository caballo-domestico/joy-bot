# what proto files are of the microservice interest
src_protos=prescription-analyzer.proto users.proto
# --<language>_out protoc flag
language=python
# suffix of the stubs generated, depending on the language
stub_suffix=_pb2.py

src_protos_dir=../proto
generatedDir=.
basenames=$(shell basename -a $(src_protos) 2>/dev/null | awk -F . '{print $$1}')
generated=$(addprefix $(generatedDir)/, $(addsuffix $(stub_suffix), $(basenames)))
flags=

$(generated): $(generatedDir)/%$(stub_suffix): $(src_protos_dir)/%.proto 
	protoc -I=$(src_protos_dir) $(flags) --$(language)_out=$(generatedDir) $<

stubs: $(generated)