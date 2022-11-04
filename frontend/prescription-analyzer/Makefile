CC=go build
srcDir=./main
SRC=$(shell find $(srcDir) -name "*.go" -a \! -name "*_test.go" )
binDir=./bin

# what proto files are of the microservice interest
src_protos=prescription-analyzer.proto
# --<language>_out protoc flag
language=go
# suffix of the stubs generated, depending on the language
stub_suffix=_pb.go

src_protos_dir=../proto
generatedDir=$(srcDir)
basenames=$(shell basename -a $(src_protos) 2>/dev/null | awk -F . '{print $$1}')
generated=$(addprefix $(generatedDir)/, $(addsuffix $(stub_suffix), $(basenames)))
flags=

$(generated): $(generatedDir)/%$(stub_suffix): $(src_protos_dir)/%.proto
	protoc --go_opt=M$(shell basename -a $< 2>/dev/null)=$(generatedDir)/proto -I=$(src_protos_dir) $(flags) --$(language)_out=. $<

stubs: $(generated)

$(binDir)/debug: $(SRC) $(generated)
	mkdir -p $(binDir)
	$(CC) -v -o $@ $^
