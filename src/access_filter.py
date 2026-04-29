"""
Access Filter — SUSHI Tool
Core IAM enforcement module.

This is where Least Privilege and SoD controls are enforced.
Sensitive fields are stripped BEFORE data reaches the user layer.

IAM Principles:
- Least Privilege: users receive only fields their role requires
- PII Protection: personal data stripped at integration layer
- SoD Enforcement: no access to fields that create control conflicts
- Role-Based Access: field visibility determined by user role
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


# --- Role-based field access policy ---
# This is the access control matrix — defines what each role can see
ROLE_ACCESS_POLICY = {
    "sales_representative": {
        "allowed_fields": [
            "order_number",
            "customer_name",
            "customer_id",
            "order_status",
            "order_date",
            "requested_delivery_date",
            "line_items_filtered",  # filtered version — no cost prices
            "special_price_eligible",
            "special_price",
            "currency"
        ],
        "blocked_fields": [
            "customer_tax_id",      # PII
            "billing_address",      # PII
            "cost_price",           # Confidential — SoD conflict
            "margin_percentage",    # Confidential — SoD conflict
            "internal_notes",       # Internal only
            "credit_limit",         # Finance only
        ],
        "description": "Standard sales rep — customer and order visibility only"
    },
    "sales_manager": {
        "allowed_fields": [
            "order_number",
            "customer_name",
            "customer_id",
            "order_status",
            "order_date",
            "requested_delivery_date",
            "line_items_filtered",
            "special_price_eligible",
            "special_price",
            "currency",
            "credit_limit"          # Managers can see credit limit
        ],
        "blocked_fields": [
            "customer_tax_id",      # PII — still blocked
            "billing_address",      # PII — still blocked
            "cost_price",           # Finance only
            "margin_percentage",    # Finance only
            "internal_notes",       # Internal only
        ],
        "description": "Sales manager — adds credit limit visibility"
    },
    "finance_controller": {
        "allowed_fields": "__all__",  # Finance has full access via separate channel
        "blocked_fields": [],
        "description": "Finance role — full access (uses separate finance system)"
    }
}


class AccessFilter:
    """
    Enforces field-level access control based on user role.

    This is the IAM enforcement point — no data passes through
    without being validated against the role access policy.
    """

    def __init__(self, user_role: str):
        self.user_role = user_role
        self.policy = ROLE_ACCESS_POLICY.get(user_role, ROLE_ACCESS_POLICY["sales_representative"])
        logger.info(f"AccessFilter initialized — Role: {user_role} | Policy: {self.policy['description']}")

    def apply(self, raw_data: dict) -> dict:
        """
        Apply role-based field filtering to raw SAP data.

        Args:
            raw_data: Complete SAP order data including sensitive fields

        Returns:
            dict: Filtered data containing only role-approved fields
        """
        if self.policy["allowed_fields"] == "__all__":
            logger.info("Full access policy — returning all fields")
            return raw_data

        filtered = {}
        blocked_count = 0

        for field, value in raw_data.items():
            if field in self.policy["blocked_fields"]:
                # Field is blocked — log it but do not include
                logger.warning(f"BLOCKED FIELD: {field} — not returned to user role: {self.user_role}")
                blocked_count += 1
                continue

            if field == "line_items":
                # Special handling for line items — filter sensitive pricing
                filtered["line_items_filtered"] = self._filter_line_items(value)
                continue

            if field in self.policy["allowed_fields"]:
                filtered[field] = value

        logger.info(f"Filter applied — {len(filtered)} fields returned, {blocked_count} fields blocked")
        return filtered

    def _filter_line_items(self, line_items: list) -> list:
        """
        Filter sensitive fields from line item data.
        Removes cost prices while keeping sales-relevant pricing.
        """
        filtered_items = []
        for item in line_items:
            filtered_item = {
                "material": item.get("material"),
                "quantity": item.get("quantity"),
                "unit": item.get("unit"),
                "standard_price": item.get("standard_price"),
                "special_price_eligible": item.get("special_price_eligible"),
                "special_price": item.get("special_price") if item.get("special_price_eligible") else None,
                "currency": item.get("currency")
                # cost_price and margin deliberately excluded
            }
            filtered_items.append(filtered_item)
        return filtered_items

    def get_allowed_fields(self) -> list:
        """Return list of allowed fields for system prompt context."""
        if self.policy["allowed_fields"] == "__all__":
            return ["all fields"]
        return self.policy["allowed_fields"]

    def is_field_allowed(self, field_name: str) -> bool:
        """Check if a specific field is accessible for this role."""
        if self.policy["allowed_fields"] == "__all__":
            return True
        return field_name in self.policy["allowed_fields"]
