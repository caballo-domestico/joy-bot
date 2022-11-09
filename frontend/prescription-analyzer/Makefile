# what proto files are of the microservice interest
src_protos=prescription_analyzer.proto
# suffix of the stubs generated, depending on the language
pb_suffix=.pb.go
grpc_suffix=_grpc.pb.go

srcDir=./main
src_protos_dir=../proto
generatedDir=$(srcDir)/rpc
basenames=$(shell basename -a $(src_protos) 2>/dev/null | awk -F . '{print $$1}')
generated_pb=$(addprefix $(generatedDir)/, $(addsuffix $(pb_suffix), $(basenames)))
generated_grpc=$(addprefix $(generatedDir)/, $(addsuffix $(grpc_suffix), $(basenames)))
flags=

$(generated_pb): $(generatedDir)/%$(pb_suffix): $(src_protos_dir)/%.proto
	protoc --go_opt=M$(shell basename -a $< 2>/dev/null)=$(generatedDir) -I=$(src_protos_dir) $(flags) --go_out=. $<

$(generated_grpc): $(generatedDir)/%$(grpc_suffix): $(src_protos_dir)/%.proto
	protoc --go-grpc_out=. --go-grpc_opt=M$(shell basename -a $< 2>/dev/null)=$(generatedDir) -I=$(src_protos_dir) $(flags) $<

stubs: $(generated_pb) $(generated_grpc) $(srcDir)/notifications/notifications$(pb_suffix)

$(srcDir)/notifications/notifications$(pb_suffix): $(src_protos_dir)/notifications.proto
	protoc --go_out=. --go_opt=M$(shell basename -a $< 2>/dev/null)=$(srcDir)/notifications -I=$(src_protos_dir) $(flags) $<