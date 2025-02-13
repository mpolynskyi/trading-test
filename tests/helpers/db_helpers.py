import logging
from pymongo.collection import Collection
LOGGER = logging.getLogger(__name__)


def populate_test_data_in_db(mongo_collection: Collection, data: dict):
    LOGGER.info(f"adding order to orders collection: {data}")
    mongo_collection.insert_one(data.copy())


def clean_test_data(mongo_collection: Collection, order_id: str):
    """Removes test data from given collection (orders) by orderId."""
    LOGGER.info(f"removing order with id '{order_id}' from orders collection")
    mongo_collection.delete_one({"orderId": order_id})