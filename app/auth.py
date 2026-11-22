from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hash password securely."""
    return generate_password_hash(password)

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hashed string."""
    return check_password_hash(hashed, password)

# Role permission matrices
ROLE_PERMISSIONS = {
    "admin": {
        "view_profits": True,
        "create_booking": True,
        "edit_booking": True,
        "delete_booking": True,
        "issue_eta": True,
        "create_voucher": True,
        "manage_users": True,
        "view_reports": True
    },
    "accountant": {
        "view_profits": True,
        "create_booking": False,
        "edit_booking": False,
        "delete_booking": False,
        "issue_eta": True,
        "create_voucher": True,
        "manage_users": False,
        "view_reports": True
    },
    "ticketing": {
        "view_profits": False,
        "create_booking": True,
        "edit_booking": True,
        "delete_booking": False,
        "issue_eta": True, # can issue simple invoice
        "create_voucher": False,
        "manage_users": False,
        "view_reports": False
    },
    "umrah": {
        "view_profits": False,
        "create_booking": True,
        "edit_booking": True,
        "delete_booking": False,
        "issue_eta": False,
        "create_voucher": True, # can receive deposit
        "manage_users": False,
        "view_reports": False
    }
}

def get_permissions(role: str) -> dict:
    return ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["ticketing"])
