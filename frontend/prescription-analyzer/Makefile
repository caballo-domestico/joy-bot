CC=go build
srcDir=./main
SRC=$(shell find $(srcDir) -name "*.go" -a \! -name "*_test.go" )
binDir=./bin

# what proto files are of the microservice interest
src_protos=prescription-analyzer.proto
# suffix of the stubs generated, depending on the language
pb_suffix=_pb.go
grpc_suffix=_pb_grpc.go

src_protos_dir=../proto
generatedDir=$(srcDir)
basenames=$(shell basename -a $(src_protos) 2>/dev/null | awk -F . '{print $$1}')
generated_pb=$(addprefix $(generatedDir)/, $(addsuffix $(pb_suffix), $(basenames)))
generated_grpc=$(addprefix $(generatedDir)/, $(addsuffix $(grpc_suffix), $(basenames)))
flags=

$(generated_pb): $(generatedDir)/%$(pb_suffix): $(src_protos_dir)/%.proto
	protoc --go_opt=M$(shell basename -a $< 2>/dev/null)=$(generatedDir)/proto -I=$(src_protos_dir) $(flags) --go_out=. $<

$(generated_grpc): $(generatedDir)/%$(grpc_suffix): $(src_protos_dir)/%.proto
	protoc --go-grpc_out=. --go-grpc_opt=M$(shell basename -a $< 2>/dev/null)=$(generatedDir)/proto -I=$(src_protos_dir) $(flags) $<

stubs: $(generated_pb) $(generated_grpc)

$(binDir)/debug: $(SRC) $(generated)
	mkdir -p $(binDir)
	$(CC) -v -o $@ $^
