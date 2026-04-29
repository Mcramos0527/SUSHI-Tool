"""
SUSHI Tool — CLI Interface
Standalone entry point for sales user interaction.
Packaged as .exe for internal distribution via company software catalogue.
"""

import os
import sys
from datetime import datetime
from sushi_tool.src.sushi_tool import SUSHITool


WELCOME_BANNER = """
╔══════════════════════════════════════════════════════╗
║       🍣  SUSHI Tool v1.0                           ║
║       Super User Sales Highly Informed              ║
║                                                      ║
║       Secure SAP Order Intelligence                 ║
║       TD SYNNEX EMEA Sales Operations               ║
╚══════════════════════════════════════════════════════╝

Type your question in plain English.
Type 'exit' to quit. Type 'help' for examples.

Examples:
  > What's the status of order 4500012345?
  > Does customer Ingram have any special pricing available?
  > Show me the latest orders for customer CUST-DE-00234
"""

HELP_TEXT = """
What you can ask SUSHI Tool:
  ✅ Order status and delivery dates
  ✅ Customer name and ID
  ✅ Standard and special pricing
  ✅ Special price eligibility
  ✅ Line item quantities and materials

What SUSHI Tool cannot show you:
  ❌ Customer tax IDs or billing addresses
  ❌ Internal cost prices or margins
  ❌ Credit limits (sales manager access only)

For access queries, contact your IT Access Management team.
"""


def get_user_credentials() -> tuple[str, str]:
    """Get user ID and role for session initialization."""
    print("\n🔐 Secure Login")
    user_id = input("Enter your Employee ID: ").strip()

    print("\nSelect your role:")
    print("  1. Sales Representative")
    print("  2. Sales Manager")
    role_input = input("Enter 1 or 2: ").strip()

    role_map = {
        "1": "sales_representative",
        "2": "sales_manager"
    }
    user_role = role_map.get(role_input, "sales_representative")
    return user_id, user_role


def run():
    """Main CLI loop."""
    print(WELCOME_BANNER)

    # Get user credentials
    user_id, user_role = get_user_credentials()

    print(f"\n✅ Session started — Welcome, {user_id} ({user_role.replace('_', ' ').title()})")
    print("─" * 55)

    # Initialize SUSHI Tool
    tool = SUSHITool(user_id=user_id, user_role=user_role)
    query_count = 0

    # Main conversation loop
    while True:
        try:
            user_input = input("\n🍣 You: ").strip()

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print(f"\n✅ Session ended. {query_count} queries processed.")
                print("Audit log updated. Goodbye!\n")
                break

            if user_input.lower() == "help":
                print(HELP_TEXT)
                continue

            # Process query
            print("\n⏳ Querying SAP...")
            response = tool.query(user_input)
            print(f"\n🤖 SUSHI: {response}")
            query_count += 1

        except KeyboardInterrupt:
            print("\n\nSession interrupted. Audit log saved.")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or contact IT support.")


if __name__ == "__main__":
    run()
