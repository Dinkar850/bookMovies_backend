from django.db import models


class ActiveManager(models.Manager):
    """Custom manager to be used in the `ActiveableModel` for filtering active entries using `active_objects`"""

    def get_queryset(self):
        """Attaches itself with the queryset for filtering only active objects"""

        return super().get_queryset().filter(is_active=True)
