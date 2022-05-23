from typing import List, Union
import hashlib
from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import localRequests as lr
from db_connectors import LocalDB

app = FastAPI()
db = LocalDB("local_database.db")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/service", response_model=lr.Answer)
async def serviceKey(api_id:str):
    return db.GetServiceKey(api_id)

# DONE
@app.post("/reg", response_model=lr.Answer)
async def registration(req:lr.RegRequest):
    service = db.CheckServiceKey(req.service_key)
    if not service["ok"]: return service

    return db.CreateUser(
        req.first_name, 
        req.last_name, 
        req.email, 
        hashlib.sha256(bytearray(req.password, "utf8")).hexdigest()
    )

# DONE
@app.post("/auth", response_model=lr.Answer)
async def auth(req:lr.AuthRequest):
    service = db.CheckServiceKey(req.service_key)
    if not service["ok"]: return service

    userID = db.CheckAuth(
        req.email,
        hashlib.sha256(bytearray(req.password, "utf8")).hexdigest()
    )

    if userID != -1:
        return db.CreateSession(userID)
    else:
        return db.answer(False, "Something get wrong")

# DONE
@app.post("/unauth", response_model=lr.Answer)
async def unauth(req:lr.UnauthRequest):
    return db.RemoveSession(req.token)

@app.get("/user", response_model=lr.Answer)
async def getUser(token:str):
    service, userId = db.CheckSession(token)
    if not service["ok"]: return service

    return db.GetUser(userId)

# DONE
@app.get("/news", response_model=lr.Answer)
async def news(token:str, count:int=5, order_by:str="date", sort_by:bool=True):
    service, _ = db.CheckSession(token)
    if not service["ok"]: return service

    return db.GetNews(count, order_by, sort_by)

# DONE
@app.get("/news/fields", response_model=lr.Answer)
async def newsFields(token:str):
    service, _ = db.CheckSession(token)
    if not service["ok"]: return service

    return db.GetTableHeaders("news")

# DONE
@app.get("/item", response_model=lr.Answer)
async def item(token:str, item_ids:str):
    service, _ = db.CheckSession(token)
    if not service["ok"]: return service

    item_ids = item_ids.replace(" ", "")
    itemIds = []
    for item_id in item_ids.split(","):
        if item_id.isdigit():
            itemIds.append(item_id)
        else:
            return db.answer(False, "Invalid item_ids")

    return db.GetItem(itemIds)

# DONE
@app.get("/items", response_model=lr.Answer)
async def items(token:str, count:int=3, scope:int=0):
    service, _ = db.CheckSession(token)
    if not service["ok"]: return service

    return db.GetItems(count, scope)

# DONE
@app.get("/cart", response_model=lr.Answer)
async def getCart(token:str):
    service, userId = db.CheckSession(token)
    if not service["ok"]: return service

    return db.GetCart(userId)

# DONE
@app.post("/cart/add", response_model=lr.Answer)
async def addToCart(req: lr.CartRequest):
    service, userId = db.CheckSession(req.token)
    if not service["ok"]: return service

    return db.AddToCart(userId, req.item_id)

# DONE
@app.delete("/cart", response_model=lr.Answer)
async def deleteFromCart(req: lr.CartRequest):
    service, userId = db.CheckSession(req.token)
    if not service["ok"]: return service

    return db.RemoveFromCart(userId, req.item_id)

# DONE
@app.post("/order/accept", response_model=lr.Answer)
async def acceptOrder(req:lr.TokenOnly):
    service, userId = db.CheckSession(req.token)
    if not service["ok"]: return service

    return db.MoveOrder(userId)

# DONE
@app.get("/orders", response_model=lr.Answer)
async def getOrders(token:str):
    service, userId = db.CheckSession(token)
    if not service["ok"]: return service

    return db.GetOrders(userId)

@app.delete("/order", response_model=lr.Answer)
async def getOrders(req:lr.OrderRemove):
    service, _ = db.CheckSession(req.token)
    if not service["ok"]: return service

    return db.RemoveOrder(req.order_id)