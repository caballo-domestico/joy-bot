from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Message(_message.Message):
    __slots__ = ["confirmed", "email", "password", "phone_num", "user_type"]
    CONFIRMED_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PHONE_NUM_FIELD_NUMBER: _ClassVar[int]
    USER_TYPE_FIELD_NUMBER: _ClassVar[int]
    confirmed: bool
    email: str
    password: str
    phone_num: str
    user_type: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ..., user_type: _Optional[str] = ..., phone_num: _Optional[str] = ..., confirmed: bool = ...) -> None: ...

class MessageResponse(_message.Message):
    __slots__ = ["received"]
    RECEIVED_FIELD_NUMBER: _ClassVar[int]
    received: bool
    def __init__(self, received: bool = ...) -> None: ...
