# syntax=docker/dockerfile:1

FROM python:3.11.0rc2-alpine
WORKDIR /manageusers
# pre-copy requirements.txt to cache dependencies and speed up builds
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "app.py", "--grpc_addr_port=signin:50051", "--cbreaker_open_after=1", "--cbreaker_reset_timeout=30"]