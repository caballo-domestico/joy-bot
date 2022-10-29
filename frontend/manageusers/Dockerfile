# syntax=docker/dockerfile:1

FROM python:3.11.0rc2-alpine
WORKDIR /manageusers
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD [ "python3", "app.py"]