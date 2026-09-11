from activity_core.authorization import can_manage_event, can_manage_student
from activity_core.validation import valid_transition, validate_password, validate_score
from activity_core.security import redact_sensitive


def test_permission_matrix():
    admin = {"role": "admin", "name": "Central"}
    major_a = {"role": "major", "name": "Major A"}
    event_a = {"owner": "Major A"}
    event_b = {"owner": "Major B"}
    student_a = {"role": "student", "major": "Major A"}
    student_b = {"role": "student", "major": "Major B"}

    assert can_manage_event(admin, event_b)
    assert can_manage_event(major_a, event_a)
    assert not can_manage_event(major_a, event_b)
    assert can_manage_student(major_a, student_a)
    assert not can_manage_student(major_a, student_b)


def test_state_machines_reject_invalid_transitions():
    assert valid_transition("registration", "waitlist", "confirmed")
    assert not valid_transition("registration", "cancelled", "confirmed")
    assert valid_transition("participation", "pending", "approved")
    assert not valid_transition("participation", "approved", "pending")


def test_password_and_score_validation():
    assert validate_password("StrongPass123")[0]
    assert not validate_password("123456")[0]
    assert validate_score(10) == (True, 10)
    assert validate_score(-1)[0] is False
    assert validate_score(10001)[0] is False


def test_sensitive_audit_fields_are_redacted_recursively():
    payload = {
        "username": "65001", "password": "secret",
        "nested": {"otp": "123456", "safe": "value"},
        "items": [{"token": "raw-token"}],
    }
    redacted = redact_sensitive(payload)
    assert redacted["password"] == "[REDACTED]"
    assert redacted["nested"]["otp"] == "[REDACTED]"
    assert redacted["items"][0]["token"] == "[REDACTED]"
    assert redacted["nested"]["safe"] == "value"
