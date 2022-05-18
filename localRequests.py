from pydantic import BaseModel
from fastapi import UploadFile

class RegRequest(BaseModel):
    first_name:  str
    last_name:   str
    email:       str
    password:    str
    service_key: str

class AuthRequest(BaseModel):
    email:       str
    password:    str
    service_key: str

class UnauthRequest(BaseModel):
    token: str

class Item(BaseModel):
    title: str
    description: str
    image: UploadFile

class CartRequest(BaseModel):
    item_id: int
    token: str

class Answer(BaseModel):
    ok: bool
    response: object

class TokenOnly(BaseModel):
    token: str

class OrderRemove(BaseModel):
    token: str
    order_id: int