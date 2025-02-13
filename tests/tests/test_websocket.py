import asyncio
import pytest
import time
import websockets
from helpers.api_helpers import create_order, cancel_order
from statistics import mean, stdev
import json
import logging

LOGGER = logging.getLogger(__name__)


@pytest.mark.websockets
@pytest.mark.asyncio
async def test_websocket_order_updates(api_client, order_status, ws_url):
    """
    1. Start listening to WebSocket.
    2. Create a new order.
    3. Validate real-time WebSocket messages.
    4. Ensure correct message order: PENDING -> EXECUTED.
    """
    async with websockets.connect(ws_url) as websocket:
        order_response = create_order(api_client, stoks="EURUSD", quantity=100.5)
        assert order_response.status_code == 201
        order_id = order_response.json()["orderId"]

        # First message: Order created with status PENDING
        pending_message = json.loads(await websocket.recv())
        assert pending_message["orderId"] == order_id
        assert pending_message["orderStatus"] == order_status.PENDING

        # Second message: Order executed
        executed_message = json.loads(await websocket.recv())
        assert executed_message["orderId"] == order_id
        assert executed_message["orderStatus"] == order_status.EXECUTED


@pytest.mark.websockets
@pytest.mark.asyncio
async def test_websocket_order_cancel(pending_order_data_fixture, api_client, order_status, ws_url):
    """
    1. Create fixture order
    2. Immediately cancel order.
    3. Validate real-time WebSocket message about cancel order.
    """
    async with websockets.connect(ws_url) as websocket:
        cancel_order_response = cancel_order(api_client, pending_order_data_fixture['orderId'])
        assert cancel_order_response.status_code == 204
        cancel_message = json.loads(await websocket.recv())
        assert cancel_message["orderId"] == pending_order_data_fixture['orderId']
        assert cancel_message["orderStatus"] == order_status.CANCELED


@pytest.mark.asyncio
@pytest.mark.websockets
@pytest.mark.websockets_performance
async def test_websocket_performance(api_client, ws_url, order_status):
    """
    Performance test:
    1. Place 100 orders simultaneously.
    2. Validate WebSocket messages.
    3. Calculate average execution delay & standard deviation.
    """
    async with websockets.connect(ws_url) as websocket:
        order_ids = []
        timestamps = {}

        # Use asyncio.to_thread to run create_order in a thread pool
        async def send_order():
            response = await asyncio.to_thread(create_order, api_client, stoks="EURUSD", quantity=100.5)
            assert response.status_code == 201
            order_id = response.json()["orderId"]
            order_ids.append(order_id)
            timestamps[order_id] = time.time()

        # Create 100 concurrent tasks to place orders
        tasks = [send_order() for _ in range(100)]
        await asyncio.gather(*tasks)

        execution_times = []
        for _ in range(200):  # Expecting 2 messages per order
            message = json.loads(await websocket.recv())
            ws_order_id = message["orderId"]
            ws_order_status = message["orderStatus"]

            if ws_order_status == order_status.EXECUTED:
                execution_times.append(time.time() - timestamps[ws_order_id])

        avg_delay = mean(execution_times)
        std_dev = stdev(execution_times)

        LOGGER.info(f"Average Execution Delay: {avg_delay:.4f} sec")
        LOGGER.info(f"Standard Deviation: {std_dev:.4f} sec")

        assert avg_delay < 4, "Average Execution Delay is slow"
