"""Security helpers that are framework-independent and unit-testable."""

SENSITIVE_KEYS = {
    "password", "currentpassword", "newpassword", "new_password",
    "token", "reset_token", "otp", "secret", "authorization",
}


def redact_sensitive(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if str(key).lower() in SENSITIVE_KEYS else redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_sensitive(item) for item in value]
    return value
