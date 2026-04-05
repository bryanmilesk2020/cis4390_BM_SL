"""
auth.py — User registry and role-based access control for LedgerCore.

Roles
-----
admin   — Full access: Overview, Submit Record, Mint Block, Ledger, Security
auditor — Read-only: Overview, Ledger (no submit, no mint, no security tab)
viewer  — Overview only (dashboard / analytics)

Passwords are stored as SHA-256 hex digests.
In a real deployment swap this for bcrypt + a proper secrets store.
"""

import hashlib

def _hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ── User registry ─────────────────────────────────────────────────────────────
# Format: { "username": { "password_hash": ..., "role": ..., "display_name": ... } }
USERS: dict = {
    "admin": {
        "password_hash": _hash("admin123"),
        "role":          "admin",
        "display_name":  "Admin User",
    },
    "auditor": {
        "password_hash": _hash("audit456"),
        "role":          "auditor",
        "display_name":  "Audit User",
    },
    "viewer": {
        "password_hash": _hash("view789"),
        "role":          "viewer",
        "display_name":  "Read-Only Viewer",
    },
}

# ── Role → allowed tabs ───────────────────────────────────────────────────────
# Tab keys match the strings used in app.py tab logic.
ROLE_PERMISSIONS: dict = {
    "admin": {
        "tabs":      ["overview", "submit", "ledger", "security"],
        "can_submit": True,
        "can_mint":   True,
        "label":      "Administrator",
        "color":      "#2563eb",
        "badge_bg":   "#0f2847",
        "badge_fg":   "#60a5fa",
    },
    "auditor": {
        "tabs":      ["overview", "ledger"],
        "can_submit": False,
        "can_mint":   False,
        "label":      "Auditor",
        "color":      "#7c3aed",
        "badge_bg":   "#1e1040",
        "badge_fg":   "#c084fc",
    },
    "viewer": {
        "tabs":      ["overview"],
        "can_submit": False,
        "can_mint":   False,
        "label":      "Viewer",
        "color":      "#0891b2",
        "badge_bg":   "#0c2535",
        "badge_fg":   "#38bdf8",
    },
}


def authenticate(username: str, password: str):
    """
    Returns (True, user_dict) on success, (False, None) on failure.
    """
    username = username.strip().lower()
    user = USERS.get(username)
    if user and user["password_hash"] == _hash(password):
        return True, {
            "username":     username,
            "display_name": user["display_name"],
            "role":         user["role"],
            **ROLE_PERMISSIONS[user["role"]],
        }
    return False, None


def get_permissions(role: str) -> dict:
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["viewer"])