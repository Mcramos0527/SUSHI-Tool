"""
SUSHI Tool — Super User Sales Highly Informed
IAM-driven AI agent for SAP order data access with least privilege enforcement.

Author: Max Ramos | TD SYNNEX EMEA
Purpose: Replace direct SAP VA02 access with a field-filtered AI interface
         enforcing SoD controls and PII protection at the integration layer.
"""

import os
import json
import logging
from datetime import datetime
from openai import OpenAI
from sushi_tool.src.sap_connector import SAPConnector
from sushi_tool.src.access_filter import AccessFilter
from sushi_tool.src.audit_logger import AuditLogger

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class SUSHITool:
    """
    SUSHI Tool — Super User Sales Highly Informed

    Core IAM design principles enforced:
    - Least Privilege: only approved fields returned to the user
    - SoD Enforcement: no direct SAP access granted to sales users
    - Audit Trail: every query logged immutably
    - PII Protection: sensitive fields stripped at integration layer
    """

    def __init__(self, user_id: str, user_role: str):
        self.user_id = user_id
        self.user_role = user_role
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.sap = SAPConnector()
        self.filter = AccessFilter(user_role=user_role)
        self.audit = AuditLogger()
        self.conversation_history = []

        logger.info(f"SUSHI Tool session started — User: {user_id} | Role: {user_role}")

    def query(self, user_input: str) -> str:
        """
        Process a natural language query from the sales user.
        Enforces field-level access filtering before returning data.
        """
        # Log the incoming query
        self.audit.log_query(
            user_id=self.user_id,
            user_role=self.user_role,
            query=user_input,
            timestamp=datetime.utcnow().isoformat()
        )

        # Build system prompt with IAM context
        system_prompt = self._build_system_prompt()

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Get SAP data if order number detected
        sap_context = ""
        order_number = self._extract_order_number(user_input)
        if order_number:
            raw_data = self.sap.get_order_data(order_number)
            filtered_data = self.filter.apply(raw_data)
            sap_context = f"\n\nSAP Order Data (filtered for your role):\n{json.dumps(filtered_data, indent=2)}"
            logger.info(f"SAP data retrieved and filtered for order {order_number}")

        # Build messages for OpenAI
        messages = [{"role": "system", "content": system_prompt + sap_context}]
        messages.extend(self.conversation_history)

        # Call OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.2,
            max_tokens=800
        )

        assistant_reply = response.choices[0].message.content

        # Add response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_reply
        })

        # Log the response
        self.audit.log_response(
            user_id=self.user_id,
            query=user_input,
            response_summary=assistant_reply[:200],
            order_number=order_number,
            timestamp=datetime.utcnow().isoformat()
        )

        return assistant_reply

    def _build_system_prompt(self) -> str:
        allowed_fields = self.filter.get_allowed_fields()
        return f"""You are SUSHI Tool — a secure AI assistant for TD SYNNEX sales representatives.

Your role is to help sales users query SAP order information in natural language.

IMPORTANT SECURITY RULES — YOU MUST FOLLOW THESE AT ALL TIMES:
1. You may ONLY share information from these approved fields: {allowed_fields}
2. You must NEVER reveal, reference, or acknowledge the existence of: Tax IDs, billing addresses, 
   cost prices, margin data, or any other sensitive financial information.
3. If the user asks for restricted information, politely explain you are not authorised to share it.
4. If no SAP data is provided, ask the user for their order number.
5. Always be helpful, concise, and professional.

Your purpose is to give sales reps exactly what they need to serve customers — nothing more."""

    def _extract_order_number(self, text: str) -> str | None:
        """Extract SAP order number from user input."""
        import re
        # SAP order numbers are typically 10 digits
        match = re.search(r'\b\d{10}\b', text)
        if match:
            return match.group()
        # Also check for patterns like "order 123456789"
        match = re.search(r'order\s+(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
