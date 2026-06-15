"""
Tool functions for the agent, including real Salesforce CRM lead capture.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def capture_lead(name: str, email: str, platform: str, plan: str = "Not specified") -> str:
    """
    Capture lead information and save it to Salesforce CRM.
    Falls back to console logging if Salesforce credentials are not configured.

    Args:
        name: Customer's full name
        email: Customer's email address
        platform: Content platform they use (YouTube, Instagram, etc.)
        plan: The AutoStream plan they are interested in (Basic Plan / Pro Plan)

    Returns:
        Confirmation message string
    """

    sf_username = os.getenv("SF_USERNAME")
    sf_password = os.getenv("SF_PASSWORD")
    sf_security_token = os.getenv("SF_SECURITY_TOKEN")

    # ── Console log (always) ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("✓ LEAD CAPTURE TRIGGERED")
    print("=" * 70)
    print(f"Name:     {name}")
    print(f"Email:    {email}")
    print(f"Platform: {platform}")
    print(f"Plan:     {plan}")
    print("=" * 70)

    # ── Salesforce CRM ───────────────────────────────────────────────────────
    if sf_username and sf_password and sf_security_token:
        try:
            from simple_salesforce import Salesforce, SalesforceAuthenticationFailed

            sf = Salesforce(
                username=sf_username,
                password=sf_password,
                security_token=sf_security_token,
            )

            # Split name into first / last
            name_parts = name.strip().split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else "Unknown"

            lead_data = {
                "FirstName": first_name,
                "LastName": last_name,
                "Email": email,
                "Company": f"Content Creator ({platform})",
                "LeadSource": "AutoStream Chatbot",
                # Store extra context in the Description field
                "Description": (
                    f"Platform: {platform}\n"
                    f"Interested Plan: {plan}\n"
                    f"Source: AutoStream AI Chat Agent"
                ),
            }

            result = sf.Lead.create(lead_data)

            if result.get("success"):
                sf_id = result.get("id", "unknown")
                print(f"✅ Salesforce Lead created! ID: {sf_id}")
                return (
                    f"Lead captured and saved to Salesforce ✅ "
                    f"(ID: {sf_id}) — {name} ({email}), "
                    f"Platform: {platform}, Plan: {plan}"
                )
            else:
                errors = result.get("errors", [])
                print(f"⚠️  Salesforce returned errors: {errors}")
                return f"Lead logged locally, Salesforce error: {errors}"

        except ImportError:
            print("⚠️  simple-salesforce not installed. Run: pip install simple-salesforce")
            return f"Lead captured locally (Salesforce SDK missing): {name} ({email})"

        except Exception as e:  # noqa: BLE001
            print(f"⚠️  Salesforce error: {e}")
            return f"Lead captured locally, Salesforce error: {str(e)}"

    else:
        print("ℹ️  Salesforce credentials not configured — saved locally only.")
        return (
            f"Lead captured (local only): {name} ({email}) — "
            f"Platform: {platform}, Plan: {plan}"
        )


# ── Validation helpers ────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    """Simple email validation."""
    return "@" in email and "." in email and len(email) > 5


def validate_name(name: str) -> bool:
    """Check if name is valid (not empty)."""
    return len(name.strip()) >= 2


def validate_platform(platform: str, valid_platforms: list) -> bool:
    """Check if platform is in the list of supported platforms."""
    return platform.lower() in [p.lower() for p in valid_platforms]