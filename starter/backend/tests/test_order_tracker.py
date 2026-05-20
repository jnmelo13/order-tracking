import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#


def test_add_order_success_with_default_status(order_tracker, mock_storage):
    """Verify add_order saves order with default status='pending' when status is omitted."""
    order_tracker.add_order(
        order_id="ORD-001",
        item_name="Widget",
        quantity=5,
        customer_id="CUST-123",
    )

    mock_storage.save_order.assert_called_once_with(
        "ORD-001",
        {
            "order_id": "ORD-001",
            "item_name": "Widget",
            "quantity": 5,
            "customer_id": "CUST-123",
            "status": "pending",
        },
    )


def test_add_order_success_with_explicit_status(order_tracker, mock_storage):
    """Verify add_order saves order with the explicitly provided status."""
    order_tracker.add_order(
        order_id="ORD-002",
        item_name="Gadget",
        quantity=2,
        customer_id="CUST-456",
        status="processing",
    )

    mock_storage.save_order.assert_called_once_with(
        "ORD-002",
        {
            "order_id": "ORD-002",
            "item_name": "Gadget",
            "quantity": 2,
            "customer_id": "CUST-456",
            "status": "processing",
        },
    )


def test_add_order_returns_order_dict(order_tracker):
    """Verify add_order returns a dictionary containing all order fields."""
    result = order_tracker.add_order(
        order_id="ORD-003",
        item_name="Sprocket",
        quantity=10,
        customer_id="CUST-789",
    )

    assert result == {
        "order_id": "ORD-003",
        "item_name": "Sprocket",
        "quantity": 10,
        "customer_id": "CUST-789",
        "status": "pending",
    }


def test_add_order_rejects_empty_order_id(order_tracker):
    """Verify add_order raises ValueError for empty order_id."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.add_order(
            order_id="",
            item_name="Widget",
            quantity=5,
            customer_id="CUST-123",
        )


def test_add_order_rejects_none_order_id(order_tracker):
    """Verify add_order raises ValueError for None order_id."""
    with pytest.raises(ValueError):
        order_tracker.add_order(
            order_id=None,
            item_name="Widget",
            quantity=5,
            customer_id="CUST-123",
        )


def test_add_order_rejects_empty_item_name(order_tracker):
    """Verify add_order raises ValueError for empty item_name."""
    with pytest.raises(ValueError, match="item_name"):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="",
            quantity=5,
            customer_id="CUST-123",
        )


def test_add_order_rejects_empty_customer_id(order_tracker):
    """Verify add_order raises ValueError for empty customer_id."""
    with pytest.raises(ValueError, match="customer_id"):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="Widget",
            quantity=5,
            customer_id="",
        )


def test_add_order_rejects_zero_quantity(order_tracker):
    """Verify add_order raises ValueError for zero quantity."""
    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="Widget",
            quantity=0,
            customer_id="CUST-123",
        )


def test_add_order_rejects_negative_quantity(order_tracker):
    """Verify add_order raises ValueError for negative quantity."""
    with pytest.raises(ValueError):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="Widget",
            quantity=-1,
            customer_id="CUST-123",
        )


def test_add_order_rejects_invalid_status(order_tracker):
    """Verify add_order raises ValueError for invalid status."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="Widget",
            quantity=5,
            customer_id="CUST-123",
            status="unknown",
        )


def test_add_order_rejects_duplicate_order_id(order_tracker, mock_storage):
    """Verify add_order raises ValueError when order_id already exists."""
    mock_storage.get_order.return_value = {"order_id": "ORD-001", "item_name": "Existing"}

    with pytest.raises(ValueError, match="(duplicate|exists)"):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="Widget",
            quantity=5,
            customer_id="CUST-123",
        )


def test_get_order_by_id_returns_order_when_present(order_tracker, mock_storage):
    """Verify get_order_by_id returns order data when found."""
    expected_order = {
        "order_id": "ORD-001",
        "item_name": "Widget",
        "quantity": 5,
        "customer_id": "CUST-123",
        "status": "pending",
    }
    mock_storage.get_order.return_value = expected_order

    result = order_tracker.get_order_by_id("ORD-001")

    assert result == expected_order
    mock_storage.get_order.assert_called_with("ORD-001")


def test_get_order_by_id_returns_none_when_absent(order_tracker, mock_storage):
    """Verify get_order_by_id returns None when order not found."""
    mock_storage.get_order.return_value = None

    result = order_tracker.get_order_by_id("ORD-NONEXISTENT")

    assert result is None
    mock_storage.get_order.assert_called_with("ORD-NONEXISTENT")


