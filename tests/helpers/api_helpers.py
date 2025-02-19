from requests import Session, Response
from typing import Optional
import httpx


async def async_create_order(httpx_async_client: httpx.AsyncClient, stoks: str = "EURUSD", quantity: float = 100.5,
                             custom_order_data: Optional[dict] = None) -> Response:
    """
        :param httpx_async_client: httpx client with set up base url
        :param stoks: str; ex EURUSD
        :param quantity: int; ex 100.5
        :param custom_order_data: dict with custom data to send it on /ORDERS. used for negative testing; ex {"wrong key": "something", "wrongkey2": "something2"}
        :return: requests Response obj
        """
    order_data = custom_order_data if custom_order_data else {"stoks": stoks, "quantity": quantity}
    response = await httpx_async_client.post("/orders", json=order_data, timeout=10)
    return response


def create_order(client: Session, stoks: str = "EURUSD", quantity: float = 100.5,
                 custom_order_data: Optional[dict] = None) -> Response:
    """
    :param client: requests client with set up base url
    :param stoks: str; ex EURUSD
    :param quantity: int; ex 100.5
    :param custom_order_data: dict with custom data to send it on /ORDERS. used for negative testing; ex {"wrong key": "something", "wrongkey2": "something2"}
    :return: requests Response obj
    """
    order_data = custom_order_data if custom_order_data else {"stoks": stoks, "quantity": quantity}
    response = client.post("/orders", json=order_data)
    return response


def get_order(client: Session, order_id: str) -> Response:
    """
    :param client: requests client with set up base url
    :param order_id: id of requested order
    :return: requests Response obj
    """
    response = client.get(f"/orders/{order_id}")
    return response


def get_orders(client: Session) -> Response:
    """
    :param client: requests client with set up base url
    :return: requests Response obj
    """
    response = client.get("/orders")
    return response


def cancel_order(client: Session, order_id: str) -> Response:
    """
    :param client: requests client with set up base url
    :param order_id: id of requested order
    :return: requests Response obj
    """
    response = client.delete(f"/orders/{order_id}")
    return response
