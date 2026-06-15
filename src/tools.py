"""
Tool functions for the agent, including real Salesforce CRM lead capture.
Uses OAuth2 Connected App flow (works with Agentforce/Developer orgs
where SOAP API login is disabled).
"""

import os
from dotenv import load_dotenv

load_dotenv()


def capture_lead(name: str, email: str, platform: str, plan: str = "Not specified") -> str:
    """
    Capture lead and save to Salesforce CRM via OAuth2 (Connected App).
    Falls back to console logging if credentials are not configured.
    """

    sf_username       = os.getenv("SF_USERNAME")
    sf_password       = os.getenv("SF_PASSWORD")
    sf_security_token = os.getenv("SF_SECURITY_TOKEN", "")   # may be empty for OAuth2 orgs
    sf_consumer_key   = os.getenv("SF_CONSUMER_KEY")
    sf_consumer_secret = os.getenv("SF_CONSUMER_SECRET")
    sf_domain         = os.getenv("SF_DOMAIN", "login")       # 'login' or 'test' for sandbox

    # ── Console log (always) ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("✓ LEAD CAPTURE TRIGGERED")
    print("=" * 70)
    print(f"Name:     {name}")
    print(f"Email:    {email}")
    print(f"Platform: {platform}")
    print(f"Plan:     {plan}")
    print("=" * 70)

    # ── Salesforce CRM via OAuth2 ─────────────────────────────────────────────
    if sf_username and sf_password and sf_consumer_key and sf_consumer_secret:
        try:
            from simple_salesforce import Salesforce

            sf = Salesforce(
                username=sf_username,
                password=sf_password,
                security_token=sf_security_token,
                consumer_key=sf_consumer_key,
                consumer_secret=sf_consumer_secret,
                domain=sf_domain,
            )

            # Split name into first / last
            name_parts = name.strip().split(" ", 1)
            first_name = name_parts[0]
            last_name  = name_parts[1] if len(name_parts) > 1 else "Unknown"

            lead_data = {
                "FirstName":  first_name,
                "LastName":   last_name,
                "Email":      email,
                "Company":    f"Content Creator ({platform})",
                "LeadSource": "AutoStream Chatbot",
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
            print("⚠️  simple-salesforce not installed.")
            return f"Lead captured locally (SDK missing): {name} ({email})"

        except Exception as e:  # noqa: BLE001
            print(f"⚠️  Salesforce error: {e}")
            return f"Lead captured locally, Salesforce error: {str(e)}"

    elif sf_username and sf_password and sf_security_token:
        # Fallback: try legacy SOAP login (works on standard orgs)
        try:
            from simple_salesforce import Salesforce

            sf = Salesforce(
                username=sf_username,
                password=sf_password,
                security_token=sf_security_token,
            )

            name_parts = name.strip().split(" ", 1)
            result = sf.Lead.create({
                "FirstName":   name_parts[0],
                "LastName":    name_parts[1] if len(name_parts) > 1 else "Unknown",
                "Email":       email,
                "Company":     f"Content Creator ({platform})",
                "LeadSource":  "AutoStream Chatbot",
                "Description": f"Platform: {platform}\nInterested Plan: {plan}",
            })
            if result.get("success"):
                print(f"✅ Salesforce Lead created (SOAP)! ID: {result.get('id')}")
                return f"Lead saved to Salesforce ✅ — {name} ({email})"
            return f"Salesforce error: {result.get('errors')}"

        except Exception as e:
            print(f"⚠️  Salesforce SOAP error: {e}")
            return f"Lead captured locally, Salesforce error: {str(e)}"

    else:
        print("ℹ️  Salesforce credentials not configured — saved locally only.")
        return (
            f"Lead captured (local only): {name} ({email}) — "
            f"Platform: {platform}, Plan: {plan}"
        )


# ── Validation helpers ────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    return "@" in email and "." in email and len(email) > 5

def validate_name(name: str) -> bool:
    return len(name.strip()) >= 2

def validate_platform(platform: str, valid_platforms: list) -> bool:
    return platform.lower() in [p.lower() for p in valid_platforms]