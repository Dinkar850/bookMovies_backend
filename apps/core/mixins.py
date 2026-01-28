from django.utils import timezone


class UpcomingSlotsQuerySetMixin:
    """Sets querysets and prefetch arguments and provides `base_queryset` method that returns entries for which slots are available"""

    queryset = None
    prefetch_related_args = ()

    def get_now(self):
        """Sets and returns `now` to a predefined time"""
        return timezone.now()

    def base_queryset(self):
        """Generates a queryset for retrieving entries having at least one active slot, eg. Movies, Cinemas"""
        now = self.get_now()
        return (
            self.queryset.filter(slots__is_active=True, slots__schedule__gte=now)
            .distinct()
            .prefetch_related(*self.prefetch_related_args)
        )