def test_get_order_by_id_rejects_empty_order_id(order_tracker):
    """Verify get_order_by_id raises ValueError for empty order_id."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id("")


def test_get_order_by_id_rejects_none_order_id(order_tracker):
    """Verify get_order_by_id raises ValueError for None order_id."""
    with pytest.raises(ValueError):
        order_tracker.get_order_by_id(None)


def test_update_order_status_success(order_tracker, mock_storage):
    """Verify update_order_status saves order with updated status."""
    existing_order = {
        "order_id": "ORD-001",
        "item_name": "Widget",
        "quantity": 5,
        "customer_id": "CUST-123",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order.copy()

    order_tracker.update_order_status("ORD-001", "shipped")

    mock_storage.save_order.assert_called_once_with(
        "ORD-001",
        {
            "order_id": "ORD-001",
            "item_name": "Widget",
            "quantity": 5,
            "customer_id": "CUST-123",
            "status": "shipped",
        },
    )


def test_update_order_status_returns_updated_order(order_tracker, mock_storage):
    """Verify update_order_status returns order dict with new status."""
    existing_order = {
        "order_id": "ORD-001",
        "item_name": "Widget",
        "quantity": 5,
        "customer_id": "CUST-123",
        "status": "pending",
    }
    mock_storage.get_order.return_value = existing_order.copy()

    result = order_tracker.update_order_status("ORD-001", "processing")

    assert result["status"] == "processing"
    assert result["order_id"] == "ORD-001"


def test_update_order_status_rejects_invalid_status_before_storage_read(order_tracker, mock_storage):
    """Verify invalid status raises ValueError before storage.get_order is called (fail-fast)."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", "invalid")

    mock_storage.get_order.assert_not_called()


def test_update_order_status_rejects_empty_status(order_tracker):
    """Verify update_order_status raises ValueError for empty status."""
    with pytest.raises(ValueError):
        order_tracker.update_order_status("ORD-001", "")


def test_update_order_status_raises_for_nonexistent_order(order_tracker, mock_storage):
    """Verify update_order_status raises ValueError when order not found."""
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="not found"):
        order_tracker.update_order_status("ORD-NONEXISTENT", "shipped")


def test_update_order_status_rejects_empty_order_id(order_tracker):
    """Verify update_order_status raises ValueError for empty order_id."""
    with pytest.raises(ValueError):
        order_tracker.update_order_status("", "shipped")


def test_update_order_status_does_not_mutate_original(order_tracker, mock_storage):
    """Verify update_order_status does not mutate the storage's original return value."""
    original_order = {
        "order_id": "ORD-001",
        "item_name": "Widget",
        "quantity": 5,
        "customer_id": "CUST-123",
        "status": "pending",
    }
    mock_storage.get_order.return_value = original_order

    order_tracker.update_order_status("ORD-001", "delivered")

    assert original_order["status"] == "pending"


def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """Verify list_all_orders returns list with all orders."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"order_id": "ORD-001", "item_name": "Widget", "status": "pending"},
        "ORD-002": {"order_id": "ORD-002", "item_name": "Gadget", "status": "shipped"},
    }

    result = order_tracker.list_all_orders()

    assert len(result) == 2


def test_list_all_orders_returns_empty_list_when_no_orders(order_tracker, mock_storage):
    """Verify list_all_orders returns empty list when no orders exist."""
    mock_storage.get_all_orders.return_value = {}

    result = order_tracker.list_all_orders()

    assert result == []


def test_list_all_orders_returns_list_not_dict(order_tracker, mock_storage):
    """Verify list_all_orders returns a list, not a dict."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"order_id": "ORD-001", "item_name": "Widget"},
    }

    result = order_tracker.list_all_orders()

    assert isinstance(result, list)


def test_list_all_orders_includes_order_id_in_each_item(order_tracker, mock_storage):
    """Verify each item in list_all_orders contains order_id field."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"order_id": "ORD-001", "item_name": "Widget"},
        "ORD-002": {"order_id": "ORD-002", "item_name": "Gadget"},
    }

    result = order_tracker.list_all_orders()

    for order in result:
        assert "order_id" in order


def test_list_orders_by_status_returns_matching_orders(order_tracker, mock_storage):
    """Verify list_orders_by_status returns only orders with matching status."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"order_id": "ORD-001", "item_name": "Widget", "status": "pending"},
        "ORD-002": {"order_id": "ORD-002", "item_name": "Gadget", "status": "shipped"},
        "ORD-003": {"order_id": "ORD-003", "item_name": "Sprocket", "status": "pending"},
    }

    result = order_tracker.list_orders_by_status("pending")

    assert len(result) == 2
    for order in result:
        assert order["status"] == "pending"


def test_list_orders_by_status_returns_empty_list_when_no_match(order_tracker, mock_storage):
    """Verify list_orders_by_status returns empty list when no orders match."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"order_id": "ORD-001", "item_name": "Widget", "status": "pending"},
        "ORD-002": {"order_id": "ORD-002", "item_name": "Gadget", "status": "shipped"},
    }

    result = order_tracker.list_orders_by_status("cancelled")

    assert result == []


def test_list_orders_by_status_rejects_empty_status(order_tracker):
    """Verify list_orders_by_status raises ValueError for empty status."""
    with pytest.raises(ValueError):
        order_tracker.list_orders_by_status("")


def test_list_orders_by_status_rejects_invalid_status(order_tracker):
    """Verify list_orders_by_status raises ValueError for invalid status."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status("unknown")


def test_list_orders_by_status_rejects_none_status(order_tracker):
    """Verify list_orders_by_status raises ValueError for None status."""
    with pytest.raises(ValueError):
        order_tracker.list_orders_by_status(None)
