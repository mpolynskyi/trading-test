import pytest
from helpers.api_helpers import create_order, get_order, get_orders, cancel_order


@pytest.mark.api
@pytest.mark.positive_scenario
def test_create_valid_order(api_client, order_status):
    """Test placing an order."""
    order = create_order(api_client, stoks="USDEUR", quantity=12)
    assert order.status_code == 201, "response code should be 201"
    order_data = order.json()
    assert "orderId" in order_data, "orderId key should be in response json"
    assert order_data["orderStatus"] == order_status.PENDING, "orderStatus should be pending right after creating order"


@pytest.mark.api
@pytest.mark.negative_scenario
@pytest.mark.parametrize(
    "custom_order_data, expected_missing_fields",
    [
        ({"quantity": 1}, ['stoks']),
        ({"": ""}, ['stoks', 'quantity']),
        ({"stoks": "EURUSD"}, ['quantity']),
        ({"something1": 1, "something2": 2}, ['stoks', 'quantity']),
    ]
)
def test_create_order_without_required_body_fields(api_client, custom_order_data, expected_missing_fields):
    """
    1. Try to create an order without required body fields.
    2. Assert it was prevented
    """
    order = create_order(api_client, custom_order_data=custom_order_data)
    assert order.status_code == 422
    error_data = order.json()

    # Extract error details from response
    response_errors = {
        (tuple(error['loc']), error['type'], error['msg'])
        for error in error_data['detail']
    }

    # Expected errors
    expected_errors = {
        (('body', field), 'missing', 'Field required')
        for field in expected_missing_fields
    }

    assert response_errors == expected_errors


@pytest.mark.api
@pytest.mark.positive_scenario
def test_get_new_order(api_client):
    """
    1. Create a new order.
    2. Get this order.
    3. Assert it was created successfully.
    """
    order = create_order(api_client, stoks="AUDEUR", quantity=120)
    assert order.status_code == 201
    order_data = order.json()
    order_id = order_data["orderId"]

    retrieved_order_response = get_order(api_client, order_id)
    assert retrieved_order_response.status_code == 200
    retrieved_order_data = retrieved_order_response.json()
    assert retrieved_order_data["orderId"] == order_id
    assert retrieved_order_data["stoks"] == "AUDEUR"
    assert retrieved_order_data["quantity"] == 120.0


@pytest.mark.api
@pytest.mark.positive_scenario
def test_get_existing_order(api_client, get_order_fixture):
    """
    1. Get order from fixture
    2. Assert data was retrieved successfully.
    """
    retrieved_order_response = get_order(api_client, get_order_fixture['orderId'])
    assert retrieved_order_response.status_code == 200
    retrieved_order_data = retrieved_order_response.json()
    assert retrieved_order_data == get_order_fixture


@pytest.mark.api
@pytest.mark.negative_scenario
def test_get_order_that_does_not_exist(api_client, faker):
    """
    1. Get order by id that does not exist.
    2. Assert error message and status code is 404.
    """
    fake_uuid = faker.uuid4()
    retrieved_order_response = get_order(api_client, fake_uuid)
    assert retrieved_order_response.status_code == 404
    error_message = retrieved_order_response.json()
    assert error_message['detail'] == "Order not found"
    print(error_message)


@pytest.mark.api
@pytest.mark.positive_scenario
def test_cancel_pending_order(api_client, order_status, pending_order_data_fixture):
    """
    1. Cancel fixture pending order.
    2. Get order data by id
    3. assert it was canceled
    """
    cancel_order_response = cancel_order(api_client, pending_order_data_fixture['orderId'])
    assert cancel_order_response.status_code == 204

    get_canceled_order_response = get_order(api_client, pending_order_data_fixture['orderId'])

    assert get_canceled_order_response.status_code == 200
    canceled_order_data = get_canceled_order_response.json()
    assert canceled_order_data["orderStatus"] == order_status.CANCELED, f"order with id {pending_order_data_fixture['order_id']} was not canceled, it's status {canceled_order_data['orderStatus']}"
    canceled_order_data.pop("orderStatus")
    pending_order_data_fixture.pop("orderStatus")
    assert canceled_order_data == canceled_order_data, "something else except order status was changed"


@pytest.mark.api
@pytest.mark.parametrize("order", ["executed_order_data_fixture", "canceled_order_data_fixture"])
@pytest.mark.negative_scenario
def test_cancel_not_pending_order(request, order, api_client, order_status):
    """
    1. Cancel fixture canceled/executed order.
    2. Assert error message and status code
    3. Get order data by id
    4. assert it was not canceled
    """
    order_data = request.getfixturevalue(order)
    cancel_order_response = cancel_order(api_client, order_data['orderId'])
    assert cancel_order_response.status_code == 400
    assert cancel_order_response.json() == {'detail': f'Only pending orders can be canceled. Current status: {order_data["orderStatus"]}'}, "unexpected error message during cancel uncancellable order"


@pytest.mark.api
@pytest.mark.positive_scenario
def test_get_all_orders(api_client, get_all_orders_fixture):
    """
    1. get all orders.
    2. assert there is orders and they have valid data
    """
    retrieved_orders_response = get_orders(api_client)
    assert retrieved_orders_response.status_code == 200
    retrieved_orders_data = retrieved_orders_response.json()
    assert len(retrieved_orders_data) != 0
    for order in retrieved_orders_data:
        assert 'orderId' in order, "Missing orderId"
        assert 'orderStatus' in order, "Missing orderStatus"
        assert isinstance(order['quantity'], (int, float)), f"Invalid quantity in order {order['orderId']}"
