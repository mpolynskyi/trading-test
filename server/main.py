import os

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from uuid import uuid4
import asyncio
import random
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import uvicorn


class OrderStatus:
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELED = "canceled"


app = FastAPI(
    title="Trading Platform API",
    description="Sample RESTful API server that exposes a set of endpoints to simulate a trading platform.",
    version="1"
)

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING")
client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())
db = client.trading
orders_collection = db.orders
orders_collection.create_index([("orderId", 1)], unique=True)


class CreateOrderRequest(BaseModel):
    """Request model for creating an order."""
    stoks: str
    quantity: float = Field(gt=0, description="Quantity must be greater than zero")


websocket_clients = set()


async def broadcast_order_update(order_id: str, order_status: str):
    """Broadcast order status update to all connected WebSocket clients"""
    update = {"orderId": order_id, "orderStatus": order_status}
    for client in websocket_clients.copy():
        try:
            await client.send_json(update)
        except Exception:
            websocket_clients.remove(client)


@app.get("/orders", status_code=200)
async def get_orders() -> list:
    await asyncio.sleep(random.uniform(0.1, 1))
    orders = await orders_collection.find().to_list(length=None)
    return [{"orderId": str(order["orderId"]), "stoks": order['stoks'], "quantity": order['quantity'],
             "orderStatus": order['orderStatus']} for order in orders]


@app.post("/orders", status_code=201)
async def create_order(order: CreateOrderRequest) -> dict:
    await asyncio.sleep(random.uniform(0.1, 1))
    order_id = str(uuid4())
    new_order = {"orderId": order_id, "stoks": order.stoks, "quantity": order.quantity,
                 "orderStatus": OrderStatus.PENDING}
    await orders_collection.insert_one(new_order)
    await broadcast_order_update(order_id, OrderStatus.PENDING)
    asyncio.create_task(process_order(order_id))
    return {"orderId": order_id, "stoks": order.stoks, "quantity": order.quantity, "orderStatus": OrderStatus.PENDING}


@app.get("/orders/{order_id}", status_code=200)
async def get_order(order_id: str) -> dict:
    await asyncio.sleep(random.uniform(0.1, 1))
    order = await orders_collection.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"orderId": order_id, "stoks": order['stoks'], "quantity": order['quantity'],
            "orderStatus": order['orderStatus']}


@app.delete("/orders/{order_id}", status_code=204)
async def cancel_order(order_id: str) -> None:
    await asyncio.sleep(random.uniform(0.1, 1))
    order = await orders_collection.find_one({"orderId": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order["orderStatus"] != OrderStatus.PENDING:
        raise HTTPException(status_code=400,
                            detail=f"Only pending orders can be canceled. Current status: {order['orderStatus']}")
    await orders_collection.update_one({"orderId": order_id}, {"$set": {"orderStatus": OrderStatus.CANCELED}})
    await broadcast_order_update(order_id, OrderStatus.CANCELED)


async def process_order(order_id: str) -> None:
    await asyncio.sleep(random.uniform(0.5, 2))  # Simulate processing time
    order = await orders_collection.find_one({"orderId": order_id})
    if order and order["orderStatus"] == OrderStatus.PENDING:
        await orders_collection.update_one({"orderId": order_id}, {"$set": {"orderStatus": OrderStatus.EXECUTED}})
        await broadcast_order_update(order_id, OrderStatus.EXECUTED)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)
