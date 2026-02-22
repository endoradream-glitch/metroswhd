from enum import Enum


class Role(str, Enum):
    """Enumerate roles for RBAC."""

    SUPER_ADMIN = "super_admin"
    HQ_OPS = "hq_ops"
    PATROL_COMD = "patrol_comd"
    PATROL_MEMBER = "patrol_member"
    VIEW_ONLY = "view_only"


ROLE_HIERARCHY = {
    Role.SUPER_ADMIN: 5,
    Role.HQ_OPS: 4,
    Role.PATROL_COMD: 3,
    Role.PATROL_MEMBER: 2,
    Role.VIEW_ONLY: 1,
}


def has_permission(user_role: Role, required_role: Role) -> bool:
    """Return True if user_role has permission equal or higher than required_role."""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)