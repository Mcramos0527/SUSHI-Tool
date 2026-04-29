"""
Tests — SUSHI Tool Access Filter
Validates that IAM field-level controls work correctly.

These tests verify:
- Sensitive fields are blocked for sales roles
- Allowed fields are returned correctly
- SoD conflicts are prevented
- PII is never exposed
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.access_filter import AccessFilter


# --- Test data: Full SAP order including ALL sensitive fields ---
MOCK_SAP_ORDER = {
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
            "cost_price": 620.00,         # SENSITIVE
            "currency": "EUR"
        }
    ],
    # Sensitive fields
    "customer_tax_id": "DE-VAT-812345678",
    "billing_address": "Ingram Allee 1, Munich",
    "cost_price": 620.00,
    "margin_percentage": 27.0,
    "internal_notes": "Priority account",
    "credit_limit": 500000.00,
}


class TestSalesRepresentativeFilter:
    """Tests for sales_representative role — most restricted."""

    def setup_method(self):
        self.filter = AccessFilter(user_role="sales_representative")

    def test_pii_tax_id_blocked(self):
        """Customer tax ID must never reach sales users."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "customer_tax_id" not in result, "TAX ID EXPOSED — IAM VIOLATION"

    def test_pii_billing_address_blocked(self):
        """Billing address is PII — must be blocked."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "billing_address" not in result, "BILLING ADDRESS EXPOSED — PII VIOLATION"

    def test_cost_price_blocked(self):
        """Cost price creates SoD conflict — must be blocked."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "cost_price" not in result, "COST PRICE EXPOSED — SOD VIOLATION"

    def test_margin_blocked(self):
        """Margin data is confidential — must be blocked."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "margin_percentage" not in result, "MARGIN EXPOSED — CONFIDENTIAL DATA VIOLATION"

    def test_credit_limit_blocked(self):
        """Credit limit is finance-only — must be blocked for sales reps."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "credit_limit" not in result, "CREDIT LIMIT EXPOSED — ACCESS VIOLATION"

    def test_order_status_allowed(self):
        """Order status is required for sales ops — must be returned."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "order_status" in result
        assert result["order_status"] == "In Delivery"

    def test_customer_name_allowed(self):
        """Customer name is required — must be returned."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "customer_name" in result
        assert result["customer_name"] == "Ingram Micro GmbH"

    def test_special_price_allowed(self):
        """Special pricing info is allowed for sales reps."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "line_items_filtered" in result
        item = result["line_items_filtered"][0]
        assert "special_price_eligible" in item
        assert item["special_price_eligible"] is True

    def test_line_item_cost_price_stripped(self):
        """Cost price inside line items must also be stripped."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        item = result["line_items_filtered"][0]
        assert "cost_price" not in item, "COST PRICE IN LINE ITEM EXPOSED"


class TestSalesManagerFilter:
    """Tests for sales_manager role — slightly elevated access."""

    def setup_method(self):
        self.filter = AccessFilter(user_role="sales_manager")

    def test_pii_still_blocked_for_manager(self):
        """PII must remain blocked even for managers."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "customer_tax_id" not in result
        assert "billing_address" not in result

    def test_credit_limit_allowed_for_manager(self):
        """Managers can see credit limit — business requirement."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "credit_limit" in result

    def test_cost_price_still_blocked_for_manager(self):
        """Cost price remains blocked — finance domain only."""
        result = self.filter.apply(MOCK_SAP_ORDER)
        assert "cost_price" not in result


class TestFieldAllowanceCheck:
    """Tests for individual field permission checks."""

    def test_is_field_allowed_positive(self):
        f = AccessFilter("sales_representative")
        assert f.is_field_allowed("order_status") is True

    def test_is_field_allowed_negative(self):
        f = AccessFilter("sales_representative")
        assert f.is_field_allowed("customer_tax_id") is False

    def test_finance_full_access(self):
        f = AccessFilter("finance_controller")
        assert f.is_field_allowed("customer_tax_id") is True
        assert f.is_field_allowed("margin_percentage") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
