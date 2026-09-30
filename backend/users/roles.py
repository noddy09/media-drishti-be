"""Shared role derivation for stock django.contrib.auth.User.

Role is not a DB field — it's derived from is_superuser/is_staff flags,
matching the same logic used to set the 'role' JWT claim in token.py.
"""


def get_user_role(user):
    if user.is_superuser:
        return 'admin'
    if user.is_staff:
        return 'employee'
    return 'client'


def is_staff_or_admin(user):
    return user.is_staff or user.is_superuser
