import httpx
import pytest
from requests.adapters import HTTPAdapter
from requests_toolbelt import sessions
from random import randint
from pymongo import MongoClient
from helpers.db_helpers import populate_test_data_in_db, clean_test_data
from urllib.parse import urljoin


@pytest.fixture(scope="session")
def mongo_connection_string():
    url = "mongodb://mongo:27017/trading" #  not very dynamic but for this project - ok
    return url


@pytest.fixture(scope="session")
def orders_collection(request, mongo_connection_string):
    client = MongoClient(mongo_connection_string)
    db = client.trading
    yield db.orders
    client.close()


def pytest_addoption(parser):
    parser.addoption("--url", action="store", default="http://localhost:8000",
                     help="url to api server")


@pytest.fixture(scope="session")
def base_url(request):
    url = (request.config.getoption("--url")).lower()
    return url


@pytest.fixture(scope="session")
def ws_url(base_url):
    ws_url = urljoin(base_url.replace("http", "ws"), "/ws")
    return ws_url


@pytest.fixture(scope="session")
def api_client(base_url):
    """Fixture for sync HTTP client using requests."""
    client = sessions.BaseUrlSession(base_url=base_url)
    adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
    client.mount('http://', adapter)
    client.mount('https://', adapter)
    yield client


@pytest.fixture(scope="session")
def async_api_client(base_url):
    return httpx.AsyncClient(base_url=base_url)


@pytest.fixture(autouse=True)
def faker_seed():
    seed = randint(0, 99999)
    return seed


class OrderStatus:
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELED = "canceled"


@pytest.fixture(scope="session")
def order_status():
    return OrderStatus


@pytest.fixture(scope="function")
def pending_order_data_fixture(orders_collection):
    data = {"orderId": "test_pending", "stoks": "EURUSD", "quantity": 100.4, "orderStatus": OrderStatus.PENDING}
    populate_test_data_in_db(orders_collection, data)
    yield data
    clean_test_data(orders_collection, data['orderId'])


@pytest.fixture(scope="function")
def executed_order_data_fixture(orders_collection):
    data = {"orderId": "test_executed", "stoks": "EURUSD", "quantity": 200.2, "orderStatus": OrderStatus.EXECUTED}
    populate_test_data_in_db(orders_collection, data)
    yield data
    clean_test_data(orders_collection, data['orderId'])


@pytest.fixture(scope="function")
def canceled_order_data_fixture(orders_collection):
    data = {"orderId": "test_canceled", "stoks": "EURUSD", "quantity": 300.3, "orderStatus": OrderStatus.CANCELED}
    populate_test_data_in_db(orders_collection, data)
    yield data
    clean_test_data(orders_collection, data['orderId'])


@pytest.fixture(scope="function")
def get_order_fixture(orders_collection):
    data = {"orderId": "test_get_order", "stoks": "EURUSD", "quantity": 400, "orderStatus": OrderStatus.PENDING}
    populate_test_data_in_db(orders_collection, data)
    yield data
    clean_test_data(orders_collection, data['orderId'])


@pytest.fixture(scope="function")
def get_all_orders_fixture(orders_collection):
    data = {"orderId": "test_get_all_orders", "stoks": "EURUSD", "quantity": 400, "orderStatus": OrderStatus.PENDING}
    populate_test_data_in_db(orders_collection, data)
    yield data
    clean_test_data(orders_collection, data['orderId'])
