from __future__ import annotations
from typing import Tuple
import os
import requests
from dotenv import load_dotenv

NEW_BASE = "https://connect.mailerlite.com/api"      # New MailerLite
CLASSIC_BASE = "https://api.mailerlite.com/api/v2"   # Classic (v2)

def _auth_headers(api_key: str, is_new: bool) -> dict:
    if is_new:
        return {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    return {"X-MailerLite-ApiKey": api_key, "Content-Type": "application/json"}

def detect_flavor(api_key: str) -> Tuple[str, bool]:
    try:
        r = requests.get(f"{NEW_BASE}/me", headers=_auth_headers(api_key, True), timeout=10)
        if r.status_code in (200, 401, 403):
            return NEW_BASE, True
    except requests.RequestException:
        pass
    try:
        r = requests.get(f"{CLASSIC_BASE}/groups", headers=_auth_headers(api_key, False), timeout=10)
        if r.status_code in (200, 401, 403, 422):
            return CLASSIC_BASE, False
    except requests.RequestException:
        pass
    raise RuntimeError("Could not determine MailerLite API flavor. Check connectivity and API key.")

def whoami(api_key: str, base_url: str, is_new: bool) -> dict:
    if is_new:
        r = requests.get(f"{base_url}/me", headers=_auth_headers(api_key, True), timeout=10)
        return {"status": r.status_code, "data": (r.json() if "application/json" in r.headers.get("Content-Type","") else None)}
    r = requests.get(f"{base_url}/groups", headers=_auth_headers(api_key, False), timeout=10)
    return {"status": r.status_code, "hint": "Classic API probe (/groups)"}

def load_api_key() -> str:
    load_dotenv()
    key = os.getenv("MAILERLITE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("MAILERLITE_API_KEY missing. Copy .env.template to .env and set the key.")
    return key

if __name__ == "__main__":
    key = load_api_key()
    base, is_new = detect_flavor(key)
    print({"base_url": base, "is_new": is_new})
    print(whoami(key, base, is_new))
