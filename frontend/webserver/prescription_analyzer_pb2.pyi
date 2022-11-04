from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class PatientUsername(_message.Message):
    __slots__ = ["username"]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    username: str
    def __init__(self, username: _Optional[str] = ...) -> None: ...

class PrescribedDrug(_message.Message):
    __slots__ = ["frequency", "name"]
    FREQUENCY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    frequency: str
    name: str
    def __init__(self, name: _Optional[str] = ..., frequency: _Optional[str] = ...) -> None: ...
