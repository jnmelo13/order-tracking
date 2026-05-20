# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

## Reflection

- **Design Decision (Fail-Fast Validation):** In `update_order_status`, I validate the `new_status` parameter *before* querying storage. This prevents unnecessary database reads for invalid requests and keeps the validation logic in the domain layer, making it framework-agnostic and easier to test.

- **Testing Insight:** The `test_update_order_status_does_not_mutate_original` test caught a subtle bug early, without using `.copy()` on the retrieved order, the original storage data would be mutated. Writing this test forced the implementation to handle data immutability correctly.

- **Next-Step Improvement:** I would add a `DELETE /api/orders/<order_id>` endpoint and migrate from in-memory storage to a persistent database (e.g., SQLite or PostgreSQL). The current storage abstraction makes this straightforward, just implement a new class with `save_order`, `get_order`, and `get_all_orders` methods.
