CC=go build
SRC=$(shell find . -name "*.go")
binDir=./bin

$(binDir)/debug: $(SRC)
	mkdir -p $(binDir)
	$(CC) -v -o $@
