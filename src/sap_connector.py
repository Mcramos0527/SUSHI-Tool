"""
SAP Connector — SUSHI Tool
Handles connection to SAP order data via BAPI_SALESORDER_GETLIST.
Sanitized for portfolio — connection details removed.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# --- Field definitions ---
# ALL fields available in VA02 Conditions tab
ALL_SAP_FIELDS = {
    "order_number": "4500012345",
    "customer_name": "Ingram Micro GmbH",
    "customer_id": "CUST-DE-00234",
    "order_status": "In Delivery",
    "order_date": "2024-03-15",
    "requested_delivery_date": "2024-03-22",
    "line_items": [
        {
            "material": "HP ProBook 450 G9",
            "quantity": 50,
            "unit": "EA",
            "standard_price": 850.00,
            "special_price_eligible": True,
            "special_price": 812.00,
            "currency": "EUR"
        }
    ],
    # --- SENSITIVE FIELDS — NEVER EXPOSED TO SALES USERS ---
    "customer_tax_id": "DE-VAT-812345678",           # PII — blocked
    "billing_address": "Ingram Allee 1, Munich",      # PII — blocked
    "cost_price": 620.00,                              # Confidential — blocked
    "margin_percentage": 27.0,                         # Confidential — blocked
    "internal_notes": "Priority account — handle carefully",  # Internal — blocked
    "credit_limit": 500000.00,                         # Confidential — blocked
}


class SAPConnector:
    """
    Simulates connection to SAP via BAPI_SALESORDER_GETLIST.

    In production:
    - Connects to SAP RFC destination via pyrfc or enterprise DB
    - Calls BAPI_SALESORDER_GETLIST with order filters
    - Returns raw order data including ALL fields

    IMPORTANT: Raw data is NEVER sent directly to the user.
    All data passes through AccessFilter before being returned.
    """

    def __init__(self):
        # In production: load SAP RFC connection config from environment
        self.connected = True
        logger.info("SAP Connector initialized (sanitized demo mode)")

    def get_order_data(self, order_number: str) -> dict:
        """
        Retrieve full order data from SAP.
        Returns ALL fields — filtering happens in AccessFilter layer.

        Args:
            order_number: SAP sales order number (10 digits)

        Returns:
            dict: Complete order data including sensitive fields
        """
        logger.info(f"SAP BAPI call: BAPI_SALESORDER_GETLIST — Order: {order_number}")

        # In production this would be:
        # result = self.connection.call('BAPI_SALESORDER_GETLIST',
        #                               SALESDOCUMENT=order_number)
        # return self._parse_bapi_result(result)

        # Sanitized demo — returns mock data structure
        return {**ALL_SAP_FIELDS, "order_number": order_number}

    def get_customer_orders(self, customer_id: str, limit: int = 10) -> list:
        """
        Retrieve recent orders for a customer.

        Args:
            customer_id: SAP customer ID
            limit: Maximum number of orders to return

        Returns:
            list: List of order summaries
        """
        logger.info(f"SAP BAPI call: BAPI_SALESORDER_GETLIST — Customer: {customer_id}")

        # Sanitized demo response
        return [
            {"order_number": "4500012345", "status": "In Delivery", "date": "2024-03-15"},
            {"order_number": "4500012289", "status": "Delivered", "date": "2024-02-28"},
            {"order_number": "4500012100", "status": "Invoiced", "date": "2024-02-10"},
        ][:limit]
