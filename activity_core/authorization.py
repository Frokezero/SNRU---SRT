"""Central authorization rules shared by API routes and services."""


def can_manage_event(user, event):
    if not user or not event:
        return False
    return user.get("role") == "admin" or (
        user.get("role") == "major" and event.get("owner") == user.get("name")
    )


def can_manage_student(user, student):
    if not user or not student:
        return False
    return user.get("role") == "admin" or (
        user.get("role") == "major"
        and student.get("role") == "student"
        and student.get("major") == user.get("name")
    )


def can_access_participation(user, participation, event=None):
    if not user or not participation:
        return False
    if user.get("role") == "admin":
        return True
    if user.get("role") == "student":
        return participation.get("username") == user.get("username")
    return can_manage_event(user, event)
