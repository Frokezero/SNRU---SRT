"""Domain validation and allowed state transitions."""

import re


REGISTRATION_TRANSITIONS = {
    "confirmed": {"cancelled"},
    "waitlist": {"confirmed", "cancelled"},
    "pending": {"confirmed", "waitlist", "cancelled"},
    "cancelled": set(),
}

PARTICIPATION_TRANSITIONS = {
    "pending": {"approved", "rejected"},
    "approved": {"rejected"},
    "rejected": {"pending", "approved"},
}


def validate_password(password):
    if not isinstance(password, str) or len(password) < 10:
        return False, "Password must be at least 10 characters"
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Password must contain both a letter and a number"
    return True, None


def valid_transition(kind, old_status, new_status, allow_same=True):
    transitions = (
        REGISTRATION_TRANSITIONS if kind == "registration"
        else PARTICIPATION_TRANSITIONS if kind == "participation"
        else None
    )
    if transitions is None or old_status not in transitions:
        return False
    if allow_same and old_status == new_status:
        return True
    return new_status in transitions[old_status]


def validate_score(score, maximum=10000):
    try:
        value = int(score)
    except (TypeError, ValueError):
        return False, None
    return 0 <= value <= maximum, value
