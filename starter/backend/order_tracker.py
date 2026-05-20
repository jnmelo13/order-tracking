# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = ("pending", "processing", "shipped", "delivered", "cancelled")
DEFAULT_STATUS = "pending"


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def _validate_order_fields(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str):
        self._validate_order_id(order_id)
        if not item_name:
            raise ValueError("item_name is required and cannot be empty")
        if not customer_id:
            raise ValueError("customer_id is required and cannot be empty")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer")
        self._validate_status(status)

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = DEFAULT_STATUS):
        self._validate_order_fields(order_id, item_name, quantity, customer_id, status)
        if self.storage.get_order(order_id) is not None:
            raise ValueError(f"Order with order_id '{order_id}' already exists")

        order_data = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order_data)
        return order_data

    def _validate_order_id(self, order_id: str):
        if not order_id:
            raise ValueError("order_id is required and cannot be empty")

    def get_order_by_id(self, order_id: str):
        self._validate_order_id(order_id)
        return self.storage.get_order(order_id)

    def _validate_status(self, status: str):
        if not status or status not in VALID_STATUSES:
            raise ValueError(f"status must be one of {VALID_STATUSES}")

    def update_order_status(self, order_id: str, new_status: str):
        self._validate_order_id(order_id)
        self._validate_status(new_status)

        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with order_id '{order_id}' not found")

        updated_order = order.copy()
        updated_order["status"] = new_status
        self.storage.save_order(order_id, updated_order)
        return updated_order

    def list_all_orders(self):
        orders_dict = self.storage.get_all_orders()
        return list(orders_dict.values())

    def list_orders_by_status(self, status: str):
        self._validate_status(status)
        orders_dict = self.storage.get_all_orders()
        return [order for order in orders_dict.values() if order["status"] == status]
