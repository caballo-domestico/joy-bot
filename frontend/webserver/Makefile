# what proto files are of the microservice interest
src_protos=prescription_analyzer.proto users.proto
# suffices of the stubs generated, depending on the language
pb_suffix=_pb2.py
grpc_suffix=_pb2_grpc.py
pyi_suffix=_pb2.pyi

src_protos_dir=../proto
generatedDir=.
basenames=$(shell basename -a $(src_protos) 2>/dev/null | awk -F . '{print $$1}')
generated_pb=$(addprefix $(generatedDir)/, $(addsuffix $(pb_suffix), $(basenames)))
generated_grpc=$(addprefix $(generatedDir)/, $(addsuffix $(grpc_suffix), $(basenames)))
generated_pyi=$(addprefix $(generatedDir)/, $(addsuffix $(pyi_suffix), $(basenames)))

$(generated_pb): $(generatedDir)/%$(pb_suffix): $(src_protos_dir)/%.proto 
	protoc -I=$(src_protos_dir) --python_out=$(generatedDir) $<

$(generated_grpc): $(generatedDir)/%$(grpc_suffix): $(src_protos_dir)/%.proto 
	python -m grpc_tools.protoc -I=$(src_protos_dir) --pyi_out=$(generatedDir) --grpc_python_out=$(generatedDir) $<

$(generated_pyi): $(generatedDir)/%$(pyi_suffix): $(src_protos_dir)/%.proto
	python -m grpc_tools.protoc -I=$(src_protos_dir) --pyi_out=$(generatedDir) --grpc_python_out=$(generatedDir) $<

stubs: $(generated_pb) $(generated_grpc) $(generated_pyi)