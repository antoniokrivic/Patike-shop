from __future__ import annotations

from django.contrib.auth.decorators import user_passes_test


def is_admin_user(user) -> bool:
    # Pristup staff/admin dijelu imaju samo authenticated staff/superuser korisnici.
    return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))


admin_required = user_passes_test(is_admin_user)
