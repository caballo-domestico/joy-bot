CC=go build
SRC=$(shell find ./main -name "*.go" -a \! -name "*_test.go" )
binDir=./bin

$(binDir)/debug: $(SRC)
	mkdir -p $(binDir)
	$(CC) -v -o $@ $^
